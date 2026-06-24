"""Structured logging and distributed tracing."""

from __future__ import annotations

import logging
from collections.abc import Generator
from contextlib import contextmanager
from typing import Any

import structlog
from google.cloud import logging as cloud_logging
from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import ConsoleSpanExporter, SimpleSpanProcessor

from config import Settings, get_settings


def init_telemetry(settings: Settings | None = None) -> None:
    """Initialize structured logging and a trace provider."""
    settings = settings or get_settings()
    structlog.configure(
        processors=[
            structlog.processors.add_log_level,
            structlog.processors.TimeStamper(fmt="iso"),
            structlog.processors.JSONRenderer(),
        ],
        wrapper_class=structlog.make_filtering_bound_logger(
            logging.getLevelName(settings.log_level.upper())
        ),
        context_class=dict,
        logger_factory=structlog.PrintLoggerFactory(),
    )
    if settings.enable_cloud_logging:
        try:
            client = cloud_logging.Client()
            client.setup_logging()
        except Exception:
            pass
    if settings.enable_cloud_trace:
        try:
            provider = TracerProvider()
            exporter = ConsoleSpanExporter()
            provider.add_span_processor(SimpleSpanProcessor(exporter))
            trace.set_tracer_provider(provider)
        except Exception:
            pass


def log_structured(**kwargs: Any) -> None:
    """Emit a structured log entry."""
    logger = structlog.get_logger()
    logger.info(**{"event": "agent_event", **kwargs})


def get_tracer(name: str = "idp-agent-platform") -> trace.Tracer:
    return trace.get_tracer(name)


@contextmanager
def trace_span(name: str, **attributes: Any) -> Generator[None, None, None]:
    tracer = get_tracer()
    with tracer.start_as_current_span(name) as span:
        for key, value in attributes.items():
            span.set_attribute(key, value)
        yield
