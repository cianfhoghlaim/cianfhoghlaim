# Tasks: 2026-08-21-flip-observability-mcps-v1

## Phase A: Wire `langfuse` MCP (1st priority)

- [ ] A.1 — Flip `enabled: false → true` for the `langfuse` entry in `opencode.json` (lines 275-288)
- [ ] A.2 — Verify the Langfuse stack is reachable at `:3000` (check `LANGFUSE_HOST: http://localhost:3000`)
- [ ] A.3 — Verify `LANGFUSE_PUBLIC_KEY` and `LANGFUSE_SECRET_KEY` are hydrated from `.infisical.env` (lines for langfuse in `.infisical.env`)
- [ ] A.4 — Add `mcp:smoke:langfuse` mise task that round-trips `langfuse_get_trace(trace_id)` against a sample trace from a recent agent run
- [ ] A.5 — Wire `mise run lint:mcp-runtime` to invoke `bun run mcp:smoke:langfuse` for the langfuse MCP entry

## Phase B: Wire `infisical` MCP (2nd priority)

- [ ] B.1 — Populate `INFISICAL_CLIENT_ID`, `INFISICAL_SECRET`, and `INFISICAL_PROJECT_ID` in `.infisical.env` (replace the empty placeholders)
- [ ] B.2 — Run `bun run secrets:init` (a.k.a. `mise run secrets:init`) to sync the new credentials to the Infisical vault
- [ ] B.3 — Verify the credentials are resolvable at session start (`mise run secrets:exec -- env | grep INFISICAL_CLIENT_ID`)
- [ ] B.4 — Flip `enabled: false → true` for the `infisical` entry in `opencode.json` (lines 199-213)
- [ ] B.5 — Verify the Infisical stack is reachable at `:8081`
- [ ] B.6 — Add `mcp:smoke:infisical` mise task that round-trips a test secret (create `mcp-smoke-test-secret`, read it back, delete it)
- [ ] B.7 — Wire `mise run lint:mcp-runtime` to invoke `bun run mcp:smoke:infisical` for the infisical MCP entry

## Validation gate

- [ ] V.1 `openspec validate 2026-08-21-flip-observability-mcps-v1 --strict` exits 0
- [ ] V.2 `bun run mcp:smoke:langfuse` passes (trace retrieval round-trip)
- [ ] V.3 `bun run mcp:smoke:infisical` passes (secret mutation round-trip)
- [ ] V.4 `mise run secrets:exec -- env | grep INFISICAL_CLIENT_ID` returns a non-empty value
- [ ] V.5 `mise run lint:mcp-runtime` exits 0 (all 12 active MCPs pass their smoke tests)