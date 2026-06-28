# Tuath Agent Architecture

Multi-agent system for Celtic language learning and mythology exploration.

## Architecture Overview

```
                    ┌─────────────────┐
                    │   User Query    │
                    └────────┬────────┘
                             │
                    ┌────────▼────────┐
                    │   Root Agent    │
                    │  (Orchestrator) │
                    └────────┬────────┘
                             │
         ┌───────────────────┼───────────────────┐
         │                   │                   │
┌────────▼────────┐ ┌────────▼────────┐ ┌────────▼────────┐
│  Celtic Tutor   │ │   Mythology     │ │  Quest Guide    │
│     Agent       │ │   Narrator      │ │     Agent       │
└────────┬────────┘ └────────┬────────┘ └────────┬────────┘
         │                   │                   │
         │          ┌────────▼────────┐          │
         │          │    Research     │          │
         │          │   Assistant     │          │
         │          └────────┬────────┘          │
         │                   │                   │
         └───────────────────┼───────────────────┘
                             │
                    ┌────────▼────────┐
                    │     Tools       │
                    │ (curriculum,    │
                    │  mythology,     │
                    │  translation)   │
                    └─────────────────┘
```

## Agent Framework

Built on **Google ADK (Agent Developer Kit)** with:
- LlmAgent for agent definitions
- Sub-agent routing for specialization
- Tool integration via function decorators
- AG-UI protocol for streaming responses

## Root Agent

**Location:** `sruth/tuath/agents/adk/root_agent.py`

The orchestrator that routes queries to specialist agents.

### Query Classification

```python
def classify_query(query: str) -> str:
    """Routes to: tutor, mythology, quest, or research."""
```

| Keywords | Agent |
|----------|-------|
| translate, grammar, vocabulary, pronunciation | celtic_tutor |
| story, legend, myth, who is, tell me about | mythology_narrator |
| quest, mission, objective, complete, hint | quest_guide |
| research, history, compare | research_assistant |

### Model Configuration

```python
# From agents/config.py
orchestrator_model = "claude-sonnet-4-20250514"  # Fast routing
specialist_model = "claude-opus-4-20250514"       # Deep expertise
```

## Specialist Agents

### 1. Celtic Tutor Agent

**File:** `agents/adk/celtic_tutor.py`

Handles language learning queries:
- Grammar explanations
- Vocabulary practice
- Translation help
- Pronunciation guidance

**Supported Languages:**
- Irish (Gaeilge) - ga
- Scottish Gaelic (Gàidhlig) - gd
- Welsh (Cymraeg) - cy

**Example Interaction:**
```
User: How do I conjugate "to be" in Irish past tense?
Agent: The verb "bí" (to be) has an irregular past tense...
       - Bhí mé (I was)
       - Bhí tú (you were)
       - Bhí sé/sí (he/she was)
```

### 2. Mythology Narrator Agent

**File:** `agents/adk/mythology_narrator.py`

Expert on Celtic mythology:
- Irish mythology (Tuatha Dé Danann, Fianna cycle)
- Welsh mythology (Mabinogion)
- Scottish legends
- Character backgrounds for NPCs

**Traditions Covered:**
- Tuatha Dé Danann
- Ulster Cycle (Cú Chulainn)
- Fianna Cycle (Fionn Mac Cumhaill)
- Mabinogion (Welsh)
- Scottish hero tales

**Example Interaction:**
```
User: Tell me about Cú Chulainn
Agent: Cú Chulainn (pronounced koo-HUL-in), the Hound of Ulster...
       He was the greatest warrior of the Ulster Cycle...
```

### 3. Quest Guide Agent

**File:** `agents/adk/quest_guide.py`

In-game quest assistance:
- Quest objectives and hints
- Learning outcome tracking
- Progress guidance
- Location navigation

**Quest Types:**
- Language quests (vocabulary, grammar)
- Mythology quests (story exploration)
- Culture quests (traditions, festivals)
- Exploration quests (geographic)

**Example Interaction:**
```
User: I'm stuck on the Fionn quest, where do I go next?
Agent: For "The Salmon of Knowledge" quest, you need to...
       Head to the River Boyne (An Bhóinn) and speak with Finnegas...
```

### 4. Research Assistant Agent

**File:** `agents/adk/research_assistant.py`

Deep research and curriculum connections:
- Historical context
- Curriculum mapping
- Comparative analysis
- Academic citations

**Research Capabilities:**
- Cross-reference curriculum standards
- Historical timeline placement
- Etymology and linguistic evolution
- Cultural practice research

