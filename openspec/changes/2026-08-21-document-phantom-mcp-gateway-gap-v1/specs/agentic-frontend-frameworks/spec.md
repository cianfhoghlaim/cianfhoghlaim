# Delta: agentic-frontend-frameworks

## ADDED Requirements

### Requirement: Phantom MCP gateway is documented, not advertised

The system SHALL NOT advertise an MCP gateway route that does not
work. The Hono route at
`web/apps/croilar-portal/src/routes/api/mcp.gateway.ts` proxies
requests to LiteLLM; if LiteLLM does not currently proxy MCPs, the
file SHALL carry a `KNOWN-ISSUE` comment explaining the gap, and
the `fetch(${LITELLM_BASE_URL}/mcp/${server})` call SHALL carry an
inline `TODO(mcp-bridge)` marker.

This rule SHALL be enforced by the `mise run lint:mcp-gateway` CI
gate, which fails the build if the `LITELLM_BASE_URL` is referenced
in `mcp.gateway.ts` without the `KNOWN-ISSUE` comment.

#### Scenario: A new developer reads the phantom gateway

- **GIVEN** this change has been archived
- **WHEN** a new developer reads `web/apps/croilar-portal/src/routes/api/mcp.gateway.ts`
- **THEN** they see the `KNOWN-ISSUE` comment block explaining that
  LiteLLM does not currently proxy MCPs
- **AND** they see the `TODO(mcp-bridge)` marker pointing to the
  future `2026-08-21-baml-orpc-mcp-typesafe-bridge-v1` change
- **AND** they do NOT assume MCP infrastructure exists that doesn't

#### Scenario: The CI gate catches a regression

- **GIVEN** a developer removes the `KNOWN-ISSUE` comment from
  `mcp.gateway.ts` (e.g. during a refactor)
- **WHEN** `mise run lint:mcp-gateway` runs as part of CI
- **THEN** the task fails with "KNOWN-ISSUE comment missing in
  `web/apps/croilar-portal/src/routes/api/mcp.gateway.ts`"
- **AND** the CI build fails

### Requirement: The phantom gateway will be replaced by the BAML → oRPC → MCP bridge

The phantom gateway at `mcp.gateway.ts` SHALL be replaced by a real
Hono → MCP bridge per the (future)
`2026-08-21-baml-orpc-mcp-typesafe-bridge-v1` change. When that
change ships, the `KNOWN-ISSUE` comment will be removed, the
`TODO(mcp-bridge)` marker will be deleted, and the file will become
a real proxy that fans out to the 12+ enabled MCPs.

#### Scenario: The phantom gateway is replaced by the bridge

- **GIVEN** `2026-08-21-baml-orpc-mcp-typesafe-bridge-v1` has been
  archived
- **WHEN** the developer opens `mcp.gateway.ts`
- **THEN** the `KNOWN-ISSUE` comment is gone
- **AND** the `TODO(mcp-bridge)` marker is gone
- **AND** the `fetch(${LITELLM_BASE_URL}/mcp/${server})` call has
  been replaced with the real bridge logic
- **AND** `mise run lint:mcp-gateway` is updated to allow the
  replacement (or removed entirely)