# Stacks Sync Loop (Layer 8)

> **The Layer 8 of the 8-layer pull-based sync architecture. Validates the 87 Docker Compose stacks at `bonneagar/stacks/` + the 6-file GOLD_STANDARD pattern + the stack-doctor audit.**

## ADDED Requirements

### Requirement: Layer 1 — `sync:stacks-drift`

The system SHALL provide a `bash scripts/sync/stacks-drift.sh` task
that detects GOLD_STANDARD violations + name collisions in the
87 stacks at `bonneagar/stacks/`.

#### Scenario: Stacks drift detection runs cleanly
- **WHEN** `bash scripts/sync/stacks-drift.sh` is invoked
- **THEN** the task SHALL scan all 87 stacks at `bonneagar/stacks/`
- **AND** the task SHALL detect:
  - Stacks missing any of the 6 GOLD_STANDARD files
    (compose.yaml + sidecar.yaml + secrets.env + pangolin.yaml +
    blueprint.yaml + .env.example)
  - Name collisions (e.g. `meaisínfhoghlaim` with fada vs
    `meaisinfhoghlaim` without)
  - Legacy `oideachais/` references
- **AND** the task SHALL write a per-stack report to
  `stedding/sync-reports/stacks-drift-{date}.md`

### Requirement: Layer 2 — `sync:stacks-ccc`

The system SHALL provide a `bash scripts/sync/stacks-ccc.sh` task
that refreshes the CCC index + appends the **23rd concept guide**
`stack-catalog-search` to `.cocoindex_code/guides.yml`.

#### Scenario: 23rd concept guide surfaces the stack catalog
- **WHEN** `bash scripts/sync/stacks-ccc.sh` is invoked
- **THEN** the task SHALL append the `stack-catalog-search` guide
  to `.cocoindex_code/guides.yml`
- **AND** the task SHALL run `bun run ccc:index` for incremental refresh

### Requirement: Layer 3 — `sync:stacks-cognee`

The system SHALL provide a `bash scripts/sync/stacks-cognee.sh`
task that ingests the 87 stack catalog entries into the **12th
Cognee cluster** `stacks_catalog`.

#### Scenario: Cognee has 12 typed clusters after sync
- **WHEN** `cognee-mcp` is queried for the cluster list
- **THEN** the response SHALL include all 12 typed clusters
  (11 existing + `stacks_catalog`)

### Requirement: Layer 4 — `sync:stacks-validate`

The system SHALL provide a `bash scripts/sync/stacks-validate.sh`
task that runs `bash scripts/stack-doctor.sh` + parses the output.

#### Scenario: stack-doctor audit runs
- **WHEN** `bash scripts/sync/stacks-validate.sh` is invoked
- **THEN** the task SHALL run `bash scripts/stack-doctor.sh`
- **AND** the task SHALL parse the output to extract:
  - The total CRITICAL count
  - The 4 known GOLD_STANDARD violators
  - The 89 stacks count

### Requirement: Layer 5 — `sync:stacks-health`

The system SHALL provide a `bash scripts/sync/stacks-health.sh`
task that reports per-stack health (GOLD_STANDARD status + drift
count + Cognee cluster populated + CCC indexed).

#### Scenario: Per-stack health report
- **WHEN** `bash scripts/sync/stacks-health.sh` is invoked
- **THEN** the task SHALL produce a per-stack report to
  `stedding/sync-reports/stacks-health-{date}.md`
- **AND** the report SHALL show the per-stack GOLD_STANDARD status
  + the drift count + the Cognee cluster status

### Requirement: Stacks evolution feedback loop

The system SHALL grow its knowledge surface over time via the
stacks evolution feedback loop.

#### Scenario: stack file change triggers re-cognify
- **WHEN** a file under `bonneagar/stacks/<stack>/` is modified
- **THEN** the next `sync:stacks-cognee` SHALL detect the change
  (via file mtime comparison)
- **AND** the task SHALL re-cognify the modified stack into the
  `stacks_catalog` Cognee cluster
- **AND** the task SHALL update the 23rd CCC concept guide

## Cross-references

- `openspec/changes/2026-08-15-knowledge-sync-loop-v1/` (the foundation)
- `openspec/changes/2026-08-15-retroactive-pre-v7-cleanup-v1/` (Layer 6)
- `openspec/changes/2026-08-15-baml-sync-loop-v1/` (Layer 7)
- `bonneagar/stacks/` (the 87 stacks)
- `scripts/stack-doctor.sh` (the canonical stack audit)
- `scripts/sync/` (the existing 8 sync scripts)