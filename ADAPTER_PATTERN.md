# Adapter Pattern — Enterprise Integration Guide

The agent platform uses **adapters** to integrate with external enterprise systems. Adapters are the only place where vendor-specific SDKs and APIs are used. The control plane, agents, and tools depend only on abstract interfaces, making the platform portable across enterprises.

## Adapter types

| Adapter | Purpose | Built-in implementations |
|---|---|---|
| `Orchestrator` | Submit workflows/pipelines, check status, and manage approvals | `InMemoryOrchestrator`, `HarnessOrchestrator` |
| `SecretStore` | Fetch secrets and API keys at runtime | `InMemorySecretStore`, `VaultSecretStore`, `GoogleSecretManagerStore` |
| `AuditStore` | Persist structured audit records | `InMemoryAuditStore`, `CloudLoggingAuditStore` (via config) |

## Configuration

Adapters are selected via environment variables in `.env`:

```env
ADAPTER_ORCHESTRATOR=memory       # memory | harness
ADAPTER_SECRET_STORE=memory       # memory | vault | gsm
ADAPTER_AUDIT_STORE=memory        # memory | cloud_logging
```

The factory in `adapters/factory.py` resolves the configured adapter at runtime.

## Adding a new orchestrator adapter

Create a file `adapters/my_orchestrator.py`:

```python
from typing import Any
from .base import Orchestrator

class MyOrchestrator(Orchestrator):
    def submit(self, workflow_id: str, inputset: dict[str, Any]) -> dict[str, Any]:
        # Call the orchestrator API to start a workflow/pipeline
        return {"execution_id": "...", "status": "submitted"}

    def status(self, execution_id: str) -> dict[str, Any]:
        # Poll the orchestrator API for status
        return {"status": "running"}

    def approve(self, request_id: str, approver: str) -> dict[str, Any]:
        # Approve a pending human-in-the-loop request
        return {"request_id": request_id, "status": "approved"}

    def reject(self, request_id: str, approver: str, reason: str) -> dict[str, Any]:
        return {"request_id": request_id, "status": "rejected", "reason": reason}

    def request_approval(self, request_id: str, requestor: str, summary: str) -> dict[str, Any]:
        # Create an approval request in the orchestrator or external system
        return {"request_id": request_id, "status": "pending"}
```

Register it in `adapters/factory.py`:

```python
from .my_orchestrator import MyOrchestrator

def _get_orchestrator(settings: Settings) -> Orchestrator:
    backend = (settings.adapter_orchestrator or "memory").lower()
    if backend == "my_orchestrator":
        return MyOrchestrator(...)
    ...
```

No agent or tool code needs to change.

## Adding a new secret store adapter

Create a file `adapters/my_secret_store.py`:

```python
from .base import SecretStore

class MySecretStore(SecretStore):
    def get_secret(self, name: str) -> str:
        # Fetch secret from the enterprise backend
        return "..."
```

Register it in `adapters/factory.py` and add the new value to `adapter_secret_store` in `config.py`.

## Adding a new audit store adapter

Create a file `adapters/my_audit_store.py`:

```python
from typing import Any
from .base import AuditStore

class MyAuditStore(AuditStore):
    def write(self, record: dict[str, Any]) -> None:
        # Send record to SIEM, log aggregator, or compliance store
        pass
```

Register it in `adapters/factory.py` and add the new value to `adapter_audit_store` in `config.py`.

## Best practices

- **Keep vendor logic inside adapters.** No SDK imports should appear in `agents/`, `tools/`, or `main.py`.
- **Return plain dicts.** Adapters should return simple Python structures so agents and tools stay vendor-agnostic.
- **Fail safely.** If an adapter raises, tools should return a clear error and emit an audit record.
- **Do not cache secrets.** Always fetch secrets from the backend at runtime.
- **Log adapter calls.** Use the audit store to record submissions, approvals, and secret access.

## Testing adapters

The built-in `InMemoryOrchestrator`, `InMemorySecretStore`, and `InMemoryAuditStore` let you run the full platform locally without external credentials. Unit tests can inject these adapters directly or rely on the default configuration.

## Author

Rohid Dev · github.com/rohiddev
