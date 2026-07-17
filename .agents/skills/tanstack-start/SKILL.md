---
name: tanstack-start
description: Comprehensive toolkit for TanStack Start — file-based routing, server functions, Query integration, multi-environment SSR, multi-tenant app scaffolding. Use when building production web/apps/cianfhoghlaim-web or web/apps/tuatha-ui surfaces, defining API routes, or wiring TanStack Query against DuckLake.
---

# TanStack Start

## KCG context (PRESERVED from the original 9-line skill)

- Adopt a **Local-First** reactive strategy.
- Use `@tanstack/react-router` for SSR routing and `@tanstack/db`
  for offline differential data syncs from DuckLake.
- **Authentication is per-surface, not global:**
  - `web/apps/cianfhoghlaim-web` — **no auth** (the public lakehouse)
  - `web/apps/tuatha-ui` — **no auth** (the public MMO)
  - `web/apps/croilar-portal` — uses `better-auth` + Pocket ID SSO + SIWE
- Bun workspaces:
  - `cianfhoghlaim-web` at `web/apps/cianfhoghlaim-web/`
  - `tuatha-ui` at `web/apps/tuatha-ui/`
  - `croilar-portal` at `web/apps/croilar-portal/`
- The route tree is generated at
  `web/apps/cianfhoghlaim-web/src/routeTree.gen.ts` — never edit by hand

## When to use this skill

Use when you need to:

- "Add a new route to `web/apps/cianfhoghlaim-web`"
- "Define a server function that calls a Dagster asset"
- "Wire a TanStack Query endpoint to a FastAPI / Hono route"
- "Create an API route that streams SSE for an agent"
- "Add a protected route in `web/apps/croilar-portal`"
- "Configure SSR mode for a specific page"
- "Build a multi-tenant layout with `RootDocument`"

## Project structure

The canonical layout for `web/apps/cianfhoghlaim-web/`:

```
web/apps/cianfhoghlaim-web/
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

## Protected routes (only in `web/apps/croilar-portal`)

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

`web/apps/cianfhoghlaim-web` is multi-tenant by design: a single deploy
serves all Irish / UK / Scottish / Welsh curricula. The
`tenant` is implicit in the route:

```typescript
// /curriculum/ie/mathematics  →  Irish Junior Cycle maths
// /curriculum/ni/ccea/english  →  Northern Ireland CCEA English
// /curriculum/sct/higher/chemistry  →  Scottish Higher Chemistry
```

The root layout reads the tenant from the URL and configures
the data fetchers (DuckLake `cianfhoghlaim.education.<tenant>`
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

## Type-Safe Forms with TanStack Form + Zod (KCG canonical)

For complex forms (multi-step, conditional fields, async
validation), use `@tanstack/react-form` + `zodValidator`:

```bash
bun add @tanstack/react-form @tanstack/zod-form-adapter zod
```

```typescript
import { useForm } from "@tanstack/react-form";
import { zodValidator } from "@tanstack/zod-form-adapter";
import { z } from "zod";

const loginSchema = z.object({
  email: z.string().email(),
  password: z.string().min(8),
});

function LoginForm() {
  const form = useForm({
    defaultValues: { email: "", password: "" },
    validators: { onChange: zodValidator(loginSchema) },
    onSubmit: async ({ value }) => {
      await loginAction({ data: value });
    },
  });

  return (
    <form
      onSubmit={(e) => {
        e.preventDefault();
        e.stopPropagation();
        form.handleSubmit();
      }}
    >
      <form.Field
        name="email"
        children={(field) => (
          <input
            name={field.name}
            value={field.state.value}
            onChange={(e) => field.handleChange(e.target.value)}
            onBlur={field.handleBlur}
          />
        )}
      />
      <form.Field
        name="password"
        children={(field) => (
          <input
            type="password"
            name={field.name}
            value={field.state.value}
            onChange={(e) => field.handleChange(e.target.value)}
            onBlur={field.handleBlur}
          />
        )}
      />
      <form.Subscribe
        selector={(state) => ({
          canSubmit: state.canSubmit,
          isSubmitting: state.isSubmitting,
        })}
        children={({ canSubmit, isSubmitting }) => (
          <button type="submit" disabled={!canSubmit}>
            {isSubmitting ? "Logging in..." : "Log in"}
          </button>
        )}
      />
    </form>
  );
}
```

The `form.Field` render-prop pattern + `form.Subscribe` for
state-derived UI is the canonical KCG form pattern. Pair with
`zodValidator` for runtime type safety (the Zod schema
mirrors the BAML Pydantic model — see
`.agents/skills/baml/SKILL.md`).

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
   `web/apps/croilar-portal` (other surfaces are public)

## Troubleshooting

- **Route tree out of sync?** Run `npx tanstack-router generate`
- **Hydration mismatch?** Check that `ssr: false` is set on
  any client-only route
- **Server function not found?** Check the import path; server
  functions must be re-exported from `src/server/functions/`
- **Build slow?** The route tree is generated on every build;
  cache the generator with `tanstackRouter: { generatedRouteTree: "src/routeTree.gen.ts" }`

## KCG TanStack patterns (round-9 deep dive)

The 6 long-form references under `references/` are KCG
synthesised patterns. The canonical lines to take from each:

### 1. Isomorphic server-fn + AI tool (`createServerFnTool`)

The "schema-first, server-only, AI-callable" pattern. One
function definition serves three consumers — the React
component, the API layer, **and** the LLM tool schema.

```typescript
import { createServerFnTool } from "@tanstack/ai-react";
import { z } from "zod";
import { getTopicSummary } from "@/lib/graph_rag";

