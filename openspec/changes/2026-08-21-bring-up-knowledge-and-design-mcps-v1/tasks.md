# Tasks: 2026-08-21-bring-up-knowledge-and-design-mcps-v1

## Phase A: Wire `cognee` MCP (1st priority)

- [ ] A.1 — Flip `enabled: false → true` for the `cognee` entry in `opencode.json` (lines 246-258)
- [ ] A.2 — Verify the Cognee Docker stack is reachable at `:8100` (check `bonneagar/stacks/cognee/compose.yaml` is up via `mise run cic:meaisin:cognee-up`)
- [ ] A.3 — Verify the `COGNEE_API_URL` and `COGNEE_API_KEY` env vars resolve at session start (per the `infisical://dev-baile/cognee/api_key` reference in `opencode.json`)
- [ ] A.4 — Add `mcp:smoke:cognee` mise task that round-trips `cognee_search(query)` against a sample dataset (per the 5-step harness in `.agents/skills/agent-memory-systems/SKILL.md`)
- [ ] A.5 — Wire `mise run lint:mcp-runtime` to invoke `bun run mcp:smoke:cognee` for the cognee MCP entry

## Phase B: Wire `graphiti` MCP (2nd priority)

- [ ] B.1 — Flip `enabled: false → true` for the `graphiti` entry in `opencode.json` (lines 259-274)
- [ ] B.2 — Verify Neo4j backend reachable at `:7687` (per `NEO4J_URI: bolt://localhost:7687` in `opencode.json`)
- [ ] B.3 — Add `mcp:smoke:graphiti` mise task that round-trips `graphiti_add_episode` + `graphiti_search_` against a Neo4j test instance
- [ ] B.4 — Wire `mise run lint:mcp-runtime` to invoke `bun run mcp:smoke:graphiti` for the graphiti MCP entry

## Phase C: Wire `design-system-server.py` MCP (3rd priority)

- [ ] C.1 — Add `design-system` entry to `opencode.json` (stdio variant via `python web/apps/cianfhoghlaim-leaving-cert/apps/web/packages/mcp/design-system-server.py --port 7777`)
- [ ] C.2 — Add `design-system` entry to `.mcp.json`
- [ ] C.3 — Verify the 4 tools (`tokens_get`, `catalog_list`, `catalog_render`, `storybook_stories`) are discoverable
- [ ] C.4 — Add `mcp:smoke:design-system` mise task that round-trips `catalog_render(component, props)` with a banned colour input and verifies the `suggested_fix` self-heal response
- [ ] C.5 — Wire `mise run lint:mcp-runtime` to invoke `bun run mcp:smoke:design-system` for the design-system MCP entry

## Phase D: Promote `cognee` and `graphiti` stacks to GOLD_STANDARD (4th priority)

- [ ] D.1 — Audit `bonneagar/stacks/cognee/` against the 6-file GOLD_STANDARD pattern; add missing files
- [ ] D.2 — Audit `bonneagar/stacks/graphiti/` against the 6-file GOLD_STANDARD pattern; add missing files
- [ ] D.3 — Run `mise run stack-doctor:strict` and confirm both stacks pass

## Validation gate

- [ ] V.1 `openspec validate 2026-08-21-bring-up-knowledge-and-design-mcps-v1 --strict` exits 0
- [ ] V.2 `bun run mcp:smoke:cognee` passes (GraphRAG round-trip)
- [ ] V.3 `bun run mcp:smoke:graphiti` passes (temporal KG round-trip)
- [ ] V.4 `bun run mcp:smoke:design-system` passes (self-heal round-trip)
- [ ] V.5 `mise run stack-doctor:strict` passes for both `cognee` and `graphiti` stacks
- [ ] V.6 `mise run lint:mcp-runtime` exits 0 (all 12 active MCPs pass their smoke tests)