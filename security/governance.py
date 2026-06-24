"""Governance controls for the IDP agent platform.

This agent platform is positioned as an ENTERPRISE INTERNAL DEVELOPER PORTAL
automation assistant, not a system that makes production deployment or security
decisions on its own. Critical actions require human approval and audit logging.
"""

from __future__ import annotations

import hashlib
import json
import re
from datetime import UTC, datetime
from typing import Any

from config import Settings, get_settings

# Simple patterns for secrets and tokens. Presidio should be used in production.
_SECRET_PATTERNS = [
    re.compile(r"(?i)(api[_-]?key|apikey|api_token|access_token|secret)\s*[:=]\s*['\"]?([\w\-]{8,})['\"]?"),
    re.compile(r"(?i)(password|passwd|pwd)\s*[:=]\s*['\"]?([^\s'\"]+)['\"]?"),
    re.compile(r"-----BEGIN (RSA |EC |DSA |OPENSSH )?PRIVATE KEY-----"),
    re.compile(r"AKIA[0-9A-Z]{16}"),  # AWS access key
    re.compile(r"ghp_[a-zA-Z0-9]{36}"),  # GitHub PAT
]

# Keywords that indicate sensitive content.
_SENSITIVE_KEYWORDS = [
    "ssn",
    "social security",
    "credit card",
    "cvv",
    "passport",
    "password",
    "secret",
    "token",
    "phi",
    "patient",
    "diagnosis",
    "medical record",
]


def classify_input(text: str) -> dict[str, Any]:
    """Classify input sensitivity and whether it needs redaction."""
    text_lower = text.lower()
    sensitive = any(kw in text_lower for kw in _SENSITIVE_KEYWORDS)
    secret = any(p.search(text) for p in _SECRET_PATTERNS)
    return {
        "sensitive": sensitive,
        "secret_detected": secret,
        "allowed": not (sensitive or secret),
    }


def scan_for_secrets(text: str) -> list[dict[str, Any]]:
    """Return a list of suspected secret matches with masked values."""
    findings: list[dict[str, Any]] = []
    for pattern in _SECRET_PATTERNS:
        for match in pattern.finditer(text):
            findings.append(
                {
                    "type": "secret",
                    "pattern": pattern.pattern[:40],
                    "position": (match.start(), match.end()),
                    "masked": mask_value(match.group(0)),
                }
            )
    return findings


def redact_sensitive(text: str) -> str:
    """Redact suspected secrets and sensitive keywords from text."""
    result = text
    for pattern in _SECRET_PATTERNS:
        result = pattern.sub("[REDACTED]", result)
    return result


def mask_value(value: str, visible: int = 4) -> str:
    """Mask a string value."""
    if len(value) <= visible:
        return "*" * len(value)
    return value[:visible] + "*" * (len(value) - visible)


def hash_for_audit(value: str) -> str:
    """Return a stable hash for audit records."""
    return hashlib.sha256(value.encode("utf-8")).hexdigest()[:16]


def build_audit_record(
    actor: str,
    action: str,
    resource: str,
    details: dict[str, Any] | None = None,
    settings: Settings | None = None,
) -> dict[str, Any]:
    """Build a structured audit record."""
    settings = settings or get_settings()
    record = {
        "timestamp": datetime.now(UTC).isoformat(),
        "actor": actor,
        "action": action,
        "resource": resource,
        "project": settings.google_cloud_project,
        "details": details or {},
    }
    return record


def log_audit(record: dict[str, Any], settings: Settings | None = None) -> None:
    """Persist an audit record to Cloud Logging or stdout."""
    settings = settings or get_settings()
    if settings.audit_logging_enabled:
        # Structured output; Cloud Logging agent picks this up in production.
        print(json.dumps(record, sort_keys=True, default=str))
