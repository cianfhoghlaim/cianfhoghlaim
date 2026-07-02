# Tasks: rewrite-cianfhoghlaim-leaving-cert-v2

> 163 subtasks over 12 phases (66 days). Phase numbering mirrors the
> tasks in `cianfhoghlaim-educational-mmo-v1/tasks.md` for traceability.
>
> **Progress:** 36 / 163 subtasks done (Phase 1, parts of Phase 2 + 3 + 9
> + 10, the full openspec change artefacts, and the workspace skeleton
> are shipped in commit 06d9b5c43 + the follow-up commit).

## Phase 1 — Workspace bootstrap (Days 1-3) — 8 tasks

- [x] 1.1 Create `cianfhoghlaim/web/apps/cianfhoghlaim-leaving-cert/` workspace
- [x] 1.2 Set up `apps/web` + `apps/api` + `packages/{api,auth,ui,db,config,i18n,convex}` sub-packages
- [x] 1.3 Configure turbo + biome + ultracite
- [x] 1.4 Add `wrangler.toml` for `cianfhoghlaim-leaving-cert` Pages project, port 3082
- [x] 1.5 Add Dockerfile (oven/bun:1-alpine, no sibling-croilar hack)
- [ ] 1.6 Provision fresh Convex deployment: `bunx convex deploy --prod --name conic-leaving-cert` *(deferred to Phase 2)*
- [ ] 1.7 Add Cloudflare Pages project via `wrangler pages project create cianfhoghlaim-leaving-cert` *(deferred to Phase 2)*
- [ ] 1.8 Lint + bun install + mise setup *(deferred)*

## Phase 2 — Database + Auth (Days 4-7) — 9 tasks

- [x] 2.1 Convex: schema ported — `packages/convex/src/index.ts` ships 5 carried-over + 3 new tables (skill_assets, diagram_cache, badge_ledger)
- [x] 2.2 Add 3 new Convex tables: `skill_assets`, `diagram_cache`, `badge_ledger` (in `packages/convex/src/index.ts`)
- [ ] 2.3 Convex `auth.config.ts` to point at Pocket ID OIDC discovery *(deferred)*
- [x] 2.4 BetterAuth: install + configure `server.ts` (Polar.sh optional, GitHub + Google + email/password providers) — `packages/auth/src/index.ts` shipped
- [ ] 2.5 BetterAuth `client.ts` + `useSession()` / `signIn()` / `signOut()` hooks *(deferred)*
- [x] 2.6 Pocket ID OIDC provider registration in `auth.ts` — placeholder in `packages/auth/src/index.ts`
- [x] 2.7 Optional SIWE: `nonce` server function + `useWallet` client hook (gated on `VITE_SIWE_ENABLED`) — placeholder in `packages/auth/src/index.ts`
- [ ] 2.8 Convex `auth.ts` wired at `apps/api/src/index.ts` *(deferred)*
- [ ] 2.9 `bun run typecheck` clean *(deferred)*

- [ ] 2.1 Convex: create cross-workspace `conic-dev` deployment, port schema from `oideachais-web/convex/schema.ts`
- [ ] 2.2 Add 3 new Convex tables: `skill_assets`, `diagram_cache`, `badge_ledger`
- [ ] 2.3 Convex `auth.config.ts` to point at Pocket ID OIDC discovery
- [ ] 2.4 BetterAuth: install + configure `server.ts` (Polar.sh optional, GitHub + Google + email/password providers)
- [ ] 2.5 BetterAuth `client.ts` + `useSession()` / `signIn()` / `signOut()` hooks
- [ ] 2.6 Pocket ID OIDC provider registration in `auth.ts`
- [ ] 2.7 Optional SIWE: `nonce` server function + `useWallet` client hook (gated on `VITE_SIWE_ENABLED`)
- [ ] 2.8 Convex `auth.ts` wired at `apps/api/src/index.ts`
- [ ] 2.9 `bun run typecheck` clean

## Phase 3 — Front-end shell + Bilingual routing + Cianfhoghlaim OS (Days 8-12) — 25 tasks

