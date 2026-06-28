# Cloudflare Workers — KCG Summary

## What It Is
Cloudflare Workers is a serverless edge computing platform that runs JavaScript/TypeScript at Cloudflare's global edge network. Better Auth Cloudflare provides seamless integration of BetterAuth authentication with Cloudflare's ecosystem — D1 (SQLite), Hyperdrive (Postgres/MySQL acceleration), KV (key-value storage), R2 (object storage), and geolocation services. The TanStack Start on Cloudflare example demonstrates deploying a full-stack React SSR application to Workers.

## Why This Matters for Kings' College Galway
The Cianfhoghlaim project targets Cloudflare Workers as the primary deployment platform for `sruth/oideachais/web/` (TanStack Start frontend) and all API layers. The BetterAuth Cloudflare integration's D1 + KV + R2 pattern directly maps to the project's auth infrastructure. The CLI tooling for schema generation and migration provides the blueprint for the project's own DevX scripts. TanStack Start on Cloudflare demonstrates SSR on the edge — the exact deployment model for all sruth/ frontends. The `cloudflare-data-ops` playground validates data pipeline patterns at the edge.

## Key Patterns Preserved
- **docs/web/cloudflare/better-auth-cloudflare/README.md** — Full BetterAuth + Cloudflare integration: D1, Hyperdrive, KV, R2, geolocation, CLI tooling, Hono/OpenNextJS examples
- **docs/web/cloudflare/better-auth-cloudflare/docs/r2.md** — R2 file storage guide for authenticated file management
- **docs/web/cloudflare/better-auth-cloudflare/cli/README.md** — CLI documentation for project generation, migrations, and schema management
- **docs/web/cloudflare/better-auth-cloudflare/cli/tests/integration/README.md** — CLI integration test patterns
- **docs/web/cloudflare/better-auth-cloudflare/examples/hono/README.md** — Hono + D1 + KV + BetterAuth on Workers example
- **docs/web/cloudflare/better-auth-cloudflare/examples/opennextjs/README.md** — OpenNextJS + D1 + KV + BetterAuth on Workers example
- **docs/web/cloudflare/tanstack-start-on-cloudflare/README.md** — TanStack Start SSR on Cloudflare Workers with server functions, middleware, query integration
- **docs/web/cloudflare/tanstack-start-on-cloudflare/CLAUDE.md** — Agent instructions for TanStack Start on Cloudflare development
- **docs/web/cloudflare/tanstack-start-on-cloudflare/.claude/agents/shadcn-ui-builder.md** — Shadcn UI builder agent instructions
- **docs/web/cloudflare/tanstack-start-on-cloudflare/.claude/agents/tanstack-server-functions.md** — TanStack server functions agent instructions
- **docs/web/cloudflare/cloudflare-data-ops/README.md** — Cloudflare data operations playground
- **docs/web/cloudflare/cloudflare-data-ops/apps/user-application/README.md** — User application example in data-ops

## Source Files
Full example repository source code removed (2026-06-06). Original repos available at <https://github.com/better-auth> and <https://github.com/tanstack>. Documentation and architectural patterns retained.

## What Was Removed
- All TypeScript/JavaScript source files (.ts, .tsx, .js, .jsx)
- All configuration files (package.json, wrangler.jsonc, tsconfig.json, vite.config.ts, etc.)
- All CSS/Styles (.css)
- All build artifacts and lock files (node_modules/, dist/)
- All SQL and database files (.sql)
- All image/assets
- .git directories
- All non-.md files
