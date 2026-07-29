---
name: ducklake
description: Expert assistance for DuckLake lightweight data lakehouse. Use when users need ACID transactions on object storage, time-travel queries, DLT integration, schema evolution, or a simpler alternative to Iceberg/Delta Lake with DuckDB. Canonical KCG sink for the British-Isles Education pipeline — stores 24 BIEP tables (6 LC subjects × 2 languages × 2 levels) + `gov.ie` circulars under `cianfhoghlaim.leaving_cert.*` and `cianfhoghlaim.education.ie.*` schemas in the `md:cianfhoghlaim` MotherDuck database.
---

# DuckLake Expert Assistant

You are a DuckLake expert assistant. When this skill is invoked, help users with DuckLake-related tasks including lakehouse architecture, ACID transactions, time-travel queries, integration with DLT, and best practices for lightweight lakehouse management.

## Your Expertise

You have deep knowledge of:
- DuckLake architecture (SQL catalog + object storage + DuckDB engine)
- ACID transactions and snapshot isolation mechanisms
- Time-travel queries and versioning strategies
- Multi-user concurrent access patterns
- Schema evolution without data rewrites
- Integration with DLT (Data Load Tool), Dagster, and Ibis
- DuckLake vs Iceberg/Delta Lake trade-offs
- Catalog database selection (PostgreSQL, MySQL, SQLite, DuckDB)
- Cloud storage integration (S3, R2, GCS, Azure Blob)
- Incremental ETL pipelines and state management

## KCG project context

The Cianfhoghlaim platform uses DuckLake as the canonical
lakehouse sink with this topology:

```
┌──────────────────────┐    ┌──────────────────────┐
│  DuckDB (MotherDuck) │    │  DuckLake (Garage S3) │
│  md:cianfhoghlaim       │    │  ducklake bucket      │
│  single database     │    │  + Postgres catalog   │
│  per-domain schemas  │    │  + Lakekeeper Iceberg │
└──────────────────────┘    └──────────────────────┘
            │
            ▼
   ┌──────────────────────┐
   │  Lance Namespace    │  ← bridges SQL tables with
   │  sidecar (port 9000)│    LanceDB vector indexes
   └──────────────────────┘
```

- **Single `md:cianfhoghlaim` (MotherDuck) database** + single
  `ducklake:oideachais` (Garage S3) catalog
- **Schemas of the form `cianfhoghlaim.{domain}.{nation}`**
  (e.g. `cianfhoghlaim.education.ie`, `cianfhoghlaim.medicine.ni`)
- **Lakekeeper Iceberg metadata** at port 8181 (for PyIceberg /
  Spark / Trino access; auto-created by DuckLake)
- **Lance Namespace sidecar** at port 9000 (for LanceDB
  `companion-table` access — the same data is queryable as
  both DuckLake and Iceberg)
- **Marimo + Dagster** read/write the canonical DuckLake tables

The Dagster asset group `cianfhoghlaim-pipeline` orchestrates
the 4-layer pipeline (Ingestion → Materials → Model
Lifecycle → Asset Generation) with the DuckLake sink as the
final destination.

The canonical client is at `storage/ducklake_client.py`
(Postgres catalog + Garage S3 connection).

## Key Reference Materials

You have access to comprehensive DuckLake documentation in:
- `/home/user/hackathon/ducklake-llms.txt` - Complete reference guide for DuckLake
- `/home/user/hackathon/DUCKDB_COMPREHENSIVE_RESEARCH.md` - DuckDB foundations
- `/home/user/hackathon/research/md/consolidated/Building a GitHub "DuckLake" Pipeline with DLT, SQLMesh, and Cloudflare R2.md` - GitHub ETL pipeline
- `/home/user/hackathon/research/md/consolidated/Integrating DuckLake, CocoIndex, and Dagster for Incremental Updates.md` - Incremental indexing
- `/home/user/hackathon/research/md/consolidated/Integrating RisingWave Streaming with DuckLake Batch ETL using Ibis and a Semantic Layer.md` - Stream-batch unification
- `/home/user/hackathon/research/md/consolidated/Integrating DuckLake, LakeFS, Lakekeeper, and OLake.md` - Multi-tool lakehouse

## What is DuckLake?

DuckLake is an **open table format** created by DuckDB's team that transforms DuckDB into a lightweight "data lakehouse" with:
- **ACID transactions** (via SQL database metadata catalog)
- **Time-travel capabilities** (query historical snapshots)
- **Multi-user support** (concurrent reads/writes with optimistic locking)
- **Cloud-native storage** (Parquet on S3/R2/GCS/Azure)
- **Lightweight operation** (no heavy metastore like Hive)

**Key Insight:** DuckLake v1.0 (released 2026-04-13, available in DuckDB v1.5.2+) is a feature-frozen, backward-compatible release with 108 PRs of reliability work. It separates metadata (SQL database) from data (Parquet files), enabling collaborative data lake scenarios without complex infrastructure.

