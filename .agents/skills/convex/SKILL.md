---
name: convex
description: Expert assistance for building real-time applications with Convex. Use when users need reactive backends, real-time sync, serverless functions, document databases, or WebSocket-based state management.
---

# Convex - Real-Time Backend Platform

**Version:** 1.x | **Last Updated:** 2025-01

## Overview

Convex is an open-source, reactive backend platform:

- **Real-Time Sync**: Automatic WebSocket synchronization
- **Document Database**: ACID-compliant document-relational store
- **Serverless Functions**: TypeScript queries, mutations, actions
- **Type Safety**: End-to-end from schema to frontend
- **Built-in Features**: File storage, scheduling, vector search

**Documentation**: https://docs.convex.dev

## When to Use This Skill

Activate when users need:

- "Build a real-time application"
- "Create a reactive backend"
- "Add WebSocket synchronization"
- "Implement live updates"
- "Build with Convex"

## Core Concepts

### 1. Function Types

| Type | Purpose | Database Access | External APIs |
|------|---------|-----------------|---------------|
| Query | Read data | Read only | No |
| Mutation | Write data | Read/Write | No |
| Action | External calls | Via query/mutation | Yes |

### 2. Queries (Read Data)

```typescript
// convex/messages.ts
import { query } from "./_generated/server"
import { v } from "convex/values"

export const list = query({
  args: { channel: v.string() },
  handler: async (ctx, args) => {
    return await ctx.db
      .query("messages")
      .withIndex("by_channel", (q) => q.eq("channel", args.channel))
      .order("desc")
      .take(100)
  },
})

// Queries are:
// - Automatically cached
// - Subscribed via WebSocket
// - Re-run when dependencies change
```

### 3. Mutations (Write Data)

```typescript
// convex/messages.ts
import { mutation } from "./_generated/server"
import { v } from "convex/values"

export const send = mutation({
  args: {
    channel: v.string(),
    body: v.string(),
    author: v.string(),
  },
  handler: async (ctx, args) => {
    const messageId = await ctx.db.insert("messages", {
      channel: args.channel,
      body: args.body,
      author: args.author,
      timestamp: Date.now(),
    })
    return messageId
  },
})

// Mutations are:
// - ACID transactions
// - Atomic (all or nothing)
// - Automatically trigger query updates
```

### 4. Actions (External APIs)

```typescript
// convex/payments.ts
import { action } from "./_generated/server"
import { api } from "./_generated/api"
import { v } from "convex/values"

export const processPayment = action({
  args: {
    userId: v.id("users"),
    amount: v.number(),
  },
  handler: async (ctx, args) => {
    // Call external API
    const result = await stripe.charges.create({
      amount: args.amount,
      currency: "usd",
    })

    // Update database via mutation
    if (result.status === "succeeded") {
      await ctx.runMutation(api.payments.record, {
        userId: args.userId,
        amount: args.amount,
        chargeId: result.id,
      })
    }

    return result
  },
})
```

### 5. Schema Definition

```typescript
// convex/schema.ts
import { defineSchema, defineTable } from "convex/server"
import { v } from "convex/values"

export default defineSchema({
  users: defineTable({
    name: v.string(),
    email: v.string(),
    avatarUrl: v.optional(v.string()),
    roles: v.array(v.string()),
  })
    .index("by_email", ["email"]),

  messages: defineTable({
    channel: v.string(),
    body: v.string(),
    author: v.id("users"),
    timestamp: v.number(),
  })
    .index("by_channel", ["channel"])
    .index("by_author", ["author"]),

  tasks: defineTable({
    title: v.string(),
    completed: v.boolean(),
    assignedTo: v.id("users"),
    dueDate: v.optional(v.number()),
  })
    .index("by_user", ["assignedTo"])
    .index("by_user_status", ["assignedTo", "completed"]),
})
```

### 6. Database Operations

