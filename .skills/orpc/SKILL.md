---
name: orpc
description: Expert assistance for building type-safe RPC APIs with oRPC. Use when users need contract-first API design, automatic client generation, end-to-end type safety, or OpenAPI documentation generation.
---

# oRPC - Type-Safe RPC Framework

**Version:** 1.x | **Last Updated:** 2025-01

## Overview

oRPC is a contract-first, type-safe RPC framework for TypeScript:

- **Contract-First**: Define API shape once, generate clients automatically
- **100% Type Safety**: Shared types between server and client
- **OpenAPI Generation**: Automatic documentation from contracts
- **Framework Agnostic**: Works with Hono, Express, TanStack Start
- **Real-Time Support**: Event iterators for streaming

**Documentation**: https://orpc.unnoq.com

## When to Use This Skill

Activate when users need:

- "Create a type-safe API"
- "Build RPC endpoints"
- "Generate API clients from contracts"
- "Add OpenAPI documentation"
- "Create type-safe server-client communication"

## Core Concepts

### 1. Contract Definition

```typescript
// packages/contracts/src/index.ts
import { oc } from '@orpc/contract'
import { z } from 'zod'

// Define schemas
const UserSchema = z.object({
  id: z.string(),
  name: z.string(),
  email: z.string().email(),
})

const CreateUserSchema = z.object({
  name: z.string().min(1),
  email: z.string().email(),
})

// Define procedures
export const signup = oc
  .input(CreateUserSchema)
  .output(UserSchema)

export const getUser = oc
  .input(z.object({ id: z.string() }))
  .output(UserSchema)

export const listUsers = oc
  .input(z.object({
    limit: z.number().default(10),
    cursor: z.number().optional(),
  }))
  .output(z.array(UserSchema))

// Export contract
export const contract = {
  auth: {
    signup,
  },
  users: {
    get: getUser,
    list: listUsers,
  },
}
```

### 2. Server Implementation

```typescript
// packages/server/src/orpc.ts
import { implement } from '@orpc/server'
import { contract } from '@repo/contracts'

export const os = implement(contract)

// Define context type
interface Context {
  user?: { id: string; name: string }
  headers: Headers
}

export const publicProcedure = os.$context<Context>()
```

```typescript
// packages/server/src/routers/auth.ts
import { publicProcedure } from '../orpc'

export const signup = publicProcedure.auth.signup
  .handler(async ({ input, context }) => {
    const user = await db.users.create({
      name: input.name,
      email: input.email,
    })
    return user
  })
```

```typescript
// packages/server/src/routers/users.ts
import { publicProcedure } from '../orpc'

export const getUser = publicProcedure.users.get
  .handler(async ({ input }) => {
    const user = await db.users.findById(input.id)
    if (!user) {
      throw new ORPCError('NOT_FOUND', { message: 'User not found' })
    }
    return user
  })

export const listUsers = publicProcedure.users.list
  .handler(async ({ input }) => {
    return await db.users.findMany({
      take: input.limit,
      skip: input.cursor,
    })
  })
```

### 3. Router Composition

```typescript
// packages/server/src/router.ts
import { publicProcedure } from './orpc'
import { signup } from './routers/auth'
import { getUser, listUsers } from './routers/users'

export const router = publicProcedure.router({
  auth: {
    signup,
  },
  users: {
    get: getUser,
    list: listUsers,
  },
})

export type AppRouter = typeof router
```

### 4. Middleware

```typescript
import { os, publicProcedure } from './orpc'
import { ORPCError } from '@orpc/server'

// Auth middleware
const authMiddleware = publicProcedure.middleware(async ({ context, next }) => {
  const session = await auth.api.getSession({
    headers: context.headers,
  })

  if (!session) {
    throw new ORPCError('UNAUTHORIZED', {
      message: 'Authentication required',
    })
  }

  return next({
    context: {
      user: session.user, // Type narrowed from User | undefined to User
    },
  })
})

export const authedProcedure = publicProcedure.use(authMiddleware)

// Use in handlers
export const updateProfile = authedProcedure.users.update
  .handler(async ({ input, context }) => {
    // context.user is guaranteed to exist
    return await db.users.update(context.user.id, input)
  })
```

### 5. Error Handling

