---
domain: data_platform
title: Data Platform Documentation
description: Canonical index for the Cianfhoghlaim data platform — architecture, orchestration, ingestion, and storage.
updated: 2026-06-06
ccc_query_hints:
  - data platform architecture
  - dagster orchestration
  - dlt pipelines
  - lakehouse duckdb ducklake
  - motherduck
---

# Data Platform — Canonical Documentation

## Documents

| File | Purpose |
|------|---------|
| [data-architecture.md](./data-architecture.md) | Lakehouse architecture, DuckDB/DuckLake, S3 Garage, Cloudflare R2, MotherDuck, storage patterns |
| [dagster-orchestration.md](./dagster-orchestration.md) | Dagster assets, partitions, schedules, sensors, jobs, dg workspace, definitions.py patterns |
| [dlt-pipelines.md](./dlt-pipelines.md) | DLT filesystem pipelines, REST API pipelines, sources, destinations, incremental loading, safety layer |

## Architecture Overview

```
Data Sources → DLT Ingestion → Storage & Cataloging → Transformation & Enrichment → Semantic / Feature Store → ML & Analytics → Orchestration & Observability
```

### 6-Layer Data Stack

| Layer | Technologies |
|-------|-------------|
| **Layer 1: Intelligent Ingestion** | DLT, Git Sparse-Checkout, Crawl4AI, Firecrawl |
| **Layer 2: Storage & Cataloging** | DuckLake, DuckDB, PostgreSQL, R2/S3 Garage, MotherDuck |
| **Layer 3: Transformation & Enrichment** | SQLMesh, Ibis, CocoIndex |
| **Layer 4a: Semantic Store** | CocoIndex (vectors), LanceDB (ANN), pgvector |
| **Layer 4b: Feature Store** | Feast (offline: DuckDB), DragonflyDB (online) |
| **Layer 5: ML & Analytics** | MLflow, Agno + BAML, RisingWave |
| **Layer 6: Orchestration** | Dagster (asset-based), CocoInsight (lineage) |

## Key Constraints

- **DuckDB**: SINGLE_THREADED_ONLY — use SerialDatabaseExecutor
- **LanceDB**: MVCC safe, single-threaded within process
- **Embeddings**: Batch minimum 100 texts per API call
- **HNSW**: Drop indexes before bulk inserts >50 rows
- **Schema**: BAML validation required for LLM extractions
- **Irish**: Use UCCIX or GaBERT specialized models

## Source Archives

Merged from:
- `docs/data_engineering/` (28 files) → [2026-06-06-data-engineering](../archive/2026-06-06-data-engineering/)
- `docs/context/` (108 files) → [2026-06-06-context](../archive/2026-06-06-context/)
