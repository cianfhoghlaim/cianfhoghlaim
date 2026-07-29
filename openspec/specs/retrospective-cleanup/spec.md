# Retrospective cleanup + extended sync loop

## Purpose

The retroactive cleanup of the 1959 pre-v7 path drift occurrences that `sync:paths` surfaced + the extension of the existing sync loop with `sync:dagster` (Layer 6 — the biggest remaining gap in the sync architecture).
## Requirements
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
- **AND** the task SHALL write the fix-applied report to
  `stedding/sync-reports/paths-fix-{date}.md`

### Requirement: Per-directory diagnostic reports

The system SHALL produce per-directory diagnostic reports for the
1912 manual occurrences (the .md docs are historical; the .py code
references are real). Each report SHALL list the file paths + line
numbers + the surrounding 3 lines of context.

#### Scenario: per-directory report identifies manual occurrences

- **WHEN** `sync:paths --fix` is invoked the first time
- **THEN** the task SHALL generate per-directory reports at
  `stedding/sync-reports/retroactive-cleanup/{date}/{subdir}.md`
- **AND** each report SHALL list the 1912 manual occurrences with
  file path, line number, and the matching pattern

### Requirement: sync:dagster (Layer 6)

The system SHALL provide a `mise run sync:dagster` task that walks
the 5-layer `orchestration/defs/` tree + validates ~833 Dagster
assets via AST parsing + produces a per-group report to
`stedding/sync-reports/dagster-{date}.md`.

#### Scenario: sync:dagster emits per-group breakdown

- **WHEN** `mise run sync:dagster` is invoked
- **THEN** the task SHALL walk `orchestration/defs/1_ingestion/`,
  `2_materials/`, `3_model_lifecycle/`, `4_asset_generation/`,
  `5_agent_ops/`
- **AND** for each layer, the task SHALL count the assets,
  groups, sensors, jobs, and broken assets
- **AND** the task SHALL write the per-group report
- **AND** the task SHALL exit 0 if no broken assets, exit 1 if any

### Requirement: dagster_sync_health Dagster asset

The system SHALL provide a Dagster asset `dagster_sync_health` at
`orchestration/defs/sync_assets.py` that reads the latest
`stedding/sync-reports/dagster-{date}.md` and emits metadata for
the 833 assets.

#### Scenario: dagster_sync_health materializes on defs/ file changes

- **WHEN** a file in `orchestration/defs/` changes (sensor triggers)
- **THEN** the `dagster_sync_health` asset SHALL re-materialize
- **AND** the asset SHALL emit `asset_count`, `sensor_count`,
  `group_count`, `broken_asset_count` metadata

### Requirement: dagster_assets Cognee cluster

The system SHALL ingest the 833 Dagster asset definitions + their
parent resources into the new `dagster_assets` Cognee cluster via
`scripts/sync_dagster_assets_to_cognee.py`.

#### Scenario: dagster_assets cluster grows over time

- **WHEN** `scripts/sync_dagster_assets_to_cognee.py` is invoked
- **THEN** it SHALL walk `orchestration/defs/` via `ast.parse`
- **AND** it SHALL ingest the 833 asset definitions into the
  `dagster_assets` Cognee cluster
- **AND** the cluster SHALL have a per-layer summary

### Requirement: dagster-asset-sync skill

The system SHALL provide `.agents/skills/dagster-asset-sync/SKILL.md`
documenting the Layer 6 sync loop + the new Cognee cluster + the
new CCC guide `dagster-asset-graph` (21st guide).

#### Scenario: skill references all 6 sync layers

- **WHEN** the operator opens the SKILL.md
- **THEN** it SHALL document the 6 sync layers (paths, ccc, cognee,
  skills, mcp, dagster)
- **AND** it SHALL explain the dagster_assets Cognee cluster
- **AND** it SHALL link to the CCC 21st guide `dagster-asset-graph`

### Requirement: Safe auto-fix mode requires AST validation

The system SHALL validate every file modification made by
`sync:paths --fix` via `ast.parse()` for Python files (skips
non-Python files like `.md`, `.json`, `.yaml`). The fix-mode
SHALL refuse to modify a file if `ast.parse()` raises a
`SyntaxError` post-rename, and SHALL report the file path + line
number to the fix-applied report.

#### Scenario: AST validation fails on a renamed file

- **GIVEN** `sync:paths --fix` renames a path inside a `.py` file
- **WHEN** the post-rename `ast.parse()` raises a `SyntaxError`
- **THEN** the fix-mode SHALL revert the change to the original file
- **AND** the fix-applied report SHALL include the file path + line
  number + the SyntaxError message
- **AND** the fix-mode exit code SHALL be 2 (partial failure)

#### Scenario: AST validation passes on all renamed files

- **GIVEN** `sync:paths --fix` renames a path inside 50 `.py` files
- **WHEN** all 50 files post-rename `ast.parse()` cleanly
- **THEN** the fix-mode SHALL commit all 50 renames
- **AND** the fix-applied report SHALL list the 50 file paths
- **AND** the fix-mode exit code SHALL be 0 (success)

## Cross-references

- `openspec/changes/2026-08-15-retrospective-cleanup-v1/` (the change dir)
- `openspec/changes/2026-08-15-knowledge-sync-loop-v1/` (the foundation)
- `scripts/sync/` (the 6 sync scripts + the new dagster)
- `.agents/skills/knowledge-sync-loop/SKILL.md` (the doc for the sync loop pattern)
- `openspec/changes/2026-08-15-centralized-model-schema-registry-and-deployment-control-panel-v1/` (the model-registry change that consumes the deployment control panel)
- `stedding/sync-reports/retroactive-cleanup/2026-08-15/` (the per-directory diagnostic reports)
