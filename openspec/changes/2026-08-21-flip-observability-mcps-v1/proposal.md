# Change: 2026-08-21-flip-observability-mcps-v1

## Why

The `agent-observability` spec (per
`openspec/specs/agent-observability/spec.md`) declares 5 layers of
observability for the agent fleet: Langfuse + Logfire + MLflow +
RAGAS + structlog. Today, **Langfuse is the only observability layer
with a wired MCP server** — and even that is `enabled: false` in
`opencode.json` (lines 275-288).

The Langfuse secrets (`LANGFUSE_PUBLIC_KEY` + `LANGFUSE_SECRET_KEY`)
are ALREADY hydrated in `.infisical.env` (lines 1194), so flipping
the MCP entry to `enabled: true` is a near-zero-cost change.

The Infisical MCP server is similarly `enabled: false` (lines 199-213)
but is blocked on the missing `INFISICAL_CLIENT_ID/SECRET/PROJECT_ID`
credentials (currently empty in `.infisical.env`). This change
populates those credentials and flips the entry to enabled.

The Langfuse MCP server exposes 3+ tools
(`langfuse_get_trace`, `langfuse_get_traces`, `langfuse_get_prompt`)
that complement the existing 5-layer observability contract by
adding a 6th layer: runtime MCP-based trace retrieval.

The Infisical MCP server exposes 3 tools
(`infisical_get_secret`, `infisical_list_secrets`,
`infisical_create_secret`) that enable runtime secret mutation
(currently secrets are only hydrated at `cd` time via mise hooks).

## What Changes

### 1. Wire `langfuse` MCP

- Flip `enabled: false → true` in `opencode.json` for the `langfuse`
  entry (lines 275-288)
- Verify the Langfuse stack is reachable at `:3000` (per
  `LANGFUSE_HOST: http://localhost:3000` in `opencode.json`)
- Add `mcp:smoke:langfuse` mise task that round-trips
  `langfuse_get_trace(trace_id)` against a sample trace
- Update `agent-observability` spec to declare the MCP wiring as a
  6th observability layer

### 2. Wire `infisical` MCP

- Populate `INFISICAL_CLIENT_ID`, `INFISICAL_SECRET`, and
  `INFISICAL_PROJECT_ID` in `.infisical.env`
- Run `bun run secrets:init` to sync to the Infisical vault
- Flip `enabled: false → true` in `opencode.json` for the `infisical`
  entry (lines 199-213)
- Verify the Infisical stack is reachable at `:8081` (per
  `INFISICAL_HOST_URL: http://localhost:8081` in `opencode.json`)
- Add `mcp:smoke:infisical` mise task that round-trips a test secret
  (create + read + delete)

## Dependencies

- `Blocked by: none`
- `Blocked by (soft): 2026-08-21-bring-up-knowledge-and-design-mcps-v1`
  (the agent-memory-systems cascade observes via langfuse)
- `Affected repos: cianfhoghlaim`

## Cross-links

- Companion to: `2026-08-21-bring-up-knowledge-and-design-mcps-v1`
  (the memory MCPs observed by langfuse)
- Companion to: `2026-08-21-complete-browserbase-archive-and-crawl4ai-mcp-v1`
  (parallel — adds MCPs to the fleet)
- Spec delta: `agent-observability` (Langfuse MCP wiring + Infisical
  MCP wiring)

## Requirements

See `tasks.md` for the 2-phase plan (A: Langfuse, B: Infisical).

## Validation gate

- [ ] `openspec validate 2026-08-21-flip-observability-mcps-v1 --strict` exits 0
- [ ] `bun run mcp:smoke:langfuse` passes (trace retrieval round-trip)
- [ ] `bun run mcp:smoke:infisical` passes (secret mutation round-trip)
- [ ] `mise run secrets:exec -- env | grep INFISICAL_CLIENT_ID` returns a non-empty value