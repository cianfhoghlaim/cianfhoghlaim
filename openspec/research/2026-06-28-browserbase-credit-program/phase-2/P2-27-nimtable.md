# P2-27 — nimtable (Phase 2, Data Plane)

**Date:** 2026-06-28
**Phase:** 2 (Light Packages)
**Budget:** ~60 credits
**Subagent:** data-platform

## TL;DR

nimtable is the **Iceberg catalog UI** that lets humans browse the lakehouse Iceberg tables (created by dlt → Iceberg on Garage S3) without writing SQL. It runs as a Docker container in the lakehouse stack on port 3018 and exposes a web UI at `nimtable.lakehouse.cianfhoghlaim.ie`.

The canonical Cianfhoghlaim pattern: nimtable is for **browsing + understanding**; MotherDuck Dives are for **dashboards**; raw SQL is for **one-off analysis**.

## Code

| Path | Purpose |
|:--|:--|
| `stacks/lakehouse/compose.yaml` (line ~120) | nimtable service definition (port 3018) |
| `stacks/lakehouse/lance-sidecar/` | Lance namespace registration sidecar |
| `stacks/lakehouse/olake/` | CDC engine (uses nimtable as its catalog UI) |
| `cognify/rules/iceberg_tables.py` | Lists 12 Iceberg tables maintained by dlt sources |

**nimtable compose snippet**:

```yaml
nimtable:
  image: nicholasdille/nimtable:latest
  container_name: lakehouse-nimtable
  restart: unless-stopped
  ports:
    - "3018:8080"
  environment:
    CATALOG_URI: postgres://lakehouse-postgres:5432/lakehouse_catalog
    WAREHOUSE: s3://lakehouse-bucket/iceberg/
    AWS_ACCESS_KEY_ID: ${GARAGE_ACCESS_KEY}
    AWS_SECRET_ACCESS_KEY: ${GARAGE_SECRET_KEY}
    AWS_ENDPOINT_URL: http://lakehouse-garage:3900
  networks:
    - lakehouse_internal
```

## Env

| Env var | Value | Source |
|:--|:--|:--|
| `CATALOG_URI` | `postgres://lakehouse-postgres:5432/lakehouse_catalog` | compose env |
| `WAREHOUSE` | `s3://lakehouse-bucket/iceberg/` | compose env |
| `AWS_ACCESS_KEY_ID` | `${GARAGE_ACCESS_KEY}` | Locket |
| `AWS_SECRET_ACCESS_KEY` | `${GARAGE_SECRET_KEY}` | Locket |
| `AWS_ENDPOINT_URL` | `http://lakehouse-garage:3900` | compose env |

## CCC anchors

`stacks/lakehouse/compose.yaml` · `stacks/lakehouse/olake/` · `cognify/rules/iceberg_tables.py` · `openspec/changes/extend-lakehouse-with-nimtable-olake-lancedb/` (archived)

Search terms: `"nimtable"`, `"CATALOG_URI"`, `"iceberg_tables"`.

## Drift log

| Date | Event |
|:--|:--|
| 2025-Q4 | First nimtable deployment |
| 2026-03 | Added nimtable to Phase 3 lakehouse deploy (`extend-lakehouse-with-nimtable-olake-lancedb` change) |
| 2026-04 | Wired `cognify/rules/iceberg_tables.py` to expose the 12 tables |
| 2026-06-28 | v4 consolidation: kept stack path (no rename needed) |

## Anti-patterns

1. Don't use nimtable for production dashboards — it's for browsing only
2. Don't bypass Iceberg ACID — nimtable respects time-travel + snapshots
3. Don't hardcode credentials in compose — use Locket + env interpolation
4. Don't use the SQL editor for table writes — use dlt (which writes atomically)
5. Don't skip the `WAREHOUSE` env var — nimtable needs to know where to find the Parquet data

## Decision matrix

| Decision | Choice | Rationale |
|:--|:--|:--|
| Catalog UI | nimtable (not Polaris/Unity) | Open-source + Iceberg-native + Garage S3 compat |
| Auth | None (port-restricted via Pangolin) | Internal-only tool |
| SQL editor | Disabled in production | Force users through MotherDuck for queries |
| Schema viewer | Tree view + column descriptions | Easier than Iceberg REST API |
| Snapshot history | Last 30 days | Storage cost trade-off |
| Lineage | From dlt source paths | Tracked in `cognify/rules/dlt_lineage.py` |
| Sharing | Read-only Pangolin link | Cross-team without leaking writes |

## Files to read next

`stacks/lakehouse/compose.yaml` · `cognify/rules/iceberg_tables.py` · `openspec/changes/archive/extend-lakehouse-with-nimtable-olake-lancedb/`
