# Change: 2026-07-02-align-cianfhoghlaim-env-with-stacks

## Why

The sibling Change 7
(`2026-07-02-replace-private-images-and-bring-wave2`)
brought 11 of 12 target stacks UP (27 containers running on bunchloch),
but the `cianfhoghlaim/` Python code still uses hardcoded hostnames
(`http://litellm:4000/v1`), wrong port defaults (langfuse `:3000`
instead of `:3001`, falkordb `:6379` instead of `:6380`), and the
old Memgraph default for Cognee. This change updates the code to
match the actual deployed stack contracts.

The 12 stack-side changes (image replacement + dev overlays) are
already deployed and committed. This change makes the code-side
catch up.

## What changes

### 1 — `dagster/resources.py` (the 5 KCG Components' resources)

- `FalkorDBResource` defaults: `host=""` + `port=0` (env-driven via
  `FALKORDB_HOST` + `FALKORDB_PORT`). The current hardcoded
  `localhost:6379` breaks on host (where falkordb is on `:6380`)
  and on docker (where the DNS name is `falkordb`).
- `CogneeMemoryResource`: replace `graph_url: bolt://localhost:7687`
  (Memgraph default) with `postgres_url` (pgvector default). The
  current cianfhoghlaim config uses `USE_UNIFIED_PROVIDER=pghybrid`
  per the cognee compose; the code should default to that.
- Deprecate `MemgraphResource`, `Neo4jResource`,
  `TemporalGraphResource` (no stack in user's 19-list + per
  `agent-observability` spec Memgraph is deprecated). The instances
  are kept for backwards compatibility but the docstrings mark them
  as deprecated.
- `ProgressTrackerResource.redis_url`: add an env-driven default
  (`REDIS_URL` first, then the local `redis://localhost:6379`).

### 2 — `observability/langfuse_config.py`

- `LANGFUSE_HOST` default: `http://localhost:3000` → `http://localhost:3001`
  (stack's host port per `langfuse/compose.yaml`).

### 3 — `observability/logfire_config.py`

- Add `logfire_instrument_local_otlp_only()` helper for dev mode:
  when `LOGFIRE_TOKEN` is empty, fall back to sending all spans to
  the local OTel collector via `OTEL_EXPORTER_OTLP_ENDPOINT` (no
  Logfire SaaS required). The local `logfire` stack in dev mode
  is an OTel collector that just buffers + drops (or forwards to
  Logfire if a token is set on the collector).

### 4 — `cocoindex/_lifespan.py`

- `LANCEDB_URI` default: `rest://lance-api.cianfhoghlaim.ie`
  → `rest://lakehouse-lance-namespace:8182` (the local dev endpoint
  per the lakehouse-lance-namespace stack).

### 5 — `baml/clients.baml` + `baml/clients_llama_swap.baml`

- All 7 litellm-routed clients in `clients.baml`:
  `"http://localhost:4000/v1"` → `env.LITELLM_BASE_URL`
- All 4 llama-swap clients in `clients_llama_swap.baml`:
  `"http://llama-swap:8080/v1"` → `env.LLAMASWAP_BASE_URL`
- Regenerate the Python client: `cd cianfhoghlaim && uv run baml-cli generate`

### 6 — `dlt/common/destinations_oideachais.py`

- Add `_resolve_aws_credentials()` helper: maps
  `GARAGE_ACCESS_KEY_ID` → `AWS_ACCESS_KEY_ID` (and SECRET analog)
  so the existing DLT pipelines work with the lakehouse's GARAGE
  env var naming convention without code changes.
- The existing `_build_local_destination` function calls the
  helper at parse time so the merged env is `AWS_*` (what boto3
  expects).

### 7 — `dlt/common/destinations_oideachais.py` COGNEE_BASE

- The two references to `http://lakehouse-cognee:8000` (default
  cianfhoghlaim code) and the cognee compose's `http://cognee:8000`
  (in-docker) are already aligned. The HOST-PORT shift from
  :8000→:8100 doesn't affect the code paths (the code uses the
  docker DNS, not the host port). No change needed for COGNEE_BASE.

### 8 — `ciansfhoghlaim/.env.dev.local` (NEW)

A canonical local env file with all the dev endpoints + dev creds:

