from adapters import InMemoryOrchestrator, InMemorySecretStore
from adapters.factory import get_adapters
from config import Settings


def test_in_memory_orchestrator_submit():
    orch = InMemoryOrchestrator()
    result = orch.submit("my-workflow", {"key": "value"})
    assert result["execution_id"].startswith("exec-")
    assert result["status"] == "submitted"


def test_in_memory_orchestrator_status():
    orch = InMemoryOrchestrator()
    result = orch.submit("my-workflow", {})
    status = orch.status(result["execution_id"])
    assert status["execution_id"] == result["execution_id"]


def test_in_memory_orchestrator_approval():
    orch = InMemoryOrchestrator()
    orch.request_approval("req-1", "dev1", "Please approve")
    approved = orch.approve("req-1", "manager1")
    assert approved["status"] == "approved"


def test_in_memory_secret_store():
    store = InMemorySecretStore(secrets={"api-key": "secret123"})
    assert store.get_secret("api-key") == "secret123"


def test_factory_defaults():
    adapters = get_adapters(Settings(google_cloud_project="local-dev"))
    assert "orchestrator" in adapters
    assert "secret_store" in adapters
    assert "audit_store" in adapters