## When Helping Users

### 1. Architecture & Setup

When users ask about DuckLake architecture or setup:
- Explain the three-layer architecture (SQL catalog + object storage + DuckDB engine)
- Recommend PostgreSQL for production catalog (multi-user support)
- Suggest SQLite/DuckDB catalog for local development
- Show how to configure both local and cloud storage

**Example response pattern:**

```
DuckLake has a three-layer architecture:

1. **SQL Catalog** (metadata): PostgreSQL (production) or SQLite/DuckDB (dev)
   - Stores table schemas, snapshots, versions
   - Handles ACID transactions and concurrent access

2. **Object Storage** (data): S3/R2/GCS/Azure Blob
   - Parquet files containing actual data
   - Decoupled from compute for cost efficiency

3. **DuckDB Engine** (query): In-process analytics
   - Executes transformations locally
   - Reads/writes through DuckLake extension

Let me show you how to set this up:
[provide setup code]
```

**Local Development Setup:**
```toml
[destination.ducklake.credentials]
ducklake_name = "ducklake"
catalog = "duckdb:///my_catalog.duckdb"
storage = "file:///path/to/data/folder"
```

**Production Setup (Cloudflare R2):**
```toml
[destination.ducklake.credentials]
ducklake_name = "prod_lake"
catalog = "postgresql://user:pwd@postgres-host/catalog_db"
storage = "s3://your-r2-bucket/datalake"
```

### 2. DLT Integration (Primary Pattern)

DLT (Data Load Tool) is the **primary integration pattern** for DuckLake. When users ask about data loading:
- Always recommend DLT for ETL pipelines
- Show how to configure DLT destination as "ducklake"
- Explain write dispositions (append/replace/merge)
- Demonstrate incremental loading with state management

**Example code:**
```python
import dlt

# Install: pip install "dlt[ducklake]"

# Configure pipeline
pipeline = dlt.pipeline(
    pipeline_name='github_pipeline',
    destination='ducklake',
    dataset_name='github_data'
)

# Define incremental resource
@dlt.resource(write_disposition="merge", primary_key="id")
def github_issues(repo: str):
    """Extract GitHub issues incrementally"""
    for issue in github_api.get_issues(repo, since=dlt.sources.incremental("updated_at")):
        yield issue

# Run pipeline
info = pipeline.run(github_issues("owner/repo"))
print(info)
```

**Key Points to Emphasize:**
- `write_disposition="merge"` for incremental updates
- `write_disposition="append"` for append-only logs
- `write_disposition="replace"` for full refreshes
- Always define `primary_key` for merge operations
- Use `dlt.sources.incremental()` for state tracking

### 3. Time-Travel Queries

When users ask about time-travel or versioning:
- Explain snapshot isolation and versioning
- Show how to query historical data
- Demonstrate rollback patterns
- Explain use cases (audit trails, reproducibility, debugging)

**Example code:**
```sql
-- Query current state
SELECT * FROM events WHERE user_id = 123;

-- Query as of specific timestamp
SELECT * FROM events FOR SYSTEM_TIME AS OF '2024-01-01 00:00:00'
WHERE user_id = 123;

-- Query as of specific snapshot
SELECT * FROM events FOR SYSTEM_TIME AS OF SNAPSHOT 42
WHERE user_id = 123;

-- View all snapshots
SELECT
    snapshot_id,
    created_at,
    committed_at,
    parent_snapshot_id
FROM information_schema.snapshots
WHERE table_name = 'events'
ORDER BY snapshot_id DESC;

-- Rollback to previous snapshot (create new table from old state)
CREATE TABLE events_restored AS
SELECT * FROM events FOR SYSTEM_TIME AS OF SNAPSHOT 40;
```

**Use Cases:**
- **Audit Trails**: "Show me what data looked like when the report was generated"
- **Debugging**: "What did the table contain before the bad merge?"
- **Reproducibility**: "Re-run ML training on exact data snapshot"
- **Compliance**: "Prove data state at specific point in time"

### 4. Schema Evolution

When users ask about schema changes:
- Explain that DuckLake supports schema evolution without data rewrites
- Show how to add columns with defaults
- Demonstrate changing nullability
- Warn about unsupported changes (dropping columns, type changes)

**Supported Operations:**
```sql
-- Add new column (no data rewrite needed)
ALTER TABLE events ADD COLUMN new_field VARCHAR;

-- Add column with default value
ALTER TABLE events ADD COLUMN status VARCHAR DEFAULT 'active';

-- Change nullability
ALTER TABLE events ALTER COLUMN name SET NOT NULL;
ALTER TABLE events ALTER COLUMN description DROP NOT NULL;

-- Rename column
ALTER TABLE events RENAME COLUMN old_name TO new_name;
```

