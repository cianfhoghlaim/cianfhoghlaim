---
title: 'Agno Framework — Comprehensive Reference & Skill Card'
domain: 'agents'
status: 'stable'
description: 'Complete Agno framework reference — fundamentals, multi-agent architecture with Dagster + DLT, A2A protocol, AgentOS deployment, agentic chunking, GitHub repo analyzer, and skill-card (Core Concepts, Tools, Memory, Knowledge Bases, Patterns, Model Providers, Built-in Tools, Best Practices).'
read_when:
  - building AI agents
  - integrating Agno with our stack
  - designing multi-agent teams
  - working with A2A protocol
  - deploying agents via AgentOS
updated: 2026-06-13
merged_from:
  - docs/03-agents/AGNO_COMPREHENSIVE_REFERENCE.md
  - docs/03-agents/agno.md
truth: sole
ccc_query_hints:
  - agno framework multi-agent
  - agno agentos openapi
  - agno a2a protocol
  - agno dagster dlt integration
  - agno memory knowledge base
---

# Agno Framework — Comprehensive Reference & Skill Card

> **Merged from 2 canonical sources**: `AGNO_COMPREHENSIVE_REFERENCE.md` (architectural deep-dive, 8 parts) + `agno.md` (skill card with code patterns, 465 lines). The originals are now `.superseded`. Three stub files (`agno-architecture-guide.md`, `agno-openapi-specification-research.md`, `agno_architecure_z_ai.md`) had only "MERGED INTO" notices and have been deleted (no content lost).

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

### 6.4 Knowledge Bases (skill card)

```python
from agno import Agent
from agno.knowledge.pdf import PDFKnowledgeBase
from agno.knowledge.url import URLKnowledgeBase
from agno.vectordb.lancedb import LanceDb

# PDF Knowledge Base
pdf_kb = PDFKnowledgeBase(
    path="documents/",
    vector_db=LanceDb(
        table_name="pdf_docs",
        uri="./lancedb"
    )
)

# URL Knowledge Base
url_kb = URLKnowledgeBase(
    urls=["https://docs.example.com"],
    vector_db=LanceDb(table_name="url_docs")
)

# Create agent with knowledge
agent = Agent(
    model=OpenAIChat(id="gpt-4o"),
    knowledge=pdf_kb,
    search_knowledge=True,
    add_references_to_prompt=True
)

# Load knowledge base (first time)
agent.knowledge.load()

# Query
agent.print_response("What does the documentation say about authentication?")
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

## Part VIII: Skill Card — Core Concepts, Tools, Patterns

### Overview (skill card)

Agno (formerly PhiData) is a high-performance framework for building AI agents:
- **Agent Orchestration**: Build single agents and multi-agent teams
- **Tool Calling**: Integrate tools and function calling seamlessly
- **Memory Systems**: Persistent agent memory across sessions
- **Knowledge Bases**: RAG-style knowledge integration
- **Multi-Model Support**: Works with OpenAI, Anthropic, Google, local models

**Documentation**: https://docs.agno.com

### When to Use This Skill

Activate when users need:
- "Build an AI agent with tools"
- "Create a multi-agent team"
- "Add memory to an agent"
- "Build an agent with knowledge base"
- "Orchestrate agent workflows"

### Core Concepts

#### 1. Basic Agent

```python
from agno import Agent
from agno.models.openai import OpenAIChat

agent = Agent(
    model=OpenAIChat(id="gpt-4o-mini"),
    description="A helpful assistant",
    instructions=["Be concise", "Be helpful"],
    markdown=True
)

# Run agent
response = agent.run("What is the capital of France?")
print(response.content)

# Print full response
agent.print_response("What is machine learning?")
```

#### 2. Agents with Tools

```python
from agno import Agent
from agno.tools.duckduckgo import DuckDuckGo
from agno.tools.calculator import Calculator

agent = Agent(
    model=OpenAIChat(id="gpt-4o"),
    tools=[DuckDuckGo(), Calculator()],
    show_tool_calls=True,
    markdown=True
)

agent.print_response("Search for the latest AI news and calculate 15% of 250")
```

#### 3. Custom Tools

```python
from agno import Agent
from agno.tools import tool

