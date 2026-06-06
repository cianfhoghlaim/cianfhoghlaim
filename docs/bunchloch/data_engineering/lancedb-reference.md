# LanceDB Reference

> Merged from 30 source files in `lance/` — research report, KCG summary, Lance+Ray distributed processing, and RAG/hybrid/multimodal/geospatial patterns.

---

## Comprehensive Research Report


> Source: `docs/data_engineering/lance/lancedb-research-report.md`

# LanceDB Comprehensive Research Report

## Executive Summary

LanceDB is an open-source, embedded, multimodal vector database designed for production-scale AI applications. Built on the Lance columnar data format and leveraging Apache Arrow and DataFusion, it provides a developer-friendly solution for vector search, full-text search, and hybrid search capabilities with support for billion-scale datasets.

---

## 1. Overview of LanceDB

### What is LanceDB?

LanceDB is a serverless, multi-modal vector database written in Rust that provides:
- **Embedded Database**: Runs in-process without requiring a separate server
- **Cloud-Native Architecture**: Fully file-based with excellent S3 compatibility
- **Multimodal Support**: Natively stores vectors, text, images, video, and audio data
- **Open Source**: Apache 2.0 licensed with active community development

### Architecture

**Core Design:**
- **Hub-and-Spoke Architecture**: Rust core with native bindings for Python, Node.js/TypeScript, and Java
- **Lance Data Format**: Modern columnar format optimized for ML/AI workloads
- **Apache Arrow Integration**: Uses Arrow 56.2.0+ for in-memory columnar data representation
- **Apache DataFusion**: Query execution engine supporting SQL across all data types

**Key Architectural Features:**
- Separation of storage from compute
- Immutable fragment-based storage
- Stateless query processes that scale horizontally
- Interoperable with Parquet, DuckDB, Polars, Pandas, and PyTorch

---

## 2. Main Use Cases

LanceDB is optimized for the following production scenarios:

1. **Retrieval-Augmented Generation (RAG)**
   - Knowledge base search for LLM applications
   - Document retrieval with semantic and keyword matching
   - Context injection for LLM prompts

2. **E-Commerce Search**
   - Product similarity search
   - Multimodal search (text, image, attributes)
   - Recommendation systems

3. **Autonomous Agents**
   - Memory systems for AI agents
   - Long-term memory storage and retrieval
   - Context-aware decision making

4. **Semantic Search Applications**
   - Content discovery platforms
   - Research and academic paper search
   - Enterprise knowledge management

5. **Computer Vision**
   - Image similarity search
   - Video content analysis
   - Facial recognition systems

---

## 3. Core API Methods and Their Purposes

### Python API

#### Database Connection
```python
import lancedb

# Connect to local database
db = lancedb.connect("data/my-database")

# Connect to cloud database
db = lancedb.connect("db://my-database", api_key="...", region="us-east-1")
```

#### Table Creation
```python
import pyarrow as pa

# Define schema with vector column
schema = pa.schema([
    pa.field("id", pa.int64()),
    pa.field("vector", pa.list_(pa.float32(), 128)),  # 128-dim vector
    pa.field("text", pa.string()),
    pa.field("metadata", pa.string())
])

# Create table with data
data = [
    {"id": 1, "vector": [0.1] * 128, "text": "example document", "metadata": "tag1"},
    {"id": 2, "vector": [0.2] * 128, "text": "another document", "metadata": "tag2"}
]
table = db.create_table("my_table", data=data, schema=schema)
```

#### Inserting Data
```python
# Add new records
new_data = [
    {"id": 3, "vector": [0.3] * 128, "text": "third document", "metadata": "tag3"}
]
table.add(new_data)

# Batch insert
table.add(large_dataframe)
```

#### Vector Search
```python
# Basic vector search
query_vector = [0.15] * 128
results = table.search(query_vector).limit(10).to_pandas()

# Vector search with metadata filtering
results = (table.search(query_vector)
          .where("metadata = 'tag1'")
          .limit(10)
          .to_pandas())

# Specify distance metric
results = (table.search(query_vector)
          .metric("cosine")  # Options: cosine, l2, dot, hamming
          .limit(10)
          .to_pandas())
```

#### Full-Text Search
```python
# Create FTS index
table.create_fts_index("text")

# Perform full-text search
results = table.search("machine learning", query_type="fts").limit(10).to_pandas()
```

#### Hybrid Search
```python
# Combine vector and full-text search
results = (table.search(query_type="hybrid")
          .vector(query_vector)
          .text("machine learning")
          .limit(10)
          .rerank(method="rrf")  # Reciprocal Rank Fusion
          .to_pandas())
```

#### Indexing
```python
# Create vector index (IVF-PQ)
table.create_index(
    metric="cosine",
    num_partitions=256,
    num_sub_vectors=16,
    index_type="IVF_PQ"
)

# Create HNSW index
table.create_index(
    metric="cosine",
    index_type="HNSW",
    m=20,
    ef_construction=150
)

# Drop index
table.drop_index()
```

#### Data Management
```python
# Update records
table.update(where="id = 1", values={"text": "updated text"})

# Delete records
table.delete("id IN (1, 2, 3)")

# Compact table (merge fragments)
table.compact()

# Get table statistics
stats = table.count_rows()
schema = table.schema
```

#### Query Optimization
```python
# Explain query plan
plan = table.search(query_vector).explain_plan()

# Analyze query execution
analysis = table.search(query_vector).analyze_plan()
```

### TypeScript/JavaScript API

#### Basic Setup
```typescript
import * as lancedb from "@lancedb/lancedb";

// Connect to database
const db = await lancedb.connect("data/my-database");

// Create table
const table = await db.createTable("my_table", [
  { id: 1, vector: [0.1, 1.0], item: "foo", price: 10.0 },
  { id: 2, vector: [3.9, 0.5], item: "bar", price: 20.0 }
]);
```

#### Vector Search
```typescript
// Basic search
const results = await table
  .vectorSearch([0.1, 0.3])
  .limit(20)
  .toArray();

// With metadata filtering
const filtered = await table
  .vectorSearch([0.1, 0.3])
  .where("price < 15")
  .limit(10)
  .toArray();
```

#### Hybrid Search
```typescript
const queryVector = [0.1, 0.3];
const results = await table
  .fullTextSearch("flower moon")
  .nearestTo(queryVector)
  .rerank(reranker)
  .limit(10)
  .toArray();
```

---

## 4. Data Model and Schema Structure

### Schema Definition

LanceDB uses **Apache Arrow schemas** to define table structures:

```python
import pyarrow as pa

schema = pa.schema([
    # Scalar types
    pa.field("id", pa.int64()),
    pa.field("title", pa.string()),
    pa.field("price", pa.float64()),
    pa.field("in_stock", pa.bool_()),

    # Vector column (FixedSizeList)
    pa.field("embedding", pa.list_(pa.float32(), 1536)),  # OpenAI ada-002

    # List types
    pa.field("tags", pa.list_(pa.string())),

    # Struct types (nested data)
    pa.field("metadata", pa.struct([
        pa.field("author", pa.string()),
        pa.field("created_at", pa.timestamp("ms"))
    ])),

    # Binary data
    pa.field("image", pa.binary())
])
```

### Vector Column Requirements

- **Type**: `FixedSizeList<Float16/Float32>` treated as vector columns
- **Dimensions**: Fixed size specified at creation
- **Supported Types**: Float16, Float32 (Float16 recommended for disk space)

### Data Types Support

- **Numeric**: int8, int16, int32, int64, uint8, uint16, uint32, uint64, float16, float32, float64
- **String**: utf8, large_utf8
- **Binary**: binary, large_binary
- **Boolean**: bool
- **Temporal**: date32, date64, timestamp, time32, time64, duration
- **Complex**: list, large_list, fixed_size_list, struct, map
- **Special**: null, decimal128, decimal256

### Multimodal Data Storage

```python
# Store images with embeddings
data = [
    {
        "id": 1,
        "image": image_bytes,
        "image_embedding": clip_embedding,
        "caption": "A sunset over mountains",
        "metadata": {"source": "unsplash", "width": 1920, "height": 1080}
    }
]
```

---

## 5. Vector Search Capabilities

### Distance Metrics

LanceDB supports multiple distance metrics for vector similarity:

1. **L2 / Euclidean** (default)
   - General-purpose similarity
   - Range: [0, ∞), smaller is more similar
   ```python
   table.search(query).metric("l2")
   ```

2. **Cosine Similarity**
   - Best for unnormalized embeddings
   - Range: [-1, 1], larger is more similar
   ```python
   table.search(query).metric("cosine")
   ```

3. **Dot Product**
   - Optimal for normalized embeddings
   - Range: [-1, 1], larger is more similar
   ```python
   table.search(query).metric("dot")
   ```

4. **Hamming Distance**
   - For binary vectors
   - Range: [0, n], smaller is more similar
   ```python
   table.search(query).metric("hamming")
   ```

### Search Methods

#### 1. Brute Force (kNN)
- No index required
- Exact results
- Suitable for small datasets (<100K vectors)

```python
# Performs brute force without index
results = table.search(query_vector).limit(10).to_pandas()
```

#### 2. Approximate Nearest Neighbor (ANN)
- Requires index creation
- Fast with slight accuracy tradeoff
- Essential for large datasets (>100K vectors)

```python
# Create index first
table.create_index(metric="cosine", num_partitions=256)

# ANN search using index
results = table.search(query_vector).limit(10).to_pandas()
```

### Advanced Vector Search Features

#### Multi-Vector Search
```python
# Search with multiple vectors per document
# Recent feature (2025) for contextualized vector lists
results = table.search([vector1, vector2, vector3]).limit(10).to_pandas()
```

#### Vector Search with Projections
```python
# Return specific columns only
results = (table.search(query_vector)
          .select(["id", "title", "score"])
          .limit(10)
          .to_pandas())
```

#### Refine Factor (Oversampling)
```python
# Request more candidates, then rerank
results = (table.search(query_vector)
          .limit(10)
          .refine_factor(5)  # Fetches 50 candidates, returns top 10
          .to_pandas())
```

---

## 6. Filtering and Querying Features

### SQL-Based Filtering

LanceDB uses **SQL expressions** for filtering:

```python
# Simple equality
results = table.search(query).where("category = 'electronics'")

# Numeric comparisons
results = table.search(query).where("price > 100 AND price < 500")

# String operations
results = table.search(query).where("title LIKE '%laptop%'")

# IN clause
results = table.search(query).where("category IN ('electronics', 'computers')")

# IS NULL
results = table.search(query).where("discount IS NOT NULL")

# Complex expressions
results = table.search(query).where(
    "(category = 'books' AND price < 30) OR (category = 'ebooks' AND price < 15)"
)
```

### Pre-Filtering vs Post-Filtering

#### Pre-Filtering (Default)
- Applied **before** vector search
- Narrows search space
- Reduces query latency
- Better for highly selective filters

```python
# Pre-filter: searches only within filtered subset
results = table.search(query).where("in_stock = true").limit(10)
```

#### Post-Filtering
- Applied **after** vector search
- Refines results
- Better when filter is not very selective
- May return fewer results than requested

```python
# Post-filter: search first, then filter
results = (table.search(query)
          .limit(100)
          .where("in_stock = true", prefilter=False)
          .limit(10))
```

### Full-Text Search

LanceDB includes native full-text search with BM25 algorithm:

```python
# Create FTS index with options
table.create_fts_index(
    "text_field",
    tokenizer="en_stem",  # English stemming
    with_stopwords=["the", "a", "an"]  # Custom stopwords
)

# Perform FTS
results = table.search("machine learning algorithms", query_type="fts").limit(10)
```

**Supported Tokenizers:**
- `en_stem`: English with stemming
- `whitespace`: Simple whitespace tokenization
- `raw`: No tokenization

### SQL Queries

Full SQL support via DataFusion:

```python
# SQL SELECT
results = db.sql("SELECT * FROM my_table WHERE price < 100").to_pandas()

# Aggregations
stats = db.sql("""
    SELECT category, AVG(price) as avg_price, COUNT(*) as count
    FROM my_table
    GROUP BY category
""").to_pandas()

# Joins (if multiple tables)
results = db.sql("""
    SELECT a.*, b.category_name
    FROM products a
    JOIN categories b ON a.category_id = b.id
""").to_pandas()
```

---

## 7. Performance Optimization Features

### Indexing Strategies

#### IVF-PQ (Inverted File with Product Quantization)

**Best For:** Large datasets with limited memory

```python
table.create_index(
    metric="cosine",
    index_type="IVF_PQ",
    num_partitions=256,      # Number of clusters (√n to n/1000)
    num_sub_vectors=16,      # PQ compression factor
    accelerator="cuda"       # Optional GPU acceleration
)
```

**Characteristics:**
- Disk-based index
- Excellent for billion-scale datasets
- Lower memory footprint
- Slightly lower recall than HNSW

**Tuning Parameters:**
- `num_partitions`: More partitions = faster search, but needs more data
- `num_sub_vectors`: Higher = better accuracy, larger index size

#### HNSW (Hierarchical Navigable Small World)

**Best For:** Maximum accuracy and speed with sufficient memory

```python
table.create_index(
    metric="cosine",
    index_type="HNSW",
    m=20,                    # Max edges per node (typical: 12-48)
    ef_construction=150,     # Build-time search depth (typical: 100-500)
    ef_search=100           # Query-time search depth
)
```

