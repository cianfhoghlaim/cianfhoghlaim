---
name: motherduck-data-modeling
description: Design and load data into MotherDuck. Use when creating tables, choosing column types, defining relationships, restructuring for analytics, or loading data from local files / object storage / HTTPS / dataframes / external databases. Covers the KCG-preferred CTAS + INSERT...SELECT patterns, bulk-loading from Parquet/CSV/JSON, secrets handling for cloud object storage, the Postgres-endpoint vs DuckDB-client tradeoff, and dbt/SQLMesh modeling on top. Triggers: 'CREATE TABLE', 'CTAS', 'INSERT...SELECT', 'load Parquet', 'load CSV', 'schema design', 'dbt project', 'SQLMesh model', 'data modeling'.
---

# MotherDuck — Data Modeling & Ingestion

Design schemas and load data into MotherDuck. Absorbs the former
`motherduck-model-data` and `motherduck-load-data` skills.

## When to use this skill

Use this skill when:

- Designing a new table or database schema for MotherDuck.
- Choosing column types (the DuckDB type system is wide; not all
  map 1:1 to Postgres or BigQuery).
- Loading data from local files (Parquet, CSV, JSON),
  object storage (S3, R2, GCS), HTTPS endpoints, Pandas /
  Polars dataframes, or another database.
- Setting up dbt-duckdb or SQLMesh projects on top of
  MotherDuck.
- Migrating an existing schema (Postgres, Snowflake, BigQuery)
  to MotherDuck.

## Table design (the DuckDB type system)

DuckDB's type system is a superset of Postgres + a handful of
analytics-friendly types. Use them when you can.

| Use case | DuckDB type | Why |
|:--|:--|:--|
| Auto-incrementing ID | `BIGINT` + `SEQUENCE` or `UUID` | Avoid `SERIAL` (Postgres-ism) |
| Categorical | `VARCHAR` (no `ENUM` needed) | ENUMs are rigid; VARCHAR is fine |
| Timestamp with TZ | `TIMESTAMPTZ` | Always TZ-aware for time-series |
| Date only | `DATE` | No `TIMESTAMP` for birthdates |
| High-cardinality string | `VARCHAR` + HASH partitioning | Watch your partition cardinality |
| Wide string (1MB+) | `BLOB` | Avoid `TEXT` for binary content |
| List / array | `INTEGER[]`, `VARCHAR[]`, `STRUCT(...)` | First-class in DuckDB |
| Map | `MAP(VARCHAR, INTEGER)` | First-class in DuckDB |
| Nested JSON | `JSON` (new in 1.1) | First-class with `->`/`->>` operators |
| Embedding vector | `FLOAT[N]` (use LanceDB) | Vector search belongs in LanceDB, not MotherDuck |

Anti-pattern: `FLOAT` without a precision spec. Always use
`DOUBLE` for full IEEE 754 precision; reserve `REAL` for legacy
compat only.

## Loading data — the KCG-preferred path

For KCG workloads, always prefer **CTAS from Parquet on S3**:

```sql
-- Single table from a Parquet file
CREATE TABLE cianfhoghlaim.curriculum_dlt.ie_education_primary
AS
SELECT *
FROM read_parquet('s3://ducklake/staging/ie_education_primary/*.parquet',
                  hive_partitioning = true);

-- Append into an existing table
INSERT INTO cianfhoghlaim.curriculum_dlt.ie_education_primary
SELECT *
FROM read_parquet('s3://ducklake/incoming/ie_education_primary_2026_06_24/*.parquet',
                  hive_partitioning = true);

-- Bulk-load from a Postgres endpoint
INSERT INTO cianfhoghlaim.curriculum_dlt.ie_education_primary
SELECT *
FROM postgres_scan('host=lakehouse-postgres port=5432 dbname=lakehouse',
                   'SELECT * FROM ie_education_primary');
```

**Why CTAS over `COPY`**: CTAS is the only KCG-tested pattern
that handles object-storage paths, hive partitioning, and
zero-copy Parquet reads correctly. The `COPY` command works
but requires the file to be local.

## Loading from dataframes

```python
import duckdb
import pandas as pd

con = duckdb.connect("md:?motherduck_token=...")
con.sql("CREATE OR REPLACE TABLE cianfhoghlaim.curriculum_dlt.ie_education_primary AS "
        "SELECT * FROM df")  # df is a Pandas DataFrame
```

For Polars, the same pattern works (`con.sql("... FROM pl_df")`).

## Loading from HTTPS

```sql
CREATE TABLE cianfhoghlaim.curriculum_dlt.ie_education_primary AS
SELECT *
FROM read_csv('https://example.com/curriculum.csv',
              header = true,
              delim = ',',
              sample_size = 10000);
```

For Parquet over HTTPS: `read_parquet('https://...')`.

## Loading secrets (S3 / R2 / GCS)

Use MotherDuck secrets (one-time set, then transparent to all
queries):

```sql
CREATE SECRET garage_secret (
    TYPE S3,
    KEY_ID 'GK...',
    SECRET '...',
    REGION 'garage',
    ENDPOINT 'lakehouse-garage:3900',
    URL_STYLE 'path',
    USE_SSL false
);
```

After the secret is set, all `read_parquet('s3://...')` calls
just work. **Never put the secret in the connection string or
the SQL text**; always use `CREATE SECRET` so the value never
appears in logs.

## dbt-duckdb on MotherDuck

For analytics modeling, prefer **dbt-duckdb** (with a MotherDuck
profile) or **SQLMesh** with a DuckDB engine. The pattern:

```
orchestration/sqlmesh/
├── dbt_project.yml
├── profiles.yml                # MotherDuck profile
├── models/
│   ├── staging/                # dbt sources → typed views
│   ├── intermediate/           # joined, denormalised
│   └── marts/                  # business-facing tables
└── macros/
    └── motherduck_macros.sql   # CREATE SECRET, ATTACH helpers
```

The dbt-duckdb adapter is the only one that handles the
MotherDuck ATTACH semantics correctly. Do not use
`dbt-postgres` against a MotherDuck Postgres endpoint.

## Schema migration

Three patterns, in order of preference:

1. **CTAS with new schema** — `CREATE OR REPLACE TABLE new AS SELECT * FROM old`
2. **ALTER TABLE ADD COLUMN** — works for nullable columns
3. **Blue-green** — create the new table, dual-write, switch
   the dashboard, drop the old.

Avoid `RENAME COLUMN` on a table that has downstream
`@materialized=incremental` dbt models; it forces a full
re-materialisation.

## Pair this skill with

- `motherduck-architecture/SKILL.md` — pick the storage pattern
- `motherduck-analytics/SKILL.md` — query the tables you just
  designed
- `dlt/SKILL.md` — DLT sources that feed into MotherDuck
- `cianfhoghlaim-storage/SKILL.md` — the KCG DuckLake layout

## Cross-references

- [DuckDB data types](https://duckdb.org/docs/sql/data_types/overview)
- [MotherDuck loading data](https://motherduck.com/docs)
- [dbt-duckdb adapter](https://github.com/duckdb/dbt-duckdb)
