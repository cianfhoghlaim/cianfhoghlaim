---
domain: data_platform
title: Data Architecture
description: Complete lakehouse architecture for the Cianfhoghlaim data platform — DuckDB, DuckLake, Iceberg, Lakekeeper, S3 Garage, Cloudflare R2, MotherDuck, LanceDB, RisingWave, and storage patterns.
updated: 2026-06-06
merged_from:
  - docs/data_engineering/ARCHITECTURE.md
  - docs/data_engineering/data-architecture.md
  - docs/data_engineering/data-pipeline-architecture.md
  - docs/data_engineering/duckdb-reference.md
  - docs/context/01-patterns/STORAGE.md
ccc_query_hints:
  - lakehouse architecture duckdb ducklake
  - garage s3 hetzner cloudflare r2
  - apache iceberg lakekeeper
  - motherduck
  - lancedb vector storage
  - risingwave streaming
  - olake cdc
  - storage patterns serial database executor
truth: partial

---

# Data Architecture

## Table of Contents

1. [Overview & Key Principles](#overview--key-principles)
2. [6-Layer Architecture](#6-layer-architecture)
3. [Lakehouse Architecture](#lakehouse-architecture)
4. [Federated Object Storage](#federated-object-storage)
5. [Streaming & Real-Time Processing](#streaming--real-time-processing)
6. [DuckDB Reference](#duckdb-reference)
7. [LanceDB Patterns](#lancedb-patterns)
8. [Semantic Layer](#semantic-layer)
9. [Best Practices](#best-practices)
10. [Architecture Diagrams](#architecture-diagrams)

---

## Overview & Key Principles

Modern data pipelines require integrating multiple specialized systems for batch processing, real-time streams, analytics, and AI workloads. This architecture unifies:

- **Lakehouse formats** (DuckLake, Iceberg) for ACID transactions on object storage
- **Streaming systems** (RisingWave) for real-time materialized views
- **Orchestration** (Dagster) for workflow management
- **Ingestion tools** (DLT, Crawl4AI) for data acquisition
- **Transformation layers** (SQLMesh, Ibis) for portable analytics
- **Incremental processing** (CocoIndex) for efficient updates
- **AI/ML integration** (LanceDB, Cognee) for semantic search and knowledge graphs

### Design Principles

1. **Separation of Storage and Compute**: Use object storage (S3, R2) with query engines that read data in-situ
2. **Open Standards**: Parquet, Iceberg, Arrow for interoperability
3. **Incremental Processing**: Only process changed data to minimize waste
4. **Unified API**: Single interface (Ibis) for batch and streaming
5. **Schema Evolution**: Automatic handling of schema changes
6. **Multi-Tenancy**: Built-in isolation for organizations
7. **Type Safety**: BAML -> Pydantic/Zod code generation for cross-language consistency

---

## 6-Layer Architecture

```
Layer 1: Intelligent Ingestion
  DLT (API data with incremental cursors)
  Git Sparse-Checkout (selective repository cloning)
  Crawl4AI / Firecrawl (documentation scraping with LLM extraction)
       |
       v
Layer 2: Storage & Cataloging
  DuckLake (versioned Parquet + PostgreSQL catalog)
  DuckDB / MotherDuck (analytics)
  PostgreSQL (CocoIndex state, Feast catalog, MLflow tracking)
       |
       v
Layer 3: Transformation & Enrichment
  SQLMesh (interval-based incremental models)
  Ibis (post-load transformations)
  CocoIndex (AI-powered transformations + embeddings)
       |
       +--------+--------+
       |                 |
       v                 v
Layer 4a: Semantic     Layer 4b: Feature Store
  CocoIndex (vectors)    Feast (offline: DuckDB)
  LanceDB (ANN search)   DragonflyDB (online)
  pgvector (Postgres)
       |                 |
       v                 v
Layer 5: ML & Analytics
  MLflow (experiment tracking, model registry)
  Agno + BAML (LLM-powered analysis agents)
  RisingWave (real-time materialized views)
       |
       v
Layer 6: Orchestration & Observability
  Dagster (asset-based workflows, sensors, schedules)
  CocoInsight (data lineage visualization)
```

---

## Lakehouse Architecture

### DuckLake: SQL-Based Table Format

DuckLake uses a SQL database for metadata and Parquet files for data storage. Unlike Iceberg/Delta which use JSON manifest files, DuckLake leverages existing SQL databases (PostgreSQL, MySQL, or DuckDB itself) as the catalog.

```
SQL Catalog (Postgres/DuckDB)  <->  DuckDB/App Client
         |                              |
   Metadata (schemas, versions)   Read/Write Parquet
         |                              |
         v                              v
     Object Storage (S3/R2) --> Parquet Files
```

**Key Features:**
- **ACID Transactions**: Snapshot isolation via SQL database
- **Time Travel**: Query historical versions of data
- **Schema Evolution**: Add/modify columns without rewriting data
- **Multi-User**: Concurrent reads/writes with optimistic locking
- **Lightweight**: No heavy services required

**Configuration:**
```python
import duckdb
con = duckdb.connect()
con.execute("""
    ATTACH 'ducklake:my_catalog.ducklake' AS catalog
    (TYPE POSTGRES,
     HOST 'localhost',
     DATABASE 'catalog_db',
     STORAGE_PATH 's3://my-bucket/data');
""")
```

### DuckLake Patterns

#### Catalog Bootstrap
```sql
INSTALL ducklake; LOAD ducklake;
ATTACH 'ducklake:catalog/ducklake.ducklake' AS lake (DATA_PATH 'data/lake/');
CALL lake.set_option('per_thread_output', 'true');
CALL lake.set_option('parquet_compression', 'zstd');
```

#### Zero-Copy File Registration
```sql
-- Register files without copying (idempotent)
CALL ducklake_add_data_files('lake', 'orders_raw', 'data/orders/*.parquet');
```

#### Hive-Style Partitioning
```sql
CREATE OR REPLACE TABLE lake.orders (
    order_id BIGINT, customer_id BIGINT, amount DECIMAL(10,2),
    order_date DATE, year INTEGER, month INTEGER
);
ALTER TABLE lake.orders SET PARTITIONED BY (year, month);
INSERT INTO lake.orders
SELECT order_id, customer_id, amount, order_date,
    YEAR(order_date) AS year, MONTH(order_date) AS month
FROM raw_orders;
```

#### Time-Travel Queries
```sql
SELECT COUNT(*) FROM lake.orders AT (VERSION => 4);
SELECT COUNT(*) FROM lake.orders AT (TIMESTAMP => '2024-12-29 10:30:00');
```

#### Compaction
```sql
-- Compact small files into larger, more efficient files
CALL lake.compact_table('orders');
```

### Apache Iceberg & Lakekeeper

Lakekeeper is an open-source Iceberg catalog service (REST API) written in Rust.

```
Query Engines (Trino, Spark, DuckDB) -> Lakekeeper (Rust REST Catalog)
  - Metadata management, OIDC auth, OPA policies
  - Change event streams
       |
       v
PostgreSQL Metadata Store -> Object Storage (S3/R2) -> Parquet/ORC Files
```

**Lakekeeper Features:**
- REST Catalog API: Standard Iceberg catalog interface
- Governance: Fine-grained access control, OIDC integration
- Event Streams: Emit change events on table modifications
- Multi-Engine: Works with Trino, Spark, Flink, DuckDB, ClickHouse

### OLake: CDC to Lakehouse

OLake is an open-source data replication tool for moving operational database data into lakehouse formats.

**Supported Sources**: PostgreSQL, MySQL, MongoDB, Oracle, Kafka (WIP)
**Destination Formats**: Apache Iceberg (with Lakekeeper catalog), Raw Parquet

**PostgreSQL CDC Setup:**
```sql
ALTER SYSTEM SET wal_level = 'logical';
ALTER SYSTEM SET max_replication_slots = 4;
CREATE PUBLICATION olake_publication FOR ALL TABLES
  WITH (publish='insert,update,delete,truncate');
```

**OLake Destination Config:**
```json
{
  "type": "ICEBERG",
  "writer": {
    "catalog_type": "rest",
    "rest_catalog_url": "https://lakekeeper.example.com/catalog",
    "iceberg_s3_path": "s3://my-bucket/warehouse",
    "s3_endpoint": "https://account-id.r2.cloudflarestorage.com"
  }
}
```

### DuckLake vs Iceberg Decision Matrix

| Criteria | DuckLake | Iceberg |
|----------|----------|---------|
| Setup complexity | Lower (SQL DB) | Higher (catalog service) |
| Multi-engine support | DuckDB primarily | Trino, Spark, Flink, DuckDB |
| Schema evolution | Via SQL DDL | Rich API |
| Time travel | Yes | Yes (more mature) |
| Partitioning | Basic | Advanced (hidden partitions) |
| Best for | Small-medium datasets | Large-scale enterprise |

---

## Federated Object Storage

### Garage S3 on Hetzner: Performance & Sovereignty Tier

Garage serves as the primary "hot" storage tier. It uses a CRDT-based architecture for robust operation on commodity hardware.

**Strategic Advantages:**
1. **Data Sovereignty**: Data resides on GDPR-compliant infrastructure under direct control
2. **Zero-Egress Compute Locality**: Co-located compute on Hetzner private network
3. **Cost Efficiency**: Significantly lower than AWS S3 Standard

**Critical Configuration — Virtual-Host Addressing:**
```toml
# garage.toml
[s3_api]
root_domain = "s3.h.yourdomain.com"
```
A wildcard DNS record (`*.s3.h.yourdomain.com`) must resolve to the Garage ingress IP.

### Cloudflare R2: Global Distribution Tier

Cloudflare R2 serves as the "warm" or "distribution" tier for consumers outside the Hetzner network, with zero egress costs.

**Integration with Lakekeeper:**
R2 does not support AWS STS AssumeRole in the same manner — Lakekeeper must use **Remote Signing**:
1. Client generates request hash
2. Sends to Lakekeeper (holding high-privilege R2 keys)
3. Lakekeeper signs and returns the signature
4. Client interacts directly with R2

### Storage Comparison

| Feature | Garage S3 (Hetzner) | Cloudflare R2 |
|---------|---------------------|---------------|
| Consistency Model | Eventual (CRDT-based) | Strong (Global) |
| Primary Use Case | High-throughput local compute | Global read access, DR |
| Addressing Style | Configurable (Path/V-Host) | Virtual-Host Preferred |
| Auth Mechanism | Static Keys / Internal | API Token |
| Lakekeeper Integ. | Direct / Static Creds | Remote Signing |
| Egress Cost | Low (Internal), Standard (External) | Zero (Global) |

### DuckDB Storage Secrets Configuration

**Garage S3:**
```sql
CREATE SECRET garage_secret (
    TYPE S3,
    KEY_ID 'garage_access_key',
    SECRET 'garage_secret_key',
    REGION 'garage',
    ENDPOINT 'http://s3.h.yourdomain.com:3900',
    URL_STYLE 'vhost',
    USE_SSL true
);
```

**Cloudflare R2:**
```sql
CREATE SECRET r2_secret (
    TYPE S3,
    KEY_ID 'r2_access_key',
    SECRET 'r2_secret_key',
    REGION 'auto',
    ENDPOINT 'https://<account_id>.r2.cloudflarestorage.com',
    URL_STYLE 'path'
);
```

### MotherDuck

MotherDuck is the cloud service for DuckDB. Use for shared analytics and team collaboration.

```python
# Local vs remote switch
# DUCKDB_DATABASE=../dashboard/sources/pypi_analytics.duckdb  # local
# DUCKDB_DATABASE=md:pypi_analytics?motherduck_token=${MOTHERDUCK_TOKEN}  # cloud
```

---

## Streaming & Real-Time Processing

### RisingWave Architecture

RisingWave is a distributed SQL streaming database with incrementally-updated materialized views.

```
Data Sources (Kafka, PostgreSQL CDC, Kinesis) -> RisingWave
  CREATE SOURCE -> CREATE TABLE -> CREATE MATERIALIZED VIEW
       |
  Sink results -> Destinations (Postgres, Redis, Iceberg, Kafka)
```

**Key Features:**
- PostgreSQL Compatible (psql and standard drivers)
- Incremental Computation (only processes changed data)
- Exactly-Once Semantics
- High Throughput: 10M+ events/second

**Real-Time User Features Example:**
```sql
CREATE SOURCE postgres_orders
WITH (connector = 'postgres-cdc', hostname = 'db.example.com',
      database.name = 'ecommerce', slot.name = 'rw_slot');

CREATE MATERIALIZED VIEW user_spending_recent AS
SELECT user_id, DATE_TRUNC('month', created_at) AS month,
       SUM(total_amount) AS total_spending, COUNT(id) AS order_count
FROM postgres_orders
WHERE created_at >= CURRENT_TIMESTAMP - INTERVAL '2 months'
GROUP BY user_id, DATE_TRUNC('month', created_at);

CREATE SINK user_spending_iceberg FROM user_spending_recent
WITH (connector = 'iceberg', type = 'upsert',
      warehouse.path = 's3://my-bucket/warehouse',
      catalog.type = 'rest', catalog.uri = 'https://lakekeeper.example.com/catalog');
```

### Stream-Batch Unification with Ibis

```python
import ibis

def compute_user_metrics(backend):
    orders = backend.table('orders')
    return orders.filter(orders.created_at >= ibis.now() - ibis.interval(months=2)) \
        .group_by([orders.user_id, orders.created_at.truncate('month').name('month')]) \
        .aggregate(total_spending=orders.total_amount.sum(), order_count=orders.count())

# Test on DuckDB (batch)
duckdb_con = ibis.duckdb.connect('data.duckdb')
batch_result = compute_user_metrics(duckdb_con).execute()

# Deploy to RisingWave (stream)
rw_con = ibis.risingwave.connect(host='risingwave.example.com')
rw_con.create_materialized_view('user_spending_stream', compute_user_metrics(rw_con))
```

---

## DuckDB Reference

DuckDB is an in-process SQL OLAP database — "SQLite for Analytics" — with columnar storage, vectorized execution, and PostgreSQL-compatible SQL dialect.

### Key Features

- **Columnar Storage**: PAX format, per-column compression, efficient CPU cache
- **Vectorized Query Execution**: SIMD, processes batches of values
- **ACID Compliance**: MVCC with snapshot isolation
- **Out-of-Core Processing**: Handles larger-than-memory datasets
- **File Format Support**: Parquet, CSV, JSON, Arrow, Iceberg, Delta, DuckLake
- **Extension System**: spatial, httpfs, postgres_scanner, mysql_scanner, sqlite_scanner

### Critical Constraint: SerialDatabaseExecutor (MANDATORY)

```python
import threading
from concurrent.futures import ThreadPoolExecutor
from typing import Callable, TypeVar

T = TypeVar("T")

class SerialDatabaseExecutor:
    _instance: "SerialDatabaseExecutor | None" = None
    _lock = threading.Lock()

    def __new__(cls) -> "SerialDatabaseExecutor":
        with cls._lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
                cls._instance._executor = ThreadPoolExecutor(
                    max_workers=1,
                    thread_name_prefix="duckdb_serial",
                )
        return cls._instance

    def run(self, fn: Callable[..., T], *args, **kwargs) -> T:
        future = self._executor.submit(fn, *args, **kwargs)
        return future.result()

executor = SerialDatabaseExecutor()
results = executor.run(query_data, "SELECT * FROM users LIMIT 100")
```

### Read-Only Connections

```python
def safe_query(db_path: str, sql: str) -> list[dict]:
    conn = duckdb.connect(db_path, read_only=True)
    try:
        columns = [desc[0] for desc in conn.execute(sql).description]
        rows = conn.execute(sql).fetchall()
        return [dict(zip(columns, row)) for row in rows]
    finally:
        conn.close()
```

### Performance Tips

1. **Always use Parquet** (up to 600x faster than CSV)
2. **Reuse connections** — don't create new connection per query
3. **Select specific columns** — avoid `SELECT *`
4. **Use EXPLAIN ANALYZE** to profile
5. **Configure memory**: `SET memory_limit = '4GB';`
6. **Cloud data** via httpfs: `SELECT * FROM 's3://bucket/data.parquet';`

### Extensions

```sql
INSTALL httpfs; LOAD httpfs;         -- S3/HTTP
INSTALL spatial; LOAD spatial;       -- Geospatial
INSTALL iceberg; LOAD iceberg;       -- Apache Iceberg
INSTALL delta; LOAD delta;           -- Delta Lake
INSTALL postgres_scanner; LOAD postgres_scanner;  -- PostgreSQL
INSTALL mysql_scanner; LOAD mysql_scanner;         -- MySQL
```

### vs Other Databases

| Feature | DuckDB | SQLite | PostgreSQL |
|---------|--------|--------|------------|
| Architecture | Embedded, in-process | Embedded, in-process | Client-server |
| Storage Model | Columnar | Row-based | Row-based |
| Best For | OLAP/Analytics | OLTP | Multi-user apps |
| File Format | Parquet-first | SQLite format | Own format |

---

## LanceDB Patterns

### HNSW Index Management (MANDATORY)

```python
HNSW_DROP_THRESHOLD = 50

class LanceDBManager:
    def __init__(self, uri: str):
        self.db = lancedb.connect(uri)

    def insert_with_index_management(self, table_name: str, data: list[dict],
                                     vector_column: str = "embedding"):
        table = self.db.open_table(table_name)
        need_rebuild = len(data) > HNSW_DROP_THRESHOLD

        if need_rebuild:
            try:
                table.drop_index(f"{vector_column}_idx")
            except Exception:
                pass

        table.add(data)

        if need_rebuild:
            table.create_index(f"{vector_column}_idx", index_type="IVF_HNSW",
                             metric="cosine", num_partitions=256, num_sub_vectors=32)

    def create_table_with_index(self, table_name: str, data: list[dict],
                                vector_column: str = "embedding"):
        table = self.db.create_table(table_name, data, mode="overwrite")
        table.create_index(f"{vector_column}_idx", index_type="IVF_HNSW",
                         metric="cosine", num_partitions=256, num_sub_vectors=32)
        table.create_fts_index("text", with_position=True)
        return table
```

### Hybrid Search (Vector + FTS)

```python
def hybrid_search(table, query_embedding: list[float], query_text: str,
                  limit: int = 10, vector_weight: float = 0.7) -> list[dict]:
    vector_results = table.search(query_embedding).metric("cosine").limit(limit * 2).to_list()
    fts_results = table.search(query_text, query_type="fts").limit(limit * 2).to_list()

    combined = {}
    for r in vector_results:
        combined[r["id"]] = {"data": r, "vector_score": 1 - r["_distance"], "fts_score": 0}
    for r in fts_results:
        if r["id"] in combined:
            combined[r["id"]]["fts_score"] = r["_score"]
        else:
            combined[r["id"]] = {"data": r, "vector_score": 0, "fts_score": r["_score"]}

    for item in combined.values():
        item["hybrid_score"] = (vector_weight * item["vector_score"] +
                                (1 - vector_weight) * item["fts_score"])

    sorted_results = sorted(combined.values(), key=lambda x: x["hybrid_score"], reverse=True)
    return [r["data"] for r in sorted_results[:limit]]
```

### Architecture Constraints

| Component | Rule |
|-----------|------|
| **DuckDB** | SINGLE_THREADED_ONLY via SerialDatabaseExecutor |
| **LanceDB** | MVCC safe multi-process; SerialDatabaseExecutor within process |
| **HNSW indexes** | DROP before bulk insert >50 rows; RECREATE after |
| **DuckLake** | Zero-copy file registration; snapshot before mutations |

---

## Semantic Layer

### Cube.js Metric Definitions Example

```javascript
cube('Orders', {
  sql: `SELECT * FROM orders`,
  measures: {
    count: { type: 'count' },
    revenue: { type: 'sum', sql: 'amount', format: 'currency' },
    avgOrderValue: { type: 'avg', sql: 'amount', format: 'currency' },
  },
  dimensions: {
    status: { type: 'string', sql: 'status' },
    createdAt: { type: 'time', sql: 'created_at' },
  },
});
```

---

## Best Practices

### Schema Management
- Use DLT's schema evolution for automatic column additions
- Use Iceberg's schema evolution API for production tables
- Enforce schema contracts with primary keys and nullable constraints

### Incremental Processing
- Default to `write_disposition="append"` with incremental cursors
- Use CocoIndex for automatic change detection on file systems
- Force full refresh only when schema changes require it

### Data Quality
- Validate data in DLT resources before loading
- Use RisingWave constraints for streaming validation
- Implement data contracts at API boundaries

### Performance
- Partition large tables by time (day/month)
- Create indexes on join and filter columns
- Use columnar formats (Parquet) for analytics
- Pre-drop HNSW for bulk LanceDB inserts

### Secrets Management
- Use `.dlt/secrets.toml` for DLT credentials (excluded from git)
- Use environment variables for Dagster resources
- Never commit credentials to version control

### Critical Constraints Checklist

- [ ] Using SerialDatabaseExecutor for DuckDB?
- [ ] Batch size >= 100 for embeddings?
- [ ] HNSW indexes dropped for bulk >50 rows?
- [ ] BAML schema validated?
- [ ] Irish content using specialized models?
- [ ] Deduplication applied to multi-result queries?

---

## Architecture Diagrams

### End-to-End Data Pipeline

```
Data Sources (Web APIs, PostgreSQL, Files)
    |                |           |
Crawl4AI/Firecrawl  OLake       DLT
    |                |           |
    v                v           v
Dagster Pipeline Orchestration <-> RisingWave Stream Processing
    |                                |
    +-------+-------+        +------+------+
    |       |       |        |      |      |
DuckLake  Iceberg  LanceDB  Memgraph  Feast
(DuckDB) (Lakekeeper) (Vectors) (Graph)
    |       |       |        |      |
    +-------+-------+--------+------+
                    |
                    v
            Object Storage (R2/S3 Garage)
```

### Lakehouse Architecture

```
LakeFS (Version Control) -> main / dev / test
       |
Catalog Layer -> Lakekeeper (Iceberg) or DuckLake (SQL DB)
       |
Object Storage (R2/S3) -> warehouse/table/data/*.parquet
```

### Federated Metadata Architecture

```
Lakekeeper (Iceberg/Lance Registry)
  - Backend: Self-hosted PostgreSQL
  - Lance tables registered via Iceberg adapter (table_type=lance)

DuckLake (SQL-Native Catalog)
  - Backend: PlanetScale (MySQL)
  - Metadata in SQL, data in Parquet on Garage/R2
```

This "Grand Unification" is achieved by treating DuckDB as the universal adapter:
1. **Lakekeeper** (with PostgreSQL) governs Iceberg and Lance domains
2. **DuckLake** (PlanetScale backend) governs DuckLake domain
3. **Garage and R2** provide flexible, cost-effective storage
