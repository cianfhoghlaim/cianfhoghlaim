# Tasks: 2026-07-30-drift-remediation-everything-bagel-v1

## Phase 1 — OpenSpec change scaffolding (4 tasks)

- [x] **T1.1**: Create `openspec/changes/2026-07-30-drift-remediation-everything-bagel-v1/proposal.md` (the why + what changes)
- [x] **T1.2**: Create `openspec/changes/2026-07-30-drift-remediation-everything-bagel-v1/tasks.md` (this file)
- [x] **T1.3**: Create `openspec/changes/2026-07-30-drift-remediation-everything-bagel-v1/cross-repo-sync.md` (single-repo; documented no-op)
- [x] **T1.4**: Create the 3 spec deltas under `openspec/changes/2026-07-30-drift-remediation-everything-bagel-v1/specs/`

## Phase 2 — Section A: Restore the sync_health_job regression (5 tasks)

- [x] **T2.1**: Restore the `from dagster import ...` block at the top of `orchestration/defs/sync_assets.py` (AssetExecutionContext, MetadataValue, SensorEvaluationContext, asset, define_asset_job, sensor, RunRequest)
- [x] **T2.2**: Restore `REPORTS_DIR = Path("stedding/sync-reports")` + `_latest_report()` + `_parse_report()` + `_latest_dagster_report()` + `_parse_dagster_report()` utility functions
- [x] **T2.3**: Restore `sync_health` + `stale_skill_alert` + `sync_report_sensor` + `sync_health_job` (the 5-layer sync orchestration)
- [x] **T2.4**: Restore `dagster_sync_health` + `dagster_sync_alert` + `dagster_assets_sensor` + `dagster_sync_health_job` (Layer 6 of the sync loop)
- [x] **T2.5**: Verify `orchestration/automation/sync_schedules.py` loads cleanly + `from orchestration.definitions import defs` registers the required schedules (3 live, including both required schedules)

## Phase 3 — Section B: Un-skip the 8 broken Dagster asset modules (1 task)

- [x] **T3.1**: Remove `from __future__ import annotations` from each of the 8 files: `biiep_v3/m0_foundation_assets.py`, `eu_multilingual/english_coverage_monitor.py`, `eu_multilingual/irish_coverage_monitor.py`, `eu_multilingual/language_alignment_mapper.py`, `ireland_education/ireland_jc_assets.py`, `endpoint_health/alerts.py`, `endpoint_health/sink.py`, `_base/jurisdiction_assets_base.py`. Verify each module's `dagster_internal_init` succeeds (no `[skip]` in `definitions.py` stderr).

## Phase 4 — Section C: Audit-pattern gaps + lint fixes (7 tasks)

- [x] **T4.1**: Add `meaisinfhoghlaim/` to `_AUDIT_DIRS` in `scripts/registry_audit.py`
- [x] **T4.2**: Whitelist `gemma-3-27b` and `gemma-3-4b` in `_KNOWN_MODEL_KEYS` in `scripts/registry_audit.py`
- [x] **T4.3**: Migrate the 4 hardcoded defaults in `meaisinfhoghlaim/process/llm_router.py` to `model_for(...)` lookups
- [x] **T4.4**: Migrate the 2 routing entries in `meaisinfhoghlaim/models/routing.py` from `model="qwen3-vl-8b"` to `model_for("ocr_vision", "default")`
- [x] **T4.5**: Bump `79 → 82` in `AGENTS.md:20` and `agents/tuatha/AGENTS.md:60`
- [x] **T4.6**: Fix `mise.toml:175` `dagster:dev` description to use the live `sync:dagster` count rather than a hardcoded count
- [x] **T4.7**: Run `mise run sync:paths --fix`; zero safe auto-fixable files remain (1,912 manual references remain informational)

## Phase 5 — Section D: `uv run` migration in mise.toml (3 tasks)

- [x] **T5.1**: Survey all 80 original `uv run python` lines in `mise.toml` and classify them as safe to migrate or workspace-dependent
- [x] **T5.2**: Substitute the 42 safe commands with `.venv/bin/python3`; retain `uv run python` for the 38 live meaisín OCR/converter/agent entrypoints
- [x] **T5.3**: Verify all 47 direct-Python tasks (42 migrated + 5 pre-existing) exit 0 with `mise run --dry-run <task>`

## Phase 6 — Validation (5 tasks)

- [x] **T6.1**: `openspec validate 2026-07-30-drift-remediation-everything-bagel-v1 --strict` exits 0
- [x] **T6.2**: `mise run lint:drift-docs` exits 0 (no number drift claims)
- [x] **T6.3**: `mise run lint:registry` exits 0 (no hardcoded model strings)
- [x] **T6.4**: `mise run sync:paths` exits 0 with 0 safe auto-fixable occurrences; manual references remain reported
- [x] **T6.5**: `from orchestration.definitions import defs` shows no `[skip]` warnings + schedules include both `sync_health_every_4h` + `dagster_sync_health_every_4h`

## Phase 7 — Commit (1 task)

- [ ] **T7.1**: Commit with the conventional message:
  ```
  feat(drift-remediation): restore sync_health cron + 8 Dagster assets + 42 standalone mise tasks

  Implements the 2026-07-30-drift-remediation-everything-bagel-v1 openspec
  change. Fixes:
  - The sync_health_job regression (commit 91b85c1c1 truncated sync_assets.py;
    the daily 0 */4 * * * cron never started; the try/except in definitions.py
    swallowed the error)
  - 8 broken Dagster asset modules (from __future__ import annotations + @asset)
  - The lint:registry audit-pattern gap (meaisinfhoghlaim/ was not scanned)
  - 42 standalone mise tasks that were regression-blocked by `uv run`'s stale dependency graph

  Validates: openspec validate --strict, lint:drift-docs, lint:registry,
  sync:paths, definitions.py (no [skip]).
  ```