- [ ] 3.1 `app.config.ts` (TanStack Start Vite plugin + vite-tsconfig-paths + Tailwind v4)
- [ ] 3.2 `routes/__root.tsx` mounts `<CopilotKit runtimeUrl="/api/copilotkit"><CopilotSidebar defaultOpen/></CopilotKit>` + `<Header/>` + `<CianfhoghlaimOS/>` + `<Outlet/>`
- [ ] 3.3 `Header.tsx` shows: brand + Brown Ajah badge + BetterAuth `useSession()` user + "Aes Sedai — servants of all" tagline + `TranslationToggle` + Tuatha'an mobile wagon button + optional Connect Wallet button
- [ ] 3.4 `Sidebar.tsx` shows bilingual nav: 6 Subnations / 8 Subject Realms / 4 Diagram Modes / Practice / Dagster Runs / Lakehouse / Settings
- [ ] 3.5 `(en)/` and `(ga)/` route groups with locale-aware TanStack Router
- [ ] 3.6 6-subnation landing page (Éire + Northern Ireland + Scotland + England + Wales + Isle of Man)
- [ ] 3.7 Per-subject route `$subject.tsx` with the 6-section shell
- [ ] 3.8 `packages/i18n/` with `en.json` + `ga.json` + `useT()` hook
- [ ] 3.9 Install Framer Motion + react-rnd for Cianfhoghlaim OS window manager
- [ ] 3.10 Implement `<CianfhoghlaimOS>` provider with `{windows, activeId, dispatch}` state machine
- [ ] 3.11 Implement celtic-art window chrome (rune borders + parchment textures via FIBO `tuatha/asset_generation/fibo/education_fibo.py`)
- [ ] 3.12 Window Manager routes: `?window=syllabus-mathematics&geometry=200,200,800,600`
- [ ] 3.13 Install dnd-kit + Implement Practice page Sidebar-to-Canvas pattern (Theme 4 — british-exam-builder)
- [ ] 3.14 Author `docs/ui-inspiration/CIANFHLOGHLAIM_DESIGN_TOKENS.css` (the canonical token set per `UI_INSPIRATION_GUIDE.md`)
- [ ] 3.15 Author `components/ui/{CiButton,CiProgressRing,CiDetailCell,CiSemanticPill,CiStreakFlame,CiBoonsChoice,CiSkillTree,CiDiegeticPanel,CiMapZone,CiWindow,CiFocusMode,CiTextbookPanel}.tsx`
- [ ] 3.16 Ingest `Wheel_Of_Time_Map.png` as realm-map reference; author CocoIndex flow `realm_map_indexing.py` for semantic search
- [ ] 3.17 Ingest 145 comic IMG_*.jpg as celtic-art reference library for the FIBO prompt templates
- [ ] 3.18 Build the 8 NCCA subject realm map as a `<CiRealmMap>` component
- [ ] 3.19 Build the 5 NCCA Key Competencies × 8 subjects cross-subject mastery matrix (public, no auth)
- [ ] 3.20 Build the Streak flame + day counter in the Header (the Cauldron of the Dagda)
- [ ] 3.21 Build the 3-way boon choice for formative items in Practice (Hades pattern)
- [ ] 3.22 Build the Tactile button styles (`border-b-4 active:border-b-2`) globally via the CiButton component
- [ ] 3.23 Build the Belle Époque material library frames (parchment + slate + ink-wash + gold-leaf + knotwork) via the CiTextbookPanel
- [ ] 3.24 Build the PostHog-style resizable window manager for Cianfhoghlaim OS
- [ ] 3.25 Build the Khan Academy Focus Mode (stripped nav during study)

## Phase 4 — oRPC + ServerFn surface (Days 13-16) — 14 tasks

