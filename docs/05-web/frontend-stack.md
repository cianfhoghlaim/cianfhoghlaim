---
domain: web
title: Frontend Stack
description: Consolidated TanStack Start architecture, React 19, SSR, edge runtime, Effect-TS, Vite build system, and all frontend framework patterns.
supersedes:
  - docs/web/tanstack-start-architecture.md
  - docs/web/tanstack-start-research-report.md
  - docs/web/tanstack-start-visual-patterns.md
  - docs/web/TANSTACK_ANALYSIS.md
  - docs/web/TANSTACK_QUICK_REFERENCE.md
  - docs/web/TanStack Start.md
  - docs/web/TanStack DB Integration and Comparison.md
  - docs/web/Overview _ TanStack AI Docs.md
  - docs/web/Overview _ TanStack DB Docs.md
  - docs/web/Integrating TanStack AI with LiteLLM.md
  - docs/web/effect-ts-comprehensive-research.md
  - docs/web/effect-ts-tanstack-start-integration.md
  - docs/web/effect-convex-integration-research.md
  - docs/web/BAML, Graphiti, Tanstack AI Pipeline.md
  - docs/web/alchemy-run_alchemy_ Infrastructure as TypeScript.md
  - docs/web/alchemy_examples_cloudflare-tanstack-start_alchemy.run.ts at main · alchemy-run_alchemy.md
  - docs/web/alchemy_examples_cloudflare-sveltekit_alchemy.run.ts at main · alchemy-run_alchemy.md
  - docs/web/alchemy_examples_cloudflare-worker_alchemy.run.ts at main · alchemy-run_alchemy.md
  - docs/web/repo-tanstack.md
  - docs/web/repo-cloudflare-workers.md
  - docs/web/repo-orpc.md
  - docs/web/orpc-comprehensive-research.md
  - docs/web/Microfrontends.md
  - docs/web/PDF.js - Examples.md
  - docs/web/ChromeDevTools_chrome-devtools-mcp_ Chrome DevTools for coding agents.md
  - docs/web/Release v28.0.0 - Mesh Shaders, Immediates, and More! · gfx-rs_wgpu.md
cognee_entities:
  - entity: TanStackStart
    type: Framework
    relationships:
      - uses: React
      - uses: Vite
      - uses: Nitro
      - integrates_with: EffectTS
      - integrates_with: BetterAuth
  - entity: EffectTS
    type: Library
    relationships:
      - integrates_with: Convex
      - integrates_with: TanStackStart
ccc_query_hints:
  - "TanStack Start SSR streaming"
  - "server functions createServerFn"
  - "file-based routing createFileRoute"
  - "Effect.gen Effect.runPromise"
  - "Effect Schema validation"
  - "Vite build plugin tanstackStart"
updated: 2026-06-06
truth: partial

---

# Frontend Stack

The product web application is built on a **TypeScript-first full-stack architecture** centered on TanStack Start and Effect-TS. This document consolidates all framework architecture, build system, SSR, edge runtime, and type safety patterns.

## 1. TanStack Start: Core Architecture

TanStack Start is a full-stack React framework (v1.132+) that combines SSR, file-based routing, server functions, and automatic code splitting. It abstracts over Vinxi/Nitro for production builds.

### Design Philosophy

- **Isomorphic by default**: Write once, run on server and client
- **Server-centric data loading**: Database access, secrets, heavy computation run server-side
- **Progressive enhancement**: Server renders HTML; client hydrates for interactivity
- **Type safety first**: End-to-end TypeScript with automatic route type generation

### Entry Points

```typescript
// src/entry-server.tsx — SSR render
export default (async (req, ctx) => {
  const router = createRouter()
  const stream = await router.server.renderToStream(
    <StartServer router={router} />, { req, ctx }
  )
  return new Response(stream, {
    headers: { 'Content-Type': 'text/html', 'Transfer-Encoding': 'chunked' }
  })
}) satisfies RequestHandler

// src/entry-client.tsx — Hydration
import { hydrateRoot } from 'react-dom/client'
const router = createRouter()
hydrateRoot(document.getElementById('root')!, <StartClient router={router} />)
```

### File-Based Routing

```
src/routes/
├── __root.tsx              # Root layout (providers, global styles)
├── index.tsx               # GET /
├── dashboard.tsx            # GET /dashboard
├── _authenticated.tsx       # Layout wrapper for protected routes
├── _authenticated/
│   ├── profile.tsx          # GET /profile
│   └── settings.tsx         # GET /settings
├── $postId.tsx              # Dynamic param: GET /:postId
└── api/
    ├── auth.$.ts            # Catch-all: /api/auth/*
    └── chat.ts              # API: POST /api/chat
```

### Server Functions Pattern

```typescript
import { createServerFn } from '@tanstack/react-start'
import { zodValidator } from '@tanstack/zod-adapter'
import { z } from 'zod'

export const getUser = createServerFn({ method: 'GET' })
  .validator(zodValidator(z.object({ id: z.string() })))
  .handler(async ({ data }) => {
    const user = await db.query.users
      .findFirst({ where: eq(users.id, data.id) })
    if (!user) throw notFound()
    return user
  })
```

