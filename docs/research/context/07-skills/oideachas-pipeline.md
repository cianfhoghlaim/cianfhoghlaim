---
name: oideachas-pipeline
description: Celtic education curriculum pipeline for Irish, UK, and pan-Celtic content processing with DLT ingestion, CocoIndex embeddings, and Dagster orchestration.
---

# Oideachas Pipeline

**Version:** 1.0 | **Last Updated:** 2025-12

## Overview

The oideachas (Irish: "education") pipeline processes Celtic education curriculum content from multiple sources (NCCA, SEC, UK DfE) and transforms it into searchable, AI-enhanced learning materials.

| Feature | Description |
|---------|-------------|
| DLT Ingestion | Multi-source curriculum extraction |
| CocoIndex Flows | Embedding generation for semantic search |
| Dagster Assets | Orchestrated data transformation |
| ADK Agents | Education-focused AI assistants |

## When to Use This Skill

Activate when users need:

- "Process curriculum documents from NCCA or SEC"
- "Generate embeddings for curriculum search"
- "Build education knowledge graph"
- "Create ADK agent for curriculum queries"
- "Extract exam papers and marking schemes"

## Project Integration

### Data Flow Location

| Component | Path |
|-----------|------|
| Main Pipeline | `sruth/oideachais/` |
| DLT Sources | `sruth/oideachais/dlt_sources/` |
| CocoIndex Flows | `sruth/oideachais/cocoindex_flows/` |
| Dagster Definitions | `sruth/oideachais/dagster/` |
| ADK Agents | `sruth/oideachais/agents/` |

### Research References (taighde/)

| Directory | Relevant Documents |
|-----------|-------------------|
| `taighde_scoil/` | Curriculum analysis, indexing strategies |
| `taighde_teanga/` | Irish NLP resources, dialect handling |

### ML Model Dependencies (sruth/meaisinfhoghlaim/)

| Model | Usage |
|-------|-------|
| UCCIX-Llama2-13B | Irish text generation |
| GaBERT | Irish embeddings |
| Qwen2.5-Math-7B | Bilingual math reasoning |
| ColPali | Visual document embeddings |

## Core Concepts

### 1. DLT Source Configuration

```python
from dlt import pipeline, source

@dlt.source
def ncca_curriculum():
    """NCCA curriculum document source."""
    yield dlt.resource(
        fetch_specifications,
        name="specifications",
        write_disposition="merge",
        primary_key="specification_id"
    )
```

### 2. CocoIndex Embedding Flow

```python
import cocoindex as ci

@ci.flow_def(name="curriculum_embeddings")
def curriculum_embeddings(doc: ci.DataScope):
    """Generate embeddings for curriculum documents."""
    text = doc.content.text
    embedding = ci.functions.embed(
        text,
        model="text-embedding-3-large",
        batch_size=100  # REQUIRED: min batch size
    )
    return {"embedding": embedding}
```

### 3. Dagster Asset Definition

```python
from dagster import asset, AssetExecutionContext

@asset(
    group_name="curriculum",
    compute_kind="dlt",
)
def curriculum_documents(context: AssetExecutionContext):
    """Ingest NCCA curriculum documents."""
    pipeline = dlt.pipeline(
        pipeline_name="ncca_curriculum",
        destination="duckdb",
        dataset_name="curriculum"
    )
    # CRITICAL: Single-threaded DuckDB access
    return pipeline.run(ncca_curriculum())
```

## Cianfhoghlaim-Specific Usage

### Database Safety (from CLAUDE.md)

**DuckDB:** SINGLE_THREADED_ONLY
```python
# Use SerialDatabaseExecutor for DuckDB access
from sruth.storage import SerialDatabaseExecutor

with SerialDatabaseExecutor() as db:
    db.execute("SELECT * FROM curriculum")
```

**LanceDB:** MVCC-safe with automatic conflict resolution
```python
# LanceDB handles concurrent writes with retry/backoff
import lancedb

db = lancedb.connect("./embeddings")
table = db.create_table("curriculum", data, mode="overwrite")
```

### Embedding Batching

```python
# REQUIRED: Batch minimum 100 texts per API call
texts = [doc.content for doc in documents]
embeddings = embed_batch(texts, batch_size=100)

# For bulk inserts >50 rows, drop HNSW index first
db.execute("ALTER TABLE curriculum DROP INDEX embedding_idx")
# ... insert data ...
db.execute("CREATE INDEX embedding_idx ON curriculum USING HNSW(embedding)")
```

## Best Practices

1. **Always batch embeddings** - Minimum 100 texts per API call
2. **Single-threaded DuckDB** - Use SerialDatabaseExecutor
3. **Irish models** - Use UCCIX or GaBERT for Irish text
4. **BAML validation** - Schema validation for LLM extraction

## Resources

- **OpenSpec:** `openspec/specs/oideachais-pipeline/spec.md`
- **Dagster Docs:** https://docs.dagster.io
- **CocoIndex Docs:** https://cocoindex.io/docs
- **Related Skills:** dagster, cocoindex, dlt, lancedb, baml
