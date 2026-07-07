# Delta: cianfhoghlaim-leaving-cert-portal

## ADDED Requirements

### Requirement: 8 NCCA LC Subjects × EN+GA (R1)

The system SHALL provide per-subject landing pages for the 8 NCCA Leaving
Certificate subjects (mathematics, applied_mathematics, chemistry, geography,
history, english, gaeilge, computer_science) in both EN and GA, with the
Leaving Cert 2026 exam-window compat for 7 legacy subjects
(mathematics, irish, biology, french, history, business, construction-studies).

#### Scenario: Mathematics bilingual landing page

- **GIVEN** the user navigates to `/en/leaving-cert/mathematics` or `/ga/leaving-cert/mata`
- **WHEN** the page loads
- **THEN** the syllabus section renders ≥1 topic per `qpack_mathematics.baml` topic
- **AND** the CopilotKit sidebar mounts in the same language
- **AND** the `TranslationToggle` swaps EN↔GA labels without page reload

### Requirement: 6-section per-subject shell (R2)

The system SHALL render each per-subject landing page with exactly 6 sections,
in this order: (1) Syllabus analysis, (2) Past exam question table, (3) Marking
scheme patterns, (4) Topic prioritisation (marks ÷ study-hours), (5) Exam layout
tips, (6) PDF library (original NCCA syllabus + SEC exam papers + marking
schemes, all served as signed R2 URLs).

#### Scenario: Mathematics 6-section shell renders

- **GIVEN** the user navigates to `/en/leaving-cert/mathematics`
- **WHEN** the page loads
- **THEN** the 6 sections render in order: SyllabusAnalysis / PastExamTable / MarkingSchemePatterns / TopicPrioritisation / ExamLayoutTips / PdfLibrary
- **AND** each section has the bilingual EN+GA heading
- **AND** the PDF library shows signed R2 URLs for `s3://cianfhoghlaim-leaving-cert/syllabus/mathematics/`, `s3://cianfhoghlaim-leaving-cert/exam-papers/mathematics/`, `s3://cianfhoghlaim-leaving-cert/marking-schemes/mathematics/`

### Requirement: Syllabus + Exam Diagram Generator (R3)

The system SHALL render 4 diagram modes for each per-subject page:

1. **Concept-map** — syllabus concept-map (uses `b.ExtractSyllabusStructure` from `baml/education/pdfs/leaving_cert_syllabus_extraction.baml`)
2. **Topic-frequency heatmap** — question × paper × topic × year (D3 v8 + Vega-Lite altair fallback)
3. **PCLM marking flow** — Partial Credit, Logical Marking flowchart per marking scheme (React Flow + dagre layout)
4. **Question-paper-topic Sankey** — question → topic → difficulty → year Sankey (D3 Sankey)

The diagrams SHALL render both on page-load (pre-rendered via Dagster asset
`daily_diagram_pre_render`) and on CopilotKit request (via `generateDiagram`
CopilotKit action).

#### Scenario: Concept-map diagram renders from the 5 NCCA Key Competencies

- **GIVEN** the user navigates to `/en/leaving-cert/mathematics?window=diagram-concept-map`
- **WHEN** the diagram loads
- **THEN** the diagram renders 5 root nodes (one per NCCA Key Competency: Information Processing, Communication, Working with Others, Personal Effectiveness, Critical & Creative Thinking) + child nodes for each Mathematics LO + bilingual EN + GA labels
- **AND** the diagram is rendered from the `cross_subject_competency_embedding` CocoIndex v1 App's LanceDB output
- **AND** the `diagram_cache` Convex table has a row with `mode=concept-map, subject=mathematics, lang=en` and `rendered_at < 24h ago`

### Requirement: 2D + 3D Asset Gallery — Hades dual-mode (R4)

The system SHALL render both 3D meshes and 2D sprite atlases for each subject:
- 3D meshes via TRELLIS.2 + SAM-3D-Objects → `s3://cianfhoghlaim-asset-v2/3d/{subject}/{slug}.glb` rendered via Babylon.js + `<model-viewer>` fallback
- 2D sprite atlases via headless render of the 3D scene → `s3://cianfhoghlaim-asset-v2/2d/{subject}/{theme}.png`

The Gallery SHALL be publicly browseable at `/en/assets/{subject}` and SHALL
respect a hard perf budget: max 5 models per scene, max 4 MB GLB per asset.

#### Scenario: Mathematics asset gallery shows 3D + 2D