## Tools

### curriculum_search

**File:** `agents/tools/curriculum_search.py`

Searches curriculum content from NCCA, SQA, WJEC.

```python
@tool
def curriculum_search(
    query: str,
    languages: list[str] = ["irish"],
    levels: list[str] = None,
    limit: int = 5
) -> list[CurriculumResult]:
    """Search Celtic curriculum content."""
```

### mythology_query

**File:** `agents/tools/mythology_query.py`

Queries the mythology knowledge graph.

```python
@tool
def mythology_query(
    query: str,
    traditions: list[str] = None,
    entity_types: list[str] = None
) -> MythologyResult:
    """Query Celtic mythology knowledge base."""
```

### translation

**File:** `agents/tools/translation.py`

Translates between Celtic languages and English.

```python
@tool
def translate(
    text: str,
    source_lang: str,
    target_lang: str
) -> TranslationResult:
    """Translate between Celtic languages and English."""
```

Supports:
- Irish (ga) ↔ English (en)
- Welsh (cy) ↔ English (en)
- Scottish Gaelic (gd) ↔ English (en)
- Irish ↔ Welsh (via English pivot)

### player_progress

**File:** `agents/tools/player_progress.py`

Accesses player state for personalized responses.

```python
@tool
def get_player_progress(
    player_id: str
) -> PlayerProgress:
    """Get current player progress and stats."""
```

### spatial_query

**File:** `agents/tools/spatial_query.py`

Queries geospatial data for Celtic regions.

```python
@tool
def spatial_query(
    query: str,
    region_type: str = None,
    near_location: tuple = None
) -> list[GeoResult]:
    """Query Celtic geographic regions."""
```

## AG-UI Protocol Integration

The agents expose an AG-UI (Agent-to-UI) protocol endpoint for streaming responses.

### Endpoint

```
POST /copilotkit/chat
```

### Event Types

| Event | Description |
|-------|-------------|
| `text` | Streaming text response |
| `tool_call` | Agent invoking a tool |
| `tool_result` | Tool execution result |
| `agent_handoff` | Sub-agent delegation |
| `done` | Stream complete |

### Example Stream

```javascript
const response = await fetch('/copilotkit/chat', {
  method: 'POST',
  body: JSON.stringify({
    messages: [{ role: 'user', content: 'Teach me Irish greetings' }],
    stream: true
  })
});

const reader = response.body.getReader();
while (true) {
  const { done, value } = await reader.read();
  if (done) break;
  const event = JSON.parse(new TextDecoder().decode(value));
  handleEvent(event);
}
```

## Prompt Engineering Patterns

### Celtic Language Awareness

All agents are instructed to:
1. Use Celtic language when relevant
2. Provide English explanations alongside
3. Include pronunciation guides
4. Note dialect variations (Connacht, Munster, Ulster)

### Curriculum Integration

Responses link to:
- NCCA learning outcomes (Ireland)
- SQA standards (Scotland)
- WJEC specifications (Wales)

### Immersive MMO Context

Agents maintain game world context:
- Reference in-game locations
- Mention NPC characters
- Track player quest progress
- Use appropriate Celtic greetings

## Callbacks

### Citation Callbacks

**File:** `agents/callbacks/citation_callbacks.py`

Tracks sources for all agent responses:

```python
class CitationCallback:
    """Captures curriculum and mythology citations."""

    def on_tool_call(self, tool_name: str, result: Any):
        if hasattr(result, 'source'):
            self.citations.append({
                'source': result.source,
                'id': result.id,
                'relevance': result.score
            })
```

## Testing Agents

### Unit Tests

```bash
uv run pytest tests/test_agents.py -v
```

### Interactive Testing

```python
from tuath.agents.adk.root_agent import app

# Run agent
response = app.run("Conas a deir mé 'thank you' as Gaeilge?")
print(response)
```

### Demo Mode

```bash
uv run python -m tuath.demo.run_demo
```

## Configuration

**File:** `agents/config.py`

```python
class AgentConfig:
    # Model settings
    orchestrator_model: str = "claude-sonnet-4-20250514"
    specialist_model: str = "claude-opus-4-20250514"

    # Tool settings
    curriculum_search_limit: int = 5
    mythology_search_limit: int = 10

    # Language settings
    default_language: str = "irish"
    supported_languages: list = ["irish", "welsh", "scottish_gaelic"]
```

## Adding New Agents

