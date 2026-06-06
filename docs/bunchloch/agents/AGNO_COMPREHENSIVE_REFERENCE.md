# Agno Framework: Comprehensive Architecture Reference

## Merged From
- `agno-architecture-guide.md`
- `agno_architecure_z_ai.md`
- `agno-openapi-specification-research.md`
- `agno/KCG_SUMMARY.md`
- `agno/agno/README.md`
- `agno/agno/SKILL_CONTEXT.md`
- `agno/agno/CONTRIBUTING.md`
- `agno/typescript/README.md`
- `agno/python/examples/README.md`
- `agno/github_repo_analyzer/README.md`

---

## Part I: Agno Framework Fundamentals

### 1.1 What is Agno?

Agno (formerly PhiData) is an open-source Python framework for building multi-agent AI systems with tool calling, knowledge bases, and persistent memory. It enables agent teams, sequential/parallel workflows, and hierarchical orchestration.

**Key Characteristics:**
- Open-source, pure Python design
- Agent instantiation in ~3 microseconds (orders of magnitude faster than graph-based alternatives)
- Knowledge base integration via vector search (LanceDB, Qdrant, pgvector)
- Persistent agent memory across multi-step workflows
- Multi-model support via LiteLLM gateway
- A2A (Agent-to-Agent) protocol for cross-agent communication
- AgentOS for serving agents as APIs

### 1.2 Why Agno for Education?

The project uses Agno for coordinating specialized educational agents:
- **Curriculum Agent:** Irish education policy analysis
- **Mathematics Agent:** Prerequisite validation
- **Irish-Language Agent:** Bilingual content quality
- **Study Asset Agent:** Educational image generation

Each agent gets domain-specific retrieval via Agno's knowledge base integration.

---

## Part II: Multi-Agent System Architecture with Dagster + DLT

### 2.1 Architecture Overview

The architecture leverages Agno in combination with BAML to enforce structured prompt-response formats. The data processing stack unifies batch and streaming workflows using DuckLake (DuckDB lakehouse) for batch storage and optionally RisingWave for streaming, with Ibis providing a common interface. Processed data (embeddings, facts, metrics) are fed into CocoIndex for vector indexing and Cognee for graph/relational knowledge storage, built on PostgreSQL, LanceDB, and Memgraph.

### 2.2 Domain-Specific Agent Teams

**Team 1: Code & Documentation Analysis**
- Responsibility: Analyzing software repositories — summarizing code structure, evaluating documentation
- Pipeline: DLT ingestion → DuckLake storage → CocoIndex indexing → Agno agents → Cognee

**Team 2: Sentiment Analysis**
- Responsibility: Processing user feedback, reviews, and social media
- Pipeline: Crawl4AI ingestion → DuckLake → Agno sentiment agents → Cognee

**Team 3: Financial Analytics**
- Responsibility: Market data analysis, report generation
- Pipeline: Financial data ingestion → vector indexing → Agno analysis agents → structured reports

### 2.3 Dagster Pipeline Orchestration

Dagster orchestrates pipelines for each team. Each pipeline:
1. Ingests data (via DLT or Crawl4AI)
2. Indexes via CocoIndex with memoized transformations
3. Invokes specialized Agno agents with BAML-defined structured outputs
4. Feeds into Cognee's unified knowledge base

This allows teams to operate independently while contributing to a common semantic index and knowledge graph.

---

## Part III: A2A Protocol — Agent-to-Agent Communication

### 3.1 Protocol Fundamentals

Agno's A2A protocol is built on **JSON-RPC 2.0** over HTTP with Server-Sent Events for streaming. Agents discover each other via Agent Cards at `/.well-known/agent.json`.

**Core Message Structure:**
```json
{
  "jsonrpc": "2.0",
  "id": "req-001",
  "method": "message/send",
  "params": {
    "message": {
      "messageId": "msg-123",
      "role": "user",
      "parts": [
        {"text": "Analyze this UI screenshot"},
        {"file": {"fileWithUri": "https://...", "mediaType": "image/png"}}
      ]
    }
  }
}
```

