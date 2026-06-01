---
name: graphiti
description: Temporal knowledge graph with bi-temporal data model for tracking prerequisite relationships, learning progressions, and curriculum changes over time.
---

# Graphiti

**Version:** >=0.5.0 | **Last Updated:** 2025-04

## Overview

Graphiti provides temporal reasoning capabilities for the Cianfhoghlaim education platform, enabling tracking of curriculum changes and prerequisite relationships across time.

| Feature | Description |
|---------|-------------|
| Bi-Temporal Model | Valid time + transaction time |
| Knowledge Graphs | Entity and relationship tracking |
| Temporal Queries | Point-in-time and period queries |
| Memory System | Episodic and semantic memory |
| HNSW Indexing | High-performance graph traversal |
| MVCC Safety | Multi-version concurrency control |

## When to Use This Skill

Activate when users need:

- "Track curriculum changes over time"
- "Query historical prerequisite relationships"
- "Build temporal knowledge graph"
- "Implement AI memory with time awareness"
- "Compare curriculum versions"

## Project Integration

### Infrastructure Location

| Component | Path |
|-----------|------|
| Stack Config | `bonneagar/storage/graphiti/` |
| Integration | `sruth/oideachais/knowledge_graph/graphiti/` |

### Research References (taighde/)

| Directory | Relevant Documents |
|-----------|-------------------|
| `taighde_scoil/` | Curriculum versioning patterns |
| `taighde_bonneagar/` | Graphiti deployment guides |

## Core Concepts

### 1. Bi-Temporal Data Model

```python
from graphiti_core import Graphiti
from datetime import datetime

# Valid time: when the fact is true in reality
# Transaction time: when the fact was recorded

client = Graphiti(
    neo4j_url="bolt://graphiti.cianfhoghlaim.ie:7687",
    neo4j_user="neo4j",
    neo4j_password="password"
)
```

### 2. Adding Episodic Memory

```python
from graphiti_core.nodes import EpisodeType

# Add curriculum change as an episode
episode = await client.add_episode(
    name="Junior Cycle Math Update 2024",
    episode_body="""
    The Junior Cycle Mathematics specification was updated
    to include new topics in Data Science and Probability.
    """,
    source_description="NCCA Circular 2024",
    reference_time=datetime(2024, 9, 1),  # Valid time
    episode_type=EpisodeType.curriculum_change
)
```

### 3. Temporal Queries

```python
# Query prerequisites as of a specific date
results = await client.search(
    query="What are the prerequisites for Leaving Cert Physics?",
    reference_time=datetime(2023, 9, 1)  # Point-in-time query
)

# Compare prerequisites between years
historical = await client.search(
    query="Prerequisites for LC Physics",
    reference_time=datetime(2020, 9, 1)
)
current = await client.search(
    query="Prerequisites for LC Physics",
    reference_time=datetime(2024, 9, 1)
)
```

### 4. Entity Extraction

```python
from graphiti_core.llm_client import OpenAIClient

# Configure LLM for entity extraction
llm_client = OpenAIClient(model="gpt-4o-mini")

# Extract entities from curriculum document
entities = await client.add_episode(
    name="LC Biology Specification",
    episode_body=curriculum_text,
    source_description="NCCA",
    reference_time=datetime.now()
)
```

## Cianfhoghlaim-Specific Usage

### Curriculum Version Tracking

```python
# Track specification versions
await client.add_episode(
    name="Junior Cycle Irish Updated",
    episode_body="""
    Specification L1 replaced by L2.
    Focus shifted from grammar to communication.
    """,
    source_description="NCCA",
    reference_time=datetime(2024, 9, 1),
    episode_type=EpisodeType.curriculum_change
)

# Query what changed
changes = await client.search(
    query="What changed in Junior Cycle Irish?",
    num_results=10
)
```

### Integration with Knowledge Graph

```python
# Connect Graphiti entities to Memgraph prerequisite graph
from memgraph import Memgraph

mg = Memgraph()
graphiti_entities = await client.get_nodes(limit=100)

for entity in graphiti_entities:
    mg.execute("""
        MERGE (n:Topic {name: $name})
        SET n.valid_from = $valid_from
    """, {"name": entity.name, "valid_from": entity.valid_at})
```

## Best Practices

1. **Always set reference_time** - Enables temporal queries
2. **Use episode types** - Categorize changes for filtering
3. **Include source_description** - Traceability for curriculum changes
4. **Batch entity extraction** - Reduces API calls

## Resources

- **GitHub:** https://github.com/getzep/graphiti
- **Documentation:** https://docs.getzep.com/graphiti
- **Related Skills:** memgraph, cognee, lancedb
