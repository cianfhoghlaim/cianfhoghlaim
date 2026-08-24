# Tasks: 2026-08-24-wave-8-final-cleanup

## Phase 1: Openspec change skeleton (3 tasks)

- [x] **T1.1**: Create `openspec/changes/2026-08-24-wave-8-final-cleanup/proposal.md`
- [x] **T1.2**: Create `openspec/changes/2026-08-24-wave-8-final-cleanup/tasks.md` (this file)
- [x] **T1.3**: Create `openspec/changes/2026-08-24-wave-8-final-cleanup/specs/final-cleanup/spec.md`

## Phase 2: Master plan update (2 tasks)

- [x] **T2.1**: Update `openspec/plans/2026-08-24-master-refactor-plan.md` §1.4 — change "The 7-wave waterfall" to "The 8-wave waterfall"
- [x] **T2.2**: Add Wave 7 + Wave 8 to the waterfall diagram + post-cascade status

## Phase 3: Audit + commit (4 tasks)

- [x] **T3.1**: Run `mise run lint:drift-docs` — exits 0 (zero drift)
- [x] **T3.2**: Capture the 8-wave commit log (`git log --oneline -8`)
- [x] **T3.3**: Stage + commit the Wave 8 openspec change + master plan update
- [x] **T3.4**: Create the `v2026.08.24-wave8-cascade-complete` git tag

## Phase 4: Push + tag (2 tasks)

- [ ] **T4.1**: Push the Wave 8 commit
- [ ] **T4.2**: Push the tag

## Total: 11 tasks across 4 phases

Estimated effort: ~1 week (per the master plan's Wave 8 estimate).
This PR completes the 8-wave cascade.
