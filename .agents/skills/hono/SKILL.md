---
name: hono
description: Expert assistance for building lightweight web APIs with Hono. Use when users need fast HTTP servers, middleware composition, multi-runtime support (Cloudflare Workers, Node.js, Bun, Deno), or API gateway functionality.
---

# Hono - Lightweight Web Framework

**Version:** 4.x | **Last Updated:** 2025-01

## Overview

Hono is a small, fast web framework for building HTTP servers:

- **Multi-Runtime**: Works on Cloudflare Workers, Node.js, Bun, Deno, AWS Lambda
- **TypeScript First**: Full type inference and safety
- **Middleware System**: Composable middleware architecture
- **Zero Dependencies**: Minimal footprint (~12KB)
- **Web Standards**: Uses Request/Response API

**Documentation**: https://hono.dev

## When to Use This Skill

Activate when users need:

- "Create a lightweight API server"
- "Build an edge function API"
- "Add middleware to HTTP routes"
- "Create a Cloudflare Workers backend"
- "Build an API gateway"

## Core Concepts

### 1. Basic Application

```typescript
import { Hono } from 'hono'

const app = new Hono()

app.get('/', (c) => {
  return c.text('Hello Hono!')
})

app.get('/json', (c) => {
  return c.json({ message: 'Hello', timestamp: Date.now() })
})

export default app
```

### 2. Route Parameters

```typescript
const app = new Hono()

// Path parameters
app.get('/users/:id', (c) => {
  const id = c.req.param('id')
  return c.json({ userId: id })
})

// Multiple parameters
app.get('/posts/:postId/comments/:commentId', (c) => {
  const { postId, commentId } = c.req.param()
  return c.json({ postId, commentId })
})

// Optional parameters
app.get('/files/:path{.+}', (c) => {
  const path = c.req.param('path')
  return c.text(`File: ${path}`)
})

// Wildcard
app.get('/api/*', (c) => {
  return c.text('API endpoint')
})
```

### 3. Request Handling

```typescript
app.post('/users', async (c) => {
  // JSON body
  const body = await c.req.json()

  // Form data
  const formData = await c.req.formData()

  // Query parameters
  const page = c.req.query('page')
  const { limit, offset } = c.req.queries()

  // Headers
  const auth = c.req.header('Authorization')

  // URL info
  const url = c.req.url
  const path = c.req.path
  const method = c.req.method

  return c.json({ received: body })
})
```

### 4. Response Methods

```typescript
app.get('/responses', (c) => {
  // Text response
  return c.text('Plain text')

  // JSON response
  return c.json({ data: 'value' })

  // HTML response
  return c.html('<h1>Hello</h1>')

  // Redirect
  return c.redirect('/new-location')

  // Not found
  return c.notFound()

  // Custom status
  return c.json({ error: 'Bad request' }, 400)

  // With headers
  return c.json(data, 200, {
    'X-Custom-Header': 'value'
  })

  // Streaming
  return c.stream(async (stream) => {
    await stream.write('Hello ')
    await stream.write('World')
  })
})
```

### 5. Middleware

```typescript
import { Hono } from 'hono'
import { logger } from 'hono/logger'
import { cors } from 'hono/cors'
import { jwt } from 'hono/jwt'
import { compress } from 'hono/compress'

const app = new Hono()

// Built-in middleware
app.use('*', logger())
app.use('*', compress())
app.use('/api/*', cors({
  origin: ['http://localhost:3000'],
  credentials: true,
}))

// JWT authentication
app.use('/protected/*', jwt({
  secret: process.env.JWT_SECRET!,
}))

// Custom middleware
const timing = async (c, next) => {
  const start = Date.now()
  await next()
  const ms = Date.now() - start
  c.header('X-Response-Time', `${ms}ms`)
}

app.use('*', timing)
```

### 6. Validation with Zod

```typescript
import { Hono } from 'hono'
import { zValidator } from '@hono/zod-validator'
import { z } from 'zod'

const app = new Hono()

const createUserSchema = z.object({
  name: z.string().min(1),
  email: z.string().email(),
  age: z.number().optional(),
})

app.post(
  '/users',
  zValidator('json', createUserSchema),
  async (c) => {
    const user = c.req.valid('json') // Fully typed!
    // user: { name: string, email: string, age?: number }

    const created = await db.users.create(user)
    return c.json(created, 201)
  }
)

// Validate query parameters
const querySchema = z.object({
  page: z.coerce.number().default(1),
  limit: z.coerce.number().default(10),
})

app.get(
  '/posts',
  zValidator('query', querySchema),
  (c) => {
    const { page, limit } = c.req.valid('query')
    return c.json({ page, limit })
  }
)
```

