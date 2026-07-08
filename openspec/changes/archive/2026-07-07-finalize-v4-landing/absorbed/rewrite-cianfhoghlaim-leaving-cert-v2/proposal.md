# rewrite-cianfhoghlaim-leaving-cert-v2 — Cianfhoghlaim MMO (Brown Ajah + accurate British Isles map)

## Why

Cianfhoghlaim has accumulated a sprawling set of web front-end experiments at `stedding/old/` (the tanstack-unified + web-unified /api-unified /data-unified /cloudflare-unified baselines) and at `cianfhoghlaim/web/apps/oideachais-web/` (the current production TanStack Start + Hono + oRPC + Convex + CopilotKit baseline serving 7 Leaving Cert subjects for the 2026 exam window).

The current production app has 6 limitations that make it unsuitable as the long-term canonical front-end for the platform's NCCA-focused educational product:

1. **Subject coverage gap.** Only the 7 LC exam-window subjects (mathematics, irish, biology, french, history, business, construction-studies) are scaffolded. The 8-subject rosetta from `cianfhoghlaim-educational-mmo-v1` (adds applied_mathematics + computer_science) cannot reuse the route group, the `LeavingCertLayout.tsx` 8-section shell, or the per-subject API surface.
2. **No diagram layer.** The existing UI is built for static dashboards. There is no React Flow / Sigma.js / Cytoscape / D3 / Babylon.js integration, no concept-map renderer, no PCLM marking-flow diagram, no question-topic-paper-year heatmap, no 3D viewer for `s3://cianfhoghlaim-asset-v2/3d/`. The retro-educational-game-asset-pipeline-v1 plan produces these assets but has no front-end to consume them.
3. **Auth is unimplemented.** The Sidebar advertises a "Sign In" button that does nothing. The `convex/schema.ts` has all 5 tables (subject_sessions / practice_attempts / annotations / classmate_shares / extraction_budget) but no auth produces `user_id`. BetterAuth is not wired. Pocket ID OIDC is not wired. SIWE is not wired.
4. **Convex drift.** The Convex schema lives at the oideachais-web monorepo root (`/convex/`) while the new app would live under `/apps/web/` — a future migration would touch all five tables. The cross-workspace Convex instance also collides with the croilar-portal Convex deployment.
5. **The CopilotKit runtime is a stub.** `apps/api/src/copilotkit/agui_stream.ts` returns a single SSE event (`{type:"text",content:"…"}`) and never yields tool_call/tool_result events. The 6 LC CopilotKit actions in `leaving-cert-actions.ts` call `/api/leaving-cert/{subject}/*` endpoints that don't exist (the API server has no per-subject router). The OideachasChat component is a hand-rolled chat panel — not CopilotKit v2's `<CopilotChat>` or `<CopilotSidebar>` component.
6. **No Brown Ajah theming.** The Wheel of Time theming (the Brown Ajah of healers and scholars, working with Earth) — which is the platform's explicit user-facing lore per the root README — has no implementation surface in the existing app. The lineage clippings at `cian_mac_an_déisigh_uí_liatháin/identity/lineage/references/clippings/` (Tuatha Dé Danann + Cian + Aos Sí + Uí Liatháin + Déisi + Delbhna Tír Dhá Locha + Leath Cuinn and Leath Moga) — which ground the platform's etymology in Irish mythology + the operator's triple-crown lineage (Deacy + Lyons + Morris + Conroy) — have no implementation surface either.

