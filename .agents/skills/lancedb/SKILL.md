---
name: lancedb
description: Expert assistance for vector database development with LanceDB. Use when users need vector search, semantic search, RAG applications, hybrid search, multimodal embeddings, time-travel / versioned RAG, LanceDB Cloud, Lance + Iceberg, Ibis + lance_scan, the embeddings registry, or production-scale vector storage. Powers the BIEP `cianfhoghlaim.lc.<subject>.<level>_<lang>` companion tables (the canonical v1 CocoIndex `mount_table_target` target for the 6 LC subjects + `gov.ie` circulars) using the shared `BAAI/bge-m3` 1024-d embedder.
---

# LanceDB - Embedded Vector Database

**Version:** >=0.33.0 (pylance >= 0.33) | **Last Updated:** 2026-06-29

## Overview

LanceDB is an open-source, embedded vector database for AI applications:

- **Embedded**: Runs in-process without a separate server
- **Multimodal**: Store vectors, text, images, and audio together
  ("fat table" pattern with BLOBs + vectors in the same row)
- **Scalable**: Billion-scale vectors with disk-based indexes
- **Cloud-Native**: S3-compatible storage with serverless option
  (LanceDB Cloud, regions: us-east-1, us-west-2, eu-west-1, ap-south-1)
- **HNSW-backed IVF Indexing**: HNSW is **not** a top-level Python
  index in LanceDB — it is exposed only as a sub-index inside IVF
  partitions: `IVF_HNSW_FLAT` (no quant), `IVF_HNSW_SQ` (scalar quant,
  best recall/latency trade-off), `IVF_HNSW_PQ` (product quant).
  Use the `IvfHnswSq` config class in async Python.
- **MVCC Safety**: Multi-version concurrency control for safe concurrent
  operations (use `lancedb.connect(...)` + `SerialDatabaseExecutor`)
- **Hybrid Search**: Combine vector and full-text search with RRF reranking
- **Time-travel**: `table.checkout(version)` for versioned RAG, A/B testing
  of embedding models, knowledge-base audits
- **Lance Namespace / Iceberg**: expose Lance tables as Iceberg to PyIceberg
  consumers
- **Lance + Ray**: distributed indexing for > 1M rows
- **Ibis + DuckDB**: federated SQL over Lance via `lance_scan()`

**Documentation**: https://lancedb.github.io/lancedb/

## When to Use This Skill

Activate when users need:

- "Build a RAG application with vector search"
- "Store and search embeddings"
- "Implement semantic search"
- "Combine vector and full-text search" (vector + BM25 with RRF reranking)
- "Store multimodal data (images, text)" — use the multimodal "fat table"
  pattern, not the "pointer strategy"
- "Version my RAG index / A/B test embedding models" — use
  `table.checkout(version)` and `table.version`
- "Use OpenAI / Cohere / HuggingFace / Gemini / Bedrock / Ollama
  embeddings" — use the `get_registry().get(...)` pattern
- "Query Lance from DuckDB / marimo" — use Ibis + `lance_scan()`
- "Expose Lance as Iceberg to PyIceberg" — use `lance.namespace`
- "Deploy to LanceDB Cloud" — see the LanceDB Cloud regions +
  auto-compaction + auto-reindexing section
- "Run a TS / Next.js app against Lance" — use the modern TS API
  (`search()` not `vectorSearch()`)

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

# Multilingual / Irish FTS — use the right tokenizer
table.create_fts_index(
    "text",
    tokenizer="en_stem",  # or "default", "whitespace", "raw", "jieba" (zh),
                          # "no", "fr", "de", "es", "it", "pt", "ru", …
    with_stopwords=["the", "a", "an"],  # optional stopword list
)

# Lowercase + ASCII folding for multilingual corpora
table.create_fts_index("text", language="English", stem=True, remove_stop_words=True)
```

**For multilingual corpora (Irish, Scottish Gaelic, Welsh, Breton)**,
use the `default` tokenizer (Unicode-aware) and pre-normalise the
text via `unicodedata.normalize("NFKC", text)` before insert. For
English-heavy corpora, use `en_stem` for Porter-stemmed matching.

### 5. Hybrid Search

```python
# Combine vector and full-text search with RRF (Reciprocal Rank Fusion)
results = (table.search(query_type="hybrid")
          .vector(query_vector)
          .text("machine learning")
          .limit(10)
          .rerank(method="rrf")
          .to_pandas())

# Pre-filter vs post-filter
results = (table.search(query_vector)
          .where("category = 'tech'")     # pre-filter (faster, selective)
          .limit(10)
          .to_pandas())

