# `croilar-data-engineering` capability spec (NEW)

The Dagster + DLT + CocoIndex + BAML data-engineering layer for the croilar subproject. Cross-links with the existing oideachais + meaisínfhoghlaim outputs via the DuckLake catalog (the lakehouse stack).

## ADDED Requirements

### Requirement: Dagster Asset Catalog
The system SHALL define 12+ Dagster assets covering music ingestion, CV extraction, teaching record, identity verification, and cross-link with oideachais + meaisínfhoghlaim.

#### Scenario: Music pipeline assets
- **WHEN** the Dagster UI is opened
- **THEN** the asset catalog SHALL include `spotify_ingestion`, `soundcloud_ingestion`, `youtube_ingestion`, and `track_metadata_embedded`
- **AND** each asset SHALL be materializable independently

#### Scenario: CV pipeline assets
- **WHEN** the Dagster UI is opened
- **THEN** the asset catalog SHALL include `cv_pdf_ingestion`, `cv_extraction`, and `cv_search_index`
- **AND** `cv_pdf_ingestion` SHALL ingest from `author_cian_deacy_lyons_mac_an_déisigh_uí_liatháin/achievement/` and `teaching/`
- **AND** `cv_extraction` SHALL use BAML `cv_extraction.baml` and `teaching_extraction.baml`

#### Scenario: Identity pipeline assets
- **WHEN** the Dagster UI is opened
- **THEN** the asset catalog SHALL include `id_document_verification` which uses BAML `identity_verification.baml`

#### Scenario: Cross-link assets
- **WHEN** the Dagster UI is opened
- **THEN** the asset catalog SHALL include `oideachais_assets_embedded` and `meaisinfhoghlaim_assets_embedded`
- **AND** these assets SHALL read from the DuckLake catalog (the existing `storage/lakehouse` stack)
- **AND** the read path SHALL be read-only (no writes back to oideachais / meaisínfhoghlaim DBs)

### Requirement: BAML Extraction Schemas
The system SHALL define BAML schemas for the 3 new extraction tasks (CV, teaching, identity).

#### Scenario: cv_extraction.baml compiles
- **WHEN** `bun run baml-cli compile` is run
- **THEN** the BAML compiler SHALL emit TypeScript + Python client code from `sruth/croilar/baml/cv_extraction.baml`
- **AND** the client SHALL expose `ExtractCV`, `ExtractEducationEntry`, `ExtractAward`, `ExtractPublication`, `ExtractReference` functions

#### Scenario: teaching_extraction.baml compiles
- **WHEN** `bun run baml-cli compile` is run
- **THEN** the compiler SHALL emit the same way from `teaching_extraction.baml`
- **AND** the client SHALL expose `ExtractPlacement`, `ExtractStudentFeedback`, `ExtractCurriculumDesigned` functions

#### Scenario: identity_verification.baml compiles
- **WHEN** `bun run baml-cli compile` is run
- **THEN** the compiler SHALL emit from `identity_verification.baml`
- **AND** the client SHALL expose `ExtractDocumentType`, `ExtractIssuingAuthority`, `ExtractExpiryDate` functions

### Requirement: Dagster Schedules
The system SHALL schedule the 12+ assets to run on appropriate cadences.

#### Scenario: Daily music ingestion
- **WHEN** the daily schedule fires at 03:00
- **THEN** all 4 music pipeline assets SHALL be materialized in dependency order

#### Scenario: Weekly CV refresh
- **WHEN** the weekly schedule fires on Sunday at 04:00
- **THEN** the 3 CV pipeline assets SHALL be materialized in dependency order
- **AND** the `cv_search_index` SHALL be re-built and the website search index SHALL be refreshed

#### Scenario: Monthly identity verification
- **WHEN** the monthly schedule fires on the 1st at 05:00
- **THEN** the identity pipeline assets SHALL be materialized
- **AND** any expired identity documents SHALL be flagged in the Dagster UI

### Requirement: DuckLake Cross-DB Read
The system SHALL use the existing DuckLake catalog (the `storage/lakehouse` stack) for cross-DB reads.

#### Scenario: oideachais assets read via DuckLake
- **WHEN** `oideachais_assets_embedded` materializes
- **THEN** Dagster SHALL query the DuckLake catalog for the latest `oideachais.curriculum` table
- **AND** the data SHALL be embedded via CocoIndex and stored in the `croilar_embeddings` table

#### Scenario: meaisínfhoghlaim assets read via DuckLake
- **WHEN** `meaisinfhoghlaim_assets_embedded` materializes
- **THEN** Dagster SHALL query the DuckLake catalog for the latest `meaisinfhoghlaim.ocr` and `meaisinfhoghlaim.asr` tables
- **AND** the data SHALL be embedded and cross-linked to the CV / research subprojects