**Characteristics:**
- Graph-based algorithm
- Highest accuracy
- Fast query time
- Higher memory usage

**Hybrid Indexes:**
```python
# IVF-HNSW-PQ: Best of both worlds
table.create_index(
    index_type="IVF_HNSW_PQ",
    num_partitions=128,
    m=20,
    num_sub_vectors=16
)
```

### Automatic Optimization Features

#### Auto-Compaction (Cloud/Enterprise)
- Automatically merges small fragments
- Maintains query performance
- Reduces metadata overhead
- Runs in background

#### Auto-Reindexing (Cloud/Enterprise)
- Incremental index updates
- Maintains index freshness
- No manual intervention required
- Supports vector, scalar, and FTS indexes

### Manual Optimization

#### Compaction
```python
# Merge small fragments
table.compact()

# Compact with options
table.compact(
    target_rows_per_fragment=1000000,  # Target fragment size
    materialize_deletions=True         # Remove deleted rows
)
```

#### Column Statistics
- Automatically collected during writes
- Enable 30x faster scans with filters
- Used for query optimization
- No configuration required

### Query Optimization Tools

```python
# Explain plan (logical + physical)
plan = table.search(query).where("price > 100").explain_plan()
print(plan)

# Analyze plan (with execution stats)
analysis = table.search(query).where("price > 100").analyze_plan()
print(analysis)
```

### Performance Characteristics

- **Latency**: Sub-100ms at thousands of QPS
- **Throughput**: 5M IOPS, 10+ GB/s with NVMe cache
- **Scale**: Billion-scale vectors on single node
- **Memory**: Disk-based indexes exceed RAM capacity
- **Storage**: 3x faster scans vs Parquet for vector data

---

## 8. Deployment Options

### 1. OSS (Open Source) - Self-Hosted

**Best For:** Development, experimentation, full control

**Features:**
- Free and open source
- Local file system or S3-compatible storage
- Manual compaction and optimization
- Full feature access

**Installation:**
```bash
# Python
pip install lancedb

# TypeScript/Node.js
npm install @lancedb/lancedb

# Rust
cargo add lancedb
```

**Usage:**
```python
import lancedb
db = lancedb.connect("./data/my-db")  # Local
# or
db = lancedb.connect("s3://my-bucket/lancedb")  # S3
```

### 2. LanceDB Cloud - Serverless

**Best For:** Production apps without infrastructure management

**Features:**
- Fully managed service
- Auto-scaling storage and compute
- Auto-compaction and reindexing
- High availability
- Usage-based pricing

**Connection:**
```python
import lancedb

db = lancedb.connect(
    "db://my-database",
    api_key="ldb_...",
    region="us-east-1"
)
```

**Regions Available:**
- us-east-1 (US East)
- us-west-2 (US West)
- eu-west-1 (Europe)
- ap-south-1 (Asia Pacific)

### 3. LanceDB Enterprise

**Best For:** Mission-critical applications with enterprise requirements

**Features:**
- Horizontally scalable architecture
- Billions of rows, petabyte-scale
- Advanced security and compliance
- Dedicated support and SLAs
- BYOC (Bring Your Own Cloud) deployment
- Native Helm charts for Kubernetes
- Azure Stack Router deployment

**Advanced Features:**
- Quantized-IVF algorithm
- Multi-tenancy support
- Advanced access controls
- Audit logging
- Custom retention policies

### Storage Options

#### Local Disk
- **Latency**: Lowest (<1ms)
- **Cost**: Medium
- **Use Case**: Single-node deployment, development

#### S3-Compatible Storage
- **Latency**: Higher (10-50ms)
- **Cost**: Lowest
- **Use Case**: Cloud deployment, serverless
- **Compatible With**: AWS S3, MinIO, R2, Tigris, GCS, Azure Blob

```python
# S3
db = lancedb.connect("s3://bucket/path")

# MinIO
db = lancedb.connect("s3://bucket/path", storage_options={
    "endpoint_url": "http://localhost:9000",
    "access_key_id": "...",
    "secret_access_key": "..."
})
```

#### EFS (Elastic File System)
- **Latency**: Medium (<100ms p95)
- **Cost**: Medium
- **Use Case**: Multi-node shared storage

#### NVMe Cache
- **Latency**: Lowest
- **Throughput**: Highest (5M IOPS)
- **Cost**: Highest
- **Use Case**: Enterprise high-performance workloads

### Deployment Architecture

**Serverless Stack:**
```
Application → LanceDB Client SDK → S3 Storage
```

**Enterprise Stack:**
```
Applications → Load Balancer → LanceDB Cluster → NVMe Cache → S3 Storage
```

---

## 9. Integration Ecosystem

### LLM Frameworks
- **LangChain**: Native vector store integration
- **LlamaIndex**: First-class support
- **Haystack**: LanceDB document store

### Data Processing
- **Pandas**: Direct DataFrame support
- **Polars**: Native integration
- **DuckDB**: Query integration
- **Apache Arrow**: Native format
- **PyArrow**: Direct compatibility

### ML Frameworks
- **PyTorch**: Dataset integration
- **HuggingFace**: Transformers, Sentence Transformers
- **Instructor**: Structured output embeddings

### Embedding Providers
- **OpenAI**: GPT embeddings, text-embedding-ada-002, text-embedding-3-*
- **Cohere**: Embed models
- **HuggingFace**: All transformer models
- **Sentence Transformers**: Popular embedding models
- **ColBERT**: Contextualized late interaction
- **Google**: Gemini text embeddings
- **AWS Bedrock**: Text embeddings
- **Ollama**: Local embedding models
- **OpenCLIP**: Vision-language models

### Query Engines
- **Apache DataFusion**: Built-in SQL engine
- **Apache Spark**: Distributed processing
- **Trino**: Federated queries
- **Apache Flink/Fluss**: Stream processing

---

## 10. Code Examples

### Complete RAG Application

```python
import lancedb
from lancedb.embeddings import get_registry
from lancedb.pydantic import LanceModel, Vector

# Define schema with automatic embeddings
model = get_registry().get("openai").create(name="text-embedding-3-small")

class Document(LanceModel):
    text: str = model.SourceField()
    vector: Vector(model.ndims()) = model.VectorField()
    metadata: dict

# Connect and create table
db = lancedb.connect("~/.lancedb")
table = db.create_table("documents", schema=Document)

# Add documents (embeddings generated automatically)
documents = [
    {"text": "LanceDB is a vector database", "metadata": {"source": "docs"}},
    {"text": "Vector search enables semantic retrieval", "metadata": {"source": "blog"}},
]
table.add(documents)

# Create index for performance
table.create_fts_index("text")
table.create_index(metric="cosine")

# Hybrid search
query = "How does semantic search work?"
results = (table.search(query, query_type="hybrid")
          .limit(5)
          .to_pydantic(Document))

for doc in results:
    print(f"Score: {doc._distance:.3f}")
    print(f"Text: {doc.text}")
    print(f"Metadata: {doc.metadata}\n")
```

### Image Similarity Search

```python
import lancedb
import torch
from PIL import Image
from transformers import CLIPProcessor, CLIPModel

# Load CLIP model
model = CLIPModel.from_pretrained("openai/clip-vit-base-patch32")
processor = CLIPProcessor.from_pretrained("openai/clip-vit-base-patch32")

def get_image_embedding(image_path):
    image = Image.open(image_path)
    inputs = processor(images=image, return_tensors="pt")
    with torch.no_grad():
        embedding = model.get_image_features(**inputs)
    return embedding[0].numpy().tolist()

# Create database
db = lancedb.connect("./image_db")

# Add images
data = []
for img_path in image_paths:
    data.append({
        "image_path": img_path,
        "embedding": get_image_embedding(img_path),
        "category": extract_category(img_path)
    })

table = db.create_table("images", data)
table.create_index(metric="cosine")

# Search similar images
query_embedding = get_image_embedding("query_image.jpg")
results = table.search(query_embedding).limit(10).to_pandas()
```

### Real-Time Streaming Updates

```python
import lancedb
from datetime import datetime

db = lancedb.connect("./streaming_db")
table = db.create_table("events", [
    {"id": 1, "embedding": [0.1] * 128, "timestamp": datetime.now(), "event": "login"}
])

# Continuous ingestion
def process_stream(event_stream):
    batch = []
    for event in event_stream:
        batch.append({
            "id": event.id,
            "embedding": event.embedding,
            "timestamp": event.timestamp,
            "event": event.type
        })

        if len(batch) >= 1000:
            table.add(batch)
            batch = []

    # Add remaining
    if batch:
        table.add(batch)

# Periodic optimization
def optimize_table():
    table.compact()
    if table.count_rows() % 1000000 == 0:
        table.create_index(metric="l2", num_partitions=256)
```

---

## 11. Best Practices

### Schema Design
1. Use **Float16** for vectors to save 50% storage
2. Store metadata with vectors (avoid joins)
3. Index only columns used in filters
4. Use appropriate vector dimensions (balance accuracy vs. cost)

### Indexing Strategy
1. Start without index (<100K vectors)
2. Add IVF-PQ for large datasets
3. Use HNSW for accuracy-critical applications
4. Tune `num_partitions` based on dataset size

### Query Optimization
1. Use pre-filtering for selective filters
2. Limit result size appropriately
3. Project only needed columns
4. Use `refine_factor` for better accuracy

### Data Management
1. Compact regularly (or use auto-compaction)
2. Batch inserts (1000-10000 rows)
3. Use appropriate fragment size
4. Monitor table statistics

### Production Deployment
1. Start with LanceDB Cloud for simplicity
2. Monitor query latency and QPS
3. Set up appropriate backup strategy
4. Use enterprise for mission-critical apps
5. Test disaster recovery procedures

---

## 12. Performance Benchmarks

### Scale Characteristics
- **Dataset Size**: Tested up to 1B+ vectors
- **Latency**: <100ms at p95
- **Throughput**: 1000s of QPS per node
- **Memory Efficiency**: Disk-based indexes exceed RAM

### Comparison Advantages
1. **vs. Pinecone**: Better pricing, local deployment option
2. **vs. Weaviate**: Simpler architecture, embedded mode
3. **vs. Qdrant**: Better S3 integration, multimodal support
4. **vs. Milvus**: Easier deployment, serverless option
5. **vs. Chroma**: Better performance at scale, enterprise features

---

## 13. Recent Updates (2024-2025)

### New Features
- **Multi-Vector Search**: Documents as contextualized vector lists
- **Apache Arrow Flight-SQL**: SQL queries on billions of rows
- **Enhanced FTS**: Configurable tokenizers and stopwords
- **drop_index Method**: Remove unused indexes
- **Improved Rerankers**: ColBERT, Cross Encoder support

### Performance Improvements
- Column statistics (30x faster scans)
- Optimized IVF-PQ algorithm
- Better S3 performance
- Enhanced caching strategies

---

## 14. Resources

### Official Documentation
- Main Docs: https://lancedb.com/docs/
- API Reference: https://lancedb.com/docs/reference/
- GitHub: https://github.com/lancedb/lancedb
- Examples: https://github.com/lancedb/vectordb-recipes

### Community
- Discord: Active community support
- Blog: https://blog.lancedb.com/
- Twitter: @lancedb

### Getting Started
1. Try quick start guide
2. Explore vectordb-recipes repository
3. Join Discord for support
4. Check out blog posts for use cases

---

## 15. Conclusion

LanceDB represents a modern approach to vector databases, combining:
- **Developer Experience**: Simple APIs, embedded mode, multiple language support
- **Performance**: Billion-scale capability, sub-100ms latency, disk-based efficiency
- **Flexibility**: OSS to Enterprise, local to cloud, multimodal support
- **Ecosystem**: Rich integrations with LLM frameworks, ML tools, and data platforms

It is particularly well-suited for:
- RAG applications with LangChain/LlamaIndex
- Production-scale semantic search
- Multimodal AI applications
- Serverless architectures
- Cost-sensitive deployments

The combination of Lance format, Apache Arrow/DataFusion, and Rust implementation provides a solid foundation for next-generation AI applications requiring efficient vector search at scale.


## KCG Summary


> Source: `docs/data_engineering/lance/KCG_SUMMARY.md`

# Lance / LanceDB — KCG Summary

## What It Is
Lance is a columnar data format for modern AI/ML workloads and LanceDB is a serverless vector database built on top of it. This directory contains the Lance namespace interface, Lance + Ray distributed indexing examples, and 15+ LanceDB example applications including advanced RAG (LOTR, multi-document agentic, time-travel), multimodal search (ColPali, recipe agent), GeoSpatial recommendation, hybrid search, Multilingual RAG, and JavaScript transformer usage.

## Why This Matters for Kings' College Galway
LanceDB is the vector database for the oideachais platform — it stores curriculum embeddings and powers the `ccc` semantic search index. The hybrid search and multimodal examples directly inform how to build RAG over examination materials (text + diagrams), the time-travel RAG pattern enables querying curriculum changes across academic years, and the Lance + Ray integration provides the blueprint for distributed indexing of large curriculum datasets on the bunchloch MacBook M4.

