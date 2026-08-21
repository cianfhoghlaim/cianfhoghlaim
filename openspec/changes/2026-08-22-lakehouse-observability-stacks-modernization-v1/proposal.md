# 2026-08-22-lakehouse-observability-stacks-modernization-v1

## Why

PR #5 of the post-lakehouse-hardening series. Addresses critical config + version drift issues identified in the upstream-docs research for the 3 observability + workflow stacks:

- **Langfuse** (`langfuse/langfuse:3`) — missing critical security env vars (`NEXTAUTH_SECRET`, `SALT`, `ENCRYPTION_KEY`, `HOSTNAME=0.0.0.0`); no native OTel exporter wired; missing ClickHouse 25.7+ lightweight delete mode
- **MLflow** (`ghcr.io/mlflow/mlflow:v3.12.0`) — version drift to v3.15.1; uses CLI flags (`--allowed-hosts`) instead of canonical env vars (`MLFLOW_SERVER_ALLOWED_HOSTS`); native OTLP `/v1/traces` endpoint not wired; missing `MLFLOW_TRACE_SAMPLING_RATIO` + `MLFLOW_ENABLE_ASYNC_TRACE_LOGGING`
- **Dagster** (`dagster-local:latest`) — version drift to v1.13.18; missing declarative `dagster.yaml` + `dagster-daemon.yaml` + `workspace.yaml` (the 1.13+ Components + Declarative Automation pattern)

Per the upstream docs research notes at `/tmp/stack-research-{langfuse-dagster,mlflow-dlt-cocoindex,baml-motherduck-controlplane}.md`.

## User preferences (locked-in from prior turns)

| Decision | Choice |
|:--|:--|
| PR #5 priority stack | **All 3 in one PR** (Langfuse + MLflow + Dagster) |
| Ship strategy | **This is PR #5 of 7** (post the 4-PR lakehouse series) — ship separately |
| Observability stack | Langfuse + MLflow + Logfire (NOT Prometheus/Grafana) |
| Deprecated stacks | Keep as read-only shadow stacks |

## Dependencies

`Blocked by: 2026-08-15-lakehouse-unified-data-plane-v1` (same lakehouse stack)
`Affected repos: cianfhoghlaim` (single-repo change)

## What changes

### 1. Langfuse modernization (`bonneagar/stacks/langfuse/compose.yaml`)
- Add critical security env vars (all `Required` per Langfuse docs):
  - `NEXTAUTH_SECRET=${NEXTAUTH_SECRET:?...}` (NextAuth auth secret)
  - `SALT=${SALT:?...}` (API key hashing)
  - `ENCRYPTION_KEY=${ENCRYPTION_KEY:?...}` (256-bit hex for secret encryption)
- Add `HOSTNAME=0.0.0.0` (required for orchestrators)
- Add `LANGFUSE_LOG_FORMAT=json` (for log shippers)
- Add native OTel exporter env vars:
  - `OTEL_EXPORTER_OTLP_ENDPOINT=${OTEL_EXPORTER_OTLP_ENDPOINT:-http://otel-collector:4317}`
  - `OTEL_SERVICE_NAME=langfuse-web` (and `=langfuse-worker`)
  - `OTEL_TRACE_SAMPLING_RATIO=1.0`
- Add `CLICKHOUSE_READ_ONLY_URL=` (for compute-compute separation on ClickHouse Cloud / BYOC)
- Add ClickHouse 25.7+ lightweight delete mode (reduce operational bottleneck):
  - `CLICKHOUSE_LIGHTWEIGHT_DELETE_MODE=lightweight_update`
  - `CLICKHOUSE_USE_LIGHTWEIGHT_UPDATE=true`
- Add `LANGFUSE_CLICKHOUSE_DELETION_TIMEOUT_MS=` (raised above default 600000 ms)

