# Memory Systems Capability

## Purpose

`memory-systems` is a capability of the Cianfhoghlaim platform. This document is the canonical capability spec; the corresponding source code lives in the appropriate quadrant. See `docs/00_index.md` for the quadrant map and `docs/00-core/CLAUDE.md` for the project identity.


## Background
Knowledge graph memory systems, temporal tracking, episodic memory, and persistent agent memory with multi-backend support.

## Requirements

### Requirement: Temporal Knowledge Graphs
The system SHALL track relationships and entities over time.

#### Scenario: Episode Creation
- **GIVEN** a knowledge graph with temporal tracking
- **WHEN** an episode is added
- **THEN** entities and relationships are extracted with timestamps

#### Scenario: Point-in-Time Queries
- **GIVEN** a knowledge graph with historical data
- **WHEN** querying as of a specific time
- **THEN** results reflect the state at that time

#### Scenario: Temporal Comparison
- **GIVEN** two points in time
- **WHEN** comparing knowledge states
- **THEN** changes between time periods are identified

### Requirement: Episodic Memory
The system SHALL store and retrieve agent experiences.

#### Scenario: User Interaction Storage
- **GIVEN** an agent with episodic memory
- **WHEN** a user interaction occurs
- **THEN** interaction is stored as an episode with metadata

#### Scenario: Episode Retrieval
- **GIVEN** stored episodes
- **WHEN** querying for relevant experiences
- **THEN** related episodes are returned based on context

### Requirement: Knowledge Graph Traversal
The system SHALL support graph-based queries.

#### Scenario: Entity Relationship Query
- **GIVEN** a knowledge graph with connected entities
- **WHEN** querying for relationships
- **THEN** related entities and relationships are returned

#### Scenario: Path Finding
- **GIVEN** two entities in the graph
- **WHEN** finding the shortest path
- **THEN** path with intermediate entities is returned

### Requirement: Hybrid Search
The system SHALL combine vector and graph search.

#### Scenario: Semantic Search
- **GIVEN** a knowledge graph with vector embeddings
- **WHEN** searching with a text query
- **THEN** semantically similar entities are returned

#### Scenario: Graph Completion
- **GIVEN** a knowledge graph with relationships
- **WHEN** asking a multi-hop question
- **THEN** answer is derived by traversing relationships

### Requirement: Multi-Backend Support
The system SHALL support multiple storage backends.

#### Scenario: Vector Database Selection
- **GIVEN** a memory system with multiple vector DB options
- **WHEN** configuring the system
- **THEN** appropriate vector DB can be selected (LanceDB, Qdrant, etc.)

#### Scenario: Graph Database Selection
- **GIVEN** a memory system with multiple graph DB options
- **WHEN** configuring the system
- **THEN** appropriate graph DB can be selected (Neo4j, Memgraph, etc.)

## Supported Frameworks

### Graphiti Core (>=0.5.0)

**Key Features:**
- Temporal tracking of relationships and entities over time
- Episodic memory for storing agent experiences
- Bi-temporal model (valid time + transaction time)
- Entity and relationship extraction from text
- Point-in-time queries for historical analysis
- Graph traversal for relationship exploration
- Neo4j backend with optional FalkorDB support

**Documentation:** https://github.com/getmemex/graphiti

**Skill:** [`.skills/graphiti-core/SKILL.md`](.skills/graphiti-core/SKILL.md)

### Cognee (>=0.1.0)

**Key Features:**
- Knowledge graphs from documents and text
- Semantic search with vector + graph hybrid approach
- Persistent memory for AI agents
- Multi-backend support (vector and graph databases)
- Graph traversal for context-aware retrieval
- Temporal tracking of knowledge changes
- Multi-modal support (text, images, structured data)
- ECL pipeline (Extract-Cognify-Load)
- Multiple search types (CHUNKS, INSIGHTS, GRAPH_COMPLETION, etc.)

**Documentation:** https://docs.cognee.ai

**Skill:** [`.skills/cognee/SKILL.md`](.skills/cognee/SKILL.md)

### LanceDB (>=0.15.0)

**Key Features:**
- Embedded vector database without separate server
- Multimodal storage (vectors, text, images, audio)
- HNSW indexing for high-performance search
- MVCC safety for concurrent operations
- Hybrid search combining vector and full-text search
- S3-compatible storage with serverless option
- Billion-scale vectors with disk-based indexes

**Documentation:** https://lancedb.github.io/lancedb/

**Skill:** [`.skills/lancedb/SKILL.md`](.skills/lancedb/SKILL.md)

## Memory Patterns

### Episodic Memory with Graphiti

```python
from graphiti_core import Graphiti
from graphiti_core.nodes import EpisodeType
from datetime import datetime

client = Graphiti(
    neo4j_url="bolt://localhost:7687",
    neo4j_user="neo4j",
    neo4j_password="password"
)

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
```

### Knowledge Graph with Cognee

```python
import cognee
from cognee.api.v1.search import SearchType

# Extract: Add data
await cognee.add(content, dataset_name="my_dataset")

# Cognify: Transform into knowledge graph
await cognee.cognify()

# Load/Search: Query the knowledge
results = await cognee.search(
    "Your question", 
    query_type=SearchType.GRAPH_COMPLETION
)
```

### Vector Search with LanceDB

