"""FastAPI entry point for the IDP agent platform.

All endpoints work with the default in-memory adapters, so the platform is fully
functional via API without any external orchestrator (e.g., Harness) configured.
"""

from __future__ import annotations

from contextlib import asynccontextmanager
from typing import Any

from fastapi import FastAPI
from pydantic import BaseModel, Field

from agents import (
    ApprovalAgent,
    AuditAgent,
    ExecutionAgent,
    IDPAssistantAgent,
    PipelineAgent,
    RouterAgent,
    WorkflowAgent,
)
from observability.telemetry import init_telemetry, log_structured
from security.governance import build_audit_record, log_audit


class AskRequest(BaseModel):
    message: str
    context: dict[str, Any] | None = None
    actor: str = "developer"


class AskResponse(BaseModel):
    agent: str
    answer: str
    data: dict[str, Any] | None = None


class GenerateWorkflowRequest(BaseModel):
    identifier: str = "example_self_service_workflow"
    name: str = "Example Self Service Workflow"
    parameters: list[dict[str, Any]] = Field(default_factory=list)
    pipeline_identifier: str = "example_pipeline"
    actor: str = "developer"


class GeneratePipelineRequest(BaseModel):
    identifier: str = "example_self_service_pipeline"
    name: str = "Example Self Service Pipeline"
    steps: list[dict[str, Any]] = Field(default_factory=list)
    requires_approval: bool = False
    actor: str = "developer"


class SubmitRequest(BaseModel):
    pipeline_identifier: str
    inputset: dict[str, Any] = Field(default_factory=dict)
    actor: str = "developer"


class StatusRequest(BaseModel):
    execution_id: str


class ApprovalRequest(BaseModel):
    request_id: str | None = None
    requestor: str = "developer"
    summary: str = ""


class ApprovalActionRequest(BaseModel):
    request_id: str
    approver: str
    reason: str | None = None


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_telemetry()
    yield


app = FastAPI(
    title="IDP Automation Agent Platform",
    description=(
        "Multi-agent self-service automation API. Works with or without an external orchestrator."
    ),
    version="0.1.0",
    lifespan=lifespan,
)

router = RouterAgent()
specialists = {
    "self_service_qa": IDPAssistantAgent(),
    "workflow_design": WorkflowAgent(),
    "pipeline_design": PipelineAgent(),
    "approval_request": ApprovalAgent(),
    "execution_status": ExecutionAgent(),
    "audit_governance": AuditAgent(),
}


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/ask", response_model=AskResponse)
async def ask(request: AskRequest) -> AskResponse:
    log_structured(event="ask_received", actor=request.actor, message_length=len(request.message))
    route = router.run(request.message, request.context or {})
    domain = route.data.get("domain", "self_service_qa")
    specialist = specialists.get(domain, specialists["self_service_qa"])
    response = specialist.run(request.message, request.context or {})
    audit = build_audit_record(
        actor=request.actor,
        action="ask",
        resource=domain,
        details={
            "agent": response.agent,
            "routed_to": domain,
        },
    )
    log_audit(audit)
    return AskResponse(
        agent=response.agent,
        answer=response.answer,
        data=response.data,
    )


@app.post("/generate/workflow", response_model=AskResponse)
async def generate_workflow(request: GenerateWorkflowRequest) -> AskResponse:
    agent = WorkflowAgent()
    context = {
        "workflow_request": {
            "identifier": request.identifier,
            "name": request.name,
            "parameters": request.parameters,
            "pipeline_identifier": request.pipeline_identifier,
        }
    }
    response = agent.run("generate workflow", context)
    log_audit(build_audit_record(
        actor=request.actor,
        action="generate_workflow",
        resource=request.identifier,
    ))
    return AskResponse(agent=response.agent, answer=response.answer, data=response.data)


@app.post("/generate/pipeline", response_model=AskResponse)
async def generate_pipeline(request: GeneratePipelineRequest) -> AskResponse:
    agent = PipelineAgent()
    context = {
        "pipeline_request": {
            "identifier": request.identifier,
            "name": request.name,
            "steps": request.steps,
            "requires_approval": request.requires_approval,
        }
    }
    response = agent.run("generate pipeline", context)
    log_audit(build_audit_record(
        actor=request.actor,
        action="generate_pipeline",
        resource=request.identifier,
    ))
    return AskResponse(agent=response.agent, answer=response.answer, data=response.data)


@app.post("/execute", response_model=AskResponse)
async def execute(request: SubmitRequest) -> AskResponse:
    agent = ExecutionAgent()
    context = {
        "execution_request": {
            "pipeline_identifier": request.pipeline_identifier,
            "inputset": request.inputset,
            "requestor": request.actor,
        }
    }
    response = agent.run("submit pipeline", context)
    return AskResponse(agent=response.agent, answer=response.answer, data=response.data)


@app.post("/status", response_model=AskResponse)
async def status(request: StatusRequest) -> AskResponse:
    agent = ExecutionAgent()
    context = {"execution_request": {"execution_id": request.execution_id}}
    response = agent.run("check status", context)
    return AskResponse(agent=response.agent, answer=response.answer, data=response.data)


@app.post("/approval/request", response_model=AskResponse)
async def approval_request(request: ApprovalRequest) -> AskResponse:
    from tools.approval_tools import request_manager_approval
    request_id = request.request_id or (
        f"req-{request.requestor}-{hash(request.summary) % 100000:05d}"
    )
    approval = request_manager_approval(request_id, request.requestor, request.summary)
    return AskResponse(
        agent="ApprovalAgent",
        answer=(
            f"Approval request **{approval['request_id']}** created for {request.requestor}.\n"
            f"Status: {approval['status']}. A manager must approve before provisioning continues."
        ),
        data={"approval": approval},
    )


@app.post("/approval/approve", response_model=AskResponse)
async def approval_approve(request: ApprovalActionRequest) -> AskResponse:
    from tools.approval_tools import approve_request
    result = approve_request(request.request_id, request.approver)
    return AskResponse(
        agent="ApprovalAgent",
        answer=f"Request {request.request_id} approved by {request.approver}.",
        data={"approval": result},
    )


@app.post("/approval/reject", response_model=AskResponse)
async def approval_reject(request: ApprovalActionRequest) -> AskResponse:
    from tools.approval_tools import reject_request
    result = reject_request(request.request_id, request.approver, request.reason or "")
    return AskResponse(
        agent="ApprovalAgent",
        answer=f"Request {request.request_id} rejected by {request.approver}.",
        data={"approval": result},
    )


@app.post("/audit", response_model=AskResponse)
async def audit(request: AskRequest) -> AskResponse:
    agent = AuditAgent()
    response = agent.run(
        request.message,
        {"actor": request.actor, "action": "manual_audit", "resource": "user_input"},
    )
    return AskResponse(agent=response.agent, answer=response.answer, data=response.data)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
