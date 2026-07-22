---
name: agentic-frontend-frameworks
description: The umbrella skill for building **agentic web frontends** in the Cianfhoghlaim stack — stitches TanStack Start + CopilotKit + AG-UI + Convex + Hono + oRPC + Cloudflare + BAML / Pydantic AI / Agno / Google ADK into a coherent agent-driven web app. Use when designing a new agentic web surface (a tutor, a research UI, a knowledge-graph explorer, a portfolio analyser), wiring the AG-UI protocol between an agent runtime and a CopilotKit React UI, picking the right backend (BAML for typed structured outputs, Pydantic AI for Pydantic-native agent graphs, Agno for multi-agent orchestration, Google ADK for Google-AI-native workflows), or asking "how do I add an agent to a cianfhoghlaim/ app?", "which CopilotKit component streams AG-UI events?", "what is the canonical 4-surface layout?". The 4 canonical surfaces are `web/apps/cianfhoghlaim-web/`, `web/apps/croilar-web/`, `web/apps/croilar-portal/`, and `web/apps/tuatha-ui/` — the same architecture diagram maps onto each. Plus a 5th cross-cutting **agent-IDE** surface: OpenChamber (`infrastructure/stacks/openchamber/`, OpenCode web/desktop UI with bundled `opencode-ai`, port 3000, deployed to `openchamber.cianfhoghlaim.ie` on `arm1-oci`).
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
- "Map a cianfhoghlaim/ app onto the canonical 4-surface layout"
- "Add a CopilotKit component (chat panel, generative UI,
  human-in-the-loop) to a TanStack Start app"
- "Add a new agent to the 4-agent Celtic Tutor system"
- "Add MCP / A2UI / MCP-UI to an existing web surface"
- "Understand the relationship between `web/apps/cianfhoghlaim-web/`,
  `web/apps/croilar-web/`, `web/apps/croilar-portal/`, `web/apps/tuatha-ui/`"
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
| 1 | **Oideachais Web** | `web/apps/cianfhoghlaim-web/` | `oideachais` | Celtic Tutor (BAML) |
| 2 | **Croílár Web** | `web/apps/croilar-web/` | `croilar` | Portfolio Research Assistant (Pydantic AI) |
| 3 | **Croílár Portal** | `web/apps/croilar-portal/` | `croilar` | Admin / Curatorial Agent (Agno) |
| 4 | **Tuatha UI** | `web/apps/tuatha-ui/` | `tuatha` | Quest Guide / Mythology Narrator (Google ADK) |

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

### 1. Oideachais Web (`web/apps/cianfhoghlaim-web/`)

- **Stack:** TanStack Start + CopilotKit + AG-UI +
  Cloudflare Workers
- **Agent runtime:** BAML (the Celtic Tutor uses BAML
  for typed `TutorStep` outputs)
- **Backend:** Convex (the Convex Agent component holds
  the RAG index of the NCCA / SEC / pan-Celtic curriculum)
- **Primary agent:** Celtic Tutor (Gaeilge)
- **Deployment:** Cloudflare Workers via Alchemy

### 2. Croílár Web (`web/apps/croilar-web/`)

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

### 3. Croílár Portal (`web/apps/croilar-portal/`)

- **Stack:** TanStack Start + CopilotKit + AG-UI +
  Hono (the OIDC bridge) + Convex
- **Agent runtime:** Agno (multi-agent orchestration; the
  portal runs a fleet of admin / curatorial agents)
- **Backend:** Convex (the admin / curatorial dataset) +
  FalkorDB (the knowledge graph)
- **Primary agent:** Curatorial Agent (manages the
  pan-Celtic knowledge graph)
- **Deployment:** Cloudflare Workers via Alchemy

### 4. Tuatha UI (`web/apps/tuatha-ui/`)

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

### 5. OpenChamber (`infrastructure/stacks/openchamber/`)

OpenChamber is the cross-cutting **agent-IDE surface** —
a web/desktop UI that gives humans direct hands-on access to
the `opencode-ai` runtime (the canonical KCG agent harness).
It is NOT a replacement for the 4 TanStack + CopilotKit +
AG-UI surfaces above; it sits orthogonal to them as the
**developer-facing workbench** for the 12-agent fleet.

- **Stack:** Bun + React (built by the `openchamber`
  upstream; 18+ themes; bundled `opencode-ai` runtime)
- **Agent runtime:** `opencode-ai` bundled inside the
  container (no `OPENCODE_HOST` override in v1)
