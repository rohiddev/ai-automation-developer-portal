"""Pipeline execution helpers: submit, poll, and report status."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from adapters.factory import get_adapters
from config import Settings, get_settings
from security.governance import build_audit_record, log_audit

_EXECUTIONS: dict[str, dict[str, Any]] = {}


def submit_pipeline_request(
    pipeline_identifier: str,
    inputset: dict[str, Any],
    requestor: str,
    settings: Settings | None = None,
) -> dict[str, Any]:
    """Submit a workflow/pipeline request through the configured orchestrator."""
    settings = settings or get_settings()
    adapters = get_adapters(settings)
    orchestrator = adapters["orchestrator"]
    result = orchestrator.submit(pipeline_identifier, inputset)
    timestamp = datetime.now(UTC).strftime("%Y%m%d%H%M%S")
    execution_id = result.get("execution_id") or f"exec-{timestamp}"
    _EXECUTIONS[execution_id] = {
        "execution_id": execution_id,
        "pipeline_identifier": pipeline_identifier,
        "requestor": requestor,
        "status": result.get("status", "submitted"),
        "orchestrator_response": result,
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
    """Poll a running execution through the configured orchestrator."""
    settings = settings or get_settings()
    execution = _EXECUTIONS.get(execution_id)
    if not execution:
        return {"error": "Execution not found"}
    adapters = get_adapters(settings)
    orchestrator = adapters["orchestrator"]
    result = orchestrator.status(execution_id)
    execution["status"] = result.get("status", "unknown")
    execution["last_poll"] = datetime.now(UTC).isoformat()
    execution["orchestrator_response"] = result
    return execution
