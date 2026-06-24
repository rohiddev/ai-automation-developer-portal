"""In-memory adapters for local development and testing."""

from __future__ import annotations

from datetime import UTC, datetime
from typing import Any

from .base import AuditStore, Orchestrator, SecretStore


class InMemoryOrchestrator(Orchestrator):
    """Non-persistent orchestrator for local development and unit tests."""

    def __init__(self) -> None:
        self._executions: dict[str, dict[str, Any]] = {}
        self._approvals: dict[str, dict[str, Any]] = {}

    def submit(self, workflow_id: str, inputset: dict[str, Any]) -> dict[str, Any]:
        execution_id = f"exec-{datetime.now(UTC).strftime('%Y%m%d%H%M%S')}"
        self._executions[execution_id] = {
            "execution_id": execution_id,
            "workflow_id": workflow_id,
            "inputset": inputset,
            "status": "submitted",
        }
        return self._executions[execution_id]

    def status(self, execution_id: str) -> dict[str, Any]:
        return self._executions.get(execution_id, {"error": "Execution not found"})

    def approve(self, request_id: str, approver: str) -> dict[str, Any]:
        approval = self._approvals.get(request_id)
        if not approval:
            return {"error": "Approval request not found"}
        approval["status"] = "approved"
        approval["approved_by"] = approver
        approval["approved_at"] = datetime.now(UTC).isoformat()
        return approval

    def reject(self, request_id: str, approver: str, reason: str) -> dict[str, Any]:
        approval = self._approvals.get(request_id)
        if not approval:
            return {"error": "Approval request not found"}
        approval["status"] = "rejected"
        approval["approved_by"] = approver
        approval["approved_at"] = datetime.now(UTC).isoformat()
        approval["reason"] = reason
        return approval

    def request_approval(self, request_id: str, requestor: str, summary: str) -> dict[str, Any]:
        self._approvals[request_id] = {
            "request_id": request_id,
            "requestor": requestor,
            "summary": summary,
            "status": "pending",
            "created_at": datetime.now(UTC).isoformat(),
        }
        return self._approvals[request_id]


class InMemoryAuditStore(AuditStore):
    """Non-persistent audit store for local development and unit tests."""

    def __init__(self) -> None:
        self._records: list[dict[str, Any]] = []

    def write(self, record: dict[str, Any]) -> None:
        self._records.append(record)


class InMemorySecretStore(SecretStore):
    """Non-persistent secret store for local development and unit tests."""

    def __init__(self, secrets: dict[str, str] | None = None) -> None:
        self._secrets = secrets or {}

    def get_secret(self, name: str) -> str:
        if name not in self._secrets:
            raise KeyError(f"Secret not found: {name}")
        return self._secrets[name]
