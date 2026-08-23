# cianfhoghlaim-uog-official-docs Specification

## Purpose

`cianfhoghlaim-uog-official-docs` is the **Stage-0-audited** public
extension of the existing `cianfhoghlaim-university-deep-extraction`
pipeline (which scrapes the UoG public catalogue) and the
authenticated `cianfhoghlaim-uog-exam-papers` pipeline (which
scrapes the locked exam index).

Stage 0 = Firecrawl `/agent` deep-analysis of the homepages the
user has called out (e.g. `https://www.universityofgalway.ie/course-information/module/`,
`https://www.universityofgalway.ie/colleges-and-schools/`) to
discover the URL paths the deep-extraction + official-doc
scrapers should then crawl.

`oide.py` is the closest analogue — NCCA-equivalent authoritative
body that publishes official supporting-document sets. The UoG
Students' Union mirrors that pattern at the student-affairs level.
NUI is the umbrella at the federation level.

## Requirements

### Requirement: Stage-0 audit via Firecrawl `/agent`

The system SHALL provide a `uog_official_docs_stage0_audit` Dagster
asset that runs `BackendRouter.pre_research(base_url, goal,
budget_hint=2)` against the UoG homepages the user has called out.

The discovered URL paths SHALL be persisted to a
`university_research_sitemap` LanceDB table so the downstream
Stage-1 collector can re-read them.

#### Scenario: Two homepages, two discovered path lists

- **GIVEN** the audit runs with
  `base_url="https://www.universityofgalway.ie/course-information/module/"`
  AND `goal="discover the URL paths for every UoG module descriptor"`
- **WHEN** the asset materialises
- **THEN** the audit SHALL emit a `url_discovery_log` row per
  page crawled
- **AND** the persisted `university_research_sitemap` LanceDB
  table SHALL contain ≥ 12 unique module URL paths
- **AND** each path SHALL match the regex
  `^https://www\.universityofgalway\.ie/.+/.+/[A-Z]{2,4}\d{3,4}(/.*)?$`

### Requirement: 5-resources DLT source for UoG official docs

The system SHALL provide
`uog_official_docs_source()` at
`dlt_sources/british_isles/ireland/education/university/official_docs/uog_official_docs_source.py`
yielding 5 `@dlt.resource` resources: `official_documents`,
`key_pages`, `url_discovery_log`, `academic_register`, `exam_board_minutes`.

Each resource SHALL use `write_disposition="merge"` and a
multi-column `primary_key` that includes `content_hash` so
re-runs are idempotent.

#### Scenario: An academic register PDF is ingested idempotently

- **GIVEN** the Stage-0 audit discovered the canonical
  `academic-register-2025-26.pdf` URL
- **WHEN** `uog_official_docs_source(schools=["academic-register"])`
  is materialised twice
- **THEN** exactly the same rows are merged
- **AND** `load_info.load_packages[0].jobs[0].file_path[-12:] ==
  last_run_hash`

### Requirement: NUI federation superset source

The system SHALL provide `nui_federation_source()` at
`dlt_sources/british_isles/ireland/education/university/official_docs/nui_federation_source.py`
yielding 3 resources: `nui_members`, `nui_constituent_circulars`,
`nui_archive`. The `nui_members` resource SHALL list the current
constituents (UCD, UCC, MU, UoG) and the historical-archive links
back to pre-1908 QUB inclusion.

#### Scenario: NUI federation lists all 4 current members + archive

- **GIVEN** `nui_federation_source()` runs
- **THEN** `nui_members` SHALL yield 4 rows (one per current constituent)
- **AND** `nui_archive` SHALL yield ≥ 1 row referencing the
  pre-1908 QUB historical record
- **AND** every row SHALL have `source_url` matching
  `^https://(www\.)?nui\.ie/`

### Requirement: UoG Students' Union authoritative-doc source

The system SHALL provide `uog_students_union_source()` yielding 2
resources: `students_union_documents`, `class_rep_handbooks`.
The scraper routes through the canonical `BackendRouter` Stage-0
audit (no SSO required — SU pages are public).

#### Scenario: SU Policy PDFs are downloaded with no auth

- **GIVEN** the scraper runs without any `UNIVERSITY_SSO_*` env vars
- **WHEN** the asset materialises
- **THEN** every SU policy PDF URL SHALL be fetched via the
  Firecrawl `/agent` discover → `bulk_scrape` flow
- **AND** the `status="skipped_fixture"` rows are emitted in CI

### Requirement: Per-institution one-liner CLI

The system SHALL provide `scripts/uog_official_docs_stage0.py`
that wraps the audit in a single command:
`uv run scripts/uog_official_docs_stage0.py --university
universityofgalway`. This is the one-liner a thesis reviewer uses
without Dagster.

#### Scenario: Reviewer runs the one-liner with no Dagster

- **GIVEN** a clean machine with `uv` + the `cianfhoghlaim` repo
- **AND** no Dagster running
- **WHEN** the reviewer executes
  `uv run scripts/uog_official_docs_stage0.py --university universityofgalway`
- **THEN** the script SHALL bootstrap a venv, run the audit, and
  print the discovered paths to stdout
- **AND** it SHALL NOT require Dagster or any other service

### Requirement: DuckLake destination wiring

The system SHALL accept `destination: Literal["local",
"motherduck","bonneagar"]` on every `*_source()` call. The
default is `"local"` (the existing local DuckDB convention).

When `destination="motherduck"`, the system SHALL pull the
`MOTHERDUCK_TOKEN` secret through `SecretsResolver` and `ATTACH`
the MotherDuck Postgres endpoint before any DLT resource yields.

When `destination="bonneagar"`, the system SHALL pull the
`BONNEAGAR_LAKEHOUSE_URI` secret and `ATTACH` via the canonical
DuckLake `postgres:host=lakehouse-postgres …` URI.

#### Scenario: Local destination writes to local DuckDB

- **GIVEN** `destination="local"` (the default)
- **WHEN** the source runs
- **THEN** the DuckDB file at `/tmp/cianfhoghlaim.duckdb` SHALL
  receive every row
- **AND** no HTTP call to MotherDuck or Bonneagar SHALL be made

#### Scenario: `BonneagarLakehouseDestination.ATTACH()` succeeds

- **GIVEN** `destination="bonneagar"` AND
  `INFISICAL_TOKEN=…` resolved via the SecretsResolver
- **WHEN** the source runs
- **THEN** `duckdb.connect(":memory:").execute("ATTACH ? AS
  bonneagar", uri)` succeeds
- **AND** every row is written to `bonneaker.cianfhoghlaim.uog_official_documents`
