# AI-Native Data Pipelines

## BAML-dlt Integration, Dagster Orchestration & Bilingual Dataset Creation

### `README.md` — 03-ai-native-data-pipelines

# AI-Native Data Pipelines

This directory consolidates research on modern data engineering infrastructure for AI-ready data production, including ETL/ELT frameworks, orchestration patterns, and real-time lakehouse architectures.

## Overview

The research covers the complete data pipeline stack for building semantic knowledge systems:
- **BAML Integration**: Schema-first AI output validation with dlt and Pydantic
- **Orchestration**: Dagster asset-based workflows with dynamic partitioning
- **Semantic Indexing**: CocoIndex for incremental vector indexing
- **Real-Time Lakehouse**: OLake, Lakekeeper, RisingWave stack
- **Metadata Management**: DuckDB-backed control planes

## Documents in this Category

| Document | Focus | Key Technologies |
|----------|-------|------------------|
| `baml-dlt-integration.md` | Schema-first ETL with AI validation | BAML, dlt, Pydantic, Zod, TanStack AI |
| `dagster-orchestration.md` | Asset-based pipeline orchestration | Dagster, CocoIndex, Graphiti, Marker |
| `metadata-control-plane.md` | Dynamic source management | DuckDB, Crawl4ai, TMX standards |
| `lakehouse-architecture.md` | Real-time open data lakehouse | OLake, Lakekeeper, RisingWave, Iceberg |

## Key Architectural Decisions

### 1. Schema-First AI Development

```
BAML Definition (Single Source of Truth)
├── Python Layer
│   ├── Pydantic Models (validated)
│   ├── dlt Resources (schema hints)
│   └── Custom Destinations (FalkorDB, Graphiti)
└── TypeScript Layer
    ├── TypeScript Interfaces
    ├── Zod Schemas (ts-to-zod)
    └── TanStack AI Tools
```

### 2. Multi-Database Ingestion Strategy

| Database | Integration Method | Use Case |
|----------|-------------------|----------|
| PostgreSQL | dlt native | Relational storage |
| LanceDB | dlt adapter | Vector similarity |
| FalkorDB | Custom destination | Graph relationships |
| Graphiti | Custom destination | Temporal knowledge |
| DuckDB | Native Python | Metadata control plane |

### 3. Real-Time Lakehouse Stack

```
Transaction (Source DB)
    ↓
OLake (Go-based CDC)
    ↓ Parquet to S3
Lakekeeper (Rust REST Catalog)
    ↓ Atomic commits
RisingWave (Streaming SQL)
    ↓ Materialized views
Analytics/ML Applications
```

## Source Files Consolidated

This category merges content from:
- `BAML, DLT, and AI Workflow Integration.md`
- `Dagster Orchestration for Cocoindex, Graphiti.md`
- `Managing Diverse Data Sources for Pipelines.md`
- `Integrating Olake, Lakekeeper, RisingWave.md`
- `BAML, Graphiti, Tanstack AI Pipeline.md`
- `BAML for Syllabus-Driven Data Extraction.md`

## Quick Reference

### Tool Selection Matrix

| Task | Tool | Rationale |
|------|------|-----------|
| PDF Extraction | Marker | LaTeX preservation, 4-10x faster than Nougat |
| Schema Validation | BAML | Compile-time verification, SAP algorithm |
| ETL Orchestration | dlt | Pydantic schema inference, auto-normalization |
| Workflow Orchestration | Dagster | Asset-based, dynamic partitions, sensors |
| Semantic Chunking | CocoIndex | Tree-sitter syntax-aware, incremental |
| Temporal Knowledge | Graphiti | Bi-temporal graphs, entity resolution |
| Metadata Store | DuckDB | In-process OLAP, JSON support |
| Real-Time Ingestion | OLake | Go-based, 300k+ rows/sec, direct Iceberg |
| Catalog Management | Lakekeeper | Rust, credential vending, OpenFGA |
| Streaming Compute | RisingWave | PostgreSQL-compatible, Iceberg native |

### Performance Benchmarks

| Operation | Tool | Throughput |
|-----------|------|------------|
| CDC Replication | OLake | >300,000 rows/sec |
| PDF Extraction | Marker | ~10 pages/sec |
| Vector Embedding | CocoIndex | Incremental (only changed) |
| Metadata Queries | DuckDB | Sub-millisecond |
| Commit Latency | Lakekeeper | Deterministic (no GC) |

### Configuration Patterns

**dlt Resource with BAML Schema:**
```python
@dlt.resource(
    name="research_insights",
    write_disposition="merge",
    primary_key="id",
    columns=ResearchInsight  # BAML-generated Pydantic
)
def extract_insights():
    for text in texts:
        insight = baml.ExtractInsight(text)
        yield insight
```

**Dagster Dynamic Partition:**
```python
exam_paper_partitions = DynamicPartitionsDefinition(name="exam_papers")

@asset(partitions_def=exam_paper_partitions)
def extracted_markdown(context):
    partition_key = context.partition_key
    return marker.process_pdf(partition_key)
```

## Implementation Priorities

### Phase 1: Schema Foundation
1. Define BAML schemas for data entities
2. Configure dual-target code generation (Python/TypeScript)
3. Set up dlt pipelines with Pydantic schema hints

### Phase 2: Orchestration Layer
1. Implement Dagster asset factories
2. Configure dynamic partitions for file ingestion
3. Add sensors for event-driven automation

### Phase 3: Semantic Intelligence
1. Integrate CocoIndex for vector indexing
2. Connect Graphiti for temporal knowledge graphs
3. Implement hybrid retrieval strategies

### Phase 4: Real-Time Lakehouse
1. Deploy OLake for CDC ingestion
2. Configure Lakekeeper for catalog management
3. Set up RisingWave for streaming analytics


---

### `baml-dlt-integration.md` — 03-ai-native-data-pipelines

# BAML-dlt Integration: Schema-First AI Workflow Architecture

## Executive Summary

This document details the integration of BAML (Boundary AI Markup Language) with dlt (Data Load Tool) to create a unified schema architecture that bridges the gap between probabilistic LLM outputs and deterministic data systems. The approach treats BAML as the single source of truth, with generated Pydantic models driving dlt pipeline schema inference.

---

## 1. The Schema Engineering Paradigm

### 1.1 From Prompt Engineering to Schema Engineering

Traditional prompt engineering is brittle - a model update or slight input variation can break downstream parsers. BAML represents the maturation to "schema engineering":

| Approach | Method | Failure Mode |
|----------|--------|--------------|
| **Prompt Engineering** | Craft English instructions for JSON | Model variations break parsers |
| **JSON Schema Validation** | Runtime schema checking | Token-heavy, slow |
| **BAML Schema Engineering** | Compile-time type definition + SAP parsing | Fail-fast, deterministic |

BAML's **Schema-Aligned Parsing (SAP)** algorithm allows robust parsing of imperfect LLM outputs in milliseconds, eliminating costly retry loops.

### 1.2 Architecture Overview

```
BAML Definition (Single Source of Truth)
├── Python Layer
│   ├── Pydantic Models (validated)
│   ├── dlt Resources (schema hints)
│   └── Custom Destinations (FalkorDB, Graphiti)
└── TypeScript Layer
    ├── TypeScript Interfaces
    ├── Zod Schemas (ts-to-zod)
    └── TanStack AI Tools
```

---

## 2. Dual-Target Code Generation

### 2.1 generators.baml Configuration

```baml
// baml_src/generators.baml

// Generator 1: Python Data Layer
generator python_client {
  output_type "python/pydantic"
  output_dir "../backend/baml_client"
  version "0.76.2"
  default_client_mode "async"  // High-throughput dlt ingestion
}

// Generator 2: TypeScript Application Layer
generator typescript_client {
  output_type "typescript"
  output_dir "../frontend/src/baml_client"
  version "0.76.2"
  default_client_mode "async"
}
```

Every `baml-cli generate` execution creates two semantically identical but language-specific libraries.

### 2.2 Complex Entity Definitions

```baml
// baml_src/models.baml

enum EntityType {
  PERSON
  ORGANIZATION
  LOCATION
  CONCEPT
}

class IdentifiedEntity {
  name string @description("The canonical name of the entity")
  type EntityType
  confidence float
}

class ResearchInsight {
  id string @description("UUID")
  title string
  summary string
  entities IdentifiedEntity[]  // Nested objects for Graph extraction
  embedding_context string @description("Text used for vectorization")
  citations string[]
  published_date string
}

function ExtractInsight(text: string) -> ResearchInsight {
  client "openai/gpt-4o"
  prompt #"
    Analyze the following text and extract the research insight.
    Identify key entities and their types.

    {{ ctx.output_format }}

    Text:
    {{ text }}
  "#
}
```

The `@description` annotations become Pydantic field descriptions (usable by dlt) and JSDoc comments in TypeScript.

---

## 3. dlt Integration: BAML-to-Pipeline Bridge

### 3.1 Resource Definition with Pydantic Schema

dlt's native Pydantic introspection turns BAML-generated classes into "Schema Hints":

```python
import dlt
from typing import Iterator
from backend.baml_client import b
from backend.baml_client.types import ResearchInsight

@dlt.source
def research_source(texts: list[str]):

    @dlt.resource(
        name="research_insights",
        write_disposition="merge",
        primary_key="id",
        columns=ResearchInsight  # Pydantic model defines schema
    )
    def extract_insights() -> Iterator:
        for text in texts:
            # BAML call returns validated Pydantic object
            insight = b.ExtractInsight(text)
            yield insight

    return extract_insights
```

BAML's SAP ensures objects are valid before dlt sees them - "fail-fast" prevents schema pollution.

### 3.2 Multi-Database Ingestion Strategy

| Database | Integration Method | Use Case |
|----------|-------------------|----------|
| **PostgreSQL** | dlt native destination | Relational storage |
| **DuckDB** | dlt native destination | Analytical queries |
| **LanceDB** | dlt adapter | Vector similarity search |
| **FalkorDB** | Custom destination | Graph relationships |
| **Graphiti** | Custom destination | Temporal knowledge |

#### LanceDB Vector Integration

```python
from dlt.destinations.adapters import lancedb_adapter

def configure_lancedb_pipeline():
    source = research_source(["..."])

    # Specify which fields to embed
    lancedb_adapter(
        source.extract_insights,
        embed=["embedding_context", "summary"]
    )

    pipeline = dlt.pipeline(
        pipeline_name="vector_ingestion",
        destination="lancedb",
        dataset_name="research_vectors"
    )
    return pipeline
```

#### FalkorDB Custom Destination

```python
import dlt
from falkordb import FalkorDB

@dlt.destination(batch_size=50)
def falkordb_destination(items, table_schema):
    """Load BAML objects into FalkorDB graph."""
    client = FalkorDB(host='localhost', port=6379)
    graph = client.select_graph('KnowledgeGraph')

    for item in items:
        # Create Insight Node
        query_insight = """
        MERGE (i:Insight {id: $id})
        SET i.title = $title, i.summary = $summary
        """
        graph.query(query_insight, {
            'id': item['id'],
            'title': item['title'],
            'summary': item['summary']
        })

        # Create Entity Nodes and Relationships
        for entity in item.get('entities', []):
            query_rel = """
            MATCH (i:Insight {id: $id})
            MERGE (e:Entity {name: $e_name})
            SET e.type = $e_type
            MERGE (i)-[:MENTIONS]->(e)
            """
            graph.query(query_rel, {
                'id': item['id'],
                'e_name': entity['name'],
                'e_type': entity['type']
            })
```

#### Graphiti Custom Destination

```python
from graphiti_core import Graphiti, EpisodeType
import asyncio

@dlt.destination(batch_size=10)
def graphiti_destination(items, table_schema):
    """Load data into Graphiti as temporal episodes."""
    async def _ingest_batch():
        client = Graphiti("falkor://localhost:6379")

        for item in items:
            await client.add_episode(
                name=f"insight_{item['id']}",
                episode_body=item,  # Pass entire Pydantic dict
                source=EpisodeType.json,
                source_description="BAML Extracted Research",
                reference_time=datetime.now()
            )

        await client.close()

    asyncio.run(_ingest_batch())
```

---

## 4. TypeScript Layer: BAML to Zod to TanStack

### 4.1 Automated Zod Generation

Since BAML generates TypeScript interfaces (not Zod schemas), bridge with `ts-to-zod`:

```json
{
  "scripts": {
    "generate:baml": "baml-cli generate",
    "generate:zod": "ts-to-zod --input ./src/baml_client/types.ts --output ./src/gen/zod.ts --skipValidation",
    "codegen": "npm run generate:baml && npm run generate:zod"
  }
}
```

### 4.2 TanStack AI Tool Integration

```typescript
import { toolDefinition } from '@tanstack/ai';
import { researchInsightSchema } from '../gen/zod';

export const saveInsightTool = toolDefinition({
  name: 'save_insight',
  description: 'Persists a validated research insight to the database.',
  inputSchema: researchInsightSchema,
  execute: async (insight) => {
    // 'insight' is fully typed as ResearchInsight
    console.log(`Saving insight: ${insight.title}`);
    return { success: true, id: insight.id };
  },
});
```

### 4.3 oRPC Integration

```typescript
import { os } from '@orpc/server';
import { researchInsightSchema } from '../gen/zod';
import { db } from '../db/drizzle';
import { insightsTable } from '../db/schema';

export const appRouter = os.router({
  submitInsight: os.procedure
    .input(researchInsightSchema)
    .handler(async ({ input }) => {
      await db.insert(insightsTable).values({
        id: input.id,
        title: input.title,
        summary: input.summary,
        publishedDate: input.published_date,
        entities: input.entities  // Store as JSONB
      });
      return { status: 'stored' };
    }),
});
```

---

## 5. Schema Evolution Workflow

### 5.1 Adding a New Field

**Step 1: Update BAML**
```baml
class ResearchInsight {
  // ...existing fields
  author string? @description("Primary author name")  // NEW
}
```

**Step 2: Run Codegen**
```bash
npm run codegen  # baml-cli generate && ts-to-zod
```

**Step 3: dlt Auto-Evolution**
On next pipeline run, dlt detects the new `author` field in Pydantic model and automatically performs `ALTER TABLE` on PostgreSQL.