results = (table.search(query_vector)
          .where("score > 0.8")
          .prefilter(False)               # post-filter (slower, non-selective)
          .limit(10)
          .to_pandas())

# refine_factor oversampling for higher accuracy
results = (table.search(query_vector)
          .refine_factor(10)              # oversample 10x then re-rank
          .limit(10)
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

**HNSW-backed IVF Index** (HNSW is NOT top-level — see vector-index.md):
```python
table.create_index(
    metric="cosine",
    index_type="IVF_HNSW_SQ",   # or "IVF_HNSW_FLAT" for unquantized
    num_partitions=64,          # num_rows // 1_048_576 starting point
    m=20,
    ef_construction=150,
)

# Async / config-object form (preferred for new code):
from lancedb.index import IvfHnswSq
await table.create_index("vector", config=IvfHnswSq(
    distance_type="cosine", num_partitions=64, m=20, ef_construction=150,
))
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

## TypeScript Usage (modern API)

The **deprecated** `vectorSearch(...)` API has been replaced by
`search(...)` with explicit `queryType`. Use the modern API:

```typescript
import * as lancedb from "@lancedb/lancedb";
import { embedding, rerankers } from "@lancedb/lancedb";
import { Field, Float32, FixedSizeList, Schema, Utf8 } from "apache-arrow";
import "dotenv/config";

const db = await lancedb.connect("data/my-database");

// Declarative schema via the embeddings registry
const openai = embedding.getRegistry().get("openai");
const embedModel = openai.create({ model: "text-embedding-3-small" });

const schema = new Schema([
  new Field("id", new Utf8(), false),
  new Field("text", new Utf8(), false),
  new Field("vector", new FixedSizeList(1024, new Field("item", new Float32())), false),
]);

// Vector search (modern API — `search()`, not `vectorSearch()`)
const table = await db.openTable("documents");
const results = await table
  .search(Array.from(embedModel.embed("machine learning")))
  .limit(10)
  .toArray();

// Hybrid search with RRF reranking
const hybrid = await table
  .search(queryType: "hybrid", Array.from(embedModel.embed("machine learning")), "machine learning")
  .rerank(rerankers.RRFReranker())
  .limit(10)
  .toArray();

// LanceDB Cloud
// .env: LANCEDB_URI=db://my-database, LANCEDB_API_KEY=...
const cloud = await lancedb.connect(process.env.LANCEDB_URI!, {
  apiKey: process.env.LANCEDB_API_KEY!,
  region: "eu-west-1",
});
```

**For the full modern TS reference**, see
[`references/typescript-modern-api.md`](references/typescript-modern-api.md).

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
| Accuracy critical | IVF_HNSW_SQ | num_partitions = num_rows // 1_048_576, m=20, ef_construction=150 |
| Best recall/size | IVF_HNSW_FLAT | m=20, ef_construction=150, no quant (raw + HNSW) |
| Max compression | IVF_RQ | num_partitions = num_rows // 4096, RaBitQ |
| Small dim (≤256) | IVF_PQ | num_partitions = num_rows // 4096, num_sub_vectors = dim // 8 |

## Advanced Patterns

### Time-travel / Versioned RAG

```python
# Get the current version
current = table.version  # e.g. 7

# Query a specific historical version (read-only)
historical = table.checkout(current - 1)
results = historical.search(query_vector).limit(10).to_pandas()

# Restore a previous version (writes a new version with the old data)
table.restore(4)  # creates version 8 with the data from version 4

# A/B test two embedding models: index the same data twice
# (once with model A, once with model B), then search both tables
# and compare scores.
```

Use cases: model rollback, A/B testing, knowledge-base audits,
reproducible experiments. See
[`references/time-travel-rag.md`](references/time-travel-rag.md).

### Embeddings Registry (10+ providers)

```python
from lancedb.embeddings import get_registry

registry = get_registry()

# OpenAI
model = registry.get("openai").create(name="text-embedding-3-small")

# Cohere
model = registry.get("cohere").create(name="embed-english-v3.0")

# HuggingFace (local)
model = registry.get("huggingface").create(
    name="sentence-transformers/all-MiniLM-L6-v2",
    device="cuda",
)

# Sentence-Transformers
model = registry.get("sentence-transformers").create(
    name="BAAI/bge-large-en-v1.5",
)

# ColBERT (multi-vector)
model = registry.get("colbert").create(name="colbert-ir/colbertv2.0")

# Gemini
model = registry.get("gemini").create(name="text-embedding-004")

# Bedrock
model = registry.get("bedrock").create(name="amazon.titan-embed-text-v1")

# Ollama (local)
model = registry.get("ollama").create(name="nomic-embed-text")

# OpenCLIP (multimodal image+text)
model = registry.get("open-clip").create(name="ViT-B-32")
```

Use `LanceModel` with `SourceField()` and `VectorField()` to bind the
embedder to a column:

```python
from lancedb.pydantic import LanceModel, Vector

class Document(LanceModel):
    text: str = model.SourceField()
    vector: Vector(model.ndims()) = model.VectorField()
    filename: str
```

See [`references/embed-functions-registry.md`](references/embed-functions-registry.md).

### Multimodal "fat table" pattern

```python
import pyarrow as pa

# Store images / audio / PDFs as BLOBs in the same row as the embedding
schema = pa.schema([
    pa.field("id", pa.int64()),
    pa.field("filename", pa.string()),
    pa.field("image_blob", pa.large_list(pa.uint8())),  # BLOB
    pa.field("image_embedding", pa.list_(pa.float32(), 768)),  # CLIP
    pa.field("description", pa.string()),
    pa.field("tags", pa.list_(pa.string())),
])

table = db.create_table("multimodal", schema=schema)

# Insert
table.add([{
    "id": 1,
    "filename": "recipe.png",
    "image_blob": open("recipe.png", "rb").read(),  # bytes
    "image_embedding": clip_embed("recipe.png"),
    "description": "Beef stew with root vegetables",
    "tags": ["main", "irish"],
}])

# Range-read the BLOB only for top-K results (avoid full-row reads)
results = table.search(query_vec).limit(10).to_pandas()
for r in results.itertuples():
    img = pa.ipc.open_stream(r.image_blob).read()  # or just use the bytes
```

For very large BLOBs (> 1 MB), prefer the "pointer strategy" — store
the BLOB in S3/R2 and put the URL in the row.

### Lance Namespace / Iceberg

Expose a Lance table to Iceberg consumers (PyIceberg, DuckDB
`iceberg_attach`):

```python
import lance.namespace

# Connect to an Iceberg REST catalog (e.g. Lakekeeper, Polaris)
ns = lance.namespace.connect(
    "iceberg",
    REST_URL="http://lakekeeper:8181/catalog",
    S3_ENDPOINT="http://minio:9000",
    S3_ACCESS_KEY_ID="...",
    S3_SECRET_ACCESS_KEY="...",
)

# Register an existing Lance table as an Iceberg table
ns.create_namespace("cianfhoghlaim")
ns.create_table("cianfhoghlaim.leabharlann_books", metadata={"lance_uri": "s3://lance/leabharlann_books"})

# Query from PyIceberg
from pyiceberg.catalog import load_catalog
catalog = load_catalog("cianfhoghlaim", type="rest", uri="http://lakekeeper:8181/catalog")
tbl = catalog.load_table("cianfhoghlaim.leabharlann_books")
df = tbl.scan().to_pandas()
```

### Ibis + DuckDB `lance_scan()`

```python
import duckdb

con = duckdb.connect()
con.execute("INSTALL lance; LOAD lance;")
con.execute(
    "CREATE VIEW books AS SELECT * FROM lance_scan('s3://lance/leabharlann_books')"
)
# Now SQL-federated queries over Lance from marimo notebooks:
df = con.execute(
    "SELECT filename, text FROM books WHERE subject = 'irish' LIMIT 10"
).df()
```

### Geospatial + FTS

```python
# Compute distance with the built-in geo operator
results = table.search("best fish and chips", query_type="hybrid")
    .where("distance(lat, lon, 53.2707, -9.0568) < 5")  # within 5 km of Galway
    .prefilter(False)  # post-filter (geo is non-selective)
    .limit(10)
    .to_pandas()
```

### `explain_plan` / `analyze_plan` / `drop_index`

```python
# Diagnose slow queries
plan = table.search(query_vector).limit(10).explain_plan(verbose=True)
print(plan)

# Run the query with metrics
metrics = table.search(query_vector).limit(10).analyze_plan()

# Drop an index (e.g. before a bulk insert, then re-create)
table.drop_index("vector_idx")
# … bulk insert …
table.create_index(metric="cosine", index_type="HNSW", m=20, ef_construction=150)
```

## Best Practices

1. **Use Float16 for vectors** — 50% storage savings
2. **Store metadata with vectors** — avoid joins
3. **Pre-filter when the filter is selective** (> 1% of rows);
   **post-filter** when the filter is non-selective
4. **Use `refine_factor`** for high-accuracy queries
5. **Compact regularly** — merge fragments for performance
6. **Batch inserts** — 1000-10000 rows at a time
7. **Drop indexes before bulk inserts > 50K rows** (HNSW rebuild is slow)
8. **Use the embeddings registry** — never roll your own embedder
9. **Use the multimodal "fat table"** for small BLOBs (< 1 MB);
   use the "pointer strategy" (S3 + URL) for larger
10. **Use `time-travel`** for model rollback, A/B testing, and audits
11. **FTS tokenizer matters for multilingual corpora** — use
    `default` (Unicode) for Irish, Welsh, etc.; `en_stem` for English
12. **TS: use `search()`, not the deprecated `vectorSearch()`**
13. **The KCG canonical embedding model is `BAAI/bge-m3`**
    (1024-d, multilingual, 100+ languages including all 6
    Celtic languages, MIT-licensed). Use it for any
    multilingual RAG corpus. Cache the model weights at
    `stedding/huggingface/hub/models--BAAI--bge-m3/`.
14. **Reconciled model selection** (resolves the
    `EMBEDDINGS.md` conflict): the
    `MultiModelEmbedder` in `.agents/skills/cocoindex/SKILL.md`
    routes Irish (`ga`) to `GaBERT`
    (`DCU-NLP/bert-base-irish-cased-v1`, 768-d) for
    linguistic accuracy (séimhiú, urú, dialectal variation),
    and everything else to `BGE-M3` (1024-d, multilingual).
    Both stored in the same LanceDB table with a `model_name`
    column.

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

**LanceDB Cloud (4 regions):**
```python
# .env
# LANCEDB_URI=db://my-database
# LANCEDB_API_KEY=...

db = lancedb.connect(
    "db://my-database",
    api_key=os.environ["LANCEDB_API_KEY"],
    region="us-east-1",  # us-east-1, us-west-2, eu-west-1, ap-south-1
)
```

LanceDB Cloud features:
- **Auto-compaction** — runs every 5 minutes (no manual `compact()`)
- **Auto-reindexing** — re-creates the HNSW index on every 1k writes
- **Serverless** — no instance management
- **Multi-region** — pick the region closest to your data

**For self-hosted Cloudflare R2 + Lance** (the KCG production target),
use the rclone-sidecar Compose pattern (see
`references/hosting-lancedb-docker-compose.md` or the deleted
`docs/lance/lancedb.compose.yaml` for the upstream example).

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

## 2026-06 updates (from the `upstream-package-monitoring` openspec change)

- **Lance Format v2.2** — 50%+ storage reduction vs Parquet; 68× faster
  blob reads. The KCG migration to format v2.2 is tracked by
  `openspec/changes/lancedb-format-v22-migration/`.
- **Lance Blob V2** — 4 storage modes: Inline / Packed / Dedicated /
  External. KCG recommends **Packed** for leabharlann assets (where
  blobs are <1 MB) and **Dedicated** for upstream blog payloads
  (where blobs can be >10 MB).
- **LanceDB embedder model note** — the value actually exported by
  `cocoindex/_lifespan.py:70` is
  `BAAI/bge-large-en-v1.5` (English-only, 1024-dim), NOT `BAAI/bge-m3`
  as some CocoIndex v1 App docstrings claim. Both are 1024-dim so the
  discrepancy is latent. Apps whose docstrings claim `bge-m3` will be
  corrected in a follow-up openspec change.
- **LanceDB upstream monitor** — `lancedb_blog.yml` in
  `infrastructure/firecrawl/monitors/upstream_packages/` is the
  Firecrawl monitor that detects Lance Format / Lance Blob / multimodal
  / Lance Namespace releases via the LLM-judge `--goal` filter.
  See the `cianfhoghlaim-cocoindex-v1` skill for the 14 v1 CocoIndex Apps
  that consume these updates.

## Examples

See [`./examples/`](./examples/) for upstream LanceDB reference
notebooks (8 total, ~17 MB). Highlights:

- `data_engineering_lance_Advance_RAG_LOTR_main.ipynb` — Lord of
  the Rings multi-document RAG baseline
- `data_engineering_lance_Advanced_RAG_Context_Enrichment_Window_*.ipynb`
  — context-enrichment window RAG pattern
- `data_engineering_lance_Chunking_Analysis_*.ipynb` — chunking
  strategy comparison
- `data_engineering_lance_cognee-RAG_cognee_demo.ipynb` — Cognee
  + LanceDB hybrid
- `data_engineering_lance_ColPali-vision-retriever_colpali.ipynb`
  — ColPali vision retriever on LanceDB
- `data_engineering_lance_Geospatial-Recommendation-System_*.ipynb`
  — geospatial point recommender
- `data_engineering_lance_multi-document-agentic-rag_main.ipynb`
  — multi-document agentic RAG
- `data_engineering_lance_multimodal-recipe-agent_*.ipynb` —
  multimodal (image + text) recipe agent

## British-Isles Education pipeline — Canonical KCG pattern (post-v4)

The post-v4 lc6 pipeline (`openspec/changes/lc6-biep/`) uses
LanceDB as the **vector companion** to DuckLake. Each of the
7 v1 CocoIndex Apps (6 LC subjects + `government_circulars`)
mounts a LanceDB table via the canonical `mount_table_target`
pattern (the v1 conformance R4 contract). The 24+1 BIEP tables
all live under `cianfhoghlaim.lc.<subject>.<level>_<lang>` and
`cianfhoghlaim.education.ie.gov_circulars`:

```python
import lancedb
from lancedb.pydantic import LanceModel, Vector
from lancedb.embeddings import get_registry

# Shared KCG embedder: BAAI/bge-m3 (1024-d, multilingual)
embedder = get_registry().get("sentence-transformers").create(
    name="BAAI/bge-m3",
    device="mps",  # M-series Mac native
)

class MathChunk(LanceModel):
    text: str = embedder.SourceField()
    vector: Vector(embedder.ndims()) = embedder.VectorField()
    subject: str
    level: str
    language: str
    module_id: str
    source_pdf: str

# Connect via the canonical KCG pattern (local + S3-compatible Garage)
db = lancedb.connect("s3://garage/lance")

# 1 of the 24 BIEP per-subject tables (en/higher/Mathematics)
table = db.open_table("cianfhoghlaim.lc.mathematics.higher_en")

# Hybrid vector + BM25 search with RRF reranking (the canonical KCG pattern)
results = (
    table.search(query_type="hybrid")
    .vector(embedder.embed("algebraic fractions").tolist())
    .text("algebraic fractions")
    .where("subject = 'mathematics' AND level = 'higher'")
    .rerank(method="rrf")
    .limit(10)
    .to_pandas()
)
```

**British-Isles Education pipeline use case:**

- **24+1 LanceDB companion tables** — one per
  `(subject, level, language)` partition, plus
  `cianfhoghlaim.education.ie.gov_circulars` for the `gov.ie`
  circulars. Each table holds 1024-d `BAAI/bge-m3` vectors
  over BAML-extracted chunks.
- **Bilingual RAG** — the `BAAI/bge-m3` embedder is
  multilingual, so a single query in English retrieves both
  English and Gaeilge chunks (ranked via the
  `BAML ExtractCrossLinguisticConcept` mapping).
- **`lance_scan()` from DuckDB** — the marimo notebooks
  join `lance_scan('s3://garage/lance/cianfhoghlaim.lc.<subject>.*')`
  against the DuckLake `curriculum_syllabus` tables in a single
  federated SQL query.
- **Time-travel for syllabus versions** — each BIEP table is
  versioned per academic year, so `table.checkout(version)`
  lets the notebooks compare the 2025 vs 2026 syllabus.
- **Reconciled embedder note** — the canonical BIEP embedder
  is `BAAI/bge-m3` (multilingual). The 2026-06 release-note
  claim that `_lifespan.py:70` exports `BAAI/bge-large-en-v1.5`
  is a latent discrepancy (both are 1024-d, so consumers see
  no error). The BIEP explicitly uses `bge-m3` for Gaeilge
  + English coverage; the `_lifespan.py` constant will be
  corrected to `bge-m3` in a follow-up openspec change.

Cross-references:
- [`.agents/skills/dlt/SKILL.md`](../dlt/SKILL.md) — the DLT
  sources that produce the BAML rows
- [`.agents/skills/cocoindex/SKILL.md`](../cocoindex/SKILL.md) —
  the canonical `mount_table_target` pattern (v1 conformance R4)
- [`.agents/skills/motherduck/SKILL.md`](../motherduck/SKILL.md) —
  the 4 Dives that query these tables
- [`.agents/skills/duckdb/SKILL.md`](../duckdb/SKILL.md) — the
  `lance_scan()` federated SQL layer
- [`.agents/skills/marimo/SKILL.md`](../marimo/SKILL.md) — the 6
  per-subject notebooks that join DuckLake + LanceDB
- [`.agents/skills/baml/SKILL.md`](../baml/SKILL.md) — the
  `ExtractCrossLinguisticConcept` cross-linguistic alignment
