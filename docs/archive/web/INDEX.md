# docs/web/ — Web Architecture Knowledge Base

Kings' College Galway web technology reference library. Contains research reports, cloned repo analysis, and layout patterns.

**Skeletonized:** 2026-06-06. All non-`.md` source code removed. Each cloned repo retains its `KCG_SUMMARY.md` (what it is, why it matters, key patterns, what was removed) plus original `README.md` files.

**Total:** 2.1 MB, 179 `.md` files across 11 subdirectories + 45 top-level research documents.

---

## Cloned Example Repos (skeletonized)

Each directory has a `KCG_SUMMARY.md` with full pattern inventory.

| Directory | Size | What |
|-----------|------|------|
| `ag-ui/` | 44K | AG-UI streaming protocol for agent↔UI communication. Python SDK (Pydantic AI, Agno), TypeScript clients |
| `tanstack/` | 188K | TanStack Start (SSR framework), TanStack AI (cross-language chat), TanStack DB (offline sync) |
| `convex/` | 108K | Real-time reactive backend. BetterAuth integration, multi-framework examples (Next.js, React, TanStack) |
| `cloudflare/` | 108K | Cloudflare Workers platform integration. BetterAuth + D1/KV/R2, TanStack Start on Workers |
| `hono/` | 16K | Lightweight edge web framework. Auth workers, DuckDB API, AI summarization patterns |
| `orpc/` | 36K | Type-safe RPC framework. Monorepo patterns, OpenAPI generation, multi-service architecture |
| `docs_examples_consolidated/` | 296K | Project's own unified examples — canonical reference implementations for the Cianfhoghlaim stack |
| `cianfhoghlaim-base/` | 52K | Base monorepo template (Better-T-Stack). Agent instructions, IDE rules, project conventions |
| `restate/` | 32K | Restate.dev coding agent demo. Durable execution, agent orchestration patterns, shadcn/ui library |
| `ui-inspiration/` | 16K | Design tokens & pattern analysis from Hades, Duolingo, Khan Academy, MotherDuck, PostHog, etc. |

---

## Pure Documentation (kept as-is)

| Directory | Size | What |
|-----------|------|------|
| `frontend/` | 40K | UI/UX architecture docs. Tech stack, key interfaces (Player Dashboard, Map, Assessment, NFT Gallery) |

---

## Top-Level Research Documents

### Architecture & Stack Decisions

- `full-stack-web-architecture-consolidated.md` (55K) — Consolidated full-stack architecture patterns
- `full-stack-dashboard-integration-plan.md` (37K) — Dashboard integration strategy
- `Educational Website Tech Stack.md` (25K) — Technology evaluation for KCG
- `implementation-plan-self-hosting-betterauth-convex-supabase-hono-tanstack-start.md` (41K) — Self-hosting implementation plan
- `Frontend Idea Catalog Development.md` (34K) — Frontend feature catalog

### TanStack

- `tanstack-start-architecture.md` (33K) — Start framework architecture deep-dive
- `tanstack-start-research-report.md` (38K) — Comprehensive research report
- `tanstack-start-visual-patterns.md` (32K) — Visual/component patterns
- `TANSTACK_ANALYSIS.md` (18K), `TANSTACK_INDEX.md` (9K), `TANSTACK_SUMMARY.md` (8K), `TANSTACK_QUICK_REFERENCE.md` (8K), `README_TANSTACK_ANALYSIS.md` (9K)
- `TanStack DB Integration and Comparison.md` (35K)
- `TanStack Start.md`, `Overview _ TanStack AI Docs.md`, `Overview _ TanStack DB Docs.md`
- `Integrating TanStack AI with LiteLLM.md` (29K)

### AG-UI / Agent Protocols

- `AG-UI Overview.md`, `AG-UI - Pydantic AI.md`, `AG-UI and A2UI_ Understanding the Differences.md`, `AG-UI Goes Mobile.md`
- `mcp-ui-integration.md` (9K) — MCP-UI for interactive agent interfaces
- `agentic-platform.md` (33K) — Agentic platform design
- `BAML, Graphiti, Tanstack AI Pipeline.md` (30K) — Agent pipeline design

### BetterAuth / Authentication

- `auth-setup.md` (9K), `Basic Usage _ Better Auth.md` (9K)
- `Sign In With Ethereum (SIWE) _ Better Auth.md` (9K)
- `PostgreSQL _ Better Auth.md`, `Drizzle ORM Adapter _ Better Auth.md`
- `Expo Integration _ Better Auth.md`, `TanStack Start Integration _ Better Auth.md`
- `convex-authentication-and-integration-guide.md` (84K)

### Convex

- `convex-core-features-architecture.md` (34K)
- `convex-backend_self-hosted_README.md`
- `Playground _ Convex Developer Hub.md`
- `RAG (Retrieval-Augmented Generation) with the Agent component _ Convex Developer Hub.md`

### Effect-TS

- `effect-ts-comprehensive-research.md` (61K)
- `effect-ts-tanstack-start-integration.md` (36K)
- `effect-convex-integration-research.md` (32K)

### Cloudflare / Alchemy

- `alchemy-run_alchemy_ Infrastructure as TypeScript.md` (10K)
- `alchemy_examples_cloudflare-worker.md`, `alchemy_examples_cloudflare-sveltekit.md`, `alchemy_examples_cloudflare-tanstack-start.md`

### UI/UX Design

- `React Drag-and-Drop for Exam Builder.md` (36K)
- `Asset Management for Full-Stack App.md` (37K)
- `Microfrontends.md` (13K)
- `routing-and-layout.md` (37K)

### Other

- `oRPC-comprehensive-research.md` (35K)
- `PDF.js - Examples.md`
- `ChromeDevTools_chrome-devtools-mcp.md` (28K)
- `Release v28.0.0 - Mesh Shaders, Immediates, and More! · gfx-rs_wgpu.md`

---

## Space Saved

| What | Before | After | Saved |
|------|--------|-------|-------|
| 9 cloned repos + ui-inspiration | ~82 MB | 876K | ~81 MB |
| Source code removed | ~5,000 files | 0 non-.md files | All |
| docs/web/ total | ~85 MB | 2.1 MB | ~83 MB |
