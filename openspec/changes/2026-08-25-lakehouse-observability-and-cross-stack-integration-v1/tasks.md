# Tasks: 2026-08-25-lakehouse-observability-and-cross-stack-integration-v1

## Phase 1: Openspec change skeleton (3 tasks)

- [ ] **T1.1**: Create `openspec/changes/2026-08-25-lakehouse-observability-and-cross-stack-integration-v1/proposal.md`
- [ ] **T1.2**: Create `openspec/changes/2026-08-25-lakehouse-observability-and-cross-stack-integration-v1/tasks.md` (this file)
- [ ] **T1.3**: Create `openspec/changes/2026-08-25-lakehouse-observability-and-cross-stack-integration-v1/specs/infrastructure-stacks/spec.md` (2 ADDED Requirements)

## Phase 2: Validate (1 task)

- [ ] **T2.1**: Run `openspec validate 2026-08-25-lakehouse-observability-and-cross-stack-integration-v1 --strict`

## Phase 3: Full otel-collector.yaml (1 file)

- [ ] **T3.1**: Replace placeholder `bonneagar/stacks/lakehouse/otel-collector.yaml` with the full config matching the existing logfire stack's `config/otelcol.yaml`:
  - `receivers.otlp` (gRPC :4317 + HTTP :4318)
  - `processors` (batch + memory_limiter + resource/logfire_metadata)
  - `exporters` (logfire + otlphttp/langfuse + debug)
  - `service.pipelines.traces` (fan-out to all 3 exporters)
  - Extensions: health_check + pprof + zpages
  - Note: the env var references `${env:LOGFIRE_TOKEN}` / `${env:LANGFUSE_AUTH_HEADER}` so the operator must set them via Locket

## Phase 4: Cross-stack dependency documentation (1 file MODIFIED + 1 NEW)

- [ ] **T4.1**: Update `bonneagar/stacks/lakehouse/README.md` with a "Downstream stacks that depend on this stack" section documenting the cross-stack dependency on `logfire-bunchloch` + `langfuse-bunchloch` + `mlflow-bunchloch` + `dagster-bunchloch`
- [ ] **T4.2**: Add a new `docs/observability/lakehouse-otel-fanout.md` doc explaining how the 16 lakehouse services route their OTLP traces through the otel-collector → logfire + langfuse (cross-stack topology)

## Phase 5: mise run lakehouse:all:up orchestrator (1 file MODIFIED)

- [ ] **T5.1**: Update `mise.toml` to add `data:all:up` + `data:all:down` tasks:
  ```toml
  [tasks."data:all:up"]
  description = "Bring up the complete data plane: lakehouse + logfire + langfuse + mlflow + dagster (in dependency order)"
  alias = ["lakehouse:all:up"]
  depends = ["data:up", "logfire:up", "langfuse:up", "mlflow:up", "dagster:up"]
  run = "echo 'Complete data plane is up.'"

  [tasks."data:all:down"]
  description = "Teardown the complete data plane (in reverse dependency order)"
  alias = ["lakehouse:all:down"]
  run = "echo 'Complete data plane is down.'"
  ```

  Also update `data:up` to add a `depends: ["sync"]` chain documenting the order.

## Phase 6: MLflow tracking integration (1 file MODIFIED + 1 NEW helper)

- [ ] **T6.1**: Update `bonneagar/stacks/lakehouse/secrets.env`:
  - ADD `MLFLOW_TRACKING_URI=infisical://dev-baile/lakehouse/mlflow_tracking_uri`
  - ADD `LANGFUSE_PUBLIC_KEY=infisical://dev-baile/lakehouse/langfuse_public_key`
  - ADD `LANGFUSE_SECRET_KEY=infisical://dev-baile/lakehouse/langfuse_secret_key`
- [ ] **T6.2**: Update `bonneagar/stacks/lakehouse/compose.yaml` — add to `dagster` or `garage` service env vars: `MLFLOW_TRACKING_URI=${MLFLOW_TRACKING_URI:-postgresql://lakekeeper:${POSTGRES_PASSWORD}@postgres:5432/mlflow}` (so Dagster can log experiments without depending on the mlflow stack container)

## Phase 7: lakehouse_health() marimo helper (1 function MODIFIED)

- [ ] **T7.1**: Update `notebooks/_shared/schema.py` to add a new function `lakehouse_health()` that:
  - Wraps `scripts/lakehouse_preflight.py` (which already checks 9 endpoints + 13 DBs + 8 buckets)
  - Adds MLflow + Langfuse + Logfire status (cross-stack checks via Docker DNS)
  - Returns a dict with per-stack status (lakehouse / logfire / langfuse / mlflow / dagster)
  - Used in marimo notebooks for the "Stack Health" tab

## Phase 8: Stack-doctor extension (1 file MODIFIED)

- [ ] **T8.1**: Update `scripts/lakehouse-stack-doctor.sh` to add a new check:
  - "every service has `OTEL_EXPORTER_OTLP_ENDPOINT` env var set"
  - The endpoint SHOULD point at either `otel-collector:4317` (local fan-out) or `logfire-otel:4317` (cross-stack fan-out)
  - If neither is set, the stack-doctor FAILS

## Phase 9: Quality gates (4 tasks)

- [ ] **T9.1**: Run `openspec validate 2026-08-25-lakehouse-observability-and-cross-stack-integration-v1 --strict`
- [ ] **T9.2**: Run `docker compose -f compose.yaml -f sidecar.yaml config --quiet` and verify otel-collector service parses
- [ ] **T9.3**: Run `mise run data:stack-doctor` (with the new OTEL check) and verify it passes
- [ ] **T9.4**: Run `mise run lint:skills`, `mise run lint:drift-docs`, `mise run lint:registry`

## Phase 10: Commit + push (2 tasks)

- [ ] **T10.1**: Stage only the PR #4 files (NOT touching the 15+ pre-existing uncommitted changes from earlier sessions)
- [ ] **T10.2**: Commit with descriptive message + push to `origin/token-plan-lc-pipeline-2026-08`

## Total: 18 tasks across 10 phases

Estimated effort: ~2-3 hours of file edits + ~30 minutes for openspec validate + CI gates.

This is the FINAL PR of the 4-PR series. After this ships, the lakehouse stack is fully production-ready + observability-integrated + cross-stack-orchestrated.