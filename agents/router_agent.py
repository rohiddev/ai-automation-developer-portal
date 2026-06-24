"""Router agent that classifies developer intent and picks a specialist."""

from __future__ import annotations

from typing import Any

from agents.base import Agent, AgentResponse


class RouterAgent(Agent):
    """Routes developer requests to the correct specialist agent."""

    def __init__(self, settings: Any | None = None) -> None:
        super().__init__(
            name="RouterAgent",
            model="gemini-2.0-flash",
            instructions=(
                "You are the Router Agent for an Internal Developer Portal assistant. "
                "Classify the request into one domain: self_service_qa, workflow_design, "
                "pipeline_design, approval_request, execution_status, audit_governance, or "
                "unknown. Return only the chosen domain and a brief reason."
            ),
            settings=settings,
        )

    def _execute(self, user_input: str, context: dict[str, Any]) -> AgentResponse:
        text = user_input.lower()
        keywords = {
            "workflow": "workflow_design",
            "pipeline": "pipeline_design",
            "yaml": "workflow_design",
            "approve": "approval_request",
            "approval": "approval_request",
            "status": "execution_status",
            "execution": "execution_status",
            "audit": "audit_governance",
            "governance": "audit_governance",
            "log": "audit_governance",
        }
        for kw, domain in keywords.items():
            if kw in text:
                return AgentResponse(
                    agent=self.name,
                    answer=f"Routing to {domain} specialist.",
                    data={"domain": domain, "reason": f"matched keyword: {kw}"},
                    routed_to=domain,
                )
        return AgentResponse(
            agent=self.name,
            answer="Routing to self-service Q&A specialist.",
            data={"domain": "self_service_qa", "reason": "default"},
            routed_to="self_service_qa",
        )
