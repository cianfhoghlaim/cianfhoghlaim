# Observability Env-Var Contract — Canonical Reference

> Source-of-truth for the 17 environment variables that wire the
> Langfuse + MLflow + Logfire observability stack across the
> Cianfhoghlaim platform. Every KCG service that emits traces,
> experiments, or LLM traces reads from this table.
>
> **Updated:** 2026-07-30 (env-contract-and-observability-fanout-v1)
> **Owner:** observability skill (`.agents/skills/agent-observability/`)
> **Spec:** `openspec/changes/2026-07-30-.../specs/agent-observability/spec.md`

## The 62 canonical variables

The contract is partitioned into 11 groups: 4 observability groups
(Langfuse SDK + MLflow + Logfire/OTel + shared cluster = 17 vars),
plus 7 additional reference groups (data ingestion, DuckLake write
path, MotherDuck federated analytics, LanceDB, S3/Garage,
embedder/model registry, and meaisinfhoghlaim + OCR backends = 45 vars).
The 17 observability variables remain the most-critical reference for
any tracing-related question; the 45 additional vars are appended below
for the 2026-08-02 drift-audit remediation.

### Group 1 — Langfuse SDK (4 vars)

| Variable | Type | Required? | Resolved from | Description |
|:--|:--|:--|:--|:--|
| `LANGFUSE_HOST` | URL | yes | `infisical://dev-baile/langfuse/host` | The Langfuse server URL. **Canonical value:** `https://langfuse.cianfhoghlaim.ie` (production) or `http://langfuse:3000` (in-cluster). Never hardcode `localhost`. |
| `LANGFUSE_PUBLIC_KEY` | string | yes | `infisical://dev-baile/langfuse/public_key` | Project public key. Format: `pk-lf-<project>-<random>`. |
| `LANGFUSE_SECRET_KEY` | string | yes | `infisical://dev-baile/langfuse/secret_key` | Project secret key. Format: `sk-lf-<project>-<random>`. |
| `LANGFUSE_AUTH_HEADER` | string | yes (collector only) | `infisical://dev-baile/logfire/auth_header` | **Logfire-collector-only**: the base64-encoded `PUBLIC_KEY:SECRET_KEY` pair used as the HTTP Basic auth header for the `otlphttp/langfuse` exporter in `otelcol.yaml`. Constructed as: `echo -n "$PUBLIC_KEY:$SECRET_KEY" \| base64 -w0`. |

### Group 2 — MLflow tracking (3 vars)

| Variable | Type | Required? | Resolved from | Description |
|:--|:--|:--|:--|:--|
| `MLFLOW_TRACKING_URI` | URL | yes | `infisical://dev-baile/mlflow/uri` | **Canonical value:** `http://mlflow:5000` (in-cluster) or `https://mlflow.cianfhoghlaim.ie` (external). Never hardcode `localhost:5000` (collides with macOS AirPlay Receiver). |
| `MLFLOW_EXPERIMENT_NAME` | string | no (default `dlt-pipelines`) | `infisical://dev-baile/mlflow/experiment_name` | The default experiment for any `mlflow.set_experiment(...)` call without an explicit name. |
| `MLFLOW_S3_ENDPOINT_URL` | URL | yes (artifact store) | `infisical://dev-baile/lakehouse/s3_endpoint` | **Canonical value:** `http://lakehouse-garage:3900` (the centralised Garage S3 from the lakehouse stack). Required for `mlflow.log_artifact(...)`. |

### Group 3 — Logfire + OpenTelemetry fan-out (7 vars)

