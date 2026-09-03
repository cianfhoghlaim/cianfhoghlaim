# agents/api — Hono API Routes

> **The Hono API layer** for the 12-agent fleet. The 8 route
> categories + the 3 endpoint patterns. The routes layer is the
> unified API surface that the TanStack Start front-end, the
> Croílár portal, and the Túatha UI all consume.

## Priority quick reference

The 4 priority skills, the 4 priority commands, and the 1
priority openspec spec at a glance.

### Priority skills (4 of 53)

| Skill | When to load |
|:--|:--|
| [`hono`](../.agents/skills/hono/SKILL.md) | Hono API patterns (the canonical router) |
| [`agentic-frontend-frameworks`](../.agents/skills/agentic-frontend-frameworks/SKILL.md) | The front-end that consumes these routes |
| [`agent-registry`](../.agents/skills/agent-registry/SKILL.md) | The 12-agent fleet dispatch |
| [`tanstack-start`](../.agents/skills/tanstack-start/SKILL.md) | The TanStack Start front-end |

### Priority commands

```bash
# The canonical Hono router
python -c "from cianfhoghlaim.agents.api import router; print(len(router.routes))"
# Expected: 8 route categories

# The Croílár Convex layer (the consumer)
bun --cwd web/apps/croilar-portal dev
```

### Priority openspec spec

| Spec | One-liner |
|:--|:--|
| `agentic-frontend-frameworks` | The front-end + back-end integration |

## Overview

`agents/api/` is the **Hono API layer** for the agent fleet. It
houses:

- **`agents/api/index.ts`** — the canonical Hono router
- **`agents/api/curriculum_endpoint.py`** — the Python-side curriculum endpoint
- **`agents/api/agent_os/`** — the AgentOS surface (Agno AgentOS hosting)
- **`agents/api/routes/`** — the 8 route categories
- **`agents/api/_croilar_convex/`** — the Croílár Convex integration
- **`agents/api/_oideachais_api/`** — the Oideachais API integration
- **`agents/api/_oideachais_agent_os/`** — the Oideachais AgentOS integration
- **`agents/api/_crypteolas_tuatha/`** — the Crypteolas Tuatha integration
- **`agents/api/_croilar_api/`** — the Croílár API integration
- **`agents/api/_croilar_functions/`** — the Croílár functions integration
- **`agents/api/_rust_api/`** + **`agents/api/_rust_crates/`** — the Rust API integration (Túatha SpacetimeDB)

## The 8 route categories

| Route category | Module | Purpose |
|:--|:--|:--|
| 1 | `routes/curriculum` | The 5-nation curriculum search |
| 2 | `routes/translation` | The 6-Celtic-language translation |
| 3 | `routes/corpus` | The Dúchas + Gaois + UD + Canúint + Téarma corpus search |
| 4 | `routes/research` | The long-form research + citations |
| 5 | `routes/geospatial` | The LSOA / Data Zone spatial analysis |
| 6 | `routes/statistics` | The education metrics + benchmarking |
| 7 | `routes/curriculum_comparison` | The cross-nation curriculum mapping |
| 8 | `routes/agui` | The AG-UI streaming surface (CopilotKit consumer) |

Each route category exports a Hono `Router` that the canonical
`agents/api/index.ts` mounts under a unique path prefix.

## The 3 endpoint patterns

| Pattern | Method | Path | Body | Response |
|:--|:--|:--|:--|:--|
| **Query** | POST | `/api/<agent>/search` | `{query: str, ...}` | `{results: list, count: int}` |
| **Stream** | POST | `/api/<agent>/stream` | `{query: str, ...}` | SSE stream of `data: {...}\n\n` events |
| **Status** | GET | `/api/<agent>/health` | n/a | `{status: "healthy", agent: str, ...}` |

The 3 patterns are the canonical contract that the front-end
consumers (TanStack Start, Croílár, Túatha UI) all use.

## Routing to agents

Each route category wraps one or more agents from `AGENT_REGISTRY`.
The dispatch logic is in the route handler:

```typescript
import { AGENT_REGISTRY } from "cianfhoghlaim/agents/agent_registry";

const handler = async (c: Context) => {
  const { query } = await c.req.json();
  const agentName = c.req.param("agent");
  const wiring = AGENT_REGISTRY[agentName];
  if (!wiring) {
    return c.json({ error: "agent not found" }, 404);
  }
  const result = await dispatch(wiring, query);
  return c.json(result);
};
```

The `dispatch` function is a thin wrapper around the canonical
`agents/_workflow_handlers.py` dispatchers.

## Quick routing — "I want to add X, where do I go?"

| If you want to... | Look at... |
|:--|:--|
| Add a new route category | `agents/api/routes/<category>.ts` |
| Modify the canonical router | `agents/api/index.ts` |
| Add a new endpoint pattern | `agents/api/agent_os/` (the AgentOS surface) |
| Wire a new consumer (front-end) | `agents/api/_croilar_convex/` (Croílár) + `agents/api/_oideachais_api/` (Oideachais) |
| Add a Rust API surface | `agents/api/_rust_api/` + `agents/api/_rust_crates/` |
| Add the API to the agent-platform cluster | `bonneagar/komodo/procedures/deploy-agent-fleet-{bunchloch,arm1-oci}.toml` |

## Cross-references

- [`agents/AGENTS.md`](../AGENTS.md) — the quadrant overview
- [`agents/tools/AGENTS.md`](../tools/AGENTS.md) — the tools layer
- [`agents/meaisinfhoghlaim/AGENTS.md`](../meaisinfhoghlaim/AGENTS.md) — the OCR/HTR sub-package
- [`web/apps/_oideachais_apps/AGENTS.md`](../../web/apps/_oideachais_apps/AGENTS.md) — the Oideachais front-end
- [`web/apps/_croilar_apps/AGENTS.md`](../../web/apps/_croilar_apps/AGENTS.md) — the Croílár front-end