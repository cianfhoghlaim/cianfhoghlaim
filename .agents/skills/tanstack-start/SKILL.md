---
name: tanstack-start
description: Comprehensive toolkit for TanStack Start — file-based routing, server functions, Query integration, multi-environment SSR, multi-tenant app scaffolding. Use when building production oideachais/web or tuatha/ui surfaces, defining API routes, or wiring TanStack Query against DuckLake.
---

# TanStack Start

## KCG context (PRESERVED from the original 9-line skill)

- Adopt a **Local-First** reactive strategy.
- Use `@tanstack/react-router` for SSR routing and `@tanstack/db`
  for offline differential data syncs from DuckLake.
- **Authentication is per-surface, not global:**
  - `oideachais/web` — **no auth** (the public lakehouse)
  - `tuatha/ui` — **no auth** (the public MMO)
  - `croilar/apps/portal` — uses `better-auth` + Pocket ID SSO + SIWE
- Bun workspaces:
  - `oideachais-web` at `oideachais/web/`
  - `tuatha-ui` at `tuatha/ui/`
  - `croilar-portal` at `croilar/apps/portal/`
- The route tree is generated at
  `oideachais/web/src/routeTree.gen.ts` — never edit by hand

## When to use this skill

Use when you need to:

- "Add a new route to `oideachais/web`"
- "Define a server function that calls a Dagster asset"
- "Wire a TanStack Query endpoint to a FastAPI / Hono route"
- "Create an API route that streams SSE for an agent"
- "Add a protected route in `croilar/apps/portal`"
- "Configure SSR mode for a specific page"
- "Build a multi-tenant layout with `RootDocument`"

## Project structure

The canonical layout for `oideachais/web/`:

```
oideachais/web/
├── src/
│   ├── routes/                    # file-based routes
│   │   ├── __root.tsx             # RootDocument (HTML shell)
│   │   ├── index.tsx              # /
│   │   ├── about.tsx              # /about
│   │   ├── curriculum/            # /curriculum/*
│   │   │   ├── index.tsx
│   │   │   ├── $subject.tsx
│   │   │   └── $subject.$strand.tsx
│   │   └── api/                   # /api/*
│   │       ├── search.ts
│   │       └── dashboard.ts
│   ├── routeTree.gen.ts           # auto-generated, never edit
│   ├── router.ts                  # createRouter() config
│   ├── server/                    # server-only code
│   │   ├── functions/             # createServerFn() handlers
│   │   ├── router.ts              # oRPC router
│   │   └── queries/               # TanStack Query endpoints
│   ├── components/                # shared components
│   ├── lib/                       # utilities
│   └── styles.css
├── app.config.ts                  # TanStack Start Vite config
├── package.json
└── tsconfig.json
```

## File-based routing

### Static routes

```typescript
// src/routes/about.tsx
import { createFileRoute } from "@tanstack/react-router";

export const Route = createFileRoute("/about")({
  component: AboutPage,
});

function AboutPage() {
  return <h1>About</h1>;
}
```

### Dynamic routes

```typescript
// src/routes/curriculum/$subject.tsx
export const Route = createFileRoute("/curriculum/$subject")({
  loader: async ({ params }) => {
    return fetch(`/api/curriculum/${params.subject}`).then(r => r.json());
  },
  component: SubjectPage,
});

function SubjectPage() {
  const { subject } = Route.useParams();
  const data = Route.useLoaderData();
  return <h1>{subject}</h1>;
}
```

### Nested routes

```typescript
// src/routes/curriculum.tsx (layout)
export const Route = createFileRoute("/curriculum")({
  component: CurriculumLayout,
});

function CurriculumLayout() {
  return (
    <div>
      <nav>...</nav>
      <Outlet />
    </div>
  );
}
```

## Server functions

`createServerFn()` is the canonical pattern for server-side
data fetching / mutations. The function runs on the server only;
the client can call it like a regular async function.

```typescript
// src/server/functions/curriculum.ts
import { createServerFn } from "@tanstack/react-start";
import { z } from "zod";

export const getCurriculumSubject = createServerFn({ method: "GET" })
  .inputValidator(z.object({ subject: z.string() }))
  .handler(async ({ data }) => {
    const response = await fetch(
      `${process.env.DUCKLAKE_API_URL}/curriculum/${data.subject}`,
    );
    return response.json();
  });
```

```typescript
// In a component
import { getCurriculumSubject } from "@/server/functions/curriculum";

function Page() {
  const data = useLoaderServerFn(getCurriculumSubject, {
    data: { subject: "mathematics" },
  });
  return <pre>{JSON.stringify(data, null, 2)}</pre>;
}
```

## TanStack Query integration

`createRouter` accepts a `QueryClient` via `RouterContext`. All
routes then have access to the query client via `useQuery` /
`useMutation`.

```typescript
// src/router.ts
import { createRouter } from "@tanstack/react-router";
import { QueryClient } from "@tanstack/react-query";

const queryClient = new QueryClient({
  defaultOptions: { queries: { staleTime: 60_000 } },
});

export const router = createRouter({
  routeTree,
  context: { queryClient },
  defaultPreload: "intent",
});

declare module "@tanstack/react-router" {
  interface Register {
    router: typeof router;
  }
}
```

```typescript
// In a component
import { useQuery } from "@tanstack/react-query";

function Page() {
  const { data } = useQuery({
    queryKey: ["curriculum", subject],
    queryFn: () => fetch(`/api/curriculum/${subject}`).then(r => r.json()),
  });
  return <pre>{JSON.stringify(data, null, 2)}</pre>;
}
```