1. Create agent file in `agents/adk/`
2. Define LlmAgent with instruction prompt
3. Register tools from `agents/tools/`
4. Add to root_agent.sub_agents
5. Update classify_query() routing

Example:
```python
from google.adk.agents import LlmAgent
from ..config import config

new_agent = LlmAgent(
    name="new_specialist",
    model=config.specialist_model,
    description="Handles X queries",
    instruction="You are an expert in X...",
    tools=[tool1, tool2],
)
```

---

## Related Documentation

- [Tuath API Reference](../00-nav/Tuath%20API%20Reference.md) - CopilotKit endpoints
- [Celtic Languages](../01-game-design/CELTIC_LANGUAGES.md) - Language-specific patterns
- [Game Client](../01-game-design/GAME_CLIENT.md) - Babylon.js integration
- [Tuath Project Analysis](../ANALYSIS.md) - System overview

---

# Part II: Adding New Agents

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

# Part III: Adding New Tools

# Adding Agent Tools

Guide for creating custom tools for ADK agents in the Tuath Celtic Educational MMO.

## Overview

Tools extend agent capabilities by providing access to external data, APIs, and game systems. Each tool has:
- Input/output schemas (Pydantic)
- Async implementation
- Error handling
- Rate limiting (optional)

### Existing Tools Reference

| Tool | File | Purpose |
|------|------|---------|
| `mythology_query` | `tools/mythology_query.py` | Search mythology knowledge graph |
| `translation` | `tools/translation.py` | Translate between Celtic languages |
| `player_progress` | `tools/player_progress.py` | Get/update player state |
| `spatial_query` | `tools/spatial_query.py` | Query geographic data |
| `curriculum_search` | `tools/curriculum_search.py` | Search curriculum content |

---

## Creating a New Tool

### Step 1: Define Schemas

```python
# agents/tools/my_tool.py
"""
My custom tool for [purpose].
"""

from pydantic import BaseModel, Field
from typing import Optional, List
from enum import Enum


class LanguageCode(str, Enum):
    """Supported Celtic languages."""
    IRISH = "ga"
    SCOTTISH_GAELIC = "gd"
    WELSH = "cy"
    ENGLISH = "en"


class MyToolInput(BaseModel):
    """Input schema for my_tool.

    All fields should have descriptions for the LLM to understand usage.
    """
    query: str = Field(
        ...,
        description="The search query or request text",
        min_length=1,
        max_length=1000,
    )
    language: LanguageCode = Field(
        default=LanguageCode.IRISH,
        description="Target language for results",
    )
    limit: int = Field(
        default=10,
        description="Maximum number of results to return",
        ge=1,
        le=100,
    )
    include_metadata: bool = Field(
        default=True,
        description="Whether to include source metadata",
    )


class ResultItem(BaseModel):
    """Individual result item."""
    id: str
    content: str
    score: float = Field(ge=0.0, le=1.0)
    source: Optional[str] = None


class MyToolOutput(BaseModel):
    """Output schema for my_tool."""
    success: bool
    results: List[ResultItem] = Field(default_factory=list)
    total_count: int = 0
    query_time_ms: float = 0.0
    error: Optional[str] = None
    metadata: dict = Field(default_factory=dict)
```

### Step 2: Implement Tool Function

```python
# agents/tools/my_tool.py (continued)

import time
import logging
from google.adk.tools import Tool

logger = logging.getLogger(__name__)


async def my_tool_impl(input: MyToolInput) -> MyToolOutput:
    """
    Execute the tool logic.

    Args:
        input: Validated input from the agent

    Returns:
        MyToolOutput with results or error
    """
    start_time = time.perf_counter()

    try:
        # Validate input
        if not input.query.strip():
            return MyToolOutput(
                success=False,
                error="Query cannot be empty",
            )

        # Execute core logic
        results = await perform_search(
            query=input.query,
            language=input.language.value,
            limit=input.limit,
        )

        # Transform results
        result_items = [
            ResultItem(
                id=r["id"],
                content=r["content"],
                score=r["score"],
                source=r.get("source") if input.include_metadata else None,
            )
            for r in results
        ]

        query_time = (time.perf_counter() - start_time) * 1000

        return MyToolOutput(
            success=True,
            results=result_items,
            total_count=len(result_items),
            query_time_ms=query_time,
            metadata={
                "language": input.language.value,
                "query_length": len(input.query),
            },
        )

    except ValidationError as e:
        logger.warning(f"Validation error in my_tool: {e}")
        return MyToolOutput(
            success=False,
            error=f"Invalid input: {str(e)}",
        )

    except ExternalAPIError as e:
        logger.error(f"External API error in my_tool: {e}")
        return MyToolOutput(
            success=False,
            error="External service temporarily unavailable",
        )

    except Exception as e:
        logger.exception(f"Unexpected error in my_tool: {e}")
        return MyToolOutput(
            success=False,
            error="An unexpected error occurred",
        )
```

