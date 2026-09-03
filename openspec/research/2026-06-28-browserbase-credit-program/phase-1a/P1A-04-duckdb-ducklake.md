# P1A-04 — DuckDB + DuckLake (Phase 1A, Data Plane)

**Date:** 2026-06-28
**Phase:** 1A (Data Plane Foundations)
**Budget:** ~180 credits
**Subagent:** data-platform

## TL;DR

DuckDB is the **in-process analytical engine** that powers every Cianfhoghlaim query. DuckLake is the **lakehouse catalog format** (built on DuckDB + object storage + Postgres metadata) that replaces the bespoke Iceberg catalog for tabular data. Together they form the lakehouse half of the Phase 0.3 deploy on bunchloch.

The canonical Cianfhoghlaim pattern is:

```sql
-- Query any lakehouse dataset from any tool via DuckLake
ATTACH 'ducklake:postgres://lakehouse-postgres:5432/lakehouse_catalog' AS lakehouse;
USE lakehouse;
SELECT subject, COUNT(*) AS exam_papers
FROM read_parquet('s3://lakehouse-bucket/examinations_ie/**/*.parquet')
GROUP BY subject
ORDER BY 2 DESC
LIMIT 24;
```

The same query runs through:
- MotherDuck (managed DuckDB service) for cross-host access
- LanceDB (vector search) for embedding similarity
- Cognee (knowledge graph) for entity-relationship queries
- Marimo (notebooks) for exploratory dashboards

## Code (where DuckDB + DuckLake live in Cianfhoghlaim)

| Path | Purpose |
|:--|:--|
| `cianfhoghlaim/core/duckdb/` | DuckDB Python wrappers + extensions |
| `cianfhoghlaim/core/ducklake/` | DuckLake catalog Python client |
| `cianfhoghlaim/core/duckdb_extensions/` | Pre-installed extensions (`iceberg`, `httpfs`, `parquet`, `json`) |
| `cianfhoghlaim/core/duckdb_macros/` | Reusable SQL macros (e.g., `uci_normalize()`, `gaelic_check()`) |
| `stacks/lakehouse/init-db.sql` | Postgres catalog initialization (Lakehouse + Cognee + MotherDuck schema) |
| `stacks/lakehouse/garage.toml` | Garage S3 bucket layout (`lakehouse-bucket` with `iceberg/`, `lance/`, `ducklake/` subdirs) |
| `motherduck-mcp` (MCP server) | Managed DuckDB service for cross-host queries |

**Canonical DuckLake attach example** (`cianfhoghlaim/core/ducklake/client.py`):

```python
import duckdb

def attach_lakehouse(connection: duckdb.DuckDBPyConnection) -> None:
    """Attach the Cianfhoghlaim lakehouse as a DuckLake catalog."""
    connection.execute("""
        INSTALL ducklake;
        INSTALL postgres;
        LOAD ducklake;
        LOAD postgres;
        ATTACH 'ducklake:postgres://lakehouse-postgres:5432/lakehouse_catalog'
            AS lakehouse (DATA_PATH 's3://lakehouse-bucket/ducklake/');
    """)

def list_datasets(conn: duckdb.DuckDBPyConnection) -> list[str]:
    """List all datasets in the lakehouse catalog."""
    return [
        row[0]
        for row in conn.execute(
            "SELECT schema_name FROM lakehouse.information_schema.schemata"
        ).fetchall()
    ]
```

**Canonical query** (`oideachais/notebooks/curriculum_educator.py`):

```python
import duckdb
from cianfhoghlaim.core.ducklake.client import attach_lakehouse

conn = duckdb.connect()
attach_lakehouse(conn)

# Cross-corpus topic frequency from DuckLake (the canonical Phase 4 KPI)
df = conn.execute("""
    SELECT
        subject,
        COUNT(DISTINCT exam_year) AS years_covered,
        SUM(n_pages) AS total_pages
    FROM lakehouse.oideachais.examinations_ie
    WHERE topic IN ('algebra', 'calculus', 'geometry')
    GROUP BY subject
    ORDER BY total_pages DESC
""").df()
```

## Env (deployed configuration)

| Env var | Value | Source |
|:--|:--|:--|
| `MOTHERDUCK_TOKEN` | `infisical://dev-baile/motherduck/token` | Locket |
| `DUCKDB_LAKEHOUSE__ATTACH_URI` | `ducklake:postgres://lakehouse-postgres:5432/lakehouse_catalog` | compose env |
| `DUCKDB_LAKEHOUSE__DATA_PATH` | `s3://lakehouse-bucket/ducklake/` | compose env |
| `AWS_ACCESS_KEY_ID` | `${GARAGE_ACCESS_KEY}` | Locket |
| `AWS_SECRET_ACCESS_KEY` | `${GARAGE_SECRET_KEY}` | Locket |
| `AWS_ENDPOINT_URL` | `http://lakehouse-garage:3900` | compose env |

The MotherDuck MCP server exposes 8 tools (`mcp__motherduck__query`, `mcp__motherduck__list_databases`, etc.) for cross-host queries.

## CCC anchors (where this code lives)

