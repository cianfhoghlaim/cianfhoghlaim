# TanStack — KCG Summary

## What It Is
TanStack is a family of open-source TypeScript libraries for building modern web applications. TanStack Start is a full-stack React framework with SSR, file-based routing, and server functions. TanStack AI provides cross-language AI chat infrastructure with SSE streaming, tool execution, and multi-framework client adapters. TanStack DB (formerly TanStack Store) offers offline-capable data sync.

## Why This Matters for Kings' College Galway
The Cianfhoghlaim project uses TanStack Start as its primary frontend framework for `tuath/` (Celtic educational MMO), `sruth/oideachais/` (Irish education platform), and `aleyum/` (developer portal). The TanStack AI patterns — particularly the SSE streaming bridge between Python/TypeScript backends and the multi-framework frontend adapters — directly inform the AG-UI streaming architecture used across all sruth/ frontends. TanStack DB's offline-first patterns inform the SpacetimeDB integration in `tuath/`. The embedded dashboards pattern is used for Dagster and marimo integration.

## Key Patterns Preserved
- **docs/web/tanstack/tanstack_ai/README.md** — Cross-language AI infrastructure: TypeScript/Python/PHP backends with SSE streaming, tool execution, and vanilla/React/Svelte/Vue frontends
- **docs/web/tanstack/tanstack_ai/ts-react-chat/README.md** — Full-stack TypeScript chat with TanStack Start, automatic tool execution loop
- **docs/web/tanstack/tanstack_ai/ts-group-chat/README.md** — Multi-user WebSocket chat with Claude integration and online presence
- **docs/web/tanstack/tanstack_ai/vanilla-chat/CHANGELOG.md** — Vanilla JS client changelog
- **docs/web/tanstack/tanstack_ai/vanilla-chat/README.md** — Framework-free chat frontend compatible with Python/PHP backends
- **docs/web/tanstack/tanstack_ai/python-fastapi/README.md** — Python FastAPI SSE backend bridging Anthropic/OpenAI to TanStack stream format
- **docs/web/tanstack/tanstack_ai/php-slim/README.md** — PHP Slim SSE backend for TanStack AI client protocol
- **docs/web/tanstack/tanstack_ai/ts-svelte-chat/CHANGELOG.md** — Svelte chat client changelog
- **docs/web/tanstack/tanstack_ai/ts-svelte-chat/README.md** — Svelte frontend for TanStack AI
- **docs/web/tanstack/tanstack_ai/ts-solid-chat/README.md** — SolidJS frontend for TanStack AI
- **docs/web/tanstack/tanstack_ai/ts-vue-chat/CHANGELOG.md** — Vue chat client changelog
- **docs/web/tanstack/tanstack_ai/ts-vue-chat/README.md** — Vue frontend for TanStack AI
- **docs/web/tanstack/tanstack_db/offline-transactions/README.md** — Offline-first data patterns with conflict resolution
- **docs/web/tanstack/tanstack_db/paced-mutations-demo/CHANGELOG.md** — Paced mutation demo changelog
- **docs/web/tanstack/tanstack_db/projects/AGENT.md** — Agent instructions for TanStack DB project
- **docs/web/tanstack/tanstack_db/projects/README.md** — TanStack DB project overview
- **docs/web/tanstack/tanstack_db/todo/CHANGELOG.md** — Todo app changelog (Postgres + Electric + TrailBase)
- **docs/web/tanstack/tanstack_db/todo/README.md** — Todo example with Postgres sync
- **docs/web/tanstack/tanstack-db-electric-sql-demo/README.md** — Electric SQL sync demo with TanStack DB
- **docs/web/tanstack/embedded-dashboards/README.md** — Embedding Dagster + marimo dashboards in TanStack Start with BetterAuth auth proxy
- **docs/web/tanstack/mcp-auth/README.md** — MCP authentication patterns
- **docs/web/tanstack/mcp-auth/.github/instructions/import-event.instructions.md** — GitHub import event instructions
- **docs/web/tanstack/mcp-auth/.github/copilot-instructions.md** — Copilot instructions for MCP auth
- **docs/web/tanstack/mcp-ui-on-tanstack/README.md** — MCP UI integration on TanStack Start

## Source Files
Full example repository source code removed (2026-06-06). Original repos available at GitHub under the TanStack organization. Only documentation and architectural patterns retained.

## What Was Removed
- All TypeScript/JavaScript source files (.ts, .tsx, .js, .jsx)
- All CSS/Styles (.css, .scss)
- All configuration files (package.json, tsconfig.json, wrangler.jsonc, .env.example, vite.config.ts, turbo.json, etc.)
- All build artifacts and lock files (node_modules/, dist/, .turbo/)
- All SQL and database files (.sql)
- All Docker files (Dockerfile, docker-compose.yml)
- All image/assets (.png, .svg, etc.)
- .git directories
- All non-.md files
