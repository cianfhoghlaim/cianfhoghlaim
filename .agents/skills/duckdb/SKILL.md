---
name: duckdb
description: Expert assistance for DuckDB analytical database. Use when users need fast OLAP queries, file-based analytics, Parquet processing, embedded SQL, or local-first data analysis. Powers the BIEP federated SQL layer (`duckdb.connect("md:cianfhoghlaim")` + `lance_scan()` joins DuckLake + LanceDB) for the 6 LC subjects (Mathematics, Chemistry, Geography, Gaeilge, English, Computer Science) and `gov.ie` circulars.
---

# DuckDB - In-Process Analytical Database

**Version:** 1.x | **Last Updated:** 2025-01

## Overview

DuckDB is an in-process OLAP database optimized for analytical workloads:

- **Columnar Storage**: Optimized for analytical queries
- **Vectorized Execution**: High-performance query processing
- **Zero-Copy Integration**: Direct Parquet/Arrow support
- **Embedded**: No server, runs in-process
- **PostgreSQL Dialect**: Familiar SQL syntax

**Documentation**: https://duckdb.org/docs/

## When to Use This Skill

Activate when users need:

- "Analyze Parquet/CSV files with SQL"
- "Fast local analytics without a server"
- "Embedded database for data applications"
- "Process large files with SQL"
- "Query data lakes locally"

## Core Concepts

### 1. Basic Usage

```python
import duckdb

# In-memory database
con = duckdb.connect()

# Or persistent database
con = duckdb.connect('analytics.db')

# Direct file querying (no loading required!)
result = con.execute("""
    SELECT * FROM 'sales.parquet'
    WHERE date >= '2024-01-01'
""").fetchdf()

# Query multiple files with glob
result = con.execute("""
    SELECT * FROM 'data/*.parquet'
""").fetchdf()

con.close()
```

### 2. File Format Support

```sql
-- Parquet (recommended for analytics)
SELECT * FROM 'data.parquet';
SELECT * FROM read_parquet('data/*.parquet');

-- CSV with auto-detection
SELECT * FROM read_csv('data.csv', AUTO_DETECT=TRUE);

-- JSON
SELECT * FROM read_json('data.json');
SELECT * FROM read_json('logs/*.json', format='newline_delimited');

-- Excel (requires extension)
INSTALL spatial; LOAD spatial;
SELECT * FROM st_read('data.xlsx');
```

### 3. Convert CSV to Parquet (600x Faster Queries)

```sql
-- Convert once
COPY (SELECT * FROM 'large_file.csv')
TO 'large_file.parquet' (FORMAT parquet);

-- Query repeatedly (much faster)
SELECT * FROM 'large_file.parquet' WHERE ...;
```

### 4. Python Integration

```python
import duckdb
import pandas as pd

con = duckdb.connect()

# Query to Pandas DataFrame
df = con.execute("SELECT * FROM 'sales.parquet'").fetchdf()

# Query from Pandas DataFrame
df = pd.DataFrame({'a': [1, 2, 3], 'b': [4, 5, 6]})
result = con.execute("SELECT * FROM df WHERE a > 1").fetchdf()

# Zero-copy Arrow integration
import pyarrow as pa
arrow_table = con.execute("SELECT * FROM 'data.parquet'").fetch_arrow_table()

# Polars integration
import polars as pl
polars_df = con.execute("SELECT * FROM 'data.parquet'").pl()
```

### 5. SQL Patterns

```sql
-- Window functions
SELECT
    product_id,
    order_date,
    amount,
    SUM(amount) OVER (
        PARTITION BY product_id
        ORDER BY order_date
    ) as running_total,
    AVG(amount) OVER (
        PARTITION BY product_id
    ) as avg_amount
FROM orders;

-- CTEs for complex queries
WITH monthly_sales AS (
    SELECT
        DATE_TRUNC('month', order_date) as month,
        SUM(amount) as total
    FROM orders
    GROUP BY 1
)
SELECT
    month,
    total,
    LAG(total) OVER (ORDER BY month) as prev_month,
    (total - LAG(total) OVER (ORDER BY month)) / LAG(total) OVER (ORDER BY month) as growth
FROM monthly_sales;

-- QUALIFY for window filtering
SELECT *
FROM orders
QUALIFY ROW_NUMBER() OVER (PARTITION BY customer_id ORDER BY order_date DESC) = 1;

-- List aggregations
SELECT
    customer_id,
    LIST(product_id) as products,
    STRING_AGG(product_name, ', ') as product_names
FROM orders
GROUP BY customer_id;
```

### 6. Complex Types

```sql
-- Arrays/Lists
SELECT list_value(1, 2, 3) as numbers;
SELECT unnest([1, 2, 3]) as number;
SELECT list_filter([1, 2, 3, 4, 5], x -> x > 2);

-- Structs
SELECT {'name': 'John', 'age': 30} as person;
SELECT person.name FROM (SELECT {'name': 'John'} as person);

-- Maps
SELECT map(['a', 'b'], [1, 2]) as my_map;
SELECT my_map['a'] FROM (SELECT map(['a', 'b'], [1, 2]) as my_map);

-- JSON extraction
SELECT
    json_extract(data, '$.name') as name,
    json_extract_string(data, '$.email') as email
FROM events;
```