## Key Patterns Preserved
29 .md files remain, including:
- `README.md` — Lance namespace interface overview
- `lance-ray/README.md` — Distributed indexing with Ray
- `lance-ray/docs/src/*.md` (6 files) — Ray integration docs: data evolution, distributed indexing, read/write patterns
- `lance-ray/CONTRIBUTING.md` — Development guide
- `quickstart/README.md` — LanceDB quick start
- `hybrid-search/README.md` — Combined full-text + vector search pattern
- `Advance_RAG_LOTR/README.md` — Advanced RAG with layered retrieval
- `multi-document-agentic-rag/README.md` — Agentic RAG over multiple documents
- `time-travel-rag/README.md` — Temporal RAG using LanceDB versioning
- `multimodal-search/README.md`, `multimodal-recipe-agent/README.md` — Multimodal search patterns
- `ColPali-vision-retriever/README.md` — Vision-based document retrieval
- `Geospatial-Recommendation-System/README.md` — Geospatial ML recommendations
- `Multilingual_RAG/README.md` — Multilingual retrieval patterns
- `Chunking_Analysis/Readme.md` — Chunking strategy analysis
- `cognee-RAG/README.md` — Cognee + LanceDB integration
- Research notes: `lancedb-research-report.md`, `From BI to AI_ A Modern Lakehouse Stack with Lance and Iceberg.md`, `Ibis, LanceDB, and Data Stack Integration.md`

## Source Files
Full source removed (2026-06-06). Available at:
- Lance: https://github.com/lancedb/lance
- LanceDB: https://github.com/lancedb/lancedb

## What Was Removed
Python source (.py), Jupyter notebooks, JSON/TOML configs, Docker files, shell scripts, CSV/TPCH data files, images, .gitignore/lock files


## Distributed Indexing with Lance + Ray


> Source: `docs/data_engineering/lance/lance-ray/README.md`

# Lance-Ray