### 7. Route Grouping

```typescript
import { Hono } from 'hono'

const app = new Hono()

// API routes group
const api = new Hono()

api.get('/users', (c) => c.json({ users: [] }))
api.get('/users/:id', (c) => c.json({ id: c.req.param('id') }))
api.post('/users', (c) => c.json({ created: true }))

// Admin routes group
const admin = new Hono()

admin.use('*', authMiddleware) // All admin routes protected
admin.get('/dashboard', (c) => c.json({ stats: {} }))
admin.get('/users', (c) => c.json({ allUsers: [] }))

// Mount groups
app.route('/api/v1', api)
app.route('/admin', admin)

// Results in:
// GET /api/v1/users
// GET /api/v1/users/:id
// POST /api/v1/users
// GET /admin/dashboard
// GET /admin/users
```

### 8. Context Variables

```typescript
import { Hono } from 'hono'

type Env = {
  Variables: {
    user: { id: string; name: string }
    requestId: string
  }
}

const app = new Hono<Env>()

// Set variables in middleware
app.use('*', async (c, next) => {
  c.set('requestId', crypto.randomUUID())
  await next()
})

app.use('/protected/*', async (c, next) => {
  const token = c.req.header('Authorization')
  const user = await validateToken(token)
  c.set('user', user)
  await next()
})

// Access variables in handlers
app.get('/protected/profile', (c) => {
  const user = c.get('user') // Typed!
  const requestId = c.get('requestId')
  return c.json({ user, requestId })
})
```

### 9. Error Handling

```typescript
import { Hono, HTTPException } from 'hono'

const app = new Hono()

// Throw HTTP exceptions
app.get('/users/:id', async (c) => {
  const user = await db.users.find(c.req.param('id'))

  if (!user) {
    throw new HTTPException(404, { message: 'User not found' })
  }

  return c.json(user)
})

// Global error handler
app.onError((err, c) => {
  if (err instanceof HTTPException) {
    return c.json({ error: err.message }, err.status)
  }

  console.error(err)
  return c.json({ error: 'Internal server error' }, 500)
})

// Not found handler
app.notFound((c) => {
  return c.json({ error: 'Route not found' }, 404)
})
```

### 10. BetterAuth Integration

```typescript
import { Hono } from 'hono'
import { betterAuth } from 'better-auth'
import { cors } from 'hono/cors'

const auth = betterAuth({
  database: { /* ... */ },
  emailAndPassword: { enabled: true },
})

const app = new Hono()

app.use('/api/auth/*', cors({
  origin: ['http://localhost:3000'],
  credentials: true,
}))

// Mount BetterAuth routes
app.on(['GET', 'POST'], '/api/auth/*', (c) => {
  return auth.handler(c.req.raw)
})

// Protected route using BetterAuth
app.use('/api/*', async (c, next) => {
  const session = await auth.api.getSession({
    headers: c.req.raw.headers,
  })

  if (!session) {
    return c.json({ error: 'Unauthorized' }, 401)
  }

  c.set('user', session.user)
  await next()
})
```

## Runtime Adapters

### Cloudflare Workers

```typescript
import { Hono } from 'hono'

type Bindings = {
  KV: KVNamespace
  DB: D1Database
}

const app = new Hono<{ Bindings: Bindings }>()

app.get('/data', async (c) => {
  const value = await c.env.KV.get('key')
  return c.json({ value })
})

export default app
```

### Node.js

```typescript
import { Hono } from 'hono'
import { serve } from '@hono/node-server'

const app = new Hono()

app.get('/', (c) => c.text('Hello Node!'))

serve({
  fetch: app.fetch,
  port: 3000,
})
```

### Bun

```typescript
import { Hono } from 'hono'

const app = new Hono()

app.get('/', (c) => c.text('Hello Bun!'))

export default {
  port: 3000,
  fetch: app.fetch,
}
```

## Built-in Middleware

| Middleware | Purpose |
|------------|---------|
| `logger()` | Request logging |
| `cors()` | CORS headers |
| `jwt()` | JWT validation |
| `basicAuth()` | Basic authentication |
| `compress()` | Response compression |
| `cache()` | Response caching |
| `etag()` | ETag headers |
| `secureHeaders()` | Security headers |
| `csrf()` | CSRF protection |

## Common Patterns

### API Gateway

