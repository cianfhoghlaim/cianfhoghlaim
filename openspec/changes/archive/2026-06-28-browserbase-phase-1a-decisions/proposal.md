# Change: 2026-06-28-browserbase-phase-1a-decisions

> **STUB — TO BE FILLED BY PHASE 1A RESEARCH AGENT.** This change
> consolidates the 5 Phase 1A decisions that emerge from the 2026-06-28
> BrowserBase 6,000-credit research program.
>
> See `openspec/research/2026-06-28-browserbase-credit-program/phase-1a/`
> for the actual research output (one `.md` file per prompt).

## Why

Phase 1A covers the **data plane** — 5 prompts × 180 credits = 900
total credits spent on the foundational packages that the rest of the
Cianfhoghlaim stack depends on:

- **P1A-01 dlt + dlthub-pro** — `dlt` ingestion patterns, hub profiles,
  transformations, data-quality rules
- **P1A-02 Dagster** — MultiPartitionsDefinition, dg CLI, dlt_assets
  wrapping, asset_check / asset_sensor / asset_observation
- **P1A-03 CocoIndex v1** — `coco.App` + `@coco.fn` + `ContextKey` +
  `mount_table_target` pattern; the 14 v1 Apps in `oideachais/cocoindex_flows/`
- **P1A-04 DuckDB + DuckLake** — `ATTACH 'ducklake:...'`, catalog
  metadata in Postgres, ACID on Garage S3
- **P1A-05 MotherDuck** — managed DuckDB service; Postgres endpoint vs
  native DuckDB API; Dives; data shares

## Cross-links

- Cross-references 2 canonical specs: `oideachais-pipeline` and
  `celtic-asset-generation`
- Companion to: `litellm-minimax-vendor-derisking` (LLM gateway choice)
- Output tree: `openspec/research/2026-06-28-browserbase-credit-program/phase-1a/`

## Requirements

_Filled by Phase 1A research agent after each prompt completes._
