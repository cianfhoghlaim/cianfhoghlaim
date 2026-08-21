# Change: 2026-08-21-document-phantom-mcp-gateway-gap-v1

## Why

The Hono route at
`web/apps/croilar-portal/src/routes/api/mcp.gateway.ts` (142 LOC)
claims to proxy requests through LiteLLM to 25+ MCP servers:

```typescript
const response = await fetch(`${LITELLM_BASE_URL}/mcp/${server}`, {
  method: "POST",
  ...
});
```

However, **LiteLLM does not currently proxy MCPs at
`${LITELLM_BASE_URL}/mcp/{server}`**. The gateway endpoint is a
placeholder. The 25+ MCP servers it claims to expose
(`browserbase`, `chrome-devtools`, `firecrawl-mcp`, `cognee-mcp`,
`qdrant`, `memgraph`, `dagster-mcp`, `dlt-workspace`, `codeolas`,
`chunkhound`, `docker-mcp`, `postgres`, `clickhouse`) are NOT
discoverable through this route today.

This creates a **phantom gateway** that misleads consumers (per the
`mcp-servers.md` reference doc section 3.4):
- CopilotKit frontends that call this route will receive 404s or
  empty tool listings
- The `mcp:smoke:mcp-gateway` task that calls this endpoint will
  fail silently
- New developers who read the gateway file will assume MCP
  infrastructure exists that doesn't

This change documents the gap with a top-of-file `KNOWN-ISSUE`
header + a `TODO(mcp-bridge)` marker, and adds a CI lint task that
fails if the phantom LiteLLM URL is referenced without the new
comment.

The future fix is the **BAML → oRPC → MCP type-safe bridge** per
the `2026-08-21-baml-orpc-mcp-typesafe-bridge-v1` change (referenced
in the planning conversation; not yet drafted). When that change
ships, the phantom gateway will be replaced with a real Hono→MCP
proxy that fans out to the 12+ enabled MCPs.

## What Changes

### 1. Add `KNOWN-ISSUE` header to `mcp.gateway.ts`

The file SHALL carry a top-of-file comment (after the existing
`/** ... */` docstring) explaining the gap:

```
// =============================================================================
// KNOWN-ISSUE (2026-08-21): LiteLLM does not currently proxy MCPs at
// `${LITELLM_BASE_URL}/mcp/${server}`. This gateway is a placeholder.
// See: openspec/changes/2026-08-21-document-phantom-mcp-gateway-gap-v1/
// Future: replaced by the BAML → oRPC → MCP type-safe bridge per
// `2026-08-21-baml-orpc-mcp-typesafe-bridge-v1` (not yet drafted).
// =============================================================================
```

### 2. Add `TODO(mcp-bridge)` marker to the `fetch()` line

The line that calls `fetch(${LITELLM_BASE_URL}/mcp/${server})` SHALL
carry an inline `// TODO(mcp-bridge): see KNOWN-ISSUE above` comment.

### 3. New `mise run lint:mcp-gateway` task

A CI gate that parses `mcp.gateway.ts` and fails if:
- The `LITELLM_BASE_URL` is referenced without the `KNOWN-ISSUE`
  comment in the same file
- The `TODO(mcp-bridge)` marker is missing from the `fetch()` call

## Dependencies

- `Blocked by: none`
- `Blocked by (soft): 2026-08-21-baml-orpc-mcp-typesafe-bridge-v1`
  (future change that will replace this gateway; not yet drafted)
- `Affected repos: cianfhoghlaim`

## Cross-links

- Future: `2026-08-21-baml-orpc-mcp-typesafe-bridge-v1` (the
  replacement — not yet drafted)
- Spec delta: `agentic-frontend-frameworks` (the Hono API gateway
  pattern; this change documents a known gap in one route)

## Requirements

See `tasks.md` for the 3-task plan.

## Validation gate

- [ ] `openspec validate 2026-08-21-document-phantom-mcp-gateway-gap-v1 --strict` exits 0
- [ ] `mise run lint:mcp-gateway` exits 0
- [ ] Removing the `KNOWN-ISSUE` comment causes `mise run lint:mcp-gateway` to fail