[![PyPI](https://img.shields.io/pypi/v/lance-ray.svg)](https://pypi.org/project/lance-ray/)
[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](https://opensource.org/licenses/Apache-2.0)
[![Documentation](https://img.shields.io/badge/docs-latest-brightgreen.svg)](https://lance.org/integrations/ray/)

A Python library that provides seamless integration between 
[Ray](https://ray.io/) and [Lance](https://lance.org) for distributed data processing.

- [User Guide and API Documentation](https://lance.org/integrations/ray/)
- [Contributing Guide and Dev Setup](./CONTRIBUTING.md)


> Source: `docs/data_engineering/lance/lance-ray/docs/README.md`

# Lance-Ray Documentation

This directory contains the documentation for Lance-Ray, built with MkDocs.

## Building Documentation

### Prerequisites

Install uv and the documentation dependencies:

```bash
# From the project root
uv pip install -e ".[docs]"
```

### Local Development

To serve the documentation locally with hot-reload:

```bash
cd docs
uv run mkdocs serve
```

The documentation will be available at http://localhost:8000

### Building Static Files

To build the static documentation:

```bash
cd docs
uv run mkdocs build
```

The built documentation will be in the `site/` directory.

## Documentation Structure

- `mkdocs.yml` - MkDocs configuration
- `src/` - Documentation source files in Markdown
  - `index.md` - Homepage
  - `read.md` - Read operations guide
  - `write.md` - Write operations guide  
  - `examples.md` - Usage examples
  - `.pages` - Navigation configuration

## Adding New Pages

1. Create a new `.md` file in `src/`
2. Update `src/.pages` to add it to navigation
3. Follow the existing documentation style

## Deployment

Documentation is automatically deployed to GitHub Pages when changes are pushed to the main branch.

> Source: `docs/data_engineering/lance/lance-ray/docs/src/distributed-indexing.md`


# Distributed Index Building

Lance-Ray provides distributed index building functionality that leverages Ray's distributed computing capabilities to efficiently create text indices for Lance datasets. This is particularly useful for large-scale datasets as it can distribute index building work across multiple Ray worker nodes.

## New Distributed APIs

`create_scalar_index()` - Distributedly create scalar index index using ray. Currently only Inverted/FTS/BTREE are supported. Will add more index type support in the future.

### How It Works
The `create_scalar_index` function allows you to create full-text search indices for Lance datasets using the Ray distributed computing framework. This function distributes the index building process across multiple Ray worker nodes, with each node responsible for building indices for a subset of dataset fragments. These indices are then merged and committed as a single index.

**Backward Compatibility**:
   - Automatically detect availability of new APIs across different Lance versions
   - Gracefully fallback to raise tips when new APIs are unavailable


**`create_scalar_index`**

```python
def create_scalar_index(
    dataset: Union[str, "lance.LanceDataset"],
    column: str,
    index_type: Union[
        Literal["BTREE"],
        Literal["BITMAP"],
        Literal["LABEL_LIST"],
        Literal["INVERTED"],
        Literal["FTS"],
        Literal["NGRAM"],
        Literal["ZONEMAP"],
        IndexConfig,
    ],
    name: Optional[str] = None,
    *,
    replace: bool = True,
    train: bool = True,
    fragment_ids: Optional[list[int]] = None,
    index_uuid: Optional[str] = None,
    num_workers: int = 4,
    storage_options: Optional[dict[str, str]] = None,
    ray_remote_args: Optional[dict[str, Any]] = None,
    **kwargs: Any,
) -> "lance.LanceDataset":

```

### Parameters

| Parameter | Type | Description |
|-----------|------|-------------|
| `dataset` | `str` or `lance.LanceDataset` | Lance dataset or its URI |
| `column` | `str` | Column name to index |
| `index_type` | `str` or `IndexConfig` | Index type, can be `"INVERTED"`, `"FTS"`, `"BTREE"`, `"BITMAP"`, `"LABEL_LIST"`, `"NGRAM"`, `"ZONEMAP"`, or `IndexConfig` object |
| `name` | `str`, optional | Index name, auto-generated if not provided |
| `replace` | `bool`, optional | Whether to replace existing index with the same name, default is `True` |
| `train` | `bool`, optional | Whether to train the index, default is `True` |
| `fragment_ids` | `list[int]`, optional | Optional list of fragment IDs to build index on |
| `index_uuid` | `str`, optional | Optional fragment UUID for distributed indexing |
| `num_workers` | `int`, optional | Number of Ray worker nodes to use, default is 4 |
| `storage_options` | `Dict[str, str]`, optional | Storage options for the dataset |
| `ray_remote_args` | `Dict[str, Any]`, optional | Ray task options (e.g., `num_cpus`, `resources`) |
| `**kwargs` | `Any` | Additional arguments passed to `create_scalar_index` |

**Note:** For distributed indexing, currently only `"INVERTED"`,`"FTS"` and `"BTREE"` index types are supported.

### Return Value

The function returns an updated Lance dataset with the newly created index.


## Examples

### FTS Index
```python
import lance
import lance_ray as lr

# Create or load Lance dataset
dataset = lance.dataset("path/to/dataset")

# Build distributed index
updated_dataset = lr.create_scalar_index(
   dataset=dataset,
   column="text",
   index_type="INVERTED",
   num_workers=4
)

# Verify index creation
indices = updated_dataset.list_indices()
print(f"Index list: {indices}")

# Use index for search
results = updated_dataset.scanner(
   full_text_query="search term",
   columns=["id", "text"]
).to_table()
print(f"Search results: {results}")
```
### BTREE Index
```python
# Assume a LanceDataset with a numeric column "id" exists at this path
import lance_ray as lr

updated_dataset = lr.create_scalar_index(
    dataset="path/to/dataset",
    column="id",
    index_type="BTREE",
    name="btree_multiple_fragment_idx",
    replace=False,
    num_workers=4,
)

# Example queries
updated_dataset.scanner(filter="id = 100", columns=["id", "text"]).to_table()
updated_dataset.scanner(filter="id >= 200 AND id < 800", columns=["id", "text"]).to_table()
```


### Custom Index Name

```python
updated_dataset = lr.create_scalar_index(
   dataset="path/to/dataset",
   column="text",
   index_type="INVERTED",
   name="custom_text_index",
   num_workers=4
)
```

### Custom Ray Options

```python
updated_dataset = lr.create_scalar_index(
   dataset="path/to/dataset",
   column="text",
   index_type="INVERTED",
   num_workers=4,
   ray_remote_args={"num_cpus": 2, "resources": {"custom_resource": 1}}
)
```

### Index Replacement Control

```python
# Create index with custom name
updated_dataset = lr.create_scalar_index(
   dataset="path/to/dataset",
   column="text",
   index_type="INVERTED",
   name="my_text_index",
   num_workers=4
)

# Try to create another index with the same name (will replace by default)
updated_dataset = lr.create_scalar_index(
   dataset="path/to/dataset",
   column="text",
   index_type="INVERTED",
   name="my_text_index",  # Same name as before
   replace=True,          # Explicitly allow replacement (default behavior)
   num_workers=4
)

# Prevent index replacement
import lance_ray as lr

try:
    updated_dataset = lr.create_scalar_index(
       dataset="path/to/dataset",
       column="text",
       index_type="INVERTED",
       name="my_text_index",  # Same name as existing index
       replace=False,         # Prevent replacement
       num_workers=4
    )
except ValueError as e:
    print(f"Index creation failed: {e}")
    # Handle the error appropriately
```

### Performance Considerations

- For very large datasets, it's recommended to use more powerful CPU/memory ray worker nodes. Increasing `num_workers` can improve index building speed, but requires more computational nodes.
- Too many num_workers can cause large number of partitions, which cause FTS queries slowness as lots of index partitions need to be loaded when searching.
- If `num_workers` is greater than the number of fragments, it will be automatically adjusted to match the fragment count

### Important Notes

- **Index Type Support**: For distributed indexing, currently only `"INVERTED"`/`"FTS"`/`"BTREE"` index types are supported, even though the function signature accepts other index types.
- **Default Behavior**: The `replace` parameter defaults to `True`, meaning existing indices with the same name will be replaced without warning. Set `replace=False` to prevent accidental overwrites.
- **Fragment Selection**: Use `fragment_ids` parameter to build indices on specific fragments only. This is useful for incremental index building or testing.
- **Error Handling**: When `replace=False` and an index with the same name exists, a `ValueError` or `RuntimeError` will be raised depending on the execution context.


> Source: `docs/data_engineering/lance/lance-ray/docs/src/data-evolution.md`

# Data Evolution

## `add_columns`

```python
add_columns(
    uri=None, 
    *, 
    namespace=None, 
    table_id=None, 
    transform, 
    **kwargs)
```

Add columns to an existing Lance dataset using Ray's distributed processing.

**Parameters:**

- `uri`: Path to the Lance dataset (either uri OR namespace+table_id required)
- `namespace`: LanceNamespace instance for metadata catalog integration (requires table_id)
- `table_id`: Table identifier as list of strings (requires namespace)
- `transform`: Transform function to apply for adding columns
- `filter`: Optional filter expression to apply
- `read_columns`: Optional list of columns to read from original dataset
- `reader_schema`: Optional schema for the reader
- `read_version`: Optional version to read
- `ray_remote_args`: Optional kwargs for Ray remote tasks
- `storage_options`: Optional storage configuration dictionary
- `batch_size`: Batch size for processing (default: 1024)
- `concurrency`: Optional number of concurrent processes

**Returns:** None


> Source: `docs/data_engineering/lance/lance-ray/docs/src/write.md`

# Writing to Lance Dataset

## `write_lance`

```python
write_lance(
    ds, 
    uri=None, 
    *, 
    namespace=None, 
    table_id=None, 
    schema=None, 
    mode="create", 
    **kwargs)
```

Write a Ray Dataset to Lance format.

**Parameters:**

- `ds`: Ray Dataset to write
- `uri`: Path to the destination Lance dataset (either uri OR namespace+table_id required)
- `namespace`: LanceNamespace instance for metadata catalog integration (requires table_id)
- `table_id`: Table identifier as list of strings (requires namespace)
- `schema`: Optional PyArrow schema
- `mode`: Write mode - "create", "append", or "overwrite"
- `min_rows_per_file`: Minimum rows per file (default: 1024 * 1024)
- `max_rows_per_file`: Maximum rows per file (default: 64 * 1024 * 1024)
- `data_storage_version`: Optional data storage version
- `storage_options`: Optional storage configuration dictionary
- `ray_remote_args`: Optional kwargs for Ray remote tasks
- `concurrency`: Optional maximum number of concurrent Ray tasks

**Returns:** None


> Source: `docs/data_engineering/lance/lance-ray/docs/src/read.md`

# Reading Lance Datasets

## `read_lance`

```python
read_lance(
    uri=None, 
    *, 
    namespace=None, 
    table_id=None, 
    columns=None, 
    filter=None, 
    storage_options=None, 
    **kwargs)
```

Read a Lance dataset and return a Ray Dataset.

**Parameters:**

- `uri`: The URI of the Lance dataset to read from (either uri OR namespace+table_id required)
- `namespace`: LanceNamespace instance for metadata catalog integration (requires table_id)
- `table_id`: Table identifier as list of strings (requires namespace)
- `columns`: Optional list of column names to read
- `filter`: Optional filter expression to apply
- `storage_options`: Optional storage configuration dictionary
- `scanner_options`: Optional scanner configuration dictionary
- `ray_remote_args`: Optional kwargs for Ray remote tasks
- `concurrency`: Optional maximum number of concurrent Ray tasks
- `override_num_blocks`: Optional override for number of output blocks

**Returns:** Ray Dataset




> Source: `docs/data_engineering/lance/lance-ray/docs/src/examples.md`

# Examples

Here are some examples to try out.
See the `examples/` directory for more comprehensive usage examples.

## Basic Read & Write

```python
import pandas as pd
import ray
from lance_ray import read_lance, write_lance

# Initialize Ray
ray.init()

# Create sample data
sample_data = {
    "user_id": range(100),
    "name": [f"User_{i}" for i in range(100)],
    "age": [20 + (i % 50) for i in range(100)],
    "score": [50.0 + (i % 100) * 0.5 for i in range(100)],
}
df = pd.DataFrame(sample_data)

# Create Ray dataset
ds = ray.data.from_pandas(df)

# Write to Lance format
write_lance(ds, "sample_dataset.lance")

# Read Lance dataset back
ds = read_lance("sample_dataset.lance")

# Perform distributed operations
filtered_ds = ds.filter(lambda row: row["age"] > 30)
print(f"Filtered count: {filtered_ds.count()}")

# Read with column selection and filtering
ds_filtered = read_lance(
    "sample_dataset.lance",
    columns=["user_id", "name", "score"],
    filter="score > 75.0"
)
print(f"Schema: {ds_filtered.schema()}")
```

## Data Evolution

```python
# Add columns using metadata catalog
from lance_ray import add_columns
import pyarrow as pa

def add_computed_column(batch: pa.RecordBatch) -> pa.RecordBatch:
    df = batch.to_pandas()
    df['computed'] = df['value'] * 2 + df['id']
    return pa.RecordBatch.from_pandas(df[["computed"]])

add_columns(
    uri="sample_dataset.lance",
    transform=add_computed_column,
    concurrency=4
)
```

## Using Namespace

For enterprise environments with metadata catalogs, you can use Lance Namespace integration:

```python
import ray
import lance_namespace as ln
from lance_ray import read_lance, write_lance

# Initialize Ray
ray.init()

# Connect to a metadata catalog (directory-based example)
namespace = ln.connect("dir", {"root": "/path/to/tables"})

# Create a Ray dataset
data = ray.data.range(1000).map(lambda row: {"id": row["id"], "value": row["id"] * 2})

# Write to Lance format using metadata catalog
write_lance(data, namespace=namespace, table_id=["my_table"])

# Read Lance dataset back using metadata catalog
ray_dataset = read_lance(namespace=namespace, table_id=["my_table"])

# Perform distributed operations
result = ray_dataset.filter(lambda row: row["value"] > 100).count()
print(f"Filtered count: {result}")
```

The package dependency comes with the directory and REST namespace implementations to use by default.
To use another implementation, install the specific extra dependency. 
For example to use it with AWS Glue catalog:

```shell
pip install lance-namespace[glue]
```

And then you can do:

```python
import ray
import lance_namespace as ln
from lance_ray import read_lance, write_lance

# Initialize Ray
ray.init()

# Connect to AWS Glue catalog 
# using the default account and region in the current AWS environment
namespace = ln.connect("glue", {})

# Create a Ray dataset
data = ray.data.range(1000).map(lambda row: {"id": row["id"], "value": row["id"] * 2})

# Write to Lance format using metadata catalog
write_lance(
    data, 
    uri="s3://my-bucket/my-table", 
    namespace=namespace, 
    table_id=["default", "my_table"]
)

# Read Lance dataset back using metadata catalog
ray_dataset = read_lance(namespace=namespace, table_id=["default", "my_table"])

# Perform distributed operations
result = ray_dataset.filter(lambda row: row["value"] > 100).count()
print(f"Filtered count: {result}")
```

## Patterns & Recipes — RAG


> Source: `docs/data_engineering/lance/Advance_RAG_LOTR/README.md`

## Better RAG with LOTR - Lord of the Retriever

### Overview
This repository contains resources and code for enhancing Retrieval-Augmented Generation (RAG) systems using a novel approach termed LOTR (Lord of the Retriever). The primary focus is on addressing the 'Lost in the Middle' (LIM) challenge in RAG systems, particularly in the context of medical/healthcare data.

### Features
Advanced Retrieval Techniques: Utilizes multiple vector stores and the Merge Retriever approach to efficiently retrieve relevant documents.
LOTR - Merger Retriever: Combines results from various retrievers to form a comprehensive, relevant document list.
LongContextReorder (LOTR): Reorders information to ensure equal attention to all parts of the text.
Domain-Specific Embeddings: Incorporates specialized embeddings for medical and healthcare-related data.


## code 

 Colab walkthrough for LOTR   <a href="https://colab.research.google.com/github/lancedb/vectordb-recipes/blob/main/examples/Advance_RAG_LOTR/main.ipynb"><img src="https://colab.research.google.com/assets/colab-badge.svg" alt="Open In Colab"></a>

### Learn deeper in Our Blog
For a deeper dive into the cutting-edge technologies of LOTR, and to access detailed technical knowledge, check out our Medium Blog.


[Read the Blog Post](https://medium.com/etoai/better-rag-with-lotr-lord-of-retriever-23c8336b9a35)


> Source: `docs/data_engineering/lance/multi-document-agentic-rag/README.md`

# Multidocument Agentic RAG

![alt text](../../assets/multidocument-agentic-rag.png)

This example provides a comprehensive guide on creating a Multi-Document Agentic RAG leveraging the power of Embeddings and VectorDB. We'll explore how we can use Reasoning + Acting (ReAct) strategy to harness our RAG setup and make it more intelligent using different tools.

Colab walkthrough - <a href="https://colab.research.google.com/github/lancedb/vectordb-recipes/blob/main/examples/multi-document-agentic-rag/main.ipynb"><img src="https://colab.research.google.com/assets/colab-badge.svg" alt="Open In Colab"></a> 

[Read the Blog Post](https://blog.lancedb.com/multi-document-agentic-rag/)

### Python
Run the script
```python
python3 -m venv env
source env/bin/activate
pip3 install -r requirements.txt
cd examples/multi-document-agentic-rag
python3 main.py
```

## Patterns & Recipes — Hybrid & Multimodal


> Source: `docs/data_engineering/lance/hybrid-search/README.md`

# Hybrid Search Example with LanceDB

🚀 **_If you haven’t signed up for LanceDB Cloud yet, click [here](https://cloud.lancedb.com) to get started!_**

This example demonstrates how to implement hybrid search using LanceDB, combining vector search and full-text search capabilities with custom reranking.

## Features

- Leverage LanceDB's build in [embedding functions API](https://lancedb.github.io/lancedb/embeddings/) to embed data and queries 
- Full-text search using LanceDB's native FTS implementation
- Hybrid search combining both vector search and FTS


## Prerequisites

- Node.js (v16 or higher)
- npm or yarn
- LanceDB Cloud account and API credentials
- OpenAI API key

## Setup

1. Clone the repository and navigate to this directory:
```bash
cd ts_example/hybrid-search
```

2. Install dependencies:
```bash
npm install
```

3. Create a `.env` file with your LanceDB Cloud credentials and OpenAI API key:
```bash
LANCEDB_API_KEY=your_lancedb_api_key_here
LANCEDB_URI=db://your-db-uri
OPENAI_API_KEY=your_api_key_here
```

## Running the Example

```bash
npm start
```

The example demonstrates three types of searches:
1. Pure vector search
2. Pure full-text search
3. Hybrid search with default RRF reranking


## Data Schema


## Dataset

By default, the example uses the BeIR/scidocs dataset from HuggingFace, loading documents in batches of 100. You can modify the `BATCH_SIZE` and target size in the code to load more or fewer documents.

> Source: `docs/data_engineering/lance/multimodal-search/README.md`

# Multimodal Search Engine -  Next.js Template

![ezgif com-optimize (7)](https://github.com/lancedb/vectordb-recipes/assets/15766192/9805fec8-da72-44c0-be12-ddbe1c2d6afc)

## Development

First, rename `.env.example` to `.env.local`, and fill out `RF_API_KEY` with your Roboflow API key.

Run the development server:

```bash
npm run dev
# or
yarn dev
# or
pnpm dev
```

Open [http://localhost:3000](http://localhost:3000) with your browser to see the result.





> Source: `docs/data_engineering/lance/ColPali-vision-retriever/README.md`




> Source: `docs/data_engineering/lance/Multilingual_RAG/README.md`

# Multilingual-RAG

![Multilingual-RAG](https://github.com/akashAD98/Multilingual-RAG/assets/62583018/a84e1839-a311-496c-b545-3533ef348dea.png)

## Overview
Multilingual-RAG is an innovative question-answering system with multilingual capabilities, capable of understanding and generating responses in multiple languages. It is built upon the powerful architecture of Large Language Models (LLMs) with Retrieve-And-Generate (RAG) capabilities. This application harnesses the capabilities of Cohere's multilingual embeddings, LanceDB vector store, LangChain for question answering, and Argos Translate for seamless translation between languages. The user interface is provided by Gradio, ensuring a smooth and interactive user experience.

## Supported Languages
Multilingual RAG is designed to support over 100 languages. The specific list of supported languages depends on the capabilities of the Cohere multilingual model and Argos Translate. By default, it includes support for English, Hindi, French, and Turkish languages. Additional languages can be added to suit your use case.

## Getting Started
Follow these instructions to set up Multilingual-RAG in your local environment.

### Prerequisites
Ensure you have the following prerequisites installed:
- Python 3.x

Create a `.env` file and add your Cohere API key:
just rename `.env-example` with `.env` & past your API



## Installation
You can install the required dependencies using the following commands:

```
pip install -r requirements.txt
```
For Argos Translate, you can install it as follows:

```
git clone https://github.com/argosopentech/argos-translate.git
cd argos-translate
virtualenv env
source env/bin/activate
pip install -e .
```

## Running the App
To run the Multilingual-RAG app, use the following command:
Currently, support text/pdf file - change the file path inside main.py

```
python3 main.py
```


## Patterns & Recipes — Temporal & Geospatial


> Source: `docs/data_engineering/lance/time-travel-rag/README.md`

# Time-travel RAG wiht versioned data

Code for tutorial example on time-travel RAG in LanceDB using versioned data.

See the docs page that describes this [here](https://lancedb.com/docs/tutorials/rag/time-travel-rag/).

## Setup
Install the dependencies using pip or uv as follows:

```bash
pip install -r requirements.txt
# OR, If you're using uv
uv pip install -r requirements.txt
```

> Source: `docs/data_engineering/lance/Geospatial-Recommendation-System/README.md`

# Geospatial Recommendation System

In this tutorial, we'll enhance our restaurant recommendation system using Full Text Search (FTS) Indexes and Geospatial APIs.

1. Extract User Preferences: Identify key details from user input such as preferred cuisines and location.
2. Construct Query String: Synthesize these details into a structured query string for searching.
3. Perform FTS Index Search: Use the query string to find relevant restaurant recommendations.
4. Apply Geospatial Filtering: Use a Geospatial API to locate the user and refine recommendations based on proximity.

We can enhance later on by adding a filter to sort the recommendations based on distance

## Setup Instructions

1. **Install Dependencies**:
   Ensure you have Python installed. Then, install the required packages:
   ```bash
   pip install lancedb pandas sentence-transformers requests openai tantivy
   ```

2. **Prepare Data**:
   Place your restaurant data CSV file in the `data.csv` format in the project directory.

3. **Run the Notebook**:
   Open the `geospatial-recommendation.ipynb` notebook in Jupyter or Google Colab and execute the cells sequentially.

## Learn More: Blog

For a detailed explanation of how this works, check out the blog post:

[Read the Blog Post](https://blog.lancedb.com/geospatial-restaurant-recommendation-system/)

## Google Colab

<a href="https://colab.research.google.com/github/lancedb/vectordb-recipes/blob/main/examples/Geospatial-Recommendation-System/geospatial-recommendation.ipynb"><img src="https://colab.research.google.com/assets/colab-badge.svg" alt="Open In Colab"></a>


> Source: `docs/data_engineering/lance/Chunking_Analysis/Readme.md`

# **Chunking Approaches for Multilingual Text Processing**  

## **Overview**  
This notebook explores various **text chunking strategies** and analyzes their effectiveness for **different languages**. It is based on insights from [this article](https://blog.lancedb.com/chunking-analysis-which-is-the-right-chunking-approach-for-your-language/).  

## **Key Topics**  
- **Fixed-length chunking** (e.g., character-based, token-based)  
- **Semantic chunking** (based on sentence structure, meaning)  
- **Language-specific considerations** (handling non-Latin scripts, different grammar structures)  
- **Impact on retrieval performance** (how chunking affects search & embeddings)  

## **Usage**  
1. Install dependencies:  
   ```bash
   pip install lancedb transformers sentence-transformers nltk spacy
   ```
2. Run the notebook to compare **different chunking methods**.  
3. Analyze results to find the best approach for your language-specific dataset.  

## **Expected Outcome**  
- Understanding of how chunking affects **semantic search** and **retrieval quality**.  
- Guidelines on selecting **optimal chunk sizes** based on language and use case.  

# Samples - 

---
1. Semantic Chunking 
![image](https://github.com/user-attachments/assets/3e72d3fc-16d9-40b1-9427-9de32f2b2d65)


2. Clustering based Chunking
![image](https://github.com/user-attachments/assets/3a923948-7cb1-41f5-be61-ad9f0f3cf232)



## Patterns & Recipes — Integrations


> Source: `docs/data_engineering/lance/cognee-RAG/README.md`

# Cognee - Get Started

## Let's talk about the problem first

### Large Language Models (LLMs) have become powerful tools for generating text and answering questions, but they still have several limitations and challenges. Below is an overview of some of the biggest problems with the results they produce:

### 1. Hallucinations and Misinformation
- Hallucinations: LLMs sometimes produce outputs that are factually incorrect or entirely fabricated. This phenomenon is known as "hallucination." Even if an LLM seems confident, the information it provides might not be reliable.
- Misinformation: Misinformation can be subtle or glaring, ranging from minor inaccuracies to entirely fictitious events, sources, or data.

### 2. Lack of Contextual Understanding
- LLMs can recognize and replicate patterns in language but don’t have true comprehension. This can lead to responses that are coherent but miss nuanced context or deeper meaning.
- They can misinterpret multi-turn conversations, leading to confusion in maintaining context over a long dialogue.

### 3. Inconsistent Reliability
- Depending on the prompt, LLMs might produce inconsistent responses to similar questions or tasks. For example, the same query might result in conflicting answers when asked in slightly different ways.
- This inconsistency can undermine trust in the model's outputs, especially in professional or academic settings.

### 4. Inability to Access Real-Time Information
- Most LLMs are trained on data up to a specific point and cannot access or generate information on current events or emerging trends unless updated. This can make them unsuitable for inquiries requiring up-to-date information.
- Real-time browsing capabilities can help, but they are not universally available.

### 5. Lack of Personalization and Adaptability
- LLMs do not naturally adapt to individual preferences or learning styles unless explicitly programmed to do so. This limits their usefulness in providing personalized recommendations or support.

### 6. Difficulty with Highly Technical or Niche Domains
- LLMs may struggle with highly specialized or technical topics where domain-specific knowledge is required.
- They can produce technically plausible but inaccurate or incomplete information, which can be misleading in areas like law, medicine, or scientific research.

### 7. Ambiguity in Response Generation
- LLMs might not always specify their level of certainty, making it hard to gauge when they are speculating or providing less confident answers.
- They lack a mechanism to say “I don’t know,” which can lead to responses that are less useful or potentially misleading.

## The next solution was RAGs

RAGs (Retrieval Augmented Generation) are systems that connect to a vector store and search for similar data so they can enrich LLM response.
![alt text](image.png)


The problem lies in the nature of the search. If you just find some keywords, and return one or many documents from vectorstore this way, you will have an issue with the the way you would use to organise and prioritise documents.


![alt text](image-1.png)


## Semantic similarity search is not magic
The most similar result isn't the most relevant one.
If you search for documents in which the sentiment expressed is "I like apples.", one of the closest results you get are documents in which the sentiment expressed is "I don't like apples."
Wouldn't it be nice to have a semantic model LLMs could use?

## That is where Cognee comes in
Cognee assists developers in introducing greater predictability and management into their Retrieval-Augmented Generation (RAG) workflows through the use of graph architectures, vector stores, and auto-optimizing pipelines. Displaying information as a graph is the clearest way to grasp the content of your documents. Crucially, graphs allow systematic navigation and extraction of data from documents based on their hierarchy.

Cognee lets you create tasks and contextual pipelines of tasks that enable composable GraphRAG, where you have full control of all the elements of the pipeline from ingestion until graph creation.


## Core Concepts
Most of the data we provide to a system can be categorized as unstructured, semi-structured, or structured. Rows from a database would belong to structured data, jsons to semi-structured data, and logs that we input into the system could be considered unstructured. To organize and process this data, we need to ensure we have custom loaders for all data types, which can help us unify and organize it properly.

![alt text](image-2.png)


In the example above, we have a pipeline in which data has been imported from various sources, normalized, and stored in a database.

## Concept 2: Data Enrichment with LLMs
LLMs are adept at processing unstructured data. They can easily extract summaries, keywords, and other useful information from documents. We use function calling with Pydantic models to extract information from the unstructured data.

![alt text](image-3.png)


## Concept 3: Graphs
Knowledge graphs simply map out knowledge, linking specific facts and their connections. When Large Language Models (LLMs) process text, they infer these links, leading to occasional inaccuracies due to their probabilistic nature. Clearly defined relationships enhance their accuracy. This structured approach can extend beyond concepts to document layouts, pages, or other organizational schemas.

![alt text](image-4.png)

## Concept 4: Vector and Graph Retrieval
Cognee lets you use multiple vector and graph retrieval methods to find the most relevant information.

## Concept 5: Auto-Optimizing Pipelines
Integrating knowledge graphs into Retrieval-Augmented Generation (RAG) pipelines leads to an intriguing outcome: the system's adeptness at contextual understanding allows it to be evaluated in a way Machine Learning (ML) engineers are accustomed to. This involves bombarding the RAG system with hundreds of synthetic questions, enabling the knowledge graph to evolve and refine its context autonomously over time. This method paves the way for developing self-improving memory engines that can adapt to new data and user feedback.


## Below is a diagram of the cognee process for the data used in this example

![alt text](image-5.png)

> Source: `docs/data_engineering/lance/Ibis, LanceDB, and Data Stack Integration.md`

# **The Converged Lakehouse: Architecting a Multimodal Data Environment with Lance Namespace and the Composable Stack**

## **1\. Executive Introduction: The Era of the Composable AI Stack**

The contemporary data infrastructure landscape is witnessing a fundamental dissolution of the historical barriers between Online Transactional Processing (OLTP), Online Analytical Processing (OLAP), and the burgeoning domain of Artificial Intelligence (AI) data management. We are moving beyond the monolithic paradigms of the single-vendor data warehouse and the unmanaged data lake into a third era: the **Composable AI Stack**. The environment proposed in this research—integrating **Ibis**, **DuckDB**, **MotherDuck**, **PlanetScale**, **Cloudflare R2**, **Iceberg**, **DuckLake**, and **Lance Namespace**—represents the vanguard of this architectural shift. It is a system designed not merely for "data processing" in the abstract, but specifically for the high-fidelity management of multimodal assets, such as PDF documents and their semantic vector embeddings, alongside rigorous transactional state management.  
The core challenge addressed by this architecture is the "impedance mismatch" between structured business data (users, subscriptions, access logs) and unstructured AI data (vectors, binary blobs, neural indices). Historically, these lived in separate silos: Postgres for the business, S3 for the files, and a specialized vector database for the embeddings. This fragmentation introduces latency, data drift, and governance nightmares. By unifying these layers through **Cloudflare R2** (as the universal storage substrate) and bridging them with **Lance Namespace** (as the metadata unifier), this architecture proposes a "Zero-Copy," "Zero-Egress" future where compute engines are brought to the data, rather than data being shipped to the compute.  
This report serves as an exhaustive architectural blueprint and implementation guide for this specific stack. It places a heavy emphasis on the role of **Lance Namespace**, dissecting its function as the integration layer that allows "AI-native" data (Lance format) to coexist and interoperate with "Analytics-native" data (Iceberg/DuckLake) and "Transaction-native" data (Postgres). We will explore the theoretical underpinnings of storage-compute separation, the mechanics of hybrid execution, and the practical implementation details of serving PDF files at the edge using this converged infrastructure.

## ---

**2\. The Architectural Foundation: Unbundling the Database**

To understand how best to utilize Lance Namespace within this stack, one must first rigorously define the role of each component. This ecosystem relies on the principle of "best-of-breed" specialization, where distinct tools solve specific classes of data engineering problems but are loosely coupled through open standards (Arrow, Parquet, Lance, SQL).

### **2.1. The Universal Interface: Ibis as the Control Plane**

In this heterogeneous environment, the developer experience is the primary risk factor. Managing connections to PlanetScale (MySQL/Postgres protocol), MotherDuck (DuckDB protocol), and LanceDB (Native/Arrow protocol) requires a unifying linguistic layer. **Ibis** fulfills this role as the portable Python DataFrame API.  
Unlike eager-execution libraries like pandas, which pull data into memory immediately, Ibis operates on a **lazy evaluation** model. It constructs an intermediate semantic representation of the query—a logical plan—and then compiles this plan into the native dialect of the target backend.1 This capability is indispensable in a stack where data resides in different physical locations (PlanetScale in AWS/GCP, MotherDuck in the cloud, Lance in R2).  
Ibis acts as the **federation coordinator**. While Ibis typically pushes a query to a single backend, the integration with **DuckDB** allows Ibis to act as a virtualization layer. Through DuckDB's ability to attach to external databases (Postgres via postgres\_scanner, S3 via httpfs), Ibis can express complex join logic across these systems in a single, fluent Python syntax.1 For the specific requirement of handling Lance datasets, Ibis serves as the orchestration tool that defines *what* data is needed, relying on DuckDB and Lance Namespace to handle the *how* of retrieval from R2.

### **2.2. The Compute Engine: DuckDB and MotherDuck**

**DuckDB** is the "engine room" of this architecture. As an in-process SQL OLAP database, it runs directly within the application container or the data processing worker. Its vectorized execution engine is optimized for analytical queries on columnar data, making it the ideal processor for the Parquet and Lance files stored in R2.2  
**MotherDuck** extends DuckDB into a serverless cloud data warehouse. It introduces the concept of **Hybrid Execution**, where a query plan can be split: purely local operations run on the developer's machine or worker node, while heavy aggregations or joins on large datasets are shipped to the MotherDuck cloud.4

* **Role in this Stack:** MotherDuck is the primary engine for heavy analytical lifting. It is responsible for joining the high-volume clickstream/access logs (stored in DuckLake format) with the dimensional user data (from PlanetScale).  
* **DuckLake:** This is MotherDuck’s optimized table format and catalog. Unlike generic data lakes, DuckLake brings ACID compliance and "time travel" to data stored in object storage.5 It is designed to work seamlessly with the DuckDB engine, offering features like **Data Inlining**, where small inserts are stored directly in the metadata to avoid the "small file problem" common in S3-based lakes.6

### **2.3. The Operational Store: PlanetScale PostgreSQL**

PlanetScale has historically been synonymous with Vitess and MySQL. However, the introduction of **PlanetScale for Postgres** fundamentally changes the integration dynamic of this stack.7

* **Role:** It serves as the immutable "System of Record" for transactional entities: User IDs, Billing, Authentication, and the mutable metadata of the PDF uploads (e.g., "is\_public", "owner\_id").  
* **The pg\_duckdb Bridge:** This is a critical synergy. PlanetScale Postgres supports the pg\_duckdb extension, which embeds the DuckDB engine *inside* the Postgres process.4 This allows the transactional database to query external data lakes (Parquet/Lance on R2) directly. It effectively blurs the line between OLTP and OLAP, allowing a developer to write a SQL query in PlanetScale that joins a local users table with a remote vector\_search\_logs table stored in MotherDuck.

### **2.4. The Storage Layer: Cloudflare R2**

**Cloudflare R2** is the physical foundation of the "Lake." Its S3-compatible API ensures compatibility with every tool in this stack (DuckDB, LanceDB, Iceberg).

* **Economic Strategic Advantage:** The "serving of PDF files" implies a high-read-volume workload. Traditional cloud object stores (AWS S3, Google GCS) charge significant egress fees for data moving out of their network. R2’s **zero-egress** model is the economic enabler of this architecture.9 It allows the PDFs to be served directly to users or retrieved by compute nodes for vectorization without incurring bandwidth penalties.  
* **Performance:** R2’s global distribution and tiering ensure low latency for retrieving large binary blobs (PDFs), effectively acting as a storage-backed CDN.

### **2.5. The Metadata Layer: Iceberg REST and Lance Namespace**

This layer provides the "governance and discovery" capabilities. Without a shared catalog, files in R2 are just "dark data," invisible to the query engines.

* **Iceberg REST Catalog:** This is the industry standard for tracking table metadata (schemas, snapshots, partitions) in a vendor-neutral way.10 It decouples the table state from the file system.  
* **Lance Namespace:** This is the specialized integration layer for the user’s vector data. It allows Lance-formatted tables (which are optimized for AI) to be registered and managed within the standard Iceberg REST catalog, making them discoverable alongside standard analytical tables.11

## ---

**3\. Deep Dive: Lance Namespace Integration Strategy**

The user's core inquiry revolves around "how best to use Lance Namespace integrating with the rest of this stack." This section serves as the definitive guide to that integration, moving from conceptual architecture to concrete implementation patterns.

### **3.1. The Problem Space: The "Split-Brain" Lakehouse**

In a standard data architecture, one often encounters a bifurcation:

1. **The Analytics Lake:** Tables stored in Parquet/Iceberg format, managed by a Hive Metastore or Iceberg Catalog, and queried by Spark, Trino, or DuckDB.  
2. **The AI Silo:** Vector embeddings stored in a specialized Vector Database (Pinecone, Milvus) or in raw files managed by a proprietary application logic.

This separation creates a "Split-Brain" problem. The data engineering team (using Iceberg) cannot see the vector data. The AI team (using vectors) cannot easily join their results with business dimensions in the analytics lake. **Lance Namespace** is the architectural solution to this schism. It is a specification and set of adapters that allow Lance datasets to "live inside" standard metadata catalogs.

### **3.2. Architecture of Lance Namespace with Iceberg REST**

When configuring Lance Namespace to use an **Iceberg REST Catalog**, the system employs a "Companion Table" mechanism. This is a sophisticated masquerade that allows the Lance data to be managed by Iceberg without forcing the data into the less-optimal Parquet format.

#### **3.2.1. The Physical vs. Logical Layout**

* **Physical Layer (R2):** The Lance data files (.lance), indices, and fragments are written to Cloudflare R2. For example: r2://my-data-lake/vectors/contracts/.  
* **Logical Layer (Iceberg REST):** The Lance Namespace implementation registers a table in the Iceberg catalog. However, this is not a standard Iceberg table.  
  * **Dummy Schema:** The registered Iceberg table often contains a placeholder schema (e.g., a single column dummy\_lance\_placeholder string). This satisfies the Iceberg requirement that a table must have a schema.  
  * **Table Properties as Pointers:** The integration relies heavily on **Iceberg Table Properties**. It sets specific keys that identify the table's true nature:  
    * table\_type: Set to lance.10  
    * lance\_location: Points to the R2 URI of the Lance dataset.  
    * lance\_schema: May cache the JSON representation of the actual Lance schema (vectors, blobs, metadata).

#### **3.2.2. The Resolution Workflow**

When a client application interacts with this setup:

1. **Discovery:** The client (e.g., Ibis or a Python script) asks the Iceberg Catalog for the table contracts.  
2. **Interception:** The Lance Namespace client (wrapping the connection) inspects the returned metadata. It sees table\_type=lance.  
3. **Redirection:** Instead of trying to read the table as an Iceberg/Parquet table, the client "mounts" the data found at lance\_location using the native Lance reader.

This architecture ensures that **Iceberg is the Single Source of Truth** for *existence, access control, and ownership*, while **Lance is the Storage Format** for *performance and vector capabilities*.

### **3.3. Strategic Implementation for "Serving PDFs and Embeddings"**

The user's specific requirement is to store and serve PDF files and their embeddings. The optimal strategy utilizes Lance's multimodal capabilities, specifically its efficiency with **Binary Large Objects (BLOBs)**.

#### **3.3.1. The "Fat Table" Schema Strategy**

Traditional architectures utilize a "Pointer Strategy": storing the PDF in S3, getting a URL, and storing the URL \+ Embedding in the database.

* **Drawback:** This creates an "N+1" query problem during retrieval. To serve the top 5 relevant documents, the application must (1) Query the vector DB (1 request), receive 5 URLs, and then (2) Make 5 separate HTTP requests to S3 to fetch the content.

**The Lance Recommendation:** Use a "Fat Table" schema where the PDF binary blob is stored *directly* in the Lance column.  
**Proposed Ibis/Lance Schema:**

Python

import pyarrow as pa

schema \= pa.schema()

Why this works on R2 with Lance:  
Lance is a fragment-based columnar format. Unlike Parquet, which must decompress and scan entire row groups, Lance supports O(1) random access to specific row IDs.

1. **Retrieval Efficiency:** When a vector search identifies the top K matches, Lance can perform a **Projection** to retrieve *only* the pdf\_blob column for those K rows.  
2. **Ranged Reads:** The Lance reader issues HTTP Range requests to R2. It does not download the whole file; it downloads only the bytes corresponding to the specific PDFs required.  
3. **Consolidated I/O:** This effectively reduces the "N+1" problem to a single (or very few) parallelized storage requests, drastically reducing latency for the user.

#### **3.3.2. Configuring the Lance Namespace with Iceberg REST and R2**

This section details the specific configuration required to wire these components together. The user must configure the Lance client to authenticate with both the Iceberg REST service (for metadata) and Cloudflare R2 (for data).  
**Python Configuration Pattern:**

Python

import lance  
from lance.namespace import connect

\# 1\. R2 Storage Configuration (S3-Compatible)  
\# These options tell Lance how to talk to Cloudflare R2  
storage\_options \= {  
    "s3\_endpoint\_override": "https://\<ACCOUNT\_ID\>.r2.cloudflarestorage.com",  
    "region": "auto",  
    "aws\_access\_key\_id": "\<R2\_ACCESS\_KEY\_ID\>",  
    "aws\_secret\_access\_key": "\<R2\_SECRET\_ACCESS\_KEY\>",  
    "allow\_http": "true", \# Required if bridging via certain proxies, otherwise false for R2  
    "timeout": "60s"  
}

\# 2\. Iceberg REST Catalog Configuration  
\# This tells Lance where to find the metadata  
catalog\_uri \= "https://\<ICEBERG\_REST\_URL\>/v1"  
warehouse\_path \= "r2://\<BUCKET\_NAME\>/lance-warehouse"

\# 3\. Connect to the Namespace  
\# This object 'ns' becomes the handle to create/manage tables  
ns \= connect(  
    "iceberg",   
    uri=catalog\_uri,   
    warehouse=warehouse\_path,   
    storage\_options=storage\_options  
)

\# 4\. Creating the Table (DDL)  
\# This registers the table in Iceberg AND creates the physical artifacts in R2  
tbl \= ns.create\_table(  
    "pdf\_documents",  
    schema=schema,  
    mode="create"   
)

### **3.4. Bridging Lance Namespace and Ibis/DuckDB**

The final piece of the integration puzzle is making these Lance tables accessible to **Ibis**. Ibis does not currently have a native "Lance Namespace" backend. Instead, we utilize the **Ibis DuckDB Backend**.  
The Integration Pattern: "Resolve and Register"  
Since DuckDB has a native lance extension (capable of reading .lance files) but may not yet automatically traverse the Iceberg/Lance-Namespace redirection link transparently, the application layer must bridge this gap.

1. **Resolve:** The application uses the lance.namespace client (as shown above) to look up the table pdf\_documents. The client returns the physical R2 URI (r2://.../data.lance).  
2. **Register:** The application registers this URI as a **View** or **Scanner** in the DuckDB connection used by Ibis.

Python

\#... assuming 'ns' is connected as above...

\# 1\. Resolve logical name to physical dataset  
lance\_table \= ns.open\_table("pdf\_documents")  
physical\_uri \= lance\_table.uri 

\# 2\. Setup Ibis with DuckDB  
import ibis  
con \= ibis.duckdb.connect()

\# 3\. Install Lance Extension in DuckDB  
con.raw\_sql("INSTALL lance; LOAD lance;")

\# 4\. Register the dataset as a View  
\# Note: We must pass the S3/R2 credentials to DuckDB as well  
con.raw\_sql(f"""  
    CREATE SECRET r2\_secret (  
        TYPE R2,  
        KEY\_ID '{r2\_key\_id}',  
        SECRET '{r2\_secret}',  
        ACCOUNT\_ID '{r2\_account\_id}'  
    );  
""")

\# Register the view using the lance\_scan function  
con.raw\_sql(f"CREATE VIEW pdf\_docs\_view AS SELECT \* FROM lance\_scan('{physical\_uri}');")

\# 5\. Ibis Object Creation  
\# Now Ibis treats it as a native table  
docs \= con.table("pdf\_docs\_view")

\# 6\. Usage: Ibis executes SQL, DuckDB scans Lance on R2  
result \= docs.filter(docs.file\_name.like("%.pdf")).execute()

This pattern provides the best of both worlds: the governance of the Namespace/Catalog and the fluid query API of Ibis.

## ---

**4\. Workflows: The Life of a PDF**

To further elucidate the stack's operation, we will trace the lifecycle of a PDF file through ingestion, storage, and serving.

### **4.1. Ingestion Workflow (Write Path)**

The write path is designed for **Concurrency** and **Atomicity**, leveraging the Iceberg REST catalog to manage state.

1. **Upload & Trigger:** A user uploads a file to the application.  
2. **Vectorization Worker:** A background worker (using Python/Ray) picks up the file. It extracts text and generates an embedding (e.g., using OpenAI or a local BERT model).  
3. **Constructing the Record:** The worker creates an Arrow RecordBatch containing:  
   * id: Generated UUID.  
   * pdf\_blob: The raw bytes of the file.  
   * vector: The computed embedding.  
   * metadata: JSON object with user\_id, timestamp, etc.  
4. **Lance Commit:** The worker calls ns.open\_table("documents").add(batch).  
   * **Phase 1 (Write):** The Lance writer writes new data fragments (files) to R2. These are invisible to readers.  
   * **Phase 2 (Commit):** The Lance client contacts the **Iceberg REST Catalog**. It attempts to swap the metadata pointer to include the new fragments.  
   * **Concurrency:** If multiple workers invoke this simultaneously, the Iceberg Catalog (backed by a database like Postgres) serializes the commits. One will succeed; the other will retry. This guarantees ACID compliance on object storage.12

### **4.2. Serving Workflow (Read Path)**

The read path optimizes for **Low Latency** using R2 and Lance’s random access capabilities.

1. **Request:** User asks "Show me contracts related to NDA."  
2. **Vector Search:** The application generates a query vector for "contracts related to NDA."  
3. **LanceDB Query:**  
   * The application connects to the Lance dataset.  
   * It executes a vector search: .search(query\_vector).limit(5).  
   * **Index Usage:** It utilizes the IVF-PQ index (stored in R2, cached locally on the compute node) to find the nearest neighbors.  
4. **Blob Retrieval:**  
   * The search returns 5 Row IDs.  
   * The query includes a request for the pdf\_blob column.  
   * **Ranged Read:** The Lance reader calculates the exact byte offsets of the blobs in the R2 files. It sends 5 parallel HTTP GET Range requests to R2.  
5. **Response:** The application receives the PDF bytes and streams them to the user.

## ---

**5\. Comparative Analysis: DuckLake vs. Iceberg REST**

The user's stack includes both **DuckLake** and **Iceberg REST**. A critical architectural decision is determining *when* to use which, as having two catalogs can lead to fragmentation.

| Feature | DuckLake | Iceberg REST (with Lance Namespace) | Recommendation for this Stack |
| :---- | :---- | :---- | :---- |
| **Primary Engine** | MotherDuck / DuckDB | Spark / Trino / LanceDB |  |
| **Metadata Storage** | SQL Database (MotherDuck managed) | JSON/Avro Files (standard spec) |  |
| **Write Latency** | **Low** (Data Inlining for small inserts) | **Higher** (File rotation required) | Use **DuckLake** for high-velocity logs (e.g., clickstream, access logs). |
| **Vector Support** | Limited (via Extensions) | **First-Class** (via Lance Namespace) | Use **Iceberg/Lance** for AI data (PDFs, Embeddings). |
| **Interoperability** | DuckDB Ecosystem primarily | Universal (Standard open format) | Use **Iceberg** for data shared with external teams/tools. |

Synthesis Strategy:  
The report recommends a Hybrid Catalog Strategy:

* **Operational Analytics:** Use **DuckLake** for tables that are primarily generated and queried by MotherDuck (e.g., aggregated usage metrics, session logs). DuckLake's "Data Inlining" feature 6 is superior for streaming small updates.  
* **AI Assets:** Use **Iceberg REST** hosting the **Lance Namespace** for the documents and embeddings tables. This adheres to the open standard for the AI assets, ensuring they are future-proof and accessible to other tools (like Spark for bulk training).  
* **Unified View:** Use Ibis \+ DuckDB to create a "Virtual Data Warehouse" that joins tables from both catalogs seamlessly.

## ---

**6\. Integrating PlanetScale and MotherDuck**

The relationship between PlanetScale (OLTP) and MotherDuck (OLAP) is the bridge between the application state and the data intelligence.

### **6.1. The pg\_duckdb Extension**

The inclusion of pg\_duckdb in the stack is pivotal. It allows the PlanetScale Postgres database to become an analytical query initiator.

* **Mechanism:** pg\_duckdb embeds a DuckDB instance inside the Postgres worker process.  
* **Capability:** It can read from MotherDuck.  
* **Workflow:**  
  1. Application writes a user subscription update to PlanetScale users table.  
  2. Analyst wants to see "Average PDF downloads per Premium User."  
  3. **Query:**  
     SQL  
     \-- Executed in PlanetScale  
     SELECT u.subscription\_tier, AVG(d.download\_count)  
     FROM public.users u  
     JOIN motherduck.analytics.daily\_downloads d ON u.id \= d.user\_id  
     GROUP BY u.subscription\_tier;

  4. **Execution:** Postgres handles the users scan. pg\_duckdb pushes the daily\_downloads aggregation to MotherDuck's cloud. The reduced result is returned to Postgres for the final join.  
  * **Performance:** Benchmarks indicate that offloading the analytical portion to MotherDuck via this extension can be **99% faster** than running the analysis in native Postgres, while avoiding resource contention on the transactional primary.4

## ---

**7\. Operationalizing the Stack on R2**

### **7.1. R2 Data Catalog vs. Self-Hosted Iceberg**

Cloudflare has recently introduced the **R2 Data Catalog** (in beta), which essentially provides a managed Iceberg REST endpoint for buckets.9

* **Recommendation:** For this stack, the user should prioritize using the **R2 Data Catalog** if available, as it removes the need to self-host an Iceberg REST service (e.g., Tabular or a Docker container).  
* **Configuration:** The Lance Namespace connection string would simply point to the R2 Data Catalog endpoint provided by Cloudflare, simplifying the infrastructure complexity significantly.

### **7.2. Caching Strategy**

Serving PDFs via Lance on R2 relies on network I/O.

* **Tiered Cache:** Enable **Smart Tiered Cache** on the R2 bucket. This helps adjacent requests for the same PDF fragments hit Cloudflare’s regional caches rather than the R2 origin, reducing latency.13  
* **Local NVMe:** For the compute nodes running LanceDB/DuckDB, ensure they have fast local NVMe storage. Lance leverages local disk to cache the **Vector Index**. A "cold" search (fetching index from R2) can take hundreds of milliseconds; a "warm" search (index on local NVMe) takes milliseconds.14

## ---

**8\. Conclusion and Future Outlook**

The proposed architecture represents a sophisticated, future-proof approach to the **AI Data Lakehouse**. By leveraging **Ibis** as the orchestrator, it achieves code portability. By utilizing **PlanetScale** and **MotherDuck**, it optimally segments transactional and analytical workloads while maintaining query interoperability.  
Most importantly, the strategic deployment of **Lance Namespace** transforms the handling of unstructured data. It elevates PDF documents and embeddings from "files in a bucket" to structured, governed, and queryable assets within the **Iceberg** catalog ecosystem. This allows for a system where a user's subscription status, their download history, and the semantic content of their documents can be queried and joined in a single, high-performance request—a capability that defines the next generation of intelligent applications.  
The successful implementation of this stack relies not on monolithic tooling, but on the disciplined integration of these composable parts, glued together by the open standards of Arrow, Lance, and the Iceberg REST protocol.

#### **Works cited**

1. Integration with Ibis \- DuckDB, accessed December 24, 2025, [https://duckdb.org/docs/stable/guides/python/ibis](https://duckdb.org/docs/stable/guides/python/ibis)  
2. DuckDB \- LanceDB, accessed December 24, 2025, [https://lancedb.com/docs/integrations/platforms/duckdb/](https://lancedb.com/docs/integrations/platforms/duckdb/)  
3. Reading and Writing Parquet Files \- DuckDB, accessed December 24, 2025, [https://duckdb.org/docs/stable/data/parquet/overview](https://duckdb.org/docs/stable/data/parquet/overview)  
4. MotherDuck Integrates with PlanetScale Postgres, accessed December 24, 2025, [https://motherduck.com/blog/motherduck-planetscale-integration/](https://motherduck.com/blog/motherduck-planetscale-integration/)  
5. accessed December 24, 2025, [https://motherduck.com/docs/integrations/file-formats/ducklake/\#:\~:text=1%20through%201.4.,files%20and%20a%20SQL%20database.](https://motherduck.com/docs/integrations/file-formats/ducklake/#:~:text=1%20through%201.4.,files%20and%20a%20SQL%20database.)  
6. DuckLake | MotherDuck Docs, accessed December 24, 2025, [https://motherduck.com/docs/integrations/file-formats/ducklake/](https://motherduck.com/docs/integrations/file-formats/ducklake/)  
7. PlanetScale Postgres, accessed December 24, 2025, [https://planetscale.com/docs/postgres](https://planetscale.com/docs/postgres)  
8. Using MotherDuck with PlanetScale, accessed December 24, 2025, [https://planetscale.com/blog/using-motherduck-with-planetscale](https://planetscale.com/blog/using-motherduck-with-planetscale)  
9. R2 Data Catalog: Managed Apache Iceberg tables with zero egress fees, accessed December 24, 2025, [https://blog.cloudflare.com/r2-data-catalog-public-beta/](https://blog.cloudflare.com/r2-data-catalog-public-beta/)  
10. Apache Iceberg REST Catalog \- Lance, accessed December 24, 2025, [https://lance.org/format/namespace/integrations/iceberg/](https://lance.org/format/namespace/integrations/iceberg/)  
11. lance-format/lance-namespace: Lance Namespace is an ... \- GitHub, accessed December 24, 2025, [https://github.com/lance-format/lance-namespace](https://github.com/lance-format/lance-namespace)  
12. Writing to LanceDB in cloud object storage while other processes are reading? \#1888, accessed December 24, 2025, [https://github.com/lancedb/lancedb/discussions/1888](https://github.com/lancedb/lancedb/discussions/1888)  
13. Public buckets · Cloudflare R2 docs, accessed December 24, 2025, [https://developers.cloudflare.com/r2/buckets/public-buckets/](https://developers.cloudflare.com/r2/buckets/public-buckets/)  
14. Storage Architecture in LanceDB, accessed December 24, 2025, [https://lancedb.com/docs/storage/](https://lancedb.com/docs/storage/)

> Source: `docs/data_engineering/lance/From BI to AI_ A Modern Lakehouse Stack with Lance and Iceberg.md`

---
title: "From BI to AI: A Modern Lakehouse Stack with Lance and Iceberg"
source: "https://lancedb.com/blog/from-bi-to-ai-lance-and-iceberg/"
author:
  - "[[[Jack Ye Prashanth Rao]]]"
published: 2025-11-24
created: 2025-12-26
description: "A comparison of where Iceberg and Lance sit in the modern lakehouse stack. We highlight emerging architectures that are bridging the worlds of analytics and …"
tags:
  - "clippings"
---
The modern, composable data stack has evolved around the idea of the *lakehouse* — a unified system that blends the flexibility of data lakes (i.e., object stores designed to hold data in open file formats) with the analytical performance and reliability of data warehouses. Projects like [Apache Iceberg](https://iceberg.apache.org/) have been pivotal in making this vision a reality, offering transactional guarantees and schema evolution at scale.

But as AI and machine learning workloads bring with them ever larger amounts of data from multiple modalities (e.g., text, images, audio, video, sensor data), newer formats like [Lance](https://lance.org/) are emerging to take the next leap forward. Lance is a high-performance columnar format that’s purpose-built for AI/ML workloads (training, feature engineering) and multimodal data at petabyte scale.

The goal of this post is to explain where Iceberg and Lance fit in the modern lakehouse stack, while discussing some of their key differences. We’ll highlight emerging data architectures that are bridging the worlds of analytics and AI/ML workloads using these two formats, all built on the same data foundation.

## Understanding the modern lakehouse stack

The modern lakehouse architecture consists of six distinct technological layers, each serving a specific purpose. Let’s dissect these layers (from the bottom up) to understand where Lance and Iceberg fit in, and how they can work together.

![](https://lancedb.com/assets/blog/from-bi-to-ai-lance-and-iceberg/lakehouse_stack.png)

### Object store

At the foundation of the lakehouse lies the **object store** — these are storage systems characterized by their simple, object-based hierarchy, typically providing high durability guarantees with HTTP-based communication for data transfer.

### File format

The **file format** describes how a single file should be stored on disk. This is where formats like Lance, Parquet, ORC, and Avro are present. The file format defines the internal structure, encoding, and compression of individual data files.

### Table format

The **table format** describes how multiple files work together to form a logical table. Table formats must include features like transactional commits and read isolation, so that multiple writers and readers can safely operate against the same table.

### Catalog spec

The **catalog spec** defines how any system can discover and manage a collection of tables within storage. It acts as the bridge between the storage layer and the compute layer of the stack (starting with the catalog *service*, more on this below).

### Catalog service

A **catalog service** offers easy connectivity to the compute engines on top, and implements one or more catalog specs to provide both table metadata and, optionally, continuous background maintenance (compaction, optimization, index updates) that table formats require to stay performant.

### Compute engine

The **compute engine** is the workhorse built on top of catalog services that leverage their awareness of catalog specs, table formats and file formats to perform complex data workflows. Compute engines are carefully designed to handle a variety of workloads, including SQL queries, analytics processing, vector search, full-text search, machine learning training.

## Differences between Lance and Iceberg

The key insight from the lakehouse architecture described above is that the file format, table format, and catalog spec layers are just **storage** specifications. **Compute power** resides only in the object store, catalog services, and compute engine layers. This clear separation of concerns is what allows lakehouse storage to be flexible, portable, and independently scalable, while opening up the same underlying data for discovery by any catalog service, and for processing by any compatible compute engine.

Iceberg operates at **two of the layers** in the stack: the table format and the catalog spec. It typically uses Parquet as the underlying file format.

Lance spans **three layers of the stack**, because it’s simultaneously a file format, table format *and* a catalog spec.

![](https://lancedb.com/assets/blog/from-bi-to-ai-lance-and-iceberg/lance_and_iceberg.png)

In the sections below, we’ll compare and contrast Lance and Iceberg at each of these layers.

### Table format

Iceberg employs a **three-level** metadata hierarchy in its table format: a table metadata file → manifest list → manifest files. The table metadata (a JSON file) rolls up a comprehensive history of past commits and schemas, and stores the partition specs, snapshot references and table properties. Each snapshot points to a manifest list (Avro) that contains metadata about manifest files and partition statistics (also Avro), and the manifests contain lists of data files that sit in the object store. Note that the Iceberg table format itself does not define how to atomically commit data — instead, it just describes the latest table metadata location, and it’s left to the catalog service to determine how to actually do the commit.

Lance employs a **single-level** metadata hierarchy, with one manifest file per table version. Lance tables use the notion of *fragments*, rather than partitions. Each commit to a Lance table produces a new manifest file that contains fragments (each with their own data and deletion files) and pointers to the index files (for FTS, vector and other scalar indexes).

![](https://lancedb.com/assets/blog/from-bi-to-ai-lance-and-iceberg/table_format.png)

### File format

Iceberg supports multiple file formats under the hood. Parquet is the most prevalent and widely used, but Avro and ORC formats are also supported.

From a file format perspective, Lance does away with row groups (unlike Parquet, which heavily relies on them), achieving a high degree of parallelism, achieving 100x the random access performance of Parquet without sacrificing scan performance. There are several other differences between Lance and Parquet that won’t be discussed here, but you can read more about it in this VLDB 2025 paper: [Efficient Random Access in Columnar Storage through Adaptive Structural Encodings](https://arxiv.org/html/2504.15247v1).

### Catalog spec

Because of the way Iceberg delegates the actual atomic write guarantees to arbitrary catalog services, over the years there have been many protocols developed by the vendors building these catalog services. Iceberg’s “REST Catalog spec” was developed as a wrapper to standardize these different protocols, and any catalog service adopting the spec is required to guarantee the atomicity of the API operation.

Lance uses “namespaces”, rather than explicitly defining a catalog spec. In fact, Lance intentionally names it “Lance Namespace” rather than “Lance Catalog”, because it’s a thin wrapper to allow storing and managing a Lance table via any catalog service, and is not aimed to be a complete catalog spec. In the future, to provide a full catalog spec experience, Lance aims to use Arrow Flight gRPC as its main standard, to be compatible with Lance’s vision of being an “Arrow-native lakehouse format”.

## When Lance is beneficial

In this section, we’ll list the key benefits of using Lance over Iceberg, especially for AI/ML workloads.

Earlier generations of open table formats (Iceberg, Delta Lake and Hudi) were primarily designed as replacements for Hive. They focus mainly on data warehouse (OLAP) workloads, with tables that are typically “long but narrow”.

Lance, on the other hand, is designed from the ground up to support machine learning and AI workloads, with fundamentally different access patterns and support for tables that are “ [long and wide](https://lancedb.com/blog/lance-v2/#very-wide-schemas) ” (e.g., embeddings, blobs and deeply nested data in columns). Lance can index [billions of vectors in hours](https://lancedb.com/blog/case-study-netflix/), storing tens of petabytes of data. For vector search, it can support more than 10,000 QPS with [<50 ms latency](https://lancedb.com/docs/enterprise/benchmark/) over object storage. For ML training, Lance integrates with PyTorch and JAX data loaders, achieving (through a distributed cache fleet) more than 5 million IOPS from NVMe SSDs.

Combining fast random access with native indexes within the same format is what gives Lance a significant advantage in ML and AI use cases, compared to scan-based approaches that are common in traditional lakehouses relying on Iceberg.

### Multimodal data done right

Multimodal data (images, videos, audio, deeply nested point clouds and their associated embeddings) is becoming more and more common, especially in the age of AI, where it’s never been easier to generate and consume huge amounts of data.

In many Iceberg deployments today, multimodal data is modeled as columns in tables (like any other tabular data), with pointers to the actual data located in object storage. This isn’t ideal from a data governance perspective, because organizations would need separate access control layers and extra operational plumbing across various systems. It’s also not ideal from a performance perspective, because there is additional I/O and network overhead while fetching individual data items.

Lance’s file format makes it more convenient to maintain multimodal data natively as blobs inside the columns, with no external lookups (the multimodal data is co-located with metadata and embeddings), thus simplifying governance and management of data that’s multimodal in nature. It’s also significantly more performant, because at the table level, Lance can pack multiple smaller rows together while storing very large rows (e.g., image or audio blobs) in a dedicated file thanks to its fragment-based design, thus balancing performance with storage size.

![](https://lancedb.com/assets/blog/from-bi-to-ai-lance-and-iceberg/multimodal_lakehouse.png)

### Flexible, zero-cost data evolution

A common need as the dataset scales in size is **data evolution,** i.e., changes to the table schema and adding, updating or removing columns and their associated data. These types of operations are especially common in ML/AI applications, where multiple developers working in parallel frequently add features, predictions or embeddings as new columns to an existing table. In Iceberg, data evolution comes with a non-trivial cost — adding data to a new column requires a **full table rewrite** since Parquet stores entire row groups together. This means that for very large tables, it’s common to see multiple new feature columns being added in parallel by multiple teams in an organization – which would require a table lock as new columns are being added, bottlenecking the feature engineering process.

In Lance, adding a new column **is essentially a zero-copy operation**. Lance’s fragment design allows independent column files per fragment (though multiple columns can share a data file), meaning that adding or updating a column simply appends new column files without touching existing data. This avoids duplication on petabytes of data, as noted by [Netflix](https://lancedb.com/blog/case-study-netflix) as they built out their media data lake incorporating LanceDB.

![](https://lancedb.com/assets/blog/from-bi-to-ai-lance-and-iceberg/data_evolution.png)

The space savings can be tremendous – say you have an existing table that’s 100 GB in size. If you update the table schema and add a new column that’s only 1% this size (1 GB) – in Iceberg, performing a backfill operation on the new column would require a **full table copy** amounting to 101 GB of writes. In LanceDB, it would just be 1 GB of writes. The larger the dataset, the more this matters. The ability to continuously or incrementally add features, without duplicating or rewriting unaffected data, makes Lance a compelling choice for teams working with petabytes of data.

## When Iceberg is beneficial

Iceberg’s partition-based, catalog-centric approach can still be beneficial for traditional BI or analytics workloads, for the reasons listed below. In this section, we’ll highlight some of them, as well as how Lance aims to address them in future versions.

### Optimized for analytical workloads

Iceberg’s hidden partitioning logic and its three-level metadata hierarchy enable efficient partition pruning for compute engines that are optimized for analytics workloads, where queries are naturally filtered on partition keys. Lance, in contrast, uses fragments (rather than partitions) as the organizational unit for data, so at present, the way Lance organizes data doesn’t fit well with traditional OLAP-style compute engines that are heavily optimized for partition-based scans.

Newer methods like [liquid clustering](https://docs.databricks.com/aws/en/delta/clustering) (developed by Databricks) can, in the future, actively leverage Lance’s features, because they avoid hard-coded table layouts and adopt an adaptive clustering approach that’s optimized based on actual query patterns. However, partitioning is a concept that’s deeply baked into current-generation query engines, so until liquid clustering gains wider adoption in the ecosystem, Iceberg has several advantages for analytics workloads.

### Mature ecosystem integration

Iceberg has years of battle-hardening from production usage and is well-integrated with a mature ecosystem, including integrations with several compute engines and catalog services. In contrast, Lance’s compute engine integrations are still emerging (primarily Spark and Ray at present), with many more upcoming and in their nascent stages. There is strong community interest in adding Lance support to popular compute engines that are part of the Iceberg ecosystem, including Flink, StarRocks, and Trino. Expect this space to evolve over time.

### Centralized observability

Iceberg’s catalog-dependent design means the catalog is aware of *all* table operations, enabling centralized monitoring and powerful automated optimization triggers. It also enable an easy-to-maintain unified audit log across all tables, with coordinated data lineage tracking.

Lance tables, like Delta Lake, can be **modified directly in storage** without catalog awareness. This storage-first design gives Lance a portability advantage but complicates activity tracking — downstream operations must rely on pull-based polling or storage event notifications (S3 Events, GCS Pub/Sub) rather than semantic catalog events. Lance’s approach to address this is through its managed offering, LanceDB Enterprise (which has knowledge of all read/write traffic), but in the future, there could be ways to onboard all operations onto open observability frameworks like OpenTelemetry for easy tracking in any tool that supports it.

## Takeaways from the comparison

The following table summarizes the reasons Lance is emerging as a **new standard for multimodal data and AI** workloads in the lakehouse.

| Feature | Lance | Iceberg |
| --- | --- | --- |
| **Metadata Structure** | Single-level manifest per version | Three-level hierarchy (metadata → manifest list → manifest) |
| **Metadata Growth** | Independent versions, no rollup | Metadata files accumulate snapshot history |
| **Data Organization** | Fragments (horizontal slices), global clustering/sorting | Partition specs with hidden partitioning, clustering/sorting within partition |
| **Row Address** | 64-bit addresses (fragment\_id + offset) | file path + position tuple |
| **File Format** | Lance file format | Parquet/ORC/Avro |
| **Index Support** | Vector and full-text index, plus a standardized framework for new scalar index specifications | Puffin for simple NDV sketch, deletion vector |

Parquet and Iceberg, developed independently (in their own time frames), have led to an explosion of connectors, integrations and innovations up and down the layers of the lakehouse stack. However, a lot of these predate the age of AI, where the kinds of workloads and user requirements involved are changing at a blazing pace.

Lance is relatively new, and so it has had the opportunity to build and iterate rapidly from the ground up while learning from the successes and existing pain points of Iceberg/Parquet. The design features of Lance, as can be seen in the table above, incorporate several proven patterns while introducing new paradigms that aim to address the unique requirements of AI/ML workloads. Lance users can seamlessly interoperate across the various ML and data processing frameworks, from Pandas and Polars, to PyTorch and beyond.

## A unified data platform with Lance and Iceberg

Looking at the trade-offs involved when choosing between Lance and Iceberg, especially for analytics vs. ML/AI workloads, we’re seeing a dual-format strategy in which large organizations are beginning to adopt Lance. Companies like Netflix are now [adopting LanceDB](https://lancedb.com/blog/case-study-netflix/) for their AI and multimodal workloads alongside Iceberg, which has long been their primary table format for BI and analytics workloads.

The figure below envisions how a unified lakehouse platform built on top of Lance and Iceberg might look, as more organizations build out their lakehouses on top of modern infrastructure. The unification occurs at the compute layers both above (catalog services and compute engines) and below (i.e., the object stores) the storage formats.

![](https://lancedb.com/assets/blog/from-bi-to-ai-lance-and-iceberg/unified_lakehouse_platform.png)

Existing catalog specifications and metadata services like Glue, Hive metadata store (HMS), Unity REST catalog and Polaris are already integrated with Lance via [lance-namespace](https://lance.org/format/namespace/impls/), an open specification built on top of Lance that standardizes access to a collection of Lance tables. On the compute engine side, there are numerous integrations in the [Lance format](https://github.com/lance-format) ecosystem (such as `lance-ray`, `lance-spark`, etc.) that are gaining adoption in open source. The main takeaway from this section is that developers who do not want the burden of maintaining multiple catalog services can choose to build on top of Lance and leveraging its integration to the compute ecosystem, while developers who are already using Iceberg can interplay with Lance for use cases that benefit from the Lance format.

These emerging architectural patterns and open source projects reflect a broader trend: managing the separate needs of analytics and AI workloads with two distinct but interoperable formats — Iceberg for BI, and Lance for AI and multimodal data, bridging the best of both worlds.

## JavaScript/TypeScript SDK


> Source: `docs/data_engineering/lance/js-transformers/README.md`

# Vector embedding search using TransformersJS
![image](https://github.com/lancedb/vectordb-recipes/assets/43097991/41c1dea3-ad28-42c1-969f-a81146f202e9)

### Setup
Install node dependencies
```javascript
npm install
```

### Javascript
Run the script
```javascript
node index.js
```


> Source: `docs/data_engineering/lance/js-transformers/walkthrough.md`

# Vector embedding search using TransformersJS

## Embed and query data from LacneDB using TransformersJS

This example shows how to use the [transformers.js](https://github.com/xenova/transformers.js) library to perform vector embedding search using LanceDB's Javascript API.


### Setting up
First, install the dependencies:
```bash
npm install @lancedb/lancedb
npm i @xenova/transformers
```

We will also be using the [all-MiniLM-L6-v2](https://huggingface.co/Xenova/all-MiniLM-L6-v2) model to make it compatible with Transformers.js

Within our `index.js` file we will import the necessary libraries and define our model and database:

```javascript
import * as lancedb from "@lancedb/lancedb"

const { pipeline } = await import('@xenova/transformers')
const pipe = await pipeline('feature-extraction', 'Xenova/all-MiniLM-L6-v2');
```

### Creating the embedding function

Next, we will create a function that will take in a string and return the vector embedding of that string. We will use the `pipe` function we defined earlier to get the vector embedding of the string.

```javascript
// Define the function. `sourceColumn` is required for LanceDB to know
// which column to use as input.
const embed_fun = {}
embed_fun.sourceColumn = 'text'
embed_fun.embed = async function (batch) {
    let result = []
    // Given a batch of strings, we will use the `pipe` function to get
    // the vector embedding of each string.
    for (let text of batch) {
        // 'mean' pooling and normalizing allows the embeddings to share the
        // same length.
        const res = await pipe(text, { pooling: 'mean', normalize: true })
        result.push(Array.from(res['data']))
    }
    return (result)
}
```

### Creating the database

Now, we will create the LanceDB database and add the embedding function we defined earlier.

```javascript
// Link a folder and create a table with data
const db = await lancedb.connect('data/sample-lancedb')

// You can also import any other data, but make sure that you have a column
// for the embedding function to use.
const data = [
    { id: 1, text: 'Cherry', type: 'fruit' },
    { id: 2, text: 'Carrot', type: 'vegetable' },
    { id: 3, text: 'Potato', type: 'vegetable' },
    { id: 4, text: 'Apple', type: 'fruit' },
    { id: 5, text: 'Banana', type: 'fruit' }
]

// Create the table with the embedding function
const table = await db.createTable('food_table', data, embed_fun)
```

### Performing the search

Now, we can perform the search using the `search` function. LanceDB automatically uses the embedding function we defined earlier to get the vector embedding of the query string.

```javascript
// Query the table
const results = await table
    .search("a sweet fruit to eat")
    .distanceType("cosine")
    .limit(2)
    .toArray()
console.log(results.map(r => r.text))
```
```bash
[ 'Banana', 'Cherry' ]
```

Output of `results`:
```bash
[
  {
    vector: Float32Array(384) [
      -0.057455405592918396,
      0.03617725893855095,
      -0.0367760956287384,
      ... 381 more items
    ],
    id: 5,
    text: 'Banana',
    type: 'fruit',
    score: 0.4919965863227844
  },
  {
    vector: Float32Array(384) [
      0.0009714411571621895,
      0.008223623037338257,
      0.009571489877998829,
      ... 381 more items
    ],
    id: 1,
    text: 'Cherry',
    type: 'fruit',
    score: 0.5540297031402588
  }
]
```

### Wrapping it up

In this example, we showed how to use the `transformers.js` library to perform vector embedding search using LanceDB's Javascript API. You can find the full code for this example on [Github](https://github.com/lancedb/lancedb/blob/main/node/examples/js-transformers/index.js)!


> Source: `docs/data_engineering/lance/js-transformers/lancedb_cloud/README.md`

# Vector embedding search using TransformersJS
![image](https://github.com/lancedb/vectordb-recipes/assets/43097991/41c1dea3-ad28-42c1-969f-a81146f202e9)


### Set credentials
if you would like to set api key through an environment variable:
```
export LANCEDB_API_KEY="sk_..."
```

replace the following lines in index.js with your project slug and api key"
```
db_url: "db://your-project-slug-name"
api_key: "sk_..."
region: "us-east-1"
```

### Setup
Install node dependencies
```javascript
npm install
```

### Javascript
Run the script
```javascript
node index.js
```

## Original Sources

- `docs/data_engineering/lance/Advance_RAG_LOTR/README.md`
- `docs/data_engineering/lance/Chatbot_with_Parler_TTS/README.md`
- `docs/data_engineering/lance/Chunking_Analysis/Readme.md`
- `docs/data_engineering/lance/cognee-RAG/README.md`
- `docs/data_engineering/lance/ColPali-vision-retriever/README.md`
- `docs/data_engineering/lance/From BI to AI_ A Modern Lakehouse Stack with Lance and Iceberg.md`
- `docs/data_engineering/lance/Geospatial-Recommendation-System/README.md`
- `docs/data_engineering/lance/hybrid-search/README.md`
- `docs/data_engineering/lance/Ibis, LanceDB, and Data Stack Integration.md`
- `docs/data_engineering/lance/js-transformers/lancedb_cloud/README.md`
- `docs/data_engineering/lance/js-transformers/README.md`
- `docs/data_engineering/lance/js-transformers/walkthrough.md`
- `docs/data_engineering/lance/KCG_SUMMARY.md`
- `docs/data_engineering/lance/lance-ray/CONTRIBUTING.md`
- `docs/data_engineering/lance/lance-ray/docs/README.md`
- `docs/data_engineering/lance/lance-ray/docs/src/data-evolution.md`
- `docs/data_engineering/lance/lance-ray/docs/src/distributed-indexing.md`
- `docs/data_engineering/lance/lance-ray/docs/src/examples.md`
- `docs/data_engineering/lance/lance-ray/docs/src/index.md`
- `docs/data_engineering/lance/lance-ray/docs/src/read.md`
- `docs/data_engineering/lance/lance-ray/docs/src/write.md`
- `docs/data_engineering/lance/lance-ray/README.md`
- `docs/data_engineering/lance/lancedb-research-report.md`
- `docs/data_engineering/lance/multi-document-agentic-rag/README.md`
- `docs/data_engineering/lance/Multilingual_RAG/README.md`
- `docs/data_engineering/lance/multimodal-recipe-agent/README.md`
- `docs/data_engineering/lance/multimodal-search/README.md`
- `docs/data_engineering/lance/quickstart/README.md`
- `docs/data_engineering/lance/README.md`
- `docs/data_engineering/lance/time-travel-rag/README.md`

---
*Generated by MERGE_PLAN.md Phase 1 — 2026-06-06*
