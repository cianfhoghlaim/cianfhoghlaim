# observability-drift-cleanup Specification

## Purpose

`observability-drift-cleanup` is a capability of the Cianfhoghlaim
platform that codifies the observability stack + the drift-cleanup gate.

After this spec is implemented:

- 4 `TracingBackend` concrete classes (Datadog, Langfuse, Logfire, Mlflow)
- OTel semantic conventions enforced on every `TraceSpan`
- `lint:drift-docs` passes (zero drift claims across 15 audited AGENTS.md files)

This spec captures Wave 7 of the 2026-08-24 master refactor plan.

## Requirements

### Requirement: 4 TracingBackend concrete classes

`observability/unified_tracer.py` SHALL define exactly 4 concrete
subclasses of `TracingBackend`:

- `DatadogBackend` (LLMObs agent traces + token usage + cost tracking)
- `LangfuseBackend` (prompt management + trace analysis)
- `LogfireBackend` (Pydantic AI specific tracing)
- `MlflowBackend` (local tracing via `mlflow.tracing`; the Wave 7 v0 straggler)

#### Scenario: All 4 backends import cleanly

- **WHEN** `from observability.unified_tracer import DatadogBackend, LangfuseBackend, LogfireBackend, MlflowBackend` runs
- **THEN** all 4 classes are accessible

### Requirement: OTel semantic conventions

Every `TraceSpan` emitted by `UnifiedTracer.trace(...)` SHALL be tagged
with the canonical OpenTelemetry semantic conventions based on the
`span_type`:

- `span_type: "db"` → tag with `db.system: duckdb`
- `span_type: "llm"` → tag with `gen_ai.system: baml`
- `span_type: "tool"` (touches S3) → tag with `object_store.system: s3`

#### Scenario: All 3 conventions apply correctly

- **WHEN** `apply_otel_semantic_conventions(span, "db")` runs
- **THEN** `span.metadata["db.system"] == "duckdb"`

### Requirement: lint:drift-docs passes

The `mise run lint:drift-docs` command SHALL exit 0 (no drift) after
all 15 audited AGENTS.md files are updated.

#### Scenario: Zero drift

- **WHEN** `uv run python scripts/lint_drift_docs.py --dry-run` runs
- **THEN** the output is `OK: 0 number drift claims in 15 audited AGENTS.md files`

### Requirement: MlflowBackend implements the 3-method ABC

`MlflowBackend` SHALL implement all 3 abstract methods of
`TracingBackend`:

- `start_span(name, span_type, metadata, parent_id) -> str`
- `end_span(span_id, status, metadata, error) -> None`
- `log_event(span_id, event_name, data) -> None`

#### Scenario: MlflowBackend.start_span works

- **WHEN** `MlflowBackend().start_span("test", "workflow")` runs
- **THEN** a non-empty span_id is returned (or `""` if mlflow not installed)

### Requirement: MlflowBackend graceful fallback

If `mlflow` is not installed OR `MLFLOW_TRACKING_URI` is not set,
`MlflowBackend.enabled` SHALL be `False` and all 3 methods SHALL
be silent no-ops.

#### Scenario: mlflow not installed

- **WHEN** `MlflowBackend()` runs without `mlflow` installed
- **THEN** `enabled=False` and `start_span(...)` returns `""`

### Requirement: UnifiedTracer accepts mlflow_enabled parameter

`UnifiedTracer.__init__` SHALL accept an `mlflow_enabled: bool = True`
parameter. When `True` (default), `MlflowBackend` is appended to
`self.backends`.

#### Scenario: UnifiedTracer with mlflow

- **WHEN** `UnifiedTracer(mlflow_enabled=True)` runs
- **THEN** `len(self.backends) >= 4`
