"""Approval workflow helpers for self-service requests."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from security.governance import build_audit_record, log_audit

_APPROVALS: dict[str, dict[str, Any]] = {}


def request_manager_approval(request_id: str, requestor: str, summary: str) -> dict[str, Any]:
    """Record a manager approval request and return its status."""
    approval = {
        "request_id": request_id,
        "requestor": requestor,
        "summary": summary,
        "status": "pending",
        "created_at": datetime.now(UTC).isoformat(),
        "approved_by": None,
        "approved_at": None,
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


def check_approval_status(request_id: str) -> dict[str, Any]:
    """Return the current approval status for a request."""
    approval = _APPROVALS.get(request_id)
    if not approval:
        return {"error": "Approval request not found"}
    return approval


def approve_request(request_id: str, approver: str) -> dict[str, Any]:
    """Approve a request (manager action)."""
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
