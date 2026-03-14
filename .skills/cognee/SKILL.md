---
name: cognee
description: Expert assistance for AI memory systems with Cognee. Use when users need knowledge graphs, semantic search, RAG applications, persistent agent memory, or transforming documents into queryable knowledge.
---

# Cognee - AI Memory Platform

**Version:** 0.x | **Last Updated:** 2025-01

## Overview

Cognee is an open-source AI memory platform that transforms data into persistent, dynamic memory:

- **Knowledge Graphs**: Extract entities and relationships from text
- **Semantic Search**: Vector + graph hybrid search
- **Persistent Memory**: Long-term memory for AI agents
- **Multi-Backend**: Support for various graph and vector databases

**Documentation**: https://docs.cognee.ai

## When to Use This Skill

Activate when users need:

- "Build a knowledge graph from documents"
- "Add persistent memory to an AI agent"
- "Create a RAG system with graph traversal"
- "Extract entities and relationships"
- "Query knowledge with semantic search"

## Core Concepts

### 1. ECL Pipeline (Extract-Cognify-Load)

```python
import cognee

# Extract: Add data
await cognee.add(content, dataset_name="my_dataset")

# Cognify: Transform into knowledge graph
await cognee.cognify()

# Load/Search: Query the knowledge
from cognee.api.v1.search import SearchType
results = await cognee.search("Your question", query_type=SearchType.GRAPH_COMPLETION)
```

### 2. Configuration

```python
import cognee
import os

# LLM Configuration
os.environ["LLM_API_KEY"] = "your-openai-key"
await cognee.config.set_llm_provider("openai")
await cognee.config.set_llm_model("gpt-4o-mini")

# Graph Database (Neo4j)
await cognee.config.set_graph_database_provider("neo4j")
await cognee.config.set_graph_database_url("bolt://localhost:7687")
await cognee.config.set_graph_database_username("neo4j")
await cognee.config.set_graph_database_password("password")

# Vector Database (LanceDB)
await cognee.config.set_vector_database_provider("lancedb")
await cognee.config.set_vector_database_url("./lancedb_data")

# Embedding Configuration
await cognee.config.set_embedding_provider("openai")
await cognee.config.set_embedding_model("text-embedding-3-large")
```

### 3. Data Ingestion

```python
# Single document
await cognee.add("Your document text", dataset_name="docs")

# Multiple documents
documents = ["doc1", "doc2", "doc3"]
for doc in documents:
    await cognee.add(doc, dataset_name="knowledge_base")
await cognee.cognify()

# File upload
with open("document.pdf", "rb") as f:
    await cognee.add(f, dataset_name="pdfs")

# With metadata
await cognee.add(content, dataset_name="posts")
await cognee.add(metadata, dataset_name="post_metadata")
await cognee.cognify()
```

### 4. Search Types

```python
from cognee.api.v1.search import SearchType

# Semantic vector search (fast)
results = await cognee.search(
    query_text="find similar concepts",
    query_type=SearchType.CHUNKS
)

# Graph-based insights (relationship-aware)
results = await cognee.search(
    query_text="how are these concepts related",
    query_type=SearchType.INSIGHTS
)

# Hybrid search with LLM reasoning (most powerful)
results = await cognee.search(
    query_text="complex multi-hop question",
    query_type=SearchType.GRAPH_COMPLETION,
    top_k=5
)

# Document summaries
results = await cognee.search(
    query_text="summarize the main themes",
    query_type=SearchType.SUMMARIES
)

# Code search
results = await cognee.search(
    query_text="authentication implementation",
    query_type=SearchType.CODE
)

# Direct Cypher queries
results = await cognee.search(
    query_text="MATCH (n:Entity) RETURN n",
    query_type=SearchType.CYPHER
)

# Automatic search type selection
results = await cognee.search(
    query_text="your question",
    query_type=SearchType.FEELING_LUCKY
)
```

### 5. Dataset Management

```python
# Scoped queries
await cognee.add(data1, dataset_name='dataset_a')
await cognee.add(data2, dataset_name='dataset_b')
await cognee.cognify()

# Search specific dataset
results = await cognee.search(
    query_text="query",
    node_name="dataset_a",
    top_k=5
)

# Clear all data
await cognee.prune.prune_data()

# Full system reset
await cognee.prune.prune_system(metadata=True)

# Delete specific data
await cognee.delete(data_id)
```

### 6. Visualization

```python
# Static visualization
await cognee.visualize_graph('/path/to/graph.html')

# Interactive server
await cognee.start_visualization_server()

# Network visualization
await cognee.cognee_network_visualization()
```

## Storage Backends

### Vector Stores
- **LanceDB** (default, local)
- **Qdrant Cloud**
- **PGVector** (PostgreSQL)
- **Weaviate**
- **FalkorDB**
- **Redis**

### Graph Databases
- **KuzuDB** (default, embedded)
- **Neo4j**
- **Neptune** (AWS)
- **Memgraph**
- **NetworkX** (in-memory)

## Dual-Engine Graph Architecture

For production AI memory systems, consider a **dual-engine strategy** that separates static knowledge from dynamic memory:

### Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                   Cognee Memory Layer                        │
├─────────────────────────────────────────────────────────────┤
│  ┌─────────────────────┐   ┌─────────────────────────────┐  │
│  │ Static Knowledge    │   │ Dynamic Memory              │  │
│  │ (Memgraph)          │   │ (FalkorDB via Graphiti)     │  │
│  │                     │   │                             │  │
│  │ - Validated facts   │   │ - Session context           │  │
│  │ - Domain ontology   │   │ - User interactions         │  │
│  │ - Reference data    │   │ - Episodic memories         │  │
│  │ - ACID guaranteed   │   │ - High write velocity       │  │
│  └─────────────────────┘   └─────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

