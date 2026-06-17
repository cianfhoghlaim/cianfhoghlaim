# `croilar-data-engineering` capability spec

## Purpose

`croilar-data-engineering` is a capability of the Cianfhoghlaim platform. This document is the canonical capability spec; the corresponding source code lives in the appropriate quadrant. See `docs/00_index.md` for the quadrant map and `docs/00-core/CLAUDE.md` for the project identity.

The Dagster + DLT + CocoIndex + BAML data-engineering layer for the croilar subproject. Cross-links with the existing oideachais + meaisínfhoghlaim outputs via the DuckLake catalog (the lakehouse stack).
## Requirements
### Requirement: Dagster Asset Catalog

The system SHALL continue to emit 9+ stream-driven Dagster assets (music, teaching, cv, research).

#### Scenario: No regression

- **WHEN** `mise turbo build dagster` runs
- **THEN** the asset catalog SHALL still include `music__spotify`, `music__soundcloud`, `music__labels`, `music__artwork`, `teaching__github`, `teaching__linkedin`, `teaching__researchgate`, `cv__cv`, `cv__filesystem`

### Requirement: BAML Extraction Schemas

The system SHALL continue to compile the 9 BAML schemas.

#### Scenario: No regression

- **WHEN** `bun run baml-cli compile` runs
- **THEN** the compiler SHALL still emit TypeScript + Python client code from `croilar/baml/{artwork_analysis, cv_extraction, identity_verification, linkedin_profile_extraction, researchgate_extraction, style_transfer, teaching_extraction, generators, clients}.baml`

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

The system SHALL continue to read from the existing DuckLake catalog.

#### Scenario: No regression

- **WHEN** `oideachais_assets_embedded` or `meaisinfhoghlaim_assets_embedded` materializes
- **THEN** Dagster SHALL continue to query the DuckLake catalog and embed the result

### Requirement: Analyzer Bun Script

The system SHALL ship `croilar/scripts/analyze-web-stack.ts` as a Bun script that walks the monorepo and posts aggregates to Convex.

#### Scenario: Walk succeeds for the 3 present projects

- **WHEN** `bun run croilar/scripts/analyze-web-stack.ts` is executed from the repo root
- **THEN** the analyzer SHALL walk `tuatha/`, `oideachais/`, `croilar/`
- **AND** it SHALL skip `meaisínfhoghlaim/` (no web app yet) with a warning
- **AND** it SHALL POST the resulting 5 tables (tanstackRoutes, convexFunctions, cloudflareResources, bamlSchemas, marimoNotebooks) to the Convex HTTP endpoint
- **AND** authentication SHALL use the `CROILAR_CONVEX_DEPLOY_KEY` from `.env` (loaded from Infisical)

#### Scenario: Walk is idempotent

- **WHEN** the analyzer is run twice in a row
- **THEN** the second run SHALL produce the same set of rows (modulo `lastCommit` / `lastCompiled` / `lastExported` timestamps)
- **AND** no duplicate rows SHALL appear

#### Scenario: Project-scope flag

- **WHEN** the analyzer is invoked with `--project tuatha` (or `oideachais` | `croilar` | `meaisinfhoghlaim`)
- **THEN** it SHALL walk only that project
- **AND** it SHALL exit 0 with a single-line summary

