# Spec Delta: agent-observability

This change modifies the `agent-observability` capability
(`openspec/specs/agent-observability/spec.md`) by adding 2 new
requirements. The full modified spec lives at
`openspec/specs/agent-observability/spec.md`.

## ADDED Requirements

### Requirement: PlatformTracer facade

The system SHALL provide a `PlatformTracer` facade at
`cianfhoghlaim/observability/platform_tracer.py` that wraps the
3 observability destinations (Langfuse + MLflow + Logfire) per
the LLM Observability Tri-Split requirement. The facade SHALL be
re-exported from `cianfhoghlaim/observability/__init__.py` so
agent code can `from cianfhoghlaim.observability import
PlatformTracer, get_tracer`.

The facade SHALL provide:

- `PlatformTracer.span(name, span_type, metadata) -> context
  manager yielding a `PlatformSpan`
- `PlatformTracer.observe(name=, span_type=) -> decorator`
- `PlatformTracer.flush()` and `PlatformTracer.shutdown()` no-ops
  that delegate to the per-backend modules
- `PlatformTracer.backend_state(backend: str) -> BackendState`
- `PlatformTracer.active_backends() -> list[str]`
- `PlatformTracer.probe_backends(force=False)` for health checks
  with 60s caching

The facade SHALL be **non-raising** — every destination call is
wrapped in `try/except` so the calling agent never sees an
observability failure.

#### Scenario: span decorator wraps the Langfuse + MLflow + Logfire cascade

- **GIVEN** an LLM call wrapped in `@tracer.observe("my_function", span_type="tool")`
- **WHEN** the function is called
- **THEN** the call is traced to Langfuse (primary) via
  `create_generation` or `log_llm_call`
- **AND** an MLflow metric `duration_ms` is logged
- **AND** a Logfire span is written (when `LOGFIRE_TOKEN` is set)
- **AND** no exception escapes to the agent

#### Scenario: PlatformSpan metadata is merged idempotently

- **GIVEN** a `with tracer.span("agent.curriculum_call") as span:`
- **WHEN** the agent does `span.set_metadata({"subject": "maths"})`
- **THEN** `span.metadata["subject"] == "maths"`
- **AND** any subsequent `set_metadata({"k": 1})` augments
  rather than overwrites

### Requirement: Langfuse 5xx falls back to MLflow (5xx → Logfire cascade)

The system SHALL fall back from Langfuse → MLflow → Logfire when
each upstream destination raises a 5xx (or network) error.
Concretely:

When `PlatformTracer._flush_to_langfuse()` raises an
`httpx.HTTPStatusError` (5xx), the tracer SHALL mark Langfuse
as `BackendState.DOWN_5XX`, re-route the current span to MLflow,
and keep the same Tracer instance for subsequent calls (so the
fallback is sticky until `probe_backends(force=True)` succeeds).

When the MLflow destination also raises, the tracer SHALL
fall back to Logfire as a last-resort destination. The cascade
order MUST be: **Langfuse (primary) → MLflow (5xx fallback) →
Logfire (5xx last-resort)**.

#### Scenario: Langfuse returns 5xx → reroute to MLflow

- **GIVEN** the Langfuse backend probe returns
  `BackendState.DOWN_5XX`
- **AND** MLflow is reachable
- **WHEN** `with tracer.span("agent.curriculum_call"): pass`
  runs
- **THEN** no trace is written to Langfuse
- **AND** an MLflow metric is logged
- **AND** `active_backends()` returns `["mlflow", "logfire"]`
  (Langfuse excluded)

#### Scenario: All backends down → graceful no-op

- **GIVEN** all 3 backends probe as DOWN
- **WHEN** `with tracer.span("agent.curriculum_call"): pass`
  runs
- **THEN** no trace is written anywhere
- **AND** the surrounding block continues normally
- **AND** a `logger.warning("PlatformTracer: ... flush failed: ...")`
  is emitted

## Cross-references

- [`cianfhoghlaim/observability/platform_tracer.py`](../../../cianfhoghlaim/observability/platform_tracer.py) (the facade)
- [`cianfhoghlaim/observability/langfuse_config.py`](../../../cianfhoghlaim/observability/langfuse_config.py) (the primary)
- [`cianfhoghlaim/observability/mlflow_config.py`](../../../cianfhoghlaim/observability/mlflow_config.py) (the fallback)
- [`cianfhoghlaim/observability/logfire_config.py`](../../../cianfhoghlaim/observability/logfire_config.py) (the last-resort)
- [`openspec/specs/meaisinfhoghlaim-agent-frameworks/spec.md`](../meaisinfhoghlaim-agent-frameworks/spec.md) (the consumers)