```typescript
// convex/tasks.ts
import { mutation, query } from "./_generated/server"
import { v } from "convex/values"

// Create
export const create = mutation({
  args: { title: v.string(), assignedTo: v.id("users") },
  handler: async (ctx, args) => {
    return await ctx.db.insert("tasks", {
      title: args.title,
      completed: false,
      assignedTo: args.assignedTo,
    })
  },
})

// Read single
export const get = query({
  args: { id: v.id("tasks") },
  handler: async (ctx, args) => {
    return await ctx.db.get(args.id)
  },
})

// Read with index
export const listByUser = query({
  args: { userId: v.id("users") },
  handler: async (ctx, args) => {
    return await ctx.db
      .query("tasks")
      .withIndex("by_user", (q) => q.eq("assignedTo", args.userId))
      .collect()
  },
})

// Update
export const toggle = mutation({
  args: { id: v.id("tasks") },
  handler: async (ctx, args) => {
    const task = await ctx.db.get(args.id)
    if (!task) throw new Error("Task not found")
    await ctx.db.patch(args.id, { completed: !task.completed })
  },
})

// Delete
export const remove = mutation({
  args: { id: v.id("tasks") },
  handler: async (ctx, args) => {
    await ctx.db.delete(args.id)
  },
})
```

### 7. React Integration

```typescript
// app/components/ChatRoom.tsx
import { useQuery, useMutation } from "convex/react"
import { api } from "../convex/_generated/api"

function ChatRoom({ channel }: { channel: string }) {
  // Subscribe to messages - auto-updates via WebSocket
  const messages = useQuery(api.messages.list, { channel })

  // Get mutation function
  const sendMessage = useMutation(api.messages.send)

  const handleSend = async (text: string) => {
    await sendMessage({
      channel,
      body: text,
      author: "user123",
    })
    // UI updates automatically!
  }

  if (messages === undefined) return <div>Loading...</div>

  return (
    <div>
      {messages.map((msg) => (
        <div key={msg._id}>
          <strong>{msg.author}:</strong> {msg.body}
        </div>
      ))}
      <MessageInput onSend={handleSend} />
    </div>
  )
}
```

### 8. Provider Setup

```typescript
// app/ConvexClientProvider.tsx
"use client"
import { ConvexProvider, ConvexReactClient } from "convex/react"

const convex = new ConvexReactClient(process.env.NEXT_PUBLIC_CONVEX_URL!)

export function ConvexClientProvider({ children }: { children: React.ReactNode }) {
  return (
    <ConvexProvider client={convex}>
      {children}
    </ConvexProvider>
  )
}

// app/layout.tsx
import { ConvexClientProvider } from "./ConvexClientProvider"

export default function RootLayout({ children }) {
  return (
    <html>
      <body>
        <ConvexClientProvider>{children}</ConvexClientProvider>
      </body>
    </html>
  )
}
```

### 9. Authentication

```typescript
// convex/auth.config.ts
export default {
  providers: [
    {
      domain: "https://your-auth-provider.com",
      applicationID: "your-client-id",
    },
  ],
}

// convex/users.ts
import { query, mutation } from "./_generated/server"

export const getCurrentUser = query({
  handler: async (ctx) => {
    const identity = await ctx.auth.getUserIdentity()
    if (!identity) return null

    return await ctx.db
      .query("users")
      .withIndex("by_token", (q) =>
        q.eq("tokenIdentifier", identity.tokenIdentifier)
      )
      .unique()
  },
})

// Protected mutation
export const updateProfile = mutation({
  args: { name: v.string() },
  handler: async (ctx, args) => {
    const identity = await ctx.auth.getUserIdentity()
    if (!identity) throw new Error("Not authenticated")

    const user = await ctx.db
      .query("users")
      .withIndex("by_token", (q) =>
        q.eq("tokenIdentifier", identity.tokenIdentifier)
      )
      .unique()

    if (!user) throw new Error("User not found")

    await ctx.db.patch(user._id, { name: args.name })
  },
})
```

### 10. HTTP Endpoints (Webhooks)