**Step 4: Frontend Updates**
TypeScript compiler flags any handlers that need updating. Zod schema includes `.optional()` for backward compatibility.

---

## 6. Feature Matrix

| Component | Role | BAML Integration | Validation Timing |
|-----------|------|------------------|-------------------|
| **dlt (Core)** | Pipeline Orchestrator | Pydantic Model (Direct) | Runtime (Schema Contract) |
| **PostgreSQL** | Relational Store | dlt Native | Write-Time (DB Constraints) |
| **LanceDB** | Vector Store | dlt Adapter | Write-Time (Schema Check) |
| **FalkorDB** | Graph Store | Custom Destination | Write-Time (Graph Logic) |
| **Graphiti** | Agent Memory | Custom Destination | Ingestion-Time |
| **TanStack AI** | Tool Definitions | Zod (via ts-to-zod) | Generation-Time (LLM output) |
| **oRPC** | API RPC | Zod (via ts-to-zod) | Request-Time (API Boundary) |

---

## 7. Performance Considerations

### 7.1 Token Efficiency

BAML reduces prompt size by up to 40% compared to verbose JSON Schema, improving latency and cost.

### 7.2 Async Pipeline Architecture

Writing to multiple databases introduces latency. Recommended pattern:

```python
async def process_document(text):
    # Phase 1: BAML extraction (background worker)
    insight = await b.ExtractInsight(text)

    # Phase 2: Parallel database writes
    await asyncio.gather(
        postgres_pipeline.load(insight),
        lancedb_pipeline.load(insight),
        graphiti_client.add_episode(insight)
    )

    return insight
```

### 7.3 Latency vs Throughput

- BAML extraction should occur in background workers (Celery/Temporal)
- Frontend should use optimistic UI patterns
- Use dlt's asyncio features for extraction parallelism
- Serialize/batch loading phase to avoid rate limits

---

## 8. Implementation Priorities

### Phase 1: Schema Foundation
1. Define BAML schemas for core data entities
2. Configure dual-target code generation (Python/TypeScript)
3. Set up dlt pipelines with Pydantic schema hints

### Phase 2: Multi-Database Integration
1. Configure native destinations (PostgreSQL, LanceDB)
2. Implement custom destinations (FalkorDB, Graphiti)
3. Set up ts-to-zod automation

### Phase 3: Frontend Integration
1. Integrate Zod schemas with TanStack AI tools
2. Configure oRPC with BAML-derived schemas
3. Implement schema evolution workflow

---

## References

- BAML Documentation: https://docs.boundaryml.com
- dlt Resources: https://dlthub.com/docs/general-usage/resource
- LanceDB Adapter: https://dlthub.com/docs/dlt-ecosystem/destinations/lancedb
- ts-to-zod: https://github.com/fabien0102/ts-to-zod
- TanStack AI: https://github.com/TanStack/ai


---

### `dagster-orchestration.md` — 03-ai-native-data-pipelines

# Dagster Orchestration for Semantic Knowledge Systems

## Executive Summary

This document details the implementation of Dagster as the orchestration layer for AI-native data pipelines, covering asset-based workflows, dynamic partitioning, sensor-driven automation, and integration with CocoIndex and Graphiti for semantic intelligence.

---

## 1. Design Philosophy: Functional Core, Imperative Shell

### 1.1 Separation of Concerns

The architecture rigorously separates business logic from I/O operations:

**Functional Core (Pure Logic):**
- Text cleaning and LaTeX normalization
- Entity extraction using linguistic patterns
- Data structuring into Pydantic objects
- Never connects to databases, APIs, or filesystems

**Imperative Shell (Dagster):**
- Manages sensors detecting new files
- Handles database connections
- Orchestrates API calls
- Controls state and execution schedules

```python
# Functional Core - Pure function
def parse_math_content(text: str) -> MathQuestion:
    """Pure function - no I/O, fully testable."""
    entities = extract_entities(text)
    latex = normalize_latex(text)
    return MathQuestion(entities=entities, latex=latex)

# Imperative Shell - Dagster handles I/O
@asset
def processed_questions(context, raw_documents):
    """Dagster asset - manages I/O and state."""
    for doc in raw_documents:
        result = parse_math_content(doc.text)  # Call pure function
        yield result
```

### 1.2 Asset-Based vs Task-Based Orchestration

| Paradigm | Focus | State Tracking | Schema Drift |
|----------|-------|----------------|--------------|
| **Task-Based (Airflow)** | "Run the script" | Exit codes only | Manual |
| **Asset-Based (Dagster)** | "Ensure data exists" | Data lineage | Automatic |

Dagster tracks **data assets**, not tasks:
- `raw_exam_pdf` → `extracted_markdown` → `semantic_chunks` → `vector_embeddings`
- Implicit dependency graph inferred from code
- Freshness policies replace cron schedules

---

## 2. Dynamic Partitioning for File Ingestion

### 2.1 The Dynamic Partitions Pattern

Static partitioning fails for educational data where files arrive irregularly. Dynamic partitioning allows runtime partition creation:

```python
from dagster import DynamicPartitionsDefinition, asset

# Define dynamic partition set (initially empty)
exam_paper_partitions = DynamicPartitionsDefinition(name="exam_papers")

@asset(partitions_def=exam_paper_partitions)
def raw_pdf_content(context):
    """Asset representing binary content of specific exam paper."""
    partition_key = context.partition_key
    file_path = resolve_path(partition_key)
    with open(file_path, "rb") as f:
        return f.read()

@asset(partitions_def=exam_paper_partitions)
def extracted_markdown(context, raw_pdf_content):
    """Marker extraction - depends on raw PDF."""
    return marker.process_pdf(raw_pdf_content)
```

**Benefits:**
- Each exam paper has discrete asset lineage
- Failure in "Math_Paper_2023" doesn't block "Math_Paper_2024"
- Granular debugging and backfilling

### 2.2 Sensor-Driven Automation

Sensors detect new files and register partitions automatically:

```python
from dagster import sensor, RunRequest

@sensor(job=process_exam_job)
def new_exam_sensor(context):
    """Poll directory for new PDFs, register partitions."""
    current_files = list_files_in_directory()
    existing_partitions = context.instance.get_dynamic_partitions("exam_papers")

    new_files = [f for f in current_files if f not in existing_partitions]

    if new_files:
        # Register new partitions in Dagster's state
        context.instance.add_dynamic_partitions("exam_papers", new_files)

        # Request run for each new file
        for filename in new_files:
            yield RunRequest(
                run_key=filename,
                partition_key=filename
            )
```

**Workflow:**
1. Sensor polls source directory
2. Diffs against existing partitions
3. Registers new partition keys
4. Yields `RunRequest` for each new file

---

## 3. Asset Graph Architecture

### 3.1 The Document Processing Pipeline

```
raw_pdf_file (Binary Input)
    ↓
extracted_markdown (Marker Processing)
    ↓
semantic_chunks (CocoIndex Splitting)
    ↓
vector_embeddings (Sentence Transformer)
    ↓
knowledge_graph_episodes (Graphiti Ingestion)
```

### 3.2 Implementation

```python
from dagster import asset, AssetIn
import marker
from cocoindex import SplitRecursively, SentenceTransformerEmbed

@asset(partitions_def=exam_paper_partitions)
def extracted_markdown(context, raw_pdf_content) -> str:
    """Convert PDF to LaTeX-preserving Markdown."""
    return marker.process_pdf(raw_pdf_content)

@asset(partitions_def=exam_paper_partitions)
def semantic_chunks(context, extracted_markdown) -> list[str]:
    """Split Markdown into syntax-aware chunks."""
    return SplitRecursively(
        extracted_markdown,
        language="markdown",
        chunk_size=2000,
        chunk_overlap=500
    )

@asset(partitions_def=exam_paper_partitions)
def vector_embeddings(context, semantic_chunks) -> list[dict]:
    """Generate embeddings for each chunk."""
    embedder = SentenceTransformerEmbed(
        model="sentence-transformers/all-MiniLM-L6-v2"
    )
    return [
        {"text": chunk, "embedding": embedder(chunk)}
        for chunk in semantic_chunks
    ]

@asset(partitions_def=exam_paper_partitions)
def knowledge_graph_episodes(context, extracted_markdown):
    """Ingest into Graphiti temporal graph."""
    from graphiti_core import Graphiti, EpisodeType

    client = Graphiti("falkor://localhost:6379")
    await client.add_episode(
        name=f"exam_{context.partition_key}",
        episode_body=extracted_markdown,
        source=EpisodeType.text,
        reference_time=extract_exam_date(context.partition_key),
        entity_types=[MathTheorem, ExamTopic]
    )
```

### 3.3 Memoization Benefits

When changing only the embedding model:
- `raw_pdf_content` - NOT recomputed
- `extracted_markdown` - NOT recomputed
- `semantic_chunks` - NOT recomputed
- `vector_embeddings` - RECOMPUTED (logic changed)
- `knowledge_graph_episodes` - NOT recomputed (independent)

---

## 4. Asset Factory Pattern for Metadata-Driven Pipelines

### 4.1 Dynamic Asset Generation

For pipelines with many sources (100+ scraping targets), generate assets programmatically:

```python
from dagster import Definitions, asset

def load_sources_from_duckdb() -> list[dict]:
    """Query DuckDB for active source configurations."""
    import duckdb
    conn = duckdb.connect("metadata.db")
    return conn.execute("""
        SELECT source_id, name, tool_driver, connection_spec, extraction_strategy
        FROM sources
        JOIN ingestion_configs USING (source_id)
        WHERE active = true
    """).fetchall()

def build_crawl_asset(config: dict):
    """Factory function to create crawler asset."""
    @asset(name=f"crawl_{config['name']}")
    def _crawl_asset(context):
        from crawl4ai import AsyncWebCrawler, CrawlerRunConfig

        run_config = CrawlerRunConfig(**config['extraction_strategy'])
        async with AsyncWebCrawler() as crawler:
            result = await crawler.arun(
                url=config['connection_spec']['url'],
                config=run_config
            )
        return result.markdown

    return _crawl_asset

# Generate assets at load time
sources = load_sources_from_duckdb()
generated_assets = [
    build_crawl_asset(s) for s in sources
    if s['tool_driver'] == 'crawl4ai'
]

defs = Definitions(assets=generated_assets)
```

### 4.2 Scaling with Generic Partitioned Assets

For thousands of sources, use a single partitioned asset instead:

```python
from dagster import DynamicPartitionsDefinition, asset, sensor

source_partitions = DynamicPartitionsDefinition(name="data_sources")

@asset(partitions_def=source_partitions)
def generic_crawler_job(context):
    """Single asset handles all crawling via partition key."""
    source_id = context.partition_key

    # Fetch config for this specific source
    config = fetch_config_from_duckdb(source_id)

    # Execute crawl with config
    result = execute_crawl(config)
    return result

@sensor(job=crawl_job)
def source_registry_sensor(context):
    """Monitor DuckDB for new sources."""
    active_sources = get_active_source_ids()
    existing = context.instance.get_dynamic_partitions("data_sources")

    new_sources = set(active_sources) - set(existing)
    if new_sources:
        context.instance.add_dynamic_partitions("data_sources", list(new_sources))
        for source_id in new_sources:
            yield RunRequest(partition_key=source_id)
```

---

## 5. CocoIndex Integration

### 5.1 Library vs Service Pattern

CocoIndex can run as a service with internal orchestration, but running "orchestrator within orchestrator" creates complexity. **Use CocoIndex as a library within Dagster assets.**

### 5.2 Semantic Chunking

CocoIndex's `SplitRecursively` uses Tree-sitter for syntax-aware splitting:

```python
@asset
def semantic_chunks(extracted_markdown: str) -> list[str]:
    """Syntax-aware chunking preserves LaTeX equations."""
    import cocoindex

    return cocoindex.SplitRecursively(
        text=extracted_markdown,
        language="markdown",  # Tree-sitter parser
        chunk_size=2000,
        chunk_overlap=500
    )
```

**Why Tree-sitter matters:**
- Recognizes code blocks (LaTeX `$$...$$`) as atomic units
- Respects header boundaries (`# Question 1`)
- Produces semantically coherent chunks

### 5.3 Hybrid Embedding Strategy

```python
@cocoindex.transform_flow()
def text_to_embedding(text: cocoindex.DataSlice[str]):
    """Reusable transform for indexing AND querying."""
    return text.transform(
        cocoindex.functions.SentenceTransformerEmbed(
            model="sentence-transformers/all-MiniLM-L6-v2"
        )
    )

@asset
def vector_index(semantic_chunks: list[str]):
    """Build vector index with hybrid strategy."""
    import cocoindex

    # Textual embedding
    embeddings = [text_to_embedding(chunk) for chunk in chunks]

    # Preserve raw LaTeX as metadata
    records = [
        {"text": chunk, "embedding": emb, "latex": extract_latex(chunk)}
        for chunk, emb in zip(chunks, embeddings)
    ]

    cocoindex.collect(records, "research_vectors")
```

---

## 6. Graphiti Integration

### 6.1 Temporal Knowledge Graph

Graphiti enables bi-temporal queries:
- **Valid Time:** When the fact was true (exam date)
- **Transaction Time:** When fact was recorded

```python
@asset(partitions_def=exam_paper_partitions)
def temporal_knowledge_graph(context, extracted_markdown):
    """Ingest exam data with temporal context."""
    from graphiti_core import Graphiti, EpisodeType
    from pydantic import BaseModel, Field

    # Define ontology
    class MathTheorem(BaseModel):
        name: str = Field(description="Theorem name, e.g., Pythagoras")
        latex_def: str = Field(description="LaTeX definition")

    class ExamTopic(BaseModel):
        name: str = Field(description="Curriculum topic")
        code: str = Field(description="Curriculum code, e.g., C1.2")

    client = Graphiti("falkor://localhost:6379")

    await client.add_episode(
        name=f"exam_{context.partition_key}",
        episode_body=extracted_markdown,
        source=EpisodeType.text,
        reference_time=parse_exam_date(context.partition_key),
        entity_types=[MathTheorem, ExamTopic]  # Constrain extraction
    )
```

### 6.2 Entity Resolution

Graphiti performs LLM-based entity resolution:
- "Question 1" in Exam Paper links to "Question 1" in Marking Scheme
- "Maths" and "Mathematics" merge into single entity

### 6.3 Hybrid Search

