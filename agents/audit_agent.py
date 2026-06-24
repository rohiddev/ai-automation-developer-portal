"""Agent that reports on governance and audit status."""

from __future__ import annotations

from typing import Any

from agents.base import Agent, AgentResponse
from security.governance import build_audit_record, log_audit, scan_for_secrets


class AuditAgent(Agent):
    """Performs governance checks and emits audit records."""

    def __init__(self, settings: Any | None = None) -> None:
        super().__init__(
            name="AuditAgent",
            model="gemini-2.0-flash",
            instructions=(
                "You are an Audit and Governance Agent. Scan developer inputs for secrets, "
                "classify sensitivity, and emit structured audit records. Do not execute "
                "provisioning actions."
            ),
            tools={
                "scan_for_secrets": scan_for_secrets,
                "build_audit_record": build_audit_record,
                "log_audit": log_audit,
            },
            settings=settings,
        )

    def _execute(self, user_input: str, context: dict[str, Any]) -> AgentResponse:
        findings = self.call_tool("scan_for_secrets", text=user_input)
        actor = context.get("actor", "developer")
        action = context.get("action", "governance_scan")
        resource = context.get("resource", "user_input")
        record = self.call_tool(
            "build_audit_record",
            actor=actor,
            action=action,
            resource=resource,
            details={"findings": findings, "input_length": len(user_input)},
        )
        self.call_tool("log_audit", record=record)
        if findings:
            answer = (
                f"Governance scan found {len(findings)} potential secret(s). "
                "Review required before proceeding."
            )
        else:
            answer = "Governance scan passed. No secrets or sensitive keywords detected."
        return AgentResponse(
            agent=self.name, answer=answer, data={"findings": findings, "audit": record}
        )
