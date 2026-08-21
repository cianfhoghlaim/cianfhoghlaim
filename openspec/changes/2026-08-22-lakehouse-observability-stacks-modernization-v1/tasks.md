# Tasks: 2026-08-22-lakehouse-observability-stacks-modernization-v1

## Phase 1: Openspec change skeleton (3 tasks)

- [ ] **T1.1**: Create `openspec/changes/2026-08-22-lakehouse-observability-stacks-modernization-v1/proposal.md`
- [ ] **T1.2**: Create `openspec/changes/2026-08-22-lakehouse-observability-stacks-modernization-v1/tasks.md` (this file)
- [ ] **T1.3**: Create `openspec/changes/2026-08-22-lakehouse-observability-stacks-modernization-v1/specs/infrastructure-stacks/spec.md` (3 ADDED Requirements)

## Phase 2: Validate (1 task)

- [ ] **T2.1**: Run `openspec validate 2026-08-22-lakehouse-observability-stacks-modernization-v1 --strict` and verify it passes

## Phase 3: Langfuse modernization (1 file)

- [ ] **T3.1**: Update `bonnegar/stacks/langfuse/compose.yaml` — add to BOTH `langfuse-worker` and `langfuse-web` services:
  - `NEXTAUTH_SECRET=${NEXTAUTH_SECRET:?NEXTAUTH_SECRET must be set via Locket/Infisical}` (NextAuth auth secret — `openssl rand -base64 32`)
  - `SALT=${SALT:?SALT must be set via Locket/Infisical}` (API key hashing — `openssl rand -base64 32`)
  - `ENCRYPTION_KEY=${ENCRYPTION_KEY:?ENCRYPTION_KEY must be set via Locket/Infisical}` (256-bit hex — `openssl rand -hex 32`)
  - `HOSTNAME=0.0.0.0` (required for orchestrators)
  - `LANGFUSE_LOG_FORMAT=json` (for log shippers)
  - `OTEL_EXPORTER_OTLP_ENDPOINT=${OTEL_EXPORTER_OTLP_ENDPOINT:-http://otel-collector:4317}`
  - `OTEL_SERVICE_NAME=langfuse-web` (or `=langfuse-worker` for the worker)
  - `OTEL_TRACE_SAMPLING_RATIO=1.0` (default 100%; lower for high-volume)
  - `CLICKHOUSE_READ_ONLY_URL=` (for compute-compute separation)
  - `CLICKHOUSE_LIGHTWEIGHT_DELETE_MODE=lightweight_update` (ClickHouse 25.7+)
  - `CLICKHOUSE_USE_LIGHTWEIGHT_UPDATE=true`
  - `LANGFUSE_CLICKHOUSE_DELETION_TIMEOUT_MS=` (raised above default 600000 ms)

- [ ] **T3.2**: Update `bonnegar/stacks/langfuse/secrets.env` — add Infisical URI refs for:
  - `NEXTAUTH_SECRET=infisical://dev-baile/langfuse/nextauth_secret`
  - `SALT=infisical://dev-baile/langfuse/salt`
  - `ENCRYPTION_KEY=infisical://dev-baile/langfuse/encryption_key`

## Phase 4: MLflow modernization (1 file)

