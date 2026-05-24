# DLT Skill

## Context
When assuming the `data-engineer` persona, use this skill to understand the DLT pipelines.

## Rules
- Use `dlt.pipeline` initialized with a DuckLake or DuckDB destination.
- Disable plugins during testing by setting `DLT_DISABLE_PLUGINS=true`.
- The main pipeline is currently located at `oideachais/data_platform/dlt_sources`.
- All `oideachais` absolute imports have been removed; use relative or local `dlt_sources` imports.
