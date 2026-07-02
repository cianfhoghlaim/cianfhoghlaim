# Cianfhoghlaim Leaving Cert Portal — Implementation Status

> **Last updated:** 2026-07-02
> **Change:** [`openspec/changes/rewrite-cianfhoghlaim-leaving-cert-v2/`](../../../openspec/changes/rewrite-cianfhoghlaim-leaving-cert-v2/)
> **Validation:** `openspec validate rewrite-cianfhoghlaim-leaving-cert-v2 --strict` ✅ PASSES

---

## What's shipped (5 commits, ~80 files)

### Commit 1 — `06d9b5c43` — Scaffold
- The new workspace at `cianfhoghlaim/web/apps/cianfhoghlaim-leaving-cert/`
- `apps/web` (TanStack Start front-end) + `apps/api` (Hono + oRPC + CopilotKit)
- 7 packages: `api` + `auth` + `ui` + `convex` + `db` + `config` + `i18n`
- 2 lore docs: `CIANFHLOGHLAIM_LORE.md` (operator-only) + `BROWN_AJAH_THEMING.md`
- 1 CSS design tokens: `CIANFHLOGHLAIM_DESIGN_TOKENS.css`
- `wrangler.toml` (Cloudflare Pages, port 3082) + `Dockerfile` (oven/bun:1-alpine)
- `apps/web/src/routes/__root.tsx` mounts `<CopilotKit>` + `<CianfhoghlaimOSProvider>` + `<Header>` + `<CopilotSidebar>`
- 5 commits, 0 openspec validation failures

### Commit 2 — `7bd9c7175` — Phase 9 + 12
- **Phase 9 — Root PDFs pipeline (6/6 tasks):**
  - `dlt/british_isles/ie/education/ncca_root_pdfs.py` — DLT source for the 5 root-level PDFs
  - `baml/education/pdfs/root_pdf_extraction.baml` — 5 BAML functions
  - `baml/education/_shared/diagram_renderer.baml` — 4 BAML functions for the 4 diagram modes
  - `cocoindex/root_pdfs_embedding.py` — v1 App with 5 LanceDB tables
  - `cocoindex/cross_subject_competency_embedding.py` — v1 App with 320 cross-subject mastery vectors
  - `dagster/defs/2_materials/root_pdf_assets.py` — 7 Dagster assets
  - `agents/tuatha/agents/cross_subject_agent.py` — the cross-subject mastery ADK agent
  - `notebooks/root_pdfs_explorer.py` — marimo notebook for teacher view
- **Phase 7 — FIBO education prompt templates:**
  - `tuatha/asset_generation/fibo/education_fibo.py` — 8 subject-specific FIBO prompt templates
- **Phase 12 — Brown Ajah + Subnation Theming (12/15 tasks):**
  - 10 `Ci*` components (CiDetailCell + CiSemanticPill + CiStreakFlame + CiBoonsChoice + CiSkillTree + CiDiegeticPanel + CiMapZone + CiWindow + CiFocusMode + CiTextbookPanel)
  - 5 lore components (CiCianHeader + CiBrownAjahBadge + CiAmyrlinSeat + CiTuathanWagon + CiDragonBanner)
  - 4 map components (CiRealmMap + CiSubnationRegion + CiLandmark + CiSubnationFlag)
  - 4 diagram components (CiConceptMapDiagram + CiTopicHeatmapDiagram + CiPCLMFlowDiagram + CiQuestionSankeyDiagram)

### Commit 3 — `55fa307b5` — oRPC + GA + Dagster + Marimo
- **Phase 4 partial — 7 oRPC routers:**
  - `leaving-cert` (6 procedures) + `diagrams` (4 endpoints) + `assets` (3 endpoints)
  - `root-pdfs` (5 endpoints) + `badges` (3 endpoints) + `practice` (2 endpoints) + `i18n` (1 endpoint)
- **Phase 1 — 3 packages completed:** `db` (Drizzle) + `config` + `i18n` (EN+GA)
- **Phase 7 + 6 — 2 more Dagster assets:** `daily_diagram_pre_render` + `daily_2d_asset_generation` + `daily_3d_asset_generation`
- **Phase 3 — `(ga)` bilingual mirror route group**
- **Phase 6 — 2 marimo notebooks:** Mathematics + Gaeilge

### Commit 4 — `0724b6302` — Phase 5 + 6 + 12
- **Phase 5 partial — 14 CopilotKit actions registered:** 6 leaving-cert + 4 diagram + 2 3D-asset + 1 cross-subject + 1 SCR commentary
- **Phase 12 — Connacht province:** Lough Corrib + Galway Bay + 4 counties + Cian lineage highlights
- **Phase 6 — 6 more marimo notebooks:** Chemistry + Geography + History + English + Applied Mathematics + Computer Science

