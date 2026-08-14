# Tasks — Web Monorepo Consolidation + Agent Integration (Mega-Change)

## PR 1: Phase A-B (packages + tooling consolidation)

### Phase A — web/packages/ consolidation (6 → 3)

- [ ] A.1 MERGE `web/packages/analytics/`, `web/packages/i18n/`, `web/packages/ui/`, `web/packages/config/` → `web/packages/ui-kit/`
  - [ ] A.1.1 Move `analytics/index.ts` → `ui-kit/analytics/index.ts`
  - [ ] A.1.2 Move `i18n/index.ts` + `i18n/resources/` → `ui-kit/i18n/`
  - [ ] A.1.3 Move `ui/index.ts` + `ui/components/` + `ui/hooks/` → `ui-kit/components/` + `ui-kit/hooks/`
  - [ ] A.1.4 Move `config/index.ts` → `ui-kit/config/index.ts`
  - [ ] A.1.5 Create `ui-kit/index.ts` re-exporting all
  - [ ] A.1.6 Create `ui-kit/package.json` with the consolidated dependencies
- [ ] A.2 KEEP `web/packages/auth/`
- [ ] A.3 KEEP `web/packages/db/` (extended with Convex generators per Phase H)
- [ ] A.4 DELETE the 4 old `web/packages/{analytics,i18n,ui,config}/` directories

### Phase B — Monorepo tooling

- [ ] B.1 NEW `web/package.json` (bun workspaces root)
  - [ ] B.1.1 Declare `apps/*` and `packages/*` workspaces
  - [ ] B.1.2 Add root dev/build scripts
- [ ] B.2 NEW `web/turbo.json` (matches root `turbo.json`)
  - [ ] B.2.1 Mirror the root `turbo.json` pipeline
  - [ ] B.2.2 Add `web:#lint`, `web:#typecheck`, `web:#build` tasks
- [ ] B.3 NEW `web/.gitignore`
- [ ] B.4 NEW `web/tsconfig.base.json` (shared TS config)
- [ ] B.5 NEW `web/.npmrc` (workspace settings)

### Validation gates
- [ ] `bun install` (workspace sync succeeds)
- [ ] `bun run typecheck` (all 6 packages + 7 apps typecheck)
- [ ] `bun run lint` (all packages pass)
- [ ] `bun run build` (all packages build)
- [ ] `openspec validate 2026-08-13-web-monorepo-consolidation-and-agent-integration-v1 --strict`

### Commit + push
- [ ] `git add web/`
- [ ] `git commit -m "feat(web): consolidate web/packages/ 6→3 + add monorepo tooling (Phase A-B)"`
- [ ] `git push`

---

## PR 2: Phase C-J (apps consolidation + cleanup)

### Phase C — Archive stale dirs
- [ ] C.1 MOVE `web/_oideachais_apps/` → `.archive/web-historical/_oideachais_apps/`
- [ ] C.2 MOVE `web/_oideachais_apps/web/` → `web/apps/oideachais-dashboard/`
- [ ] C.3 MOVE `web/_croilar_shared/` → `.archive/web-historical/_croilar_shared/`

### Phase D — Merge 5 apps → apps/oideachais/
- [ ] D.1 MERGE `cianfhoghlaim-web` + `cianfhoghlaim-leaving-cert` + `cianfhoghlaim-mmo` + `tuatha-ui` + `tuatha-demo` → `web/apps/oideachais/`
- [ ] D.2 Update all `package.json` scripts to use the monorepo root
- [ ] D.3 Update all `vite.config.ts` (single canonical)
- [ ] D.4 Update all `tsconfig.json` (extends from base)
- [ ] D.5 Update all `tailwind.config.ts` (extends from ui-kit)

### Phase E — Merge 3 apps → apps/croilar/
- [ ] E.1 MERGE `croilar-web` + `croilar-portal` + `game_showcase` → `web/apps/croilar/`

### Phase F — Move dashboard
- [ ] F.1 MOVE `web/_oideachais_dashboard/` → `web/apps/oideachais-dashboard/`

