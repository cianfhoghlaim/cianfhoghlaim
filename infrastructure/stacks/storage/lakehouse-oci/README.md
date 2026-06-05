# Lakehouse OCI — Production Lakehouse on Oracle Cloud

## Overview

The OCI variant of the lakehouse stack, designed for the production deployment on `arm1-oci` (Oracle Cloud Ampere A1). Unlike the standard lakehouse which uses PlanetScale, this stack runs a standalone PostgreSQL instance alongside Lakekeeper, providing fully self-contained catalog metadata on the ARM64 control plane node.

## Why This Matters for Kings' College Galway

The OCI deployment is the production lakehouse — the canonical data plane serving the Dagster pipeline, the web app, and all marimo notebooks. Running PostgreSQL locally on the ARM64 node eliminates the latency and dependency of a cloud-hosted catalog database. This stack is the source of truth for all Iceberg tables, meaning every curriculum ingestion run, every exam paper OCR pass, and every vector embedding index is ultimately materialised here before being replicated to the development MacBook.

## Key Features

- **Self-contained PostgreSQL** — No external database dependency; catalog metadata lives on the ARM64 node
- **Iceberg REST Catalog** — Identical Lakekeeper API to the development lakehouse, ensuring dev/prod parity
- **ARM64-optimised** — PostgreSQL 16 Alpine and Lakekeeper both have native aarch64 images
- **Encrypted at rest** — Lakekeeper encrypts catalog metadata with a configurable encryption key

## Deployment

### Docker Compose (Local on arm1-oci)

```bash
cd infrastructure/stacks/storage/lakehouse-oci
docker compose up -d
```

### Docker Compose (Production with Locket)

```bash
docker compose -f compose.yaml -f sidecar.yaml -f pangolin.yaml up -d
```

### Komodo (GitOps)

Deployed via Komodo on arm1-oci. Locket resolves `LAKEKEEPER_DB_PASSWORD`, `LAKEKEEPER_ENCRYPTION_KEY`, `LAKEKEEPER_S3_ACCESS_KEY`, and `LAKEKEEPER_S3_SECRET_KEY` from Infisical.

## Environment Variables

| Variable | Required | Description | Default |
|:--|:--|:--|:--|
| `POSTGRES_PORT` | No | PostgreSQL port | `5433` |
| `LAKEKEEPER_DB_USER` | No | PostgreSQL user | `lakekeeper` |
| `LAKEKEEPER_DB_PASSWORD` | Yes | PostgreSQL password | — |
| `LAKEKEEPER_ENCRYPTION_KEY` | Yes | Catalog encryption key (64-char hex) | — |
| `LAKEKEEPER_S3_ACCESS_KEY` | Yes | Garage S3 access key | — |
| `LAKEKEEPER_S3_SECRET_KEY` | Yes | Garage S3 secret key | — |
| `LAKEKEEPER_PORT` | No | Lakekeeper REST API port | `8181` |
| `LANCE_NAMESPACE_PORT` | No | Lance namespace sidecar port | `8182` |

## Access

- **Lakekeeper REST API**: `https://lakekeeper.cianfhoghlaim.ie` (private)
- **PostgreSQL**: `localhost:5433` (internal, not exposed publicly)
- **Auth**: Pocket ID SSO for Lakekeeper; PostgreSQL credentials via Locket

## Upstream

- **Lakekeeper**: <https://github.com/lakekeeper/lakekeeper>
- **PostgreSQL 16**: <https://www.postgresql.org/docs/16/release-16.html>

## Screenshot

Headless infrastructure services. The Lakekeeper REST API at port 8181 serves Iceberg catalog metadata. PostgreSQL on port 5433 is internal-only with no web UI.