| Variable | Type | Required? | Resolved from | Description |
|:--|:--|:--|:--|:--|
| `OTEL_EXPORTER_OTLP_ENDPOINT` | URL | yes (every backend) | `infisical://dev-baile/logfire/otel_endpoint` | **Canonical value:** `http://logfire-otel:4317` (gRPC) or `http://logfire-otel:4318` (HTTP). The collector fans out to BOTH logfire cloud AND langfuse. |
| `OTEL_EXPORTER_OTLP_PROTOCOL` | enum | no (default `grpc`) | env block only | `grpc` (preferred for Python OTEL SDKs) or `http/protobuf` (fallback). |
| `OTEL_SERVICE_NAME` | string | yes | compose.yaml literal | The service name as it appears in the Logfire/Langfuse UI. Convention: lowercase, hyphenated, matches the compose service name. |
| `LOGFIRE_TOKEN` | string | yes (collector) | `infisical://dev-baile/logfire/write_token` | Pydantic Logfire write token (from `https://logfire.pydantic.dev` → Project Settings → Tokens). Required for the `logfire` exporter in the collector. |
| `LOGFIRE_PROJECT_NAME` | string | no (default `oideachas-celtic-education`) | env block only | Resource attribute on every trace; groups spans by project in the Logfire UI. |
| `LOGFIRE_ENVIRONMENT` | enum | no (default `production`) | env block only | Resource attribute; values: `production`, `staging`, `development`. |
| `LOGFIRE_SERVICE_NAME` | string | no (legacy) | env block only | Legacy attr (replaced by `OTEL_SERVICE_NAME`). Keep for backwards compat with old dashboards. |

### Group 4 — Shared cluster identity (3 vars)

| Variable | Type | Required? | Resolved from | Description |
|:--|:--|:--|:--|:--|
| `INFISICAL_TOKEN` | string | yes (operator-side) | `.env` only | Universal Auth machine-identity token for the operator's local CLI (`bun run scripts/init-vault.ts`). NOT shipped to containers — they use the bons-locket-shim instead. |
| `INFISICAL_PROJECT_ID` | UUID | yes (operator-side) | `.env` only | The `dev-baile` workspace UUID. Canonical value (verified live 2026-07-29): `d900f50a-acbf-446b-b4f6-e439710253e4`. |
| `INFISICAL_ENV` | string | no (default `dev`) | `.env` only | The environment slug. Canonical: `dev-baile` (not `dev` — the human-readable name differs from the slug). |

## Beyond observability — additional canonical env vars

The 2026-08-02 drift audit identified 30+ additional env vars that
the BIEP data platform, scraping layer, and lakehouse stack depend
on. They are appended here in Groups 5-10 to give the team a single
canonical reference. **Do not move tracing-related questions off the
original 17 vars** — those remain the source of truth for
Langfuse / MLflow / Logfire wiring.

### Group 5 — Data ingestion & scraping (6 vars)

| Variable | Type | Required? | Resolved from | Description |
|:--|:--|:--|:--|:--|
| `USE_LOCAL_SCRAPES` | bool | no (default `true`) | env block only | If true, route all dlt extractions to `stedding/ingest_queue/` instead of live web scraping (saves Firecrawl credits + bypasses rate limits). Per agent critical protocol #2. |
| `STEDDING_INGEST_QUEUE` | path | no (default `stedding/ingest_queue/`) | env block only | Local fixture path for offline extraction fallback. |
| `FIRECRAWL_API_KEY` | string | yes (prod) | `infisical://dev-baile/firecrawl/api_key` | Firecrawl scraping API key. Used by `dlt_sources/british_isles/ireland/`, `agents/`, etc. |
| `BROWSERBASE_API_KEY` | string | yes (prod) | `infisical://dev-baile/browserbase/api_key` | Browserbase hosted-browser API key. |
| `BROWSERBASE_PROJECT_ID` | string | yes (prod) | `infisical://dev-baile/browserbase/project_id` | Browserbase project ID. |
| `CRAWL4AI_ENABLED` | bool | no (default `true`) | env block only | Toggle for the Crawl4AI scraper fallback. |

### Group 6 — DuckLake write path (9 vars)

