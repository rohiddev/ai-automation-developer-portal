# Executive Pitch — IDP Automation Agent Platform

## One-sentence value proposition

Build a single, governed, agent-powered front door for developers to discover, request, and track internal platform self-service tasks through the Internal Developer Portal.

## The problem

Internal platform teams are buried in repetitive, ticket-driven work:

- **Fragmented workflows:** K8s onboarding, repo creation, AD group management, and cloud provisioning each live in separate forms and pipelines.
- **Slow delivery:** Developers wait hours or days for common requests that could be automated.
- **Inconsistent quality:** Hand-written YAML and manual pipeline configuration introduce errors and security gaps.
- **Weak governance:** Approvals, audit logs, and secret handling are inconsistent across teams.
- **Poor discoverability:** Developers do not know which workflow to use or how to fill it out correctly.

## The solution

An agent platform that sits in front of the existing IDP and workflow/pipeline infrastructure. It:

1. Understands the developer's request in natural language.
2. Recommends the right self-service workflow.
3. Generates validated Workflow and Pipeline YAML.
4. Enforces manager approval for critical actions.
5. Submits and tracks execution through the configured orchestrator adapter.
6. Logs every action for audit and compliance.

The platform is **orchestrator-agnostic**: it connects to Harness, GitHub Actions, GitLab CI, Azure DevOps, Argo, Tekton, or any custom orchestrator via pluggable adapters without changing the agent core.

## Why agents

- **Domain expertise:** Each agent specializes in one part of the process (routing, workflow design, pipeline design, approval, execution, audit).
- **Composable safety:** Governance is enforced at the input, agent, tool, and pipeline layers.
- **Scalable growth:** Adding a new self-service domain means adding one agent and a few tools, not rebuilding the entire platform.
- **Developer experience:** One conversational interface replaces many forms and wikis.

## Business outcomes

| Metric | Impact |
|---|---|
| Time to onboard a namespace | From hours to minutes |
| YAML errors in production | Reduced through automated validation |
| Self-service discoverability | Improved with natural-language search |
| Audit coverage | 100% of agent actions logged |
| Approval compliance | Enforced by 4-eyes approval gates |

## Technology stack

- **Google ADK** for multi-agent orchestration patterns
- **Gemini** for intent classification and YAML generation
- **Vertex AI** for retrieval and model serving
- **Pluggable orchestrator adapters** for self-service workflows and execution
- **Pluggable secret store adapters** for secrets (Vault, GSM, AWS SM, Azure Key Vault)
- **Pluggable audit adapters** for observability (Cloud Logging, Datadog, Splunk)

## Roadmap

| Priority | Item |
|---|---|
| 1 | Agent platform core with workflow and pipeline generation |
| 2 | Live orchestrator adapter integration for submission and polling |
| 3 | Vertex AI Search retrieval backend for policies and templates |
| 4 | Manager approval workflow with email and Slack notifications |
| 5 | Deploy to Cloud Run with Gemini Enterprise Agent Platform governance |
| 6 | Fine-grained RBAC and per-domain access control |

## Author

Rohid Dev · github.com/rohiddev
