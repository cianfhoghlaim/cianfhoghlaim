# Agentic Frontend Frameworks Capability

## Purpose

`agentic-frontend-frameworks` is a capability of the Cianfhoghlaim
platform. The corresponding source code lives at
`sruth/oideachais/web/` (TanStack Start front-end), `sruth/croilar/apps/web/` (Croilar
public persona site), `sruth/croilar/apps/portal/` (Croilar self-hosted
dashboard), and `sruth/meaisinfhoghlaim/agents/agui_*` (the AG-UI integration).
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

- **GIVEN** a file `sruth/oideachais/web/apps/web/src/routes/curriculum.tsx`
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
   MotherDuck / DuckLake (per `.agents/skills/oideachais-
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
  - The 4 canonical surfaces (sruth/oideachais/web, sruth/croilar/apps/
    web, sruth/croilar/apps/portal, sruth/tuatha/ui)
  - The 4 backend options (Pydantic AI / Agno / Google
    ADK / BAML)
  - The 3 auth models (no-auth, OAuth + SIWE + 2FA,
    Pocket ID OIDC SSO)
- **AND** the developer can wire the new persona surface
  end-to-end without re-deriving the framework choices

#### Scenario: A new agent UI is added to the existing surface

- **GIVEN** the developer wants to add a chat UI to the
  sruth/oideachais/web surface
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
| 1 | `sruth/oideachais/web` | TanStack Start + Hono | **No auth** (public lakehouse) | `oideachais.education.ie.*` (MotherDuck) | Irish educators + students |
| 2 | `sruth/croilar/apps/web` | TanStack Start + Hono | **No auth** (public portfolio) | Convex (read-only) | Public visitors |
| 3 | `sruth/croilar/apps/portal` | TanStack Start + Hono + BetterAuth | **OAuth + SIWE + 2FA** | Convex (read-write) | The 3 personas (aleyum, cianfhoghlaim, carlcashman) |
| 4 | `sruth/tuatha/ui` | TanStack Start + Babylon.js | **SIWE** (Ethereum wallet) | Convex (realtime) + SpacetimeDB | Tuatha game players |

The 5th surface (marimo, analyst notebook) is
documented separately at
`.agents/skills/marimo/SKILL.md`.

#### Scenario: A developer is asked to add an auth wall

- **GIVEN** the user wants to add auth to a surface
- **WHEN** the developer looks at the 4 surfaces table
- **THEN** the developer sees:
  - `sruth/oideachais/web` and `sruth/croilar/apps/web` have NO auth
    (public)
  - `sruth/croilar/apps/portal` has BetterAuth + Pocket ID +
    SIWE
  - `sruth/tuatha/ui` has SIWE (Ethereum wallet only)
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
Brown Ajah of the Wheel of Time; tagline = "Aes Sedai — servants of all"
(the Brown Ajah motto).

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
semantic quest icons → 24 SVG icons; Khan mastery → Brown Ajah éraic
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

### Requirement: Brown Ajah theming + accurate British Isles map (R7 — NEW per `rewrite-cianfhoghlaim-leaving-cert-v2`)

The system SHALL implement the **Brown Ajah** Wheel of Time theming
per the 4 WoT excerpts: Aes Sedai = the 8 NCCA subject specialists;
Amyrlin Seat = the orchestrator agent; Dragon Reborn = the student who
completes the cross-subject mastery; Dragon Banner = the Wales subnation
flag (Cadwaladr ap Cadwallon + Owain Glyndwr; red dragon on white);
Tuatha'an = the Irish Travellers (the student-as-traveller; the
Cianfhoghlaim mobile client). The realm map SHALL be an **accurate**
map of the British Isles (NOT fictional). The 6 subnations SHALL be:
Éire (Ireland, v1 active) + Northern Ireland + Scotland + England +
Wales + Isle of Man. The 5 NCCA Key Competencies SHALL be the 5
land-marks (Dublin + Edinburgh + Cardiff + London + Douglas) plus a
6th Belfast node (Cross-Border Studies). The 8 NCCA subjects SHALL be
the 8 overlay buttons. The Connacht province SHALL be the "home base"
with the Cian lineage highlights (Delbhna Tír Dhá Locha + Lough Corrib
+ Galway Bay + Moycullen).

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

- **GIVEN** the user opens any page on `oideachais.cianfhoghlaim.ie`
- **WHEN** the page renders
- **THEN** no text matches the regex `Ci[ae]n M[ae]c a[nm] D[ée]isi[gh]`
- **AND** no text matches the family surnames Deacy, Lyons, Morris, Conroy
- **AND** no text references the 3 Gemini Deep Research warrants

## Cross-references

- [`.agents/skills/tanstack-start/SKILL.md`](../../.agents/skills/tanstack-start/SKILL.md)
- [`.agents/skills/copilotkit/SKILL.md`](../../.agents/skills/copilotkit/SKILL.md)
- [`.agents/skills/hono/SKILL.md`](../../.agents/skills/hono/SKILL.md)
- [`.agents/skills/convex/SKILL.md`](../../.agents/skills/convex/SKILL.md)
- [`sruth/oideachais/web/`](../../sruth/oideachais/web/) (the oideachais web app)
- [`sruth/croilar/apps/web/`](../../sruth/croilar/apps/web/) (the croilar public site)
- [`sruth/croilar/apps/portal/`](../../sruth/croilar/apps/portal/) (the croilar dashboard)
