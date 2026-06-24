"""FastAPI entry point for the IDP agent platform."""

from __future__ import annotations

from contextlib import asynccontextmanager
from typing import Any

from fastapi import FastAPI
from pydantic import BaseModel

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


@asynccontextmanager
async def lifespan(app: FastAPI):
    init_telemetry()
    yield


app = FastAPI(
    title="IDP Automation Agent Platform",
    description="Multi-agent self-service automation for the Internal Developer Portal.",
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


@app.post("/audit")
async def audit(request: AskRequest) -> AskResponse:
    agent = AuditAgent()
    response = agent.run(
        request.message,
        {"actor": request.actor, "action": "manual_audit", "resource": "user_input"},
    )
    return AskResponse(agent=response.agent, answer=response.answer, data=response.data)


@app.post("/execute")
async def execute(request: AskRequest) -> AskResponse:
    agent = ExecutionAgent()
    response = agent.run(request.message, request.context or {})
    return AskResponse(agent=response.agent, answer=response.answer, data=response.data)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
