---
name: cloudflare
description: Expert assistance for Cloudflare's serverless developer platform. Use when users need Workers, D1 databases, R2 storage, KV stores, Durable Objects, Containers, or edge computing solutions.
---

# Cloudflare - Serverless Edge Platform

**Version:** 2025.1 | **Last Updated:** 2025-01

## Overview

Cloudflare provides a comprehensive serverless developer platform:

- **Workers**: JavaScript/TypeScript on V8 isolates at edge
- **D1**: Serverless SQLite with global replication
- **R2**: S3-compatible storage with zero egress fees
- **KV**: Eventually-consistent key-value storage
- **Durable Objects**: Strongly-consistent stateful compute
- **Containers**: Serverless containers with programmable sidecars
- **Tunnels**: Secure connectivity from private networks

**Documentation**: https://developers.cloudflare.com/workers/

## When to Use This Skill

Activate when users need:

- "Deploy to Cloudflare Workers"
- "Create a serverless API at the edge"
- "Store data in D1/R2/KV"
- "Build real-time applications with Durable Objects"
- "Set up Cloudflare Tunnels"

## Core Concepts

### 1. Workers (Serverless Functions)

```typescript
// ES Modules syntax (recommended)
export default {
  async fetch(request: Request, env: Env, ctx: ExecutionContext) {
    const url = new URL(request.url)

    if (url.pathname === "/api/users") {
      return handleUsers(request, env)
    }

    return new Response("Hello from the Edge!")
  }
}

interface Env {
  DB: D1Database
  BUCKET: R2Bucket
  CACHE: KVNamespace
}
```

### 2. D1 Database (SQLite at Edge)

```typescript
// Query with parameter binding (prevents SQL injection)
export default {
  async fetch(request: Request, env: Env) {
    const userId = new URL(request.url).searchParams.get("id")

    // Single query
    const user = await env.DB
      .prepare("SELECT * FROM users WHERE id = ?")
      .bind(userId)
      .first()

    // Batch operations for better performance
    const results = await env.DB.batch([
      env.DB.prepare("SELECT * FROM users WHERE id = ?").bind(userId),
      env.DB.prepare("SELECT * FROM posts WHERE author_id = ?").bind(userId),
    ])

    return Response.json({ user, posts: results[1].results })
  }
}
```

### 3. R2 Object Storage

```typescript
export default {
  async fetch(request: Request, env: Env) {
    const key = new URL(request.url).pathname.slice(1)

    if (request.method === "PUT") {
      await env.BUCKET.put(key, request.body, {
        httpMetadata: {
          contentType: request.headers.get("content-type") || "application/octet-stream",
        },
      })
      return new Response("Uploaded", { status: 201 })
    }

    if (request.method === "GET") {
      const object = await env.BUCKET.get(key)
      if (!object) return new Response("Not Found", { status: 404 })

      return new Response(object.body, {
        headers: { "content-type": object.httpMetadata?.contentType || "" },
      })
    }

    return new Response("Method Not Allowed", { status: 405 })
  }
}
```

### 4. KV Storage

```typescript
export default {
  async fetch(request: Request, env: Env) {
    // Read (high performance for hot keys)
    const session = await env.SESSIONS.get(`session:${sessionId}`, "json")

    // Write with TTL
    await env.SESSIONS.put(
      `session:${sessionId}`,
      JSON.stringify(sessionData),
      { expirationTtl: 86400 } // 24 hours
    )

    // Delete
    await env.SESSIONS.delete(`session:${sessionId}`)

    return Response.json({ session })
  }
}
```

### 5. Durable Objects (Stateful Compute)

```typescript
// durable-object.ts
export class Counter {
  state: DurableObjectState

  constructor(state: DurableObjectState) {
    this.state = state
  }

  async fetch(request: Request) {
    const count = await this.state.storage.get("count") || 0

    if (request.method === "POST") {
      const newCount = count + 1
      await this.state.storage.put("count", newCount)
      return Response.json({ count: newCount })
    }

    return Response.json({ count })
  }
}

// worker.ts
export default {
  async fetch(request: Request, env: Env) {
    const id = env.COUNTER.idFromName("global")
    const stub = env.COUNTER.get(id)
    return stub.fetch(request)
  }
}
```

