---
name: google-adk
description: Expert assistance for building AI agents with Google's Agent Development Kit. Use when users need multi-agent coordination via the Multi-Agent Workflow Engine + NodeRunner, Native Inter-Agent Routing (v2.1+), the A2A Protocol for cross-agent communication, neuro-symbolic OWL truth-anchoring, or production deployment to Agent Engine. KCG-specific: agent chain is OCR → BAML → embedding → Graphiti → RAGAS.
---

# Google ADK - Agent Development Kit

**Version:** >=2.1.0 | **Last Updated:** 2026-06

## Overview

Google's Agent Development Kit (ADK) is a framework for building
production AI agents with first-class multi-agent coordination:

- **Multi-Agent Workflow Engine** + **NodeRunner** — explicit
  workflow graph with deterministic orchestration
- **Native Inter-Agent Routing** (v2.1+) — agents route to other
  agents based on request content, with fallback chains
- **A2A Protocol** — agent-to-agent communication via the open
  protocol (`/.well-known/agent.json` Agent Cards, JSON-RPC
  2.0 over SSE)
- **Workflow Primitives** — `SequentialAgent`, `LoopAgent`
  (with `TerminationStrategy`), `ParallelAgent` (fan-out /
  gather), Coordinator Pattern
- **Neuro-Symbolic Truth Anchoring** — OWL knowledge graph
  enforces hard constraints on LLM outputs (e.g. compliance,
  regulatory)
- **Production deployment** — `make deploy` to Agent Engine
  (managed), with `make register-gemini-enterprise`,
  always-on Cloud Trace, optional GCS / BigQuery / Cloud Logging
- **Google AI Integration** — Gemini Live API, Firecrawl
  integration via TypeScript adapters

**Documentation:** <https://cloud.google.com/agent-development-kit>

## When to Use This Skill

Activate when users need:

- "Build a multi-agent system with explicit workflow control"
- "Create Google AI agents"
- "Coordinate multiple agents with the A2A Protocol"
- "Anchor an LLM's output to an OWL knowledge graph"
- "Deploy agents to Google Agent Engine"
- "Wire Gemini Live API into a voice agent"
- "Integrate Firecrawl scraping into an agent"

## Core Concepts

### Agent

The basic unit. Created via `Agent(...)` with a model, system
prompt, tools, and (optionally) a sub-agent list.

```python
from google.adk.agents import Agent

agent = Agent(
    name="curriculum_extractor",
    model="gemini-2.5-pro",
    system_prompt="Extract curriculum areas and learning outcomes.",
    tools=[pdf_extractor, schema_validator],
)
```

### Multi-Agent Coordination (v2.1+)

The `Multi-Agent Workflow Engine` + `NodeRunner` provides
**explicit, deterministic** orchestration. There are 4
workflow primitives:

#### 1. `SequentialAgent`

A → B → C. The output of A is the input of B, etc.

```python
from google.adk.agents import SequentialAgent

pipeline = SequentialAgent(
    name="ocr_to_kg_pipeline",
    sub_agents=[
        ocr_agent,        # step 1: PDF → text
        baml_extractor,   # step 2: text → typed BAML class
        embedder,         # step 3: text → vector embedding
        kg_writer,        # step 4: embedding + metadata → Graphiti
    ],
)
```

#### 2. `LoopAgent` (with `TerminationStrategy`)

A → B → A → B → ... until a termination strategy is met. The
canonical use case is **draft-critique-refine**:

```python
from google.adk.agents import LoopAgent, TerminationStrategy

loop = LoopAgent(
    name="draft_critique_refine",
    sub_agents=[draft_writer, critic],
    termination=TerminationStrategy(
        # Stop when the critic returns "approved"
        stop_on=lambda critic_output: "approved" in critic_output,
        max_iterations=5,  # safety cap
    ),
)
```

#### 3. `ParallelAgent` (fan-out / gather)

Run N agents in parallel, gather their outputs.

```python
from google.adk.agents import ParallelAgent

parallel = ParallelAgent(
    name="multi_perspective_analyzer",
    sub_agents=[
        linguistic_analyzer,    # runs in parallel
        cultural_analyzer,      # runs in parallel
        historical_analyzer,    # runs in parallel
    ],
    # The outputs are gathered into a list and passed to the
    # downstream agent.
)
```

