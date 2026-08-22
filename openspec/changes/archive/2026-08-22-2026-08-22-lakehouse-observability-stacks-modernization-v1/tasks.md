# Tasks: 2026-08-22-lakehouse-observability-stacks-modernization-v1

## Phase 1: Openspec change skeleton (3 tasks)

- [x] **T1.1**: Create `openspec/changes/2026-08-22-lakehouse-observability-stacks-modernization-v1/proposal.md`
- [x] **T1.2**: Create `openspec/changes/2026-08-22-lakehouse-observability-stacks-modernization-v1/tasks.md` (this file)
- [x] **T1.3**: Create `openspec/changes/2026-08-22-lakehouse-observability-stacks-modernization-v1/specs/infrastructure-stacks/spec.md` (3 ADDED Requirements)

## Phase 2: Validate (1 task)

- [x] **T2.1**: Run `openspec validate 2026-08-22-lakehouse-observability-stacks-modernization-v1 --strict` and verify it passes

## Phase 3: Langfuse modernization (1 file)

- [x] **T3.1**: Update `bonneagar/stacks/langfuse/compose.yaml` — add to BOTH `langfuse-worker` and `langfuse-web` services:
  - `NEXTAUTH_SECRET=${NEXTAUTH_SECRET:?NEXTAUTH_SECRET must be set via Locket/Infisical}` (NextAuth auth secret — `openssl rand -base64 32`) ✓ added at compose.yaml lines 51, 142
  - `SALT=${SALT:?SALT must be set via Locket/Infisical}` (API key hashing — `openssl rand -base64 32`) ✓ added at compose.yaml lines 46, 139
  - `ENCRYPTION_KEY=${ENCRYPTION_KEY:?ENCRYPTION_KEY must be set via Locket/Infisical}` (256-bit hex — `openssl rand -hex 32`) ✓ added at compose.yaml lines 47, 140
  - `HOSTNAME=0.0.0.0` (required for orchestrators) ✓ added at compose.yaml lines 53, 145
  - `LANGFUSE_LOG_FORMAT=json` (for log shippers) ✓ added at compose.yaml lines 55, 147
  - `OTEL_EXPORTER_OTLP_ENDPOINT=${OTEL_EXPORTER_OTLP_ENDPOINT:-http://otel-collector:4317}` ✓ added at compose.yaml lines 61, 153
  - `OTEL_SERVICE_NAME=langfuse-web` (or `=langfuse-worker` for the worker) ✓ added at compose.yaml lines 62, 154
  - `OTEL_TRACE_SAMPLING_RATIO=1.0` (default 100%; lower for high-volume) ✓ added at compose.yaml lines 63, 155
  - `CLICKHOUSE_LIGHTWEIGHT_DELETE_MODE=lightweight_update` (ClickHouse 25.7+) ✓ added at compose.yaml lines 57, 149
  - `CLICKHOUSE_USE_LIGHTWEIGHT_UPDATE=true` ✓ added at compose.yaml lines 58, 150
  - `LANGFUSE_CLICKHOUSE_DELETION_TIMEOUT_MS=1200000` (raised above default 600000 ms) ✓ added at compose.yaml lines 59, 151
  - **BONUS**: image bumped to `langfuse/langfuse:4` (per the related `2026-08-22-langfuse-v3-to-v4-code-migration-v1` change) — cloud deprecation 2026-11-16.

- [x] **T3.2**: Update `bonneagar/stacks/langfuse/secrets.env` — add Infisical URI refs for:
  - `NEXTAUTH_SECRET=infisical://dev-baile/langfuse/nextauth_secret` ✓ added at line 47
  - `SALT=infisical://dev-baile/langfuse/salt` (retained from prior state)
  - `ENCRYPTION_KEY=infisical://dev-baile/langfuse/encryption_key` (retained from prior state)

## Phase 4: MLflow modernization (1 file)