| Variable | Type | Required? | Resolved from | Description |
|:--|:--|:--|:--|:--|
| `USE_DUCKLAKE` | bool | no (default `true`) | env block only | Switch between DuckLake (production) and local DuckDB (dev). |
| `DLT_ENVIRONMENT` | enum | no (default `local`) | env block only | `local` or `production`. Selects which destination factory branch is used. |
| `DUCKLAKE_BUCKET` | string | no (default `ducklake-cianfhoghlaim`) | `infisical://dev-baile/lakehouse/bucket_name` | The canonical Garage S3 bucket for DuckLake writes. **Must match the bucket created by `lakehouse/compose.yaml`'s `garage-init` service.** |
| `DUCKLAKE_POSTGRES_HOST` | string | yes (prod) | `infisical://dev-baile/lakehouse/postgres_host` | Host of the centralised lakehouse-postgres. Canonical: `lakehouse-postgres`. |
| `DUCKLAKE_POSTGRES_PORT` | int | no (default `5432`) | env block only | Port. |
| `DUCKLAKE_POSTGRES_USER` | string | no (default `lakekeeper`) | `infisical://dev-baile/lakehouse/postgres_user` | Owner of the 6 `ducklake_*` databases. |
| `DUCKLAKE_POSTGRES_PASSWORD` | string | yes (prod) | `infisical://dev-baile/lakehouse/postgres_password` | Owner password. |
| `DUCKLAKE_POSTGRES_DB` | string | per-namespace | `infisical://dev-baile/<namespace>/postgres_db` | One of 6 active: `ducklake_oideachais`, `ducklake_crypteolas`, `ducklake_croilar`, `ducklake_tuath`, `ducklake_meaisinfhoghlaim`, `ducklake_aleyum` (legacy). |
| `DUCKLAKE_POSTGRES_SSLMODE` | enum | no (default `disable`) | env block only | `disable` (dev), `prefer` (laptop), `require` (managed). |

### Group 7 — MotherDuck federated analytics (6 vars)

| Variable | Type | Required? | Resolved from | Description |
|:--|:--|:--|:--|:--|
| `MOTHERDUCK_TOKEN` | string | yes | `infisical://dev-baile/motherduck/token` | MotherDuck service-account PAT (canonical path; not `lakehouse/token`). |
| `MOTHERDUCK_MODE` | enum | no (default `byob`) | `infisical://dev-baile/motherduck/mode` | `managed` / `byob` / `byoc`. |
| `MOTHERDUCK_DATABASE` | string | no (default `cianfhoghlaim`) | `infisical://dev-baile/motherduck/database` | Database name. **Post-v7 canonical alias is `md:cianfhoghlaim` (NOT `md:oideachais`).** |
| `MOTHERDUCK_S3_BUCKET` | string | no (default `ducklake-cianfhoghlaim`) | `infisical://dev-baile/motherduck/s3_bucket` | S3 bucket for `byob`/`byoc`. |
| `MOTHERDUCK_S3_ENDPOINT` | string | no (default `http://lakehouse-garage:3900`) | `infisical://dev-baile/motherduck/s3_endpoint` | S3 endpoint URL. |
| `MOTHERDUCK_ENABLED` | bool | no (default `true`) | env block only | Toggle for the MotherDuck federated query path. |

### Group 8 — Vector store (LanceDB) (3 vars)

| Variable | Type | Required? | Resolved from | Description |
|:--|:--|:--|:--|:--|
| `LANCEDB_URI` | string | yes | `infisical://dev-baile/lancedb/uri` | Canonical: `rest://lakehouse-lance-namespace:8182` (the Lance Namespace REST adapter inside the lakehouse stack). |
| `LANCEDB_API_KEY` | string | yes (prod) | `infisical://dev-baile/lancedb/api_key` | Bearer token for the Lance Namespace REST adapter. |
| `LANCEDB_VIEWER_ADMIN_TOKEN` | string | yes (prod) | `infisical://dev-baile/lakehouse/lancedb_viewer_admin_token` | Admin token for the standalone LanceDB viewer UI. |

### Group 9 — S3 / Garage (9 vars)

