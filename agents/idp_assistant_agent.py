"""Self-service Q&A agent for IDP developers."""

from __future__ import annotations

from typing import Any

from agents.base import Agent, AgentResponse
from tools.idp_tools import find_self_service_workflow, search_idp_knowledge


class IDPAssistantAgent(Agent):
    """Answers developer questions and recommends self-service workflows."""

    def __init__(self, settings: Any | None = None) -> None:
        super().__init__(
            name="IDPAssistantAgent",
            model="gemini-2.0-flash",
            instructions=(
                "You are a helpful Internal Developer Portal assistant. Answer questions about "
                "workflows, pipelines, onboarding, and self-service tasks. Recommend the right "
                "workflow and guide the developer to the next step. Never expose secrets or "
                "internal credentials."
            ),
            tools={
                "search_idp_knowledge": search_idp_knowledge,
                "find_self_service_workflow": find_self_service_workflow,
            },
            settings=settings,
        )

    def _execute(self, user_input: str, context: dict[str, Any]) -> AgentResponse:
        workflow = self.call_tool("find_self_service_workflow", task_description=user_input)
        knowledge = self.call_tool("search_idp_knowledge", query=user_input, top_k=3)
        answer = (
            f"Recommended workflow: **{workflow['workflow']}** "
            f"(confidence: {workflow['confidence']}).\n\n"
            f"Related knowledge:\n{knowledge}\n\n"
            "Say 'create workflow' to generate the Harness IDP Workflow YAML, or "
            "'create pipeline' to generate the underlying pipeline."
        )
        return AgentResponse(
            agent=self.name,
            answer=answer,
            data={"workflow": workflow, "knowledge": knowledge},
        )
