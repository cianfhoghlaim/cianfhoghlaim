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
- **THEN** the compiler SHALL still emit TypeScript + Python client code from `sruth/croilar/baml/{artwork_analysis, cv_extraction, identity_verification, linkedin_profile_extraction, researchgate_extraction, style_transfer, teaching_extraction, generators, clients}.baml`

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

The system SHALL ship `sruth/croilar/scripts/analyze-web-stack.ts` as a Bun script that walks the monorepo and posts aggregates to Convex.

#### Scenario: Walk succeeds for the 3 present projects

- **WHEN** `bun run sruth/croilar/scripts/analyze-web-stack.ts` is executed from the repo root
- **THEN** the analyzer SHALL walk `sruth/tuatha/`, `sruth/oideachais/`, `sruth/croilar/`
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
identifier in `sruth/croilar/config/personas.yaml` + the persona
site routes, which are 1-persona identifiers, not 5-alias
registry entries). The 5 collapsed aliases are:

1. **Env prefix** — `ALEYUM_*` env vars SHALL be renamed to
   `STREAMS_*` (already partially retired in
   `sruth/croilar/_shared/config/settings.py`)
2. **DuckDB file** — the `./data/aleyum.duckdb` default SHALL
   be renamed to `./data/croilar.duckdb`
3. **R2 bucket** — the `aleyum-data` R2 bucket default SHALL
   be renamed to `croilar-data` (plus the legacy
   `aleyum-assets` R2 bucket constant in
   `sruth/croilar/pipelines/shared/r2_client.py` SHALL be removed)
4. **DLT pipeline names** — the 4 `aleyum_local` /
   `aleyum_ducklake` / `aleyum_vectors` pipeline names SHALL
   be renamed to `croilar_local` / `croilar_ducklake` /
   `croilar_vectors`
5. **DuckLake catalog path** — the `./data/aleyum_catalog.duckdb`
   default SHALL be renamed to `./data/croilar_catalog.duckdb`

Plus: the deprecated `AleyumSettings` alias in
`sruth/croilar/_shared/config/settings.py` SHALL be removed (the
`StreamSettings` Pydantic BaseSettings is the only API).
Plus: the `ALEYUM_ENV` env var SHALL be renamed to
`CROILAR_ENV`.

#### Scenario: A pipeline name no longer references aleyum

- **WHEN** a developer greps the croilar data engineering
  layer for `aleyum` (case-insensitive)
- **THEN** no matches SHALL be found in code, env vars, or
  config defaults (only the `aleyum` persona identifier in
  `sruth/croilar/config/personas.yaml` + the persona site routes
  SHALL match)

### Requirement: Stream-registry canonical config surface

The Croílár data-engineering layer SHALL expose a canonical
config surface via the `StreamSettings` Pydantic BaseSettings
class at `sruth/croilar/_shared/config/settings.py`. The
`StreamSettings` class:

- Loads stream definitions from `sruth/croilar/config/sources.yaml`
- Exposes a typed `streams()` accessor + a `stream(id)` lookup
- Uses a `STREAMS_` env prefix (the canonical env var namespace)
- Caches the result via `@lru_cache` (the `get_settings()`
  factory)

The `Stream` Pydantic model at `sruth/croilar/_shared/streams.py`
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
`sruth/croilar/config/sources.yaml`:

- 4 music: `music__spotify`, `music__soundcloud`,
  `music__labels`, `music__artwork`
- 3 teaching: `teaching__github`, `teaching__linkedin`,
  `teaching__researchgate`
- 3 CV: `cv__cv`, `cv__filesystem`, `cv__search_index`
- 2 research: `research__os`, `research__identity`

#### Scenario: A developer adds a new stream via the YAML

- **WHEN** a developer adds a new stream id to
  `sruth/croilar/config/sources.yaml`
- **THEN** `StreamSettings.streams()` returns the new stream
  in the list
- **AND** `StreamSettings.stream("<new-id>")` returns the
  new `Stream` instance
- **AND** the corresponding Dagster asset materializes the
  new stream on its cron schedule

### Requirement: No local fallback in `sruth/croilar/dlt_utils/destinations.py`

The system SHALL NOT include a local pre-Phase-2.3 fallback
implementation in `sruth/croilar/dlt_utils/destinations.py`.
The file SHALL be a thin re-export shim from the canonical
`sruth.oideachais.dlt_utils.destinations` module via the
`with_namespace("croilar")` factory.

The local fallback was originally needed because the croilar
packaging fix (commit `e9e0fc7d2`) had not yet been applied,
so `import sruth.oideachais.dlt_utils.destinations` would
fail from inside the croilar venv. The packaging fix
introduced `croilar/__init__.py` + changed pyproject
`packages = ["."]` + post-install `croilar/scripts/fix-pth.sh`
that rewrites the broken uv-generated `.pth` to put `sruth/`
on `sys.path` (so both `import croilar` and
`import sruth.oideachais` work).