```
DuckDB Python wrappers:      cianfhoghlaim/core/duckdb/
DuckLake client:             cianfhoghlaim/core/ducklake/
DuckDB extensions:           cianfhoghlaim/core/duckdb_extensions/
SQL macros:                  cianfhoghlaim/core/duckdb_macros/
MotherDuck MCP:               motherduck MCP (in opencode.json)
MotherDuck init:              cianfhoghlaim/core/motherduck/init.py
Lakehouse stack:              stacks/lakehouse/
Garage bucket config:         stacks/lakehouse/garage.toml
Postgres catalog init:        stacks/lakehouse/init-db.sql
```

Use these CCC search terms:
```
"ATTACH 'ducklake:"              → 7 DuckLake attach call sites
"read_parquet("                  → 23 Parquet read call sites
"INSTALL ducklake"               → 3 install scripts
"MotherDuckToken"                → MCP token plumbing
"duckdb.DuckDBPyConnection"      → Python connection usage
```

## Drift log

| Date | Event | Action |
|:--|:--|:--|
| 2025-Q3 | Initial DuckDB 0.10 (raw Parquet on S3) | Used for BAML extraction preview queries |
| 2025-Q4 | Switched to DuckDB 1.0 + iceberg extension | Replaced custom Parquet reader |
| 2026-01 | Adopted DuckLake 0.3 | First time ACID on object storage worked |
| 2026-02 | Added MotherDuck MCP server | Enabled cross-host queries |
| 2026-03 | Added 12 DuckDB SQL macros | Reduced query boilerplate by 40% |
| 2026-05 | Upgraded to DuckDB 1.2 | Better parallel query execution |
| 2026-06-04 | Archived `extend-lakehouse-with-nimtable-olake-lancedb` change | 8 requirements, validated |
| 2026-06-28 | v4 consolidation: `sruth/oideachais/dlt_utils/ducklake_options.py` → `cianfhoghlaim/core/ducklake/` | Pure rename |

Current version pins:
```toml
[project.dependencies]
duckdb = ">=1.2.0,<2.0.0"
ducklake = ">=0.3.0,<1.0.0"
motherduck = ">=0.5.0,<1.0.0"
```

## Anti-patterns (don't do this)

1. **Don't store Postgres catalog credentials in `~/.duckdb/stored_state`.** Use the Locket + Infisical pattern via `DUCKDB_LAKEHOUSE__ATTACH_URI`.
2. **Don't use `COPY ... TO 's3://...'` directly.** Use `COPY ... TO lakehouse.dataset_name` (DuckLake catalog abstraction) — this lets the catalog track lineage + Iceberg ACID semantics.
3. **Don't install extensions via Python on every connection.** Install them once in `init.sql` and rely on `~/.duckdb/extensions/` persistence.
4. **Don't use `read_parquet()` over `read_csv_auto()` for CSV data.** DuckDB's CSV reader is fine but `read_csv_auto` infers types better.
5. **Don't put credentials in SQL strings** like `ATTACH 'postgres://user:pass@host/db'`. Use environment variables: `ATTACH 'postgres://user::host/db' WHERE password = getenv('POSTGRES_PASSWORD')`.
6. **Don't bypass the DuckLake catalog** for large writes. Use `COPY ... TO lakehouse.dataset` so the catalog tracks partitions + snapshots.
7. **Don't use the `jdbc` extension** unless you've validated the driver — it has known memory leaks with PostgreSQL catalogs.

## Decision matrix (Phase 1A-04 conclusion)

| Decision | Choice | Rationale |
|:--|:--|:--|
| Catalog format | DuckLake 0.3 (built on DuckDB + Postgres) | Simpler than Iceberg; ACID on object storage |
| Object storage | Garage S3 (S3-compatible) | Already deployed in lakehouse stack |
| Query interface | MotherDuck MCP + direct DuckDB | Dual-mode (local + managed) |
| SQL extensions | `iceberg`, `httpfs`, `parquet`, `json` | Pre-installed in `core/duckdb_extensions/` |
| Backup strategy | Daily `COPY ... TO parquet` snapshots | Off-catalog safety net |
| Cross-host access | MotherDuck (managed service) | Avoids running DuckDB on every host |
| Local development | `USE_LOCAL_SCRAPES=true` + MotherDuck dev token | Same API surface as production |
| Security | Locket + Infisical (no plaintext) | Per `.agents/skills/secrets-management/` |

## Anti-pattern priority for Phase 1A-05

When researching MotherDuck next, look for:
- The MotherDuck-specific SQL dialect extensions (`md:` prefix)
- `ATTACH 'md:my_database'` (cloud database attach)
- `CREATE SHARE` syntax (zero-copy data sharing with orgs)
- The `motherduck-mcp` tool list (8 tools total)
- Cloud-vs-self-hosted decision matrix

## Files to read next

- `cianfhoghlaim/core/ducklake/client.py` — canonical DuckLake attach
- `stacks/lakehouse/init-db.sql` — Postgres catalog schema
- `stacks/lakehouse/garage.toml` — Garage S3 bucket layout
- `docs/skills/duckdb/SKILL.md` — canonical DuckDB skill
- `docs/skills/ducklake/SKILL.md` — canonical DuckLake skill