```python
def search_knowledge_graph(query: str):
    """Combine semantic, keyword, and graph traversal."""
    client = Graphiti("falkor://localhost:6379")

    results = await client.search(
        query=query,
        search_type="hybrid",  # Semantic + BM25 + Graph
        limit=10
    )

    return results
```

---

## 7. Operational Patterns

### 7.1 Asset Checks

```python
from dagster import asset_check, AssetCheckResult

@asset_check(asset=extracted_markdown)
def latex_density_check(context, extracted_markdown):
    """Verify PDF extraction produced LaTeX."""
    latex_count = extracted_markdown.count("$$")
    density = latex_count / len(extracted_markdown)

    return AssetCheckResult(
        passed=density > 0.01,
        metadata={"latex_density": density}
    )
```

### 7.2 Retry Policies

```python
from dagster import RetryPolicy

@asset(
    partitions_def=exam_paper_partitions,
    retry_policy=RetryPolicy(max_retries=3, delay=30)
)
def extracted_markdown(raw_pdf_content):
    """Retry on transient failures."""
    return marker.process_pdf(raw_pdf_content)
```

### 7.3 Resource Configuration

```python
from dagster import resource, Definitions

@resource
def graphiti_resource(context):
    """Configurable Graphiti connection."""
    return Graphiti(context.resource_config["uri"])

defs = Definitions(
    assets=[...],
    resources={
        "graphiti": graphiti_resource.configured({
            "uri": "falkor://localhost:6379"
        })
    }
)
```

---

## 8. Deployment Architecture

### 8.1 Dockerized Stack

```yaml
services:
  dagster-daemon:
    image: dagster/dagster:latest
    command: dagster-daemon run

  dagster-webserver:
    image: dagster/dagster:latest
    command: dagster-webserver -h 0.0.0.0 -p 3000

  postgres:
    image: postgres:15
    # Shared storage for Dagster metadata + CocoIndex vectors

  falkordb:
    image: falkordb/falkordb:latest
    # Graph storage for Graphiti

  gpu-worker:
    image: custom/extraction-worker
    deploy:
      resources:
        reservations:
          devices:
            - driver: nvidia
              count: 1
              capabilities: [gpu]
```

### 8.2 Database Independence

- **Graphiti:** Swap Neo4j/FalkorDB via connection URI
- **CocoIndex:** Uses PostgreSQL + pgvector (vendor-neutral)
- **Marker:** Local GPU inference (no API dependency)

---

## 9. Implementation Priorities

### Phase 1: Core Pipeline
1. Implement Marker extraction asset
2. Add dynamic partitioning for file ingestion
3. Configure sensor for new file detection

### Phase 2: Semantic Intelligence
1. Integrate CocoIndex for syntax-aware chunking
2. Build vector embedding pipeline
3. Add hybrid embedding strategy

### Phase 3: Knowledge Graph
1. Deploy Graphiti with FalkorDB
2. Define domain ontology (Pydantic models)
3. Implement temporal episode ingestion

### Phase 4: Operational Maturity
1. Add asset checks for data quality
2. Configure retry policies
3. Implement monitoring/alerting

---

## References

- Dagster Partitioning: https://docs.dagster.io/guides/build/partitions-and-backfills
- Dagster Sensors: https://docs.dagster.io/guides/automate/sensors
- CocoIndex: https://cocoindex.io/docs/
- Graphiti: https://help.getzep.com/graphiti/
- Marker PDF: https://github.com/VikParuchuri/marker


---

### `lakehouse-architecture.md` — 03-ai-native-data-pipelines

# Real-Time Open Data Lakehouse Architecture

## Executive Summary

This document details the integration of OLake, Lakekeeper, and RisingWave to construct a second-generation open data lakehouse. The architecture eliminates JVM overhead, provides secure credential vending, and delivers sub-second data freshness from transactional sources to analytical endpoints.

---

## 1. The Modern Data Stack Crisis

### 1.1 Legacy Bottlenecks

| Component | Problem | Impact |
|-----------|---------|--------|
| **Debezium** | JVM GC pauses, Kafka dependency | Latency spikes, operational overhead |
| **Hive Metastore** | Centralized bottleneck | Slow query planning, no multi-table transactions |
| **Spark** | Batch-only, heavy resource footprint | High latency, expensive compute |

Specific limitations:
- Debezium MongoDB connector: 16MB document size cap
- HMS lacks native Iceberg atomic transaction support
- GC pauses introduce unpredictable latency

### 1.2 Second-Generation Stack

| Layer | Technology | Advantage |
|-------|------------|-----------|
| **Ingestion** | OLake (Go) | 300K+ rows/sec, no JVM, direct Iceberg writes |
| **Governance** | Lakekeeper (Rust) | Deterministic latency, credential vending |
| **Compute** | RisingWave | Streaming SQL, materialized views on Iceberg |

---

## 2. OLake: High-Velocity Ingestion

### 2.1 Architecture

OLake is a Go-based ELT framework with modular **Protocol Layer**:
- **Drivers:** Database-specific extraction logic
- **Writers:** Destination-specific loading (Iceberg, Parquet)

### 2.2 Parallelized Snapshotting

Single-threaded snapshots on large tables take days. OLake splits tables into chunks processed concurrently:

| Database | Chunking Strategy | Method |
|----------|-------------------|--------|
| **PostgreSQL** | Physical Block | CTID (tuple identifier) ranges |
| **MySQL** | Key Range | Primary key range queries |
| **MongoDB** | Vector Splitting | Split-Vector/Bucket-Auto commands |

**Result:** >300,000 rows/second throughput

### 2.3 Log-Based CDC Mechanics

**PostgreSQL (pgoutput):**
```sql
-- Create publication for CDC
CREATE PUBLICATION olake_pub FOR ALL TABLES;

-- Create replication slot
SELECT pg_create_logical_replication_slot('olake_slot', 'pgoutput');
```

OLake consumes WAL stream via logical replication.

**MySQL (Binlog):**
```sql
-- Required settings
SET GLOBAL binlog_format = 'ROW';
SET GLOBAL binlog_row_image = 'FULL';  -- Both before/after images
```

OLake acts as replica, consuming binary log stream.

**MongoDB (Oplog):**
- Tails operations log (capped collection)
- Maintains native BSON structure (handles >16MB documents)

### 2.4 Configuration

**source.json (PostgreSQL):**
```json
{
  "host": "postgres.example.com",
  "port": 5432,
  "database": "production",
  "update_method": {
    "replication_slot": "olake_slot",
    "publication": "olake_pub",
    "initial_wait_time": 5
  },
  "max_threads": 8,
  "ssl": {
    "mode": "verify-full"
  }
}
```

**destination.json (Lakekeeper REST Catalog):**
```json
{
  "type": "ICEBERG",
  "writer": {
    "catalog_type": "rest",
    "uri": "http://lakekeeper:8181/catalog/",
    "iceberg_s3_path": "s3://warehouse/",
    "io_impl": "org.apache.iceberg.aws.s3.S3FileIO",
    "s3_path_style": true
  }
}
```

**Key Parameters:**
- `s3_path_style: true` - Required for MinIO (prevents DNS bucket resolution)
- `io_impl` - Use native Iceberg S3FileIO (not Hadoop S3A)

### 2.5 State Management

OLake maintains `state.json` with exact transaction log position:
- PostgreSQL: LSN (Log Sequence Number)
- MySQL: Binlog filename + offset
- MongoDB: Oplog timestamp

**Exactly-Once Semantics:**
1. Crash occurs mid-write
2. OLake restarts, reads `state.json`
3. Resumes from last checkpoint
4. Iceberg commits are atomic - no partial data

---

## 3. Lakekeeper: Governance Control Plane

### 3.1 Rust Architecture Benefits

| JVM Catalog | Rust (Lakekeeper) |
|-------------|-------------------|
| GC pauses cause latency spikes | Deterministic, predictable latency |
| Large memory footprint | Minimal binary, sidecar-deployable |
| Complex threading model | Memory-safe concurrency |

### 3.2 Entity Hierarchy

```
Server (Root)
└── Project (Tenant Isolation)
    └── Warehouse (Storage Backend)
        └── Namespace (Hierarchical Grouping)
            └── Table/View (Iceberg Tables)
```

**Multi-Tenancy:** Credentials for one warehouse cannot access another.

### 3.3 Credential Vending

Traditional lakes require "god mode" S3 access for all compute engines. Lakekeeper provides table-level security:

**Flow:**
1. Client authenticates with Lakekeeper (OAuth2/OIDC)
2. Lakekeeper verifies permissions
3. Lakekeeper calls AWS STS to assume role
4. Returns short-lived, scoped credentials (specific table prefix only)

**Result:** Compromised compute worker can't access entire lake.

### 3.4 Fine-Grained Authorization (OpenFGA)

Relationship-Based Access Control (ReBAC):
```
# Policy: User can read table if owner of parent project OR in auditor group
user:alice can read table:sales.q1 if
  owner of project:sales OR
  member of group:auditors
```

### 3.5 Bootstrapping

```bash
# Initialize Lakekeeper
curl -X POST http://localhost:8181/management/v1/bootstrap \
  -H 'Content-Type: application/json' \
  -d '{"accept-terms-of-use": true}'

# Create warehouse with MinIO storage
curl -X POST http://localhost:8181/management/v1/warehouse \
  -H 'Content-Type: application/json' \
  -d '{
    "warehouse-name": "main-warehouse",
    "storage-profile": {
      "type": "s3",
      "bucket": "iceberg-data",
      "endpoint": "http://minio:9000",
      "region": "us-east-1",
      "path-style-access": true,
      "flavor": "minio"
    },
    "storage-credential": {
      "type": "s3",
      "aws-access-key-id": "minioadmin",
      "aws-secret-access-key": "minioadmin"
    }
  }'
```

---

## 4. RisingWave: Streaming Compute

### 4.1 Architecture

- **Hummock:** LSM-tree storage engine optimized for S3
- **PostgreSQL Compatible:** Standard SQL, psql connectivity
- **Iceberg Native:** First-class source and sink support

### 4.2 Iceberg REST Catalog Connection

```sql
-- Create connection to Lakekeeper
CREATE CONNECTION lakekeeper_conn WITH (
  type = 'iceberg',
  catalog.type = 'rest',
  catalog.uri = 'http://lakekeeper:8181/catalog/',
  warehouse.path = 'main-warehouse',
  s3.endpoint = 'http://minio:9000',
  s3.access.key = 'minioadmin',
  s3.secret.key = 'minioadmin',
  s3.region = 'us-east-1',
  s3.path.style.access = 'true'
);

-- Set as default connection
SET iceberg_engine_connection = 'lakekeeper_conn';

-- Query OLake-created tables
SELECT * FROM main_warehouse.public.users LIMIT 10;
```

### 4.3 Materialized Views

```sql
-- Real-time aggregation on streaming data
CREATE MATERIALIZED VIEW order_stats AS
SELECT
  date_trunc('hour', created_at) as hour,
  count(*) as order_count,
  sum(total_amount) as revenue
FROM main_warehouse.sales.orders
GROUP BY 1;
```

RisingWave detects Iceberg snapshot changes and automatically refreshes.

---

## 5. Integration Architecture

### 5.1 Data Flow

```
PostgreSQL (Source)
    │
    ▼
OLake (CDC via pgoutput)
    │
    ├── Write Parquet files to S3
    │
    └── Commit Transaction to Lakekeeper
            │
            ▼
    Lakekeeper (Atomic metadata update)
            │
            ▼
    RisingWave (Detect new snapshot)
            │
            ▼
    Materialized Views / BI Tools
```

### 5.2 Latency Analysis

| Stage | Latency |
|-------|---------|
| Database replication | ~100ms |
| OLake buffering | Configurable (batch size/time) |
| Iceberg commit | ~50ms |
| RisingWave refresh | Configurable |
| **End-to-End** | Sub-minute (tuned) |

### 5.3 Consistency Guarantees

- **Read Committed / Snapshot Isolation**
- RisingWave never sees partial writes
- Snapshot switch in Lakekeeper is atomic
- No dirty reads of uncommitted files

---

## 6. Docker Compose Deployment

```yaml
version: "3.8"

services:
  # Storage Layer
  minio:
    image: minio/minio:latest
    command: server /data --console-address ":9090"
    ports: ["9000:9000", "9090:9090"]
    environment:
      MINIO_ROOT_USER: minioadmin
      MINIO_ROOT_PASSWORD: minioadmin

  # Metadata Database
  postgres:
    image: postgres:15
    environment:
      POSTGRES_USER: postgres
      POSTGRES_PASSWORD: password
      POSTGRES_DB: postgres

  # Governance Layer
  lakekeeper:
    image: quay.io/lakekeeper/catalog:latest
    ports: ["8181:8181"]
    depends_on:
      postgres:
        condition: service_healthy
    environment:
      LAKEKEEPER__PG_DATABASE_URL_READ: postgresql://postgres:password@postgres:5432/postgres
      LAKEKEEPER__PG_DATABASE_URL_WRITE: postgresql://postgres:password@postgres:5432/postgres
      LAKEKEEPER__PG_ENCRYPTION_KEY: "change-me-in-production"
      RUST_LOG: info
    command: ["serve"]

  # Ingestion Layer
  olake-ui:
    image: registry-1.docker.io/olakego/ui:latest
    ports: ["8000:8000"]
    environment:
      POSTGRES_DB: "postgres://postgres:password@postgres:5432/olake_db"
      PERSISTENT_DIR: /mnt/olake-data
    volumes:
      - ./olake-data:/mnt/olake-data

  # Compute Layer
  risingwave:
    image: risingwavelabs/risingwave:latest
    ports: ["4566:4566", "5691:5691"]
    command: risingwave playground
```

---

## 7. Operational Considerations

### 7.1 Schema Evolution

```
Source DDL Change (ALTER TABLE ADD COLUMN)
    │
    ▼
OLake CDC detects DDL event
    │
    ▼
OLake pauses data write
    │
    ▼
Sends UpdateSchema to Lakekeeper
    │
    ▼
Lakekeeper validates (safe evolution?)
    │
    ▼
Metadata updated, OLake resumes
```

**RisingWave:** May need `REFRESH` command or `auto.schema.change` configuration.

### 7.2 Small File Problem