```typescript
// convex/http.ts
import { httpRouter } from "convex/server"
import { httpAction } from "./_generated/server"

const http = httpRouter()

http.route({
  path: "/webhook/stripe",
  method: "POST",
  handler: httpAction(async (ctx, request) => {
    const payload = await request.json()

    // Verify signature
    const signature = request.headers.get("stripe-signature")
    // ... verification logic

    // Process webhook
    await ctx.runMutation(api.payments.processWebhook, payload)

    return new Response(null, { status: 200 })
  }),
})

export default http
```

### 11. File Storage

```typescript
// convex/files.ts
import { mutation, query } from "./_generated/server"
import { v } from "convex/values"

export const generateUploadUrl = mutation(async (ctx) => {
  return await ctx.storage.generateUploadUrl()
})

export const saveFile = mutation({
  args: { storageId: v.id("_storage"), fileName: v.string() },
  handler: async (ctx, args) => {
    await ctx.db.insert("files", {
      storageId: args.storageId,
      fileName: args.fileName,
      uploadedAt: Date.now(),
    })
  },
})

export const getFileUrl = query({
  args: { storageId: v.id("_storage") },
  handler: async (ctx, args) => {
    return await ctx.storage.getUrl(args.storageId)
  },
})

// Client usage
const generateUploadUrl = useMutation(api.files.generateUploadUrl)
const saveFile = useMutation(api.files.saveFile)

const handleUpload = async (file: File) => {
  const uploadUrl = await generateUploadUrl()
  const result = await fetch(uploadUrl, {
    method: "POST",
    headers: { "Content-Type": file.type },
    body: file,
  })
  const { storageId } = await result.json()
  await saveFile({ storageId, fileName: file.name })
}
```

### 12. Scheduled Functions

```typescript
// convex/crons.ts
import { cronJobs } from "convex/server"
import { internal } from "./_generated/api"

const crons = cronJobs()

// Daily at 9 AM UTC
crons.daily(
  "daily-cleanup",
  { hourUTC: 9, minuteUTC: 0 },
  internal.tasks.cleanupOldTasks
)

// Every hour
crons.hourly(
  "send-reminders",
  { minuteUTC: 0 },
  internal.notifications.sendReminders
)

// Custom cron expression
crons.cron(
  "weekly-report",
  "0 9 * * MON",
  internal.reports.generateWeekly
)

export default crons

// One-time scheduling
export const scheduleTask = mutation({
  handler: async (ctx) => {
    await ctx.scheduler.runAfter(
      3600 * 1000, // 1 hour
      api.tasks.processTask,
      { taskId: "123" }
    )
  },
})
```

### 13. Vector Search

```typescript
// convex/schema.ts
import { defineSchema, defineTable } from "convex/server"
import { v } from "convex/values"

export default defineSchema({
  documents: defineTable({
    text: v.string(),
    embedding: v.array(v.float64()),
    metadata: v.object({
      title: v.string(),
      author: v.string(),
    }),
  }).vectorIndex("by_embedding", {
    vectorField: "embedding",
    dimensions: 1536,
    filterFields: ["metadata.author"],
  }),
})

// convex/search.ts
import { action, query } from "./_generated/server"

export const search = action({
  args: { query: v.string() },
  handler: async (ctx, args) => {
    // Generate embedding
    const embedding = await openai.embeddings.create({
      model: "text-embedding-3-small",
      input: args.query,
    })

    // Vector search
    return await ctx.runQuery(api.documents.vectorSearch, {
      embedding: embedding.data[0].embedding,
      limit: 10,
    })
  },
})

export const vectorSearch = query({
  args: {
    embedding: v.array(v.float64()),
    limit: v.number(),
  },
  handler: async (ctx, args) => {
    return await ctx.db
      .query("documents")
      .withIndex("by_embedding", (q) =>
        q.similar(args.embedding, args.limit)
      )
      .collect()
  },
})
```

## Validators Reference

```typescript
import { v } from "convex/values"

// Primitives
v.string()
v.number()
v.boolean()
v.null()
v.id("tableName")

// Containers
v.array(v.string())
v.object({
  name: v.string(),
  age: v.number(),
})

// Optional and Union
v.optional(v.string())
v.union(v.string(), v.number())
v.literal("specific_value")

// Special
v.any()
v.bytes()
v.float64()
```

