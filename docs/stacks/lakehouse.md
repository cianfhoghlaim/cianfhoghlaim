# lakehouse

## Purpose for the Cianfhoghlaim project

The lakehouse stack is the **centralised data plane** for every other
stack in the platform. After the `centralise-data-plane` rewrite
(2026-07-30) it hosts 11 services, 12 databases, and 7 S3 buckets
that are the source-of-truth for the agent-platform cluster
(langfuse / litellm / mlflow), the per-subject Dagster pipelines,
the 14 v1 CocoIndex Apps, and the LLM/agent fleet. Every
curriculum Parquet file, every vector index, every trace, and
every generated study asset passes through this stack.

### Service Inventory (11 services)

| # | Service | Container | Port | Role |
|:--|:--|:--|--:|:--|
| 1 | Garage | `lakehouse-garage` | 3900-3904 | S3-compatible object store, virtual-host DNS |
| 2 | Postgres 16 | `lakehouse-postgres` | 5433 (host) | 12 databases (12 services share this one) |
| 3 | ClickHouse 24 | `lakehouse-clickhouse` | 8123, 9000 | Columnar engine (consumed by langfuse) |
| 4 | Redis 7 | `lakehouse-redis` | 6379 | Queue + cache (consumed by langfuse) |
| 5 | Lakekeeper | `lakehouse-lakekeeper` | 8181 | Iceberg REST catalog |
| 6 | Lance Namespace | `lakehouse-lance-namespace` | 8182 | Lance table sidecar (built in-stack) |
| 7 | Nimtable | `lakehouse-nimtable` | 3018 | Iceberg catalog UI (Spring-Boot) |
| 8 | Olake | `lakehouse-olake` | ephemeral | CDC engine (Postgres/MySQL → Iceberg) |
| 9 | LanceDB Viewer | `lakehouse-lancedb-viewer` | 8081 | LanceDB table browser |
| 10 | Lakekeeper Migrate | `lakehouse-lakekeeper-migrate` | n/a | One-shot DB migration |
| 11 | Garage Init | `lakehouse-garage-init` | n/a | One-shot bucket creator |
| 12 | Locket | `lakehouse-locket` | ephemeral | Infisical secret injector (sidecar) |

### 12 Databases (single Postgres, multi-DB isolation)

| Database | Consumer(s) |
|:--|:--|
| `ducklake_oideachais`, `ducklake_crypteolas`, `ducklake_croilar`, `ducklake_tuath`, `ducklake_meaisinfhoghlaim`, `ducklake_aleyum` (legacy) | 6 DuckLake catalogs (one per active sruth) |
| `dagster_local` | dagster stack |
| `langfuse` | langfuse stack (after centralise-data-plane) |
| `mlflow` | mlflow stack (after centralise-data-plane) |
| `litellm` | litellm stack (after centralise-data-plane) |
| `olake_state` | Olake CDC checkpoints |
| `nimtable` | Nimtable dashboard state |

### 7 S3 Buckets (single Garage, multi-bucket isolation)

| Bucket | Consumer(s) |
|:--|:--|
| `iceberg` | Lakekeeper Iceberg tables |
| `lance` | Lance vector tables |
| `ducklake` | DuckLake write-ahead-log |
| `langfuse-events` | langfuse trace ingest |
| `langfuse-media` | langfuse media uploads |
| `langfuse-exports` | langfuse batch exports |
| `mlflow-artifacts` | mlflow artifact store |

## Why it stays in komodo/pangolin/infisical GitOps

The lakehouse is the **single most important infrastructure stack** in
the project: if it's down, 4 other stacks (langfuse, litellm, mlflow,
dagster) are down. The pair of komodo +
`deploy-lakehouse-bunchloch` + `lakehouse-oci.toml` procedures plus the
pangolin private-resource routes + the Infisical vault entries (13
secrets under `lakehouse`, `lakehouse-garage`, `lakehouse-clickhouse`,
`lakehouse-redis`, `lakehouse/encryption_key`) ensure the stack is
deployable + secure + reproducible.

`PLANETSCALE_DATABASE_URL` is retained as an OPTIONAL override for
managed-Postgres deployments, but the default is always the local
lakehouse-postgres container (defaulted for both dev and bunchloch prod).

## Centralised Data Plane Contract

Every stack that needs PG / S3 / ClickHouse / Redis uses these via
Docker DNS names:

| Consumer | Postgres | S3 | ClickHouse | Redis |
|:--|:--|:--|:--|:--|
| langfuse | `lakehouse-postgres:5432` (db=langfuse) | `lakehouse-garage:3900` (3 buckets) | `lakehouse-clickhouse:8123` | `lakehouse-redis:6379` |
| litellm | `lakehouse-postgres:5432` (db=litellm) | — | — | — |
| mlflow | `lakehouse-postgres:5432` (db=mlflow) | `lakehouse-garage:3900` (bucket=mlflow-artifacts) | — | — |
| dagster | `lakehouse-postgres:5432` (db=dagster_local) | `lakehouse-garage:3900` (stedding/ mount) | — | — |

## Cross-references

- **Ops**: `bonneagar/stacks/lakehouse/` (the 6-file GOLD_STANDARD + `init-db.sql` + `init-buckets.sh`)
- **Code**: `cianfhoghlaim/` (the per-subject pipeline patterns at `dlt/british_isles/ie/education/subjects/<subject>/`)
- **Komodo procedure**: `bonneagar/komodo/procedures/deploy-lakehouse-bunchloch.toml` (production) + `lakehouse-oci.toml` (OCI alternative) + `storage-lakehouse.toml` (legacy)
- **Pangolin**: 7 routes — `lakekeeper.cianfhoghlaim.ie`, `lance-api.cianfhoghlaim.ie`, `nimtable.cianfhoghlaim.ie`, `olake.cianfhoghlaim.ie`, `lance-viewer.cianfhoghlaim.ie`, `lakehouse-garage.cianfhoghlaim.ie`, `lakehouse-clickhouse.cianfhoghlaim.ie`

## Tags

- `host:bunchloch` (primary) / `host:arm1-oci` (production)
- `tier:data-engineering`
- `project:cianfhoghlaim`
- `group:foundation` (every other agent-platform stack depends on this)