High-frequency CDC creates many small Parquet files. Mitigation:

```sql
-- Periodic compaction job (Flink/Spark)
CALL system.rewrite_data_files(
  table => 'db.table',
  options => map('target-file-size-bytes', '134217728')  -- 128MB
);
```

Future Lakekeeper versions will support automated table maintenance.

### 7.3 Monitoring

| Component | Metrics |
|-----------|---------|
| **OLake** | `stats.json`: rows_synced, speed_rps, memory_usage |
| **Lakekeeper** | HTTP 5xx rate on `/catalog/` endpoints |
| **RisingWave** | Dashboard (port 5691), Prometheus metrics |

---

## 8. Performance Benchmarks

### 8.1 OLake Throughput

| Source | Rows/Second | Notes |
|--------|-------------|-------|
| PostgreSQL | 300,000+ | CTID chunking |
| MySQL | 250,000+ | PK range splitting |
| MongoDB | 200,000+ | Vector splitting |

### 8.2 Latency Comparison

| Stack | End-to-End Latency |
|-------|-------------------|
| Debezium + Kafka + Spark | 5-30 minutes |
| OLake + Lakekeeper + RisingWave | <1 minute |

### 8.3 Resource Footprint

| Component | Memory | Notes |
|-----------|--------|-------|
| OLake | ~500MB | Go, no JVM |
| Lakekeeper | ~100MB | Rust binary |
| Debezium + Kafka | 4-8GB+ | JVM heap tuning |

---

## 9. Implementation Priorities

### Phase 1: Core Infrastructure
1. Deploy MinIO + PostgreSQL + Lakekeeper
2. Bootstrap Lakekeeper with warehouse configuration
3. Verify REST catalog connectivity

### Phase 2: Ingestion Pipeline
1. Configure OLake source (PostgreSQL/MySQL)
2. Configure OLake destination (REST catalog)
3. Run initial snapshot + CDC

### Phase 3: Compute Layer
1. Deploy RisingWave
2. Create Iceberg connection
3. Build materialized views

### Phase 4: Production Hardening
1. Configure credential vending
2. Set up OpenFGA policies
3. Implement compaction jobs
4. Configure monitoring/alerting

---

## References

- OLake Documentation: https://olake.io/docs/
- Lakekeeper: https://docs.lakekeeper.io/
- RisingWave Iceberg: https://docs.risingwave.com/iceberg/
- Apache Iceberg REST Catalog Spec: https://iceberg.apache.org/docs/latest/rest-catalog/


---

### `metadata-control-plane.md` — 03-ai-native-data-pipelines

# Metadata Control Plane: DuckDB-Backed Dynamic Source Management

## Executive Summary

This document details the architecture for migrating from static YAML configuration to a DuckDB-backed metadata control plane. The approach enables dynamic asset generation, polymorphic tool configuration, and metadata-driven pipeline orchestration.

---

## 1. The Case Against Static Configuration

### 1.1 YAML Limitations

| Limitation | Impact |
|------------|--------|
| **No Referential Integrity** | Source renamed in one place breaks downstream references |
| **No Query Capability** | Can't answer "Which Spanish-English sources update daily?" |
| **Concurrency Issues** | Merge conflicts in collaborative editing |
| **Static Orchestration** | Code deployment required for new sources |

### 1.2 The DuckDB Advantage

DuckDB is uniquely suited as an application metadata store:

| Feature | Benefit |
|---------|---------|
| **In-Process** | No server to provision; single file on disk |
| **OLAP Optimized** | High-performance metadata introspection |
| **Native JSON** | Store complex configs without rigid migrations |
| **Python Integration** | Zero-copy with dicts, Pydantic, DataFrames |

---

## 2. Comprehensive Schema Design

### 2.1 Core Entity: sources

Tool-agnostic master registry:

```sql
CREATE TABLE sources (
    source_id UUID PRIMARY KEY,
    name VARCHAR NOT NULL,
    source_type VARCHAR NOT NULL,  -- 'REST_API', 'GITHUB_REPO', 'WEB_CRAWL', 'PDF_ARCHIVE'
    owner_team VARCHAR,
    active BOOLEAN DEFAULT true,
    created_at TIMESTAMP DEFAULT now(),
    last_updated TIMESTAMP DEFAULT now()
);
```

### 2.2 Polymorphic Configuration: ingestion_configs

JSON columns accommodate different tool "shapes":

```sql
CREATE TABLE ingestion_configs (
    config_id UUID PRIMARY KEY,
    source_id UUID REFERENCES sources(source_id),
    tool_driver VARCHAR NOT NULL,  -- 'dlt', 'crawl4ai', 'cocoindex', 'custom_python'
    connection_spec JSON NOT NULL,
    extraction_strategy JSON NOT NULL,
    secrets_ref VARCHAR  -- 'env:GITHUB_TOKEN' - never store raw secrets
);
```

**JSON Structure by Tool:**

**dlt (REST API):**
```json
{
  "connection_spec": {
    "base_url": "https://api.example.com",
    "pagination": "header_link"
  },
  "extraction_strategy": {
    "endpoints": ["users", "posts"],
    "write_disposition": "merge",
    "primary_key": "id"
  }
}
```

**Crawl4ai (Web Scraping):**
```json
{
  "connection_spec": {
    "headless": true,
    "user_agent": "Mozilla/5.0...",
    "proxy_config": {}
  },
  "extraction_strategy": {
    "css_selector": "article.content",
    "word_count_threshold": 10,
    "excluded_tags": ["nav", "footer"]
  }
}
```

**CocoIndex (Semantic Indexing):**
```json
{
  "connection_spec": {
    "source_path": "s3://bucket/pdfs/"
  },
  "extraction_strategy": {
    "chunk_size": 2000,
    "chunk_overlap": 500,
    "embedding_model": "sentence-transformers/all-MiniLM-L6-v2"
  }
}
```

### 2.3 Bilingual Metadata

TMX and DataCite aligned for interoperability:

```sql
CREATE TABLE bilingual_metadata (
    meta_id UUID PRIMARY KEY,
    source_id UUID REFERENCES sources(source_id),
    source_lang VARCHAR NOT NULL,  -- ISO 639-1/3 code
    target_lang VARCHAR NOT NULL,
    domain VARCHAR,  -- 'Legal', 'Medical', 'Technical'
    alignment_method VARCHAR,  -- 'sentence_aligned', 'document_aligned'
    license_type VARCHAR,  -- 'CC-BY-4.0', 'MIT'
    citation_ref VARCHAR  -- DOI or URL
);
```

### 2.4 Schedule Definitions

Interface between metadata and Dagster:

```sql
CREATE TABLE schedule_definitions (
    schedule_id UUID PRIMARY KEY,
    source_id UUID REFERENCES sources(source_id),
    cron_schedule VARCHAR,  -- '0 2 * * *' for daily at 2 AM
    partition_def JSON,  -- {"type": "daily", "format": "%Y-%m-%d"}
    dagster_group VARCHAR  -- Asset graph grouping
);
```

---

## 3. Tool Hydration Patterns

### 3.1 dlt Dynamic Source Factory

```python
import dlt
from typing import Iterator

def build_dlt_source(config: dict):
    """Factory to create dlt source from database config."""

    @dlt.source
    def dynamic_source():
        base_url = config['connection_spec']['base_url']

        for endpoint in config['extraction_strategy']['endpoints']:
            @dlt.resource(
                name=endpoint,
                write_disposition=config['extraction_strategy'].get('write_disposition', 'append'),
                primary_key=config['extraction_strategy'].get('primary_key')
            )
            def fetch_data(ep=endpoint):
                import requests
                response = requests.get(f"{base_url}/{ep}")
                yield from response.json()

            yield fetch_data

    return dynamic_source
```

### 3.2 Crawl4ai Configuration Hydration

```python
from crawl4ai import AsyncWebCrawler, BrowserConfig, CrawlerRunConfig

async def execute_crawl(config: dict):
    """Hydrate Crawl4ai configs from database JSON."""

    # Deserialize JSON to config objects
    browser_config = BrowserConfig(**config['connection_spec'])
    run_config = CrawlerRunConfig(**config['extraction_strategy'])

    async with AsyncWebCrawler(config=browser_config) as crawler:
        result = await crawler.arun(
            url=config['url'],
            config=run_config
        )

    return result.markdown
```

### 3.3 CocoIndex Flow Hydration

```python
import cocoindex

def build_cocoindex_flow(config: dict):
    """Create CocoIndex flow from database config."""

    @cocoindex.flow_def(name=config['name'])
    def dynamic_flow():
        source = cocoindex.sources.directory(
            path=config['connection_spec']['source_path']
        )

        chunks = source.transform(
            cocoindex.SplitRecursively,
            chunk_size=config['extraction_strategy']['chunk_size'],
            chunk_overlap=config['extraction_strategy']['chunk_overlap']
        )

        embeddings = chunks.transform(
            cocoindex.SentenceTransformerEmbed,
            model=config['extraction_strategy']['embedding_model']
        )

        return embeddings

    return dynamic_flow
```

---

## 4. Dagster Asset Factory Implementation

### 4.1 Loading Sources at Definition Time

```python
from dagster import Definitions, asset
import duckdb

def load_sources_from_duckdb() -> list[dict]:
    """Query active sources with their configurations."""
    conn = duckdb.connect("metadata.db")

    query = """
        SELECT
            s.source_id,
            s.name,
            s.source_type,
            ic.tool_driver,
            ic.connection_spec,
            ic.extraction_strategy,
            sd.cron_schedule,
            sd.dagster_group
        FROM sources s
        JOIN ingestion_configs ic USING (source_id)
        LEFT JOIN schedule_definitions sd USING (source_id)
        WHERE s.active = true
    """

    return conn.execute(query).fetchdf().to_dict('records')

def build_asset_for_source(config: dict):
    """Factory function to create asset from config."""

    @asset(
        name=f"source_{config['name']}",
        group_name=config.get('dagster_group', 'default')
    )
    def _asset(context):
        if config['tool_driver'] == 'dlt':
            source = build_dlt_source(config)
            return source()
        elif config['tool_driver'] == 'crawl4ai':
            return execute_crawl(config)
        elif config['tool_driver'] == 'cocoindex':
            flow = build_cocoindex_flow(config)
            return flow.update()

    return _asset

# Generate all assets at load time
sources = load_sources_from_duckdb()
generated_assets = [build_asset_for_source(s) for s in sources]

defs = Definitions(assets=generated_assets)
```

### 4.2 Scaling with Dynamic Partitions

For thousands of sources, use single partitioned asset:

```python
from dagster import DynamicPartitionsDefinition, asset, sensor, RunRequest

source_partitions = DynamicPartitionsDefinition(name="data_sources")

@asset(partitions_def=source_partitions)
def universal_ingestion_asset(context):
    """Single asset handles all sources via partition key."""
    source_id = context.partition_key

    # Fetch config for this specific source
    config = fetch_source_config(source_id)

    # Route to appropriate tool
    if config['tool_driver'] == 'dlt':
        return run_dlt_pipeline(config)
    elif config['tool_driver'] == 'crawl4ai':
        return run_crawl_pipeline(config)
    elif config['tool_driver'] == 'cocoindex':
        return run_cocoindex_pipeline(config)

@sensor(job=ingestion_job)
def source_registry_sensor(context):
    """Detect new sources in database."""
    import duckdb
    conn = duckdb.connect("metadata.db")

    active_sources = conn.execute(
        "SELECT source_id FROM sources WHERE active = true"
    ).fetchall()
    active_ids = [str(s[0]) for s in active_sources]

    existing = context.instance.get_dynamic_partitions("data_sources")

    new_sources = set(active_ids) - set(existing)
    if new_sources:
        context.instance.add_dynamic_partitions("data_sources", list(new_sources))
        for source_id in new_sources:
            yield RunRequest(partition_key=source_id)
```

### 4.3 Schedule-Driven Automation

```python
@sensor(job=scheduled_ingestion_job, minimum_interval_seconds=60)
def schedule_check_sensor(context):
    """Check DuckDB for sources due for update."""
    import duckdb
    from croniter import croniter
    from datetime import datetime

    conn = duckdb.connect("metadata.db")

    schedules = conn.execute("""
        SELECT source_id, cron_schedule, last_run
        FROM schedule_definitions sd
        JOIN sources s USING (source_id)
        WHERE s.active = true AND sd.cron_schedule IS NOT NULL
    """).fetchall()

    now = datetime.now()

    for source_id, cron, last_run in schedules:
        cron_iter = croniter(cron, last_run or datetime.min)
        next_run = cron_iter.get_next(datetime)

        if next_run <= now:
            yield RunRequest(
                run_key=f"{source_id}_{now.isoformat()}",
                partition_key=str(source_id)
            )
```

---

## 5. Administrative Interface

### 5.1 Streamlit Control Plane

```python
import streamlit as st
import duckdb
from pydantic import BaseModel, ValidationError

# Tool-specific config schemas
class DltConfig(BaseModel):
    base_url: str
    endpoints: list[str]
    write_disposition: str = "append"
    primary_key: str | None = None

class CrawlConfig(BaseModel):
    url: str
    css_selector: str
    headless: bool = True
    word_count_threshold: int = 10

st.title("Data Source Registry")

# Source type selection
source_type = st.selectbox("Source Type", ["REST_API", "WEB_CRAWL", "PDF_ARCHIVE"])
tool_driver = st.selectbox("Tool", ["dlt", "crawl4ai", "cocoindex"])

# Dynamic form based on tool
if tool_driver == "dlt":
    base_url = st.text_input("Base URL")
    endpoints = st.text_area("Endpoints (one per line)").split("\n")

    config = DltConfig(base_url=base_url, endpoints=endpoints)

elif tool_driver == "crawl4ai":
    url = st.text_input("URL")
    css_selector = st.text_input("CSS Selector", "article.content")

    config = CrawlConfig(url=url, css_selector=css_selector)

# Validation and save
if st.button("Save Source"):
    try:
        # Pydantic validates before saving
        validated = config.model_dump()

        conn = duckdb.connect("metadata.db")
        # Insert into database...
        st.success("Source saved!")
    except ValidationError as e:
        st.error(f"Validation error: {e}")
```

### 5.2 Bilingual Metadata Form

