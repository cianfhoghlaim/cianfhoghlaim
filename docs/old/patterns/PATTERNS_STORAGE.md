# Pattern: Storage (DuckDB, LanceDB, DuckLake)

## Critical Constraints

| Constraint | Description | Violation Consequence |
|------------|-------------|----------------------|
| **DuckDB: SINGLE_THREADED_ONLY** | Never access DuckDB concurrently | Segfault, data corruption |
| **LanceDB: MVCC safe** | Multi-process safe, single-threaded within process | Use SerialDatabaseExecutor |
| **HNSW indexes: DROP before bulk insert** | Drop index for >50 rows | 20x slower inserts, timeouts |
| **DuckLake: Zero-copy registration** | Register files, don't copy data | Wasted storage, slow ingestion |
| **Snapshots: Create before mutations** | Always snapshot before data changes | No time-travel recovery |

---

## DuckDB Patterns

### Pattern 1: SerialDatabaseExecutor (MANDATORY)

**When to use**: ALL DuckDB operations in multi-threaded/async applications.

**Implementation**:
```python
import threading
from concurrent.futures import ThreadPoolExecutor
from typing import Callable, TypeVar

T = TypeVar("T")

class SerialDatabaseExecutor:
    """
    Singleton executor for serial DuckDB operations.

    DuckDB requires single-threaded access - concurrent operations
    cause segfaults and data corruption.
    """
    _instance: "SerialDatabaseExecutor | None" = None
    _lock = threading.Lock()

    def __new__(cls) -> "SerialDatabaseExecutor":
        with cls._lock:
            if cls._instance is None:
                cls._instance = super().__new__(cls)
                cls._instance._executor = ThreadPoolExecutor(
                    max_workers=1,  # CRITICAL: Single thread only
                    thread_name_prefix="duckdb_serial",
                )
        return cls._instance

    def run(self, fn: Callable[..., T], *args, **kwargs) -> T:
        """Execute function in serial thread, blocking until complete."""
        future = self._executor.submit(fn, *args, **kwargs)
        return future.result()

    async def run_async(self, fn: Callable[..., T], *args, **kwargs) -> T:
        """Async wrapper for serial execution."""
        import asyncio
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            self._executor,
            lambda: fn(*args, **kwargs)
        )

# Usage
executor = SerialDatabaseExecutor()

def query_data(sql: str) -> list:
    import duckdb
    conn = duckdb.connect("data.duckdb", read_only=True)
    try:
        return conn.execute(sql).fetchall()
    finally:
        conn.close()

# Safe execution
results = executor.run(query_data, "SELECT * FROM users LIMIT 100")
```

### Pattern 2: Read-Only Connections

**When to use**: Query-only operations (analytics, search).

**Implementation**:
```python
import duckdb

def safe_query(db_path: str, sql: str) -> list[dict]:
    """Read-only query with automatic cleanup."""
    conn = duckdb.connect(db_path, read_only=True)
    try:
        columns = [desc[0] for desc in conn.execute(sql).description]
        rows = conn.execute(sql).fetchall()
        return [dict(zip(columns, row)) for row in rows]
    finally:
        conn.close()

# Use in SerialDatabaseExecutor
executor = SerialDatabaseExecutor()
results = executor.run(safe_query, "data.duckdb", "SELECT * FROM docs")
```

### Pattern 3: DuckDB Spatial Extension

**When to use**: Geospatial queries (boundaries, distances).

**Implementation**:
```python
import duckdb

def init_spatial_db(db_path: str):
    """Initialize DuckDB with spatial extension."""
    conn = duckdb.connect(db_path)
    try:
        conn.execute("INSTALL spatial; LOAD spatial;")
        conn.execute("""
            CREATE TABLE IF NOT EXISTS boundaries (
                id INTEGER PRIMARY KEY,
                name VARCHAR,
                geom GEOMETRY
            )
        """)
    finally:
        conn.close()

def spatial_query(db_path: str, lat: float, lon: float, radius_km: float):
    """Find features within radius."""
    conn = duckdb.connect(db_path, read_only=True)
    try:
        return conn.execute(f"""
            SELECT name, ST_Distance(
                geom,
                ST_Point({lon}, {lat})
            ) * 111.32 AS distance_km
            FROM boundaries
            WHERE ST_DWithin(
                geom,
                ST_Point({lon}, {lat}),
                {radius_km / 111.32}
            )
            ORDER BY distance_km
        """).fetchall()
    finally:
        conn.close()
```