### Step 3: Create Tool Object

```python
# agents/tools/my_tool.py (continued)

my_tool = Tool(
    name="my_tool",
    description="""Search for [specific content type].

    Use this tool when:
    - The user asks about [specific topic]
    - You need to find [specific information]

    Example queries:
    - "Find vocabulary related to weather"
    - "Search for grammar rules about verbs"

    Returns results with relevance scores and source metadata.
    """,
    input_schema=MyToolInput,
    output_schema=MyToolOutput,
    function=my_tool_impl,
)
```

### Step 4: Export Tool

```python
# agents/tools/__init__.py

from .my_tool import my_tool

__all__ = [
    "mythology_query",
    "translation",
    "player_progress",
    "spatial_query",
    "curriculum_search",
    "my_tool",  # Add here
]
```

### Step 5: Add to Agent

```python
# agents/adk/celtic_tutor.py

from ..tools.my_tool import my_tool

celtic_tutor_agent = LlmAgent(
    name="celtic_tutor",
    model=config.agent_model,
    tools=[
        translation,
        curriculum_search,
        my_tool,  # Add to tools list
    ],
    instruction="""
    ...
    **TOOLS AVAILABLE:**
    - my_tool: Search for [description]
    ...
    """,
)
```

---

## Tool Categories

### Database Query Tools

```python
# tools/curriculum_search.py
"""Search curriculum content using vector similarity."""

from tuath.storage.lancedb_client import LanceDBClient
from tuath.knowledge_graph.hybrid_search import HybridSearch


class CurriculumSearchInput(BaseModel):
    query: str
    nation: Optional[str] = None  # ireland, scotland, wales
    level: Optional[str] = None   # primary, secondary, higher
    subject: Optional[str] = None
    limit: int = 10


async def curriculum_search_impl(input: CurriculumSearchInput) -> CurriculumSearchOutput:
    """Search curriculum using hybrid vector + keyword search."""

    hybrid_search = HybridSearch()

    results = await hybrid_search.search(
        query=input.query,
        content_types=["curriculum"],
        filters={
            "nation": input.nation,
            "level": input.level,
            "subject": input.subject,
        },
        limit=input.limit,
    )

    return CurriculumSearchOutput(
        success=True,
        results=[
            CurriculumResult(
                id=r.id,
                title=r.metadata.get("title", ""),
                content=r.content,
                nation=r.metadata.get("nation"),
                level=r.metadata.get("level"),
                learning_outcomes=r.metadata.get("learning_outcomes", []),
                score=r.score,
            )
            for r in results
        ],
    )
```

### Graph Query Tools

```python
# tools/mythology_query.py
"""Query mythology knowledge graph."""

from tuath.knowledge_graph.falkordb_client import FalkorDBClient


class MythologyQueryInput(BaseModel):
    entity_name: Optional[str] = None
    entity_type: Optional[str] = None  # character, story, place, artifact
    relationship: Optional[str] = None  # related_to, appears_in, child_of
    tradition: Optional[str] = None     # irish, welsh, scottish
    limit: int = 20


async def mythology_query_impl(input: MythologyQueryInput) -> MythologyQueryOutput:
    """Query mythology entities and relationships."""

    client = FalkorDBClient()

    # Build Cypher query
    if input.entity_name:
        query = """
        MATCH (n:MythologyEntity {name: $name})
        OPTIONAL MATCH (n)-[r]->(related)
        RETURN n, type(r) as rel_type, related
        LIMIT $limit
        """
        params = {"name": input.entity_name, "limit": input.limit}
    elif input.entity_type:
        query = """
        MATCH (n:MythologyEntity {type: $type})
        RETURN n
        LIMIT $limit
        """
        params = {"type": input.entity_type, "limit": input.limit}
    else:
        query = "MATCH (n:MythologyEntity) RETURN n LIMIT $limit"
        params = {"limit": input.limit}

    results = await client.execute(query, params)

    return MythologyQueryOutput(
        success=True,
        entities=[parse_entity(r) for r in results],
    )
```

### Translation Tools

