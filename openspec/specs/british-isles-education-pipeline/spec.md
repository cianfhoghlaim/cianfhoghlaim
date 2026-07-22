# British-Isles Education Pipeline Capability

## Purpose

`british-isles-education-pipeline` (BIEP) is the flagship
ingestion+extraction+embedding+orchestration+analytics capability of the
Cianfhoghlaim platform. v1 covers the 6 priority Irish Leaving
Certificate subjects (Mathematics, Chemistry, Geography, Gaeilge,
English, Computer Science) plus the cross-cutting `gov.ie` education
circulars stream.

The corresponding source code lives at:

- `cianfhoghlaim/dlt/british_isles/` (NCCA + SEC + gov.ie DLT sources)
- `cianfhoghlaim/baml/education/lc_extraction/*.baml` (the BAML extraction schemas)
- `cianfhoghlaim/cocoindex/chemistry_embedding.py` + 5 sibling per-subject CocoIndex flows
- `cianfhoghlaim/orchestration/defs/2_materials/lc_extraction/` (Dagster lc5/lc6 assets)
- `cianfhoghlaim/notebooks/leaving_cert/` (per-subject marimo notebooks)
- `motherduck:` (`md:oideachais`) as the analytics surface (4 Dives + 1 daily Flight)

## Background

The platform has been ingesting education content from NCCA and SEC
since 2026-03 (the pre-v4 `cianfhoghlaim-pipeline`). v1 brings the
6 priority subjects to fully-runnable end-to-end pipelines and adds
`gov.ie` education circulars as the cross-cutting ingestion stream.
Cross-nation extension (Scotland / Wales / England / NI / Isle of Man
/ Crown Dependencies) is deferred to v2 and explicitly out of scope for
this spec.
## Requirements
### Requirement: 6 Irish LC subjects end-to-end

The system SHALL provide NCCA + SEC + gov.ie DLT sources, BAML
extraction (lc5 + lc6), 6 v1 CocoIndex flows (one per subject), 42+
Dagster assets (`lc5_<subject>_documents` + `lc5_<subject>_extract` +
`lc6_<subject>_marking_schemes` + ... + the 2 gov.ie circular assets),
6 per-subject marimo notebooks + 1 cross-subject competency notebook,
for the 6 priority subjects: Mathematics, Chemistry, Geography,
Gaeilge, English, Computer Science.

#### Scenario: mise run dagster:oideachais → materialize all

- **WHEN** a teacher clicks "Materialize all" in the Dagster UI for the 6-subject pipeline
- **THEN** the 42+ lc5/lc6 assets materialise within minutes
- **AND** the 6 marimo notebooks show real data via `mo.sql(engine=md:oideachais)`
- **AND** the per-subject LanceDB `cianfhoghlaim.lc.<subject>.<level>_<lang>` tables are populated

#### Scenario: gaeilge-only syllabuses (no English sibling)

- **GIVEN** Gaeilge is taught through Irish only (no `en/`-sibling per syllabus)
- **WHEN** the BAML extraction runs
- **THEN** the system SHALL extract Ga-classified records only
- **AND** not raise a missing-English error

### Requirement: gov.ie education circulars ingestion

The system SHALL ingest `gov.ie` education circulars via a DLT source at
`cianfhoghlaim/dlt/british_isles/ireland/gov_ie_circulars.py`, extract via
BAML `circular_extraction.baml`, embed via the 7th v1 CocoIndex App
`government_circulars`, and surface via a dedicated MotherDuck Dive.

#### Scenario: New circular arrives

- **WHEN** the gov.ie RSS monitor detects a new circular
- **THEN** the BAML `ClassifyCircular` function is invoked
- **AND** the extracted record lands in `md:cianfhoghlaim.education.ie.circulars`
- **AND** the `governance_circulars` CocoIndex App fires within the 60-second live-update window

### Requirement: Daily MotherDuck Flight for BAML backfill

The system SHALL schedule a daily MotherDuck Flight `lc_pdf_sync_flight`
that re-runs BAML extraction on any new PDFs landed in
`s3://garage/cianfhoghlaim/leaving_cert/<subject>/<lang>/<year>/<file>.pdf`.

#### Scenario: PDF lands in Garage S3

- **WHEN** a new PDF is written to `s3://garage/cianfhoghlaim/leaving_cert/mathematics/en/2026/Q1.pdf`
- **THEN** the daily Flight picks it up within 24h
- **AND** the corresponding lc5/lc6 rows appear in `md:cianfhoghlaim.leaving_cert.mathematics`

### Requirement: Cross-nation extension deferred to v2

The system SHALL NOT (in v1) ingest Scotland (SQA), Wales (WJEC),
England (AQA/OCR/Edexcel), Northern Ireland (CCEA), Isle of Man,
Jersey, or Guernsey curricula. These are scoped for the separate v2
change and are explicitly out of scope for this spec.

#### Scenario: v2 boundary

