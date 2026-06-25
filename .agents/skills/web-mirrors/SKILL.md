---
name: web-mirrors
description: The 7 KCG-authored mirror summaries of upstream repositories that the Cianfhoghlaim **web frontends** depend on — TanStack (the primary frontend framework), Convex (real-time backend), Hono (edge web framework), oRPC (type-safe RPC), AG-UI (CopilotKit's agent↔UI protocol), Cloudflare Workers (D1/R2/KV/Hyperdrive deploy), and Restate (durable execution + agent coding patterns). Sister skill to `upstream-mirrors` which covers the 11 game/infra-stack mirrors (SpacetimeDB / wgpu / x402 / etc.). Use when asking "how does KCG use Convex?", "what is the Hono API gateway pattern?", "which TanStack packages do sruth/ apps pin?", "what is AG-UI in KCG terms?", "how does KCG deploy to Cloudflare Workers?", or "what is the Restate coding-agent pattern?" — this skill is the registry + the KCG annotations on top of each upstream.
---

# Web Mirrors (KCG registry)

## When to use this skill

Use when you need to:

- "What does the TanStack mirror pin (Start / AI / DB / Router)?"
- "How do sruth/ apps use Convex?"
- "What is the Hono API gateway pattern in KCG?"
- "How does oRPC fit into the monorepo?"
- "What is the AG-UI protocol in KCG terms?"
- "Which Cloudflare Workers products does KCG use (D1 / R2 / KV / Hyperdrive)?"
- "What is the Restate coding-agent pattern?"
- "Where is the canonical AG-UI reference for the CopilotKit integration?"
- "What is the difference between the web-mirrors and upstream-mirrors skills?"
- "Update a KCG web mirror from its upstream"

## Overview

The **web-mirrors** skill is the KCG registry of the **7
upstream web-stack repositories** the Cianfhoghlaim web
frontends depend on. The KCG-authored summaries (one per
mirror) live under `references/<mirror>.md` in this skill.
This skill is the **web-stack sibling** of
`.agents/skills/upstream-mirrors/SKILL.md` which covers
the **game/infra-stack** mirrors (SpacetimeDB, wgpu, x402,
AnyLanguageModel, agui_kotlin, etc.).

The split exists because the two stacks answer different
questions:

- `upstream-mirrors` (11 mirrors) — the **game / 3D /
  blockchain / ML** layer: the Tuatha MMO's state engine
  (SpacetimeDB), the WebGPU renderer (wgpu), the HTTP
  micropayment rail (x402), the Apple unified LLM API
  (AnyLanguageModel), and the cross-platform client bridges
  (agui_kotlin, react-native-godot, react-native-reusables).
- `web-mirrors` (7 mirrors) — the **web application**
  layer: the primary frontend framework (TanStack), the
  real-time backend (Convex), the edge gateway (Hono), the
  type-safe RPC layer (oRPC), the agent↔UI streaming
  protocol (AG-UI), the deploy target (Cloudflare Workers),
  and the durable-execution agent pattern (Restate).

Both skills follow the same **mirror policy** (see
`upstream-mirrors/SKILL.md`): KCG-authored summaries live
under `references/<mirror>.md`; source trees (when
preserved) live under the source docs dir; external
clippings (release notes, blog posts) live under
`references/clippings/`. The summary is the **canonical
entry point** — agents read the summary first, then the
source tree / docs only when the summary is insufficient.

## The 7 web-mirror summaries

| # | Mirror | KCG summary | Primary use case |
|:--|:--|:--|:--|
| 1 | `tanstack` | `references/tanstack.md` | TanStack Start / AI / DB / Router — the primary frontend framework for all `sruth/` web apps |
| 2 | `convex` | `references/convex.md` | Convex real-time backend (queries / mutations / actions / vector / scheduled / HTTP actions) — the `sruth/` backend default |
| 3 | `hono` | `references/hono.md` | Hono edge web framework — the API gateway pattern for auth workers, DuckDB API endpoints, and Convex-adjacent microservices |
| 4 | `orpc` | `references/orpc.md` | oRPC type-safe RPC — the contract-first API layer across the monorepo (auto-OpenAPI generation, TanStack Query client) |
| 5 | `ag-ui-protocol` | `references/ag-ui-protocol.md` | AG-UI protocol (CopilotKit) — the agent↔UI streaming protocol used by all `sruth/` frontends for agentic UIs |
| 6 | `cloudflare-workers` | `references/cloudflare-workers.md` | Cloudflare Workers + D1 / R2 / KV / Hyperdrive — the primary deploy target for `oideachais/web/` and several `sruth/` apps |
| 7 | `restate-coding-agent` | `references/restate-coding-agent.md` | Restate durable execution + agent coding patterns (orchestrator-agent loop, parallel fan-out, racing, evaluator-optimizer) — the long-running agent pattern |

The 8th `repo-*.md` in `docs/web/08-repos/`
(`repo-restate-ui-readme.md`, 5 lines, "this is a demo UI
generated with v0") was trivial and is DELETEd.

## The KCG use of each mirror (1-liner)

- **TanStack** — the primary frontend framework. Every
  `sruth/` web app is a TanStack Start + TanStack Router
  + TanStack Query (and, where agentic, TanStack AI)
  application. TanStack DB is the local-first sync layer
  for the Celtic Knowledge Grid.
- **Convex** — the real-time backend for `sruth/` apps.
  Convex handles auth (BetterAuth integration), vector
  search (for RAG), scheduled functions, HTTP actions (for
  webhooks), and the Convex Agent component (used by the
  agentic web frontends).
- **Hono** — the edge web framework used to build API
  gateway workers (the OIDC bridge between BetterAuth and
  PocketID, the DuckDB API endpoint for analytics, and the
  Cloudflare Worker wrappers around Convex). The Hono +
  Cloudflare + Alchemy pattern is the KCG edge stack.
- **oRPC** — the type-safe RPC layer. The oRPC contract
  lives in the monorepo root; TanStack Query clients
  consume it on the web side, Python `httpx` clients
  consume the auto-generated OpenAPI on the backend side.
- **AG-UI** — the agent↔UI streaming protocol (CopilotKit).
  The AG-UI server runs in the TanStack Start backend;
  CopilotKit + AG-UI components render in the browser; the
  agent (BAML / Pydantic AI / Agno / Google ADK) streams
  tool calls and UI events through the protocol.
- **Cloudflare Workers** — the primary deploy target.
  Workers handle the Oideachais `web/` app, several `sruth/`
  apps, and the Hono-based API gateway workers. The
  companion tool Alchemy (see the `cloudflare` skill) is
  the IaC layer for Workers + D1 + R2 + Hyperdrive.
- **Restate** — the durable-execution + coding-agent
  pattern. The Restate coding-agent article describes
  orchestrator-agent loops, parallel agent fan-out, racing
  agents, and evaluator-optimizer patterns. These patterns
  inform the long-running agent design in the Tuatha MMO
  and the Oideachais tutor agents.

## Why two mirror skills?

The Cianfhoghlaim monorepo has 4 quadrants
(`oideachais/`, `sruth/meaisinfhoghlaim/`, `tuatha/`, `croilar/`)
plus a shared web stack that runs across all of them. The
shared web stack pulls on a different set of upstream
projects than the game / infra stack, so the KCG mirror
policy splits the registry into two complementary skills:

| | `upstream-mirrors` | `web-mirrors` |
|:--|:--|:--|
| Quadrant | `tuatha/` (game / 3D / crypto) | `oideachais/web/`, `croilar/`, shared web stack |
| Tech layer | State engine, GPU, blockchain, ML, cross-platform client | Frontend framework, real-time backend, edge gateway, RPC, agent protocol, deploy target |
| Mirror count | 11 | 7 |
| Sample repos | SpacetimeDB, wgpu, x402, AnyLanguageModel, agui_kotlin | TanStack, Convex, Hono, oRPC, AG-UI, Cloudflare Workers, Restate |
| Sister skill | `web-mirrors` (this) | `upstream-mirrors` |

If a repo could plausibly land in either (e.g. agui_kotlin
is an agent↔UI client, but it's used in the KMP Tuatha
mobile client, not the web), it stays in
`upstream-mirrors` (the original host quadrant wins). The
`AG-UI` mirror in `web-mirrors` covers the web protocol;
the `agui_kotlin` mirror in `upstream-mirrors` covers the
Kotlin client.

## References (in this skill)

- `references/tanstack.md` — TanStack family KCG summary
  (Start / Router / Query / AI / DB).
- `references/convex.md` — Convex KCG summary (queries,
  mutations, actions, vectors, auth).
- `references/hono.md` — Hono KCG summary (the API gateway
  pattern for OIDC, DuckDB, and Convex-adjacent services).
- `references/orpc.md` — oRPC KCG summary (contract-first
  RPC, OpenAPI auto-gen, TanStack Query integration).
- `references/ag-ui-protocol.md` — AG-UI protocol KCG
  summary (CopilotKit's agent↔UI streaming).
- `references/cloudflare-workers.md` — Cloudflare Workers
  KCG summary (D1 / R2 / KV / Hyperdrive).
- `references/restate-coding-agent.md` — Restate
  coding-agent patterns (orchestrator-agent, parallel,
  racing, evaluator-optimizer).

## Cross-references

- `.agents/skills/upstream-mirrors/SKILL.md` — the sister
  skill (11 game/infra-stack mirrors). The split is
  explained in the **"Why two mirror skills?"** section
  above.
- `.agents/skills/tanstack-start/SKILL.md` — the deeper
  dive into the TanStack patterns used in the
  `web-mirrors/tanstack` summary.
- `.agents/skills/convex/SKILL.md` — the deeper dive into
  Convex queries / mutations / actions / vectors / auth.
- `.agents/skills/hono/SKILL.md` — the deeper dive into
  the Hono edge gateway pattern.
- `.agents/skills/orpc/SKILL.md` — the deeper dive into
  the oRPC type-safe RPC contract.
- `.agents/skills/ag-ui/SKILL.md` — the deeper dive into
  the AG-UI protocol + the KMP Kotlin client.
- `.agents/skills/cloudflare/SKILL.md` — the deeper dive
  into Cloudflare Workers + D1 + R2 + KV + Hyperdrive +
  Alchemy.
- `.agents/skills/agentic-frontend-frameworks/SKILL.md` —
  the umbrella skill that stitches the 7 mirrors together
  into a coherent agentic web frontend.
- `.agents/skills/copilotkit/SKILL.md` — the CopilotKit
  React components that consume the AG-UI protocol.
- `.agents/skills/better-auth/SKILL.md` — the auth layer
  that sits on top of Convex (and is the most common
  consumer of the Hono OIDC bridge).
- `.agents/skills/monorepo/SKILL.md` — the monorepo
  structure that hosts the oRPC contract.
- `docs/web/08-repos/` — the source `repo-*.md` files
  (round 9: the KCG-authored summaries move into this
  skill's `references/`).
