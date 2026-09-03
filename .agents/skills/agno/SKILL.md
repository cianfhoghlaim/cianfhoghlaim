---
name: agno
description: Expert assistance for building AI agent systems with Agno (formerly PhiData) v2.0+. Use when users need multi-agent orchestration via the A2A Protocol, AgentOS production hosting, Z.ai GLM-4.6 via OpenAILike, agentic chunking, native Browserbase MCP integration, or Dagster+DLT+Agno KCG integration.
---

# Agno - AI Agent Framework

**Version:** >=2.0.0 | **Last Updated:** 2026-06

## Overview

Agno (formerly PhiData) is a high-performance framework for
building AI agents with a unique architecture:

- **Agent Orchestration** — single agents, multi-agent teams,
  and explicit workflows. Fully stateless design.
- **AgentOS** — a production-ready API for hosting agents,
  teams, and workflows. OpenAPI at
  `https://raw.githubusercontent.com/agno-agi/agno-docs/main/reference-api/openapi.json`.
- **AGUIInterface** — built-in AG-UI SSE adapter for
  CopilotKit integration.
- **A2A Protocol** — agent-to-agent communication (route /
  coordinate / collaborate team modes).
- **Tool Calling** — any Python function becomes a tool with
  auto-generated schema (signature + docstring).
- **Unified Media** — images, audio, video, files all
  handled the same way.
- **Memory Systems** — persistent agent memory across sessions
  via unified DB structure (Postgres / SQLite).
- **Knowledge Bases** — RAG with `async` insert / fetch;
  **agentic chunking** pattern.
- **Multi-Model Support** — OpenAI, Anthropic, Google, local
  models, **Z.ai GLM-4.6 via `OpenAILike`**.
- **Knowledge Graphs** — native support for graph-based
  knowledge representation.

**Documentation:** <https://docs.agno.com>

## When to Use This Skill

Activate when users need:

- "Build an AI agent with tools and memory"
- "Create a multi-agent team with route / coordinate / collaborate
  modes"
- "Host agents in production with AgentOS + OpenAPI"
- "Wire the AG-UI SSE protocol to a CopilotKit UI"
- "Use Z.ai GLM-4.6 (or any OpenAI-compatible model)"
- "Add agentic chunking to a knowledge base"
- "Integrate with Browserbase for browser automation"
- "Build the KCG 5-stage Dagster+DLT+Agno pipeline"

## KCG context (PRESERVED + extended)

- LLM backend: **LiteLLM gateway** (routes to OpenAI, Anthropic,
  Google, Z.ai, etc.)
- Tracing: **Langfuse** (project tracing)
- Memory: **Postgres** (unified DB structure) or **SQLite**
  for dev
- Knowledge base: **LanceDB** (BGE-M3 embeddings) or
  **PgVector** for Postgres-native
- Knowledge graph: **FalkorDB** (the KCG primary) or
  **Memgraph** for Cypher
- The KCG agent chain: **OCR → BAML → embedding → Graphiti
  → RAGAS** (5 SequentialAgents in a Dagster asset)
- Dagster wiring: `cianfhoghlaim-curriculum-extraction` runs the
  agent chain against NCCA PDFs
- DLT wiring: `@dlt.destination` writes the BAML output to
  DuckLake

## Domain-specific agent teams (KCG)

For the Cianfhoghlaim platform, the standard agent team is:

```python
from agno.team import Team
from agno.models.openai.like import OpenAILike

# KCG uses Z.ai GLM-4.6 for cost + speed, with OpenAI as fallback
model = OpenAILike(
    id="glm-4.6",
    base_url="https://api.z.ai/v1",
    api_key=os.environ["Z_AI_API_KEY"],
)

team = Team(
    name="curriculum_team",
    mode="coordinate",  # coordinator routes to specialists
    members=[
        curriculum_agent,   # NCCA + SEC + DES specialist
        translation_agent,  # EN → GA translation
        corpus_agent,       # leabharlann corpus specialist
        geospatial_agent,   # Gaeltacht + heritage site specialist
        statistics_agent,   # CSO + DES education statistics
        research_agent,     # Zotero + Gemini deep research
    ],
    model=kcg_model,
)
```

The 6 domain agents correspond to the 6 "Domain Agent" surfaces
in the `meaisínfhoghlaim-platform` spec.

## Core Agent

