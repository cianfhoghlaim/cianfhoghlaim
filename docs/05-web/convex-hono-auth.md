---
domain: web
title: Convex, Hono & Authentication
description: Consolidated Convex backend architecture, Hono edge framework, BetterAuth, SIWE, multi-tenant, and all web authentication/integration patterns.
supersedes:
  - docs/web/convex-authentication-and-integration-guide.md
  - docs/web/convex-core-features-architecture.md
  - docs/web/convex-backend_self-hosted_README.md at main · get-convex_convex-backend.md
  - docs/web/auth-setup.md
  - docs/web/Playground _ Convex Developer Hub.md
  - docs/web/RAG (Retrieval-Augmented Generation) with the Agent component _ Convex Developer Hub.md
  - docs/web/Sign In With Ethereum (SIWE) _ Better Auth.md
  - docs/web/TanStack Start Integration _ Better Auth.md
  - docs/web/Basic Usage _ Better Auth.md
  - docs/web/PostgreSQL _ Better Auth.md
  - docs/web/Drizzle ORM Adapter _ Better Auth.md
  - docs/web/Expo Integration _ Better Auth.md
  - docs/web/repo-convex.md
  - docs/web/repo-hono.md
  - docs/web/implementation-plan-self-hosting-betterauth-convex-supabase-hono-tanstack-start.md
  - docs/web/mcp-ui-integration.md
  - docs/web/AG-UI Overview.md
  - docs/web/AG-UI - Pydantic AI.md
  - docs/web/AG-UI and A2UI_ Understanding the Differences _ CopilotKit.md
  - docs/web/AG-UI Goes Mobile_ The Kotlin SDK Unlocks Full Agent Connectivity Across Android, iOS, and JVM.md
  - docs/web/ag-ui_docs_sdk_kotlin_overview.mdx at main · ag-ui-protocol_ag-ui.md
  - docs/web/🌉 How to Use Swift Inside Kotlin Multiplatform_ The iOS Bridge Explained (with a Real Example).md
cognee_entities:
  - entity: ConvexBackend
    type: BackendPlatform
    relationships:
      - supports: VectorSearch
      - supports: CronJobs
      - integrates_with: BetterAuth
      - integrates_with: Hono
  - entity: BetterAuth
    type: AuthService
    relationships:
      - supports: OAuth
      - supports: SIWE
      - integrates_with: DrizzleORM
      - integrates_with: ConvexBackend
  - entity: HonoFramework
    type: EdgeFramework
    relationships:
      - runs_on: CloudflareWorkers
      - integrates_with: ConvexBackend
ccc_query_hints:
  - "Convex authentication convexAuth"
  - "BetterAuth setup Drizzle adapter"
  - "Convex queries mutations actions"
  - "self-hosted Convex Docker"
  - "Hono edge routes middleware"
  - "SIWE Sign-In Ethereum BetterAuth"
  - "Convex vector search RAG"
updated: 2026-06-06
truth: partial

---

# Convex, Hono & Authentication

Consolidated reference for the backend, edge, and authentication layers of the product web application.

## 1. Convex: Real-Time Reactive Backend

Convex is an open-source reactive backend platform combining a document-relational database, serverless functions, and real-time synchronization into a unified TypeScript-first environment.

### Core Philosophy

Just as React components react to state changes, Convex **queries react to database changes**. The platform tracks all dependencies for every query function; when any dependency changes, Convex automatically reruns the query and pushes updates to all active subscriptions.

### Document-Relational Database

Convex uses a hybrid model:
- **Document**: Store JSON-like nested objects (like MongoDB)
- **Relational**: Use document IDs to create relationships (like PostgreSQL)

```typescript
// Schema definition (convex/schema.ts)
import { defineSchema, defineTable } from "convex/server"
import { v } from "convex/values"

export default defineSchema({
  users: defineTable({
    name: v.string(),
    email: v.string(),
    roles: v.array(v.string()),
  }).index("by_email", ["email"]),

  tasks: defineTable({
    title: v.string(),
    completed: v.boolean(),
    assignedTo: v.id("users"),
    dueDate: v.optional(v.number()),
  }).index("by_user", ["assignedTo"]),
})
```

### Queries, Mutations, Actions

| Feature | Queries | Mutations | Actions |
|---------|---------|-----------|---------|
| Read DB | Yes | Yes | Via queries only |
| Write DB | No | Yes | Via mutations only |
| Third-party APIs | No | No | Yes |
| Deterministic | Yes | Yes | No |
| Auto-retry on conflict | Yes | Yes | No |
| Real-time sync | Yes | Triggers update | No |
| Transactional (ACID) | Yes | Yes | No |

### Query Pattern

```typescript
export const listMessages = query({
  args: { channel: v.string() },
  handler: async (ctx, args) => {
    return await ctx.db
      .query("messages")
      .withIndex("by_channel", (q) => q.eq("channel", args.channel))
      .order("desc")
      .take(100)
  },
})

// Client: automatically updates on data change
const messages = useQuery(api.messages.listMessages, { channel: "general" })
```

### Mutation Pattern

