# Lakehouse — Unified Data Plane + Graph DB Stack

## Overview

The lakehouse stack is the **single canonical entry point** for the entire Cianfhoghlaim data plane. As of 2026-08-15 (`2026-08-15-lakehouse-unified-data-plane-v1`), it hosts **16 services** in one Docker Compose project on one shared network:

- **11 data plane services** — Garage S3, Lakehouse Postgres, ClickHouse, Redis, Lakekeeper (Iceberg REST), Lance Namespace sidecar, Nimtable UI, Olake CDC, LanceDB Viewer, garage-init, lakekeeper-migrate
- **5 graph DB backends** — Cognee (knowledge graph builder) + Graphiti (bi-temporal KG) + FalkorDB (vector+graph hybrid) + Memgraph (Bolt+MAGE) + Memgraph Lab (Web UI)

Bring up the entire data plane with one command:

```bash
mise run lakehouse:up
# (or: docker compose -f compose.yaml -f sidecar.yaml up -d  from this directory)
```

## Why This Matters for Kings' College Galway

This is the single most important infrastructure stack. It provides ACID transactions on object storage via Iceberg tables, enabling time-travel queries on curriculum data (e.g., "show me the syllabus as it existed before the 2023 reform"). The Lance Namespace sidecar bridges LanceDB's vector format with Iceberg's catalog, allowing semantic search over vector embeddings to coexist with SQL analytics over structured tables. DuckLake tables built on Garage S3 are registered in the Iceberg catalog, making them queryable from Dagster, marimo notebooks, and the web app through a single namespace.

The 3 services added in `extend-lakehouse-with-nimtable-olake-lancedb` complete the over-engineered dev experience:

- **Nimtable** — a Spring-Boot web UI on top of Lakekeeper so contributors can browse tables, schemas, and snapshots without `curl`
- **Olake** — an open-source CDC engine that streams Postgres / MySQL / MongoDB changes into Iceberg on Garage
- **LanceDB Viewer** — a Web UI for browsing LanceDB tables (the same vector store used by croilar + meaisínfhoghlaim agents)

The 5 graph DB services added in `2026-08-15-lakehouse-unified-data-plane-v1` complete the AI memory layer:

- **Cognee** — knowledge graph builder with 6 datasets (aistear + primary + JC + SC + tertiary + cross_stage); uses shared lakehouse-postgres at `cognee_cianfhoghlaim` database (no separate cognee-postgres container)
- **Graphiti** — bi-temporal knowledge graph API using FalkorDB as the graph backend
- **FalkorDB** — Redis-protocol graph DB with AOF persistence + vector.so hybrid queries (`THREAD_COUNT 8 CACHE_SIZE 50 TIMEOUT_MAX 60000`)
- **Memgraph** — Bolt-protocol in-memory graph DB with MAGE algorithms
- **Memgraph Lab** — Web UI for Memgraph (Cypher IDE + graph visualisation)

## Unified Graph DB Backends (added 2026-08-15)

The 5 graph DB backends previously lived as separate Docker Compose stacks under `bonneagar/stacks/{cognee,graphiti,falkordb,memgraph,lancedb}/`. The 2026-08-15 unification change collapses them into this single `bonneagar/stacks/lakehouse/` project — one `docker compose up -d` brings up the entire data plane.

| Service | Image | Container | Port | Purpose |
|:--|:--|:--|--:|:--|
| `cognee` | `cognee/cognee:1.2.2` | `lakehouse-cognee` | 8000 | Knowledge graph builder (6 datasets, pghybrid backend on shared lakehouse-postgres) |
| `graphiti` | `graphiti:local` | `lakehouse-graphiti` | 8001 | Bi-temporal KG API (FalkorDB backend) |
| `falkordb` | `falkordb/falkordb:v4.18.11` | `lakehouse-falkordb` | 6379 + 3000 | Redis-protocol graph DB + vector.so hybrid (AOF persistence) |
| `memgraph` | `memgraph/memgraph-mage:3.6.0` | `lakehouse-memgraph` | 7687 + 7444 | Bolt-protocol in-memory graph DB + MAGE |
| `memgraph-lab` | `memgraph/lab:3.6.0` | `lakehouse-memgraph-lab` | 3001 | Web UI for Memgraph (Cypher IDE + graph viz) |

### Why consolidate?

