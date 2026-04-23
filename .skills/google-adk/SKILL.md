---
name: google-adk
description: Expert assistance for building AI agents with Google's Agent Development Kit. Use when users need multi-agent coordination, agent frameworks, or Google AI agent development.
---

# Google ADK - Agent Development Kit

**Version:** >=0.1.0 | **Last Updated:** 2025-04

## Overview

Google's Agent Development Kit (ADK) is a framework for building sophisticated AI agents:

- **Multi-Agent Coordination**: Build teams of collaborating agents
- **Agent Framework**: Structured patterns for agent development
- **Google AI Integration**: Seamless integration with Google's AI services
- **Scalable Architecture**: Production-ready agent orchestration

**Documentation**: https://cloud.google.com/agent-development-kit

## When to Use This Skill

Activate when users need:

- "Build a multi-agent system"
- "Create Google AI agents"
- "Coordinate multiple agents"
- "Implement agent workflows with Google services"

## Core Concepts

### 1. Basic Agent Setup

```python
from google.adk import Agent, AgentConfig

# Configure agent
config = AgentConfig(
    model="gemini-2.0-flash-exp",
    temperature=0.7,
    max_tokens=2048
)

# Create agent
agent = Agent(
    name="research_agent",
    config=config,
    instructions="You are a research assistant that helps find and summarize information."
)

# Run agent
response = agent.run("What are the latest developments in quantum computing?")
print(response.content)
```

### 2. Multi-Agent Coordination

```python
from google.adk import Agent, AgentOrchestrator

# Define specialized agents
researcher = Agent(
    name="researcher",
    instructions="Gather information from web search and knowledge bases."
)

analyst = Agent(
    name="analyst",
    instructions="Analyze research findings and extract key insights."
)

writer = Agent(
    name="writer",
    instructions="Compose clear summaries from analyzed data."
)

# Create orchestrator
orchestrator = AgentOrchestrator(
    agents=[researcher, analyst, writer],
    workflow="sequential"  # Options: sequential, parallel, hierarchical
)

# Run coordinated task
result = orchestrator.run("Research and summarize recent AI safety research")
```

### 3. Tool Integration

```python
from google.adk import Agent, Tool
from google.adk.tools import WebSearchTool, CalculatorTool

# Create custom tool
@Tool
def database_query(query: str) -> str:
    """Query the internal database.

    Args:
        query: SQL query to execute
    """
    # Implementation
    return results

# Configure agent with tools
agent = Agent(
    name="data_agent",
    tools=[
        WebSearchTool(),
        CalculatorTool(),
        database_query
    ],
    instructions="Use tools to gather and analyze data."
)
```

### 4. Memory and Context

```python
from google.adk import Agent, MemoryConfig

# Configure persistent memory
memory_config = MemoryConfig(
    type="vector_store",  # Options: vector_store, key_value, hybrid
    max_context=10000,
    retrieval_strategy="semantic"
)

agent = Agent(
    name="memory_agent",
    memory_config=memory_config,
    instructions="Remember important information from conversations."
)

# Agent maintains context across interactions
response1 = agent.run("My name is Alice and I prefer Python.")
response2 = agent.run("What programming language do I prefer?")
# Agent recalls: "You prefer Python."
```

## Best Practices

### Agent Design

1. **Clear Instructions**: Provide specific, actionable instructions
2. **Single Responsibility**: Each agent should have a focused purpose
3. **Tool Selection**: Only include relevant tools to reduce complexity

### Multi-Agent Patterns

1. **Sequential**: For linear workflows where output flows to next agent
2. **Parallel**: For independent tasks that can run simultaneously
3. **Hierarchical**: For complex workflows with supervisor agents

### Performance

1. **Batch Operations**: Process multiple items together when possible
2. **Caching**: Cache frequently accessed information
3. **Async Execution**: Use async for I/O-bound operations

## Installation

```bash
pip install google-adk
```

## Configuration

```python
import os
from google.adk import ADKConfig

# Configure API keys
os.environ["GOOGLE_API_KEY"] = "your-api-key"

# Global configuration
ADKConfig.set_default_model("gemini-2.0-flash-exp")
ADKConfig.set_default_temperature(0.7)
```

## Project Integration

### Use Cases

| Scenario | Pattern |
|----------|---------|
| Research Assistant | Multi-agent sequential workflow |
| Customer Support | Single agent with knowledge base |
| Data Analysis | Agent with tools and memory |
| Content Creation | Parallel agents for different aspects |

### Related Skills

- [`agno`](.skills/agno/SKILL.md) - Alternative agent framework
- [`cognee`](.skills/cognee/SKILL.md) - Knowledge graph memory
- [`graphiti`](.skills/graphiti/SKILL.md) - Temporal knowledge graphs