```typescript
export const sendMessage = mutation({
  args: { channel: v.string(), body: v.string() },
  handler: async (ctx, args) => {
    const identity = await ctx.auth.getUserIdentity()
    if (!identity) throw new Error("Not authenticated")
    return await ctx.db.insert("messages", {
      channel: args.channel,
      body: args.body,
      author: identity.subject,
      timestamp: Date.now(),
    })
  },
})
```

### Action Pattern (External APIs)

```typescript
export const processPayment = action({
  args: { amount: v.number(), orderId: v.id("orders") },
  handler: async (ctx, args) => {
    // Call external API
    const paymentResult = await fetch("https://api.stripe.com/v1/charges", {
      method: "POST",
      headers: { Authorization: `Bearer ${process.env.STRIPE_SECRET_KEY}` },
      body: JSON.stringify({ amount: args.amount, currency: "usd" }),
    })
    // Update database via mutation
    await ctx.runMutation(api.orders.markAsPaid, {
      orderId: args.orderId,
      paymentId: (await paymentResult.json()).id,
    })
  },
})
```

**Best Practice — Mutation-First Pattern:**
```typescript
export const createOrder = mutation({
  handler: async (ctx, args) => {
    // 1. Persist the order atomically
    const orderId = await ctx.db.insert("orders", { ...args, status: "pending" })
    // 2. Schedule background processing
    await ctx.scheduler.runAfter(0, api.actions.processPayment, { orderId })
    return orderId
  },
})
```

### Vector Search (RAG)

```typescript
// Schema with vector index
documents: defineTable({
  text: v.string(),
  embedding: v.array(v.float64()),
}).vectorIndex("by_embedding", {
  vectorField: "embedding",
  dimensions: 1536,
  filterFields: ["metadata.source"],
})

// Search (action only — non-deterministic)
export const semanticSearch = action({
  args: { query: v.string() },
  handler: async (ctx, args) => {
    const embedding = await generateEmbedding(args.query)
    return await ctx.vectorSearch("documents", "by_embedding", {
      vector: embedding,
      limit: 10,
    })
  },
})
```

### Cron Jobs (`convex/crons.ts`)

```typescript
import { cronJobs } from "convex/server"

const crons = cronJobs()
crons.interval("clear-presence", { seconds: 60 }, api.presence.clear)
crons.daily("send-digest", { hourUTC: 9, minuteUTC: 0 }, api.emails.sendDailyDigest)
crons.weekly("cleanup", { hourUTC: 8, minuteUTC: 0, dayOfWeek: "monday" }, api.cleanup.weekly)
crons.cron("sync-external", "*/5 * * * *", api.sync.external) // Every 5 min
export default crons
```

### HTTP Actions & Webhooks

```typescript
// convex/http.ts
import { httpRouter } from "convex/server"
import { httpAction } from "./_generated/server"

const http = httpRouter()

http.route({
  path: "/webhook/stripe",
  method: "POST",
  handler: httpAction(async (ctx, request) => {
    const body = await request.json()
    await ctx.runMutation(api.payments.handleWebhook, { event: body })
    return new Response(JSON.stringify({ received: true }), { status: 200 })
  }),
})

// Exposed at: https://<deployment>.convex.site/webhook/stripe
export default http
```

### Convex Components

Reusable backend building blocks:
- **Resend**: Transactional emails
- **Rate Limiter**: API protection
- **Cloudflare R2**: Object storage
- **Crons**: Dynamic scheduling
- **Text Streaming**: AI chat streaming
- **Aggregate**: Atomic counters

### Self-Hosted Convex

```bash
# Docker compose
docker compose up  # Backend (port 3210) + Dashboard (port 6791)

# Generate admin key
docker compose exec backend ./generate_admin_key.sh

# Configure project
# .env.local (gitignored)
CONVEX_SELF_HOSTED_URL='http://127.0.0.1:3210'
CONVEX_SELF_HOSTED_ADMIN_KEY='<your admin key>'

# Push code
npx convex dev
```

Self-hosted supports SQLite (default), PostgreSQL, MySQL, and S3 storage. Advanced hosting via fly.io, Railway, or custom infrastructure.

## 2. BetterAuth: Authentication

BetterAuth (v1.3.4+) is the authentication framework for the platform.

### Server Setup (Drizzle Adapter)

```typescript
// src/lib/auth.ts
import { betterAuth } from "better-auth"
import { drizzleAdapter } from "better-auth/adapters/drizzle"
import { db } from "./db"
import * as schema from "../db/schema"

export const auth = betterAuth({
  database: drizzleAdapter(db, {
    provider: "pg",
    schema: { user: schema.user, session: schema.session, account: schema.account, verification: schema.verification }
  }),
  socialProviders: {
    github: { clientId: process.env.GITHUB_CLIENT_ID!, clientSecret: process.env.GITHUB_CLIENT_SECRET! },
    google: { clientId: process.env.GOOGLE_CLIENT_ID!, clientSecret: process.env.GOOGLE_CLIENT_SECRET! },
  },
})
```

### Client Setup

```typescript
// src/lib/auth-client.ts
import { createAuthClient } from "better-auth/react"

export const { signIn, signUp, useSession, signOut } = createAuthClient({
  baseURL: "http://localhost:3000"
})
```

