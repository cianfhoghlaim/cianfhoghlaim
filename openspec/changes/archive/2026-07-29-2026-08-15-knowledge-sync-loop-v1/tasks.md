# Tasks: 2026-08-15-knowledge-sync-loop-v1

## Phase 1: Openspec + Spec docs (3 tasks)

- [ ] **T1.1**: Create `openspec/changes/2026-08-15-knowledge-sync-loop-v1/proposal.md` (the why + what changes)
- [ ] **T1.2**: Create `openspec/changes/2026-08-15-knowledge-sync-loop-v1/tasks.md` (this file)
- [ ] **T1.3**: Create `openspec/specs/knowledge-sync-loop/spec.md` (the new capability spec with the 5 sync layer requirements + 3 feedback loop requirements)

## Phase 2: Retroactive cleanup (3 tasks)

- [ ] **T2.1**: Run the 6-file bulk sed for the `sruth/cianfhoghlaim/cocoindex_flows` refs in `cocoindex/`
  - `cocoindex_flows/knowledge_graph/multihop_search.py`
  - `cocoindex_flows/_shared/reranker.py`
  - `cocoindex_flows/_shared/repo_type_detector.py`
  - `cocoindex_flows/infrastructure/arch_doc_cache.py`
  - `cocoindex_flows/infrastructure/cocoindex_v1_conformance.py`
  - `tests_pkg_temp/_oideachais/test_canuint_alignment.py` (mark for deletion)
- [ ] **T2.2**: Run `mise run drift-audit` to verify the count drops to 0 in source files
- [ ] **T2.3**: Spot-check 3 of the 6 files to ensure the rename was correct (the canonical replacement is `pathlib.Path("cocoindex/codebase_indexing")`)

## Phase 3: mise tasks (1 task)

- [ ] **T3.1**: Add the 6 sync tasks to `mise.toml`:
  - `[tasks."sync:paths"]` — Layer 1: extended drift-audit
  - `[tasks."sync:ccc"]` — Layer 2: `bun run ccc:index` + 20th concept guide
  - `[tasks."sync:cognee"]` — Layer 3: 4 Cognee ingestion scripts
  - `[tasks."sync:skills"]` — Layer 4: lint:skills + validate_skill_references
  - `[tasks."sync:mcp"]` — Layer 5: 14 MCP health checks
  - `[tasks."sync:all"]` — Orchestrator: runs 1-5 in sequence

## Phase 4: Scripts (4 tasks)

- [ ] **T4.1**: Create `scripts/sync_openspec_to_ccc.py` (appends the 20th concept guide to `.cocoindex_code/guides.yml`)
- [ ] **T4.2**: Create `scripts/validate_skill_references.py` (validates each SKILL.md references paths that exist on disk)
- [ ] **T4.3**: Create `scripts/sync_report.py` (generates the per-layer summary at `stedding/sync-reports/`)
- [ ] **T4.4**: Modify `scripts/drift-audit.sh` (or the new `sync:paths` task) to extend the grep to include `sruth/` as a 6th pattern

## Phase 5: Cognee (3 tasks)

- [ ] **T5.1**: Create `scripts/cognee_ingest_openspec.py` (ingests `openspec/changes/**/*.md` + `openspec/specs/**/*.md` into the 2 new Cognee clusters)
- [ ] **T5.2**: Create `scripts/cognee_ingest_skills.py` (ingests `.agents/skills/**/SKILL.md` into the `agent_skills` cluster)
- [ ] **T5.3**: Verify `cognee-mcp` returns the 10 typed clusters (7 existing + 3 new)

## Phase 6: CCC (1 task)

- [ ] **T6.1**: Append the 20th concept guide `openspec-archive-search` to `.cocoindex_code/guides.yml` + run `bun run ccc:index` to refresh

## Phase 7: Dagster (2 tasks)

- [ ] **T7.1**: Create `orchestration/defs/sync_assets.py` — the `sync_health` asset with a `0 */4 * * *` cron + a sensor that fires on new `stedding/sync-reports/all-*.md` files
- [ ] **T7.2**: Wire `sync_health` into the existing `orchestration/sensors/__init__.py` (add it to the `__all__` re-exports)

## Phase 8: Marimo + Skill (3 tasks)

- [ ] **T8.1**: Create `notebooks/24_deployment_control_panel.py` — the sync health + model registry + schema + stacks dashboard
- [ ] **T8.2**: Create `.agents/skills/knowledge-sync-loop/SKILL.md` — the new skill documenting the 5 layers + 3 feedback loops
- [ ] **T8.3**: Verify `mise run lint:skills` still reports 53+ skills pass (the new skill adds 1)

## Phase 9: Smoke test integration (2 tasks)

- [ ] **T9.1**: Extend `scripts/bring-up-smoke-test.sh` with a Step 6 = `mise run sync:all`
- [ ] **T9.2**: Extend `scripts/week4-smoke-test.sh` with a Gate 6 = `mise run sync:paths` (the fast-path subset of sync:all)

## Phase 10: Documentation + openspec update (3 tasks)

- [ ] **T10.1**: Update `openspec/AGENTS.md` to add `knowledge-sync-loop` to the priority specs list
- [ ] **T10.2**: Update `openspec/ACTIVE_ROADMAP.md` to add this change to the active list
- [ ] **T10.3**: Update `.agents/skills/INDEXING_AND_COGNITION.md` to document the new sync layer (the 5th surface of the ccc + cognee stack)

## Phase 11: Final verification + archive (3 tasks)

- [ ] **T11.1**: Run `mise run biep:v3:smoke-test` + `mise run bring-up:smoke-test` to verify all gates still pass
- [ ] **T11.2**: Run `openspec validate 2026-08-15-knowledge-sync-loop-v1 --strict` and verify it passes
- [ ] **T11.3**: Run `openspec archive 2026-08-15-knowledge-sync-loop-v1 --yes` to move the change to `archive/`

## Total: 28 tasks across 11 phases

Estimated effort: ~3 days (1 day per the 3-day rollout in the plan).