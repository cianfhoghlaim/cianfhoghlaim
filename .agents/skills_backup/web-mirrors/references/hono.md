# Hono — KCG Summary

## What It Is
Hono (Japanese for "flame") is a lightweight, ultra-fast web framework for building APIs and web applications at the edge. It runs on Cloudflare Workers, Deno, Bun, and Node.js with a single codebase. Its minimal footprint and middleware-based architecture make it ideal for serverless edge computing.

## Why This Matters for Kings' College Galway
Hono is used as the HTTP framework throughout the Cianfhoghlaim stack: API gateways on Cloudflare Workers, MCP server endpoints, and the `api-unified` example that combines MCP + oRPC + OpenAPI + AI streaming in a single Hono app. The `cloudflare-auth-worker` shows the auth pattern used for securing API routes. The `duckdb-api` example demonstrates querying analytical databases from edge functions — the pattern used for curriculum analytics in `sruth/cianfhoghlaim/`. The `hn-summary` example shows AI-powered content summarization at the edge, directly informing the content generation pipelines.

## Key Patterns Preserved
- **docs/web/hono/cloudflare-auth-worker/README.md** — Authentication worker with Hono on Cloudflare Workers
- **docs/web/hono/duckdb-api/README.md** — DuckDB query API via Hono on the edge
- **docs/web/hono/hn-summary/README.md** — Hacker News summarization with Cloudflare Workers AI, KV, and Hono

## Source Files
Full example repository source code removed (2026-06-06). Original repos available at <https://github.com/honojs>. Documentation and architectural patterns retained.

## What Was Removed
- All TypeScript/JavaScript source files (.ts, .tsx, .js, .jsx)
- All configuration files (package.json, wrangler.jsonc, tsconfig.json, etc.)
- All CSS/Styles
- All build artifacts and lock files (node_modules/, dist/)
- All SQL and data files
- .git directories
- All non-.md files