#### 4. Coordinator Pattern (TripPlanner)

A "root" agent that has a fleet of sub-agents and routes to
them based on the request. The canonical example is TripPlanner
— a coordinator with `flights`, `hotels`, and `activities`
sub-agents:

```python
coordinator = Agent(
    name="trip_planner",
    model="gemini-2.5-pro",
    system_prompt="You are a trip planner. Route to the right sub-agent.",
    sub_agents=[flights_agent, hotels_agent, activities_agent],
)
```

In v2.1+, the routing is **native** — the coordinator's model
makes the routing decision automatically, no manual routing
logic required.

## A2A Protocol (Agent-to-Agent)

For cross-agent communication across processes (or even across
vendors), use the [A2A Protocol](https://a2a.dev/). The wire
format is JSON-RPC 2.0 over SSE, with a discovery endpoint
(`/.well-known/agent.json`).

### Server side (your agent)

```python
from google.adk.a2a import A2AServer

server = A2AServer(
    agent=my_agent,
    agent_card_url="https://my-agent.example.com/.well-known/agent.json",
    port=8080,
)
server.serve()
```

### Client side (another agent calling yours)

```python
from google.adk.a2a import A2AClient

client = A2AClient("https://my-agent.example.com")
result = client.call("extract_curriculum", {"pdf_url": "..."})
```

The agent card (at `/.well-known/agent.json`) advertises the
capabilities, input/output schema, and version.

## Neuro-Symbolic Truth Anchoring

For compliance-critical agents (e.g. medical, legal, financial),
ADK supports an OWL knowledge graph as a **hard constraint**
on the LLM output. The LLM proposes, the OWL engine disposes.

```python
from google.adk.symbolic import OWLTruthAnchor

# Load the OWL ontology
anchor = OWLTruthAnchor.from_file("compliance.owl")

# Wrap any agent with the truth anchor
anchored_agent = anchor.wrap(
    agent=my_compliance_agent,
    # If the agent output violates the OWL ontology,
    # reject it and ask the agent to retry.
    reject_and_retry=True,
)
```

**Canonical KCG use case:** the `Mionnscríbhinn` (Irish-language
land deed) Compliance Agent. The LLM proposes extracted
entities, the OWL ontology (which encodes the 19th-century
Irish land-tenure model) validates, and any output that
violates the ontology is rejected.

## Production Deployment

The canonical deployment is Google Agent Engine (managed):

```bash
# Build and push the container
make deploy

# Or directly
gcloud run deploy my-agent \
  --image gcr.io/PROJECT/my-agent \
  --region us-central1 \
  --set-env-vars GOOGLE_API_KEY=...
```

`make deploy` (in the KCG `saoi/` project layout) builds,
pushes, and deploys in one step. After deployment, the agent
endpoint is available at the Agent Engine URL.

### Register with Gemini Enterprise

```bash
make register-gemini-enterprise
```

This makes the agent discoverable in the Gemini Enterprise
console (for users with a Google Workspace license).

### Observability

Agent Engine automatically enables:

- **Cloud Trace** (always on) — every agent invocation is
  traced with full input / output / tool calls
- **GCS export** (optional) — `GOOGLE_CLOUD_STORAGE_BUCKET=...`
- **BigQuery export** (optional) — for SQL analytics on
  agent traffic
- **Cloud Logging** (optional) — `GOOGLE_CLOUD_LOGGING=true`

## Tools

Any Python function can be a tool:

```python
from google.adk.tools import tool

@tool
async def get_weather(city: str) -> dict:
    """Get the current weather for a city."""
    response = await fetch(f"https://api.weather.com/{city}")
    return response.json()
```

The function's signature + docstring are auto-extracted into
the agent's tool schema. The LLM decides when to call the tool.

## Multimodal (Gemini Vision)

```python
agent = Agent(
    name="receipt_extractor",
    model="gemini-2.5-pro",  # vision-capable
    system_prompt="Extract line items from this receipt image.",
    tools=[receipt_validator],
)
```

Pass images / PDFs as `parts` in the request; Gemini handles
the rest.

## Gemini Live API (voice / streaming)

```python
from google.adk.live import LiveAgent

agent = LiveAgent(
    name="voice_assistant",
    model="gemini-2.5-flash-live",
    voice="en-US-Neural2-A",
)
```

Use the Live API for real-time voice conversations, low-latency
chat, or streaming audio. The ADK handles the WebSocket /
audio encoding for you.

## Firecrawl Integration (TypeScript)

For agents that need to scrape web pages, use the Firecrawl
adapter (TypeScript):

```typescript
import { Agent, firecrawl } from "@google/adk";

const agent = new Agent({
  name: "scraper",
  model: "gemini-2.5-pro",
  tools: [
    firecrawl({
      apiKey: process.env.FIRECRAWL_API_KEY,
    }),
  ],
});
```

The `firecrawl` tool can scrape, crawl, and extract structured
data from any URL.

## KCG agent chain (KCG-specific)

The KCG ingestion pipeline is a 5-stage SequentialAgent:

```python
from google.adk.agents import SequentialAgent

kcg_pipeline = SequentialAgent(
    name="kcg_ingestion",
    sub_agents=[
        ocr_agent,        # PDF → text (Docling, PaddleOCR, ColPali)
        baml_extractor,   # text → typed BAML class
        embedder,         # text → vector (BGE-M3 or BGE-large-en)
        graphiti_agent,   # vector + metadata → Graphiti episode
        ragas_evaluator,  # run 6 deterministic evals
    ],
)
```

This is wired up via the `oideachais-curriculum-extraction`
Dagster asset, which runs the pipeline against incoming NCCA
PDFs.

## Memory and Context

```python
from google.adk.memory import InMemoryMemory

memory = InMemoryMemory()

agent = Agent(
    name="tutor",
    model="gemini-2.5-pro",
    memory=memory,
    system_prompt="You are a tutor. Remember the student's progress.",
)
```

For production, use a persistent memory store (Vertex AI
Memory Bank or a custom backend).

## KCG integration notes

- LLM backend: **LiteLLM gateway** (project gateway; LiteLLM
  routes to Gemini, OpenAI, Anthropic, etc.)
- Tracing: **Langfuse** (project tracing) — every agent
  invocation is traced
- Memory: **Graphiti** (bi-temporal knowledge graph) + Cognee
  (the primary KG) for long-term context
- Eval: **RAGAS** (project eval) for end-to-end agent quality
- Related skills: `.agents/skills/agno/`,
  `.agents/skills/pydantic-ai/`, `.agents/skills/baml/`,
  `.agents/skills/litellm/`, `.agents/skills/langfuse/`,
  `.agents/skills/ragas/`

## Resources

- ADK docs: <https://cloud.google.com/agent-development-kit>
- A2A Protocol: <https://a2a.dev/>
- Agent Engine: <https://cloud.google.com/agent-engine>
- Gemini Live API: <https://ai.google.dev/gemini-api/docs/live>
- KCG agent chain: `oideachais-curriculum-extraction` Dagster
  asset
- KCG examples: `oideachais/saoi/` (the canonical KCG ADK
  project layout)

## Framework comparison (when to use this vs Pydantic AI / Agno)

| Use case | Google ADK | Pydantic AI | Agno |
|:--|:--|:--|:--|
| Gemini Live API / voice | ✅ first-class | ⚠️ via OpenAI | ⚠️ via OpenAI |
| A2A Protocol | ✅ built-in | ⚠️ via adapter | ✅ built-in |
| AgentOS / managed deploy | ✅ Agent Engine | ⚠️ self-host | ✅ AgentOS |
| Neuro-symbolic OWL | ✅ Truth Anchoring | ❌ | ❌ |
| MCP server | ✅ built-in | ✅ via adapter | ✅ via adapter |
| Workflow primitives (Sequential/Loop/Parallel) | ✅ first-class | ⚠️ via DBOS | ✅ first-class |
| Type-safe I/O (Pydantic) | ✅ | ✅ first-class | ✅ |
| Multi-model support (OpenAI, Anthropic, Gemini) | ⚠️ Gemini-first | ✅ any | ✅ any |
| AG-UI SSE integration | ⚠️ via adapter | ✅ first-class | ✅ first-class |

**Rule of thumb**: use **Google ADK** for Gemini-heavy
workflows (Live API, A2A, Agent Engine); use **Pydantic AI**
for type-safe I/O with Pydantic models (the KCG standard);
use **Agno** for multi-agent teams with Z.ai GLM-4.6
(cost-effective).
