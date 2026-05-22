# Meaisínfhoghlaim - Machine Learning & AI

Meaisínfhoghlaim handles data ingestion, model training, knowledge graph construction, and AI agent orchestration for the Celtic Education Platform. This stream provides the ML/AI foundation for curriculum processing, semantic search, and intelligent tutoring.

## Tech Stack Overview

### Data Orchestration
| Package | Version | Purpose |
|---------|---------|---------|
| **dagster** | >=1.9.0 | Data orchestration platform with asset-based pipelines |
| **dlt** | >=1.4.0 | Data load tool for Pythonic pipelines with streaming support |
| **duckdb** | >=1.1.0 | In-process analytical database for local data processing |
| **lancedb** | >=0.15.0 | Vector database with HNSW indexing and MVCC safety |
| **neo4j** | >=5.0.0 | Graph database for relationship modeling |

### Machine Learning & Embeddings
| Package | Version | Purpose |
|---------|---------|---------|
| **sentence-transformers** | >=3.0.0 | State-of-the-art sentence embeddings |
| **transformers** | >=4.45.0 | Pre-trained models and tokenizers |
| **torch** | >=2.4.0 | Deep learning framework with GPU acceleration |
| **accelerate** | >=1.0.0 | PyTorch optimization for multi-GPU training |

### Agent Frameworks
| Package | Version | Purpose |
|---------|---------|---------|
| **google-adk** | >=0.1.0 | Google's Agent Development Kit for multi-agent coordination |
| **agno** | >=2.0.0 | Multi-agent orchestration with knowledge graphs |
| **litellm** | Latest | Unified interface for 100+ LLM providers |
| **cocoindex** | >=0.1.0 | Indexing and search for unstructured data |

### Memory & Knowledge Systems
| Package | Version | Purpose |
|---------|---------|---------|
| **graphiti-core** | >=0.5.0 | Temporal knowledge graph with bi-temporal model |
| **cognee** | >=0.1.0 | Graph-based knowledge management with temporal tracking |

### Model Training & Fine-tuning
| Package | Version | Purpose |
|---------|---------|---------|
| **unsloth** | >=2024.12 | LLM fine-tuning with 2x faster training |
| **trl** | >=0.12.0 | Transformer Reinforcement Learning for fine-tuning |
| **datasets** | >=3.0.0 | Hugging Face datasets for training |
| **mlflow** | >=2.18.0 | ML experiment tracking and model registry |
| **wandb** | >=0.18.0 | Experiment tracking and visualization |

### Observability & Evaluation
| Package | Version | Purpose |
|---------|---------|---------|
| **langfuse** | >=2.0.0 | LLM observability with tracing and evaluation |
| **ragas** | >=0.1.10 | RAG evaluation with trace-based metrics |
| **ddtrace** | >=2.15.0 | Datadog APM tracing |
| **opentelemetry-sdk** | >=1.28.0 | OpenTelemetry instrumentation |

## Key Features & Capabilities

### Data Ingestion & Processing
- **DLT Pipelines**: Pythonic data pipelines with streaming support and schema inference
- **Dagster Assets**: Observable, partitioned data assets with lineage tracking
- **Incremental Loading**: Cursor-based extraction for efficient updates
- **DuckDB Integration**: Local analytical processing with zero-egress design

### Vector Search & Retrieval
- **LanceDB**: High-performance vector database with HNSW indexing
- **Hybrid Search**: Combine semantic and keyword search for better relevance
- **MVCC Safety**: Concurrent operations with snapshot isolation
- **Multi-modal Support**: Text, image, and audio embeddings

### Knowledge Graphs
- **Graphiti-Core**: Temporal knowledge graph tracking changes over time
- **Cognee**: Graph-based knowledge management with graph traversal
- **Bi-temporal Model**: Track valid time and transaction time
- **Episodic Memory**: Store and retrieve contextual episodes

### Model Training & Fine-tuning
- **Unsloth**: Fast LLM fine-tuning with flash attention
- **Multi-lingual Support**: Train models for Irish, Welsh, Scottish Gaelic
- **Experiment Tracking**: MLflow and Weights & Biases integration
- **Model Registry**: Versioned model storage and deployment

### Agent Orchestration
- **Multi-Agent Coordination**: Sequential and parallel workflows via Google ADK
- **Knowledge Graph Memory**: Persistent memory across agent sessions
- **Tool Integration**: MCP protocol for agent-tool communication
- **Unified LLM Interface**: LiteLLM for 100+ provider support