```typescript
import { oc } from '@orpc/contract'
import { z } from 'zod'

// Define errors in contract
export const updateUser = oc
  .route({
    method: 'PUT',
    path: '/users/{id}',
  })
  .errors({
    NOT_FOUND: {
      message: 'User not found',
      data: z.object({ id: z.string() }),
    },
    UNAUTHORIZED: {
      message: 'Not authorized to update this user',
    },
    VALIDATION_ERROR: {
      message: 'Invalid input',
      data: z.object({ field: z.string() }),
    },
  })
  .input(UpdateUserSchema)
  .output(UserSchema)

// Server implementation
export const updateUser = authedProcedure.users.update
  .handler(async ({ input, context, errors }) => {
    const user = await db.users.find(input.id)

    if (!user) {
      throw errors.NOT_FOUND({ data: { id: input.id } })
    }

    if (user.id !== context.user.id) {
      throw errors.UNAUTHORIZED()
    }

    return await db.users.update(input.id, input)
  })
```

### 6. Client Setup

```typescript
// apps/web/src/lib/orpc.ts
import { createORPCClient } from '@orpc/client'
import { RPCLink } from '@orpc/client/fetch'
import { createTanstackQueryUtils } from '@orpc/tanstack-query'

// Create RPC link
export const link = new RPCLink({
  url: '/api/rpc',
  fetch(url, options) {
    return fetch(url, {
      ...options,
      credentials: 'include', // Include cookies
    })
  },
  headers: async () => {
    const token = localStorage.getItem('token')
    return token ? { Authorization: `Bearer ${token}` } : {}
  },
})

// Create client
const client = createORPCClient(link)

// Create TanStack Query utilities
export const orpc = createTanstackQueryUtils(client)
```

### 7. React Integration

```typescript
import { useQuery, useMutation } from '@tanstack/react-query'
import { orpc } from '@/lib/orpc'

function UserList() {
  // Query with full type safety
  const { data: users, isLoading } = useQuery(
    orpc.users.list.queryOptions({
      input: { limit: 20 }
    })
  )

  // Mutation
  const { mutate: createUser } = useMutation(
    orpc.auth.signup.mutationOptions({
      onSuccess: () => {
        queryClient.invalidateQueries({
          queryKey: orpc.users.list.key(),
        })
      },
    })
  )

  const handleCreate = () => {
    createUser({
      name: 'John Doe',
      email: 'john@example.com',
    })
  }

  if (isLoading) return <div>Loading...</div>

  return (
    <div>
      {users?.map(user => (
        <div key={user.id}>{user.name}</div>
      ))}
      <button onClick={handleCreate}>Add User</button>
    </div>
  )
}
```

### 8. Infinite Queries

```typescript
import { useSuspenseInfiniteQuery } from '@tanstack/react-query'
import { orpc } from '@/lib/orpc'

function InfiniteUserList() {
  const { data, fetchNextPage, hasNextPage } = useSuspenseInfiniteQuery(
    orpc.users.list.infiniteOptions({
      input: (cursor) => ({ cursor, limit: 10 }),
      getNextPageParam: (lastPage) =>
        lastPage.length === 10 ? lastPage.at(-1)?.id : null,
      initialPageParam: 0,
    })
  )

  return (
    <div>
      {data.pages.flat().map(user => (
        <div key={user.id}>{user.name}</div>
      ))}
      <button
        onClick={() => fetchNextPage()}
        disabled={!hasNextPage}
      >
        Load More
      </button>
    </div>
  )
}
```

### 9. Server Integration (Hono)

```typescript
import { Hono } from 'hono'
import { RPCHandler } from '@orpc/server/fetch'
import { router } from './router'

const app = new Hono()
const rpcHandler = new RPCHandler(router)

app.all('/api/rpc/*', async (c) => {
  const { response } = await rpcHandler.handle(c.req.raw, {
    prefix: '/api/rpc',
    context: {
      headers: c.req.raw.headers,
      user: c.get('user'),
    },
  })

  return response || c.text('Not Found', 404)
})

export default app
```

### 10. TanStack Start Integration