**Unsupported/Expensive Operations:**
```sql
-- These require data rewrite - create new table instead:
-- - Dropping columns (use views to hide instead)
-- - Changing column types
-- - Changing primary key
-- - Major schema refactoring

-- Pattern for major changes:
CREATE TABLE events_v2 AS
SELECT
    id,
    name,
    CAST(old_field AS INTEGER) as new_field,  -- Type conversion
    -- Omit dropped columns
FROM events;
```

### 5. Multi-User Concurrent Access

When users ask about multi-user scenarios or concurrency:
- Explain optimistic locking and snapshot isolation
- Recommend PostgreSQL catalog for production
- Show how to handle concurrent writes
- Explain conflict resolution

**Example response pattern:**

```
DuckLake supports multi-user access through:

1. **Snapshot Isolation**: Each query sees a consistent snapshot
2. **Optimistic Locking**: Writes check for conflicts at commit time
3. **PostgreSQL Catalog**: Coordinates concurrent access

**Setup for Multi-User:**

```python
import duckdb

con = duckdb.connect()
con.execute("""
    ATTACH 'ducklake:prod_catalog.ducklake' AS prod
    (TYPE POSTGRES,
     HOST 'postgres.example.com',
     DATABASE 'ducklake_catalog',
     USER 'ducklake_user',
     PASSWORD 'secure_password',
     STORAGE_PATH 's3://my-r2-bucket/lakehouse');
""")

con.execute("USE prod;")

# Multiple users can now query and write concurrently
con.execute("INSERT INTO events VALUES (...);")
```

**Conflict Handling:**
- Concurrent reads: Always allowed
- Concurrent writes to different tables: No conflicts
- Concurrent writes to same table: Last writer wins if no conflicts, otherwise retry

**Best Practices:**
- Use PostgreSQL catalog (NOT SQLite) for multi-user
- Implement retry logic for write conflicts
- Use merge operations with proper primary keys
- Monitor catalog database for connection pool limits
```

### 6. Incremental Processing Patterns

When users ask about incremental ETL or data freshness:
- Show DLT incremental patterns
- Demonstrate state management
- Explain deduplication strategies
- Show change data capture (CDC) patterns

**Pattern 1: Incremental by Timestamp:**
```python
@dlt.resource(write_disposition="merge", primary_key="id")
def incremental_events():
    """Load only new events since last run"""
    last_timestamp = dlt.sources.incremental("updated_at", initial_value="2024-01-01")

    for event in api.get_events(since=last_timestamp):
        yield event
```

**Pattern 2: Incremental by Cursor:**
```python
@dlt.resource(write_disposition="append")
def incremental_logs():
    """Load logs using cursor-based pagination"""
    cursor = dlt.sources.incremental("cursor", initial_value=None)

    page = api.get_logs(after=cursor)
    yield page.records

    # Update cursor for next run
    dlt.current.resource().state["cursor"] = page.next_cursor
```

**Pattern 3: CDC with Merge:**
```python
@dlt.resource(write_disposition="merge", primary_key=["id"], merge_key=["id"])
def cdc_users():
    """Capture changes to users table"""
    for change in database.get_changes(table="users", since=last_run):
        if change.operation == "DELETE":
            yield {"id": change.id, "_dlt_deleted": True}
        else:
            yield change.data
```

### 7. Integration with Dagster

When users ask about orchestration or Dagster integration:
- Show Dagster asset definitions for DLT pipelines
- Demonstrate scheduling and dependencies
- Explain materialization patterns
- Show monitoring and alerting setup

**Example code:**
```python
from dagster import asset, AssetExecutionContext
import dlt

@asset(group_name="github_data")
def github_issues_table(context: AssetExecutionContext):
    """Extract GitHub issues to DuckLake"""

    pipeline = dlt.pipeline(
        pipeline_name='github_pipeline',
        destination='ducklake',
        dataset_name='github_data'
    )

    info = pipeline.run(github_issues_source())

    context.log.info(f"Loaded {info.stats['loaded_packages']} packages")

    return info

@asset(group_name="github_data", deps=[github_issues_table])
def github_issues_summary(context: AssetExecutionContext):
    """Create summary table from raw issues"""

    import duckdb

    con = duckdb.connect()
    con.execute("""
        CREATE OR REPLACE TABLE github_issues_summary AS
        SELECT
            DATE_TRUNC('day', created_at) as date,
            state,
            COUNT(*) as issue_count,
            COUNT(DISTINCT author) as unique_authors
        FROM github_issues_table
        GROUP BY date, state
    """)

    return {"rows": con.execute("SELECT COUNT(*) FROM github_issues_summary").fetchone()[0]}
```

### 8. Stream-Batch Unification with Ibis

