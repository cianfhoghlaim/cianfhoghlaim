---
name: agentic-frontend-frameworks
description: The umbrella skill for building **agentic web frontends** in the Cianfhoghlaim stack — stitches TanStack Start + CopilotKit + AG-UI + Convex + Hono + oRPC + Cloudflare + BAML / Pydantic AI / Agno / Google ADK into a coherent agent-driven web app. Use when designing a new agentic web surface (a tutor, a research UI, a knowledge-graph explorer, a portfolio analyser), wiring the AG-UI protocol between an agent runtime and a CopilotKit React UI, picking the right backend (BAML for typed structured outputs, Pydantic AI for Pydantic-native agent graphs, Agno for multi-agent orchestration, Google ADK for Google-AI-native workflows), or asking "how do I add an agent to a sruth/ app?", "which CopilotKit component streams AG-UI events?", "what is the canonical 4-surface layout?". The 4 canonical surfaces are `oideachais/web/`, `croilar/apps/web/`, `croilar/apps/portal/`, and `tuatha/ui/` — the same architecture diagram maps onto each.
---

# Agentic Frontend Frameworks (umbrella skill)

## When to use this skill

Use when you need to:

- "Design a new agentic web surface (tutor, research UI,
  knowledge graph explorer, portfolio analyser)"
- "Wire AG-UI between an agent runtime and a CopilotKit
  React UI"
- "Pick the right backend (BAML / Pydantic AI / Agno /
  Google ADK) for a new agent"
- "Map a sruth/ app onto the canonical 4-surface layout"
- "Add a CopilotKit component (chat panel, generative UI,
  human-in-the-loop) to a TanStack Start app"
- "Add a new agent to the 4-agent Celtic Tutor system"
- "Add MCP / A2UI / MCP-UI to an existing web surface"
- "Understand the relationship between `oideachais/web/`,
  `croilar/apps/web/`, `croilar/apps/portal/`, `tuatha/ui/`"
- "Explain the KCG agentic-web pattern to a new contributor"

## Overview

The **agentic-frontend-frameworks** skill is the umbrella
skill for building **agentic web frontends** in the
Cianfhoghlaim stack. The round-6 capability spec
(`openspec/specs/agentic-frontend-frameworks/spec.md`)
listed the capability, but the skill body was missing —
this skill fills that gap.