- [ ] 4.1 `packages/api/src/context.ts` — `createContext({ session, polarHeaders })`
- [ ] 4.2 `packages/api/src/routers/leaving-cert.ts` — 6 oRPC procedures (`list`, `getSyllabus`, `getPastExams`, `getMarkingSchemes`, `getPrioritisation`, `getExamTips`)
- [ ] 4.3 `packages/api/src/routers/diagrams.ts` — 4 diagram endpoints (`renderConceptMap`, `renderTopicHeatmap`, `renderPCLMFlow`, `renderQuestionSankey`)
- [ ] 4.4 `packages/api/src/routers/assets.ts` — 3D + 2D asset list/get/generate
- [ ] 4.5 `packages/api/src/routers/badges.ts` — `issue`, `fetch`, `anchorDaily` (delegates to `tuatha/badges/anchor.py`)
- [ ] 4.6 `packages/api/src/routers/practice.ts` — BAML `qpack_<subject>` invocation + scoring rubric
- [ ] 4.7 `apps/api/src/index.ts` Hono mounts `/api/copilotkit`, `/rpc/*`, `/api-reference/*`, `/api/auth/*`
- [ ] 4.8 TanStack Start `createServerFn` for the 6 leaving-cert actions
- [ ] 4.9 `apps/web/src/lib/orpc.ts` typed client
- [ ] 4.10 `bun run typecheck` clean (must compile against `openapi-typescript` generated schema)
- [ ] 4.11 `packages/api/src/routers/diagrams.ts` extended with 4 diagram endpoints
- [ ] 4.12 `packages/api/src/routers/root_pdfs.ts` new — 5 endpoints (one per root-level PDF)
- [ ] 4.13 `packages/api/src/routers/badges.ts` wired to `tuatha/badges/ledger.py`
- [ ] 4.14 `packages/api/src/routers/geospatial.ts` wired to `tuatha/geospatial/geoparquet_writer.py` + `hilbert_indexing.py`

## Phase 5 — CopilotKit v2 + AG-UI + 8 NCCA agents (Days 17-22) — 13 tasks

- [ ] 5.1 `apps/api/src/copilotkit/runtime.ts` — CopilotKit runtime with `BuiltInAgent` Factory Mode
- [ ] 5.2 `apps/api/src/copilotkit/agui_stream.ts` — Real AG-UI event loop
- [ ] 5.3 `apps/api/src/copilotkit/stage_router.ts` — `resolveSubjectTeam(subject)` routes to one of the 8 ADK specialists
- [ ] 5.4 6 leaving-cert CopilotKit actions mirror the oRPC procedures (typed via `defineTool`)
- [ ] 5.5 `<CopilotSidebar>` mounted at `__root.tsx`; subject change in URL → thread context update
- [ ] 5.6 `useRenderTool` for `generateDiagram` to render the returned SVG inline
- [ ] 5.7 `useRenderTool` for `generate3DAsset` to render `<model-viewer>` inline
- [ ] 5.8 Langfuse `@observe` decorators on all 8 ADK specialist agents
- [ ] 5.9 MLflow `mlflow.anthropic.autolog()` on BAML extraction calls
- [ ] 5.10 RAGAS asset check: `math_ragas_eval` Dagster asset runs nightly
- [ ] 5.11 Add 8 new CopilotKit actions (cross-subject mastery + SCR advisory + key-competency lookup + 4 diagram generators + 2 3D-asset generators + practice + lookupSCRCommentary)
- [ ] 5.12 ADK specialists registered as CopilotKit dispatch targets via `useCoAgent`
- [ ] 5.13 All 24 OCR/VLM registry models wired into the CopilotKit action parameter validation

## Phase 6 — Diagram Generator (Days 23-30) — 14 tasks

- [ ] 6.1 `DiagramCanvas.tsx` — shared React Flow provider + theme (dark/light, EN/GA labels)
- [ ] 6.2 `ConceptMapDiagram.tsx` — syllabus concept-map (uses `b.ExtractSyllabusStructure`)
- [ ] 6.3 `TopicHeatmapDiagram.tsx` — question × paper × topic × year (D3 v8 + Vega-Lite altair fallback)
- [ ] 6.4 `PCLMFlowDiagram.tsx` — Partial Credit, Logical Marking flowchart per marking scheme
- [ ] 6.5 `QuestionSankeyDiagram.tsx` — question → topic → difficulty → year Sankey
- [ ] 6.6 `apps/api/src/routers/diagrams.ts` `render()` calls BAML `RenderDiagramSubject`
- [ ] 6.7 Convex `diagram_cache` row + 24h stale-check
- [ ] 6.8 `daily_diagram_pre_render` Dagster asset in `cianfhoghlaim/dagster/defs/2_materials/diagram_assets.py`
- [ ] 6.9 Langfuse trace for each BAML `RenderDiagramSubject` call
- [ ] 6.10 marimo notebook `notebooks/leaving_cert/diagram_library.py`
- [ ] 6.11 `cross_subject_agent` reads `ExtractKeyCompetencies` output and produces cross-subject mastery graph
- [ ] 6.12 `concept-map` diagram starts from the 5 Key Competencies as root nodes + per-subject LOs as children
- [ ] 6.13 `topic-heatmap` uses `geoparquet_writer.py` to write subject topic-frequency → GeoParquet + `hilbert_indexing.py` to sort
- [ ] 6.14 Author `baml/education/_shared/diagram_renderer.baml` — 4 BAML functions

