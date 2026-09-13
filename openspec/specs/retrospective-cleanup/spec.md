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

### Requirement: every AGENTS.md count claim SHALL match ground truth

The system MUST keep every claim of the form
`<N> (specs|skills|stacks|models|notebooks)` in every
in-scope `AGENTS.md` file (the 16 files enumerated in
`scripts/lint_drift_docs.py:AGENTS_FILES`) matching the
live ground-truth count produced by
`scripts/lint_drift_docs.py:ground_truth()`.

A new `mise run lint:drift-docs:rebaseline` task
(implemented by `scripts/rebaseline_drift_docs.py`) MUST
walk every drift violation reported by
`mise run lint:drift-docs` and rewrite the count claim
in place. The script MUST support:

1. A default **dry-run mode** that prints the planned
   diff and exits 0
2. An `--apply` mode that writes the fix to disk

The script MUST emit a JSON report at
`stedding/sync-reports/drift-docs-rebaseline-{date}.json`
listing every planned/applied fix with the file path,
line number, old value, and new value.

#### Scenario: Operator rebaselines a stale count claim

- **GIVEN** an operator runs `mise run lint:drift-docs`
  and the report shows a violation (e.g.
  `AGENTS.md:20 specs: claimed 89, actual 92`)
- **WHEN** the operator runs
  `mise run lint:drift-docs:rebaseline:dry-run`
- **THEN** the script MUST print a diff showing the
  planned fix: "`AGENTS.md:20` `89` → `92`"
- **AND** the script MUST exit 0 without modifying any
  files
- **WHEN** the operator then runs
  `mise run lint:drift-docs:rebaseline` (with `--apply`)
- **THEN** the script MUST write the fix to disk
- **AND** a subsequent run of `mise run lint:drift-docs`
  MUST report 0 violations

#### Scenario: New AGENTS.md file is added with a stale count

- **GIVEN** a developer adds a new file
  `orchestration/defs/2_materials/_base/AGENTS.md` that
  claims `45 Dagster assets` but the actual count is 833
- **WHEN** the operator runs `mise run lint:drift-docs`
- **THEN** the script MUST report the violation
- **WHEN** the operator runs
  `mise run lint:drift-docs:rebaseline`
- **THEN** the script MUST fix the count to `833`
- **AND** the AGENTS_FILES list in
  `scripts/lint_drift_docs.py` MUST auto-include the new
  file (or the operator MUST add it manually if the
  in-scope list is curated)

### Requirement: INDEXING_AND_COGNITION.md SHALL reflect the current agent + skill + MCP counts

The system MUST keep the
`.agents/skills/INDEXING_AND_COGNITION.md` skill
(the 655-line consolidated doc that replaced the
`docs/01-cognee/*.md` files during the v4 consolidation)
reflecting the live ground truth of:

1. The number of MCP servers wired in `opencode.json`
2. The number of OpenCode agents wired in `opencode.json`
3. The number of skills discoverable via
   `bun run ccc:search` (recursive count of SKILL.md
   files under `.agents/skills/`)
4. The CCC chunk count (from `bun run ccc:status` or
   `ccc status`)
5. The Cognee cluster count (the 7 typed clusters from
   the per-cluster cognify model)

…matching the live ground truth at all times.

The file MUST NOT reference dead paths (e.g.
`sruth/cianfhoghlaim/STATUS.md`) that no longer exist on
disk.

#### Scenario: A new skill is added

- **GIVEN** a developer adds a new skill
  `.agents/skills/new-skill/SKILL.md` (e.g. the
  `firecrawl-research-index` skill)
- **WHEN** the operator runs `bun run ccc:status` and
  `mise run lint:skills`
- **THEN** the skill count MUST increment by 1
- **AND** the operator MUST update
  `.agents/skills/INDEXING_AND_COGNITION.md` to reflect
  the new count
- **OR** the `lint:drift-docs` gate MUST catch the
  inconsistency on the next CI run

#### Scenario: INDEXING_AND_COGNITION.md references a dead path

- **GIVEN** INDEXING_AND_COGNITION.md references
  `sruth/cianfhoghlaim/STATUS.md` (a path that no longer
  exists post-v7 flattening)
- **WHEN** an agent searches for that file
- **THEN** the search MUST fail
- **AND** `mise run lint:drift-docs` MUST NOT catch this
  (drift-docs only checks count claims, not path claims)
- **AND** the `lint:guides-yml` gate (from Change 2)
  MUST catch it if the path appears in `.cocoindex_code/guides.yml`
- **AND** the operator MUST manually delete the dead
  reference

## Cross-references

- `openspec/changes/2026-08-15-retrospective-cleanup-v1/` (the change dir)
- `openspec/changes/2026-08-15-knowledge-sync-loop-v1/` (the foundation)
- `scripts/sync/` (the 6 sync scripts + the new dagster)
- `.agents/skills/knowledge-sync-loop/SKILL.md` (the doc for the sync loop pattern)
- `openspec/changes/2026-08-15-centralized-model-schema-registry-and-deployment-control-panel-v1/` (the model-registry change that consumes the deployment control panel)
- `stedding/sync-reports/retroactive-cleanup/2026-08-15/` (the per-directory diagnostic reports)