The canonical pattern is: **TanStack Start** (isomorphic
React 19 + server functions) hosts a **CopilotKit** React
app (the agentic UI primitives) that consumes the **AG-UI**
protocol (CopilotKit's open agent↔UI streaming protocol)
served by an **agent runtime** (BAML / Pydantic AI / Agno /
Google ADK) that calls **Convex** (the real-time backend)
and **Hono + oRPC + Cloudflare** (the edge gateway). The
same diagram is reused across 4 canonical surfaces in the
monorepo:

| # | Surface | Path | Quadrant | Primary agent |
|:--|:--|:--|:--|:--|
| 1 | **Oideachais Web** | `oideachais/web/` | `oideachais` | Celtic Tutor (BAML) |
| 2 | **Croílár Web** | `croilar/apps/web/` | `croilar` | Portfolio Research Assistant (Pydantic AI) |
| 3 | **Croílár Portal** | `croilar/apps/portal/` | `croilar` | Admin / Curatorial Agent (Agno) |
| 4 | **Tuatha UI** | `tuatha/ui/` | `tuatha` | Quest Guide / Mythology Narrator (Google ADK) |

The 4 surfaces share the same architecture diagram; the
delta is the agent runtime, the dataset the agent reads
from, and the deploy target.

## The canonical integration diagram

```
┌─────────────────────────────────────────────────────────────────────┐
│                    AGENTIC WEB FRONTEND STACK                       │
└─────────────────────────────────────────────────────────────────────┘

Browser (React 19 + CopilotKit + TanStack Router/Query)
   │  ▲  AG-UI (HTTP + SSE over HTTP/2)
   │  │  ── threadId, runId, messages[], state, events
   │  │
   ▼  │
TanStack Start (TS) ─── Cloudflare Workers
   │                ─── Alchemy IaC (D1, R2, KV, Hyperdrive)
   │                ─── TanStack AI (chat() / tool() / embed())
   │
   ▼
AG-UI Server (CopilotKit runtime / Pydantic AI AGUIAdapter / Agno A2UI)
   │                ─── Hono RPC handlers
   │                ─── oRPC contract (typed RPC, OpenAPI)
   │
   ▼
Agent Runtime ─── BAML (typed structured outputs)
   │          ─── Pydantic AI (typed agent graphs)
   │          ─── Agno (multi-agent orchestration + AgentOS)
   │          ─── Google ADK (NodeRunner, native inter-agent routing)
   │
   ▼
Convex ─── queries / mutations / actions / vector.search
   │    ─── scheduled (cron, durable)
   │    ─── HTTP actions (webhooks)
   │    ─── Convex Agent component (RAG, thread persistence)
   │
   ▼
Dagster ─── Celtic curriculum assets
       ─── Mythology embeddings
       ─── Knowledge graph (FalkorDB / Memgraph)
       ─── Vector store (LanceDB HNSW)
       ─── Observability (Langfuse / MLflow)
```

The same diagram, with the 4 layers (Browser / TanStack
Start / Agent Runtime / Convex + Dagster) is reused across
all 4 canonical surfaces.

## The 7 layers of the stack

| Layer | Choice | Why |
|:--|:--|:--|
| **1. Frontend framework** | TanStack Start (React 19 + Vite) | Isomorphic (SSR + RSC + server functions); the same TanStack Router / Query / AI primitives the rest of the monorepo uses |
| **2. Agentic UI primitives** | CopilotKit React components | Chat panels, generative UI, human-in-the-loop, state diffs; the canonical React-side agentic UI |
| **3. Agent↔UI protocol** | AG-UI (CopilotKit) | Open, typed, event-streamed protocol; transport-agnostic (HTTP, SSE, WebSocket); tool-call and state-diff events |
| **4. Edge gateway** | Hono | Lightweight, runs on Cloudflare Workers, Bun, Node, Deno; the KCG OIDC bridge and DuckDB API wrapper |
| **5. Type-safe RPC** | oRPC | Contract-first RPC; auto-OpenAPI generation; TanStack Query client on the web side; Python `httpx` on the backend side |
| **6. Real-time backend** | Convex | Reactive queries, durable mutations, scheduled functions, vector search, the Convex Agent component for RAG |
| **7. Agent runtime** | BAML / Pydantic AI / Agno / Google ADK | One of 4 (see **"Picking the agent runtime"** below) |

## Picking the agent runtime

The KCG agentic-web pattern is **runtime-agnostic** at the
AG-UI / Convex / TanStack layers. Pick the runtime based on
the agent's shape:

| Runtime | When to use it | KCG exemplar |
|:--|:--|:--|
| **BAML** | Typed structured outputs (the agent emits strongly-typed objects: a `TutorStep`, a `CelticConcept`, a `RAGResponse`). Use when the LLM call is "extract → type" shaped. | Oideachais Celtic Tutor (BAML generates the typed response from a Celtic-language model) |
| **Pydantic AI** | Pydantic-native agent graphs. Use when the agent is a stateful Pydantic graph (typed inputs, typed outputs, tool-calling, structured streaming). | Croílár Portfolio Research Assistant (Pydantic AI + Pydantic models + FastAPI) |
| **Agno** | Multi-agent orchestration with AgentOS. Use when the agent is one of many specialised agents (Root, Curriculum, Translation, Corpus) that need a shared knowledge base and stateless execution. | Oideachais 12 specialised agents (Root / Curriculum / Translation / Corpus / …) |
| **Google ADK** | Google-AI-native workflows. Use when the agent uses Gemini / Vertex AI and you want Google's native inter-agent routing, NodeRunner, and the multi-agent workflow engine. | Tuatha Quest Guide (Google ADK + Gemini 2.5 + AG-UI) |

The choice is **not exclusive** — a single surface can mix
runtimes (e.g. Tuatha uses Google ADK for the Quest Guide
and BAML for the Celtic Tutor). The AG-UI protocol is the
common denominator.

## The AG-UI protocol (event-stream)

AG-UI is the open protocol CopilotKit uses to stream agent
state to a React UI. The server emits typed events over
SSE; the client (CopilotKit) consumes them and updates the
React tree. The event types are:

| Event | Direction | Purpose |
|:--|:--|:--|
| `RUN_STARTED` | server → client | A new agent run (threadId, runId) |
| `TEXT_MESSAGE_CHUNK` | server → client | A streaming text token (the agent's prose) |
| `TOOL_CALL_START` / `TOOL_CALL_ARGS` / `TOOL_CALL_END` | server → client | The agent is calling a tool (with typed args) |
| `TOOL_RESULT` | client → server | The tool's result is streamed back |
| `STATE_SNAPSHOT` / `STATE_DELTA` | server → client | JSON-Patch-style state diffs (typed state shape) |
| `MESSAGES_SNAPSHOT` | server → client | The full message history (re-sync) |
| `RUN_FINISHED` / `RUN_ERROR` | server → client | Run completed (or failed) |

The KCG pattern uses **typed state** (Zod / Pydantic) for
the `STATE_*` events — the agent emits a typed
`TutorState` (lesson progress, mastery score, last
concept), the client applies the delta, and CopilotKit
re-renders the right component.

## The 4 canonical surfaces

### 1. Oideachais Web (`oideachais/web/`)

- **Stack:** TanStack Start + CopilotKit + AG-UI +
  Cloudflare Workers
- **Agent runtime:** BAML (the Celtic Tutor uses BAML
  for typed `TutorStep` outputs)
- **Backend:** Convex (the Convex Agent component holds
  the RAG index of the NCCA / SEC / pan-Celtic curriculum)
- **Primary agent:** Celtic Tutor (Gaeilge)
- **Deployment:** Cloudflare Workers via Alchemy

### 2. Croílár Web (`croilar/apps/web/`)

- **Stack:** TanStack Start + CopilotKit + AG-UI +
  Cloudflare Workers
- **Agent runtime:** Pydantic AI (the Portfolio Research
  Assistant is a Pydantic graph with typed state)
- **Backend:** Convex (the portfolio dataset) + BetterAuth
  (OIDC)
- **Primary agent:** Portfolio Research Assistant
  (analyses the author's personas: aleyum, cianfhoghlaim,
  carlcashman)
- **Deployment:** Cloudflare Workers via Alchemy

### 3. Croílár Portal (`croilar/apps/portal/`)

- **Stack:** TanStack Start + CopilotKit + AG-UI +
  Hono (the OIDC bridge) + Convex
- **Agent runtime:** Agno (multi-agent orchestration; the
  portal runs a fleet of admin / curatorial agents)
- **Backend:** Convex (the admin / curatorial dataset) +
  FalkorDB (the knowledge graph)
- **Primary agent:** Curatorial Agent (manages the
  pan-Celtic knowledge graph)
- **Deployment:** Cloudflare Workers via Alchemy

### 4. Tuatha UI (`tuatha/ui/`)

- **Stack:** TanStack Start + CopilotKit + AG-UI +
  SpacetimeDB (the MMO state engine) + Convex (the
  agent state) + x402 (paywalls)
- **Agent runtime:** Google ADK (the Quest Guide +
  Mythology Narrator use Google's native inter-agent
  routing) + BAML (the Celtic Tutor)
- **Backend:** SpacetimeDB (the MMO state) + Convex (the
  agent state) + BetterAuth (SIWE)
- **Primary agents:** Quest Guide, Mythology Narrator,
  Celtic Tutor, Research Assistant
- **Deployment:** Cloudflare Workers (TanStack Start SSR)
  + SpacetimeDB (the game state)

## The 3 backend options (under the AG-UI server)

| Backend | When to use it | KCG exemplar |
|:--|:--|:--|
| **BAML** | Typed structured outputs (the LLM emits a typed object) | Oideachais Celtic Tutor (BAML `TutorStep` / `CelticConcept` / `RAGResponse`) |
| **Pydantic AI** | Stateful Pydantic agent graphs | Croílár Portfolio Research Assistant |
| **Agno / Google ADK** | Multi-agent orchestration, knowledge base, AgentOS | Oideachais 12 specialised agents (Agno); Tuatha Quest Guide (Google ADK) |

## Cross-cutting concerns

| Concern | Skill |
|:--|:--|
| TanStack Start / Router / Query / AI | `.agents/skills/tanstack-start/SKILL.md` |
| CopilotKit components (chat, generative UI, HITL) | `.agents/skills/copilotkit/SKILL.md` |
| AG-UI protocol (event types, KMP client) | `.agents/skills/ag-ui/SKILL.md` |
| Convex (queries, mutations, actions, vectors, auth) | `.agents/skills/convex/SKILL.md` |
| Hono edge gateway (OIDC bridge, DuckDB API) | `.agents/skills/hono/SKILL.md` |
| oRPC type-safe RPC (contract, OpenAPI) | `.agents/skills/orpc/SKILL.md` |
| Cloudflare Workers + D1 + R2 + KV + Hyperdrive | `.agents/skills/cloudflare/SKILL.md` |
| BAML typed structured outputs | `.agents/skills/baml/SKILL.md` |
| Pydantic AI agent graphs | `.agents/skills/pydantic-ai/SKILL.md` |
| Agno multi-agent orchestration | `.agents/skills/agno/SKILL.md` |
| Google ADK multi-agent workflow engine | `.agents/skills/google-adk/SKILL.md` |
| BetterAuth (the OIDC / SIWE auth layer) | `.agents/skills/better-auth/SKILL.md` |
| Celtic Tutor + Celtic-language models | `.agents/skills/celtic-language-ai/SKILL.md` |
| Knowledge graph (FalkorDB / Memgraph / Cognee) | `.agents/skills/cognee/SKILL.md` |
| Vector search (LanceDB HNSW) | `.agents/skills/lancedb/SKILL.md` |
| Observability (Langfuse / MLflow / RAGAS) | `.agents/skills/agent-observability/SKILL.md` |
| MMO state engine (SpacetimeDB) | `.agents/skills/upstream-mirrors/SKILL.md` (SpacetimeDB mirror) |
| The 7 web-stack upstream mirrors | `.agents/skills/web-mirrors/SKILL.md` |
| The 11 game/infra-stack upstream mirrors | `.agents/skills/upstream-mirrors/SKILL.md` |

## References (in this skill)

- `references/agentic-academy.md` — the Agentic Academy
  architecture (CopilotKit + AG-UI + MCP for a British
  Isles Celtic education hub).
- `references/full-stack-dashboard.md` — the canonical
  TanStack + Convex + CodeRabbit + Agno + Cognee
  interactive dashboard.
- `references/full-stack-architecture.md` — the
  ~2200-line canonical full-stack web architecture guide
  (the synthesis reference for the entire stack).

## Cross-references

- `.agents/skills/web-mirrors/SKILL.md` — the 7 web-stack
  upstream mirrors (the consumer of this skill's stack).
- `.agents/skills/upstream-mirrors/SKILL.md` — the 11
  game/infra-stack mirrors (the Tuatha MMO side).
- `.agents/skills/tanstack-start/SKILL.md` — the primary
  frontend framework.
- `.agents/skills/copilotkit/SKILL.md` — the React-side
  agentic UI primitives.
- `.agents/skills/ag-ui/SKILL.md` — the agent↔UI
  protocol.
- `.agents/skills/convex/SKILL.md` — the real-time
  backend.
- `.agents/skills/hono/SKILL.md` — the edge gateway.
- `.agents/skills/orpc/SKILL.md` — the type-safe RPC.
- `.agents/skills/cloudflare/SKILL.md` — the deploy
  target.
- `.agents/skills/baml/SKILL.md`,
  `.agents/skills/pydantic-ai/SKILL.md`,
  `.agents/skills/agno/SKILL.md`,
  `.agents/skills/google-adk/SKILL.md` — the 4 agent
  runtime options.
- `.agents/skills/tuatha-mmo/SKILL.md` — Tuatha UI is one
  of the 4 canonical surfaces.
- `.agents/skills/better-auth/SKILL.md` — the OIDC / SIWE
  auth layer.
- `.agents/skills/celtic-language-ai/SKILL.md` — the
  Celtic-language models used by the Celtic Tutor.
- `.agents/skills/agent-observability/SKILL.md` — the
  Langfuse / MLflow / RAGAS observability stack.
- `openspec/specs/agentic-frontend-frameworks/spec.md` —
  the round-6 capability spec (this skill is the body).
- `oideachais/web/`, `croilar/apps/web/`,
  `croilar/apps/portal/`, `tuatha/ui/` — the 4 canonical
  surfaces.