### 2. MLflow modernization (`bonneagar/stacks/mlflow/compose.yaml`)
- Bump image `ghcr.io/mlflow/mlflow:v3.12.0` → `ghcr.io/mlflow/mlflow:v3.15.1`
- Add canonical env vars (per MLflow v3.5.0+ security middleware — env var form is canonical):
  - `MLFLOW_SERVER_ALLOWED_HOSTS="localhost,localhost:*,127.0.0.1,127.0.0.1:*,mlflow.cianfhoghlaim.ie"`
  - `MLFLOW_SERVER_CORS_ALLOWED_ORIGINS="https://cianfhoghlaim.cianfhoghlaim.ie,http://localhost:3335"`
  - `MLFLOW_SERVER_X_FRAME_OPTIONS=SAMEORIGIN`
  - `MLFLOW_SERVER_DISABLE_SECURITY_MIDDLEWARE=false` (NEVER true in prod)
- Add native OTLP `/v1/traces` endpoint env var:
  - `MLFLOW_OTEL_EXPORTER_OTLP_TRACES_ENDPOINT=${MLFLOW_OTEL_EXPORTER_OTLP_TRACES_ENDPOINT:-http://otel-collector:4317/v1/traces}`
- Add tracing tunables:
  - `MLFLOW_TRACE_SAMPLING_RATIO=1.0` (default 100%; lower for high-volume)
  - `MLFLOW_ENABLE_ASYNC_TRACE_LOGGING=true`
  - `MLFLOW_ASYNC_TRACE_LOGGING_MAX_WORKERS=10`
  - `MLFLOW_ASYNC_TRACE_LOGGING_MAX_QUEUE_SIZE=1000`
  - `MLFLOW_ASYNC_TRACE_LOGGING_RETRY_TIMEOUT=500`
- Add `MLFLOW_USE_DEFAULT_TRACER_PROVIDER=false` (for combining OTel SDK + MLflow spans)

### 3. Dagster modernization (`bonneagar/stacks/dagster/compose.yaml`)
- Pin to official Dagster images (NOT the locally-built `dagster-local:latest`):
  - `dagster/dagster-webserver:1.13.18`
  - `dagster/dagster-daemon:1.13.18`
- Add declarative config files (NEW files):
  - `dagster.yaml` — instance config (storage + run coordinator + logging)
  - `dagster-daemon.yaml` — daemon-specific config (scheduler + sensor concurrency)
  - `workspace.yaml` — code location declarations
- Document: `dagster-daemon` is **officially singleton** (1 replica max per Dagster docs)
- Adopt **Components + Declarative Automation** patterns (the 1.13+ recommended scaffolding)

### 4. Update `secrets.env` for all 3 stacks
Add Infisical URI refs for the new env vars:
- Langfuse: `NEXTAUTH_SECRET`, `SALT`, `ENCRYPTION_KEY`
- MLflow: keep existing keys
- Dagster: keep existing keys

### 5. Quality gates (4 tasks)
- `openspec validate --strict` PASS
- `docker compose config` for all 3 stacks PASS
- `mise run cic:stack-doctor` PASS
- `mise run lint:skills` / `lint:drift-docs` / `lint:registry` PASS

## Out of scope (deferred to PR #6 / #7)

- **PR #6**: BAML + dlt + CocoIndex + MotherDuck + Infisical + Pangolin + Komodo + LiteLLM proxy image
- **PR #7**: Wire the upgraded Langfuse + MLflow OTel endpoints into the lakehouse otel-collector

## Cross-references

- Spec delta: `openspec/changes/2026-08-22-lakehouse-observability-stacks-modernization-v1/specs/infrastructure-stacks/spec.md`
- Tasks: `openspec/changes/2026-08-22-lakehouse-observability-stacks-modernization-v1/tasks.md`
- Research notes: `/tmp/stack-research-{langfuse-dagster,mlflow-dlt-cocoindex}.md`
- Related change: `openspec/changes/2026-08-15-lakehouse-unified-data-plane-v1/` (the unified lakehouse stack)
- Related change: `openspec/changes/2026-08-24-lakehouse-stack-doctor-and-env-var-cleanup-v1/` (PR #3 — added `scripts/lakehouse-stack-doctor.sh`)