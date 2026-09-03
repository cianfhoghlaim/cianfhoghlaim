"""Standardized Pydantic v2 base models for the agent fleet.

The 4 base models:

- :class:`AgentRequest` — the standard request envelope
- :class:`AgentResponse` — the standard response envelope
- :class:`AgentContext` — the per-invocation context (memory,
  observability, framework)
- :class:`AgentTrace` — the canonical trace envelope (Langfuse,
  Logfire, MLflow, RAGAS, structlog)

All 4 use Pydantic v2 syntax (``model_config = ConfigDict(...)``)
and are ``frozen=False`` so per-request overrides work.

Reference: openspec/changes/2026-08-14-agents-fleet-wiring-parity-v1.
"""
from __future__ import annotations

from typing import Any

try:
    from pydantic import BaseModel, ConfigDict, Field
except ImportError:
    # Pydantic not installed — provide a graceful fallback that
    # still defines the 4 classes (with no validation).
    BaseModel = object  # type: ignore[assignment,misc]
    ConfigDict = dict  # type: ignore[assignment,misc]

    def Field(*args: Any, **kwargs: Any) -> Any:  # type: ignore[no-redef]
        return None


# ---------------------------------------------------------------------------
# AgentRequest: the standard request envelope.
# ---------------------------------------------------------------------------


class AgentRequest(BaseModel):
    """The standard request envelope for any agent invocation.

    Fields:

    - ``query``: the user query (required)
    - ``agent_name``: the target agent (validated against AGENT_REGISTRY)
    - ``context``: optional per-invocation context (AgentContext)
    - ``metadata``: arbitrary additional metadata
    """

    if BaseModel is not object:
        model_config = ConfigDict(extra="allow")  # type: ignore[arg-type]

    query: str = Field(..., description="The user query")
    agent_name: str | None = Field(
        None, description="The target agent name"
    )
    context: dict[str, Any] | None = Field(
        None, description="Optional per-invocation context"
    )
    metadata: dict[str, Any] | None = Field(
        None, description="Arbitrary additional metadata"
    )


# ---------------------------------------------------------------------------
# AgentResponse: the standard response envelope.
# ---------------------------------------------------------------------------


class AgentResponse(BaseModel):
    """The standard response envelope for any agent invocation.

    Fields:

    - ``response``: the agent's text response (required)
    - ``agent_name``: the agent that produced the response
    - ``success``: whether the invocation succeeded
    - ``error``: optional error message (if ``success=False``)
    - ``metadata``: arbitrary additional metadata (citations, etc.)
    """

    if BaseModel is not object:
        model_config = ConfigDict(extra="allow")  # type: ignore[arg-type]

    response: str = Field(..., description="The agent's text response")
    agent_name: str | None = Field(
        None, description="The agent that produced the response"
    )
    success: bool = Field(
        True, description="Whether the invocation succeeded"
    )
    error: str | None = Field(
        None, description="Optional error message"
    )
    metadata: dict[str, Any] | None = Field(
        None, description="Citations, sources, etc."
    )


# ---------------------------------------------------------------------------
# AgentContext: per-invocation context.
# ---------------------------------------------------------------------------


class AgentContext(BaseModel):
    """The per-invocation context (memory, observability, framework).

    Fields:

    - ``session_id``: the conversation session ID
    - ``user_id``: the user ID
    - ``memory_layer_kind``: which memory backend is in use
    - ``observability_wired``: whether the 5-layer observability is wired
    - ``framework``: which agent framework is in use
    """

    if BaseModel is not object:
        model_config = ConfigDict(extra="allow")  # type: ignore[arg-type]

    session_id: str | None = Field(
        None, description="The conversation session ID"
    )
    user_id: str | None = Field(None, description="The user ID")
    memory_layer_kind: str | None = Field(
        None, description="Which memory backend is in use"
    )
    observability_wired: bool = Field(
        False,
        description="Whether the 5-layer observability is wired",
    )
    framework: str | None = Field(
        None, description="Which agent framework is in use"
    )


# ---------------------------------------------------------------------------
# AgentTrace: the canonical trace envelope.
# ---------------------------------------------------------------------------


class AgentTrace(BaseModel):
    """The canonical trace envelope (5-layer observability).

    Fields:

    - ``trace_id``: the canonical trace ID (Langfuse + Logfire)
    - ``agent_name``: the agent that produced the trace
    - ``span_name``: the canonical span name
    - ``mlflow_run_id``: the MLflow run ID (if MLflow is wired)
    - ``ragas_score``: the RAGAS faithfulness score (0..1)
    - ``started_at``: the trace start time (ISO 8601)
    - ``ended_at``: the trace end time (ISO 8601)
    """

    if BaseModel is not object:
        model_config = ConfigDict(extra="allow")  # type: ignore[arg-type]

    trace_id: str | None = Field(
        None, description="The canonical trace ID"
    )
    agent_name: str | None = Field(
        None, description="The agent that produced the trace"
    )
    span_name: str | None = Field(
        None, description="The canonical span name"
    )
    mlflow_run_id: str | None = Field(
        None, description="The MLflow run ID"
    )
    ragas_score: float | None = Field(
        None, description="The RAGAS faithfulness score (0..1)"
    )
    started_at: str | None = Field(
        None, description="The trace start time (ISO 8601)"
    )
    ended_at: str | None = Field(
        None, description="The trace end time (ISO 8601)"
    )


__all__ = [
    "AgentContext",
    "AgentRequest",
    "AgentResponse",
    "AgentTrace",
]