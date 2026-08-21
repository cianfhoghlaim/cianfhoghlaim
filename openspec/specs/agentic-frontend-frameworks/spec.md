# Agentic Frontend Frameworks Capability

## Purpose

`agentic-frontend-frameworks` is a capability of the Cianfhoghlaim
platform. The corresponding source code lives at
`cianfhoghlaim/web/` (TanStack Start front-end), `cianfhoghlaim/apps/web/` (Croilar
public persona site), `cianfhoghlaim/apps/portal/` (Croilar self-hosted
dashboard), and `cianfhoghlaim/agents/agui_*` (the AG-UI integration).
See `docs/00_index.md` for the quadrant map and `docs/00-core/CLAUDE.md`
for the project identity.

This spec was renamed from `frontend-frameworks` to disambiguate it from
the public-facing marketing site (which is the `croilar-portfolio` spec).
This spec is the *agent UI* surface — CopilotKit + AG-UI + TanStack Start
streaming + the streaming response pattern.

## Background

Full-stack React frameworks with AI agent UI components: TanStack Start
(file-based routing, server functions, server-side rendering with
streaming), CopilotKit (AI chat, multi-agent support), AG-UI (agent
streaming protocol). The full 436-line description that was here in the
old `frontend-frameworks` spec is in the skills
[`.agents/skills/{tanstack-start,copilotkit,hono,convex,react}/SKILL.md`](../../.agents/skills/).
## Requirements
### Requirement: File-based routing

The system SHALL use TanStack Start's file-based routing for the
oideachais web app and the croilar apps.

#### Scenario: Routes are auto-generated

- **GIVEN** a file `cianfhoghlaim/web/apps/web/src/routes/curriculum.tsx`
- **WHEN** the app is built
- **THEN** the route `/curriculum` is auto-generated and accessible

### Requirement: Server functions

The system SHALL use TanStack Start server functions for all data fetching
and agent calls.

#### Scenario: Type-safe server function

- **GIVEN** a server function defined on the server (e.g.
  `getCurriculum(subject: string)`)
- **WHEN** called from the client with `subject="ga101"`
- **THEN** the function executes on the server with type safety
- **AND** the result is typed end-to-end

### Requirement: Agent UI streaming

The system SHALL stream agent responses to the client using the AG-UI
protocol.

#### Scenario: AG-UI streaming

- **GIVEN** a user issues a query to a CopilotKit chat component
- **WHEN** the agent generates a response
- **THEN** the response is streamed to the client via AG-UI
- **AND** the client renders each token as it arrives

### Requirement: Agentic web front-end framework stack

The `agentic-frontend-frameworks` skill SHALL define the
canonical KCG agentic-web stack. The 7 layers, top to
bottom:

1. **Surface** — TanStack Start (React 19, file-based
   routing) or Hono (server) at the edge
2. **UI components** — shadcn/ui + Radix + Tailwind 4
   (per `.agents/skills/ui-components/`)
3. **Agent UI framework** — CopilotKit consuming the
   AG-UI SSE protocol (per `.agents/skills/copilotkit/` +
   `.agents/skills/ag-ui/`)
4. **Realtime backend** — Convex (per
   `.agents/skills/convex/`) for persona surfaces, or
   MotherDuck / DuckLake (per `.agents/skills/cianfhoghlaim-
   storage/`) for read-only surfaces
5. **API gateway** — Hono + oRPC (per
   `.agents/skills/hono/` + `.agents/skills/orpc/`)
6. **Agent backend** — Pydantic AI / Agno / Google ADK /
   BAML (4 backend options) per
   `.agents/skills/pydantic-ai/`, `.agents/skills/agno/`,
   `.agents/skills/google-adk/`, `.agents/skills/baml/`
7. **LLM gateway** — LiteLLM (per
   `.agents/skills/litellm/`) on the `bunchloch` M4 Max