- **WHEN** a developer queries the v1 BIEP for Scottish curriculum data
- **THEN** the system returns an empty result with the message
  "deferred to v2; cross-nation extension is the next phase"

### Requirement: 4 MotherDuck Dives (analytics layer)

The system SHALL provide 4 live MotherDuck Dives:

1. `lc_syllabus_topics` — topic coverage per subject
2. `lc_exam_paper_difficulty` — Bloom's taxonomy distribution per year
3. `lc_marking_complexity` — mark-allocation patterns per question
4. `gov_circulars_archive` — chronological archive with topic classification

#### Scenario: BIEP Dive analytics

- **WHEN** a teacher opens the `lc_syllabus_topics` Dive
- **THEN** the chart shows topic counts grouped by subject
- **AND** the data updates within 24h of new BAML extractions

### Requirement: BIEP Subject Notebooks — ibis-first wiring to local lakehouse

The system MUST ensure the 6 BIEP subject marimo notebooks (Mathematics, Chemistry, Geography,
Gaeilge, English, Computer Science) under
`cianfhoghlaim/notebooks/04_biep_motherduck/` MUST default to the
local `bunchloch-infra` lakehouse via the `ibis.duckdb.connect()` +
`ibis.lancedb.connect()` entrypoints, with the per-subject
`ducklake_<subject>` database name. The system SHALL reject any raw
`duckdb.connect()` call in these notebooks per the ibis-first
contract from the `cianfhoghlaim-marimo-dashboards` spec.

#### Scenario: Math notebook reads from local Lakekeeper via ibis

- **GIVEN** the lakehouse stack (Garage + Lakekeeper + Lance) is up
  per the upgrade-4-stacks-with-infisical change
- **WHEN** the operator runs
  `marimo run cianfhoghlaim/notebooks/04_biep_motherduck/01_curriculum_educator.py`
- **THEN** the notebook's first data cell SHALL execute
      `conn = ibis.duckdb.connect("ducklake:postgres:...")`
- **AND** it SHALL resolve
      `lance = ibis.lancedb.connect("rest://lakehouse-lance-namespace:8182")`
- **AND** every data query SHALL be expressed as an ibis expression
  rather than raw SQL strings
- **AND** the operation SHALL complete within 10 seconds against the
  empty Lakekeeper (returns 0-row DataFrames, not errors)

#### Scenario: ibis is the canonical entrypoint, not raw duckdb

- **WHEN** the 6 BIEP notebooks are grepped
- **THEN** every `import duckdb` is replaced by `import ibis`
- **AND** every `duckdb.connect(uri)` call is replaced by
  `ibis.duckdb.connect(uri)`
- **AND** the `ibis` skill is referenced in the per-notebook
  `## KCG patterns used` docstring

### Requirement: BIEP BAML surface drift fix (5 categories)

The system SHALL compile the full BIEP BAML surface without errors. The
following 5 drift categories SHALL be eliminated:

1. **Default-value class fields** SHALL NOT exist in `baml_src/`. Class
   field declarations SHALL NOT carry `= "<value>"` syntax. Optional
   fields SHALL use the `field type?` syntax instead.
2. **Unterminated strings** SHALL NOT exist in any `@description`,
   `prompt`, or `args { ... }` block.
3. **Test block keyword** SHALL be PascalCase `Test` (not `test`). BAML
   0.222+ requires PascalCase.
4. **Function block `client` field** SHALL be present on every `function`
   block. The `client <Name>` line SHALL appear before `prompt #"..."`.
5. **String-literal type references** SHALL NOT exist in class field
   type annotations. Use bare class references (resolved by the BAML
   type system) instead.

#### Scenario: baml-cli generate succeeds

- **WHEN** the user runs `mise run baml:generate` (or `cic:baml:generate`)
- **THEN** BAML SHALL generate the Python client into `baml_client/` without error
- **AND THEN** exit 0

#### Scenario: baml-cli test passes

- **WHEN** the user runs `mise run baml:test` (or `cic:baml:test`)
- **THEN** all `Test PascalCaseDescription { ... }` blocks SHALL execute
- **AND THEN** all assertions SHALL pass
- **AND THEN** exit 0

#### Scenario: BIEP client declarations

- **WHEN** the BIEP v3 hardening change (`2026-08-07-biep-v3-hardening-v1`) ships
- **THEN** the BIEP canonical 3 clients (`BIEPV3Extract`,
      `BIEPV3ExtractStrong`, `BIEPV3Vision`) SHALL each declare a distinct
      model: `gemma-3-4b-it`, `qwen3-vl-8b-it`,
      `qwen3-vl-8b-it-via-llama-swap` respectively
- **AND THEN** the legacy `ExtractEn` / `ExtractEnStrong` aliases MAY collapse to
      a single model (per the BIEP v3 consolidation rationale)

#### Scenario: No `baml_src` field references latent missing types

- **WHEN** any `.baml` file references a class (e.g., `GradeDescriptor`)
- **THEN** that class SHALL be either declared in the same file or
      imported from `_shared/` (no string-literal type references)