### When to Use Dual-Engine

| Use Case | Static (Memgraph) | Dynamic (FalkorDB) |
|----------|-------------------|-------------------|
| Domain knowledge | ✅ | |
| Conversation history | | ✅ |
| Validated facts | ✅ | |
| Learning from interactions | | ✅ |
| Multi-hop reasoning | ✅ | |
| Session-specific context | | ✅ |

### Configuration Example

```python
import cognee

# Configure dual-engine setup
# Static knowledge graph (Memgraph)
await cognee.config.set_graph_database_provider("memgraph")
await cognee.config.set_graph_database_url("bolt://memgraph:7687")

# For dynamic memory, use Graphiti with FalkorDB
# (configured separately in your application layer)
from graphiti_core import Graphiti
from graphiti_core.graph import FalkorDBDriver

dynamic_memory = Graphiti(
    driver=FalkorDBDriver(host="falkordb", port=6379)
)
```

### Query Routing Strategy

```python
async def hybrid_search(query: str, session_id: str = None):
    # Static knowledge (always query)
    static_results = await cognee.search(
        query_text=query,
        query_type=SearchType.GRAPH_COMPLETION
    )

    # Dynamic memory (if session context exists)
    if session_id:
        dynamic_results = await dynamic_memory.search(
            query=query,
            center_node_uuid=session_id
        )
        return merge_results(static_results, dynamic_results)

    return static_results
```

### Data Promotion Pattern

Validated insights can be promoted from dynamic to static storage:

```python
async def promote_insight(insight_id: str):
    """Move validated insight from FalkorDB to Memgraph."""
    # Extract from dynamic memory
    insight = await dynamic_memory.get_node(insight_id)

    # Validate and transform
    if insight.confidence > 0.95 and insight.verification_count > 3:
        # Add to static knowledge
        await cognee.add(
            insight.content,
            dataset_name="validated_insights"
        )
        await cognee.cognify()

        # Optionally archive from dynamic
        await dynamic_memory.archive_node(insight_id)
```

## Integration Patterns

### DLT Integration

```python
import dlt
import cognee

@dlt.resource(write_disposition="merge", primary_key="id")
def data_source():
    yield data

# Load with DLT
pipeline = dlt.pipeline(
    pipeline_name="cognee_pipeline",
    destination="duckdb"
)
pipeline.run(data_source())

# Process with Cognee
await cognee.add(data, dataset_name="dlt_dataset")
await cognee.cognify()
```

### LangGraph Integration

```python
from langgraph.graph import StateGraph
import cognee

async def retrieve_context(state):
    results = await cognee.search(state["query"])
    return {"context": results}

workflow = StateGraph(...)
workflow.add_node("memory", retrieve_context)
```

### MCP Integration

```python
from cognee import MCP

# Expose cognee as MCP server
cognee_server = MCP()
cognee_server.start()

# Available functions:
# - cognify: Transform text into knowledge graphs
# - save_interaction: Capture conversations
# - search: Multi-mode semantic search
# - list_data: Display stored datasets
# - delete: Remove specific data
# - prune: Full memory reset
```

## Common Use Cases

1. **Conversational AI Memory**: Persistent context across sessions
2. **Document Q&A**: Query documentation as knowledge graph
3. **Code Intelligence**: Semantic code search
4. **Research Analysis**: Knowledge discovery from documents
5. **Enterprise Search**: Cited answers with sources
6. **Multi-Agent Memory**: Shared knowledge base for agents

## Environment Variables

```bash
# LLM
export LLM_API_KEY="your-openai-key"
export LLM_PROVIDER="openai"
export LLM_MODEL="gpt-4o-mini"

# Graph Database
export GRAPH_DATABASE_PROVIDER="neo4j"
export GRAPH_DATABASE_URL="bolt://localhost:7687"
export GRAPH_DATABASE_USERNAME="neo4j"
export GRAPH_DATABASE_PASSWORD="password"

# Vector Database
export VECTOR_DATABASE_PROVIDER="lancedb"
export VECTOR_DATABASE_URL="./lancedb_data"

# Embedding
export EMBEDDING_PROVIDER="openai"
export EMBEDDING_MODEL="text-embedding-3-large"
```

## Quick Reference

```python
import cognee
from cognee.api.v1.search import SearchType

# Setup
await cognee.config.set_llm_provider("openai")
await cognee.config.set_llm_api_key("your-key")

# Add data
await cognee.add(content, dataset_name="docs")

# Build knowledge graph
await cognee.cognify()

# Search
results = await cognee.search(
    query_text="your question",
    query_type=SearchType.GRAPH_COMPLETION
)

# Visualize
await cognee.visualize_graph('/path/to/graph.html')

# Clean up
await cognee.prune.prune_data()
```

## Best Practices

1. **Use Datasets**: Group related content in named datasets
2. **Choose Search Type**: CHUNKS for speed, GRAPH_COMPLETION for depth
3. **Incremental Updates**: Add data incrementally vs full reloads
4. **Async Operations**: All Cognee operations are async
5. **Configure First**: Set up LLM/databases before ingesting
6. **Visualize**: Use visualization to understand graph structure
7. **Monitor top_k**: Limit results for performance

## Troubleshooting

### No Results
- Verify data was cognified: `await cognee.cognify()`
- Try SearchType.FEELING_LUCKY

### Connection Failures
- Check database URLs and credentials
- Verify services are running

### High Memory
- Use `await cognee.prune.prune_data()`
- Process in batches

## Resources

- **Documentation**: https://docs.cognee.ai
- **GitHub**: https://github.com/topoteretes/cognee
- **Website**: https://www.cognee.ai
