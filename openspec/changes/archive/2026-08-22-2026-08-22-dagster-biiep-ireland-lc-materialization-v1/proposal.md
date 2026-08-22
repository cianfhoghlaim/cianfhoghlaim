# 2026-08-22-dagster-biiep-ireland-lc-materialization-v1

## Summary

Materializes the Dagster asset chain for the Ireland LC (Leaving Cert) BIEP v3 pipeline against the 80 pre-downloaded PDFs in `/leaving_certificate/`. This is the end-to-end Dagster materialization that the Phase 4 audit was designed to verify. The chain loads PDFs → classifies them → extracts syllabus/exam/marking data via BAML → embeds in LanceDB → cognifies into the knowledge graph.

## Why

The 2026-08-21 Phase 4 audit found that the BIEP LC pipeline was being run via `uv run python -c "..."` against `/tmp/lc5_biep_*.duckdb` — bypassing the Dagster asset chain entirely. The canonical flow per the dagster-5-layer-component-architecture spec requires:

1. **Layer 1 (Ingestion)**: `sf_filesystem_leaving_cert_<subject>` (filesystem scanner for the 80 PDFs)
2. **Layer 2 (Materials)**: `lc5_<subject>_ingested` (per-subject ingestion assets)
3. **Layer 3 (Model Lifecycle)**: `lc5_<subject>_<stage>_extracted` (BAML extraction for syllabus, exam, marking, diagrams)
4. **Layer 4 (Asset Generation)**: `lc5_<subject>_cognified` (cognee knowledge graph)
5. **Layer 5 (Agent Operations)**: `lc5_all_baml_extraction` (umbrella asset)

We need to actually trigger the materialization to prove the 5-layer chain works end-to-end with the v3.30 dlt + v3.15 mlflow + v1.97 litellm + v4.16 langfuse stack.

## What changes

- Trigger the 62 Ireland-LC asset materialization via Dagster.
- Verify each layer produces the expected outputs.
- Capture the materialization run IDs + output rows per asset in `stedding/audit/2026-08-22-dagster-materialization.md`.
- Fix any broken asset definitions discovered during the run.

## Test plan

1. Identify the canonical job that wraps the LC assets.
2. Use `dagster job launch` (CLI) to launch the materialization.
3. Wait for the runs to complete.
4. Verify each asset's output via direct database queries + filesystem checks.
5. If any asset fails, fix the code in `orchestration/defs/` and re-run.

## Rollback

The materialization is non-destructive: it only writes to the destination tables / files. No rollback needed unless the assets corrupt the destination, in which case a `dlt pipeline lc5_biep_test drop` would clear the loaded data.
