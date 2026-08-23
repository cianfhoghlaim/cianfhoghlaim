# Tasks: 2026-08-22-stale-changes-triage-v1

## Phase 1: Openspec change skeleton (3 tasks)

- [x] **T1.1**: Create `openspec/changes/2026-08-22-stale-changes-triage-v1/proposal.md`
- [x] **T1.2**: Create `openspec/changes/2026-08-22-stale-changes-triage-v1/tasks.md` (this file)
- [x] **T1.3**: Document per-change triage decisions in the proposal (34 changes)

## Phase 2: Validate (1 task)

- [ ] **T2.1**: Run `openspec validate 2026-08-22-stale-changes-triage-v1 --strict` — should pass even without spec deltas

## Phase 3: Commit + push (3 tasks)

- [ ] **T3.1**: Stage the 2 openspec change files
- [ ] **T3.2**: Commit with descriptive message + push to `origin/token-plan-lc-pipeline-2026-08`
- [ ] **T3.3**: Verify the triage document is visible in `openspec list`

## Phase 4: Future work (NOT in this change) — separate openspec changes per group

### Group A: KEEP (12 changes)
- No action — these 12 stay in the pending list for their respective teams

### Group B: CLOSE (4 changes) — separate change
- Phase 1 of the execution plan: archive the 4 superseded changes (estimated ~30 min)

### Group C: SPLIT (7 changes) — separate changes per group
- Phase 2 of the execution plan: split each oversized change (estimated 4-6 hrs)

### Group D: TRIAGE (11 changes) — separate change
- Phase 3 of the execution plan: per-change review (estimated 2-3 hrs)

## Total: 6 tasks across 3 phases for this change

Estimated effort: ~15 minutes (this change is documentation only).

## Cross-references

- `openspec/changes/2026-08-22-stale-changes-triage-v1/proposal.md` — the per-change triage decisions
- `openspec/changes/2026-08-22-openspec-audit-and-merge-v1/proposal.md` — the audit
- `openspec/changes/2026-08-22-retire-pre-v7-oideachais-stubs-v1/` — Phase E1
- `openspec/changes/2026-08-22-archive-biep-v1-v2-retirement-v1/` — Phase E2