The protocol supports **seven task states**: submitted, working, completed, failed, cancelled, rejected, input-required.

**Three communication patterns:**
- Synchronous request/response
- SSE streaming (critical for progressive knowledge graph building)
- Webhook-based push notifications

**Agent Card Registration:**
```json
{
  "name": "Vision Analysis Agent",
  "skills": [
    {"id": "ui-analysis", "description": "Extract UI components from screenshots"},
    {"id": "pattern-detection", "description": "Identify design patterns and hierarchies"}
  ],
  "defaultInputModes": ["image/png", "application/json"],
  "defaultOutputModes": ["application/json"]
}
```

### 3.2 Team Modes

Agno supports three team modes:
- **Route:** Single agent handles the request (simple queries)
- **Coordinate:** Team leader orchestrates agents sequentially based on task requirements
- **Collaborate:** Parallel execution where multiple agents work simultaneously

The **coordinate** mode is used for UI learning pipelines because ordered data flow is required.

---

## Part IV: The Agentic UI Learning Pipeline

### 4.1 Specialized Agent Architecture

| Agent | Role | Tools | Outputs |
|-------|------|-------|---------|
| Scraper Agent | Browser control, navigation, screenshot capture | Browserbase SDK, Stagehand | Screenshots, HTML, DOM structure |
| Vision Agent | Screenshot analysis, component extraction | Z.AI GLM MCP tools | Structured UI data, BAML-typed components |
| Memory Agent | Knowledge graph management, ontology building | Cognee APIs | Graph updates, pattern associations |
| UI Generator Agent | Prototype recreation from learned patterns | AG-UI, component library | Generative UI specifications |

### 4.2 Team Configuration

```python
from agno.agent import Agent
from agno.team.team import Team
from agno.models.openai import OpenAIChat
from agno.tools.mcp import MCPTools

# Scraper Agent with Browserbase
scraper_agent = Agent(
    name="Scraper Agent",
    role="Capture screenshots and extract DOM from target URLs",
    model=OpenAIChat(id="gpt-4.1"),
    tools=[MCPTools(
        transport="stdio",
        command="npx",
        args=["@browserbasehq/mcp-server-browserbase"],
    )]
)

# Vision Agent with Z.ai MCP
vision_agent = Agent(
    name="Vision Agent",
    role="Analyze screenshots for UI components and design tokens",
    model=OpenAIChat(id="gpt-4o"),
    tools=[MCPTools(
        command="npx",
        args=["-y", "@z_ai/mcp-server"],
        env={"Z_AI_API_KEY": "...", "Z_AI_MODE": "ZAI"}
    )]
)

# Team orchestration
ui_learning_team = Team(
    name="UI Learning Pipeline",
    mode="coordinate",
    members=[scraper_agent, vision_agent, memory_agent, ui_generator_agent],
    model=OpenAIChat(id="gpt-4.1"),
    instructions="Coordinate the end-to-end UI learning pipeline..."
)
```

### 4.3 Custom Model Integration (Z.ai GLM-4.6)

```python
from agno.models.openai.like import OpenAILike

zhipu_text_model = OpenAILike(
    id="glm-4.6",
    api_key=os.getenv("ZHIPU_API_KEY"),
    base_url="https://open.bigmodel.cn/api/paas/v4/",
    max_tokens=4096,
    temperature=0.1
)

chief_examiner = Agent(
    name="ChiefExaminer",
    role="Orchestrator of the digitization pipeline",
    model=zhipu_text_model,
    monitoring=True
)
```

---

## Part V: Agno AgentOS — OpenAPI and API Deployment

### 5.1 AgentOS Overview

