"""Abstract adapter interfaces for enterprise integration points."""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import Any


class SecretStore(ABC):
    """Abstract secrets backend. Implement for Vault, GSM, AWS SM, Azure Key Vault, etc."""

    @abstractmethod
    def get_secret(self, name: str) -> str:
        """Return the secret value for the given name or path."""


class Orchestrator(ABC):
    """Abstract workflow/pipeline orchestrator.

    Implement for Harness IDP, GitHub Actions, GitLab CI, Azure DevOps, Argo, Tekton, etc.
    """

    @abstractmethod
    def submit(self, workflow_id: str, inputset: dict[str, Any]) -> dict[str, Any]:
        """Submit a workflow/pipeline execution and return an execution handle."""

    @abstractmethod
    def status(self, execution_id: str) -> dict[str, Any]:
        """Return the current execution status."""

    @abstractmethod
    def approve(self, request_id: str, approver: str) -> dict[str, Any]:
        """Approve a pending human-in-the-loop request."""

    @abstractmethod
    def reject(self, request_id: str, approver: str, reason: str) -> dict[str, Any]:
        """Reject a pending human-in-the-loop request."""

    @abstractmethod
    def request_approval(
        self, request_id: str, requestor: str, summary: str
    ) -> dict[str, Any]:
        """Create a new human-in-the-loop approval request."""


class AuditStore(ABC):
    """Abstract audit backend. Implement for Cloud Logging, Datadog, Splunk, SIEM, etc."""

    @abstractmethod
    def write(self, record: dict[str, Any]) -> None:
        """Persist a structured audit record."""
