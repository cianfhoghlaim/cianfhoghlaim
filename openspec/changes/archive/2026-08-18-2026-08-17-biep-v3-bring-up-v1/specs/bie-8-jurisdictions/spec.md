# bie-8-jurisdictions

## ADDED Requirements

### Requirement: England DLT sources for 3 GCSE + 3 A-Level boards

The system SHALL host 6 DLT sources for the England BIEP v3 pipeline:

1. `dlt_sources/british_isles/england/education/gcse/aqa_source.py`
2. `dlt_sources/british_isles/england/education/gcse/ocr_source.py`
3. `dlt_sources/british_isles/england/education/gcse/edexcel_source.py`
4. `dlt_sources/british_isles/england/education/a_level/aqa_source.py`
5. `dlt_sources/british_isles/england/education/a_level/ocr_source.py`
6. `dlt_sources/british_isles/england/education/a_level/edexcel_source.py`

Each source SHALL be exported from
`dlt_sources/british_isles/england/education/__init__.py` and SHALL
emit to the canonical BIEP DuckLake namespace
`cianfhoghlaim.education.british_isles.england.{stage}.{board}.{subject}`.

Per the `2026-08-10-england-biiep-pipeline-v1` change proposal.

#### Scenario: AQA GCSE source emits to DuckLake

- **GIVEN** the AQA GCSE source is registered via `@dlt.source(name="england_gcse_aqa")`
- **WHEN** `dagster asset materialize --select england_gcse_aqa_assets` runs
- **THEN** the source reads `stedding/site_scrape_samples/england/gcse/{subject}/`
- **AND** writes to `md:cianfhoghlaim.education.british_isles.england.gcse.aqa.{subject}`
- **AND** the asset check `row_count` passes with `row_count > 0`

#### Scenario: 6 sources are wired into Dagster

- **WHEN** `dagster job list | grep england` runs
- **THEN** the 6 jobs (one per board × stage) appear in the list
- **AND** `dagster asset materialize --select england_*` materializes all 6

### Requirement: England Dagster asset groups (6)

The system SHALL host 6 Dagster asset groups wrapping the 6 England
DLT sources + BAML extraction + CocoIndex embedding + MotherDuck load:

1. `orchestration/defs/2_materials/england_education/gcse/aqa_assets.py`
2. `orchestration/defs/2_materials/england_education/gcse/ocr_assets.py`
3. `orchestration/defs/2_materials/england_education/gcse/edexcel_assets.py`
4. `orchestration/defs/2_materials/england_education/a_level/aqa_assets.py`
5. `orchestration/defs/2_materials/england_education/a_level/ocr_assets.py`
6. `orchestration/defs/2_materials/england_education/a_level/edexcel_assets.py`

Each asset group SHALL wire:
- The DLT source (per Requirement 1 above)
- The BAML extraction function (`Extract<Board>QualSpec`)
- The CocoIndex v1 App (`england_<board>_<stage>_embedding`)
- The MotherDuck landing (per Requirement 1 above namespace)

#### Scenario: All 6 asset groups register with Dagster

- **WHEN** `dg list defs --location england_education` runs
- **THEN** all 6 asset groups are registered
- **AND** each group has 4 assets (source + BAML + CocoIndex + MotherDuck load)

### Requirement: England cross-board coverage check

The system SHALL host
`orchestration/defs/2_materials/england_education/misconfig_check.py`
that verifies the 3 boards (AQA / OCR / Edexcel) cover the same
~92 subjects (43 GCSE + 49 A-Level) — no board is missing any
subject.

#### Scenario: AQA is missing 2 subjects

- **GIVEN** the AQA GCSE source has 41 of the 43 expected subjects
  (missing `computer-science-aqa` and `drama-aqa`)
- **WHEN** `dagster asset check --select england_misconfig_check` runs
- **THEN** the check fails with `AQA GCSE missing 2 subjects: computer-science-aqa, drama-aqa`
- **AND** the check identifies which subjects are missing from which board

#### Scenario: All 3 boards cover all 92 subjects

- **WHEN** all 6 sources have the full subject coverage
- **THEN** the misconfig check exits 0
- **AND** `dagster asset check --select england_misconfig_check` returns passed