### Phase G — Unify Hono API
- [ ] G.1 MOVE per-app CopilotKit actions → `web/hono-api/src/routes/copilotkit/`
- [ ] G.2 Update Hono routes to namespace by app

### Phase H — Unify Convex
- [ ] H.1 MERGE 3 Convex deployments → 1
- [ ] H.2 Create per-subject Convex schemas (60)

### Phase I — Unify themes
- [ ] I.1 NEW `web/packages/ui-kit/theme/tailwind.config.ts`
- [ ] I.2 NEW `web/packages/ui-kit/theme/tokens.css`
- [ ] I.3 Per-app `theme-overrides.ts`

### Phase J — Cleanup
- [ ] J.1 DELETE stale dirs
- [ ] J.2 Update `web/README.md` + `web/AGENTS.md`

### Commit + push
- [ ] `git commit -m "feat(web): consolidate 7 apps → 4 + 4 Hono → 1 + 3 Convex → 1 (Phase C-J)"`
- [ ] `git push`

---

## PR 3: Phase K-N (agent-frontend integration + new specs)

### Phase K — Agent-frontend integration
- [ ] K.1 `apps/oideachais/`: add CopilotKit + Hono + Convex + AGENTS.md
- [ ] K.2 `apps/croilar/`: add CopilotKit + Hono + Convex + AGENTS.md
- [ ] K.3 `apps/oideachais-dashboard/`: add CopilotKit + Hono + Convex + AGENTS.md

### Phase L — Image-gen agent consumer
- [ ] L.1 NEW `agents/adk/image_generation_agent.py`
- [ ] L.2 NEW `agents/adk/image_generation_handlers.py`
- [ ] L.3 NEW `agents/adk/image_generation_tools.py`
- [ ] L.4 NEW `baml_src/clients_image_gen.baml`
- [ ] L.5 NEW `cocoindex/media/image_generation_flow.py`
- [ ] L.6 MODIFY `agents/agent_registry.py:AGENT_REGISTRY`
- [ ] L.7 EXTEND `centralized-registry/SKILL.md §11`

### Phase M — Cross-links + router
- [ ] M.1 NEW `agents/WEB_INTEGRATION.md`
- [ ] M.2 MODIFY `agents/AGENTS.md` + `web/AGENTS.md` + per-app AGENTS.md

### Phase N — New openspec specs
- [ ] N.1 NEW `openspec/specs/web-monorepo-consolidation/spec.md`
- [ ] N.2 NEW `openspec/specs/image-generation-agent/spec.md`
- [ ] N.3 DELTA `openspec/specs/agent-registry/spec.md` (web-binding req)

### Commit + push
- [ ] `git commit -m "feat(agents): wire per-app CopilotKit + image-gen agent + WEB_INTEGRATION router (Phase K-N)"`
- [ ] `git push`

---

## PR 4: Phase O (schema-driven codegen pipeline)

- [ ] O.1 NEW `scripts/schema-codegen/index.ts` (orchestrator)
- [ ] O.2 NEW `scripts/schema-codegen/baml-to-ts.ts`
- [ ] O.3 NEW `scripts/schema-codegen/convex-from-zod.ts`
- [ ] O.4 NEW `scripts/schema-codegen/copilotkit-actions.ts`
- [ ] O.5 NEW `scripts/schema-codegen/ag-ui-types.ts`
- [ ] O.6 NEW `scripts/schema-codegen/per-subject-routes.ts`
- [ ] O.7 EXTEND `scripts/schema-generate.ts` (existing R30 codegen)
- [ ] O.8 NEW `mise run codegen:all` task
- [ ] O.9 NEW `.agents/skills/schema-codegen/SKILL.md`
- [ ] O.10 NEW `openspec/specs/schema-driven-codegen/spec.md`

### Commit + push
- [ ] `git commit -m "feat(codegen): BAML → Zod → Convex → CopilotKit → AG-UI pipeline (Phase O)"`
- [ ] `git push`

---

## PR 5: Phase P (per-subject end-to-end coverage, 60 subjects)

