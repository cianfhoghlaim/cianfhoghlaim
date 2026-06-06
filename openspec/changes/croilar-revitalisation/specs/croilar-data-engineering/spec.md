# `croilar-data-engineering` spec delta — MODIFIED for per-persona pipelines

## MODIFIED Requirements

### Requirement: Dagster Asset Catalog with Persona Groups
The system SHALL extend the existing 15-asset Dagster catalog to group assets by persona.

#### Scenario: Aleyum asset group
- **WHEN** the Dagster UI is opened
- **THEN** the asset catalog SHALL include a group `aleyum` containing `spotify_ingestion`, `soundcloud_ingestion`, `label_ingestion`, `artwork_processing`, `artwork_embedding`
- **AND** each asset SHALL be materializable independently

#### Scenario: Cianfhoghlaim asset group
- **WHEN** the Dagster UI is opened
- **THEN** the asset catalog SHALL include a group `cianfhoghlaim` containing `cv_pdf_ingestion`, `cv_extraction`, `cv_search_index`, `placement_ingestion`, `teaching_extraction`, `teaching_search`
- **AND** assets SHALL accept a `persona` parameter in their config

#### Scenario: Cross-persona assets
- **WHEN** the Dagster UI is opened
- **THEN** the asset catalog SHALL include `oideachais_assets_embedded`, `meaisinfhoghlaim_assets_embedded`, and `motherduck_sync` in a `cross_link` group

### Requirement: BAML Extraction Schemas with Persona Field
The system SHALL add a `persona` discriminator field to all extraction schemas.

#### Scenario: cv_extraction.baml includes persona
- **WHEN** `cv_extraction.baml` is compiled
- **THEN** all extracted records SHALL include a `persona` field set to `"cianfhoghlaim"`
- **AND** records from teaching/achievement dirs SHALL be filterable by persona

#### Scenario: Per-persona BAML schemas
- **WHEN** new persona-specific schemas are added (e.g., `aleyum_music.baml`, `cianfhoghlaim_publications.baml`)
- **THEN** the BAML compiler SHALL emit TypeScript + Python clients for each

### Requirement: Dagster Schedules with Persona Scoping
The system SHALL schedule persona-specific assets on appropriate cadences.

#### Scenario: Aleyum daily music schedule
- **WHEN** the daily schedule fires at 03:00
- **THEN** only aleyum-group assets SHALL be materialized

#### Scenario: Cianfhoghlaim weekly CV schedule
- **WHEN** the weekly CV schedule fires on Sunday at 04:00
- **THEN** only cianfhoghlaim-group assets SHALL be materialized

## ADDED Requirements

### Requirement: MotherDuck Sync Asset
The system SHALL include a Dagster asset `motherduck_sync` that copies DuckDB tables to MotherDuck cloud.

#### Scenario: MotherDuck sync materializes
- **WHEN** `motherduck_sync` is materialized
- **THEN** all tables in `spotify_data`, `github_data`, `cv_data`, and `teaching_data` SHALL be copied to `md:aleyum_md` and `md:cianfhoghlaim_md` per persona
- **AND** the sync SHALL be idempotent (CREATE OR REPLACE)

### Requirement: PlanetScale PostgreSQL Integration
The system SHALL use PlanetScale PostgreSQL as the production database for BetterAuth, Convex, and DuckLake catalog.

#### Scenario: All 3 schemas accessible
- **WHEN** the production stack starts
- **THEN** BetterAuth SHALL connect via pgbouncer port 6432
- **AND** Convex SHALL connect via direct port 5432
- **AND** DuckLake catalog SHALL read/write to `ducklake_catalog_*` schema
