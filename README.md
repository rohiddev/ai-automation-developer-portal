# IDP Automation Agent Platform

An enterprise multi-agent platform for Internal Developer Portal (IDP) self-service automation. Built with Google ADK and Gemini Enterprise Agent Platform patterns, it helps developers discover workflows, generate Harness IDP Workflow and Pipeline YAML, request approvals, and track execution with built-in governance, audit, and observability.

**Author:** Rohid Dev · github.com/rohiddev

---

## What it does

- **Self-service discovery:** Developers describe what they need, and the agent recommends the right IDP workflow.
- **Workflow generation:** Produces `Workflow` YAML for Harness IDP 2.0 with proper parameters and pipeline triggers.
- **Pipeline generation:** Produces `Custom` stage Harness pipeline YAML with Http steps, delegate selectors, retry logic, and optional manager approvals.
- **Approval management:** Creates and tracks manager approval requests before provisioning runs.
- **Execution tracking:** Submits and polls Harness pipeline executions.
- **Governance:** Secret detection, input classification, audit logging, and redaction before any model call or tool execution.
- **Observability:** Structured logs and Cloud Trace integration.

## Architecture

```
Developer UI / Chat
        |
        v
FastAPI /ask endpoint
        |
        v
RouterAgent (intent classification)
        |
        +---> IDPAssistantAgent (self-service Q&A)
        +---> WorkflowAgent (Workflow YAML)
        +---> PipelineAgent (Pipeline YAML)
        +---> ApprovalAgent (manager approval)
        +---> ExecutionAgent (submit / monitor)
        +---> AuditAgent (governance scan)
```

## Project structure

```
ai-automation-developer-portal/
├── agents/              Specialist agents
├── tools/               IDP, workflow, pipeline, approval, execution tools
├── security/            IAM, governance, audit logging
├── retrieval/           Knowledge/template retrieval backend
├── observability/       Cloud Logging and Trace
├── data/templates/      Sample Workflow and Pipeline YAML templates
├── tests/               Unit tests
├── main.py              FastAPI app
├── config.py            Pydantic settings
└── README.md
```

## Quick start

1. Install dependencies:

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

2. Copy `.env.example` to `.env` and fill in your GCP project, Harness identifiers, and secret backend.

3. Run the app:

```bash
uvicorn main:app --reload
```

4. Test:

```bash
curl -X POST http://localhost:8000/ask \
  -H "Content-Type: application/json" \
  -d '{"message": "I need a K8s namespace for SYSID-12345", "actor": "dev1"}'
```

## Governance

See [GOVERNANCE.md](GOVERNANCE.md) for the full security, audit, and responsible-automation controls.

## Deployment

Deploy to Cloud Run or GKE with Workload Identity. Use HashiCorp Vault for all secrets. Configure Cloud Logging and Cloud Trace for observability. Integrate with Gemini Enterprise Agent Platform for enterprise-scale deployment and model governance.

## License

MIT
