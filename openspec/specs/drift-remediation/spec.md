# drift-remediation Specification

## Purpose
TBD - created by archiving change 2026-07-30-drift-remediation-everything-bagel-v1. Update Purpose after archive.
## Requirements
### Requirement: Dagster schedule expectations are restored on file truncation

The system SHALL treat any commit that removes public symbols from
`orchestration/defs/sync_assets.py` (the canonical sync_health asset
home) as a regression that breaks the `knowledge-sync-loop` cron
half of the `repo-hygiene-agent-routing-and-sync-wiring-v1` change.
The `daily sync_health cron` requirement from the `knowledge-sync-loop`
spec MUST remain satisfiable at all times.

#### Scenario: A commit truncates sync_assets.py

- **GIVEN** `orchestration/automation/sync_schedules.py` imports
  `sync_health_job` + `dagster_sync_health_job` from
  `orchestration.defs.sync_assets`
- **WHEN** a commit deletes the `sync_health_job` + `dagster_sync_health_job`
  definitions from `sync_assets.py`
- **THEN** the next `mise run sync:all` (or any `dagster dev` startup)
  must emit a `sync_schedules_load_failed` warning
- **AND** the daily `0 */4 * * *` cron must NOT silently disappear
- **AND** the `knowledge-sync-loop` spec's "Daily sync_health cron"
  requirement is violated

#### Scenario: The drift-remediation change restores the deleted assets

- **GIVEN** the regression above
- **WHEN** the `drift-remediation` change appends the 4 deleted assets
  + 2 utility functions + 2 sensor definitions + 2 job definitions
  to `sync_assets.py`
- **THEN** `from orchestration.definitions import defs` succeeds
  with no `[skip]` warnings
- **AND** `defs.schedules` includes both `sync_health_every_4h` +
  `dagster_sync_health_every_4h`
- **AND** the `knowledge-sync-loop` spec's "Daily sync_health cron"
  requirement is satisfied again

### Requirement: Every `@asset` module is importable without `from __future__ import annotations`

The system SHALL NOT have `from __future__ import annotations` in any
`.py` file that uses `@asset(context: AssetExecutionContext)`. The
PEP 563 string-style annotation breaks the runtime identity check
(`params[0].annotation not in [AssetExecutionContext, ...]`).

#### Scenario: A new module is added with the bad pattern

- **GIVEN** a developer creates `orchestration/defs/2_materials/<new>/<thing>.py`
  with `from __future__ import annotations` + a `@asset` using
  `context: AssetExecutionContext`
- **WHEN** `dagster dev` (or `mise run dagster:dev`) starts
- **THEN** the module is silently `[skip]`-ed at `definitions.py:139`
  with the error `Cannot annotate 'context' parameter with type AssetExecutionContext`
- **AND** the asset is never registered with Dagster
- **AND** the `dagster:dev` task description's claimed count
  ("199 assets + 22 asset checks") is now wrong

#### Scenario: The drift-remediation change removes the bad pattern

- **GIVEN** the regression above
- **WHEN** the `drift-remediation` change removes
  `from __future__ import annotations` from the 8 broken files
- **THEN** all 8 modules register their assets
- **AND** the AST scan in `scripts/sync/ast_walk.py` reports the
  expected ~199 assets + 50 asset_checks
- **AND** the `dagster:dev` task description becomes accurate again

### Requirement: mise tasks use direct Python paths, not `uv run`

The system SHALL use `.venv/bin/python3` in `mise.toml` `run` fields
for tasks that execute a Python script. The `uv run` command fails
on a stale dependency graph (`dagster-components<=0.26.9 is available
and your project depends on dagster-components>=1.13`), which regression-blocks 42 standalone mise tasks.

#### Scenario: A developer adds a `uv run python` task

- **GIVEN** the active Python is 3.13 + the project's dagster-components
  pin is `>=1.13`
- **WHEN** the developer adds `run = "uv run python scripts/foo.py"` to
  `mise.toml`
- **THEN** `mise run <task>` fails with
  `requirements are unsatisfiable` because the dep resolver can't find
  a compatible dagster-components version
- **AND** the task is regression-blocked for any operator who runs
  it without first running `uv sync`

#### Scenario: The drift-remediation change migrates to direct paths

- **GIVEN** the regression above
- **WHEN** the `drift-remediation` change substitutes `.venv/bin/python3`
  for `uv run python` in the safe-to-migrate scripts (`scripts/*.py`
  that don't require the workspace env)
- **THEN** `mise run <task>` succeeds because the `.venv` is already
  installed and the dependencies resolve correctly
- **AND** the 79 mis-tasks in `miep:v3:*`, `cic:*`, `agents:*`, etc.
  all work without `uv sync` as a precondition

### Requirement: The registry audit covers all hardcoded-model surfaces

The system SHALL include `meaisinfhoghlaim/` in the `_AUDIT_DIRS` list
of `scripts/registry_audit.py`. The audit's purpose is to catch
hardcoded model strings; the gap means the 4 hardcoded defaults in
`meaisinfhoghlaim/process/llm_router.py` + the 2 routing entries in
`meaisinfhoghlaim/models/routing.py` are invisible to the gate.

#### Scenario: A hardcoded model is added to meaisinfhoghlaim/process/llm_router.py

- **GIVEN** a developer adds `default_model="gpt-4.5-turbo"` to a new
  function in `meaisinfhoghlaim/process/llm_router.py`
- **WHEN** `mise run lint:registry` runs
- **THEN** the audit does NOT detect the new hardcoded string
  (because `meaisinfhoghlaim/` is not in `_AUDIT_DIRS`)
- **AND** the centralized-model-registry spec requirement is violated
  silently

#### Scenario: The drift-remediation change closes the audit gap

- **GIVEN** the regression above
- **WHEN** the `drift-remediation` change adds `meaisinfhoghlaim/` to
  the `_AUDIT_DIRS` list AND migrates the 6 hardcoded models to
  `model_for(...)` lookups
- **THEN** `mise run lint:registry` exits 0 with "Found 0 hardcoded model strings"
- **AND** the 6 migrated call sites resolve via `MODEL_REGISTRY` at runtime
- **AND** the next `mise run cic:meaisin:litellm-regenerate` regenerates
  `litellm/config/config.yaml` with the canonical names

