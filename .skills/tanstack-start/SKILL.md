---
name: tanstack-start
description: Expert assistance for building full-stack React applications with TanStack Start. Use when users need file-based routing, server functions, SSR, streaming, or integration with TanStack Router and Query.
---

# TanStack Start - Full-Stack React Framework

**Version:** ^1.94.0 | **Last Updated:** 2025-04

## Overview

TanStack Start is a full-stack meta-framework built on React and TanStack Router:

- **File-Based Routing**: Automatic route tree generation
- **Server Functions**: Type-safe RPC-style server calls
- **SSR/Streaming**: Server-side rendering with streaming support
- **Type Safety**: End-to-end TypeScript integration
- **Integrations**: TanStack Query, Store, and ecosystem
- **React Server Components**: Full RSC support for optimal performance
- **Edge Runtime**: Deploy to edge platforms (Vercel, Cloudflare)
- **Streaming Suspense**: Progressive UI rendering with Suspense boundaries

**Documentation**: https://tanstack.com/start

## When to Use This Skill

Activate when users need:

- "Create a TanStack Start application"
- "Add file-based routing"
- "Create server functions"
- "Implement SSR with streaming"
- "Integrate TanStack Query"

## Core Concepts

### 1. Project Structure

```
src/
├── routes/                    # File-based routing
│   ├── __root.tsx            # Root layout
│   ├── index.tsx             # Home page (/)
│   ├── demo/
│   │   └── page.tsx          # /demo/page
│   ├── users/
│   │   ├── index.tsx         # /users
│   │   └── $userId.tsx       # /users/:userId
│   └── api.$.ts              # Catch-all API route
├── components/               # React components
├── lib/                      # Utilities
├── integrations/            # Third-party integrations
├── router.tsx               # Router initialization
└── routeTree.gen.ts         # AUTO-GENERATED (do not edit)
```

### 2. File-Based Routing

```typescript
// src/routes/index.tsx
import { createFileRoute } from '@tanstack/react-router'

export const Route = createFileRoute('/')({
  component: HomePage,
})

function HomePage() {
  return <div>Welcome to TanStack Start</div>
}
```

### 3. Dynamic Routes

```typescript
// src/routes/users/$userId.tsx
import { createFileRoute } from '@tanstack/react-router'

export const Route = createFileRoute('/users/$userId')({
  component: UserPage,
  loader: async ({ params }) => {
    const user = await fetchUser(params.userId)
    if (!user) throw new Error('User not found')
    return user
  },
})

function UserPage() {
  const user = Route.useLoaderData()
  const { userId } = Route.useParams()

  return (
    <div>
      <h1>{user.name}</h1>
      <p>ID: {userId}</p>
    </div>
  )
}
```

### 4. Server Functions

```typescript
// src/routes/demo/todos.tsx
import { createServerFn } from '@tanstack/react-start'
import { createFileRoute } from '@tanstack/react-router'

// GET server function
const getTodos = createServerFn({
  method: 'GET',
}).handler(async () => {
  return await db.query.todos.findMany()
})

// POST server function with validation
const addTodo = createServerFn({ method: 'POST' })
  .inputValidator((d: { title: string }) => d)
  .handler(async ({ data }) => {
    await db.insert(todos).values({ title: data.title })
    return { success: true }
  })

export const Route = createFileRoute('/demo/todos')({
  component: TodoPage,
  loader: async () => await getTodos(),
})

function TodoPage() {
  const todos = Route.useLoaderData()
  const router = useRouter()

  const handleAdd = async (title: string) => {
    await addTodo({ data: { title } })
    router.invalidate() // Refresh loader data
  }

  return (
    <div>
      <ul>
        {todos.map(todo => <li key={todo.id}>{todo.title}</li>)}
      </ul>
      <button onClick={() => handleAdd('New Todo')}>Add</button>
    </div>
  )
}
```

### 5. Root Layout

```typescript
// src/routes/__root.tsx
import { createRootRouteWithContext } from '@tanstack/react-router'
import { HeadContent, Scripts } from '@tanstack/react-router'
import type { QueryClient } from '@tanstack/react-query'

interface RouterContext {
  queryClient: QueryClient
}

export const Route = createRootRouteWithContext<RouterContext>()({
  head: () => ({
    meta: [
      { charSet: 'utf-8' },
      { name: 'viewport', content: 'width=device-width, initial-scale=1' },
      { title: 'My App' },
    ],
  }),
  component: RootLayout,
})

function RootLayout() {
  return (
    <html lang="en">
      <head>
        <HeadContent />
      </head>
      <body>
        <Header />
        <main>
          <Outlet />
        </main>
        <Scripts />
      </body>
    </html>
  )
}
```

### 6. Navigation

```typescript
import { Link, useRouter } from '@tanstack/react-router'

function Navigation() {
  const router = useRouter()

  return (
    <nav>
      {/* Simple link */}
      <Link to="/">Home</Link>

      {/* Link with parameters */}
      <Link to="/users/$userId" params={{ userId: '123' }}>
        User Profile
      </Link>

      {/* Link with search params */}
      <Link to="/posts" search={{ page: 1, limit: 10 }}>
        Posts
      </Link>

      {/* Active state styling */}
      <Link
        to="/dashboard"
        activeProps={{ className: 'font-bold text-blue-600' }}
        inactiveProps={{ className: 'text-gray-600' }}
      >
        Dashboard
      </Link>

      {/* Programmatic navigation */}
      <button onClick={() => router.navigate({
        to: '/users/$userId',
        params: { userId: '456' }
      })}>
        Go to User
      </button>
    </nav>
  )
}
```

