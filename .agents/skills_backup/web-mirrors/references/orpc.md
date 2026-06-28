# oRPC — KCG Summary

## What It Is
oRPC is a type-safe RPC framework for TypeScript that provides end-to-end type safety from server to client. Procedures are defined once and automatically exposed as both type-safe RPC endpoints and OpenAPI-compliant REST APIs with interactive documentation. It supports serverless, edge, and Node.js runtimes with automatic client generation.

## Why This Matters for Kings' College Galway
oRPC is used as the API layer across all Cianfhoghlaim TypeScript applications — the `turborepo-based` monorepo pattern in `orpc_query` directly matches the project's own monorepo structure. The `learn-orpc` example demonstrates OpenAPI auto-generation from oRPC procedures — the pattern used for the `sruth/oideachais/` API. The `orpc-multiservice-monorepo-playground` shows the multi-service architecture used for the `api-unified` example that combines MCP, oRPC, OpenAPI, and AI streaming. End-to-end type safety between TanStack Start frontends and Hono backends is powered by oRPC's contract-first design.

## Key Patterns Preserved
- **docs/web/orpc/orpc_query/README.md** — Production-ready Turborepo monorepo with oRPC + Hono + BetterAuth + TanStack Start + React Native, Docker deployment
- **docs/web/orpc/orpc_query/MEDIUM.md** — Medium article writeup of oRPC monorepo patterns
- **docs/web/orpc/learn-orpc/README.md** — oRPC learning project with Next.js, OpenAPI auto-generation
- **docs/web/orpc/orpc-multiservice-monorepo-playground/README.md** — Multi-service monorepo playground with oRPC

## Source Files
Full example repository source code removed (2026-06-06). Original repos available at <https://github.com/unnoq/orpc>. Documentation and architectural patterns retained.

## What Was Removed
- All TypeScript/JavaScript source files (.ts, .tsx, .js, .jsx)
- All configuration files (package.json, tsconfig.json, turbo.json, etc.)
- All CSS/Styles (.css)
- All build artifacts and lock files (node_modules/, dist/, .turbo/)
- All Docker files (Dockerfile, docker-compose.yml)
- All image/assets
- .git directories
- All non-.md files
