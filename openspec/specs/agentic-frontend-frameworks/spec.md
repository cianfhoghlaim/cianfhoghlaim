# Agentic Frontend Frameworks Capability

## Purpose

`agentic-frontend-frameworks` is a capability of the Cianfhoghlaim
platform. The corresponding source code lives at
`oideachais/web/` (TanStack Start front-end), `croilar/apps/web/` (Croilar
public persona site), `croilar/apps/portal/` (Croilar self-hosted
dashboard), and `meaisinfhoghlaim/agents/agui_*` (the AG-UI integration).
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

- **GIVEN** a file `oideachais/web/apps/web/src/routes/curriculum.tsx`
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

## Cross-references

- [`.agents/skills/tanstack-start/SKILL.md`](../../.agents/skills/tanstack-start/SKILL.md)
- [`.agents/skills/copilotkit/SKILL.md`](../../.agents/skills/copilotkit/SKILL.md)
- [`.agents/skills/hono/SKILL.md`](../../.agents/skills/hono/SKILL.md)
- [`.agents/skills/convex/SKILL.md`](../../.agents/skills/convex/SKILL.md)
- [`oideachais/web/`](../../oideachais/web/) (the oideachais web app)
- [`croilar/apps/web/`](../../croilar/apps/web/) (the croilar public site)
- [`croilar/apps/portal/`](../../croilar/apps/portal/) (the croilar dashboard)