```python
from agno.agent import Agent
from agno.models.openai import OpenAIChat

agent = Agent(
    name="curriculum_extractor",
    model=OpenAIChat(id="gpt-4o-mini"),
    instructions=[
        "Extract the curriculum area, strands, and learning outcomes.",
        "Always return a CurriculumArea object, not free text.",
    ],
    tools=[pdf_extractor, schema_validator],
    markdown=True,
    # Memory + knowledge base
    db=postgres_db,
    knowledge=lancedb_kb,
    # Stream intermediate results
    stream=True,
)

response = agent.run("Extract from this NCCA Primary PDF...")
```

**Key parameters:**

- `name` — required; used in observability
- `model` — `OpenAIChat`, `AnthropicChat`, `Gemini`, `OpenAILike`
  (for any OpenAI-compatible API like Z.ai, vLLM, llama.cpp)
- `instructions` (list) — preferred over `system_prompt` (which
  is also supported for backward compatibility)
- `tools` (list) — Python functions, MCP servers, or
  pre-built tools
- `db` — session memory store
- `knowledge` — RAG knowledge base
- `markdown` — render output as markdown (for CopilotKit UI)
- `stream` — return `AsyncIterator` of intermediate events

## Tools (Python functions)

Any Python function with a type-annotated signature and
docstring becomes a tool:

```python
from agno.tools import tool

@tool
def get_weather(city: str) -> dict:
    """Get the current weather for a city.

    Args:
        city: The city name, e.g. "Dublin" or "Galway".

    Returns:
        A dict with 'temperature', 'conditions', 'humidity' keys.
    """
    response = fetch(f"https://api.weather.com/{city}")
    return response.json()

agent = Agent(tools=[get_weather])
```

The function's signature + docstring are auto-extracted into
the tool schema (name, description, parameters, types).

## Browserbase MCP Integration

```python
from agno.tools.mcp import MCPTools

browserbase = MCPTools(
    command="npx",
    args=["@browserbasehq/mcp-server-browserbase"],
    env={
        "BROWSERBASE_API_KEY": os.environ["BROWSERBASE_API_KEY"],
    },
)

agent = Agent(
    name="scraper",
    model=OpenAIChat(id="gpt-4o"),
    tools=[browserbase, stagehand],
    instructions=["Scrape the SEC EDGAR filings and extract the 10-K summary."],
)
```

The MCP server runs as a subprocess; Agno handles the JSON-RPC
transport.

## Z.ai GLM-4.6 via `OpenAILike`

```python
from agno.models.openai.like import OpenAILike

z_ai = OpenAILike(
    id="glm-4.6",
    base_url="https://api.z.ai/v1",
    api_key=os.environ["Z_AI_API_KEY"],
)

agent = Agent(name="kcg_translator", model=z_ai)
```

Z.ai's GLM-4.6 is a fast, cheap Chinese model that performs
well on translation + structured extraction. KCG uses it as
the cost-effective default, with OpenAI / Anthropic as
fallback for high-stakes calls.

## Multi-Agent Teams

Agno teams have 3 modes (all using the A2A Protocol internally
for inter-agent communication):

| Mode | When |
|:--|:--|
| `route` | Coordinator routes to ONE sub-agent based on the request |
| `coordinate` | Coordinator routes to multiple sub-agents and combines |
| `collaborate` | All sub-agents work on the task together, with shared state |

```python
from agno.team import Team

team = Team(
    name="multi_perspective",
    mode="coordinate",
    members=[linguistic_agent, cultural_agent, historical_agent],
    model=OpenAIChat(id="gpt-4o"),
    instructions=[
        "Coordinate the team to analyze this poem.",
        "Each member contributes their perspective.",
    ],
)

response = team.run("Analyze the poem 'An Cailín Rua' by Ó Rathaille.")
```

## A2A Protocol

For cross-agent / cross-vendor communication, the A2A Protocol
is built in:

```python
from agno.os.a2a import A2AInterface

# Expose this agent as an A2A server
a2a = A2AInterface(
    agent=my_agent,
    agent_card_url="https://my-agent.example.com/.well-known/agent.json",
)

# Or consume a remote A2A agent
from agno.os.a2a import A2AClient

client = A2AClient("https://remote-agent.example.com")
result = client.call("extract_curriculum", {"pdf_url": "..."})
```

## AgentOS (production hosting)

