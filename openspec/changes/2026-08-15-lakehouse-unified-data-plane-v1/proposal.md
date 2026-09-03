# 2026-08-15-lakehouse-unified-data-plane-v1

## Why

The 5 graph DB backends (Cognee + Graphiti + FalkorDB + Memgraph + LanceDB
Viewer) are deployed as separate Docker Compose stacks that each require
their own `docker compose up -d` invocation, Locket sidecar, secrets.env,
Pangolin blueprint, and Komodo registration:

```
bonneagar/stacks/cognee/compose.yaml      →  cognee + cognee-postgres (2 services)
bonneagar/stacks/graphiti/compose.yaml    →  graphiti + falkordb-local (2 services)
bonneagar/stacks/falkordb/compose.yaml    →  falkordb (1 service, BROWSER=1)
bonneagar/stacks/memgraph/compose.yaml    →  memgraph + memgraph-lab (2 services)
bonneagar/stacks/lancedb/compose.yaml     →  lancedb + rclone (2 services, profile=s3)
```

This fragmentation makes the data plane NOT self-sufficient — operators
must run **6 separate docker compose commands + 6 health checks + 6
Pangolin registrations** to bring up the complete data engineering
pipeline. Worse, the 5 stacks each declare their own **bridge network**
(not the shared `lakehouse_lakehouse` external network), so the graph
backends can't resolve `lakehouse-postgres` / `lakehouse-redis` /
`lakehouse-garage` by Docker DNS — the #1 critical gap per the
2026-07-29 full-tree audit.

This change consolidates the 5 graph DB stacks into the unified
`bonneagar/stacks/lakehouse/` Compose project — a single
`docker compose -f compose.yaml -f sidecar.yaml up -d` brings up all 16
services on the shared `lakehouse_lakehouse` network with one Locket
sidecar + one Pangolin blueprint + one Komodo registration. The 4
deprecated stacks (`cognee/`, `graphiti/`, `falkordb/`, `memgraph/`) get
1-line deprecation banners pointing at the unified stack; `lancedb/`
also becomes a banner (its viewer is already part of lakehouse).

### User decisions

