"""Base agent abstraction for the IDP platform."""

from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass, field
from typing import Any

from config import Settings, get_settings
from observability.telemetry import trace_span
from security.governance import classify_input, redact_sensitive


@dataclass
class AgentResponse:
    agent: str
    answer: str
    data: dict[str, Any] = field(default_factory=dict)
    routed_to: str | None = None


class Agent:
    """Lightweight agent with instructions, optional tools, and governance."""

    def __init__(
        self,
        name: str,
        model: str,
        instructions: str,
        tools: dict[str, Callable[..., Any]] | None = None,
        settings: Settings | None = None,
    ):
        self.name = name
        self.model = model
        self.instructions = instructions
        self.tools = tools or {}
        self.settings = settings or get_settings()

    def run(self, user_input: str, context: dict[str, Any] | None = None) -> AgentResponse:
        with trace_span("agent.run", agent=self.name):
            classification = classify_input(user_input)
            if not classification["allowed"]:
                safe_input = redact_sensitive(user_input)
                return AgentResponse(
                    agent=self.name,
                    answer=(
                        "This request contains sensitive or secret-like content. "
                        "Please remove secrets, tokens, or personal data before retrying."
                    ),
                    data={"classification": classification, "redacted_input": safe_input},
                )
            safe_input = redact_sensitive(user_input)
            return self._execute(safe_input, context or {})

    def _execute(self, user_input: str, context: dict[str, Any]) -> AgentResponse:
        # Subclasses override this. Default returns a plain response.
        return AgentResponse(agent=self.name, answer=f"Agent {self.name} received: {user_input}")

    def call_tool(self, tool_name: str, **kwargs: Any) -> Any:
        if tool_name not in self.tools:
            raise ValueError(f"Tool {tool_name} not available on agent {self.name}")
        return self.tools[tool_name](**kwargs)