```python
# tools/translation.py
"""Translate between Celtic languages."""

from tuath.services.translation import TranslationService


class TranslationInput(BaseModel):
    text: str = Field(..., max_length=5000)
    source_language: str = Field(default="en")
    target_language: str = Field(...)
    include_pronunciation: bool = Field(default=True)
    include_alternatives: bool = Field(default=False)


class TranslationOutput(BaseModel):
    success: bool
    translation: str
    pronunciation: Optional[str] = None
    alternatives: List[str] = Field(default_factory=list)
    confidence: float = 0.0
    notes: Optional[str] = None


async def translation_impl(input: TranslationInput) -> TranslationOutput:
    """Translate text between languages."""

    service = TranslationService()

    result = await service.translate(
        text=input.text,
        source=input.source_language,
        target=input.target_language,
    )

    output = TranslationOutput(
        success=True,
        translation=result.text,
        confidence=result.confidence,
    )

    if input.include_pronunciation:
        output.pronunciation = await service.get_pronunciation(
            text=result.text,
            language=input.target_language,
        )

    if input.include_alternatives:
        output.alternatives = result.alternatives[:5]

    return output
```

### Player State Tools

```python
# tools/player_progress.py
"""Manage player progress and achievements."""

from tuath.storage.spacetimedb_client import SpacetimeDBClient


class PlayerProgressInput(BaseModel):
    player_id: str
    action: str = Field(description="get, update, add_xp, complete_quest, learn_word")
    data: Optional[dict] = None


class PlayerProgressOutput(BaseModel):
    success: bool
    player_state: Optional[dict] = None
    xp_earned: int = 0
    level_up: bool = False
    achievements_unlocked: List[str] = Field(default_factory=list)
    message: Optional[str] = None


async def player_progress_impl(input: PlayerProgressInput) -> PlayerProgressOutput:
    """Get or update player progress."""

    client = SpacetimeDBClient()

    if input.action == "get":
        state = await client.get_player(input.player_id)
        return PlayerProgressOutput(
            success=True,
            player_state=state.dict(),
        )

    elif input.action == "add_xp":
        xp_amount = input.data.get("xp", 0)
        result = await client.add_xp(input.player_id, xp_amount)

        return PlayerProgressOutput(
            success=True,
            xp_earned=xp_amount,
            level_up=result.level_changed,
            message=f"Earned {xp_amount} XP!",
        )

    elif input.action == "learn_word":
        word = input.data.get("word")
        language = input.data.get("language", "ga")

        await client.add_vocabulary(input.player_id, word, language)

        return PlayerProgressOutput(
            success=True,
            message=f"Learned new word: {word}",
        )

    # ... other actions
```

---

## Advanced Patterns

### Caching Results

```python
from functools import lru_cache
from cachetools import TTLCache
import asyncio

# In-memory cache with TTL
_cache = TTLCache(maxsize=1000, ttl=300)  # 5 minutes
_cache_lock = asyncio.Lock()


async def cached_tool_impl(input: MyToolInput) -> MyToolOutput:
    """Tool with caching."""

    cache_key = f"{input.query}:{input.language}:{input.limit}"

    async with _cache_lock:
        if cache_key in _cache:
            return _cache[cache_key]

    result = await perform_actual_search(input)

    async with _cache_lock:
        _cache[cache_key] = result

    return result
```

### Rate Limiting

```python
from asyncio import Semaphore
from datetime import datetime, timedelta

# Rate limiter: 10 requests per minute
_rate_limit = Semaphore(10)
_request_times: list[datetime] = []


async def rate_limited_tool_impl(input: MyToolInput) -> MyToolOutput:
    """Tool with rate limiting."""

    # Clean old request times
    cutoff = datetime.now() - timedelta(minutes=1)
    _request_times[:] = [t for t in _request_times if t > cutoff]

    if len(_request_times) >= 10:
        wait_time = (_request_times[0] + timedelta(minutes=1) - datetime.now()).total_seconds()
        return MyToolOutput(
            success=False,
            error=f"Rate limit exceeded. Try again in {wait_time:.0f}s",
        )

    async with _rate_limit:
        _request_times.append(datetime.now())
        return await perform_search(input)
```

### Batching Requests