## API routes

For non-server-fn endpoints (e.g. SSE for an AG-UI agent):

```typescript
// src/routes/api/agent/chat.ts
import { createFileRoute } from "@tanstack/react-router";

export const Route = createFileRoute("/api/agent/chat")({
  server: {
    handlers: {
      POST: async ({ request }) => {
        const { message } = await request.json();
        const stream = await fetch(AGENT_BACKEND_URL, {
          method: "POST",
          body: JSON.stringify({ message }),
        }).then(r => r.body);
        return new Response(stream, {
          headers: { "content-type": "text/event-stream" },
        });
      },
    },
  },
});
```

## SSR modes

Three modes, configurable per-page or globally:

| Mode | When | Trade-off |
|:--|:--|:--|
| `"default"` (full SSR) | Most pages | Fast first paint, no client JS needed for HTML |
| `"data-only"` | Dashboards, heavy data | HTML is static, client fetches data |
| `false` (client-only) | Auth-gated pages, websockets | No SSR; minimal server cost |

```typescript
// Global config (app.config.ts)
export default defineConfig({
  server: { ssr: true },  // full SSR for all routes
});

// Per-page (in a route file)
export const Route = createFileRoute("/dashboard")({
  ssr: "data-only",  // override for this route
});
```

## Streaming

For SSE (AG-UI, log streaming, large data exports):

```typescript
export const Route = createFileRoute("/api/agent/chat")({
  server: {
    handlers: {
      POST: async ({ request }) => {
        return new Response(
          new ReadableStream({
            async start(controller) {
              const encoder = new TextEncoder();
              for await (const chunk of upstream) {
                controller.enqueue(encoder.encode(chunk));
              }
              controller.close();
            },
          }),
          { headers: { "content-type": "text/event-stream" } },
        );
      },
    },
  },
});
```

## Protected routes (only in `croilar/apps/portal`)

```typescript
import { redirect } from "@tanstack/react-router";

export const Route = createFileRoute("/portal/")({
  beforeLoad: async ({ context }) => {
    if (!context.auth.user) {
      throw redirect({ to: "/login" });
    }
  },
  component: PortalLayout,
});
```

## Error boundaries

```typescript
export const Route = createFileRoute("/curriculum/")({
  errorComponent: ({ error, reset }) => (
    <div>
      <h1>Error: {error.message}</h1>
      <button onClick={reset}>Try again</button>
    </div>
  ),
  pendingComponent: () => <Spinner />,
});
```

## Vite config (canonical)

```typescript
// app.config.ts
import { defineConfig } from "@tanstack/react-start/config/vite";
import tsconfigPaths from "vite-tsconfig-paths";

export default defineConfig({
  vite: {
    plugins: [tsconfigPaths()],
  },
});
```

## Multi-tenant app scaffolding

`oideachais/web` is multi-tenant by design: a single deploy
serves all Irish / UK / Scottish / Welsh curricula. The
`tenant` is implicit in the route:

```typescript
// /curriculum/ie/mathematics  →  Irish Junior Cycle maths
// /curriculum/ni/ccea/english  →  Northern Ireland CCEA English
// /curriculum/sct/higher/chemistry  →  Scottish Higher Chemistry
```

The root layout reads the tenant from the URL and configures
the data fetchers (DuckLake `oideachais.education.<tenant>`
schema).

## Naming conventions

- Route files use `kebab-case.tsx` (e.g. `about-us.tsx`)
- Server functions use `camelCase` (e.g. `getCurriculumSubject`)
- Component files use `PascalCase.tsx` (e.g. `SubjectCard.tsx`)
- API routes mirror the URL path (e.g. `/api/curriculum/$subject`)

## Forms

For forms that submit to a server function, use the
`<form action={serverFn}>` pattern:

```typescript
function ContactForm() {
  const submit = useServerFn(contactAction);
  return (
    <form action={(formData) => submit({ data: Object.fromEntries(formData) })}>
      <input name="email" type="email" required />
      <button type="submit">Send</button>
    </form>
  );
}
```

## Best practices

1. **Use file-based routing** — never define routes by hand
2. **Use `createServerFn` for server-only code** — never use
   `useEffect` for data fetching
3. **Use TanStack Query for client-cached data** — the
   `staleTime` default is 60s
4. **Use `errorComponent` + `pendingComponent`** on every route
5. **Use `ssr: "data-only"` for dashboards** — full SSR is
   overkill for data-heavy pages
6. **Use `beforeLoad` + `redirect` for auth** — but only in
   `croilar/apps/portal` (other surfaces are public)

## Troubleshooting

- **Route tree out of sync?** Run `npx tanstack-router generate`
- **Hydration mismatch?** Check that `ssr: false` is set on
  any client-only route
- **Server function not found?** Check the import path; server
  functions must be re-exported from `src/server/functions/`
- **Build slow?** The route tree is generated on every build;
  cache the generator with `tanstackRouter: { generatedRouteTree: "src/routeTree.gen.ts" }`

## Resources

- TanStack Start docs: <https://tanstack.com/start/latest>
- TanStack Router docs: <https://tanstack.com/router/latest>
- TanStack Query docs: <https://tanstack.com/query/latest>
- AG-UI SSE protocol: `.agents/skills/ag-ui/SKILL.md`
- CopilotKit UI: `.agents/skills/copilotkit/SKILL.md`
- oRPC API: `.agents/skills/orpc/SKILL.md`
- Hono server: `.agents/skills/hono/SKILL.md`