### 7. Cloud Storage

```sql
-- Install and load httpfs extension
INSTALL httpfs;
LOAD httpfs;

-- Configure S3
SET s3_region = 'us-east-1';
SET s3_access_key_id = 'your_key';
SET s3_secret_access_key = 'your_secret';

-- Query S3 directly
SELECT * FROM 's3://bucket/data/*.parquet';

-- Or use environment variables
-- AWS_ACCESS_KEY_ID, AWS_SECRET_ACCESS_KEY, AWS_DEFAULT_REGION

-- GCS
SET s3_endpoint = 'storage.googleapis.com';
SELECT * FROM 's3://gcs-bucket/data.parquet';
```

### 8. Extensions

```sql
-- List available extensions
SELECT * FROM duckdb_extensions();

-- Install and load extensions
INSTALL spatial;    LOAD spatial;    -- Geospatial
INSTALL httpfs;     LOAD httpfs;     -- S3/HTTP files
INSTALL parquet;    LOAD parquet;    -- Parquet (built-in)
INSTALL json;       LOAD json;       -- JSON (built-in)
INSTALL fts;        LOAD fts;        -- Full-text search
INSTALL postgres_scanner; LOAD postgres_scanner; -- PostgreSQL
INSTALL sqlite_scanner;   LOAD sqlite_scanner;   -- SQLite
INSTALL delta;      LOAD delta;      -- Delta Lake
INSTALL iceberg;    LOAD iceberg;    -- Apache Iceberg
INSTALL excel;      LOAD excel;      -- Excel files
```

### 9. Performance Tuning

```sql
-- Check current settings
SELECT * FROM duckdb_settings() WHERE name LIKE 'memory%';

-- Configure memory
SET memory_limit = '8GB';
SET threads = 4;

-- Profile queries
EXPLAIN SELECT ...;
EXPLAIN ANALYZE SELECT ...;

-- Create indexes (rarely needed)
CREATE INDEX idx_customer ON orders(customer_id);
```

### 10. ETL Patterns

```python
import duckdb

def etl_pipeline(source_path: str, output_path: str):
    """ETL pipeline with DuckDB"""
    con = duckdb.connect()

    # Transform and export
    con.execute(f"""
        COPY (
            SELECT
                customer_id,
                DATE_TRUNC('day', timestamp) as date,
                COUNT(*) as events,
                SUM(amount) as total_amount
            FROM read_parquet('{source_path}/*.parquet')
            WHERE timestamp >= CURRENT_DATE - INTERVAL 30 DAYS
            GROUP BY customer_id, date
        ) TO '{output_path}' (FORMAT parquet, COMPRESSION zstd)
    """)

    con.close()

# Usage
etl_pipeline('raw_data', 'processed/daily_summary.parquet')
```

## CLI Usage

```bash
# Start interactive CLI
duckdb

# Start with database file
duckdb analytics.db

# Execute single query
duckdb -c "SELECT * FROM 'data.parquet' LIMIT 10"

# Execute SQL file
duckdb < query.sql

# Export to CSV
duckdb -c "COPY (SELECT * FROM 'data.parquet') TO 'output.csv'"
```

## Decision Guide

### Use DuckDB When:
- Single-machine analytics
- Processing files (Parquet, CSV, JSON)
- Embedded analytics in applications
- Data science/ML pipelines
- Local-first workflows
- ETL transformations

### Don't Use DuckDB When:
- Multi-user concurrent writes needed
- Distributed architecture required
- High-frequency transactions (OLTP)
- Network database server needed

### DuckDB vs Alternatives

| Use Case | Recommendation |
|----------|----------------|
| Analytical queries | DuckDB |
| Transactions (OLTP) | SQLite, PostgreSQL |
| Multi-user server | PostgreSQL |
| Distributed | Spark, ClickHouse |

## Best Practices

1. **Use Parquet**: Convert CSV to Parquet for 600x faster queries
2. **Reuse Connections**: Don't create new connection per query
3. **Select Specific Columns**: Avoid SELECT * in production
4. **Profile Queries**: Use EXPLAIN ANALYZE to find bottlenecks
5. **Configure Memory**: Set memory_limit based on available RAM
6. **Direct File Queries**: Query files directly, no loading needed
7. **Use Parameterized Queries**: Prevent SQL injection

## Troubleshooting

### Memory Issues
```sql
-- Reduce memory limit
SET memory_limit = '2GB';

-- Check current usage
SELECT * FROM duckdb_settings() WHERE name = 'memory_limit';
```

### Performance Issues
```sql
-- Profile the query
EXPLAIN ANALYZE SELECT ...;

-- Ensure using Parquet
COPY (SELECT * FROM 'data.csv') TO 'data.parquet' (FORMAT parquet);
```

