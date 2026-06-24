"""Agent that manages manager approval workflows."""

from __future__ import annotations

from typing import Any

from agents.base import Agent, AgentResponse
from tools.approval_tools import check_approval_status, request_manager_approval


class ApprovalAgent(Agent):
    """Handles manager approval requests and status checks."""

    def __init__(self, settings: Any | None = None) -> None:
        super().__init__(
            name="ApprovalAgent",
            model="gemini-2.0-flash",
            instructions=(
                "You are an Approval Agent. Create approval requests for self-service actions "
                "that require manager sign-off, and report approval status. Always enforce "
                "4-eyes separation: the requestor cannot approve their own request."
            ),
            tools={
                "request_manager_approval": request_manager_approval,
                "check_approval_status": check_approval_status,
            },
            settings=settings,
        )

    def _execute(self, user_input: str, context: dict[str, Any]) -> AgentResponse:
        request = context.get("approval_request", {})
        request_id = request.get("request_id")
        requestor = request.get("requestor", "developer")
        summary = request.get("summary", user_input)
        if not request_id:
            approval = self.call_tool(
                "request_manager_approval",
                request_id=f"req-{requestor}-{hash(summary) % 100000:05d}",
                requestor=requestor,
                summary=summary,
            )
            answer = (
                f"Approval request **{approval['request_id']}** created for {requestor}.\n"
                f"Status: {approval['status']}. A manager must approve before "
                "provisioning continues."
            )
        else:
            approval = self.call_tool("check_approval_status", request_id=request_id)
            answer = f"Approval status for {request_id}: {approval.get('status', 'unknown')}."
        return AgentResponse(agent=self.name, answer=answer, data={"approval": approval})
