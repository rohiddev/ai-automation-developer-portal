"""Pipeline YAML generation and validation helpers for Harness."""

from __future__ import annotations

import re
from typing import Any

import yaml

from config import Settings, get_settings


def _sanitize_name(value: str) -> str:
    """Convert a string into a Harness-safe name."""
    value = re.sub(r"[^0-9a-zA-Z_\s]", "", value)
    return re.sub(r"\s+", " ", value.strip())[:128]


def generate_pipeline_yaml(
    identifier: str,
    name: str,
    steps: list[dict[str, Any]],
    requires_approval: bool = False,
    settings: Settings | None = None,
) -> str:
    """Generate a Harness pipeline YAML with Http steps and optional approval."""
    settings = settings or get_settings()
    pipeline = {
        "pipeline": {
            "identifier": identifier,
            "name": _sanitize_name(name),
            "orgIdentifier": settings.harness_org_identifier,
            "projectIdentifier": settings.harness_project_identifier,
            "stages": [
                {
                    "stage": {
                        "identifier": "provision",
                        "name": "Provision",
                        "type": "Custom",
                        "spec": {
                            "execution": {
                                "steps": steps,
                            }
                        },
                    }
                }
            ],
        }
    }
    if requires_approval:
        pipeline["pipeline"]["stages"][0]["stage"]["spec"]["execution"]["steps"].insert(
            0,
            {
                "step": {
                    "identifier": "manager_approval",
                    "name": "Manager Approval",
                    "type": "HarnessApproval",
                    "spec": {
                        "approvalMessage": "Please approve the self-service request.",
                        "approvers": {
                            "userGroups": ["manager_approvers"],
                            "minimumCount": 1,
                            "disallowPipelineExecutor": True,
                        },
                    },
                    "timeout": "24h",
                }
            },
        )
    return yaml.safe_dump(pipeline, sort_keys=False)


def validate_pipeline_yaml(yaml_text: str) -> dict[str, Any]:
    """Validate a pipeline YAML for required fields and safe step names."""
    try:
        data = yaml.safe_load(yaml_text)
    except yaml.YAMLError as exc:
        return {"valid": False, "errors": [f"YAML parse error: {exc}"]}
    errors = []
    pipeline = data.get("pipeline", {})
    for field in ("identifier", "name", "stages"):
        if not pipeline.get(field):
            errors.append(f"Missing required field: {field}")
    if not re.match(r"^[a-zA-Z][0-9a-zA-Z_]{0,127}$", pipeline.get("identifier", "")):
        errors.append(f"Pipeline identifier invalid: {pipeline.get('identifier')}")
    if not re.match(r"^[a-zA-Z][0-9a-zA-Z_\s]{0,127}$", pipeline.get("name", "")):
        errors.append(f"Pipeline name invalid: {pipeline.get('name')}")
    for stage in pipeline.get("stages", []):
        stage_data = stage.get("stage", {})
        if not stage_data.get("identifier") or not stage_data.get("name"):
            errors.append("Each stage must have identifier and name")
        for step in stage_data.get("spec", {}).get("execution", {}).get("steps", []):
            step_data = step.get("step", {})
            if not step_data.get("identifier") or not step_data.get("name"):
                errors.append("Each step must have identifier and name")
            if not re.match(r"^[a-zA-Z][0-9a-zA-Z_\s]{0,127}$", step_data.get("name", "")):
                errors.append(f"Step name invalid: {step_data.get('name')}")
    return {"valid": len(errors) == 0, "errors": errors}