## Project Structure

```
project/
├── convex/
│   ├── _generated/     # Auto-generated types
│   ├── schema.ts       # Database schema
│   ├── messages.ts     # Message functions
│   ├── users.ts        # User functions
│   ├── http.ts         # HTTP endpoints
│   ├── crons.ts        # Scheduled functions
│   └── auth.config.ts  # Auth configuration
├── app/
│   └── ...             # Frontend code
└── convex.json         # Convex config
```

## Development Commands

```bash
# Start development
npx convex dev

# Deploy to production
npx convex deploy

# Generate types
npx convex codegen
```

## Best Practices

1. **Use Indexed Queries**: Always use `.withIndex()` instead of `.filter()` for performance
2. **Keep Functions Pure**: Queries and mutations must be deterministic
3. **Use Actions for APIs**: External calls only in actions
4. **Validate Inputs**: Define args for all functions
5. **Use Internal Functions**: Mark sensitive functions as internal
6. **Await All Promises**: Missing await causes silent failures

## Troubleshooting

### Query Returns Undefined
- Query is still loading; handle loading state
- Check argument types match function definition

### Mutation Not Updating UI
- Ensure using `useMutation` hook
- Verify mutation completes without errors

### Real-Time Not Working
- Check WebSocket connection in browser devtools
- Verify Convex client is initialized correctly

## Resources

- **Documentation**: https://docs.convex.dev
- **Dashboard**: https://dashboard.convex.dev
- **GitHub**: https://github.com/get-convex
- **Discord**: https://discord.gg/convex

## AI Agents component (KCG)

The Tuatha MMO uses Convex's `@convex-dev/agent` package for
real-time agent state (NPC dialogue, player inventory, world
state). The agent component provides:

- **Threads** — persistent conversation state per player
- **Streaming** — real-time SSE for the AG-UI protocol
- **RAG** — vector search over the leabharlann corpus
- **Workflows** — multi-step agent flows (NPC quest generation)
- **Files** — uploaded audio / image storage
- **Rate limiter** — per-player action quotas

```bash
# Install
bun add @convex-dev/agent
```

```typescript
// convex/agents/myAgent.ts
import { Agent } from "@convex-dev/agent";
import { components } from "./_generated/api";

export const myAgent = new Agent(components.agent, {
  name: "Tuatha Guide",
  languageModel: openai.chat("gpt-4o-mini"),
  instructions: "You are a Celtic mythology guide.",
  tools: { /* ... */ },
});
```

The Convex MCP server (`npx -y convex@latest mcp start`) is
the canonical way to expose Convex queries / mutations to
LLM agents (Pydantic AI, Agno, Google ADK).

## BetterAuth + Hono integration

The KCG auth layer (BetterAuth, see `.agents/skills/better-auth/SKILL.md`)
runs behind a Hono API in the web/apps/croilar-portal app:

```typescript
// web/apps/croilar-portal/src/server/auth.ts
import { Hono } from "hono";
import { auth } from "@/lib/auth";

const app = new Hono();
app.on(["GET", "POST"], "/api/auth/*", (c) => auth.handler(c.req.raw));
export default app;
```

## KCG Convex patterns (round-9 deep dive)

The 3,400-line `references/auth-integration-guide.md` is the
canonical Convex reference for KCG. The patterns that matter:

### 1. Function-type discipline (Q/M/A)

| Type | DB access | External API | Determinism | Use for |
|:--|:--|:--|:--|:--|
| `query` | read | no | required | live subscriptions |
| `mutation` | read+write | no | required | ACID writes |
| `action` | via Q/M only | yes | not required | LLM, payment, email |

**The cardinal rule:** never put `await fetch(...)` or
`Date.now()` (when it changes the result) inside a query or
mutation. Move the side-effect into an action and **batch
all the data the action needs before calling
`ctx.runMutation` exactly once** (multiple mutation calls
from an action = race conditions).

**Mutation-first pattern** (preferred for background jobs):

