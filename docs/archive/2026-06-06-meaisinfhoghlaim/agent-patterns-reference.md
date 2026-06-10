# Agent Patterns, MCP, and Autonomous Systems

**Merged From:**
- `agents/Building a Hybrid Self-Hosted Agent Stack.md`, `agents/Building an Agentic Tutor.md`
- `agents/Central MCP Management for LiteLLM.md`, `agents/claude-extensions.md`
- `agents/github-copilot-configuration.md`, `agents/Interactive Map & AI Agents.md`
- `agents/Maximizing Claude Credits for Project Improvement.md`, `agents/MMO Geospatial Data & Visual RAG.md`
- `agents/Multimodal Video Knowledge Graph Pipeline.md`, `agents/Use Agent Skills in VS Code.md`
- `agents/useAgent Hook.md`
- `Google ADK with LiteLLM _ liteLLM.md`, `Interactions API _ Gemini API _ Google AI for Developers.md`
- `AI_MEMORY.md`, `huggingface-design-patterns-analysis.md`

---

## Table of Contents

1. [Agent Architecture Overview](#agent-architecture)
2. [Google ADK: Agent Orchestration](#google-adk)
3. [Model Context Protocol (MCP)](#model-context-protocol)
4. [Agentic Tutoring Systems](#agentic-tutoring)
5. [Browser Automation Agents](#browser-automation)
6. [Knowledge & Memory Systems](#knowledge-memory)
7. [Gemini API for Agents](#gemini-api)
8. [Agent-Driven Fine-Tuning](#agent-driven-fine-tuning)

---

## Agent Architecture Overview

### The Tiered Agent Stack

```text
┌─────────────────────────────────────────┐
│         Orchestration Layer              │
│  Google ADK / Agno / Claude Code         │
├─────────────────────────────────────────┤
│         Connectivity Layer               │
│  Model Context Protocol (MCP)            │
├─────────────────────────────────────────┤
│         Reasoning Engines                │
│  Gemini 3 Flash/Pro, GLM-4.6v           │
├─────────────────────────────────────────┤
│         Capability Layer                 │
│  Crawl4AI, Skyvern, Docling, Search     │
├─────────────────────────────────────────┤
│         Memory Layer                     │
│  Cognee, CocoIndex, LanceDB, Memgraph   │
└─────────────────────────────────────────┘
```

### Agent Types by Use Case

| Agent Type | Framework | Model | Key Tools |
|-----------|-----------|-------|-----------|
| **Deep Research** | Google ADK | Gemini 3 Pro + GLM-4.6v | Crawl4AI, Skyvern, Search MCP |
| **Educational Tutor** | Agno | Gemini 3 Flash | CocoIndex, LanceDB, Graphiti |
| **Code Assistant** | Claude Code | Claude Code Max | Repomix, MCP servers |
| **Vision Specialist** | MCP + Z.AI | GLM-4.6v | Vision MCP, Reader MCP |
| **Browser Agent** | ADK + Patchright | Gemini 3 Flash | Chrome DevTools MCP |

---

## Google ADK

Google's Agent Development Kit provides a rigorous framework for agentic behavior.

### Core Primitives

```python
from google.adk.agents import LlmAgent
from google.adk.tools import FunctionTool
from google.adk.tools.mcp import McpToolset

# Research agent with MCP tools
research_agent = LlmAgent(
    name="DeepResearcher",
    model="gemini-3-pro",
    instruction="""
    1. Formulate search queries to find information
    2. Cross-reference data from at least 2 sources
    3. Stop when 80% of requested fields are populated
    4. Synthesize findings into structured report
    """,
    tools=[
        FunctionTool(search_web),
        McpToolset(connection_params={
            "url": "http://crawl4ai:8000/sse",
            "transport": "sse"
        })
    ]
)
```

### Model Selection Strategy

- **Gemini 3 Flash** — Inner loops: URL validation, selector checks, short snippets. High-frequency, low-cost.
- **Gemini 3 Pro** — Outer loops: research planning, result synthesis, complex reasoning.
- **thinking_level** — Configure per-task: "LOW" for simple extraction, "HIGH" for multi-step wizard navigation.

### MCP Integration in ADK

ADK's `McpToolset` treats local Python functions, remote HTTP endpoints, and Dockerized services as uniform tools. Supports:
- **stdio** transport for local processes
- **SSE** transport for containerized services
- **Hybrid fallback**: Agent sees `scrape_local` and `scrape_remote` as equivalent tools, chooses based on context

---

## Model Context Protocol (MCP)

MCP standardizes the interface between agents (Clients) and tools (Servers).

### Architecture

```text
Agent (MCP Client)
    │
    ├──→ Vision MCP Server (GLM-4.6v)
    ├──→ Search MCP Server (web search)
    ├──→ Reader MCP Server (page → clean text)
    ├──→ Crawl4AI MCP Server (extraction)
    ├──→ Docling MCP Server (PDF → structured)
    └──→ Chrome DevTools MCP (browser state)
```

### MCP + LiteLLM Gateway

```yaml
# Central MCP management through LiteLLM
mcp_servers:
  docling_service:
    command: "uvx"
    args: ["docling-mcp-server"]

  vision_service:
    command: "npx"
    args: ["-y", "@vision/mcp-server"]
    env:
      API_KEY: os.environ/VISION_API_KEY

  search_service:
    command: "npx"
    args: ["-y", "@search/mcp-server"]
```

### Self-Hosted Deep Research Stack

Replicating Firecrawl/Browserbase capabilities:

| Capability | SaaS | Self-Hosted Alternative |
|-----------|------|------------------------|
| Browser automation | Browserbase | Patchright (anti-bot) + Skyvern (vision-based) |
| Web scraping | Firecrawl /agent | Crawl4AI + MCP server |
| Semantic extraction | Firecrawl LLM extract | Crawl4AI + Gemini Flash |
| Visual navigation | Stagehand | Skyvern + GLM-4.6v Vision MCP |
| Session management | Browserbase sessions | Docker browsers + Redis state |

---

## Agentic Tutoring

### Architecture for Educational AI

**Ingestion Plane** (async, heavy processing):
1. CocoIndex: PDF parsing → Smart chunking → Embedding
2. Cloudflare R2: Source asset storage (zero egress)
3. LanceDB: Vector embeddings for semantic search
4. Graphiti + FalkorDB: Temporal knowledge graph (curriculum validity windows)

**Interaction Plane** (sync, real-time):
1. Agno agent receives student query
2. Hybrid retrieval: LanceDB (semantic) + Graphiti (temporal graph)
3. Structured output via BAML schema
4. Generative UI via CopilotKit/mcp-ui

### Smart Chunking for Exams

Educational documents require hierarchy-aware chunking:
- **Paper level**: Year, Level (Higher/Ordinary), Season
- **Section level**: Section A (Concepts) vs Section B (Applications)
- **Question level**: Preamble + sub-parts (a)(b)(c) — never split
- **Marking schemes**: Must retrieve alongside questions

### Temporal Validity

Graphiti's bi-temporal model tags knowledge with validity windows:
- "This chemistry question is valid 2010-2023"
- Agent reasons about *current* syllabus alignment before generating content
- Prevents negative transfer (teaching obsolete material)

---

## Browser Automation

### Self-Hosted Alternatives

**Patchright** — Anti-bot browser:
- Mimics human fingerprints (User-Agent, Canvas noise, WebGL)
- Replaces hardcoded `.cuda()` calls for MPS compatibility

**Skyvern** — Visual navigation:
- Vision-driven interaction (no CSS selectors)
- "Click the login button" resolved via vision model
- Natural language `act()` and `observe()` primitives

**Crawl4AI** — Semantic extraction:
- LLM-ready markdown generation
- Session management + proxy support
- Docker deployment for MCP server

### Hybrid Fallback Pattern

```python
async def scrape_page(url, prefer_local=True):
    try:
        if prefer_local:
            result = await crawl4ai.arun(url)  # Free, local
        else:
            result = await firecrawl_scrape(url)  # SaaS
    except Exception:
        result = await firecrawl_scrape(url)  # Fallback to SaaS
    return result
```

---

## Knowledge & Memory

### Cognee

Ready-to-use AI memory layer:
- Extract-Cognify-Load pipeline
- Chunks documents, generates embeddings, identifies entities/relationships
- Hybrid retrieval: Vector, Graph, GraphRAG
- MCP server for agent integration

### CocoIndex

Data engineering toolkit for indexing:
- Incremental processing with Postgres state tracking
- LLM-powered transformations (extraction, embedding)
- Multi-backend export (LanceDB, Memgraph, Qdrant)

### Cognee vs CocoIndex

| Feature | Cognee | CocoIndex |
|---------|--------|-----------|
| Primary Focus | Ready-to-use AI memory | Data engineering for indexing |
| Query Interface | Built-in (Python API + MCP) | Manual (query DBs directly) |
| Pipeline Control | Opinionated (simple ingestion) | Fine-grained (custom flows, incremental) |
| Online Learning | Supported | Not built-in |
| Best For | Runtime query answering, agent memory | Complex ETL, large-scale indexing |

### Recommended Strategy

**CocoIndex for Indexing + Cognee for Querying:**
1. CocoIndex handles heavy ETL extraction + incremental updates → LanceDB + Memgraph
2. Cognee provides intelligent retrieval with MCP server for agent integration

---

## Gemini API

### Key Features

- **1M token context window** (Gemini 3 Pro)
- **Structured output** with JSON schema enforcement
- **Interactions API**: Break tasks into "turns" — each turn produces thought → action → observation
- **Grounding**: Link responses to Google Search results
- **Code execution**: Built-in Python sandbox

### Interactions API

```python
# Gemini Interactions API pattern
interaction = {
    "turns": [
        {
            "thought": "I need to calculate the determinant...",
            "action": {"tool": "calculate_determinant", "params": {"matrix": [[2,3],[-1,1]]}},
            "observation": "det = 5"
        },
        {
            "thought": "The determinant is 5...",
            "action": {"tool": "solve_system", "params": {...}},
            "observation": "x = 1, y = -2"
        }
    ]
}
```

### ADK + Gemini Integration

```python
agent = LlmAgent(
    model="gemini-3-flash",
    instruction="You are a research agent. Plan first, then execute.",
    tools=[search_tool, scrape_tool],
    thinking_level="HIGH"  # Internal CoT before actions
)
```

---

## Agent-Driven Fine-Tuning

### Hugging Face Skills

Claude Code (and other coding agents) can autonomously:
1. Validate dataset format
2. Select appropriate GPU hardware
3. Generate and submit training scripts
4. Monitor progress with Trackio
5. Push finished models to Hugging Face Hub

```bash
# Claude Code plugin installation
/plugin marketplace add huggingface/skills
/plugin install hf-llm-trainer@huggingface-skills

# Then just ask:
"Fine-tune Qwen3-0.6B on open-r1/codeforces-cots"
```

**Cost:** ~$0.30 for a 0.6B model fine-tune on t4-small.

### Hardware Mapping

| Model Size | GPU | Est. Cost |
|-----------|-----|-----------|
| <1B | t4-small | $1-2 |
| 1-3B | t4-medium / a10g-small | $5-15 |
| 3-7B | a10g-large / a100-large (LoRA) | $15-40 |
| 7B+ | Not suitable for HF Jobs | - |

---

## MCP Tool Reference

### Available MCP Servers

| Server | Capability | Usage |
|--------|-----------|-------|
| **Vision MCP** | Screenshot → structured data | `ui_to_artifact`, `analyze_chart` |
| **Search MCP** | Web search | `webSearchPrime` |
| **Reader MCP** | Webpage → clean text | Browser reader mode via API |
| **Docling MCP** | PDF → structured Markdown | `uvx docling-mcp-server` |
| **Chrome DevTools MCP** | Browser diagnostics | Network/console logs, element inspection |
| **Crawl4AI MCP** | Web scraping | Async extraction with JS rendering |

### Agent-Observability Pipeline

```python
from langfuse.decorators import observe

@observe(name="agent_research_task")
def run_research(query: str):
    plan = planner_agent.run(f"Plan research for: {query}")
    data = worker_agent.run(f"Execute: {plan}")
    report = synthesizer_agent.run(f"Synthesize: {data}")
    return report
```
