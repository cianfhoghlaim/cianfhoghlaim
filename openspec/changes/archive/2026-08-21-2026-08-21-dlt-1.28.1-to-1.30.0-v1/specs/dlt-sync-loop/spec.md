## ADDED Requirements

### Requirement: DLT pin (>=1.30.0) — Priority 1 bump per the 2026-08-21 audit

The system SHALL pin `dlt[duckdb,motherduck,filesystem]>=1.30.0,<2.0.0` per the 2026-08-21 upstream-version alignment audit. The 1.30.0 bump supersedes 1.28.1 (which was the floor before this change) and includes:

- **1.25+** — `pipeline.dataset()` now returns all schemas by default. The 10 jurisdiction pipelines MUST continue using the explicit `dataset_name=` kwarg in `JurisdictionPipelineBase.build_pipeline(...)`.
- **1.27** — `dlt[hub]` plugin split (impacts dlthub CLI users; not relevant for our pipeline).
- **1.28** — `refresh` write_disposition supersedes `replace` (per audit).
- **1.30.0** — latest stable as of 2026-08.

#### Scenario: BIEP v3 Ireland LC pipeline loads the 80 /leaving_certificate/ PDFs

- **GIVEN** the platform is on DLT 1.30 + the canonical 80 PDFs at `/leaving_certificate/{subject}/{en|ga}/`
- **WHEN** `uv run python -c "import dlt; ..." + lc5_documents` runs
- **THEN** the pipeline completes in <120s with **80 rows** in `lc5_documents` table
- **AND** per-subject counts match: chemistry 16, compsci 11, english 8, gaeilge 11, geography 18, mathematics 16

#### Scenario: A new jurisdiction pipeline uses dlt 1.30 with explicit schema

- **WHEN** `JurisdictionPipelineBase.build_pipeline(name='england_aqa_a_level', dataset_name='england_aqa_a_level')` is called
- **THEN** the pipeline writes to the `england_aqa_a_level` schema only (NOT all schemas)
- **AND** the audit `sync:dlt-drift` reports 0 schema-leak findings

#### Scenario: Stale `write_disposition="replace"` is caught

- **WHEN** the operator runs `bash scripts/sync/dlt-drift.sh`
- **THEN** any DLT resource with `write_disposition="replace"` is flagged for migration to `merge` (incremental) or `refresh` (full-table refresh)
- **AND** the script prints the line + file + suggests the replacement

### Requirement: DLT BIEP Ireland LC pipeline perf — MUST complete in <30s

The system MUST complete the BIEP Ireland LC pipeline (against the 80 /leaving_certificate/ PDFs) in under 30 seconds wall-clock when running on DLT >=1.30. This is the perf gate per the 2026-08-21 audit:

- DLT 1.28.x → 80 PDFs processed in 76s (baseline)
- DLT 1.30.0 → 80 PDFs processed in 20.7s (~3.7x faster)

#### Scenario: BIEP Ireland LC pipeline timing

- **WHEN** the operator runs `uv run python -c "..."` against the 80 PDFs
- **THEN** total wall-clock MUST be <30s (vs the 76s baseline on 1.28.x)
- **AND** the loaded row count MUST remain exactly 80 (no semantic drift)