### 6. wrangler.toml Configuration

```toml
name = "my-worker"
main = "src/index.ts"
compatibility_date = "2025-01-01"

# D1 Database
[[d1_databases]]
binding = "DB"
database_name = "my-database"
database_id = "xxxx-xxxx-xxxx-xxxx"

# R2 Bucket
[[r2_buckets]]
binding = "BUCKET"
bucket_name = "my-bucket"

# KV Namespace
[[kv_namespaces]]
binding = "CACHE"
id = "xxxx-xxxx-xxxx-xxxx"

# Durable Objects
[[durable_objects.bindings]]
name = "COUNTER"
class_name = "Counter"

[[migrations]]
tag = "v1"
new_classes = ["Counter"]

# Environment Variables
[vars]
ENVIRONMENT = "production"

# Cron Triggers
[triggers]
crons = ["0 0 * * *"]
```

### 7. Hono Framework Integration

```typescript
import { Hono } from "hono"

type Bindings = {
  DB: D1Database
  BUCKET: R2Bucket
  KV: KVNamespace
}

const app = new Hono<{ Bindings: Bindings }>()

app.get("/users/:id", async (c) => {
  const user = await c.env.DB
    .prepare("SELECT * FROM users WHERE id = ?")
    .bind(c.req.param("id"))
    .first()

  if (!user) return c.json({ error: "Not found" }, 404)
  return c.json(user)
})

app.post("/upload", async (c) => {
  const body = await c.req.arrayBuffer()
  const key = c.req.header("x-file-name") || "upload"
  await c.env.BUCKET.put(key, body)
  return c.json({ success: true })
})

export default app
```

## Service Selection Guide

| Use Case | Service | Why |
|----------|---------|-----|
| Session storage | KV | High-read, eventual consistency OK |
| User data | D1 | Relational queries needed |
| File uploads | R2 | Zero egress, S3-compatible |
| Real-time coordination | Durable Objects | Strong consistency |
| API caching | KV | Sub-millisecond reads |
| Feature flags | KV | Global distribution |
| Rate limiting | Durable Objects | Per-key coordination |
| WebSocket servers | Durable Objects | Stateful connections |

## CLI Commands

```bash
# Project setup
npm create cloudflare@latest my-app

# Development
wrangler dev                     # Local development
wrangler dev --remote            # With production resources

# Database management
wrangler d1 create my-db
wrangler d1 execute my-db --command="SELECT * FROM users"
wrangler d1 migrations apply my-db

# Storage
wrangler kv namespace create CACHE
wrangler r2 bucket create my-bucket

# Deployment
wrangler deploy
wrangler deploy --dry-run

# Monitoring
wrangler tail                    # Live logs
wrangler tail --format=pretty

# Secrets
wrangler secret put API_KEY
```

## Common Architectures

### API Gateway Pattern
```
User -> Workers (auth, validation) -> D1/R2
                                   -> External APIs (via fetch)
```

### Real-time Application
```
WebSocket -> Durable Objects -> D1 (persistence)
                             -> KV (caching)
```

### Static Site + API
```
Static assets -> R2 with custom domain
Dynamic API   -> Workers -> D1 + KV cache
```

## Best Practices

1. **Use Parameter Binding**: Always use `?` placeholders for SQL
2. **Batch D1 Operations**: Use `DB.batch()` for multiple queries
3. **Leverage KV Caching**: Reduce compute costs with caching
4. **waitUntil for Async**: Use `ctx.waitUntil()` for non-blocking work
5. **Stream Large Responses**: Don't buffer entire responses
6. **Smart Placement**: Enable for database-heavy workloads
7. **Zero Egress**: Use R2 for media to eliminate bandwidth costs

