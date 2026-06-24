"""Workflow YAML generation and validation helpers for Harness IDP."""

from __future__ import annotations

import re
from typing import Any

import yaml

from config import Settings, get_settings


def _sanitize_identifier(value: str) -> str:
    """Convert a string into a Harness-safe identifier."""
    value = re.sub(r"[^0-9a-zA-Z_\s]", "", value)
    value = re.sub(r"\s+", "_", value.strip())
    return value[:64]


def generate_workflow_yaml(
    identifier: str,
    name: str,
    parameters: list[dict[str, Any]],
    pipeline_identifier: str,
    settings: Settings | None = None,
) -> str:
    """Generate a Harness IDP Workflow YAML that triggers a custom pipeline."""
    settings = settings or get_settings()
    workflow = {
        "apiVersion": "harness.io/v1",
        "kind": "Workflow",
        "identifier": _sanitize_identifier(identifier),
        "name": name,
        "type": "service",
        "owner": "platform_engineering",
        "metadata": {
            "orgIdentifier": settings.harness_org_identifier,
            "projectIdentifier": settings.harness_project_identifier,
            "description": f"Self-service workflow for {name}",
            "tags": ["self-service", "idp", "generated"],
        },
        "spec": {
            "parameters": parameters or [{"title": "Request Details", "properties": {}}],
            "steps": [
                {
                    "id": "trigger_pipeline",
                    "name": "Trigger Pipeline",
                    "action": "trigger:harness-custom-pipeline",
                    "input": {
                        "url": (
                            f"{settings.harness_idp_base_url}/account/"
                            f"{settings.harness_account_identifier}/org/"
                            f"{settings.harness_org_identifier}/projects/"
                            f"{settings.harness_project_identifier}/pipelines/"
                            f"{pipeline_identifier}"
                        ),
                        "inputset": {
                            "requestorEmail": "${{ parameters.requestorEmail }}",
                        },
                    },
                }
            ],
            "output": {
                "links": [
                    {
                        "title": "View Pipeline",
                        "url": "${{ steps.trigger_pipeline.output.url }}",
                    }
                ]
            },
        },
    }
    return yaml.safe_dump(workflow, sort_keys=False)


def validate_workflow_yaml(yaml_text: str) -> dict[str, Any]:
    """Validate a workflow YAML for required fields and safe identifiers."""
    try:
        data = yaml.safe_load(yaml_text)
    except yaml.YAMLError as exc:
        return {"valid": False, "errors": [f"YAML parse error: {exc}"]}
    errors = []
    if data.get("apiVersion") != "harness.io/v1":
        errors.append("apiVersion must be harness.io/v1")
    if data.get("kind") != "Workflow":
        errors.append("kind must be Workflow")
    for field in ("identifier", "name", "spec"):
        if not data.get(field):
            errors.append(f"Missing required field: {field}")
    spec = data.get("spec", {})
    if not spec.get("parameters"):
        errors.append("Workflow spec must contain parameters")
    if not spec.get("steps"):
        errors.append("Workflow spec must contain steps")
    for step in spec.get("steps", []):
        if not step.get("id") or not step.get("name"):
            errors.append("Each step must have id and name")
        if not re.match(r"^[a-zA-Z][0-9a-zA-Z_\s]{0,127}$", step.get("name", "")):
            errors.append(f"Step name invalid: {step.get('name')}")
    return {"valid": len(errors) == 0, "errors": errors}