@tool
def get_weather(city: str) -> str:
    """Get the current weather for a city.

    Args:
        city: The city name to get weather for
    """
    # Your implementation
    return f"Weather in {city}: 72°F, Sunny"

@tool
def search_database(query: str, limit: int = 10) -> list:
    """Search the database for relevant records.

    Args:
        query: Search query
        limit: Maximum number of records to return
    """
    return [{"id": 1, "name": "Result 1"}]

agent = Agent(
    model=OpenAIChat(id="gpt-4o"),
    tools=[get_weather, search_database],
    show_tool_calls=True
)

agent.print_response("What's the weather in San Francisco?")
```

#### 4. Agent Teams

```python
from agno import Agent, Team
from agno.models.openai import OpenAIChat
from agno.tools.duckduckgo import DuckDuckGo
from agno.tools.yfinance import YFinanceTools

# Define specialized agents
web_researcher = Agent(
    name="Web Researcher",
    role="Search the web for information",
    model=OpenAIChat(id="gpt-4o-mini"),
    tools=[DuckDuckGo()],
    instructions=["Search for accurate, recent information"]
)

financial_analyst = Agent(
    name="Financial Analyst",
    role="Analyze financial data and stocks",
    model=OpenAIChat(id="gpt-4o"),
    tools=[YFinanceTools(stock_price=True, analyst_recommendations=True)],
    instructions=["Provide detailed financial analysis"]
)

# Create team
research_team = Team(
    name="Research Team",
    agents=[web_researcher, financial_analyst],
    instructions=["Collaborate to answer complex questions"],
    show_tool_calls=True
)

# Run team
research_team.print_response("What are the latest developments at Tesla and its stock outlook?")
```

#### 5. Agent with Memory

```python
from agno import Agent
from agno.models.openai import OpenAIChat
from agno.memory import AgentMemory
from agno.storage.postgres import PostgresStorage

# Configure memory storage
storage = PostgresStorage(
    db_url="postgresql://user:pass@localhost/agno",
    table_name="agent_sessions"
)

# Create agent with memory
agent = Agent(
    model=OpenAIChat(id="gpt-4o"),
    memory=AgentMemory(
        db=storage,
        create_user_memories=True,
        create_session_summary=True
    ),
    add_history_to_messages=True,
    num_history_responses=3
)

# Conversations persist across sessions
agent.print_response("My name is Alice", session_id="user-123")
agent.print_response("What's my name?", session_id="user-123")  # Remembers "Alice"
```

#### 6. Structured Outputs

```python
from agno import Agent
from agno.models.openai import OpenAIChat
from pydantic import BaseModel, Field
from typing import List

class MovieScript(BaseModel):
    title: str = Field(..., description="Movie title")
    setting: str = Field(..., description="Where the movie takes place")
    characters: List[str] = Field(..., description="Main characters")
    plot_summary: str = Field(..., description="Brief plot summary")

agent = Agent(
    model=OpenAIChat(id="gpt-4o"),
    description="A creative screenwriter",
    response_model=MovieScript
)

response = agent.run("Write a sci-fi movie about AI")
script: MovieScript = response.content
print(f"Title: {script.title}")
print(f"Setting: {script.setting}")
```

#### 7. Streaming Responses

```python
from agno import Agent
from agno.models.openai import OpenAIChat

agent = Agent(
    model=OpenAIChat(id="gpt-4o"),
    markdown=True
)

# Stream response
for chunk in agent.run("Write a story about a robot", stream=True):
    print(chunk.content, end="", flush=True)
```

### Common Patterns

#### Research Agent

```python
from agno import Agent
from agno.tools.duckduckgo import DuckDuckGo
from agno.tools.newspaper import Newspaper4k

research_agent = Agent(
    name="Research Agent",
    model=OpenAIChat(id="gpt-4o"),
    tools=[DuckDuckGo(), Newspaper4k()],
    description="Research assistant that searches and summarizes information",
    instructions=[
        "Search for relevant information",
        "Read and extract key points from articles",
        "Provide well-cited summaries"
    ],
    show_tool_calls=True,
    markdown=True
)

research_agent.print_response("Research the latest developments in quantum computing")
```

#### Data Analysis Agent

```python
from agno import Agent
from agno.tools.python import PythonTools

