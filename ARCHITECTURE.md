# Architecture — IDP Automation Agent Platform

## The problem

Developers need a single place to request internal platform resources: K8s namespaces, GitHub repos, AD groups, cloud environments, and more. Today these requests flow through a UI form, a `workflow.yaml` that calls an API, and a custom Harness pipeline that executes a sequence of API calls. The process is hard to discover, repetitive to build, and difficult to govern at scale.

## The solution

Replace the scattered manual flow with a single agent-powered front door. The agent platform understands the developer's intent, recommends the right workflow, generates the required YAML, manages approvals, and tracks execution — all with enterprise-grade audit, security, and observability.

## High-level flow

```
Developer request
        |
        v
FastAPI /ask
        |
        v
RouterAgent (classify intent)
        |
        v
Specialist Agent + Tools
        |
        v
Harness IDP Workflow / Pipeline
        |
        v
Backend APIs (AD, GitHub, Vault, Jenkins, K8s, cloud)
```

## Specialist agents

| Agent | Responsibility |
|---|---|
| RouterAgent | Classifies intent into domain and routes to the right specialist. |
| IDPAssistantAgent | Answers questions and recommends the correct self-service workflow. |
| WorkflowAgent | Generates and validates Harness IDP `Workflow` YAML. |
| PipelineAgent | Generates and validates Harness `Custom` stage pipeline YAML. |
| ApprovalAgent | Creates manager approval requests and reports status. |
| ExecutionAgent | Submits pipeline requests and polls execution status. |
| AuditAgent | Scans input for secrets, classifies sensitivity, and emits audit records. |

## Tools layer

Each tool is a plain Python function that can be called by an agent:

- `search_idp_knowledge` — retrieves policies, templates, and examples.
- `find_self_service_workflow` — maps a request to a known workflow.
- `generate_workflow_yaml` / `validate_workflow_yaml`
- `generate_pipeline_yaml` / `validate_pipeline_yaml`
- `request_manager_approval` / `check_approval_status`
- `submit_pipeline_request` / `get_execution_status`

## Governance layers

1. **Input classification** — every request is scanned for sensitive keywords and secret-like patterns before processing.
2. **Redaction** — suspected secrets are redacted before any model call or log entry.
3. **Audit logging** — every agent action emits a structured audit record with actor, action, resource, and timestamp.
4. **Approval gates** — critical provisioning actions require a manager approval with 4-eyes separation.
5. **Secrets via Vault** — no secrets are stored in code or GitHub; all API keys are fetched from HashiCorp Vault or Secret Manager.

## Observability

- **Structured logging** with `structlog` and JSON output.
- **Cloud Logging** integration when running in GCP.
- **Cloud Trace** distributed tracing for agent runs and tool calls.

## Key design decisions

### Why agents instead of a single monolithic flow?

Agents separate concerns: routing, workflow design, pipeline design, approvals, and execution each have different safety and expertise requirements. This makes it easier to add new domains, enforce governance per domain, and debug failures.

### Why generate YAML instead of calling Harness APIs directly?

IDP teams already review and version YAML. Generating YAML keeps the platform compatible with existing GitOps and approval workflows while reducing boilerplate and human error.

### Why a mock retrieval backend by default?

The mock backend lets teams run and test locally without a live Vertex AI Search corpus. Switching to `vertex-ai-search` is a configuration change in `.env`.

## Deployment targets

- Cloud Run for the FastAPI service
- GKE for long-running or high-throughput deployments
- Gemini Enterprise Agent Platform for enterprise model governance, evaluation, and deployment

## Author

Rohid Dev · github.com/rohiddev
