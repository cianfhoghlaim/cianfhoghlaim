---
domain: web
title: Web Architecture Reference
description: Consolidated knowledge base for the Oideachais web application layer, covering the full-stack TypeScript ecosystem.
supersedes:
  - docs/web/README.md
  - docs/web/INDEX.md
  - docs/web/INDEX-from-bonneagar-web-research.md
  - docs/web/README_TANSTACK_ANALYSIS.md
  - docs/web/TANSTACK_INDEX.md
  - docs/web/TANSTACK_SUMMARY.md
  - docs/web/Educational Website Tech Stack.md
  - docs/web/full-stack-web-architecture-consolidated.md
  - docs/web/full-stack-dashboard-integration-plan.md
  - docs/web/routing-and-layout.md
  - docs/web/ref-cianfhoghlaim-base-template.md
  - docs/web/ref-unified-examples.md
  - docs/web/repo-restate-coding-agent.md
  - docs/web/repo-restate-ui-readme.md
  - docs/web/repo-ag-ui-protocol.md
  - docs/web/agentic-platform.md
cognee_entities:
  - entity: OideachaisWeb
    type: Application
    relationships:
      - uses: TanStackStart
      - uses: ConvexBackend
      - uses: EffectTS
      - uses: BetterAuth
ccc_query_hints:
  - "web application architecture"
  - "full-stack TypeScript framework"
  - "oideachais web tech stack"
  - "Kings College Galway frontend"
updated: 2026-06-06
truth: partial

---

# Web Architecture

The Oideachais web application layer is a modern full-stack TypeScript architecture built on TanStack Start (React 19), Convex (real-time backend), Effect-TS (functional error handling), and BetterAuth (authentication). This directory consolidates all web research, architecture decisions, and implementation patterns.

## Core Tech Stack

| Layer | Technology | Purpose |
|-------|-----------|---------|
| **Framework** | TanStack Start 1.132+ | Full-stack React with SSR, file-based routing, server functions |
| **Routing** | TanStack Router 1.132+ | File-based routing with type-safe params |
| **Real-time Backend** | Convex | Reactive database with automatic WebSocket sync, ACID transactions |
| **Type Safety** | Effect-TS 3.15+ | Functional effect system with typed errors, dependency injection |
| **RPC** | oRPC | Type-safe RPC with OpenAPI generation |
| **Edge/Runtime** | Hono, Cloudflare Workers | Lightweight HTTP framework, edge deployment |
| **Auth** | BetterAuth 1.3.4+ | OAuth (GitHub/Google), SIWE, Drizzle adapter |
| **Database** | Drizzle ORM + PostgreSQL | Type-safe ORM with schema-first design |
| **Styling** | Tailwind CSS 4, Radix UI, shadcn/ui | Accessible component system |
| **AI/Agents** | CopilotKit, AG-UI Protocol, MCP-UI | Agent UI integration |
| **Build** | Vite, Vinxi, Nitro | Build toolchain with streaming SSR |

## Architecture Layers

```
┌─────────────────────────────────────────────────────────────┐
│  Presentation Layer (React 19 + shadcn/ui + CopilotKit)     │
├─────────────────────────────────────────────────────────────┤
│  Routing & Request (TanStack Router + Server Functions)     │
├─────────────────────────────────────────────────────────────┤
│  Data Layer (Convex real-time + TanStack Query + Drizzle)   │
├─────────────────────────────────────────────────────────────┤
│  Infrastructure (Vite + TanStack Plugin + Platform Adapter) │
└─────────────────────────────────────────────────────────────┘
```

## Key Documentation

- **[frontend-stack.md](./frontend-stack.md)** — TanStack Start, React 19, SSR, edge runtime, build system
- **[convex-hono-auth.md](./convex-hono-auth.md)** — Convex, Hono, BetterAuth, authentication, multi-tenant
- **[ui-components.md](./ui-components.md)** — shadcn/ui, CopilotKit, drag-and-drop, exam builder

## Technology Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| **Framework** | TanStack Start over Next.js | File-based routing, type-safe server functions, Vite-native |
| **Backend** | Convex over traditional API | Automatic reactivity, ACID transactions, no WebSocket boilerplate |
| **ORM** | Drizzle over Prisma | More type-safe, smaller bundle, PostgreSQL-first |
| **RPC** | oRPC over tRPC | Better monorepo patterns, OpenAPI generation |
| **Auth** | BetterAuth over Auth.js | Lightweight, Drizzle-native, SIWE support |
| **Type Safety** | Effect-TS + Zod | Best-in-class error handling, composable validation |
| **Styling** | Tailwind 4 + shadcn/ui over MUI | Accessibility (Radix), copy-paste control, consistent theming |

## Implementation Roadmap

### Phase 1: Foundation (Days 1-2)
- TanStack Start setup with file-based routing
- Root layout with theme support (next-themes)
- Tailwind CSS 4 + shadcn component library
- Vite build configuration

### Phase 2: Authentication (Days 3-4)
- BetterAuth server setup with Drizzle adapter
- OAuth providers (GitHub, Google)
- SIWE (Sign-In with Ethereum) for Web3 users
- Auth middleware for route protection
- Auth API endpoints (`/api/auth/$`)

### Phase 3: Data Layer (Days 5-6)
- Drizzle schema definitions
- Server functions for CRUD operations
- TanStack Query client integration
- Convex real-time subscriptions for collaborative features

### Phase 4: Forms & Validation (Days 7-8)
- React Hook Form + Zod integration
- Effect Schema for server-side validation
- Reusable form components
- Server-side form handling with type inference

### Phase 5: Advanced (Days 9-10)
- Protected route layouts with role-based access
- Example dashboard with TanStack Table + Recharts
- Agent integration via CopilotKit + MCP-UI
- Testing infrastructure (Vitest + convex-test)

## Deployment

| Platform | Adapter | Environment Variables |
|----------|---------|----------------------|
| **Netlify** | `@netlify/vite-plugin-tanstack-start` | `CONVEX_SELF_HOSTED_URL`, `CONVEX_SELF_HOSTED_ADMIN_KEY` |
| **Cloudflare Workers** | `cloudflarePlugin` | Same via wrangler.toml |
| **Node.js** | Standalone | `.env.local` (gitignored) |
| **Docker** | `docker-compose.yml` | Self-hosted Convex backend + dashboard |

## Directory Structure

```
src/
├── lib/           # Auth, database, shared utilities
├── db/            # Drizzle schema definitions
├── components/    # UI components (shadcn pattern)
├── routes/        # File-based routing
│   ├── __root.tsx # Root layout
│   └── api/       # API route handlers
├── schemas/       # Zod / Effect Schema definitions
├── integrations/  # Third-party provider wrappers
└── styles.css     # Global styles
```

## Reference Repositories (Skeletonized)

| Repo | Stars | Purpose |
|------|-------|---------|
| ag-ui/ | — | AG-UI streaming protocol (Python + TypeScript) |
| tanstack/ | — | TanStack Start examples: auth, dashboards, forms |
| convex/ | — | Convex + BetterAuth + framework integration |
| cloudflare/ | — | Cloudflare Workers + BetterAuth patterns |
| hono/ | — | Hono edge framework patterns |
| orpc/ | — | Type-safe RPC monorepo patterns |
| restate/ | — | Durable execution coding agent demo |
