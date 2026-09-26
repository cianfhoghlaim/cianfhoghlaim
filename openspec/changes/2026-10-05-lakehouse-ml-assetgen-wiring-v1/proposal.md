# Change: 2026-10-05-lakehouse-ml-assetgen-wiring-v1

## Why

The Lakehouse stack has 17 services in compose but only 9 currently
running on bunchloch. The 8 currently-down services (garage + garage-init +
nimtable + olake + graphiti + falkordb + memgraph(-lab) + otel-collector)
block the asset bridge — the LanceDB → DuckLake → Iceberg pipeline
that lets assets (image_gen + retro_design + fibo) become queryable via SQL.

Plus the asset bridge code itself is missing — there's no
`orchestration/assets/ducklake_maintenance.py` to sync the LanceDB
asset catalog into the DuckLake → Iceberg catalog, and no marimo
dashboard that queries the per-asset Lakehouse table.

This is Plan 5 of the convergence saga
(`openspec/plans/2026-10-01-convergence-saga-v1.md`).

## What Changes

### Code — new (~4 files)
- `orchestration/assets/ducklake_maintenance.py` — the Lakehouse bridge
  - `sync_lancedb_to_iceberg(table_name, lance_db_uri)` — moves a LanceDB
    table into the Iceberg catalog (Lakekeeper-managed)
  - `register_asset_table()` — registers the `media.image_gen_chunks`
    table in the Iceberg catalog (so it's queryable via SQL via DuckLake)
  - `create_ducklake_assets_database()` — creates the
    `ducklake_cianfhoghlaim.media` schema if it doesn't exist
- `orchestration/assets/otel_image_gen_traces.py` — OTel spans for the
  DLT → BAML → CocoIndex → image-gen → LanceDB → DuckLake chain
- `notebooks/dashboards/asset_lakehouse_browser.py` — marimo dashboard
  that queries the asset table via DuckLake SQL

### Spec materialised
- `openspec/specs/lakehouse-assetgen-wiring/spec.md` — 4 Requirements

### Reference surfaces
- `bonneagar/stacks/lakehouse/compose.yaml` — the 17-service unified data plane
- `bonneagar/stacks/lakehouse/init-db.sql` — the lakehouse database init
- `agents/adk/tools/image_generation.py` — the image-gen tool (writes to LanceDB)
- `agents/adk/tools/retro_pattern_extractor.py` — the retro pattern tool (writes to LanceDB)
- `tuatha/asset_generation/fibo/assets.py` — the FIBO asset tool (writes to LanceDB)

## What this does NOT ship
- The 3 image-pull issues (olake + graphiti:local + memgraph-mage 3.6.0 don't exist on dockerhub). These are infrastructure issues out of scope; Plan 5 ships the soft bridge code + spec, Plan 7 (Celtic) + Plan 8 (Tuatha) handle the full image-bringup
- The full lakehouse-postgres init-db.sql run (the lakehouse databases aren't initialized yet)
- The lakehouse-postgres → Lakekeeper → Iceberg → LanceDB full chain (depends on the init-db run)

Licence: BUSL-1.1 Cianfhoghlaim edition (per LICENSE.md).