- [ ] **T4.1**: Update `bonnegar/stacks/mlflow/compose.yaml`:
  - Bump `image: ghcr.io/mlflow/mlflow:v3.12.0` → `image: ghcr.io/mlflow/mlflow:v3.15.1`
  - ADD env vars to the `mlflow` service environment:
    - `MLFLOW_SERVER_ALLOWED_HOSTS="localhost,localhost:*,127.0.0.1,127.0.0.1:*,mlflow.cianfhoghlaim.ie"`
    - `MLFLOW_SERVER_CORS_ALLOWED_ORIGINS="https://cianfhoghlaim.cianfhoghlaim.ie,http://localhost:3335"`
    - `MLFLOW_SERVER_X_FRAME_OPTIONS=SAMEORIGIN`
    - `MLFLOW_SERVER_DISABLE_SECURITY_MIDDLEWARE=false`
    - `MLFLOW_OTEL_EXPORTER_OTLP_TRACES_ENDPOINT=${MLFLOW_OTEL_EXPORTER_OTLP_TRACES_ENDPOINT:-http://otel-collector:4317/v1/traces}`
    - `MLFLOW_TRACE_SAMPLING_RATIO=1.0`
    - `MLFLOW_ENABLE_ASYNC_TRACE_LOGGING=true`
    - `MLFLOW_ASYNC_TRACE_LOGGING_MAX_WORKERS=10`
    - `MLFLOW_ASYNC_TRACE_LOGGING_MAX_QUEUE_SIZE=1000`
    - `MLFLOW_ASYNC_TRACE_LOGGING_RETRY_TIMEOUT=500`
    - `MLFLOW_USE_DEFAULT_TRACER_PROVIDER=false`

## Phase 5: Dagster modernization (4 files — 1 modified + 3 NEW)

- [ ] **T5.1**: Update `bonnegar/stacks/dagster/compose.yaml`:
  - Replace `image: dagster-local:latest` with `image: dagster/dagster-webserver:1.13.18` (for `dagster` service)
  - Replace `image: dagster-local:latest` with `image: dagster/dagster-daemon:1.13.18` (for `dagster-daemon` service)
  - REMOVE the `build:` context directives (no longer needed — use official images)
  - ADD `dagster.yaml` mount for both services
  - ADD `workspace.yaml` mount for both services
  - ADD `dagster-daemon.yaml` mount for `dagster-daemon` service
  - Add `dagster-daemon` singleton comment ("Dagster daemon is officially singleton per docs")
  - ADD OTel exporter env var: `OTEL_EXPORTER_OTLP_ENDPOINT=${OTEL_EXPORTER_OTLP_ENDPOINT:-http://otel-collector:4317}`

- [ ] **T5.2**: Create `bonnegar/stacks/dagster/dagster.yaml` (NEW — declarative instance config):
  ```yaml
  # Dagster instance configuration (Dagster 1.13+ declarative format)
  # Per https://docs.dagster.io/deployment/oss/dagster-yaml
  instance_class:
    module: dagster._core.instance.core
    class: DagsterInstance
  code_servers:
    local_startup_timeout: 120
  telemetry:
    enabled: true
  ```

- [ ] **T5.3**: Create `bonnegar/stacks/dagster/dagster-daemon.yaml` (NEW — daemon config):
  ```yaml
  # Dagster daemon configuration
  # Per https://docs.dagster.io/deployment/execution/dagster-daemon
  scheduler:
    max_catchup_runs: 5
  sensors:
    use_threads: true
    num_workers: 8
  ```

- [ ] **T5.4**: Create `bonnegar/stacks/dagster/workspace.yaml` (NEW — code locations):
  ```yaml
  # Dagster workspace.yaml — code locations
  # Per https://docs.dagster.io/concepts/code-locations/workspace
  load_from:
    - python_module: orchestration.defs
  ```

## Phase 6: Quality gates (4 tasks)

- [ ] **T6.1**: Run `openspec validate 2026-08-22-lakehouse-observability-stacks-modernization-v1 --strict`
- [ ] **T6.2**: Run `docker compose -f compose.yaml -f sidecar.yaml config --quiet` for all 3 stacks (langfuse, mlflow, dagster)
- [ ] **T6.3**: Run `mise run cic:stack-doctor` and verify no new criticals
- [ ] **T6.4**: Run `mise run lint:skills`, `mise run lint:drift-docs`, `mise run lint:registry`

## Phase 7: Commit + push (2 tasks)

- [ ] **T7.1**: Stage only the PR #5 files (NOT touching the 15+ pre-existing uncommitted changes from earlier sessions)
- [ ] **T7.2**: Commit with descriptive message + push to `origin/token-plan-lc-pipeline-2026-08`

## Total: 18 tasks across 7 phases

Estimated effort: ~3-4 hours of file edits + ~30 minutes for openspec validate + CI gates.