```python
st.subheader("Bilingual Configuration")

source_lang = st.selectbox("Source Language", ["en", "ga", "es", "fr", "de"])
target_lang = st.selectbox("Target Language", ["en", "ga", "es", "fr", "de"])
domain = st.selectbox("Domain (TMX)", ["Legal", "Medical", "Technical", "General"])
alignment = st.selectbox("Alignment", ["sentence_aligned", "document_aligned"])
license_type = st.selectbox("License", ["CC-BY-4.0", "MIT", "Proprietary"])

# URL template for bilingual crawling
url_template = st.text_input(
    "URL Template",
    "https://site.com/{lang}/page",
    help="Use {lang} placeholder for language code"
)
```

---

## 6. Migration Roadmap

### Phase 1: Schema & Migration (Week 1)
1. Provision DuckDB persistent file
2. Define SQL DDL with JSON columns
3. Write migration script from `sources.yaml`

### Phase 2: Asset Factories (Week 2)
1. Refactor Dagster to remove hardcoded assets
2. Implement `load_sources_from_duckdb()`
3. Build tool-specific factory functions
4. Wire into Definitions

### Phase 3: Dynamic Scaling (Week 3)
1. Transition to partitioned asset pattern
2. Implement registry sensor
3. Configure schedule-driven automation

### Phase 4: Admin UI (Week 4)
1. Deploy Streamlit application
2. Implement Pydantic validation
3. Add TMX/ISO language code validation

---

## 7. Platform Comparison

### 7.1 Meltano

| Aspect | Assessment |
|--------|------------|
| **Pros** | CLI-driven, manages virtual environments, can orchestrate dlt |
| **Cons** | Creates YAML silo, doesn't solve scalability issue |
| **Verdict** | Replaces one static config with another |

### 7.2 Airbyte

| Aspect | Assessment |
|--------|------------|
| **Pros** | User-friendly UI for standard APIs |
| **Cons** | Custom code requires Docker containers conforming to Airbyte protocol |
| **Verdict** | Too heavy for lightweight dlt/Crawl4ai/CocoIndex stack |

### 7.3 Recommendation

**Custom DuckDB + Streamlit + Dagster**
- DuckDB: Queryable, typed configuration store
- Streamlit: Validation-rich admin interface
- Dagster: Dynamic asset generation and scheduling

This provides optimal flexibility without connector-centric constraints.

---

## 8. TMX and Metadata Standards

### 8.1 TMX Header Mapping

```sql
-- Map database fields to TMX attributes
SELECT
    source_lang AS srclang,
    'en' AS adminlang,
    'DagsterPipeline' AS creationtool,
    CASE source_type
        WHEN 'WEB_CRAWL' THEN 'HTML'
        WHEN 'PDF_ARCHIVE' THEN 'PlainText'
        ELSE 'unknown'
    END AS datatype,
    domain
FROM bilingual_metadata bm
JOIN sources s USING (source_id);
```

### 8.2 DataCite Integration

```sql
-- Add citation fields for academic datasets
ALTER TABLE bilingual_metadata ADD COLUMN doi VARCHAR;
ALTER TABLE bilingual_metadata ADD COLUMN contributor_type VARCHAR DEFAULT 'DataCollector';
ALTER TABLE bilingual_metadata ADD COLUMN is_translation_of VARCHAR;  -- Reference to original
```

---

## References

- DuckDB JSON: https://duckdb.org/docs/sql/data_types/json
- DuckDB Concurrency: https://duckdb.org/docs/connect/concurrency
- Dagster Dynamic Partitions: https://dagster.io/blog/dynamic-partitioning
- TMX Standard: https://standards.clarin.eu/sis/views/view-format.xq?id=fTMX
- DataCite Schema: https://schema.datacite.org/
- Streamlit: https://streamlit.io/


---

### `README.md` — 03-bilingual-dataset-creation

# Bilingual Dataset Creation

This directory contains research on creating high-quality Irish-English parallel corpora from multiple sources, with alignment tools and processing workflows.

## Overview

Creating bilingual datasets for Celtic languages requires combining multiple data sources with varying levels of quality and alignment. The primary goal is generating sentence-aligned parallel text suitable for machine translation training and evaluation.

### Dataset Size Estimates

| Source | Irish Words | English Words | Segments | Quality |
|--------|-------------|---------------|----------|---------|
| **Parallel Corpus (TMX)** | 68M | 62.5M | 130M | Excellent |
| **Duchas Folklore** | ~50M | ~30M | 80,000+ | Good |
| **Logainm Placenames** | - | - | 100,000+ | Excellent |
| **Tearma Terminology** | 100K+ | 100K+ | 10,000+ | Excellent |
| **Ainm Biographies** | 1.3M | - | 1,785 | Irish only |
| **Corpas.ie** | 240M | - | - | Monolingual |
| **Total Parallel** | **118M+** | **93M+** | **200K+ items** | Mixed |

## Documents in this Category

| Document | Focus | Key Topics |
|----------|-------|------------|
| `tmx-processing.md` | TMX file handling | Parsing, validation, export |
| `parallel-corpus-sources.md` | Source identification | Gaois, EU, government |
| `alignment-tools.md` | Text alignment | gaoisalign, hunalign |

## Primary Parallel Sources

### 1. Gaois Parallel Corpus (Highest Quality)

**URL:** https://www.gaois.ie/en/corpora/parallel/data

| Property | Value |
|----------|-------|
| **Format** | TMX (Translation Memory eXchange) |
| **Total Size** | ~130.5 million words |
| **Irish** | 68.0 million words |
| **English** | 62.5 million words |
| **Alignment** | Sentence-level |
| **License** | Open (verify specific terms) |

**Content Domains:**
- EU legislation (Regulations & Directives)
- Constitution of Ireland (1937)
- Acts of the Oireachtas (1922-2003+)
- Irish statutory instruments
- COVID-19 terminology

### 2. Duchas Folklore Collection

**API:** https://www.duchas.ie/api/v0.6

| Property | Value |
|----------|-------|
| **Irish Content** | ~66% |
| **English Content** | ~33% |
| **Items** | 80,000+ stories |
| **Alignment** | Metadata aligned, text requires processing |

**Collections:**
- Main Manuscript Collection (CBE): 2,400 volumes
- Schools' Collection (CBES): 740,000 pages
- Photographic Collection (CBEG): 80,000 photographs

### 3. Logainm Placenames

**API:** https://www.logainm.ie/api/v1.0

| Property | Value |
|----------|-------|
| **Entries** | 100,000+ |
| **Alignment** | Exact Irish-English pairs |
| **Metadata** | Geographic, historical variants |

### 4. Tearma Terminology

**URL:** https://www.tearma.ie/

| Property | Value |
|----------|-------|
| **Domains** | 40+ subject categories |
| **Alignment** | Term-level pairs |
| **Content** | Legal, medical, technical, EU |

## Data Quality Tiers

### Tier 1: Professional Translation (Highest)

- Gaois Parallel Corpus (TMX)
- EU official translations
- Government documents

**Characteristics:**
- Human translated
- Sentence-aligned
- Quality reviewed
- Consistent terminology

### Tier 2: Community/Editorial Content

- Duchas folklore (where aligned)
- Ainm.ie metadata
- Bilingual website content

**Characteristics:**
- Mixed translation quality
- Requires alignment
- May have style variations

### Tier 3: Machine-Assisted

- Back-translated content
- Web-scraped parallel pages
- Auto-aligned content

**Characteristics:**
- Requires quality filtering
- Higher noise ratio
- Useful for domain coverage

## Output Formats

### 1. JSON Lines (Streaming)

```json
{"id": 1, "irish": "Baile Átha Cliath", "english": "Dublin", "source": "logainm"}
{"id": 2, "irish": "Dia dhuit", "english": "Hello", "source": "tearma"}
```

### 2. TMX (Translation Memory)

```xml
<tu tuid="1">
  <tuv xml:lang="ga"><seg>Baile Átha Cliath</seg></tuv>
  <tuv xml:lang="en"><seg>Dublin</seg></tuv>
</tu>
```

### 3. Parquet (Analytics)

- Columnar storage
- Compressed (snappy/zstd)
- Schema-enforced
- Query-optimized

### 4. HuggingFace Datasets

```python
from datasets import Dataset
dataset = Dataset.from_dict({
    "irish": [...],
    "english": [...],
    "source": [...]
})
dataset.push_to_hub("gaois/irish-english-parallel")
```

## Processing Pipeline

```
Source Data
    |
    v
+-------------------+
|   Extraction      |  TMX parsing, API collection,
|                   |  web scraping
+--------+----------+
         |
         v
+-------------------+
|   Alignment       |  gaoisalign, hunalign,
|                   |  sentence splitting
+--------+----------+
         |
         v
+-------------------+
|   Normalization   |  UTF-8, orthography,
|                   |  deduplication
+--------+----------+
         |
         v
+-------------------+
|   Quality Filter  |  Length ratio, language ID,
|                   |  alignment score
+--------+----------+
         |
         v
+-------------------+
|   Export          |  JSONL, Parquet,
|                   |  HuggingFace
+-------------------+
```

## Quality Metrics

| Metric | Threshold | Purpose |
|--------|-----------|---------|
| **Length Ratio** | 0.5 - 2.0 | Filter misaligned |
| **Language ID Confidence** | >0.95 | Verify language |
| **Alignment Score** | >0.7 | Sentence correspondence |
| **Duplicate Ratio** | <5% | Deduplication check |

## Cross-References

- **Category 01 (Celtic Language AI)** - Models trained on this data
- **Category 02 (Data Acquisition)** - Collection pipelines
- Main research Category 03 (AI-Native Data Pipelines) - dlt patterns


---

### `alignment-tools.md` — 03-bilingual-dataset-creation

# Text Alignment Tools for Irish-English

## Overview

Text alignment is the process of matching parallel segments (sentences, phrases, or terms) between source and target languages. This document covers tools and techniques for aligning Irish-English parallel content.

---

## 1. Alignment Tools

### 1.1 gaoisalign (Irish-Specific)

**Repository:** https://github.com/gaois/gaoisalign

| Property | Value |
|----------|-------|
| **Language** | Python |
| **License** | MIT |
| **Focus** | Irish-English alignment |
| **Maintained** | Gaois Research Group |

**Installation:**

```bash
git clone https://github.com/gaois/gaoisalign.git
cd gaoisalign
pip install -e .
```

**Usage:**

```python
from gaoisalign import align

# Align parallel texts
irish_text = "Is é seo an chéad abairt. Seo an dara habairt."
english_text = "This is the first sentence. This is the second sentence."

alignments = align(irish_text, english_text)
for pair in alignments:
    print(f"GA: {pair.source}")
    print(f"EN: {pair.target}")
```

### 1.2 hunalign

**Repository:** https://github.com/danielvarga/hunalign

| Property | Value |
|----------|-------|
| **Language** | C++ |
| **License** | LGPL |
| **Focus** | Language-agnostic sentence alignment |
| **Dictionary** | Optional bilingual dictionary |

**Installation:**

```bash
# Ubuntu/Debian
sudo apt-get install hunalign

# From source
git clone https://github.com/danielvarga/hunalign.git
cd hunalign/src
make
```

**Usage:**

```bash
# Basic alignment
hunalign dictionary.txt source.txt target.txt > aligned.txt

# Without dictionary
hunalign -text /dev/null source.txt target.txt > aligned.txt
```

**Python Wrapper:**

```python
import subprocess
from pathlib import Path
from typing import List, Tuple

def hunalign(
    source_file: Path,
    target_file: Path,
    dictionary: Path = None
) -> List[Tuple[str, str]]:
    """Run hunalign and parse results."""
    cmd = ["hunalign"]

    if dictionary:
        cmd.append(str(dictionary))
    else:
        cmd.extend(["-text", "/dev/null"])

    cmd.extend([str(source_file), str(target_file)])

    result = subprocess.run(cmd, capture_output=True, text=True)

    alignments = []
    for line in result.stdout.strip().split("\n"):
        parts = line.split("\t")
        if len(parts) >= 2:
            alignments.append((parts[0], parts[1]))

    return alignments
```

### 1.3 Bleualign

**Repository:** https://github.com/rsennrich/Bleualign

| Property | Value |
|----------|-------|
| **Language** | Python |
| **License** | LGPL |
| **Method** | Uses MT output for alignment |
| **Quality** | High for noisy parallel text |

**Installation:**

```bash
pip install bleualign
```

**Usage:**

```python
from bleualign.align import Aligner

aligner = Aligner(
    source_file="irish.txt",
    target_file="english.txt",
    source_translation="irish_translated.txt"  # MT output
)

alignments = aligner.align()
```

### 1.4 vecalign

**Repository:** https://github.com/thompsonb/vecalign

| Property | Value |
|----------|-------|
| **Language** | Python |
| **License** | Apache 2.0 |
| **Method** | Neural sentence embeddings |
| **Model** | LASER/LaBSE |

**Installation:**

```bash
pip install vecalign
```

**Usage:**

```python
from vecalign import align

# Uses sentence embeddings for alignment
alignments = align(
    source_sentences=["Irish sentence 1", "Irish sentence 2"],
    target_sentences=["English sentence 1", "English sentence 2"],
    embedding_model="laser"
)
```

---

## 2. Sentence Splitting

### 2.1 Irish Sentence Tokenizer

```python
import re
from typing import List

def split_irish_sentences(text: str) -> List[str]:
    """
    Split Irish text into sentences.
    Handles common Irish abbreviations.
    """
    # Irish abbreviations that don't end sentences
    abbreviations = [
        r'Dr\.', r'Mr\.', r'Mrs\.', r'Ms\.',
        r'Uimh\.', r'lgh\.', r'féach',
        r'e\.g\.', r'i\.e\.',
        r'c\.', r'm\.sh\.'  # circa, mar shampla
    ]

    # Protect abbreviations
    protected = text
    for i, abbr in enumerate(abbreviations):
        protected = re.sub(abbr, f"<ABBR{i}>", protected)

    # Split on sentence boundaries
    sentences = re.split(r'(?<=[.!?])\s+', protected)

    # Restore abbreviations
    restored = []
    for sent in sentences:
        for i, abbr in enumerate(abbreviations):
            sent = sent.replace(f"<ABBR{i}>", abbr.replace('\\', ''))
        restored.append(sent.strip())

    return [s for s in restored if s]
```