data_agent = Agent(
    name="Data Analyst",
    model=OpenAIChat(id="gpt-4o"),
    tools=[PythonTools()],
    description="Analyze data and generate visualizations",
    instructions=[
        "Use pandas for data manipulation",
        "Create clear visualizations with matplotlib",
        "Explain your analysis step by step"
    ],
    show_tool_calls=True
)

data_agent.print_response("Load data.csv and create a summary with visualizations")
```

#### SQL Agent

```python
from agno import Agent
from agno.tools.postgres import PostgresTools

sql_agent = Agent(
    name="SQL Agent",
    model=OpenAIChat(id="gpt-4o"),
    tools=[PostgresTools(
        db_url="postgresql://user:pass@localhost/mydb"
    )],
    description="Query databases and analyze results",
    instructions=[
        "Write efficient SQL queries",
        "Explain query results clearly"
    ]
)

sql_agent.print_response("Show me the top 10 customers by revenue")
```

#### Workflow Agent

```python
from agno import Agent, Workflow
from agno.tasks import Task

# Define tasks
research_task = Task(
    name="Research",
    description="Research the topic thoroughly",
    agent=research_agent
)

analyze_task = Task(
    name="Analyze",
    description="Analyze the research findings",
    agent=analyst_agent,
    depends_on=[research_task]
)

report_task = Task(
    name="Report",
    description="Generate final report",
    agent=writer_agent,
    depends_on=[analyze_task]
)

# Create workflow
workflow = Workflow(
    name="Research Workflow",
    tasks=[research_task, analyze_task, report_task]
)

# Run workflow
result = workflow.run("Analyze the impact of AI on healthcare")
```

### Model Providers

#### OpenAI
```python
from agno.models.openai import OpenAIChat

model = OpenAIChat(id="gpt-4o")
model = OpenAIChat(id="gpt-4o-mini", temperature=0.7)
```

#### Anthropic
```python
from agno.models.anthropic import Claude

model = Claude(id="claude-sonnet-4-20250514")
```

#### Google
```python
from agno.models.google import Gemini

model = Gemini(id="gemini-1.5-pro")
```

#### Ollama (Local)
```python
from agno.models.ollama import Ollama

model = Ollama(id="llama3.2")
```

#### Azure OpenAI
```python
from agno.models.azure import AzureOpenAI

model = AzureOpenAI(
    id="gpt-4",
    azure_endpoint="https://your-resource.openai.azure.com",
    azure_deployment="your-deployment"
)
```

### Built-in Tools

| Tool | Purpose |
|------|---------|
| `DuckDuckGo` | Web search |
| `Calculator` | Mathematical calculations |
| `YFinanceTools` | Stock and financial data |
| `PythonTools` | Execute Python code |
| `PostgresTools` | SQL database queries |
| `Newspaper4k` | Article extraction |
| `ArxivTools` | Academic paper search |
| `FileTools` | File operations |
| `ShellTools` | System commands |

### Vector Database Support

- **LanceDB**: Local/cloud vector storage
- **PgVector**: PostgreSQL extension
- **Qdrant**: Distributed vector DB
- **Pinecone**: Managed vector service
- **Weaviate**: Open-source vector search

### Storage Backends

- **PostgreSQL**: Production-ready persistence
- **SQLite**: Local development
- **Redis**: High-performance caching
- **DynamoDB**: AWS serverless

### Best Practices

1. **Clear Instructions**: Provide specific, actionable instructions
2. **Tool Selection**: Only include tools the agent needs
3. **Memory Management**: Use session IDs for multi-turn conversations
4. **Error Handling**: Implement retries for API failures
5. **Structured Outputs**: Use Pydantic models for predictable responses
6. **Team Coordination**: Define clear roles for multi-agent teams

### Troubleshooting

#### Agent Not Using Tools
- Verify tool is in the `tools` list
- Check tool docstring is descriptive
- Enable `show_tool_calls=True` for debugging

#### Memory Issues
- Verify storage connection
- Check session_id is consistent
- Ensure `add_history_to_messages=True`

#### Knowledge Base Empty
- Run `agent.knowledge.load()` first
- Check vector DB connection
- Verify documents are in correct path

---

## Part IX: Key Commands and Configurations

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
- Examples: https://github.com/agno-agi/agno/tree/main/cookbook