## Troubleshooting

### KV Writes Failing (429)
- Rate limit: 1 write/second per key
- Solution: Use Durable Objects for write-heavy workloads

### D1 Query Timeout
- Optimize query with indexes
- Batch operations
- Check query execution plan

### Durable Object State Lost
- In-memory state lost after 70-140s inactivity
- Always persist critical data to `state.storage`

### R2 CORS Errors
```typescript
// Set CORS on bucket or handle in Worker
const headers = new Headers()
headers.set("Access-Control-Allow-Origin", "*")
return new Response(object.body, { headers })
```

## Alchemy IaC (round-9 deep dive)

The KCG primary deploy for `web/apps/cianfhoghlaim-web` and
`tuath/ui/` uses **[Alchemy](https://alchemy.run/)** (an
embeddable, pure-TypeScript IaC library) rather than
Pulumi / Terraform / wrangler.toml. The key property:
**resources are memoised async functions** — no second
language, no extra toolchain, no service to host.

```typescript
import alchemy from "alchemy";
import { Worker, D1, R2, DurableObject } from "alchemy/cloudflare";

const app = await alchemy("cianfhoghlaim-web");

export const db = await D1("cianfhoghlaim-db", {
  name: "cianfhoghlaim-db",
  migrationsDir: "./drizzle",
});

export const assets = await R2("cianfhoghlaim-assets", {
  name: "cianfhoghlaim-assets",
});

export const worker = await Worker("cianfhoghlaim-web", {
  name: "cianfhoghlaim-web",
  entrypoint: "./src/index.ts",
  bindings: {
    DB: db,
    ASSETS: assets,
    GITHUB_CLIENT_ID: alchemy.secret(process.env.GITHUB_CLIENT_ID),
    GITHUB_CLIENT_SECRET: alchemy.secret(process.env.GITHUB_CLIENT_SECRET),
  },
});

await app.finalize();   // triggers deletion of orphaned resources
```

**Why Alchemy over `wrangler.toml`:**

- The IaC is a **TypeScript program** that you can import,
  test, and extend (e.g. add a per-environment worker
  variant, a custom resource for Infisical secrets)
- The state lives in a local file you can inspect, diff,
  and commit (no Pulumi Cloud / Terraform state backend)
- It runs in **any JS runtime** — Bun, Node, Workers, the
  browser (yes, IaC in the browser)
- It's **AI-first** — the README explicitly encourages
  using an LLM to create / copy / fork / modify resources
  when the library doesn't ship a provider

**KCG use:** `web/apps/cianfhoghlaim-web/alchemy.run.ts` declares the
Worker + D1 + R2 + Hyperdrive + Queues. Run with
`bun run alchemy/deploy`. The state file
`.alchemy/state.json` is gitignored. The secret
hydration layer is `.infisical.env` (see
`secrets-management` skill).

**Examples that ship with Alchemy:**

- `cloudflare-worker` — Queue + R2 + Durable Objects +
  Workflows + RPC
- `cloudflare-tanstack-start` — TanStack Start app
  deployment
- `cloudflare-vite` — Vite + Durable Objects
- `cloudflare-sveltekit`, `cloudflare-redwood`,
  `cloudflare-react-router` — full framework deploys
- `aws-app` — Lambda + DynamoDB + IAM (multi-cloud)

The 236 releases and Apache-2.0 licence put Alchemy in
the **production-ready** tier for the KCG stack. The
canonical KCG surface is the
`infrastructure/stacks/web/apps/cianfhoghlaim-web/` Alchemy run file.

See `references/alchemy-iac.md` for the upstream README
in full.

## Resources

- **Documentation**: https://developers.cloudflare.com/workers/
- **D1 Docs**: https://developers.cloudflare.com/d1/
- **R2 Docs**: https://developers.cloudflare.com/r2/
- **Examples**: https://github.com/cloudflare/workers-sdk
- **Discord**: https://discord.cloudflare.com
