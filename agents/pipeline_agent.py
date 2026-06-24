"""Agent that generates and validates Harness Pipeline YAML."""

from __future__ import annotations

from typing import Any

from agents.base import Agent, AgentResponse
from tools.pipeline_tools import generate_pipeline_yaml, validate_pipeline_yaml


class PipelineAgent(Agent):
    """Generates and validates Harness Pipeline YAML."""

    def __init__(self, settings: Any | None = None) -> None:
        super().__init__(
            name="PipelineAgent",
            model="gemini-2.0-flash",
            instructions=(
                "You are a Pipeline Design Agent. Given a self-service request, produce a "
                "Harness Custom stage pipeline with Http steps that call backend APIs. "
                "Add a HarnessApproval step when the request requires manager approval. "
                "Validate step names and identifiers."
            ),
            tools={
                "generate_pipeline_yaml": generate_pipeline_yaml,
                "validate_pipeline_yaml": validate_pipeline_yaml,
            },
            settings=settings,
        )

    def _execute(self, user_input: str, context: dict[str, Any]) -> AgentResponse:
        request = context.get("pipeline_request", {})
        identifier = request.get("identifier", "example_self_service_pipeline")
        name = request.get("name", "Example Self Service Pipeline")
        steps = request.get("steps", [])
        requires_approval = request.get("requires_approval", False)
        yaml_text = self.call_tool(
            "generate_pipeline_yaml",
            identifier=identifier,
            name=name,
            steps=steps,
            requires_approval=requires_approval,
        )
        validation = self.call_tool("validate_pipeline_yaml", yaml_text=yaml_text)
        if not validation["valid"]:
            answer = f"Generated pipeline YAML has validation errors:\n{validation['errors']}"
        else:
            answer = f"Generated and validated Pipeline YAML:\n\n```yaml\n{yaml_text}\n```"
        return AgentResponse(
            agent=self.name,
            answer=answer,
            data={"yaml": yaml_text, "validation": validation},
        )