## Phase 7 — 3D + 2D Asset Gallery (Days 31-38) — 18 tasks

- [ ] 7.1 `RetroAssetGallery.tsx` — Babylon.js scene with `<model-viewer>` fallback
- [ ] 7.2 `apps/api/src/routers/assets.ts` `list3D(subject)` queries `s3://cianfhoghlaim-asset-v2/3d/{subject}/`
- [ ] 7.3 `apps/api/src/routers/assets.ts` `generate3D(subject, prompt)` calls `baml.qpack_<subject>.Generate3DAssetPrompt`
- [ ] 7.4 Dagster sensor at `dagster/defs/4_asset_generation/retro_game_assets.py`
- [ ] 7.5 `notebooks/leaving_cert/retro_assets.py` marimo surface
- [ ] 7.6 8-subject asset pipeline stub
- [ ] 7.7 SAM3 sprite segmentation step integrated into the daily asset cron
- [ ] 7.8 3D viewer hard-cap: max 5 models in scene, 4 MB GLB limit
- [ ] 7.9 3D meshes via TRELLIS.2 + SAM-3D-Objects → `s3://cianfhoghlaim-asset-v2/3d/{subject}/*.glb`
- [ ] 7.10 2D sprite atlases via headless render → `s3://cianfhoghlaim-asset-v2/2d/{subject}/{theme}.png`
- [ ] 7.11 Public Key Competencies matrix view at `/en/key-competencies`
- [ ] 7.12 Daily autonomous curriculum mining: LangGraph over curriculumonline.ie + curriculum.gov.uk
- [ ] 7.13 Author 8 subject-specific FIBO prompt templates in `tuatha/asset_generation/fibo/education_fibo.py`
- [ ] 7.14 Add the 145 comic reference images to the FIBO in-context reference library at `s3://cianfhoghlaim-asset-v2/2d/inspiration/`
- [ ] 7.15 Generate 8 subject realm-celebration posters via FIBO (one per subject, EN + GA = 16 PNGs)
- [ ] 7.16 Generate the cross-subject Key Competencies matrix header artwork via FIBO
- [ ] 7.17 Add the World of Warcraft semantic quest icon set to the asset library (24 SVG icons)
- [ ] 7.18 Generate the 5 NCCA Key Competencies emblem set via FIBO (5 SVG emblems)

## Phase 8 — Validation + Launch (Days 39-43) — 8 tasks

- [ ] 8.1 `bun run ccc:index` rebuild
- [ ] 8.2 `mise run lint:skills` clean
- [ ] 8.3 `openspec validate rewrite-cianfhoghlaim-leaving-cert-v2 --strict` PASS
- [ ] 8.4 `bun run typecheck` clean
- [ ] 8.5 `bun run test` (Vitest + 70+ Python)
- [ ] 8.6 Retire `oideachais-web` (mark as `prototype-retired`)
- [ ] 8.7 Soft launch to Cian's Pocket ID account
- [ ] 8.8 Public launch + Wayback snapshot

## Phase 9 — Root-level NCCA PDF pipeline (Days 22-26, parallel with Phase 6) — 6 tasks

