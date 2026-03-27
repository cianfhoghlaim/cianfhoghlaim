# Adding New Agents

Guide for creating new ADK agents in the Tuath Celtic Educational MMO.

## Overview

Tuath uses Google ADK (Agent Development Kit) for multi-agent orchestration. The root agent routes queries to specialized sub-agents based on user intent.

### Current Agent Architecture

```
Root Agent (Orchestrator)
├── Celtic Tutor        - Language learning
├── Mythology Narrator  - Celtic lore/stories
├── Quest Guide        - Game guidance
└── Research Assistant - Deep research
```

---

## Creating a New Agent

### Step 1: Create Agent File

Create a new file in `agents/adk/`:

```python
# agents/adk/new_agent.py
"""
New Agent for Tuath.

[Description of what this agent does]
"""

import datetime

from google.adk.agents import LlmAgent
from google.adk.tools import Tool

from ..config import config
from ..tools.my_tool import my_tool

new_agent = LlmAgent(
    name="new_agent",
    model=config.agent_model,
    description="Short description for the orchestrator to understand when to route here",
    instruction="""
    You are a specialized agent for [specific purpose].

    **CAPABILITIES:**
    - Capability 1
    - Capability 2

    **TOOLS AVAILABLE:**
    - tool_name: What it does

    **RESPONSE GUIDELINES:**
    1. Always provide bilingual responses when dealing with Celtic languages
    2. Include learning objectives when educational
    3. Maintain the game world context

    **SUPPORTED LANGUAGES:**
    - Irish (Gaeilge) - ga
    - Scottish Gaelic (Gàidhlig) - gd
    - Welsh (Cymraeg) - cy

    Current date: {datetime.datetime.now().strftime("%Y-%m-%d")}
    """,
    tools=[my_tool],
    output_key="response",
)
```

### Step 2: Create Agent Tools

If your agent needs custom tools, create them in `agents/tools/`:

```python
# agents/tools/my_tool.py
"""
Custom tool for the new agent.
"""

from google.adk.tools import Tool
from pydantic import BaseModel, Field


class MyToolInput(BaseModel):
    """Input schema for the tool."""
    query: str = Field(..., description="The query to process")
    language: str = Field(default="ga", description="Target language code")


class MyToolOutput(BaseModel):
    """Output schema for the tool."""
    result: str
    confidence: float
    metadata: dict = Field(default_factory=dict)


async def my_tool_impl(input: MyToolInput) -> MyToolOutput:
    """
    Tool implementation.

    Args:
        input: The tool input

    Returns:
        MyToolOutput with results
    """
    # Your implementation here
    result = await process_query(input.query, input.language)

    return MyToolOutput(
        result=result.text,
        confidence=result.score,
        metadata={"source": result.source},
    )


my_tool = Tool(
    name="my_tool",
    description="What this tool does and when to use it",
    input_schema=MyToolInput,
    output_schema=MyToolOutput,
    function=my_tool_impl,
)
```

### Step 3: Register with Root Agent

Add the new agent to the root orchestrator:

```python
# agents/adk/root_agent.py

from .new_agent import new_agent

root_agent = LlmAgent(
    name="tuath_agent",
    # ...
    sub_agents=[
        celtic_tutor_agent,
        mythology_narrator_agent,
        quest_guide_agent,
        research_assistant_agent,
        new_agent,  # Add here
    ],
    instruction="""
    ...
    5. **new_agent**
       - Description of when to use
       - Example queries
    """,
)
```

### Step 4: Update Exports

Add to the agents package exports:

```python
# agents/adk/__init__.py

from .new_agent import new_agent

__all__ = [
    "root_agent",
    "celtic_tutor_agent",
    "mythology_narrator_agent",
    "quest_guide_agent",
    "research_assistant_agent",
    "new_agent",
]
```

---

## Agent Configuration

### Model Selection

Configure models in `agents/config.py`:

```python
# agents/config.py
from dataclasses import dataclass
import os


@dataclass
class AgentConfig:
    """Agent configuration."""

    # Model for the root orchestrator (fast routing)
    orchestrator_model: str = "gemini-2.0-flash-exp"

    # Model for sub-agents (quality responses)
    agent_model: str = "gemini-2.0-flash-exp"

    # Model for complex research tasks
    research_model: str = "gemini-1.5-pro"

    # API configuration
    google_api_key: str = os.environ.get("GOOGLE_API_KEY", "")

    # Rate limiting
    max_requests_per_minute: int = 60


config = AgentConfig()
```

### Using Different Models

For specialized tasks, you can override the model:

```python
research_agent = LlmAgent(
    name="research_agent",
    model=config.research_model,  # Uses more capable model
    # ...
)
```

---

## Tool Development

### Tool Design Principles

