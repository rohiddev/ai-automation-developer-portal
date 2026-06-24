"""Pluggable adapters for enterprise integration points.

This package abstracts the external systems the agent platform talks to:
- Orchestrator: any workflow/pipeline engine (Harness, GitHub Actions, GitLab CI, Azure DevOps)
- SecretStore: any secrets backend (HashiCorp Vault, Google Secret Manager, AWS Secrets Manager)
- AuditStore: any audit/observability backend (Cloud Logging, Datadog, Splunk)

The default implementations are in-memory for local development. Production deployments
swap them by setting ADAPTER_ORCHESTRATOR, ADAPTER_SECRET_STORE, and ADAPTER_AUDIT_STORE.
"""

from .base import AuditStore, Orchestrator, SecretStore
from .cloud_logging import CloudLoggingAuditStore
from .factory import get_adapters
from .harness import HarnessOrchestrator
from .memory import InMemoryAuditStore, InMemoryOrchestrator, InMemorySecretStore
from .vault import VaultSecretStore

__all__ = [
    "AuditStore",
    "CloudLoggingAuditStore",
    "Orchestrator",
    "SecretStore",
    "get_adapters",
    "HarnessOrchestrator",
    "InMemoryAuditStore",
    "InMemoryOrchestrator",
    "InMemorySecretStore",
    "VaultSecretStore",
]
