# Lakehouse — Unified Data Lakehouse Stack

## Overview

The lakehouse stack integrates Garage S3-compatible storage, Lakekeeper Iceberg REST Catalog, a Lance Namespace sidecar, the Nimtable Iceberg catalog UI, the Olake CDC engine, and the LanceDB table viewer into a single deployable unit. It is the primary data plane for the Kings' College Galway project — every curriculum Parquet file, every vector index, and every generated study asset passes through this stack. Uses PlanetScale (MySQL-compatible cloud DB) as the catalog metadata backend.

## Why This Matters for Kings' College Galway

This is the single most important infrastructure stack. It provides ACID transactions on object storage via Iceberg tables, enabling time-travel queries on curriculum data (e.g., "show me the syllabus as it existed before the 2023 reform"). The Lance Namespace sidecar bridges LanceDB's vector format with Iceberg's catalog, allowing semantic search over vector embeddings to coexist with SQL analytics over structured tables. DuckLake tables built on Garage S3 are registered in the Iceberg catalog, making them queryable from Dagster, marimo notebooks, and the web app through a single namespace.

The 3 services added in `extend-lakehouse-with-nimtable-olake-lancedb` complete the over-engineered dev experience:

- **Nimtable** — a Spring-Boot web UI on top of Lakekeeper so contributors can browse tables, schemas, and snapshots without `curl`
- **Olake** — an open-source CDC engine that streams Postgres / MySQL / MongoDB changes into Iceberg on Garage
- **LanceDB Viewer** — a Web UI for browsing LanceDB tables (the same vector store used by croilar + meaisínfhoghlaim agents)

## Key Features

- **Iceberg ACID on S3** — Lakekeeper provides snapshot isolation, time travel, and schema evolution on Garage S3
- **Lance + Iceberg bridge** — Custom lance-namespace sidecar registers LanceDB vector tables as Iceberg tables
- **Nimtable catalog UI** — Spring-Boot web UI at `http://localhost:3018` for browsing tables, schemas, and snapshots
- **Olake CDC engine** — Open-source CDC engine for streaming external Postgres/MySQL/MongoDB into Iceberg
- **LanceDB table viewer** — Web UI at `http://localhost:8081` for browsing LanceDB tables
- **PlanetScale-backed catalog** — Production-grade MySQL for catalog metadata (schema, partition specs, snapshots)
- **Single namespace** — All tables (DuckLake SQL + LanceDB vectors + Olake-ingested CDC) queryable through one Iceberg catalog

## Deployment

### Docker Compose (Local)

```bash
cd infrastructure/stacks/lakehouse
docker compose up -d
```

### Docker Compose (Production with Locket)

```bash
docker compose -f compose.yaml -f sidecar.yaml -f pangolin.yaml up -d
```

### Komodo (GitOps)

Deployed via Komodo on arm1-oci. Locket resolves `GARAGE_RPC_SECRET`, `GARAGE_ADMIN_TOKEN`, `LAKEKEEPER_DB_PASSWORD`, and `LAKEKEEPER_ENCRYPTION_KEY` from Infisical. PlanetScale connection string is injected via Locket.

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
| `LAKEKEEPER_DB_PASSWORD` | Yes | PlanetScale database password | — |
| `LAKEKEEPER_ENCRYPTION_KEY` | Yes | 64-char hex key for catalog encryption at rest | — |
| `LAKEKEEPER_S3_ACCESS_KEY` | Yes | Garage S3 access key | — |
| `LAKEKEEPER_S3_SECRET_KEY` | Yes | Garage S3 secret key | — |
| `NIMTABLE_PORT` | No | Nimtable catalog UI host port | `3018` |
| `OLAKE_SOURCE_HOST` | No | Source DB host for Olake CDC | `postgres` |
| `OLAKE_SOURCE_PORT` | No | Source DB port | `5432` |
| `OLAKE_SOURCE_DB` | No | Source DB name | `staging_pg` |
| `LANCEDB_VIEWER_PORT` | No | LanceDB viewer host port | `8081` |
| `POSTGRES_PASSWORD` | No | Postgres password (overridden by Locket) | `devpassword` |
| `RUST_LOG` | No | Log level | `garage=info` |
| `RUST_BACKTRACE` | No | Backtrace on panic | `1` |

## Access

- **Lakekeeper REST API**: `http://localhost:8181`
- **Lance Namespace**: `http://localhost:8182`
- **Garage S3**: `http://localhost:3900`
- **Nimtable catalog UI**: `http://localhost:3018` (Iceberg table browser)
- **LanceDB viewer**: `http://localhost:8081` (LanceDB table browser)
- **Olake CDC engine**: admin via `docker exec` (ephemeral port)
- **Pangolin routes** (production): `lakekeeper.cianfhoghlaim.ie`, `lance-api.cianfhoghlaim.ie`, `nimtable.cianfhoghlaim.ie`, `olake.cianfhoghlaim.ie`, `lance-viewer.cianfhoghlaim.ie`
- **Auth**: S3 access/secret key pairs; all services private via Pangolin (Tinyauth + secure-headers middlewares)