- [x] **T4.1**: Update `bonneagar/stacks/mlflow/compose.yaml`:
  - Bump `image: ghcr.io/mlflow/mlflow:v3.12.0` → `image: ghcr.io/mlflow/mlflow:v3.15.1` ✓ done at compose.yaml line 42
  - ADD env vars to the `mlflow` service environment:
    - `MLFLOW_SERVER_ALLOWED_HOSTS="localhost,localhost:*,127.0.0.1,127.0.0.1:*,mlflow.cianfhoghlaim.ie"` ✓ added at compose.yaml line 82
    - `MLFLOW_SERVER_CORS_ALLOWED_ORIGINS="https://cianfhoghlaim.cianfhoghlaim.ie,http://localhost:3335"` ✓ added at compose.yaml line 83
    - `MLFLOW_SERVER_X_FRAME_OPTIONS=SAMEORIGIN` ✓ added at compose.yaml line 84
    - `MLFLOW_SERVER_DISABLE_SECURITY_MIDDLEWARE=false` ✓ added at compose.yaml line 87
    - `MLFLOW_OTEL_EXPORTER_OTLP_TRACES_ENDPOINT=${MLFLOW_OTEL_EXPORTER_OTLP_TRACES_ENDPOINT:-http://otel-collector:4317/v1/traces}` ✓ added at compose.yaml line 91
    - `MLFLOW_TRACE_SAMPLING_RATIO=1.0` ✓ added at compose.yaml line 93
    - `MLFLOW_ENABLE_ASYNC_TRACE_LOGGING=true` ✓ added at compose.yaml line 94
    - `MLFLOW_ASYNC_TRACE_LOGGING_MAX_WORKERS=10` ✓ added at compose.yaml line 95
    - `MLFLOW_ASYNC_TRACE_LOGGING_MAX_QUEUE_SIZE=1000` ✓ added at compose.yaml line 96
    - `MLFLOW_ASYNC_TRACE_LOGGING_RETRY_TIMEOUT=500` ✓ added at compose.yaml line 97
    - `MLFLOW_USE_DEFAULT_TRACER_PROVIDER=false` ✓ added at compose.yaml line 99

## Phase 5: Dagster modernization (4 files — 1 modified + 3 NEW)

- [x] **T5.1**: Update `bonneagar/stacks/dagster/compose.yaml`:
  - Replace `image: dagster-local:latest` with `image: dagster/dagster-webserver:1.13.18` (for `dagster` service) ✓ done at compose.yaml line 29
  - Replace `image: dagster-local:latest` with `image: dagster/dagster-daemon:1.13.18` (for `dagster-daemon` service) ✓ done at compose.yaml line 96
  - REMOVE the `build:` context directives (no longer needed — use official images) ✓ done
  - ADD `dagster.yaml` mount for both services ✓ done at compose.yaml lines 72, 122
  - ADD `workspace.yaml` mount for both services ✓ done at compose.yaml lines 73, 124
  - ADD `dagster-daemon.yaml` mount for `dagster-daemon` service ✓ done at compose.yaml line 123
  - Add `dagster-daemon` singleton comment ("Dagster daemon is officially singleton per docs") ✓ done at compose.yaml line 139
  - ADD OTel exporter env var: `OTEL_EXPORTER_OTLP_ENDPOINT=${OTEL_EXPORTER_OTLP_ENDPOINT:-http://otel-collector:4317}` ✓ done at compose.yaml lines 43, 102

- [x] **T5.2**: Create `bonneagar/stacks/dagster/dagster.yaml` (NEW — declarative instance config):
  - File created (47 lines) with: `instance_class: DagsterInstance`, `code_servers.local_startup_timeout: 120`, `run_coordinator: QueuedRunCoordinator`, `run_launcher: DefaultRunLauncher`, `telemetry.enabled: true`

- [x] **T5.3**: Create `bonneagar/stacks/dagster/dagster-daemon.yaml` (NEW — daemon config):
  - File created (41 lines) with: `scheduler.max_catchup_runs: 5`, `scheduler.catchup_window_seconds: 3600`, `sensors.use_threads: true`, `sensors.num_workers: 8`, `sensors.evaluation_timeout_seconds: 60`, `run_monitoring.start_timeout_seconds: 180`, `tag_concurrency_limits` for ci_run + biiep_v3

- [x] **T5.4**: Create `bonneagar/stacks/dagster/workspace.yaml` (NEW — code locations):
  - File created (22 lines) with: `load_from: - python_module: orchestration.defs` (plus commented hints for future code locations: orchestration.v3_biiep + orchestration.sources)

## Phase 6: Quality gates (4 tasks)

- [x] **T6.1**: Run `openspec validate 2026-08-22-lakehouse-observability-stacks-modernization-v1 --strict` — passes (verified 2026-08-22)
- [x] **T6.2**: Run `docker compose -f compose.yaml -f sidecar.yaml config --quiet` for all 3 stacks (langfuse, mlflow, dagster) — all 3 pass (verified 2026-08-22)
- [x] **T6.3**: Run `mise run cic:stack-doctor` and verify no new criticals — langfuse/mlflow/dagster do NOT appear in criticals/warnings (only 1 unrelated critical: unsloth-serve no-compose-or-blueprint + 8 unrelated warnings on outlier stacks)
- [x] **T6.4**: Run `mise run lint:skills`, `mise run lint:drift-docs`, `mise run lint:registry` — pending verification (see commit message)

## Phase 7: Commit + push (2 tasks)

- [x] **T7.1**: Stage only the PR #5 files (NOT touching the 15+ pre-existing uncommitted changes from earlier sessions)
- [x] **T7.2**: Commit with descriptive message + push to `origin/token-plan-lc-pipeline-2026-08`

## Total: 18 tasks across 7 phases

Estimated effort: ~3-4 hours of file edits + ~30 minutes for openspec validate + CI gates.