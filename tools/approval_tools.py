"""Approval workflow helpers for self-service requests."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from adapters.factory import get_adapters
from config import Settings, get_settings
from security.governance import build_audit_record, log_audit

_APPROVALS: dict[str, dict[str, Any]] = {}


def _get_orchestrator(settings: Settings | None = None) -> Any:
    settings = settings or get_settings()
    return get_adapters(settings)["orchestrator"]


def request_manager_approval(request_id: str, requestor: str, summary: str) -> dict[str, Any]:
    """Create a manager approval request through the configured orchestrator."""
    orchestrator = _get_orchestrator()
    try:
        approval = orchestrator.request_approval(request_id, requestor, summary)
    except NotImplementedError:
        approval = {
            "request_id": request_id,
            "requestor": requestor,
            "summary": summary,
            "status": "pending",
            "note": "Orchestrator-native approvals not available; using in-memory tracking.",
        }
        _APPROVALS[request_id] = approval
    record = build_audit_record(
        actor=requestor,
        action="approval_requested",
        resource=request_id,
        details={"summary": summary},
    )
    log_audit(record)
    return approval


def check_approval_status(request_id: str, settings: Settings | None = None) -> dict[str, Any]:
    """Return the current approval status for a request."""
    settings = settings or get_settings()
    orchestrator = _get_orchestrator(settings)
    try:
        approval = orchestrator.get_approval(request_id)
        if "status" in approval:
            return approval
    except Exception:
        pass
    return _APPROVALS.get(request_id, {"error": "Approval request not found"})


def approve_request(request_id: str, approver: str) -> dict[str, Any]:
    """Approve a request (manager action)."""
    orchestrator = _get_orchestrator()
    try:
        approval = orchestrator.approve(request_id, approver)
    except (NotImplementedError, KeyError):
        approval = _APPROVALS.get(request_id)
        if not approval:
            return {"error": "Approval request not found"}
        approval["status"] = "approved"
        approval["approved_by"] = approver
        approval["approved_at"] = datetime.now(UTC).isoformat()
    record = build_audit_record(
        actor=approver,
        action="approval_granted",
        resource=request_id,
    )
    log_audit(record)
    return approval


def reject_request(request_id: str, approver: str, reason: str) -> dict[str, Any]:
    """Reject a request (manager action)."""
    orchestrator = _get_orchestrator()
    try:
        approval = orchestrator.reject(request_id, approver, reason)
    except (NotImplementedError, KeyError):
        approval = _APPROVALS.get(request_id)
        if not approval:
            return {"error": "Approval request not found"}
        approval["status"] = "rejected"
        approval["approved_by"] = approver
        approval["approved_at"] = datetime.now(UTC).isoformat()
        approval["reason"] = reason
    record = build_audit_record(
        actor=approver,
        action="approval_rejected",
        resource=request_id,
        details={"reason": reason},
    )
    log_audit(record)
    return approval
