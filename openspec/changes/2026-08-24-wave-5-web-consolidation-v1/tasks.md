# Tasks: 2026-08-24-wave-5-web-consolidation-v1

## Phase 1: Openspec change skeleton (3 tasks)

- [x] **T1.1**: Create `openspec/changes/2026-08-24-wave-5-web-consolidation-v1/proposal.md`
- [x] **T1.2**: Create `openspec/changes/2026-08-24-wave-5-web-consolidation-v1/tasks.md` (this file)
- [x] **T1.3**: Create `openspec/changes/2026-08-24-wave-5-web-consolidation-v1/specs/web-consolidation/spec.md`

## Phase 2: Safe moves (executed in this PR) (4 tasks)

- [x] **T2.1**: Archive `web/apps/_oideachais_apps/` → `web/_archive/_oideachais_apps/` (552 KB)
- [x] **T2.2**: Rename `web/apps/tuatha-ui/` → `web/apps/tuatha/` (60 MB)
- [x] **T2.3**: Update `web/AGENTS.md` to document the new layout
- [x] **T2.4**: Verify `web/apps/` and `web/_archive/` look correct

## Phase 3: Deferred (NOT executed in this PR — too large) (6 tasks)

- [ ] **T3.1**: Merge `cianfhoghlaim-leaving-cert/` (2.4 GB) + `oideachais-dashboard/` (1.0 MB) → `oideachais/` (Wave 5 follow-up PR)
- [ ] **T3.2**: Merge `cianfhoghlaim-web/` (10 MB) + `cianfhoghlaim-mmo/` (55 MB) → `cianfhoghlaim/` (Wave 5 follow-up PR)
- [ ] **T3.3**: Merge `croilar-portal/` (265 MB) + `croilar-web/` (35 MB) → `croilar/` (Wave 5 follow-up PR)
- [ ] **T3.4**: Lift shared packages from sub-monorepos into root `web/packages/*` (auth, db, ui-kit, api-client, contracts)
- [ ] **T3.5**: Update `web/turbo.json` + `web/package.json` workspaces (deferred until per-app merges complete)
- [ ] **T3.6**: Wire TanStack Start + AG-UI + CopilotKit v2 (Wave 6)

## Phase 4: Verification (3 tasks)

- [ ] **T4.1**: `ls web/apps/` shows 11 canonical + 2 demo + game_showcase (12 total, was 13)
- [ ] **T4.2**: `ls web/_archive/` shows `_oideachais_apps/` (archived)
- [ ] **T4.3**: `web/AGENTS.md` documents the new layout

## Phase 5: Commit + push (2 tasks)

- [ ] **T5.1**: Stage only Wave 5 files
- [ ] **T5.2**: Commit + push

## Total: 18 tasks across 5 phases

Estimated effort: ~8 weeks (per the master plan's Wave 5 estimate).
This PR delivers the structural skeleton + safe moves (~1 day).
Subsequent PRs deliver the per-app merges (3-5 days each).
