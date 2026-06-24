"""Pipeline execution helpers: submit, poll, and report status."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

import httpx

from config import Settings, get_settings
from security.governance import build_audit_record, log_audit
from security.iam import get_harness_api_key

_EXECUTIONS: dict[str, dict[str, Any]] = {}


def submit_pipeline_request(
    pipeline_identifier: str,
    inputset: dict[str, Any],
    requestor: str,
    settings: Settings | None = None,
) -> dict[str, Any]:
    """Submit a pipeline request and record the execution."""
    settings = settings or get_settings()
    execution_id = f"exec-{datetime.now(UTC).strftime('%Y%m%d%H%M%S')}"
    if not settings.harness_account_identifier or not settings.harness_project_identifier:
        return {
            "execution_id": execution_id,
            "status": "submitted_mock",
            "message": "Harness account/project not configured; returning mock submission.",
        }
    try:
        api_key = get_harness_api_key(settings)
        url = (
            f"{settings.harness_idp_base_url}/gateway/pipeline/api/webhook/custom/"
            f"{pipeline_identifier}/v3?accountIdentifier={settings.harness_account_identifier}"
            f"&orgIdentifier={settings.harness_org_identifier}"
            f"&projectIdentifier={settings.harness_project_identifier}"
        )
        response = httpx.post(
            url,
            headers={
                "Content-Type": "application/json",
                "X-Api-Key": api_key,
            },
            json={"inputset": inputset},
            timeout=30.0,
        )
        response.raise_for_status()
        data = response.json()
        _EXECUTIONS[execution_id] = {
            "execution_id": execution_id,
            "pipeline_identifier": pipeline_identifier,
            "requestor": requestor,
            "status": "submitted",
            "api_url": data.get("data", {}).get("apiUrl"),
        }
    except Exception as exc:
        _EXECUTIONS[execution_id] = {
            "execution_id": execution_id,
            "pipeline_identifier": pipeline_identifier,
            "requestor": requestor,
            "status": "submit_error",
            "error": str(exc),
        }
    record = build_audit_record(
        actor=requestor,
        action="pipeline_submitted",
        resource=pipeline_identifier,
        details={
            "execution_id": execution_id,
            "status": _EXECUTIONS[execution_id]["status"],
        },
    )
    log_audit(record)
    return _EXECUTIONS[execution_id]


def get_execution_status(execution_id: str) -> dict[str, Any]:
    """Return the recorded execution status."""
    return _EXECUTIONS.get(execution_id, {"error": "Execution not found"})


def poll_execution(execution_id: str, settings: Settings | None = None) -> dict[str, Any]:
    """Poll a running Harness execution via its API URL."""
    settings = settings or get_settings()
    execution = _EXECUTIONS.get(execution_id)
    if not execution or not execution.get("api_url"):
        return execution or {"error": "Execution not found"}
    try:
        api_key = get_harness_api_key(settings)
        response = httpx.get(
            execution["api_url"],
            headers={"X-Api-Key": api_key},
            timeout=30.0,
        )
        response.raise_for_status()
        data = response.json()
        summary = (
            data.get("data", {})
            .get("executionDetails", {})
            .get("pipelineExecutionSummary", {})
        )
        execution["status"] = summary.get("status", "unknown")
        execution["last_poll"] = datetime.now(UTC).isoformat()
    except Exception as exc:
        execution["status"] = "poll_error"
        execution["error"] = str(exc)
    return execution
