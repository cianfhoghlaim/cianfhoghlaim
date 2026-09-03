# Tasks: 2026-08-15-dlt-sync-loop-v1

## Phase 1: Openspec + Spec docs (3 tasks)

- [x] **T1.1**: Create openspec/changes/2026-08-15-dlt-sync-loop-v1/proposal.md
- [x] **T1.2**: Create openspec/changes/2026-08-15-dlt-sync-loop-v1/tasks.md (this file)
- [x] **T1.3**: Create openspec/specs/dlt-sync-loop/spec.md (the new capability spec)

## Phase 2: Sync scripts (6 tasks)

- [x] **T2.1**: Create scripts/sync/dlt-drift.sh (Layer 1)
- [x] **T2.2**: Create scripts/sync/dlt-ccc.sh (Layer 2)
- [x] **T2.3**: Create scripts/sync/dlt-cognee.sh (Layer 3)
- [x] **T2.4**: Create scripts/sync/dlt-test.sh (Layer 4)
- [x] **T2.5**: Create scripts/sync/dlt-lint.sh (Layer 5)
- [x] **T2.6**: Update scripts/sync/all.sh to include sync:dlt

## Phase 3: Mise tasks (1 task)

- [x] **T3.1**: Add 6 sync:dlt tasks to mise.toml

## Phase 4: Skill + CCC guide + Cognee cluster (3 tasks)

- [x] **T4.1**: Create .agents/skills/dlt-sync/SKILL.md
- [x] **T4.2**: Append 24th concept guide dlt-source-search to guides.yml
- [x] **T4.3**: Create scripts/cognee_ingest_dlt_sources.py

## Phase 5: Dagster asset + Marimo notebook (2 tasks)

- [x] **T5.1**: Add dlt_sync_health asset to orchestration/defs/sync_assets.py
- [x] **T5.2**: Create notebooks/28_dlt_sync_dashboard.py

## Phase 6: Update existing surfaces (3 tasks)

- [x] **T6.1**: Update notebooks/24_deployment_control_panel.py
- [x] **T6.2**: Update scripts/bring-up-smoke-test.sh (Step 9 = sync:dlt)
- [x] **T6.3**: Update scripts/week4-smoke-test.sh (Gate 10 = sync:dlt)

## Phase 7: Final verification + archive (3 tasks)

- [x] **T7.1**: Run all 3 smoke tests
- [x] **T7.2**: Run openspec validate
- [x] **T7.3**: Run openspec archive

## Total: 21 tasks across 7 phases