### 2.2 Using spaCy

```python
import spacy

# Load Irish model (if available) or multilingual
try:
    nlp = spacy.load("ga_core_news_sm")
except:
    nlp = spacy.load("xx_sent_ud_sm")

def split_sentences_spacy(text: str) -> List[str]:
    """Split sentences using spaCy."""
    doc = nlp(text)
    return [sent.text.strip() for sent in doc.sents]
```

---

## 3. Alignment Quality Metrics

### 3.1 Length Ratio Check

```python
def length_ratio(source: str, target: str) -> float:
    """Calculate character length ratio."""
    if len(target) == 0:
        return float('inf')
    return len(source) / len(target)

def is_valid_alignment(source: str, target: str) -> bool:
    """Check if alignment is plausible based on length."""
    ratio = length_ratio(source, target)
    # Irish-English typically has ratio 0.8-1.3
    return 0.5 <= ratio <= 2.0
```

### 3.2 Alignment Score

```python
from sentence_transformers import SentenceTransformer
import numpy as np

model = SentenceTransformer('paraphrase-multilingual-MiniLM-L12-v2')

def alignment_score(source: str, target: str) -> float:
    """Calculate semantic similarity score."""
    embeddings = model.encode([source, target])
    similarity = np.dot(embeddings[0], embeddings[1]) / (
        np.linalg.norm(embeddings[0]) * np.linalg.norm(embeddings[1])
    )
    return float(similarity)

def filter_by_score(
    alignments: List[Tuple[str, str]],
    threshold: float = 0.7
) -> List[Tuple[str, str]]:
    """Filter alignments by semantic similarity."""
    filtered = []
    for source, target in alignments:
        score = alignment_score(source, target)
        if score >= threshold:
            filtered.append((source, target, score))
    return filtered
```

---

## 4. Complete Alignment Pipeline

```python
#!/usr/bin/env python3
"""
Complete Irish-English Alignment Pipeline
"""

from pathlib import Path
from typing import List, Dict, Tuple
from dataclasses import dataclass
import json

@dataclass
class AlignedPair:
    source: str
    target: str
    score: float
    method: str

class IrishEnglishAligner:
    def __init__(self):
        self.min_score = 0.7
        self.min_length = 5
        self.max_ratio = 2.0

    def preprocess(self, text: str) -> str:
        """Clean and normalize text."""
        # Normalize whitespace
        text = ' '.join(text.split())
        # Normalize quotes
        text = text.replace('"', '"').replace('"', '"')
        return text.strip()

    def split_sentences(self, text: str, lang: str) -> List[str]:
        """Split text into sentences."""
        sentences = split_irish_sentences(text)
        return [s for s in sentences if len(s) >= self.min_length]

    def align_documents(
        self,
        irish_text: str,
        english_text: str
    ) -> List[AlignedPair]:
        """Align two parallel documents."""
        # Preprocess
        irish = self.preprocess(irish_text)
        english = self.preprocess(english_text)

        # Split sentences
        irish_sents = self.split_sentences(irish, "ga")
        english_sents = self.split_sentences(english, "en")

        # Align using hunalign
        alignments = self._hunalign(irish_sents, english_sents)

        # Score and filter
        results = []
        for ga, en in alignments:
            if not is_valid_alignment(ga, en):
                continue

            score = alignment_score(ga, en)
            if score >= self.min_score:
                results.append(AlignedPair(
                    source=ga,
                    target=en,
                    score=score,
                    method="hunalign+semantic"
                ))

        return results

    def _hunalign(
        self,
        source_sents: List[str],
        target_sents: List[str]
    ) -> List[Tuple[str, str]]:
        """Run hunalign on sentence lists."""
        import tempfile

        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as sf:
            sf.write('\n'.join(source_sents))
            source_file = sf.name

        with tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False) as tf:
            tf.write('\n'.join(target_sents))
            target_file = tf.name

        return hunalign(Path(source_file), Path(target_file))

    def export(
        self,
        alignments: List[AlignedPair],
        output_path: Path
    ):
        """Export alignments to JSONL."""
        with output_path.open('w', encoding='utf-8') as f:
            for pair in alignments:
                record = {
                    "irish": pair.source,
                    "english": pair.target,
                    "score": pair.score,
                    "method": pair.method
                }
                f.write(json.dumps(record, ensure_ascii=False) + '\n')

def main():
    aligner = IrishEnglishAligner()

    # Example usage
    irish = """
    Is é seo an chéad abairt sa téacs.
    Tá an dara habairt anseo.
    Seo an tríú habairt.
    """

    english = """
    This is the first sentence in the text.
    The second sentence is here.
    This is the third sentence.
    """

    alignments = aligner.align_documents(irish, english)

    for pair in alignments:
        print(f"GA: {pair.source}")
        print(f"EN: {pair.target}")
        print(f"Score: {pair.score:.3f}")
        print()

    aligner.export(alignments, Path("alignments.jsonl"))

if __name__ == "__main__":
    main()
```

---

## 5. Dictionary Resources

### 5.1 Irish-English Dictionary Format

For hunalign and similar tools:

```text
# Irish-English dictionary for alignment
# Format: irish_word @ english_word
agus @ and
an @ the
atá @ is
bhí @ was
bheith @ be
```

### 5.2 Building from Téarma

```python
import httpx
from pathlib import Path

async def build_dictionary_from_tearma(output_path: Path):
    """Build alignment dictionary from Téarma terminology."""
    # Note: This is a conceptual example
    # Actual implementation depends on Téarma API availability

    terms = []
    # Fetch terms from Téarma API or scrape

    with output_path.open('w', encoding='utf-8') as f:
        for term in terms:
            irish = term.get("ga", "")
            english = term.get("en", "")
            if irish and english:
                f.write(f"{irish} @ {english}\n")
```

---

## 6. Tool Comparison

| Tool | Speed | Quality | Irish Support | Dependencies |
|------|-------|---------|---------------|--------------|
| **gaoisalign** | Medium | High | Native | Python |
| **hunalign** | Fast | Good | Generic | C++ |
| **Bleualign** | Slow | High | Via MT | Python, MT |
| **vecalign** | Medium | High | Via embeddings | Python, LASER |

### Recommendation

1. **Start with gaoisalign** - Irish-specific, maintained by Gaois
2. **Fall back to hunalign** - Fast, good for large volumes
3. **Use vecalign for noisy data** - Better at handling mismatches
4. **Score all alignments** - Filter by semantic similarity

---

## References

- gaoisalign: https://github.com/gaois/gaoisalign
- hunalign: https://github.com/danielvarga/hunalign
- Bleualign: https://github.com/rsennrich/Bleualign
- vecalign: https://github.com/thompsonb/vecalign
- LASER embeddings: https://github.com/facebookresearch/LASER


---

### `education-subject-inventory.md` — 03-bilingual-dataset-creation

# Irish Education Subject Data Inventory

Comprehensive inventory of subject data availability across the three scraped education websites.

## Executive Summary

| Metric | Value |
|--------|-------|
| Total JSON Files | ~1,100 |
| Junior Cycle Subjects | 18 core + 16 short courses |
| Senior Cycle Subjects | 50+ |
| Years of Statistics | 2011-2024 (14 years) |
| Languages | English (EN) and Irish (GA) |

---

## Data Sources Overview

### 1. curriculumonline.ie (300 files)

**Strongest Coverage:** Junior Cycle (8 of 18 subjects well covered)

| Content Type | Count | Notes |
|--------------|-------|-------|
| English pages | 171 | Main curriculum content |
| Irish (GA) pages | 129 | Bilingual mirror |
| Subject pages | ~150 | Junior Cycle focus |
| Short courses | ~20 | Various JC short courses |
| Early Childhood | 14 | Aistear framework |
| Primary | 2 | Limited coverage |
| Senior Cycle | 0 content | Navigation only |

### 2. examinations.ie (498 JSON + 102 stats files)

**Strongest Coverage:** Examination logistics, statistics, circulars

| Content Type | Count | Notes |
|--------------|-------|-------|
| Parameterized pages | 117 | Bilingual (EN/IR) |
| PDF references | 338 | Chief Examiner Reports, circulars |
| Statistics files | 102 | CSV + PDF (2011-2024) |
| Exam info pages | ~60 | 2024-2026 exams |

### 3. ncca.ie (300 files)

**Strongest Coverage:** Senior Cycle curriculum development, policy

| Content Type | Count | Notes |
|--------------|-------|-------|
| English pages | 224 | Primary content |
| Irish (GA) pages | 76 | Partial mirror |
| Development groups | 28 | All boards and groups |
| SC developments | 40+ | Subject development status |
| Research/publications | ~30 | Reports and papers |

---

## Junior Cycle Subject Inventory

### Subjects with Strong Data (8 subjects)

| Subject | curriculumonline | examinations | ncca | EN | GA | CBAs |
|---------|-----------------|--------------|------|----|----|------|
| **Gaeilge** | 44 pages | Stats | Dev group | ✓ | ✓ | CBA-1, CBA-2 |
| **Business Studies** | 25 pages | Stats | Dev group | ✓ | ✓ | CBA-1, CBA-2 |
| **English** | 21 pages | Stats | Dev group | ✓ | ✓ | CBA-1, CBA-2 |
| **Geography** | 23 pages | Stats | Dev group | ✓ | ✓ | CBA-1, CBA-2 |
| **Engineering** | 24 pages | Stats | Dev group | ✓ | ✓ | CBA-1, CBA-2 |
| **Applied Technology** | 23 pages | Stats | - | ✓ | ✓ | CBA-1, CBA-2 |
| **Graphics** | 20 pages | Stats | Dev group | ✓ | ✓ | CBA-1, CBA-2 |
| **Classics** | 18 pages | Stats | - | ✓ | ✓ | CBA-1, CBA-2 |

### Subjects with Limited Data (10 subjects - needs expansion)

| Subject | curriculumonline | examinations | ncca | Notes |
|---------|-----------------|--------------|------|-------|
| History | Navigation only | Stats | JC Dev group | Needs scraping |
| Home Economics | Navigation only | Stats | Dev group | Needs scraping |
| Mathematics | 1 page | Stats | Dev group | Needs scraping |
| Modern Foreign Languages | Navigation only | Stats | JC MFL Dev group | Needs scraping |
| Music | Navigation only | Stats | Dev group | Needs scraping |
| Religious Education | Navigation only | Stats | - | Needs scraping |
| Science | Navigation only | Stats | - | Needs scraping |
| Visual Art | Navigation only | Stats | - | Needs scraping |
| Wood Technology | Navigation only | Stats | - | Needs scraping |
| Jewish Studies | Navigation only | Stats | - | Needs scraping |

### Junior Cycle Short Courses (16 available)

| Short Course | Pages | Level | Notes |
|--------------|-------|-------|-------|
| Coding | ~5 | Standard | Strong data |
| CSPE | ~5 | Standard | Civic education |
| Digital Media Literacy | ~3 | Standard | |
| Philosophy | ~3 | Standard | |
| Physical Education | ~5 | Standard | |
| SPHE | ~5 | Standard | |
| Chinese Language & Culture | ~3 | Standard | |
| Artistic Performance | ~2 | Standard | |
| CSI: Forensic Science | ~2 | Level 2 | L2LP |
| History | ~2 | Level 2 | L2LP |
| Enterprise in Animation | ~2 | Level 2 | L2LP |
| + 5 others | ~10 | Various | |

---

## Senior Cycle Subject Inventory

### Subjects Under Active Development (40+)

Data from ncca.ie curriculum-developments section:

| Subject | Development Status | Draft Available | Consultation | Dev Group |
|---------|-------------------|-----------------|--------------|-----------|
| **Accounting** | Commenced | No | No | ✓ |
| **Agricultural Science** | In development | No | No | ✓ |
| **Applied Mathematics** | Existing | N/A | N/A | - |
| **Arabic** | Redeveloped | Yes | Closed | - |
| **Art** | Draft in progress | No | No | ✓ |
| **Biology** | Existing | N/A | N/A | - |
| **Business** | Envisioned | No | No | - |
| **Chemistry** | Existing | N/A | N/A | - |
| **Classical Languages** | In development | No | No | - |
| **Classical Studies** | Existing | N/A | N/A | - |
| **Climate Action & SD** | Envisioned | No | No | - |
| **Computer Science** | Draft completed | Yes | Open | ✓ |
| **Construction Studies** | Commenced | Yes | Open | ✓ |
| **Design & Comm Graphics** | Draft completed | Yes | Open | ✓ |
| **Drama, Film, Theatre** | Envisioned | No | No | - |
| **Economics** | Draft in progress | No | No | ✓ |
| **Engineering** | Commenced | No | No | ✓ |
| **English** | Commenced | No | No | ✓ |
| **Gaeilge** | In development | No | No | ✓ |
| **Geography** | Commenced | No | No | ✓ |
| **History** | Commenced | No | No | ✓ |
| **Home Economics** | Commenced | No | No | ✓ |
| **Mathematics** | Commenced | No | No | ✓ |
| **Modern Foreign Languages** | In development | No | No | ✓ |
| **Music** | Commenced | No | No | ✓ |
| **Physics** | Draft in progress | No | No | - |
| **Physics and Chemistry** | Existing | N/A | N/A | ✓ |
| **Politics and Society** | Existing | N/A | N/A | ✓ |
| **Technology** | In development | No | No | ✓ |
| **LC Physical Education** | Commenced | No | No | ✓ |
| **LCVP Link Modules** | Commenced | No | No | ✓ |
| **Transition Year** | In development | No | No | - |

### Modern Foreign Languages (8+)

| Language | LC Available | Statistics | Notes |
|----------|-------------|------------|-------|
| French | ✓ | ✓ | Traditional |
| German | ✓ | ✓ | Traditional |
| Spanish | ✓ | ✓ | Traditional |
| Italian | ✓ | ✓ | Traditional |
| Japanese | ✓ | ✓ | |
| Russian | ✓ | ✓ | |
| Arabic | ✓ (redeveloped) | ✓ | Recently updated |
| Mandarin Chinese | ✓ | ✓ | |
| Lithuanian | In development | - | New |
| Polish | In development | - | New |
| Portuguese | In development | - | New |

### LCA Modules (27 identified)