The skill body at
`.agents/skills/agentic-frontend-frameworks/SKILL.md`
documents the canonical 7-layer stack; the deep-dive
references live at
`.agents/skills/agentic-frontend-frameworks/references/`.

#### Scenario: A new persona surface is added

- **GIVEN** a developer wants to add a new persona
  surface for the croilar portfolio
- **WHEN** they look at
  `.agents/skills/agentic-frontend-frameworks/SKILL.md`
  + the 5-surface map at
  `.agents/skills/frontend-topology/SKILL.md`
- **THEN** the developer sees:
  - The 7-layer stack (TanStack Start + CopilotKit + AG-UI
    + Convex + Hono + oRPC + BAML)
  - The 4 canonical surfaces (cianfhoghlaim/web, cianfhoghlaim/apps/
    web, cianfhoghlaim/apps/portal, cianfhoghlaim/ui)
  - The 4 backend options (Pydantic AI / Agno / Google
    ADK / BAML)
  - The 3 auth models (no-auth, OAuth + SIWE + 2FA,
    Pocket ID OIDC SSO)
- **AND** the developer can wire the new persona surface
  end-to-end without re-deriving the framework choices

#### Scenario: A new agent UI is added to the existing surface

- **GIVEN** the developer wants to add a chat UI to the
  cianfhoghlaim/web surface
- **WHEN** they look at the AG-UI section of
  `.agents/skills/agentic-frontend-frameworks/SKILL.md`
- **THEN** the developer sees the 17 AG-UI event types
  + the 4 event groups (Lifecycle / Message / Tool /
  State)
- **AND** the SSE streaming pattern (CopilotChat
  consumes the stream from any backend: Pydantic AI /
  Agno / Google ADK / BAML)
- **AND** the typed tool-call pattern via
  `useCopilotAction({ parameters: z.object(...) })`
- **AND** the chat can be wired end-to-end

### Requirement: 4 canonical surfaces (cross-cutting map)

The system SHALL expose exactly 4 canonical front-end
surfaces. Each surface has a fixed (stack, auth, data
plane, user) tuple. The 4 surfaces are:

| # | Surface | Stack | Auth | Data plane | User |
|:--|:--|:--|:--|:--|:--|
| 1 | `cianfhoghlaim/web` | TanStack Start + Hono | **No auth** (public lakehouse) | `cianfhoghlaim.education.ie.*` (MotherDuck) | Irish educators + students |
| 2 | `cianfhoghlaim/apps/web` | TanStack Start + Hono | **No auth** (public portfolio) | Convex (read-only) | Public visitors |
| 3 | `cianfhoghlaim/apps/portal` | TanStack Start + Hono + BetterAuth | **OAuth + SIWE + 2FA** | Convex (read-write) | The 3 personas (aleyum, cianfhoghlaim, carlcashman) |
| 4 | `cianfhoghlaim/ui` | TanStack Start + Babylon.js | **SIWE** (Ethereum wallet) | Convex (realtime) + SpacetimeDB | Tuatha game players |

The 5th surface (marimo, analyst notebook) is
documented separately at
`.agents/skills/marimo/SKILL.md`.

#### Scenario: A developer is asked to add an auth wall

- **GIVEN** the user wants to add auth to a surface
- **WHEN** the developer looks at the 4 surfaces table
- **THEN** the developer sees:
  - `cianfhoghlaim/web` and `cianfhoghlaim/apps/web` have NO auth
    (public)
  - `cianfhoghlaim/apps/portal` has BetterAuth + Pocket ID +
    SIWE
  - `cianfhoghlaim/ui` has SIWE (Ethereum wallet only)
- **AND** the developer can pick the right auth pattern
  for the target surface without re-deriving

### Requirement: hono-api path consolidation

