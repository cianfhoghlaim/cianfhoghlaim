---
name: graphiti-core
description: "DEPRECATED — canonical replacement is `graphiti` (v0.29.2). Documents Graphiti Core v0.5.0 (2025-04) for temporal knowledge graphs, episodic memory for agents, and tracking relationships over time. Use the canonical `graphiti` skill for new work."
---

> **DEPRECATION NOTICE (2026-07-06):** This skill is retained for backward
> compatibility but is no longer the canonical KCG pattern. It documents
> Graphiti Core v0.5.0 from 2025-04 and is two minor versions behind the
> current Graphiti. The canonical replacement is `graphiti` (v0.29.2 with
> `FalkorDB Lite` embedded mode, `summarize_saga`, `EpisodeType.{text,
> json,fact_triple,message}`) at
> `.agents/skills/graphiti/SKILL.md`. Use the canonical `graphiti` skill
> for new work.

# Graphiti Core - Knowledge Graph Memory

**Version:** >=0.5.0 | **Last Updated:** 2025-04

## Overview

Graphiti Core is a knowledge graph memory system designed for AI agents:

- **Temporal Tracking**: Track relationships and entities over time
- **Episodic Memory**: Store and retrieve agent experiences
- **Knowledge Graphs**: Extract entities and relationships from text
- **Bi-Temporal Model**: Valid time + transaction time support

**Documentation**: https://github.com/getmemex/graphiti

## When to Use This Skill

Activate when users need:

- "Build a knowledge graph for agent memory"
- "Track temporal relationships between entities"
- "Implement episodic memory for agents"
- "Query historical data with time awareness"

## Core Concepts

### 1. Basic Setup

```python
from graphiti_core import Graphiti
from datetime import datetime

# Initialize Graphiti client
client = Graphiti(
    neo4j_url="bolt://localhost:7687",
    neo4j_user="neo4j",
    neo4j_password="password"
)
```

### 2. Adding Episodes

```python
from graphiti_core.nodes import EpisodeType

# Add an episode (memory)
episode = await client.add_episode(
    name="User Interaction - Curriculum Query",
    episode_body="""
    User asked about Junior Cycle Mathematics curriculum.
    Discussed topics including algebra, geometry, and statistics.
    User expressed interest in data science integration.
    """,
    source_description="chat_session_123",
    reference_time=datetime(2025, 4, 23, 10, 30, 0),
    episode_type=EpisodeType.user_interaction
)

print(f"Episode ID: {episode.uuid}")
```

### 3. Entity and Relationship Extraction

```python
# Extract entities and relationships from text
text = """
The Junior Cycle Mathematics specification includes algebra, geometry,
and statistics. Data science has been added as a new topic area.
"""

await client.add_episode(
    name="Curriculum Content",
    episode_body=text,
    source_description="curriculum_document",
    reference_time=datetime.now()
)

# Graphiti automatically extracts:
# - Entities: Junior Cycle Mathematics, algebra, geometry, statistics, data science
# - Relationships: includes, added_as, related_to
```

### 4. Temporal Queries

```python
# Query as of a specific point in time
results = await client.search(
    query="What topics are included in Junior Cycle Mathematics?",
    reference_time=datetime(2024, 1, 1)  # Query historical state
)

# Compare across time periods
historical = await client.search(
    query="Junior Cycle Mathematics topics",
    reference_time=datetime(2023, 1, 1)
)

current = await client.search(
    query="Junior Cycle Mathematics topics",
    reference_time=datetime.now()
)

# Identify changes
changes = await client.compare_temporal_states(
    query="Junior Cycle Mathematics topics",
    time1=datetime(2023, 1, 1),
    time2=datetime.now()
)
```

### 5. Graph Traversal

```python
# Find related entities
related = await client.search(
    query="What is related to algebra in the curriculum?",
    search_type="graph_traversal"
)

# Find shortest path between entities
path = await client.find_path(
    entity1="Junior Cycle Mathematics",
    entity2="data science"
)

# Get entity neighborhoods
neighbors = await client.get_neighbors(
    entity="algebra",
    depth=2  # How many hops to explore
)
```

## Episode Types

```python
from graphiti_core.nodes import EpisodeType

# Available episode types
EpisodeType.user_interaction    # User-agent conversations
EpisodeType.system_event        # System-level events
EpisodeType.curriculum_change   # Curriculum updates
EpisodeType.learning_progress   # Student progress
EpisodeType.knowledge_update   # Knowledge base updates
```

## Best Practices

### Memory Management

1. **Episode Granularity**: Keep episodes focused and specific
2. **Reference Time**: Always set accurate reference times for temporal queries
3. **Source Tracking**: Include source descriptions for provenance

### Query Optimization

1. **Time Bounds**: Specify time ranges to improve query performance
2. **Entity Filtering**: Filter by entity types when possible
3. **Caching**: Cache frequently accessed query results

### Schema Design

1. **Entity Types**: Define clear entity type hierarchies
2. **Relationship Types**: Use consistent relationship naming
3. **Metadata**: Add metadata for filtering and organization

## Installation

```bash
pip install graphiti-core
```

## Configuration

```python
from graphiti_core import Graphiti
from graphiti_core.llm_client import OpenAIClient

# Configure LLM for entity extraction
llm_client = OpenAIClient(
    api_key="your-openai-key",
    model="gpt-4o-mini"
)

client = Graphiti(
    neo4j_url="bolt://localhost:7687",
    neo4j_user="neo4j",
    neo4j_password="password",
    llm_client=llm_client
)
```

## Project Integration

### Use Cases

| Scenario | Pattern |
|----------|---------|
| Agent Memory | Episodic memory with temporal tracking |
| Curriculum Tracking | Bi-temporal curriculum versioning |
| Knowledge Graph | Entity and relationship extraction |
| Historical Analysis | Point-in-time queries |

### Related Skills

- [`cognee`](.skills/cognee/SKILL.md) - Alternative knowledge graph platform
- [`agno`](.skills/agno/SKILL.md) - Agent framework with memory
- [`google-adk`](.skills/google-adk/SKILL.md) - Google's agent framework