### Observability
- **Full Tracing**: End-to-end tracing via Langfuse and OpenTelemetry
- **RAG Evaluation**: Faithfulness, answer relevance, and context metrics
- **Infrastructure Monitoring**: Datadog APM for performance insights
- **Experiment Tracking**: MLflow and W&B for ML experiments

## Latest Package Updates (April 2026)

### Dagster v1.9.0
- Asset-based pipelines with observability
- Partitioning support for time-series data
- Improved sensor and schedule definitions

### DLT v1.4.0
- Streaming support for real-time data
- Schema inference for automatic type detection
- Improved incremental loading with cursors

### LanceDB v0.15.0
- HNSW indexing for faster vector search
- MVCC safety for concurrent operations
- Hybrid search combining semantic and keyword

### Graphiti-Core v0.5.0
- Bi-temporal model for temporal tracking
- Episodic memory for contextual retrieval
- Improved graph traversal algorithms

### Cognee v0.1.0
- Graph traversal for relationship queries
- Temporal tracking for evolving data
- Multi-modal support for text, images, audio

### Unsloth 2024.12
- Multi-lingual support for Celtic languages
- Flash attention for 2x faster training
- Improved memory efficiency

### Ragas v0.1.10
- Trace-based metrics for deeper insights
- Faithfulness and answer relevance evaluation
- Support for multi-modal RAG

## Directory Structure

```
sruth/meaisínfhoghlaim/
├── agents/              # AI agent implementations
│   ├── api/            # Agent API endpoints
│   └── routes/         # Agent routing
├── alignment/          # Alignment and safety tools
├── catalog/            # Data catalog and metadata
├── evaluation/         # Model evaluation and testing
├── language/           # Language processing and NLP
├── notebooks/          # Jupyter notebooks for experiments
├── ocr/               # OCR and document processing
├── pipelines/          # DLT and Dagster pipelines
├── quality/            # Data quality and validation
├── adk/               # Google ADK agent implementations
├── agno/              # Agno framework agents
├── cocoindex_flows/    # CocoIndex integration
├── dlt_sources/       # DLT data sources
├── dlt_utils/         # DLT utilities
├── embeddings/         # Embedding generation and storage
├── graph/             # Knowledge graph operations
├── memory/            # Memory systems and retrieval
├── observability/      # Observability integrations
├── rag/               # RAG implementations
├── search/            # Search and retrieval
├── services/          # ML services and APIs
├── training/          # Model training scripts
├── ui/                # ML UI components
├── visualization/      # Data visualization tools
└── README.md          # This file
```

## Quick Start

### Data Ingestion with DLT

```python
import dlt
from sruth.meaisínfhoghlaim.dlt_sources import curriculum_source

# Create pipeline
pipeline = dlt.pipeline(
    pipeline_name="curriculum_ingestion",
    destination="duckdb",
    dataset_name="education",
)

# Ingest curriculum data
pipeline.run(curriculum_source(
    cycle="junior_cycle",
    language="en",
))
```

### Dagster Assets

```python
from dagster import asset
from sruth.meaisínfhoghlaim.pipelines import process_curriculum

@asset
def curriculum_embeddings():
    """Generate embeddings for curriculum documents"""
    return process_curriculum.generate_embeddings()

@asset(deps=[curriculum_embeddings])
def vector_index(embeddings):
    """Build vector index for search"""
    return lancedb.create_index(embeddings)
```

### Vector Search with LanceDB

```python
import lancedb
from sentence_transformers import SentenceTransformer

# Connect to LanceDB
db = lancedb.connect("./lancedb")
table = db.open_table("curriculum")

# Generate embeddings
model = SentenceTransformer('all-MiniLM-L6-v2')
query_embedding = model.encode("Irish history curriculum")

# Search
results = table.search(query_embedding).limit(10).to_pandas()
```

### Knowledge Graph with Graphiti

```python
from graphiti_core import GraphitiClient
from datetime import datetime

# Initialize client
client = GraphitiClient()

# Add episode
episode = await client.add_episode(
    name="Curriculum Update",
    episode_body="Added data science to Junior Cycle Mathematics",
    reference_time=datetime(2025, 4, 23),
    episode_type=EpisodeType.knowledge_update
)

# Query relationships
results = await client.search(
    query="How does Irish history relate to cultural identity?",
    limit=5
)
```