- **Backend:** `infrastructure/stacks/openclaw/` (the
  channel-fanout gateway for messaging channels) +
  `infrastructure/stacks/langfuse/` (the LLM
  observability dashboard)
- **Primary use cases:** hands-on agent debugging,
  prompt engineering, single-pane-of-glass for the
  12-agent meaisínfhoghlaim fleet, MCP server
  configuration, skills curation
- **Provider parity:** OpenAI + Anthropic + minimax
  (graceful degradation if any are missing)
- **Deployment:** Docker Compose on `arm1-oci`,
  routed via Pangolin to `openchamber.cianfhoghlaim.ie`
  (port 3000); 6-file GOLD_STANDARD pattern
- **Auth:** Pangolin `tinyauth` + `secure-headers`
  middlewares (Pocket ID OIDC) + the
  `OPENCHAMBER_UI_PASSWORD` Locket-injected env var

The full contract is in
`openspec/changes/add-openchamber-stack-and-opencode-ui/specs/agentic-frontend-frameworks/spec.md`.

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
- `web/apps/cianfhoghlaim-web/`, `web/apps/croilar-web/`,
  `web/apps/croilar-portal/`, `web/apps/tuatha-ui/` — the 4 canonical
  surfaces.
- `infrastructure/stacks/openchamber/` — the 5th
  cross-cutting agent-IDE surface (OpenCode web/desktop UI
  with bundled `opencode-ai`, deployed on `arm1-oci`).
- `infrastructure/stacks/openclaw/` — the inbound
  channel-fanout gateway (the messaging-channel sibling
  to OpenChamber; both share the `arm1-oci` control-plane
  host tier and the Langfuse observability backplane).
- `.agents/skills/infrastructure-stacks/SKILL.md` — the
  6-file GOLD_STANDARD pattern that OpenChamber + OpenClaw
  follow.
- `.agents/skills/agent-fleet-orchestration/SKILL.md` —
  the canonical skill for the 12-agent meaisínfhoghlaim
  fleet that OpenChamber exposes as a workbench.
- `infrastructure/komodo/procedures/deploy-openchamber-arm1-oci.toml`
  — the 5-stage arm1-oci deploy procedure.

## MCP protocol

The **Model Context Protocol (MCP)** is the open-source
standard (Anthropic, 2024-11-18) that connects AI
applications to external systems — "USB-C for AI". Built on
**JSON-RPC 2.0**, transport-agnostic (stdio, HTTP, SSE,
WebSocket, in-memory), and supported by Anthropic, OpenAI,
DeepMind, and Microsoft.

**3-component architecture**:

```
┌─────────────┐   ┌─────────────┐   ┌─────────────┐
│   MCP Host  │ ◄►│ MCP Client  │ ◄►│ MCP Server  │
│  (Claude)   │   │             │   │  (Tools)    │
└─────────────┘   └─────────────┘   └─────────────┘
```

**4 core primitives**: **Resources** (read-only data,
URI-referenced like `@github:issue://123`), **Tools**
(executable functions via `tools/call`), **Prompts**
(discoverable instruction templates, executable as slash
commands), **Sampling** (servers can request LLM completions
— enables agentic + nested LLM calls).

**6 protocol layers**: Base Protocol (JSON-RPC 2.0),
Lifecycle Management, Authorization (OAuth 2.1 + PKCE for
HTTP transports), Server Features, Client Features,
Utilities. Connection lifecycle: Transport Connection →
Capability Negotiation → Feature Discovery → Active Session
→ Shutdown.

**Transport recommendation**: **HTTP for production**
(remote cloud services); stdio for local processes
(desktop apps, CLI tools); SSE is deprecated; WebSocket
for bidirectional real-time; in-memory for testing.

**MCP + AG-UI relationship**: MCP is the **agent↔tool**
protocol; AG-UI is the **agent↔UI** protocol. They
complement — an agent reads tools via MCP and streams
state to the UI via AG-UI events.

The comprehensive 1,111-line research (compiled 2025-11-18
against the 2025-06-18 spec) covers 10 parts: fundamentals,
integration patterns, server implementations, MCP-UI,
security, SIWE, ecosystem, Firecrawl, common patterns,
real-world use cases, OWASP alignment, performance, SDKs
(Python + TypeScript + FastMCP), future outlook, resources.

