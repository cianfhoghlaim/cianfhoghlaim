# 2026-08-24-wave-6-frontend-tanstack-modernisation-v1

## Why

Wave 5 consolidated the web apps to 5 canonical targets. Wave 6
modernises the FRONTEND stack to the 2026 ecosystem:

- **TanStack Start 1.0+** (file-based routing + server functions + RSC)
- **TanStack AI + TanStack DB + TanStack Form**
- **AG-UI protocol** for agent↔UI streaming
- **CopilotKit v2** for chat interfaces + frontend tools
- **Convex** as the single reactive backend (consolidates 3 deployments)
- **Better Auth 1.7** (consolidates 3 installs)
- **Tailwind 4 + Radix UI** (consolidates 3 installs)
- **Bun 1.4+ runtime** for the monorepo

Per the 2026-08-24 master refactor plan, Wave 6 establishes the
canonical 2026 frontend stack by:
1. **Fetching** the latest docs from each framework via firecrawl
2. **Auditing** the existing `web/packages/{auth,db,ui-kit}/` to see
   what's already installed
3. **Scaffolding** a reference app (the `tuatha/` app) with all the
   pieces wired together
4. **Documenting** the canonical patterns in `web/AGENTS.md`

## User preferences (locked-in from prior turns)

| Decision | Choice |
|:--|:--|
| Frontend stack (2026) | **TanStack Start + TanStack AI/DB/Form + AG-UI + CopilotKit v2 + Convex + Better Auth 1.7 + Tailwind 4 + Radix UI + Bun 1.4+** |
| Reference app | **`web/apps/tuatha/`** (was `tuatha-ui/`, renamed in Wave 5) — the Celtic MMO front-end |
| Convex schema | **Single `web/packages/db/convex/schema.ts`** — the canonical reactive schema for the platform |
| Better Auth | **Single `web/packages/auth/src/index.ts`** — consolidates the 3 installs |
| AG-UI handler | **Single `web/hono-api/src/routes/agui/index.ts`** — the canonical SSE endpoint |

## Dependencies

`Blocked by: 2026-08-24-wave-5-web-consolidation-v1` (✅ landed commit `dd0b2272e`)
`Unblocks: Future per-app migration PRs (Wave 5 follow-up #2-#4) that consume the canonical stack`

## What changes

### 1. Web packages canonical structure

The 3 existing packages at `web/packages/{auth,db,ui-kit}/` are
modernised to the 2026 stack. Two NEW packages are added:

```
web/packages/
├── auth/            # Better Auth 1.7 (consolidates 3 installs)
├── db/              # Convex schema + reactive queries (consolidates 3 deployments)
├── ui-kit/          # Radix UI + Tailwind 4 (consolidates 3 installs)
├── api-client/      # TanStack AI/DB/Form + CopilotKit v2 + AG-UI (NEW)
└── contracts/       # Shared TS types + Zod schemas (NEW)
```

### 2. Reference scaffold in `web/apps/tuatha/`

The `tuatha/` app (renamed in Wave 5) gets the full canonical
stack wired in:
- `app.config.ts` — TanStack Start 1.0+ config (file-based routing)
- `src/server/curriculum.ts` — server functions (TanStack Start)
- `src/components/agui/` — AG-UI agent slots
- `src/components/copilot/` — CopilotKit v2 chat interfaces
- `src/hooks/useCurriculumSearch.ts` — TanStack Query + Convex
- `convex/schema.ts` — Convex schema (mirrors `web/packages/db/convex/`)

### 3. `web/hono-api/` AG-UI route

The single Hono API gateway at `web/hono-api/` gets a new
`/agui/sse` endpoint that streams agent events to the frontend
via Server-Sent Events (SSE). This is the canonical AG-UI
integration point — every frontend app talks to one endpoint.

### 4. Documentation

- `web/AGENTS.md` — updated to document the canonical 2026 stack
- `web/packages/auth/README.md` — Better Auth 1.7 setup
- `web/packages/db/README.md` — Convex setup
- `web/packages/ui-kit/README.md` — Radix UI + Tailwind 4 setup
- `web/packages/api-client/README.md` — TanStack AI/DB/Form + CopilotKit v2 + AG-UI

## Out of scope (deferred)

- **Migrating all 5 apps to the canonical stack** — that's Wave 5
  follow-up #2-#4 (cianfhoghlaim-leaving-cert, croilar-portal, etc.)
- **TanStack Start production deployment** — deferred until the
  Cloudflare Pages migration PR lands (separate openspec change)
- **Convex schema migration** — the `web/packages/db/convex/` schema
  starts as an empty stub. Real Convex functions land in a Wave 6
  follow-up PR.

## Verification

After Wave 6 lands:

1. `web/packages/auth/package.json` shows `better-auth@^1.7.0`
2. `web/packages/db/convex/schema.ts` exists (stub ok)
3. `web/packages/ui-kit/package.json` shows `@radix-ui/*` + `tailwindcss@^4.0.0`
4. `web/packages/api-client/package.json` shows `@tanstack/react-start@^1.0.0`
   + `@copilotkit/runtime@^2.0.0`
5. `web/apps/tuatha/app.config.ts` exists (TanStack Start 1.0+ config)
6. `web/hono-api/src/routes/agui/index.ts` exists (AG-UI SSE endpoint)
7. `web/AGENTS.md` documents the canonical 2026 stack

## References

- Master plan: `openspec/plans/2026-08-24-master-refactor-plan.md`
- Wave 0-5: see prior openspec changes
