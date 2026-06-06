# DuckDB — Embedded Analytical Database

## Overview

DuckDB is an open-source, embedded OLAP database management system. It runs in-process (no server needed) and is designed for fast analytical queries on large datasets. Supports SQL, Parquet, CSV, JSON, and Iceberg tables natively. Created by the DuckDB Foundation, it is the analytical engine powering the curriculum data warehouse.

## Why This Matters for Kings' College Galway

Every analytical query in the platform — curriculum statistics, exam paper grade distributions, embedding similarity comparisons, RAGAS evaluation aggregations — runs through DuckDB. It reads Parquet files directly from Garage S3 via the `httpfs` extension and queries Iceberg tables via the Lakekeeper catalog, so there is no ETL step between storage and analytics. The Python API (`duckdb.connect()`) is used in every Dagster asset and marimo notebook, and the SQL dialect is shared with MotherDuck for cloud scaling.

## Key Features

- **Embedded/zero-config** — No server, no daemon, just `import duckdb`
- **Parquet native** — Read/write Parquet files with predicate pushdown
- **Iceberg support** — Query Apache Iceberg tables via the `iceberg` extension
- **Vectorized execution** — Columnar engine optimised for analytical workloads
- **Extensions** — HTTPFS (S3), spatial, full-text search, JSON, and Iceberg

## Installation

```bash
uv add duckdb
```

## Integration with Our Stack

DuckDB connects to Garage S3 via `httpfs` to query Parquet files, and to Lakekeeper's Iceberg REST catalog for catalog-aware queries. The LiteLLM gateway's tracing data and RAGAS evaluation scores are stored as DuckDB tables for analytical querying.

## Upstream

- **Repository**: <https://github.com/duckdb/duckdb>
- **Documentation**: <https://duckdb.org/docs>
- **Latest**: v1.2.x (2025) — Iceberg extension GA, improved Parquet performance, Python 3.13 support

## Screenshot

DuckDB's CLI (`duckdb`) provides an interactive SQL shell with syntax highlighting, table formatting, and `.mode` output options. The Python API is headless — integrate with any dataframe library (Polars, pandas, Ibis) or use `.df()` to convert results.