The `hono-api` backend at `cianfhoghlaim/web/hono-api/hono-api/` SHALL be moved to `cianfhoghlaim/web/hono-api/` to dedupe the doubled path that was residue from the 2026-06-28 v4 consolidation. The hono-api SHALL continue to host the BetterAuth OIDC issuer at `/.well-known/openid-configuration`, the JWKS public keys at `/.well-known/jwks.json`, the health check at `/api/health`, and the BetterAuth handler at `/api/auth/*` (sign-in, sign-up, sign-out, etc.). The 3 OIDC audiences SHALL be `convex_backend` (Convex), `croilar_web` (croilar-web app), and `croilar_portal` (croilar-portal app).

#### Scenario: the hono-api is mounted at the consolidated path

- **GIVEN** the v4 consolidation left a doubled `web/hono-api/hono-api/` path
- **WHEN** the developer runs `bun run dev` from `web/hono-api/`
- **THEN** the Hono server starts on port 4000
- **AND** `curl http://localhost:4000/.well-known/jwks.json` returns a valid JWKS payload

### Requirement: BetterAuth client in web/packages/packages/auth/

The empty `web/packages/packages/auth/src/index.ts` (currently `export {};`) SHALL be populated with a BetterAuth client that wraps the hono-api's `auth.ts` configuration. The client SHALL use `better-auth/react` for the React-side and `better-auth/client` for the vanilla JS side. The client SHALL read `PUBLIC_AUTH_URL` from the environment (default `http://localhost:4000`) and SHALL export a typed `Auth` instance.

#### Scenario: croilar-web imports @croilar/auth

- **GIVEN** the @croilar/auth package is populated
- **WHEN** a croilar-web component does `import { auth } from "@croilar/auth"`
- **THEN** the auth instance is available
- **AND** `auth.signIn.email(...)` calls `POST /api/auth/sign-in/email` on the hono-api

### Requirement: 5th canonical front-end surface — Cianfhoghlaim OS (R5 — NEW per `rewrite-cianfhoghlaim-leaving-cert-v2`)

The system SHALL expose a 5th canonical front-end surface:
`cianfhoghlaim/web/apps/cianfhoghlaim-leaving-cert/`. The stack tuple
is: TanStack Start (Vite plugin) + file-based routing; CopilotKit v2
Factory Mode + AG-UI SSE streaming; Convex (fresh standalone
`conic-leaving-cert` deployment, NOT cross-workspace with
`croilar-portal`); Hono + oRPC + BetterAuth + Pocket ID OIDC +
optional SIWE; React Flow + D3 + Babylon.js + model-viewer; MotherDuck
(read-only lakehouse) + Convex (read-write persona); map = accurate
British Isles (OpenStreetMap base) split into 6 subnations; theming =
professional + minimal (the mythology / historical-sources layer is
deferred to BIEP-v2 per `2026-07-09-remove-brown-ajah-theming-v1`).

#### Scenario: A new spec wants to declare a 6th surface

- **GIVEN** the 5 canonical surfaces table is locked
- **WHEN** a new spec requests a 6th row
- **THEN** the developer MUST first refactor an existing surface out
- **AND** no surface count growth without consolidation

### Requirement: Celtic UI Design System (R6 — NEW per `rewrite-cianfhoghlaim-leaving-cert-v2`)

The system SHALL implement the design tokens + 12 reusable `<Ci*>`
components documented in
`docs/ui-inspiration/CIANFHLOGHLAIM_DESIGN_TOKENS.css`, drawing on
the 4 product UIs (MotherDuck 3-panel + PostHog Lemon UI + Duolingo
streak flame + Khan Academy mastery) and the 4 game UIs (Hades
diegetic + Clair Obscur material library + WoW semantic icons +
BitCraft Empire Panel) from
`docs/ui-inspiration/UI_INSPIRATION_GUIDE.md`, with the 8 Celtic
adaptations (Belle Époque Ironwork → Insular Art Knotwork; Oil Painting
→ Ink-Wash & Gold Leaf; Obsidian/Marble → Slate & Ogham Stone; Cinzel
→ Uncial/Insular Script; Hades diegetic UI → window chrome; WoW
semantic quest icons → 24 SVG icons; Khan mastery → 4-tier éraic
treasures; Duolingo streak → Cauldron of the Dagda). The 145 comic
reference images at `docs/comics/` SHALL be ingested as the celtic-art
reference library for the FIBO asset generator.

