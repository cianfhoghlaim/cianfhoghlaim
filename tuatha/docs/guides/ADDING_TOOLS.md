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

## Related Documentation

- [Adding Agents](./ADDING_AGENTS.md) - Create new ADK agents
- [Architecture](../ARCHITECTURE.md) - System overview
- [API Reference](../api/README.md) - Backend endpoints