- **GIVEN** the user navigates to `/en/assets/mathematics`
- **WHEN** the page loads
- **THEN** the Gallery shows ≥1 GLB from `s3://cianfhoghlaim-asset-v2/3d/mathematics/` rendered in Babylon.js
- **AND** the Gallery shows ≥1 sprite atlas from `s3://cianfhoghlaim-asset-v2/2d/mathematics/` rendered as a CSS sprite
- **AND** the asset list is paginated 12 per page

### Requirement: CopilotKit v2 Factory Mode + AG-UI (R5)

The system SHALL mount a `<CopilotSidebar defaultOpen>` from
`@copilotkit/react-core/v2` at the root layout. The CopilotKit runtime URL
SHALL be `/api/copilotkit`. The 8 NCCA subject ADK specialists
(`agents/tuatha/agents/{math,appm,chem,comp,engl,gael,geog,hist}_agent.py`)
SHALL be registered as CopilotKit dispatch targets.

The CopilotKit actions SHALL include:
- 6 leaving-cert actions (per `openspec/changes/leaving-cert-2026/`): `getSyllabusTopics`, `listExamMaterials`, `getMarkingSchemeSummary`, `getTopicPrioritisation`, `getExamLayoutTips`, `openPdf`
- 4 diagram actions: `generateConceptMap`, `generateTopicHeatmap`, `generatePCLMFlow`, `generateQuestionSankey`
- 2 3D-asset actions: `generate3DAsset`, `listAssets`
- 2 cross-subject actions: `lookupKeyCompetency`, `lookupSCRCommentary`

The Hono CopilotKit runtime SHALL yield real AG-UI events
(`text` + `tool_call` + `tool_result` + `agent_handoff` + `done`), not a stub.

#### Scenario: Mathematics student asks "what topics should I revise first?"

- **GIVEN** the user opens the CopilotKit sidebar on `/en/leaving-cert/mathematics`
- **WHEN** the user types "what topics should I revise first?"
- **THEN** the orchestrator (`apps/api/src/copilotkit/stage_router.ts`) dispatches to `math_agent`
- **AND** the CopilotKit sidebar streams the AG-UI text events
- **AND** the `math_agent` calls `b.GetMathPrioritisation` (BAML) which returns the topic prioritisation
- **AND** the `useRenderTool` hook renders the prioritisation as an inline `<CiTopicPrioritisation>` component

### Requirement: BetterAuth + Pocket ID OIDC + optional SIWE (R6)

The system SHALL use BetterAuth for email/password + GitHub + Google OAuth
providers. Pocket ID OIDC SHALL be the production SSO identity provider.
SIWE SHALL be an optional wallet-sign-in (gated on `VITE_SIWE_ENABLED=true`).

The Convex deployment SHALL be the fresh standalone `conic-leaving-cert`
deployment (NOT cross-workspace with `croilar-portal`). The schema SHALL
be byte-for-byte identical to the legacy `oideachais-web/convex/schema.ts`
(5 carried-over tables: `subject_sessions`, `practice_attempts`,
`annotations`, `classmate_shares`, `extraction_budget`) PLUS 3 new tables
(`skill_assets`, `diagram_cache`, `badge_ledger`).

#### Scenario: Pocket ID sign-in round-trips

- **GIVEN** the user clicks "Sign In" in the Header
- **WHEN** the Pocket ID OAuth flow completes
- **THEN** the BetterAuth `auth.ts` instance creates a session with `user_id` derived from the Pocket ID `sub` claim
- **AND** the Convex client receives the session token
- **AND** the Convex `subject_sessions` table receives a row with `user_id` + `stage` + `subject` + `language`

### Requirement: Accurate British Isles map + 6 subnations (R7)

The system SHALL render an **accurate** map of the British Isles as the
realm map. The base layer SHALL be OpenStreetMap tiles for Ireland + Great
Britain + Isle of Man, served from Cloudflare CDN. The 6 subnations SHALL
be rendered as the 6 administrative divisions: Éire (Ireland, v1 active)
+ Northern Ireland + Scotland + England + Wales + Isle of Man.

The map SHALL overlay:
- The 5 NCCA Key Competencies as 5 land-marks (Dublin + Edinburgh + Cardiff + London + Douglas)
- The 6th Cross-Border Studies node at Belfast
- The 8 NCCA subjects as 8 overlay buttons

The Éire subnation SHALL be split into the 4 provinces (Connacht + Leinster
+ Munster + Ulster) and the 26 counties. The Connacht province SHALL be the
"home base" with the Cian lineage highlights (Delbhna Tír Dhá Locha + Lough
Corrib + Galway Bay + Moycullen).

#### Scenario: Éire subnation is the v1 active region