After the packaging fix, the canonical import always succeeds,
so the local fallback is dead code (~88 lines of duplication).
It also creates a maintenance burden: 2 places to update when
the destination API changes.

#### Scenario: Canonical import is the only code path

- **GIVEN** the croilar packaging fix is in place (commit `e9e0fc7d2`)
- **AND** `sruth/croilar/scripts/fix-pth.sh` has been run
- **WHEN** a developer imports
  `from sruth.croilar.dlt_utils.destinations import NAMESPACE`
- **THEN** the import succeeds
- **AND** `NAMESPACE == "croilar"`
- **AND** the value comes from the canonical
  `sruth.oideachais.dlt_utils.destinations.with_namespace("croilar")`
  factory (not from a local fallback)

#### Scenario: The 4 canonical exports are all available

- **GIVEN** the thin shim is in place
- **WHEN** a developer imports the 4 canonical names
  ```python
  from sruth.croilar.dlt_utils.destinations import (
      NAMESPACE,
      create_pipeline,
      get_dlt_destination,
      get_duckdb_fallback_destination,
  )
  ```
- **THEN** all 4 imports succeed

#### Scenario: The 3 fallback-only exports are NOT available

- **GIVEN** the thin shim is in place
- **WHEN** a developer tries to import the 3 names that
  the local fallback used to export (`DuckLakeConfig`,
  `_get_local_config`, `get_duckdb_fallback`)
- **THEN** `ImportError` is raised
- **AND** the 3 names are not in `dir(sruth.croilar.dlt_utils.destinations)`

#### Scenario: `sruth/croilar/dlt_utils/__init__.py` re-exports the canonical surface

- **GIVEN** the thin shim is in place
- **AND** `sruth/croilar/dlt_utils/__init__.py` has been updated
  to import from `.destinations`
- **WHEN** a developer imports the public surface
  ```python
  from dlt_utils import (
      NAMESPACE,
      create_pipeline,
      get_dlt_destination,
      get_duckdb_fallback_destination,
  )
  ```
- **THEN** all 4 imports succeed

### Requirement: No drift in `pipelines/shared/`

The system SHALL NOT include `sruth/croilar/pipelines/shared/destinations.py`
(the 4-function destination factory that duplicates the canonical surface at
`sruth/oideachais/dlt_utils/destinations.py`).
The system SHALL NOT include `sruth/croilar/pipelines/shared/ducklake.py`
(the 352-line `DuckLakeCatalog` class that has no production callers).
The croilar data-engineering layer MUST consume the canonical destination
factory surface at `sruth/oideachais/dlt_utils/destinations.py` (the
`with_namespace("croilar")` shim introduced in round 11 phase 1 of croilar)
rather than re-implementing its own destination factory or its own
`DuckLakeCatalog`.

#### Scenario: Only `r2_client.py` + `__init__.py` remain in `pipelines/shared/`

- **WHEN** `ls sruth/croilar/pipelines/shared/` is run
- **THEN** the directory SHALL contain only `__init__.py` (1-line `R2Client` re-export) + `r2_client.py` (187 lines)
- **AND** the directory SHALL NOT contain `destinations.py` or `ducklake.py`

#### Scenario: Production callers of the canonical surface still work

- **WHEN** `pipelines/teaching/__init__.py:47` runs `from dlt_utils import get_dlt_destination`
- **THEN** the canonical `get_dlt_destination()` function SHALL be importable from `sruth/croilar.dlt_utils.destinations`
- **AND** the production `pipelines.teaching` module SHALL remain importable

#### Scenario: Production caller of `R2Client` still works

- **WHEN** `pipelines/soundcloud/downloader.py:18` runs `from pipelines.shared.r2_client import R2Client`
- **THEN** `R2Client` SHALL remain importable from `sruth.croilar.pipelines.shared.r2_client`
- **AND** the production `pipelines.soundcloud.downloader` module SHALL remain importable

#### Scenario: No fallback shims

- **WHEN** the round 11 change is committed
- **THEN** there SHALL be no `try/except ImportError` fallback, no `__getattr__` lazy import, no deprecation warning
- **AND** the deleted modules SHALL be removed outright (no `destinations.py.bak`, no `destinations.py.deprecated`)

#### Scenario: `tests/test_smoke.py::test_pipelines_shared_exports` updated

- **WHEN** `pytest sruth/croilar/tests/test_smoke.py::test_pipelines_shared_exports` runs
- **THEN** the test SHALL assert only `R2Client` is present on `pipelines.shared`
- **AND** the test SHALL NOT assert `create_duckdb_destination` or `create_ducklake_destination` (those names moved to the canonical `dlt_utils` surface in round 11 phase 1 of croilar)