1. **Single Responsibility**: Each tool should do one thing well
2. **Clear Schemas**: Use Pydantic for input/output validation
3. **Async by Default**: All tool functions should be async
4. **Error Handling**: Handle errors gracefully and return meaningful messages

### Existing Tools Reference

| Tool | File | Purpose |
|------|------|---------|
| `mythology_query` | `tools/mythology_query.py` | Search mythology knowledge graph |
| `translation` | `tools/translation.py` | Translate between Celtic languages |
| `player_progress` | `tools/player_progress.py` | Get/update player state |
| `spatial_query` | `tools/spatial_query.py` | Query geographic data |
| `curriculum_search` | `tools/curriculum_search.py` | Search curriculum content |

### Tool Template

```python
# agents/tools/template_tool.py
"""
Template tool for reference.
"""

from google.adk.tools import Tool
from pydantic import BaseModel, Field
from typing import Optional


class TemplateInput(BaseModel):
    """Input schema."""
    required_field: str = Field(..., description="Required input")
    optional_field: Optional[str] = Field(None, description="Optional input")
    with_default: int = Field(10, description="Input with default", ge=1, le=100)


class TemplateOutput(BaseModel):
    """Output schema."""
    success: bool
    result: str
    metadata: dict = Field(default_factory=dict)


async def template_impl(input: TemplateInput) -> TemplateOutput:
    """Implementation."""
    try:
        # Your logic here
        result = f"Processed: {input.required_field}"

        return TemplateOutput(
            success=True,
            result=result,
            metadata={"processed_at": "2025-01-01T00:00:00Z"},
        )
    except Exception as e:
        return TemplateOutput(
            success=False,
            result=f"Error: {str(e)}",
            metadata={},
        )


template_tool = Tool(
    name="template_tool",
    description="A template tool for reference",
    input_schema=TemplateInput,
    output_schema=TemplateOutput,
    function=template_impl,
)
```

---

## Testing Agents

### Unit Tests

```python
# tests/test_new_agent.py
import pytest
from agents.adk.new_agent import new_agent


@pytest.mark.asyncio
async def test_agent_responds():
    """Test that agent generates a response."""
    response = await new_agent.generate(
        message="Test query",
        context={"language": "ga"},
    )

    assert response is not None
    assert len(response.content) > 0


@pytest.mark.asyncio
async def test_agent_uses_tool():
    """Test that agent calls expected tools."""
    response = await new_agent.generate(
        message="Query that should trigger tool",
        context={},
    )

    # Check tool was called
    assert any(tc.tool_name == "my_tool" for tc in response.tool_calls)
```

### Integration Tests

```python
# tests/test_agent_integration.py
import pytest
from agents.adk.root_agent import root_agent


@pytest.mark.asyncio
async def test_routing_to_new_agent():
    """Test that root agent routes appropriately."""
    response = await root_agent.generate(
        message="Query that should go to new_agent",
        context={},
    )

    # Check correct sub-agent was used
    assert "new_agent" in response.metadata.get("agent_path", [])
```

### Running Tests

```bash
# Run agent tests
uv run pytest tests/test_new_agent.py -v

# Run with coverage
uv run pytest tests/ --cov=tuath.agents --cov-report=html
```

---

## Best Practices

### 1. Agent Instructions

- Be specific about capabilities and limitations
- Include example queries to help routing
- Specify output format expectations
- Include cultural/educational context

### 2. Tool Design

- Validate inputs thoroughly
- Return structured, parseable outputs
- Include confidence scores when relevant
- Log tool usage for debugging

### 3. Error Handling

```python
async def safe_tool_impl(input: Input) -> Output:
    """Tool with proper error handling."""
    try:
        result = await risky_operation(input)
        return Output(success=True, result=result)
    except ValidationError as e:
        logger.warning(f"Validation error: {e}")
        return Output(success=False, error=f"Invalid input: {e}")
    except ExternalAPIError as e:
        logger.error(f"External API error: {e}")
        return Output(success=False, error="Service temporarily unavailable")
    except Exception as e:
        logger.exception(f"Unexpected error in tool: {e}")
        return Output(success=False, error="An unexpected error occurred")
```

### 4. Performance

- Cache frequently accessed data
- Use async operations for I/O
- Batch similar operations
- Set reasonable timeouts

---

## Debugging

### Enable Verbose Logging

```python
import logging

logging.getLogger("google.adk").setLevel(logging.DEBUG)
```

### Trace Agent Execution

```python
response = await agent.generate(
    message="Test query",
    context={},
    trace=True,  # Enable tracing
)

# Access trace
for step in response.trace:
    print(f"{step.agent}: {step.action}")
```

---

## Related Documentation

- [Architecture](../ARCHITECTURE.md) - System overview
- [AGENTS.md](../AGENTS.md) - Existing agent documentation
- [API Reference](../api/README.md) - CopilotKit endpoints
