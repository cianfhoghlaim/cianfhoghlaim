# Tasks: 2026-08-22-archive-biep-v1-v2-retirement-v1

## Phase 1: Openspec change skeleton (3 tasks)

- [x] **T1.1**: Create `openspec/changes/2026-08-22-archive-biep-v1-v2-retirement-v1/proposal.md`
- [x] **T1.2**: Create `openspec/changes/2026-08-22-archive-biep-v1-v2-retirement-v1/tasks.md` (this file)
- [x] **T1.3**: Create `specs/british-isles-education-pipeline-v2/spec.md` (REMOVED + ADDED retirement marker)

## Phase 2: Validate (1 task)

- [ ] **T2.1**: Run `openspec validate 2026-08-22-archive-biep-v1-v2-retirement-v1 --strict`

## Phase 3: Archive + commit + push (3 tasks)

- [ ] **T3.1**: Run `openspec archive 2026-08-22-archive-biep-v1-v2-retirement-v1 --yes`
- [ ] **T3.2**: Stage only the openspec change files + archive moves
- [ ] **T3.3**: Commit + push to `origin/token-plan-lc-pipeline-2026-08`

## Phase 4: Verification (2 tasks)

- [ ] **T4.1**: Verify `openspec list --specs` still contains the canonical `british-isles-education-pipeline` (v1) + `british-isles-education-pipeline-v3`
- [ ] **T4.2**: Verify `openspec list --specs` no longer contains v2 as a substantive spec (it's now a retirement marker)

## Total: 9 tasks across 4 phases

Estimated effort: ~15 minutes (single-requirement swap).