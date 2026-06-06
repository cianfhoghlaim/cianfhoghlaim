---
title: "Agent Frameworks & Orchestration"
domain: agents
status: stable
description: "Consolidated reference for all agent frameworks and orchestration patterns: Agno AgentOS, Google ADK, CopilotKit, Convex, Pydantic AI, Restate/DBOS durable execution, A2UI, and the Irish Education Platform blueprint."
supersedes:
  - docs/agents/agent-frameworks.md
  - docs/agents/AGNO_COMPREHENSIVE_REFERENCE.md
  - docs/agents/agno_architecure_z_ai.md
  - docs/agents/agno-architecture-guide.md
  - docs/agents/agno-openapi-specification-research.md
  - docs/agents/GOOGLE_ADK_COMPREHENSIVE_REFERENCE.md
  - docs/agents/CONVEX_AGENT_PLATFORM.md
  - docs/agents/AGENT_IMPLEMENTATIONS_SUMMARY.md
  - docs/agents/ai-sdk-tools.md
  - docs/agents/PYDIANTIC_AI_REFERENCE.md
  - docs/agents/DURABLE_EXECUTION_COMPREHENSIVE_REFERENCE.md
  - docs/agents/backend-platforms.md
  - docs/agents/Agent UI Ecosystem - A2UI.md
  - docs/agents/IRISH_EDUCATION_PLATFORM_BLUEPRINT.md
  - docs/agents/Agentic Education Platform Development.md
  - docs/agents/Agentic Translation Workflow Technologies.md
  - docs/agents/AI Agents for Irish Language Resources.md
entities:
  - AgnoAgent
  - AgnoTeam
  - AgentOS
  - GoogleADK
  - CopilotKit
  - CoAgent
  - ConvexAgent
  - PydanticAI
  - RestateService
  - DBOSWorkflow
  - A2UIProtocol
  - IrishEducationPlatform
  - ZaiGLM
  - T5Gemma2
  - Gemini3
related_skills:
  - .agents/skills/agno/SKILL.md
  - .agents/skills/google-adk/SKILL.md
  - .agents/skills/copilotkit/SKILL.md
  - .agents/skills/dagster/SKILL.md
  - .agents/skills/dignified-python/SKILL.md
ccc_query_hints:
  - "Agno AgentOS OpenAPI specification"
  - "Google ADK workflow primitives sequential loop parallel"
  - "CopilotKit useCopilotAction useCoAgent hooks"
  - "Restate durable execution awakeables human-in-the-loop"
  - "Irish education platform agentic architecture"
  - "Z.ai GLM-4.6v vision MCP integration"
  - "how to set up multi-agent teams in Agno"
last_reviewed: 2026-06-06
---

# Agent Frameworks & Orchestration

## Part I: Agno Framework (AgentOS)

### Overview

Agno (formerly PhiData) is an open-source Python framework for multi-agent AI systems. Key characteristics:
- Agent instantiation in **~3 microseconds** (orders of magnitude faster than graph-based alternatives)
- Knowledge base integration via vector search (LanceDB, Qdrant, pgvector)
- Persistent agent memory across multi-step workflows
- Multi-model support via LiteLLM gateway
- A2A (Agent-to-Agent) protocol for cross-agent communication
- AgentOS for serving agents as APIs

### Team Modes

| Mode | Behavior | Use Case |
|---|---|---|
| **Route** | Single agent handles the request | Simple queries |
| **Coordinate** | Team leader orchestrates agents sequentially | Ordered data flow (UI learning) |
| **Collaborate** | Parallel execution — multiple agents work simultaneously | Independent subtasks |

### AgentOS — OpenAPI & API Deployment

AgentOS provides a FastAPI-compatible server for deploying agents as APIs. The AGUI interface wraps agents in standard protocol endpoints (POST `/agui`, SSE streams for events).

```python
from agno.agent import Agent
from agno.os import AgentOS
from agno.os.interfaces.agui import AGUI

agent = Agent(name="My Agent", model=OpenAIChat(id="gpt-4o"))
agent_os = AgentOS(agents=[agent], interfaces=[AGUI(agent=agent)])
app = agent_os.get_app()
agent_os.serve(app="app:app", port=7777, reload=True)
```