The 5 separate stacks each declared their own bridge network (NOT the shared `lakehouse_lakehouse` external network), so the graph backends couldn't resolve `lakehouse-postgres` / `lakehouse-redis` / `lakehouse-garage` by Docker DNS — the #1 critical gap per the 2026-07-29 full-tree audit. The unified stack joins all 16 services to `lakehouse_lakehouse` and uses the single shared Locket sidecar.

## Key Features

- **Iceberg ACID on S3** — Lakekeeper provides snapshot isolation, time travel, and schema evolution on Garage S3
- **Lance + Iceberg bridge** — Custom lance-namespace sidecar registers LanceDB vector tables as Iceberg tables
- **Nimtable catalog UI** — Spring-Boot web UI at `http://localhost:3018` for browsing tables, schemas, and snapshots
- **Olake CDC engine** — Open-source CDC engine for streaming external Postgres/MySQL/MongoDB into Iceberg
- **LanceDB table viewer** — Web UI at `http://localhost:8081` for browsing LanceDB tables
- **Cognee KG builder** — 6-dataset knowledge graph builder using pgvector + Postgres graph
- **Graphiti bi-temporal KG** — temporal knowledge graph API with FalkorDB backend
- **FalkorDB hybrid** — graph + vector queries in one engine (AOF persistence enabled)
- **Memgraph + Lab** — production graph DB + Web UI for Cypher queries
- **PlanetScale-backed catalog** — Production-grade MySQL for catalog metadata (schema, partition specs, snapshots)
- **Single namespace** — All tables (DuckLake SQL + LanceDB vectors + Olake-ingested CDC + KG nodes/edges) queryable through one Iceberg catalog

## Deployment

### One-command bring-up (recommended)

```bash
mise run lakehouse:up
# Brings up all 16 services + runs mise run lakehouse:preflight
```

### Docker Compose (Local)

```bash
docker compose -f compose.yaml -f sidecar.yaml up -d
```

### Docker Compose (Production with Locket)

```bash
docker compose -f compose.yaml -f sidecar.yaml up -d
# Locket resolves all secrets from Infisical (dev-baile vault)
```

### Komodo (GitOps)

Deployed via Komodo on bunchloch. Locket resolves `GARAGE_RPC_SECRET`, `GARAGE_ADMIN_TOKEN`, `LAKEKEEPER_ENCRYPTION_KEY`, `FALKORDB_PASSWORD`, `MEMGRAPH_PASSWORD`, `COGNEE_POSTGRES_PASSWORD`, etc. from Infisical.

## Environment Variables

| Variable | Required | Description | Default |
|:--|:--|:--|:--|
| `GARAGE_RPC_PORT` | No | Garage RPC port | `3901` |
| `GARAGE_S3_API_PORT` | No | S3 API port | `3900` |
| `GARAGE_K2V_API_PORT` | No | K2V API port | `3902` |
| `GARAGE_WEB_PORT` | No | Web console port | `3903` |
| `GARAGE_ADMIN_PORT` | No | Admin API port | `3904` |
| `GARAGE_RPC_SECRET` | Yes | 64-char hex secret for inter-node encryption | dev default |
| `GARAGE_ADMIN_TOKEN` | Yes | Admin token for Garage CLI operations | dev default |
| `LAKEKEEPER_ENCRYPTION_KEY` | Yes | 64-char hex key for catalog encryption at rest | — |
| `POSTGRES_PASSWORD` | Yes | lakehouse-postgres password (shared by 13 databases) | — |
| `FALKORDB_PASSWORD` | Yes | FalkorDB auth password | — |
| `MEMGRAPH_PASSWORD` | Yes | Memgraph auth password | — |
| `COGNEE_LLM_MODEL` | No | LiteLLM model alias | `deepseek/deepseek-chat` |
| `COGNEE_EMBEDDING_MODEL` | No | LiteLLM embedding alias | `openai/text-embedding-3-small` |
| `GRAPHITI_PORT` | No | Graphiti host port | `8001` |
| `MEMGRAPH_LAB_PORT` | No | Memgraph Lab host port | `3001` |
| `NIMTABLE_PORT` | No | Nimtable catalog UI host port | `3018` |
| `LANCEDB_VIEWER_PORT` | No | LanceDB viewer host port | `8081` |
| `RUST_LOG` | No | Log level | `garage=info` |
| `RUST_BACKTRACE` | No | Backtrace on panic | `1` |

## Access

### Local (dev)