See `references/mcp/MCP.md` for the full 1,111-line
reference: 10 parts (Part I-X), the JSON-RPC 2.0 message
framework, the 4-primitive + 6-layer model, the transport
selection matrix, the Claude Code integration patterns,
the FastMCP Python SDK, the TypeScript SDK, the MCP-UI
protocol (the UI↔agent companion to MCP), the x402 MCP
payment extension, the Better Auth + SIWE integration, the
OWASP-aligned security checklist, and the Dagger MCP
workflow.

## MCP servers

The **9 MCP servers** wired in `opencode.json` for the
KCG agent layer (cognition, code search, tracing, web
scraping, browser automation, SQL analytics, secret
management):

| Server | Port | MCP package | Agent tools |
|:--|:--|:--|:--|
| `cocoindex-code` | — | `ccc mcp` | `cocoindex-code_search(query, limit, languages, paths)` |
| `cognee` | 8100 | `cognee-mcp` | `cognee_add`, `cognee_cognify`, `cognee_search` |
| `graphiti` | 8000 | `graphiti_core.mcp` | `graphiti_search`, `graphiti_get_node`, `graphiti_get_edges` |
| `langfuse` | — | `@langfuse/mcp` | `langfuse_get_trace`, `langfuse_get_traces`, `langfuse_get_prompt` |
| `motherduck` | — | `mcp-server-motherduck` | `motherduck_execute_query`, `motherduck_list_tables` |
| `firecrawl` | — | `firecrawl-mcp` | `firecrawl_scrape`, `firecrawl_search`, `firecrawl_crawl`, `firecrawl_map` |
| `browserbase` | — | `@browserbasehq/mcp` | `browserbase_navigate`, `browserbase_act`, `browserbase_extract`, `browserbase_observe` |
| `chrome` | — | `chrome-devtools-mcp` | `chrome_navigate_page`, `chrome_take_screenshot`, `chrome_take_snapshot` |
| `infisical` | 8081 | `@infisical/mcp` | `infisical_get_secret`, `infisical_list_secrets`, `infisical_create_secret` |

**MCP activation flow**: opencode starts → reads
`opencode.json` → for each `"enabled": true` server →
resolves `infisical://dev-baile/...` URI refs →
auto-installs package (bunx/uvx) → starts subprocess →
registers tools. All sensitive config uses the
`infisical://dev-baile/...` pattern — never plain secrets
on disk; mise directory hooks hydrate `INFISICAL_CLIENT_ID`,
`INFISICAL_CLIENT_SECRET`, `INFISICAL_PROJECT_ID` from
`.env`.

**5-step procedure to add a new MCP server**:
(1) add the block to `opencode.json` under `"mcp"`,
(2) add secrets to Infisical vault,
(3) add the Infisical reference to `.infisical.env`,
(4) run `bun run secrets:init` to hydrate,
(5) restart opencode to pick up the new server.

The 670-line canonical reference (`mcp-servers.md`,
cleaner version selected over the 1,111-line
`MCP_COMPREHENSIVE_RESEARCH.md` per the round-10 merge
map) consolidates 13 source files. It includes the
Python FastMCP SDK, the TypeScript SDK, the Claude Code
integration, OAuth 2.1 + x402 + SIWE authentication,
MCP-UI/Gradio/Evidence integration, and security best
practices.

See `references/mcp-servers/mcp-servers.md` for the full
670-line reference: the protocol fundamentals, the
3-component architecture, the Python FastMCP server
example, the TypeScript SDK usage, the Claude Code
transport wiring, the OAuth 2.1 + x402 + SIWE
authentication, the MCP-UI Gradio + Evidence integration,
the 12 superseded sources, and the 9 entity types.

## Agent framework index

The canonical 4-file index for agent-related
documentation in the Cianfhoghlaim monorepo, after
rounds 1-9 consolidated 36 source files from the legacy
`docs/agents/` subtree into 4 canonical files:

| Canonical file | Covers |
|:--|:--|
| `agent-frameworks.md` | Agno (AgentOS, A2A, Teams), Google ADK (Sequential, Loop, Parallel, Coordinator), CopilotKit (useCopilotAction, useCoAgent, AG-UI), Convex (Agent component, MCP server), Pydantic AI (AG-UI, Gateway, Logfire), durable execution (Restate/DBOS), A2UI, Irish Education Platform blueprint |
| `browser-automation.md` | Browserbase (CDP, stealth, proxies), Stagehand V3 (act, extract, observe, agent), Firecrawl (agent API, MCP tools), Smolagents + Firecrawl deep research, CDP screenshot capture, multi-agent scraping pipelines |
| `baml-extraction.md` | BAML fundamentals, Irish education schemas (Primary/Junior/Senior Cycle), DuckDB/Dragonfly integration, dynamic TypeBuilder, self-healing pipelines (Cognee → BAML generation) |
| `mcp-servers.md` | MCP protocol specification, Python/TypeScript SDKs, Claude Code integration, x402 payments, Better Auth, MCP-UI/Gradio/Evidence, security best practices |