When users ask about batch/stream processing or Ibis:
- Explain how to write once, run on batch (DuckDB) and stream (RisingWave)
- Show Ibis abstraction layer
- Demonstrate semantic layer (BSL) for consistent metrics
- Explain deployment patterns

**Example code:**
```python
import ibis
from ibis import _

# Connect to DuckLake (batch)
con = ibis.duckdb.connect()
events = con.table("events")

# Define transformation (backend-agnostic)
daily_summary = (
    events
    .filter(_.timestamp >= "2024-01-01")
    .group_by([_.date.truncate("day").name("date"), _.event_type])
    .aggregate(
        event_count=_.count(),
        unique_users=_.user_id.nunique()
    )
)

# Execute on DuckDB (development/batch)
result_batch = daily_summary.execute()

# Same code can run on RisingWave (production/streaming)
# con_stream = ibis.risingwave.connect(...)
# result_stream = daily_summary.execute()
```

**Semantic Layer (BSL YAML):**
```yaml
metrics:
  - name: daily_active_users
    description: Count of unique users per day
    type: count_distinct
    sql: |
      SELECT COUNT(DISTINCT user_id)
      FROM events
      WHERE DATE_TRUNC('day', timestamp) = {{ date }}

  - name: event_rate
    description: Events per second
    type: gauge
    sql: |
      SELECT COUNT(*) / {{ time_window_seconds }}
      FROM events
      WHERE timestamp BETWEEN {{ start_time }} AND {{ end_time }}
```

### 9. DuckLake vs Iceberg/Delta Lake

When users ask about choosing between lakehouse formats:
- Explain DuckLake's lightweight positioning
- Compare features and trade-offs
- Recommend based on team size and requirements
- Show migration paths if needed

**Decision Framework:**

| Factor | DuckLake | Iceberg/Delta Lake |
|--------|----------|-------------------|
| **Team Size** | Small-medium (<50 users) | Large (>100 users) |
| **Complexity** | Low - simple setup | High - complex ecosystem |
| **Multi-Engine** | DuckDB-centric | Spark/Trino/Presto/many |
| **Catalog** | SQL database | REST catalog/Hive metastore |
| **Concurrency** | Moderate | Very high |
| **Operational Cost** | Low | High |
| **Format Maturity** | Newer | Industry standard |

**Use DuckLake When:**
✅ Small to medium team (<50 users)
✅ DuckDB-centric workflows
✅ Simplified operational overhead
✅ Cost-sensitive projects
✅ Embedded analytics scenarios
✅ Local-first development

**Use Iceberg When:**
✅ Large multi-engine environment (Spark, Trino, Presto)
✅ Very high concurrency (>100 concurrent writers)
✅ Industry-standard format requirement
✅ Complex schema evolution needs
✅ Multiple processing engines needed

**Hybrid Approach:**
```python
# DuckDB can query Iceberg tables (read-only)
import duckdb

con = duckdb.connect()
con.execute("INSTALL iceberg; LOAD iceberg;")

# Read Iceberg table
result = con.execute("""
    SELECT * FROM iceberg_scan('s3://bucket/iceberg-table')
    WHERE date >= '2024-01-01'
""").df()
```

### 10. Performance Optimization

When users report performance issues:
- Check if they're using Parquet (should be automatic with DuckLake)
- Verify catalog database performance (PostgreSQL tuning)
- Suggest partitioning strategies for large tables
- Show how to use EXPLAIN ANALYZE
- Recommend connection pooling

**Diagnostic Checklist:**

1. **File Format**: DuckLake uses Parquet automatically ✓
2. **Catalog Performance**: Is PostgreSQL properly tuned?
3. **Query Patterns**: Are they selecting only needed columns?
4. **Partitioning**: Are large tables partitioned by date/category?
5. **Connection Reuse**: Are they creating new connections per query?

**Optimization Examples:**

```sql
-- Profile query performance
EXPLAIN ANALYZE SELECT * FROM events WHERE date >= '2024-01-01';

-- Configure DuckDB memory
SET memory_limit = '8GB';
SET threads = 4;

-- Partition large tables for better performance
CREATE TABLE events_partitioned AS
SELECT * FROM events
PARTITION BY (DATE_TRUNC('month', date));

-- Use column projection (select only needed columns)
SELECT id, event_type, timestamp  -- Good
FROM events;

SELECT *  -- Avoid in production
FROM events;
```

**PostgreSQL Catalog Tuning:**
```sql
-- Tune PostgreSQL for DuckLake catalog
ALTER SYSTEM SET shared_buffers = '256MB';
ALTER SYSTEM SET work_mem = '16MB';
ALTER SYSTEM SET maintenance_work_mem = '128MB';
ALTER SYSTEM SET max_connections = 100;
SELECT pg_reload_conf();

-- Index for snapshot queries
CREATE INDEX idx_snapshots_table ON snapshots(table_name, snapshot_id);
```

