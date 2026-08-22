# dlt-sync-loop Specification

## Purpose
The DLT sync loop surface orchestrates the 5-layer sync contract across the Cianfhoghlaim monorepo. It defines 8 invariants: Layer 1 (sync:dlt-drift) detects drift between pinned DLT sources and the registered DLT registry, Layer 2 (sync:dlt-ccc) indexes DLT source metadata into the CCC semantic index, Layer 3 (sync:dlt-cognee) ingests DLT metadata into the Cognee cluster, Layer 4 (sync:dlt-test) runs the DLT contract tests, Layer 5 (sync:dlt-lint) validates DTL files against ruff + the BAML registry, the orchestrator (sync:dlt) runs all 5 layers in topological order, the staleness detection on the CCC index, and the per-jurisdiction drift report.

## Requirements
### Requirement: Layer 1 - sync:dlt-drift

The system SHALL provide a `bash scripts/sync/dlt-drift.sh` task
that detects DLT source drift across the 928 files.

#### Scenario: DLT drift detection runs cleanly
- **WHEN** `bash scripts/sync/dlt-drift.sh` is invoked
- **THEN** the task SHALL scan all 928 files at `dlt_sources/`
- **AND** the task SHALL detect:
  - `@dlt.source(name=...)` duplicates across files
  - `@dlt.resource(name=...)` duplicates across files
  - Stale `write_disposition="replace"` (should be `merge`)
  - Stale destination references

### Requirement: Layer 2 - sync:dlt-ccc

The system SHALL provide a `bash scripts/sync/dlt-ccc.sh` task
that refreshes the CCC index + appends the **24th concept guide**
`dlt-source-search` to `.cocoindex_code/guides.yml`.

#### Scenario: 24th concept guide surfaces the DLT sources
- **WHEN** `bash scripts/sync/dlt-ccc.sh` is invoked
- **THEN** the task SHALL append the `dlt-source-search` guide
  to `.cocoindex_code/guides.yml`
- **AND** the task SHALL run `bun run ccc:index` for incremental refresh

### Requirement: Layer 3 - sync:dlt-cognee

The system SHALL provide a `bash scripts/sync/dlt-cognee.sh` task
that ingests the 928 DLT source files into the **13th Cognee
cluster** `dlt_sources`.

#### Scenario: Cognee has 13 typed clusters after sync
- **WHEN** `cognee-mcp` is queried for the cluster list
- **THEN** the response SHALL include all 13 typed clusters
  (12 existing + `dlt_sources`)

### Requirement: Layer 4 - sync:dlt-test

The system SHALL provide a `bash scripts/sync/dlt-test.sh` task
that runs `dlt pipeline ... --dry-run` on a sampling of the 13
subdirs.

#### Scenario: DLT pipeline dry-run
- **WHEN** `bash scripts/sync/dlt-test.sh` is invoked
- **THEN** the task SHALL run `dlt pipeline ... --dry-run` on a
  sampling of the 13 subdirs (1 source per subdir)
- **AND** the task SHALL report pass/fail per subdir

### Requirement: Layer 5 - sync:dlt-lint

The system SHALL provide a `bash scripts/sync/dlt-lint.sh` task
that reports per-jurisdiction stats.

#### Scenario: Per-jurisdiction stats
- **WHEN** `bash scripts/sync/dlt-lint.sh` is invoked
- **THEN** the task SHALL produce a per-jurisdiction report to
  `stedding/sync-reports/dlt-lint-{date}.md`
- **AND** the report SHALL show the per-jurisdiction file counts +
  the canonical `dlt_sources/common/` helpers used

### Requirement: DLT evolution feedback loop

The system SHALL grow its knowledge surface over time via the
DLT evolution feedback loop.

#### Scenario: DLT source change triggers re-cognify
- **WHEN** a file under `dlt_sources/` is modified
- **THEN** the next `sync:dlt-cognee` SHALL detect the change
  (via file mtime comparison)
- **AND** the task SHALL re-cognify the modified source into the
  `dlt_sources` Cognee cluster

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

