# 2026-08-25-lakehouse-observability-and-cross-stack-integration-v1

## Why

PR #4 of the **4-PR lakehouse hardening series** (and the final PR). Wires the
16-service unified lakehouse stack into the canonical observability surface
(Langfuse + MLflow + Logfire) and adds the cross-stack orchestrator that
brings up the full data plane with one command.

This change closes the last remaining gap from PR #2 (which added the
otel-collector stub). After PR #4:

- All 16 lakehouse services emit OTLP traces → otel-collector → **Logfire cloud + Langfuse** (the existing logfire stack already does the fan-out — per `config/otelcol.yaml`).
- MLflow tracks all Dagster asset runs (uses `mlflow` database on shared lakehouse-postgres).
- `mise run lakehouse:all:up` brings up the **complete data plane** in sequence: lakehouse → logfire → langfuse → mlflow → dagster (with cross-stack `depends_on`).
- marimo notebooks can call `lakehouse_health()` for one-line status checks.

## User preferences (locked-in)

| Decision | Choice |
|:--|:--|
| Observability stack | **Langfuse + MLflow + Logfire** (NOT Prometheus/Grafana) |
| Ship strategy | This is **PR #4 of 4** — ship separately (final) |
| Deprecated stacks | Keep as read-only shadow stacks |
| Lance sidecar | Official libs (DONE in PR #2) |

## Dependencies

`Blocked by: 2026-08-15-lakehouse-unified-data-plane-v1` (unified stack)
`Blocked by: 2026-08-22-lakehouse-config-and-env-var-hardening-v1` (secrets hygiene)
`Blocked by: 2026-08-23-lakehouse-production-config-and-lance-sidecar-modernization-v1` (production config + otel-collector stub)
`Blocked by: 2026-08-24-lakehouse-stack-doctor-and-env-var-cleanup-v1` (db_manifest + config.py + stack-doctor)
`Affected repos: cianfhoghlaim` (single-repo change)

## What changes

### 1. otel-collector.yaml full config (1 MODIFIED)
**File**: `bonneagar/stacks/lakehouse/otel-collector.yaml`

Replace the placeholder config with the **full config matching the existing logfire stack's `config/otelcol.yaml`**:
- Receivers: `otlp` (gRPC :4317 + HTTP :4318)
- Processors: `batch`, `memory_limiter`, `resource/logfire_metadata`
- Exporters: `logfire` (SaaS), `otlphttp/langfuse` (self-hosted), `debug`
- Service pipelines: `traces: [otlp] -> [memory_limiter, resource/logfire_metadata, batch] -> [logfire, otlphttp/langfuse, debug]`
- Health check + pprof + zpages extensions
- File-based logging exporter (replaces `debug` exporter)

The local lakehouse otel-collector (stub added in PR #2) becomes a **standalone local fan-out** for cases where the logfire stack isn't deployed (e.g., local dev without the full observability stack). Operators opt-in via `docker compose --profile otel up -d`.

### 2. Cross-stack observability fan-out (1 MODIFIED)
**File**: `bonneagar/stacks/lakehouse/compose.yaml`

The 16 lakehouse services already set `OTEL_EXPORTER_OTLP_ENDPOINT: http://otel-collector:4317` (per PR #2). For production, this endpoint resolves to the **shared logfire stack's `logfire-otel` collector** which fans out to BOTH Logfire cloud + Langfuse.

This PR formalizes the cross-stack dependency in the Komodo deployment TOMLs + the lakehouse README:
- `bonneagar/komodo/procedures/deploy-lakehouse-bunchloch.toml` — adds `requires: logfire-bunchloch` before `lakehouse-bunchloch`
- The lakehouse services can reach `logfire-otel:4317` because both stacks join the `lakehouse_lakehouse` external network (logfire stack uses Docker DNS for the cianfhoghlaim network — needs verification)

### 3. `mise run lakehouse:all:up` orchestrator (1 MODIFIED)
**File**: `mise.toml`

NEW task that brings up the full data plane in sequence:

```toml
[tasks."lakehouse:all:up"]
description = "Bring up the complete data plane: lakehouse + logfire + langfuse + mlflow + dagster (in dependency order)"
run = """
bash scripts/lakehouse_unified_up.sh &&
docker compose -f ../logfire/compose.yaml -f ../logfire/sidecar.yaml up -d &&
docker compose -f ../langfuse/compose.yaml -f ../langfuse/sidecar.yaml up -d &&
docker compose -f ../mlflow/compose.yaml -f ../mlflow/sidecar.yaml up -d &&
docker compose -f ../dagster/compose.yaml -f ../dagster/sidecar.yaml up -d &&
sleep 30 && mise run lakehouse:preflight
"""

[tasks."lakehouse:all:down"]
description = "Teardown the complete data plane (in reverse dependency order)"
run = """
docker compose -f ../dagster/compose.yaml down &&
docker compose -f ../mlflow/compose.yaml down &&
docker compose -f ../langfuse/compose.yaml down &&
docker compose -f ../logfire/compose.yaml down &&
bash scripts/lakehouse_unified_down.sh
"""
```

### 4. MLflow tracking integration (1 MODIFIED)
**File**: `bonneagar/stacks/lakehouse/compose.yaml` + `notebooks/_shared/schema.py`

The Dagster asset definitions can use MLflow tracking via the `mlflow` database on shared lakehouse-postgres. The lakehouse compose already exposes `mlflow` DB + `mlflow-artifacts` bucket (created by garage-init). PR #4 adds:

- `MLFLOW_TRACKING_URI=postgresql://lakekeeper:${POSTGRES_PASSWORD}@postgres:5432/mlflow` env var in lakehouse compose (optional profile `observability` so Dagster + marimo can log experiments)
- A new helper in `notebooks/_shared/schema.py`:
  ```python
  def lakehouse_mlflow_tracking_uri() -> str:
      """Return the MLflow tracking URI for the lakehouse stack."""
      return "postgresql://lakekeeper:devpassword@postgres:5432/mlflow"
  ```

### 5. `lakehouse_health()` marimo helper (1 NEW function in existing file)
**File**: `notebooks/_shared/schema.py`

NEW Python function:
```python
def lakehouse_health() -> Dict[str, Any]:
    """One-line health check for the unified lakehouse stack.

    Wraps `scripts/lakehouse_preflight.py` + adds MLflow/Langfuse/Logfire status.
    Returns a dict with per-service health + the 14 databases + the 8 buckets.
    """
    # Imports + composes from the existing preflight + new cross-stack checks
```

### 6. Quality gates (3 tasks)
- `mise run data:stack-doctor` — extended to verify OTEL_EXPORTER_OTLP_ENDPOINT on every service
- `openspec validate --strict` PASS
- `docker compose config` PASS

## Out of scope (deferred to future PRs)

- **Cross-stack network bridging** between `lakehouse_lakehouse` and `cianfhoghlaim` networks (handled by Komodo stack-depends_on — not by compose)
- **OpenTelemetry collector high availability** (single-instance is fine for dev; production needs a second instance — separate ops PR)
- **Langfuse tracing for the Dagster asset orchestration** (already wired via mlflow LANGFUSE_HOST env var in PR #2)
- **Logfire span filtering rules** (production-tuning, not config)

## Cross-references

- Spec delta: `openspec/changes/2026-08-25-lakehouse-observability-and-cross-stack-integration-v1/specs/infrastructure-stacks/spec.md`
- Tasks: `openspec/changes/2026-08-25-lakehouse-observability-and-cross-stack-integration-v1/tasks.md`
- Related change: `openspec/changes/2026-08-23-lakehouse-production-config-and-lance-sidecar-modernization-v1/` (PR #2 added the otel-collector stub)
- Related change: `openspec/changes/2026-08-24-lakehouse-stack-doctor-and-env-var-cleanup-v1/` (PR #3 added the stack-doctor that we extend)
- Related archive: `openspec/changes/archive/2026-07-30-env-contract-and-observability-fanout-v1/` (the original logfire+langfuse fan-out spec)