```typescript
// src/routes/api.rpc.$.ts
import { RPCHandler } from '@orpc/server/fetch'
import { createFileRoute } from '@tanstack/react-router'
import { router } from '@/orpc/router'

const handler = new RPCHandler(router)

async function handle({ request }: { request: Request }) {
  const { response } = await handler.handle(request, {
    prefix: '/api/rpc',
    context: {
      headers: request.headers,
    },
  })
  return response ?? new Response('Not Found', { status: 404 })
}

export const Route = createFileRoute('/api/rpc/$')({
  server: {
    handlers: {
      GET: handle,
      POST: handle,
      PUT: handle,
      DELETE: handle,
    },
  },
})
```

### 11. OpenAPI Generation

```typescript
import { OpenAPIHandler } from '@orpc/openapi/fetch'
import { OpenAPIReferencePlugin } from '@orpc/openapi/plugins'
import { router } from './router'

const handler = new OpenAPIHandler(router, {
  plugins: [
    new OpenAPIReferencePlugin({
      specGenerateOptions: {
        info: {
          title: 'My API',
          version: '1.0.0',
        },
        security: [{ bearerAuth: [] }],
        components: {
          securitySchemes: {
            bearerAuth: {
              type: 'http',
              scheme: 'bearer',
            },
          },
        },
      },
    }),
  ],
})

// OpenAPI docs served at /api endpoint
```

### 12. Streaming (Event Iterators)

```typescript
import { oc, eventIterator } from '@orpc/contract'
import { z } from 'zod'

// Contract
export const subscribe = oc
  .route({
    method: 'GET',
    path: '/room/subscribe',
  })
  .input(z.object({ room: z.string() }))
  .output(eventIterator(z.object({
    message: z.string(),
    timestamp: z.number(),
  })))

// Server
export const subscribe = authedProcedure.room.subscribe
  .handler(async function* ({ input, context, signal }) {
    const subscription = pubsub.subscribe(input.room)

    try {
      for await (const message of subscription) {
        if (signal.aborted) break
        yield {
          message: message.text,
          timestamp: Date.now(),
        }
      }
    } finally {
      subscription.unsubscribe()
    }
  })
```

## Monorepo Structure

```
project/
├── packages/
│   ├── contracts/           # API contracts
│   │   ├── src/
│   │   │   ├── index.ts    # Contract definitions
│   │   │   └── schemas/    # Zod schemas
│   │   └── package.json
│   ├── server/             # Server implementation
│   │   ├── src/
│   │   │   ├── orpc.ts     # ORPC setup
│   │   │   ├── router.ts   # Main router
│   │   │   └── routers/    # Procedure implementations
│   │   └── package.json
│   └── shared/             # Shared utilities
├── apps/
│   ├── web/               # Frontend app
│   │   ├── src/
│   │   │   └── lib/
│   │   │       └── orpc.ts # Client setup
│   │   └── package.json
│   └── api/               # API server
└── package.json
```

## Type Inference

```typescript
import {
  InferContractRouterInputs,
  InferContractRouterOutputs
} from '@orpc/contract'

// Infer types from contract
type Inputs = InferContractRouterInputs<typeof contract>
type Outputs = InferContractRouterOutputs<typeof contract>

// Usage
type SignupInput = Inputs['auth']['signup']
// { name: string; email: string }

type UserOutput = Outputs['users']['get']
// { id: string; name: string; email: string }
```

## Best Practices

1. **Contract-First**: Define contracts before implementation
2. **Centralize Schemas**: Keep Zod schemas in contracts package
3. **Use Middleware**: Compose authentication and logging via middleware
4. **Define Errors**: Specify errors in contracts for type-safe handling
5. **Separate Concerns**: Keep contracts, server, and client in separate packages
6. **Use External Deps**: Externalize @orpc/* in tsup.config.ts to prevent TS2742

## Troubleshooting

### TS2742 Errors
- Centralize @orpc/* dependencies in root package.json
- Add external configuration to tsup.config.ts:
  ```typescript
  export default defineConfig({
    external: ['@orpc/contract', '@orpc/server', 'zod'],
  })
  ```

### Type Inference Issues
- Ensure contracts are exported correctly
- Check that Zod schemas match expected types
- Verify client is created from correct contract

### Context Not Available
- Check middleware provides context correctly
- Ensure `next()` returns context updates
- Verify middleware order in procedure chain

## Resources

- **Documentation**: https://orpc.unnoq.com
- **GitHub**: https://github.com/unnoq/orpc
- **Examples**: https://github.com/unnoq/orpc/tree/main/examples