- [ ] P.1 14 LC subjects × 8 BAML functions = 112 functions
- [ ] P.2 14 LC subjects × 1 DLT source = 14 DLT sources
- [ ] P.3 14 LC subjects × 1 CocoIndex flow = 14 CocoIndex flows
- [ ] P.4 14 LC subjects × 1 Convex schema = 14 Convex schemas
- [ ] P.5 14 LC subjects × 8-13 CopilotKit actions = ~150 actions
- [ ] P.6 Repeat for 8 JC subjects (64 + 8 + 8 + 8 + ~80 = 168)
- [ ] P.7 Repeat for 9 GCSE subjects (72 + 9 + 9 + 9 + ~90 = 189)
- [ ] P.8 Repeat for 15+ A-Level subjects (120+ + 15 + 15 + 15 + ~150 = 315+)
- [ ] P.9 60 per-subject marimo notebooks
- [ ] P.10 60 per-subject AGENTS.md
- [ ] P.11 240+ per-subject routes
- [ ] P.12 NEW `openspec/specs/per-subject-coverage/spec.md`

### Commit + push
- [ ] `git commit -m "feat(data): per-subject end-to-end coverage for 60 subjects (Phase P)"`
- [ ] `git push`

---

## PR 6: Phase Q (TanStack AI + AG-UI integration)

- [ ] Q.1 NEW `web/apps/oideachais/src/lib/tanstack-ai-client.ts`
- [ ] Q.2 NEW `web/apps/oideachais/src/lib/convex-client.ts`
- [ ] Q.3 NEW `web/packages/ui-kit/chat/` (shared chat components)
- [ ] Q.4 NEW routes/api/chat/$subjectId.ts (per subject)
- [ ] Q.5 NEW routes/api/copilotkit/$subjectId.ts (per subject)
- [ ] Q.6 EXTEND `.agents/skills/agentic-frontend-frameworks/SKILL.md`
- [ ] Q.7 NEW `openspec/specs/tanstack-ai-agui-integration/spec.md`

### Commit + push
- [ ] `git commit -m "feat(web): TanStack AI + AG-UI + Convex integration (Phase Q)"`
- [ ] `git push`

---

## PR 7: Phase R (e2e verification per subject)

- [ ] R.1 NEW `tests/e2e/subjects/<subject>.test.ts` (×60)
- [ ] R.2 NEW `tests/e2e/convex/<subject>.test.ts`
- [ ] R.3 NEW `tests/e2e/copilotkit/<subject>.test.ts`
- [ ] R.4 NEW `mise run test:subjects:<subject>` task
- [ ] R.5 CI gate for e2e

### Commit + push
- [ ] `git commit -m "test(e2e): per-subject e2e verification (Phase R)"`
- [ ] `git push`

---

## PR 8: Phase S (recent pipeline integration)

- [ ] S.1 BIEP v3 orchestration → dashboard health route
- [ ] S.2 OCR/VLM ensemble → per-subject OCR route
- [ ] S.3 Knowledge graph → Convex table + dashboard route
- [ ] S.4 BAML extraction completion → schema generator source
- [ ] S.5 CopilotKit action wiring → regenerated per subject
- [ ] S.6 England BIEP pipeline → per-subject A-Level + GCSE routes
- [ ] S.7 Cascading registry integration → deployment control panel
- [ ] S.8 Lakehouse memory stack → memory-health dashboard

### Commit + push
- [ ] `git commit -m "feat(integration): 8 recent openspec changes wired in (Phase S)"`
- [ ] `git push`

---

## PR 9: Phase T (Central Cianfhoghlaim Homepage + agentic chat)

