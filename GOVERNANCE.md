# Governance and Responsible Automation — IDP Agent Platform

This document describes the governance, security, and responsible automation controls built into the IDP Automation Agent Platform.

## 1. Scope and positioning

This platform is an **enterprise Internal Developer Portal automation assistant**. It helps developers discover self-service workflows, generate YAML, request approvals, and track execution. It does **not** make production deployment, security, or infrastructure decisions on its own. All critical provisioning actions require human approval and are executed by the configured orchestrator (e.g., Harness, GitHub Actions, GitLab CI, Azure DevOps), not the agent directly.

## 2. Governance pillars

### 2.1 Input safety

Every user request is scanned before processing:
- Secret-like patterns (API keys, passwords, private keys, tokens)
- Sensitive keywords (SSN, PHI, credit card, passport, etc.)
- If detected, the request is rejected or redacted before any model call or tool execution.

### 2.2 Redaction

Suspected secrets and sensitive values are replaced with `[REDACTED]` in:
- Model prompts
- Tool inputs
- Logs and audit records
- API responses

### 2.3 Audit logging

Every agent action emits a structured record containing:
- Timestamp (UTC)
- Actor identifier
- Action name
- Resource identifier
- Project/environment
- Relevant details (with secrets redacted)

Records are written to Cloud Logging or stdout in JSON format for ingestion by SIEM tools.

### 2.4 Approval gates

Self-service actions that create or modify production resources require manager approval:
- `HarnessApproval` step with `disallowPipelineExecutor: true`
- Minimum one approver from a designated user group
- 24-hour timeout before auto-rejection
- Approval status is recorded in the audit log

### 2.5 Secret management

All secrets are retrieved from HashiCorp Vault or Google Secret Manager at runtime. No secrets are committed to the repository, stored in environment variables as plain text, or embedded in generated YAML.

### 2.6 Least privilege

The service runs with Workload Identity or a dedicated service account. It has only the permissions needed to read secrets, write logs, and submit orchestrator requests through the configured adapter. It cannot directly create cloud resources, modify production systems, or bypass approval gates.

## 3. Responsible automation principles

- **Human-in-the-loop:** Critical actions stop for human approval.
- **Transparency:** Every recommendation explains which workflow, pipeline, and approval gate apply.
- **Reversibility:** Orchestrator executions can be re-run or rolled back from the failed stage when the orchestrator supports it.
- **Observability:** All actions are traceable from the chat request through to execution completion.
- **Non-discrimination:** Recommendations are based on the request description, not the requestor's identity.

## 4. Compliance alignment

This platform is designed to support enterprise expectations for:
- Auditability and traceability
- Secret management and access control
- Change management and approval workflows
- Security scanning and input validation

## 5. Incident response

If a secret is accidentally submitted:
1. The agent detects and redacts it immediately.
2. The request is rejected with guidance to rotate the exposed credential.
3. A high-priority audit record is emitted.
4. The security team is notified through existing alerting channels.

## Author

Rohid Dev · github.com/rohiddev
