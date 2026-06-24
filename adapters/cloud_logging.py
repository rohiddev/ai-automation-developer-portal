"""Google Cloud Logging audit store adapter."""

from __future__ import annotations

import json
from typing import Any

from google.cloud import logging as cloud_logging

from .base import AuditStore


class CloudLoggingAuditStore(AuditStore):
    """Write audit records to Google Cloud Logging."""

    def __init__(self, logger_name: str = "idp-agent-platform-audit") -> None:
        self._logger_name = logger_name
        try:
            self._client = cloud_logging.Client()
            self._logger = self._client.logger(logger_name)
        except Exception:
            self._client = None
            self._logger = None

    def write(self, record: dict[str, Any]) -> None:
        if self._logger:
            self._logger.log_struct(record)
        else:
            print(json.dumps(record, sort_keys=True, default=str))