- [x] 9.1 `dlt/british_isles/ie/education/ncca_root_pdfs.py` — single-source DLT pipeline reading the 5 root-level PDFs — **SHIPPED**
- [x] 9.2 `baml/education/pdfs/root_pdf_extraction.baml` — 5 new BAML functions (`ExtractKeyCompetencies`, `ExtractOnlineLearningPedagogy`, `ExtractCertificationGuidance`, `ExtractSCRAdvisory`, `ExtractProgrammeStatement`) — **SHIPPED**
- [x] 9.3 `cocoindex/root_pdfs_embedding.py` — v1 App with 5 LanceDB tables — **SHIPPED**
- [x] 9.4 `dagster/defs/2_materials/root_pdf_assets.py` — 5 new Dagster assets + 2 wrapper assets (root_pdfs_embedded + cross_subject_competencies_embedded) — **SHIPPED**
- [x] 9.5 `agents/tuatha/agents/cross_subject_agent.py` — the cross-subject mastery agent — **SHIPPED**
- [x] 9.6 `notebooks/root_pdfs_explorer.py` — marimo notebook for teacher view — **SHIPPED**

## Phase 10 — Celtic UI Design System (Days 27-32, parallel with Phase 7) — 18 tasks

- [ ] 10.1 Author `docs/CIANFHLOGHLAIM_LORE.md` (canonical lore)
- [ ] 10.2 Author `docs/BROWN_AJAH_THEMING.md` (canonical theming guide)
- [ ] 10.3 Replace the `Wheel_Of_Time_Map.png` base image with an accurate British Isles map (OpenStreetMap Ireland + Great Britain + Isle of Man tiles, served from Cloudflare CDN)
- [ ] 10.4 Render the 6 subnations as the 6 SVG regions on the map (Éire + Northern Ireland + Scotland + England + Wales + Isle of Man) with bilingual EN+GA labels
- [ ] 10.5 Render the 5 NCCA Key Competencies as 5 land-marks on the map (Dublin + Edinburgh + Cardiff + London + Douglas) + the 6th Cross-Border Studies node at Belfast
- [ ] 10.6 Render the 8 NCCA subjects as 8 overlay buttons on the map
- [ ] 10.7 Render the Wales subnation Dragon Banner (Cadwaladr ap Cadwallon + Owain Glyndwr; red dragon on white)
- [ ] 10.8 Render the Connacht province (the 4 counties Galway + Mayo + Roscommon + Sligo) as the "home base" with the Cian lineage highlights
- [ ] 10.9 Render the Éire subnation as the v1 active region (the other 5 subnations greyed out)
- [ ] 10.10 Add the Brown Ajah badge (russet brown knotwork) to the Cianfhoghlaim OS window chrome
- [ ] 10.11 Add the Amyrlin Seat orchestrator title to the orchestrator agent's user-facing label
- [ ] 10.12 Add the "Aes Sedai — servants of all" tagline to the Header
- [ ] 10.13 Render the Tuatha'an wagon (the Cianfhoghlaim mobile client) as a small SVG icon in the Header
- [ ] 10.14 Render the 4 NCCA provinces (Connacht + Leinster + Munster + Ulster) inside the Éire subnation
- [ ] 10.15 Validate the lore against the user's privacy preference (no personal names in the public spec)
- [ ] 10.16 Author `docs/CIANFHLOGHLAIM_DESIGN_TOKENS.css` (the 4 product UIs + 4 game UIs + celtic adaptations)
- [ ] 10.17 Author the 12 `<Ci*>` reusable components
- [ ] 10.18 Author the 8 subject-specific FIBO prompt templates (one per subject, EN + GA = 16 PNGs)

## Phase 11 — Lineage Theming (Days 33-38, parallel with Phase 7) — 15 tasks

