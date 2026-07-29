# Tasks: 2026-08-15-retroactive-pre-v7-cleanup-v1

## Phase 1: Openspec + Spec docs (3 tasks)

- [ ] **T1.1**: Create `openspec/changes/2026-08-15-retroactive-pre-v7-cleanup-v1/proposal.md` (the why + what changes)
- [ ] **T1.2**: Create `openspec/changes/2026-08-15-retroactive-pre-v7-cleanup-v1/tasks.md` (this file)
- [ ] **T1.3**: Create `openspec/specs/retrospective-cleanup/spec.md` (the new capability spec with the 3-section requirements: cleanup, dagster layer, auto-fix)

## Phase 2: Auto-fix script (3 tasks)

- [ ] **T2.1**: Create `scripts/sync_paths_fix.py` (reads the sync:paths report, applies the 3 safe rename patterns, validates via `ast.parse` per file, writes the fix-applied report)
- [ ] **T2.2**: Update `scripts/sync/paths.sh` to support the `--fix` flag (calls sync_paths_fix.py + re-runs sync:paths to verify the count drops)
- [ ] **T2.3**: Run `mise run sync:paths --fix` and verify the 47 auto-fixable occurrences drop to 0 (the 1912 .md occurrences are excluded)

## Phase 3: Layer 6 (Dagster) script (2 tasks)

- [ ] **T3.1**: Create `scripts/sync/dagster.sh` (Layer 6; walks the 5-layer defs/ tree + validates ~833 assets; produces per-group report to stedding/sync-reports/dagster-{date}.md)
- [ ] **T3.2**: Update `scripts/sync/all.sh` to include the new sync:dagster layer in the orchestrator

## Phase 4: Mise tasks (2 tasks)

- [ ] **T4.1**: Add the `sync:dagster` task to mise.toml (description: "Layer 6: validate ~833 Dagster assets via AST parsing + per-group breakdown; per the 2026-08-15-retroactive-pre-v7-cleanup-v1 change")
- [ ] **T4.2**: Update the `sync:paths` task description in mise.toml to mention the new `--fix` mode

## Phase 5: Dagster asset (1 task)

- [ ] **T5.1**: Add the `dagster_sync_health` asset to `orchestration/defs/sync_assets.py` (emits asset_count, sensor_count, group_count, broken_asset_count metadata + fires on defs/ file changes)

## Phase 6: Cognee ingestion (1 task)

- [ ] **T6.1**: Create `scripts/sync_dagster_assets_to_cognee.py` (ingests the 833 Dagster asset definitions + their parent resources into the new `dagster_assets` Cognee cluster)

## Phase 7: Marimo + Skill (3 tasks)

- [ ] **T7.1**: Create `notebooks/25_dagster_sync_dashboard.py` (the analog of notebook 24 for the knowledge surface; reads the latest stedding/sync-reports/dagster-{date}.md + shows the per-group breakdown)
- [ ] **T7.2**: Create `.agents/skills/dagster-asset-sync/SKILL.md` (documents the Layer 6 sync loop + the new Cognee cluster + the new CCC guide)
- [ ] **T7.3**: Append the 21st concept guide `dagster-asset-graph` to `.cocoindex_code/guides.yml`

## Phase 8: Update existing surfaces (3 tasks)

- [ ] **T8.1**: Update `notebooks/24_deployment_control_panel.py` (add the `dagster` layer status to the 6 layer statuses)
- [ ] **T8.2**: Update `scripts/bring-up-smoke-test.sh` (add Step 7 = sync:dagster; update the expected skill count from 54 to 55)
- [ ] **T8.3**: Update `openspec/AGENTS.md` (add the new spec to the priority list)

## Phase 9: Final verification (3 tasks)

- [ ] **T9.1**: Run `mise run biep:v3:smoke-test` + `bash scripts/bring-up-smoke-test.sh` + `bash scripts/week4-smoke-test.sh` to verify all 3 smoke tests pass
- [ ] **T9.2**: Run `openspec validate 2026-08-15-retroactive-pre-v7-cleanup-v1 --strict` and verify it passes
- [ ] **T9.3**: Run `openspec archive 2026-08-15-retroactive-pre-v7-cleanup-v1 --yes` to move the change to `archive/`

## Total: 21 tasks across 9 phases

Estimated effort: ~2 days (1 day per the 2-day rollout in the plan).