Agno AgentOS provides a FastAPI-compatible server for deploying agents as APIs. The AGUI interface wraps agents in standard protocol endpoints (POST /agui, SSE streams for events).

```python
from agno.agent import Agent
from agno.os import AgentOS
from agno.os.interfaces.agui import AGUI

agent = Agent(name="My Agent", model=OpenAIChat(id="gpt-4o"))

agent_os = AgentOS(
    agents=[agent],
    interfaces=[AGUI(agent=agent)]
)

app = agent_os.get_app()
agent_os.serve(app="app:app", port=7777, reload=True)
```

### 5.2 Official OpenAPI Specification

**Primary Location:** `https://raw.githubusercontent.com/agno-agi/agno-docs/main/reference-api/openapi.json`

**Version:** 1.0.0
**Title:** AI Agent Operating System API
**Local:** `http://localhost:7777/openapi.json` when running locally

**API Capabilities:**
1. **Agent Management:** Create/execute individual agents with multimodal support (text, images, audio, video, documents)
2. **Team Collaboration:** Coordinate teams of agents, task transfer between members, shared knowledge and memory
3. **Workflow Orchestration:** Multi-step workflows, sequential or parallel execution, input validation

---

## Part VI: Agentic Chunking and Knowledge Bases

### 6.1 Agentic Chunking

Agno addresses the "Fixed Size Chunking" problem with agentic chunking that uses an LLM to identify semantic boundaries.

**Workflow:**
1. Ingestion: Load document (e.g., exam paper PDF)
2. Semantic Scanning: LLM (e.g., GPT-4o-mini) reads text stream
3. Boundary Detection: Identifies start/end of distinct Assessment Units
4. Indexing: Creates chunks that correspond 1:1 with assessment units

This ensures when a student asks "Help me with Question 3," the Agent retrieves the entirety of Question 3 as a single coherent context unit.

### 6.2 Knowledge Base Configuration

```python
from agno.knowledge import Knowledge
from agno.vectordb.pgvector import PgVector

class DynamicKnowledge(Knowledge):
    def add_dynamic_document(self, pydantic_obj):
        content = pydantic_obj.question_text
        metadata = pydantic_obj.model_dump(exclude={"question_text"})
        self.vector_db.upsert(documents=[...])
```

### 6.3 Hybrid Search

Agno supports hybrid search — keyword filter on metadata BEFORE semantic vector search. This drastically improves precision compared to pure vector similarity.

```sql
SELECT * FROM exam_questions
WHERE metadata->>'topic' = 'Kinematics'
AND (metadata->>'AO2')::int > 0
ORDER BY embedding <=> query_embedding
LIMIT 1
```

---

## Part VII: GitHub Repo Analyzer Example

A complete example demonstrating Agno's GitHub integration for code analysis:

```python
from agno.agent import Agent
from agno.tools.github import GitHubTools

analyzer = Agent(
    name="GitHub Analyzer",
    tools=[GitHubTools()],
    instructions="Analyze GitHub repositories and provide structured summaries."
)

response = analyzer.run("Analyze https://github.com/agno-agi/agno")
```

---

## Part VIII: Key Commands and Configurations

```bash
# Install
pip install agno openai

# Run AgentOS
python app.py  # Serves at http://localhost:7777

# Start Dagster with Agno agents
dagster dev -m sruth.oideachas

# MCP Toolbox integration
pip install toolbox-core
```

### Environment Configuration
```env
OPENAI_API_KEY=sk-...
AGNO_API_KEY=...
BROWSERBASE_API_KEY=bb_...
Z_AI_API_KEY=...
GRAPH_DB_URL=localhost
```

---

## Resources

- GitHub: https://github.com/agno-agi/agno
- Docs: https://docs.agno.com
- OpenAPI Spec: https://raw.githubusercontent.com/agno-agi/agno-docs/main/reference-api/openapi.json
- Agent Skill: `.agents/skills/agno/SKILL.md`
