# Tasks: Sync health dashboard consolidation (marimo v14)

> **Phase plan**: 2 phases, ~1.5 days work.
> **Branch**: `token-plan-lc-pipeline-2026-08` (current working branch).
> **OpenSpec change**: `2026-08-10-marimo-v14-sync-health-dashboard-consolidation-v1`.

## Phase 1 — Build the `notebooks/sync_health.py` dashboard (1 day)

### T1.1 — Build `notebooks/_shared/area_shims/sync_health.py` (~120 LOC)

- [ ] T1.1.a — Write the `dev_env_tools_overview()` helper
- [ ] T1.1.b — Write the `observability_overview()` helper
- [ ] T1.1.c — Write the `dagster_sync_overview()` helper
- [ ] T1.1.d — Write the `baml_sync_overview()` helper
- [ ] T1.1.e — Write the `stacks_sync_overview()` helper
- [ ] T1.1.f — Write the `dlt_sync_overview()` helper
- [ ] T1.1.g — Write the `agents_sync_overview()` helper
- [ ] T1.1.h — Write the `notebooks_sync_overview()` helper
- [ ] T1.1.i — Write the `cognee_sync_overview()` helper
- [ ] T1.1.j — Write the `ccc_sync_overview()` helper
- [ ] T1.1.k — Write the `paths_sync_overview()` helper

### T1.2 — Build `notebooks/sync_health.py` (~600 LOC)

- [ ] T1.2.a — Write the PEP 723 header
- [ ] T1.2.b — Write the imports
- [ ] T1.2.c — Build the `_overview` cell (renders the 11 sync layer
  statuses as a mo.callout grid)
- [ ] T1.2.d — Build the 10 tab cells (Dev Env Tools /
  Observability / Dagster / BAML / Stacks / DLT / Agents / Notebooks
  / Cognee / CCC)
- [ ] T1.2.e — Wrap all 10 tabs in `mo.ui.tabs`
- [ ] T1.2.f — Add the LLM "Ask about sync health" tab (P3)
- [ ] T1.2.g — Add the 5 educative outline patterns (E1-E5)
- [ ] T1.2.h — Add the dual-mode CLI (`_cli_main` +
  `if __name__ == "__main__":` per https://docs.marimo.io/guides/scripts/)
- [ ] T1.2.i — Add the 3-column grid (`layout_file` +
  `sync_health.grid.json`)

## Phase 2 — Move the 10 old sync sub-notebooks + validate + archive (0.5 day)

### T2.1 — Move the 10 old sync sub-notebooks to `notebooks/legacy/v7_consolidation/sync/`

- [ ] T2.1.a — `mkdir -p notebooks/legacy/v7_consolidation/sync/`
- [ ] T2.1.b — `git mv` the 10 sub-notebooks:
  - `14_dev_env_tools_05_openspec_list.py`
  - `14_dev_env_tools_06_mise_lint_skills.py`
  - `14_dev_env_tools_07_model_registry.py`
  - `14_dev_env_tools_08_registry_drift_watch.py`
  - `14_dev_env_tools_09_registry_drift_history.py`
  - `14_dev_env_tools_10_deployment_choice_editor.py`
  - `15_observability_01_baml_drift_audit.py`
  - `15_observability_02_irish_extraction_quality.py`
  - `15_observability_03_cognee_knowledge_graph.py`
  - `25_dagster_sync_dashboard.py`
  - `26_baml_sync_dashboard.py`
  - `27_stacks_sync_dashboard.py`
  - `28_dlt_sync_dashboard.py`
  - `29_agents_sync_dashboard.py`
  - `30_notebooks_sync_dashboard.py`
- [ ] T2.1.c — Add a `DEPRECATED.md` redirect note pointing to the
  new `sync_health.py` dashboard

### T2.2 — `mise.toml` updates

- [ ] T2.2.a — Add `biep:v3:marimo:sync:dev` task

### T2.3 — OpenSpec validation

- [ ] T2.3.a — Run `openspec validate
  2026-08-10-marimo-v14-sync-health-dashboard-consolidation-v1 --strict`
- [ ] T2.3.b — Run `marimo check` on `notebooks/sync_health.py`
- [ ] T2.3.c — Run `mise run biep:v3:marimo:lint`

### T2.4 — Archive

- [ ] T2.4.a — Run `openspec archive
  2026-08-10-marimo-v14-sync-health-dashboard-consolidation-v1 --yes`
- [ ] T2.4.b — Commit + push the change (per the AGENTS.md mandatory
  push policy)

## Acceptance gates

- [ ] `notebooks/sync_health.py` opens via `marimo edit` without
  errors
- [ ] The 10 tabs render the per-sync-layer overview
- [ ] All 10 old sync sub-notebooks moved to
  `notebooks/legacy/v7_consolidation/sync/`
- [ ] The subdirectory has a `DEPRECATED.md` redirect note
- [ ] `openspec validate --strict` passes
- [ ] `marimo check` passes on `notebooks/sync_health.py`
- [ ] Total LOC saved: ~500+ (consolidation of the 10 sync
  sub-notebooks)