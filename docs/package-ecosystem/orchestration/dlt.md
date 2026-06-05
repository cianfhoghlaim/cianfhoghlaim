# dlt — Data Load Tool (Python SDK)

## Overview

dlt (data load tool) is an open-source Python library for building data ingestion pipelines. It provides a declarative API for extracting data from APIs, files, and databases, normalising nested JSON, inferring schemas, and loading into destinations (DuckDB, MotherDuck, PostgreSQL, BigQuery, etc.). Created by dltHub, it is the ingestion layer for the curriculum data platform.

## Why This Matters for Kings' College Galway

Every data source in the platform — Irish curriculum APIs, UK education databases, SEC exam paper scrapers, HuggingFace model registries — is ingested through dlt pipelines. The library's schema inference automatically handles the inconsistent JSON structures common in government education APIs, and its incremental loading support means each curriculum update only ingests changed records, not the full dataset. The `filesystem` source reads CSV, Parquet, and JSONL files from local disk and S3, powering the offline-first ingestion strategy (`USE_LOCAL_SCRAPES=true`).

## Key Features

- **Declarative pipelines** — `@dlt.resource` and `@dlt.source` decorators
- **Schema inference** — Automatic type detection and normalisation from JSON
- **Incremental loading** — `@dlt.resource(write_disposition="merge")` for upserts
- **30+ destinations** — DuckDB, MotherDuck, PostgreSQL, BigQuery, Snowflake
- **Filesystem source** — Read CSV, Parquet, JSONL from local/S3/GCS/Azure

## Installation

```bash
uv add dlt
# With DuckDB destination:
uv add "dlt[duckdb]"
```

## Integration with Our Stack

dlt pipelines are orchestrated by Dagster assets in `oideachais/data_platform/dagster_defs/`. The `dlt_sources/ireland/` package contains custom sources for Irish curriculum data. Destination is DuckDB (local) or MotherDuck (cloud) via DuckLake tables on Garage S3.

## Upstream

- **Repository**: <https://github.com/dlt-hub/dlt>
- **Documentation**: <https://dlthub.com/docs>
- **Latest**: v1.4.x (2025) — streaming support, dlt+ projects, schema evolution v2

## Screenshot

dlt is a programmatic library with no UI. Pipeline progress is visible in the terminal output showing normalised tables, row counts, and load status. The Dagster UI surfaces dlt pipeline status as asset materializations with metadata (rows loaded, schema changes, errors).