| Variable | Type | Required? | Resolved from | Description |
|:--|:--|:--|:--|:--|
| `AWS_ACCESS_KEY_ID` | string | yes (prod) | `infisical://dev-baile/garage/access_key_id` | S3 access key for the lakehouse-garage instance. |
| `AWS_SECRET_ACCESS_KEY` | string | yes (prod) | `infisical://dev-baile/garage/secret_access_key` | S3 secret access key. |
| `AWS_ENDPOINT_URL` | string | yes (prod) | `infisical://dev-baile/garage/s3_endpoint` | Canonical: `http://lakehouse-garage:3900`. |
| `AWS_REGION` | string | no (default `garage`) | env block only | S3 region. The literal string `garage` (the Garage instance name). |
| `AWS_DEFAULT_REGION` | string | no (default `garage`) | env block only | Fallback if `AWS_REGION` unset. |
| `GARAGE_ACCESS_KEY_ID` | string | yes (prod) | `infisical://dev-baile/garage/access_key_id` | Same as `AWS_ACCESS_KEY_ID`; the `GARAGE_*` prefix is a backward-compat alias. |
| `GARAGE_SECRET_ACCESS_KEY` | string | yes (prod) | `infisical://dev-baile/garage/secret_access_key` | Same as `AWS_SECRET_ACCESS_KEY`. |
| `GARAGE_RPC_SECRET` | string | yes (prod) | `infisical://dev-baile/lakehouse/rpc_secret` | Garage internal RPC secret. |
| `GARAGE_ADMIN_TOKEN` | string | yes (prod) | `infisical://dev-baile/lakehouse/admin_token` | Garage admin API token. |

### Group 10 — Embedder / model registry (5 vars)

| Variable | Type | Required? | Resolved from | Description |
|:--|:--|:--|:--|:--|
| `CIANFHOGHLAIM_EMBED_MODEL` | string | yes | `infisical://dev-baile/embed/model` | Canonical: `BAAI/bge-m3`. Read by `cocoindex/_shared/_lifespan.py:103`. |
| `CIANFHOGHLAIM_EMBED_DIM` | int | yes | `infisical://dev-baile/embed/dim` | Canonical: `1024`. |
| `MLFLOW_EXPERIMENT_NAME` | string | no (default `dlt-pipelines`) | env block only | Default MLflow experiment for `dlt` pipelines. |
| `MLFLOW_S3_ENDPOINT_URL` | URL | yes (prod) | `infisical://dev-baile/lakehouse/s3_endpoint` | MLflow's S3 endpoint. Canonical: `http://lakehouse-garage:3900`. |
| `BIEP_REGISTRY_URI` | string | no (default `md:cianfhoghlaim`) | env block only | The v7 source-of-truth DuckDB registry location for the BIEP v3 notebook set. |

### Group 11 — Meaisinfhoghlaim + OCR backends (14 vars)

Added 2026-08-02 (post-trilogy-cleanup). Covers the 7 OCR backend stacks
(`paddleocr` + `dots-ocr` + `olmocr` + `docling-serve` + `mlx-omni` +
`llama-swap` + `meaisinfoghlaim`) plus the `ocr-router` capability router
and the `agent-os` cross-cutting stack. Backend URL vars are resolved at
container runtime by the bons-locket-shim against the `dev-baile` Infisical
project; the literals in the *default* column are the canonical in-cluster
values, never hardcoded in production secrets.

