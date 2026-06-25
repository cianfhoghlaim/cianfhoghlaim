# Proposal: State-of-the-Art Refactor & Build-Out for 5 Frontend Workspaces

## Why

The 5 TypeScript frontend workspaces in the Cianfhoghlaim monorepo have substantial scaffolding (~17K LOC) but are not end-to-end deployable. Key gaps:
- No root READMEs or on-ramps for 3 of 5 projects
- Auth is scaffolded but never wired (Better Auth, SIWE, x402, org-scoped JWT)
- Convex `_generated/` types are missing — all Convex imports fail
- Router configs are mismatched (Vinxi legacy in oideachais)
- Mocks instead of real backends in portal (stacks, agents, monitoring, analytics all mock)
- PLACEHOLDER_* data arrays in sruth/croilar/web instead of real data sources
- BAML schema exists but oRPC procedures only partially wired
- CopilotKit AG-UI runtime mounted but no consumer
- TanStack DB available but never wired
- `docs/` contains 285 MB of reference material matching each project's tech stack 1:1

This change transforms the 5 workspaces from scaffolds into a deployable, full-stack platform with state-of-the-art patterns sourced from the existing docs and the latest upstream blog posts.

## What Changes

### Workspaces Affected

| # | Path | Stack | LOC | Target |
|:--|:--|:--|:--|:--|
| 1 | `sruth/oideachais/web/` | TanStack Start + Hono/oRPC + Convex + CopilotKit + BAML | 2,907 | Education platform front-end with AG-UI streaming, bilingual routing, MotherDuck embeds |
| 2 | `sruth/tuatha/ui/` | TanStack Start + Babylon.js + SIWE + x402 + SpacetimeDB | 5,578 | Celtic MMO front-end with wallet auth, real-time multiplayer, mythology knowledge graph |
| 3 | `sruth/croilar/apps/web/` | Vite + TanStack Router + Radix + i18n | 2,471 | Personal portfolio + CV with real GitHub/Zotero data sources |
| 4 | `sruth/croilar/apps/portal/` | TanStack Start + AI SDK + MCP-UI + TanStack DB | 6,173 | Internal developer portal with live MCP gateway, agent chat, multi-tenant themes |
| 5 | `sruth/croilar/hono-api/` | Hono + BetterAuth + Drizzle + Postgres | 449 | OIDC issuer for all 4 apps, x402 paid MCP, DuckDB wired |

### Changes by Phase

**Phase 1 — Restructure**: Root READMEs, config fixes, Convex codegen, BAML gen, route tree regen. Zero feature changes.

**Phase 2 — `sruth/croilar/hono-api`**: Real SIWE plugin, x402 paid MCP, Convex auth provider, DuckDB wired, Drizzle migrations + seed.

**Phase 3 — `sruth/oideachais/web` (AG-UI + auth + DB)**: Real AG-UI streaming CopilotKit runtime, TanStack DB reactive cache, Better Auth via `protectedProcedure`, BAML extraction pipeline.

**Phase 4 — `sruth/oideachais/web` (observability + bilingual)**: MotherDuck Dive embed, Effect-TS Convex client, bilingual route data loaders, Langfuse tracing on all oRPC procedures.

**Phase 5 — `sruth/tuatha/ui` (backend)**: Babylon.js + SpacetimeDB real-time multiplayer, SIWE auth via Better Auth, x402 paywall component, mythology + curriculum server functions wired to Graphiti.

**Phase 6 — `sruth/tuatha/ui` (front-end)**: MapLibre map, mythology A2UI cards, crypteolas demo, Vinxi dead-code purge.

**Phase 7 — `sruth/croilar/apps/web`**: Replace all PLACEHOLDER_* arrays with real createServerFn loaders. Bilingual i18n. Contact form via MCP. Marimo WASM notebook.

**Phase 8 — `sruth/croilar/apps/portal` (core)**: Real MCP gateway to LiteLLM, AG-UI agent chat, MCP-UI components, Komodo stack management.

**Phase 9 — `sruth/croilar/apps/portal` (periphery)**: Monitoring to Prometheus, Pipelines to Dagster GraphQL, Analytics to Langfuse + MotherDuck, multi-tenant theme CSS injection.

**Phase 10 — Cross-cutting**: Root mono-graph README update, Docker compose frontend stack, Cloudflare Pages config verify, E2E smoke test, typecheck pipeline, TODO audit.

### Pattern Sources

- **docs/web/** (68 files): AG-UI, TanStack DB, Better Auth, Convex, MCP-UI, billing
- **docs/sruth/tuatha/** (115 files): SpacetimeDB, Babylon.js, SIWE, x402, mythology
- **docs/teanga/** (295 files): BAML schemas, translation, OCR, language data
- **docs/agents/** (39 files): CopilotKit, AG-UI, BAML patterns, agentic scraping
- **docs/bonneagar/** (150 files): Infrastructure, Komodo, Dagster, LiteLLM
- **docs/data_engineering/** (27 files): Pipeline architecture, DuckDB, MotherDuck
- **Supplemented by Firecrawl** fetch of latest 2026-Q1 blog posts for TanStack Start 1.132, Convex v1.16+, oRPC v1.12, CopilotKit, Babylon.js 7.x, SpacetimeDB 1.x

## Impact

- **Frontend coverage**: 5 workspaces gain real backends, real data, real auth
- **Deployability**: All 5 become runnable via `bun run dev` and deployable to Cloudflare Pages + Docker
- **Observability**: Langfuse tracing on all API calls; all env keys hydrated through Infisical
- **Reversion**: All work is additive on a feature branch; no deletions of existing logic besides dead Vinxi code
- **Testing**: Each phase ends with `bun run turbo typecheck` passing; Phase 10 adds a smoke test
