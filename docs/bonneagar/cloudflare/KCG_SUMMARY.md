# Cloudflare — KCG Summary

## What It Is
A collection of Cloudflare Workers ecosystem examples and templates: better-auth-cloudflare (seamless authentication integration for Cloudflare Workers with D1, KV, R2, Hyperdrive, and geolocation), TanStack Start on Cloudflare (production-ready full-stack React template with server functions and edge deployment), and cloudflare-data-ops (Cloudflare data operations playground).

## Why This Matters for Kings' College Galway
Cloudflare Workers is our edge compute platform for the `oideachais-web` frontend, serving bilingual curriculum content globally with sub-50ms latency. The better-auth-cloudflare pattern provides the authentication layer for our student and teacher portals, with D1-backed user sessions and R2 storage for user-uploaded learning materials. The TanStack Start template is the architectural foundation of our React Server Components strategy — enabling type-safe server functions, streaming SSR, and edge-rendered curriculum pages. The D1 + Hyperdrive database pattern directly informs our education data caching layer that sits between the edge and our MotherDuck analytics backend.

## Key Patterns Preserved
- `better-auth-cloudflare/README.md` — Full auth library documentation, features, setup, examples
- `better-auth-cloudflare/docs/r2.md` — R2 storage integration documentation
- `better-auth-cloudflare/examples/hono/README.md` — Hono framework example
- `better-auth-cloudflare/examples/opennextjs/README.md` — OpenNextJS example
- `better-auth-cloudflare/cli/README.md` — CLI tool documentation
- `better-auth-cloudflare/cli/tests/integration/README.md` — Integration test docs
- `tanstack-start-on-cloudflare/README.md` — Full template documentation
- `tanstack-start-on-cloudflare/CLAUDE.md` — Architecture guide for AI agents
- `tanstack-start-on-cloudflare/.claude/agents/shadcn-ui-builder.md` — UI builder agent
- `tanstack-start-on-cloudflare/.claude/agents/tanstack-server-functions.md` — Server functions agent
- `cloudflare-data-ops/README.md` — Data ops reference
- `cloudflare-data-ops/apps/user-application/README.md` — Application reference

## Source Files
Full source removed (2026-06-06), available at their respective GitHub repositories:
- better-auth-cloudflare: https://github.com/code-yeongyu/better-auth-cloudflare
- TanStack Start on Cloudflare: (community template)
- cloudflare-data-ops: (course playground)

## What Was Removed
TypeScript/JavaScript source code, React/Next.js components, build configuration (vite.config.ts, wrangler.toml, tailwind.config.ts), Drizzle ORM schemas, test files, npm/pnpm package files, Cloudflare Workers deployment scripts, CSS files, SVG assets, environment type definitions, database migration files, and all non-documentation files.
