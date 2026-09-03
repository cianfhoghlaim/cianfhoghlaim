# P1B-08 — Garage S3 + Iceberg REST Catalog + Lakekeeper (Phase 1B, Vector + Graph + Storage)

**Date:** 2026-06-28
**Phase:** 1B (Vector + Graph + Storage Tier)
**Budget:** ~180 credits
**Subagent:** research

## TL;DR

Garage is the **S3-compatible object storage** that holds every Cianfhoghlaim byte (Parquet data, Iceberg manifests, Lance files, MLflow artifacts, Langfuse traces). Lakekeeper is the **Iceberg REST Catalog** (port 8181) that sits in front of Garage and provides ACID transactions + time-travel queries on top of Parquet. Together they're the **physical lakehouse** that DuckLake + LanceDB + Iceberg + MotherDuck all read from.

The canonical Cianfhoghlaim pattern: Garage stores the bytes; Lakekeeper is the metadata layer; Iceberg is the table format; DuckLake is the SQL interface; MotherDuck/LanceDB are the query engines.

## Code

| Path | Purpose |
|:--|:--|
| `stacks/lakehouse/garage.toml` | Garage cluster config (3 nodes for HA) |
| `stacks/lakehouse/garage-init/` | Bucket initialization (lakehouse-bucket, lance-bucket, mlflow-artifacts, langfuse-traces, nimtable) |
| `stacks/lakehouse/lakekeeper/` | Iceberg REST Catalog service (port 8181) |
| `stacks/lakehouse/lakekeeper-migrate/` | Postgres catalog schema migration |
| `stacks/lakehouse/init-db.sql` | Lakekeeper Postgres schema |
| `cognify/rules/garage_health.py` | Dagster asset check for Garage nodes |

**Canonical Garage config** (`stacks/lakehouse/garage.toml`):

```toml
metadata_servers = [
  { id = "garage-meta-1", addr = "10.0.1.10:3901" },
  { id = "garage-meta-2", addr = "10.0.1.11:3901" },
  { id = "garage-meta-3", addr = "10.0.1.12:3901" },
]

data_nodes = [
  { id = "garage-data-1", addr = "10.0.1.10:3902", data_dir = "/var/lib/garage/data1" },
  { id = "garage-data-2", addr = "10.0.1.11:3902", data_dir = "/var/lib/garage/data2" },
  { id = "garage-data-3", addr = "10.0.1.12:3902", data_dir = "/var/lib/garage/data3" },
]

# Buckets
buckets = [
  { name = "lakehouse-bucket", website_access = false },
  { name = "lance-bucket", website_access = false },
  { name = "mlflow-artifacts", website_access = false },
  { name = "langfuse-traces", website_access = false },
  { name = "nimtable", website_access = false },
]
```

**Canonical Lakekeeper compose** (`stacks/lakehouse/compose.yaml`):

```yaml
lakekeeper:
  image: treeverse/lakekeeper:latest
  container_name: lakehouse-lakekeeper
  restart: unless-stopped
  ports:
    - "8181:8181"
  environment:
    LAKEKEEPER__PG_HOST: lakehouse-postgres
    LAKEKEEPER__PG_USER: lakehouse
    LAKEKEEPER__PG_PASSWORD: ${POSTGRES_PASSWORD}
    LAKEKEEPER__PG_DATABASE: lakehouse_catalog
    LAKEKEEPER__LISTEN_ADDR: "0.0.0.0:8181"
    LAKEKEEPER__AUTH_DISABLE: "true"  # dev only; prod uses Pangolin SSO
```

## Env

| Env var | Value | Source |
|:--|:--|:--|
| `GARAGE_ENDPOINT_URL` | `http://lakehouse-garage:3900` | compose env |
| `GARAGE_ACCESS_KEY` | `infisical://dev-baile/garage/access_key` | Locket |
| `GARAGE_SECRET_KEY` | `infisical://dev-baile/garage/secret_key` | Locket |
| `LAKEKEEPER_URI` | `http://lakehouse-lakekeeper:8181` | compose env |
| `AWS_DEFAULT_REGION` | `garage` | compose env |

## CCC anchors

`stacks/lakehouse/garage.toml` · `stacks/lakehouse/lakekeeper/` · `stacks/lakehouse/init-db.sql` · `cognify/rules/garage_health.py`

Search terms: `"garage.toml"`, `"lakekeeper"`, `"LAKEKEEPER__PG"`, `"iceberg_catalog"`.

## Drift log

| Date | Event |
|:--|:--|
| 2025-09 | Initial Garage deploy (single node) |
| 2025-12 | Migrated to 3-node cluster (HA) |
| 2026-01 | Added Lakekeeper (Iceberg REST Catalog) |
| 2026-03 | Migrated from raw Parquet to Iceberg format |
| 2026-04 | Added Lance Blob (large object support) |

## Anti-patterns

1. Don't bypass Lakekeeper for direct S3 writes — Iceberg ACID requires the catalog
2. Don't use a single Garage node in production — 3 nodes for HA
3. Don't put Garage data on the same disk as the OS — use a dedicated data partition
4. Don't disable Garage replication factor to 1 — always 3
5. Don't skip the `garage-init` bucket setup — first-time deploys need explicit bucket creation

## Decision matrix

| Decision | Choice | Rationale |
|:--|:--|:--|
| Object storage | Garage (S3-compatible) | Open-source + native S3 API |
| Cluster size | 3 nodes (1 per zone) | HA + no SPOF |
| Replication factor | 3 | Survives 1-zone outage |
| Table format | Iceberg 1.4 | ACID + time-travel + standard |
| Catalog | Lakekeeper (REST) | Open-source + Iceberg-native |
| Versioning | Iceberg snapshots | Time-travel queries |
| Partitioning | Hive-style by date | Common for time-series data |
| Compaction | Daily Dagster asset | Keeps query performance |

## Files to read next

`stacks/lakehouse/garage.toml` · `stacks/lakehouse/lakekeeper/` · `stacks/lakehouse/init-db.sql` · `cognify/rules/garage_health.py` · `.agents/skills/infrastructure-stacks/SKILL.md`