**OpenAPI Spec:** `https://raw.githubusercontent.com/agno-agi/agno-docs/main/reference-api/openapi.json`
**Local:** `http://localhost:7777/openapi.json` when running locally

### A2A Protocol

Agno's A2A protocol is built on **JSON-RPC 2.0** over HTTP with Server-Sent Events for streaming. Agents discover each other via Agent Cards at `/.well-known/agent.json`. Seven task states: submitted, working, completed, failed, cancelled, rejected, input-required.

### Agentic Chunking

Agno uses LLM-driven semantic boundary detection for chunking documents — each chunk maps 1:1 to an assessment unit (e.g., an exam question). Combines with hybrid search: keyword filter on metadata BEFORE semantic vector search.

### Multi-Agent System Architecture with Dagster + DLT

Teams of Agno agents are orchestrated by Dagster pipelines:
1. Ingestion (DLT or Crawl4AI) → 2. CocoIndex indexing → 3. Agno agents with BAML-defined structured outputs → 4. Cognee knowledge graph

### Custom Model Integration (Z.ai GLM-4.6)

```python
from agno.models.openai.like import OpenAILike

zhipu_text_model = OpenAILike(
    id="glm-4.6",
    api_key=os.getenv("ZHIPU_API_KEY"),
    base_url="https://open.bigmodel.cn/api/paas/v4/",
    max_tokens=4096,
    temperature=0.1
)
```

---

## Part II: Google Agent Development Kit (ADK)

### Workflow Primitives

| Primitive | Pattern | Description |
|---|---|---|
| **Sequential Agent** | Linear phases | OCR → Text Cleaning → Context Extraction |
| **Loop Agent** | Draft-Critique-Refine | Drafter + Critic iterate until quality threshold |
| **Parallel Agent** | Fan-Out/Gather | Splits documents into sections, processes concurrently |
| **Coordinator** | TripPlanner pattern | Root Agent as persistent Project Manager, prevents "Receptionist Problem" |

### Neuro-Symbolic Truth Anchoring

The ADK Compliance Agent integrates symbolic Ontology (OWL Knowledge Graph) for deterministic verification. If Glossary mandates "Mionnscríbhinn" for "Affidavit" and neural model outputs "Ráiteas faoi mhionn" (valid synonym), symbolic layer detects mismatch and forces correction.

### Deployment

Terraform-based deployment to Google Cloud: Agent Engine for production serving, Cloud Build for CI/CD, Cloud Trace for telemetry.

```bash
make install && make playground
make deploy
make register-gemini-enterprise
```

### Example Projects

- **Academic Research:** Multi-agent pipeline — Web Search Agent → New Research Agent
- **Deep Search:** Full-stack React frontend + ADK-powered FastAPI backend, Human-in-the-Loop plan approval
- **Firecrawl Integration:** ADK agent with Firecrawl tools for web scraping
- **LaunchMyBakery:** Complete business launch agent using ADK with MCP tools

---

## Part III: CopilotKit Framework

### Architecture

CopilotKit is a monorepo-based framework with these core packages:

| Package | Purpose |
|---|---|
| `react-core` | Core React hooks and context |
| `react-ui` | Pre-built UI components |
| `runtime` | Backend runtime |
| `runtime-client-gql` | GraphQL client |

### Core Hooks

**`useCopilotAction`** — Register frontend actions the agent can call:
```typescript
useCopilotAction({
  name: "updateUserProfile",
  parameters: [{ name: "name", type: "string" }, { name: "email", type: "string" }],
  handler: async ({ name, email }) => { await api.updateProfile({ name, email }); },
});
```

**`useCoAgent`** — Bidirectional shared-state agent management:
```typescript
const { state, setState, running, start, stop } = useCoAgent<AgentState>({
  name: "my-agent",
  initialState: { count: 0 },
});
```

