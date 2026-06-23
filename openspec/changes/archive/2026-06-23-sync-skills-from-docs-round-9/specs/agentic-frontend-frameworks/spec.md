# Spec Delta: agentic-frontend-frameworks

## ADDED Requirements

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
  - The 4 canonical surfaces (oideachais/web, croilar/apps/
    web, croilar/apps/portal, tuatha/ui)
  - The 4 backend options (Pydantic AI / Agno / Google
    ADK / BAML)
  - The 3 auth models (no-auth, OAuth + SIWE + 2FA,
    Pocket ID OIDC SSO)
- **AND** the developer can wire the new persona surface
  end-to-end without re-deriving the framework choices

#### Scenario: A new agent UI is added to the existing surface

- **GIVEN** the developer wants to add a chat UI to the
  oideachais/web surface
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
| 1 | `oideachais/web` | TanStack Start + Hono | **No auth** (public lakehouse) | `oideachais.education.ie.*` (MotherDuck) | Irish educators + students |
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
  - `oideachais/web` and `croilar/apps/web` have NO auth
    (public)
  - `croilar/apps/portal` has BetterAuth + Pocket ID +
    SIWE
  - `tuatha/ui` has SIWE (Ethereum wallet only)
- **AND** the developer can pick the right auth pattern
  for the target surface without re-deriving

## REMOVED Requirements

(None.)