### API Route Handlers

```typescript
// src/routes/api/rpc.$.ts
export const Route = createFileRoute('/api/rpc/$')({
  server: {
    handlers: {
      GET: async ({ request }) => { /* handle */ },
      POST: async ({ request }) => { /* handle */ },
    }
  }
})
```

## 2. Unified Template Stack (from 6 Example Analysis)

Six TanStack Start examples were analyzed to derive the canonical stack.

| Example | Focus | Key Technologies |
|---------|-------|-----------------|
| tanstack-better-auth | Auth + tRPC | better-auth, tRPC, React Query |
| learn-platform | Monorepo full-stack | Hono, Prisma, better-auth |
| orcish-saas | Dashboard UI | Tables, Charts, Radix UI |
| tanstack-without-cloudflare | Server functions | Prisma, Forms, Zod |
| orcish-tanstack-dashboard | Advanced UI | DnD, Charts, Themes |
| tanstack-betterauth | Auth + Drizzle | better-auth, Drizzle, PostgreSQL |

### Universal Patterns (All 6 Examples)
1. File-based routing with `createFileRoute()`
2. Root layout in `__root.tsx` with `HeadContent`, `Scripts`
3. Tailwind CSS 4 with `@tailwindcss/vite`
4. Radix UI primitives + shadcn component patterns

### Canonical Project Structure

```
src/
├── lib/
│   ├── auth.ts              # better-auth + Drizzle setup
│   ├── auth-client.ts       # Client auth hooks
│   ├── auth-middleware.ts   # Protected route middleware
│   ├── db.ts                # Database connection
│   └── utils.ts
├── db/
│   └── schema.ts            # Drizzle schema definitions
├── components/
│   ├── ui/                  # shadcn base components
│   ├── Header.tsx
│   └── ThemeProvider.tsx
├── routes/
│   ├── __root.tsx           # Root layout + auth middleware
│   ├── index.tsx            # Public home
│   ├── login.tsx            # Auth pages
│   ├── dashboard.tsx        # Protected route
│   ├── _authenticated.tsx   # Protected layout wrapper
│   └── api/
│       ├── auth.$.ts        # Auth API handler
│       └── demo.ts          # Example API route
├── schemas/
│   └── user.ts              # Zod validation schemas
├── styles.css
├── router.tsx
└── server.ts
```

### Eliminated Patterns
- **tRPC** → Server functions are simpler for full-stack framework
- **Separate Hono server** → TanStack Start server functions suffice
- **Monorepo complexity** → Single app cleaner for most use cases
- **Prisma** → Drizzle is more type-safe and modern

## 3. Build System

### Vite Configuration

```typescript
// vite.config.ts
import { tanstackStart } from '@tanstack/react-start/plugin/vite'
import react from '@vitejs/plugin-react'
import tailwindcss from '@tailwindcss/vite'

export default defineConfig({
  plugins: [
    react({ babel: { plugins: [['babel-plugin-react-compiler', {}]] } }),
    ...tanstackStart(),  // Route tree gen, server/client split
    tailwindcss(),
    tsconfigPaths(),
  ],
})
```

### TanStack Start Plugin Duties
1. **Route Tree Generation**: Scans `src/routes/` → `routeTree.gen.ts`
2. **Server/Client Split**: Identifies server-only vs shared code
3. **API Route Recognition**: Converts file routes to HTTP endpoints
4. **Code Splitting**: Automatic per-route chunking
5. **Type Generation**: Creates TypeScript types for routes

### Platform Adapters
- **Netlify**: `@netlify/vite-plugin-tanstack-start`
- **Cloudflare Workers**: `@tanstack/react-start/adapters/cloudflare`
- **Node.js**: Standalone (no special adapter needed)
- **Vercel**: Node.js adapter (no special plugin)

## 4. Effect-TS Integration

Effect-TS (v3.15+) is the functional effect system providing type-safe error handling, dependency injection, and structured concurrency.

### Core Concepts

| Concept | Purpose |
|---------|---------|
| `Effect<A, E, R>` | Three-parameter type: Success (A), Error (E), Requirements (R) |
| `Effect.gen` | Generator syntax (like async/await but typed) |
| `Layer` | Dependency injection — composable service recipes |
| `Fiber` | Lightweight green threads for concurrency |
| `Stream` | Pull-based streaming with automatic backpressure |
| `Scope` | Resource lifecycle management |
| `Cause<E>` | Lossless error representation |

### TanStack Start Integration Pattern

```typescript
import { createServerFn } from '@tanstack/react-start'
import { Effect, Either } from 'effect'

// Define Effect-based business logic
const getUserEffect = (id: string): Effect.Effect<User, UserNotFoundError> =>
  Effect.gen(function* () {
    const service = yield* UserService
    return yield* service.getUser(id)
  })

// Bridge to TanStack Start server function
export const getUser = createServerFn({ method: 'GET' })
  .handler(async ({ data }) => {
    const result = await Effect.runPromise(
      getUserEffect(data.id).pipe(
        Effect.provide(AppLayer),
        Effect.either
      )
    )
    if (Either.isLeft(result)) {
      throw new Response('User not found', { status: 404 })
    }
    return result.right
  })
```

