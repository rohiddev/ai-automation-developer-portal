# Enterprise IDP Automation Agent Platform

An enterprise-grade, multi-agent self-service automation platform for Internal Developer Portals (IDP). Built with Google ADK and Gemini Enterprise Agent Platform patterns, it helps developers discover workflows, generate orchestrator YAML, request approvals, and track execution — with built-in governance, audit, and observability.

The platform is **orchestrator-agnostic**: it works with Harness IDP, GitHub Actions, GitLab CI, Azure DevOps, Argo, Tekton, or any custom workflow engine by swapping adapters.

**Author:** Rohid Dev · github.com/rohiddev

---

## What it does

- **Self-service discovery:** Developers describe what they need, and the agent recommends the right workflow.
- **Workflow generation:** Produces IDP Workflow YAML (Harness IDP 2.0 reference) with parameters and pipeline triggers.
- **Pipeline generation:** Produces orchestrator pipeline YAML with API steps, retry logic, and optional human approvals.
- **Approval management:** Creates and tracks human-in-the-loop approvals before provisioning runs.
- **Execution tracking:** Submits and polls workflow/pipeline executions through a pluggable orchestrator adapter.
- **Governance:** Secret detection, input classification, audit logging, and redaction before any model call or tool execution.
- **Observability:** Structured logs and distributed tracing.

## Architecture

```
Developer UI / Chat / API
        |
        v
API Gateway + Auth
        |
        v
FastAPI Control Plane (/ask /audit /execute /health)
        |
        v
RouterAgent (intent classification)
        |
        +---> IDPAssistantAgent (self-service Q&A)
        +---> WorkflowAgent (Workflow YAML)
        +---> PipelineAgent (Pipeline YAML)
        +---> ApprovalAgent (human approval)
        +---> ExecutionAgent (submit / monitor)
        +---> AuditAgent (governance scan)
        |
        v
Tools Layer + Adapter Plane
        |
        +---> Orchestrator Adapter (Harness, GitHub Actions, GitLab CI, Azure DevOps, etc.)
        +---> Secret Store Adapter (Vault, GSM, AWS SM, Azure Key Vault)
        +---> Audit Store Adapter (Cloud Logging, Datadog, Splunk)
        +---> Knowledge Retrieval (Vertex AI Search, internal corpus)
```

See [ARCHITECTURE.md](ARCHITECTURE.md) for the full enterprise design and [ARCHITECTURE_DEFENSE.md](ARCHITECTURE_DEFENSE.md) for the rationale and responses to common objections.

## Project structure

```
ai-automation-developer-portal/
├── adapters/            Pluggable orchestrator, secret, and audit adapters
├── agents/              Specialist agents
├── tools/               IDP, workflow, pipeline, approval, execution tools
├── security/            IAM, governance, audit logging
├── retrieval/           Knowledge/template retrieval backend
├── observability/       Structured logging and tracing
├── data/templates/      Sample Workflow and Pipeline YAML templates
├── pipeline-processing/ Architecture options for pipeline processing backends
├── scripts/             Smoke tests and helper scripts
├── tests/               Unit tests
├── main.py              FastAPI app
├── config.py            Pydantic settings
├── README.md
├── ARCHITECTURE.md
├── ARCHITECTURE_DEFENSE.md
├── GOVERNANCE.md
├── PITCH.md
├── USE_CASES.md
└── ADAPTER_PATTERN.md
```

## Quick start

1. Install dependencies:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

2. Copy `.env.example` to `.env`. The default settings use in-memory adapters, so no external systems are required.

3. Run the app:

```bash
uvicorn main:app --reload
```

4. Test:

```bash
curl -X POST http://localhost:8000/ask \
  -H "Content-Type: application/json" \
  -d '{"message": "I need a K8s namespace for application SYSID-12345", "actor": "dev1"}'
```

## API endpoints

All endpoints work with the default in-memory adapters, so the platform is fully functional via API without any external orchestrator.

| Method | Path | Description |
|---|---|---|
| GET | `/health` | Health check |
| POST | `/ask` | Natural-language request; router picks the right specialist |
| POST | `/generate/workflow` | Generate IDP Workflow YAML |
| POST | `/generate/pipeline` | Generate orchestrator Pipeline YAML |
| POST | `/execute` | Submit a workflow/pipeline execution |
| POST | `/status` | Check execution status |
| POST | `/approval/request` | Create a human approval request |
| POST | `/approval/approve` | Approve a request |
| POST | `/approval/reject` | Reject a request |
| POST | `/audit` | Run a governance/secret scan |

Run the smoke test against a local server to verify every endpoint works without Harness:

```bash
uvicorn main:app --reload &
python scripts/test_api.py
```

## Configure production adapters

Set in `.env`:

```env
ADAPTER_ORCHESTRATOR=harness
ADAPTER_SECRET_STORE=vault
ADAPTER_AUDIT_STORE=cloud_logging

HARNESS_ACCOUNT_IDENTIFIER=...
HARNESS_PROJECT_IDENTIFIER=...
VAULT_ADDR=https://vault.yourcompany.com
```

See [ADAPTER_PATTERN.md](ADAPTER_PATTERN.md) for how to add custom adapters.

## Governance

See [GOVERNANCE.md](GOVERNANCE.md) for the full security, audit, and responsible-automation controls.

## Deployment

Deploy to Cloud Run or GKE with Workload Identity. Use the `SecretStore` adapter for secrets. Configure the `AuditStore` adapter for SIEM ingestion. Integrate with Gemini Enterprise Agent Platform for enterprise model governance and deployment.

## License

MIT
