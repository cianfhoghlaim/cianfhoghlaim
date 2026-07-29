# Retrospective cleanup + extended sync loop

> **The retroactive cleanup of the 1959 pre-v7 path drift occurrences that `sync:paths` surfaced + the extension of the existing sync loop with `sync:dagster` (Layer 6 — the biggest remaining gap in the sync architecture).**

## ADDED Requirements

### Requirement: Retroactive cleanup of pre-v7 path drift

The system SHALL provide a `mise run sync:paths --fix` task that
applies the 3 safe rename patterns to the 47 auto-fixable
occurrences surfaced by `sync:paths`:
- `sruth/cianfhoghlaim/` → `.` (or specific canonical replacement; 19 occurrences)
- `infrastructure/stacks/` → `bonneagar/stacks/` (27 occurrences)
- `infrastructure/komodo/` → `bonneagar/komodo/` (1 occurrence)

#### Scenario: sync:paths --fix reports 0 auto-fixable occurrences
- **WHEN** `mise run sync:paths --fix` is invoked
- **THEN** the task SHALL apply the 3 safe rename patterns to the
  auto-fixable occurrences
- **AND** the task SHALL validate via `ast.parse` per file post-rename
- **AND** the task SHALL skip files that contain the
  `was sruth/...pre-v7` annotation (intentionally historical)
- **AND** the task SHALL re-run `sync:paths` to verify the count
  drops to the expected baseline
- **AND** the task SHALL write a `fix-applied` report to
  `stedding/sync-reports/paths-fix-{date}.md`

#### Scenario: sync:paths produces per-directory diagnostic reports
- **WHEN** `sync:paths` reports 1912 manual occurrences
  (the .md docs + the BAML files in `baml_src/european_nations/`)
- **THEN** the task SHALL produce per-directory reports at
  `stedding/sync-reports/retroactive-cleanup/2026-08-15/dlt/` +
  `baml/`
- **AND** each per-directory report SHALL list the specific files +
  lines + the canonical replacement

### Requirement: Layer 6 — sync:dagster

The system SHALL provide a `mise run sync:dagster` task that
validates the ~833 Dagster assets in the 5-layer `defs/` tree.

#### Scenario: sync:dagster produces a per-group report
- **WHEN** `mise run sync:dagster` is invoked
- **THEN** the task SHALL walk the 5-layer `defs/` tree
  (`1_ingestion/`, `2_materials/`, `3_model_lifecycle/`,
  `4_asset_generation/`, `5_agent_ops/`)
- **AND** the task SHALL parse each `.py` file with `ast`
- **AND** the task SHALL validate:
  - All `@asset` decorators have working imports
  - All sensors reference existing jobs
  - All asset checks reference existing assets
  - Group names match the 5-layer convention
  - No orphaned definitions
- **AND** the task SHALL write a per-group report to
  `stedding/sync-reports/dagster-{date}.md`

#### Scenario: Cognee has 11 typed clusters after sync
- **WHEN** `cognee-mcp` is queried for the cluster list
- **THEN** the response SHALL include all 11 typed clusters
  (7 existing + 4 new: `openspec_changes`, `openspec_specs`,
  `agent_skills`, `dagster_assets`)

### Requirement: Safe auto-fix mode

The system SHALL provide a `--fix` flag on `sync:paths` that
auto-fixes ONLY the safe rename patterns.

#### Scenario: Auto-fix applies only to safe patterns
- **WHEN** `sync:paths --fix` is invoked
- **THEN** the task SHALL apply the 3 safe rename patterns only
  (`sruth/cianfhoghlaim/`, `infrastructure/stacks/`,
  `infrastructure/komodo/`)
- **AND** the task SHALL NOT apply unsafe patterns
  (`cianfhoghlaim/dlt/`, `cianfhoghlaim/baml/`) — those require
  manual review
- **AND** the task SHALL validate the rename doesn't break any
  imports (via `ast.parse` after the rename)

### Requirement: dagster_sync_health Dagster asset

The system SHALL provide a Dagster asset `dagster_sync_health` that
emits metadata about the Dagster asset health.

#### Scenario: dagster_sync_health materializes on cron
- **GIVEN** the `0 */4 * * *` cron fires (every 4 hours)
- **WHEN** the `dagster_sync_health` asset materializes
- **THEN** it SHALL emit the following Dagster metadata:
  `asset_count` (~833), `sensor_count` (11), `group_count` (5),
  `broken_asset_count` (0)
- **AND** it SHALL trigger a downstream Dagster job
  `dagster_sync_alert` if `broken_asset_count > 0`

## Cross-references

- `openspec/changes/2026-08-15-knowledge-sync-loop-v1/` (the foundation)
- `openspec/specs/knowledge-sync-loop/spec.md` (the parent sync loop spec)
- `scripts/sync/` (the 6 sync scripts)
- `.agents/skills/knowledge-sync-loop/SKILL.md` (the doc for the sync loop pattern)
- `openspec/changes/2026-08-15-centralized-model-schema-registry-and-deployment-control-panel-v1/` (the model-registry change that consumes the deployment control panel)
- `stedding/sync-reports/retroactive-cleanup/2026-08-15/` (the per-directory diagnostic reports)