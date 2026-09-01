# Tasks — Cianfhoghlaim-Nua Web Consolidation Completion v1

> 5 sections, 17 tasks. All tasks PASSED before
> `openspec archive 2026-09-01-cianfhoghlaim-nua-web-consolidation-completion-v1 --yes`.

## Phase A — OpenSpec scaffolding (5 min)

- [x] **A.1** Author `proposal.md` + `tasks.md` + spec delta
- [x] **A.2** `uv run openspec validate 2026-09-01-cianfhoghlaim-nua-web-consolidation-completion-v1 --strict` exits 0

## Phase B — Author the 7 missing skeleton files (§1, 7 tasks)

- [x] **B.1** `web/apps/cianfhoghlaim-nua/routes/__root.tsx`
- [x] **B.2** `web/apps/cianfhoghlaim-nua/app.config.ts`
- [x] **B.3** `web/apps/cianfhoghlaim-nua/src/convex/schema.ts` (re-export)
- [x] **B.4** `web/apps/cianfhoghlaim-nua/src/convex/auth.ts`
- [x] **B.5** `web/apps/cianfhoghlaim-nua/src/copilot/agui-bridge.ts`
- [x] **B.6** `web/apps/cianfhoghlaim-nua/src/lib/study_plan_stub.ts`
- [x] **B.7** `web/apps/cianfhoghlaim-nua/src/components/study-plan/StudyPlanCard.tsx` (lifted from oideachais)

## Phase C — Mount the 4 Hono study-plan endpoints (§2, 1 task)

- [x] **C.1** `web/hono-api/src/index.ts` — add the 4 study-plan mounts + 1 AG-UI SSE mount

## Phase D — Archive the 5 old apps (§3, 5 tasks)

- [x] **D.1** Archive `web/apps/cianfhogltaim` → `web/apps/_archive/cianfhoghlaim-pre-v6/`
- [x] **D.2** Archive `web/apps/oideachais` → `web/apps/_archive/oideachais-pre-v6/`
- [x] **D.3** Archive `web/apps/oideachais-dashboard` → `web/apps/_archive/oideachais-dashboard-pre-v6/`
- [x] **D.4** Archive `web/apps/tuatha` → `web/apps/_archive/tuatha-pre-v6/`
- [x] **D.5** Archive `web/apps/croilar-web` → `web/apps/_archive/croilar-web-pre-v6/`

## Phase E — Update the monorepo config (§4, 1 task)

- [x] **E.1** `web/AGENTS.md` — apps table replaced with `1 active + 5 archived`

---

*Last updated by build subagent at 2026-09-01.*