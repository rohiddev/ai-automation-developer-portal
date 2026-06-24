# Architecture — Enterprise IDP Automation Agent Platform

## Design goal

The platform is a **generic, enterprise-ready, multi-agent self-service automation layer** that sits in front of any Internal Developer Portal (IDP) or workflow orchestrator. It uses a conversational interface to help developers discover, request, and track internal services while enforcing governance, audit, and observability.

The architecture is intentionally **orchestrator-agnostic**: the same agent core can drive Harness IDP, GitHub Actions, GitLab CI, Azure DevOps, Argo Workflows, Tekton, or any custom orchestrator by swapping adapters.

---

## High-level architecture

```
                         ┌─────────────────────────────┐
                         │   Developer UI / Chat / API │
                         └──────────────┬──────────────┘
                                        │
                         ┌──────────────▼──────────────┐
                         │      API Gateway / WAF      │
                         │   AuthN (OIDC / SAML / SSO) │
                         └──────────────┬──────────────┘
                                        │
                         ┌──────────────▼──────────────┐
                         │     FastAPI Control Plane     │
                         │  /ask /audit /execute /health │
                         └──────────────┬──────────────┘
                                        │
                         ┌──────────────▼──────────────┐
                         │        Router Agent         │
                         │   (intent classification)   │
                         └──────────────┬──────────────┘
                                        │
          ┌──────────────┬──────────────┼──────────────┬──────────────┐
          │              │              │              │              │
          ▼              ▼              ▼              ▼              ▼
   ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐
   │  IDP QA  │  │ Workflow │  │ Pipeline │  │ Approval │  │ Execution│
   │  Agent   │  │  Agent   │  │  Agent   │  │  Agent   │  │  Agent   │
   └──────────┘  └──────────┘  └──────────┘  └──────────┘  └──────────┘
          │              │              │              │              │
          └──────────────┴──────────────┴──────────────┴──────────────┘
                                        │
                         ┌──────────────▼──────────────┐
                         │        Tools Layer          │
                         │  YAML generation, validation, │
                         │  approval, execution, search  │
                         └──────────────┬──────────────┘
                                        │
          ┌──────────────┬──────────────┼──────────────┬──────────────┐
          │              │              │              │              │
          ▼              ▼              ▼              ▼              ▼
   ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐  ┌──────────┐
   │Knowledge │  │Orchestrator│  │  Secret  │  │  Audit   │  │ Identity │
   │Retrieval │  │  Adapter  │  │  Store   │  │  Store   │  │ Provider │
   │ (RAG)   │  │           │  │ Adapter  │  │ Adapter  │  │          │
   └──────────┘  └──────────┘  └──────────┘  └──────────┘  └──────────┘
          │              │              │              │              │
          ▼              ▼              ▼              ▼              ▼
   Vertex AI   Harness /      Vault / GSM /   Cloud Logging/   Enterprise
   Search     GitHub Actions  AWS SM / Azure  Datadog / Splunk  IdP / LDAP
              GitLab CI      Key Vault
```

---

## Control plane vs. data plane

| Layer | Components | Responsibility |
|---|---|---|
| **Control plane** | FastAPI app, Router Agent, specialist agents | Receives requests, classifies intent, orchestrates agent reasoning, returns responses |
| **Tool plane** | `tools/` modules | Encapsulates business logic: YAML generation, validation, approval, execution, search |
| **Adapter plane** | `adapters/` modules | Abstracts every external system so the control plane stays portable |
| **Data plane** | Orchestrator, secret store, audit store, knowledge corpus | Stores state, executes workflows, holds secrets, records audit trails |

This separation lets enterprises swap vendors without rewriting agents or business logic.

---

## Agent responsibilities

| Agent | Responsibility |
|---|---|
| **RouterAgent** | Classifies intent into a domain and routes to the right specialist. |
| **IDPAssistantAgent** | Answers questions and recommends the correct self-service workflow. |
| **WorkflowAgent** | Generates and validates IDP `Workflow` YAML ( Harness IDP 2.0 by default, swappable). |
| **PipelineAgent** | Generates and validates orchestrator pipeline YAML. |
| **ApprovalAgent** | Creates and tracks human-in-the-loop approvals. |
| **ExecutionAgent** | Submits workflow/pipeline requests and polls execution status. |
| **AuditAgent** | Scans input for secrets, classifies sensitivity, and emits audit records. |

