---
title: 'Dagster Python SDK — Data Orchestration Framework'
domain: 'data_platform'
status: 'stable'
description: 'Dagster is an open-source data orchestration platform for building, testing, and running data pipelines. The Python SDK provides decorators (`@asset`, `@op`, `@job`, `@schedule`, `@sensor`) for defining data assets with typed dependencies, automatic lineage tracking, and rich met'
read_when:
  - looking for documentation on this topic
updated: '2026-06-10'
supersedes:
  - docs/dagster-sdk.md
ccc_query_hints:
  - dagster python sdk — data orchestration 
---

# Dagster Python SDK — Data Orchestration Framework

## Overview

Dagster is an open-source data orchestration platform for building, testing, and running data pipelines. The Python SDK provides decorators (`@asset`, `@op`, `@job`, `@schedule`, `@sensor`) for defining data assets with typed dependencies, automatic lineage tracking, and rich metadata. Created by Dagster Labs, it is the orchestration layer for all curriculum data pipelines.

## Why This Matters for Kings' College Galway

Every data operation in the platform is a Dagster asset: DLT ingestion runs, curriculum extraction jobs, model conversions (HF → GGUF), embedding generation, image asset creation, and RAGAS evaluation. The asset graph provides a visual map of all data dependencies — from raw SEC exam PDFs through to published study assets. This lineage is essential for educational content: every generated study resource is traceable back to its source syllabus document and the LLM model that produced it.

## Key Features

- **Asset-based architecture** — Define data products, not just task sequences
- **Automatic lineage** — Dagster traces dependencies between assets
- **Partitioning** — Process data by time, subject, or curriculum cycle
- **I/O management** — Pluggable I/O managers for DuckDB, S3, LanceDB
- **Rich metadata** — Attach markdown, tables, and URLs to asset materializations

## Installation

```bash
uv add dagster dagster-duckdb dagster-dlt
```

## Integration with Our Stack

Dagster assets live in `oideachais/data_platform/dagster_defs/`. The `dg.toml` file configures the workspace. Assets interact with dlt (ingestion), BAML (extraction), DuckDB (analytics), LanceDB (embeddings), and the LiteLLM gateway (LLM calls). The Dagster UI runs at port 3335 (engineering stack) or 3000 (croilar-dagster stack).

## Upstream

- **Repository**: <https://github.com/dagster-io/dagster>
- **Documentation**: <https://docs.dagster.io>
- **Latest**: v1.13.x (2025) — branch deployments, AI skills integration, improved partitioning

## Screenshot

Dagster's web UI (Dagit) shows: an asset graph with nodes colour-coded by materialization status, a run timeline showing pipeline execution history, per-asset detail views with metadata and lineage, and a job launcher for triggering pipeline runs. The asset graph for the curriculum pipeline shows 4 layer groups (Ingestion → Materials → Model Lifecycle → Asset Generation).
