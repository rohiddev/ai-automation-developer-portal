from main import app
from fastapi.testclient import TestClient

client = TestClient(app)


def test_health():
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "ok"


def test_ask_routes():
    response = client.post("/ask", json={"message": "I need a K8s namespace", "actor": "dev1"})
    assert response.status_code == 200
    data = response.json()
    assert "agent" in data
    assert "answer" in data


def test_ask_with_secret():
    response = client.post("/ask", json={"message": "My password is secret123", "actor": "dev1"})
    assert response.status_code == 200
    data = response.json()
    assert "REDACTED" in data["answer"] or "sensitive" in data["answer"].lower()


def test_generate_workflow():
    response = client.post(
        "/generate/workflow",
        json={
            "identifier": "k8s_namespace_workflow",
            "name": "K8s Namespace Workflow",
            "parameters": [
                {"title": "App", "properties": {"sysid": {"type": "string"}}}
            ],
            "pipeline_identifier": "k8s_pipeline",
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert "yaml" in data["data"]
    assert "apiVersion: harness.io/v1" in data["data"]["yaml"]


def test_generate_pipeline():
    response = client.post(
        "/generate/pipeline",
        json={
            "identifier": "k8s_namespace_pipeline",
            "name": "K8s Namespace Pipeline",
            "requires_approval": True,
        },
    )
    assert response.status_code == 200
    data = response.json()
    assert "yaml" in data["data"]
    assert "HarnessApproval" in data["data"]["yaml"]


def test_execute_and_status():
    response = client.post(
        "/execute",
        json={"pipeline_identifier": "my_pipeline", "inputset": {"sysid": "SYSID-12345"}},
    )
    assert response.status_code == 200
    data = response.json()
    execution_id = data["data"]["execution"]["execution_id"]

    response = client.post("/status", json={"execution_id": execution_id})
    assert response.status_code == 200
    data = response.json()
    assert data["data"]["execution"]["execution_id"] == execution_id


def test_approval_request_and_approve():
    response = client.post(
        "/approval/request",
        json={"request_id": "req-123", "requestor": "dev1", "summary": "Please approve"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["data"]["approval"]["status"] == "pending"

    response = client.post(
        "/approval/approve",
        json={"request_id": "req-123", "approver": "manager1"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["data"]["approval"]["status"] == "approved"


def test_approval_reject():
    client.post(
        "/approval/request",
        json={"request_id": "req-456", "requestor": "dev1", "summary": "Please approve"},
    )
    response = client.post(
        "/approval/reject",
        json={"request_id": "req-456", "approver": "manager1", "reason": "Not ready"},
    )
    assert response.status_code == 200
    data = response.json()
    assert data["data"]["approval"]["status"] == "rejected"