### API Route Handler

```typescript
// src/routes/api/auth.$.ts
export const APIRoute = createAPIFileRoute("/api/auth/$")({
  GET: ({ request }) => auth.handler(request),
  POST: ({ request }) => auth.handler(request),
})
```

### Route Protection Middleware

```typescript
export const authMiddleware = createMiddleware()
  .server(async ({ next }) => {
    const session = await auth.api.getSession({
      headers: getHeaders() as unknown as Headers
    })
    if (!session) throw redirect({ to: "/login" })
    return next({ context: { user: session.user } })
  })
```

### SIWE (Sign-In with Ethereum)

BetterAuth supports ERC-4361 Sign-In with Ethereum for Web3 wallet authentication:

```typescript
import { siwe } from "better-auth/plugins"

export const auth = betterAuth({
  plugins: [siwe()],
  // ... rest of config
})
```

### Multi-Layer Auth Architecture

| Layer | System | Purpose |
|-------|--------|---------|
| **Customer Facing** | BetterAuth | Google/GitHub OAuth, SIWE |
| **Admin Interfaces** | PocketID | Passkey-based OIDC |
| **Proxy Layer** | TinyAuth / Pangolin | Lightweight auth proxy, zero-trust |
| **Secrets** | Infisical + mise | Automatic environment hydration |

### Database Schema (Drizzle)

```typescript
export const user = pgTable("user", {
  id: text("id").primaryKey(),
  name: text("name").notNull(),
  email: text("email").notNull().unique(),
  emailVerified: boolean("email_verified").notNull().default(false),
  image: text("image"),
  createdAt: timestamp("created_at").notNull().defaultNow(),
  updatedAt: timestamp("updated_at").notNull().defaultNow(),
})

export const session = pgTable("session", {
  id: text("id").primaryKey(),
  userId: text("user_id").notNull().references(() => user.id),
  token: text("token").notNull().unique(),
  expiresAt: timestamp("expires_at").notNull(),
  // ...
})
```

## 3. Hono: Edge Framework

Hono is a lightweight edge web framework used for API gateways, auth workers, and DuckDB API endpoints.

### Core Pattern

```typescript
import { Hono } from "hono"

const app = new Hono()

app.get("/hello/:name", (c) => {
  const name = c.req.param("name")
  return c.json({ message: `Hello ${name}!` })
})

app.post("/api/data", async (c) => {
  const body = await c.req.json()
  // ...
  return c.json(result)
})

export default app
```

### Hono + Convex Integration

```typescript
import { Hono } from "hono"
import { HonoWithConvex, HttpRouterWithHono } from "convex-helpers/server/hono"

const app: HonoWithConvex = new Hono()

app.get("/users/:userId", async (c) => {
  const userId = c.req.param("userId")
  const user = await c.env.runQuery(api.users.get, { id: userId })
  return c.json(user)
})

export default new HttpRouterWithHono(app)
```

### Use Cases
- Auth proxy workers for domain-specific OIDC
- Lightweight API gateway for DuckDB queries
- AI summarization endpoints
- Multi-runtime deployment (Cloudflare Workers, Bun, Deno, Node.js)

## 4. AG-UI Protocol

The Agent User Interaction (AG-UI) protocol enables streaming communication between AI agents and user interfaces.

### Key Concepts
- **Event Types**: `text`, `tool_call`, `tool_result`, `agent_handoff`, `done`
- **Streaming**: Server-Sent Events over HTTP/WebSocket
- **SDKs**: Python (Pydantic AI, Agno), TypeScript, Kotlin Multiplatform
- **Mobile**: Kotlin SDK for Android, iOS, JVM

### AG-UI vs A2UI
- **AG-UI**: Open protocol for agent↔UI communication (streaming text, tool calls)
- **A2UI**: CopilotKit's specific implementation of agent-to-UI rendering

## 5. Convex Auth (Alternative to BetterAuth)

For projects preferring Convex-native auth:

```typescript
// convex/auth.ts
import { convexAuth } from "@convex-dev/auth/server"
import GitHub from "@auth/core/providers/github"

export const { auth, signIn, signOut, store } = convexAuth({
  providers: [GitHub, Google, Password],
})

// convex/schema.ts
import { authTables } from "@convex-dev/auth/server"

export default defineSchema({
  ...authTables,
  // your other tables
})
```

Supports 80+ OAuth providers, Magic Links, OTP, Email/Password, and custom OIDC.

## 6. Security Best Practices

1. **Never commit secrets** — use Infisical + mise for automatic `.env` hydration
2. **Separate dev/prod** — different OAuth apps, DB connections, API keys per environment
3. **Route protection** — middleware checking session on all authenticated routes
4. **Input validation** — Zod/Effect Schema on all server boundaries
5. **Rate limiting** — Convex Rate Limiter component for API protection
6. **Internal functions** — `internalMutation`/`internalQuery` for admin operations not exposed to clients
7. **Webhook verification** — Always verify webhook signatures (Stripe, Clerk, Svix)
8. **Token lifetimes** — Short-lived sessions with refresh token rotation
