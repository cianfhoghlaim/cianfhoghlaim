# Tasks: 2026-08-15-agent-definitions-sync-loop-v1

21 tasks across 7 phases, ~2 days.

## Phase 1: Openspec + Spec docs (3 tasks)

- [x] **T1.1**: Create `openspec/changes/2026-08-15-agent-definitions-sync-loop-v1/proposal.md` (the why + what changes)
- [x] **T1.2**: Create `openspec/changes/2026-08-15-agent-definitions-sync-loop-v1/tasks.md` (this file)
- [x] **T1.3**: Expand `openspec/specs/agent-definitions-sync-loop/spec.md` (the new capability spec with 8 requirements: 5 sub-layers + orchestrator + feedback loop + Dagster asset)

## Phase 2: Sync scripts (6 tasks)

- [x] **T2.1**: Create `scripts/sync/agents-drift.sh` (Layer 1: detect agent registration drift across the 188 agent files — unregistered agents + stale model refs)
- [x] **T2.2**: Create `scripts/sync/agents-ccc.sh` (Layer 2: append the 25th CCC concept guide + reindex)
- [x] **T2.3**: Create `scripts/sync/agents-cognee.sh` (Layer 3: ingest the 188 agent files into the 14th Cognee cluster `agent_definitions`)
- [x] **T2.4**: Create `scripts/sync/agents-test.sh` (Layer 4: agent registration test)
- [x] **T2.5**: Create `scripts/sync/agents-lint.sh` (Layer 5: per-subdir stats + AGENTS.md + 8 NCCA subjects)
- [x] **T2.6**: Update `scripts/sync/all.sh` to include the new sync:agents layer in the orchestrator loop

## Phase 3: Mise tasks (1 task)

- [x] **T3.1**: Add the `sync:agents` orchestrator + 5 sub-layer tasks to mise.toml (description: "Layer 10 orchestrator: runs sync:agents-drift + sync:agents-ccc + sync:agents-cognee + sync:agents-test + sync:agents-lint in sequence")

## Phase 4: Skill + CCC guide + Cognee cluster (3 tasks)

- [x] **T4.1**: Create `.agents/skills/agents-sync/SKILL.md` (documents Layer 10 + the 5 sub-layers + the agent definitions evolution feedback loop)
- [x] **T4.2**: Append the 25th concept guide `agent-fleet-search` to `.cocoindex_code/guides.yml`
- [x] **T4.3**: Create `scripts/cognee_ingest_agent_definitions.py` (ingests the 188 agent files into the 14th Cognee cluster `agent_definitions`)

## Phase 5: Dagster asset + Marimo notebook (2 tasks)

- [x] **T5.1**: Add the `agents_sync_health` asset to `orchestration/defs/sync_assets.py` (reads the latest agents report + emits metadata: file_count, agents_md_count, ncca_subject_count, agent_subdir_count)
- [x] **T5.2**: Create `notebooks/29_agents_sync_dashboard.py` (the Layer 10 marimo dashboard for the 188 agent files)

## Phase 6: Update existing surfaces (3 tasks)

- [x] **T6.1**: Update `notebooks/24_deployment_control_panel.py` (add the `agents` layer status to the 8 layer statuses → 9 layer statuses including Layer 10)
- [x] **T6.2**: Update `scripts/bring-up-smoke-test.sh` (add Step 10 = sync:agents; update the expected skill count from 60 to include agents-sync)
- [x] **T6.3**: Update `scripts/week4-smoke-test.sh` (add Gate 10 = sync:agents)

## Phase 7: Final verification + archive (3 tasks)

- [x] **T7.1**: Run `mise run agents:smoke` + `bash scripts/bring-up-smoke-test.sh` + `bash scripts/week4-smoke-test.sh` to verify all 3 smoke tests pass
- [x] **T7.2**: Run `openspec validate 2026-08-15-agent-definitions-sync-loop-v1 --strict` and verify it passes
- [x] **T7.3**: Run `openspec archive 2026-08-15-agent-definitions-sync-loop-v1 --yes` to move the change to `archive/`

## Total: 21 tasks across 7 phases

Estimated effort: ~2 days (per the 2-day rollout in the plan).