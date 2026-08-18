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
hardcoded model strings; the gap means the hardcoded defaults in
`meaisinfhoghlaim/models/routing.py` are invisible to the gate.

The previous requirement's reference to "4 hardcoded defaults in
`meaisinfhoghlaim/process/llm_router.py`" is **stale** — those defaults
were migrated to `model_for(...)` lookups by the
`2026-07-30-drift-remediation-everything-bagel-v1` change (commits
verified during the `2026-08-17-hygiene-drift-cleanup-v1` ccc audit;
`llm_router.py:315,332,350,365` all call `model_for(...)` correctly).

The remaining gap was `meaisinfhoghlaim/models/routing.py:58-79,97`:
~15 hardcoded model strings (`uccix-mistral-24b`, `gemma-4-26B-A4B`,
`molmo2-8b`) in the per-`(source_group, language)` routing table. These
were also migrated as part of `2026-08-17-hygiene-drift-cleanup-v1`
(P3.1 + P3.3 tasks). The routing table now references 4 canonical
constants (`DEFAULT_TEXT_MODEL`, `IRISH_TEXT_MODEL`,
`DIAGRAM_OCR_MODEL`, `DEFAULT_OCR_MODEL`) that all resolve via
`model_for(...)`.

The regression gate that enforces this going forward is
`tests/test_routing_model_registry.py`, which fails if any entry in
`ROUTING_TABLE` uses a model string that is NOT one of the 4 canonical
constants.

#### Scenario: A hardcoded model is added to meaisinfhoghlaim/models/routing.py

- **GIVEN** a developer adds a new entry to `ROUTING_TABLE` with
  `model="qwen3-vl-30b-a3b"` (a raw string, not a constant)
- **WHEN** `mise run lint:registry` runs
- **THEN** the audit MUST detect the new hardcoded string (because
  `meaisinfhoghlaim/` is in `_AUDIT_DIRS` per the
  `2026-07-30-drift-remediation-everything-bagel-v1` change)
- **AND** `pytest tests/test_routing_model_registry.py` MUST fail with
  a finding like `routing_table[(new_source, 'en')] uses an unknown model string 'qwen3-vl-30b-a3b'; expected one of the 4 canonical constants`

#### Scenario: The 4 canonical constants resolve via model_for()

- **WHEN** `meaisinfhoghlaim.models.routing` is imported
- **THEN** all 4 constants (`DEFAULT_TEXT_MODEL`, `IRISH_TEXT_MODEL`,
  `DIAGRAM_OCR_MODEL`, `DEFAULT_OCR_MODEL`) MUST resolve to the same
  strings that `model_for("text_llm", "default")`,
  `model_for("text_llm", "irish", language="ga")`,
  `model_for("ocr_vision", "specialist")`, and
  `model_for("ocr_vision", "default")` return
- **AND** `tests/test_routing_model_registry.py` MUST pass all 12
  assertions