| Variable | Type | Required? | Resolved from | Description |
|:--|:--|:--|:--|:--|
| `FALKORDB_HOST` | string | yes | env block only | Canonical: `falkordb`. The Redis-protocol graph backend host used by Graphiti (knowledge-graph triangulation in the agents layer). |
| `FALKORDB_PORT` | int | yes (default `6379`) | env block only | Port. Canonical: `6379` (the Redis default). |
| `FALKORDB_PASSWORD` | string | yes (prod) | `infisical://dev-baile/falkordb/password` | FalkorDB auth password. Required when running the Graphiti stack in production. |
| `CONFLUENT_API_KEY` | string | yes (prod) | `infisical://dev-baile/confluent/api_key` | Confluent Cloud API key for the `confluent-kafka` Kafka client (used by RisingWave + agent event streaming). |
| `CONFLUENT_API_SECRET` | string | yes (prod) | `infisical://dev-baile/confluent/api_secret` | Confluent Cloud API secret (paired with `CONFLUENT_API_KEY`). |
| `CONFLUENT_BOOTSTRAP_SERVERS` | string | yes (prod) | `infisical://dev-baile/confluent/bootstrap_servers` | Confluent Cloud bootstrap servers (canonical: `pkc-xxxxx.us-east-1.aws.confluent.cloud:9092`). |
| `PADDLEOCR_URL` | URL | yes | env block only | Canonical: `http://paddleocr:8000/v1`. Endpoint for the `forms` capability (used by `umeaisínfhoghlaim.ocr.adapters`). |
| `DOCLING_URL` | URL | yes | env block only | Canonical: `http://docling-serve:5001/v1`. Endpoint for the `doctags` capability (IBM Docling). |
| `DOTS_OCR_URL` | URL | yes | env block only | Canonical: `http://dots-ocr:8001/v1`. Endpoint for the `tesseract-fallback` capability. |
| `UNSTRACT_URL` | URL | yes | env block only | Canonical: `http://unstract:8002/v1`. Endpoint for the Unstract LLM-friendly parser (alternative to docling-serve). |
| `HF_TOKEN` | string | yes (prod) | `infisical://dev-baile/huggingface/token` | HuggingFace Hub token — used by `llama-swap`, `mlx-omni`, `docling-serve`, `olmocr` for on-demand model downloads. |
| `SLACK_WEBHOOK_URL` | URL | no (optional) | `infisical://dev-baile/slack/webhook_url` | Optional Slack incoming-webhook URL for agent ops alerts (used by `meaisinfhoghlaim/observability`). Empty by default — graceful skip. |
| `OCR_WEBHOOK_URL` | URL | no (optional) | `infisical://dev-baile/ocr-router/webhook_url` | OCR completion webhook (per the BIEP v3 spec delta). Empty = graceful skip (no emission). |
| `LITELLM_BASE_URL` | URL | yes | env block only | Canonical: `http://litellm:4000/v1`. The OpenAI-compatible base URL that all agent-OS instances and the 12-agent fleet point at. |

## Why these groups

This document now covers **62 canonical env vars** (up from 17 in the
2026-07-30 baseline, 48 in the 2026-08-01 drift-audit baseline). The 17
observability vars in Groups 1-4 remain the most-critical reference for
any tracing-related question — if you are debugging Langfuse, MLflow, or
Logfire wiring, start there. The 31 additional vars in Groups 5-10
were added as part of the 2026-08-02 drift-audit remediation to give the
data-platform team a single canonical reference for the BIEP ingestion
→ DuckLake → MotherDuck → LanceDB pipeline. The 14 new vars in Group
11 were added by the 2026-08-02 post-trilogy-cleanup pass to cover the
meaisinfhoghlaim + 6 OCR backends + ocr-router + agent-os surface.
Groups 5-11 are scoped to the data + agent plane; per-LLM-provider
keys remain out of scope (see `docs/llm-env-var-contract.md` TODO).

## How the 62 variables flow through the platform

```
Operator's .env (local)
  │
  ▼
mise run secrets:init          (syncs to Infisical)
  │
  ▼
Infisical dev-baile vault
  │
  ├─► bons-locket-shim (sidecar in 86 of 91 stacks)
  │     │
  │     ▼
  │   /run/secrets/locket/secrets.env (resolved values)
  │     │
  │     ▼
  │   service's env block  (e.g. graphiti, cognee, mlflow, agent-os)
  │
  └─► otelcol.yaml (logfire stack)
        │
        ├─► logfire exporter → logfire cloud
        └─► otlphttp/langfuse exporter → langfuse-web:3000/api/public/otel
```