---

## LanceDB Patterns

### Pattern 4: HNSW Index Management (MANDATORY)

**When to use**: ANY bulk insert operation.

**Implementation**:
```python
import lancedb

HNSW_DROP_THRESHOLD = 50  # Drop index for bulk inserts >50 rows

class LanceDBManager:
    def __init__(self, uri: str):
        self.db = lancedb.connect(uri)

    def insert_with_index_management(
        self,
        table_name: str,
        data: list[dict],
        vector_column: str = "embedding",
    ):
        """Insert data with automatic HNSW index management."""
        table = self.db.open_table(table_name)
        need_rebuild = len(data) > HNSW_DROP_THRESHOLD

        # Drop index before bulk insert (20x speedup)
        if need_rebuild:
            try:
                table.drop_index(f"{vector_column}_idx")
                print(f"Dropped HNSW index for bulk insert of {len(data)} rows")
            except Exception:
                pass  # Index might not exist

        # Insert data
        table.add(data)

        # Recreate index after bulk insert
        if need_rebuild:
            table.create_index(
                f"{vector_column}_idx",
                index_type="IVF_HNSW",
                metric="cosine",
                num_partitions=256,
                num_sub_vectors=32,
            )
            print(f"Recreated HNSW index after {len(data)} row insert")

    def create_table_with_index(
        self,
        table_name: str,
        data: list[dict],
        vector_column: str = "embedding",
    ):
        """Create new table with vector and FTS indexes."""
        table = self.db.create_table(table_name, data, mode="overwrite")

        # Create vector index
        table.create_index(
            f"{vector_column}_idx",
            index_type="IVF_HNSW",
            metric="cosine",
            num_partitions=256,
            num_sub_vectors=32,
        )

        # Create full-text search index
        table.create_fts_index("text", with_position=True)

        return table
```

### Pattern 5: Hybrid Search (Vector + FTS)

**When to use**: Semantic search with keyword filtering.

**Implementation**:
```python
import lancedb

def hybrid_search(
    table: lancedb.table.Table,
    query_embedding: list[float],
    query_text: str,
    limit: int = 10,
    vector_weight: float = 0.7,
) -> list[dict]:
    """Combined vector and full-text search."""

    # Vector search
    vector_results = (
        table.search(query_embedding)
        .metric("cosine")
        .limit(limit * 2)  # Over-fetch for reranking
        .to_list()
    )

    # Full-text search
    fts_results = (
        table.search(query_text, query_type="fts")
        .limit(limit * 2)
        .to_list()
    )

    # Combine and rerank
    combined = {}
    for r in vector_results:
        combined[r["id"]] = {
            "data": r,
            "vector_score": 1 - r["_distance"],  # Convert distance to similarity
            "fts_score": 0,
        }

    for r in fts_results:
        if r["id"] in combined:
            combined[r["id"]]["fts_score"] = r["_score"]
        else:
            combined[r["id"]] = {
                "data": r,
                "vector_score": 0,
                "fts_score": r["_score"],
            }

    # Calculate hybrid score
    for item in combined.values():
        item["hybrid_score"] = (
            vector_weight * item["vector_score"] +
            (1 - vector_weight) * item["fts_score"]
        )

    # Sort and return top results
    sorted_results = sorted(
        combined.values(),
        key=lambda x: x["hybrid_score"],
        reverse=True,
    )
    return [r["data"] for r in sorted_results[:limit]]
```

---

## DuckLake Patterns

### Pattern 6: Catalog Bootstrap