- **Lakekeeper REST API**: `http://localhost:8181`
- **Lance Namespace**: `http://localhost:8182`
- **Garage S3**: `http://localhost:3900`
- **Nimtable catalog UI**: `http://localhost:3018` (Iceberg table browser)
- **LanceDB viewer**: `http://localhost:8081` (LanceDB table browser)
- **Olake CDC engine**: admin via `docker exec` (ephemeral port)
- **Cognee REST API**: `http://localhost:8000` (knowledge graph builder)
- **Graphiti REST API**: `http://localhost:8001/healthcheck` (bi-temporal KG)
- **FalkorDB Browser**: `http://localhost:3000` (graph + vector queries)
- **Memgraph Bolt**: `bolt://localhost:7687` (Cypher queries)
- **Memgraph Lab**: `http://localhost:3001` (Cypher IDE + graph viz)

### Production (Pangolin)

- `lakehouse.cianfhoghlaim.ie` → Lakekeeper :8181
- `lance-api.cianfhoghlaim.ie` → Lance sidecar :8182
- `nimtable.cianfhoghlaim.ie` → Nimtable UI :3018
- `olake.cianfhoghlaim.ie` → Olake admin :8080
- `lance-viewer.cianfhoghlaim.ie` → LanceDB viewer :8081
- `cognee.cianfhoghlaim.ie` → Cognee :8000
- `graphiti.cianfhoghlaim.ie` → Graphiti :8001
- `falkordb.cianfhoghlaim.ie` → FalkorDB Browser :3000
- `memgraph.cianfhoghlaim.ie` → Memgraph Lab :3001

## Service Inventory

| # | Service | Container | Port | Image | Notes |
|--:|:--|:--|:--|:--|:--|
| 1 | Garage | `lakehouse-garage` | 3900/3901/3903/3904 | `dxflrs/garage:v2.3.0` | S3-compatible object storage |
| 2 | Garage-init | `lakehouse-garage-init` | ephemeral | `curlimages/curl:latest` | Bucket initialization |
| 3 | Postgres | `lakehouse-postgres` | 5432 → 5433 | `postgres:16-alpine` | 13 databases (12 + cognee_cianfhoghlaim) |
| 4 | ClickHouse | `lakehouse-clickhouse` | 8123/9000 → 127.0.0.1 | `clickhouse/clickhouse-server:25.8` | Columnar engine (consumed by langfuse) |
| 5 | Redis | `lakehouse-redis` | 6379 → 127.0.0.1 | `redis:7-alpine` | Queue + cache (consumed by langfuse) |
| 6 | Lakekeeper-migrate | `lakehouse-lakekeeper-migrate` | ephemeral | `quay.io/lakekeeper/catalog:v0.13.1` | DB migrations |
| 7 | Lakekeeper | `lakehouse-lakekeeper` | 8181 | `quay.io/lakekeeper/catalog:v0.13.1` | Iceberg REST catalog |
| 8 | Lance Namespace | `lakehouse-lance-namespace` | 8182 | `lakehouse-lance-namespace:latest` (built) | FastAPI sidecar |
| 9 | Nimtable | `lakehouse-nimtable` | 3000 → 3018 | `nimtable/nimtable:latest` | Iceberg catalog UI |
| 10 | Olake | `lakehouse-olake` | ephemeral | `ghcr.io/olake-io/olake:v0.8.0` | CDC engine |
| 11 | LanceDB Viewer | `lakehouse-lancedb-viewer` | 8080 → 8081 | `ghcr.io/gordonmurray/lance-data-viewer:lancedb-0.24.3` | LanceDB table viewer |
| **12** | **Cognee** | `lakehouse-cognee` | 8000 | `cognee/cognee:1.2.2` | **Knowledge graph builder (uses shared lakehouse-postgres)** |
| **13** | **Graphiti** | `lakehouse-graphiti` | 8001 | `graphiti:local` | **Bi-temporal KG API** |
| **14** | **FalkorDB** | `lakehouse-falkordb` | 6379 + 3000 | `falkordb/falkordb:v4.18.11` | **Graph + vector hybrid (AOF persistence)** |
| **15** | **Memgraph** | `lakehouse-memgraph` | 7687 + 7444 | `memgraph/memgraph-mage:3.6.0` | **Bolt graph DB + MAGE** |
| **16** | **Memgraph Lab** | `lakehouse-memgraph-lab` | 3000 → 3001 | `memgraph/lab:3.6.0` | **Memgraph Web UI** |
| -- | Locket | `lakehouse-locket` | ephemeral | `ghcr.io/bpbradley/locket:infisical` | Infisical secret injector (sidecar) |

