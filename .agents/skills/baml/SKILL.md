# BAML Skill

## Context
Use this when designing extraction schemas for the `meaisínfhoghlaim` brain.

## Rules
- Define all prompt engineering and extraction boundaries in `.baml` files within `oideachais/baml_src/`.
- Use BAML to enforce Zod-like constraints on the LLM output, preventing parser crashes downstream in the Dagster/DLT pipelines.
- Ensure the extraction schemas map directly to the `DuckLake` tables defined in `oideachais/data_platform/dlt_sources/ireland/`.
