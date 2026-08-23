# Tasks: 2026-08-22-retire-pre-v7-oideachais-stubs-v1

## Phase 1: Openspec change skeleton (3 tasks)

- [x] **T1.1**: Create `openspec/changes/2026-08-22-retire-pre-v7-oideachais-stubs-v1/proposal.md`
- [x] **T1.2**: Create `openspec/changes/2026-08-22-retire-pre-v7-oideachais-stubs-v1/tasks.md` (this file)
- [x] **T1.3**: Create spec deltas in `specs/oideachais-{cocoindex-v1-migration,leabharlann,university-deep-extraction}/spec.md`

## Phase 2: Validate (1 task)

- [ ] **T2.1**: Run `openspec validate 2026-08-22-retire-pre-v7-oideachais-stubs-v1 --strict`

## Phase 3: Archive + commit + push (3 tasks)

- [ ] **T3.1**: Run `openspec archive 2026-08-22-retire-pre-v7-oideachais-stubs-v1 --yes`
- [ ] **T3.2**: Stage only the openspec change files + archive moves
- [ ] **T3.3**: Commit + push to `origin/token-plan-lc-pipeline-2026-08`

## Phase 4: Verification (2 tasks)

- [ ] **T4.1**: Verify `openspec list --specs` no longer contains the 3 stubs
- [ ] **T4.2**: Verify `mise run lint:drift-docs` still passes (no count drift)

## Total: 9 tasks across 4 phases

Estimated effort: ~30 minutes (the implementation is mechanical — each MODIFIED is a 1-line Requirement swap).