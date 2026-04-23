---
name: lancedb
description: Expert assistance for vector database development with LanceDB. Use when users need vector search, semantic search, RAG applications, hybrid search, multimodal embeddings, or production-scale vector storage.
---

# LanceDB - Embedded Vector Database

**Version:** >=0.15.0 | **Last Updated:** 2025-04

## Overview

LanceDB is an open-source, embedded vector database for AI applications:

- **Embedded**: Runs in-process without a separate server
- **Multimodal**: Store vectors, text, images, and audio together
- **Scalable**: Billion-scale vectors with disk-based indexes
- **Cloud-Native**: S3-compatible storage with serverless option
- **HNSW Indexing**: High-performance approximate nearest neighbor search
- **MVCC Safety**: Multi-version concurrency control for safe concurrent operations
- **Hybrid Search**: Combine vector and full-text search

**Documentation**: https://lancedb.github.io/lancedb/

## When to Use This Skill

Activate when users need:

- "Build a RAG application with vector search"
- "Store and search embeddings"
- "Implement semantic search"
- "Combine vector and full-text search"
- "Store multimodal data (images, text)"

## Core Concepts

### 1. Connection and Tables

```python
import lancedb
import pyarrow as pa

# Local connection
db = lancedb.connect("data/my-database")

# Cloud connection
db = lancedb.connect("db://my-database", api_key="...", region="us-east-1")

# S3 connection
db = lancedb.connect("s3://my-bucket/lancedb")

# Create table with data
data = [
    {"id": 1, "text": "Hello world", "vector": [0.1] * 128},
    {"id": 2, "text": "Goodbye world", "vector": [0.2] * 128}
]
table = db.create_table("documents", data=data)

# Open existing table
table = db.open_table("documents")

# List tables
print(db.table_names())
```

### 2. Schema Definition

```python
import pyarrow as pa

schema = pa.schema([
    pa.field("id", pa.int64()),
    pa.field("text", pa.string()),
    pa.field("vector", pa.list_(pa.float32(), 128)),  # 128-dim vector
    pa.field("metadata", pa.string()),
    pa.field("tags", pa.list_(pa.string()))
])

table = db.create_table("documents", schema=schema)
```

### 3. Vector Search

```python
# Basic search
query_vector = [0.15] * 128
results = table.search(query_vector).limit(10).to_pandas()

# With metadata filtering (pre-filter)
results = (table.search(query_vector)
          .where("category = 'tech'")
          .limit(10)
          .to_pandas())

# Specify distance metric
results = (table.search(query_vector)
          .metric("cosine")  # cosine, l2, dot
          .limit(10)
          .to_pandas())

# Select specific columns
results = (table.search(query_vector)
          .select(["id", "text"])
          .limit(10)
          .to_pandas())
```

### 4. Full-Text Search

```python
# Create FTS index
table.create_fts_index("text")

# Perform full-text search
results = table.search("machine learning", query_type="fts").limit(10).to_pandas()
```

### 5. Hybrid Search

```python
# Combine vector and full-text search
results = (table.search(query_type="hybrid")
          .vector(query_vector)
          .text("machine learning")
          .limit(10)
          .rerank(method="rrf")  # Reciprocal Rank Fusion
          .to_pandas())
```

### 6. Indexing

**IVF-PQ Index** (for large datasets):
```python
table.create_index(
    metric="cosine",
    index_type="IVF_PQ",
    num_partitions=256,
    num_sub_vectors=16
)
```

**HNSW Index** (for accuracy):
```python
table.create_index(
    metric="cosine",
    index_type="HNSW",
    m=20,
    ef_construction=150
)
```

## Common Patterns

### RAG Application

```python
import lancedb
from lancedb.embeddings import get_registry
from lancedb.pydantic import LanceModel, Vector

# Setup embedding model
model = get_registry().get("openai").create(name="text-embedding-3-small")

class Document(LanceModel):
    text: str = model.SourceField()
    vector: Vector(model.ndims()) = model.VectorField()
    source: str
    chunk_id: int

# Create table
db = lancedb.connect("~/.lancedb")
table = db.create_table("documents", schema=Document)

# Add documents (embeddings auto-generated)
docs = [
    {"text": "LanceDB is a vector database", "source": "docs", "chunk_id": 1},
    {"text": "Vector search enables semantic retrieval", "source": "blog", "chunk_id": 2}
]
table.add(docs)

# Create indexes
table.create_fts_index("text")
table.create_index(metric="cosine")

# Search
def search_documents(query: str, limit: int = 5):
    results = (table.search(query, query_type="hybrid")
              .limit(limit)
              .to_pydantic(Document))
    return results

results = search_documents("How does semantic search work?")
```

