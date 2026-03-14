---
name: agno
description: Expert assistance for building AI agent systems with Agno (formerly PhiData). Use when users need multi-agent orchestration, agent teams, tool-calling agents, or agent workflows with memory and knowledge bases.
---

# Agno - AI Agent Framework

**Version:** 1.x | **Last Updated:** 2025-01

## Overview

Agno (formerly PhiData) is a high-performance framework for building AI agents:

- **Agent Orchestration**: Build single agents and multi-agent teams
- **Tool Calling**: Integrate tools and function calling seamlessly
- **Memory Systems**: Persistent agent memory across sessions
- **Knowledge Bases**: RAG-style knowledge integration
- **Multi-Model Support**: Works with OpenAI, Anthropic, Google, local models

**Documentation**: https://docs.agno.com

## When to Use This Skill

Activate when users need:

- "Build an AI agent with tools"
- "Create a multi-agent team"
- "Add memory to an agent"
- "Build an agent with knowledge base"
- "Orchestrate agent workflows"

## Core Concepts

### 1. Basic Agent

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

### 2. Agents with Tools

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

### 3. Custom Tools

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
        limit: Maximum number of results
    """
    return [{"id": 1, "name": "Result 1"}]

agent = Agent(
    model=OpenAIChat(id="gpt-4o"),
    tools=[get_weather, search_database],
    show_tool_calls=True
)

agent.print_response("What's the weather in San Francisco?")
```

### 4. Agent Teams

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

### 5. Agent with Memory

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

### 6. Knowledge Bases

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

### 7. Structured Outputs

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

### 8. Streaming Responses

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

## Common Patterns

### Research Agent

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

### Data Analysis Agent

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

### SQL Agent

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

### Workflow Agent

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

## Model Providers

### OpenAI
```python
from agno.models.openai import OpenAIChat

model = OpenAIChat(id="gpt-4o")
model = OpenAIChat(id="gpt-4o-mini", temperature=0.7)
```

### Anthropic
```python
from agno.models.anthropic import Claude

model = Claude(id="claude-sonnet-4-20250514")
```

### Google
```python
from agno.models.google import Gemini

model = Gemini(id="gemini-1.5-pro")
```

### Ollama (Local)
```python
from agno.models.ollama import Ollama

model = Ollama(id="llama3.2")
```

### Azure OpenAI
```python
from agno.models.azure import AzureOpenAI

model = AzureOpenAI(
    id="gpt-4",
    azure_endpoint="https://your-resource.openai.azure.com",
    azure_deployment="your-deployment"
)
```

## Built-in Tools

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

## Vector Database Support

- **LanceDB**: Local/cloud vector storage
- **PgVector**: PostgreSQL extension
- **Qdrant**: Distributed vector DB
- **Pinecone**: Managed vector service
- **Weaviate**: Open-source vector search

## Storage Backends

- **PostgreSQL**: Production-ready persistence
- **SQLite**: Local development
- **Redis**: High-performance caching
- **DynamoDB**: AWS serverless

## Best Practices

1. **Clear Instructions**: Provide specific, actionable instructions
2. **Tool Selection**: Only include tools the agent needs
3. **Memory Management**: Use session IDs for multi-turn conversations
4. **Error Handling**: Implement retries for API failures
5. **Structured Outputs**: Use Pydantic models for predictable responses
6. **Team Coordination**: Define clear roles for multi-agent teams

## Troubleshooting

### Agent Not Using Tools
- Verify tool is in the `tools` list
- Check tool docstring is descriptive
- Enable `show_tool_calls=True` for debugging

### Memory Issues
- Verify storage connection
- Check session_id is consistent
- Ensure `add_history_to_messages=True`

### Knowledge Base Empty
- Run `agent.knowledge.load()` first
- Check vector DB connection
- Verify documents are in correct path

## Resources

- **Documentation**: https://docs.agno.com
- **GitHub**: https://github.com/agno-agi/agno
- **Examples**: https://github.com/agno-agi/agno/tree/main/cookbook