## Common Integration Patterns

### Pattern 1: GitHub Data Pipeline

**Stack:** DLT + DuckLake + Cloudflare R2 + PostgreSQL

```python
import dlt
from dlt.sources.rest_api import rest_api_source

# Configure GitHub API source
github_source = rest_api_source({
    "client": {
        "base_url": "https://api.github.com/repos/owner/repo",
        "auth": {"token": "ghp_xxxxx"}
    },
    "resources": [
        {
            "name": "issues",
            "endpoint": {"path": "issues", "params": {"state": "all"}},
            "write_disposition": "merge",
            "primary_key": "id"
        }
    ]
})

# Load to DuckLake
pipeline = dlt.pipeline(
    pipeline_name='github_pipeline',
    destination='ducklake',
    dataset_name='github_data'
)

info = pipeline.run(github_source)
print(f"Loaded {info.stats['loaded_packages']} packages")
```

**Reference:** `/home/user/hackathon/research/md/consolidated/Building a GitHub "DuckLake" Pipeline with DLT, SQLMesh, and Cloudflare R2.md`

### Pattern 2: Incremental Indexing

**Stack:** DuckLake + CocoIndex + Dagster + Postgres LISTEN/NOTIFY

**Flow:**
1. DLT loads data to DuckLake (Postgres catalog)
2. Updates go to `documents_index` table
3. Postgres triggers fire LISTEN/NOTIFY events
4. CocoIndex picks up changes via subscription
5. Only changed documents re-indexed

```python
# Dagster asset for incremental indexing
@asset
def documents_table():
    """Load documents to DuckLake"""
    pipeline = dlt.pipeline(destination='ducklake')
    return pipeline.run(documents_source())

@asset(deps=[documents_table])
def documents_index():
    """Incrementally index only changed documents"""
    # CocoIndex listens to Postgres NOTIFY
    # Only processes changes since last run
    indexer.process_incremental()
```

**Reference:** `/home/user/hackathon/research/md/consolidated/Integrating DuckLake, CocoIndex, and Dagster for Incremental Updates.md`

### Pattern 3: Version Control with LakeFS

**Stack:** DuckLake + LakeFS + S3/R2

```python
import lakefs

# Create LakeFS branch for testing
branch = lakefs.create_branch("dev", source="main")

# Make changes on dev branch
con.execute("""
    INSERT INTO events
    SELECT * FROM new_data
""")

# Test changes
test_results = run_tests()

if test_results.passed:
    # Merge to main
    lakefs.merge(source="dev", destination="main")
else:
    # Discard changes
    lakefs.delete_branch("dev")
```

**Reference:** `/home/user/hackathon/research/md/consolidated/Integrating DuckLake, LakeFS, Lakekeeper, and OLake.md`

## Code Generation Guidelines

When generating code for DuckLake:

1. **Always use DLT for ETL** - It's the primary integration pattern
2. **Show complete examples** - Include pipeline config, credentials, execution
3. **Use proper write dispositions** - merge/append/replace based on use case
4. **Define primary keys** - Essential for merge operations
5. **Include error handling** - DLT pipelines can fail
6. **Show state management** - Incremental processing requires state
7. **Configure for environment** - Local dev vs production differences
8. **Add monitoring** - Log load stats, pipeline info

**Complete Example:**

```python
import dlt
from dlt.sources.rest_api import rest_api_source
import logging

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def load_github_data(repo: str, token: str):
    """
    Load GitHub repository data to DuckLake.

    Args:
        repo: Repository in format 'owner/name'
        token: GitHub personal access token

    Returns:
        LoadInfo with pipeline statistics
    """
    # Configure source
    source = rest_api_source({
        "client": {
            "base_url": f"https://api.github.com/repos/{repo}",
            "auth": {"token": token}
        },
        "resources": [
            {
                "name": "issues",
                "endpoint": {
                    "path": "issues",
                    "params": {"state": "all", "per_page": 100}
                },
                "write_disposition": "merge",
                "primary_key": "id"
            },
            {
                "name": "pull_requests",
                "endpoint": {
                    "path": "pulls",
                    "params": {"state": "all", "per_page": 100}
                },
                "write_disposition": "merge",
                "primary_key": "id"
            }
        ]
    })

    # Configure pipeline
    pipeline = dlt.pipeline(
        pipeline_name=f'github_{repo.replace("/", "_")}',
        destination='ducklake',
        dataset_name='github_data',
        progress="log"  # Show progress
    )

    try:
        # Run pipeline
        info = pipeline.run(source)

        # Log stats
        logger.info(f"Pipeline completed successfully")
        logger.info(f"Loaded packages: {info.stats.get('loaded_packages', 0)}")
        logger.info(f"Total rows: {info.stats.get('total_rows', 0)}")

        return info

    except Exception as e:
        logger.error(f"Pipeline failed: {e}")
        raise

# Usage
if __name__ == "__main__":
    info = load_github_data(
        repo="owner/repo",
        token="ghp_xxxxx"
    )
    print(f"Success! Loaded {info.stats['loaded_packages']} packages")
```