A from-scratch rewrite addresses all 6 limitations in a single atomic openspec change, with the existing `oideachais-web` retired as a prototype (per the user's explicit instruction).

## What

A single openspec change with 6 deliverables + 12 implementation phases:

### D1. New capability spec `cianfhoghlaim-leaving-cert-portal`

`openspec/specs/cianfhoghlaim-leaving-cert-portal/spec.md` (NEW spec) + the delta at `openspec/changes/rewrite-cianfhoghlaim-leaving-cert-v2/specs/cianfhoghlaim-leaving-cert-portal/spec.md`.

The new spec covers 10 Requirements × ≥1 Scenario each:

| # | Requirement |
|--:|:--|
| R1 | **8 NCCA LC subjects × EN+GA** — full coverage including Mathematics / Applied Mathematics / Chemistry / Geography / History / English / Gaeilge / Computer Science; 7-subject LC exam-window compat for mathematics / irish / biology / french / history / business / construction-studies |
| R2 | **6-section per-subject shell** (Syllabus / Past Exams / Marking Schemes / Prioritisation / Exam Tips / PDF Library) replacing the 8-section `LeavingCertLayout.tsx` |
| R3 | **Syllabus + Exam Diagram Generator** — 4 diagram modes (concept-map, topic-frequency heatmap, PCLM marking flow, question-paper-topic Sankey) |
| R4 | **2D + 3D Asset Gallery (Hades dual-mode)** — 3D meshes via TRELLIS.2 + SAM-3D-Objects + 2D sprite atlases shipped to `s3://cianfhoghlaim-asset-v2/{3d,2d}/{subject}/` |
| R5 | **CopilotKit v2 Factory Mode + AG-UI** — `<CopilotSidebar>` mounted in the root layout; 8 NCCA subject specialists + 6 leaving-cert CopilotKit actions + 4 diagram actions + 2 3D-asset actions |
| R6 | **BetterAuth + Pocket ID OIDC + optional SIWE** — Convex `conic-leaving-cert` deployment with 5 carried-over tables (subject_sessions / practice_attempts / annotations / classmate_shares / extraction_budget) + 3 new tables (skill_assets / diagram_cache / badge_ledger) |
| R7 | **Accurate British Isles map + 6 subnations** — Éire (Ireland, v1 active) + Northern Ireland + Scotland + England + Wales + Isle of Man; 5 NCCA Key Competencies as 5 land-marks; Wales flies the Dragon Banner |
| R8 | **Brown Ajah theming + Amyrlin Seat orchestrator** — Wheel of Time theming per the 4 WoT references (Aes Sedai / Amyrlin Seat / Dragon Reborn / Tuatha'an); Cian of the Tuatha Dé Danann (Cian Mac an Déisigh Uí Liatháin) lore documented in `docs/CIANFHLOGHLAIM_LORE.md` only — NEVER on the public surface |
| R9 | **Celtic UI Design System** — 4 product UIs (MotherDuck 3-panel + PostHog Lemon UI + Duolingo streak flame + Khan Academy mastery) + 4 game UIs (Hades diegetic + Clair Obscur material library + WoW semantic icons + BitCraft Empire Panel); 12 reusable `<Ci*>` components |
| R10 | **Cianfhoghlaim OS PostHog-style window manager** — Framer Motion physics; celtic-art window chrome; URL reflects the active window |

### D2. New capability spec `retro-game-asset-pipeline`

`openspec/specs/retro-game-asset-pipeline/spec.md` (NEW spec) + the delta at `openspec/changes/rewrite-cianfhoghlaim-leaving-cert-v2/specs/retro-game-asset-pipeline/spec.md`.

The new spec covers 6 Requirements — re-publish of `retro-game-design-catalogue` integrated with the new app's Diagram Generator + 3D Asset Gallery, theming conditioned on NCCA LOs + bilingual EN+GA.

### D3. New capability spec `ncca-leaving-cert-root-pdfs`

`openspec/specs/ncca-leaving-cert-root-pdfs/spec.md` (NEW spec) + the delta at `openspec/changes/rewrite-cianfhoghlaim-leaving-cert-v2/specs/ncca-leaving-cert-root-pdfs/spec.md`.

The new spec covers 6 Requirements — captures the 5 NCCA root-level programme PDFs at `cianfhoghlaim/leaving_certificate/*.pdf` (key-competencies-in-senior-cycle + the-potential-of-online-learning-environments + the-potential-of-technology-to-support-online-certification-and-reporting + scr-advisory-report + SC-L1-L2-Programme-Statement) as a first-class asset.

### D4. Spec delta to `cianfhoghlaim-educational-mmo`

`openspec/changes/rewrite-cianfhoghlaim-leaving-cert-v2/specs/cianfhoghlaim-educational-mmo/spec.md` — ADDED Requirement (R10):
> **R10 · Cian of the Tuatha Dé Danann Lore** — the platform's lore document (in `docs/CIANFHLOGHLAIM_LORE.md`) identifies the hero as **Cian Mac an Déisigh Uí Liatháin** of the triple-crown lineage (Deacy Uí Dhéisigh + Lyons Mac Liatháin + Morris City of Tribes + Conroy Mac Conraoi). The lore is referenced from the Brown Ajah theming but NEVER displayed on the public surface.

### D5. Spec delta to `agentic-frontend-frameworks`

`openspec/changes/rewrite-cianfhoghlaim-leaving-cert-v2/specs/agentic-frontend-frameworks/spec.md` — ADDED Requirements (R6, R7):
> **R6 · Celtic UI Design System** — 4 product UIs + 4 game UIs + 12 reusable components; 145 comic reference images from `docs/comics/` as the celtic-art reference library for the FIBO asset generator
> **R7 · Brown Ajah theming + accurate British Isles map** — Brown Ajah / Amyrlin Seat / Dragon Reborn / Dragon Banner / Tuatha'an; accurate British Isles map (OpenStreetMap base) split into 6 subnations

### D6. New scripts (Bun)

- `scripts/sync-leaving-cert-r2.ts` — daily sync of `leaving_certificate/{subject}/{en,ga}/*.pdf` to `s3://cianfhoghlaim-leaving-cert/syllabus/`, `s3://cianfhoghlaim-leaving-cert/exam-papers/`, `s3://cianfhoghlaim-leaving-cert/marking-schemes/`
- `scripts/seed-diagram-cache.ts` — one-shot pre-render of all 4 diagram modes × 8 subjects × EN/GA (for `?cache=true` page-load fast path)

## Impact

### Affected specs (NEW)

- `cianfhoghlaim-leaving-cert-portal` (NEW) — the bilingual study portal
- `retro-game-asset-pipeline` (NEW) — extends `retro-game-design-catalogue` with Diagram Generator + 3D Asset Gallery
- `ncca-leaving-cert-root-pdfs` (NEW) — captures the 5 NCCA root-level programme PDFs as first-class assets

### Affected specs (MODIFIED)

- `cianfhoghlaim-educational-mmo` — ADDED R10 (Cian of the Tuatha Dé Danann lore)
- `agentic-frontend-frameworks` — ADDED R6 (Celtic UI Design System) + R7 (Brown Ajah theming + accurate British Isles map)

### New workspace at `cianfhoghlaim/web/apps/cianfhoghlaim-leaving-cert/`

The new app has the following structure (Bun + turbo workspace):

```
cianfhoghlaim/web/apps/cianfhoghlaim-leaving-cert/
├── apps/
│   ├── web/                           ← TanStack Start front-end (port 3082)
│   │   ├── src/
│   │   │   ├── routes/
│   │   │   │   ├── __root.tsx        ← CopilotKit + CopilotSidebar + Cianfhoghlaim OS
│   │   │   │   ├── (en)/             ← Bilingual EN group
│   │   │   │   │   ├── key-competencies.tsx
│   │   │   │   │   ├── leaving-cert/{$subject,practice,papers,assets}.tsx
│   │   │   │   │   └── map.tsx        ← The accurate British Isles map
│   │   │   │   └── (ga)/             ← Bilingual GA group (mirror)
│   │   │   ├── components/
│   │   │   │   ├── leaving-cert/{SubjectLayout,DiagramCanvas,RetroAssetGallery,ConceptMapDiagram,TopicHeatmapDiagram,PCLMFlowDiagram,QuestionSankeyDiagram,LessonPlayer}.tsx
│   │   │   │   ├── ui/{CiButton,CiProgressRing,CiDetailCell,CiSemanticPill,CiStreakFlame,CiBoonsChoice,CiSkillTree,CiDiegeticPanel,CiMapZone,CiWindow,CiFocusMode,CiTextbookPanel}.tsx
│   │   │   │   ├── map/{CiRealmMap,CiSubnationRegion,CiLandmark,CiSubnationFlag}.tsx
│   │   │   │   ├── lore/{CiCianHeader,CiBrownAjahBadge,CiAmyrlinSeat,CiTuathanWagon,CiDragonBanner}.tsx
│   │   │   │   ├── Header.tsx, Sidebar.tsx, TranslationToggle.tsx, OideachasChat.tsx
│   │   │   ├── server/{_metadata,leaving-cert,workflows,diagrams,badges}.ts
│   │   │   ├── lib/{auth,auth-client,auth-server-fn,orpc,pocket-id,siwe,utils}.ts
│   │   │   ├── router.tsx, routeTree.gen.ts, client.tsx, ssr.tsx, app.css
│   │   ├── app.config.ts, vite.config.ts, package.json, tsconfig.json
│   └── api/                          ← Hono + oRPC + CopilotKit runtime
│       ├── src/
│       │   ├── index.ts              ← Hono root, /api/copilotkit + /rpc/* + /api-reference/* + /api/auth/*
│       │   ├── copilotkit/{runtime,agui_stream,stage_router,subject_router}.ts
│       │   ├── routers/{leaving-cert,diagrams,assets,practice,badges,geospatial,baml,root_pdfs,key_competencies,aistear,primary,junior_cycle,senior_cycle,tertiary,i18n}.ts
│       │   └── lib/{auth,pocket-id,siwe,dagster}.ts
├── packages/
│   ├── api/                          ← Shared oRPC router + ServerFn
│   ├── auth/                         ← BetterAuth + Pocket ID shared
│   ├── ui/                           ← @cianfhoghlaim/ui + diagram/retro primitives
│   ├── db/                           ← Drizzle + D1 schema
│   ├── config/                       ← tsconfig + biome + tailwind preset
│   ├── i18n/                         ← Bilingual string tables EN/GA
│   └── convex/                       ← Cross-workspace Convex
│       └── schema.ts                 ← 5 carried-over + 3 new tables
├── docs/
│   ├── CIANFHLOGHLAIM_LORE.md        ← The lore (private; operator-only)
│   ├── BROWN_AJAH_THEMING.md         ← The theming guide
│   ├── CIANFHLOGHLAIM_DESIGN_TOKENS.css
│   └── ui-inspiration/CIANFHLOGHLAIM_DESIGN_TOKENS.css
├── wrangler.toml, turbo.json, biome.json, Dockerfile, package.json, README.md
```

### New BAML files in `cianfhoghlaim/baml/education/`

- `pdfs/root_pdf_extraction.baml` — 5 functions for the 5 NCCA root-level PDFs
- `_shared/diagram_renderer.baml` — 4 functions for the 4 diagram modes

### New CocoIndex v1 Apps in `cianfhoghlaim/cocoindex/`

- `root_pdfs_embedding.py` — embeds the 5 root-level PDFs into LanceDB
- `cross_subject_competency_embedding.py` — embeds the 5 NCCA Key Competencies × 8 subjects × 3 levels × 2 languages = 240 cross-subject mastery vectors

### New Dagster assets in `cianfhoghlaim/dagster/`

- `defs/2_materials/root_pdf_assets.py` — 5 new assets (one per root PDF)
- `defs/4_asset_generation/education_asset_assets.py` — 3D + 2D asset generation assets
- `defs/5_agent_ops/cross_subject_assets.py` — cross-subject agent assets

### New ADK agents in `cianfhoghlaim/agents/tuatha/agents/`

- `cross_subject_agent.py` — uses `ExtractKeyCompetencies` to provide cross-subject mastery reasoning

### New FIBO prompt templates in `cianfhoghlaim/tuatha/asset_generation/fibo/`

- `education_fibo.py` — 8 syllabus-conditioned FIBO prompt templates (one per subject) for celtic-art window chrome

### New marimo notebooks in `cianfhoghlaim/notebooks/`

- `root_pdfs_explorer.py` — teacher view of the 5 root PDF extractions

### New DLT source in `cianfhoghlaim/dlt/british_isles/ie/education/`

- `ncca_root_pdfs.py` — single-source DLT pipeline reading the 5 root-level PDFs

### Existing 8 sub-packages (reused as-is)

- `cianfhoghlaim/agents/tuatha/` (the 8 NCCA ADK specialists + their 40 tools)
- `cianfhoghlaim/baml/education/` (5 _shared + 5 stages + 8 qpack_*.baml + 3 pdfs + statistics + university + cross_nation)
- `cianfhoghlaim/tuatha/` (asset_generation/fibo + badges + contracts + geospatial)
- `cianfhoghlaim/dlt/` (50+ existing sources across 7 sub-dirs)
- `cianfhoghlaim/cocoindex/` (8 subject embeddings + 5 catalogue embeddings + _lifespan.py)
- `cianfhoghlaim/dagster/` (5 main buckets + 3 KCG components)
- `cianfhoghlaim/meaisinfhoghlaim/` (24-entry OCR/VLM registry + 12-agent fleet + 11 submodules)
- `cianfhoghlaim/leaving_certificate/` (133+ subject PDFs + 5 root-level NCCA programme PDFs)

### Theming inputs

- 7 lineage clippings at `cian_mac_an_déisigh_uí_liatháin/identity/lineage/references/clippings/` (Tuatha Dé Danann + Cian + Aos Sí + Uí Liatháin + Déisi + Delbhna Tír Dhá Locha + Leath Cuinn and Leath Moga)
- 145 comic reference images at `docs/comics/` (the celtic-art reference library)
- 11 UI inspiration files at `docs/ui-inspiration/` (4 product UIs + 4 game UIs + GAME_DESIGN_CATALOGUE.md + UI_INSPIRATION_GUIDE.md)
- 4 Wheel of Time excerpts (Aes Sedai / Amyrlin Seat / Dragon Reborn / Dragon Banner / Tuatha'an)

## Non-Goals

- No additional web scraping beyond the existing DLT assets
- No additional OCR/VLM model training — the 24-entry registry is final
- No new external scanning beyond the existing ROMM library
- No crypteolas / Anam / BitCraft / Tuatha MMO / Pent-Elemental Cosmology surface naming — these are explicitly DROPPED per `cianfhoghlaim-educational-mmo-v1` R2.1
- No personal identification of Cian Mac an Déisigh Uí Liatháin in the public app — the triple-crown lineage is documented in `docs/CIANFHLOGHLAIM_LORE.md` only

## Risks

1. **Convex drift** — `conic-leaving-cert` is a fresh standalone deployment; the 5 carried-over tables must be byte-for-byte identical to the legacy `oideachais-web/convex/schema.ts`. Mitigation: spec delta R6 + integration tests.
2. **Pocket ID OIDC + BetterAuth integration delay** — fall back to GitHub OAuth via BetterAuth's stock provider until Pocket ID is available.
3. **3D asset pipeline cost** (TRELLIS.2 + SAM-3D) — per-subject cap of 50 GLB/week; cache hit before re-generate.
4. **Map accuracy** — the accurate British Isles map must reflect the `leaving_certificate/geography` syllabus; the OpenStreetMap base + county-level overlay must be reviewed by a geography teacher.
5. **Brown Ajah theming review** — the 4 WoT excerpts are user-provided; the theming must remain sophisticated and not childish.
6. **Personal lineage privacy** — `docs/CIANFHLOGHLAIM_LORE.md` is operator-only; the public app must NEVER display Cian Mac an Déisigh Uí Liatháin's personal lineage.
7. **Map accuracy vs. accessibility** — WCAG 2.1 AA: the accurate map must include a text-based realm list as the accessibility fallback.

## Validation

1. `openspec validate rewrite-cianfhoghlaim-leaving-cert-v2 --strict` PASS
2. `bun run typecheck` clean for both apps/web and apps/api
3. 8 NCCA subjects × EN+GA × 6 sections render with live BAML data
4. 4 diagram modes × 8 subjects × EN/GA = 64 SVG cached in Convex `diagram_cache`
5. 3D retro asset gallery shows ≥1 GLB + ≥1 sprite atlas per subject (16+ assets total)
6. CopilotKit `<CopilotSidebar>` emits real AG-UI events (Langfuse trace verified)
7. BetterAuth + Pocket ID round-trips with `200 OK` on `/api/auth/*`
8. Accurate British Isles map renders the 6 subnations + the 5 NCCA Key Competencies land-marks + the 8 NCCA subject overlays
9. Dragon Banner flies on Wales when active
10. Éire subnation ships as the v1 active region; the other 5 subnations greyed out
11. All 70+ pre-existing tests pass + ≥40 new Vitest tests
12. Per-subject marimo notebook renders the 4-mode diagram library
13. `oideachais-web` retired as a prototype (the existing app is not migrated; it is replaced)

## Out-of-scope (deferred to v2)

- The 5 additional subnations (Northern Ireland / Scotland / England / Wales / Isle of Man) — v2-v6
- The 13 éraic treasures as the 13-tier SkillTreeBadge progression — deferred to a follow-up change after the v1 ships
- The 5 NCCA Key Competencies matrix rendered as a Grianan of Aileach ringfort header — v2
- The Samhain (1 Nov) + Beltane (1 May) seasonal events — v2
- The Babylon.js 3D client for the deferred MMO v2 — v2
- The Arthur Griffith dual-monarchy theming reference — v2 (documented in lore but not on the surface)