### Effect + Convex Integration (via Confect)

Two community libraries enable Effect in Convex:

| Library | Approach | Best For |
|---------|----------|----------|
| **Confect** (`@rjdellecese/confect`) | Deep integration, Effect Schema for DB | New projects, schema-first |
| **@maple/convex-effect** | Lightweight 1:1 API wrapper | Existing projects, gradual adoption |

TypeScript constraint: `exactOptionalPropertyTypes: false` required due to convex-js limitation.

### Error Handling Pattern

```typescript
// Tagged errors for discrimination
class NotFoundError extends Data.TaggedError("NotFoundError")<{ id: string }> {}
class ValidationError extends Data.TaggedError("ValidationError")<{ message: string }> {}

const program = fetchUser(id).pipe(
  Effect.catchTag("NotFoundError", (error) =>
    Effect.succeed(createDefaultUser(error.id))
  ),
  Effect.catchTag("ValidationError", (error) =>
    Effect.fail(new BadRequestError(error.message))
  )
)
```

### When to Use Effect vs Standard Patterns

**Use Effect when:**
- Complex error handling required
- Multiple services need orchestration
- Structured concurrency needed
- Building reusable business logic

**Avoid Effect when:**
- Simple CRUD operations
- Team lacks FP experience
- Rapid prototyping phase

## 5. SSR & Streaming

### Streaming HTML

TanStack Start supports streaming SSR, where HTML chunks are sent progressively:

```
HTTP Request → Router Match → Loader Executes → React SSR → Stream HTML
                                                              ↓
                                          Browser parses HTML progressively
                                          Client bundle downloads
                                          hydrateRoot() attaches React
```

### Isomorphic Functions

Code that runs differently on server vs client:

```typescript
const getORPCClient = createIsomorphicFn()
  .server(() => createRouterClient(router, {
    context: () => ({ headers: getRequestHeaders() })
  }))
  .client(() => {
    const link = new RPCLink({ url: `${window.location.origin}/api/rpc` })
    return createORPCClient(link)
  })
```

### Hydration Contract

Server and client renders must produce identical output. Mechanisms:
- No randomness in server render
- No date/time differences
- Metadata embedded in HTML for state restoration
- `suppressHydrationWarning` on known-different elements

## 6. oRPC: Type-Safe RPC

oRPC provides end-to-end type safety from server schema to client call:

```typescript
// Server: Define procedure
const createChat = os
  .input(z.object({ title: z.string() }))
  .handler(async ({ input }) => {
    return await db.insert(chats).values(input).returning()
  })

// Client: Fully typed
const result = await client.createChat({ title: "New Chat" })
// TypeScript knows result type from server handler
```

Benefits:
- OpenAPI specification generation
- Automatic client type generation
- JSON schema validation at runtime
- Middleware support

## 7. TanStack DB & AI

### TanStack DB
- Offline-first database with automatic sync
- PostgreSQL, SQLite, or in-memory backends
- Plugin system for custom storage adapters

### TanStack AI
- Cross-language chat SDK (TypeScript, Kotlin, Swift, Python)
- Model-agnostic provider system
- Integrates with LiteLLM for routing across 100+ models
- BAML integration for type-safe AI function calling

## 8. Cloudflare Workers / Edge

### Alchemy Infrastructure-as-TypeScript
- Define Cloudflare Workers, Durable Objects, KV, R2 entirely in TypeScript
- Type-safe bindings for all Cloudflare primitives
- Examples for TanStack Start, SvelteKit, and standalone Workers

### Edge Deployment Pattern
```typescript
// wrangler.toml
[[d1_databases]]
binding = "DB"
database_id = "xxx"

// src/lib/db.ts
export const db = drizzle(client(env.DB))
```

## 9. Performance

- **Code splitting**: Per-route automatic chunking
- **Preloading**: `defaultPreload: 'intent'` (preloads on hover)
- **Bundle size**: Effect-TS core ~15KB compressed, ~25KB minimum
- **Streaming**: HTML arrives before data loads (progressive rendering)
- **Convex reactivity**: Only changed data transmitted, smart diffing

## 10. Testing

```typescript
// Vitest + @effect/vitest
import { it, expect } from "@effect/vitest"
import { Layer, Effect } from "effect"

// Mock service layer
const TestLayer = Layer.succeed(UserRepository, {
  findById: (id) => Effect.succeed({ id, name: "Test" }),
  save: () => Effect.void,
})

it.effect("should fetch user", () =>
  Effect.gen(function* () {
    const repo = yield* UserRepository
    const user = yield* repo.findById("123")
    expect(user.name).toBe("Test")
  }).pipe(Effect.provide(TestLayer))
)
```

For Convex: `convex-test` with `convexTest(schema)` provides a mock Convex backend.
