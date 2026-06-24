"""Factory for resolving configured adapters."""

from __future__ import annotations

from typing import Any

from google.cloud import secretmanager

from config import Settings, get_settings

from .base import AuditStore, Orchestrator, SecretStore
from .cloud_logging import CloudLoggingAuditStore
from .harness import HarnessOrchestrator
from .memory import InMemoryAuditStore, InMemoryOrchestrator, InMemorySecretStore
from .vault import VaultSecretStore


class GoogleSecretManagerStore(SecretStore):
    """Adapter for Google Secret Manager."""

    def __init__(self, project: str | None = None) -> None:
        self._client = secretmanager.SecretManagerServiceClient()
        self._project = project

    def get_secret(self, name: str) -> str:
        if name.startswith("projects/"):
            path = name
        elif self._project:
            path = f"projects/{self._project}/secrets/{name}/versions/latest"
        else:
            raise ValueError("Secret name must be a full resource path or project must be set")
        response = self._client.access_secret_version(request={"name": path})
        return response.payload.data.decode("utf-8")


def _get_secret_store(settings: Settings) -> SecretStore:
    backend = (settings.adapter_secret_store or "memory").lower()
    if backend == "vault":
        return VaultSecretStore(addr=settings.vault_addr)
    if backend == "gsm":
        return GoogleSecretManagerStore(project=settings.google_cloud_project)
    return InMemorySecretStore()


def _get_orchestrator(settings: Settings) -> Orchestrator:
    backend = (settings.adapter_orchestrator or "memory").lower()
    if backend == "harness":
        return HarnessOrchestrator(secret_store=_get_secret_store(settings), settings=settings)
    return InMemoryOrchestrator()


def _get_audit_store(settings: Settings) -> AuditStore:
    backend = (settings.adapter_audit_store or "memory").lower()
    if backend in ("cloud_logging", "cloudlogging"):
        return CloudLoggingAuditStore()
    return InMemoryAuditStore()


def get_adapters(settings: Settings | None = None) -> dict[str, Any]:
    """Return the configured orchestrator, secret store, and audit store."""
    settings = settings or get_settings()
    return {
        "orchestrator": _get_orchestrator(settings),
        "secret_store": _get_secret_store(settings),
        "audit_store": _get_audit_store(settings),
    }
