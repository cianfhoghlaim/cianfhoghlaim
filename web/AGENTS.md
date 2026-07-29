# `web/` — Agentic Frontend Apps

> **The agent-driven web surface of the Cianfhoghlaim stack — TanStack Start + CopilotKit + AG-UI + Hono + Convex + oRPC + Cloudflare.** Houses 7 app subdirs (cianfhoghlaim-web, tuatha-ui, croilar-web, croilar-portal, tuatha-demo, game_showcase, cianfhoghlaim-mcp-filesystem) + the Hono API gateway.

## Routing

Load this AGENTS.md when:

- You need to add / modify a frontend app (any of the 7)
- You need to wire an AG-UI stream from an agent runtime to a CopilotKit React UI
- You need to add / modify a Hono API route
- You need to deploy to Cloudflare Pages (Workers + R2 + D1 + Vectorize)

For platform-wide context, load [`../AGENTS.md`](../AGENTS.md).

## Quick start

```bash
mise run ts:install                 # Install all TypeScript dependencies (bun workspaces)
mise run ts:typecheck               # Type check TypeScript code via turbo
mise run ts:lint                    # Lint TypeScript code via turbo
mise run schema:generate            # Regenerate Zod + TanStack DB schemas (CI drift gate)
```

## Key sources

| Path | Why it matters |
|:--|:--|
| `web/apps/cianfhoghlaim-web/` | The TanStack Start + React public web app (the flagship frontend) |
| `web/apps/tuatha-ui/` | The Túatha educational MMO frontend (Babylon.js + AG-UI) |
| `web/apps/croilar-web/` | The Croílár multi-persona portfolio (TanStack Start) |
| `web/apps/croilar-portal/` | The Croílár portfolio dashboard |
| `web/apps/tuatha-demo/` | The Tuatha Babylon.js demo |
| `web/apps/cianfhoghlaim-mcp-filesystem/` | The filesystem MCP server for the data platform |
| `web/hono-api/` | The Hono API gateway (the canonical backend-for-frontend) |
| `web/_oideachais_dashboard/` | The Oideachais dashboard sub-tree |
| `web/_croilar_shared/` | The shared Croílár components + design tokens |
| `web/packages/` | The shared React component libraries |

## Adjacent specs

- [`agentic-frontend-frameworks`](../openspec/specs/agentic-frontend-frameworks/spec.md) — TanStack Start + CopilotKit + AG-UI + Hono + Convex
- [`deployment-control-panel`](../openspec/specs/deployment-control-panel/spec.md) — the web UI for `deployment-choice.yaml`
- [`british-isles-education-pipeline-v3`](../openspec/specs/british-isles-education-pipeline-v3/spec.md) — the BIEP v3 web UI consumer

## DO NOT

- **Never** import a hardcoded model string in a frontend — route through `MODEL_REGISTRY` (the centralized registry).
- **Never** bypass the Hono API gateway — every backend call goes through `web/hono-api/`.
- **Never** deploy a frontend without running `mise run schema:generate` + `mise run schema:validate` (the Zod drift gate).

## Skill pointers

| Skill | When to load |
|:--|:--|
| [`tanstack-start`](../.agents/skills/tanstack-start/SKILL.md) | React framework (file-based routing, server functions, RSC v1.94+) |
| [`copilotkit-develop`](../.agents/skills/copilotkit-develop/SKILL.md) | CopilotKit v2 (chat interfaces, frontend tools, runtime wiring) |
| [`ag-ui`](../.agents/skills/ag-ui/SKILL.md) | The AG-UI SSE protocol (agent↔UI streaming) |
| [`hono`](../.agents/skills/hono/SKILL.md) | The Hono API gateway pattern |
| [`cloudflare`](../.agents/skills/cloudflare/SKILL.md) | Workers + Pages + R2 + D1 + Vectorize |
| [`centralized-registry`](../.agents/skills/centralized-registry/SKILL.md) | The model + schema registry (used by `deployment-choice.yaml`) |

<!-- generated: 2026-07-29; do not hand-edit -->
