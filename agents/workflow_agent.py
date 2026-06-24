"""Agent that generates and validates Harness IDP Workflow YAML."""

from __future__ import annotations

from typing import Any

from agents.base import Agent, AgentResponse
from tools.workflow_tools import generate_workflow_yaml, validate_workflow_yaml


class WorkflowAgent(Agent):
    """Generates and validates Harness IDP Workflow YAML."""

    def __init__(self, settings: Any | None = None) -> None:
        super().__init__(
            name="WorkflowAgent",
            model="gemini-2.0-flash",
            instructions=(
                "You are a Workflow Design Agent. Given a self-service request, produce a "
                "Harness IDP Workflow YAML with the correct apiVersion, parameters, and a "
                "trigger:harness-custom-pipeline step. Validate the YAML for Harness-safe "
                "identifiers and step names."
            ),
            tools={
                "generate_workflow_yaml": generate_workflow_yaml,
                "validate_workflow_yaml": validate_workflow_yaml,
            },
            settings=settings,
        )

    def _execute(self, user_input: str, context: dict[str, Any]) -> AgentResponse:
        request = context.get("workflow_request", {})
        identifier = request.get("identifier", "example_self_service_workflow")
        name = request.get("name", "Example Self Service Workflow")
        parameters = request.get("parameters", [])
        pipeline_identifier = request.get("pipeline_identifier", "example_pipeline")
        yaml_text = self.call_tool(
            "generate_workflow_yaml",
            identifier=identifier,
            name=name,
            parameters=parameters,
            pipeline_identifier=pipeline_identifier,
        )
        validation = self.call_tool("validate_workflow_yaml", yaml_text=yaml_text)
        if not validation["valid"]:
            answer = f"Generated workflow YAML has validation errors:\n{validation['errors']}"
        else:
            answer = f"Generated and validated Workflow YAML:\n\n```yaml\n{yaml_text}\n```"
        return AgentResponse(
            agent=self.name,
            answer=answer,
            data={"yaml": yaml_text, "validation": validation},
        )