```python
from typing import List
import asyncio


class BatchInput(BaseModel):
    queries: List[str] = Field(..., max_length=50)
    language: str = "ga"


async def batched_tool_impl(input: BatchInput) -> BatchOutput:
    """Tool that processes multiple queries efficiently."""

    # Process in batches of 10
    batch_size = 10
    all_results = []

    for i in range(0, len(input.queries), batch_size):
        batch = input.queries[i:i + batch_size]

        # Process batch concurrently
        tasks = [
            perform_single_search(q, input.language)
            for q in batch
        ]
        batch_results = await asyncio.gather(*tasks, return_exceptions=True)

        all_results.extend([
            r for r in batch_results
            if not isinstance(r, Exception)
        ])

    return BatchOutput(success=True, results=all_results)
```

### Fallback Chains

```python
async def resilient_tool_impl(input: MyToolInput) -> MyToolOutput:
    """Tool with fallback chain."""

    # Try primary source
    try:
        result = await primary_search(input)
        if result.success and result.results:
            return result
    except Exception as e:
        logger.warning(f"Primary search failed: {e}")

    # Fallback to secondary source
    try:
        result = await secondary_search(input)
        if result.success and result.results:
            result.metadata["source"] = "fallback"
            return result
    except Exception as e:
        logger.warning(f"Secondary search failed: {e}")

    # Final fallback: cached/static data
    return await get_cached_results(input)
```

---

## Testing Tools

### Unit Tests

```python
# tests/test_my_tool.py
import pytest
from agents.tools.my_tool import my_tool_impl, MyToolInput


@pytest.mark.asyncio
async def test_basic_query():
    """Test basic query execution."""
    input = MyToolInput(
        query="Irish weather vocabulary",
        language="ga",
        limit=5,
    )

    result = await my_tool_impl(input)

    assert result.success is True
    assert len(result.results) <= 5
    assert result.query_time_ms > 0


@pytest.mark.asyncio
async def test_empty_query():
    """Test handling of empty query."""
    input = MyToolInput(query="", language="ga")

    result = await my_tool_impl(input)

    assert result.success is False
    assert "empty" in result.error.lower()


@pytest.mark.asyncio
async def test_invalid_language():
    """Test handling of invalid language code."""
    with pytest.raises(ValueError):
        MyToolInput(query="test", language="invalid")
```

### Integration Tests

```python
# tests/integration/test_tool_integration.py
import pytest
from agents.adk.celtic_tutor import celtic_tutor_agent


@pytest.mark.asyncio
async def test_agent_uses_tool():
    """Test that agent correctly invokes tool."""

    response = await celtic_tutor_agent.generate(
        message="Search for vocabulary about the sea",
        context={"language": "ga"},
    )

    # Verify tool was called
    tool_calls = [tc for tc in response.tool_calls if tc.tool_name == "my_tool"]
    assert len(tool_calls) > 0

    # Verify tool produced results
    tool_result = tool_calls[0].result
    assert tool_result["success"] is True
```

### Mock Testing

```python
# tests/test_my_tool_mocked.py
import pytest
from unittest.mock import AsyncMock, patch


@pytest.mark.asyncio
async def test_tool_with_mock():
    """Test tool with mocked dependencies."""

    mock_results = [
        {"id": "1", "content": "Test", "score": 0.9},
    ]

    with patch("agents.tools.my_tool.perform_search", new_callable=AsyncMock) as mock:
        mock.return_value = mock_results

        input = MyToolInput(query="test", language="ga")
        result = await my_tool_impl(input)

        assert result.success is True
        assert len(result.results) == 1
        mock.assert_called_once()
```

---

## Best Practices

### 1. Schema Design

- Use descriptive field names and descriptions
- Set appropriate constraints (min/max, regex patterns)
- Make outputs structured and parseable
- Include confidence scores where applicable

### 2. Error Handling

- Never let exceptions propagate unhandled
- Return structured error responses
- Log errors with context for debugging
- Provide user-friendly error messages

### 3. Performance

- Cache expensive operations
- Use connection pooling for databases
- Batch similar operations
- Set reasonable timeouts

### 4. Documentation

- Document when to use the tool in the description
- Provide example queries
- Explain output format
- Note any rate limits or quotas

---

# Part IV: Related Documentation

- [API Reference](../00-nav/Tuath%20API%20Reference.md) - CopilotKit endpoints
- [Architecture Overview](../ANALYSIS.md) - Project analysis
- [Celtic Languages](../01-game-design/CELTIC_LANGUAGES.md) - Language-specific patterns
- [Game Client](../01-game-design/GAME_CLIENT.md) - Babylon.js integration
- [Tuath MMO Concept](../01-game-design/mythology-framework.md) - Mythology context