Located at /senior-cycle/lca/ on curriculumonline.ie:
- Active Leisure Studies, Agriculture/Horticulture, Childcare/Community Care
- Craft and Design, Dance, Drama, Engineering
- English and Communication, Gaeilge Chumarsáideach
- Graphics and Construction Studies, Hair and Beauty
- Hotel Catering and Tourism, ICT, Leisure and Recreation
- Mathematical Applications, Modern Languages, Music
- Office Administration, Religious Education, Science
- Sign Language, Social Education, Technology, Visual Art
- Vocational Preparation and Guidance

---

## Special Assessment Components by Subject

### Subjects with Oral Components

| Subject | Level | Oral % | Notes |
|---------|-------|--------|-------|
| Gaeilge | JC & LC | 40% | Mandatory |
| French | LC | 25% | Mandatory |
| German | LC | 25% | Mandatory |
| Spanish | LC | 25% | Mandatory |
| Italian | LC | 25% | Mandatory |
| Japanese | LC | 25% | Mandatory |
| Russian | LC | 25% | Mandatory |
| Arabic | LC | 25% | Mandatory |
| English | LC | 0% | No oral |

### Subjects with Practical/Lab Components

| Subject | Level | Practical % | Type |
|---------|-------|------------|------|
| Biology | LC | 0% | Mandatory experiments (no marks) |
| Chemistry | LC | 0% | Mandatory experiments (no marks) |
| Physics | LC | 0% | Mandatory experiments (no marks) |
| Agricultural Science | LC | 25% | Project |
| Construction Studies | LC | 50% | Project |
| Engineering | LC | 50% | Project |
| Technology | LC | 50% | Project |
| Home Economics | LC | 20% | Practical exam |
| Art | LC | 50% | Practical + written |
| Music | LC | 25% | Performance |
| PE (new) | LC | TBD | Physical activities |

### Subjects with Project/Coursework

| Subject | Level | Project % | Description |
|---------|-------|-----------|-------------|
| Geography | LC | 20% | Geographical investigation |
| History | LC | 20% | Research study |
| Politics & Society | LC | 20% | Citizenship project |
| Computer Science | LC | 30% | Coding project |
| Design & Comm Graphics | LC | 40% | Design project |
| LCVP | LC | 60% | Portfolio + link modules |

### Junior Cycle CBAs

All JC subjects have two Classroom-Based Assessments:
- **CBA-1**: Typically in 2nd year
- **CBA-2**: Typically in 3rd year
- **Assessment Task**: Linked to CBA-2, contributes to final grade

---

## Statistics Data Availability (examinations.ie)

### Years with Complete Data

| Year | JC Stats | LC Stats | LCA Stats | Gender | County |
|------|----------|----------|-----------|--------|--------|
| 2024 | ✓ | ✓ | ✓ | ✓ | ✓ |
| 2023 | ✓ | ✓ | ✓ | ✓ | ✓ |
| 2022 | ✓ | ✓ | ✓ | ✓ | ✓ |
| 2021 | ✓ | ✓ | ✓ | ✓ | ✓ |
| 2020 | ✓ | ✓ | ✓ | ✓ | ✓ |
| 2019 | ✓ | ✓ | ✓ | ✓ | ✓ |
| 2018 | ✓ | ✓ | ✓ | ✓ | ✓ |
| 2017 | ✓ | ✓ | ✓ | ✓ | ✓ |
| 2016 | ✓ | ✓ | ✓ | ✓ | ✓ |
| 2015 | ✓ | ✓ | ✓ | ✓ | ✓ |
| 2014 | Partial | Partial | Partial | ✓ | ✓ |
| 2013 | ✓ | ✓ | ✓ | ✓ | ✓ |
| 2012 | ✓ | ✓ | ✓ | ✓ | ✓ |
| 2011 | ✓ | ✓ | ✓ | ✓ | ✓ |

**Note:** 2014 data has some failed downloads (404 errors)

### Statistics File Types

- National results summary (CSV)
- Results by gender (CSV)
- Results by county (CSV)
- Results with >10 candidates (privacy filter)
- Grade distribution (PDF)

---

## Bilingual Coverage Analysis

### curriculumonline.ie

| Level | EN Pages | GA Pages | Coverage |
|-------|----------|----------|----------|
| Early Childhood | 7 | 7 | 100% |
| Primary | 1 | 1 | 100% |
| Junior Cycle | ~100 | ~80 | ~80% |
| Senior Cycle | 0 | 0 | N/A |

### ncca.ie

| Section | EN Pages | GA Pages | Coverage |
|---------|----------|----------|----------|
| Senior Cycle | ~150 | ~50 | ~33% |
| Junior Cycle | ~40 | ~15 | ~38% |
| Primary | ~20 | ~8 | ~40% |
| About | ~30 | ~3 | ~10% |

### examinations.ie

- Uses URL parameter `l=en` or `l=ir`
- Most pages have bilingual versions
- Statistics in English only

---

## Data Gaps and Expansion Priorities

### Priority 1: Critical Gaps

1. **Senior Cycle Subject Content** (curriculumonline.ie)
   - Only navigation pages exist
   - 50+ subjects need full scraping
   - Estimated: 300-500 additional pages

2. **Exam Papers and Marking Schemes** (examinations.ie)
   - References exist but PDFs not downloaded
   - Archive at /exammaterialarchive/
   - Estimated: 1000+ PDFs

3. **10 Junior Cycle Subjects** (curriculumonline.ie)
   - History, Mathematics, Science, etc.
   - Specification pages exist but not scraped

### Priority 2: Enhancement

1. **Statistics Files** (examinations.ie)
   - Directories exist but many files empty
   - Need targeted re-scraping

2. **Irish Language Versions** (all sites)
   - ~60-70% bilingual coverage
   - Complete GA versions needed

3. **Chief Examiner Reports** (examinations.ie)
   - Referenced 1999-2013
   - PDFs need downloading

### Priority 3: Completeness

1. **Primary Curriculum** (curriculumonline.ie)
   - Recently redeveloped (2025)
   - Limited current coverage

2. **Research Publications** (ncca.ie)
   - Many PDFs referenced
   - Need systematic download

---

## Subject Progression Mapping

### Junior Cycle → Senior Cycle Progressions

| JC Subject | LC Progression | Notes |
|------------|----------------|-------|
| Business Studies | Business, Accounting, Economics | Three pathways |
| Science | Biology, Chemistry, Physics | Specialization |
| Geography | Geography | Direct continuation |
| History | History | Direct continuation |
| Gaeilge | Gaeilge | T1→L1, T2→L2 streams |
| English | English | Direct continuation |
| Mathematics | Mathematics, Applied Maths | Two pathways |
| MFL | French, German, Spanish, etc. | Same languages |
| Graphics | Design & Comm Graphics | Renamed |
| Engineering | Engineering | Direct continuation |
| Home Economics | Home Economics | Direct continuation |
| Music | Music | Direct continuation |
| Art (Visual Art) | Art | Renamed |
| Wood Technology | Construction Studies, Technology | Two pathways |
| Coding (short course) | Computer Science | New subject |

---

## Recommended Next Steps

1. **Run Crawl4AI** with provided configurations to expand coverage
2. **Download PDFs** from examinations.ie archive
3. **Process with CocoIndex** pipeline to extract and embed
4. **Build BAML extraction** for structured data
5. **Create unified search** across all content
6. **Implement QwenVL** for PDF/image extraction


---

### `parallel-corpus-sources.md` — 03-bilingual-dataset-creation

# Parallel Corpus Sources for Irish-English

## Overview

This document catalogs all known sources of Irish-English parallel text, organized by quality tier and domain.

---

## 1. Tier 1: Professional Translation Sources

### 1.1 Gaois Parallel Corpus

**Primary source for high-quality parallel text.**

| Property | Value |
|----------|-------|
| **URL** | https://www.gaois.ie/en/corpora/parallel/data |
| **Size** | 130.5M words |
| **Format** | TMX |
| **Alignment** | Sentence-level |
| **Quality** | Professional translation |

**Content Breakdown:**

| Domain | Irish Words | English Words |
|--------|-------------|---------------|
| EU Legislation | ~30M | ~28M |
| Acts of Oireachtas | ~25M | ~23M |
| Constitution | ~50K | ~45K |
| Statutory Instruments | ~13M | ~12M |

### 1.2 EUR-Lex (EU Official Journal)

| Property | Value |
|----------|-------|
| **URL** | https://eur-lex.europa.eu |
| **Languages** | 24 EU languages including Irish |
| **Format** | Various (HTML, PDF, XML) |
| **Access** | Public domain |

**Irish Coverage:**
- Regulations and Directives (since 2007)
- Official Journal of the EU
- Court judgments

### 1.3 Houses of the Oireachtas

| Property | Value |
|----------|-------|
| **URL** | https://www.oireachtas.ie |
| **Content** | Debates, legislation |
| **Format** | HTML, PDF |
| **Alignment** | Document-level (needs processing) |

**Resources:**
- Dáil/Seanad debates (bilingual sections)
- Legislation (Acts, SIs)
- Committee reports

---

## 2. Tier 2: Institutional Sources

### 2.1 Logainm API (Placenames)

| Property | Value |
|----------|-------|
| **URL** | https://www.logainm.ie/api/v1.0 |
| **Items** | 100,000+ |
| **Alignment** | Term-level (exact pairs) |
| **Quality** | Expert validated |

**Data Fields:**
- `nameGA`: Irish placename
- `nameEN`: English placename
- `variants`: Historical forms
- `coordinates`: Geographic location

### 2.2 Téarma (Terminology)

| Property | Value |
|----------|-------|
| **URL** | https://www.tearma.ie |
| **Domains** | 40+ subject areas |
| **Alignment** | Term-level (exact pairs) |
| **Quality** | Expert validated |

**Subject Categories:**
- Legal/Law
- Medicine/Health
- Science/Technology
- Business/Finance
- EU terminology
- COVID-19 terms

### 2.3 Ainm.ie (Biographies)

| Property | Value |
|----------|-------|
| **URL** | https://www.ainm.ie |
| **Items** | 1,785 biographies |
| **Words** | 1.3M+ Irish |
| **Parallel** | Metadata only (names, places) |

**Note:** Biographies are Irish-only. Parallel content limited to:
- Person names (Irish/English forms)
- Place names (via Logainm links)
- Dates and metadata

---

## 3. Tier 3: Folklore & Heritage

### 3.1 Dúchas API (Folklore Collection)

| Property | Value |
|----------|-------|
| **URL** | https://www.duchas.ie/api/v0.6 |
| **Items** | 80,000+ stories |
| **Irish Content** | ~66% |
| **English Content** | ~33% |

**Collections:**

| Collection | Pages | Content |
|------------|-------|---------|
| **CBE (Main)** | 2,400 volumes | Ethnography, folklore |
| **CBES (Schools)** | 740,000 pages | Local traditions |
| **CBEG (Photos)** | 80,000 images | Visual documentation |

**Alignment Status:**
- Metadata aligned (bilingual)
- Story text: ~10% parallel, ~90% monolingual
- Requires manual alignment for parallel use

### 3.2 Tobar an Dualchais (Scotland)

| Property | Value |
|----------|-------|
| **URL** | https://www.tobarandualchais.co.uk |
| **Items** | 50,000+ recordings |
| **Languages** | Scottish Gaelic, Scots, English |
| **Format** | Audio with transcripts |

**Use Case:** Cross-Celtic comparison, not Irish-English parallel.

---

## 4. Tier 4: Web-Scraped Sources

### 4.1 Government Websites

Bilingual Irish government sites with `/en/` and `/ga/` paths:

| Site | Content | Alignment |
|------|---------|-----------|
| **gov.ie** | Government services | Page-level |
| **rte.ie/gaeilge** | News articles | Some parallel |
| **ncca.ie** | Curriculum documents | PDF parallel |

### 4.2 Wikipedia

| Property | Value |
|----------|-------|
| **Irish Wikipedia** | ~56,000 articles |
| **English Wikipedia** | 6.7M+ articles |
| **Overlap** | ~10-15% with interlanguage links |

**Challenges:**
- Articles not direct translations
- Different scope and detail
- Requires sentence alignment

### 4.3 Tatoeba

| Property | Value |
|----------|-------|
| **URL** | https://tatoeba.org |
| **Irish Sentences** | ~3,000 |
| **Format** | TSV download |
| **License** | CC BY 2.0 |

---

## 5. Monolingual Sources (For Back-Translation)

### 5.1 Corpas.ie

| Corpus | Words | Content |
|--------|-------|---------|
| **CNG (National Corpus)** | 100M | 2000-2024 texts |
| **Written Irish** | 131M | Literature, journalism |
| **Spoken Irish** | 9M | Transcribed speech |
| **Historical** | 3,000+ texts | 1600-1926 |

**URL:** https://www.corpas.ie

### 5.2 Common Crawl (Irish)

| Property | Value |
|----------|-------|
| **CC-100 Irish** | 108M tokens |
| **OSCAR Irish** | Variable |
| **Quality** | Mixed (web text) |

---

## 6. Dataset Licensing

| Source | License | Commercial Use |
|--------|---------|----------------|
| **Gaois TMX** | Open Government | Verify |
| **EUR-Lex** | Public Domain | Yes |
| **Logainm** | Open Data | Yes |
| **Duchas** | Open Data | Yes |
| **Tatoeba** | CC BY 2.0 | Yes (with attribution) |
| **Wikipedia** | CC BY-SA | Yes (share-alike) |

---

## 7. Acquisition Priority

### Phase 1: High-Quality Parallel (Week 1-2)

1. Download Gaois TMX files
2. Set up Logainm API collection
3. Set up Duchas API collection
4. Download Tatoeba Irish-English pairs

### Phase 2: Institutional Content (Week 3-4)

1. Scrape Téarma terminology
2. Process EUR-Lex Irish content
3. Collect government bilingual pages

### Phase 3: Extended Coverage (Week 5-6)

1. Wikipedia article alignment
2. Process folklore for parallel sections
3. Back-translation of monolingual content

---

## 8. Quality Assessment Matrix

