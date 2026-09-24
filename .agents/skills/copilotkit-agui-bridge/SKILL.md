---
name: copilotkit-agui-bridge
description: CopilotKit + AG-UI protocol + TanStack AI + Hono wire-up guide. Use when wiring an agent runtime to a TanStack Start SPA via CopilotKit + AG-UI events, when adding a new CopilotKit action, or when bridging the Python agent_registry_runtime to the TS front-end. Triggers: 'copilotkit', 'ag-ui', 'agui', 'tanstack ai', 'agent registry', 'AG-UI handshake', 'copilotkit action', 'agent events'.
---

# CopilotKit + AG-UI Bridge Router

Per the 2026-09-24-web-agentic-deep-refactor-v1 change. The bridge
between the Python agent fleet (the 24-agent fleet + the 3 Pillar
orchestrators) and the TanStack Start SPA via CopilotKit + AG-UI
events.

## The two surfaces

1. **TS side** (the SPA + Hono API):
   - `web/apps/cianfhoghlaim-web/apps/api/src/copilotkit/` (the
     CopilotKit runtime + the 18 canonical actions)
   - `web/hono-api/src/routes/copilotkit/registry.ts` (the agent
     registry end-to-end wire-up)
   - `web/apps/_shared/copilotkit/` (the canonical shared module)

2. **Python side** (the agents + the runtime):
   - `agents/integrations/agent_registry_runtime.py` (the 3 canonical
     helpers: `register_all_agents_with_copilotkit`,
     `collect_all_agui_events`, `build_copilotkit_runtime_config`)
   - `agents/agent_registry.py` (the 24-agent fleet registry)

## The wire-up (3 layers)

### Layer 1 — In-process dev fallback
`web/apps/cianfhoghlaim-web/apps/api/src/copilotkit/_base.ts` exports
`devFallbackConfig` which is used by the Hono route in dev mode (when
`NODE_ENV !== "production"` or `COPILOTKIT_DEV_MODE=1`). No subprocess
call — works offline.

### Layer 2 — Production subprocess bridge
`callAgentRegistryRuntime()` uses `subprocess.execFile` (NOT `exec`)
to invoke `python -c "..."` and return the parsed JSON config. The
Python expression is a fixed string — no user input is interpolated.

### Layer 3 — AG-UI protocol handshake
`POST /api/copilotkit/registry/handshake` acknowledges the SPA's
register event + returns `{ acknowledged, protocol, runtime_config,
registered_agents, collected_events, handshake_with }`.

## Adding a new CopilotKit action

1. Define the tool in `web/apps/cianfhoghlaim-web/apps/api/src/copilotkit/actions.ts`
2. Add it to `ALL_ACTIONS` at the bottom of the file
3. The runtime's `/actions` endpoint automatically exposes it
4. The leaving-cert app re-exports from the shared module if it's
   leaving-cert specific

Example:
```ts
export const getMyNewAction = defineTool({
  name: "getMyNewAction",
  description: "...",
  parameters: [...],
  handler: async (params) => {
    return await db.execute(`SELECT ...`, [...]);
  },
});
ALL_ACTIONS.push(getMyNewAction);
```

## When to use the dev fallback

```bash
# Dev: no Python needed
NODE_ENV=development bun run dev

# Prod: Python required
NODE_ENV=production COPILOTKIT_DEV_MODE=0 bun run dev

# Canary: force dev even in prod (smoke test)
COPILOTKIT_DEV_MODE=1 bun run dev
```

## Reference

- `web/AGENTS.md` (the web + agentic surface declaration)
- `agents/integrations/agent_registry_runtime.py` (the Python runtime helpers)
- `web/apps/_shared/copilotkit/README.md` (the shared module guide)
- `agents/meaisinfhoghlaim/_shared/` (the Pydantic I/O + ADK 2 types)
- `docs/google_examples/adk2-tutorial/` (the 10-level ADK 2 walkthrough)
- `docs/google_examples/agent-valley-archive/` (the AG-UI memory ladder twin)
