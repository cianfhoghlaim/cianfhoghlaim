# `web/` — Agentic Frontend Apps

The Cianfhoghlaim web surface — 7 frontend apps + the Hono API gateway,
all routed through the centralized model registry + the deployment
control panel.

| App | Surface | Stack |
|:--|:--|:--|
| `apps/cianfhoghlaim-web/` | The public web app (TanStack Start) | React 19 + RSC + Hono |
| `apps/tuatha-ui/` | The Túatha educational MMO | Babylon.js + AG-UI |
| `apps/croilar-web/` | The Croílár multi-persona portfolio | TanStack Start + Convex |
| `apps/croilar-portal/` | The Croílár portfolio dashboard | TanStack Start |
| `apps/tuatha-demo/` | The Tuatha Babylon.js demo | Babylon.js + AG-UI |
| `apps/game_showcase/` | The web game showcase | (varies) |
| `apps/cianfhoghlaim-mcp-filesystem/` | The filesystem MCP server | MCP + Hono |
| `hono-api/` | The Hono API gateway | Hono + oRPC |

For agent-routing context (when to load which skill, which adjacent
openspec spec, which mise task), see [`AGENTS.md`](AGENTS.md).
For the canonical 4-surface architecture diagram, see
[`../openspec/specs/agentic-frontend-frameworks/spec.md`](../openspec/specs/agentic-frontend-frameworks/spec.md).

## Developer onboarding

```bash
mise run ts:install       # bun install across all workspaces
mise run ts:typecheck     # bunx turbo run typecheck
mise run ts:lint          # bunx turbo run lint
mise run schema:generate  # regenerate the Zod + TanStack DB schemas (CI drift gate)
```
