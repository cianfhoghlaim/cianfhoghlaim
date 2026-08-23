---
name: cognee
description: Expert assistance for AI memory systems with Cognee. Use when users need knowledge graphs, semantic search, RAG applications, persistent agent memory, or transforming documents into queryable knowledge.

## What's new in 2026-08/09

This skill was refreshed as part of the 2026-08-23 omnibus skill refresh
(per the  change). Key
updates:

- **2026-08 tooling**: aligned with the latest versions of upstream
  libraries (per the dev-tooling version-pinning change)
- **2026-08 patterns**: documented new features surfaced via the
  Phase 3 (surfaces round) refactor
- **Cross-references**: linked to adjacent skills (per the AGENTS.md
  dispatch matrix)

See the linked spec changes for full details.

---

# Cognee - AI Memory Platform

**Version:** >=1.0.0,<2 (v1.0 surface) — verified against **cognee 1.2.2** (PyPI 2026-06-26) | **Last Updated:** 2026-06-29
**Live docs root:** https://docs.cognee.ai (Mintlify) | **Verified URLs:** `/getting-started/{installation,quickstart}`, `/python-api`, `/python-api/{remember,recall,search-type}`, `/cognee-mcp/{mcp-overview,mcp-tools}` | **llms.txt:** https://docs.cognee.ai/llms.txt
**Python:** >=3.10,<3.15 | **Default LLM:** openai/gpt-5-mini | **Default embeddings:** openai/text-embedding-3-large (3072-d)

## Overview

Cognee is an open-source AI memory platform that transforms data into persistent, dynamic memory:

- **Knowledge Graphs**: Extract entities and relationships from text
- **Semantic Search**: Vector + graph hybrid search
- **Persistent Memory**: Long-term memory for AI agents
- **Multi-Backend**: Support for various graph and vector databases
- **Graph Traversal**: Navigate relationships for context-aware retrieval
- **Temporal Tracking**: Track knowledge changes over time
- **Multi-Modal**: Support text, images, and structured data

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

## KCG Quick Start

The Cianfhoghlaim deployment of Cognee is a **Docker container on port 8100**, using **DeepSeek V4 Pro** (via the OpenAI-compatible API), **Neo4j** for the graph backend, and **LanceDB** for vector storage:

```bash
# 1. Start the cognition infrastructure (Neo4j, Graphiti, FalkorDB)
cd infrastructure/stacks/graphiti && docker compose up neo4j -d
cd ../falkordb && docker compose up -d

# 2. Start Cognee with DeepSeek API key (from Infisical)
cd ../cognee
DEEPSEEK_API_KEY="$DEEPSEEK_API_KEY" docker compose up -d
sleep 10
curl -s http://localhost:8100/docs | head -5  # Swagger HTML

# 3. Index the codebase
bun run ccc:index

# 4. Cognify the docs (6 datasets, ~$6 total on DeepSeek V4 Pro)
for ds in docs-agents docs-bonneagar docs-data-eng docs-ml docs-web docs-context; do
  curl -X POST http://localhost:8100/api/v1/cognify \
    -H "Content-Type: application/json" \
    -d "{\"datasets\": [\"$ds\"]}"
done
```

The **8 MCP servers** wired in `opencode.json` give every agent
read access to the cognition stack: `cognee`, `cocoindex-code`,
`graphiti`, `langfuse`, `firecrawl`, `browserbase`, `chrome`,
`motherduck`, `infisical`.

See `references/cognee-readme.md` (the 80-line
`docs/01-cognee/README.md` index) for the full quick-start
table, the per-file purpose list, and the MCP server inventory.

## KCG Architecture Diagram

The 8-stack cognition pipeline that turns `docs/` into a
queryable knowledge graph, accessible to agents via MCP and
applications via REST:

```
.md documentation  ──────▶  Cognee (port 8100, DeepSeek V4 Pro)
docs/agents/                       │ ingest + KG
docs/bonneagar/                    │
docs/data_engineering/             ▼
                              Neo4j (KG) + LanceDB (vectors)
                                   │
                       ┌───────────┼────────────┐
                       ▼           ▼            ▼
                  Graphiti    FalkorDB     Langfuse
                (temporal KG)  (hybrid)    (traces @ :3000)
                  @ :8000      @ :6379
                       │           │            │
                       └───────────┼────────────┘
                                   ▼
                    CCC ◀────  Lakehouse  ────▶  LakeFS
                  (.cocoindex)  (Garage S3)      (versioning)
                                Iceberg + Lance
                                   │
                                   ▼
                           Dozzle + Beszel
                          (logs + metrics)
```

Each component owns a clear surface: Cognee ingests + extracts
entities; Graphiti adds bi-temporal metadata; FalkorDB does
sub-millisecond hybrid (Cypher + HNSW); Langfuse captures cost
+ latency for every LLM call; CCC indexes the codebase;
Lakehouse is the single Parquet/Lance/Iceberg namespace;
LakeFS branches datasets for experiments; Dozzle + Beszel
monitor.

See `references/architecture/ARCHITECTURE.md` for the full
component-role table, the end-to-end data flow, and the
agent-access matrix.

