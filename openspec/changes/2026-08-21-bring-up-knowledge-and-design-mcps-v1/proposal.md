# Change: 2026-08-21-bring-up-knowledge-and-design-mcps-v1

## Why

The `agent-platform-cluster` spec (8-stack observability + memory +
LLM-routing substrate per `openspec/specs/agent-platform-cluster/spec.md`)
mandates that all 8 stacks be deployed together: lakehouse +
litellm + langfuse + mlflow + logfire + cognee + graphiti + lancedb.
The `agent-memory-systems` spec (5-backend memory layer per
`openspec/specs/agent-memory-systems/spec.md`) declares Cognee +
Graphiti + LanceDB + FalkorDB + Memgraph as the canonical memory
cascade.

Per the 2026-06-28 research program output, the **5 agent-facing
memory backends** are: Cognee (structured KG, port 8100), Graphiti
(temporal KG, port 8000), LanceDB (vector RAG, port 8002), FalkorDB
(vector + graph hybrid, port 8003), Memgraph (production graph,
port 7687). The `agent-memory-systems` spec defines a cascade where
the first available backend wins; the documented intent is for
Cognee + Graphiti to be the canonical production deployment.

Today, **neither `cognee` nor `graphiti` MCP servers are wired** in
`opencode.json` or `.mcp.json` (both are `enabled: false`). The
`cognee` and `graphiti` Docker stacks at `bonneagar/stacks/cognee/`
and `bonneagar/stacks/graphiti/` are also not yet promoted to the
full 6-file GOLD_STANDARD pattern.

Additionally, the in-house `design-system-server.py` MCP server
(513 LOC at `web/apps/cianfhoghlaim-leaving-cert/apps/web/packages/mcp/`)
is fully implemented with 4 self-heal tools (`tokens_get`,
`catalog_list`, `catalog_render`, `storybook_stories`) per R23 of
`2026-07-18-british-isles-portal-activation-v3`, but is **never wired**
into either MCP config. This blocks the AG-UI self-heal loop.

This change brings all 3 (cognee + graphiti + design-system-server)
up as production MCP surfaces.

## What Changes

### 1. Wire `cognee` MCP

- Flip `enabled: false → true` in `opencode.json` for the `cognee`
  entry (lines 246-258)
- Verify the Cognee Docker stack is reachable at `:8100` (per
  `bonneagar/stacks/cognee/`)
- Add `mcp:smoke:cognee` mise task that round-trips
  `cognee_search(query)` against a sample dataset
- Update `agent-memory-systems` spec to declare the MCP wiring

### 2. Wire `graphiti` MCP

- Flip `enabled: false → true` in `opencode.json` for the `graphiti`
  entry (lines 259-274)
- Verify Neo4j backend reachable at `:7687` (per
  `bonneagar/stacks/graphiti/`)
- Add `mcp:smoke:graphiti` mise task that round-trips
  `graphiti_add_episode` + `graphiti_search_` against a Neo4j test
  instance
- Update `agent-memory-systems` spec to declare the MCP wiring

### 3. Wire `design-system-server.py` MCP

- Add `design-system` entry to both `opencode.json` and `.mcp.json`
- The 4 tools (`tokens_get`, `catalog_list`, `catalog_render`,
  `storybook_stories`) SHALL be discoverable from any AG-UI agent
- Add `mcp:smoke:design-system` mise task that round-trips
  `catalog_render(component, props)` and verifies the
  `suggested_fix` self-heal response on a banned colour input
- Update `agentic-frontend-frameworks` spec to declare the MCP
  wiring

### 4. Promote `bonneagar/stacks/cognee/` and `bonneagar/stacks/graphiti/` to GOLD_STANDARD

Per `bonneagar/AGENTS.md` (cognee + graphiti are part of the 8-stack
cluster but are NOT yet promoted to GOLD_STANDARD).

## Dependencies

- `Blocked by: none`
- `Blocked by (soft): 2026-08-21-flip-observability-mcps-v1` (the
  agent-memory-systems cascade in `agent-platform-cluster` also
  depends on langfuse observability)
- `Affected repos: cianfhoghlaim, bonneagar`

## Cross-links

- Companion to: `2026-08-21-complete-browserbase-archive-and-crawl4ai-mcp-v1`
  (parallel — both add MCPs to the fleet)
- Companion to: `2026-08-21-flip-observability-mcps-v1` (the
  observability MCPs that observe the memory MCPs)
- Spec delta: `agent-memory-systems` (cognee + graphiti MCP wiring)
- Spec delta: `agentic-frontend-frameworks` (design-system MCP wiring)

## Requirements

See `tasks.md` for the 4-phase plan (A: cognee, B: graphiti,
C: design-system, D: GOLD_STANDARD promotion).

## Validation gate

- [ ] `openspec validate 2026-08-21-bring-up-knowledge-and-design-mcps-v1 --strict` exits 0
- [ ] `bun run mcp:smoke:cognee` passes (GraphRAG round-trip)
- [ ] `bun run mcp:smoke:graphiti` passes (temporal KG round-trip)
- [ ] `bun run mcp:smoke:design-system` passes (self-heal round-trip)
- [ ] `mise run stack-doctor:strict` passes for both `cognee` and `graphiti` stacks