# Tasks: 2026-08-15-stacks-sync-loop-v1

## Phase 1: Openspec + Spec docs (3 tasks)

- [x] **T1.1**: Create `openspec/changes/2026-08-15-stacks-sync-loop-v1/proposal.md` (the why + what changes)
- [x] **T1.2**: Create `openspec/changes/2026-08-15-stacks-sync-loop-v1/tasks.md` (this file)
- [x] **T1.3**: Create `openspec/specs/stacks-sync-loop/spec.md` (the new capability spec with the 5-layer requirements + 1 feedback loop requirement)

## Phase 2: Sync scripts (6 tasks)

- [x] **T2.1**: Create `scripts/sync/stacks-drift.sh` (Layer 1: detect GOLD_STANDARD violations + name collisions)
- [x] **T2.2**: Create `scripts/sync/stacks-ccc.sh` (Layer 2: append the 23rd CCC concept guide + reindex)
- [x] **T2.3**: Create `scripts/sync/stacks-cognee.sh` (Layer 3: ingest the 87 stacks into the 12th Cognee cluster)
- [x] **T2.4**: Create `scripts/sync/stacks-validate.sh` (Layer 4: run stack-doctor.sh + parse the output)
- [x] **T2.5**: Create `scripts/sync/stacks-health.sh` (Layer 5: per-stack health report)
- [x] **T2.6**: Update `scripts/sync/all.sh` to include the new sync:stacks layer

## Phase 3: Mise tasks (1 task)

- [x] **T3.1**: Add the 6 sync:stacks tasks to mise.toml (sync:stacks-drift + sync:stacks-ccc + sync:stacks-cognee + sync:stacks-validate + sync:stacks-health + sync:stacks)

## Phase 4: Skill + CCC guide + Cognee cluster (3 tasks)

- [x] **T4.1**: Create `.agents/skills/stacks-sync/SKILL.md` (documents Layer 8 + the 5 sub-layers + the stacks evolution feedback loop)
- [x] **T4.2**: Append the 23rd concept guide `stack-catalog-search` to `.cocoindex_code/guides.yml`
- [x] **T4.3**: Create `scripts/cognee_ingest_stacks_catalog.py` (ingests the 87 stack catalog entries into the 12th Cognee cluster)

## Phase 5: Dagster asset + Marimo notebook (2 tasks)

- [x] **T5.1**: Add the `stacks_sync_health` asset to `orchestration/defs/sync_assets.py` (reads the latest stacks report + emits metadata: stack_count, gold_standard_violator_count, criticals_count)
- [x] **T5.2**: Create `notebooks/27_stacks_sync_dashboard.py` (the Layer 8 marimo dashboard for the 87 stacks)

## Phase 6: Update existing surfaces (3 tasks)

- [x] **T6.1**: Update `notebooks/24_deployment_control_panel.py` (add the `stacks` layer status to the 8 layer statuses)
- [x] **T6.2**: Update `scripts/bring-up-smoke-test.sh` (add Step 8 = sync:stacks; update the expected skill count from 57 to 58)
- [x] **T6.3**: Update `scripts/week4-smoke-test.sh` (add Gate 9 = sync:stacks)

## Phase 7: Final verification + archive (3 tasks)

- [x] **T7.1**: Run `mise run biep:v3:smoke-test` + `bash scripts/bring-up-smoke-test.sh` + `bash scripts/week4-smoke-test.sh` to verify all 3 smoke tests pass
- [x] **T7.2**: Run `openspec validate 2026-08-15-stacks-sync-loop-v1 --strict` and verify it passes
- [x] **T7.3**: Run `openspec archive 2026-08-15-stacks-sync-loop-v1 --yes` to move the change to `archive/`

## Total: 21 tasks across 7 phases

Estimated effort: ~2 days (1 day per the 2-day rollout in the plan).