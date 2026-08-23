# Tasks: 2026-08-22-openspec-audit-and-merge-v1

## Phase 0 — Audit + inventory (5 tasks, ~2 hours) [DONE]

- [x] **T0.1**: Inventory all 101 capability specs (1075 total requirements)
- [x] **T0.2**: Inventory all 38 pending changes (35 at 0/N tasks, 5 in-flight)
- [x] **T0.3**: Identify the 7 pre-v7 `oideachais-*` specs that should be retired
- [x] **T0.4**: Identify the `british-isles-education-pipeline-v1/v2/v3` redundancy
- [x] **T0.5**: Identify the 3 agent/memory/observability specs with fuzzy boundaries

## Phase 1 — Spec deltas (this change, 6 tasks, ~1 hour)

- [x] **T1.1**: Write `proposal.md` (the audit findings + the merge plan)
- [x] **T1.2**: Write `tasks.md` (this file — the phased rollout)
- [x] **T1.3**: Create `specs/british-isles-education-pipeline/spec.md` (MODIFIED — adopt v3 requirements)
- [x] **T1.4**: Create `specs/agent-observability/spec.md` (MODIFIED — cross-reference to agent-platform-cluster)
- [x] **T1.5**: Create `specs/agent-platform-cluster/spec.md` (MODIFIED — cross-reference to agent-observability)
- [x] **T1.6**: Create REMOVED requirements blocks for: 7 `oideachais-*`, 2 BIEP versions

## Phase 2 — Validate (1 task, ~5 min)

- [ ] **T2.1**: Run `openspec validate 2026-08-22-openspec-audit-and-merge-v1 --strict` and verify it passes

## Phase 3 — Stage + commit + push (3 tasks, ~10 min)

- [ ] **T3.1**: Stage only the openspec change files (4 spec delta files + 2 audit files)
- [ ] **T3.2**: Commit with descriptive message + push to `origin/token-plan-lc-pipeline-2026-08`
- [ ] **T3.3**: Verify the post-archive state: `openspec list --specs` no longer contains the retired specs

## Phase 4 — Per-spec AGENTS.md regeneration (1 task, ~5 min)

- [ ] **T4.1**: Run `mise run sync:spec-agents` to regenerate per-spec AGENTS.md files (the per-spec convention)

## Phase 5 — Future work (NOT in this change) — separate openspec changes

- [ ] **T5.1** (Phase E, separate change): Triage the 34 stale pending changes; per-change CLOSE / SPLIT / KEEP decisions
- [ ] **T5.2** (Phase E, separate change): Implement the SPEC splits for the 4 oversized changes:
  - `2026-08-13-web-monorepo-consolidation-and-agent-integration-v1` (148 tasks)
  - `2026-08-13-skill-consolidation-and-extension-v1` (45 tasks)
  - `2026-08-13-guides-yml-repair-and-docs-integrations-index-v1` (46 tasks)
  - `2026-08-10-marimo-v14-cascading-effects-verification-v1` (123 tasks)
  - `2026-08-10-marimo-v14-tier3-grouped-dashboards-consolidation-v1` (107 tasks)
  - `2026-08-10-marimo-v14-ireland-england-dashboards-refactor-v1` (93 tasks)
  - `2026-08-10-baml-extraction-completion-v1` (22 tasks)
- [ ] **T5.3** (Phase E, separate change): Bulk-archive the 7 `oideachais-*` specs (move to `openspec/changes/archive/2026-08-22-.../` for historical reference)
- [ ] **T5.4** (Phase E, separate change): Implement the agent-observability ↔ agent-platform-cluster boundary clarification (separate change after this audit)

## Verification (1 task, ~5 min)

- [ ] **T6.1**: `openspec list --specs | wc -l` shows the expected count post-archive

## Total: 14 tasks across 6 phases (this change covers 9 tasks; 5 deferred to Phase E)

Estimated effort for this change: ~3 hours (mostly writing the proposal + spec deltas).

## Cross-references

- `openspec/changes/2026-08-22-openspec-audit-and-merge-v1/proposal.md` — the audit findings
- `openspec/changes/2026-08-22-openspec-audit-and-merge-v1/specs/british-isles-education-pipeline/spec.md` — the unified BIEP spec
- `openspec/changes/2026-08-22-openspec-audit-and-merge-v1/specs/agent-observability/spec.md` — observability boundary clarification
- `openspec/changes/2026-08-22-openspec-audit-and-merge-v1/specs/agent-platform-cluster/spec.md` — platform cluster boundary clarification
- `.agents/skills/openspec/SKILL.md` — the canonical openspec workflow