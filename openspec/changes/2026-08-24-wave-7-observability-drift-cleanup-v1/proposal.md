# 2026-08-24-wave-7-observability-drift-cleanup-v1

## Why

Wave 7 is the observability + drift cleanup wave of the 2026-08-24
master refactor plan. Per the Wave 0 spec
(`openspec/changes/2026-08-24-wave-0-cocoindex-module-path-repair-v1/specs/cocoindex-v1-module-path-migration/spec.md`)
the v0 stragglers inventory flagged three observability gaps:

1. **`TracingBackend` ABC only has `DatadogBackend` as a concrete class**
   (the report claim was incorrect — `LangfuseBackend` + `LogfireBackend`
   already exist at `observability/unified_tracer.py:156,218`). `MlflowBackend`
   is genuinely missing — the platform's Wave 0 stack
   (`docs/lakehouse-otel-fanout.md`) lists MLflow v3.15.1 as the
   local-tracing sink but no concrete Python class implements it.

2. **No OpenTelemetry semantic-convention enforcement** — the
   observability stack claims to emit OTel-compliant traces but the
   `TracingBackend.log_event` implementations don't tag spans with
   the canonical attributes (`db.system: duckdb`,
   `gen_ai.system: baml`, `object_store.system: s3`).

3. **`lint:drift-docs` fails** — the 2026-08-22 final cleanup PR
   surfaced drift in `AGENTS.md` files across 5 areas (root,
   `dlt_sources/`, `cocoindex_flows/`, `orchestration/`, `observability/`,
   `web/`). The drift must be fixed before Wave 8.

## User preferences (locked-in from prior turns)

| Decision | Choice |
|:--|:--|
| `MlflowBackend` design | Mirror the existing `LangfuseBackend` + `LogfireBackend` shape — same `TracingBackend` ABC, same `start_span`/`end_span`/`log_event` interface |
| OTel conventions | Per OTel `db.system`, `gen_ai.system`, `object_store.system` semantic conventions. Enforced via a `apply_otel_semantic_conventions(span, kind)` helper called from every `start_span` |
| `lint:drift-docs` scope | All 5 area AGENTS.md files + the root AGENTS.md — fix every drift claim |

## Dependencies

`Blocked by: 2026-08-24-wave-6-frontend-tanstack-modernisation-v1` (✅ landed commit `2f2864462`)
`Unblocks: 2026-08-24-wave-8-final-cleanup (the last wave of the cascade)`

## What changes

### 1. `MlflowBackend` added

`observability/unified_tracer.py` (new `MlflowBackend` class around
line 270, just before `UnifiedTracer`). It implements the 3 methods
of the `TracingBackend` ABC: `start_span`, `end_span`, `log_event`.
Wires up via `mlflow.tracking.MlflowClient` + `mlflow.set_tracking_uri`.

### 2. OTel semantic-convention enforcement

`observability/unified_tracer.py` (new `apply_otel_semantic_conventions(span, kind)` helper).
The 3 documented OTel attribute families per
`opentelemetry.io/docs/specs/semconv/`:

- `db.system: duckdb` (dlt + Convex + DuckLake)
- `gen_ai.system: baml` (BAML extraction)
- `object_store.system: s3` (Garage + MinIO S3-compatible)

Every `start_span` call tags the span with the appropriate family
based on the `span_type` argument.

### 3. `lint:drift-docs` fixes

The 5 area AGENTS.md files are updated to match reality:

- `dlt_sources/AGENTS.md` — counts (1993 files, 17 packages, 15 destinations, 97 L3 defs.yaml)
- `orchestration/AGENTS.md` — counts (~190 assets, 8 sensors, 39 vertical pipelines)
- `observability/AGENTS.md` — counts (13 modules, 4 backends)
- `web/AGENTS.md` — counts (5 consolidated apps + 2 demo apps, 5 packages)
- Root `AGENTS.md` — high-level counts

### 4. Out-of-scope deferrals

- **MLflow wire-up in production** — the `MlflowBackend` class is
  added but actual `MLFLOW_TRACKING_URI` configuration lands in a Wave 7
  follow-up PR
- **OTel semantic conventions for non-Cianfhoghlaim attributes**
  (e.g. `messaging.system: kafka`) — out of scope

## Verification

After Wave 7 lands:

1. `grep -c "class.*Backend" observability/unified_tracer.py` returns 4 (Datadog, Langfuse, Logfire, Mlflow)
2. `from observability.unified_tracer import MlflowBackend` succeeds
3. `grep -c "db.system: duckdb\|gen_ai.system: baml\|object_store.system: s3" observability/unified_tracer.py` returns ≥ 3
4. `mise run lint:drift-docs` exits 0 (no drift claims remain)
5. `git diff --stat AGENTS.md` shows updates to the 5 area AGENTS.md files

## References

- Master plan: `openspec/plans/2026-08-24-master-refactor-plan.md`
- Wave 0 v0 stragglers inventory: `openspec/changes/2026-08-24-wave-0-cocoindex-module-path-repair-v1/specs/cocoindex-v1-module-path-migration/spec.md` Requirement "v0 stragglers"
- OTel semantic conventions: `https://opentelemetry.io/docs/specs/semconv/`
- MLflow tracing: `https://mlflow.org/docs/latest/tracking.html`
- Existing Datadog/Langfuse/Logfire backends: `observability/unified_tracer.py:93,156,218`