**`useCopilotChat`** — Headless chat hook for programmatic control:
```typescript
const { visibleMessages, appendMessage, reloadMessages, stopGeneration, reset } = useCopilotChat();
```

### Action Availability Modes

| Mode | Behavior |
|---|---|
| `disabled` | Action unavailable to agent |
| `enabled` | Standard agent-callable action |
| `remote` | Only callable from backend, rendered on frontend |
| `frontend` | Client-side only, never sent to backend |

### Runtime — Multi-LLM Support

OpenAI (with Assistant API), Anthropic, Google GenAI, Groq, Bedrock (AWS), Unify, Ollama (experimental), LangChain/LangServe, custom adapters.

### State Management Comparison

| Aspect | CopilotKit | Agno AgentOS |
|---|---|---|
| State Manager | React Context | Zustand |
| Persistence | In-memory | localStorage (endpoint) |
| Auth | Per-action | Global bearer token |
| Thread Management | Via runtime client | Via session IDs |
| Backend Coupling | Custom runtime required | Direct API calls |

---

## Part IV: Convex Agent Platform

### Agent Component

The `@convex-dev/agent` component manages threads and messages for cooperative agent workflows:
- **Agents:** Units of use-case-specific prompting with models, prompts, tool calls
- **Threads:** Persist messages, shared by multiple users and agents
- **Streaming:** Text and objects using deltas over WebSockets
- **RAG:** Supports prompt augmentation, integrates with RAG Component
- **Workflows:** Multi-step operations spanning agents and users, durably
- **Usage Tracking:** Per-provider, per-model, per-user, per-agent attribution

### Convex MCP Server

```bash
npx -y convex@latest mcp start
```

Exposes tools for deployment status, table inspection, data queries, function execution, and environment variable management.

---

## Part V: Pydantic AI

### AG-UI Protocol Integration

The Agent-User Interaction (AG-UI) Protocol is an open standard by the CopilotKit team. Pydantic AI supports full AG-UI spec: events, messages, state management, and tools — using ASGI with Starlette/FastAPI.

```bash
pip install 'pydantic-ai-slim[ag-ui]'
```

### Pydantic AI Gateway

Unified interface for multiple AI providers with a single key. Features: API key management, cost limits, BYOK and managed providers, multi-provider support (OpenAI, Anthropic, Google Vertex, Groq, AWS Bedrock), OpenTelemetry observability, zero-translation pass-through, self-hosting under AGPL-3.0.

```python
agent = Agent('gateway/openai:gpt-5')
```

### Logfire — MCP Instrumentation

```python
import logfire
logfire.instrument_mcp()
logfire.instrument_pydantic_ai()
```

---

## Part VI: Durable Execution (Restate & DBOS)

### Restate

Restate adds production-grade resilience to AI agent workflows:

| Feature | What it Solves |
|---|---|
| **Durable Execution** | Crash-safe LLM/tool calls, idempotent retries |
| **Observability** | Auto-captured trace of every step, retry, message |
| **Human-in-the-loop** | Suspend while waiting for approval; pay for compute, not wall-clock time |
| **Stateful sessions** | Virtual Objects keep multi-turn conversations isolated |
| **Multi-agent orchestration** | Reliable RPC, queuing, scheduling between agents |

**Awakeables (Human-in-the-Loop):**
```typescript
await ctx.awakeable();  // Suspends — zero compute consumed
// Days later, teacher clicks "Approve"
// Restate restores state, resumes at next line
finalizeGrade();
```

**Composable AI Patterns:** Prompt Chaining, Tool Routing, Parallel Tools, Multi-Agent Routing, Human-in-the-loop, Chat Sessions, Orchestrator-Worker, Evaluator-Optimizer, Racing Agents.

**SDK Integrations:** Vercel AI SDK, OpenAI Agents SDK, A2A protocol, MCP tool servers.

### DBOS

DBOS (Database-Backed Operating System) provides durable execution primitives: workflows, steps, transactions, communicators, queues, scheduled workflows. Examples include: Widget Store (e-commerce), S3 Mirror (reliable transfers), Reliable Refunds with LangChain, Hacker News Research Agent, Document Detective (RAG pipeline).

