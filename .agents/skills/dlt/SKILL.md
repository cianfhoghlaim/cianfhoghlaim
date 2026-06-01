---
name: dlt
description: Master routing skill for data load tool (dlt). Use this to understand dlt rules and determine which specialized dlt workbench skill to invoke.
---

# DLT Master Router & Rules

You are operating within the `cianfhoghlaim` stack which utilizes `dlt` (data load tool) for extracting and loading data.

## Context & Core Rules
When assuming the `data-engineer` persona, use these rules to understand the DLT pipelines:
- Use `dlt.pipeline` initialized with a DuckLake or DuckDB destination.
- Disable plugins during testing by setting `DLT_DISABLE_PLUGINS=true`.
- The main pipeline is currently located at `oideachais/data_platform/dlt_sources`.
- All `oideachais` absolute imports have been removed; use relative or local `dlt_sources` imports (e.g. `from dlt_sources.ireland...`).
- Offline Fallback (`USE_LOCAL_SCRAPES=true`): To avoid API rate limits, pipelines intercept network calls and load from `stedding/ingest_queue/`.

## Specialized Sub-Skills
When tasked with DLT operations or data exploration, use this guide to invoke the most appropriate sub-skill:

### Data Exploration & Notebooks (oideachais/notebooks)
- **`explore-data`**: Use to analyze datasets and create an `analysis_plan.md` artifact.
- **`build-notebook`**: Use to assemble or regenerate a marimo notebook from an `analysis_plan.md`. This is critical for maintaining the notebooks in `oideachais/notebooks`.

### Pipeline Creation & Maintenance
- **`create-filesystem-pipeline`**: Use to build pipelines that read from local files, which is highly relevant for our `USE_LOCAL_SCRAPES` offline fallback pattern.
- **`add-incremental-loading`**: Use to add state and incremental extraction to a filesystem pipeline.
- **`create-rest-api-pipeline`**: Use for generic REST/HTTP API sources.
