# 2026-08-23-lakehouse-production-config-and-lance-sidecar-modernization-v1

## Why

PR #2 of the **4-PR lakehouse hardening series** (after PR #1 fixed config hygiene). This change addresses **production readiness + the Lance namespace sidecar rewrite** — the most impactful improvements identified in the post-consolidation reanalysis.

The upstream `lance-format/lance-namespace-impls/python/src/lance_namespace_impls/iceberg.py` (the canonical Iceberg REST Catalog implementation for Lance) **already implements the exact logic our custom 567-LOC FastAPI sidecar reinvents**:

- Talks to Iceberg REST Catalogs (like Lakekeeper)
- Handles the `table_type=lance` property hack for registering Lance tables as "trojan horse" Iceberg tables
- Implements the `LanceNamespace` interface (list_namespaces, create_namespace, declare_table, describe_table, etc.)
- Caches warehouse prefix

Our custom `lakehouse/lance-sidecar/main.py` was a hand-rolled reimplementation of this. This change **adopts the official libraries** (`lance-namespace>=0.11.1`, `lance-namespace-urllib3-client>=0.11.1`, `lance-namespace-impls[iceberg]>=0.4.1`) and replaces ~567 LOC with ~150 LOC of thin FastAPI wrapper.

Other improvements addressed in this PR:

