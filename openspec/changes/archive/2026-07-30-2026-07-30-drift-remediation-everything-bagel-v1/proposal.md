# 2026-07-30-drift-remediation-everything-bagel-v1

## Why

The repo-hygiene-agent-routing-and-sync-wiring-v1 change (archived 2026-07-30
in commit `5c9506ef7`) shipped the 7-layer sync architecture + the `lint:drift-docs`
gate + the per-spec AGENTS.md convention. The Wave 9 commit closed 26/28 tasks.

Three things broke *after* that change shipped, plus the audit surfaced 4 new
drift categories that the original change didn't cover. This change fixes them
all in one consistent pass.

### The 4 drift categories

1. **The `sync_health_job` regression (critical)** — commit `91b85c1c1 feat(baml-sync)`
   rewrote `orchestration/defs/sync_assets.py` to add the new baml_sync_health
   assets, but in doing so it accidentally truncated the file from 297 lines
   to 139 lines, deleting the `sync_health`, `stale_skill_alert`,
   `dagster_sync_health`, `dagster_sync_alert` assets + the `sync_health_job`
   + `dagster_sync_health_job` definitions. The new `orchestration/automation/sync_schedules.py`
   (which I shipped) still imports those missing jobs, so the daily `0 */4 * * *`
   cron now fails silently at `definitions.py:139`
   (`sync_schedules_load_failed: cannot import name 'sync_health_job'`).
   The whole `knowledge-sync-loop` cron half is dead.

2. **8 more broken Dagster asset modules** — `from __future__ import annotations`
   + `@asset(context: AssetExecutionContext)` is silently `[skip]`-ed at
   `definitions.py` load time. Only 4 of the 12 affected files were fixed in
   Wave 9; the other 8 silently skip ~80+ assets. The `dagster:dev` task
   description claims "199 assets + 22 asset checks" but the actual count is
   118 + 50.

3. **Audit-pattern gaps + lint failures** — `lint:registry` skips
   `meaisinfhoghlaim/process/` and `meaisinfhoghlaim/models/` (the audit
   `_AUDIT_DIRS` doesn't include them), so the 4 hardcoded model defaults
   in `llm_router.py` + the 2 routing entries in `models/routing.py` are
   invisible to the gate. Plus `lint:drift-docs` already drifted again
   (81 → 82 specs after the baml-sync-loop archive). Plus `lint:registry`
   has a false positive on `sync_assets.py:49` (a regex pattern, not a model
   reference).

4. **`uv run python` blocking 42 standalone mise tasks** — `uv run` fails on the stale
   dependency graph (`dagster-components<=0.26.9 is available and your project
   depends on dagster-components>=1.13`). The fix is to migrate to `.venv/bin/python3`
   (which works). I already fixed the 2 `lint:drift-docs` tasks; 79 more
   regression-blocked mise tasks remain.

### What this change does

#### Section A — Restore the sync_health_job regression (the cron-killer fix)

Append the 4 deleted assets + 2 utility functions + 2 sensor definitions +
2 job definitions to `orchestration/defs/sync_assets.py`. The file becomes
~300 lines (1 import block + 6 assets + 3 sensors + 3 jobs + 3 utility
function pairs). The `sync_health_job` + `dagster_sync_health_job` names
are preserved exactly so `orchestration/automation/sync_schedules.py`
loads cleanly.

#### Section B — Un-skip the 8 broken Dagster asset modules

Remove `from __future__ import annotations` (PEP 563 string-style annotations
break the `@asset` runtime type-hint validator) from these 8 files:

- `orchestration/defs/2_materials/biiep_v3/m0_foundation_assets.py`
- `orchestration/defs/2_materials/eu_multilingual/english_coverage_monitor.py`
- `orchestration/defs/2_materials/eu_multilingual/irish_coverage_monitor.py`
- `orchestration/defs/2_materials/eu_multilingual/language_alignment_mapper.py`
- `orchestration/defs/2_materials/ireland_education/ireland_jc_assets.py`
- `orchestration/defs/2_materials/endpoint_health/alerts.py`
- `orchestration/defs/2_materials/endpoint_health/sink.py`
- `orchestration/defs/2_materials/_base/jurisdiction_assets_base.py`

After this, the AST scan should report ~199 assets + 50 asset_checks (the
canonical counts from the `dagster:dev` description).

#### Section C — Audit-pattern gaps + lint fixes

1. Add `meaisinfhoghlaim/` to the `_AUDIT_DIRS` in `scripts/registry_audit.py`.
2. Whitelist `gemma-3-27b` and `gemma-3-4b` in `scripts/registry_audit.py:_KNOWN_MODEL_KEYS`
   (the `gemma-3-27b` in `sync_assets.py:49` is a regex pattern, not a model ref).
3. Migrate the 4 hardcoded defaults in `meaisinfhoghlaim/process/llm_router.py`
   to `model_for("text_llm", "default")` / `model_for("text_llm", "irish",
   language="ga")` / `model_for("text_llm", "fast")` lookups.
4. Migrate the 2 routing entries in `meaisinfhoghlaim/models/routing.py`
   from `model="qwen3-vl-8b"` to `model_for("ocr_vision", "default")`.
5. Bump the spec count claim `81 → 82` in `AGENTS.md:20` and
   `agents/tuatha/AGENTS.md:60` (the baml-sync-loop archive).
6. Fix `mise.toml:175` `dagster:dev` description (the 199 assets + 31 jobs
   count is now wrong; reflect the actual post-fix count).
7. Run `mise run sync:paths --fix` to clean the 47 auto-fixable occurrences
   (per the `2026-08-15-retroactive-pre-v7-cleanup-v1` change).

#### Section D — `uv run` migration in mise.toml

Replace the 42 safe `uv run python` lines with `.venv/bin/python3` for tasks that
just run a Python script or module. Keep `uv run` for the 38 live
`meaisin:ocr:test:*` + `meaisin:converter:test:*` + `meaisin:agent:test:*`
entry-points (those need the workspace env).

## Cross-references

- `openspec/changes/archive/2026-07-30-2026-07-29-repo-hygiene-agent-routing-and-sync-wiring-v1/`
  (archived — the Wave 9 commit that this change extends)
- `openspec/changes/2026-08-15-baml-sync-loop-v1/` (in-flight — the change that
  accidentally truncated `sync_assets.py` in commit `91b85c1c1`)
- `openspec/changes/archive/2026-07-29-2026-08-15-retroactive-pre-v7-cleanup-v1/`
  (archived — the `sync:paths --fix` mode this change re-runs)

## Out of scope

- **The 5 pre-existing failing specs** (`baml-sync-loop`, `cianfhoghlaim-marimo-dashboards`,
  `dlthub-platform-integration`, `meaisinfhoghlaim-ocr-htr`, `site-crawler`) —
  each is its own author/intent; will be opened as separate openspec changes.
- **The 13 multi-line bash blocks remaining in `mise.toml`** — they work today;
  future drift risk only.
- **Pre-v7 path drift beyond the 47 auto-fixable occurrences** — the 1912
  manual occurrences are documented historical context (per the
  `2026-08-15-retroactive-pre-v7-cleanup-v1` change).
- **Renaming `ModelRouter` to `BAMLModelClient`** — separate refactor.

## Dependencies

- `Blocked by: none`
- `Blocked by (soft): 2026-08-15-baml-sync-loop-v1` (the sibling change that
  accidentally truncated sync_assets.py in commit `91b85c1c1`)
- `Affected repos: cianfhoghlaim` (single-repo; bonneagar is a subdirectory)
