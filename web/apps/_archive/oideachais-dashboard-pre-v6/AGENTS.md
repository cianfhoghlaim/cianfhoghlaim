# `apps/oideachais-dashboard/` — The Operator Dashboard

> **The Cianfhoghlaim operator dashboard — the canonical
> observability + control plane for the BIEP v3 + the 93-stack
> IaC + the centralized model registry + the lakehouse memory
> stack.** Lives at `web/apps/oideachais-dashboard/` (moved
> from `web/_oideachais_dashboard/` by the
> 2026-08-13-web-monorepo-consolidation-and-agent-integration-v1
> change, Phase F).

## Routing

Load this AGENTS.md when:

- You need to add / modify an operator dashboard route
- You need to wire a new observability metric (Dagster health,
  Cianfhoghlaim coverage, model registry, stack health, etc.)
- You need to add / modify a Convex table that the dashboard
  consumes
- You need to deploy the dashboard to Cloudflare Pages

For platform-wide context, load [`../../../AGENTS.md`](../../../AGENTS.md).

## Quick start

```bash
# From /web/apps/oideachais-dashboard/
bun run dev                       # vite dev
bun run typecheck                 # tsc --noEmit
bun run build                     # vite build
bun run start                     # node .output/server/index.mjs
```

## Key sources

| Path | Why it matters |
|:--|:--|
| `apps/oideachais-dashboard/src/routes/` | The operator dashboard routes (health / dagster / kg / deployment / memory) |
| `apps/oideachais-dashboard/convex/` | The shared Convex deployment (this app + oideachais + croilar + cianfhoghlaim) |
| `apps/oideachais-dashboard/convex/schema/` | The Convex schema (umbrella + per-subject tables) |
| `apps/oideachais-dashboard/app.config.ts` | The TanStack Start config |
| `apps/oideachais-dashboard/tailwind.config.ts` | The per-app Tailwind override |
| `web/packages/ui-kit/` | The shared UI surface |

## Adjacent specs

- [`central-cianfhoghlaim-homepage`](../openspec/specs/central-cianfhoghlaim-homepage/spec.md) — the central homepage (consumer of this dashboard's data)
- [`deployment-control-panel`](../openspec/specs/deployment-control-panel/spec.md) — the deployment-choice.yaml web UI
- [`dagster-5-layer-component-architecture`](../openspec/specs/dagster-5-layer-component-architecture/spec.md) — the 5 Cianfhoghlaim Components
- [`web-monorepo-consolidation`](../openspec/specs/web-monorepo-consolidation/spec.md) — this app's location in the consolidated web/

## DO NOT

- **Never** import a hardcoded model string — route through `MODEL_REGISTRY`
- **Never** add a per-app Convex deployment — extend the umbrella schema
- **Never** add a per-app Hono API — extend `web/hono-api/`
- **Never** deploy without running `mise run schema:generate` first

## Skill pointers

| Skill | When to load |
|:--|:--|
| [`tanstack-start`](../.agents/skills/tanstack-start/SKILL.md) | React framework (file-based routing, server functions) |
| [`copilotkit-develop`](../.agents/skills/copilotkit-develop/SKILL.md) | CopilotKit v2 (operator-side CopilotKit actions) |
| [`hono`](../.agents/skills/hono/SKILL.md) | The Hono API gateway (the dashboard calls these) |
| [`centralized-registry`](../.agents/skills/centralized-registry/SKILL.md) | The model + schema registry |
| [`dagster`](../.agents/skills/dagster/SKILL.md) | Dagster orchestration (the health routes consume this) |

<!-- created: 2026-08-13 (per the 2026-08-13-web-monorepo-consolidation-and-agent-integration-v1 change, Phase F) -->
