# `web/` — Agentic Frontend Apps

The Cianfhoghlaim web surface — the consolidated monorepo of
agentic frontend apps + the Hono API gateway + the shared
packages, all routed through the centralized model registry +
the deployment control panel.

| App | Surface | Status | Stack |
|:--|:--|:--|:--|
| `apps/oideachais/` | The unified CONTENT app (LC + JC + GCSE + A-Level) | **Planned merge** (Phase D) | TanStack Start + Convex + Hono |
| `apps/croilar/` | The unified PORTFOLIO app (multi-persona) | **Planned merge** (Phase E) | TanStack Start + Convex |
| `apps/oideachais-dashboard/` | The OPERATOR dashboard | **Moved** (Phase F, PR 2) | TanStack Start + Convex |
| `apps/cianfhoghlaim/` | The CENTRAL Cianfhoghlaim homepage | **Planned new** (Phase T, PR 9) | TanStack AI + Convex + CopilotKit v2 + AG-UI |
| `hono-api/` | The SINGLE canonical Hono API gateway | Unified (Phase G) | Hono + oRPC |

| Package | Purpose | Status |
|:--|:--|:--|
| `packages/ui-kit/` | The consolidated UI surface (analytics + i18n + components + config) | **Merged** (Phase A, PR 1) |
| `packages/auth/` | better-auth + Pocket ID OIDC | Kept |
| `packages/db/` | Convex generators + Drizzle helpers | Kept |

## Quick start

```bash
# From /web/
bun install                       # Install all workspace dependencies
bun run dev                       # Run all apps in dev mode (turbo)
bun run typecheck                 # Type check across the monorepo
bun run lint                      # Lint across the monorepo
bun run build                     # Build all apps + packages
```

## Per-app commands

```bash
# Run a specific app
bun run dev:oideachais
bun run dev:croilar
bun run dev:dashboard
bun run dev:cianfhoghlaim

# Per-package scripts
bun --filter '@cianfhoghlaim/ui-kit' typecheck
bun --filter '@cianfhoghlaim/auth' typecheck
bun --filter '@cianfhoghlaim/db' typecheck
```

## Per-app routing

- **oideachais**: per-subject content pages (LC + JC + GCSE + A-Level), routes under `/<stage>/<subject>/`
- **croilar**: multi-persona portfolio + dashboard, routes under `/persona/$slug/`, `/dashboard/`, `/games/`
- **oideachais-dashboard**: operator dashboard, routes under `/health/`, `/dagster/`, `/kg/`, `/deployment/`, `/memory/`
- **cianfhoghlaim**: central homepage with agentic chat, route at `/`

For agent-routing context, see [`AGENTS.md`](AGENTS.md).

## Adjacent specs

- [`agentic-frontend-frameworks`](../openspec/specs/agentic-frontend-frameworks/spec.md) — TanStack Start + CopilotKit + AG-UI + Hono + Convex
- [`web-monorepo-consolidation`](../openspec/specs/web-monorepo-consolidation/spec.md) — this consolidation (post-Phase A)
- [`central-cianfhoghlaim-homepage`](../openspec/specs/central-cianfhoghlaim-homepage/spec.md) — the central homepage (Phase T)
- [`per-subject-coverage`](../openspec/specs/per-subject-coverage/spec.md) — the 60-subject coverage matrix
- [`per-subject-agents`](../openspec/specs/per-subject-agents/spec.md) — the 60 per-subject agents
- [`deployment-control-panel`](../openspec/specs/deployment-control-panel/spec.md) — the web UI for `deployment-choice.yaml`
- [`british-isles-education-pipeline-v3`](../openspec/specs/british-isles-education-pipeline-v3/spec.md) — the BIEP v3 web UI consumer

## DO NOT

- **Never** import a hardcoded model string in a frontend — route through `MODEL_REGISTRY`
- **Never** bypass the Hono API gateway — every backend call goes through `web/hono-api/`
- **Never** create a per-app `apps/<app>/apps/api/src/` directory for CopilotKit actions — they live at `web/hono-api/src/routes/copilotkit/`
- **Never** create a per-app `convex/` deployment — all apps share `apps/oideachais-dashboard/convex/`

## Skill pointers

| Skill | When to load |
|:--|:--|
| [`tanstack-start`](../.agents/skills/tanstack-start/SKILL.md) | React framework (file-based routing, server functions, RSC v1.94+) |
| [`copilotkit-develop`](../.agents/skills/copilotkit-develop/SKILL.md) | CopilotKit v2 (chat interfaces, frontend tools, runtime wiring) |
| [`ag-ui`](../.agents/skills/ag-ui/SKILL.md) | The AG-UI SSE protocol (agent↔UI streaming) |
| [`hono`](../.agents/skills/hono/SKILL.md) | The Hono API gateway pattern |
| [`cloudflare`](../.agents/skills/cloudflare/SKILL.md) | Workers + Pages + R2 + D1 + Vectorize |
| [`centralized-registry`](../.agents/skills/centralized-registry/SKILL.md) | The model + schema registry |
| [`schema-codegen`](../.agents/skills/schema-codegen/SKILL.md) | The BAML → Zod → Convex → CopilotKit codegen pipeline |

<!-- generated: 2026-07-29; updated per 2026-08-13-web-monorepo-consolidation-and-agent-integration-v1 PR 2 -->