## Service Inventory

| Service | Container | Port | Image | Notes |
|:--|:--|:--|:--|:--|
| Garage | `lakehouse-garage` | 3900 (S3), 3901 (RPC), 3903 (Web), 3904 (Admin) | `dxflrs/garage:v1.0.1` | S3-compatible object storage |
| Postgres | `lakehouse-postgres` | 5432 → 5433 | `postgres:16-alpine` | Lakekeeper + DuckLake + Olake + Nimtable metadata |
| Lakekeeper | `lakehouse-lakekeeper` | 8181 | `quay.io/lakekeeper/catalog:latest` | Iceberg REST catalog |
| Lance Namespace | `lakehouse-lance-namespace` | 8182 | `lakehouse-lance-namespace:latest` (built) | FastAPI sidecar registering LanceDB tables as Iceberg |
| Nimtable | `lakehouse-nimtable` | 3000 → 3018 | `nimtable/nimtable:0.1.6` | Iceberg catalog UI (added in `extend-lakehouse-with-nimtable-olake-lancedb`) |
| Olake | `lakehouse-olake` | ephemeral | `ghcr.io/olake-io/olake:0.1.5` | CDC engine: Postgres/MySQL/MongoDB → Iceberg (added in `extend-lakehouse-with-nimtable-olake-lancedb`) |
| LanceDB Viewer | `lakehouse-lancedb-viewer` | 8080 → 8081 | `ghcr.io/gordonmurray/lance-data-viewer:lancedb-0.24.3` | Web UI for LanceDB tables (added in `extend-lakehouse-with-nimtable-olake-lancedb`) |
| Locket | `lakehouse-locket` | ephemeral | `ghcr.io/cianfhoghlaim/locket:1.2.3` | Infisical secret injector (sidecar) |

## Cross-Sruth Lakehouse Wiring

Every active srutha in the Cianfhoghlaim monorepo MUST wire into the canonical dev lakehouse via two contracts:

1. **`LANCEDB_URI=rest://lakehouse-lance-namespace:8182`** — every active srutha stack MUST default `LANCEDB_URI` to the lakehouse Lance namespace (not a local file path).
2. **`ducklake_{namespace}` database** — every active srutha MUST have a dedicated `ducklake_{namespace}` database in `infrastructure/stacks/lakehouse/init-db.sql` for DuckLake write-ahead-log storage.

The canonical factory for both contracts is `oideachais/dlt_utils/destinations.py:with_namespace()` (the `with_namespace()` method at line 289 of the file).

| Srutha | DuckLake DB | LANCEDB_URI | Stack |
|:--|:--|:--|:--|
| `oideachais` | `ducklake_oideachais` | `rest://lakehouse-lance-namespace:8182` | `infrastructure/stacks/oideachais/` |
| `crypteolas` | `ducklake_crypteolas` | inherits `rest://...` | `infrastructure/stacks/tuatha/crypteolas/` |
| `croilar` | `ducklake_croilar` | `rest://lakehouse-lance-namespace:8182` (was `./lancedb_data_cv`) | `infrastructure/stacks/croilar-{dagster,marimo}/` |
| `tuath` | `ducklake_tuath` | inherits `rest://...` | `infrastructure/stacks/tuatha/` |
| `meaisinfhoghlaim` | `ducklake_meaisinfhoghlaim` (added here) | inherits `rest://...` | `infrastructure/stacks/meaisinfhoghlaim/` |
| `aleyum` (legacy) | `ducklake_aleyum` | n/a — superseded by croilar | (deprecated, redirects to croilar) |

## Bringup order

```bash
cd infrastructure/stacks/lakehouse
docker compose up -d        # brings up garage + postgres + lakekeeper + lance-namespace + nimtable + olake + lancedb-viewer + locket

# Verify
curl -sf http://localhost:8181/v1/config | jq .          # Lakekeeper REST catalog
curl -sf http://localhost:8182/health                     # Lance namespace
curl -sf http://localhost:3018/api/v1/health              # Nimtable catalog UI
curl -sf http://localhost:8081/health                     # LanceDB viewer
aws --endpoint-url http://localhost:3900 s3 ls            # Garage S3 (uses dev keys)
```

## Upstream

- **Garage**: <https://git.deuxfleurs.fr/Deuxfleurs/garage> — v1.0.1
- **Lakekeeper**: <https://github.com/lakekeeper/lakekeeper> — actively maintained Iceberg REST catalog
- **LanceDB**: <https://github.com/lancedb/lancedb> — embedded vector database with Iceberg support (v0.15+)

## Screenshot

All services in this stack are headless APIs. Lakekeeper exposes a REST API at port 8181 with catalog metadata; Garage provides an S3-compatible API at port 3900 and a minimal web console at port 3903.