```typescript
export const scheduleJob = mutation({
  handler: async (ctx, args) => {
    const jobId = await ctx.db.insert("jobs", { status: "pending", ...args });
    await ctx.scheduler.runAfter(0, internal.jobs.runJob, { jobId });
    return jobId;
  },
});
```

### 2. Auth integration (Convex Auth vs BetterAuth)

Two viable paths in the KCG stack:

- **Convex Auth** (`@convex-dev/auth`) — built on Auth.js;
  ships GitHub / Google / Resend / Password providers
  out of the box. Use when you want one stack and don't
  need SIWE / passkeys.
- **BetterAuth** (`better-auth/convex` adapter) — use when
  you also need SIWE (crypteolas), passkeys, or 2FA, or
  when you're already running BetterAuth for the rest of
  the monorepo (e.g. Hono + TanStack Start). The BetterAuth
  Convex integration is via OIDC: set
  `auth.config.ts` with the BetterAuth issuer domain and
  the client ID as the audience.

**Authorization** is per-function (always check at the
top of every public query/mutation):

```typescript
const identity = await ctx.auth.getUserIdentity();
if (!identity) throw new Error("Not authenticated");
const user = await ctx.db
  .query("users").withIndex("by_token",
    (q) => q.eq("tokenIdentifier", identity.tokenIdentifier))
  .unique();
if (!user?.isAdmin) throw new Error("Not authorized");
```

### 3. HTTP endpoints (webhooks)

`convex/http.ts` exposes a webhook surface that's separate
from the reactive query/mutation API:

```typescript
import { httpRouter } from "convex/server";
import { httpAction } from "./_generated/server";

const http = httpRouter();
http.route({
  path: "/webhook/stripe",
  method: "POST",
  handler: httpAction(async (ctx, request) => {
    const sig = request.headers.get("stripe-signature");
    // verify signature ...
    const payload = await request.json();
    await ctx.runMutation(api.payments.processWebhook, payload);
    return new Response(null, { status: 200 });
  }),
});
```

`httpAction` is the **only** place where you can do signature
verification + `request.json()` + a side-effecting mutation
in a single round-trip.

### 4. Vector search (RAG)

```typescript
// convex/schema.ts
documents: defineTable({
  text: v.string(),
  embedding: v.array(v.float64()),
  metadata: v.object({ title: v.string(), author: v.string() }),
}).vectorIndex("by_embedding", {
  vectorField: "embedding",
  dimensions: 1536,        // text-embedding-3-small
  filterFields: ["metadata.author"],
});

// convex/search.ts
export const vectorSearch = query({
  args: { embedding: v.array(v.float64()), limit: v.number() },
  handler: async (ctx, args) => {
    return await ctx.db
      .query("documents")
      .withIndex("by_embedding", (q) => q.similar(args.embedding, args.limit))
      .collect();
  },
});
```

Pair with a `search` **action** that calls OpenAI for the
embedding, then `ctx.runQuery(api.documents.vectorSearch, ...)`.
The `@convex-dev/agent` package builds on this primitive
for the KCG agent RAG layer.

### 5. Scheduled + cron + scheduler

- **One-shot** (e.g. send an email in 1h):
  `ctx.scheduler.runAfter(3600 * 1000, api.tasks.process, { id })`
- **Cron** (e.g. daily 9am cleanup):
  `convex/crons.ts` with `crons.daily("name", { hourUTC: 9, minuteUTC: 0 }, internal.tasks.cleanup)`

### 6. Component architecture (modular Convex)

Convex **components** are deployable sub-apps that own
their own tables and functions but share the deployment.
The KCG stack uses:

- `@convex-dev/agent` — agent threads, RAG, workflows
- `@convex-dev/rate-limiter` — per-player action quotas
- `@convex-dev/prosemirror` — collaborative exam editor
  (for the British exam builder)

Components are imported with `import { Agent } from
"@convex-dev/agent";` and configured in `convex.config.ts`.

See `references/auth-integration-guide.md` for the full
2000-line deep-dive on auth, actions, HTTP, vector,
scheduler, components, env vars, testing, framework
integration, file storage, and real-time subscriptions.