- **GIVEN** the user opens `/en/map`
- **WHEN** the page loads
- **THEN** the accurate British Isles map renders with all 6 subnations visible
- **AND** the Éire subnation is highlighted as the v1 active region
- **AND** the other 5 subnations are greyed out with a "Coming soon" badge
- **AND** the 5 NCCA Key Competencies are placed at their landmark cities
- **AND** the 8 NCCA subject overlays are buttons

### Requirement: Brown Ajah theming + Amyrlin Seat orchestrator (R8)

The system SHALL implement the **Brown Ajah** theming per the 4 Wheel of
Time references (Aes Sedai / Amyrlin Seat / Dragon Reborn / Tuatha'an).
The lore SHALL be documented in `docs/CIANFHLOGHLAIM_LORE.md` only —
NEVER on the public surface.

The Brown Ajah = the 8 NCCA subject specialists (healers, scholars, Earth-workers).
The Amyrlin Seat = the orchestrator agent (`root_agent.py`).
The Dragon Reborn = the student who completes the cross-subject mastery.
The Tuatha'an = the student-as-Irish-Traveller (the Cianfhoghlaim mobile client).

The Header tagline SHALL be **"Aes Sedai — servants of all"** (the Brown Ajah motto).
The Brown Ajah badge (russet brown knotwork) SHALL appear in the window chrome.

#### Scenario: Header shows Brown Ajah tagline

- **GIVEN** the user opens any page
- **WHEN** the Header renders
- **THEN** the tagline "Aes Sedai — servants of all" appears below the brand
- **AND** the Brown Ajah russet-brown knotwork badge appears in the window chrome
- **AND** the lore document `docs/CIANFHLOGHLAIM_LORE.md` references the 7 lineage clippings + the 4 WoT excerpts but is NEVER linked from the Header

### Requirement: Celtic UI Design System (R9)

The system SHALL implement the design tokens + 12 reusable `<Ci*>` components
documented in `docs/ui-inspiration/CIANFHLOGHLAIM_DESIGN_TOKENS.css`,
drawing on the 4 product UIs (MotherDuck + PostHog + Duolingo + Khan Academy)
and the 4 game UIs (Hades + Clair Obscur + WoW + BitCraft) from
`docs/ui-inspiration/UI_INSPIRATION_GUIDE.md`.

The 12 components SHALL include:
`<CiButton>` + `<CiProgressRing>` + `<CiDetailCell>` + `<CiSemanticPill>` +
`<CiStreakFlame>` + `<CiBoonsChoice>` + `<CiSkillTree>` + `<CiDiegeticPanel>` +
`<CiMapZone>` + `<CiWindow>` + `<CiFocusMode>` + `<CiTextbookPanel>`.

The 145 comic reference images at `docs/comics/` SHALL be ingested as the
celtic-art reference library for the FIBO asset generator
(`tuatha/asset_generation/fibo/education_fibo.py`).

#### Scenario: CiButton applies the tactile press feedback

- **GIVEN** the user clicks any CiButton component
- **WHEN** the click fires
- **THEN** the button's `border-bottom` compresses from `4px` to `2px` (the Duolingo 3D tactile pattern)
- **AND** the CiProgressRing fills per the Khan Academy 4-tier mastery levels (Attempted / Familiar / Proficient / Mastered)

### Requirement: Cianfhoghlaim OS PostHog-style window manager (R10)

The system SHALL implement a `<CianfhoghlaimOS>` provider that maintains a
window state machine with `{windows, activeId, dispatch}`. Each window
SHALL have `{id, component, geometry, zIndex, status}` per the
`celtic-os-product-os.md` reference.

The URL SHALL reflect the active window (`?window=syllabus-mathematics&geometry=200,200,800,600`).
The Framer Motion physics SHALL drive drag/snap with momentum. The celtic-art
window chrome SHALL use the Clair Obscur material library (parchment + slate
+ ink-wash + gold-leaf + knotwork) per the UI_INSPIRATION_GUIDE.md shared
tokens.

#### Scenario: Student opens multiple windows

- **GIVEN** the user opens `/en/leaving-cert/mathematics?window=syllabus-mathematics&geometry=200,200,800,600`
- **WHEN** the user clicks the "+" button in the header
- **AND** selects "Past exams" from the menu
- **THEN** a second window opens with `id=syllabus-mathematics-past-exams` + `geometry=1000,200,800,600`
- **AND** the Framer Motion physics animates the new window from the "+" button position
- **AND** the URL updates to `?window=syllabus-mathematics-past-exams&geometry=1000,200,800,600`

## MODIFIED Requirements

None — this is a new spec.