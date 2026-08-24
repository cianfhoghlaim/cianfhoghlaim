# @cianfhoghlaim/db — Convex reactive backend

Per the **2026-08-24-wave-6-frontend-tanstack-modernisation-v1**
openspec change. The canonical Convex reactive schema + client for the
Cianfhoghlaim platform.

## Setup

```bash
bun add @cianfhoghlaim/db
```

## Convex CLI

The `convex:dev` and `convex:deploy` scripts are exposed:

```bash
bun run convex:dev      # Local dev deployment
bun run convex:deploy   # Production deployment
```

## Schema

The schema is defined at `web/packages/db/convex/schema.ts`. Wave 6
delivers a STUB schema with a placeholder table — the real schema
(agents, threads, runs, messages, knowledge_graph_nodes, per-subject
caches) lands in a Wave 6 follow-up PR.

## Convex + TanStack Start

The integration is documented at
https://docs.convex.dev/client/tanstack/tanstack-start. The 5
consolidated web apps use this integration via
`web/packages/api-client` (TanStack DB reactive subscription).

## Convex + Better Auth

The integration is documented at
https://www.better-auth.com/docs/integrations/convex. The auth client
lives at `web/packages/db/convex/auth.ts` and is consumed by
`web/packages/auth`.
