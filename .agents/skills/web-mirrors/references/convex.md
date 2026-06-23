# Convex — KCG Summary

## What It Is
Convex is a real-time backend-as-a-service platform that combines a reactive database, serverless functions, and real-time subscriptions. All code is TypeScript; the database provides automatic reactivity (UI re-renders when data changes without polling). Convex handles state management, file storage, scheduling, and authentication — all within a single TypeScript codebase deployed to Convex's managed infrastructure.

## Why This Matters for Kings' College Galway
The Cianfhoghlaim project uses Convex as the primary real-time backend for `oideachais/` (curriculum data, student progress), `tuath/` (game state, quest tracking), and `crypteolas/` (real-time DeFi data). The `better-auth-convex` integration shows how to combine Convex's reactivity with BetterAuth's session management — the exact pattern used across all sruth/ frontends. The generative AI canvas example (SolidJS + Cloudflare Workers + Convex) demonstrates the multi-service architecture used in `tuath/`. The image generation system guide informs the AI agent orchestration patterns used for educational content generation.

## Key Patterns Preserved
- **docs/web/convex/better-auth-convex/README.md** — Convex + BetterAuth integration overview with live demo
- **docs/web/convex/better-auth-convex/CONTRIBUTING.md** — Contribution guide for convex-better-auth
- **docs/web/convex/better-auth-convex/CHANGELOG.md** — Version history for better-auth-convex
- **docs/web/convex/better-auth-convex/docs/README.md** — Documentation site guide
- **docs/web/convex/better-auth-convex/examples/README.md** — Example app overview (Next.js, React, TanStack)
- **docs/web/convex/better-auth-convex/examples/next/README.md** — Next.js + Convex + BetterAuth example
- **docs/web/convex/better-auth-convex/examples/next/convex/README.md** — Convex backend for Next.js example
- **docs/web/convex/better-auth-convex/examples/react/README.md** — React SPA + Convex + BetterAuth example
- **docs/web/convex/better-auth-convex/examples/react/convex/README.md** — Convex backend for React example
- **docs/web/convex/better-auth-convex/examples/tanstack/README.md** — TanStack Start + Convex + BetterAuth example
- **docs/web/convex/better-auth-convex/examples/tanstack/convex/README.md** — Convex backend for TanStack example
- **docs/web/convex/convex-cloudflare-workers-solid-tanstack-spa-betterauth-D1-KV/README.md** — Generative AI Canvas: multi-service architecture with SolidJS, Workers, Convex, D1, KV, R2, BetterAuth
- **docs/web/convex/convex-cloudflare-workers-solid-tanstack-spa-betterauth-D1-KV/convex/README.md** — Convex schema and functions for generative canvas
- **docs/web/convex/convex-cloudflare-workers-solid-tanstack-spa-betterauth-D1-KV/DRAG_IMPROVEMENTS.md** — Canvas drag interaction improvements
- **docs/web/convex/convex-cloudflare-workers-solid-tanstack-spa-betterauth-D1-KV/image-generation-system.md** — AI image generation pipeline design
- **docs/web/convex/convex-cloudflare-workers-solid-tanstack-spa-betterauth-D1-KV/.windsurf/rules/main.md** — Windsurf IDE rules for the canvas project
- **docs/web/convex/convex-cloudflare-workers-solid-tanstack-spa-betterauth-D1-KV/src/lib/__tests__/README.md** — Test setup and approach

## Source Files
Full example repository source code removed (2026-06-06). Original repos available at <https://github.com/jhomra21> and <https://github.com/better-auth>. Documentation and architectural patterns retained.

## What Was Removed
- All TypeScript/JavaScript source files (.ts, .tsx, .js, .jsx)
- All configuration files (package.json, convex.json, wrangler.jsonc, tailwind.config.ts, vite.config.ts, etc.)
- All CSS/Styles (.css)
- All build artifacts and lock files (node_modules/, dist/)
- All SQL and database files (.sql)
- All image/assets
- .git directories
- All non-.md files