```typescript
import { Hono } from 'hono'

const app = new Hono()

// Rate limiting
app.use('/api/*', rateLimiter({
  windowMs: 60 * 1000,
  max: 100,
}))

// Request logging
app.use('*', logger())

// Route to backend services
app.all('/api/users/*', async (c) => {
  const url = new URL(c.req.url)
  url.host = 'users-service.internal'
  return fetch(url.toString(), c.req.raw)
})

app.all('/api/products/*', async (c) => {
  const url = new URL(c.req.url)
  url.host = 'products-service.internal'
  return fetch(url.toString(), c.req.raw)
})
```

### RESTful Resource

```typescript
import { Hono } from 'hono'

const users = new Hono()

users.get('/', async (c) => {
  const users = await db.users.findMany()
  return c.json(users)
})

users.get('/:id', async (c) => {
  const user = await db.users.findById(c.req.param('id'))
  return user ? c.json(user) : c.notFound()
})

users.post('/', async (c) => {
  const data = await c.req.json()
  const user = await db.users.create(data)
  return c.json(user, 201)
})

users.put('/:id', async (c) => {
  const data = await c.req.json()
  const user = await db.users.update(c.req.param('id'), data)
  return c.json(user)
})

users.delete('/:id', async (c) => {
  await db.users.delete(c.req.param('id'))
  return c.json({ deleted: true })
})

export default users
```

## Best Practices

1. **Use Typed Context**: Define Env type for bindings and variables
2. **Group Related Routes**: Use `new Hono()` and `.route()` for organization
3. **Validate Input**: Use `@hono/zod-validator` for request validation
4. **Handle Errors Globally**: Set up `onError` and `notFound` handlers
5. **Use Built-in Middleware**: Leverage logger, cors, jwt before custom solutions
6. **Keep Handlers Small**: Extract business logic to separate modules

## Troubleshooting

### CORS Issues
- Ensure `cors()` middleware is applied before route handlers
- Check `origin` whitelist includes client domain
- Enable `credentials: true` if sending cookies

### Type Errors with Context
- Define `Env` type with `Variables` and `Bindings`
- Use `Hono<Env>()` when creating app instance

### Middleware Not Running
- Check middleware order (runs top to bottom)
- Ensure `await next()` is called in custom middleware
- Verify route patterns match

## KCG integration

The Cianfhoghlaim platform's API layer — serving curriculum
data to the TanStack Start front-end, exposing the MCP server
for agent integration, and routing AG-UI SSE streams — is
built on Hono. Its multi-runtime support means the same API
code runs on Bun during development, on Cloudflare Workers
for edge deployment, and on the ARM1-OCI server for production.

The middleware composition enables:

- **Pocket ID SSO** — `auth.pocketId()` middleware
- **Langfuse tracing** — `tracing.langfuse()` middleware
  (every request traced end-to-end)
- **Rate limiting** — `rateLimit()` middleware
- **AG-UI SSE** — `mount('/agui', AGUIAdapter(agent).as_starlette_app())`

The KCG Hono apps are:

- `web/apps/cianfhoghlaim-web/src/server/router.ts` — the public
  lakehouse API
- `agents/api/_cianfhoghlaim_api/` — the FastAPI + Hono adapters for the
  oideachais web app
- `web/apps/tuatha-ui/src/server/` — the Tuatha MMO + crypto API

## Convex integration

The Tuatha MMO front-end uses Convex for real-time state
sync. Hono integrates with Convex via two patterns:

### `HonoWithConvex` (run Hono inside Convex)

```typescript
import { Hono } from "hono";
import { HonoWithConvex } from "convex-helpers";

const app = new Hono();
app.get("/api/me", (c) => c.json({ user: "..." }));

// Deploy Hono as a Convex HTTP action
export default HonoWithConvex(app, "/api");
```

### `HttpRouterWithHono` (call Convex from Hono)

```typescript
import { Hono } from "hono";
import { HttpRouterWithHono } from "convex-helpers";

const app = new Hono();
app.get("/api/curriculum", async (c) => {
  const convex = getConvexClient();
  const data = await convex.query("curriculum:list");
  return c.json(data);
});

// Bridge Hono routes into the Convex HTTP router
export const http = HttpRouterWithHono(app);
```

The canonical KCG pattern is `HttpRouterWithHono` — Hono
runs as the public API gateway; Convex handles the
real-time subscriptions and mutations.

## Resources

- **Documentation**: https://hono.dev
- **GitHub**: https://github.com/honojs/hono
- **Middleware**: https://hono.dev/middleware
- **Examples**: https://github.com/honojs/examples