## KCG Docker Stack

The KCG Cognee container runs `cognee/cognee:latest`
(v1.1.2) on **port 8100** with the following
`compose.yaml` shape:

```yaml
services:
  cognee:
    image: cognee/cognee:latest
    ports: ["8100:8000"]
    environment:
      LLM_API_KEY: ${DEEPSEEK_API_KEY}      # hydrated from Infisical
      LLM_PROVIDER: openai                  # DeepSeek is OpenAI-compatible
      LLM_MODEL: deepseek-chat              # DeepSeek V4 Pro
      LLM_ENDPOINT: https://api.deepseek.com/v1
      EMBEDDING_PROVIDER: openai
      EMBEDDING_MODEL: text-embedding-3-small
      GRAPH_DATABASE_PROVIDER: neo4j
      GRAPH_DATABASE_URL: bolt://host.docker.internal:7687
      VECTOR_DATABASE_PROVIDER: lancedb
```

The 8 API endpoints (`/api/v1/{add,cognify,search,auth/...}`)
accept multipart form uploads for batch ingestion. The MCP
server is `cognee-mcp` in `opencode.json`, exposing
`cognee_search` to every agent.

Common failure modes: `LLMAPIKeyNotSetError` (check
`DEEPSEEK_API_KEY`); `RateLimitError` (reduce concurrent
cognify batches); search returns no results (re-run
`cognify()` after `add()`).

See `references/docker/COGNEE_SETUP.md` for the full 190-line
setup guide, the Docker Compose configuration, the API
endpoint reference, the ingestion patterns (HTTP + Python),
and the troubleshooting matrix.

## KCG Per-Cluster Cognify Model

The `cognee_readiness_audit` (517 lines, the
round-1 audit) recommended **per-cluster cognify** over a
single flat graph, to avoid entity-namespace collisions
(e.g. `Token` = crypto in `bonneagar/` vs LLM in
`meaisínfhoghlaim/`) and to enable incremental updates.

The **7 typed clusters** + their `graph_model_file` Python
modules:

| Cluster | Dataset | Graph model | Core entities |
|:--|:--|:--|:--|
| Data Platform | `docs-data-eng` | `data_platform_graph.py` | DagsterAsset, DltPipeline, LakehouseTable, CocoIndexFlow, LanceDBIndex, SqlMeshModel |
| Infrastructure | `docs-bonneagar` | `infrastructure_graph.py` | KomodoStack, PangolinTunnel, DaggerPipeline, PulumiResource, AnsibleRole |
| Agents & MCP | `docs-agents` | `agents_graph.py` | McpServer, AgentTool, LlmAgent, BamlSchema, BrowserSession |
| ML & AI | `docs-ml` | `ml_graph.py` | FineTunedModel, TrainingDataset, MlflowExperiment, UnslothConfig, LanceDBCollection |
| Celtic Language | `docs-teanga` | `celtic_language_graph.py` | LanguageDataset, HuggingFaceModel, GaeltachtBoundary, CensusTable |
| Web & Frontend | `docs-web` | `web_graph.py` | TanStackRoute, ConvexQuery, BetterAuthProvider, EffectService |
| Tuatha MMO | `docs-tuatha` | `tuatha_graph.py` | GameAsset, SpacetimeDBTable, X402Payment, NpcCharacter |

A federated search layer queries all 7 datasets and re-ranks
merged results by score. Total estimated cognify cost: **~$6
for 2,242 documents on DeepSeek V4 Pro**.

The **5 rules of cognify-clean docs** (entity density 15+ per
100 words, relationship verbs, section boundaries, tables for
entity catalogs, no redirect stubs) are the audit's scoring
rubric; ~80% of `docs/` is A-grade on the rubric.

See `references/cluster-model/cognee_readiness_audit.md` for
the full 517-line audit: the per-subtree scoring (8 subtrees ×
4 sample files), the entity-density rubric, the
BEFORE/AFTER cognify-clean rewrite example, the
`data_platform_graph.py` template with 7 entity classes + 12
relationship types, and the single-vs-per-cluster
recommendation rationale.

## Supporting Infrastructure

The 4 supporting stacks the cognition pipeline depends on
(Lakehouse, LakeFS, Dozzle, Beszel), with their roles and
KCG-specific ports:

| Stack | Stack path | Port | Role in cognition pipeline |
|:--|:--|:--|:--|
| **Lakehouse** | `infrastructure/stacks/lakehouse/` | 3900-3904 (Garage S3), 8181 (Lakekeeper), 8182 (Lance Namespace) | Single Parquet + Lance + Iceberg namespace; ACID transactions between Dagster writes (cognify) and app reads (GraphRAG) |
| **Dozzle** | `infrastructure/stacks/dozzle/` | 8080 | Real-time container logs (cognee, graphiti-neo4j-1, falkordb, langfuse-*) |
| **Beszel** | `infrastructure/stacks/beszel/` | 8090 | Host metrics across `cax41-hetzner` (32 GB), `arm1-oci` (24 GB), `bunchloch` (48 GB unified) |

