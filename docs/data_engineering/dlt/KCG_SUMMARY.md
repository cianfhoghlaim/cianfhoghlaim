# dlt (Data Load Tool) — KCG Summary

## What It Is
dlt (Data Load Tool / dlthub) is a Python library for declarative ELT pipelines that infers schemas, normalizes nested JSON, and supports incremental loading into DuckDB, MotherDuck, BigQuery, Snowflake, and more. This directory contains the dlt expert agent documentation, GitHub API research pipeline (multi-source init from API → dlt), dlt + SQLMesh transformation patterns, Small Data SF 2025 workshop materials, BAML + oRPC + MCP typesafe pipeline analysis, and deployment docs for Google Cloud Functions/Run.

## Why This Matters for Kings' College Galway
dlt is the ingestion backbone of the oideachais platform — it loads Leaving Cert examination data from filesystem or REST sources into DuckDB/MotherDuck staging tables. The GitHub API research pipeline provides reusable patterns for `dlt init` source generation and incremental loading configuration. The SQLMesh integration docs show the DLT → SQLMesh transformation handoff. The deployment patterns (Cloud Run, Cloud Functions) inform production pipeline deployment on the Komodo+Pangolin infrastructure.

## Key Patterns Preserved
22 .md files remain, including:
- `dlthub.md` — Full dlt expert agent instruction (501 lines)
- `dlthub-codebase-analysis.md` — Deep analysis of dlt internals
- `dlt-baml-orpc-mcp-typesafe-pipeline-analysis.md` — BAML + oRPC + MCP for typesafe dlt pipelines
- `dlt - SQLMesh.md` — DLT to SQLMesh transformation patterns
- `github_api_init/` (7 .md files) — Comprehensive GitHub API source research: pipeline analysis, comparison with source init, quick reference, executive summary
- `dlt_modal/README.md` — Modal cloud deployment
- `small-data-sf-2025/` (3 files) — Workshop materials: basics, presentation, README
- Deployment docs: Cloud Functions webhook, Cloud Functions deploy, Cloud Run (3 files)
- `Explore data with marimo _ dlt Docs.md` — dlt + marimo data exploration
- `Kafka _ dlt Docs.md` — dlt + Kafka streaming
- `Load Datadog data in Python using dltHub.md` — Observability pipeline
- `Transformations _ dlt Docs.md` — dlt transformation patterns

## Source Files
Full source removed (2026-06-06). Available at https://github.com/dlt-hub/dlt

## What Was Removed
Python source (.py), TOML/JSON/YAML configs, lock files, .gitignore, SQL files, shell scripts, CSV data, Jupyter notebooks
