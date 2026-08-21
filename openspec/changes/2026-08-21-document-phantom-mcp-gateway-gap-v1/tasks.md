# Tasks: 2026-08-21-document-phantom-mcp-gateway-gap-v1

## Phase A: Add `KNOWN-ISSUE` header + `TODO(mcp-bridge)` marker (1st priority)

- [ ] A.1 — Read `web/apps/croilar-portal/src/routes/api/mcp.gateway.ts` (already audited)
- [ ] A.2 — Insert the `KNOWN-ISSUE` comment block after the existing `/** ... */` docstring (around line 24)
- [ ] A.3 — Insert the `TODO(mcp-bridge): see KNOWN-ISSUE above` comment above the `fetch(${LITELLM_BASE_URL}/mcp/${server})` line (line 92)
- [ ] A.4 — Verify the file is still valid TypeScript (`bun run typecheck` passes for `web/apps/croilar/`)

## Phase B: New `mise run lint:mcp-gateway` CI gate (2nd priority)

- [ ] B.1 — Add the `lint:mcp-gateway` task to `mise.toml`
- [ ] B.2 — Implement the task as a shell script that:
  - Checks that `web/apps/croilar-portal/src/routes/api/mcp.gateway.ts` contains the `KNOWN-ISSUE` comment block
  - Checks that the `TODO(mcp-bridge)` marker is present on the `fetch()` line
  - Fails with a clear error message if either is missing
- [ ] B.3 — Wire the task into `.github/workflows/lint-mcp-gateway.yaml` (the CI workflow)

## Validation gate

- [ ] V.1 `openspec validate 2026-08-21-document-phantom-mcp-gateway-gap-v1 --strict` exits 0
- [ ] V.2 `mise run lint:mcp-gateway` exits 0 with the comments in place
- [ ] V.3 Removing the `KNOWN-ISSUE` comment causes `mise run lint:mcp-gateway` to fail
- [ ] V.4 `bun run typecheck` passes for `web/apps/croilar/`