# DuckLake — Lightweight Data Lakehouse on Object Storage

## Overview

DuckLake is a lightweight data lakehouse that provides ACID transactions, time travel, and schema evolution on object storage (S3-compatible) using DuckDB as the query engine. Think of it as DuckDB + Iceberg semantics without the heavyweight infrastructure — tables are stored as Parquet files with Iceberg metadata on Garage S3.

## Why This Matters for Kings' College Galway

DuckLake is the analytical backbone of the curriculum data platform. Every DLT ingestion pipeline writes Parquet files to Garage S3, and DuckLake registers them as versioned tables with time-travel capability. This means curriculum researchers can query "what did the syllabus look like before the 2023 reform?" without maintaining separate database snapshots. The Lance Namespace sidecar bridges DuckLake's SQL tables with LanceDB's vector indexes, enabling hybrid SQL+semantic search across the same curriculum data.

## Key Features

- **ACID on S3** — Snapshot isolation, time travel, schema evolution via Iceberg
- **DuckDB-powered** — Same SQL engine, same extensions, same performance
- **Zero-copy branching** — Create branches of data without duplicating storage
- **Schema evolution** — Add/drop/rename columns without rewriting data
- **Garage S3 native** — Designed for self-hosted S3-compatible storage

## Installation

```bash
uv add ducklake
```

## Integration with Our Stack

DuckLake sits between Garage S3 (storage) and Lakekeeper (Iceberg catalog). Dagster jobs write to DuckLake tables; marimo notebooks query them; the Lance Namespace registers them as Iceberg tables for unified catalog discovery.

## Upstream

- **Documentation**: Project-specific — built on DuckDB + Iceberg + Garage S3 integration
- **Latest**: Active development as part of the Kings' College Galway infrastructure

## Screenshot

DuckLake is a programmatic library with no UI. Query results appear in Dagster materialization logs, marimo notebook cells, and DuckDB's SQL shell. The Lakekeeper catalog UI (Nimtable) provides graphical table discovery for DuckLake-managed tables.
