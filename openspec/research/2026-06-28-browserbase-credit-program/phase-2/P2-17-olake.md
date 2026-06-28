# P2-17 — olake (Phase 2, Agent-Platform)

**Date:** 2026-06-28
**Phase:** 2 (Light Packages)
**Budget:** ~60 credits
**Subagent:** agent-platform

## TL;DR

Olake is the **CDC (change-data-capture) engine** that streams OLTP database changes (PlanetScale Postgres) into the lakehouse Iceberg catalog in real-time. It runs as an ephemeral admin container in the lakehouse stack and exposes a Postgres-compatible logical-replication interface.

The canonical Cianfhoghlaim pattern: olake is for **OLTP → Lakehouse** streaming; dlt is for **batch ingestion**; Dagster orchestrates both.

## Code

| Path | Purpose |
|:--|:--|
| `stacks/lakehouse/olake/` | Olake service definition |
| `stacks/lakehouse/olake/config.yaml` | CDC table-to-Iceberg mapping |
| `stacks/lakehouse/olake/secrets.env` | Locket-injected |
| `cognify/rules/olake_tables.py` | Lists 12 OLTP tables streamed |
| `oideachais/dagster_defs/assets/cdc/` | Dagster wrappers around olake CDC streams |

**Canonical olake config** (`stacks/lakehouse/olake/config.yaml`):

```yaml
name: olake-psql-to-iceberg
source:
  type: postgres
  connection:
    host: planetscale-host
    port: 5432
    database: oideachais_prod
    user: olake_user
    ssl: require
  publication: oideachais_publication
  slot: olake_slot
destination:
  type: iceberg
  catalog_uri: postgres://lakehouse-postgres:5432/lakehouse_catalog
  warehouse: s3://lakehouse-bucket/iceberg/
tables:
  - source: oideachais.users
    destination: lakehouse.oideachais.users_cdc
    primary_key: [user_id]
  - source: oideachais.curriculum_progress
    destination: lakehouse.oideachais.curriculum_progress_cdc
    primary_key: [user_id, subject_id, exam_year]
```

## Env

| Env var | Value | Source |
|:--|:--|:--|
| `OLAKE_SOURCE_HOST` | `infisical://dev-baile/planetscale/host` | Locket |
| `OLAKE_DESTINATION_WAREHOUSE` | `s3://lakehouse-bucket/iceberg/` | compose env |
| `OLAKE_DATABASE_URL` | `infisical://dev-baile/lakehouse/postgres_url` | Locket |
| `GARAGE_ACCESS_KEY` | `infisical://dev-baile/garage/access_key` | Locket |

## CCC anchors

`stacks/lakehouse/olake/` · `cognify/rules/olake_tables.py` · `oideachais/dagster_defs/assets/cdc/` · `openspec/changes/archive/extend-lakehouse-with-nimtable-olake-lancedb/`

Search terms: `"olake"`, `"publication"`, `"CDC stream"`.

## Drift log

| Date | Event |
|:--|:--|
| 2026-03 | Initial olake deploy (`extend-lakehouse-with-nimtable-olake-lancedb` archived) |
| 2026-04 | Streamed 12 OLTP tables to Iceberg |
| 2026-05 | Added Dagster wrappers for CDC asset tracking |

## Anti-patterns

1. Don't use olake for batch ingestion — use dlt
2. Don't disable logical replication on the OLTP DB — olake needs it
3. Don't bypass the publication/slot setup — without it, olake silently fails
4. Don't use olake without Iceberg catalog — it has no other destination

## Decision matrix

| Decision | Choice | Rationale |
|:--|:--|:--|
| CDC tool | olake (not Debezium) | Simpler + Postgres-native |
| Destination | Iceberg catalog | Same as dlt batch writes |
| Publication | One per OLTP DB | Clean separation |
| Slot | One per olake service | WAL retention |
| Primary key | Composite (user_id + ...) | For tables without natural PK |
| Schema evolution | Auto-tracked via Iceberg | No manual migration |

## Files to read next

`stacks/lakehouse/olake/` · `cognify/rules/olake_tables.py`
