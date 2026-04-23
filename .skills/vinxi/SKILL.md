---
name: vinxi
description: Expert assistance for building full-stack applications with Vinxi. Use when users need file-based routing, server functions, SSR, or Vite-powered full-stack development.
---

# Vinxi - Full-Stack Framework

**Version:** ^0.5.1 | **Last Updated:** 2025-04

## Overview

Vinxi is a full-stack framework by Poimandres (Vite team):

- **Vite-Powered**: Built on Vite for fast development
- **File-Based Routing**: Automatic route generation
- **Server Functions**: Type-safe RPC-style server calls
- **SSR/Streaming**: Server-side rendering with streaming
- **Modular Architecture**: Plugin-based extensibility

**Documentation**: https://vinxi.dev

## When to Use This Skill

Activate when users need:

- "Create a Vinxi application"
- "Build a full-stack app with Vite"
- "Implement server-side rendering"
- "Add file-based routing"
- "Create server functions"

## Core Concepts

### 1. Project Setup

```bash
# Create new project
npm create vinxi@latest my-app
cd my-app
npm install
npm run dev
```

### 2. File-Based Routing

```
app/
├── routes/
│   ├── index.tsx          # /
│   ├── about.tsx          # /about
│   ├── blog/
│   │   ├── index.tsx      # /blog
│   │   └── $slug.tsx     # /blog/:slug
│   └── api/
│       └── hello.ts        # /api/hello
└── components/
```

### 3. Basic Route

```tsx
// app/routes/index.tsx
import { createFileRoute } from 'vinxi/routes'

export default createFileRoute('/')({
  component: HomePage,
})

function HomePage() {
  return (
    <div>
      <h1>Welcome to Vinxi</h1>
      <p>A full-stack framework powered by Vite</p>
    </div>
  )
}
```

### 4. Dynamic Routes

```tsx
// app/routes/blog/$slug.tsx
import { createFileRoute } from 'vinxi/routes'

export default createFileRoute('/blog/$slug')({
  component: BlogPost,
  loader: async ({ params }) => {
    const post = await fetchPost(params.slug)
    return post
  },
})

function BlogPost() {
  const post = Route.useLoaderData()
  const { slug } = Route.useParams()

  return (
    <article>
      <h1>{post.title}</h1>
      <p>{post.content}</p>
    </article>
  )
}
```

### 5. Server Functions

```tsx
// app/routes/api/hello.ts
import { createServerFn } from 'vinxi/server'

export const hello = createServerFn({ method: 'GET' })
  .validator((name: string) => name)
  .handler(async ({ data: name }) => {
    return { message: `Hello, ${name}!` }
  })

// Usage in component
import { hello } from '~/routes/api/hello'

async function handleClick() {
  const result = await hello({ data: 'World' })
  console.log(result.message) // "Hello, World!"
}
```

### 6. Server-Side Rendering

```tsx
// app/routes/index.tsx
import { createFileRoute } from 'vinxi/routes'

export default createFileRoute('/')({
  component: HomePage,
  ssr: true,  // Enable SSR
  streaming: true,  // Enable streaming
})

async function HomePage() {
  const data = await fetchData()  // Runs on server

  return (
    <div>
      <h1>{data.title}</h1>
      <Suspense fallback={<Loading />}>
        <AsyncComponent />
      </Suspense>
    </div>
  )
}
```

## Advanced Features

### Middleware

```tsx
// app/middleware.ts
import { createMiddleware } from 'vinxi/middleware'

export const middleware = createMiddleware({
  onRequest: async ({ request }) => {
    // Add authentication headers
    const auth = await checkAuth(request)
    if (!auth) {
      return new Response('Unauthorized', { status: 401 })
    }
  },
})
```

### Layouts

```tsx
// app/routes/__root.tsx
import { createFileRoute } from 'vinxi/routes'
import { Outlet } from 'vinxi/react-router-dom'

export default createFileRoute('/')({
  component: RootLayout,
})

function RootLayout() {
  return (
    <html>
      <head>
        <title>My App</title>
      </head>
      <body>
        <Header />
        <Outlet />
        <Footer />
      </body>
    </html>
  )
}
```

### Error Handling

```tsx
// app/routes/$.tsx
export default createFileRoute('/$')({
  component: NotFound,
  errorComponent: ErrorPage,
})

function NotFound() {
  return <div>404 - Page not found</div>
}

function ErrorPage({ error }) {
  return (
    <div>
      <h1>Something went wrong</h1>
      <p>{error.message}</p>
    </div>
  )
}
```

## Configuration

### vinxi.config.ts

```ts
import { defineConfig } from 'vinxi'

export default defineConfig({
  app: {
    head: {
      title: 'My App',
      meta: [
        { name: 'description', content: 'A Vinxi app' }
      ],
    },
  },
  routes: {
    defineRoutes: (route) => {
      route('/', './app/routes/index.tsx')
      route('/about', './app/routes/about.tsx')
    },
  },
  server: {
    preset: 'vercel',  // or 'netlify', 'cloudflare', 'node'
  },
})
```

## Best Practices

### Route Organization

1. **Group Related Routes**: Use folders for related routes
2. **Index Routes**: Use `index.tsx` for directory roots
3. **Catch-All Routes**: Use `$.tsx` for 404 handling

### Server Functions

1. **Validation**: Use validators for input validation
2. **Error Handling**: Handle errors gracefully
3. **Type Safety**: Leverage TypeScript for type safety

### Performance

1. **Code Splitting**: Use lazy loading for large components
2. **Streaming**: Enable streaming for slow data
3. **Caching**: Cache server function results

## Installation

```bash
npm create vinxi@latest
# or
npm install vinxi
```

## Project Integration

### Use Cases

| Scenario | Pattern |
|----------|---------|
| Full-Stack App | File-based routing + server functions |
| API Server | Server functions with validation |
| SSR App | Enable SSR with streaming |
| Multi-Platform | Deploy to Vercel, Netlify, Cloudflare |

### Related Skills

- [`tanstack-start`](.skills/tanstack-start/SKILL.md) - Alternative full-stack framework
- [`copilotkit`](.skills/copilotkit/SKILL.md) - AI agent UI integration