- [ ] T.1 NEW `web/apps/cianfhoghlaim/` (4th app)
- [ ] T.2 NEW `web/apps/cianfhoghlaim/routes/index.tsx` (central homepage)
- [ ] T.3 NEW `web/apps/cianfhoghlaim/routes/chat.tsx`
- [ ] T.4 NEW `web/apps/cianfhoghlaim/routes/api/chat/$threadId.ts`
- [ ] T.5 NEW `web/apps/cianfhoghlaim/src/components/AgenticChat.tsx`
- [ ] T.6 NEW `web/apps/cianfhoghlaim/src/components/PipelineStatusPanel.tsx`
- [ ] T.7 NEW `web/apps/cianfhoghlaim/src/components/SubjectGrid.tsx`
- [ ] T.8 NEW `web/apps/cianfhoghlaim/src/components/SubjectAgentCards.tsx`
- [ ] T.9 NEW `web/apps/cianfhoghlaim/src/components/KnowledgeGraphPanel.tsx`
- [ ] T.10 NEW `web/apps/cianfhoghlaim/src/components/RecentActivityFeed.tsx`
- [ ] T.11 NEW `web/apps/cianfhoghlaim/src/lib/tanstack-ai-client.ts`
- [ ] T.12 NEW `web/apps/cianfhoghlaim/src/lib/convex-client.ts`
- [ ] T.13 NEW `web/apps/cianfhoghlaim/src/lib/ducklake-query.ts`
- [ ] T.14 NEW `web/apps/cianfhoghlaim/src/lib/lancedb-search.ts`
- [ ] T.15 NEW `web/apps/cianfhoghlaim/src/lib/cognee-query.ts`
- [ ] T.16 NEW `web/apps/cianfhoghlaim/src/lib/baml-extract.ts`
- [ ] T.17 NEW `web/apps/cianfhoghlaim/src/lib/subject-detector.ts`
- [ ] T.18 NEW `web/apps/cianfhoghlaim/src/lib/agent-router.ts`
- [ ] T.19 NEW `web/apps/cianfhoghlaim/convex/schema/homepage.ts`
- [ ] T.20 NEW `web/apps/cianfhoghlaim/convex/schema/threads.ts`
- [ ] T.21 NEW `web/apps/cianfhoghlaim/convex/schema/agent_routing.ts`
- [ ] T.22 NEW `web/apps/cianfhoghlaim/AGENTS.md`
- [ ] T.23 NEW `openspec/specs/central-cianfhoghlaim-homepage/spec.md`

### Commit + push
- [ ] `git commit -m "feat(cianfhoghlaim): central homepage with agentic chat (Phase T)"`
- [ ] `git push`

---

## PR 10: Phase U (60 subject-specific agents)

- [ ] U.1 NEW `agents/adk/subjects/__init__.py`
- [ ] U.2 NEW `agents/adk/subjects/base.py` (SubjectAgentBase)
- [ ] U.3 NEW `agents/adk/subjects/_factory.py` (60-agent factory)
- [ ] U.4 NEW `agents/adk/subjects/tools/{ducklake,cocoindex,baml,convex}.py`
- [ ] U.5 NEW `agents/adk/subjects/config/{lc,jc,gcse,a-level}.json`
- [ ] U.6 NEW 60 per-subject agent files at `agents/adk/subjects/<stage>/<subject>_agent.py`
  - [ ] U.6.1 14 LC agents
  - [ ] U.6.2 8 JC agents
  - [ ] U.6.3 9 GCSE agents
  - [ ] U.6.4 15+ A-Level agents
- [ ] U.7 MODIFY `agents/agent_registry.py:AGENT_REGISTRY` (add all 60 with web_integration)
- [ ] U.8 NEW `openspec/specs/per-subject-agents/spec.md`

### Commit + push
- [ ] `git commit -m "feat(agents): 60 per-subject agents fully integrated with DuckLake + CocoIndex + BAML (Phase U)"`
- [ ] `git push`

---

## Final validation (after all 10 PRs)

- [ ] `openspec validate 2026-08-13-web-monorepo-consolidation-and-agent-integration-v1 --strict`
- [ ] `mise run lint:skills` (67 skills pass)
- [ ] `mise run lint:drift-docs` (0 violations)
- [ ] `mise run lint:guides-yml` (all 26 guides valid)
- [ ] `bun run typecheck && bun run lint && bun run build`
- [ ] `openspec archive 2026-08-13-web-monorepo-consolidation-and-agent-integration-v1 --yes`