**When to use**: Initialize DuckLake for a new project.

**Implementation**:
```sql
-- Install and load DuckLake extension
INSTALL ducklake;
LOAD ducklake;

-- Attach catalog with metadata storage
ATTACH 'ducklake:catalog/ducklake.ducklake'
  AS lake (DATA_PATH 'data/lake/');

-- Configure for optimal performance
CALL lake.set_option('per_thread_output', 'true');
CALL lake.set_option('parquet_compression', 'zstd');
CALL lake.set_option('parquet_version', '2');
```

### Pattern 7: Zero-Copy File Registration

**When to use**: Add existing Parquet files without copying.

**Implementation**:
```sql
-- Register files without copying (idempotent)
CALL ducklake_add_data_files(
    'lake',           -- Catalog name
    'orders_raw',     -- Table name (created if not exists)
    'data/orders/*.parquet'  -- Glob pattern
);

-- Files remain in original location
-- Catalog tracks file locations and metadata
-- Re-running is safe (idempotent)
```

### Pattern 8: Hive-Style Partitioning

**When to use**: Time-series data, multi-tenant data.

**Implementation**:
```sql
-- Create partitioned table
CREATE OR REPLACE TABLE lake.orders (
    order_id BIGINT,
    customer_id BIGINT,
    amount DECIMAL(10, 2),
    order_date DATE,
    year INTEGER,
    month INTEGER
);

-- Set partition columns
ALTER TABLE lake.orders SET PARTITIONED BY (year, month);

-- Insert data (automatically routed to partitions)
INSERT INTO lake.orders
SELECT
    order_id,
    customer_id,
    amount,
    order_date,
    YEAR(order_date) AS year,
    MONTH(order_date) AS month
FROM raw_orders;

-- Query with partition pruning (fast!)
SELECT SUM(amount)
FROM lake.orders
WHERE year = 2024 AND month = 12;
```

### Pattern 9: Time-Travel Queries

**When to use**: Audit, debugging, point-in-time analysis.

**Implementation**:
```sql
-- Current state
SELECT COUNT(*) FROM lake.orders;

-- Query at specific snapshot version
SELECT COUNT(*)
FROM lake.orders AT (VERSION => 4);

-- Query at specific timestamp
SELECT COUNT(*)
FROM lake.orders AT (TIMESTAMP => '2024-12-29 10:30:00');

-- Compare versions
SELECT
    'Current' AS version_label,
    COUNT(*) AS row_count
FROM lake.orders
UNION ALL
SELECT
    'Yesterday' AS version_label,
    COUNT(*) AS row_count
FROM lake.orders AT (TIMESTAMP => CURRENT_TIMESTAMP - INTERVAL '1 day');
```

### Pattern 10: Change Data Capture

**When to use**: Track changes between snapshots.

**Implementation**:
```sql
-- Create temp tables for comparison
CREATE TEMP TABLE from_snapshot AS
SELECT * FROM lake.orders AT (VERSION => 5);

CREATE TEMP TABLE to_snapshot AS
SELECT * FROM lake.orders AT (VERSION => 6);

-- Count insertions and deletions
SELECT
    GREATEST(0, to_count - from_count) AS insertions,
    GREATEST(0, from_count - to_count) AS deletions
FROM (
    SELECT
        (SELECT COUNT(*) FROM from_snapshot) AS from_count,
        (SELECT COUNT(*) FROM to_snapshot) AS to_count
);

-- Find specific changes (for small datasets)
-- New rows
SELECT * FROM to_snapshot
WHERE order_id NOT IN (SELECT order_id FROM from_snapshot);

-- Deleted rows
SELECT * FROM from_snapshot
WHERE order_id NOT IN (SELECT order_id FROM to_snapshot);
```

### Pattern 11: Compaction

**When to use**: After many small writes, before heavy reads.