### Agent Orchestration with Agno

```python
from agno import Agent, KnowledgeGraph

# Create agent with knowledge graph
agent = Agent(
    name="curriculum_agent",
    knowledge_graph=KnowledgeGraph(),
    tools=[search_tool, embedding_tool]
)

# Run agent
result = agent.run("Find all Junior Cycle mathematics topics")
```

## Related Documentation

- [.skills/dagster/SKILL.md](../../.skills/dagster/SKILL.md) - Dagster orchestration
- [.skills/dlt/SKILL.md](../../.skills/dlt/SKILL.md) - DLT data pipelines
- [.skills/lancedb/SKILL.md](../../.skills/lancedb/SKILL.md) - LanceDB vector database
- [.skills/graphiti-core/SKILL.md](../../.skills/graphiti-core/SKILL.md) - Temporal knowledge graphs
- [.skills/cognee/SKILL.md](../../.skills/cognee/SKILL.md) - Graph-based knowledge management
- [.skills/unsloth/SKILL.md](../../.skills/unsloth/SKILL.md) - LLM fine-tuning
- [.skills/langfuse/SKILL.md](../../.skills/langfuse/SKILL.md) - LLM observability
- [.skills/ragas/SKILL.md](../../.skills/ragas/SKILL.md) - RAG evaluation

## Deployment

- **Development**: Local on MacBook M4 Max (48GB unified memory)
- **Production**: Komodo stacks with zero-egress design
- **Storage**: DuckDB (local) + LanceDB (vectors) + Neo4j (graphs)
- **Observability**: Langfuse, MLflow, Datadog, W&B

## Architecture

Meaisínfhoghlaim follows a layered architecture:

1. **Data Layer**: DLT sources, Dagster assets, DuckDB storage
2. **Processing Layer**: Embeddings, OCR, language processing
3. **Memory Layer**: LanceDB (vectors), Graphiti (temporal graphs), Cognee (knowledge)
4. **Agent Layer**: Google ADK and Agno for multi-agent orchestration
5. **Training Layer**: Unsloth, TRL, MLflow for model training
6. **Observability Layer**: Langfuse, Ragas, Datadog for monitoring

## Infrastructure Strategy

All ML workloads are converged on the **48GB MacBook M4 Max (`bunchloch`)**:

- **Reason**: ML inference and vector graph processing are memory-intensive
- **Benefit**: 48GB unified memory allows large local embedding models
- **Performance**: High-concurrency crawling without swapping
- **Privacy**: Zero-egress design keeps data local

## Core Components

### Crawl4AI (Scraping & Ingestion)
- **Benefit**: High-performance, LLM-optimized web crawling
- **Role**: Extracts curriculum content from NCCA and SEC websites
- **April 2026 Features (v0.8.6)**: Adaptive web crawling, deep crawl crash recovery, Cloud API Beta

### Langfuse (Observability & Evaluation)
- **Benefit**: Full lifecycle tracking for LLM applications
- **Role**: Traces every interaction with Gemini/GPT models
- **April 2026 Features (v3.169.0)**: Experiments as first-class concept, Hosted MCP Server, Agent Observability UI

### Cognee (AI Memory & GraphRAG)
- **Benefit**: Automated construction of queryable knowledge graphs
- **Role**: Implements GraphRAG for understanding curriculum relationships
- **April 2026 Features (v1.0.1)**: Claude Code Memory Plugin, faster duplicate detection

### Perplexica / Vane (Research Engine)
- **Benefit**: Self-hosted, privacy-first AI search engine
- **Role**: Research interface for Celtic linguistics and educational policy

## Contributing

When adding new packages or updating existing ones:

1. Update Tech Stack Overview table
2. Add relevant skills documentation to `.skills/`
3. Test with Dagster assets before production deployment
4. Ensure observability integrations are configured

## 🔌 MCP Integration & Neuro-Symbolic Pipeline
This stream heavily integrates our data extraction and intelligence MCPs:
*   **Browserbase MCP (`@browserbasehq/mcp-server-browserbase`)** & **Firecrawl MCP (`firecrawl-mcp`)**: Used for resilient, stealthy data ingestion, crawling, and visual capture.
*   **Qdrant MCP (`mcp-server-qdrant`)**: Manages high-performance vector embeddings for semantic search.
*   **Memgraph MCP (`mcp-memgraph`)**: Interacts with the knowledge graph for complex educational relational queries.
