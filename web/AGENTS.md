# `web/` — Agentic Frontend Apps

> **The agent-driven web surface of the Cianfhoghlaim stack —
> TanStack Start + CopilotKit + AG-UI + Hono + Convex + oRPC +
> Cloudflare.** Per the **2026-08-24-wave-5-web-consolidation-v1**
> openspec change, houses 5 consolidated app subdirs (cianfhoghlaim +
> oideachais + croilar + tuatha + game_showcase) + 2 demo apps
> (cianfhoghlaim-mmo + tuatha-demo) + the Hono API gateway + 3 shared
> packages. The legacy `_oideachais_apps/` (sruth-era dead weight) has
> been archived to `web/_archive/`.

> **Wave 5 in progress**: the canonical merge targets (oideachais,
> croilar, tuatha) have placeholders for the 2.4 GB +
> `cianfhoghlaim-leaving-cert/` → `oideachais/` migration that lands
> in follow-up PRs.

## Routing

Load this AGENTS.md when:

- You need to add / modify a frontend app (any of the 4)
- You need to wire an AG-UI stream from an agent runtime to a
  CopilotKit React UI
- You need to add / modify a Hono API route
- You need to add / modify a shared UI component
- You need to deploy to Cloudflare Pages (Workers + R2 + D1 +
  Vectorize)

For platform-wide context, load [`../AGENTS.md`](../AGENTS.md).

## Quick start

```bash
# From /web/
bun install                       # Install all workspace dependencies (bun workspaces)
bun run dev                       # Run all apps + packages in dev mode (turbo)
bun run typecheck                 # Type check across the monorepo
bun run lint                      # Lint across the monorepo
bun run build                     # Build everything
```

## Key sources (post-Wave 5, 2026-08-24)

| Path | Why it matters |
|:--|:--|
| `web/apps/cianfhoghlaim/` | The CENTRAL Cianfhoghlaim homepage (with agentic chat) — Wave 5 target for merging `cianfhoghlaim-web/` + `cianfhoghlaim-mmo/` |
| `web/apps/oideachais/` | The CONTENT app (LC + JC + GCSE + A-Level per-subject pages) — Wave 5 target for merging `cianfhoghlaim-leaving-cert/` + `oideachais-dashboard/` |
| `web/apps/croilar/` | The PORTFOLIO app (multi-persona + dashboard + games) — Wave 5 target for merging `croilar-portal/` + `croilar-web/` |
| `web/apps/tuatha/` | The TÚATHA Celtic MMO front-end (TanStack Start + React + Babylon.js) — was `tuatha-ui/`, renamed in Wave 5 |
| `web/apps/game_showcase/` | Game showcase (kept as-is) |
| `web/apps/cianfhoghlaim-mmo/` | Babylon.js + SpacetimeDB MMO client (pending Wave 5 merge into `cianfhoghlaim/`) |
| `web/apps/oideachais-dashboard/` | OPERATOR dashboard (pending Wave 5 merge into `oideachais/`) |
| `web/apps/tuatha-demo/` | Python Túatha demo (separate concern, kept as-is) |
| `web/_archive/_oideachais_apps/` | **ARCHIVED** (Wave 5): legacy sruth-era workspace |
| `web/hono-api/` | The SINGLE canonical Hono API gateway (per-app CopilotKit actions live here) |
| `web/packages/ui-kit/` | The consolidated UI surface (analytics + i18n + components + config + hooks) |
| `web/packages/auth/` | better-auth + Pocket ID OIDC |
| `web/packages/db/` | Convex generators + Drizzle helpers |

## Adjacent specs

- [`agentic-frontend-frameworks`](../openspec/specs/agentic-frontend-frameworks/spec.md) — TanStack Start + CopilotKit + AG-UI + Hono + Convex
- [`web-monorepo-consolidation`](../openspec/specs/web-monorepo-consolidation/spec.md) — this consolidation (the canonical structure)
- [`central-cianfhoghlaim-homepage`](../openspec/specs/central-cianfhoghlaim-homepage/spec.md) — the central homepage
- [`per-subject-coverage`](../openspec/specs/per-subject-coverage/spec.md) — the 60-subject coverage matrix
- [`per-subject-agents`](../openspec/specs/per-subject-agents/spec.md) — the 60 per-subject agents
- [`tanstack-ai-agui-integration`](../openspec/specs/tanstack-ai-agui-integration/spec.md) — TanStack AI + AG-UI compliance
- [`schema-driven-codegen`](../openspec/specs/schema-driven-codegen/spec.md) — BAML → Zod → Convex → CopilotKit pipeline
- [`deployment-control-panel`](../openspec/specs/deployment-control-panel/spec.md) — the web UI for `deployment-choice.yaml`
- [`british-isles-education-pipeline-v3`](../openspec/specs/british-isles-education-pipeline-v3/spec.md) — the BIEP v3 web UI consumer

## DO NOT

- **Never** import a hardcoded model string in a frontend — route through `MODEL_REGISTRY`
- **Never** bypass the Hono API gateway — every backend call goes through `web/hono-api/`
- **Never** create a per-app `apps/<app>/apps/api/src/` directory for CopilotKit actions — they live at `web/hono-api/src/routes/copilotkit/`
- **Never** create a per-app `convex/` deployment — all apps share `apps/oideachais-dashboard/convex/`
- **Never** create a per-app `tailwind.config.ts` — extend from `web/packages/ui-kit/theme/tailwind.config.ts`
- **Never** create a per-app AGENTS.md without cross-linking `agents/WEB_INTEGRATION.md`

## Skill pointers

| Skill | When to load |
|:--|:--|
| [`tanstack-start`](../.agents/skills/tanstack-start/SKILL.md) | React framework (file-based routing, server functions, RSC v1.94+) |
| [`copilotkit-develop`](../.agents/skills/copilotkit-develop/SKILL.md) | CopilotKit v2 (chat interfaces, frontend tools, runtime wiring) |
| [`ag-ui`](../.agents/skills/ag-ui/SKILL.md) | The AG-UI SSE protocol (agent↔UI streaming) |
| [`hono`](../.agents/skills/hono/SKILL.md) | The Hono API gateway pattern |
| [`cloudflare`](../.agents/skills/cloudflare/SKILL.md) | Workers + Pages + R2 + D1 + Vectorize |
| [`centralized-registry`](../.agents/skills/centralized-registry/SKILL.md) | The model + schema registry |
| [`schema-codegen`](../.agents/skills/schema-codegen/SKILL.md) | The BAML → Zod → Convex → CopilotKit codegen pipeline (NEW) |

<!-- generated: 2026-07-29; updated per 2026-08-13-web-monorepo-consolidation-and-agent-integration-v1 PR 2 -->
