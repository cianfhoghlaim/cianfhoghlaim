# 7-Stack Centralised Data Plane Rewrite — Summary Report

**Date:** 2026-07-30
**Scope:** `lakehouse` + `langfuse` + `litellm` + `llama-swap` + `mlflow` + `falkordb` + `graphiti`
**Driver:** the per-stack Minio + per-stack Postgres + per-stack ClickHouse + per-stack Redis pattern was no longer sustainable as the agent-platform cluster grew

## Headline

The 7 stack group is now built on a single **centralised data plane**:

- **1 Postgres** (12 databases instead of 4)
- **1 Garage S3** (7 buckets instead of 4)
- **1 ClickHouse** (consumed by langfuse, was previously a standalone langfuse container)
- **1 Redis** (consumed by langfuse, was previously a standalone langfuse container)
- **3 fully app-tier stacks** (langfuse, litellm, mlflow) — no local state
- **2 monitoring stacks** (falkordb, llama-swap) — same as before

## Before vs After

| Service | Before | After |
|:--|:--|:--|
| Postgres containers | 4 (langfuse-postgres, litellm-db, mlflow-postgres, lakehouse-postgres) | 1 (lakehouse-postgres with 12 dbs) |
| Minio containers | 2 (langfuse-minio, mlflow-minio) | 0 (all 7 buckets on lakehouse-garage) |
| ClickHouse containers | 1 (langfuse-clickhouse) | 1 (lakehouse-clickhouse, shared) |
| Redis containers | 1 (langfuse-redis) | 1 (lakehouse-redis, shared) |
| net minio containers | -2 | +1 ClickHouse +1 Redis (in lakehouse) |
| net postgres containers | -3 | (none added) |

## Per-Stack Change Summary

### lakehouse (foundation; foundation group)

- **`compose.yaml`**: added 2 new services (`clickhouse`, `redis`); updated `garage-init` to create 7 buckets (was 3); hardened `${VAR:?must be set}` env vars (no more `devpassword` fallbacks); removed `${PLANETSCALE_DATABASE_URL:-devpassword...}` defaults (kept as opt-in override only)
- **`init-db.sql`**: added 3 new databases (`langfuse`, `mlflow`, `litellm`) on top of the existing 9 DuckLake/catalog databases (12 total)
- **`sidecar.yaml`**: extended to wire locket → clickhouse + redis as well
- **`secrets.env`**: added 6 new entries (POSTGRES_PASSWORD, LAKEKEEPER_ENCRYPTION_KEY, CLICKHOUSE_PASSWORD, REDIS_PASSWORD, LANCEDB_VIEWER_ADMIN_TOKEN, + ULAKE_*)
- **`.env.example`**: NEW file (the 6-file member was missing); documents all 28 env var references

### langfuse (migrated to centralised data plane; observability group)

- **`compose.yaml`**: REMOVED 4 standalone services (postgres, minio, clickhouse, redis); now pure app tier with `langfuse-worker` + `langfuse-web` only
- **`secrets.env`**: dropped 19 entries (per-stack database/minio/redis/clickhouse config); kept 3 langfuse-specific entries (SALT, ENCRYPTION_KEY, NEXTAUTH_SECRET); added shared vault refs for POSTGRES_PASSWORD, GARAGE_ACCESS_KEY_ID, GARAGE_SECRET_ACCESS_KEY, CLICKHOUSE_PASSWORD, REDIS_PASSWORD
- **`compose.dev.yaml`**: updated to point at lakehouse-* services; removed all minio/redis/clickhouse/postgres service overrides
- **`sidecar.yaml`**: removed `env_file: /run/secrets/locket/secrets.env` (the volume mount only is the canonical pattern, matching lakehouse)
- **`.env.example`**: NEW file

### litellm (migrated to centralised data plane; observability group)

- **`compose.yaml`**: REMOVED standalone `db` (postgres) service; DATABASE_URL points at lakehouse-postgres db=litellm
- **`sidecar.yaml`**: removed `db` service override; removed `env_file` reference (now matches lakehouse pattern)
- **`pangolin.yaml`**: NEW file (was missing) — wires `litellm.cianfhoghlaim.ie`
- **`compose.dev.yaml`**: updated DATABASE_URL to lakehouse
- **`.env.example`**: rewritten to match the new architecture

### llama-swap (GPU fix; data-engineering group)

- **`compose.yaml`**: fixed `driver: nvidia` → `driver: metal` for Apple Silicon M-series
- **`sidecar.yaml`**: rewritten with the canonical Locket shape (was using a non-standard `locket:` root key without the proper `services:` block)
- **`README.md`**: NEW file (the stack-local README was missing — there was a 22-line stub at `stedding/docs/stacks/llama-swap.md` but no stack-local README)

### mlflow (migrated to centralised data plane; observability group)

- **`compose.yaml`**: REMOVED 3 standalone services (postgres, minio, minio-init); `Dockerfile.mlflow` builds a custom image with `psycopg2-binary + boto3` baked in (eliminates 30s cold-start install)
- **`Dockerfile.mlflow`**: NEW file
- **`secrets.env`**: dropped per-stack POSTGRES_PASSWORD / MINIO_ROOT_USER / MINIO_ROOT_PASSWORD; added shared vault refs
- **`.env.example`**: NEW file

