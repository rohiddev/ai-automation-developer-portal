"""End-to-end API smoke test using only in-memory adapters (no Harness required)."""

from __future__ import annotations

import sys

import httpx

BASE_URL = "http://localhost:8000"


def main() -> int:
    client = httpx.Client(base_url=BASE_URL, timeout=30.0)

    # Health check
    r = client.get("/health")
    assert r.status_code == 200, r.text
    print("✓ /health")

    # Natural-language ask
    r = client.post("/ask", json={"message": "I need a K8s namespace", "actor": "dev1"})
    assert r.status_code == 200, r.text
    print("✓ /ask")

    # Generate workflow YAML
    r = client.post(
        "/generate/workflow",
        json={
            "identifier": "k8s_namespace_workflow",
            "name": "K8s Namespace Workflow",
            "parameters": [{"title": "App", "properties": {"sysid": {"type": "string"}}}],
            "pipeline_identifier": "k8s_namespace_pipeline",
        },
    )
    assert r.status_code == 200, r.text
    print("✓ /generate/workflow")

    # Generate pipeline YAML
    r = client.post(
        "/generate/pipeline",
        json={
            "identifier": "k8s_namespace_pipeline",
            "name": "K8s Namespace Pipeline",
            "requires_approval": True,
        },
    )
    assert r.status_code == 200, r.text
    print("✓ /generate/pipeline")

    # Submit execution
    r = client.post(
        "/execute",
        json={
            "pipeline_identifier": "k8s_namespace_pipeline",
            "inputset": {"sysid": "SYSID-12345"},
        },
    )
    assert r.status_code == 200, r.text
    execution_id = r.json()["data"]["execution"]["execution_id"]
    print(f"✓ /execute -> {execution_id}")

    # Check status
    r = client.post("/status", json={"execution_id": execution_id})
    assert r.status_code == 200, r.text
    print("✓ /status")

    # Request approval
    r = client.post(
        "/approval/request",
        json={"request_id": "req-123", "requestor": "dev1", "summary": "Approve K8s namespace"},
    )
    assert r.status_code == 200, r.text
    print("✓ /approval/request")

    # Approve
    r = client.post("/approval/approve", json={"request_id": "req-123", "approver": "manager1"})
    assert r.status_code == 200, r.text
    print("✓ /approval/approve")

    # Audit scan
    r = client.post("/audit", json={"message": "test request", "actor": "dev1"})
    assert r.status_code == 200, r.text
    print("✓ /audit")

    print("\nAll API endpoints work without an external orchestrator.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
