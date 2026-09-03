# Tasks: 2026-08-15-baml-sync-loop-v1

## Phase 1: Openspec + Spec docs (3 tasks)

- [x] **T1.1**: Create `openspec/changes/2026-08-15-baml-sync-loop-v1/proposal.md` (the why + what changes)
- [x] **T1.2**: Create `openspec/changes/2026-08-15-baml-sync-loop-v1/tasks.md` (this file)
- [x] **T1.3**: Create `openspec/specs/baml-sync-loop/spec.md` (the new capability spec with the 5-layer requirements + 3 feedback loop requirements)

## Phase 2: Sync scripts (6 tasks)

- [x] **T2.1**: Create `scripts/sync/baml-drift.sh` (Layer 1: detect reference + syntax drift in the 320 .baml files)
- [x] **T2.2**: Create `scripts/sync/baml-ccc.sh` (Layer 2: append the 22nd CCC concept guide + reindex)
- [x] **T2.3**: Create `scripts/sync/baml-cognee.sh` (Layer 3: ingest the 320 .baml files into the 11th Cognee cluster `baml_schemas`)
- [x] **T2.4**: Create `scripts/sync/baml-test.sh` (Layer 4: run `baml-cli test` on the 11 test blocks)
- [x] **T2.5**: Create `scripts/sync/baml-lint.sh` (Layer 5: BAML lint checks for client references + model drift)
- [x] **T2.6**: Update `scripts/sync/all.sh` to include the new sync:baml layer

## Phase 3: Mise tasks (1 task)

- [x] **T3.1**: Add the `sync:baml` task to mise.toml (description: "Layer 7 orchestrator: runs sync:baml-drift + sync:baml-ccc + sync:baml-cognee + sync:baml-test + sync:baml-lint in sequence")

## Phase 4: Skill + CCC guide + Cognee cluster (3 tasks)

- [x] **T4.1**: Create `.agents/skills/baml-schema-sync/SKILL.md` (documents Layer 7 + the 5 sub-layers + the BAML evolution feedback loop)
- [x] **T4.2**: Append the 22nd concept guide `baml-function-search` to `.cocoindex_code/guides.yml`
- [x] **T4.3**: Create `scripts/cognee_ingest_baml_schemas.py` (ingests the 320 .baml files into the 11th Cognee cluster `baml_schemas`)

## Phase 5: Dagster asset + Marimo notebook (2 tasks)

- [x] **T5.1**: Add the `baml_sync_health` asset to `orchestration/defs/sync_assets.py` (reads the latest baml report + emits metadata: baml_file_count, function_count, class_count, client_count, test_block_count, broken_ref_count)
- [x] **T5.2**: Create `notebooks/26_baml_sync_dashboard.py` (the Layer 7 marimo dashboard for the 320 .baml files)

## Phase 6: Update existing surfaces (3 tasks)

- [x] **T6.1**: Update `notebooks/24_deployment_control_panel.py` (add the `baml` layer status to the 7 layer statuses)
- [x] **T6.2**: Update `scripts/bring-up-smoke-test.sh` (add Step 7 = sync:baml; update the expected skill count from 56 to 57)
- [x] **T6.3**: Update `scripts/week4-smoke-test.sh` (add Gate 8 = sync:baml)

## Phase 7: Final verification + archive (3 tasks)

- [x] **T7.1**: Run `mise run biep:v3:smoke-test` + `bash scripts/bring-up-smoke-test.sh` + `bash scripts/week4-smoke-test.sh` to verify all 3 smoke tests pass
- [x] **T7.2**: Run `openspec validate 2026-08-15-baml-sync-loop-v1 --strict` and verify it passes
- [x] **T7.3**: Run `openspec archive 2026-08-15-baml-sync-loop-v1 --yes` to move the change to `archive/`

## Total: 21 tasks across 7 phases

Estimated effort: ~2 days (1 day per the 2-day rollout in the plan).