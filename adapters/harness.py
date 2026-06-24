"""Harness IDP / Harness pipeline orchestrator adapter."""

from __future__ import annotations

from typing import Any

import httpx

from config import Settings, get_settings

from .base import Orchestrator, SecretStore


class HarnessOrchestrator(Orchestrator):
    """Production adapter for Harness IDP and Harness pipelines."""

    def __init__(
        self,
        secret_store: SecretStore,
        settings: Settings | None = None,
    ) -> None:
        self._secret_store = secret_store
        self._settings = settings or get_settings()

    def submit(self, workflow_id: str, inputset: dict[str, Any]) -> dict[str, Any]:
        account = self._settings.harness_account_identifier
        org = self._settings.harness_org_identifier
        project = self._settings.harness_project_identifier
        if not account or not project:
            raise RuntimeError("Harness account and project identifiers are required")
        url = (
            f"{self._settings.harness_idp_base_url}/gateway/pipeline/api/webhook/custom/"
            f"{workflow_id}/v3?accountIdentifier={account}&orgIdentifier={org}"
            f"&projectIdentifier={project}"
        )
        api_key = self._secret_store.get_secret("harness-api-key")
        response = httpx.post(
            url,
            headers={"Content-Type": "application/json", "X-Api-Key": api_key},
            json={"inputset": inputset},
            timeout=30.0,
        )
        response.raise_for_status()
        return response.json()

    def status(self, execution_id: str) -> dict[str, Any]:
        # Harness returns an apiUrl on submission; this adapter assumes callers store it.
        raise NotImplementedError(
            "Use the apiUrl returned by submit() with a Harness poll adapter."
        )

    def approve(self, request_id: str, approver: str) -> dict[str, Any]:
        # Harness approvals are modeled as HarnessApproval steps inside the pipeline.
        raise NotImplementedError(
            "Harness approvals are handled inside the pipeline via HarnessApproval steps."
        )

    def reject(self, request_id: str, approver: str, reason: str) -> dict[str, Any]:
        raise NotImplementedError(
            "Harness approvals are handled inside the pipeline via HarnessApproval steps."
        )

    def request_approval(
        self, request_id: str, requestor: str, summary: str
    ) -> dict[str, Any]:
        raise NotImplementedError(
            "Harness approvals are handled inside the pipeline via HarnessApproval steps."
        )