---

## Adapter pattern

Adapters turn vendor-specific APIs into plain Python interfaces. The control plane and tools only depend on the interfaces, never on the vendor SDKs directly.

```python
class Orchestrator(ABC):
    def submit(self, workflow_id: str, inputset: dict) -> dict: ...
    def status(self, execution_id: str) -> dict: ...
    def approve(self, request_id: str, approver: str) -> dict: ...
    def reject(self, request_id: str, approver: str, reason: str) -> dict: ...
    def request_approval(self, request_id: str, requestor: str, summary: str) -> dict: ...
```

Existing adapters:
- `InMemoryOrchestrator` — local development and unit tests
- `HarnessOrchestrator` — Harness IDP + Harness pipelines (reference implementation)
- `InMemorySecretStore` / `VaultSecretStore` / `GoogleSecretManagerStore`
- `InMemoryAuditStore` / `CloudLoggingAuditStore` (via configuration)

Adding a new orchestrator means implementing one adapter class; no agent or tool changes are required.

---

## Governance and security layers

1. **Input classification** — every request is scanned for sensitive keywords and secret-like patterns before processing.
2. **Redaction** — suspected secrets are redacted before model calls, tool execution, and log entries.
3. **Audit logging** — every agent action writes a structured record to the configured `AuditStore`.
4. **Approval gates** — critical provisioning actions require human approval with 4-eyes separation.
5. **Secrets via adapter** — no secrets are stored in code or Git; all API keys are fetched through the `SecretStore` adapter.
6. **Least-privilege identity** — the service runs with a dedicated identity (Workload Identity, IAM role, service account) and only the permissions needed to read secrets and submit workflows.

---

## Observability

- **Structured logging** with `structlog` and JSON output.
- **Distributed tracing** with OpenTelemetry.
- **Audit store** integration for SIEM ingestion.
- **Health endpoint** (`/health`) for load balancer and Kubernetes probes.

---

## Deployment patterns

The platform is designed to run in any enterprise Kubernetes or serverless environment:

- **Cloud Run** — stateless FastAPI service, scale-to-zero, Workload Identity
- **GKE / EKS / AKS** — for long-running, high-throughput, or multi-replica deployments
- **Agent Engine / Gemini Enterprise Agent Platform** — for enterprise model governance, evaluation, and deployment
- **Behind an API gateway** — for rate limiting, auth, and request transformation

---

## Key design decisions

### Why a control plane + adapter pattern?

Enterprises use different orchestrators, secret stores, and observability stacks. A direct integration with Harness (or any single vendor) would make the platform hard to adopt. Adapters isolate vendor specifics and let teams adopt the agent core incrementally.

### Why agents instead of a single monolithic flow?

Agents separate concerns: routing, workflow design, pipeline design, approvals, and execution each have different safety and expertise requirements. This makes it easier to add new domains, enforce governance per domain, and debug failures.

### Why generate declarative YAML instead of imperative API calls?

Declarative workflow/pipeline artifacts are reviewable, versionable, and fit existing GitOps and approval processes. The agent reduces boilerplate while preserving enterprise change-management discipline.

### Why default to in-memory adapters?

In-memory adapters let developers run and test the full stack locally without provisioning Vault, Harness, or Vertex AI. Switching to production backends is a configuration change.

---

## Enterprise adoption path

| Phase | Activity |
|---|---|
| 1 | Deploy locally with in-memory adapters; validate agents and tools |
| 2 | Connect knowledge retrieval (Vertex AI Search or internal corpus) |
| 3 | Implement the `Orchestrator` adapter for your IDP/pipeline engine |
| 4 | Connect the `SecretStore` adapter to Vault or cloud secret manager |
| 5 | Connect the `AuditStore` adapter to Cloud Logging / SIEM |
| 6 | Add enterprise auth (OIDC/SSO) at the API gateway |
| 7 | Production hardening: rate limiting, RBAC, model evaluation |

---

## Author

Rohid Dev · github.com/rohiddev
