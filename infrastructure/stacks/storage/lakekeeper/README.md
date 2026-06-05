# Lakekeeper — Apache Iceberg REST Catalog

## Overview

Lakekeeper is an open-source Apache Iceberg REST Catalog implementation written in Rust. It provides the catalog layer that enables ACID transactions, time travel, schema evolution, and partition management on object storage. Think of it as the "metadata database" that tells query engines which Parquet files belong to which table snapshot.

## Why This Matters for Kings' College Galway

Every data pipeline in this project — DLT ingestion, Dagster transformations, DuckDB analytics, marimo notebooks — reads and writes through the Iceberg catalog. Lakekeeper makes it possible to run `SELECT * FROM curriculum.leaving_cert_mathematics FOR VERSION AS OF <timestamp>` to see the syllabus as it existed at any point in time. This is essential for curriculum research where exam specifications change year-over-year and we need to track those changes at the data level, not in application code.

## Key Features

- **Apache Iceberg REST spec** — Fully compatible with Spark, Trino, DuckDB, PyIceberg
- **Rust-native performance** — Low-latency catalog operations, sub-millisecond metadata lookups
- **Schema evolution** — Add, rename, drop, or reorder columns without rewriting data
- **Partition evolution** — Change partition schemes without table rewrites
- **Snapshot isolation** — Readers see a consistent snapshot even during concurrent writes

## Deployment

### Docker Compose (Local)

```bash
cd infrastructure/stacks/storage/lakekeeper
docker compose up -d
```

### Docker Compose (Production with Locket)

```bash
docker compose -f compose.yaml -f sidecar.yaml -f pangolin.yaml up -d
```

### Komodo (GitOps)

Deployed via Komodo on arm1-oci. Locket resolves `LAKEKEEPER_DB_PASSWORD` and `LAKEKEEPER_ENCRYPTION_KEY` from Infisical. The catalog connects to a co-located PostgreSQL 16 Alpine instance for metadata storage.

## Environment Variables

| Variable | Required | Description | Default |
|:--|:--|:--|:--|
| `LAKEKEEPER_DB_USERNAME` | No | PostgreSQL user | `lakekeeper` |
| `LAKEKEEPER_DB_PASSWORD` | Yes | PostgreSQL password | — |
| `LAKEKEEPER_ENCRYPTION_KEY` | Yes | Encryption key for catalog metadata (64-char hex) | — |
| `LAKEKEEPER_PORT` | No | REST API port | `8181` |
| `MINIO_ROOT_USER` | No | MinIO access key (dev only) | `minio` |
| `MINIO_ROOT_PASSWORD` | No | MinIO secret key (dev only) | `devpassword` |
| `MINIO_API_PORT` | No | MinIO S3 API port | `9000` |
| `MINIO_CONSOLE_PORT` | No | MinIO web console port | `9001` |

## Access

- **REST API**: `http://localhost:8181`
- **MinIO Console**: `http://localhost:9001`
- **Auth**: Internal-only; REST API used by Dagster, DuckDB, and PyIceberg clients

## Upstream

- **Repository**: <https://github.com/lakekeeper/lakekeeper>
- **Documentation**: <https://docs.lakekeeper.dev>
- **Latest**: Active development; Rust rewrite of the Java Iceberg catalog with focus on performance and small footprint

## Screenshot

Headless REST API. The MinIO console at port 9001 provides a web UI for browsing S3 buckets and objects. The Lakekeeper REST catalog at port 8181 is a JSON API with no built-in UI — query it via `curl` or the Iceberg client libraries.