```python
from agno.os import AgentOS

agent_os = AgentOS(
    agents=[kcg_team, curriculum_agent, translation_agent],
    # The OpenAPI spec is auto-generated
)

# Serve via FastAPI
app = agent_os.get_app()
# Or via Uvicorn directly
agent_os.serve("agent_os:app", host="0.0.0.0", port=8000)
```

The OpenAPI spec is at
`https://raw.githubusercontent.com/agno-agi/agno-docs/main/reference-api/openapi.json`
— use it to generate client SDKs (Python, TS, Go, etc.).

## AG-UI Interface (CopilotKit SSE)

```python
from agno.os.agui import AGUIInterface

agui = AGUIInterface(agent=kcg_team)

# Mount under any FastAPI app
from fastapi import FastAPI
app = FastAPI()
app.mount("/agui", agui.app)
```

The CopilotKit frontend auto-detects the AG-UI protocol and
consumes the SSE stream. See `.agents/skills/ag-ui/SKILL.md` for
the full protocol.

## Agentic Chunking

The canonical pattern for adding LLM-aware chunking to a
knowledge base:

```python
from agno.knowledge.chunking import AgenticChunker

chunker = AgenticChunker(
    model=OpenAIChat(id="gpt-4o-mini"),
    # The LLM reads the document and decides how to split
    # (respects headers, sections, code blocks, etc.)
    max_chunk_size=2000,
)

agent = Agent(
    knowledge=lancedb_kb,
    knowledge_chunking=chunker,
)
```

`AgenticChunker` is better than fixed-size chunking for
documents with semantic structure (e.g. NCCA syllabi,
Zotero papers, leabharlann books).

## Hybrid Search SQL

For knowledge base queries, the canonical pattern is hybrid
(vector + full-text + RRF reranking) via SQL:

```python
from agno.knowledge.search import HybridSearch

search = HybridSearch(
    vector=lancedb_vector,
    full_text=tantivy_fts,
    reranker=RRFReranker(k=60),  # Reciprocal Rank Fusion
)

agent = Agent(knowledge_search=search)
```

Or use the SQL-level pattern:

```sql
SELECT filename, text,
    (1.0 - (embedding <=> $1)) AS vector_score,
    ts_rank(fts, plainto_tsquery('english', $2)) AS fts_score,
    (1.0 - (embedding <=> $1)) * 0.7 + ts_rank(fts, plainto_tsquery('english', $2)) * 0.3 AS combined_score
FROM chunks
ORDER BY combined_score DESC
LIMIT 10
```

## DynamicKnowledge (extending the KB at runtime)

```python
from agno.knowledge import DynamicKnowledge

# A knowledge base that can be updated at runtime
class CurriculumDynamicKnowledge(DynamicKnowledge):
    def update(self, source_path: str):
        """Re-index the source directory."""
        for pdf in Path(source_path).glob("**/*.pdf"):
            doc = self.load(pdf)
            self.add(doc)
```

## Memory and Context

```python
from agno.memory import PostgresMemory

memory = PostgresMemory(
    db_url="postgresql://user:pass@localhost:5432/agno",
    table_name="agent_memory",
)

agent = Agent(
    name="tutor",
    model=OpenAIChat(id="gpt-4o"),
    memory=memory,
    add_history_to_messages=True,  # include past messages in context
    num_history_messages=10,
)
```

For production, use Postgres. For dev, SQLite is fine.

## KCG integration: Dagster + DLT + Agno

The KCG 5-stage pipeline is a Dagster asset that orchestrates
5 Agno agents:

```python
# orchestration/defs/curriculum_assets.py
from dagster import asset, AssetExecutionContext
from agno.os import AgentOS
from cianfhoghlaim.agents.agno import (
    ocr_agent, baml_extractor, embedder, graphiti_agent, ragas_evaluator
)

@asset(group_name="curriculum")
def ireland_curriculum_extraction(context: AssetExecutionContext):
    """Run the 5-stage KCG agent chain against an NCCA PDF."""
    pipeline = AgentOS(agents=[
        ocr_agent, baml_extractor, embedder, graphiti_agent, ragas_evaluator,
    ])
    result = pipeline.run_agent("ocr_to_kg_pipeline", {
        "pdf_path": "stedding/ingest_queue/ncca/primary_math_2024.pdf",
    })
    return result
```

The asset writes to DuckLake via a custom `@dlt.destination`.

## GitHub repo analyzer example

