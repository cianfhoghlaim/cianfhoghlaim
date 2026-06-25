# Agentic Frontend Frameworks Capability

## Purpose

`agentic-frontend-frameworks` is a capability of the Cianfhoghlaim
platform. The corresponding source code lives at
`sruth/oideachais/web/` (TanStack Start front-end), `croilar/apps/web/` (Croilar
public persona site), `croilar/apps/portal/` (Croilar self-hosted
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
  - The 4 canonical surfaces (sruth/oideachais/web, croilar/apps/
    web, croilar/apps/portal, tuatha/ui)
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
| 2 | `croilar/apps/web` | TanStack Start + Hono | **No auth** (public portfolio) | Convex (read-only) | Public visitors |
| 3 | `croilar/apps/portal` | TanStack Start + Hono + BetterAuth | **OAuth + SIWE + 2FA** | Convex (read-write) | The 3 personas (aleyum, cianfhoghlaim, carlcashman) |
| 4 | `tuatha/ui` | TanStack Start + Babylon.js | **SIWE** (Ethereum wallet) | Convex (realtime) + SpacetimeDB | Tuatha game players |

The 5th surface (marimo, analyst notebook) is
documented separately at
`.agents/skills/marimo/SKILL.md`.

#### Scenario: A developer is asked to add an auth wall

- **GIVEN** the user wants to add auth to a surface
- **WHEN** the developer looks at the 4 surfaces table
- **THEN** the developer sees:
  - `sruth/oideachais/web` and `croilar/apps/web` have NO auth
    (public)
  - `croilar/apps/portal` has BetterAuth + Pocket ID +
    SIWE
  - `tuatha/ui` has SIWE (Ethereum wallet only)
- **AND** the developer can pick the right auth pattern
  for the target surface without re-deriving

## Cross-references

- [`.agents/skills/tanstack-start/SKILL.md`](../../.agents/skills/tanstack-start/SKILL.md)
- [`.agents/skills/copilotkit/SKILL.md`](../../.agents/skills/copilotkit/SKILL.md)
- [`.agents/skills/hono/SKILL.md`](../../.agents/skills/hono/SKILL.md)
- [`.agents/skills/convex/SKILL.md`](../../.agents/skills/convex/SKILL.md)
- [`sruth/oideachais/web/`](../../sruth/oideachais/web/) (the oideachais web app)
- [`croilar/apps/web/`](../../croilar/apps/web/) (the croilar public site)
- [`croilar/apps/portal/`](../../croilar/apps/portal/) (the croilar dashboard)