```bash
# Litellm gateway (chokepoint) — docker DNS inside, localhost outside
LITELLM_BASE_URL=http://litellm:4000/v1
LLAMASWAP_BASE_URL=http://llama-swap:8080/v1

# Langfuse (note: stack exposes :3001 → container :3000)
LANGFUSE_HOST=http://langfuse:3000   # in-docker; or http://localhost:3001 on host
LANGFUSE_PUBLIC_KEY=pk-lf-dev
LANGFUSE_SECRET_KEY=sk-lf-dev

# MLflow (stack exposes :5001 → :5000)
MLFLOW_TRACKING_URI=http://mlflow:5000
MLFLOW_BACKEND_STORE_URI=postgresql://lakekeeper:devpassword@lakehouse-postgres:5432/mlflow

# Cognee (in-docker; or http://localhost:8100 on host)
COGNEE_BASE=http://cognee:8000

# Lakehouse DuckLake
DUCKLAKE_POSTGRES_HOST=lakehouse-postgres
DUCKLAKE_POSTGRES_PORT=5432
DUCKLAKE_POSTGRES_USER=lakekeeper
DUCKLAKE_POSTGRES_PASSWORD=devpassword

# Garage S3
AWS_ENDPOINT_URL=http://lakehouse-garage:3900
AWS_ACCESS_KEY_ID=GK1601dev
AWS_SECRET_ACCESS_KEY=dev-secret-key-not-for-prod
AWS_REGION=garage

# LanceDB
LANCEDB_URI=rest://lakehouse-lance-namespace:8182
LANCEDB_API_KEY=devtoken

# FalkorDB (in-docker; or 127.0.0.1:6380 on host)
FALKORDB_HOST=falkordb
FALKORDB_PORT=6379
FALKORDB_PASSWORD=devpassword

# Dagster
DAGSTER_HOME=./
USE_DUCKLAKE=true

# OTel collector (logfire)
OTEL_EXPORTER_OTLP_ENDPOINT=http://logfire:4317
```

### 9 — 8 stage marimo notebooks wired to live lakehouse data

The 8 stage/cross-domain marimo notebooks in
`cianfhoghlaim/notebooks/dashboards/` currently use hardcoded
dataframes. Wire them to live lakehouse data:

- `aistear.py` → query Cognee `oideachais.aistear` dataset
- `primary.py` → query Cognee `oideachais.primary` dataset
- `junior_cycle.py` → query Cognee `oideachais.junior_cycle` dataset
- `senior_cycle.py` → query Cognee `oideachais.senior_cycle` dataset
- `tertiary.py` → query Cognee `oideachais.tertiary` dataset
- `cross_domain.py` → query Cognee `oideachais.cross_stage` dataset
- `leabharlann_full_stack_demo.py` → read from local DuckDB
  `/tmp/leabharlann_demo.duckdb` (existing default)
- `email_inbox_triage.py` → query lakehouse-postgres
  `oideachais_inbox_messages` table

The 4 lakehouse notebooks in `notebooks/dashboards/duckdb/`
(4 already wired) stay as-is.

## Impact

- **Affected specs:** `infrastructure-stacks` (host:port alignment),
  `agent-observability` (langfuse port + logfire dev mode),
  `agent-memory-systems` (Cognee default), `oideachais-pipeline`
  (BAML env vars + DLT credential mapping + marimo wiring),
  `dagster-5-layer-component-architecture` (5 KCG Components
  resource defaults)
- **Affected code:** 7 files in `cianfhoghlaim/` + 1 new
  `.env.dev.local` file + 1 BAML regeneration
- **Affected hosts:** `bunchloch` only (dagster dev mode)
- **Risk:** low — code changes are env-var default updates; BAML
  regeneration produces a new client module. No data migrations
  needed.
- **Audit gates:** `openspec validate --strict` + 10/12 smoke
  tests from Change 7 (should now all pass with the code
  defaults pointing at the right hosts) + `dagster dev -m
  cianfhoghlaim.dagster.definitions` boots cleanly

## Non-goals

- **Not adding new spec definitions** for each individual
  service. This change is implementation-only — the canonical
  specs are updated via the deltas.
- **Not migrating Cognee from pgvector to a graph DB.** The
  cianfhoghlaim code already uses `USE_UNIFIED_PROVIDER=pghybrid`
  (postgres + pgvector). No graph DB migration needed.
- **Not deploying Wave 3 or Wave 4.** That's a separate
  follow-up change.
- **Not fixing the openchamber stack or graphiti stack.** Both
  remain in the deferred list.

## Open follow-up issues

| Issue | Tracking change |
|:--|:--|
| Langfuse /api/public/health empty reply | `2026-07-XX-fix-langfuse-health` (open investigation) |
| Wave 3 deploy (invokeai + convex + risingwave + marimo) | `2026-07-03-wave-3-ui-streams-deploy` |
| Wave 4 deploy (hermes + openclaw) | `2026-07-03-wave-4-agent-deploy` |
| olmocr / docling-serve / paddleocr / dots-ocr / graphiti / openchamber deferred from Change 7 | per the deferred table in HEALTH_REPORT.md |