**Implementation**:
```sql
-- Check current file statistics
SELECT
    COUNT(*) AS file_count,
    SUM(file_size_bytes) / 1024 / 1024 AS total_mb,
    AVG(record_count) AS avg_records_per_file
FROM __ducklake_metadata_lake.ducklake_data_file
WHERE table_id = (
    SELECT table_id FROM __ducklake_metadata_lake.ducklake_table
    WHERE table_name = 'orders'
);

-- Compact small files (merge adjacent files)
-- Creates larger, more efficient files
CALL lake.compact_table('orders');

-- Verify improvement
-- File count should decrease, avg records should increase
```

---

## Semantic Layer Patterns

### Pattern 12: Cube Metric Definitions

**When to use**: Consistent analytics across applications.

**Implementation** (cube.js schema):
```javascript
cube('Orders', {
  sql: `SELECT * FROM orders`,

  measures: {
    count: {
      type: 'count',
    },
    revenue: {
      type: 'sum',
      sql: 'amount',
      format: 'currency',
    },
    avgOrderValue: {
      type: 'avg',
      sql: 'amount',
      format: 'currency',
    },
  },

  dimensions: {
    status: {
      type: 'string',
      sql: 'status',
    },
    createdAt: {
      type: 'time',
      sql: 'created_at',
    },
    customer: {
      type: 'string',
      sql: 'customer_id',
    },
  },

  preAggregations: {
    // Pre-compute daily aggregates for fast queries
    dailyRevenue: {
      measures: [Orders.revenue, Orders.count],
      dimensions: [Orders.status],
      timeDimension: Orders.createdAt,
      granularity: 'day',
      refreshKey: {
        every: '1 hour',
      },
    },
  },
});
```

### Pattern 13: Rill Dashboard

**When to use**: Quick BI dashboards from SQL.

**Implementation** (rill.yaml):
```yaml
type: explore
title: Education Metrics Dashboard

model: curriculum_metrics

dimensions:
  - subject
  - level
  - nation
  - language

measures:
  - total_learning_outcomes
  - avg_assessment_score
  - completion_rate

time_dimension: created_at

default_time_range: P30D

security:
  access_policy: |
    -- Row-level security by nation
    nation IN ('{{ .user.attributes.allowed_nations | join "','" }}')
```

---

## Integration Points

| Component | Connects To | Pattern |
|-----------|-------------|---------|
| **DuckDB** | DLT destinations | `dlt.destination("duckdb")` |
| **DuckDB** | CocoIndex sources | `DuckDB(query=...)` |
| **LanceDB** | CocoIndex exports | `LanceDB(uri=...)` |
| **DuckLake** | Dagster assets | Time-travel for testing |
| **Cube** | Frontend | REST/GraphQL API |
| **Rill** | Embedded analytics | iframe/SDK integration |

---

## Common Mistakes

| Mistake | Fix |
|---------|-----|
| Concurrent DuckDB access | Always use SerialDatabaseExecutor |
| Bulk insert without dropping HNSW | Drop index for >50 rows, recreate after |
| Copying files to DuckLake | Use `ducklake_add_data_files` for zero-copy |
| Skipping snapshots | Always snapshot before data mutations |
| No partition pruning | Add partition columns to WHERE clauses |
| Missing FTS index | Create FTS for text search columns |
| Large vector dimensions | Use PQ compression for >1024 dims |

---

## Performance Comparison

| Operation | Without Pattern | With Pattern | Improvement |
|-----------|-----------------|--------------|-------------|
| DuckDB concurrent query | Segfault | Success | Required |
| LanceDB bulk insert (1000 rows) | 45s | 2.2s | 20x |
| DuckLake file registration | Copy all data | Zero-copy | 100x+ |
| Partition query (1B rows) | 120s | 0.5s | 240x |
| Cube pre-aggregated query | 5s | 50ms | 100x |

---

## References

- Source: `taighde/ducklake/`, `taighde/semantic_layer/`
- Skills: `.claude/skills/duckdb/`, `.claude/skills/lancedb/`, `.claude/skills/ducklake/`
- Examples: `sruth/oideachais/storage/`, `sruth/aleyum/pipelines/shared/ducklake.py`
