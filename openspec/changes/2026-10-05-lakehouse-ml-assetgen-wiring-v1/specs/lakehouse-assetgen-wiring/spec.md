# lakehouse-assetgen-wiring Specification

## Purpose
`lakehouse-assetgen-wiring` is the contract for the Lakehouse bridge
that connects the agent fleet's asset generation (image_gen + retro_design
+ fibo) to the unified data plane (LanceDB → DuckLake → Iceberg via
Lakekeeper + Garage). Once wired, assets become queryable via SQL via
DuckLake (so marimo dashboards can render the asset catalog) + the
Iceberg catalog (so external BI tools can consume the same data).

Per the 2026-10-05-lakehouse-ml-assetgen-wiring-v1 saga change (Plan 5 of
`openspec/plans/2026-10-01-convergence-saga-v1.md`).

## ADDED Requirements

### Requirement: DuckLake → Iceberg asset table registration

The system MUST register the per-asset LanceDB tables (image_gen_chunks,
retro_design_patterns, fibo_assets) in the Iceberg catalog (Lakekeeper-
managed) so they're queryable via SQL via DuckLake. The system MUST
create the `ducklake_cianfhoghlaim.media` schema if it doesn't exist.

#### Scenario: media.image_gen_chunks becomes queryable via DuckLake SQL
- **GIVEN** `agents/adk/tools/image_generation.py` writes assets to LanceDB at `lance://media.image_gen_chunks`
- **WHEN** `register_asset_table("image_gen_chunks")` runs (in `orchestration/assets/ducklake_maintenance.py`)
- **THEN** the table is registered in the Iceberg catalog (under `media.image_gen_chunks`)
- **AND** a `ducklake_cianfhoghlaim.media.image_gen_chunks` view is created that points at the Iceberg table
- **AND** `SELECT * FROM ducklake_cianfhoghlaim.media.image_gen_chunks WHERE subject = 'chemistry'` returns the chemistry assets

### Requirement: LanceDB → Iceberg sync

The system MUST provide a `sync_lancedb_to_iceberg(table_name, lance_db_uri)` function that:
1. Reads the LanceDB table
2. Writes the rows to the corresponding Iceberg table (via Garage S3 + Lakekeeper)
3. Updates the DuckLake view metadata
4. Returns the row count + the sha256 of the Iceberg manifest

#### Scenario: sync_lancedb_to_iceberg moves 100 rows
- **WHEN** `sync_lancedb_to_iceberg("image_gen_chunks", "lance://media/image_gen_chunks")` runs
- **THEN** 100 rows are written to the Iceberg table
- **AND** the function returns `{"rows_written": 100, "manifest_sha256": "abc..."}`

### Requirement: OTel spans for the asset-gen chain

The system MUST emit OTel spans for the full DLT → BAML → CocoIndex →
image-gen → LanceDB → DuckLake → Iceberg chain. Each span MUST carry:
- `asset.asset_id`
- `asset.subject`
- `asset.role` (one of: default / fast / bilingual / legacy / diagrams)
- `asset.prompt_sha256` (the hash of the input prompt)
- `asset.litellm_alias` (the model that was called)
- `asset.lancedb_table` (the target LanceDB table)

#### Scenario: OTel collector receives the spans
- **WHEN** `agents/adk/tools/image_generation.py:generate_2d_asset` runs
- **THEN** the OTel collector at `otel-collector:4317` (or `http://localhost:4318` for HTTP) receives 5 spans: `dlt.load` → `baml.extract` → `cocoindex.embed` → `image_gen.litellm` → `lancedb.upsert`
- **AND** each span carries the `asset.*` attributes

### Requirement: Asset Lakehouse browser (marimo dashboard)

The system MUST provide a marimo dashboard at
`notebooks/dashboards/asset_lakehouse_browser.py` that:
1. Queries the asset table via DuckLake SQL
2. Lets the operator filter by subject + role + language + palette
3. Shows the asset metadata + the OTel trace IDs
4. Lets the operator click through to the source PDF (when the asset has a `source_pdf` provenance field)

#### Scenario: Chemistry asset browser shows 12 rows
- **GIVEN** the chemistry subject has 12 generated assets in `media.image_gen_chunks`
- **WHEN** the operator opens the marimo dashboard
- **THEN** the chemistry filter shows 12 rows (one per role + per iteration)
- **AND** clicking a row expands to show the prompt + the validation score + the OTel trace ID