The **single pane of glass** invariant: every trace that reaches the
collector reaches BOTH backends.

## Per-stack wireup matrix

Quick reference for which stacks read which vars. **✓** = declared in
`compose.yaml`; **L** = resolved by Locket from `secrets.env`.

| Stack | LANGFUSE_HOST | LANGFUSE_PUBLIC_KEY | LANGFUSE_SECRET_KEY | MLFLOW_TRACKING_URI | OTEL_EXPORTER_OTLP_ENDPOINT | OTEL_SERVICE_NAME |
|:--|:-:|:-:|:-:|:-:|:-:|:-:|
| graphiti | ✓ L | ✓ L | ✓ L | — | ✓ L | `graphiti` |
| cognee | ✓ L | ✓ L | ✓ L | — | ✓ L | `cognee` |
| mlflow | — | — | — | ✓ L (server-side) | ✓ L | `mlflow` |
| agent-os (×4) | ✓ L | ✓ L | ✓ L | — | — | — |
| dagster | ✓ L | ✓ L | ✓ L | — | ✓ env | `dagster` |
| openclaw | ✓ L | ✓ L | ✓ L | — | ✓ L | `openclaw-gateway` |
| openchamber | — | — | — | — | ✓ L | `openchamber` |
| hermes | ✓ L | ✓ L | ✓ L | — | ✓ L | `hermes-agent` |
| litellm | ✓ L | ✓ L | ✓ L | ✓ L | — | — |
| logfire (collector) | — | ✓ L | ✓ L | — | — | — |

## CI gate

The grammar + wireup invariant is enforced by the mise task:

```bash
mise run stack-doctor:strict
```

This runs `bash scripts/stack-doctor.sh --strict --check-grammar` which:

1. Fails any `secrets.env` with mixed bare + Jinja grammar
2. Fails any `secrets.env` with zero `infisical://` URIs
3. (Future) Fails any stack that declares `${LANGFUSE_*}` in compose.yaml but lacks the matching `infisical://...` line in `secrets.env`

The third check is the contract-enforcement for this table — it
prevents the "silent Langfuse loss" pattern (the agent-os bug fixed
in this change).

## Why 17 + 31 + 14 = 62 variables (not 50)?

The 17 observability variables are the **set that spans the full
observability stack** — every variable in Groups 1-4 is read by at
least 2 stacks; every Langfuse / MLflow / Logfire / OTel use case is
covered.

The 31 additional variables in Groups 5-10 are the **set that
spans the data plane** — every variable in Groups 5-10 is read by
at least one dlt pipeline, BAML extraction, CocoIndex flow, or
MotherDuck federated query path.

Variables that exist but are NOT in this 48-var contract:
- Per-service debug knobs (`LOG_LEVEL`, `LOGFIRE_VERBOSITY`,
  `OTEL_LOG_LEVEL`)
- Per-LLM-provider keys (`OPENAI_API_KEY`, `ANTHROPIC_API_KEY`,
  `GEMINI_API_KEY`, `KIMI_API_KEY`, `DEEPSEEK_API_KEY`, `ZAI_API_KEY`,
  `MINIMAX_API_KEY`, `MIMO_API_KEY`) — see
  `docs/llm-env-var-contract.md` (TODO)
- Per-stack port mappings — see `infrastructure-stacks` spec
- Per-Langfuse-project keys (one set per project, all templated
  from the same 4 Group-1 vars)

## Cross-references

- `.agents/skills/agent-observability/SKILL.md` — the operator-facing usage guide
- `.agents/skills/secrets-management/SKILL.md` — the Infisical + Locket + mise contract
- `openspec/changes/2026-07-30-.../specs/agent-observability/spec.md` — the formal requirement
- `bonneagar/stacks/logfire/config/otelcol.yaml` — the fan-out collector config
- `dlt_sources/common/observability.py` — the canonical DLT instrumentation helper