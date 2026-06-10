# Hono — Lightweight Web API Framework

## Overview

Hono is an ultrafast, lightweight web framework for building APIs and middleware. It runs on Bun, Node.js, Deno, and Cloudflare Workers — with a unified API across all runtimes. Its small bundle size (<20 KB) and fast routing make it ideal for edge and serverless deployments, while its middleware composition model supports auth, CORS, caching, and logging out of the box.

## Why This Matters for Kings' College Galway

The platform's API layer — serving curriculum data to the TanStack Start frontend, exposing the MCP server for agent integration, and routing AG-UI SSE streams — is built on Hono. Its multi-runtime support means the same API code runs on Bun during development, on Cloudflare Workers for edge deployment, and on the ARM1-OCI server for production. The middleware composition enables Pocket ID SSO auth, Langfuse tracing headers, and rate limiting to be composed cleanly without spaghetti middleware chains.

## Key Features

- **Multi-runtime** — Bun, Node.js, Deno, Cloudflare Workers, AWS Lambda
- **Ultrafast routing** — RegExpRouter with linear-time matching
- **Middleware composition** — Auth, CORS, caching, logging, compression
- **JSX support** — Server-side JSX rendering for HTML responses
- **Tiny bundle** — <20 KB, zero dependencies

## Installation

```bash
bun add hono
```

## Integration with Our Stack

Hono serves as the API layer between the TanStack Start frontend and backend services. It exposes REST endpoints for curriculum data, MCP server routes for agent integration, and SSE streams for CopilotKit's real-time AI chat. Auth middleware integrates with Pocket ID OIDC. The `oideachais/web/` workspace contains Hono route definitions.

## Upstream

- **Repository**: <https://github.com/honojs/hono>
- **Documentation**: <https://hono.dev>
- **Latest**: v4.x (2025) — Bun native support, streaming helpers, RPC mode, JSX improvements

## Screenshot

Hono is a programmatic framework. The `hono.dev` website shows code examples with syntax highlighting. Route definitions are clean TypeScript files. The development server (`bun run --hot src/index.ts`) shows request logs and response times. The `.agents/skills/hono/` skill documents project Hono patterns.
