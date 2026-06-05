# Olake — High-Performance Database CDC to Data Lakes

## Overview

Olake is an open-source Change Data Capture (CDC) tool that replicates data from databases (MongoDB, PostgreSQL, MySQL) to data lake formats (Iceberg, Parquet) at high throughput. It is designed as a cost-effective alternative to Fivetran and Airbyte for database-to-lake replication, achieving 300K+ rows per second.

## Why This Matters for Kings' College Galway

The curriculum data platform has multiple data sources that change over time: the MongoDB instances backing the web app, the PostgreSQL databases backing Langfuse and Dagster, and the MySQL database backing PlanetScale. Olake provides CDC replication from these operational databases into the Iceberg lakehouse, ensuring the analytics layer (DuckDB, marimo notebooks) always has a consistent, up-to-date view of production data. This is the bridge between the transactional world (web app, Langfuse) and the analytical world (curriculum dashboards, RAGAS evaluation reports).

## Key Features

- **High-throughput CDC** — 300K+ rows/sec replication
- **Multi-source** — MongoDB, PostgreSQL, MySQL connectors
- **Iceberg writer** — Write directly to Iceberg tables in the lakehouse
- **Dagster integration** — Orchestrate CDC jobs as Dagster assets
- **Incremental sync** — Only replicate changed data, not full table scans

## Deployment

### Docker Compose (Local)

```bash
cd infrastructure/stacks/machine_learning/olake
docker compose up -d
```

### Production (via Komodo)

Deployed via Komodo on cax41-hetzner. Configuration files (config.json, catalog.json, writer.json, state.json) are mounted from the stack directory.

## Environment Variables

| Variable | Required | Description | Default |
|:--|:--|:--|:--|
| `MONGODB_CONNECTION_STRING` | Yes | Source MongoDB URI | — |
| `ICEBERG_CATALOG_URL` | Yes | Lakekeeper REST catalog URL | — |
| `S3_ACCESS_KEY` | Yes | Garage S3 access key | — |
| `S3_SECRET_KEY` | Yes | Garage S3 secret key | — |

## Access

- **API**: Internal only (CLI-driven)
- **Config**: Mounted JSON files (`config.json`, `catalog.json`, `writer.json`)
- **Auth**: Database credentials in config files

## Upstream

- **Repository**: <https://github.com/olake/olake>
- **Latest**: Active development — MongoDB CDC improvements, Iceberg writer performance, Dagster integration

## Screenshot

Olake is a CLI-driven tool with no built-in web UI. Sync status and throughput metrics are logged to stdout and can be monitored via Docker logs or Dozzle. The Dagster integration surfaces CDC job status as asset materializations in the Dagster UI.