### Image Similarity

```python
from transformers import CLIPProcessor, CLIPModel
import torch
from PIL import Image

# Load CLIP
model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32")
processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")

def get_image_embedding(image_path):
    image = Image.open(image_path)
    inputs = processor(images=image, return_tensors="pt")
    with torch.no_grad():
        embedding = model.get_image_features(**inputs)
    return embedding[0].numpy().tolist()

# Create image database
db = lancedb.connect("./image_db")
data = [
    {"path": img, "embedding": get_image_embedding(img), "category": cat}
    for img, cat in image_files
]
table = db.create_table("images", data)
table.create_index(metric="cosine")

# Search similar images
query_embedding = get_image_embedding("query.jpg")
results = table.search(query_embedding).limit(10).to_pandas()
```

### Incremental Updates

```python
# Add new data
new_data = [{"id": 3, "text": "New document", "vector": [0.3] * 128}]
table.add(new_data)

# Update records
table.update(where="id = 1", values={"text": "Updated text"})

# Delete records
table.delete("id IN (1, 2)")

# Compact table (merge fragments)
table.compact()
```

### Multi-Tenant Setup

```python
def get_tenant_table(tenant_id: str):
    db = lancedb.connect(f"s3://my-bucket/{tenant_id}")
    return db.open_table("documents")

# Each tenant has isolated data
tenant_a = get_tenant_table("tenant-a")
tenant_b = get_tenant_table("tenant-b")
```

## TypeScript Usage

```typescript
import * as lancedb from "@lancedb/lancedb";

const db = await lancedb.connect("data/my-database");

const table = await db.createTable("my_table", [
  { id: 1, vector: [0.1, 1.0], text: "foo" },
  { id: 2, vector: [3.9, 0.5], text: "bar" }
]);

// Search
const results = await table
  .vectorSearch([0.1, 0.3])
  .limit(10)
  .toArray();

// With filter
const filtered = await table
  .vectorSearch([0.1, 0.3])
  .where("id > 1")
  .limit(10)
  .toArray();
```

## Distance Metrics

| Metric | Use Case | Range |
|--------|----------|-------|
| `l2` (Euclidean) | General purpose | [0, inf), lower = similar |
| `cosine` | Unnormalized embeddings | [-1, 1], higher = similar |
| `dot` | Normalized embeddings | [-1, 1], higher = similar |

## Index Selection Guide

| Scenario | Index Type | Parameters |
|----------|-----------|------------|
| <100K vectors | None (brute force) | - |
| Memory constrained | IVF_PQ | num_partitions=256 |
| Accuracy critical | HNSW | m=20, ef_construction=150 |
| Large scale | IVF_HNSW_PQ | Combine both |

## Best Practices

1. **Use Float16 for vectors** - 50% storage savings
2. **Store metadata with vectors** - Avoid joins
3. **Pre-filter when possible** - Narrow search space
4. **Compact regularly** - Merge fragments for performance
5. **Batch inserts** - 1000-10000 rows at a time

## SQL Queries

```python
# Full SQL support via DataFusion
results = db.sql("SELECT * FROM documents WHERE score > 0.8").to_pandas()

# Aggregations
stats = db.sql("""
    SELECT category, AVG(score) as avg_score
    FROM documents
    GROUP BY category
""").to_pandas()
```

## Deployment Options

**OSS (Self-Hosted):**
```python
db = lancedb.connect("./data")  # Local
db = lancedb.connect("s3://bucket/path")  # S3
```

**LanceDB Cloud:**
```python
db = lancedb.connect("db://my-database", api_key="...", region="us-east-1")
```

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

## Resources

- **Documentation**: https://lancedb.github.io/lancedb/
- **GitHub**: https://github.com/lancedb/lancedb
- **Examples**: https://github.com/lancedb/vectordb-recipes
- **Blog**: https://blog.lancedb.com/