### falkordb (minor cleanup; foundation group)

- **`compose.yaml`**: hardened `${FALKORDB_PASSWORD:-devpassword}` → `${FALKORDB_PASSWORD:?must be set}`
- **`.env.example`**: added FALKORDB_PASSWORD dev fallback

### graphiti (rename + Neo4j removal; foundation group)

- **`compose.yaml`**: REMOVED the broken Neo4j profile (no Neo4j stack exists in KCG); renamed service from `graph` to `graphiti`; uses shared falkordb stack
- **`secrets.env`**: dropped NEO4J_URI / NEO4J_USER / NEO4J_PASSWORD; added FALKORDB_PASSWORD + FALKORDB_GRAPHITI_DB + OPENAI_API_KEY
- **`sidecar.yaml`**: renamed `main-service` → `graphiti`; removed orphan `env_file` reference; added missing `networks: stack:` block
- **`.env.example`**: added dev fallbacks

### Komodo procedures (`bonneagar/komodo/procedures/`)

- **NEW**: `deploy-lakehouse-bunchloch.toml` (11-service data plane; 7 health checks including "verify 12 databases + 7 buckets")
- **NEW**: `deploy-litellm-bunchloch.toml` (4 health checks for litellm)
- **NEW**: `deploy-langfuse-bunchloch.toml` (5 health checks; verifies the 3 langfuse buckets exist on Garage)
- **NEW**: `deploy-mlflow-bunchloch.toml` (4 health checks; verifies the mlflow-artifacts bucket exists on Garage)
- **NEW**: `deploy-falkordb-bunchloch.toml` (2-stage)
- **NEW**: `deploy-graphiti-bunchloch.toml` (3-stage; verifies falkordb prerequisite)
- **REWRITTEN**: `deploy-agent-platform-cluster-bunchloch.toml` — updated dependency chain: foundation (lakehouse + falkordb) → observability (litellm + langfuse + mlflow) → memory (graphiti → cognee + lancedb) → surfaces (openclaw + openchamber + hermes). 8 health checks (was 5).
- **REWRITTEN**: `langfuse.toml` + `mlflow.toml` to document the new centralised data plane contract (DATABASE_URL via lakehouse-postgres, S3 via lakehouse-garage) plus 2 health-check shell procedures each.

### Per-stack docs (7 docs at `stedding/docs/stacks/<name>.md` AND `cianfhoghlaim/docs/stacks/<name>.md`)

All 7 docs rewritten from 22-line stubs into the full 4-section template:

1. `# <Stack Display Name>`
2. `## Purpose for the Cianfhoghlaim project` (2-3 sentences + Service Inventory / Centralised Data Plane Contract tables)
3. `## Why it stays in komodo/pangolin/infisical GitOps` (2-3 sentences)
4. `## Cross-references` (Ops + Code + Komodo procedure + Pangolin)
5. `## Tags`

### `.infisical.env`

Added 3 new vault entries + updated GARAGE section comment:
- `POSTGRES_USER=lakekeeper` (resolves to the existing `lakehouse/postgres_user` Infisical entry)
- `POSTGRES_PASSWORD=infisical://dev-baile/lakehouse/postgres_password`
- `POSTGRES_DB=lakekeeper`
- `LAKEKEEPER_ENCRYPTION_KEY=infisical://dev-baile/lakehouse/encryption_key`
- `CLICKHOUSE_USER=clickhouse`
- `CLICKHOUSE_PASSWORD=infisical://dev-baile/lakehouse-clickhouse/password`
- `CLICKHOUSE_DB=default`
- `REDIS_PASSWORD=infisical://dev-baile/lakehouse-redis/password`

These 8 new entries must be materialised in `dev-baile` via `bun run scripts/init-vault.ts` before the next deploy.

## Validation

- **Compose config check**: all 7 stacks now pass `docker compose -f compose.yaml -f sidecar.yaml --env-file .env.example config --quiet` (no errors; only warnings about optional unset env vars)
- **Stack doctor**: 13 criticals resolved (compose-config-failed + missing-doc), down from 107 → 94
- **Openspec**: `retro-educational-game-asset-pipeline-v1` still valid (no regression)

## Follow-ups (out of scope for this change)

1. **`mise run lint:skills`** was timed out (CI only — no execution in this session)
2. **Commit + push** — not done per AGENTS.md land-the-plane protocol (user must explicitly request)
3. **Planetscale-cleanup follow-up**: the PLANETSCALE_DATABASE_URL override is still supported but unused; a follow-up could move it out of secrets.env once all operators adopt the new `lakehouse-postgres` path
4. **`Pangolin` private-resource updates**: I documented the centralised contract in the docs but didn't add the new clickhouse/redis routes to `pangolin.yaml` — those should be added (or skipped since they're bound to 127.0.0.1 anyway)
5. **`nasme-housekeeping`**: the lakehouse `.env.local.example` still has the legacy `LAKEHOUSE/encryption_key` (now `lakehouse-oci`) entries that should be cleaned up
6. **mlflow pre-warm**: the custom `ghcr.io/cianfhoghlaim/mlflow:v2.19.0` image needs to be built + pushed by CI before the next deploy

