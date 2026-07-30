# dlt-sync-loop Specification

## Purpose
TBD - created by archiving change 2026-08-15-dlt-sync-loop-v1. Update Purpose after archive.
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