### 7. TanStack Query Integration

```typescript
// src/router.tsx
import { createRouter } from '@tanstack/react-router'
import { QueryClient, QueryClientProvider } from '@tanstack/react-query'
import { routeTree } from './routeTree.gen'

export const getRouter = () => {
  const queryClient = new QueryClient()

  const router = createRouter({
    routeTree,
    context: { queryClient },
    defaultPreload: 'intent',
    Wrap: ({ children }) => (
      <QueryClientProvider client={queryClient}>
        {children}
      </QueryClientProvider>
    ),
  })

  return router
}
```

### 8. API Routes

```typescript
// src/routes/api.users.ts
import { createFileRoute, json } from '@tanstack/react-start'

export const Route = createFileRoute('/api/users')({
  server: {
    handlers: {
      GET: async ({ request }) => {
        const users = await getAllUsers()
        return json(users)
      },
      POST: async ({ request }) => {
        const body = await request.json()
        const user = await createUser(body)
        return json(user, { status: 201 })
      },
    },
  },
})
```

### 9. Streaming Responses

```typescript
import { createServerFn } from '@tanstack/react-start'

export const streamAI = createServerFn({
  method: 'POST',
  response: 'raw',
}).handler(async ({ data, signal }) => {
  const stream = new ReadableStream({
    async start(controller) {
      const response = await fetch('https://api.openai.com/v1/chat', {
        method: 'POST',
        body: JSON.stringify({ prompt: data.prompt }),
        signal,
      })

      const reader = response.body.getReader()
      while (true) {
        const { done, value } = await reader.read()
        if (done) break
        controller.enqueue(value)
      }
      controller.close()
    },
  })

  return new Response(stream, {
    headers: { 'Content-Type': 'text/event-stream' },
  })
})
```

### 10. SSR Modes

```typescript
// Full SSR (default)
export const Route = createFileRoute('/page')({
  component: PageComponent,
  loader: async () => await getData(),
})

// Data-only SSR (client renders)
export const Route = createFileRoute('/page')({
  ssr: 'data-only',
  component: PageComponent,
  loader: async () => await getData(),
})

// SPA mode (no SSR)
export const Route = createFileRoute('/page')({
  ssr: false,
  component: PageComponent,
})
```

## Vite Configuration

```typescript
// vite.config.ts
import { defineConfig } from 'vite'
import { tanstackStart } from '@tanstack/react-start/plugin/vite'
import viteReact from '@vitejs/plugin-react'
import viteTsConfigPaths from 'vite-tsconfig-paths'

export default defineConfig({
  plugins: [
    viteTsConfigPaths(),
    tanstackStart(),
    viteReact(),
  ],
})
```

## File Naming Conventions

| Pattern | Route Path |
|---------|------------|
| `index.tsx` | `/` |
| `about.tsx` | `/about` |
| `users.tsx` | `/users` |
| `users/index.tsx` | `/users` |
| `users/$userId.tsx` | `/users/:userId` |
| `posts.$postId.tsx` | `/posts/:postId` |
| `api.$.ts` | `/api/*` (catch-all) |

## Common Patterns

### Protected Routes

```typescript
export const Route = createFileRoute('/_authenticated')({
  beforeLoad: async ({ location }) => {
    if (!isAuthenticated()) {
      throw redirect({
        to: '/login',
        search: { redirect: location.href },
      })
    }
  },
  component: AuthenticatedLayout,
})
```

### Error Boundaries

```typescript
export const Route = createFileRoute('/posts')({
  loader: () => fetchPosts(),
  errorComponent: ({ error, reset }) => (
    <div>
      <p>Error: {error.message}</p>
      <button onClick={reset}>Retry</button>
    </div>
  ),
  component: PostsPage,
})
```

### Form Handling

```typescript
function CreateTodoForm() {
  const router = useRouter()

  const handleSubmit = async (e: React.FormEvent<HTMLFormElement>) => {
    e.preventDefault()
    const formData = new FormData(e.currentTarget)
    const title = formData.get('title') as string

    await addTodo({ data: { title } })
    router.invalidate()
    e.currentTarget.reset()
  }

  return (
    <form onSubmit={handleSubmit}>
      <input type="text" name="title" required />
      <button type="submit">Add</button>
    </form>
  )
}
```

## Best Practices

1. **Use File-Based Routing**: Automatic code splitting per route
2. **Prefer Server Functions**: Type-safe server communication
3. **Leverage Loaders**: Pre-fetch data for faster page loads
4. **Use router.invalidate()**: Refresh data after mutations
5. **Enable Preloading**: Set `defaultPreload: 'intent'` for faster navigation
6. **Type Your Context**: Define router context interface for type safety

## Troubleshooting

### Route Not Found
- Check file naming conventions
- Run `npx tanstack-router generate` to regenerate route tree
- Verify route path matches file structure

### Server Function Errors
- Ensure server functions are in route files or imported correctly
- Check input validators match expected data shape
- Verify server-side dependencies are available

### SSR Hydration Mismatch
- Ensure server and client render same content
- Check for browser-only APIs in server code
- Use `useEffect` for client-only operations

## Resources

- **Documentation**: https://tanstack.com/start
- **Router Docs**: https://tanstack.com/router
- **Query Docs**: https://tanstack.com/query
- **GitHub**: https://github.com/TanStack/router