| Decision | Choice |
|:--|:--|
| Consolidation scope | **Full consolidation** into existing `bonneagar/stacks/lakehouse/compose.yaml` (not a new directory) |
| Cognee DB host | **Shared `lakehouse-postgres`** with new `cognee_cianfhoghlaim` database (drop the dedicated `cognee-postgres` container) |
| FalkorDB persistence | **AOF enabled** (`--appendonly yes --appendfsync everysec`) + production `FALKORDB_ARGS=THREAD_COUNT 8 CACHE_SIZE 50 TIMEOUT_MAX 60000` |
| Deprecated stacks | **Banner only** (not deletion) — readable but not the canonical path |
| New databases | **Only `cognee_cianfhoghlaim`** (graphiti uses falkordb; memgraph is Bolt + in-memory; both don't need Postgres) |

## Dependencies

`Blocked by: none`
`Blocked by (soft): 2026-08-14-2026-08-15-dagster-load-path-repair-and-lakehouse-preflight-v1` (this change extends the preflight to the 4 new graph DB endpoints)
`Affected repos: cianfhoghlaim` (single-repo change — bonneagar is now a subdirectory of cianfhoghlaim post-v7)

## What changes

### 1. The unified 16-service compose (1 file modified)

`bonneagar/stacks/lakehouse/compose.yaml` grows from 11 to 16 services.
The 5 new services join the shared `lakehouse_lakehouse` external network
(no per-stack bridge networks for graph backends anymore):

| # | Service | Container | Image | Purpose |
|--:|:--|:--|:--|:--|
| 1-11 | garage + garage-init + postgres + clickhouse + redis + lakekeeper-migrate + lakekeeper + lance-namespace + nimtable + olake + lancedb-viewer | unchanged | unchanged | existing lakehouse data plane |
| **12** | **`cognee`** | `lakehouse-cognee` | `cognee/cognee:1.2.2` | knowledge graph builder (6 datasets: aistear + primary + JC + SC + tertiary + cross_stage) |
| **13** | **`graphiti`** | `lakehouse-graphiti` | `graphiti:local` | bi-temporal KG API |
| **14** | **`falkordb`** | `lakehouse-falkordb` | `falkordb/falkordb:v4.18.11` | Redis-protocol graph DB + vector.so for hybrid queries |
| **15** | **`memgraph`** | `lakehouse-memgraph` | `memgraph/memgraph-mage:3.6.0` | Bolt-protocol graph DB + MAGE algorithms |
| **16** | **`memgraph-lab`** | `lakehouse-memgraph-lab` | `memgraph/lab:3.6.0` | Web UI for Memgraph |

Cognee uses the **shared lakehouse-postgres** at
`postgresql://lakekeeper:${POSTGRES_PASSWORD}@postgres:5432/cognee_cianfhoghlaim`
(NO separate `cognee-postgres` container). Graphiti uses the unified
falkordb container at `falkordb:6379`. Memgraph is Bolt-only + in-memory
(no Postgres needed). Memgraph-lab connects to memgraph at
`memgraph:7687`. Lancedb-viewer (existing) already covers the LanceDB
vector viewer use case.

### 2. Cognee database on shared Postgres (1 file modified)

`bonneagar/stacks/lakehouse/init-db.sql` adds 1 new database
(`cognee_cianfhoghlaim`) — total 13 (12 + 1 new):

```sql
-- Cognee knowledge graph (added 2026-08-15-lakehouse-unified-data-plane-v1)
-- Replaces the dedicated cognee-postgres container that lived in
-- bonneagar/stacks/cognee/compose.yaml. Cognee now connects to the
-- shared lakehouse-postgres at database `cognee_cianfhoghlaim` with
-- USE_UNIFIED_PROVIDER=pghybrid (postgres for both vector + graph).
CREATE DATABASE cognee_cianfhoghlaim;
GRANT ALL PRIVILEGES ON DATABASE cognee_cianfhoghlaim TO lakekeeper;
```

(We do NOT add `graphiti_cianfhoghlaim` or `memgraph_cianfhoghlaim` —
Graphiti uses FalkorDB (Redis protocol), Memgraph is Bolt + in-memory.
Neither needs Postgres.)

### 3. Shared Locket sidecar (1 file modified)

`bonneagar/stacks/lakehouse/sidecar.yaml` keeps the existing single
Locket — no Locket per graph backend. The 4 new services
(cognee + graphiti + falkordb + memgraph) all depend on the unified
Locket + mount `lakehouse-secrets:/run/secrets/locket:ro`.

### 4. Extended secrets.env (1 file modified)

`bonneagar/stacks/lakehouse/secrets.env` grows from 163 to ~190 lines
with ~30 new keys. All keys use the canonical
`infisical://dev-baile/<svc>/<key>` URI form:

- Cognee keys (16): `COGNEE_LLM_MODEL`, `COGNEE_EMBEDDING_MODEL`,
  `COGNEE_POSTGRES_PASSWORD` (resolved from `POSTGRES_PASSWORD` at
  compose time), `LANCEDB_API_KEY`, `LANCEDB_NAMESPACE_TOKEN`, OTel +
  Langfuse + Galileo + LiteLLM + PLANETSCALE_DATABASE_URL
- Graphiti keys (5): `FALKORDB_PASSWORD`, `FALKORDB_GRAPHITI_DB`,
  `OPENAI_API_KEY`, `OPENAI_BASE_URL`, OTel + Langfuse
- FalkorDB keys (3): `FALKORDB_PASSWORD`, `VECTOR_MODULE_URL`,
  `CLUSTER_MODE`
- Memgraph keys (4): `MEMGRAPH_USER`, `MEMGRAPH_PASSWORD`,
  `MEMGRAPH_LICENSE_FILE_PATH`, OTel

### 5. Unified Pangolin blueprint (2 files modified)

`bonneagar/stacks/lakehouse/blueprint.yaml` grows from 7 to 11
private-resources (the 4 existing + 4 new + 2 existing kept):

- **existing**: lakehouse-admin, lakekeeper, lance-api, nimtable,
  olake, lancedb-viewer
- **NEW**: cognee (port 8000, `cognee.cianfhoghlaim.ie`),
  graphiti (port 8000, `graphiti.cianfhoghlaim.ie`),
  falkordb-browser (port 3000, `falkordb.cianfhoghlaim.ie`),
  memgraph-lab (port 3000, `memgraph.cianfhoghlaim.ie`)

`bonneagar/stacks/lakehouse/pangolin.yaml` becomes a single
multi-route dev declaration (the deprecated `cognee/pangolin.yaml` +
`graphiti/pangolin.yaml` + `falkordb/pangolin.yaml` + `memgraph/pangolin.yaml`
are kept as deprecated shadow stacks with banners).

### 6. Deprecation banners (5 files modified — banner only, content unchanged)

- `bonneagar/stacks/cognee/compose.yaml` — 1-line banner pointing at lakehouse
- `bonneagar/stacks/graphiti/compose.yaml` — 1-line banner
- `bonneagar/stacks/falkordb/compose.yaml` — 1-line banner
- `bonneagar/stacks/memgraph/compose.yaml` — 1-line banner
- `bonneagar/stacks/lancedb/compose.yaml` — 1-line banner (viewer already in lakehouse)

Banner format:
```yaml
# DEPRECATED 2026-08-15: this stack has been consolidated into
# `bonneagar/stacks/lakehouse/compose.yaml` per the
# 2026-08-15-lakehouse-unified-data-plane-v1 change. The standalone
# files (compose.yaml / sidecar.yaml / secrets.env / blueprint.yaml /
# pangolin.yaml / README.md) are kept as readable shadow stacks for
# one release cycle; they will be deleted in
# 2026-XX-XX-delete-deprecated-graph-db-stacks. Do NOT deploy this
# stack via Komodo — deploy the unified lakehouse instead.
```

### 7. Extended lakehouse preflight (1 file modified)

`scripts/lakehouse_preflight.py` adds the 4 graph DB endpoints to the
required set (was 5 endpoints → now 5 + 4 = 9 endpoints):

```
REQUIRED_ENDPOINTS (now 9):
  existing (5): Nimtable :3018, Olake :3901, LanceDB Viewer :8081,
                Lance sidecar :8182, Lakekeeper :8181
  new (4):      cognee     :8000,
                graphiti   :8000,
                falkordb   :6379 (TCP probe — was OPTIONAL),
                memgraph   :7687 (TCP probe — was OPTIONAL)

EXPECTED_DATABASES (now 13):
  existing (12): 6 ducklake_* + dagster_local + olake_state + nimtable + langfuse + mlflow + litellm
  new (1):       cognee_cianfhoghlaim
```

The 4 graph backends transition from OPTIONAL (graceful skip) to
REQUIRED (must respond). Operators that don't need graph memory can
still pass `--skip-cognify` to keep the old behaviour.

### 8. Komodo resource-sync trim (1 file modified)

`bonneagar/komodo/resource-syncs/bunchloch.toml` removes 5 graph DB
stack references from the bunchloch resource_path (cognee-bunchloch +
graphiti-bunchloch + falkordb-bunchloch + memgraph-bunchloch +
lancedb-bunchloch are gone — lakehouse-bunchloch is the single
unified entry point).

### 9. Canonical bring-up shell entry-point (1 file NEW)

`scripts/lakehouse_unified_up.sh` — the canonical shell entry-point
for the unified stack. Wraps:

```bash
docker compose -f compose.yaml -f sidecar.yaml up -d
sleep 30  # wait for healthchecks
mise run lakehouse:preflight  # validate
```

Plus aliases for down (`scripts/lakehouse_unified_down.sh` is a 1-line
companion).

### 10. mise.toml task aliases (1 file modified)

Adds 3 new tasks:

```toml
[tasks."lakehouse:up"]      # canonical bring-up = scripts/lakehouse_unified_up.sh
[tasks."lakehouse:down"]    # canonical teardown = scripts/lakehouse_unified_down.sh
[tasks."lakehouse:preflight:unified"]  # alias for lakehouse:preflight --strict-cognify
```

### 11. Updated README (1 file modified)

`bonneagar/stacks/lakehouse/README.md` documents the 16-service
unified stack + the 5 deprecation banners + the 1 canonical bring-up
command + the 9-endpoint preflight.

## Out of scope (explicit deferrals)

- The 5 deprecated stacks are NOT removed (banner only). They will be
  deleted in a follow-up change `2026-XX-XX-delete-deprecated-graph-db-stacks`
  after one release cycle.
- The 619 dead placeholder YAMLs (per previous user decision).
- L3 cognify + federated_ocr `automation_condition: manual` (prior change).
- 3 `defs.yaml.planned` files (kept as recovery markers).
- Cross-region pipelines (american_nations, commonwealth,
  european_nations, european_union).
- Bringing up the cognify stack automatically in BIEP M1-M4 (still
  opt-in via `mise run lakehouse:preflight --strict-cognify`).
- Removing the existing 4 `pangolin.yaml` files in the deprecated stacks
  (they're harmless once they have the banner).
- Updating the `agent-platform-cluster` spec — it lists cognee +
  graphiti + lancedb as separate stacks; will be updated in a
  follow-up change after this ships.

## Cross-references

- Spec delta: `openspec/changes/2026-08-15-lakehouse-unified-data-plane-v1/specs/infrastructure-stacks/spec.md`
- Tasks: `openspec/changes/2026-08-15-lakehouse-unified-data-plane-v1/tasks.md`
- Canonical skill: `.agents/skills/infrastructure-stacks/SKILL.md`
  (post-archive update will reference this change)
- Canonical skill: `.agents/skills/agent-memory-systems/SKILL.md`
  (post-archive update will document the unified graph DB layer)
- Related archive: `openspec/changes/archive/2026-07-29-2026-08-15-centralized-model-schema-registry-and-deployment-control-panel-v1/`
- Related archive: `openspec/changes/archive/2026-07-29-2026-08-15-knowledge-sync-loop-v1/`
- Related archive: `openspec/changes/archive/2026-08-14-2026-08-15-dagster-load-path-repair-and-lakehouse-preflight-v1/`