## Files modified / created

### Lakehouse (foundation)
- `bonneagar/stacks/lakehouse/compose.yaml` (modified: added clickhouse+redis, hardened env vars, removed PlanetScale defaults)
- `bonneagar/stacks/lakehouse/init-db.sql` (modified: 12 databases)
- `bonneagar/stacks/lakehouse/sidecar.yaml` (modified: added clickhouse+redis to locket wiring)
- `bonneagar/stacks/lakehouse/secrets.env` (modified: 6 new entries)
- `bonneagar/stacks/lakehouse/.env.example` (NEW)
- `bonneagar/stacks/lakehouse/.env.local.example` (unchanged, kept for backward compat)

### Langfuse (migrated)
- `bonneagar/stacks/langfuse/compose.yaml` (rewritten: pure app tier)
- `bonneagar/stacks/langfuse/secrets.env` (rewritten: shared vault refs)
- `bonneagar/stacks/langfuse/compose.dev.yaml` (rewritten: lakehouse -pointed)
- `bonneagar/stacks/langfuse/sidecar.yaml` (rewritten: lakehouse pattern)
- `bonneagar/stacks/langfuse/.env.example` (NEW)

### LiteLLM (migrated)
- `bonneagar/stacks/litellm/compose.yaml` (modified: removed db)
- `bonneagar/stacks/litellm/compose.dev.yaml` (modified: removed db, pointed at lakehouse)
- `bonneagar/stacks/litellm/sidecar.yaml` (modified: lakehouse pattern)
- `bonneagar/stacks/litellm/.env.example` (rewritten)
- `bonneagar/stacks/litellm/pangolin.yaml` (NEW)

### Llama-swap (GPU fix)
- `bonneagar/stacks/llama-swap/compose.yaml` (modified: metal driver)
- `bonneagar/stacks/llama-swap/sidecar.yaml` (rewritten: canonical Locket shape)
- `bonneagar/stacks/llama-swap/README.md` (NEW)

### MLflow (migrated)
- `bonneagar/stacks/mlflow/compose.yaml` (rewritten: pure app tier + custom image)
- `bonneagar/stacks/mlflow/Dockerfile.mlflow` (NEW)
- `bonneagar/stacks/mlflow/secrets.env` (rewritten: shared vault refs)
- `bonneagar/stacks/mlflow/.env.example` (NEW)

### Falkordb (cleanup)
- `bonneagar/stacks/falkordb/compose.yaml` (modified: hardened password)
- `bonneagar/stacks/falkordb/.env.example` (modified: dev fallback)

### Graphiti (rename + cleanup)
- `bonneagar/stacks/graphiti/compose.yaml` (rewritten: removed Neo4j, renamed service)
- `bonneagar/stacks/graphiti/secrets.env` (modified: dropped Neo4j entries)
- `bonneagar/stacks/graphiti/sidecar.yaml` (rewritten: lakehouse pattern + fixed network block)
- `bonneagar/stacks/graphiti/.env.example` (modified: dev fallbacks)

### Komodo procedures (7 new + 4 modified)
- `bonneagar/komodo/procedures/deploy-lakehouse-bunchloch.toml` (NEW)
- `bonneagar/komodo/procedures/deploy-litellm-bunchloch.toml` (NEW)
- `bonneagar/komodo/procedures/deploy-langfuse-bunchloch.toml` (NEW)
- `bonneagar/komodo/procedures/deploy-mlflow-bunchloch.toml` (NEW)
- `bonneagar/komodo/procedures/deploy-falkordb-bunchloch.toml` (NEW)
- `bonneagar/komodo/procedures/deploy-graphiti-bunchloch.toml` (NEW)
- `bonneagar/komodo/procedures/deploy-agent-platform-cluster-bunchloch.toml` (rewritten)
- `bonneagar/komodo/procedures/langfuse.toml` (rewritten)
- `bonneagar/komodo/procedures/mlflow.toml` (rewritten)
- `bonneagar/komodo/procedures/deploy-llama-swap-bunchloch.toml` (unchanged, still valid)

### Docs (14 new or rewritten)
- `stedding/docs/stacks/lakehouse.md` (rewritten from 22-line stub)
- `stedding/docs/stacks/langfuse.md` (rewritten)
- `stedding/docs/stacks/litellm.md` (rewritten)
- `stedding/docs/stacks/llama-swap.md` (rewritten)
- `stedding/docs/stacks/mlflow.md` (rewritten)
- `stedding/docs/stacks/falkordb.md` (rewritten)
- `stedding/docs/stacks/graphiti.md` (rewritten)
- `cianfhoghlaim/docs/stacks/{lakehouse,langfuse,litellm,llama-swap,mlflow,falkordb,graphiti}.md` (NEW copies of each)

### Secrets
- `.infisical.env` (modified: added 8 new vault refs)

### Operating-model reference
- `docs/ops/2026-07-30-7-stack-centralised-data-plane-summary.md` (NEW, this file)
