## ADDED Requirements

### Requirement: British Isles Education Source Inventory

The system SHALL keep the British Isles education source surface auditable: NCCA (Ireland), OFQUAL (England), SQA (Scotland), WJEC (Wales), CCEA (Northern Ireland), and the 3 Crown dependencies (Guernsey, Jersey, Isle of Man).

#### Scenario: All 8 jurisdictions have DLT source files

- **WHEN** any developer runs `uv run pytest tests/education_sources/`
- **THEN** the following DLT source counts are met (minimum):
  - Ireland (NCCA): ≥ 80 files
  - England (OFQUAL): ≥ 25 files
  - Scotland (SQA): ≥ 5 files
  - Wales (WJEC): ≥ 5 files
  - Northern Ireland (CCEA): ≥ 5 files
  - Guernsey, Jersey, Isle of Man: ≥ 3 files each
- **AND** the 6 Ireland LC subjects (mathematics, chemistry, geography, gaeilge, english, computer_science) each have a DLT source

#### Scenario: BIEP v3 orchestration change is present

- **WHEN** any developer runs `uv run pytest tests/education_sources/`
- **THEN** `openspec/changes/pipeline-biep-v3-orchestration/` exists with a `proposal.md` describing the British Isles education pipeline

#### Scenario: NCCA unified curriculum source exists

- **WHEN** any developer runs `uv run pytest tests/education_sources/`
- **THEN** `dlt_sources/british_isles/ireland/education/curriculum.py` exists (the unified NCCA curriculum source)