## Best Practices to Emphasize

1. **Use PostgreSQL Catalog for Production**: SQLite is only for local dev
2. **Always Define Primary Keys**: Required for merge operations
3. **Use DLT for ETL**: It handles state, incremental loading, schema evolution
4. **Leverage Time-Travel**: Query historical snapshots for audit/debug
5. **Partition Large Tables**: By date or category for query performance
6. **Monitor Catalog Database**: PostgreSQL performance affects DuckLake
7. **Use Incremental Loading**: Don't full-reload large datasets
8. **Test on Dev Catalog First**: Use separate catalog for testing
9. **Configure Cloudflare R2**: Zero egress costs for data lake storage
10. **Implement Retry Logic**: Handle concurrent write conflicts gracefully

## Troubleshooting Guide

### Issue: Concurrent Write Conflicts

```python
# Implement retry logic for conflicts
import time

def write_with_retry(con, sql, max_retries=3):
    for attempt in range(max_retries):
        try:
            con.execute(sql)
            return
        except duckdb.ConcurrentWriteException:
            if attempt < max_retries - 1:
                time.sleep(2 ** attempt)  # Exponential backoff
            else:
                raise
```

### Issue: Slow Catalog Queries

```sql
-- Check PostgreSQL catalog performance
SELECT
    schemaname,
    tablename,
    seq_scan,
    seq_tup_read,
    idx_scan,
    idx_tup_fetch
FROM pg_stat_user_tables
WHERE tablename LIKE 'ducklake_%'
ORDER BY seq_tup_read DESC;

-- Add indexes if needed
CREATE INDEX IF NOT EXISTS idx_snapshots_lookup
ON ducklake_snapshots(table_name, snapshot_id);
```

### Issue: DLT Pipeline Failures

```python
import dlt

# Enable detailed logging
import logging
logging.basicConfig(level=logging.DEBUG)

# Check pipeline state
pipeline = dlt.pipeline(pipeline_name='my_pipeline')
print(pipeline.state)

# Reset state if corrupted
pipeline.drop()

# Validate schema before load
info = pipeline.run(source, validate=True)
```

### Issue: R2 Connection Problems

```python
import duckdb

con = duckdb.connect()

# Load httpfs extension
con.execute("INSTALL httpfs; LOAD httpfs;")

# Configure R2 credentials
con.execute("""
    SET s3_endpoint = 'your-account.r2.cloudflarestorage.com';
    SET s3_access_key_id = 'your-r2-key';
    SET s3_secret_access_key = 'your-r2-secret';
    SET s3_region = 'auto';
    SET s3_url_style = 'path';
""")

# Test connection
result = con.execute("SELECT * FROM 's3://bucket/test.parquet' LIMIT 1").fetchall()
print(f"Connection successful: {result}")
```

## Quick Reference Commands

```python
# DLT Pipeline
pipeline = dlt.pipeline(
    pipeline_name='name',
    destination='ducklake',
    dataset_name='data'
)
info = pipeline.run(source)

# DuckDB Connection to DuckLake
con = duckdb.connect()
con.execute("""
    ATTACH 'ducklake:catalog.ducklake' AS catalog
    (TYPE POSTGRES,
     HOST 'localhost',
     DATABASE 'ducklake_db',
     STORAGE_PATH 's3://bucket/path');
""")
con.execute("USE catalog;")

# Time-Travel Query
con.execute("""
    SELECT * FROM table
    FOR SYSTEM_TIME AS OF '2024-01-01 00:00:00';
""")

# View Snapshots
con.execute("""
    SELECT * FROM information_schema.snapshots
    WHERE table_name = 'events';
""")

# Schema Evolution
con.execute("ALTER TABLE events ADD COLUMN new_field VARCHAR;")

# Export to Parquet
con.execute("""
    COPY (SELECT * FROM events)
    TO 's3://bucket/export.parquet' (FORMAT parquet);
""")
```

## Your Approach

When users invoke this skill:

1. **Understand the use case**: Are they building ETL, querying data, or managing schema?
2. **Ask clarifying questions**: Team size, concurrent users, data volume, cloud provider
3. **Provide complete, runnable examples**: Full pipeline code, not fragments
4. **Explain the "why"**: Why DuckLake vs Iceberg? Why PostgreSQL catalog?
5. **Show integration patterns**: DLT, Dagster, Ibis - how they work together
6. **Reference research materials**: Point to detailed docs for deep dives
7. **Offer optimization tips**: Partitioning, catalog tuning, incremental loading
8. **Consider their stack**: Local dev, cloud deployment, multi-user scenarios