| Source | Alignment | Translation | Domain | Volume |
|--------|-----------|-------------|--------|--------|
| **Gaois TMX** | ★★★★★ | ★★★★★ | Legal | ★★★★★ |
| **Logainm** | ★★★★★ | ★★★★★ | Geographic | ★★★★☆ |
| **Téarma** | ★★★★★ | ★★★★★ | Technical | ★★★☆☆ |
| **Duchas** | ★★★☆☆ | ★★★★☆ | Cultural | ★★★★★ |
| **EUR-Lex** | ★★★★☆ | ★★★★★ | Legal | ★★★★☆ |
| **Wikipedia** | ★★☆☆☆ | ★★★☆☆ | General | ★★★☆☆ |
| **Tatoeba** | ★★★★★ | ★★★☆☆ | General | ★★☆☆☆ |

---

## 9. Combined Dataset Structure

```
celtic_parallel_corpus/
├── legal/
│   ├── gaois_legislation.parquet
│   ├── eurlex_irish.parquet
│   └── oireachtas_acts.parquet
├── geographic/
│   ├── logainm_placenames.parquet
│   └── geographic_entities.parquet
├── terminology/
│   ├── tearma_terms.parquet
│   └── domain_glossaries.parquet
├── cultural/
│   ├── duchas_parallel.parquet
│   └── folklore_aligned.parquet
├── general/
│   ├── tatoeba_pairs.parquet
│   └── wikipedia_aligned.parquet
└── metadata/
    ├── sources.json
    └── statistics.json
```

---

## References

- Gaois Corpora: https://www.gaois.ie/en/corpora/
- EUR-Lex: https://eur-lex.europa.eu
- Tatoeba: https://tatoeba.org/en/downloads
- CC-100: https://data.statmt.org/cc-100/


---

### `tmx-processing.md` — 03-bilingual-dataset-creation

# TMX File Processing

## Overview

TMX (Translation Memory eXchange) is the standard format for parallel corpora in the translation industry. The Gaois Parallel Corpus provides 130.5 million words in TMX format, making it the largest single source of Irish-English parallel text.

---

## 1. TMX Format Structure

### 1.1 Basic Structure

```xml
<?xml version="1.0" encoding="UTF-8"?>
<!DOCTYPE tmx SYSTEM "tmx14.dtd">
<tmx version="1.4">
  <header
    creationtool="Gaois"
    creationtoolversion="1.0"
    datatype="plaintext"
    segtype="sentence"
    adminlang="en"
    srclang="ga"
    o-tmf="unknown">
  </header>
  <body>
    <tu tuid="1">
      <tuv xml:lang="ga">
        <seg>Is é seo an téacs Gaeilge.</seg>
      </tuv>
      <tuv xml:lang="en">
        <seg>This is the Irish text.</seg>
      </tuv>
    </tu>
  </body>
</tmx>
```

### 1.2 Key Elements

| Element | Description |
|---------|-------------|
| `<tmx>` | Root element with version |
| `<header>` | Metadata about the file |
| `<body>` | Contains translation units |
| `<tu>` | Translation unit (segment pair) |
| `<tuv>` | Translation unit variant (language) |
| `<seg>` | Segment text content |

### 1.3 Language Codes

| Code | Language | Usage |
|------|----------|-------|
| `ga` | Irish (Gaeilge) | ISO 639-1 |
| `en` | English | ISO 639-1 |
| `ga-IE` | Irish (Ireland) | BCP 47 |
| `en-IE` | English (Ireland) | BCP 47 |

---

## 2. Parsing Implementation

### 2.1 Basic Parser (xml.etree)

```python
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Iterator, Dict, Optional

def parse_tmx(filepath: Path) -> Iterator[Dict]:
    """
    Parse TMX file to extract parallel segments.

    Args:
        filepath: Path to TMX file

    Yields:
        Dict with id, irish, english fields
    """
    tree = ET.parse(filepath)
    root = tree.getroot()

    # Handle namespace if present
    ns = {"xml": "http://www.w3.org/XML/1998/namespace"}

    for tu in root.findall(".//tu"):
        segment = {
            "id": tu.get("tuid", ""),
            "changedate": tu.get("changedate", ""),
            "creationdate": tu.get("creationdate", "")
        }

        for tuv in tu.findall("tuv"):
            # Get language from xml:lang attribute
            lang = tuv.get("{http://www.w3.org/XML/1998/namespace}lang", "")

            seg = tuv.find("seg")
            if seg is not None and seg.text:
                text = seg.text.strip()

                if lang.startswith("ga"):
                    segment["irish"] = text
                elif lang.startswith("en"):
                    segment["english"] = text

        # Only yield if both languages present
        if "irish" in segment and "english" in segment:
            yield segment
```

### 2.2 Streaming Parser (Large Files)

```python
from xml.etree.ElementTree import iterparse
from typing import Iterator, Dict

def parse_tmx_streaming(filepath: Path) -> Iterator[Dict]:
    """
    Memory-efficient streaming parser for large TMX files.

    Args:
        filepath: Path to TMX file

    Yields:
        Dict with parallel segments
    """
    context = iterparse(str(filepath), events=("end",))

    current_tu = {}
    for event, elem in context:
        if elem.tag == "seg":
            # Get parent tuv for language
            pass  # Handle in tu processing

        elif elem.tag == "tuv":
            lang = elem.get("{http://www.w3.org/XML/1998/namespace}lang", "")
            seg = elem.find("seg")

            if seg is not None and seg.text:
                if lang.startswith("ga"):
                    current_tu["irish"] = seg.text.strip()
                elif lang.startswith("en"):
                    current_tu["english"] = seg.text.strip()

        elif elem.tag == "tu":
            if "irish" in current_tu and "english" in current_tu:
                current_tu["id"] = elem.get("tuid", "")
                yield current_tu.copy()

            current_tu = {}
            elem.clear()  # Free memory
```

### 2.3 Using translate-toolkit

```python
from translate.storage.tmx import tmxfile
from pathlib import Path
from typing import Iterator, Dict

def parse_with_toolkit(filepath: Path) -> Iterator[Dict]:
    """
    Parse TMX using translate-toolkit library.

    Args:
        filepath: Path to TMX file

    Yields:
        Dict with source, target, id
    """
    with open(filepath, 'rb') as f:
        tmx = tmxfile(f)

        for unit in tmx.units:
            if unit.source and unit.target:
                yield {
                    "id": unit.getid(),
                    "source": unit.source,
                    "target": unit.target,
                    "notes": unit.getnotes()
                }
```

---

## 3. Validation

### 3.1 Segment Validation

```python
from dataclasses import dataclass
from typing import List, Optional

@dataclass
class ValidationResult:
    valid: bool
    errors: List[str]
    warnings: List[str]

def validate_segment(segment: Dict) -> ValidationResult:
    """Validate a single parallel segment."""
    errors = []
    warnings = []

    irish = segment.get("irish", "")
    english = segment.get("english", "")

    # Check for empty content
    if not irish:
        errors.append("Empty Irish segment")
    if not english:
        errors.append("Empty English segment")

    # Check length ratio
    if irish and english:
        ratio = len(irish) / len(english)
        if ratio < 0.3 or ratio > 3.0:
            warnings.append(f"Unusual length ratio: {ratio:.2f}")

    # Check for encoding issues
    try:
        irish.encode('utf-8')
        english.encode('utf-8')
    except UnicodeEncodeError:
        errors.append("Encoding error in segment")

    # Check for likely misalignment
    if irish == english:
        warnings.append("Identical source and target")

    return ValidationResult(
        valid=len(errors) == 0,
        errors=errors,
        warnings=warnings
    )
```

### 3.2 Language Detection

```python
from langdetect import detect, detect_langs
from typing import Tuple

def verify_languages(segment: Dict) -> Tuple[bool, float, float]:
    """
    Verify language of each segment.

    Returns:
        Tuple of (valid, irish_confidence, english_confidence)
    """
    irish = segment.get("irish", "")
    english = segment.get("english", "")

    irish_conf = 0.0
    english_conf = 0.0

    try:
        irish_langs = detect_langs(irish)
        for lang in irish_langs:
            if lang.lang == "ga":
                irish_conf = lang.prob
                break
    except:
        pass

    try:
        english_langs = detect_langs(english)
        for lang in english_langs:
            if lang.lang == "en":
                english_conf = lang.prob
                break
    except:
        pass

    # Accept if confidence > 0.5 or text too short for detection
    valid = (
        (irish_conf > 0.5 or len(irish) < 20) and
        (english_conf > 0.5 or len(english) < 20)
    )

    return valid, irish_conf, english_conf
```

---

## 4. Export Formats

### 4.1 JSONL Export

```python
import json
from pathlib import Path
from typing import Iterator, Dict

def export_jsonl(
    segments: Iterator[Dict],
    output_path: Path,
    include_metadata: bool = True
):
    """Export segments to JSON Lines format."""
    with output_path.open("w", encoding="utf-8") as f:
        for segment in segments:
            record = {
                "irish": segment["irish"],
                "english": segment["english"]
            }

            if include_metadata:
                record["id"] = segment.get("id", "")
                record["source"] = segment.get("source_file", "")

            f.write(json.dumps(record, ensure_ascii=False) + "\n")
```

### 4.2 Parquet Export

```python
import pyarrow as pa
import pyarrow.parquet as pq
from typing import List, Dict

def export_parquet(
    segments: List[Dict],
    output_path: Path,
    compression: str = "snappy"
):
    """Export segments to Parquet format."""
    schema = pa.schema([
        pa.field("id", pa.string()),
        pa.field("irish", pa.string()),
        pa.field("english", pa.string()),
        pa.field("source", pa.string())
    ])

    # Build arrays
    ids = [s.get("id", "") for s in segments]
    irish = [s.get("irish", "") for s in segments]
    english = [s.get("english", "") for s in segments]
    sources = [s.get("source_file", "") for s in segments]

    table = pa.table({
        "id": ids,
        "irish": irish,
        "english": english,
        "source": sources
    }, schema=schema)

    pq.write_table(table, output_path, compression=compression)
```

### 4.3 HuggingFace Dataset

```python
from datasets import Dataset, DatasetDict
from typing import List, Dict

def export_huggingface(
    segments: List[Dict],
    dataset_name: str,
    push_to_hub: bool = False
):
    """Export to HuggingFace Datasets format."""
    dataset = Dataset.from_dict({
        "irish": [s["irish"] for s in segments],
        "english": [s["english"] for s in segments],
        "id": [s.get("id", "") for s in segments]
    })

    # Create train/validation/test splits
    splits = dataset.train_test_split(test_size=0.1)
    train_valid = splits["train"].train_test_split(test_size=0.1)

    dataset_dict = DatasetDict({
        "train": train_valid["train"],
        "validation": train_valid["test"],
        "test": splits["test"]
    })

    if push_to_hub:
        dataset_dict.push_to_hub(dataset_name)

    return dataset_dict
```

---

## 5. Complete Processing Pipeline

```python
#!/usr/bin/env python3
"""
Complete TMX Processing Pipeline
"""

import asyncio
from pathlib import Path
from typing import List, Dict, Iterator
from dataclasses import dataclass

@dataclass
class ProcessingStats:
    total_segments: int = 0
    valid_segments: int = 0
    invalid_segments: int = 0
    warnings: int = 0

class TMXProcessor:
    def __init__(self, input_dir: Path, output_dir: Path):
        self.input_dir = input_dir
        self.output_dir = output_dir
        self.stats = ProcessingStats()

    def process_file(self, filepath: Path) -> Iterator[Dict]:
        """Process single TMX file."""
        for segment in parse_tmx(filepath):
            self.stats.total_segments += 1

            # Validate
            result = validate_segment(segment)

            if result.valid:
                self.stats.valid_segments += 1
                segment["source_file"] = filepath.name
                yield segment
            else:
                self.stats.invalid_segments += 1

            self.stats.warnings += len(result.warnings)

    def process_all(self) -> List[Dict]:
        """Process all TMX files in directory."""
        all_segments = []

        for tmx_file in self.input_dir.glob("*.tmx"):
            print(f"Processing: {tmx_file.name}")
            segments = list(self.process_file(tmx_file))
            all_segments.extend(segments)

        return all_segments

    def export(self, segments: List[Dict]):
        """Export to all formats."""
        self.output_dir.mkdir(parents=True, exist_ok=True)

        # JSONL
        export_jsonl(
            iter(segments),
            self.output_dir / "parallel.jsonl"
        )

        # Parquet
        export_parquet(
            segments,
            self.output_dir / "parallel.parquet"
        )

        print(f"Exported {len(segments)} segments")

    def run(self):
        """Run complete pipeline."""
        print("Starting TMX processing...")

        segments = self.process_all()

        print(f"Stats: {self.stats}")

        self.export(segments)

        print("Processing complete!")

def main():
    processor = TMXProcessor(
        input_dir=Path("./tmx_files"),
        output_dir=Path("./output")
    )
    processor.run()

if __name__ == "__main__":
    main()
```

---

## 6. Gaois TMX Sources

### 6.1 Download URLs

| Corpus | Content | URL |
|--------|---------|-----|
| **EU Legislation** | Regulations, Directives | https://www.gaois.ie/en/corpora/parallel/data |
| **Constitution** | Bunreacht na hÉireann | Included in above |
| **Acts of Oireachtas** | 1922-2003+ | Included in above |
| **Statutory Instruments** | Irish law | Included in above |

### 6.2 Acquisition Script

```bash
#!/bin/bash
# Download Gaois Parallel Corpus TMX files

OUTPUT_DIR="./tmx_files"
mkdir -p "$OUTPUT_DIR"

# Download from Gaois (check actual URLs)
wget -P "$OUTPUT_DIR" \
  "https://www.gaois.ie/en/corpora/parallel/data/eu_legislation.tmx" \
  "https://www.gaois.ie/en/corpora/parallel/data/constitution.tmx" \
  "https://www.gaois.ie/en/corpora/parallel/data/acts.tmx"

echo "Download complete"
```

---

## References

- TMX 1.4 Specification: https://www.gala-global.org/tmx-14b
- translate-toolkit: https://toolkit.translatehouse.org/
- Gaois Parallel Corpus: https://www.gaois.ie/en/corpora/parallel/


---

## Original Sources

- `03-ai-native-data-pipelines/` (README.md, baml-dlt-integration.md, dagster-orchestration.md, lakehouse-architecture.md, metadata-control-plane.md)
- `03-bilingual-dataset-creation/` (README.md, alignment-tools.md, education-subject-inventory.md, parallel-corpus-sources.md, tmx-processing.md)