export const fetchCommunitySummary = createServerFnTool({
  name: "fetch_community_summary",
  description:
    "Retrieves the pre-computed community summary for a syllabus topic.",
  inputSchema: z.object({
    topicId: z.string().describe("Official topic ID, e.g. 'JC-SCI-1.4'"),
    level: z.enum(["Higher", "Ordinary"]).default("Higher"),
  }),
  execute: async ({ topicId, level }) => {
    return await getTopicSummary(topicId, level);
  },
});
```

`useServerFn(...)` in the component, `tools: [...]` in
`useChat(...)` for the agent. Same Zod schema, same handler,
same execution context. No OpenAPI spec to maintain.

### 2. BAML → Zod schema bridge (the "Schema Gap")

BAML generates **TypeScript interfaces** for outputs; TanStack
AI requires **Zod schemas** for inputs. The KCG bridge pattern
is the **"Interface-Implements" utility type**:

```typescript
import type { LeavingCertSubject } from "@/baml_client/types";
import { z } from "zod";

type Implements<Model, Schema> =
  Schema extends z.ZodType<Model> ? Schema : never;

export const LeavingCertSubjectSchema: Implements<
  LeavingCertSubject,
  typeof schema
> = z.object({
  subject: z.string(),
  level: z.enum(["Higher", "Ordinary", "Foundation"]),
  grade: z.string().optional(),
  is_bonus_math: z.boolean(),
});

const schema = LeavingCertSubjectSchema;
```

If a BAML class field changes, the Implements guard raises
a TS error in the Zod schema — single source of truth
preserved. For large schemas, the round-9 reference shows
a `baml-to-zod.ts` generator script that reads the `.baml`
AST and emits `z.object({...})` definitions.

### 3. TanStack DB + DuckDB-WASM (the "Zero-Backend Analytics" stack)

The Oideachais data platform uses **TanStack DB** as the
reactive client cache on top of **DuckDB-WASM** in the
browser. The `QueryCollection` pattern bridges async
DuckDB results to sync TanStack DB collections:

1. User changes a filter → TanStack DB captures state
2. `queryFn` builds a SQL string against the DuckDB
   worker
3. Worker returns an Arrow table; main thread normalises
   by primary key
4. Live queries re-render only the changed components

For > 4 GB datasets, **MotherDuck** transparently routes
the same SQL to cloud execution; the client sees the
Arrow result either way. The KCG pattern uses
`registerFileUrl` + `httpfs` so DuckDB streams Parquet
column groups from R2 over HTTP Range requests — only
the queried columns download.

### 4. Better-T-Stack monorepo (the Cianfhoghlaim base)

Every `cianfhoghlaim/` frontend (`web/apps/cianfhoghlaim-web`, `tuath/ui`,
`aleyum`, `crypteolas`) is scaffolded from
`cianfhoghlaim-base`, which is the **Better-T-Stack CLI**
output with the KCG agent-instructions overlay
(`.roo/rules/ultracite.md`, `.ruler/bts.md`,
`.github/copilot-instructions.md`). The layout is fixed:

```
apps/web          TanStack Start
apps/native       Expo (mobile)
packages/api      oRPC (type-safe RPC)
packages/auth     BetterAuth
packages/db       Drizzle ORM
```

The agent-instruction files (AGENTS.md, CLAUDE.md,
GEMINI.md) are the *source of truth* for AI-assisted
dev. Never modify them per-app without bumping the
`cianfhoghlaim-base` template.

### 5. SSR / streaming mental model

`loaders` are **isomorphic** — they run on server (SSR) and
on client (navigation). The `beforeLoad` hook is the
canonical place for auth gates + tenant resolution.
`createServerFn()` is server-only; `useServerFn()` is the
client hook that calls it like a local function. SSE
streams use the `ReadableStream` controller in a route
file's `server.handlers.POST` — see `tanstack-ai-litellm.md`
for the full pattern (agent + RAG chunk streaming).

## KCG file conventions (round-9 synthesis)

From the `patterns-conventions.md` deep-dive:

- Routes: `kebab-case.tsx` for static, `$param.tsx` for
  dynamic (NOT `[param].tsx`), `$.tsx` for catch-all,
  `api.rpc.$.ts` for oRPC catch-all
- Components: `PascalCase.tsx`; colocate with the route
  in `src/components/`
- Server functions: `src/server/functions/`, one file
  per domain (curriculum.ts, leabharlann.ts, etc.)
- API routes: `src/routes/api/*` mirroring the URL path
- **Never** edit `src/routeTree.gen.ts` — it's regenerated
  on every `bun run build` from the file-based routes

The `visual-patterns.md` reference has the full
request/response cycle (HTTP → route match → loader → SSR
→ hydrate → client navigation → server fn → SSE) as
ASCII diagrams; see it for the canonical mental model.

See `references/tanstack-examples-analysis.md` for the
full 650-line 6-example canonical deep-dive, and
`references/architecture-deep-dive.md` for the 911-line
architecture reference.

## Resources

- TanStack Start docs: <https://tanstack.com/start/latest>
- TanStack Router docs: <https://tanstack.com/router/latest>
- TanStack Query docs: <https://tanstack.com/query/latest>
- AG-UI SSE protocol: `.agents/skills/ag-ui/SKILL.md`
- CopilotKit UI: `.agents/skills/copilotkit/SKILL.md`
- oRPC API: `.agents/skills/orpc/SKILL.md`
- Hono server: `.agents/skills/hono/SKILL.md`
