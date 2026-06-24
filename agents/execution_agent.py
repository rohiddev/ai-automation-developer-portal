"""Agent that monitors and reports pipeline execution status."""

from __future__ import annotations

from typing import Any

from agents.base import Agent, AgentResponse
from tools.execution_tools import get_execution_status, submit_pipeline_request


class ExecutionAgent(Agent):
    """Submits and monitors Harness pipeline executions."""

    def __init__(self, settings: Any | None = None) -> None:
        super().__init__(
            name="ExecutionAgent",
            model="gemini-2.0-flash",
            instructions=(
                "You are an Execution Agent. Submit self-service requests to Harness pipelines "
                "and report execution status. Never expose API keys or secrets in responses."
            ),
            tools={
                "submit_pipeline_request": submit_pipeline_request,
                "get_execution_status": get_execution_status,
            },
            settings=settings,
        )

    def _execute(self, user_input: str, context: dict[str, Any]) -> AgentResponse:
        request = context.get("execution_request", {})
        execution_id = request.get("execution_id")
        if execution_id:
            status = self.call_tool("get_execution_status", execution_id=execution_id)
            answer = f"Execution **{execution_id}** status: {status.get('status', 'unknown')}."
        else:
            pipeline = request.get("pipeline_identifier", "example_pipeline")
            inputset = request.get("inputset", {})
            requestor = request.get("requestor", "developer")
            status = self.call_tool(
                "submit_pipeline_request",
                pipeline_identifier=pipeline,
                inputset=inputset,
                requestor=requestor,
            )
            answer = (
                f"Submitted pipeline **{pipeline}**. Execution ID: **{status['execution_id']}**.\n"
                f"Status: {status['status']}."
            )
        return AgentResponse(agent=self.name, answer=answer, data={"execution": status})