The **Iceberg time-travel** capability (via Lakekeeper) lets
you query "what was in Cognee's KG after last month's cognify
run?". The **LakeFS branch + merge** flow enables experiment
isolation: test a new Cognee model on a branch, validate
extraction quality, merge to production.

A single combined health check (`cognee`, `Neo4j`, `FalkorDB`,
`Garage`, `LakeFS`, `Dozzle`, `Beszel`, `CCC` index) lives in
the reference; recommended alerts: `bunchloch_memory > 40 GB`
(reduce concurrent cognify batches), `hetzner_disk > 80%`
(LanceDB indexes growing), `arm1_cpu > 90% sustained 5min`
(S3 writes saturating).

See `references/infrastructure/INFRASTRUCTURE.md` for the
full 176-line reference: per-stack deployment commands, the
LakeFS branch/merge workflow, the Dozzle key log patterns
(ingestion progress, cognify status, LLM API errors), the
Beszel alert matrix, and the combined health-check script.

## Resources

- **Documentation**: https://docs.cognee.ai
- **GitHub**: https://github.com/topoteretes/cognee
- **Website**: https://www.cognee.ai

## 2026-06 update: temporal cognify + session memory + auto-routing

Cognee 0.1+ adds the 3 features below that the KCG curriculum pipeline uses.

### Temporal cognify

The new `cognify` accepts a `time_range` parameter to scope the knowledge graph to a specific time window. Use this for any "what did the curriculum look like in 2024?" question:

```python
import cognee

await cognee.cognify(
    time_range=("2024-01-01", "2024-12-31"),
    dataset="cianfhoghlaim_2024",
)
```

The graph stores the temporal context as a first-class node, so a query about "the 2024 syllabus" returns only the 2024 facts (not the 2025 revision).

### Session memory + `improve()`

Sessions let you store Q&A without the full cognify pipeline, then later bridge the session into the permanent graph:

```python
# Phase 1: fast session storage
await cognee.remember(session_id="agent_42", data="agent Q&A pair")

# Phase 2 (later): bridge session to permanent graph
await cognee.improve(
    dataset_name="main_dataset",
    session_ids=["agent_42", "agent_43", "agent_44"],
)
```

The 4-stage `improve()` pipeline: (1) apply feedback weights to graph nodes/edges, (2) persist session Q&A into the permanent graph, (3) enrich graph with triplet embeddings (memify), (4) sync enriched graph back into session caches.

### Auto-routing search (`recall()`)

The new `recall()` function picks the best search strategy automatically. When a `session_id` is provided, it first searches the session cache, then falls through to the permanent graph:

```python
results = await cognee.recall(
    query="What changed in the JC maths syllabus?",
    session_id="agent_42",
    top_k=10,
)
# -> First checks session cache by keyword match
# -> Falls through to GRAPH_COMPLETION on the permanent graph
```

The available search types (per `SearchType` enum) are: `GRAPH_COMPLETION`, `GRAPH_COMPLETION_COT`, `RAG_COMPLETION`, `CHUNKS`, `SUMMARIES`, `TEMPORAL`, `FEELING_LUCKY`. Override with `search_type=...`.

For the KCG curriculum pipeline specifically, the `cocoindex/cognee_integration/cross_stage_cognify.py` uses these features to:

- Store 5-stage cognify (Aistear → Primary → JC → SC → Tertiary)
- Run `improve()` after each agent session
- Use `recall(session_id=...)` to surface the 2024 vs 2025 syllabus facts

## See also

- **[`../INDEXING_AND_COGNITION.md`](../INDEXING_AND_COGNITION.md)** — Consolidated setup + MCP reference for both `ccc` (semantic code search) and `cognee` (knowledge graph over docs). Includes current state, first-time setup, daily-use commands, MCP tool inventory for both, dual-search workflow, and troubleshooting matrix. Read this when an agent or team member asks "how do I set up cognee?", "what MCP tools are available?", or "how do I run cognify against the docs?".

## Live version (verified 2026-06-29, Agent 79)

- **Latest**: `cognee 1.2.2` (PyPI 2026-06-26). The v1.0+ surface uses `remember` / `recall` (replaces the legacy `add` + `cognify` + `search` ECL pipeline).
- **Search types**: 15 values; `GRAPH_COMPLETION` is default. Verbatim: `SUMMARIES, CHUNKS, CHUNKS_LEXICAL, RAG_COMPLETION, TRIPLET_COMPLETION, GRAPH_COMPLETION (default), GRAPH_COMPLETION_DECOMPOSITION, GRAPH_SUMMARY_COMPLETION, CYPHER, NATURAL_LANGUAGE, GRAPH_COMPLETION_COT, GRAPH_COMPLETION_CONTEXT_EXTENSION, FEELING_LUCKY, TEMPORAL, CODING_RULES`.
- **Per-call override**: `LLMConfig(provider="anthropic", model="claude-3-5-sonnet", api_key="...")` via `cognee.infrastructure.llm.config`.
- **Dataset delete**: `await cognee.forget(everything=True)` (v1.0 clean-slate) or `await cognee.forget(dataset="<name>")`. The legacy `cognee.prune.prune_data()` is deprecated.