### Connection Issues
```python
# Bad: Creating connection repeatedly
for file in files:
    con = duckdb.connect()
    con.execute(f"SELECT * FROM '{file}'")
    con.close()

# Good: Reuse connection
con = duckdb.connect()
for file in files:
    con.execute(f"SELECT * FROM '{file}'")
con.close()
```

## Resources

- **Documentation**: https://duckdb.org/docs/
- **SQL Reference**: https://duckdb.org/docs/sql/introduction
- **Extensions**: https://duckdb.org/docs/extensions/overview
- **GitHub**: https://github.com/duckdb/duckdb

## British-Isles Education pipeline — Canonical KCG pattern (post-v4)

The post-v4 BIEP (`openspec/changes/lc6-biep/`) uses DuckDB as
the **federated SQL layer** that joins DuckLake (the OLTP sink
for BAML-extracted rows) with LanceDB (the vector store for
chunks) via `lance_scan()`. The canonical connection string is
`md:cianfhoghlaim` (MotherDuck + DuckLake + Lance Namespace sidecar
on port 9000):

```sql
-- 1. Federated SQL over the lc_mathematics LanceDB chunk table
SELECT * FROM lance_scan('s3://garage/lance/cianfhoghlaim.lc.mathematics.higher_en/*.lance');

-- 2. Federated SQL joining DuckLake + LanceDB in one query
SELECT
    d.subject,
    d.module_id,
    d.title,
    count(c.chunk_id) AS n_chunks,
    avg(c.similarity) AS avg_sim
FROM cianfhoghlaim.leaving_cert.curriculum_syllabus d
JOIN lance_scan(
    's3://garage/lance/cianfhoghlaim.lc.mathematics.higher_en/*.lance'
) c
  ON d.subject = c.subject
WHERE d.level = 'higher'
  AND d.language = 'en'
GROUP BY d.subject, d.module_id, d.title
ORDER BY n_chunks DESC
LIMIT 25;
```

```python
import duckdb

# The KCG-preferred pattern: federated SQL via MotherDuck + DuckLake
con = duckdb.connect("md:cianfhoghlaim")  # MOTHERDUCK_TOKEN from Infisical

# Pull the Mathematics syllabus topics (DuckLake) + LanceDB chunks in one go
df = con.execute("""
    SELECT
        d.subject,
        d.level || '_' || d.language AS partition,
        d.module_id,
        d.title,
        count(c.chunk_id) AS n_chunks
    FROM cianfhoghlaim.leaving_cert.curriculum_syllabus d
    LEFT JOIN lance_scan(
        's3://garage/lance/cianfhoghlaim.lc.mathematics.higher_en/*.lance'
    ) c ON d.subject = c.subject
    WHERE d.subject IN (
        'mathematics', 'chemistry', 'geography',
        'gaeilge', 'english', 'computer_science'
    )
    GROUP BY d.subject, partition, d.module_id, d.title
    ORDER BY n_chunks DESC
""").df()
```

**British-Isles Education pipeline use case:**

- **6 LC subjects × 2 languages × 2 levels** — Mathematics,
  Chemistry, Geography, Gaeilge, English, Computer Science,
  each with `en`/`ga` × `higher`/`ordinary` partitions under
  `cianfhoghlaim.leaving_cert.<subject>_<lang>_<level>`.
- **`gov.ie` circulars** — the 7th subject (`government_circulars`)
  populates `cianfhoghlaim.education.ie.gov_circulars_archive`
  in DuckLake + `cianfhoghlaim.education.ie.gov_circulars` in LanceDB.
- **Federated SQL** — the marimo notebooks use
  `duckdb.connect("md:cianfhoghlaim")` to combine BAML-extracted
  DuckLake rows with vector-search LanceDB results in a single
  query.
- **`QUALIFY` for "latest version"** — the BIEP curriculum
  tables are partitioned by `academic_year`; use `QUALIFY
  ROW_NUMBER() OVER (PARTITION BY subject, module_id ORDER BY
  academic_year DESC) = 1` to fetch the latest.

Cross-references:
- [`.agents/skills/ducklake/SKILL.md`](../ducklake/SKILL.md) —
  the DuckLake `ATTACH` for the same `md:cianfhoghlaim` database
- [`.agents/skills/lancedb/SKILL.md`](../lancedb/SKILL.md) —
  the LanceDB `lance_scan()` integration
- [`.agents/skills/motherduck/SKILL.md`](../motherduck/SKILL.md) —
  the 4 Dives that consume the BIEP rows
- [`.agents/skills/marimo/SKILL.md`](../marimo/SKILL.md) — the 6
  per-subject notebooks
- [`.agents/skills/ibis/SKILL.md`](../ibis/SKILL.md) — the Ibis
  backend on top of `md:cianfhoghlaim`
- **GitHub**: https://github.com/duckdb/duckdb