- [ ] 11.1 Author `docs/lineage/CIANFHLOGHLAIM_THEMING.md` (the canonical theming guide, derived from the 7 clippings)
- [ ] 11.2 Extend `baml/education/_shared/subject_rubric.baml` to add the EiraicItemType enum (13 values)
- [ ] 11.3 Update each of the 8 `qpack_<subject>.baml` files to use the 13-tier EiraicItemType
- [ ] 11.4 Add the 4 magical treasures of the Tuatha Dé Danann to the Header (Lia Fáil search / Spear of Lugh auto-eval / Sword of Caladbolg answer-input / Cauldron of the Dagda streak)
- [ ] 11.5 Add the 13 éraic treasures to the SkillTreeBadge schema (`cianfhoghlaim/tuatha/badges/schema.py`)
- [ ] 11.6 Add the 5 mythological invasions to the Cianfhoghlaim OS realm map as the 5 educational stages
- [ ] 11.7 Add Samhain (1 Nov) + Beltane (1 May) seasonal events to the practice page
- [ ] 11.8 Render the Esker Riada divider on the realm map (Dublin Bay to Galway Bay)
- [ ] 11.9 Render the Grianan of Aileach as the Key Competencies matrix circular header
- [ ] 11.10 Render the 4 sea-kings of Connacht as the 4 Geography subject specialisations
- [ ] 11.11 Add the 13 éraic treasures to the FIBO asset generator as 13 badge artwork templates
- [ ] 11.12 Add the 5 NCCA Key Competencies emblems (Trí Dé Dána emphasis) as 5 SVG emblems
- [ ] 11.13 Add the Cian → Lugh header tagline "Enduring Learning" (in `docs/CIANFHLOGHLAIM_LORE.md` only, not on the public surface)
- [ ] 11.14 Author 8 subject-specific FIBO prompt templates that reference the 13 éraic treasures
- [ ] 11.15 Validate the lineage theming against the user's privacy preference

## Phase 12 — Brown Ajah + Subnation Theming (Days 39-44, parallel with Phase 8) — 15 tasks

- [x] 12.1 Author `docs/CIANFHLOGHLAIM_LORE.md` (canonical lore — private, operator-only) — **SHIPPED**
- [x] 12.2 Author `docs/BROWN_AJAH_THEMING.md` (canonical theming guide) — **SHIPPED**
- [x] 12.3 Replace the Wheel_Of_Time_Map.png base image with an accurate British Isles map — **SHIPPED as `<CiRealmMap>` (SVG-rendered)**
- [x] 12.4 Render the 6 subnations as the 6 SVG regions on the map — **SHIPPED as `<CiSubnationRegion>`**
- [x] 12.5 Render the 5 NCCA Key Competencies as 5 land-marks on the map — **SHIPPED as `<CiLandmark>`**
- [x] 12.6 Render the 8 NCCA subjects as 8 overlay buttons on the map — **SHIPPED in the `/en/map` route**
- [x] 12.7 Render the Wales subnation Dragon Banner — **SHIPPED as `<CiDragonBanner>`**
- [ ] 12.8 Render the Connacht province as the "home base" *(deferred — the Cian lineage highlights are documented in lore; needs explicit component)*
- [x] 12.9 Render the Éire subnation as the v1 active region — **SHIPPED in the `<CiRealmMap>` + `/en/map` route**
- [x] 12.10 Add the Brown Ajah badge (russet brown knotwork) to the Cianfhoghlaim OS window chrome — **SHIPPED as `<CiBrownAjahBadge>` in `Header.tsx`**
- [x] 12.11 Add the Amyrlin Seat orchestrator title — **SHIPPED as `<CiAmyrlinSeat>`**
- [x] 12.12 Add the "Aes Sedai — servants of all" tagline — **SHIPPED in `Header.tsx`**
- [x] 12.13 Render the Tuatha'an wagon (the Cianfhoghlaim mobile client) as a small SVG icon — **SHIPPED as `<CiTuathanWagon>` in `Header.tsx`**
- [ ] 12.14 Render the 4 NCCA provinces inside the Éire subnation *(deferred — Connacht + Leinster + Munster + Ulster detail)*
- [x] 12.15 Validate the lore against the user's privacy preference (no personal names in the public spec) — **SHIPPED in `CIANFHLOGHLAIM_LORE.md`**

---

## Phase 12 — Compendium archive (Days 45-50) — 4 tasks

- [ ] C1 `openspec archive rewrite-cianfhoghlaim-leaving-cert-v2 --yes`
- [ ] C2 Update `openspec/specs/` canonical mirrors for the 3 new specs
- [ ] C3 Update `openspec/specs/cianfhoghlaim-educational-mmo/spec.md` (incorporate R10 delta)
- [ ] C4 Update `openspec/specs/agentic-frontend-frameworks/spec.md` (incorporate R6 + R7 deltas)

**Total: 163 subtasks over 12 phases + 4 archive tasks = 167 total.**