## Preflight

`scripts/lakehouse_preflight.py` validates the 16-service stack via:

- **9 required endpoints** (5 data plane + 4 graph DB)
- **13 postgres databases** (12 + cognee_cianfhoghlaim)
- **8 Garage buckets** (iceberg + lance + ducklake + ducklake-cianfhoghlaim + langfuse-events + langfuse-media + langfuse-exports + mlflow-artifacts)

```bash
mise run lakehouse:preflight                        # human-readable
mise run lakehouse:preflight --json                 # machine-readable
mise run lakehouse:preflight --strict-cognify       # require 4 graph DB backends
```

## Observability (added 2026-08-25)

The 10 **application services** in the unified lakehouse stack emit OpenTelemetry traces via `OTEL_EXPORTER_OTLP_ENDPOINT`. Traces fan out to 3 backends:

- **Logfire cloud** (SaaS) via `LOGFIRE_TOKEN` env var
- **Langfuse** (self-hosted) via `LANGFUSE_PUBLIC_KEY` + `LANGFUSE_SECRET_KEY`
- **MLflow** (local tracking) via `MLFLOW_TRACKING_URI`

Two modes:
1. **Local mode** (`docker compose --profile otel up -d`) — uses the in-stack `otel-collector` service for fan-out
2. **Cross-stack mode** (production) — uses the existing `logfire-bunchloch` stack's `logfire-otel` collector

See `docs/observability/lakehouse-otel-fanout.md` for the full architecture.

The `lakehouse:stack-doctor` script enforces that every application service sets `OTEL_EXPORTER_OTLP_ENDPOINT` (storage infra + read-only web UIs are exempt).

## Cross-Stack Orchestration (added 2026-08-25)

```bash
# Bring up the COMPLETE data plane with one command
mise run lakehouse:all:up    # alias: data:all:up
# → lakehouse (16 services) → logfire → langfuse → mlflow → dagster
#    (in dependency order; verified via mise run lakehouse:preflight)

# Teardown in reverse order
mise run lakehouse:all:down  # alias: data:all:down
```

## Deprecated Stacks

The 5 standalone graph DB stacks (`cognee/`, `graphiti/`, `falkordb/`, `memgraph/`, `lancedb/`) carry 1-line deprecation banners pointing at this unified stack. They are kept as readable shadow stacks for one release cycle; deletion is deferred to `2026-XX-XX-delete-deprecated-graph-db-stacks`. **Do NOT deploy any of the deprecated stacks** — they will fail to resolve `lakehouse-postgres` by Docker DNS (the network is `lakehouse_lakehouse` external, not the deprecated stack's local bridge).

## Cross-Sruth Lakehouse Wiring

Every active srutha in the Cianfhoghlaim monorepo MUST wire into the canonical dev lakehouse via two contracts:

1. **`LANCEDB_URI=rest://lakehouse-lance-namespace:8182`** — every active srutha stack MUST default `LANCEDB_URI` to the lakehouse Lance namespace (not a local file path).
2. **`ducklake_{namespace}` database** — every active srutha MUST have a dedicated `ducklake_{namespace}` database in `bonneagar/stacks/lakehouse/init-db.sql` for DuckLake write-ahead-log storage.

The canonical factory for both contracts is `cianfhoghlaim/dlt_sources/destinations.py:with_namespace()` (the `with_namespace()` method at line 289 of the file).

## Upstream

- **Garage**: <https://git.deuxfleurs.fr/Deuxfleurs/garage> — v2.3.0
- **Lakekeeper**: <https://github.com/lakekeeper/lakekeeper> — v0.13.1
- **LanceDB**: <https://github.com/lancedb/lancedb> — embedded vector database with Iceberg support (v0.15+)
- **Cognee**: <https://github.com/topoteretes/cognee> — v1.2.2 (knowledge graph builder)
- **Graphiti**: <https://github.com/getzep/graphiti> — bi-temporal KG API
- **FalkorDB**: <https://github.com/falkordb/falkordb> — v4.18.11 (graph + vector hybrid)
- **Memgraph**: <https://github.com/memgraph/memgraph> — v3.6.0 (Bolt + MAGE)

## Screenshot

All services in this stack are headless APIs. Lakekeeper exposes a REST API at port 8181 with catalog metadata; Garage provides an S3-compatible API at port 3900 and a minimal web console at port 3903. Memgraph Lab at port 3001 provides a Cypher IDE + graph visualisation interface.