### Commit 5 — `666b36bd9` — Subject Router + Project.md
- **Phase 5 partial — `subject_router.py`:** canonical `make_subject_agent(subject)` function that lazy-imports the 8 NCCA subject ADK specialists with the Brown Ajah ↔ Tuatha Dé deity mapping
- **Phase 5 client — `tools/__init__.py`:** re-exports the math tool functions + `MATH_TOOLS` list
- **Phase 5 client — `math_syllabus_lookup.py`:** the 5 Mathematics tools (lookup_math_lo + get_math_past_papers + get_math_marking_scheme + score_math_response + generate_math_formative_item)
- **openspec/project.md — added Plan 1.5** (the Cianfhoghlaim Leaving Cert portal + the 8 NCCA ADK specialists + retro-game-asset-pipeline + ncca-leaving-cert-root-pdfs)

---

## What's deferred to the next session (~150 tasks remaining)

### Phase 2 — Database + Auth
- `bunx convex deploy --prod --name conic-leaving-cert` (provisioning)
- `wrangler pages project create cianfhoghlaim-leaving-cert` (provisioning)
- BetterAuth client.ts + useSession() / signIn() / signOut() hooks
- Convex auth.config.ts to point at Pocket ID OIDC discovery
- Convex auth.ts wired at apps/api/src/index.ts
- bun run typecheck clean

### Phase 4 — oRPC routers (8 more remaining)
- `key_competencies` (5 endpoints — the 5 NCCA Key Competencies with the cross-subject reasoning)
- The 5 stages (aistear + primary + junior_cycle + senior_cycle + tertiary) — 5 routers
- TanStack Start `createServerFn` for the 6 leaving-cert actions
- `apps/web/src/lib/orpc.ts` typed client
- `bun run typecheck` clean (openapi-typescript generation)

### Phase 5 — CopilotKit client wiring
- The 8 NCCA subject ADK specialists (the actual LlmAgent subclasses with the tools) — the subject_router.py makes_subject_agent is wired but the 8 agent.py files need to be ported from the existing 40-tool pattern
- Langfuse `@observe` decorators on all 8 ADK specialist agents
- MLflow `mlflow.anthropic.autolog()` on BAML extraction calls
- RAGAS asset check: `math_ragas_eval` Dagster asset runs nightly
- All 24 OCR/VLM registry models wired into the CopilotKit action parameter validation
- The 8 NCCA subject routes + the per-subject marimo notebook finalisation

### Phase 6 — Diagrams + Diagram library notebook
- The diagram_library marimo notebook (per T6.10)
- The actual subject cocoindex embeddings re-wired to the new `conic-leaving-cert` deployment
- The cross_subject_competency_embedding CocoIndex v1 App fully tested

### Phase 7 — 3D + 2D assets
- The actual 3D asset generation (TRELLIS.2 + SAM-3D-Objects + R2 upload)
- The actual 2D sprite atlas generation (FIBO)
- The 16 FIBO PNGs (8 subjects × EN+GA)
- The 24 SVG icons (3 per subject × 8 subjects)
- The 5 NCCA Key Competencies emblems (the Trí Dé Dána emphasis)

### Phase 8 — Validation
- Full cross-workspace Convex tests
- `bun run typecheck` clean
- `bun run test` clean (Vitest + 70+ Python)
- `mise run lint:skills` clean
- Public launch + Wayback snapshot
- `oideachais-web` retired as a prototype (per T8.6)

### Phase 10 — UI Design System finalisation
- The 12 `Ci*` components fully integrated with all the design tokens
- The 145 comic reference images at `docs/comics/` ingested as the FIBO in-context reference library
- The 5 NCCA Key Competencies emblems rendered as 5 SVG emblems

### Phase 11 — Lineage Theming finalisation
- The 13 éraic treasures added to the SkillTreeBadge schema (`cianfhoghlaim/tuatha/badges/schema.py`)
- The 4 magical treasures of the Tuatha Dé Danann added to the Header (Lia Fáil / Spear of Lugh / Sword of Caladbolg / Cauldron of the Dagda)
- Samhain (1 Nov) + Beltane (1 May) seasonal events added to the practice page

---

## Final scope (203 subtasks over 12 phases)

The 203 subtasks are tracked in `openspec/changes/rewrite-cianfhoghlaim-leaving-cert-v2/tasks.md`. The current progress is **52 / 203 tasks done (26%)** across 4 commits in this build session.

The remaining work spans:
- Database provisioning (Convex deployment + Cloudflare Pages project)
- BetterAuth client hooks (the hooks + the Pocket ID OIDC + SIWE)
- The 8 NCCA subject ADK specialists (port from the existing 40-tool pattern)
- The 3D + 2D asset generation (TRELLIS.2 + SAM-3D-Objects + FIBO)
- The actual cross-workspace Convex tests
- The post-launch Wayback snapshot

All tracked in `openspec/changes/rewrite-cianfhoghlaim-leaving-cert-v2/tasks.md` for the next session.