The 12 components SHALL be: `<CiButton>`, `<CiProgressRing>`,
`<CiDetailCell>`, `<CiSemanticPill>`, `<CiStreakFlame>`,
`<CiBoonsChoice>`, `<CiSkillTree>`, `<CiDiegeticPanel>`,
`<CiMapZone>`, `<CiWindow>`, `<CiFocusMode>`, `<CiTextbookPanel>`.

#### Scenario: CiButton applies the tactile press feedback

- **GIVEN** the user clicks any CiButton component
- **WHEN** the click fires
- **THEN** the button's `border-bottom` compresses from `4px` to `2px`
- **AND** the CiProgressRing fills per the Khan Academy 4-tier mastery levels

#### Scenario: CiStreakFlame is the Cauldron of the Dagda

- **GIVEN** the user opens any page
- **WHEN** the Header renders
- **THEN** the streak indicator shows the user's day count
- **AND** the indicator is themed as the Cauldron of the Dagda (never empties)
- **AND** on Beltane (1 May) the indicator resets to 100%

### Requirement: (R7 REMOVED 2026-07-09 — Brown Ajah theming)

The system SHALL render an **accurate** map of the British Isles (NOT
fictional). The Brown Ajah Wheel of Time theming (Aes Sedai / Amyrlin
Seat / Dragon Reborn / Dragon Banner / Tuatha'an + the "Aes Sedai —
servants of all" tagline) was removed per the
`2026-07-09-remove-brown-ajah-theming-v1` change. The mythology /
historical-sources theming layer is deferred to BIEP-v2 (see the
`british-isles-education-pipeline` spec). The accurate British Isles
map remains (kept below).

The 6 subnations SHALL be: Éire (Ireland, v1 active) +
Northern Ireland + Scotland + England + Wales + Isle of Man. The 5 NCCA
Key Competencies SHALL be the 5 land-marks (Dublin + Edinburgh +
Cardiff + London + Douglas) plus a 6th Belfast node (Cross-Border
Studies). The 8 NCCA subjects SHALL be the 8 overlay buttons. The
Connacht province SHALL be the "home base" with the Cian lineage
highlights (Delbhna Tír Dhá Locha + Lough Corrib + Galway Bay +
Moycullen).

#### Scenario: Accurate British Isles map renders 6 subnations

- **GIVEN** the user opens `/en/map`
- **WHEN** the page loads
- **THEN** the accurate British Isles map renders
- **AND** all 6 subnations are visible with bilingual EN+GA labels
- **AND** the Éire subnation is highlighted as the v1 active region
- **AND** the other 5 subnations are greyed out with "Coming soon" badges
- **AND** the 5 NCCA Key Competencies are placed at their landmark cities

#### Scenario: Wales subnation flies the Dragon Banner

- **GIVEN** the user hovers over the Wales subnation
- **WHEN** the hover fires
- **THEN** the Dragon Banner (red dragon on white) animates into view
- **AND** the bilingual label "Wales / an Bhreatain Bheag" appears

#### Scenario: Personal lineage never appears on the public surface

- **GIVEN** the user opens any page on `cianfhoghlaim.cianfhoghlaim.ie`
- **WHEN** the page renders
- **THEN** no text matches the regex `Ci[ae]n M[ae]c a[nm] D[ée]isi[gh]`
- **AND** no text matches the family surnames Deacy, Lyons, Morris, Conroy
- **AND** no text references the 3 Gemini Deep Research warrants

### Requirement: Per-subject Convex + TanStack interactive web surface for the 6 BIEP v1 LC subjects

The system SHALL ship a per-subject Convex + TanStack interactive web
surface for each of the 6 BIEP v1 LC subjects: Mathematics, Chemistry,
Geography, Gaeilge, English, Computer Science (per the user's locked
plan; Applied Maths + History are out of scope).

For each of the 6 subjects, the system SHALL ship:
- 5 per-subject TanStack Start route files at
  `apps/cianfhoghlaim-leaving-cert/apps/web/src/routes/en/subjects/<subject>/`
  named `index.tsx`, `syllabus.tsx`, `exam-papers.tsx`,
  `marking-schemes.tsx`, `study-plan.tsx` (30 files total).
- 6 per-subject Convex files at `convex/<subject>/` named
  `schema.ts`, `createSession.ts`, `getSession.ts`,
  `updateSession.ts`, `generateStudyPlan.ts`,
  `discussExamPaper.ts` (36 files total).
- 1 per-subject BAML backend file at
  `baml/education/web/<subject>_web.baml` exposing the functions
  `WebStudyPlan`, `WebExamPaperDiscussion`, and
  `WebMarkingSchemeExplanation` (6 files total).

Total: 30 + 36 + 6 = 72 per-subject source files.

The per-subject Convex `generateStudyPlan` action SHALL call into the
per-subject BAML `WebStudyPlan` function. The per-subject Convex
`discussExamPaper` action SHALL call into the per-subject BAML
`WebExamPaperDiscussion` function. The per-subject BAML backend files
SHALL delegate to the existing per-subject foundation at
`baml/education/subjects/qpack_<subject>.baml`.

Per-subject route trees are added alongside (not replacing) the
existing flat `apps/.../routes/en/subjects/<subject>.tsx` files so
existing book-marks resolve to the new per-subject directories.

#### Scenario: Mathematics per-subject study plan generation

- **GIVEN** the user is on `/en/subjects/mathematics/study-plan`
- **WHEN** they press "Start studying" with `weeksUntilExam=12`,
  `targetLevel="hl"`, `language="en"`
- **THEN** the `convex/mathematics/createSession.ts` mutation runs and
  returns a session id
- **AND** the `convex/mathematics/generateStudyPlan.ts` action runs
  and calls `b.WebStudyPlan(subject="mathematics", ...)`
- **AND** the `WebStudyPlan` function returns a
  `MathematicsWebStudyPlanResponse` (bilingual EN+GA) with at least 12
  weeks + 3-5 milestones
- **AND** the response is persisted to the `study_plans` table by the
  `insertStudyPlan` internal mutation
- **AND** the UI re-renders the per-subject plan in real time via the
  Convex subscription

#### Scenario: Chemistry per-subject exam paper discussion

- **GIVEN** the user is on `/en/subjects/chemistry/exam-papers`
- **WHEN** they click a past paper question for the 2024 LC Chemistry
  HL paper
- **THEN** the `convex/chemistry/discussExamPaper.ts` action runs and
  calls `b.WebExamPaperDiscussion(subject="chemistry", paper_year=2024,
  paper_level="LC_HL", paper_language="EN", question_text="...")`
- **AND** the `WebExamPaperDiscussion` function returns a
  `ChemistryWebExamPaperDiscussionResponse` with a PCLM marking-scheme
  explanation + a model answer outline + common student mistakes +
  follow-up questions
- **AND** the response is persisted to the
  `exam_paper_discussions` table

#### Scenario: Geography per-subject marking scheme explanation

- **GIVEN** the user is on `/en/subjects/geography/marking-schemes`
- **WHEN** they select the 2023 LC Geography OL paper
- **THEN** the per-subject BAML `WebMarkingSchemeExplanation` function
  (at `baml/education/web/geography_web.baml`) returns a
  `GeographyWebMarkingSchemeExplanationResponse` with sections +
  questions + PCLM patterns
- **AND** the response renders in the UI without writing to Convex
  (this function is read-only)

#### Scenario: Gaeilge per-subject bilingual handling

- **GIVEN** the user is on `/ga/subjects/gaeilge` (the Irish-language
  mirror of the Gaeilge BIEP page)
- **WHEN** they press "Start studying" with `language="ga"`
- **THEN** the per-subject Convex action accepts the Gaeilge language
  flag
- **AND** the per-subject BAML backend responds in Gaeilge
  (or bilingual EN+GA where Gaeilge is the primary)
- **AND** the `study_plans.plan_json` row is tagged `language="ga"`

#### Scenario: English per-subject session progress

- **GIVEN** the user has an active English study session
- **WHEN** they complete a syllabus topic on
  `/en/subjects/english/syllabus`
- **THEN** the `convex/english/updateSession.ts` mutation runs with
  `messageCountDelta=1`
- **AND** the session's `message_count` and `last_active_at` are
  patched in the `study_sessions` table

#### Scenario: Computer Science per-subject BAML delegation

- **GIVEN** the `baml/education/web/computer_science_web.baml` backend
- **WHEN** any of `WebStudyPlan`, `WebExamPaperDiscussion`, or
  `WebMarkingSchemeExplanation` is invoked
- **THEN** the function delegates to the foundation at
  `baml/education/subjects/qpack_computer_science.baml` for the
  per-subject syllabus + past-paper grounding

### Requirement: 5th-surface lock — no 6th surface without a separate openspec change

The system SHALL NOT add a 6th row to the 4 canonical surfaces table
without first opening a separate openspec change that explicitly amends
this requirement.

The current 5-surface table (per this spec's R-5Surface requirement) is
locked as of the archive date of
`2026-07-18-british-isles-portal-activation-v3`.

#### Scenario: A developer asks for a 6th surface

- **GIVEN** a developer asks "can I add a 6th surface to the table?"
- **WHEN** the openspec change is reviewed
- **THEN** the reviewer MUST reject any PR that adds a 6th row without a
  separate openspec change explicitly amending this requirement

### Requirement: 5th-surface activation marker

The system SHALL publish the 5th surface (`cianfhoghlaim-leaving-cert`)
to `portal.cianfhoghlaim.ie` via the `portal-cloudflare-r2` stack
(see `openspec/changes/2026-07-18-british-isles-portal-activation-v3/`).

The Pangolin resource binding SHALL live at
`bonneagar/pangolin/resources/portal.yaml`.

#### Scenario: portal.cianfhoghlaim.ie resolves

- **WHEN** the operator opens `https://portal.cianfhoghlaim.ie`
- **THEN** the British Isles map renders with Éire active
- **AND** at least 1 NCCA subject (Mathematics) shows the 6-section shell
- **AND** the CopilotKit sidebar is mounted with EN+GA

### Requirement: Pocket ID SSO as the 7th layer authentication provider

The system SHALL document Pocket ID OIDC as the canonical SSO provider
in the 7-layer agentic-frontend-framework stack spec. The 5 OIDC
audiences are documented in the `infrastructure-stacks` spec.

#### Scenario: A new agent surface is added

- **WHEN** a developer looks at the 7-layer stack spec
- **THEN** they see Pocket ID OIDC as the canonical SSO provider
- **AND** they see the 5 OIDC audiences

### Requirement: PlanetScale Postgres Centralisation (agentic-frontend-frameworks)

The system SHALL migrate the 7-layer agentic-web stack's Convex self-host DB to PlanetScale PostgreSQL per `openspec/specs/planetscale-postgres-data-strategy/spec.md` R7 (row 2: Convex).

#### Scenario: Convex connects to PlanetScale PG

- **GIVEN** the Phase B change has archived
- **WHEN** `bonneagar/stacks/convex/compose.yaml` is inspected
- **THEN** `POSTGRES_URL` SHALL be set
- **AND** `POSTGRES_URL` SHALL resolve via Locket to PlanetScale PG
- **AND** the `convex-` prefixed schema SHALL be pre-created on the PlanetScale branch

#### Scenario: Hono + oRPC env vars

- **GIVEN** the Phase B change has archived
- **WHEN** the leaving-cert app starts
- **THEN** the per-subject Hono routes' `DATABASE_URL` env var SHALL point at PlanetScale PG (when they add Postgres connections in a follow-up)
- **AND** no local Postgres container SHALL be required for the leaving-cert app's data plane

### Requirement: Web UI control panel is registered as the 5th canonical surface

The system SHALL register the new `web/apps/cianfhoghlaim-web/control-panel/`
as the 5th canonical agentic web surface (TanStack Start + Convex +
Hono + oRPC). The 5 surfaces are:

1. `web/apps/cianfhoghlaim-web/` (the public web app)
2. `web/apps/croilar-web/` (multi-persona portfolio)
3. `web/apps/croilar-portal/` (portfolio dashboard)
4. `web/apps/tuatha-ui/` (Túatha educational MMO)
5. `web/apps/cianfhoghlaim-web/control-panel/` (NEW: deployment
   control panel)

#### Scenario: Control panel boots with all 5 routes

- **GIVEN** `web/apps/cianfhoghlaim-web/` configured with the
  control-panel routes
- **WHEN** the operator runs `bun run dev` and navigates to
  `http://localhost:3000/control-panel`
- **THEN** all 5 routes render without error:
  `/control-panel/models`, `/control-panel/pipelines`,
  `/control-panel/datasets`, `/control-panel/stacks`,
  `/control-panel/registry`

### Requirement: agentic-frontend-frameworks MUST register the 5th web surface (control-panel)

The system SHALL register `web/apps/cianfhoghlaim-web/src/routes/control-panel/index.tsx`
as the 5th canonical web surface for the deployment control panel.
The 5 surfaces are:

1. `web/apps/cianfhoghlaim-web/` (the public web app)
2. `web/apps/tuatha-ui/` (the Túatha educational MMO frontend)
3. `web/apps/croilar-web/` (the Croílár multi-persona portfolio)
4. `web/apps/croilar-portal/` (the Croílár portfolio dashboard)
5. `web/apps/cianfhoghlaim-web/control-panel/` (NEW: deployment control panel)

#### Scenario: The 5th surface mounts in the Hono API router

- **GIVEN** the new TanStack Start route at `web/apps/cianfhoghlaim-web/src/routes/control-panel/index.tsx`
- **WHEN** `web/hono-api/src/index.ts` imports `controlPanelApp` and mounts it at `/api/control-panel`
- **THEN** the 8 Hono endpoints (5 GETs + 3 POSTs) are reachable
- **AND** the marimo notebook + the web UI both read/write the same `deployment-choice.yaml`

#### Scenario: The 5th surface conforms to the agentic-frontend-frameworks contract

- **GIVEN** the deployment control panel TanStack Start route
- **WHEN** the operator opens `localhost:3000/control-panel`
- **THEN** the 5 tabs render without error (Models / Pipelines / Datasets / Stacks / Registry)
- **AND** the data is sourced from the Hono API at `/api/control-panel/*`
- **AND** the Hono API delegates to the Python bridge at `web/hono-api/control-panel/_python_bridge.py`

### Requirement: CopilotKit >= 1.67.1 pin

The 12 web apps under `web/apps/` that depend on CopilotKit SHALL
pin `@copilotkit/runtime >= 1.67.1` +
`@copilotkit/react-core >= 1.67.1` +
`@copilotkit/react-ui >= 1.67.1` (per the `agentic-frontend-frameworks`
spec).

The reason: per `CopilotKit issue #2946` (confirmed regression in
v1.50.1 where `useLazyToolRenderer` only processes `toolCalls[0]`)
+ `CopilotKit issue #3030` (Strands adapter required text
\nclose guard), the v1.50 series has 2 known regressions that are
fixed in v1.67.1 (verified via `CopilotKit v1.67.1 release notes`).

Additionally, `ag-ui-strands` MUST be upgraded alongside the
CopilotKit pin (per `ag-ui-strands` integration with CopilotKit).

#### Scenario: Pin is set in package.json

- **WHEN** `bun pm ls copilotkit --filter 'copilotkit'` runs in
  `web/apps/cianfhoghlaim-leaving-cert/`
- **THEN** the resolved versions are >= 1.67.1
- **AND** the same is true for `web/apps/cianfhoghlaim-web/`,
  `web/apps/oideachais/`, `web/apps/croilar-web/`,
  `web/apps/croilar-portal/`, `web/apps/tuatha-ui/`, etc.

#### Scenario: ag-ui-strands is upgraded

- **WHEN** `bun pm ls ag-ui-strands` runs
- **THEN** the resolved version is >= the version that ships with
  CopilotKit v1.67.1 (currently 0.0.3)

#### Scenario: CopilotKit useLazyToolRenderer renders all tool calls

- **GIVEN** an AG-UI agent emits multiple sequential `TOOL_CALL_*`
  events for the same assistant message
- **WHEN** the CopilotKit runtime processes the events
- **THEN** the runtime MUST render all tool calls (not just
  `toolCalls[0]` per the v1.50 regression)
- **AND** the chat UI shows all tool components side-by-side

### Requirement: `web/COPILOTKIT_PIN.md` canonical doc

The system SHALL maintain `web/COPILOTKIT_PIN.md` (canonical
reference) documenting:
- The 1.67.1 pin + the v1.50 regression context (per
  `CopilotKit issue #2946`)
- The `ag-ui-strands` upgrade requirement
- The Strands adapter `TEXT_MESSAGE_END` close-guard fix (per
  `CopilotKit issue #3030`)
- The recommended path to the v2 headless API (`@copilotkit/react-core/v2`)
  for new surfaces (per `CopilotKit v1.50 release announcement`)

#### Scenario: New developer consults the doc

- **WHEN** a developer is wiring a new CopilotKit surface
- **THEN** they MUST consult `web/COPILOTKIT_PIN.md` for the
  canonical pin + decision + 1.67.1 migration notes
- **AND** the doc covers the v1 → v2 migration path

### Requirement: marimo_to_fastapi integration helper

The system SHALL provide `notebooks/_shared/marimo_to_fastapi.py`
that mounts the 6 BIEP v3 stage dashboards + the canonical
`00_marimo_patterns_tour.py` as FastAPI endpoints.

The helper exposes each notebook's public functions via
`@app.get("/<stage>/<function>")` (per the
`frameworks/fastapi/` pattern).

#### Scenario: The 6 BIEP notebooks are exposed as FastAPI endpoints

- **WHEN** the operator runs `curl http://localhost:8000/ireland_lc/curriculum_educator`
- **THEN** the endpoint returns the canonical `curriculum_educator`
  output from the LC stage dashboard

### Requirement: FastAPI Auth for the 6 BIEP notebooks

The system SHALL lock down the 6 BIEP v3 stage dashboards with the
canonical `frameworks/fastapi-auth/` pattern.

The auth includes:
- Token-based authentication
- Rate limiting
- CORS configuration

#### Scenario: Unauthenticated requests are rejected

- **WHEN** the operator sends `curl http://localhost:8000/ireland_lc/curriculum_educator` (without auth)
- **THEN** the server returns 401 Unauthorized

## Cross-references

- [`.agents/skills/tanstack-start/SKILL.md`](../../.agents/skills/tanstack-start/SKILL.md)
- [`.agents/skills/copilotkit/SKILL.md`](../../.agents/skills/copilotkit/SKILL.md)
- [`.agents/skills/hono/SKILL.md`](../../.agents/skills/hono/SKILL.md)
- [`.agents/skills/convex/SKILL.md`](../../.agents/skills/convex/SKILL.md)
- [`cianfhoghlaim/web/`](../../cianfhoghlaim/web/) (the oideachais web app)
- [`cianfhoghlaim/apps/web/`](../../cianfhoghlaim/apps/web/) (the croilar public site)
- [`cianfhoghlaim/apps/portal/`](../../cianfhoghlaim/apps/portal/) (the croilar dashboard)