```python
import lancedb

# Connect
db = lancedb.connect("data/my-database")

# Create table
data = [
    {"id": 1, "text": "Hello world", "vector": [0.1] * 128},
    {"id": 2, "text": "Goodbye world", "vector": [0.2] * 128}
]
table = db.create_table("documents", data=data)

# Search
query_vector = [0.15] * 128
results = table.search(query_vector).limit(10).to_pandas()
```

### Hybrid Search

```python
# Cognee hybrid search
results = await cognee.search(
    query_text="complex multi-hop question",
    query_type=SearchType.GRAPH_COMPLETION,
    top_k=5
)

# LanceDB hybrid search
results = (table.search(query_type="hybrid")
          .vector(query_vector)
          .text("machine learning")
          .limit(10)
          .rerank(method="rrf")
          .to_pandas())
```

## Episode Types

| Type | Description | Use Case |
|------|-------------|----------|
| `user_interaction` | User-agent conversations | Chat sessions, queries |
| `system_event` | System-level events | Errors, state changes |
| `curriculum_change` | Curriculum updates | Syllabus modifications |
| `learning_progress` | Student progress | Assessment results, milestones |
| `knowledge_update` | Knowledge base updates | New information added |

## Search Types

| Type | Purpose | Speed | Depth |
|------|----------|-------|-------|
| `CHUNKS` | Semantic vector search | Fast | Shallow |
| `INSIGHTS` | Graph-based insights | Medium | Medium |
| `GRAPH_COMPLETION` | Multi-hop reasoning | Slow | Deep |
| `SUMMARIES` | Document summaries | Fast | Shallow |
| `CODE` | Code search | Medium | Medium |
| `FEELING_LUCKY` | Automatic type selection | Variable | Variable |
| `CYPHER` | Direct graph queries | Fast | Deep |

## Storage Backends

### Vector Stores

| Backend | Use Case | Notes |
|---------|----------|-------|
| LanceDB | Local/cloud vector storage | Default, embedded |
| Qdrant Cloud | Managed vector service | Scalable |
| PGVector | PostgreSQL extension | Existing Postgres |
| Weaviate | Open-source vector search | GraphQL API |
| FalkorDB | Redis-based | High performance |
| Redis | In-memory caching | Fast access |

### Graph Databases

| Backend | Use Case | Notes |
|---------|----------|-------|
| KuzuDB | Embedded graph DB | Default, ACID |
| Neo4j | Enterprise graph DB | Production, Cypher |
| Neptune | AWS graph service | Cloud-native |
| Memgraph | In-memory graph | Fast, ACID |
| NetworkX | In-memory graphs | Analytics, research |

## Dual-Engine Architecture

For production AI memory systems, consider a dual-engine strategy:

### Architecture Overview

```
┌─────────────────────────────────────────────────────────────┐
│                   Memory Layer                        │
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

### Data Ingestion
1. **Incremental Updates**: Add data incrementally vs full reloads
2. **Dataset Organization**: Group related content in named datasets
3. **Async Operations**: All memory operations are async

## Configuration

### Graphiti Core Configuration

```python
from graphiti_core import Graphiti
from graphiti_core.llm_client import OpenAIClient

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

### Cognee Configuration

```python
import cognee

# LLM Configuration
await cognee.config.set_llm_provider("openai")
await cognee.config.set_llm_model("gpt-4o-mini")

# Graph Database (Neo4j)
await cognee.config.set_graph_database_provider("neo4j")
await cognee.config.set_graph_database_url("bolt://localhost:7687")

# Vector Database (LanceDB)
await cognee.config.set_vector_database_provider("lancedb")
await cognee.config.set_vector_database_url("./lancedb_data")

# Embedding Configuration
await cognee.config.set_embedding_provider("openai")
await cognee.config.set_embedding_model("text-embedding-3-large")
```

### LanceDB Configuration

```python
import lancedb

# Local connection
db = lancedb.connect("data/my-database")

# Cloud connection
db = lancedb.connect("db://my-database", api_key="...", region="us-east-1")

# S3 connection
db = lancedb.connect("s3://my-bucket/lancedb")
```

## Integration with Other Systems

### Agent Integration
- **Agno**: Memory backend for agent conversations
- **Google ADK**: Vector store for agent memory

### Data Pipeline Integration
- **Dagster**: Memory updates as assets
- **DLT**: Load data into knowledge graphs

### Observability Integration
- **Langfuse**: Trace memory operations
- **RAGAS**: Evaluate memory retrieval quality

## Index Selection Guide

| Scenario | Index Type | Parameters |
|----------|-----------|------------|
| <100K vectors | None (brute force) | - |
| Memory constrained | IVF_PQ | num_partitions=256 |
| Accuracy critical | HNSW | m=20, ef_construction=150 |
| Large scale | IVF_HNSW_PQ | Combine both |

## Troubleshooting

### Slow Searches
- Create an index for datasets >100K
- Use pre-filtering for selective filters
- Check if compaction is needed

### Out of Memory
- Use disk-based indexes (IVF-PQ)
- Enable compression with Float16
- Query with projections

### Schema Mismatch
- Verify vector dimensions match
- Check data types in schema

### No Results
- Verify data was cognified: `await cognee.cognify()`
- Try different search types
- Check query format matches expected input
