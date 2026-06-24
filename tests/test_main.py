from fastapi.testclient import TestClient

from main import app

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
