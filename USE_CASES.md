# Use Cases — IDP Automation Agent Platform

## 1. K8s namespace onboarding

**Actor:** Developer
**Goal:** Request a new K8s namespace for an application.

**Flow:**
1. Developer asks, "I need a K8s namespace for SYSID-06435 on SHARED1."
2. RouterAgent routes to `IDPAssistantAgent`.
3. IDPAssistantAgent recommends the K8s Namespace Onboarding workflow.
4. Developer asks to generate the workflow.
5. WorkflowAgent produces validated `Workflow` YAML with SYS ID, App Key, Cluster, and Requestor fields.
6. PipelineAgent produces the underlying Harness pipeline with validation, AD group creation, GitHub teams, repo creation, Jenkins trigger, and Vault setup.
7. Manager approval is requested before provisioning.
8. ExecutionAgent submits the pipeline and reports status.

## 2. Git repository provisioning

**Actor:** Developer
**Goal:** Create a new GitHub repository with AD groups and teams.

**Flow:**
1. Developer asks, "Create a new repo for my payments service."
2. IDPAssistantAgent recommends the Repo Provisioning workflow.
3. WorkflowAgent generates a Workflow YAML with repo name, owner, and template fields.
4. PipelineAgent generates a pipeline with Http steps to GitHub, AD, and team APIs.
5. ApprovalAgent checks if manager approval is required.
6. ExecutionAgent submits and tracks the pipeline.

## 3. AD group user management

**Actor:** Developer or team lead
**Goal:** Add or remove users from an existing AD group.

**Flow:**
1. Developer asks, "Add user D108991 to the developer group for SYSID-06435."
2. RouterAgent routes to `IDPAssistantAgent` or `ExecutionAgent` depending on context.
3. AuditAgent scans the request for sensitive data.
4. ApprovalAgent creates a request for the group owner.
5. Once approved, ExecutionAgent submits the pipeline to update group membership.

## 4. Public cloud onboarding

**Actor:** Cloud architect or developer
**Goal:** Provision AWS or Azure infrastructure for a new application.

**Flow:**
1. Developer describes the infrastructure need.
2. IDPAssistantAgent recommends the Public Cloud Onboarding workflow.
3. WorkflowAgent builds a multi-page Workflow YAML matching the original form fields.
4. PipelineAgent builds a pipeline with Http steps to the infrastructure provisioning API.
5. ExecutionAgent tracks the long-running provisioning job with retry and polling.

## 5. Workflow and pipeline design assistance

**Actor:** Platform engineer
**Goal:** Build a new self-service workflow or pipeline.

**Flow:**
1. Platform engineer asks, "Build a workflow for Vault namespace onboarding."
2. WorkflowAgent generates the Workflow YAML.
3. PipelineAgent generates the corresponding pipeline YAML.
4. Both are validated for Harness-safe identifiers and step names.
5. The platform engineer reviews and commits the YAML to the IDP repository.

## 6. Approval and execution tracking

**Actor:** Developer or manager
**Goal:** Check status of a pending request.

**Flow:**
1. User asks, "What is the status of request REQ-12345?"
2. ApprovalAgent or ExecutionAgent returns the current status.
3. AuditAgent logs the status lookup.

## 7. Governance and audit inquiries

**Actor:** Security auditor or platform engineer
**Goal:** Review recent self-service activity.

**Flow:**
1. User asks, "Show me recent K8s namespace requests by dev1."
2. AuditAgent queries structured audit logs and returns a summary.
3. All sensitive data remains redacted in the response.

## Author

Rohid Dev · github.com/rohiddev