```python
from agno.tools.github import GitHubTools

agent = Agent(
    name="github_analyzer",
    model=OpenAIChat(id="gpt-4o"),
    tools=[GitHubTools(token=os.environ["GITHUB_TOKEN"])],
    instructions=[
        "Analyze the GitHub repository.",
        "Return a summary of the README, the top 5 files by commit count, "
        "and any open issues with 'help wanted' label.",
    ],
)

result = agent.run("https://github.com/agno-agi/agno")
```

## Best practices

1. **Use `OpenAILike` for any OpenAI-compatible API** (Z.ai,
   vLLM, llama.cpp, Ollama) — `OpenAIChat` is OpenAI-specific
2. **Use `team.mode="coordinate"` for multi-perspective tasks**
3. **Use `AgentOS` for production hosting** — never
   `uvicorn agent:app` directly
4. **Use `AGUIInterface` for CopilotKit UI integration** —
   auto-handles SSE + event protocol
5. **Use `AgenticChunker` for documents with semantic
   structure** — fixed-size chunking is a last resort
6. **Use `HybridSearch` with `RRFReranker`** for knowledge
   base queries — pure vector search misses keyword matches
7. **Always add memory to long-running agents** — stateless
   agents forget everything between turns
8. **Stream intermediate events to the UI** — don't wait for
   the full response

## Common issues

### Agent not using tools
- Verify the function has a docstring
- Verify the parameters have type annotations
- Check the model is multi-modal-capable (some cheap models
  are text-only)

### Memory not persisting
- Verify the DB connection
- Check `add_history_to_messages=True`
- Ensure `session_id` is consistent across calls

### Knowledge base empty
- Run `agent.knowledge.load()` first
- Check vector DB connection
- Verify documents are in the correct path

## Resources

- **Documentation:** <https://docs.agno.com>
- **OpenAPI spec:**
  <https://raw.githubusercontent.com/agno-agi/agno-docs/main/reference-api/openapi.json>
- **GitHub:** <https://github.com/agno-agi/agno>
- **Examples:** <https://github.com/agno-agi/agno/tree/main/cookbook>
- **Z.ai GLM-4.6:** <https://docs.z.ai/guides/llm/glm-4.6>
- **A2A Protocol:** <https://a2a.dev/>
- **AG-UI Protocol:** <https://ag-ui.com/>
- **KCG Dagster asset:** `orchestration/defs/curriculum_assets.py`
- **Related skills:** `.agents/skills/google-adk/`,
  `.agents/skills/pydantic-ai/`, `.agents/skills/litellm/`,
  `.agents/skills/langfuse/`, `.agents/skills/cognee/`,
  `.agents/skills/falkordb/`

## Framework comparison (when to use Agno vs Google ADK / Pydantic AI)

| Use case | Agno | Google ADK | Pydantic AI |
|:--|:--|:--|:--|
| Multi-agent teams (route / coordinate / collaborate) | ✅ first-class | ✅ | ⚠️ via DBOS |
| AgentOS production hosting | ✅ | ✅ Agent Engine | ⚠️ self-host |
| Z.ai GLM-4.6 (cost-effective) | ✅ `OpenAILike` | ⚠️ | ✅ `OpenAICompatibleModel` |
| A2A Protocol | ✅ built-in | ✅ built-in | ⚠️ via adapter |
| AG-UI SSE | ✅ `AGUIInterface` | ⚠️ via adapter | ✅ first-class |
| Tools (any Python function) | ✅ | ✅ | ✅ |
| Knowledge bases (RAG) | ✅ | ⚠️ via Vertex AI | ✅ via `pydantic_ai_agents` |
| Memory (Postgres) | ✅ | ✅ via Memory Bank | ✅ |
| Knowledge graphs (FalkorDB) | ✅ | ⚠️ | ⚠️ |
| Type-safe I/O (Pydantic) | ✅ | ✅ | ✅ first-class |
| MCP server | ✅ via adapter | ✅ built-in | ✅ via adapter |
| Modal H100 burst | ✅ | ✅ | ✅ |

**Rule of thumb**: use **Agno** for multi-agent teams with
Z.ai GLM-4.6 (cost-effective, the KCG default); use
**Google ADK** for Gemini-heavy workflows (Live API, A2A,
Agent Engine); use **Pydantic AI** for type-safe I/O with
Pydantic models (the KCG standard).
