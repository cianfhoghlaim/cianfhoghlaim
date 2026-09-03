# BAML Schema Sync Loop (Layer 7)

## Purpose

The Layer 7 of the 6-layer pull-based sync architecture. Validates the 320 .baml files (558 functions + 838 classes + 288 enums + 33 LLM clients) + closes the biggest remaining gap in the sync loop.
## Requirements
### Requirement: Layer 1 — sync:baml-drift

The system SHALL provide a `bash scripts/sync/baml-drift.sh` task that detects reference + syntax drift in the 320 .baml files.

#### Scenario: BAML drift detection runs cleanly

- **WHEN** `bash scripts/sync/baml-drift.sh` is invoked
- **THEN** the task SHALL scan all `baml_src/**/*.baml` files
- **AND** the task SHALL detect:
  - References to non-existent types/functions
  - Python type annotations not matching BAML output_type
  - Duplicate function names within the same file
  - Missing `@description` on output fields
  - Client references that don't exist in `clients.baml`

### Requirement: Layer 2 — sync:baml-ccc

The system SHALL provide a `bash scripts/sync/baml-ccc.sh` task that ingests the 320 .baml files into the 22nd CCC concept guide `baml-function-search`.

#### Scenario: baml-function-search concept guide surfaces 320 .baml files

- **WHEN** `bash scripts/sync/baml-ccc.sh` is invoked
- **THEN** the task SHALL walk `baml_src/` via AST parsing
- **AND** it SHALL append the 22nd concept guide to `.cocoindex_code/guides.yml`
- **AND** the guide SHALL list the 558 functions + 838 classes + 288 enums

### Requirement: Layer 3 — sync:baml-cognee

The system SHALL provide a `bash scripts/sync/baml-cognee.sh` task that ingests the 320 .baml files into a new `baml_schemas` Cognee cluster.

#### Scenario: baml_schemas cluster grows over time

- **WHEN** `bash scripts/sync/baml-cognee.sh` is invoked
- **THEN** the task SHALL ingest the 320 .baml files
- **AND** the cluster SHALL have a per-file summary

### Requirement: Layer 4 — sync:baml-test

The system SHALL provide a `bash scripts/sync/baml-test.sh` task that runs `baml-cli test` on all 320 .baml files.

#### Scenario: baml-cli test runs cleanly

- **WHEN** `bash scripts/sync/baml-test.sh` is invoked
- **THEN** the task SHALL run `baml-cli test` on each .baml file
- **AND** the task SHALL aggregate failures to a single report

### Requirement: Layer 5 — sync:baml-lint

The system SHALL provide a `bash scripts/sync/baml-lint.sh` task that runs the BAML linter.

#### Scenario: baml-cli lint runs cleanly

- **WHEN** `bash scripts/sync/baml-lint.sh` is invoked
- **THEN** the task SHALL run `baml-cli lint` on all 320 .baml files

### Requirement: Layer 6 — sync:baml orchestrator

The system SHALL provide a `bash scripts/sync/baml.sh` task that runs all 5 layers in sequence.

#### Scenario: sync:baml orchestrator runs all 6 layers

- **WHEN** `bash scripts/sync/baml.sh` is invoked
- **THEN** the task SHALL run sync:baml-drift + sync:baml-ccc + sync:baml-cognee + sync:baml-test + sync:baml-lint in sequence
- **AND** the task SHALL write a unified report to `stedding/sync-reports/baml-{date}.md`

### Requirement: Layer 1 — `sync:baml-drift`

The system SHALL provide a `bash scripts/sync/baml-drift.sh` task that
detects reference + syntax drift in the 320 .baml files.

#### Scenario: BAML drift detection runs cleanly
- **WHEN** `bash scripts/sync/baml-drift.sh` is invoked
- **THEN** the task SHALL scan all `baml_src/**/*.baml` files
- **AND** the task SHALL detect:
  - References to non-existent types/functions
  - Python type annotations not matching BAML output_type
  - Duplicate function names within the same file
  - Missing `@description` on output fields
  - Client references that don't exist in `clients.baml`
- **AND** the task SHALL write a per-file report to
  `stedding/sync-reports/baml-drift-{date}.md`

### Requirement: Layer 2 — `sync:baml-ccc`

The system SHALL provide a `bash scripts/sync/baml-ccc.sh` task that
refreshes the CCC index + appends the **22nd concept guide**
`baml-function-search` to `.cocoindex_code/guides.yml`.

#### Scenario: 22nd concept guide surfaces BAML functions
- **WHEN** `bash scripts/sync/baml-ccc.sh` is invoked
- **THEN** the task SHALL append the `baml-function-search` guide
  to `.cocoindex_code/guides.yml`
- **AND** the task SHALL run `bun run ccc:index` for incremental refresh
- **AND** a user searching CCC for "ExtractCurriculumSyllabus" SHALL
  get the new guide in the top 3 hits

### Requirement: Layer 3 — `sync:baml-cognee`

The system SHALL provide a `bash scripts/sync/baml-cognee.sh` task that
ingests the 320 .baml files into the **11th Cognee cluster**
`baml_schemas`.

#### Scenario: Cognee has 11 typed clusters after sync
- **WHEN** `cognee-mcp` is queried for the cluster list
- **THEN** the response SHALL include all 11 typed clusters
  (10 existing + `baml_schemas`)

### Requirement: Layer 4 — `sync:baml-test`

The system SHALL provide a `bash scripts/sync/baml-test.sh` task that
runs `baml-cli test` on the 11 test blocks identified in Week 1.

#### Scenario: BAML test gate passes
- **WHEN** `bash scripts/sync/baml-test.sh` is invoked
- **THEN** the task SHALL run `baml-cli test --from baml_src`
- **AND** the task SHALL report 11 test blocks run

### Requirement: Layer 5 — `sync:baml-lint`

The system SHALL provide a `bash scripts/sync/baml-lint.sh` task that
runs the canonical BAML lint checks.

#### Scenario: BAML lint gate passes
- **WHEN** `bash scripts/sync/baml-lint.sh` is invoked
- **THEN** the task SHALL verify:
  - All functions have a `client X` reference
  - All clients route to canonical models (per `clients_biep_v3.py`)
  - No leftover `gemma-3-4b-it` / `gemma-3-27b-it` references

### Requirement: BAML evolution feedback loop

The system SHALL grow its knowledge surface over time via the
BAML evolution feedback loop.

#### Scenario: .baml file change triggers re-cognify
- **WHEN** a `.baml` file in `baml_src/` is modified
- **THEN** the next `sync:baml-cognee` SHALL detect the change
  (via file mtime comparison)
- **AND** the task SHALL re-cognify the modified file into the
  `baml_schemas` Cognee cluster
- **AND** the task SHALL update the 22nd CCC concept guide to
  include the newly-modified file

