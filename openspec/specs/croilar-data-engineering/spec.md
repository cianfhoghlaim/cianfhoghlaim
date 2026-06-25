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
- **THEN** the analyzer SHALL walk `tuatha/`, `sruth/oideachais/`, `croilar/`
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

### Requirement: Aleyum-to-croilar cleanup mandate

The Croílár data-engineering layer SHALL NOT reference the
legacy `aleyum` name in code, env vars, config defaults, or
documentation (with the exception of the `aleyum` persona
identifier in `croilar/config/personas.yaml` + the persona
site routes, which are 1-persona identifiers, not 5-alias
registry entries). The 5 collapsed aliases are:

1. **Env prefix** — `ALEYUM_*` env vars SHALL be renamed to
   `STREAMS_*` (already partially retired in
   `croilar/_shared/config/settings.py`)
2. **DuckDB file** — the `./data/aleyum.duckdb` default SHALL
   be renamed to `./data/croilar.duckdb`
3. **R2 bucket** — the `aleyum-data` R2 bucket default SHALL
   be renamed to `croilar-data` (plus the legacy
   `aleyum-assets` R2 bucket constant in
   `croilar/pipelines/shared/r2_client.py` SHALL be removed)
4. **DLT pipeline names** — the 4 `aleyum_local` /
   `aleyum_ducklake` / `aleyum_vectors` pipeline names SHALL
   be renamed to `croilar_local` / `croilar_ducklake` /
   `croilar_vectors`
5. **DuckLake catalog path** — the `./data/aleyum_catalog.duckdb`
   default SHALL be renamed to `./data/croilar_catalog.duckdb`

Plus: the deprecated `AleyumSettings` alias in
`croilar/_shared/config/settings.py` SHALL be removed (the
`StreamSettings` Pydantic BaseSettings is the only API).
Plus: the `ALEYUM_ENV` env var SHALL be renamed to
`CROILAR_ENV`.

#### Scenario: A pipeline name no longer references aleyum

- **WHEN** a developer greps the croilar data engineering
  layer for `aleyum` (case-insensitive)
- **THEN** no matches SHALL be found in code, env vars, or
  config defaults (only the `aleyum` persona identifier in
  `croilar/config/personas.yaml` + the persona site routes
  SHALL match)

### Requirement: Stream-registry canonical config surface

The Croílár data-engineering layer SHALL expose a canonical
config surface via the `StreamSettings` Pydantic BaseSettings
class at `croilar/_shared/config/settings.py`. The
`StreamSettings` class:

- Loads stream definitions from `croilar/config/sources.yaml`
- Exposes a typed `streams()` accessor + a `stream(id)` lookup
- Uses a `STREAMS_` env prefix (the canonical env var namespace)
- Caches the result via `@lru_cache` (the `get_settings()`
  factory)

The `Stream` Pydantic model at `croilar/_shared/streams.py`
defines the per-stream contract:

- `id: str` — the stream id (e.g. "music__spotify")
- `name: str` — the stream name (e.g. "Spotify Catalogue")
- `description: str` — a 1-line description
- `cron: str` — the cron schedule (e.g. "0 3 * * *")
- `source_module: str` — the Python module path
- `source_factory: str` — the factory function name
- `baml_function: str` — the BAML extraction function
- `dataset_name: str` — the DuckDB dataset name
- `local_only: bool` — True for sensitive corpora (CV PDFs,
  identity documents)
- `embedding_required: bool` — True for semantic-search streams

The 12 default streams SHALL be declared in
`croilar/config/sources.yaml`:

- 4 music: `music__spotify`, `music__soundcloud`,
  `music__labels`, `music__artwork`
- 3 teaching: `teaching__github`, `teaching__linkedin`,
  `teaching__researchgate`
- 3 CV: `cv__cv`, `cv__filesystem`, `cv__search_index`
- 2 research: `research__os`, `research__identity`

#### Scenario: A developer adds a new stream via the YAML

- **WHEN** a developer adds a new stream id to
  `croilar/config/sources.yaml`
- **THEN** `StreamSettings.streams()` returns the new stream
  in the list
- **AND** `StreamSettings.stream("<new-id>")` returns the
  new `Stream` instance
- **AND** the corresponding Dagster asset materializes the
  new stream on its cron schedule