Remember: You're not just answering questions, you're teaching modern lakehouse architecture and helping users build production-grade data pipelines with DuckLake's lightweight approach.

## KCG-Specific Patterns

The Cianfhoghlaim platform uses DuckDB + DuckLake in
production. These KCG-specific patterns are not in the generic
DuckDB/DuckLake upstream docs.

### DuckLake `ATTACH` (production)

```python
import duckdb

con = duckdb.connect()

# Production: attach DuckLake (MotherDuck + Garage S3 + Postgres catalog)
con.execute("INSTALL ducklake FROM core_nightly; LOAD ducklake;")
con.execute("""
    CREATE SECRET r2_secret (
        TYPE R2,
        KEY_ID '...',
        SECRET '...',
        ACCOUNT_ID '...'
    )
""")
con.execute("""
    ATTACH 'ducklake:md:cianfhoghlaim' AS oideachais (
        TYPE ducklake,
        SECRET r2_secret,
        CATALOG postgres_catalog
    )
""")
```

### MotherDuck connection string

```python
import duckdb
con = duckdb.connect("md:cianfhoghlaim")
# `md:cianfhoghlaim` is the MotherDuck database name;
# the MOTHERDUCK_TOKEN env var authenticates.
```

### KCG-cocoindex chunked Parquet writes

The `cocoindex/` Apps write to DuckLake in
ZSTD-compressed Parquet, with row group size tuned for HNSW
rebuild performance:

```python
# In a CocoIndex target mount
await lancedb.mount_table_target(
    LANCE_DB,
    table_name="chunks",
    table_schema=await lancedb.TableSchema.from_class(MyRecord, primary_key=["id"]),
    # ... 1024-d vectors, 100 row groups per fragment
)
```

### `stedding/ingest_queue/` reads

The KCG offline-fallback cache is at `stedding/ingest_queue/`.
Read partitioned Parquet via DuckDB's hive-partitioning
support:

```python
import duckdb
con = duckdb.connect()

df = con.execute("""
    SELECT * FROM read_parquet(
        'stedding/ingest_queue/**/*.parquet',
        hive_partitioning=true
    )
    WHERE source = 'ncca'
""").df()
```

### KCG-specific QUALIFY/ROW_NUMBER pattern (latest version)

The KCG `ireland/curriculum/` partitions are versioned
(by academic year). To get the "latest" version of each
curriculum area, use `QUALIFY`:

```sql
SELECT *
FROM cianfhoghlaim.education.ie.curriculum
QUALIFY ROW_NUMBER() OVER (
    PARTITION BY subject, curriculum_area
    ORDER BY academic_year DESC
) = 1;
```

### marimo + Polars round-trip

The marimo skill uses `duckdb.sql("...").pl()` to convert
DuckDB query results to Polars for downstream visualisation:

```python
import polars as pl

df: pl.DataFrame = mo.sql(
    "SELECT subject, COUNT(*) AS n FROM curriculum GROUP BY subject",
    engine=con,
    output=False,
)
mo.ui.table(df)
```

## Examples

See [`./examples/`](./examples/) for upstream DuckLake reference
notebooks (6 total). Highlights:

- `data_engineering_ducklake_duckdb.ipynb` — minimal DuckLake + DuckDB
- `data_engineering_ducklake_ibis.ipynb` — Ibis backend on DuckLake
- `data_engineering_ducklake_plotly.ipynb` — Plotly visualisations
- `data_engineering_ducklake_vega_altair.ipynb` — Vega-Altair charts
- `data_engineering_ducklake_pointblank.ipynb` — data validation
- `data_engineering_ducklake_mlflow_kafka_ducklake_notebooks_econ_comp.ipynb` — MLflow + Kafka streaming on DuckLake

## British-Isles Education pipeline — Canonical KCG pattern (post-v4)

The post-v4 lc6 pipeline (`openspec/changes/lc6-biep/`) uses
DuckLake as the **canonical BIEP sink**. The 24+ per-subject
tables (`6 subjects × 2 languages × 2 levels = 24 partitions`
per BAML extraction stage) all live in DuckLake under the
`cianfhoghlaim.leaving_cert.*` schema, plus the `gov.ie` circulars
in `cianfhoghlaim.education.ie.gov_circulars_archive`. The
canonical MotherDuck-DuckLake pattern is:

```python
import duckdb

con = duckdb.connect()

# Attach the DuckLake (MotherDuck managed) catalog
con.execute("INSTALL ducklake; LOAD ducklake;")
con.execute("""
    CREATE SECRET motherduck_secret (
        TYPE MOTHERDUCK,
        TOKEN '...from_infisical://dev-baile/cianfhoghlaim/MOTHERDUCK_TOKEN'
    )
""")
con.execute("""
    ATTACH 'ducklake:md:cianfhoghlaim' AS oideachais (
        TYPE ducklake,
        SECRET motherduck_secret,
        CATALOG postgres_catalog
    )
""")

# Now query the BIEP tables
df = con.execute("""
    SELECT subject, level, language, count(*) AS n_modules
    FROM cianfhoghlaim.leaving_cert.curriculum_syllabus
    WHERE subject IN (
        'mathematics', 'chemistry', 'geography',
        'gaeilge', 'english', 'computer_science'
    )
    GROUP BY subject, level, language
    ORDER BY subject, level, language
""").df()
```

The BIEP DuckLake catalog layout:

- **Schemas**: `cianfhoghlaim.leaving_cert` (LC subjects),
  `cianfhoghlaim.education.ie` (gov.ie circulars + NCCA raw).
- **Per-subject tables**:
  `cianfhoghlaim.leaving_cert.<subject>_<lang>_<level>.curriculum_syllabus`
  / `exam_paper_layout` / `marking_scheme_guideline` /
  `cross_linguistic_concept` / `syllabus_diagram`.
- **`gov.ie` circulars**:
  `cianfhoghlaim.education.ie.gov_circulars_archive` — populated
  by the `government_circulars` CocoIndex v1 App.

**British-Isles Education pipeline use case:**

- **24+1 DuckLake tables** for the BIEP curriculum layer
- **DuckLake 1.0 features** that the BIEP relies on:
  `set_sorted_by` for `curriculum_syllabus` (10× filter pushdown),
  `set_bucket_partition` for `marking_scheme_guideline` (per-topic
  distribution), `VARIANT` for `cross_linguistic_concept` rows
  (term mapping payload), `GEOMETRY` for the geospatial subject
  tables (Geography, in development).
- **Time-travel for syllabus versions** —
  `SELECT * FROM cianfhoghlaim.leaving_cert.mathematics_en_higher.curriculum_syllabus
  FOR SYSTEM_TIME AS OF '2026-06-01'` lets the marimo notebooks
  diff academic years.
- **Lakekeeper Iceberg shadow** — the same data is exposed as
  Iceberg to PyIceberg / Spark / Trino via the
  `cianfhoghlaim_lakekeeper:8181` REST catalog (see
  `iceberg-lakekeeper/SKILL.md`).

Cross-references:
- [`.agents/skills/dlt/SKILL.md`](../dlt/SKILL.md) — the DLT
  writers that populate the BIEP tables
- [`.agents/skills/motherduck/SKILL.md`](../motherduck/SKILL.md) —
  the 4 Dives
- [`.agents/skills/duckdb/SKILL.md`](../duckdb/SKILL.md) —
  the federated `lance_scan()` layer
- [`.agents/skills/cocoindex/SKILL.md`](../cocoindex/SKILL.md) —
  the 7 v1 Apps that produce the LanceDB companion tables
- [`.agents/skills/iceberg-lakekeeper/SKILL.md`](../iceberg-lakekeeper/SKILL.md) —
  the Iceberg shadow of the same data

## DuckLake 1.0 features (verified 2026-06-29, Agent 87)

- **Data inlining**: small (≤10 row) inserts stay in the catalog DB (default threshold = 10, was 100 in 0.x)
- **Sorted tables**: `ALTER TABLE t SET SORTED BY (col)` for filter pushdown
- **Bucket partitioning**: `ALTER TABLE t SET PARTITIONED BY (bucket(N, col))`
- **VARIANT type with shredding** (replaces JSON for semi-structured)
- **GEOMETRY type with bounding-box stats**
- **Experimental deletion vectors** (Iceberg V3 compatibility)
- **Explicit `AUTOMATIC_MIGRATION` opt-in** (was on by default in 0.x)

## DuckLake 1.0 ATTACH parameters (NEW)

`AUTOMATIC_MIGRATION`, `OVERRIDE_DATA_PATH`, `SNAPSHOT_TIME`, `SNAPSHOT_VERSION`,
`METADATA_CATALOG`, `METADATA_PATH`, `METADATA_SCHEMA`, `METADATA_PARAMETERS`, `ENCRYPTED`

## DuckLake 1.0 session-level SET options (NEW)

- `ducklake_default_data_inlining_row_limit` (default 10)
- `ducklake_max_retry_count` (default 10)
- `ducklake_retry_backoff` (default 1.5)
- `ducklake_retry_wait_ms` (default 100)
- `ducklake_write_deletion_vectors` (default false — experimental)

See also: `.agents/skills/iceberg-lakekeeper/SKILL.md` — Iceberg REST catalog backing
the same lakehouse-net Postgres that DuckLake reads. Use DuckLake for SQL-DDL-style
append/merge on the same data; use Iceberg REST + PyIceberg for v2/v3 features
(V3 Variant, soft-delete, undrop, vended creds, branch/tag).
