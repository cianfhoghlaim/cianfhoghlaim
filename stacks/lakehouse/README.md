# Lakehouse — Unified Data Lakehouse Stack

## Overview

The lakehouse stack integrates Garage S3-compatible storage, Lakekeeper Iceberg REST Catalog, and a Lance Namespace sidecar into a single deployable unit. It is the primary data plane for the Kings' College Galway project — every curriculum Parquet file, every vector index, and every generated study asset passes through this stack. Uses PlanetScale (MySQL-compatible cloud DB) as the catalog metadata backend.

## Why This Matters for Kings' College Galway

This is the single most important infrastructure stack. It provides ACID transactions on object storage via Iceberg tables, enabling time-travel queries on curriculum data (e.g., "show me the syllabus as it existed before the 2023 reform"). The Lance Namespace sidecar bridges LanceDB's vector format with Iceberg's catalog, allowing semantic search over vector embeddings to coexist with SQL analytics over structured tables. DuckLake tables built on Garage S3 are registered in the Iceberg catalog, making them queryable from Dagster, marimo notebooks, and the web app through a single namespace.

## Key Features

- **Iceberg ACID on S3** — Lakekeeper provides snapshot isolation, time travel, and schema evolution on Garage S3
- **Lance + Iceberg bridge** — Custom lance-namespace sidecar registers LanceDB vector tables as Iceberg tables
- **PlanetScale-backed catalog** — Production-grade MySQL for catalog metadata (schema, partition specs, snapshots)
- **Single namespace** — All tables (DuckLake SQL + LanceDB vectors) queryable through one Iceberg catalog

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
| `RUST_LOG` | No | Log level | `garage=info` |
| `RUST_BACKTRACE` | No | Backtrace on panic | `1` |

## Access

- **Lakekeeper REST API**: `http://localhost:8181`
- **Lance Namespace**: `http://localhost:8182`
- **Garage S3**: `http://localhost:3900`
- **Auth**: S3 access/secret key pairs; all services private via Pangolin

## Upstream

- **Garage**: <https://git.deuxfleurs.fr/Deuxfleurs/garage> — v1.0.1
- **Lakekeeper**: <https://github.com/lakekeeper/lakekeeper> — actively maintained Iceberg REST catalog
- **LanceDB**: <https://github.com/lancedb/lancedb> — embedded vector database with Iceberg support (v0.15+)

## Screenshot

All services in this stack are headless APIs. Lakekeeper exposes a REST API at port 8181 with catalog metadata; Garage provides an S3-compatible API at port 3900 and a minimal web console at port 3903.