**Entity map** (4 top-level entities, 17 children):

```
AgentFramework ──┬── Agno (AgentOS, A2A, Teams)
                 ├── Google ADK (Sequential, Loop, Parallel, Coordinator)
                 ├── CopilotKit (useCopilotAction, useCoAgent, AG-UI)
                 ├── Convex (Agent component, MCP server)
                 ├── Pydantic AI (AG-UI, Gateway, Logfire)
                 └── DurableExecution (Restate, DBOS)

BrowserAutomation ──┬── Browserbase (CDP, stealth, proxies)
                    ├── Stagehand V3 (act, extract, observe, agent)
                    └── Firecrawl (agent API, MCP tools)

BAMLSchema ──┬── IrishEducation (Primary, Junior Cycle, Senior Cycle)
             ├── DynamicTypeBuilder (runtime schema generation)
             └── SelfHealingPipeline (Cognee → BAML generation)

MCPServer ──┬── Protocol (JSON-RPC 2.0, transports, auth)
            ├── Integrations (Claude, Agno, Dagger, x402)
            └── UI (MCP-UI, Gradio, Evidence, MCP Apps)
```

**8 related agent skills** (the routing layer for any
"which skill should I load?" question): `agno` (Agno
agent dev), `google-adk` (ADK agent dev), `copilotkit` (UI
integration), `browser` (Browserbase interactive browsing),
`firecrawl` (scraping + crawling), `mcp-builder` (MCP
server creation), `dagster` (orchestration),
`dignified-python` (Python engineering standards).

The frontmatter declares `truth: partial` — this is the
**consolidated canonical** but the per-tool deep dives
still live in the skill bodies (this skill, mcp-builder,
baml, etc.).

See `references/agent-frameworks/README.md` for the full
84-line canonical index: the 4-file table, the entity map
(4 entities, 17 children), the 8 related-skills routing
table, and the migration note that all 36 original files
were archived to `docs/archive/2026-06-06-agents/`.

## 2026-06 update: AG-UI + Pydantic AI + DBOS

The 4 agentic-frontend frameworks KCG uses (TanStack Start, CopilotKit, AG-UI, Hono, oRPC) are joined by 3 new ones in 2026.

### AG-UI protocol (CopilotKit's agent↔UI protocol)

The AG-UI protocol is the open SSE-based standard for agent↔UI streaming. The KCG surface uses it for the oideachais API (port 8000) and the croilar portal (port 3001). The protocol handles:

- Streamed text tokens (the agent's response as it's generated)
- Streamed tool calls (the agent's BAML extraction in flight)
- Streamed state updates (the agent's working memory mid-conversation)
- Custom events (per-framework: BAML validation errors, RAGAS scores, etc.)

The `ag-ui` skill (in `.agents/skills/ag-ui/SKILL.md`) documents the full protocol. The oideachais API uses `ag-ui` events for the BAML extraction flow; the copilotkit React components consume them.

### Pydantic AI + the Pydantic AI Gateway

Pydantic AI is a Pydantic-native agent framework that pairs naturally with the AG-UI protocol. The Pydantic AI Gateway (BYOK/managed/cost-limits) routes the agent's LLM calls through a central gateway, with cost limits per agent per model.

The KCG pattern: any new agent (e.g. the 12 in `agents/`) should use Pydantic AI for typed I/O. The `pydantic-ai` skill documents the framework.

### DBOS durable execution

DBOS is a durable execution layer for Python — the agent's state survives crashes and restarts. The KCG pattern is documented in the `pydantic-ai` skill, with a reference implementation in `agents/dbos_demo.py`.

### Pair this skill with

- `ag-ui/SKILL.md` — the AG-UI protocol detail
- `pydantic-ai/SKILL.md` — the Pydantic AI + Gateway + DBOS detail
- `tanstack-start/SKILL.md` — the TanStack Start front-end detail
- `copilotkit/SKILL.md` — the CopilotKit React components
- `hono/SKILL.md` — the Hono API
- `orpc/SKILL.md` — the oRPC type-safe RPC
- `conex/SKILL.md` — the Convex real-time backend
- `cloudflare/SKILL.md` — the Cloudflare Workers / D1 / R2 deploy
