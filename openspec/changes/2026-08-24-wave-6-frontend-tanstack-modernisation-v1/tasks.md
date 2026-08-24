# Tasks: 2026-08-24-wave-6-frontend-tanstack-modernisation-v1

## Phase 1: Openspec change skeleton (3 tasks)

- [x] **T1.1**: Create `openspec/changes/2026-08-24-wave-6-frontend-tanstack-modernisation-v1/proposal.md`
- [x] **T1.2**: Create `openspec/changes/2026-08-24-wave-6-frontend-tanstack-modernisation-v1/tasks.md` (this file)
- [x] **T1.3**: Create `openspec/changes/2026-08-24-wave-6-frontend-tanstack-modernisation-v1/specs/frontend-tanstack-modernisation/spec.md`

## Phase 2: Modernise the 3 existing packages (3 tasks)

- [x] **T2.1**: Update `web/packages/auth/package.json` (bump `better-auth` to `^1.7.0` + add `convex` peer)
- [x] **T2.2**: Update `web/packages/db/package.json` (bump `convex` to `^1.19.0` + add `convex:dev` + `convex:deploy` scripts)
- [x] **T2.3**: Update `web/packages/ui-kit/package.json` (add Radix UI + Tailwind 4 dependencies)

## Phase 3: Create 2 new packages (4 tasks)

- [x] **T3.1**: Create `web/packages/api-client/` directory + `package.json` + `src/index.ts`
- [x] **T3.2**: Create `web/packages/api-client/src/copilotkit.ts` (HttpAgent + CIANFHOGHLAIM_RUNTIME_URL)
- [x] **T3.3**: Create `web/packages/api-client/src/tanstack.ts` (useChat, useLiveQuery, useForm hooks)
- [x] **T3.4**: Create `web/packages/api-client/src/agui.ts` (AG-UI re-exports)
- [ ] **T3.5**: Create `web/packages/contracts/` directory + `package.json` + `src/index.ts` (BIEP, jurisdiction, pipeline event schemas)

## Phase 4: Convex schema stub (1 task)

- [x] **T4.1**: Create `web/packages/db/convex/schema.ts` (Wave 6 stub; real schema lands in follow-up PR)

## Phase 5: AG-UI SSE handler (1 task)

- [x] **T5.1**: Create `web/hono-api/src/routes/agui/index.ts` (canonical SSE handler for AG-UI events)

## Phase 6: Update tuatha app (1 task)

- [x] **T6.1**: Update `web/apps/tuatha/package.json` (add `@cianfhoghlaim/{auth,db,ui-kit,api-client,contracts}` + AG-UI + CopilotKit deps)

## Phase 7: README updates (5 tasks)

- [x] **T7.1**: Write `web/packages/auth/README.md`
- [x] **T7.2**: Write `web/packages/db/README.md`
- [x] **T7.3**: Write `web/packages/ui-kit/README.md`
- [x] **T7.4**: Write `web/packages/api-client/README.md`
- [x] **T7.5**: Write `web/packages/contracts/README.md`

## Phase 8: Verification + commit (3 tasks)

- [ ] **T8.1**: All 5 package.json files parse + READMEs exist
- [ ] **T8.2**: AG-UI SSE handler stub file present at `web/hono-api/src/routes/agui/index.ts`
- [ ] **T8.3**: Commit + push

## Total: 24 tasks across 8 phases

Estimated effort: ~3 weeks (per the master plan's Wave 6 estimate).
This PR delivers the framework + 5 packages + AG-UI handler.
Subsequent PRs deliver the per-app migration + Cloudflare deployment.