---

## Part VII: A2UI — Agent-Driven User Interfaces

A2UI is a streaming protocol where agents send JSON component blueprints to a client renderer, producing native UI. Key positioning: complementary to AG UI/CopilotKit — "secure like data, expressive like code."

**How A2UI differs from MCP Apps:** A2UI sends native component blueprints (not opaque HTML payloads), allowing the host app's styling and accessibility to be inherited. In multi-agent systems, orchestrator agents can understand A2UI message content for fluid collaboration.

**Transports:** A2A protocol, AG UI protocol. REST/SSE/WebSocket transports are feasible but not yet available.

---

## Part VIII: Irish Education Platform Blueprint

### Agentic Academy Architecture

The platform transitions from static LMS to an agentic model where Tutor Agents dynamically generate lessons, assess proficiency, and transact value in a decentralized economy.

**Core Components:**

| Component | Technology | Role |
|---|---|---|
| Agent Framework | CopilotKit / Agno | Application-level orchestration |
| UI Protocol | AgUI | Event-based agent-frontend communication |
| Data Protocol | MCP | Standardized tool/resource access |
| Payments | x402 + Coinbase AgentKit | Machine-to-machine payments |
| Reputation | EAS + Soulbound Tokens | On-chain academic credentials |

**Dual-Token System:** "Pinginn" (ERC-20 USDC, medium of exchange) and "Screpall" (Soulbound Token, store of merit).

### Neuro-Symbolic Gaeilge Engine

**Challenge:** Preserving Irish language artifacts requires processing historical manuscripts, bilingual documents with Cló Gaelach, and mathematical diagrams.

**Team Topology (Agno):**

| Agent | Role | Model |
|---|---|---|
| Chief Examiner | Orchestrator, decomposes user requests | GLM-4.6 |
| Palaeographer | Visual interpretation of handwriting/diagrams | GLM-4.6v via MCP |
| Ontologist | BAML parsing into Leaving Certificate schema | GLM-4.6 |

**Z.ai GLM-4.6v MCP Integration:** Vision MCP tools expose `ui_to_artifact`, `extract_text_from_screenshot`, `Web Reader` for advanced OCR and DOM extraction.

### Agentic Translation Workflow

**Gemini 3 (System 2 Reasoning):** Adaptive Compute protocols allocate inference resources dynamically. Critic Agent flow: Plan → Verify → Reflect → Justify (immutable "Thought Signature" audit log).

**T5Gemma-2 (Efficiency Core):** Encoder-decoder architecture with tied embeddings (~10.5% parameter reduction), merged attention, UL2 adaptation from Gemma 3 weights. Supports 140+ languages including low-resource Celtic.

**ADK Workflow Application:** Sequential (OCR → Cleaning → Extraction), Loop (Draft-Critique-Refine with T5Gemma-2 + Gemini 3), Parallel (Fan-Out/Gather for concurrent section translation).

---

## Technology Stack Summary

| Layer | Technology | Purpose |
|---|---|---|
| Agent Framework | Agno / CopilotKit | Application-level orchestration |
| UI Protocol | AgUI / A2UI | Agent-frontend communication |
| Data Protocol | MCP | Standardized tool/resource access |
| Durable Execution | Restate / DBOS | Crash-safe agent workflows |
| Vision | Z.ai GLM-4.6v | Handwriting recognition, diagram analysis |
| Reasoning | Gemini 3 Pro | System 2 deep reasoning, critique |
| Drafting | T5Gemma-2 | Encoder-decoder translation |
| Orchestration | Google ADK | Workflow primitives (Sequential, Loop, Parallel) |
| ETL | CocoIndex | Incremental dataflow with memoization |
| Knowledge Graph | Cognee + Graphiti | Semantic graph + temporal reasoning |
| Vector DB | LanceDB / pgvector | Hybrid search for curriculum content |
| Schema | BAML | Type-safe LLM extraction |
| Monitoring | Langfuse + Ragas | Observability and evaluation |
| Serving | Transformers v5 | Continuous batching, local model hosting |