1. **Lakekeeper missing 10+ production env vars** from official docs (read replica routing, metrics port, pagination, OpenID, OpenFGA, caches, x-forwarded-headers)
2. **Cognee uses legacy `USE_UNIFIED_PROVIDER=pghybrid`** instead of new Cognee Dataset Database Handlers pattern (per official Cognee docs)
3. **FalkorDB uses inline `command:` args** instead of official `REDIS_ARGS` + `FALKORDB_ARGS` env vars
4. **Cognee uses shared `lakekeeper` superuser** instead of dedicated cognee user (security best-practice per Lakekeeper docs)
5. **No OpenTelemetry collector** for Langfuse + Logfire fan-out (PR #4 will use it)

## User preferences (locked-in from prior turns)

| Decision | Choice |
|:--|:--|
| Lance Namespace sidecar | **Full rewrite using official libs** |
| Ship strategy | **This is PR #2 of 4** — ship separately |
| Observability stack | **Langfuse + MLflow + Logfire** (NOT Prometheus/Grafana) |
| Deprecated stacks | Keep as read-only shadow stacks |

## Dependencies

`Blocked by: none`
`Blocked by (soft): 2026-08-22-lakehouse-config-and-env-var-hardening-v1` (extends the same compose.yaml + secrets.env + init-db.sql)
`Affected repos: cianfhoghlaim` (single-repo change)

## What changes

### 1. Lance Namespace sidecar rewrite (1 file rewritten)
**File**: `bonneagar/stacks/lakehouse/lance-sidecar/main.py` (567 → ~150 LOC)

Replace the hand-rolled `RestClient` + custom Iceberg REST calls + 5 endpoint handlers with:
```python
from lance_namespace_impls.iceberg import IcebergNamespace

ns = IcebergNamespace(
    endpoint="http://lakekeeper:8181",
    auth_token="${LANCE_ICEBERG_AUTH_TOKEN}",
    root="${LANCE_ROOT}",
    connect_timeout=int("${ICEBERG_CONNECT_TIMEOUT_MILLIS:-10000}") // 1000,
    read_timeout=int("${ICEBERG_READ_TIMEOUT_MILLIS:-30000}") // 1000,
    max_retries=int("${ICEBERG_MAX_RETRIES:-3}"),
)
# FastAPI exposes the Lance REST API on top of ns
```

Keeps the same `table_type=lance` property hack + FastAPI surface (for backward compat with the existing lance-sidecar REST API that cogeen + graphiti + lancedb-viewer + 47 CocoIndex Apps consume).

**requirements.txt** additions:
```
lance-namespace>=0.11.1
lance-namespace-urllib3-client>=0.11.1
lance-namespace-impls[iceberg]>=0.4.1
pylance>=7.0.0
pyarrow>=15.0.0
```

### 2. Lance sidecar image publishing (1 NEW file)
**File**: `.github/workflows/build-lance-namespace-sidecar.yml`

CI workflow that:
- Triggers on PR merge to main with changes under `bonneagar/stacks/lakehouse/lance-sidecar/`
- Builds the sidecar image + pushes to `ghcr.io/cianfhoghlaim/lance-namespace-sidecar:v0.3.0` (semver)
- Lakehouse compose uses the pinned image (keep `build:` as fallback for local dev)

### 3. Lakekeeper production env vars (1 file modified + secrets updated)
**File**: `bonneagar/stacks/lakehouse/compose.yaml` + `secrets.env`

Add 10+ missing env vars from official Lakekeeper docs:
- `LAKEKEEPER__PG_HOST_R` / `LAKEKEEPER__PG_HOST_W` (read replica routing — defaults to single postgres)
- `LAKEKEEPER__METRICS__PORT=9100`
- `LAKEKEEPER__PAGINATION_SIZE_DEFAULT=1024` / `LAKEKEEPER__PAGINATION_SIZE_MAX=2048`
- `LAKEKEEPER__USE_X_FORWARDED_HEADERS=true` (for Pangolin reverse proxy)
- `LAKEKEEPER__CACHE__STC__ENABLED=true` (short-term credentials cache)
- `LAKEKEEPER__CACHE__WAREHOUSE__ENABLED=true` (warehouse metadata cache)
- `LAKEKEEPER__CACHE__WAREHOUSE__CAPACITY=1000`
- Documented (off by default): `LAKEKEEPER__OPENID_PROVIDER_URI`, `LAKEKEEPER__OPENFGA__ENDPOINT`, `LAKEKEEPER__INSTANCE_ADMINS` (production auth/authz)

### 4. Cognee Dataset Database Handlers (1 file modified)
**File**: `bonneagar/stacks/lakehouse/compose.yaml`

Replace legacy `USE_UNIFIED_PROVIDER: pghybrid` with the new Dataset Database Handlers pattern:
```yaml
# REMOVED:
USE_UNIFIED_PROVIDER: pghybrid

# NEW:
DB_PROVIDER: postgres
VECTOR_DB_PROVIDER: pgvector
GRAPH_DATABASE_PROVIDER: postgres  # or kuzu (separate openspec)
LANCEDB_PROVIDER: lancedb  # uses the Lance Namespace adapter
```

### 5. FalkorDB canonical env vars (1 file modified)
**File**: `bonneagar/stacks/lakehouse/compose.yaml`

Replace inline `command:` args with `REDIS_ARGS` + `FALKORDB_ARGS` env vars per official docs:
```yaml
falkordb:
  command: ["falkordb"]  # simplified — all args via env vars
  environment:
    REDIS_ARGS: "--requirepass ${FALKORDB_PASSWORD} --appendonly yes --appendfsync everysec --maxmemory 2gb --maxmemory-policy allkeys-lru"
    FALKORDB_ARGS: "THREAD_COUNT 8 CACHE_SIZE 50 TIMEOUT_MAX 60000 TIMEOUT_DEFAULT 30000 QUERY_MEM_CAPACITY 104857600"
    BROWSER: "1"
```

### 6. Cognee PostgreSQL user isolation (2 files modified)
**File**: `bonneagar/stacks/lakehouse/init-db.sql` + `compose.yaml`

Create dedicated `cognee` user (NOT shared superuser):
```sql
-- After CREATE DATABASE cognee_cianfhoghlaim:
CREATE USER cognee WITH PASSWORD '${COGNEE_POSTGRES_PASSWORD}';
GRANT ALL PRIVILEGES ON DATABASE cognee_cianfhoghlaim TO cognee;
GRANT ALL ON SCHEMA public TO cognee;  -- required for the pghybrid provider
```

Update Cognee compose env vars:
```yaml
# FROM:
COGNEE_POSTGRES_USER: ${POSTGRES_USER:-lakekeeper}
COGNEE_POSTGRES_PASSWORD: ${POSTGRES_PASSWORD:?...}
# TO:
COGNEE_POSTGRES_USER: ${COGNEE_POSTGRES_USER:-cognee}
COGNEE_POSTGRES_PASSWORD: ${COGNEE_POSTGRES_PASSWORD:?COGNEE_POSTGRES_PASSWORD must be set via Locket/Infisical}
```

### 7. OpenTelemetry collector (1 file modified — deferred profile)
**File**: `bonneagar/stacks/lakehouse/compose.yaml`

Add `otel-collector` service (optional profile `otel`):
- Receives OTLP from cognee, graphiti, memgraph, falkordb, lance-namespace, clickhouse, garage
- Fans out to Langfuse (`http://langfuse:3000/api/otlp`) + Logfire cloud (via `LOGFIRE_TOKEN`)
- NOT Prometheus/Grafana (per user preference)
- **NOT committed in PR #2** — only the compose service definition + a stub OTLP env var on each service. The collector image + config land in PR #4 (observability integration).

### 8. Quality gates (4 tasks)
- `openspec validate --strict` PASS
- `docker compose -f compose.yaml -f sidecar.yaml config --quiet` PASS
- `mise run cic:stack-doctor` PASS (no new criticals)
- `mise run lint:skills` / `lint:drift-docs` / `lint:registry` PASS

## Out of scope (deferred to PR #4)

- **OTel collector full config** + Langfuse/MLflow/Logfire service definitions in compose (PR #4)
- **Lance Namespace sidecar publishing to ghcr.io** via the new CI workflow (PR #2 includes the workflow definition; the actual publishing happens once merged + the workflow runs)
- **Lakekeeper OpenID/OpenFGA production auth** (off by default; only enabled when operator sets the env vars)

## Cross-references

- Spec delta: `openspec/changes/2026-08-23-lakehouse-production-config-and-lance-sidecar-modernization-v1/specs/infrastructure-stacks/spec.md`
- Tasks: `openspec/changes/2026-08-23-lakehouse-production-config-and-lance-sidecar-modernization-v1/tasks.md`
- Upstream: https://github.com/lance-format/lance-namespace-impls (iceberg adapter)
- Upstream: https://github.com/lance-format/lance-namespace (spec + urllib3 client)
- Lakekeeper docs: https://docs.lakekeeper.io/docs/latest/configuration/
- FalkorDB docs: https://docs.falkordb.com/operations/docker/
- Cognee docs: https://docs.cognee.ai/setup-configuration/overview
- Related change: `openspec/changes/2026-08-22-lakehouse-config-and-env-var-hardening-v1/` (PR #1 — prerequisite)
- Related archive: `openspec/changes/archive/2026-08-14-2026-08-15-dagster-load-path-repair-and-lakehouse-preflight-v1/`