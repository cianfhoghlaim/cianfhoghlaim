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
