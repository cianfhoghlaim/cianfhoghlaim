# Data Versioning Reference

> Merged from 45 source files across `lakefs/` and `ducklake/` — Git-like data versioning for S3/lakehouses and DuckLake lakehouse on DuckDB.

---

# Part 1: DuckLake — Lakehouse on DuckDB


## DuckLake Overview


> Source: `docs/data_engineering/ducklake/README.md`

# DuckLake TPCH Demo

This project demonstrates generating TPCH data and managing it using **[DuckLake](https://ducklake.select/docs/stable/)**, a DuckDB extension that provides lakehouse capabilities.

## Prerequisites

- **DuckDB** 1.4.0+ (installed and in PATH) - Required for DuckLake extension
  ```bash
  curl https://install.motherduck.com | sh
  ```
- **Python 3.9+** - Required for data generation scripts
- **uv** (recommended) - Fast Python package installer:
  ```bash
  curl -LsSf https://astral.sh/uv/install.sh | sh
  ```

**Windows Users:** You will need to install `uv` per [the uv install page](https://docs.astral.sh/uv/getting-started/installation/#__tabbed_1_2) with PowerShell and then DuckDB from [the DuckDB install page](https://duckdb.org/install/?platform=windows&environment=cli) into `C:\Program Files\DuckDB`.

After installing `uv` and `duckdb`, ensure both are added to your PATH environment variable so they can be accessed from the command line.

Example using PowerShell (run as Administrator):
```powershell
# Add uv to PATH (adjust path if installed elsewhere)
$env:Path += ";$env:USERPROFILE\.cargo\bin"

# Add duckdb to PATH (adjust path if installed elsewhere)
$env:Path += ";C:\Program Files\DuckDB"

# Make the changes permanent for current user
[Environment]::SetEnvironmentVariable("Path", $env:Path, [EnvironmentVariableTarget]::User)
```

Dependencies are automatically installed via `uv` when running Python scripts:
- `tpchgen-cli` - TPCH data generator
- `pyyaml` - YAML configuration parsing
- `duckdb` - DuckDB Python package

## Quick Start

### Using Makefile (Unix/macOS)

```bash
make tpch                 # Generate TPCH data - MUST DO THIS FIRST!
make catalog              # Initialize DuckLake catalog
make repartition          # Load data into DuckLake partitioned table
make verify               # Verify row counts
make manifest             # Create snapshot
...
```

**Run everything in sequence:**
```bash
make run                  # Execute all steps from tpch to clean
```

### Using DuckDB CLI Directly (Windows/All Platforms)

```bash
uv run python scripts/00_generate_data.py
duckdb -f scripts/01_bootstrap_catalog.sql
duckdb -f scripts/02_repartition_orders.sql
duckdb -f scripts/03_verify_counts.sql
duckdb -f scripts/04_make_manifest.sql
...
```

## Project Structure

```
ducklake-tpch/
  config/
    tpch.yaml                  # Configuration for TPCH generation
  catalog/
    ducklake.ducklake           # DuckLake catalog database (contains all metadata)
  data/
    tpch/                       # Raw TPCH Parquet files (by table)
      orders/
      lineitem/
    lake/                       # DuckLake managed partitioned data
      orders/                   # Partitioned by year/month/day
      lineitem/                 # Partitioned by year
  scripts/
    00_generate_data.py         # TPCH data generation script
    01_bootstrap_catalog.sql    # Initialize DuckLake catalog
    02_repartition_orders.sql   # Load data into partitioned table
    03_verify_counts.sql        # Verify row counts
    04_make_manifest.sql        # Create snapshot
    05_load_small_files.py      # Load files one at a time
    06_compaction.sql            # Compact files
    07_time_travel.sql          # Time travel queries
    08_change_feed.sql          # Change feed analysis
    09_expire_snapshots.sql     # Expire old snapshots
    10_clean.py                 # Remove all generated data
  Makefile                      # Convenience wrapper (Unix/macOS)
```

## Available Commands

### Using Makefile (Unix/macOS)

```bash
make help                  # Show all available commands
make tpch                  # Generate TPCH data
make catalog               # Initialize DuckLake catalog
make repartition           # Repartition orders table
make verify                # Verify row counts
make manifest              # Create snapshot
make load-small-files      # Load files one at a time
make compact               # Compact files (default: lineitem)
make time-travel           # Demonstrate time travel queries
make change-feed           # Show changes between snapshots
make expire-snapshots      # Expire old snapshots
make clean                 # Remove all generated data
make run                   # Run all steps in sequence
```

### Using DuckDB CLI Directly (All Platforms)

**Basic Commands:**
```bash
# Initialize catalog
duckdb -f scripts/01_bootstrap_catalog.sql

# Repartition orders table
duckdb -f scripts/02_repartition_orders.sql

# Verify row counts
duckdb -f scripts/03_verify_counts.sql

# Create snapshot
duckdb -f scripts/04_make_manifest.sql

# Time travel queries
duckdb -f scripts/07_time_travel.sql

# Change feed analysis
duckdb -f scripts/08_change_feed.sql

# Compact files (default: lineitem)
duckdb -f scripts/06_compaction.sql

# Compact specific table
duckdb -c "SET VARIABLE table_name = 'orders';" -f scripts/06_compaction.sql

# Expire snapshots (default: 1 minute)
duckdb -f scripts/09_expire_snapshots.sql

# Expire snapshots older than 7 days
duckdb -c "SET VARIABLE older_than = INTERVAL '7 days';" -f scripts/09_expire_snapshots.sql
```

### Python Scripts (All Platforms)

```bash
# Generate TPCH data
uv run python scripts/00_generate_data.py

# Generate specific part
uv run python scripts/00_generate_data.py --part 1

# Load files one at a time (default: lineitem)
uv run python scripts/05_load_small_files.py

# Load files for specific table
uv run python scripts/05_load_small_files.py --table orders

# Clean up all generated data
uv run python scripts/10_clean.py
```

## Exploring DuckLake

Connect to DuckDB and explore DuckLake features:

```bash
# Initialize catalog and explore metadata
duckdb -f scripts/01_bootstrap_catalog.sql

# Query partitioned orders table
duckdb -f scripts/03_verify_counts.sql

# Time travel queries
duckdb -f scripts/07_time_travel.sql

# Change feed analysis
duckdb -f scripts/08_change_feed.sql

# Explore snapshots and metadata
duckdb -f scripts/04_make_manifest.sql
```

All SQL scripts connect to the DuckLake catalog automatically. The metadata tables (`__ducklake_metadata_lake.ducklake_snapshot`, `__ducklake_metadata_lake.ducklake_data_file`, etc.) are accessible within each script.

## DuckLake Features Demonstrated

- **Zero-Copy File Registration**: Uses `ducklake_add_data_files` to register existing Parquet files without copying
- **Partitioning**: Automatic Hive-style partitioning (`year=YYYY/month=MM/day=DD`)
- **Snapshots**: Time-travel queries via `CREATE SNAPSHOT` and `AT (VERSION => N)`
- **Metadata Storage**: All metadata in DuckLake catalog database - no external manifest files
- **File Compaction**: Merge adjacent files to improve query performance
- **Change Data Capture**: Identify insertions and deletions between snapshots
- **Snapshot Expiration**: Clean up old snapshots and orphaned files

## Scripts

All scripts are numbered sequentially in `scripts/` directory:

### Python Scripts
- `00_generate_data.py` - Generate TPCH data using tpchgen-cli
- `05_load_small_files.py` - Load Parquet files one at a time to create small files
- `10_clean.py` - Remove all generated data and catalog

### SQL Scripts
- `01_bootstrap_catalog.sql` - Initialize DuckLake catalog and register files
- `02_repartition_orders.sql` - Load data into partitioned orders table
- `03_verify_counts.sql` - Verify row counts match
- `04_make_manifest.sql` - Create snapshot and show metadata
- `06_compaction.sql` - Compact small files (uses `table_name` variable)
- `07_time_travel.sql` - Demonstrate time travel queries
- `08_change_feed.sql` - Show changes between snapshots
- `09_expire_snapshots.sql` - Expire old snapshots (uses `older_than` variable)

All SQL files are executable directly via `duckdb -f scripts/XX_script.sql`

## Cross-Platform Support

- **Unix/macOS**: Use `make` commands for convenience
- **Windows**: Use `duckdb -f scripts/file.sql` directly
- **All Platforms**: Python scripts work everywhere via `uv run python`

## Configuration (Optional)

Edit `config/tpch.yaml` or set environment variables:
- `TPCH_SCALE`: Scale factor (default: 10)
- `TPCH_PARTS`: Number of parts to generate (default: 100)
- `TPCH_TABLES`: Comma-separated list of tables (default: orders,lineitem)

## Troubleshooting

**DuckDB not found:**
```bash
# Install DuckDB (macOS)
curl https://install.motherduck.com | sh

# Or download from https://duckdb.org/docs/installation/
```

**DuckLake extension not available:**
- Ensure DuckDB 1.4.0+ is installed
- Check extension is installed: `duckdb -c "INSTALL ducklake; LOAD ducklake;"`

**Python dependencies:**
```bash
# Install dependencies
uv sync

# Verify installation
uv run python scripts/00_generate_data.py --help
```


> Source: `docs/data_engineering/ducklake/ducklake.md`

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

**Key Insight:** DuckLake separates metadata (SQL database) from data (Parquet files), enabling collaborative data lake scenarios without complex infrastructure.

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


## DuckLake KCG Summary


> Source: `docs/data_engineering/ducklake/KCG_SUMMARY.md`

# DuckLake — KCG Summary

## What It Is
DuckLake is a DuckDB extension providing lakehouse capabilities: zero-copy file registration, ACID snapshots, time-travel queries, change data capture, and file compaction — all without external manifest files. This directory contains the DuckLake TPCH demo (10-script end-to-end lakehouse workflow), a DuckLake + SQLMesh tutorial for building a modern data lakehouse on a laptop, and an MLflow + Kafka + DuckLake pipeline for streaming ML telemetry to a lakehouse.

## Why This Matters for Kings' College Galway
DuckLake is the lakehouse layer for the oideachais platform, providing ACID guarantees over curriculum data stored on Garage S3. The zero-copy file registration pattern directly maps to DLT's filesystem pipeline output — curriculum Parquet files are registered into DuckLake without data duplication. The time-travel and CDC features enable curriculum version auditing across academic years. The DuckLake → MotherDuck pattern provides the local-to-cloud workflow for development on bunchloch and production on MotherDuck.

## Key Patterns Preserved
6 .md files remain:
- `README.md` — Full DuckLake TPCH demo documentation: catalog bootstrap, partitioning, snapshots, compaction, time travel, CDC, expiration
- `ducklake.md` — DuckLake concept reference
- `DuckLake + SQLMesh Tutorial_ Build a Modern Data Lakehouse On Your Laptop.md` — DuckLake + SQLMesh integration walkthrough
- `DuckLake to MotherDuck_ Validate locally, deploy to cloud in minutes.md` — Local-to-cloud deployment pattern
- `mlflow_kafka_ducklake/README.md` + CHANGELOG — MLflow + Kafka streaming to DuckLake

## Source Files
Full source removed (2026-06-06). Available at https://github.com/ducklake/ducklake

## What Was Removed
Python scripts (.py), SQL scripts (.sql), Makefile, YAML configs, lock files, .gitignore, README without .md extension


## DuckLake Tutorials & Guides


> Source: `docs/data_engineering/ducklake/DuckLake + SQLMesh Tutorial_ Build a Modern Data Lakehouse On Your Laptop.md`

---
title: "DuckLake + SQLMesh Tutorial: Build a Modern Data Lakehouse On Your Laptop"
source: "https://www.tobikodata.com/blog/ducklake-sqlmesh-tutorial-a-hands-on"
author:
published:
created: 2025-12-11
description: "DuckLake brings lakehouse capabilities to DuckDB, providing ACID transactions and time travel on your data lake. SQLMesh adds sophisticated transformation management with incremental processing. Together, they create a powerful, open source lakehouse for the post-modern data era."
tags:
  - "clippings"
---
DuckLake brings lakehouse capabilities to DuckDB, providing ACID transactions and time travel on your data lake. SQLMesh adds sophisticated transformation management with incremental processing. Together, they create a powerful, open source lakehouse for the post-modern data era.

## Building an Open Lakehouse with DuckLake and SQLMesh: A Practical Guide

*In this tutorial, we’ll create a small data lakehouse on your laptop, ingesting a CSV of e-commerce events and producing a daily revenue report using DuckLake’s ACID-compliant table format and SQLMesh’s incremental pipeline.*

## Part 1: The Stack

In the post-modern data stack, separating storage, metadata, and compute is essential for flexibility and scalability. This architecture enables you to leverage best-in-class open-source components.

### What is an Open Table Format?

A data lake (like S3 or local storage) is excellent at storing raw files but lacks organization, transaction support, and schema enforcement. An Open Table Format (like DuckLake, Apache Iceberg, or Delta Lake) sits on top of the data file format (Parquet) and organizes the files as a table. It defines how data files are organized and provides a metadata layer that tracks which files belong to which table version, enabling critical data warehouse-like functionality.

### The Table Format - Ducklake

[DuckLake](https://ducklake.select/) is an open table format. It is not a storage system. Instead, it organizes data stored in Parquet files on your object storage and maintains metadata. DuckLake acts like a metadata catalog for your object storage.

As a result, DuckLake provides:

- ACID Transactions: Ensures data integrity during writes.
- Time Travel: Allows querying historical versions of a table.
- Schema Enforcement: Ensures data adheres to the defined structure.

### The Compute and State Storage - DuckDB

DuckDB is a fast, in-process analytical database engine. In this stack, DuckDB serves as the compute engine. It reads the DuckLake metadata, understands the table structure, and executes the SQL queries against the underlying Parquet files.

### The Transformation & Orchestration Layer - SQLMesh

[SQLMesh](https://sqlmesh.com/) is a next-generation data transformation framework. It serves as the orchestration and transformation layer. SQLMesh defines the data pipeline logic, manages model dependencies, and ensures data correctness through features like audits, tests, state management, and Virtual Data Environments.

### How They Work Together

In this scenario, SQLMesh defines the transformation logic and orchestrates the pipeline. SQLMesh stores project metadata and state information in DuckDB. SQLMesh instructs DuckDB (the compute engine) to execute the transformations. DuckDB reads and writes data to your object storage (local Parquet files in this case), organized using the DuckLake table format (the metadata layer).

1. Storage Layer (Object Storage): This is where your actual data lives (e.g., a local directory or an S3 bucket). Data is stored here as local Apache Parquet files.
2. Metadata Layer (DuckLake Table Format): DuckLake organizes the storage layer. It uses a Catalog Database (which can be a DuckDB file, PostgreSQL, or MySQL) to store metadata, like schemas, table versions, and pointers to the Parquet files in the storage layer.
3. Compute Layer (DuckDB): The engine that performs the actual data processing. It reads the DuckLake metadata to locate the correct Parquet files and executes the queries.
4. Orchestration Layer (SQLMesh): Manages the pipeline logic and execution sequence using cron.
5. SQLMesh State Management (Separate State DuckDB Database): SQLMesh needs to track its own execution state (which models have run, time intervals processed, etc.). This requires frequent UPDATE operations. To maintain efficiency, we configure a separate database (e.g., another local DuckDB file) specifically for SQLMesh's internal state, separate from the DuckLake catalog.

Note - DuckLake tables do not currently support `UPDATE ` statements so SQLMesh cannot store its state in a DuckLake-managed table. The state database (`data/sqlmesh_state.db`) is a regular DuckDB database used by SQLMesh for tracking job state, while `catalog.ducklake` is a DuckLake-format database used **only** for the data's metadata. This separation improves efficiency (avoids contention with frequent state updates) but is functionally necessary given DuckLake’s current design.

## Prerequisites and Environment Setup

Ensure you have Python 3.8 or higher installed.

### Create Your Project Structure

Let's set up a standard SQLMesh project directory.

```javascript
mkdir ducklake-sqlmesh-tutorial
cd ducklake-sqlmesh-tutorial
```

### Set Up a Python Virtual Environment

Isolate your project dependencies.

```javascript
python3 -m venv .venv

source .venv/bin/activate  # On macOS/Linux

.venv/Scripts/activate  # On Windows
```

### Install Required Packages

Install SQLMesh with DuckDB support. The DuckLake extension is included in recent DuckDB versions.

`pip install 'sqlmesh[lsp,duckdb]'`

### Download the VS Code Extension, Initialize the SQLMesh Project

Download the official SQLMesh VS Code extension from the Extensions: Marketplace

![](https://cdn.prod.website-files.com/67f7cdf0feddc96ca194ff33/6895060ef814c3a3c416cc30_AD_4nXdxY2Lyr5I44yaJ7f4dJD7nvQEFQ-zF_UA8cUA5iDToE5DNqc3ONtVlJujHHEWVzCg5CzKxX-tv-XaLSJlJYiTc9kgB0NtFjA_us8hwq45oHca_LPetwEDj_iwyt0UQ9iZFZj-88A.png)

Select your Python interpreter (you may need to use “Ctrl + P” or “Ctrl + Shift + P” to access the developer menu in VS Code):

![](https://cdn.prod.website-files.com/67f7cdf0feddc96ca194ff33/6895060ef814c3a3c416cc37_AD_4nXfZlzFFfJrXXGEfgYsvn9ErGAYYquCbKrOuC6pKlMZwjYSnFKLxXo8lf_T2sTN0yrkFq_CrZx1iLv92ZU-P6zVqT8fPMRtXpnnHOXMzwiak4jGPahvDt-4d02ggyBK4Kwv3s2Cz7A.png)

Reload your windows:

![](https://cdn.prod.website-files.com/67f7cdf0feddc96ca194ff33/6895060ef814c3a3c416cc3a_AD_4nXfxXUn0H601c4Lvssh7VA3kJglbRZXekPPMTvJX97WXY7uA1FmNuwxf1u4H8NXuBDssU4QlsCg0vPIDDiTJBc4JObsEK_0yFfLqTe8LycnshD9LkXxaVJcgr3QfYXe6OYLRS6iTMg.png)

Initialize the SQLMesh Project and build the project scaffolding. In your terminal:

```javascript
sqlmesh init
──────────────────────────────Welcome to SQLMesh!──────────────────────────────‍
What type of project do you want to set up?‍    
[1]  DEFAULT - Create SQLMesh example project models and files    
[2]  dbt     - You have an existing dbt project and want to run it with SQLMesh    
[3]  EMPTY   - Create a SQLMesh configuration file and project directories only‍
Enter a number: 3‍
──────────────────────────────‍
Choose your SQL engine:‍    
[1]  DuckDB     
[2]  Snowflake     
[3]  Databricks     
[4]  BigQuery     
[5]  MotherDuck     
[6]  ClickHouse     
[7]  Redshift     
[8]  Spark     
[9]  Trino     
[10] Azure SQL     
[11] MSSQL    
[12] Postgres    
[13] GCP Postgres    
[14] MySQL    
[15] Athena    
[16] RisingWave‍
Enter a number: 1‍
──────────────────────────────‍
Choose your SQLMesh CLI experience:‍    
[1]  DEFAULT - See and control every detail    
[2]  FLOW    - Automatically run changes and show summary output‍
Enter a number: 1‍
──────────────────────────────‍
Your SQLMesh project is ready!
```

Add a `data/storage` folder to the project. This will hold the Parquet files as well as the DuckLake metadata and SQLMesh State databases.

`mkdir -p data/storage #mac/linux`

`md data\storage #Windows PowerShell`

You should see your SQLMesh project scaffolded in your File Explorer window:

![](https://cdn.prod.website-files.com/67f7cdf0feddc96ca194ff33/6895060ef814c3a3c416cc34_AD_4nXf50A3w_OCt5RTGCotVMkslKi0Mc8OU9e1pP6C-rTTQJ2StPMhWKkOl9dYWCOsz-zddDL6EVYnVC6kxZufL79CugW_OAIDjYpnl7bp4GcHMMBDznUHjnNjYzBH-q5aw8G8jla8x-w.png)

## Configure the Project

We will use DuckDB as the engine (and state database) and define how DuckDB should interact with the DuckLake table format.

Create a file named config.yaml in your project root:

```javascript
# Define the connections
gateways:
  local_gateway:
    connection:
      # DuckDB is the compute engine
      type: duckdb

      # Define how DuckDB interacts with the storage and format
      catalogs:
        # The name we will use to reference this database
        my_lakehouse:
          # Specify the table format
          type: ducklake

          # Metadata Path (The Catalog Database): Where DuckLake stores table versions.
          # In this local example, we use a DuckDB file for the catalog.
          path: data/catalog.ducklake

          # Data Path (The Object Storage): Where the actual Parquet files are stored.
          data_path: data/storage/

      # Ensure the ducklake extension is automatically loaded by DuckDB
      extensions:
        - ducklake
    state_connection:
      # State connection for SQLMesh to track model states
      type: duckdb
      database: 'data/sqlmesh_state.db'
# Set the default gateway
default_gateway: local_gateway

# Default settings for models
model_defaults:
  dialect: duckdb
  start: '2024-01-01'
```

### Understanding the Configuration

- `connection.type: duckdb`: Sets DuckDB as the compute engine.
- `catalogs.my_lakehouse`: Defines a database connection named my\_lakehouse.  
	- `type: ducklake`: Tells the DuckDB engine to use the DuckLake table format for this connection.
	- `path`: The location of the DuckLake Catalog Database (metadata storage).
	- `data_path`: The location of the Object Storage (Parquet file storage).
- `state_connection`: A separate DuckDB file dedicated to tracking SQLMesh's internal execution state.

## Install DuckLake

We attach the DuckLake catalog to specify where metadata will be stored and link it to our data directory. This registers the `data_path` in the DuckLake metastore, so DuckDB knows where to write Parquet files.

```javascript
#log into duckdb cli
duckdb data/storage/sqlmesh_state.db‍

#install ducklake
INSTALL ducklake;‍

#attach ducklake to the db
ATTACH 'ducklake:data/catalog.ducklake' AS my_ducklake (DATA_PATH 'data/storage/');
USE my_ducklake;‍

#exit duckdb
.exit
```

Test your configuration. If there are no errors, then you are good to go!

`sqlmesh migrate`

## Building the Pipeline

Now that our environment is ready, let’s set up a simple pipeline. We’ll use a small CSV of raw e-commerce events as our source data, then create a staging view to clean the data, and finally an incremental model to aggregate daily revenue.

### Sample Data

Create ` seeds/raw_events.csv`:

```javascript
event_id,user_id,event_type,event_timestamp,revenue
1,101,page_view,2024-01-01 10:00:00,0
2,101,purchase,2024-01-01 10:10:00,29.99
3,102,page_view,2024-01-01 11:00:00,0
4,103,page_view,2024-01-02 09:00:00,0
5,103,purchase,2024-01-02 09:08:00,29.99
```

### Define the Seed Model

A SEED model tells SQLMesh how to load the CSV data.

Create `models/raw_events.sql`:

```javascript
MODEL (
    name raw.events,
    kind SEED (
        path '../seeds/raw_events.csv'
    ),
    columns (
        event_id INT,
        user_id INT,
        event_type TEXT,
        event_timestamp TIMESTAMP,
        revenue DECIMAL(10,2)
    )
);
```

### Define the Staging Model

A staging model cleans and standardizes the raw data.

Create `models/stg_events.sql`:

```javascript
MODEL (
    name staging.stg_events,
    kind VIEW
);

SELECT
    event_id,
    user_id,
    event_type,
    event_timestamp,
    -- Extract date for incremental processing
    DATE(event_timestamp) as event_date,
    revenue
FROM
    raw.events
WHERE
    event_id IS NOT NULL;
```

### Define the Incremental Model

This model aggregates data into a daily summary. We use `INCREMENTAL_BY_TIME_RANGE` so that SQLMesh only processes new days as they arrive.

Create `models/daily_revenue.sql`:

```javascript
MODEL (
    name analytics.daily_revenue,
    kind INCREMENTAL_BY_TIME_RANGE (
        time_column event_date,
        lookback 2,
        partition_by_time_column TRUE
    ),
    start '2024-01-01',
    cron '@daily',
    allow_partials TRUE,
    interval_unit 'day',
    grain event_date
);

SELECT
    event_date,
    COUNT(DISTINCT user_id) as unique_users,
    COALESCE(SUM(CASE WHEN event_type = 'purchase' THEN revenue END), 0) as total_revenue
FROM
    staging.stg_events
WHERE
    event_date >= @start_ds
    AND event_date < @end_ds
GROUP BY
    event_date;
```

**Note:** In our `analytics.daily_revenue` model, the `INCREMENTAL_BY_TIME_RANGE` config handles **what data to recompute** (new daily partitions, with a 2-day lookback), while `partition_by_time_column=TRUE ` controls **how the output is stored** on disk (one folder per event\_date). Incremental processing is about efficiency in recomputation, and partitioning is about efficient data layout.

### The SQL Query Explained

The SQL query defines the business logic for the transformation:

```javascript
SELECT
    event_date,
    COUNT(DISTINCT user_id) as unique_users,
    COALESCE(SUM(CASE WHEN event_type = 'purchase' THEN revenue END), 0) as total_revenue
FROM
    staging.stg_events
WHERE
    event_date >= @start_ds
    AND event_date < @end_ds
GROUP BY
    event_date;
```

The most critical part of this query for an incremental model is the WHERE clause:

- `WHERE event_date >= @start_ds AND event_date < @end_ds`: This is where the magic of incremental processing happens. `@start_ds` and `@end_ds` are special macros that SQLMesh automatically replaces with the start and end dates of the specific interval it is processing.
	- For example, when the daily cron job runs on the morning of January 4th to process data for January 3rd, SQLMesh will render the query with `WHERE event_date >= '2024-01-03' AND event_date < '2024-01-04'`.
	- This ensures that on each run, the query only scans and computes data for a single day from the upstream `staging.stg_events` model, making the process incredibly fast and cost-effective.

### Putting It All Together

Here’s how it all works together:

1. Scheduled Run: The `@daily` cron schedule triggers a run.
2. Interval Calculation: SQLMesh determines the next interval to process (e.g., `2024-01-03`). It also considers the lookback of `2`, adding the previous two days (`2024-01-01, 2024-01-02`) to the processing plan to account for late data.
3. Query Execution: For each of these daily intervals, SQLMesh executes your SQL query, substituting `@start_ds` and `@end_ds` with the correct dates.
4. Efficient Deletes and Inserts: For the intervals being reprocessed (the lookback), SQLMesh first runs a `DELETE ` statement on the target table for those specific dates. It then runs an `INSERT ` statement to load the newly computed data for all processed intervals.
5. Partitioned Writes: Because we've specified `partition_by_time_column`, the newly inserted data is written to the correct physical directory on disk (e.g.,` .../event_date=2024-01-03/`), keeping your data lake organized and fast to query.

Using the `LINEAGE ` tab, powered by the SQLMesh VS Code extension, you can see the project’s column-level lineage.

![](https://cdn.prod.website-files.com/67f7cdf0feddc96ca194ff33/6895060ef814c3a3c416cc40_AD_4nXdReOaw8Tx3DpVmhFKJkN4acuIZ-BGkp0uFduSWd2m8Sry7e-xurSXc8oaXtY3qik4q4O-z_aT9P3vFg9kODLMrzB7G6bONwQJSum03_SxQb8nw3cbjxwAkjniBwuOp_q2m0gNv1g.png)

## Running and Verifying the Pipeline

### Plan/Apply the Changes

Run the plan command. SQLMesh compares the current state to the desired state defined by your models.

```javascript
sqlmesh plan dev

\`dev\` environment will be initialized

Models:
└── Added:
    ├── analytics__dev.daily_revenue
    ├── raw__dev.events
    └── staging__dev.stg_events
Models needing backfill:
├── analytics__dev.daily_revenue: [2024-01-01 - 2025-08-05]
├── raw__dev.events: [full refresh]
└── staging__dev.stg_events: [recreate view]
Apply - Backfill Tables [y/n]: y

Updating physical layer ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 100.0% • 3/3 • 0:00:00

✔ Physical layer updated

[1/1] raw__dev.events                [insert seed file]                 0.01s
[1/1] staging__dev.stg_events        [recreate view]                    0.04s
[1/1] analytics__dev.daily_revenue   [insert 2024-01-01 - 2025-08-05]   0.04s
Executing model batches ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 100.0% • 3/3 • 0:00:00

✔ Model batches executed

Updating virtual layer  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 100.0% • 3/3 • 0:00:00

✔ Virtual layer updated
```

SQLMesh will identify that all models need to be created and backfilled for the time range present in the data.

Type `y ` and press `Enter ` to apply the plan.

### What Exactly Happened?

1. SQLMesh initialized its tracking database (`data/sqlmesh_state.db`) and recorded the new models.
2. DuckDB (the compute engine) created the physical tables for our models.
3. DuckDB, using DuckLake, created a **catalog file** (`data/catalog.ducklake`) to store table metadata (versions, schemas).
4. DuckDB wrote the raw and transformed data as Parquet files in `data/storage/`, partitioned by date.
5. DuckLake’s metadata was updated to point to all the new Parquet files that form the current table versions.

If you explore the `data/storage/` directory, you will now see the actual data stored as Parquet files, organized by the DuckLake format.

![](https://cdn.prod.website-files.com/67f7cdf0feddc96ca194ff33/68950bcfe8e0547ef6555d5b_Screenshot%202025-08-07%20132531.png)

### Verify the Data

You can verify the results using SQLMesh's `fetchdf ` command.

Notice the model names like ` raw__dev.events`, SQLMesh automatically creates a dev version of each model (with a ` __dev` suffix) in our DuckLake catalog. This is part of SQLMesh’s [**Virtual Data Environments**](https://www.tobikodata.com/blog/virtual-data-environments) feature: the `dev ` environment data is isolated from `prod.`

`sqlmesh fetchdf "SELECT * FROM analytics__dev.daily_revenue ORDER BY event_date"`

You will see the following output:

```javascript
event_date  unique_users  total_revenue
0  2024-01-01             2          29.99
1  2024-01-02             1          29.99
```

### Load the Data Into Prod

Follow the same process to do the initial Plan/Apply for the prod environment:

`sqlmesh plan`

`Apply - Backfill Tables [y/n]: Y`

Notice that only the virtual layer was updated when you promoted the project to prod. The physical changes are executed in the development environments. When updates are promoted to production, the production view modifies it’s pointer to point to the most recent physical table, which was generated during `sqlmesh plan dev`. This virtual data environment development process enables seamless deployment across environments because only the underlying table pointer is updated, keeping the production table view name unchanged. Downstream users will have uninterrupted access when production views are updated to the most recently physical table.

## Incremental Processing

State management is a strength of SQLMesh. Understanding e enables SQLMesh to process incremental models efficiently by only processing new data, and prevent data leakage by capturing late-arriving rows.

### Add New Data

Append the following lines to `seeds/raw_events.csv`. This adds data for two new days. Change the dates to correspond with 2 days before the UTC day that you are running this tutorial so that the data is captured in the incremental model lookback.

```javascript
6,104,page_view,2025-08-05 14:00:00,0
7,104,purchase,2025-08-06 14:15:00,49.99
```

### Rerun the Pipeline

Run the plan again to add any changes to our dev environment.

```javascript
sqlmesh plan dev

Differences from the \`dev\` environment:

Models:
├── Directly Modified:
│   └── raw__dev.events
└── Indirectly Modified:
    ├── staging__dev.stg_events
    └── analytics__dev.daily_revenue
Models needing backfill:
├── analytics__dev.daily_revenue: [2024-01-01 - 2025-08-05]
├── raw__dev.events: [full refresh]
└── staging__dev.stg_events: [recreate view]
Apply - Backfill Tables [y/n]: y

Updating physical layer ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 100.0% • 3/3 • 0:00:00

✔ Physical layer updated

[1/1] raw__dev.events                [insert seed file]                 0.01s
[1/1] staging__dev.stg_events        [recreate view]                    0.05s
[1/1] analytics__dev.daily_revenue   [insert 2024-01-01 - 2025-08-05]   0.04s
Executing model batches ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 100.0% • 3/3 • 0:00:00

✔ Model batches executed

Updating virtual layer  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 100.0% • 3/3 • 0:00:00

✔ Virtual layer updated
```

We can clearly see how `dev ` has two extra rows that `prod ` doesn’t (the new dates) by using SQLMesh’s `table_diff ` feature:

```javascript
sqlmesh table_diff prod:dev analytics.daily_revenue --show-sample

Models to compare:
└── analytics.daily_revenue

Calculating model differences ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 100.0% • 1/1 • 0:00:00

Table diff completed successfully!

Table Diff
├── Model:
│   └── analytics.daily_revenue
├── Environment:
│   ├── Source: prod
│   └── Target: dev
├── Tables:
│   ├── Source: my_lakehouse.analytics.daily_revenue
│   └── Target: my_lakehouse.analytics__dev.daily_revenue
└── Join On:
    └── event_date

Schema Diff Between 'PROD' and 'DEV' environments for model 'analytics.daily_revenue':
└── Schemas match

Row Counts:
├──  FULL MATCH: 2 rows (66.67%)
└──  DEV ONLY: 2 rows (33.33%)

COMMON ROWS column comparison stats:
               pct_match
unique_users       100.0
total_revenue      100.0

COMMON ROWS sample data differences:
  All joined rows match

DEV ONLY sample rows:
event_date  unique_users  total_revenue
2025-08-05             1           0.00
2025-08-06             1          49.99
```

SQLMesh compared the data across the prod and dev environments for the `analytics.daily_revenue` table. The diff shows 2 rows exist only in `dev ` (33% of rows), corresponding to the new dates we added, while all other rows match 100%. This confirms that prod hasn’t processed the new data yet.

Let’s run our incremental model in prod to capture the new data. We use `sqlmesh run --ignore-cron` to force an immediate run of the incremental model in `prod`, rather than waiting for the cron schedule. This processes the new data for the latest dates right now.

```javascript
sqlmesh run --ignore-cron
[1/1] analytics.daily_revenue   [insert 2025-08-05 - 2025-08-07]   0.15s
Executing model batches ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 100.0% • 1/1 • 0:00:00

✔ Model batches executed

Run finished for environment 'prod'
```

Our model processed the new data for today (August 7, 2025 as of this writing), and the 2 day lookback.

Let’s promote any changes that we made to the project in dev to our prod environment.

```javascript
sqlmesh plan

Differences from the \`prod\` environment:

Models:
├── Directly Modified:
│   └── raw.events
└── Indirectly Modified:
    ├── analytics.daily_revenue
    └── staging.stg_events
Apply - Virtual Update [y/n]: y

SKIP: No physical layer updates to perform

SKIP: No model batches to execute

Updating virtual layer  ━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━ 100.0% • 3/3 • 0:00:00

✔ Virtual layer updated
```

SQLMesh detects the change in the seed file. When you apply the plan, SQLMesh efficiently updates the `raw.events` table and then processes the `analytics.daily_revenue` model only for the affected time intervals. DuckDB writes only the new data to storage, and DuckLake efficiently updates the metadata, avoiding a full reprocessing of the dataset.

Now, with our newly arrived data processed in both environments, our models should match:

```javascript
sqlmesh table_diff prod:dev analytics.daily_revenue
No models contain differences with the selection criteria: 'analytics.daily_revenue'
```

Our `prod ` environment shows the latest version of the `analytics.daily_revenue` table.

## Conclusion

You have successfully built a modern, open data lakehouse by separating compute (DuckDB), storage (local directory), metadata (DuckLake table format), and orchestration (SQLMesh). Thanks to DuckLake’s ACID guarantees and metadata management, we were able to handle data increments and schema enforcement seamlessly which would be veryhard to DIY on raw Parquet files, especially at scale*.*

This foundation enables you to build data transformation pipelines that scale efficiently. While DuckLake is new, it continues to evolve. On their roadmap are exciting new features like Apache Iceberg compatibility, which will continue to make it a game-changing technology. The future is exciting!

[Talk With Us](https://www.tobikodata.com/talk-with-us) [Read the Tobiko Cloud Docs](https://www.tobikodata.com/blog/#) [Read the SQLMesh Docs](https://sqlmesh.readthedocs.io/en/stable/) [Read the SQLGlot Docs](https://github.com/tobymao/sqlglot#readme) [Sign Up for Tobiko University](https://www.tobikodata.com/blog/#) [Learn More About Tobiko Cloud](https://www.tobikodata.com/tobiko-cloud) [Learn More About SQLMesh](https://www.tobikodata.com/sqlmesh) [Learn More About SQLGlot](https://www.tobikodata.com/sqlglot) [Join Our Slack Community](https://www.tobikodata.com/slack)

> Source: `docs/data_engineering/ducklake/DuckLake to MotherDuck_ Validate locally, deploy to cloud in minutes.md`

---
title: "DuckLake to MotherDuck: Validate locally, deploy to cloud in minutes"
source: "https://dlthub.com/blog/ducklake-to-motherduck-with-dlt"
author:
published: 2025-12-16
created: 2025-12-23
description: "Start local with DuckLake, validate your data, then deploy to MotherDuck in minutes. Same pipeline, same code, just switch the destination."
tags:
  - "clippings"
---
Most data teams start by developing locally, then load data and deploy to the cloud. It’s the familiar path, but not the shortest. The friction usually comes when merging the two worlds: Local prototyping & development vs production credentials and cloud deployment.

So naturally, as data people, we want this friction removed. But we also want to be efficient about it, so we want to keep our local workflows while making the “go to online” path simple.

### Starting local

Early pipeline work is about getting the ground truth right - how am I calling data from the source, what does the data look like, what of it will I load, and how can I make it incremental?

Because in a data pipeline, you can't really separate the code from the semantics of the data. You want to quickly get some data, have a look at it, discard it and continue development.

Having to connect to production just to look at some data is just an inconvenience.

DuckLake fixes this by giving you a fast local environment. You load the data locally, validate it, and once everything looks right, you flip the destination switch to the cloud.

![](https://cdn.sanity.io/images/nsq559ov/production/f6aaff5414bf4b69949971ad6a0d7b1ba84999e2-3792x2544.png?w=120&auto=format)

### How DuckLake helps local development

DuckLake stores table data in Parquet files while keeping all table and partition metadata in a SQL catalog database. Being lightweight, it lets you spin up a lakehouse on your laptop instantly. And that fast feedback loop is what makes pipeline development easier.

### How MotherDuck fits into production

Ducklake lets you use a decoupled runtime + storage, so when you publish the data into production, you want to make sure that there’s a runtime available for users who want to read the data - that runtime is Motherduck.

### Walkthrough: Validate locally, deploy to the cloud

We’ll use the Hacker News API to walk through the workflow. First, we’ll load the data locally in DuckLake. Once we’ve validated it using dlt's DBML export and the Dashboard, we’ll switch the pipeline destination to MotherDuck and run the pipeline as-is.

If you want to try this yourself, here’s the Colab notebook: [link.](https://colab.research.google.com/drive/14t6-k6so_J9ANaKDCr_6NH-GdgNyMllX?usp=sharing)

#### Install dependencies

```
!pip install "dlt[ducklake,motherduck, dbml, workspace]"
```

#### Define a Hacker News source

```
import dlt

import requests

session = requests.Session()

# fetch top Hacker News stories

@dlt.resource(

    table_name="stories",

    write_disposition="merge",

    primary_key="id"

)

def hacker_news(limit=30):

    ids = session.get(

        "https://hacker-news.firebaseio.com/v0/topstories.json"

    ).json()[:limit]

    for story_id in ids:

        story = session.get(

            f"https://hacker-news.firebaseio.com/v0/item/{story_id}.json"

        ).json()

        if story:

            yield story

            

# run the pipeline with 'ducklake' destination

pipeline = dlt.pipeline(

    pipeline_name="hn_local",

    destination="ducklake",

    dataset_name="hacker_news"

)

print(pipeline.run(hacker_news(50)))
```

#### Inspect the schema locally

```
!dlt pipeline hn_local schema --format dbml
```

This prints the inferred schema in DBML format. It’s a quick way to verify that the schema structure matches your expectations. You can take the output and paste it in the third-party apps like dbdiagram, as shown below.

To inspect your data further, we’ll use the [workspace dashboard](https://dlthub.com/docs/general-usage/dashboard).

The dashboard is a web app that shows you pipeline metadata, the schema, and table previews at a glance. It also lets you run SQL directly against your DuckLake files using datasets, so you can check row counts or run quick QA queries.

For example:

**Schema Check:** View tables, columns, data types and hints.

![](https://cdn.sanity.io/images/nsq559ov/production/7919584ad91ad224e47008c9579dfa3b9eeb2577-2286x1618.png?w=120&auto=format)

**Dataset Browser:** Run SQL queries.

**Row count:**

![](https://cdn.sanity.io/images/nsq559ov/production/7c2ab19b71900353f5833749541300f169439af5-2138x1590.png?w=120&auto=format)

**Data Preview:** a quick look at the data usually tells you half the story.

![](https://cdn.sanity.io/images/nsq559ov/production/d1fad67caa937937dc3027f421effdd2af58a238-2294x1444.png?w=120&auto=format)

After the sample data, columns, and schema look good, we’ll deploy to MotherDuck.

#### Switch to MotherDuck

We only change one thing to move to MotherDuck. No rewrites to your logic or API handling. We simply flip the destination parameter to `motherduck`.

```
pipeline = dlt.pipeline(

    pipeline_name="hacker_news_pipeline_md",

    destination="motherduck",

    dataset_name="hacker_news_data",

    dev_mode=True,

)

load_info = pipeline.run(hacker_news(50))

print(load_info)
```

Nothing else changes. Same code. Just a different destination.

#### Confirm the Cloud load

In MotherDuck, let's confirm that the schema and data match what we validated locally.

**Schema:**

![](https://cdn.sanity.io/images/nsq559ov/production/fb416a40fc4aa9c4c574d930486c840b03298bf2-898x1102.png?w=120&auto=format)

**Row count:**

![](https://cdn.sanity.io/images/nsq559ov/production/2cff129922da1ffa69fb90baf3376b222ef61ae1-936x377.png?w=120&auto=format)

Same data, just living in the cloud now.

You can inspect the data further in the dashboard. For example, the trace from the last pipeline run helps you debug any load issues.

![](https://cdn.sanity.io/images/nsq559ov/production/383860776d447b63381243938fdfe862d1df6fe5-2197x663.png?w=120&auto=format)

Here, when you run queries in the dashboard, it connects to MotherDuck and displays the data from the destination.

### Why this works

- **Fast feedback loop:** Develop and test locally, without infrastructure in the way. Answers come fast.
- **What works locally works in production:** DuckLake and MotherDuck both run on the same DuckDB engine. That means the pipeline you trust on your laptop behaves the same way in production. Fewer surprises when you ship.
- **Focus on logic, not config:** Your time goes into extraction, transformation, and shaping how data lands. Not babysitting environments or rewriting things for production.

You write once, validate once, and trust it.

From here, you can:

- read the [dlt docs](https://dlthub.com/docs/intro) to go deeper
- use workspace to vibe code an [API pipeline](https://dlthub.com/workspace) in minutes
- take a [course](https://dlthub.com/events) if you prefer video learning
- or add [tests and quality checks](https://dlthub.com/docs/general-usage/dataset-access/data-quality-dashboard) to your pipeline

The pattern stays simple. Explore and validate locally, then let MotherDuck take it from there. This keeps your local environment close to the logic, and the cloud handles the parts that need scale.

Speaking of cloud scale, we have some news.

We're proud to be **MotherDuck’s official launch partner for Europe.** Read the announcement [here](https://dlthub.com/blog/motherduck-europe-dlt-integration).

### Still here? Try it yourself

You have the code, and you know the pattern. Try this workflow and see how simple it can be. It will not take more than a coffee break.

- Link [to Colab](https://colab.research.google.com/drive/14t6-k6so_J9ANaKDCr_6NH-GdgNyMllX?usp=sharing)
- Need help? Join our [Slack community](https://dlthub.com/community)[Data contract agreement vs enforcement](https://dlthub.com/blog/data-contracts-agreement-vs-enforcement)

[

11 Pythonic Data Quality Recipes for every day

](https://dlthub.com/blog/practical-data-quality-recipes-with-dlt)

> Source: `docs/data_engineering/ducklake/mlflow_kafka_ducklake/README.md`

# 🧪 Data Lab

Tooling for a minimalist data lab running on top of DuckLake.

## 📋 Requirements

Minimum requirements:

- [uv](https://docs.astral.sh/uv/getting-started/installation/) with [Python 3.13](https://docs.astral.sh/uv/guides/install-python/#installing-a-specific-version) installed.
- Access to [MinIO](https://min.io/) or [S3](https://aws.amazon.com/s3/)-compatible object storage.

> [!TIP]
> I keep a MinIO instance on my tiny home lab, made of an old laptop running Proxmox, but you can easily spin up a MinIO instance using the `minio` service using the `dev` profile under `infra/services/docker/compose.yml`, after setting up your `.env` (see below).

To run your own infrastructure, you'll also need:

- [Proxmox VE 9.x](https://proxmox.com/en/products/proxmox-virtual-environment/get-started)
- [Terraform 1.13.x](https://developer.hashicorp.com/terraform/install) (see [tfswitch](https://tfswitch.warrensbox.com/Installation/))
- [Docker 28.4.x](https://docs.docker.com/engine/install/)

> [!TIP]
> Most workflows are saved as [just](https://just.systems/man/en/) commands, which are available after you install `uv` dependencies and load the virtual environment. Run `just -l` to list all available commands (more details below).

> [!NOTE]
> *The following is no longer required, and will be updated and tested soon:*
>
> We rely on the official [duckdb/dbt-duckdb](https://github.com/duckdb/dbt-duckdb) adapter to connect to DuckLake. At this time, the latest stable version of the adapter does not support attaching the external DuckLake catalog with the `DATA_PATH` option and S3 credentials, but there is [PR #564](https://github.com/duckdb/dbt-duckdb/issues/564) that solves this, so we're using what is, at this point, unreleased code (see the [dbt-duckdb](pyproject.toml#L16) dependency and the corresponding entry under [[tools.uv.sources]](pyproject.toml#L37) in the [pyproject.toml](pyproject.toml) file).

## 🚀 Quick Start

First create your own `.env` file from the provided example:

```bash
cp .env.example .env
```

Make sure you fill-in the S3 configuration for:

```bash
S3_ACCESS_KEY_ID=minio_username
S3_SECRET_ACCESS_KEY=minio_password
```

You can then activate `just` and `dlctl` via:

```bash
uv sync
source .venv/bin/activate
```

You can then setup the MinIO service as follows (it will use your env vars):

```bash
docker compose -p datalab -f infra/services/docker/compose.yml \
    --profile dev up minio minio-init -d
```

Or you can spin up the whole infrastructure locally, after Docker is running, by using:

```bash
just infra-provision-local
```

> [!TIP]
> If you're you're having trouble connecting to MinIO, make sure you're using the correct zone, which you set via the `S3_REGION` variable in `.env`.

You should also generate the `init.sql` file, so you can easily connect to your DuckLake from the CLI as well:

```bash
dlctl tools generate-init-sql
duckdb -init local/init.sql local/engine.duckdb
```

Or simply run the following command whenever you want to access your DuckLake, which will take care of the setup process for you:

```bash
just lakehouse
```

The general workflow you're expected to follow for data engineering is illustrated in the following diagram:

![Data Lab Architecture Diagram](docs/datalab-architecture.png)

You're expected to implement your own [dbt](https://docs.getdbt.com/) models to power `dlctl transform`. We provide an example of this under `transform/models/`, based on the following Kaggle datasets:

- [andreagarritano/deezer-social-networks](https://www.kaggle.com/datasets/andreagarritano/deezer-social-networks)
- [undefinenull/million-song-dataset-spotify-lastfm](https://www.kaggle.com/datasets/undefinenull/million-song-dataset-spotify-lastfm)

A few datasets are already supported and pipeline are encoded using `just` commands (e.g., `econ-compnet-etl`, `graphrag-etl`, `mlops-etl`, which correspond to projects with their own YouTube videos).

You can learn all other details below.

## 🧩 Components

### dlctl/

This is where the `dlctl` command lives—standing for 'Data Lab Control'. This helps you run all the tasks supported by the data lab package. It is available as a script under [pyproject.toml](pyproject.toml#L31) and it can be accessed via:

```bash
uv sync
source .venv/bin/activate
dlctl ...
```

> [!NOTE]
> A few `torch` dependencies, like `torch_sparse` require `UV_FIND_LINKS` to be set when adding or removing any dependencies, but not during install, where `uv.lock` already has all the required information. We currently don't rely on this, but, if we do in the future, here's how to approach it:
>
> ```bash
> export UV_FIND_LINKS="https://data.pyg.org/whl/torch-2.7.0+cu126.html"
> uv add --no-build-isolation pyg_lib torch_scatter torch_sparse \
>   torch_cluster torch_spline_conv
> ```

### infra/

Implements a 4-layer infrastructure architecture to help you deploy a data stack on-premise using Proxmox, Terraform, and Docker.

![Infrastructure Architecture](./docs/infra-architecture.png)

- Layer 1 (`foundation/`) is a Terraform project that will provision MinIO on an LXC running on Proxmox.
- Layer 2 (`platform/`) is a Terraform project, with state storage on MinIO, that will provision three Docker VMs and a GitLab VM. GitLab will provide a container registry and come preconfigured with a GitLab Runner that executes on top of one of the Docker VMs.
- Layer 3 (`services/`) contains a Terraform project (`gitlab/`) to optionally initialize CI/CD variables/secrets from the local `.env`, and a Docker Compose project (`docker/`) to provision the data stack services.
- Layer 4 (`applications/`) contains local application deployments via Dockerized services (e.g., `ml.server`) and CI/CD integration to provision the required resources (e.g., postgres database and credentials).

### ingest/

Helps manage ingestion from difference data sources, creating the proper directory structure (see [Storage Layout](#%EF%B8%8F-storage-layout)) consisting of the retrieval for raw data and the creation proper directory structure creation. Raw data might be dropped manually, from Kaggle, Hugging Face, or some other source. This will make it easy to load it and keep it organized.

### transform/

This is the core of the data lakehouse, using [dbt](https://docs.getdbt.com/) to transform raw data into usable data, with [DuckLake](https://ducklake.select/) as the underlying catalog, running on top of SQLite.

We purposely keep this simple with SQLite, using a backup/restore strategy to/from S3, as this assumes exploratory lab work, but you can easily replace [SQLite](https://ducklake.select/docs/stable/duckdb/usage/choosing_a_catalog_database#sqlite) with a [PostgreSQL](https://ducklake.select/docs/stable/duckdb/usage/choosing_a_catalog_database#postgresql) node, if you prefer.

### export/

Gold tier datasets under your data marts are only usable externally after you export them. This component manages exports, creating them for a specific data mart catalog and schema, listing them, or purging old versions.

### graph/

Graph loading and computation on top of KùzuDB. We support operations like graph loading from S3 parquet files, and node embedding via FRP (Fast Random Projection), which is implemented using node batching with input/output from/to KùzuDB and training on top of PyTorch.

### ml/

Complete ML Engineering lifecycle implementation, including feature extraction, and model training and testing, with MLflow experiment tracking and evaluation. It also provides a REST API endpoint for inference, prediction logging, and user feedback tracking, implemented using an even-driven architecture based on Kafka topics. This optionally serves models using an A/B/n testing approach. Finally, we also implement several methods for simulating inference requests and user feedback, based on a monitoring dataset, that we use to compute monitoring metrics over time, like prediction drift, feature drift, estimated performance, or user evaluation.

### shared/

Includes the following modules:

- `settings` – loads and provides access to environment variables and other relevant constants;
- `storage` – handles mid-level S3 storage operations, like creating a dated directory structure, uploading and downloading files and directories, or managing the manifest files;
- `cache` – provides utilities to manage filesystem-based caching based on a user data directory (usually `~/.cache/datalab`);
- `lakehouse` – connects the DuckDB engine and helps with tasks like exporting datasets, or loading the latest snapshot for an export;
- `templates` – contains helper functions and `string.Template` instances to produce files like `init.sql`;
- `color` – palette and color processing utilities, mostly used to support plotting;
- `logging` – interceptor logger to replace inconsistent logging utilities (e.g., from `uvicorn`).
- `tools` – provides a function per CLI tool (callable via `dlctl tools`), for example to generate the `init.sql` file described in the `templates` module;
- `utils` – provides a `@timed` annotator to print run time, and function name sanitization code.

### notebooks/

Jupyter notebook for prototyping or standalone analyzes. Notebooks are dropped directly on the root path, since all data is loaded and saved to the DuckLake instance.

### scripts/

Individual Bash or Python scripts for generic tasks (e.g., launching KùzuDB Explorer).

### local/

Untracked directory where all your local files will live. This includes the engine database (DuckDB) and the DuckLake catalogs (e.g., `stage.sqlite`, `marts/graphs.sqlite`), which you can restore from a [backup](#backup), or create from scratch. KùzuDB databases will also live here, under `graphs/`, as well as the `init.sql` script for CLI access to the lakehouse.


## 🗃️ Storage Layout

All data is stored in a single S3 bucket (e.g., `s3://lakehouse`, tested with MinIO), with directory structure:

```
s3://lakehouse/
├── backups/
│   └── catalog/
│       ├── YYYY_MM_DD/
│       │   └── HH_mm_SS_sss/
│       │       └── lakehouse.dump
│       └── manifest.json
├── raw/
│   └── <dataset-name>/
│       ├── YYYY_MM_DD/
│       │   └── HH_mm_SS_sss/
│       │       ├── *.csv
│       │       ├── *.json
│       │       └── *.parquet
│       └── manifest.json
├── stage/
│   └── ducklake-*.parquet
├── marts/
│   └── <domain>/
│           └── ducklake-*.parquet
└── exports/
    └── <domain>/
        └── <dataset-name>/
            ├── YYYY_MM_DD/
            │   └── HH_mm_SS_sss/
            │       ├── *.csv
            │       ├── *.json
            │       └── *.parquet
            └── manifest.json
```

> [!NOTE]
> Date/time entries should be always UTC.

## ⚙️ Configuration

Configuration for data lab is all done through the environment variables defined in `.env`.

This will also support the generation of an `init.sql` file, which contains the DuckLake configurations, including the MinIO/S3 secret and all attached catalogs.

### Environment Variables

#### S3 Configurations

```bash
S3_ENDPOINT=localhost:9000
S3_USE_SSL=false
S3_URL_STYLE=path
S3_ACCESS_KEY_ID=minio_username
S3_SECRET_ACCESS_KEY=minio_password
S3_REGION=eu-west-1
```

`S3_ENDPOINT` and `S3_URL_STYLE` are only required if you're using a non-AWS object store like MinIO.

`S3_REGION` must match MinIO's region (explicitly setting one in MinIO is recommended).

#### PostgreSQL

```bash
PSQL_ROOT_PASSWORD=datalabtech
```

Set this to the `root` user password of your PostgreSQL database—only used when deploying your on-premise infrastructure, so that databases and credentials can be provisioned at a later stage. Otherwise not accessed.

#### Data Lab Specifics

```bash
S3_BUCKET=lakehouse
S3_INGEST_PREFIX=raw
S3_STAGE_PREFIX=stage
S3_SECURE_STAGE_PREFIX=secure-stage
S3_GRAPHS_MART_PREFIX=marts/graphs
S3_ANALYTICS_MART_PREFIX=marts/analytics
S3_EXPORTS_PREFIX=exports
S3_BACKUPS_PREFIX=backups
```

You can use the defaults here. Everything will live under the `S3_BUCKET`. Each stage has its own prefix under that bucket, but the mart prefixes are special—any environment variable that ends with `*_MART_PREFIX` will be associated with its down `*_MART_DB`, as show in the next section.

#### DuckLake Configurations

```bash
ENGINE_DB=engine.duckdb
STAGE_DB=stage.sqlite
SECURE_STAGE_DB=secure_stage.sqlite
GRAPHS_MART_DB=marts/graphs.sqlite
ANALYTICS_MART_DB=marts/analytics.sqlite
```

These files will live under `local/`. The DuckDB `ENGINE_DB` will be leveraged for querying. All data is tracked on the `STAGE_DB` and `*_MART_DB` catalog databases and stored on the corresponding object storage locations, as shown in the previous section. You can also used `SECURE_STAGE_DB` if you need to encrypt your data (e.g., for sensitive user data).

#### Kuzu Configurations

```bash
MUSIC_TASTE_GRAPH_DB=graphs/music_taste.kuzu
ECON_COMP_GRAPH_DB=graphs/econ_comp.kuzu
```

The data lab also leverages [Kuzu](https://kuzudb.com/) for graph data science tasks. The path for each graph database can be set here as `*_GRAPH_DB`.

#### Ollama Configurations

```bash
OLLAMA_MODELS=gemma3:latest,phi4:latest
```

Here you can preconfigure the Ollama models you want to download when running your local or on-premise infrastructure, as comma-separated `model:version` entries.

#### MLflow Configurations

```bash
MLFLOW_TRACKING_URI=http://docker-shared:5000
MLFLOW_TRACKING_USERNAME=datalabtech
S3_MLFLOW_BUCKET=mlflow
S3_MLFLOW_ARTIFACTS_PREFIX=artifacts
```

The `MLFLOW_TRACKING_*` variables configure how you interact with the MLflow server, while the `S3_MLFLOW_*` variables configure the S3 bucket where artifacts (e.g., serialized models) will be dropped into.

#### Kafka Configurations

```bash
KAFKA_BROKER_ENDPOINT=docker-shared:9092
KAFKA_GROUP_TOPIC_LIST=ml_inference_results:lakehouse-inference-result-consumer,ml_inference_feedback:lakehouse-inference-feedback-consumer
```

You can configure your Kafka endpoint here, as well as any required topics. We initialize each topic via comma-separated list of `topic:group`, so that consumers can be initialized and no warning is printed when first connecting to a topic from that consumer—this is likely overkill, but it feels cleaner.

### Generating init.sql

You can generate an `init.sql` once you setup your `.env`, so you can access your DuckLake from the CLI using `duckdb`:

```bash
dlctl tools generate-init-sql
duckdb -init local/init.sql local/engine.duckdb
```

## 📖 Usage

### Ingestion

As a rule of thumb, ingestion will be done via the `dlctl ingest` command. If a version for the current date already exists, it will output an error and do nothing—just wait a millisecond.

#### Manual

For manually uploaded datasets, you can create a directory in S3 by giving it the dataset name:

```bash
dlctl ingest dataset --manual "Your Dataset Name"
```

This will create a directory like `s3://lakehouse/raw/your_dataset_name/2025_06_03/19_56_03_000`, update `s3://lakehouse/raw/your_dataset_name/manifest.json` to point to it, and print the path to stdout.

#### From Kaggle or Hugging Face

```bash
dlctl ingest dataset \
    "https://www.kaggle.com/datasets/<username>/<dataset>"

dlctl ingest dataset \
    "https://huggingface.co/datasets/<username>/<dataset>"
```

The dataset name will be automatically extracted from the `<dataset>` slug and transformed into snake case for storage. Then, a directory like `s3://lakehouse/raw/your_dataset_name/2025_06_03/19_56_03_000` will be created, `s3://lakehouse/raw/your_dataset_name/manifest.json` updated to point to it, and the final path printed to stdout.

#### Listing Ingested Datasets

You can also list existing dataset paths for the most recent version, to be used for transformation:

```bash
dlctl ingest ls
```

Or all of them:

```bash
dlctl ingest ls -a
```

#### Pruning Empty Datasets

Sometimes you'll manually create a dataset and never upload data into the directory, or an ingestion process from a URL will fail and leave an empty directory behind. You can prune those directories using:

```bash
dlctl ingest prune
```

### Transformation

Transformations can be done via `dlctl transform`, which will call `dbt` with the appropriate arguments:

```bash
dlctl transform "<dataset-name>"
```

You can also run data tests using:

```bash
dlctl test
dlctl test -m test_type:singular
```

Or generate or serve dbt documentation using:

```bash
dlctl docs generate
dlctl docs serve
```

### Export

#### Exporting to Parquet

In order to externally use a dataset from the Lakehouse, you first need to export it. This can be done for any data mart catalog, over a selected schema. Exported datasets will be kept in dated directories with their own `manifest.json`.

```bash
dlctl export dataset "<data-mart-catalog>" "<schema>"
```

#### Listing Exported Datasets

You can list the most recent versions of exported datasets:

```bash
dlctl export ls
```

Or all of them:

```bash
dlctl export ls -a
```

#### Pruning Empty Datasets

After a few exports, you might want to remove old versions to claim space. You can prune those directories using:

```bash
dlctl export prune
```

### Backup

Since we rely on embedded databases and S3 object storage, we need to backup our databases.

> [!IMPORTANT]
> Data Lab was designed to be used in an education or research environment, so it currently doesn't support concurrent users. This could easily be added, though, as DuckLake supports PostgreSQL catalogs in place of SQLite, which we are using here.

#### Create

You can create a backup by running:

```bash
dlctl backup create
```

#### Restore

In order to restore a backup, just run:

```bash
dlctl backup restore --source "<YYYY-mm-ddTHH:MM:SS.sss>"
```

Omitting `--source` will restore the latest backup.

> [!CAUTION]
> Omitting `--target` will restore to `local/` by default, so take care not to overwrite your working version by mistake!

#### List

You can list all backups using:

```bash
dlctl backup ls
```

And you can list all files in all backups using:

```bash
dlctl backup ls -a
```

### Graph

#### Load

This will load nodes and edges into a KùzuDB database stored under `local/graphs/<schema>`, where `schema` is a schema containing nodes and edges under the `graphs` data mart catalog. Table names for nodes or edges are usually prefixed with `<dataset>_nodes_` or `<dataset>_edges_`, respectively, and should follow the format described on KùzuDB's docs.

```bash
dlctl graph load "<schema>"
```

#### Compute

A collection of graph computation calls will live here. These can be wrappers to native KùzuDB computations, or external computations. Currently, we just include the `embeddings` computation, which runs in Python using PyTorch. This will compute FRP embeddings with dimension 256, over batches of 9216 nodes, trained using 5 epochs, for the `<schema>` graph:

```bash
dlctl graph compute embeddings "<schema>" -d 256 -b 9216 -e 5
```

### ML

#### Train

Train and evaluate a model using the `dataset` table under the provided `<schema>`, while tracking the experiment using MLflow:

```bash
dlctl ml train <schema> --method logreg --features embeddings
```

The `--method` can be one of the supported algorithms (e.g., `logreg` or `xgboost`), and `--features` follows a similar approach for supported features (e.g., `tfidf` or `embeddings`). Currently only text-based datasets are supported, but the schema and training code has been generalized to support tabular data as well.

#### Server

A REST API endpoint can be run to provide an inference service with optional A/B/n testing and event-based logging, or to receive user feedback on the predictions:

```bash
dlctl ml server
dlctl ml server -h 0.0.0.0 -p 8000
```

#### Simulate

In order to help us implement and test monitoring statistics, we implemented a request simulation framework, where feedback is provided based on a monitoring dataset, which is completely separate from the dataset using for training, validation and testing. For example, to use a 1% sample of the `monitor` table from `<schema>` for A/B testing with the `dd_xgboost_embeddings` and `dd_logreg_tfidf` latest models, we can use:

```bash
dlctl ml simulate <schema> \
    --sample-fraction 0.01 \
    --model-uri "models:/dd_xgboost_embeddings/latest" \
    --model-uri "models:/dd_logreg_tfidf/latest"
```

The `models:/` URIs correspond to models trained and logged within MLflow. For production, we usually replace `latest` with a particular tag that we assign to our production models (e.g., a version).

There are several other options to help you control the simulation as well, which you can check under:

```bash
dlctl ml simulate --help
```

These include the number of passes, the batch size, the decision threshold, and several ranges to help control the fraction of feedback to provide, the fraction of wrong feedback, or the date range to simulate.

#### Monitor

This will let you compute and plot monitor statistics over time for a specific `<schema>`, optionally specifying a date range and a window size:

```bash
dlctl ml monitor compute <schema>
dlctl ml monitor compute <schema> \
    --since <start> \
    --until <end> \
    --window-size 7
```

For plotting, you must also specify one or several model URIs:

```bash
dlctl ml monitor plot <schema> \
    --model-uri "models:/dd_xgboost_embeddings/latest" \
    --model-uri "models:/dd_logreg_tfidf/latest"
```

This will produce several PNG plots under `local/monitor/`.

## 🧾 Just Commands

We provide several `just` commands, both for convenience and to keep track of data pipelines (e.g., ETL) for specific datasets. Below we provide an overview on these commands, excluding most secondary commands.

### Common

We provide a `check binary` command that will look for a specific binary in the path and check whether it's executable—the command will fail otherwise, causing any depending commands to fail as well. We implement specific check commands per binary, since we cannot use parameters in dependencies. For example:

```bash
just check duckdb
just check-terraform
```

We also provide a `confirm` command, to add as a dependency of critical commands (e.g., `terraform destroy`). This will display a confirmation message and require user input to continue:

```bash
just confirm
```

```
Are you sure? [y/N] n
error: Recipe `confirm` failed with exit code 1
```

### DuckLake

**Related video:** https://youtu.be/zn69Q7FiFfo?si=tiG4DT_apbR_-sVC

In order to run a REPL for the datalab's DuckLake instance, you can simply run:

```bash
just lakehouse
```

This will take care of the `init.sql` generation for you, but you might want to regenerate it later as well:

```bash
just generate-init-sql
```

### GraphRAG with Kuzu

**Related video:** https://youtu.be/m61u3mqu1qY?si=kmjmPHTY5-8M8Q81

| Command | Description |
| ------- | ----------- |
| `graphrag-etl` | Ingest [DSN](https://www.kaggle.com/datasets/andreagarritano/deezer-social-networks) and [MSDSL](https://www.kaggle.com/datasets/undefinenull/million-song-dataset-spotify-lastfm) datasets, run DuckLake transformations, export to Parquet, and load graph into Kuzu. |
| `graphrag-embeddings` | Compute node embeddings of dimension 256 using 5 epochs and batches of size 9216, and create vector index. |
| `graphrag` | Launch REPL for graph RAG. |
| `graphrag-all` | Run all of the above, in order. |

### Economic Competition Networks

**Related video:** https://youtu.be/pIwN7oe54i4?si=-nB0upswBGacklh4

| Command | Description |
| ------- | ----------- |
| `econ-compnet-ingest` | Ingest [The Atlas of Economic Complexity](https://atlas.hks.harvard.edu/data-downloads). |
| `econ-compnet-transform` | Run DuckLake transformations on the dataset, to produce a knowledge graph. |
| `econ-compnet-export` | Export the graph data to Parquet. |
| `econ-compnet-load` | Load the graph into Kuzu. |
| `econ-compnet-etl` | Run all of the above, in order. |
| `econ-compnet-scoring` | Computes the Common Out-Neighbor (CON) score for the Country-CompetesWith-Country graph projection. |
| `econ-compnet-all` | Run ETL and scoring commands. |

### MLOps: A/B Testing with MLflow, Kafka, and DuckLake

**Related video:** https://youtu.be/MGuj13NcdjE?si=i56T6updcLE-NFC3

#### Training

| Command | Description |
| ------- | ----------- |
| `mlops-ingest` | Ingest the depression dataset for [training](https://huggingface.co/datasets/ShreyaR/DepressionDetection) and [monitoring](https://huggingface.co/datasets/joangaes/depression). |
| `mlops-transform` | Run DuckLake transformations on the datasets, normalizing into a common format for the ML pipelines, including a train/test split and fixed folds on the training set for validation. |
| `mlops-etl` | Run all of the above, in order. |
| `mlops-train-logreg-tfidf` | Train a model using logistic regression and TF-IDF features. |
| `mlops-train-logreg-embeddings` | Train a model using logistic regression and text embedding features. |
| `mlops-train-logreg` | Train all logistic regression models. |
| `mlops-train-xgboost-tfidf` | Train a model using XGBoost and TF-IDF features. |
| `mlops-train-xgboost-embeddings` | Train a model using XGBoost and text embedding features. |
| `mlops-train-xgboost` | Train all XGBoost models. |
| `mlops-train` | Train all models. |
| `mlops-all` | Run ETL and training. |

#### Inference

| Command | Description |
| ------- | ----------- |
| `mlops-serve` | Run ML server listening on 0.0.0.0 and port 8000. |
| `mlops-test-inference` | Use `curl` to test the inference endpoint. |
| `mlops-test-feedback` | Use `curl` to test the feedback endpoint. |

#### Monitoring

| Command | Description |
| ------- | ----------- |
| `mlops-simulate-inference` | Run inference simulation for XGBoost with text embedding features, and logistic regression with TF-IDF features, using the monitor set to produce feedback. |
| `mlops-monitor-compute` | Compute monitoring statistics for the two models. |
| `mlops-monitor-plot` | Plot monitoring statistics for the two models. |

### Data Lab Infra

**Related videos:** https://www.youtube.com/playlist?list=PLeKtvIdgbljMyhjPgJeoXwa_7J9DTx3Fo

#### Config Checks

| Command | Description |
| ------- | ----------- |
| `infra-config-check-foundation` | Look for `terraform.tfvars` under `infra/foundation`. |
| `infra-config-check-platform` | Look for `terraform.tfvars` and `state.config` under `infra/platform`. |
| `infra-config-check-services` | Look for the `docker-shared` context, that should point to the corresponding Docker VM. |
| `infra-config-check-all` | Run all of the above, in order. |

#### Initializations

| Command | Description |
| ------- | ----------- |
| `infra-foundation-init` | Run `terraform init` for `infra/foundation`. |
| `infra-platform-init` | Run `terraform init` for `infra/platform`. |
| `infra-init` | Run all of the above, in order. |

#### Provisioning

| Command | Description |
| ------- | ----------- |
| `infra-provision-foundation` | Run `terraform apply` for `infra/foundation`. |
| `infra-provision-platform` | Run `terraform apply` for `infra/platform`. |
| `infra-provision-services` | Run `terraform apply` for `infra/services/gitlab` (required a configured `.env`), and `docker compose up` under the appropriate `docker-shared` context, using `infra/services/docker/compose.yml`. |
| `infra-provision-all` | Run all of the above, in order. |
| `infra-provision-local` | Run `docker compose up` with the `dev` profile enabled, using `infra/services/docker/compose.yml`. |

#### Destruction

| Command | Description |
| ------- | ----------- |
| `infra-destroy-foundation` | Run `terraform destroy` for `infra/foundation`. |
| `infra-destroy-platform` | Run `terraform destroy` for `infra/platform`. |
| `infra-destroy-services` | Run `docker compose down` and `terraform destroy` for `infra/services`. |
| `infra-destroy-all` | Run all of the above, in reversed order. |
| `infra-destroy-local` | Run `docker compose down` with the `dev` profile enabled for `infra/services`. |

#### Utilities

| Command | Description |
| ------- | ----------- |
| `infra-show-tf-credentials` `<layer>` | Print the credentials for a specific `layer` (`foundation` or `platform`). |
| `infra-show-credentials` | Print all credentials. |


> Source: `docs/data_engineering/ducklake/mlflow_kafka_ducklake/CHANGELOG.md`

# CHANGELOG


## v1.1.0 (2025-11-25)

### Bug Fixes

- Missing S3_EXPORTS_PREFIX and S3_BACKUPS_PREFIX
  ([`93b8bb5`](https://github.com/DataLabTechTV/datalab/commit/93b8bb51eabecee6e8f34397a3fd0062f88b190a))

### Chores

- Implement just command for migrating from a sqlite to a postgres catalog on ducklake
  ([`81e082f`](https://github.com/DataLabTechTV/datalab/commit/81e082f99fae1faeeeda58dc2e029002135211e5))

- Normalize etl related commands, create tl only commands, and global etl, ingest, and tl commands
  ([`c7dca94`](https://github.com/DataLabTechTV/datalab/commit/c7dca94f2241b988f95a5bbf499bfea3878106e5))

- **deps**: Bump up duckdb and switch dbt-duckdb to stable non-git version
  ([`2c6bb02`](https://github.com/DataLabTechTV/datalab/commit/2c6bb02ac2b8c3926823247f980167e865f59b9f))

### Code Style

- Remove new line
  ([`8b2a148`](https://github.com/DataLabTechTV/datalab/commit/8b2a148cc7402843478025a15aff1fb1aea75e87))

- Wrap sql script path in double quotes
  ([`0894362`](https://github.com/DataLabTechTV/datalab/commit/08943627646cd573c1b2390972b389a722f2be8d))

### Documentation

- Update file structure and dlctl commands to match new postgres catalog backups
  ([`0febe4a`](https://github.com/DataLabTechTV/datalab/commit/0febe4add0737085911ff172f518c33c48f78c66))

### Features

- Add env vars required to get lakehouse connectivity
  ([`9cf6bf5`](https://github.com/DataLabTechTV/datalab/commit/9cf6bf5095c57d9ce5effca42391317fa19a858b))

- Migrate ducklake catalog from sqlite to postgres
  ([`c077595`](https://github.com/DataLabTechTV/datalab/commit/c077595aa92c0a12d2acf4d45efdd7a8a5154375))

- Migrate the dlctl backup from sqlite to postgres support
  ([`0fe2c6d`](https://github.com/DataLabTechTV/datalab/commit/0fe2c6d2894b672d208fb42d32684fc5377c48ed))

### Refactoring

- Change engine_db variable scope (not used anywhere else)
  ([`2fad9de`](https://github.com/DataLabTechTV/datalab/commit/2fad9de12d158a49bad90b3897cda578d36a5f4d))

- Extract sql script to a separate file
  ([`66e282c`](https://github.com/DataLabTechTV/datalab/commit/66e282cb39577a9ba5c89082f5b1d46ea091d695))

- Reformat inline sql into fewer columns
  ([`5a81765`](https://github.com/DataLabTechTV/datalab/commit/5a81765050db285fb3af72bda07c952337317668))

- Remove unused imports
  ([`acaccd0`](https://github.com/DataLabTechTV/datalab/commit/acaccd00cb0bb2ff3880dff99a0ff83aea7700e9))

- Rename env var for postgres root password
  ([`17b82a0`](https://github.com/DataLabTechTV/datalab/commit/17b82a06641ee61437b985ee632d8d163a2a03be))


## v1.0.1 (2025-10-21)

### Bug Fixes

- Kuzu overwrite would fail when other files remained in the directory
  ([`186a774`](https://github.com/DataLabTechTV/datalab/commit/186a774e9754173039d6a3cd853ab40c4937bc16))

### Chores

- Add overwrite to graph load commands for idempotency
  ([`8de97c9`](https://github.com/DataLabTechTV/datalab/commit/8de97c9c38c0cce88833db97b65ad4a1235b4319))

- Bump up datalab locked version to 1.0.0 (latest)
  ([`d58130b`](https://github.com/DataLabTechTV/datalab/commit/d58130bdc36877f458d1606b4074451685e0af83))

- Just command to setup dev tools
  ([`345aecf`](https://github.com/DataLabTechTV/datalab/commit/345aecfeffc416b7008aa1792626eac374875e95))

- Setup nbstripout so that notebooks are not committed with any output
  ([`3bdef36`](https://github.com/DataLabTechTV/datalab/commit/3bdef365399db7a7dfb47fd9c5e11a7c8c7a5cd9))

- Strip outputs from existing notebooks
  ([`cf439e0`](https://github.com/DataLabTechTV/datalab/commit/cf439e0b6a332b9347a58431cf939ad603985671))


## v1.0.0 (2025-10-20)

### Bug Fixes

- Add default value to env vars on dbt models
  ([`eef59ff`](https://github.com/DataLabTechTV/datalab/commit/eef59ff367d5c21e9c6e68a7104e650e91f1e43d))

- Add missing curl and jq dependencies
  ([`99ce192`](https://github.com/DataLabTechTV/datalab/commit/99ce192aaac5c64f2b3b9df8986b6e8fcca8ee27))

- Add missing curl dependency
  ([`0d4609f`](https://github.com/DataLabTechTV/datalab/commit/0d4609fee635042f026818c0dedd1c906d42c1cc))

- Add missing env vars
  ([`a5e153d`](https://github.com/DataLabTechTV/datalab/commit/a5e153d8820a296f35b4a89d4a33b7ae6829d19c))

- Add missing graph load command, add spacing and comment sections
  ([`f9150bc`](https://github.com/DataLabTechTV/datalab/commit/f9150bc40a2b64536757dbb6860ca360ac9005fa))

- Add universe apt repo
  ([`ce5e18a`](https://github.com/DataLabTechTV/datalab/commit/ce5e18a13afd0ed73b1ce4c871049d72fff84def))

- Change to correct context path
  ([`4534a27`](https://github.com/DataLabTechTV/datalab/commit/4534a2778c45d74856dbb3229977550406c6c19c))

- Correct command to ml server
  ([`29dfbf7`](https://github.com/DataLabTechTV/datalab/commit/29dfbf7df289fa7f03c3a188bc1bdb9079bd89a7))

- Destroy services was not switching to the appropriate docker context
  ([`3aee07e`](https://github.com/DataLabTechTV/datalab/commit/3aee07e286a82cb64160f8eed95a1a91ac2fd7c7))

- Enable prevent_destroy so we can tune cores and memory without risking destruction in the future
  ([`ae7947d`](https://github.com/DataLabTechTV/datalab/commit/ae7947d886b683ca3219cc0a419f8e8f6c1be88a))

- Expired password by default and dhcp hostname broadcast
  ([`2e5bc08`](https://github.com/DataLabTechTV/datalab/commit/2e5bc0841c31b7dba49e4870d0b804b7485168df))

- Force build to ensure image is rebuilt when required
  ([`d84cc77`](https://github.com/DataLabTechTV/datalab/commit/d84cc774acec06a01f821a0175c7a499fd7d329a))

- Incorrect create user script path
  ([`22e6e0f`](https://github.com/DataLabTechTV/datalab/commit/22e6e0f343a77a17d653ab5a0d0e351caf92912d))

- Indentation
  ([`c7f1b17`](https://github.com/DataLabTechTV/datalab/commit/c7f1b17410f74464d416f44d05be3ccdbb058e3b))

- Mark env var secrets as sensitive
  ([`c52f940`](https://github.com/DataLabTechTV/datalab/commit/c52f9401ea5caca1ed55eaea6ee3ce1426467d77))

- Mark gitlab token as sensitive
  ([`3832bb1`](https://github.com/DataLabTechTV/datalab/commit/3832bb149314a332a605aa2b93e309678583a6d6))

- Missing add-apt-repository
  ([`2e2cf53`](https://github.com/DataLabTechTV/datalab/commit/2e2cf533380582cd764c04d58100970a68ae7d1d))

- Missing backslash
  ([`3ab832d`](https://github.com/DataLabTechTV/datalab/commit/3ab832d23f82552bc82880ab40b591f5554dcf09))

- Overcommit gitlab resources with 4 cores and 8 GiB without ballooning, for stability
  ([`48622fe`](https://github.com/DataLabTechTV/datalab/commit/48622fe5b4e3ea4ff01f61048477410a3b5b4218))

- Portainer would collide with minio when running locally
  ([`fcc0093`](https://github.com/DataLabTechTV/datalab/commit/fcc00932f09edbdf8d00bd2d44997093d95ce7a3))

- Preinstall missing jq
  ([`4c80525`](https://github.com/DataLabTechTV/datalab/commit/4c80525bd7e18a8a2786f65fa0a994b4bf067df2))

- Pushing large images would fail without checksum_disabled on the registry storage
  ([`eae3d6f`](https://github.com/DataLabTechTV/datalab/commit/eae3d6ff56a5cb22c4fd81e750883f7f3240a7bb))

- Re-enable prevent_destroy
  ([`94a5d69`](https://github.com/DataLabTechTV/datalab/commit/94a5d69fb74edcbccf24d34f0150fa1523839ee0))

- Script executable permissions
  ([`17bfd3b`](https://github.com/DataLabTechTV/datalab/commit/17bfd3b7e6ea59dc1ddf712f3a629c2072993d69))

- Set env file to the ci project dir
  ([`2642e03`](https://github.com/DataLabTechTV/datalab/commit/2642e034ac66559f94d88f2a5da81230ab6a8945))

- Set options that reconfigure couldn't using gitlab-rails console
  ([`d4e88cd`](https://github.com/DataLabTechTV/datalab/commit/d4e88cdd3b3d923334da12ce390f9f059393d5a9))

- Should be secret_key, not a duplicate access_key
  ([`e10b44e`](https://github.com/DataLabTechTV/datalab/commit/e10b44efc86bce17e2611d0b5f4f54873482c35c))

- Should be the node name, not the endpoint
  ([`09816d4`](https://github.com/DataLabTechTV/datalab/commit/09816d43240c3c704e3367e424fb8458c0f89f22))

- Tfstate backups have a timestamp before the backup extension
  ([`74261fe`](https://github.com/DataLabTechTV/datalab/commit/74261fe77604ed2a340fbdf3c538610302e1f058))

- Use env var instead of input, return empty string on null
  ([`f7ea5db`](https://github.com/DataLabTechTV/datalab/commit/f7ea5db491f69672ba5cb5c88d7c05250f734ed5))

- Use env var to expose external kafka advertised listener
  ([`355c787`](https://github.com/DataLabTechTV/datalab/commit/355c787d3314a70730f11581d73fe501bc2568c3))

- Variables were not being expanded
  ([`5c97801`](https://github.com/DataLabTechTV/datalab/commit/5c97801b3976e60086cdfe88da42aad97838b3b7))

- Wrong env filename
  ([`0d26f03`](https://github.com/DataLabTechTV/datalab/commit/0d26f033cf1e57321fcb8e49f98a67865a77a167))

### Chores

- Add gitlab bucket to default buckets
  ([`f56252c`](https://github.com/DataLabTechTV/datalab/commit/f56252cad7fc1680515a7718482222bd70bfb757))

- Add mlflow bucket to default foundation layer minio buckets
  ([`63a6ab9`](https://github.com/DataLabTechTV/datalab/commit/63a6ab96e99b5c88baa98de59ec2101a9a3f0ee7))

- Bump up mlflow from 3.2.0 to 3.4.0
  ([`cd3760d`](https://github.com/DataLabTechTV/datalab/commit/cd3760d8f69faba2d36fababe9257099e389242e))

- Enable prevent_destroy for docker and gitlab vms
  ([`0b1e914`](https://github.com/DataLabTechTV/datalab/commit/0b1e914cb7933aab566c3880c7c85dc0c660aea0))

- Ignore terraform state files and tfvars
  ([`4e3bc78`](https://github.com/DataLabTechTV/datalab/commit/4e3bc785dce3372f02750cd0c69f721eaf30e85e))

- Increase cores and memory for gitlab, reducing memory for docker-apps
  ([`b65292e`](https://github.com/DataLabTechTV/datalab/commit/b65292edefc6d7a17772d486881865902203cc80))

- Increase the number of concurrent jobs
  ([`602b85a`](https://github.com/DataLabTechTV/datalab/commit/602b85a1f73f0288fb4e189d6eb49ad47ebda10c))

- Minimal s3 config example
  ([`22bddc6`](https://github.com/DataLabTechTV/datalab/commit/22bddc658f7ef4aaaaca8f798075f827d800e5a5))

- Normalize tags to use layer number and name
  ([`ea5ef9d`](https://github.com/DataLabTechTV/datalab/commit/ea5ef9db0a64d6cce4f50c634b9690523e565bce))

- Postgres root password config
  ([`34bfb06`](https://github.com/DataLabTechTV/datalab/commit/34bfb064554d5437258d974e3ec2618e23949f5d))

- **deps**: Add http provider
  ([`0f90970`](https://github.com/DataLabTechTV/datalab/commit/0f90970c77dbe1bcb7939268ba3286c31a58de50))

- **deps**: Update uv.lock with the latest datalab version
  ([`5f3c233`](https://github.com/DataLabTechTV/datalab/commit/5f3c23387c972f6614134ebec624c2b862e55eac))

### Continuous Integration

- Add explicit stage to postgres template
  ([`840c4f8`](https://github.com/DataLabTechTV/datalab/commit/840c4f8db1289d8b69999bcbba086c77649132f3))

- Add explicit stages block
  ([`b7ee333`](https://github.com/DataLabTechTV/datalab/commit/b7ee3338775e5101160b24fb04cd69afdcefeed4))

- Add explicit stages to kafka and ollama templates
  ([`b56bd57`](https://github.com/DataLabTechTV/datalab/commit/b56bd5706db8420e53fd2f64960d60f7907abd83))

- Add missing provision stage
  ([`f2091c6`](https://github.com/DataLabTechTV/datalab/commit/f2091c6eae13177c42d0652d4eb1a7493008505e))

- Add missing stage
  ([`abe9df5`](https://github.com/DataLabTechTV/datalab/commit/abe9df55c398ae901f386f2e7d56f027496129fc))

- Automated apps deployment
  ([`39facd0`](https://github.com/DataLabTechTV/datalab/commit/39facd017c31f9331158fe67a6369040e0044cb7))

- Change entry point to force trigger
  ([`9a86ada`](https://github.com/DataLabTechTV/datalab/commit/9a86adac6d1a1c879d3742b76a978d9af5615772))

- Change entry point to force trigger
  ([`093a8a9`](https://github.com/DataLabTechTV/datalab/commit/093a8a9f0425d81aad2a34debad4f43c1fc779d5))

- Create_db now returns a credentials.env file that expires in 15 min
  ([`ed66f69`](https://github.com/DataLabTechTV/datalab/commit/ed66f69a81754c8292c60a3ada7d4b308c72adad))

- Deploy job only runs when services are changed
  ([`cc857df`](https://github.com/DataLabTechTV/datalab/commit/cc857df71b8c39f152f549acad0e048a623834df))

- Docker compose stack update
  ([`6785af2`](https://github.com/DataLabTechTV/datalab/commit/6785af2e62f93fd35f60ab36f84c4e2d9e9c7523))

- Drop intermediary job
  ([`d3649c4`](https://github.com/DataLabTechTV/datalab/commit/d3649c46897794265541ba04477b27ea79f90b9a))

- Ensure both topics are created
  ([`6668b22`](https://github.com/DataLabTechTV/datalab/commit/6668b228da7fcc9838521be80fb2ebdce28df47d))

- Fix changes rule with matches to files
  ([`08c6d1d`](https://github.com/DataLabTechTV/datalab/commit/08c6d1dd08066c1551a8704e9264f034969ccb77))

- Fix syntax for manual triggering conditions
  ([`33d667b`](https://github.com/DataLabTechTV/datalab/commit/33d667b7d0935ecb900d4edd3ef37e5e1f3d57fb))

- Implement kafka topic and topic consumer group creation
  ([`cd3f8ea`](https://github.com/DataLabTechTV/datalab/commit/cd3f8ea5447fda6e502ac292b85bd11361a4aec1))

- Implement ollama model pull
  ([`2956c09`](https://github.com/DataLabTechTV/datalab/commit/2956c09ab5afe973b85d2390d144e52cb1a89831))

- Improve logging messages
  ([`30f9b31`](https://github.com/DataLabTechTV/datalab/commit/30f9b31e28b8e62cd421919d2c04766d67760e69))

- Kafka and ollama provisioner templates to use on external projects
  ([`e1acd62`](https://github.com/DataLabTechTV/datalab/commit/e1acd6254a87a0486715d0df19e9c7d19abf0dd9))

- Manual trigger option for services and apps deployment
  ([`685ecda`](https://github.com/DataLabTechTV/datalab/commit/685ecda9c6926412989091f8a513fbcf9ea13abf))

- Missing variable name for update
  ([`cadf82c`](https://github.com/DataLabTechTV/datalab/commit/cadf82cce83f7a0679399eb8970eaa94ead76c4d))

- Posgres provisioning job template for including on other projects
  ([`2c3008e`](https://github.com/DataLabTechTV/datalab/commit/2c3008efdeff847da4731f9495e96be3181a2be0))

- Postgres user and db creation, kafka initial setup
  ([`1cd1ec2`](https://github.com/DataLabTechTV/datalab/commit/1cd1ec289a7421f66d99d52f06b8f0572fb4f609))

- Provision kafka topics and groups explicitly for the mlserver app
  ([`fdaeaa0`](https://github.com/DataLabTechTV/datalab/commit/fdaeaa018b51e5833375f3bf325bae6854a6e527))

- Refactor so variables are on top
  ([`bfb8847`](https://github.com/DataLabTechTV/datalab/commit/bfb88478075165c4eab2d1911820991b8296780a))

- Refactor with more general job names
  ([`c04c149`](https://github.com/DataLabTechTV/datalab/commit/c04c1490064f043cb7c5141a39b01a0df3244f44))

- Remove redundant when manual that was blocking the job
  ([`d4f7305`](https://github.com/DataLabTechTV/datalab/commit/d4f7305f5be6bc8a4729b79536d8c47aebd9ae45))

- Remove unrequired sleep
  ([`1bab0dc`](https://github.com/DataLabTechTV/datalab/commit/1bab0dcd246a5d63221910310dd382b081c4add2))

- Replace before_script with custom ubuntu image
  ([`6271461`](https://github.com/DataLabTechTV/datalab/commit/627146151c14b620a8d6622bb65bd5d9ee3333b5))

- Reproduce rules from apps deploy job
  ([`f40fde4`](https://github.com/DataLabTechTV/datalab/commit/f40fde43ee1fe1a2f12cf219207624efab75baca))

- Rollback to production topic and group names
  ([`2dc2e6b`](https://github.com/DataLabTechTV/datalab/commit/2dc2e6b9044d867d9cb4d39a87895e8e1366e097))

- Soft fail when db exists
  ([`82415ba`](https://github.com/DataLabTechTV/datalab/commit/82415ba2e1a57e5f3648c6b8f43f9660c69bc96e))

- Stub for ollama jobs
  ([`17ee3de`](https://github.com/DataLabTechTV/datalab/commit/17ee3de2df929d6d5d5ed4b3e3460b997128daa5))

- Switch back to inline scripts for postgres
  ([`59f7e81`](https://github.com/DataLabTechTV/datalab/commit/59f7e81d7961ffa4dea802fd4c126749b5a6aa9a))

- Testing docker access
  ([`92c35d1`](https://github.com/DataLabTechTV/datalab/commit/92c35d13fa35385d937ee7f3d931a1655e56a066))

- Testing file list
  ([`f6257bd`](https://github.com/DataLabTechTV/datalab/commit/f6257bd1613aa3409a014b6a088d41f0822da1dd))

- Testing topic and group provisioning
  ([`92eba7a`](https://github.com/DataLabTechTV/datalab/commit/92eba7a8b11b6d09c528a092fd519daf67b5be8e))

- Trigger on changes to the deploy template
  ([`01e1048`](https://github.com/DataLabTechTV/datalab/commit/01e1048b287a4943499d110a7657731956710a8d))

- Upsert behavior for PSQL_SECRETS
  ([`efc00ba`](https://github.com/DataLabTechTV/datalab/commit/efc00ba55f3c1ff0da87cb279de1604072d6ea58))

- **fix**: Missing backslash
  ([`8627b5c`](https://github.com/DataLabTechTV/datalab/commit/8627b5c7f466a11c18a0e6c87be1bb002f4ea055))

- **fix**: Remove -it from docker command
  ([`eadcdab`](https://github.com/DataLabTechTV/datalab/commit/eadcdabd7c65312438b9a599bbfe5e5828ba385c))

- **fix**: Single line command
  ([`024fc4a`](https://github.com/DataLabTechTV/datalab/commit/024fc4ac299bd3d9c136786eaf9e46af78a57e9b))

- **fix**: Try again
  ([`eab2623`](https://github.com/DataLabTechTV/datalab/commit/eab26231a4550a3fee727996ab6885a7d661efab))

- **refactor**: Clarify log message
  ([`1e2a976`](https://github.com/DataLabTechTV/datalab/commit/1e2a976863721d225cc95a279dbfb88a545e51f8))

- **refactor**: Improve description
  ([`c2f5472`](https://github.com/DataLabTechTV/datalab/commit/c2f5472f4e43a7d164aef7b4f727e77f0ef87608))

- **refactor**: Rename job to init consumer
  ([`bcaedb5`](https://github.com/DataLabTechTV/datalab/commit/bcaedb5ae6eb2698a30caf08b9bdeb16e129ee10))

### Documentation

- Update requirements and quick start
  ([`b1ef974`](https://github.com/DataLabTechTV/datalab/commit/b1ef974c2e09b41bd41444df23040bd86f9de3af))

- Update with latest workflows and add missing documentation
  ([`ba48b98`](https://github.com/DataLabTechTV/datalab/commit/ba48b987d198c5788527e054b31a7d7528a7c91b))

- Add missing requirements. - Add missing ml/ and infra/ components. - Add missing shared/ modules.
  - Add PosgreSQL dotenv config. - Add missing dotenv configs: datalab, DuckLake, Kuzu, Ollama,
  MLflow, and Kafka. - Add docs for CLI test and docs commands. - Add docs for ML CLI commands. -
  Add just commands documentation.

### Features

- Add confirmation task, destroy services but never volumes
  ([`43fa345`](https://github.com/DataLabTechTV/datalab/commit/43fa34553558496036b310e6187faf14b8167a33))

- Add custom image for gitlab runner
  ([`91c86ae`](https://github.com/DataLabTechTV/datalab/commit/91c86ae4298127d246a02d4c9ef469c11cd2f536))

- Add GITLAB_TOKEN to CI/CD variables
  ([`2602d5b`](https://github.com/DataLabTechTV/datalab/commit/2602d5b05af043e2497800e626e74aa882073f57))

- Add missing docker configs to use the nvidia gpu
  ([`a005a68`](https://github.com/DataLabTechTV/datalab/commit/a005a681e2735a0f3022c3f6710c0ae79dc7f4fa))

- Add missing registry config and configure a remote docker gitlab runner
  ([`81784cd`](https://github.com/DataLabTechTV/datalab/commit/81784cd5d70233deaf8088eb5bb7887f2ed70280))

- Add open webui and switch to plain http on portainer
  ([`4c23e64`](https://github.com/DataLabTechTV/datalab/commit/4c23e6407f13e1397226b3f1fdc5a5b3b6540897))

- Add volume to open webui for persistence
  ([`0d4c883`](https://github.com/DataLabTechTV/datalab/commit/0d4c883b2bda61eb4bfb4690254c8fcee98564dd))

- Basic Docker VM provisioning (untested)
  ([`1f2f7fd`](https://github.com/DataLabTechTV/datalab/commit/1f2f7fd8d13f5b9201be1b248faa34dff6e6e1b6))

- Basic gitlab-terraform project to handle CI/CD variables
  ([`1e04c04`](https://github.com/DataLabTechTV/datalab/commit/1e04c04630b51ed2b8fd931dff3a765bf744e427))

- Basic Terraform project with stored state using S3 backend
  ([`d14b5cb`](https://github.com/DataLabTechTV/datalab/commit/d14b5cb7741ed01a99f43c68fc459103acd664a3))

- Basic Terraform setup for provisioning an LXC running MinIO on Proxmox
  ([`60cb6b2`](https://github.com/DataLabTechTV/datalab/commit/60cb6b2dff96b5cbe8f85d7485d085fdf033f226))

- Change to official open-webui image and preconfigure the ollama endpoint
  ([`fd56c92`](https://github.com/DataLabTechTV/datalab/commit/fd56c92cce1b91f014700ce3be6bfbc1645e063a))

- Configs now done via gitlab.rb directly, added container registry
  ([`1a79081`](https://github.com/DataLabTechTV/datalab/commit/1a79081511930679b64462163c451ec9ceee925e))

- Data lab infra config check tasks
  ([`b861d95`](https://github.com/DataLabTechTV/datalab/commit/b861d957da14de2c2f37f316826436d75a6995ed))

- Disable usage tracking and user creation, remove unused gitlab-env, and fix indentation
  ([`4c2333a`](https://github.com/DataLabTechTV/datalab/commit/4c2333a5483f211a3a400d2de76a2db824240b95))

- Dockerized ml server
  ([`544427f`](https://github.com/DataLabTechTV/datalab/commit/544427ff926adcda399662ec7defcab756064842))

- Dotenv loading into gitlab ci/cd vars now working
  ([`1dd5691`](https://github.com/DataLabTechTV/datalab/commit/1dd569132ba786f3e6726459bc500e5073d271bb))

- Env var configurable topics and consumer groups
  ([`87d7b55`](https://github.com/DataLabTechTV/datalab/commit/87d7b55beb14636f1044f188d67642be13598042))

- Extract MinIO environment variables from the install script into Terraform and produce random
  passwords
  ([`d6ab46e`](https://github.com/DataLabTechTV/datalab/commit/d6ab46e2c95954a3fd9d9ba263c1a3eead4f6270))

- First gitlab working deployment, and docker and gitlab now split into separate tf files
  ([`09a7ca0`](https://github.com/DataLabTechTV/datalab/commit/09a7ca097c9599048fdac7f5862f3b3b98b9a78d))

- Gpu passthrough for docker-shared VM
  ([`12eecef`](https://github.com/DataLabTechTV/datalab/commit/12eecefeda53a0ef906e5f2f78cc565aea8e0cf3))

- Improve error control and add credentials printing task
  ([`406f5b8`](https://github.com/DataLabTechTV/datalab/commit/406f5b899776d550e347d730cdee2f6ed09f10e5))

- Improve postgres workflow for credentials and db creation
  ([`ac7c573`](https://github.com/DataLabTechTV/datalab/commit/ac7c57387f183389f6b01317392ab2e7cf46fd5e))

- Optional NVIDIA driver install for Docker VMs (cloud-config now a template)
  ([`8a2abfb`](https://github.com/DataLabTechTV/datalab/commit/8a2abfb3a78f3b44a8a1077ab7b7f81e1b912a65))

- Overall task cleanup, add infra provisioning for services layer and destruction tasks
  ([`f88158c`](https://github.com/DataLabTechTV/datalab/commit/f88158c7fd0116f2f71e0ad2153b28ff7bff08f1))

- Postgres deployment
  ([`f8f7db2`](https://github.com/DataLabTechTV/datalab/commit/f8f7db2cf8f4bea706c73f617697b123dae42793))

- Preconfigure gitlab container registry as an insecure registry for all docker vms
  ([`5520d35`](https://github.com/DataLabTechTV/datalab/commit/5520d3528b129bffe2b97f1685ca121396bf7759))

- Refactor docker-compose.yml into the services layer compose file, adding portainer and limiting
  minio to the dev profile
  ([`fcb43e0`](https://github.com/DataLabTechTV/datalab/commit/fcb43e040bcf51fc8934a3b6644599d877dc3b44))

BREAKING CHANGE: There no longer is a docker-compose.yml, as it will be integrated into
  infra/services/docker/compose.yml with MinIO available only under the dev project.

- S3 config variables (required by gitlab)
  ([`a544409`](https://github.com/DataLabTechTV/datalab/commit/a5444094348a0259b05c8d20a2238c19476e59bc))

- Set a fixed port for MinIO's console
  ([`78741fe`](https://github.com/DataLabTechTV/datalab/commit/78741fee86f7caa8d78095d1a49c3c6593c5f985))

- Simplify showing credentials and add validation
  ([`d0a7d36`](https://github.com/DataLabTechTV/datalab/commit/d0a7d362a03661dcd1fdfa07a194a4a8da7946a4))

- Simplify the way the custom docker context is accessed
  ([`57977f4`](https://github.com/DataLabTechTV/datalab/commit/57977f4e3cd1ff24fa5abcaa7b28cbe46bba64ca))

- Tcp listening for remote access
  ([`a0caf5a`](https://github.com/DataLabTechTV/datalab/commit/a0caf5a7d8e5ef3fdb2de43262189882b8d30a0b))

- Update PSQL_SECRETS env var
  ([`0dbd79d`](https://github.com/DataLabTechTV/datalab/commit/0dbd79d53f0b1f37a7e2fec50de7742bd89b0e0d))

### Refactoring

- Better defaults, less redundant title comments
  ([`6c3f42b`](https://github.com/DataLabTechTV/datalab/commit/6c3f42b2883d7cca1eeb8dbc7c69884e3de6117f))

- Explicitly use true/false for masked and improve formatting
  ([`4e63668`](https://github.com/DataLabTechTV/datalab/commit/4e63668b77ae0e523036121e410b90fc44faae6a))

- Extract scripts from templates
  ([`cdf5283`](https://github.com/DataLabTechTV/datalab/commit/cdf52838d0887f8f810e0040d24eaa08c1837fed))

- Fix linting issues
  ([`01bdae2`](https://github.com/DataLabTechTV/datalab/commit/01bdae2c7740f367d40147e73a8ce1f501979317))

- Make it clear that create database can safely fail
  ([`9fff4c1`](https://github.com/DataLabTechTV/datalab/commit/9fff4c1b5b55569881ed443d707bc2f78cd6c54b))

- Move services docker files into its own directory
  ([`2ae6fee`](https://github.com/DataLabTechTV/datalab/commit/2ae6fee4e5e1489d6ff4aa3aa80b4ad2a2f9a7e6))

- Normalize comment title formatting
  ([`9b255d3`](https://github.com/DataLabTechTV/datalab/commit/9b255d335bb23b302b47b4179bcc51d51da42881))

- Remove explicit user
  ([`9d2118a`](https://github.com/DataLabTechTV/datalab/commit/9d2118a542f65523fcf10a55e87187ec920f63c2))

- Rename the container resource to minio
  ([`3c41783`](https://github.com/DataLabTechTV/datalab/commit/3c417838d6c48d673216bc50fd642770196a907d))

- Rename to gitlab
  ([`c2c383c`](https://github.com/DataLabTechTV/datalab/commit/c2c383c5e0825361b6aa970269f2646f0c147d28))

- Rollback to inline scripts, move templates to root of dotci
  ([`f0d12b8`](https://github.com/DataLabTechTV/datalab/commit/f0d12b8141a09e231a5ed69c697c0fd75265c963))

- Split docker vm passwords into multiple outputs again
  ([`23b4cbe`](https://github.com/DataLabTechTV/datalab/commit/23b4cbe57634161cc494891bd20567645170f6ba))

- Split script into multiple lines for psql_create_db
  ([`10444ff`](https://github.com/DataLabTechTV/datalab/commit/10444ff76f7a3ec5e00412756e919d7de874c7a4))

- Switch to single rootfs volume and improve resource naming
  ([`f773714`](https://github.com/DataLabTechTV/datalab/commit/f7737143005d908869a67703af4a837e3d3864ba))


## v0.7.0 (2025-08-28)

### Bug Fixes

- Lakehouse is now a singleton, to avoid initialization when running the help command
  ([`ca5a7ea`](https://github.com/DataLabTechTV/datalab/commit/ca5a7ea9cde99ec0c19201e2a8828a1fc01dec97))

- Normalize loggers to use loguru via an intercept handler
  ([`d18f572`](https://github.com/DataLabTechTV/datalab/commit/d18f572423d69966299de472e0e5b721d70f021d))

- Shift should be drift, and count plot should be stacked
  ([`62aefb2`](https://github.com/DataLabTechTV/datalab/commit/62aefb28ff089e38d736e544043b7b5992df1d00))

### Chores

- Add a default task that lists all just tasks
  ([`897c520`](https://github.com/DataLabTechTV/datalab/commit/897c520c1e9714f4b6af2a7378ce803244ab0c59))

- Add missing help message and fix the one for ml monitor plot
  ([`7b17e14`](https://github.com/DataLabTechTV/datalab/commit/7b17e14f9f98a93decae7150c41a724a0b9dbbe9))

### Features

- Improve performance of REST API by moving Kafka payload queueing to the background
  ([`2fe859d`](https://github.com/DataLabTechTV/datalab/commit/2fe859d28aa6156fdf261d65f03c208b00367572))

### Refactoring

- Drop unused matplotlib imports
  ([`48b9e31`](https://github.com/DataLabTechTV/datalab/commit/48b9e3115fee7717c914f942c7d953a6bbded0ce))

- Remove unused imports
  ([`f1f8a1f`](https://github.com/DataLabTechTV/datalab/commit/f1f8a1f89828c910c82b62b2287a7b5cf4b50401))


## v0.6.0 (2025-08-25)

### Bug Fixes

- Attempt to solve group coordinator errors
  ([`25e9cf1`](https://github.com/DataLabTechTV/datalab/commit/25e9cf1d137824e9370c4b39305cb72d2af61e38))

- Capture asyncio cancel exception
  ([`5f5f07f`](https://github.com/DataLabTechTV/datalab/commit/5f5f07f9fc67a84d218621b1b1212cb3e736390e))

- Consumer task was meant to be awaited from inside the loop
  ([`0bede44`](https://github.com/DataLabTechTV/datalab/commit/0bede44dee55e854b62eb8c25d03ab0d6a684ea7))

- Correct model uri scheme
  ([`a6c589b`](https://github.com/DataLabTechTV/datalab/commit/a6c589be80a8ea6cb4c4cf5d47499862aae67f74))

- Dataframe was being forced through the model loaded using mlflow.pyfunc.load, so now we handle
  multiple input types
  ([`4d9541e`](https://github.com/DataLabTechTV/datalab/commit/4d9541ee071beef230489a9c58967fefd87f576a))

- Handle failed runs and drop unrequired columns from logged inputs
  ([`29f9259`](https://github.com/DataLabTechTV/datalab/commit/29f92595ccf6aee8a99ee83d51f3bcf3890da1d7))

- Kafka now runs and initializes properly
  ([`b94dfc4`](https://github.com/DataLabTechTV/datalab/commit/b94dfc49eac632b8379269a3ebde2d2d5e7df207))

- Mlflow healthcheck, switch to kafka's official image
  ([`cea3edf`](https://github.com/DataLabTechTV/datalab/commit/cea3edff3d9c077e59670dff67a8b8751d076424))

- Model needs to be initialized every time, otherwise there is a memory leak
  ([`e53c85f`](https://github.com/DataLabTechTV/datalab/commit/e53c85f36d0a323a582cca7fa81cb1db2ade0742))

- Move mlflow.db to root since db directory didn't exist
  ([`3fed7f1`](https://github.com/DataLabTechTV/datalab/commit/3fed7f1b03570b3ee58b80f381af43c230ad61b6))

- Ollama will now default to CPU when GPU is not available
  ([`a13fd72`](https://github.com/DataLabTechTV/datalab/commit/a13fd72258d7d4e96320bc70cdfa506516a101c6))

This will, most likely, make it unusable, but at least it won't stop the other services from
  starting and working as expected.

- Positive label probability selection
  ([`00d738e`](https://github.com/DataLabTechTV/datalab/commit/00d738e843528957359b207650f52f0363a9a7a1))

- Queue logic incompatible with list logic, always flush in the end
  ([`9d59f90`](https://github.com/DataLabTechTV/datalab/commit/9d59f90bfc56b8920725ac24ec1ec35a50548970))

- Requests cache was causing memory overload
  ([`b734e08`](https://github.com/DataLabTechTV/datalab/commit/b734e0869456a3dcdc91951af26dac7a090bffc9))

- Schema name, remove unused tasks
  ([`e1944fa`](https://github.com/DataLabTechTV/datalab/commit/e1944fac63c757c1e32b194e19a5dd82b1000e94))

- Train/test split now separate from cross-validation (train only)
  ([`11b448e`](https://github.com/DataLabTechTV/datalab/commit/11b448e8e980439006d365ae9336025775befa38))

- Transform failed when other datasets were not ingested
  ([`029e8c4`](https://github.com/DataLabTechTV/datalab/commit/029e8c49eb5328732fc3947519b06f37e6e3ac53))

- Update to new lakehouse schema
  ([`1240dc9`](https://github.com/DataLabTechTV/datalab/commit/1240dc9d691e558f7ac7f37f4fefcf4c3c5463d2))

- Update to new ml types and lakehouse schema
  ([`063d28b`](https://github.com/DataLabTechTV/datalab/commit/063d28b5aa7142dbdddd763998d23cd2284edb15))

### Chores

- Add a second topic for updating inference results with user feedback
  ([`6abb221`](https://github.com/DataLabTechTV/datalab/commit/6abb221689d5fe272917933b1a284f5aba6a606e))

- Add config for new stage catalog with secure storage
  ([`1009792`](https://github.com/DataLabTechTV/datalab/commit/10097927143ec3efdc8980a39affbb08dfdae2f4))

- Add config for pairs of topic and expected consumer group
  ([`6224c6c`](https://github.com/DataLabTechTV/datalab/commit/6224c6c11af50112bfd945fb1e5d0021a83e6065))

- Add config for stage catalog with secure storage
  ([`7d3fbb9`](https://github.com/DataLabTechTV/datalab/commit/7d3fbb94ded24d1cabadca9d894bb262e06bebe9))

- Add kafka config section
  ([`175474f`](https://github.com/DataLabTechTV/datalab/commit/175474fa985c687942c4794b5668ec0b64068a15))

- Add name to each asyncio task
  ([`dad0fbe`](https://github.com/DataLabTechTV/datalab/commit/dad0fbe981c6d36a62c4b3b658f6d425d84a6d9b))

- Create justfile with tasks from previous and upcoming videos
  ([`9289e70`](https://github.com/DataLabTechTV/datalab/commit/9289e706cf523caffc9f9fbe147a730796d863a3))

- Delete unused test module
  ([`04964ef`](https://github.com/DataLabTechTV/datalab/commit/04964ef7b971a754bfdf1049de3f114a0c8a2cd1))

- Reduce sample fraction
  ([`a9ab9a7`](https://github.com/DataLabTechTV/datalab/commit/a9ab9a79b92ee2cb8d6796ba0f5819ec66dbbb9b))

- Rename insert/update to result/feedback to match new event topics
  ([`4ae3ef1`](https://github.com/DataLabTechTV/datalab/commit/4ae3ef1565c09d9a93f007cfe4926a27826949fb))

- Setup mlflow service with sqlite and s3
  ([`3a0f1ca`](https://github.com/DataLabTechTV/datalab/commit/3a0f1ca0916846ab662495110b316f12a0fcc44b))

- **deps**: Add anyascii and inflection for a more robust sanitization, add just for task running,
  add xgboost for ML project
  ([`17cbf48`](https://github.com/DataLabTechTV/datalab/commit/17cbf48ca452a0b045fc4dc2cec0002503e1a9b9))

- **deps**: Add faker to create random dates
  ([`0814e54`](https://github.com/DataLabTechTV/datalab/commit/0814e545c1dcf092f5c20139f0e8366b0dfc98bf))

- **deps**: Add fastapi and uvicorn for the ml server
  ([`5907a38`](https://github.com/DataLabTechTV/datalab/commit/5907a38aaeee23b959bc81510c9b3cd71fe84eea))

- **deps**: Add joblib to use Memory for caching
  ([`1676db1`](https://github.com/DataLabTechTV/datalab/commit/1676db1a8ab2cee1a63a543dcf4e9c08db2eb870))

- **deps**: Add kafka official library
  ([`2de36e8`](https://github.com/DataLabTechTV/datalab/commit/2de36e82267e49cefe19500fd98c6d6605a22ee3))

- **deps**: Add mlflow
  ([`5d0b94a`](https://github.com/DataLabTechTV/datalab/commit/5d0b94acacd7cdd03bb0cd195b4e838b29e7f1a0))

- **deps**: Add pip so its version is properly detected by mlflow during model logging
  ([`63edc5a`](https://github.com/DataLabTechTV/datalab/commit/63edc5a058202895f43a6504d89032eb48c7378d))

- **deps**: Add scikit-learn
  ([`204411b`](https://github.com/DataLabTechTV/datalab/commit/204411b2a8940e5a6211738486d44f304ce344f3))

- **deps**: Add sentence transformers for text embedding
  ([`0a852d8`](https://github.com/DataLabTechTV/datalab/commit/0a852d8dcf404988371318f8216d28f031d29bcc))

- **deps**: Downgrade from 3.0.3 to 3.0.2 due to mlflow compatibility
  ([`8e2d1bd`](https://github.com/DataLabTechTV/datalab/commit/8e2d1bd23c0fbbd0ec575a7ef08810d089a138d8))

- **deps**: Replace confluent-kafka with aiokafka
  ([`a052aa8`](https://github.com/DataLabTechTV/datalab/commit/a052aa8a5249693ca6e2aa2dca1a1ede4e040ed5))

### Features

- Add 3-folds
  ([`9c58bfb`](https://github.com/DataLabTechTV/datalab/commit/9c58bfb61d988ebf21222fb453cdcb20f73ead57))

- Add create_at timestamp that defaults to the current date
  ([`6badaf2`](https://github.com/DataLabTechTV/datalab/commit/6badaf291bae580166181179d7f3578b47d4cd44))

- Add custom MLflow user for tracking
  ([`4818df8`](https://github.com/DataLabTechTV/datalab/commit/4818df818699f98396aa917e424f7ae398dfe657))

- Add model logging to mlflow_end_run
  ([`54027f2`](https://github.com/DataLabTechTV/datalab/commit/54027f2741c082064cf7efc6ac8de82128e0c2fb))

- Add monitor compute task
  ([`36d2b91`](https://github.com/DataLabTechTV/datalab/commit/36d2b91665c094d00514412a622747bb777d5532))

- Add monitor dataset to mlops etl pipeline
  ([`c227f62`](https://github.com/DataLabTechTV/datalab/commit/c227f62ba537a1e8402b9484922a7385c228eaa8))

- Add monitor plot task
  ([`27bd6bb`](https://github.com/DataLabTechTV/datalab/commit/27bd6bbc64584ed734952c89e84d93575f9fa698))

- Add reload option to use during development
  ([`5e175ad`](https://github.com/DataLabTechTV/datalab/commit/5e175ad042b76f45a59fa1a4ffcee114663ef666))

- Add sample fraction parameter
  ([`813f031`](https://github.com/DataLabTechTV/datalab/commit/813f0310b4e5ad76e67164b79d8ee3bdff5405dc))

- Add train and test tasks, update ETL task with transformation
  ([`54e1adb`](https://github.com/DataLabTechTV/datalab/commit/54e1adb47785e5210740f4aed6db0fc9211765a9))

- Apache Kafka server
  ([`b2acb5d`](https://github.com/DataLabTechTV/datalab/commit/b2acb5d07772b5f78752ce92056825a62b81bf17))

- Basic training pipelines and CLI command
  ([`e27cc5d`](https://github.com/DataLabTechTV/datalab/commit/e27cc5d23fc00ed5b256ace35ccbcc90f6aeabbe))

- Check for curl and add -f to ensure the task fails when status code is >= 400
  ([`b02c5a1`](https://github.com/DataLabTechTV/datalab/commit/b02c5a173e26cc68129322f03e47d89a9c790d8d))

- Default to 3-folds, since it is now supported
  ([`daf3db9`](https://github.com/DataLabTechTV/datalab/commit/daf3db9d704b3099337573c27a4ec6ff0989ec84))

- Drop tasks for mlflow model server (images are too bloated)
  ([`c20ec10`](https://github.com/DataLabTechTV/datalab/commit/c20ec107afb91887a3ca54d97c560b38ecbd76ce))

- Enable artifacts proxy and install boto3 as a dependency
  ([`8e844a6`](https://github.com/DataLabTechTV/datalab/commit/8e844a606b187e7e4b61782874d0eeba90961e66))

- End-to-end kafka producer/consumer implementation
  ([`c1fbbc6`](https://github.com/DataLabTechTV/datalab/commit/c1fbbc6c6bebf731fbccdbb5a93af9d1e30ee3a2))

- Endpoint to flush inference log, refactor inference request to handle A/B/n testing
  ([`8ba2a7e`](https://github.com/DataLabTechTV/datalab/commit/8ba2a7e624ee726014ee8bf698f12c2024dda637))

- Feature pipelines for TF-IDF and sentence transformers
  ([`70c4182`](https://github.com/DataLabTechTV/datalab/commit/70c41823414c9fe58ae382b39c26d62271aa73ff))

- Feedback is now an array and created_at keeps track of time
  ([`19d0527`](https://github.com/DataLabTechTV/datalab/commit/19d052771994d0a7d44c1618782e94a862c04fc6))

- Generic ml dataset loader function
  ([`f364327`](https://github.com/DataLabTechTV/datalab/commit/f364327b69c41a9961d9d93cf6ce143908e66c1e))

- Health check endpoint, and refactor insert/update to results/feedback for clarity
  ([`d00f612`](https://github.com/DataLabTechTV/datalab/commit/d00f612286dc8447bee1dc66bb42a9915f8c6635))

- Implement dataset transformation with train/test split and 5-folds and 10-folds
  ([`3e552e0`](https://github.com/DataLabTechTV/datalab/commit/3e552e0ce5d0cf3f9ee5e6d042ae951e3ac46eda))

- Implement scaffolding for monitoring statistics computation class and count stat
  ([`6d25335`](https://github.com/DataLabTechTV/datalab/commit/6d25335782585dbacf08bf801f7a09a263dff14a))

- Inference API request
  ([`ccbc242`](https://github.com/DataLabTechTV/datalab/commit/ccbc242425bd9dfb146e0dd14b90f103cd54da70))

- Inference feedback update workflow
  ([`9127a92`](https://github.com/DataLabTechTV/datalab/commit/9127a9281029aa5483cd6131c6edf0c413504c8e))

- Load ml inference results for a date range
  ([`d6df078`](https://github.com/DataLabTechTV/datalab/commit/d6df07856df76286efed2029d46ea9459a4c2f54))

- Load monitor stats
  ([`5969151`](https://github.com/DataLabTechTV/datalab/commit/5969151253ea78c5dd528928645eb26546fceec3))

- Ml monitor is now ml monitor compute and since/until are unspecificed by default
  ([`5e66a95`](https://github.com/DataLabTechTV/datalab/commit/5e66a955d3d086998b1eedc2eba07f6690c1c920))

- Ml monitor plot command
  ([`9dc514c`](https://github.com/DataLabTechTV/datalab/commit/9dc514c6c364acc47a3c4248c4f1df2c075e8e56))

- Ml server start command
  ([`3261c06`](https://github.com/DataLabTechTV/datalab/commit/3261c0627ab8a0a625adf34f0a8907181bc89e97))

- Mlflow docker image building, container running and server testing tasks
  ([`054f499`](https://github.com/DataLabTechTV/datalab/commit/054f49909786f9c81204f91591d356b6f48aaed1))

- Mlflow tracking URI env var
  ([`5511986`](https://github.com/DataLabTechTV/datalab/commit/551198665ada7fb6f1d08dd6495e43bcdc8a3b54))

- Mlops train per method and features (added), split everything into individual tasks
  ([`1e897f3`](https://github.com/DataLabTechTV/datalab/commit/1e897f3c0c01fe22031026f84945e887e4fa1489))

- Monitoring metrics for prediction and feature drift, estimated performance, and user evaluation
  ([`72286b6`](https://github.com/DataLabTechTV/datalab/commit/72286b6f73f61c5232cef2981e590ce17e88b512))

- Now always the latest model is used to build the docker image
  ([`6fbb824`](https://github.com/DataLabTechTV/datalab/commit/6fbb8245a712e8ff14bf009d92fd5513b89aa679))

- Output is now probabilities, so threshold can be set externally
  ([`18d814a`](https://github.com/DataLabTechTV/datalab/commit/18d814a1a9eccc022b4c92fe85b3944bd511fd97))

- Payloads is now types and inference request contains one or multiple models
  ([`d7b31b7`](https://github.com/DataLabTechTV/datalab/commit/d7b31b720a6d69365abaf41bd0b46d419c62f737))

- Plotting for model monitoring statistics
  ([`f14d51e`](https://github.com/DataLabTechTV/datalab/commit/f14d51e0d1528d0678dd457db79eadaebde38bb2))

- Query latest snapshot_id (version)
  ([`779aa61`](https://github.com/DataLabTechTV/datalab/commit/779aa611b398d4ed1abc4c33d0da7bd647d8ec06))

- Replace slugify with custom sanitization alternative
  ([`cf437c3`](https://github.com/DataLabTechTV/datalab/commit/cf437c3bac95a330df317d46bc13bb247eedd798))

- Rolling prediction drift computation
  ([`29c439a`](https://github.com/DataLabTechTV/datalab/commit/29c439a53376f2dd8d0e47a236a402abd1ce3fac))

- Safer attach (if not exists only)
  ([`0ebf16d`](https://github.com/DataLabTechTV/datalab/commit/0ebf16d11a6d36086f8e044a4752cf48d8c85e83))

- Scaffolding for inference simulation and monitoring
  ([`5d78f5e`](https://github.com/DataLabTechTV/datalab/commit/5d78f5e49dbb213e5bde00eb83857a455fe69396))

- Scaffolding for ML CLI and workflow functions
  ([`647559f`](https://github.com/DataLabTechTV/datalab/commit/647559f025939ca0a2da5e61873d3b2dc7d6bbb6))

- Scaffolding for ml server
  ([`3f3d05d`](https://github.com/DataLabTechTV/datalab/commit/3f3d05dd5be373f3ce7d6da4afc6ac59892b9812))

- Schema and count functions, remove redundant initialization code (same as generate_init_sql)
  ([`b816c9b`](https://github.com/DataLabTechTV/datalab/commit/b816c9b946764d8e38c7dc423bafa66e147de3a4))

- Separate tracking from training logic, and use PandasDataset instead of custom dataset
  ([`80b895a`](https://github.com/DataLabTechTV/datalab/commit/80b895a069aca721b50cd78552bff68718c23817))

- Start consumer thread with ml server
  ([`7523cfb`](https://github.com/DataLabTechTV/datalab/commit/7523cfbd32fc9b2c483407d257dbd494411d02cd))

- Support for 3-fold dataset loading and CV training
  ([`106a6ef`](https://github.com/DataLabTechTV/datalab/commit/106a6ef36bc741699b7ebbd63d9179451acf1e0f))

- Support for catalogs with secure storage
  ([`e96ce72`](https://github.com/DataLabTechTV/datalab/commit/e96ce725077ca6a8031f174887b22538966b9961))

- Switch to expression api and make since/until optional, and implement loading for monitor stats
  ([`368d039`](https://github.com/DataLabTechTV/datalab/commit/368d0395693569a86e29a9c171ba7cc4ddc14930))

- Task to generate init SQL, also used on check fail, rename mlflow model server tasks, add
  mlops-serve task
  ([`a79c379`](https://github.com/DataLabTechTV/datalab/commit/a79c37940221c2ccb6c252e3a2ea6aaa4895b353))

- Task to run inference simulation using monitor dataset
  ([`fa48f2c`](https://github.com/DataLabTechTV/datalab/commit/fa48f2ca9271c7eecce3f7faa4004b27d3e4703a))

- Tasks to test inference and logging requests
  ([`cc1aa31`](https://github.com/DataLabTechTV/datalab/commit/cc1aa3146a9d16f251363ab80d15ad6172cf4837))

- Time tracking logging utils
  ([`d59abe4`](https://github.com/DataLabTechTV/datalab/commit/d59abe4a2e16063ef8fc2805772c7eaf4bdbb8eb))

- Train and test set loaders for document datasets
  ([`9bbd7c9`](https://github.com/DataLabTechTV/datalab/commit/9bbd7c94a2988be10ff02f9691c2649fa4c28420))

- Transformation for monitor depression dataset
  ([`5fb5d78`](https://github.com/DataLabTechTV/datalab/commit/5fb5d78fbe5bdf7db561bdfec3387c35757c3a1a))

- Update to new ml types, fix lakehouse collision with transform, and improve API to make flush
  usable externally
  ([`68ef918`](https://github.com/DataLabTechTV/datalab/commit/68ef9189663ebc235b9c024009af34a745fbcd03))

- Working inference simulation
  ([`6a3fcab`](https://github.com/DataLabTechTV/datalab/commit/6a3fcab63dcbce1692d533a1a269122261b40643))

### Refactoring

- Cleaner variable names and paths
  ([`1d52213`](https://github.com/DataLabTechTV/datalab/commit/1d52213df06ffff39afb79ec0b76c586bb9cae48))

- Correct and improve log messages
  ([`c8fc5ca`](https://github.com/DataLabTechTV/datalab/commit/c8fc5cac0f4a7f163aad2571b26c734c2b3f03d0))

- Easier naming for MLOps tasks
  ([`6ac1853`](https://github.com/DataLabTechTV/datalab/commit/6ac1853e1b60ec2a1ef2dfe9b8dab688b46fae57))

- Extract color functions into a shared module
  ([`6a859ef`](https://github.com/DataLabTechTV/datalab/commit/6a859efd2b666a754b7e0cf62015dc942d9c0096))

- Extract prediction from server to its own module using joblib Memory for cache
  ([`60467b7`](https://github.com/DataLabTechTV/datalab/commit/60467b717d21caf7addf64104f92b07652fbc8f6))

- Lakehouse logging is now the default
  ([`de16c77`](https://github.com/DataLabTechTV/datalab/commit/de16c77b00eb9f9581d16df7db12ebdd37b86409))

- Move server health check to server module
  ([`c63cd22`](https://github.com/DataLabTechTV/datalab/commit/c63cd22762b8947713ae23b78c890df028214bc0))

- Normalize method names and group by context
  ([`c01be6c`](https://github.com/DataLabTechTV/datalab/commit/c01be6c298df96bd2476cc3c88313e8c36e30adf))

- Normalize ml dataset column names and target type
  ([`bee2af9`](https://github.com/DataLabTechTV/datalab/commit/bee2af97cf5c756c6abed192bcfb4b7f09ffd612))

- Remove redundant case for computing the S3 prefix
  ([`b836af2`](https://github.com/DataLabTechTV/datalab/commit/b836af2d8ce3c1010ae18014eadb6497b0e5fe17))

- Remove unneeded echo
  ([`5e6dbb9`](https://github.com/DataLabTechTV/datalab/commit/5e6dbb907859380b32c94329359aae0887badcfe))

- Rename all init containers with init suffix
  ([`99e3939`](https://github.com/DataLabTechTV/datalab/commit/99e3939b4d13e7f209d578fa5d6037d391db5e1b))

- Rename n_folds to k_folds
  ([`b3ac002`](https://github.com/DataLabTechTV/datalab/commit/b3ac002e8857765ad01c9fdf25e6dbf692498e49))

- Set random model section log level to debug
  ([`228b805`](https://github.com/DataLabTechTV/datalab/commit/228b805d246f25e3c4c44cbfb7614eb75e8265ad))


## v0.5.0 (2025-08-05)

### Bug Fixes

- Any positive ESI is now considered competition, and is separate from intensity
  ([`25844f1`](https://github.com/DataLabTechTV/datalab/commit/25844f1433dc64148ebad3a6002968741175987e))

- Log file relative path to cwd failed when not directly contained using Path
  ([`e4f5b62`](https://github.com/DataLabTechTV/datalab/commit/e4f5b62468d240731e52f4066113eb55d96f321a))

### Chores

- Commit notebook generated during video recording
  ([`454d0dd`](https://github.com/DataLabTechTV/datalab/commit/454d0dd0b2eccf1bf2c1cbea43996a3c925d45a3))

- **deps**: Add adjustText to optionally fix rendering of overlapping node labels
  ([`36cbc33`](https://github.com/DataLabTechTV/datalab/commit/36cbc33dbbae6c8c73f29ff0f69ad3bd0de8ae72))

- **deps**: Add geopandas to plot maps
  ([`62d5ef1`](https://github.com/DataLabTechTV/datalab/commit/62d5ef1f54e970da0fa614a06f24e6363dc30d35))

- **deps**: Add jupyterlab, matplotlib, and networkx for graph data science
  ([`e29c08f`](https://github.com/DataLabTechTV/datalab/commit/e29c08fcf80f8ea6cb1a2b08732a1e1d8ca28d99))

- **deps**: Remove unneeded adjustText and add scipy back as a requirement for networkx layout
  computation
  ([`76ef5d4`](https://github.com/DataLabTechTV/datalab/commit/76ef5d40e64250da468c49327e90a5d67b96ec5c))

### Features

- Add CLI support for computing the CON score
  ([`8c94f6e`](https://github.com/DataLabTechTV/datalab/commit/8c94f6eebdda87a6233c467127ce72812eaffefc))

- Add edge arrows and node colors per label
  ([`ed56184`](https://github.com/DataLabTechTV/datalab/commit/ed561842696538ee51cc590b250dbee07f0588e6))

- Add graph analytics module, starting with a CON score
  ([`ff1f926`](https://github.com/DataLabTechTV/datalab/commit/ff1f92632e8f9073d29f1e51b89a93b797dd4bdc))

- Add graph transparency and improve labels
  ([`02dc859`](https://github.com/DataLabTechTV/datalab/commit/02dc859889c94beb7e810d953f7c083f3836f275))

- Add scale to arrow placement, add optional visualization weight
  ([`9190d2c`](https://github.com/DataLabTechTV/datalab/commit/9190d2ca25e86e19ace553f496d26fca0a53ee6d))

- Compare communities and components, study economical pressure
  ([`afceea8`](https://github.com/DataLabTechTV/datalab/commit/afceea8378a8d72bd62016b982f23ff293edba96))

- Competiton network analysis, including community and weak component analysis
  ([`62e54fd`](https://github.com/DataLabTechTV/datalab/commit/62e54fd56fa17cd3ada215401135456f9a106c9c))

- Create a basic graph theme matching DLT
  ([`3210fa5`](https://github.com/DataLabTechTV/datalab/commit/3210fa585450707b323dcf5ce9d69a44cfe9c2f7))

- Dominating and weaker economy individual analysis
  ([`986a2d6`](https://github.com/DataLabTechTV/datalab/commit/986a2d6a7c877468ce9ab7e38de54e68d9514e7b))

- Edge direction now based on common exports, from highest to lowest total amound
  ([`77325bd`](https://github.com/DataLabTechTV/datalab/commit/77325bdfa781f5a79fa122cc5d441cbb920cf09d))

- Improve graph plotting and add map plotting
  ([`266dfca`](https://github.com/DataLabTechTV/datalab/commit/266dfcaf682188ff16b8da01391c2dbcc245c893))

- Networkx graph plot helper to use with notebooks
  ([`a36b6c9`](https://github.com/DataLabTechTV/datalab/commit/a36b6c9eb482b095b62e91c162ee51ec25fb38b9))

- Revisted the whole notebook, restructuring and adding depth where needed
  ([`6a3dcb1`](https://github.com/DataLabTechTV/datalab/commit/6a3dcb1c05b3219645136bf8e654b44116fd133c))

- Script to easily convert Jupyter Notebooks to markdown
  ([`4b0c792`](https://github.com/DataLabTechTV/datalab/commit/4b0c792ae6ae56d030e814bf05bd3f08159a53e8))

- Set label w/ prop per node type and render label wo/ overlapping
  ([`8c0b6fb`](https://github.com/DataLabTechTV/datalab/commit/8c0b6fba1d2700a65346b878b1610ffa4e89d4a9))

- Setup notebook for graph data science
  ([`1d96e63`](https://github.com/DataLabTechTV/datalab/commit/1d96e63f79f68889701dbc4efefd08649f31d28b))

- Support for loading Parquet into DuckLake from Python
  ([`4035f63`](https://github.com/DataLabTechTV/datalab/commit/4035f6335698b3aef193c7b72275e9d58d9f9e4e))

- Trade alignment analysis
  ([`80d5ef1`](https://github.com/DataLabTechTV/datalab/commit/80d5ef1f702119f6d0e298d662c41bde4832172c))

- Trade alignment analysis (cont)
  ([`da6e848`](https://github.com/DataLabTechTV/datalab/commit/da6e848dff30ed7ef706fcaabbe951eb5dc09da4))

### Refactoring

- Different score reset strategy
  ([`d4d7d9d`](https://github.com/DataLabTechTV/datalab/commit/d4d7d9da4675ac86c47bb253764fef0840429683))

- No longer setting flags for dominating and weaker
  ([`d8013c4`](https://github.com/DataLabTechTV/datalab/commit/d8013c41c48645e1748649277a8b77a774641845))

- Remove unused import
  ([`65defb1`](https://github.com/DataLabTechTV/datalab/commit/65defb1d203a3a5e557a891c31ccc2dad8b826c6))

- Replace os.path ops with Path ops
  ([`84c73a9`](https://github.com/DataLabTechTV/datalab/commit/84c73a9de6fea587c95558aa84414d0c913d9c8a))

- Use kuzu extension instead of kz
  ([`d815cef`](https://github.com/DataLabTechTV/datalab/commit/d815cefe683c93636ddb4f931fefcc30c84b7b48))

- Use ref instead of hardcoded FQN
  ([`ba6de1a`](https://github.com/DataLabTechTV/datalab/commit/ba6de1afb81c635c0ca6d99edddde588588a373b))


## v0.4.0 (2025-07-16)

### Bug Fixes

- Add missing schema configs for new econ comp models
  ([`c4daafb`](https://github.com/DataLabTechTV/datalab/commit/c4daafbd574b0435041878fd210ae3951d94e1bc))

- Edges needed to be defined based on node_id, which required these changes
  ([`398ba70`](https://github.com/DataLabTechTV/datalab/commit/398ba70234661c77d32886269abd81cffc6366b6))

- Remove inexistent property
  ([`918f23a`](https://github.com/DataLabTechTV/datalab/commit/918f23ac5e2d901e448b51bc2d37456091eba3b2))

- Remove not null tests where they were not required
  ([`43efc61`](https://github.com/DataLabTechTV/datalab/commit/43efc6158b4c3789d00a409a690f9f1ce5b71d7c))

- Remove product parent relationship, as there is no multi-level data here
  ([`2d26651`](https://github.com/DataLabTechTV/datalab/commit/2d26651d7ccfca977887ca040ecf2c6d8d5dc30d))

- Remove repeated country pairs in reverse order
  ([`1f2f867`](https://github.com/DataLabTechTV/datalab/commit/1f2f8676223ac381204f58e65aa37457a0bc4eed))

- Required aggregation per country and product, disregarding partner
  ([`635dc72`](https://github.com/DataLabTechTV/datalab/commit/635dc729b0a38e345d34250decce67da378393c0))

- Types and missing null strings
  ([`40a79d7`](https://github.com/DataLabTechTV/datalab/commit/40a79d7bc851a17f06329c06a63220ce27059e19))

### Chores

- Add cypher script to compute music_taste graph stats
  ([`7a0a48d`](https://github.com/DataLabTechTV/datalab/commit/7a0a48de97fadc5a3963ec608005f55c785e9545))

- Add env var for econ comp graph db
  ([`3e34e80`](https://github.com/DataLabTechTV/datalab/commit/3e34e8023a15969250faae133805f02112e0b681))

- Configs for analytics mart
  ([`40dee56`](https://github.com/DataLabTechTV/datalab/commit/40dee562661fcdbdaaa7223e9dcfca4524b761a3))

- Re-enable requests-cache with streaming
  ([`62c7dff`](https://github.com/DataLabTechTV/datalab/commit/62c7dffe4aaa1d8c0d761bff3272fff98c5943c1))

- Rename KuzuDBs to match new single-file format
  ([`0e797ae`](https://github.com/DataLabTechTV/datalab/commit/0e797aeb5cc37b77421a0d1924cfec6b12e5a245))

- Simplify music taste graph stats script
  ([`5b964fb`](https://github.com/DataLabTechTV/datalab/commit/5b964fb926a5ef56aba139bb9649c1c8f7710442))

- Upgrade explorer script to work with kuzu 0.11.0
  ([`36f6cf7`](https://github.com/DataLabTechTV/datalab/commit/36f6cf77e5a24098058185dc194a60a363f00b51))

- **deps**: Add humanize to print byte sizes in human-readable format
  ([`6238484`](https://github.com/DataLabTechTV/datalab/commit/62384843681b5cf1a104a97c9e6acfc2d03a3343))

- **deps**: Add requests cache dep
  ([`b7c5fd5`](https://github.com/DataLabTechTV/datalab/commit/b7c5fd5f89e3c80ea4e46aeed3909721f787291d))

- **deps**: Add tqdm dep for tracking download progress
  ([`5e2ba51`](https://github.com/DataLabTechTV/datalab/commit/5e2ba51b9b37658f33f2ced693359cca5cb765f3))

- **deps**: Bump up kuzu to 0.11.0
  ([`74f2f4f`](https://github.com/DataLabTechTV/datalab/commit/74f2f4f171d45653138a666137e1a34487efef65))

- **deps**: Bump up version inside uv.lock
  ([`7124ff4`](https://github.com/DataLabTechTV/datalab/commit/7124ff4b0087f8cc49dfa47833e344b8e37ce4d9))

### Documentation

- Fill-in the missing schema models for analytics, and econ_comp nodes and edges
  ([`aa65fcd`](https://github.com/DataLabTechTV/datalab/commit/aa65fcda2420ef7e4c35e08f9ad4a049d411003c))

### Features

- Add model selection CLI option to test cmd
  ([`499bac0`](https://github.com/DataLabTechTV/datalab/commit/499bac02bcd0f1eb6e405ae1ffe0ba0f884b390c))

- Aggregated view for 2020-2023 trade covering recent years
  ([`c579742`](https://github.com/DataLabTechTV/datalab/commit/c579742c9d9fe6d2c22f1c74b12239f763bfd411))

- Cli command to expunge/clean cache
  ([`f412b51`](https://github.com/DataLabTechTV/datalab/commit/f412b5161ee405217722290b334f7817625127ec))

- Complete dataset template for The Atlas of Economic Complexity
  ([`6e2cb9c`](https://github.com/DataLabTechTV/datalab/commit/6e2cb9ca6643512b09a8b3c8c5c82af566900851))

- Country and product nodes, product-country export and import edges, and product parent edges
  ([`cca6d5c`](https://github.com/DataLabTechTV/datalab/commit/cca6d5c1b631bfd57a684d0dfdc73a4874bef1aa))

- Country-country ESI calculation
  ([`0ca0346`](https://github.com/DataLabTechTV/datalab/commit/0ca03462e6c1396bc207caec28bddb0584c6a225))

- Datacite working downloader
  ([`bf09fb1`](https://github.com/DataLabTechTV/datalab/commit/bf09fb16a6ca7b980fe2b5f806e4216e690fbda4))

- Ingest country classification data
  ([`09c3ac7`](https://github.com/DataLabTechTV/datalab/commit/09c3ac7c5fa28acf994fe7712c78af41acdf6be6))

- Logic changed to account for the last 3 years in data instead of a fixed range
  ([`8599498`](https://github.com/DataLabTechTV/datalab/commit/85994988af3ae3c3283b3cba2e9247b83d020bf4))

- Move cache to shared level and add expunge function and requests cache
  ([`805511f`](https://github.com/DataLabTechTV/datalab/commit/805511f336bb7230ec7d7472e5949c337cdebcc0))

- Rename 2020-2023 to latest 3y and add schema for country-country metrics
  ([`af044f8`](https://github.com/DataLabTechTV/datalab/commit/af044f875b1509c2aea9e8f5d344ae9b691aca70))

- Select top 5% ESI country-country relations for edges
  ([`3356e4f`](https://github.com/DataLabTechTV/datalab/commit/3356e4f0095f90e5a92141fbc67428b27c16fc7f))

- Skip cache for downloads and display progress bar
  ([`039e08a`](https://github.com/DataLabTechTV/datalab/commit/039e08abc2658784e18bd5a6d54d53bd921bbeaf))

- Split ingestion into multiple modules and add dataset templates
  ([`8e3c6b8`](https://github.com/DataLabTechTV/datalab/commit/8e3c6b8be6708b03448f394b457294f550e39fa5))

- Stage transformations for TAoEC
  ([`6e082e3`](https://github.com/DataLabTechTV/datalab/commit/6e082e3bcb71fb68f5ef7ce329b9fd7b88182c65))

- Support for cache usage statistic printing
  ([`436391b`](https://github.com/DataLabTechTV/datalab/commit/436391b6dacc32bc6a4abcb5dc8f435b7b767645))

- Support for loading econ_comp graph
  ([`93396df`](https://github.com/DataLabTechTV/datalab/commit/93396dfd465d52e3efd879442c2bc74e2ac0fb3b))

### Performance Improvements

- Increase chunk size and make sure temp files are cleaned even when the script is stopped
  ([`39943df`](https://github.com/DataLabTechTV/datalab/commit/39943dfdbe596640b639250daf3dad674de01030))

### Refactoring

- Log debug message containing produced context
  ([`5917a15`](https://github.com/DataLabTechTV/datalab/commit/5917a150cb831aa485e495fb131232f7f5598c94))

- Rename context to entities when referring to entity nodes
  ([`ff6e0df`](https://github.com/DataLabTechTV/datalab/commit/ff6e0df4fdea9eb37f004a8dbab5ff890bb2f56e))

### Testing

- Ensure ESI is within a 0..1 range
  ([`d1ef5ce`](https://github.com/DataLabTechTV/datalab/commit/d1ef5ceeaac7e38b1a4d5b1b3283b07ee267a134))


## v0.3.0 (2025-07-08)

### Bug Fixes

- Add error control to the GraphRAG chain
  ([`4f015ca`](https://github.com/DataLabTechTV/datalab/commit/4f015ca309974f1623a36a5b2dfd09d6c86a5484))

### Chores

- **deps**: Add colorama to color error messages
  ([`389a8a1`](https://github.com/DataLabTechTV/datalab/commit/389a8a1399d6dfdfeefe8038b85322f5eeb22384))

### Features

- Graph rag CLI options for interactive and direct querying
  ([`8f54d81`](https://github.com/DataLabTechTV/datalab/commit/8f54d812d1e17196da01aac9c2d7e0dc1bc9e9f9))

### Refactoring

- Remove unused import
  ([`c5bfb82`](https://github.com/DataLabTechTV/datalab/commit/c5bfb825ccdea4166f4952d2fa6c8642c817008c))


## v0.2.0 (2025-07-04)

### Bug Fixes

- Correct logic for deleting vector index if exists
  ([`516b677`](https://github.com/DataLabTechTV/datalab/commit/516b67790aaed0a1b2d6d2736d52a611d7c34375))

### Chores

- Add missing word in prompt
  ([`2001d8d`](https://github.com/DataLabTechTV/datalab/commit/2001d8d76e28d788266a2b65b0d219d078e10496))

- Container names will now use the default naming schema
  ([`6d267b8`](https://github.com/DataLabTechTV/datalab/commit/6d267b873d5ce8fd07b61a3b0595cc4700f95603))

- Ensure predictable table indexing order
  ([`4547bd3`](https://github.com/DataLabTechTV/datalab/commit/4547bd31b9d6ba7c104ebc027a1ce57d163f16be))

- Graph retriever and context assembler class scaffolds
  ([`eae806d`](https://github.com/DataLabTechTV/datalab/commit/eae806d2cd5eba6e7a4384ac8c272b35ceca44a4))

- Make sure kuzudb-explorer is using a fixed image version (0.10.0 currently)
  ([`80c8aca`](https://github.com/DataLabTechTV/datalab/commit/80c8aca4f74034e69c7ca18b324289b2770a91b3))

- Path combination and scaffolding for hydrating
  ([`1c7db62`](https://github.com/DataLabTechTV/datalab/commit/1c7db625c3bd80604d67d4b9194e807b61db3314))

- Prefix log message is now debug-level
  ([`de7d708`](https://github.com/DataLabTechTV/datalab/commit/de7d708cb53280b8de149e5a3b6220e5456cd159))

- Print version from pyproject.toml via CLI argument
  ([`2fa5b86`](https://github.com/DataLabTechTV/datalab/commit/2fa5b86c8e5c5e9ae4d7d4c4a8cbee77d40bdf44))

- Remove unused semantic-release config
  ([`1692e14`](https://github.com/DataLabTechTV/datalab/commit/1692e1473e8cc5c0811a49f31555cf5ec87d37a6))

This option was set in the wrong location, so it did nothing. We don't need it.

- Replace default nomic-embed-text ollama model with phi4:latest
  ([`ee324f1`](https://github.com/DataLabTechTV/datalab/commit/ee324f1ef3b41716cabf2f5f67f4ddf9888e3772))

- Setup ollama service and add env var for default model install
  ([`4af078b`](https://github.com/DataLabTechTV/datalab/commit/4af078ba17bcffdbd23c392459f66271bab4a761))

- **deps**: Add ollama dependency
  ([`4d1608d`](https://github.com/DataLabTechTV/datalab/commit/4d1608dd05b638224773bcb91a2aadfda22e7f08))

- **deps**: Add pytest to dev deps and configure default CLI options
  ([`baabcd5`](https://github.com/DataLabTechTV/datalab/commit/baabcd5055887fd9b47f6d203eeaacf51923ce32))

- **deps**: Langchain with ollama support, and a prompt helper library
  ([`4565ec9`](https://github.com/DataLabTechTV/datalab/commit/4565ec9444ca3242f7166c2dcef4df3b69df6254))

- **deps**: Langchain-kuzu
  ([`eed603d`](https://github.com/DataLabTechTV/datalab/commit/eed603d6e331bf0bc3781c35e247bdc3fcb1a3e3))

- **deps**: More-itertools
  ([`ecb7f9c`](https://github.com/DataLabTechTV/datalab/commit/ecb7f9c6ce6df46a197630abd92b3e4023c32fb5))

### Continuous Integration

- Add missing version to semantic-version command
  ([`c6facd1`](https://github.com/DataLabTechTV/datalab/commit/c6facd16d251c97967d21c9668452dd980a93802))

- Fix call to semantic release using a function
  ([`d577a45`](https://github.com/DataLabTechTV/datalab/commit/d577a45625c46d0081242fdb911b8f1d09af742c))

- Fix changelog_file config location
  ([`b5bb8d7`](https://github.com/DataLabTechTV/datalab/commit/b5bb8d780084f955bdc234120a5f766bc685a4fc))

- Fix pyproject.toml version setting for semantic release
  ([`db96d22`](https://github.com/DataLabTechTV/datalab/commit/db96d2204984a9303a62fb58117e3ca856aec810))

- Remove redundant build option, already set on pyproject.toml
  ([`e8f6d6b`](https://github.com/DataLabTechTV/datalab/commit/e8f6d6baf47609fbd00bd5bcd2003c1e954be2d0))

### Documentation

- Add knn method info to clarify the max_distance param
  ([`0fdf01f`](https://github.com/DataLabTechTV/datalab/commit/0fdf01f37c85e99165ee2ddd465c816a2998eecd))

### Features

- Add file logging by default (and option to disable)
  ([`2f9a36e`](https://github.com/DataLabTechTV/datalab/commit/2f9a36e07a3fd895952aa9aa32c1790b4877b75e))

- Add final answer pipeline and improve interactive mode
  ([`58bff5a`](https://github.com/DataLabTechTV/datalab/commit/58bff5adb0285f43e83b117dcc668b3a6ec177c8))

- Basic prompt for graph RAG and langchain scaffolding
  ([`50173de`](https://github.com/DataLabTechTV/datalab/commit/50173de3fbee66e34e7a4c97ad9e0a53fc2b6a02))

- Combined knn step for context assembler
  ([`33b20ab`](https://github.com/DataLabTechTV/datalab/commit/33b20abcfd6983a6b8d5420cb63bad5ccf32f651))

- Context assembly based on ANN, paths to neighbors, and random walks from neighbors
  ([`9323352`](https://github.com/DataLabTechTV/datalab/commit/932335291cc4eb62d657db7a424320d9b219a8b7))

- Cypher friendly schema format
  ([`87f8171`](https://github.com/DataLabTechTV/datalab/commit/87f81711718ed77caeac1c2e89c7515f8a484c58))

- First working NER implementation based on langchain-kuzu
  ([`a743062`](https://github.com/DataLabTechTV/datalab/commit/a74306230e6f109ede1b26e0c1d6b62b7ed1c507))

- Graphrag is now a LangChain Runnable and components became methods
  ([`cd04d33`](https://github.com/DataLabTechTV/datalab/commit/cd04d33776debd768a882085119515483f639529))

- Knn query support
  ([`2bca4a0`](https://github.com/DataLabTechTV/datalab/commit/2bca4a090d3539977bc956420732b359d46cc041))

- Knn, shortest paths sampler and random walk computation for context assembler
  ([`22d4f0a`](https://github.com/DataLabTechTV/datalab/commit/22d4f0a4079d0820efa0cf52d9980dfc8817fce1))

- Kuzudb-explorer launcher script now handles different paths
  ([`4dc65a9`](https://github.com/DataLabTechTV/datalab/commit/4dc65a9406c9cf34aa82f0fb2e908bff48f31ad4))

- Lazy singleton S3 resource and bucket connection
  ([`63388a1`](https://github.com/DataLabTechTV/datalab/commit/63388a1d97dd254f45c4b253bca3c99339feb6b9))

- Ollama service with gemma3 and nomic-embed-text
  ([`83b68dd`](https://github.com/DataLabTechTV/datalab/commit/83b68dd5c23e767789c935e24cc55317a35e133d))

- Path hydration and bulk description
  ([`97ea465`](https://github.com/DataLabTechTV/datalab/commit/97ea465f721930afe64d09bb114e29d38ff1e92a))

- Return paths as interleavings of node_id and rel label
  ([`17b790a`](https://github.com/DataLabTechTV/datalab/commit/17b790ad7b5463af56ef1c409d60732fe861b7a5))

- Support for indexing embeddings
  ([`c687f81`](https://github.com/DataLabTechTV/datalab/commit/c687f81f4fbcec6aad30d3402881b2a4c62bef9d))

- **graph.ops**: Automatically add a custom embeddings column to all node tables
  ([`1900f21`](https://github.com/DataLabTechTV/datalab/commit/1900f2135b8a5be406cb38b3d4a06cbcd45fb7ce))

Closes #2

- **graph.ops**: Produce node schema with properties names and types
  ([`291d42f`](https://github.com/DataLabTechTV/datalab/commit/291d42f59914f296efffc8f54cc44df074a27e33))

### Performance Improvements

- Migrated from KuzuQAChain to a custom strategy still based on langchain-kuzu
  ([`ebce585`](https://github.com/DataLabTechTV/datalab/commit/ebce5853e1121e3fe7aba56be4107ca359828f45))

### Refactoring

- Change property match to WHERE cond and lower the temperature
  ([`f0f9198`](https://github.com/DataLabTechTV/datalab/commit/f0f919895c4079d0c88f998dbb657346666859d2))

### Testing

- Correct paths_df fixture and add missing exclude_props
  ([`c167b0c`](https://github.com/DataLabTechTV/datalab/commit/c167b0cb0dc318999d383ab2444f557487096aff))

- Invoke test for GraphRAG runnable
  ([`f724224`](https://github.com/DataLabTechTV/datalab/commit/f72422478f13505d5c9545dd1d3ec68f3346a79b))

- Move graph db check to global fixtures
  ([`d2963e3`](https://github.com/DataLabTechTV/datalab/commit/d2963e3b1027de909f64f497629004ac6a7514a3))

- Print final chain output
  ([`40f2d14`](https://github.com/DataLabTechTV/datalab/commit/40f2d14540167791e970607f6a5c06a9684278ff))

- Setup ops and paths_df to test path_descriptions()
  ([`3f3c160`](https://github.com/DataLabTechTV/datalab/commit/3f3c1602f239c9f142e3d54efd3fa991f52b5f17))

- Tests will only print logs to stderr and always use debug level
  ([`fafb3bf`](https://github.com/DataLabTechTV/datalab/commit/fafb3bfdbb854a3134b01bdb0fe1d7b47abd8611))


## v0.1.0 (2025-06-25)

### Bug Fixes

- Add node_id to all nodes
  ([`f927dcd`](https://github.com/DataLabTechTV/datalab/commit/f927dcd26b61fd50fd784a16cd1a6d983499b7f7))

- Batch should be column, not parameters
  ([`73eeb9e`](https://github.com/DataLabTechTV/datalab/commit/73eeb9effa01b51bd171be3ff7af2c682051d505))

- Condition for ignoring files during deletion
  ([`9da0e0f`](https://github.com/DataLabTechTV/datalab/commit/9da0e0f997dc63aae6251d433088c1cdf5094f2e))

The manifest.json was being deleted by mistake.

- Correct name for placeholder models
  ([`fa07609`](https://github.com/DataLabTechTV/datalab/commit/fa07609b4985d6279ffde955adfadbfef123cb5e))

feat: implement all missing edge models

- Ducklake integration using dev version for upcoming dbt-duckdb 1.4.1
  ([`effe0d7`](https://github.com/DataLabTechTV/datalab/commit/effe0d70b4ac93e2b533b740f3fd03c017ee9df5))

- Duplicate alias for source_id and target_id columns
  ([`d6b6790`](https://github.com/DataLabTechTV/datalab/commit/d6b679064d8306dad2462a2eed5787a82e9cfc67))

- Ensure tags are checked out
  ([`d833c89`](https://github.com/DataLabTechTV/datalab/commit/d833c89b015ced234f0de245f5a67093f613cc0d))

- Generate sequential node ID globally for all nodes
  ([`8d019ac`](https://github.com/DataLabTechTV/datalab/commit/8d019ac5402a472d606714318a6b56bbe6c932f2))

- Genre loading queries
  ([`abc6833`](https://github.com/DataLabTechTV/datalab/commit/abc683357df6d2cb47e0793b5b90d8246bf616d6))

refactor: reorganize models into stage and marts

feat: support for edge loading (untested)

- Genre nodes become a single table to ensure uniqueness
  ([`7ec7f03`](https://github.com/DataLabTechTV/datalab/commit/7ec7f03cc1a671eaba64f3bfa154a4a475e740ee))

- Incorrect S3 secret variable
  ([`6fa7394`](https://github.com/DataLabTechTV/datalab/commit/6fa739476c004d711a8dea3cc981c2d0626d2761))

- Missing description for playcount
  ([`c505c9c`](https://github.com/DataLabTechTV/datalab/commit/c505c9c6ce95315d89404c432ff26cff236f9601))

- Missing node ID dataset-based prefix
  ([`bfecf9f`](https://github.com/DataLabTechTV/datalab/commit/bfecf9f249186d4e6dcf1bc8f1ba65b82ea47606))

- Missing nodes prefix on ref table
  ([`58b04f5`](https://github.com/DataLabTechTV/datalab/commit/58b04f58c5eb99053090aa8fce423806c26e1d4c))

- Missing underscore after prefix
  ([`3a0d6d9`](https://github.com/DataLabTechTV/datalab/commit/3a0d6d97544f99c8b2d3d62e9a734b7490a0ced7))

- No longer defaulting to upstream dependencies
  ([`6d2d68a`](https://github.com/DataLabTechTV/datalab/commit/6d2d68aa9ad390fab108b2782c6fa4cadf6c6742))

- Regression introduced by removing key_parts
  ([`668a31c`](https://github.com/DataLabTechTV/datalab/commit/668a31cae84eab1680c029a045f60a24da142a44))

- Removed extra bracket in log message
  ([`782bcc9`](https://github.com/DataLabTechTV/datalab/commit/782bcc9cc0a16592c7405cf3ccd4e7be53678de6))

- Should be alias, not name
  ([`d03e079`](https://github.com/DataLabTechTV/datalab/commit/d03e07982e2a05a5adfe4b177a9c5172a461446f))

- Should be list of list, not list of tuple
  ([`c3b7419`](https://github.com/DataLabTechTV/datalab/commit/c3b7419c56298614548c8e56d41b1ee25740e15a))

- Sqlite prefix missing
  ([`78bae87`](https://github.com/DataLabTechTV/datalab/commit/78bae87dbab67470f93d4db0d3a5655169a02236))

- Switch to single table for genre nodes
  ([`6d5dd1f`](https://github.com/DataLabTechTV/datalab/commit/6d5dd1fdf7f38f5571a954054a703c2ae2317266))

- Update graph loading process based on new config schema
  ([`eebc677`](https://github.com/DataLabTechTV/datalab/commit/eebc677257feed5353c60e5b924ffdd6f17659d2))

- Update prune to use class prefix
  ([`49ca20f`](https://github.com/DataLabTechTV/datalab/commit/49ca20fdac51b33d29ed08737633fbcf0237f373))

- Using map instead of list per node embedding
  ([`e6f1caf`](https://github.com/DataLabTechTV/datalab/commit/e6f1cafc14fdb8811883471f1527a8efc6017ad3))

fix: add missing schema alter to add embedding property to all nodes

- Wrapper to copy from data mart via a temporary file
  ([`3cd0268`](https://github.com/DataLabTechTV/datalab/commit/3cd0268d3677f79dea02ecdf7caa3a6097369f3b))

- Wrong column name in schema
  ([`af2a693`](https://github.com/DataLabTechTV/datalab/commit/af2a693c217321d4128f29134709ca7484f0c555))

- Wrong filename case, should be RO, not ro
  ([`905a303`](https://github.com/DataLabTechTV/datalab/commit/905a303bf6c31f80ccce50e0109e7c3b314b4b99))

- Wrong model name in schema
  ([`588f3bc`](https://github.com/DataLabTechTV/datalab/commit/588f3bc36cdb1f6fdc45db15432d62e328a49e65))

- Wrong reference, missing schema prefix
  ([`701fb1d`](https://github.com/DataLabTechTV/datalab/commit/701fb1d832eb52aedae62394ded25745c7cd602a))

- Wrong variable order in log message
  ([`40cb055`](https://github.com/DataLabTechTV/datalab/commit/40cb055f586db954ec371faca1949006838b4867))

### Chores

- Add description and pandas dep
  ([`b7c40d0`](https://github.com/DataLabTechTV/datalab/commit/b7c40d0dc36dba15cffe805e849ef009a1f3e6ba))

- Add DUCKLAKE_PATH to .env
  ([`3ab2bee`](https://github.com/DataLabTechTV/datalab/commit/3ab2bee4c69f15c0325a4cff2dcfeb5e80f01bf3))

- Add kuzu as a dependency
  ([`f1e2a5c`](https://github.com/DataLabTechTV/datalab/commit/f1e2a5ce134d866411f04b469844e6c492c08873))

- Add S3 prefix for exports
  ([`88ee16c`](https://github.com/DataLabTechTV/datalab/commit/88ee16cd3636ba2d0b8d5e6d35fddc8f458abf26))

- Add solid background to diagram
  ([`7499f46`](https://github.com/DataLabTechTV/datalab/commit/7499f46d7924b78759f43519e28a72e501563df3))

- Add torch, torch-sparse, and torch-geometric deps
  ([`5ddd0f8`](https://github.com/DataLabTechTV/datalab/commit/5ddd0f8838121867ab6e785d1d61006d8801f0c6))

- Better schema name organization for graphs
  ([`948759a`](https://github.com/DataLabTechTV/datalab/commit/948759ae06c3cd55c23b298ebfff80840777f0d3))

- Click and minio deps
  ([`c6e450f`](https://github.com/DataLabTechTV/datalab/commit/c6e450f245e025055024d37153ba5cedaf9ba03b))

- Default to eu-west-1, as MinIO also defaulted to it
  ([`6afa282`](https://github.com/DataLabTechTV/datalab/commit/6afa28204728965393d7648072fd2a9a69deb620))

- Delete example models
  ([`7012b5b`](https://github.com/DataLabTechTV/datalab/commit/7012b5b64df856b25a179127662f7edf9eb91796))

- Fix version for python-semantic-release to match deps
  ([`3ff93d9`](https://github.com/DataLabTechTV/datalab/commit/3ff93d9867a267a863f5209ed91e2785a6fd9ca7))

- Github dark mode background color
  ([`ca97d44`](https://github.com/DataLabTechTV/datalab/commit/ca97d44005cca71a37733a2746c489f2faab3c34))

- Gitignore vscode directory
  ([`a2fcabd`](https://github.com/DataLabTechTV/datalab/commit/a2fcabd53521f9235d01f25e330563b891de291b))

- Initial log message for export
  ([`1207e93`](https://github.com/DataLabTechTV/datalab/commit/1207e9319ce21c5de5dc5956b866379268d4d065))

- Initial log string is now a welcome string
  ([`0edefc6`](https://github.com/DataLabTechTV/datalab/commit/0edefc6418c91991f6b5a37b0176f48e73a28059))

- Make sure we start from 0.1.0, not 1.0.0
  ([`cb2b7c5`](https://github.com/DataLabTechTV/datalab/commit/cb2b7c5e4515c2dcfd5c8fe3a88f4f9f6385ea04))

- Remove unused dep
  ([`ba09c90`](https://github.com/DataLabTechTV/datalab/commit/ba09c90ddcf6c21f5fde9da0f3870740f6ba36ea))

- Remove unused deps and update docs referring to them
  ([`7da0d24`](https://github.com/DataLabTechTV/datalab/commit/7da0d24b19a07ae25edc6337d4eb0d6f5345833c))

- Replace with official GHA for python-semantic-release
  ([`7301029`](https://github.com/DataLabTechTV/datalab/commit/7301029dc2b83755c278b2b86ab5893beff7aea7))

- Script to launch temporary docker container with KuzuDB Explorer for a database
  ([`52b617a`](https://github.com/DataLabTechTV/datalab/commit/52b617ab3fc4eb6179dd29d4d666896d83a6c7f4))

- Setup dltctl CLI tool (replaces Makefile)
  ([`405d800`](https://github.com/DataLabTechTV/datalab/commit/405d8009fb458839917156c3e2dc8ae6fc349d0f))

- Simplify node and edge schemas, using Gremlin-like notation
  ([`887dddc`](https://github.com/DataLabTechTV/datalab/commit/887dddc030de0d9e925cb1b27bf07eae4d2d7c47))

- Solid background in individual rectangles
  ([`8f68204`](https://github.com/DataLabTechTV/datalab/commit/8f6820495887a87969807cce6f4667b9fb05d3f9))

- Switch to a multi-database marts config
  ([`1cf615c`](https://github.com/DataLabTechTV/datalab/commit/1cf615c93a7b1e547472988b714ebddf9459c900))

- Temporarily removed
  ([`bd26438`](https://github.com/DataLabTechTV/datalab/commit/bd264383309094e20647beac16982c10ce4ad4a3))

Schema was outdated and was blocking dbt run.

- Update config to match multi-database marts
  ([`d47f96f`](https://github.com/DataLabTechTV/datalab/commit/d47f96fb161378f38637f45d6ca6a8bca29d6747))

- Won't use the extra command in favor of one entry point
  ([`698a3d1`](https://github.com/DataLabTechTV/datalab/commit/698a3d125aaa4d1f99cb27be18bc87083548bb75))

- **deps**: Move python-semantic-release to dev deps
  ([`9df3ed6`](https://github.com/DataLabTechTV/datalab/commit/9df3ed65d058c8ac13cd927c0b10767effc2e133))

### Documentation

- Add graph and shared
  ([`866b37c`](https://github.com/DataLabTechTV/datalab/commit/866b37c1577e4dd91d72cddb009a7fdea988b14a))

- Add specification for exports pruning
  ([`e42acbf`](https://github.com/DataLabTechTV/datalab/commit/e42acbf198efa382aad21125437ac9294ea0c7c4))

- Dependency management development instructions
  ([`2f9393f`](https://github.com/DataLabTechTV/datalab/commit/2f9393f3523a47fffeaaf9be72b7c657120789e4))

- Duckdb init script description
  ([`94b1959`](https://github.com/DataLabTechTV/datalab/commit/94b19595a1f18e5fc6ea84a0875a500149f49abd))

- End-to-end documentation
  ([`190ef1b`](https://github.com/DataLabTechTV/datalab/commit/190ef1bb5ed840de28090c3a9672a10ea49e7f15))

- Fix section links
  ([`e00a537`](https://github.com/DataLabTechTV/datalab/commit/e00a5374add7bf6abf6c35c1157659e7b5469183))

- Latest.json is now manifest.json
  ([`6cdb057`](https://github.com/DataLabTechTV/datalab/commit/6cdb057874f32fd7a0c166e7549ef1e7c0922076))

- Remove suffix from info boxes
  ([`170ebff`](https://github.com/DataLabTechTV/datalab/commit/170ebffa5c2c43b4709b5fdaa153c32e1fc0965d))

- Requirements, quick start, architecture diagram
  ([`8009821`](https://github.com/DataLabTechTV/datalab/commit/800982183defb20edd942f0e761010d177780212))

- Schemas for nodes and edges of the music graph
  ([`409b4cb`](https://github.com/DataLabTechTV/datalab/commit/409b4cb96ede819d48d745796f845834a9655843))

- Structured sections for README
  ([`5a6c128`](https://github.com/DataLabTechTV/datalab/commit/5a6c12876f697fb99a4af4d0265006f952706f9d))

- Update schema for the DSN and MSDSL datasets
  ([`9a56aaa`](https://github.com/DataLabTechTV/datalab/commit/9a56aaaa5d21419b57b0edff0b8dbcba5855bc9c))

- Update storage layout
  ([`f60d021`](https://github.com/DataLabTechTV/datalab/commit/f60d021df1b4a52cd91fcf34864d25e3845f276a))

- Update storage layout
  ([`1383bfd`](https://github.com/DataLabTechTV/datalab/commit/1383bfd5145c1ca70c5a452a1a4e03ad244fa409))

- Update storage layout and specification for the ingest command
  ([`b66cffe`](https://github.com/DataLabTechTV/datalab/commit/b66cffef16803f5c228d5e22802dbb33fe5febbf))

- Using generic dark background
  ([`85476f1`](https://github.com/DataLabTechTV/datalab/commit/85476f12b0d30f1f4ff742b3d43e8627ecb4dfb2))

### Features

- Add CLI args for read only and to reset
  ([`dbfefa8`](https://github.com/DataLabTechTV/datalab/commit/dbfefa81f9ccd9421f6e8cd5fc01fb6dac2d2b8a))

Container is now kept between sessions, unless explicitly reset.

- Backup restore can now specify source date
  ([`62a52af`](https://github.com/DataLabTechTV/datalab/commit/62a52af38fc4d05e8dda90662ed67732ec6387b9))

- Basic support for dbt run via dlctl transform
  ([`b3f6240`](https://github.com/DataLabTechTV/datalab/commit/b3f6240de443c714e199a474cd83172ded6415b3))

- Catalog backup and restore
  ([`cb87830`](https://github.com/DataLabTechTV/datalab/commit/cb878305704afd1af1719a5f9faa0e2a36f3883e))

refactor: prefix is now set when instancing Storage

feat: Storage can now upload/download files or a directory

- Create directories for DuckDB databases
  ([`3976b19`](https://github.com/DataLabTechTV/datalab/commit/3976b190fd4cb46e3500aa2302a8ee37aa3c64bb))

This way we can set the marts databases to be stored under local/marts/.

- Dbt debug option
  ([`f64313e`](https://github.com/DataLabTechTV/datalab/commit/f64313ee2e3626f85e20d2a42d83ea8a031f199d))

- Debug option controlling log level
  ([`9e5f030`](https://github.com/DataLabTechTV/datalab/commit/9e5f0304bc3f4c1c1d1cb2204a7977326fd15f94))

- Directory structure for a DuckLake lakehouse
  ([`87ed579`](https://github.com/DataLabTechTV/datalab/commit/87ed57917bf5d8f7643542ad858b11e8b696b72f))

- Dlctl tools generate-init-sql
  ([`c24ca39`](https://github.com/DataLabTechTV/datalab/commit/c24ca39aab1fa222d0e8054b2a5f0817c117f622))

This will output into local/init.sql. The scripts/init.example.sql or the gitignored
  scripts/init.sql are no longer used.

docs: add a help message to all commands

- Duckdb CLI init script to connect to the lakehouse
  ([`788691f`](https://github.com/DataLabTechTV/datalab/commit/788691f4fcba9409e940edade878072331b8c9fa))

- Error control for empty results
  ([`d5e1d65`](https://github.com/DataLabTechTV/datalab/commit/d5e1d654b25b7db7b51f874e22ba5bb5ebf96dbf))

- Exception capture for KuzuOps
  ([`6a2a498`](https://github.com/DataLabTechTV/datalab/commit/6a2a4981580945c66ab2ed16a0c9f4b4a4896ff8))

- Export scripts that output parquet
  ([`218bfeb`](https://github.com/DataLabTechTV/datalab/commit/218bfebfdd588bdd433b3e3f2c98bcd6a785fcd5))

- Frp node embedding over KuzuDB
  ([`68a7514`](https://github.com/DataLabTechTV/datalab/commit/68a7514e6929d40e9669cb2b737fb4f67e91272e))

- Improve backups listing
  ([`8c5284d`](https://github.com/DataLabTechTV/datalab/commit/8c5284dae6deff93de40e2570e1e6de23113ad29))

- Load all genres tables based on shared macro
  ([`ed8197b`](https://github.com/DataLabTechTV/datalab/commit/ed8197bdbea62e9638dd3cab682363d5c31e910e))

- Ls and prune for ingest and exports
  ([`e9a3505`](https://github.com/DataLabTechTV/datalab/commit/e9a3505c88861971c2bfe49c31d35977e0e0c958))

fix: add missing manifest to exports

fix: ignored file filtering

fix: add prefix logic to upload manifest

- Minio docker service
  ([`00f2dab`](https://github.com/DataLabTechTV/datalab/commit/00f2dab8764deabfdee43f979657d27a28d9a5b7))

- Node embedding computation and graph DB update
  ([`579b477`](https://github.com/DataLabTechTV/datalab/commit/579b4770c049a06983bb9ae80add7d3dc22fe093))

- Option to use latest export when loading a graph
  ([`3b00439`](https://github.com/DataLabTechTV/datalab/commit/3b004390cac238452b3dbdaec1c633d6a2cc3a56))

refactor: exports now stored using the same directory structure as marts

- Qol for CLI parameters and defaults, and logging
  ([`c6ee19b`](https://github.com/DataLabTechTV/datalab/commit/c6ee19ba65908069b06d22a89640dc5af53a3d7c))

- Quality of life for explorer startup and exit
  ([`4562ab6`](https://github.com/DataLabTechTV/datalab/commit/4562ab65721efdc48391d2a54ecdf4a7fb792a8b))

- Replace export scripts with a load method from the new graph package
  ([`8c356d6`](https://github.com/DataLabTechTV/datalab/commit/8c356d66d76c4e8cabca05ef6bacb15502d7445c))

- Replace load_dotenv with proper validation via environs
  ([`aacb1a3`](https://github.com/DataLabTechTV/datalab/commit/aacb1a3a7e26449553378e56824f54c91e92f68e))

refactor: centralize storage and environment variable loading into shared packages

refactor: improve function naming and arguments

feat: set placeholder upload as optional

refactor: rename lastest.json to manifest.json

feat: storage now implements an env var loader with latest file paths

- Schema name without the 'main_' prefix
  ([`37b0bff`](https://github.com/DataLabTechTV/datalab/commit/37b0bff909e6f20f38d12957b27c86cb9d71b291))

- Setup semantic releases
  ([`ef856fd`](https://github.com/DataLabTechTV/datalab/commit/ef856fd28a8d6820241431bb55d5fb2df731c225))

- Strip schema name from table name
  ([`fc83dfa`](https://github.com/DataLabTechTV/datalab/commit/fc83dfa3e9dd69d1ba63f012aeec372e1782ba19))

- Stubs for node computation embedding command
  ([`f220fc2`](https://github.com/DataLabTechTV/datalab/commit/f220fc2a81c5e81d465b26313d09c66eea19e251))

- Support file downloading from object storage
  ([`eff8a8b`](https://github.com/DataLabTechTV/datalab/commit/eff8a8b2e59b24bb854a0df78037134dac488c21))

- Support for kaggle and hugging face ingestion
  ([`39f8fb5`](https://github.com/DataLabTechTV/datalab/commit/39f8fb58e43a16ede7c6d4d23e0c4b449f5ffc24))

- Support for manual dataset ingestion
  ([`3b6c3d1`](https://github.com/DataLabTechTV/datalab/commit/3b6c3d18b4f848da7d2adeebef95af6ae873ebdc))

- Support for running a subset of models during transform
  ([`4986aee`](https://github.com/DataLabTechTV/datalab/commit/4986aeea0ab6b7eea4fc8c1e34d87c9a010721fb))

### Performance Improvements

- Switch to UNPIVOT strategy
  ([`51059e2`](https://github.com/DataLabTechTV/datalab/commit/51059e27b0dd3844e95f3af1e3160cfef4e7da1a))

### Refactoring

- Better naming scheme for graph schemas, and node and edge tables
  ([`1716d17`](https://github.com/DataLabTechTV/datalab/commit/1716d17a8a6dee7b222ef3c7e1244b2b3f663e8e))

- Cleanup file to avoid inline comments
  ([`498534d`](https://github.com/DataLabTechTV/datalab/commit/498534d5b52327653a708d684855b831d6f3bd83))

- Con is now conn
  ([`cc99988`](https://github.com/DataLabTechTV/datalab/commit/cc99988c570a81224ea50a0b1d3e7a38c787d2be))

- Embedding batch updates now handled directly by NodeEmbedder
  ([`5dc6e51`](https://github.com/DataLabTechTV/datalab/commit/5dc6e5148f042cb534bb71408d91f9fa55fee600))

- Genres/nodes and edges are now stored in the graphs mart
  ([`9963909`](https://github.com/DataLabTechTV/datalab/commit/9963909b1966daa10a4bd16baf76628559a9b637))

docs: schemas updated with node and edge information and basic testing

- Graph manager is now ops
  ([`c84dbf5`](https://github.com/DataLabTechTV/datalab/commit/c84dbf58cc323a2db0c40ae22a76d9b5c24e4057))

- Improved docs and better naming for DuckLake DBs
  ([`0b8097d`](https://github.com/DataLabTechTV/datalab/commit/0b8097dbb3fc2de935a10aea77f019b5fa5dfb46))

- Latest export is now default, but re-exporting can be forced
  ([`54324c3`](https://github.com/DataLabTechTV/datalab/commit/54324c3a917b9440946a4f5ecc6c7974b2131828))

- Log exception message without stack trace
  ([`1d52f40`](https://github.com/DataLabTechTV/datalab/commit/1d52f40e0a6302c6587830a1b8e47ffba820e846))

- Name source and target columns
  ([`b0c83fd`](https://github.com/DataLabTechTV/datalab/commit/b0c83fd31f8b1e3ac2ed1285799d49b5c8ddc203))

feat: cast node IDs to integer

- Nodes and edges directories to match graph DB loading format
  ([`86ef29e`](https://github.com/DataLabTechTV/datalab/commit/86ef29e0f78de3c0fd0c0bcaa4c35fd6e017c607))

feat: million song dataset, spotify and lastfm transformation

feat: improve deezer genres and edges mart table schemas

- Overall simplification of the explore graph script
  ([`94b0bb0`](https://github.com/DataLabTechTV/datalab/commit/94b0bb0d131c7ba0b82b08424e27262c2a7c90a4))

- Qol, log message in lower case after colon
  ([`76cccc8`](https://github.com/DataLabTechTV/datalab/commit/76cccc82f780b56653fa002c57bdd078fb492fb5))

- Qol, log message now includes epoch
  ([`51c96cd`](https://github.com/DataLabTechTV/datalab/commit/51c96cd334954ddc04a376ccace39dc5b6be4a39))

- Remove source from edges
  ([`ca15947`](https://github.com/DataLabTechTV/datalab/commit/ca159477c97fe52184d9554e98260b485c6384f6))

- Remove uneeded echos
  ([`a5f86a0`](https://github.com/DataLabTechTV/datalab/commit/a5f86a0bc9c7ba85d242b89366a4194f9df73466))

- Rename models to include a schema prefix
  ([`dd263ab`](https://github.com/DataLabTechTV/datalab/commit/dd263abfb30118c5308ad2abf9ed283ff1acea91))

feat: implement missing node models

- Rename music graph back to music_taste
  ([`d0d7a57`](https://github.com/DataLabTechTV/datalab/commit/d0d7a5741505ebfe856bf8faab3409a5599ddb5a))

- S3 access key and secret renamed to reflect common naming schema
  ([`d00a4c9`](https://github.com/DataLabTechTV/datalab/commit/d00a4c96295b6472730e3b9d45e1e75e7bad1329))

- Table materialization is now default
  ([`35dc856`](https://github.com/DataLabTechTV/datalab/commit/35dc856e59c933956e156a6358f8a9d1c0e06840))

- Taking advantage of parents accessor
  ([`1038678`](https://github.com/DataLabTechTV/datalab/commit/1038678f9742da018647ea87a3fcf61f924b52e1))

- Tools and utils moved to shared
  ([`3900df1`](https://github.com/DataLabTechTV/datalab/commit/3900df16c399a5a3c5ee9dd15c5ab88e215f465c))

feat: init SQL can now be returned as a string

fix: lakehouse relied on an init script that's no longer there

Using generate_init_sql to produce a string with the required SQL instead.

chore: uncommended code that didn't run due to KuzuDB bug

- Util is now templates for clarity
  ([`7518c06`](https://github.com/DataLabTechTV/datalab/commit/7518c06212831493d6303382d740654f9ee81064))

chore: groups no longer invokable without arguments

This had been added for better performance, but did nothing.

refactor: split export into standalone feature

Extracted from graph load and integrated into the existing export command (renamed from exports to
  export).

### Testing

- Column only contains positive integers
  ([`c4459fb`](https://github.com/DataLabTechTV/datalab/commit/c4459fbbbf1ca92010c8b8b63400a589bf44b0b7))

- List/array not null or empty
  ([`3ff573f`](https://github.com/DataLabTechTV/datalab/commit/3ff573f93d3bfc37b13d5c70569bf6317fb9ae36))

- Make sure node IDs are globally unique
  ([`5d9a1ff`](https://github.com/DataLabTechTV/datalab/commit/5d9a1ffaa550b19c3882c0919412349f8ab9528a))


# Part 2: lakeFS — Git-Like Data Versioning


## lakeFS Overview


> Source: `docs/data_engineering/lakefs/README.md`

# lakeFS Examples

This directory contains examples demonstrating lakeFS integration for data versioning, lakehouse patterns, and ML/AI workflows.

## Examples Index

### Iceberg / Data Lakehouse

| Example | Description | Complexity |
|---------|-------------|------------|
| [iceberg/spark-basic](./iceberg/spark-basic/) | Basic Spark + lakeFS integration | Low |
| [iceberg/spark-medallion](./iceberg/spark-medallion/) | Medallion architecture (bronze/silver/gold) | Medium |
| [iceberg/trino](./iceberg/trino/) | Trino SQL with Iceberg REST Catalog | Medium |
| [iceberg/write-audit-publish](./iceberg/write-audit-publish/) | WAP pattern for data quality | Medium |
| [delta-lake](./delta-lake/) | Delta Lake versioning | Medium |

### ML / AI

| Example | Description | Complexity |
|---------|-------------|------------|
| [ml/llm-langchain](./ml/llm-langchain/) | AI agents with LangChain + OpenAI | Medium |
| [ml/image-segmentation](./ml/image-segmentation/) | PyTorch + MLflow reproducibility | High |
| [ml/ml-reproducibility](./ml/ml-reproducibility/) | ML experimentation tracking | Medium |

### Workflow Orchestration

| Example | Description | Complexity |
|---------|-------------|------------|
| [dagster-integration](./dagster-integration/) | Dagster + lakeFS workflows | High |
| [lakefs-mount-demo](./lakefs-mount-demo/) | lakeFS mount with Git integration | Medium |

## Prerequisites

- Docker and Docker Compose installed
- For ML examples: adequate disk space (see individual READMEs)
- For LLM examples: OpenAI API key

## Quick Start

1. Navigate to an example directory
2. Run the stack:
   ```bash
   # Full local stack (lakeFS + MinIO + Jupyter)
   docker compose --profile local-lakefs up

   # Or connect to existing lakeFS
   docker compose up
   ```
3. Open Jupyter at http://localhost:8888
4. Open lakeFS UI at http://localhost:8000

## Default Credentials

| Service | Username | Password |
|---------|----------|----------|
| lakeFS | AKIAIOSFOLKFSSAMPLES | wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY |
| MinIO | minioadmin | minioadmin |

## Shared Assets

The `_shared/` directory contains common utilities:
- `assets/lakefs_demo.py` - Helper functions for notebooks
- `images/` - Common images and logos

## Architecture Overview

```
lakeFS provides Git-like version control for data:

Repository (quickstart)
├── main branch (production)
│   ├── tables/
│   ├── models/
│   └── features/
├── dev branch (development)
└── experiment-1 branch (ML experiments)
```

## More Resources

- [lakeFS Documentation](https://docs.lakefs.io/)
- [lakeFS GitHub](https://github.com/treeverse/lakeFS)
- [lakeFS Slack](https://lakefs.io/slack)


> Source: `docs/data_engineering/lakefs/KCG_SUMMARY.md`

# lakeFS — KCG Summary

## What It Is
lakeFS is a Git-like version control system for data lakes, providing branch/commit/merge semantics over S3-compatible object stores. This directory contains the full lakeFS-samples repository with 3,100+ files demonstrating Iceberg table versioning, Delta Lake integration, Spark medallion architecture, Trino SQL querying, write-audit-publish (WAP) patterns, and ML reproducibility workflows with PyTorch and LangChain.

## Why This Matters for Kings' College Galway
lakeFS-style data versioning directly supports the curriculum data platform's need for reproducible data pipelines. The WAP and branching patterns documented here are directly applicable to DLT ingestion of Leaving Cert examination data, ensuring data quality gates before promotion to production. The Iceberg catalog examples inform our DuckLake/MotherDuck lakehouse architecture, and the ML reproducibility workflows map to model versioning needs for our educational AI models.

## Key Patterns Preserved
37 .md files remain, including:
- `README.md` — Overview of all lakeFS examples and architecture
- `lakeFS-samples/README.md` — Sample project index with 20+ standalone examples
- `dagster-integration/README.md` — Dagster + lakeFS orchestration patterns
- `iceberg/spark-medallion/README.md` — Bronze/silver/gold medallion architecture
- `iceberg/write-audit-publish/README.md` — WAP quality gate pattern
- `ml/llm-langchain/README.md` — AI agents with LangChain + OpenAI + lakeFS
- `ml/image-segmentation/README.md` — PyTorch + MLflow reproducibility
- `ml/README.md` — ML experimentation patterns
- `delta-lake/README.md` — Delta Lake versioning
- 19 standalone example READMEs covering Airflow, Databricks CI/CD, Kafka, Flink, Trino, Spark, Prefect, Red Hat OpenShift AI, Labelbox, ParadeDB

## Source Files
Full source removed (2026-06-06). Available at https://github.com/treeverse/lakeFS-samples

## What Was Removed
Python notebooks (.ipynb), Docker configurations, JSON/YAML config files, Python scripts, JAR/Scala files, images/logos, shell scripts, Terraform, CSV/Parquet data


## lakeFS Samples Overview


> Source: `docs/data_engineering/lakefs/lakeFS-samples/README.md`

# lakefs-samples

[![Check notebooks](https://github.com/treeverse/lakeFS-samples/actions/workflows/check-notebooks.yml/badge.svg?branch=main)](https://github.com/treeverse/lakeFS-samples/actions/workflows/check-notebooks.yml?query=branch:main)

_Incorporating the Docker Compose formally known as **Everything Bagel**._

![lakeFS logo](images/logo.png)

**This sample repository captures a collection of notebooks, dockerized applications and code snippets that demonstrate how to use lakeFS.**

_lakeFS is a popular open-source solution for managing data. It provides a consistent and scalable data management layer on top of cloud storage, such as Amazon S3, Azure Blob Storage, or Google Cloud Storage. It allows users to create and manage data in a version-controlled and immutable manner, and offers features such as data governance, data lineage, and data access controls. lakeFS is compatible with a wide range of data processing frameworks and tools._

### **Go to [lakefs_enterprise](./02_lakefs_enterprise/) folder if you want to use [lakeFS Enterprise](https://docs.lakefs.io/understand/enterprise/) instead of lakeFS open source**


## Let's Get Started 👩🏻‍💻

Clone this repository

```bash
git clone https://github.com/treeverse/lakeFS-samples.git
cd lakeFS-samples
```

You now have two options: 

### **Run a Notebook server with your existing lakeFS Server**

If you have already [installed lakeFS](https://docs.lakefs.io/deploy/) or are utilizing [lakeFS cloud](https://lakefs.cloud/), all you need to run is the Jupyter notebook server:

```bash
docker compose up
```

Once the stack's up and running, open the Jupyter Notebook (http://localhost:8888) and check out the [catalog of sample notebooks](./00_notebooks/00_index.ipynb) to explore lakeFS. 

Once you've finished, run the following to remove all the containers: 

```bash
docker compose down
```

### **Don't have a lakeFS Server or Object Store?**

If you want to provision a lakeFS server as well as MinIO for your object store, plus Jupyter then bring up the full stack:

```bash
docker compose --profile local-lakefs up
```

As above, open the Jupyter Notebook (http://localhost:8888) peruse the [catalog of sample notebooks](./00_notebooks/00_index.ipynb) to explore lakeFS. 


## Environment Details

* **Jupyter Notebook** is based on the [Jupyter PySpark notebook](https://hub.docker.com/r/jupyter/pyspark-notebook/) and provides an interactive environment in which to explore lakeFS using Python and PySpark. 
* **lakeFS** can be provisioned as part of this environment, or provided by [lakeFS cloud](http://https://lakefs.cloud/) or your [own installation](https://docs.lakefs.io/deploy/).
* If you run lakeFS as part of this environment, **MinIO** is provided as an S3-compatible object store. If you run lakeFS yourself you can use other S3-compatible object stores include S3, GCS, as well as MinIO

### Containers

![](images/containers.excalidraw.png)

### URLs and login details

* Jupyter http://localhost:8888/

If you've brought up the full stack you'll also have: 

* LakeFS http://localhost:8000/ (`AKIAIOSFOLKFSSAMPLES` / `wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY`)
* MinIO http://localhost:9001/ (`minioadmin`/`minioadmin`)
* Spark UI http://localhost:4040/

## Other Examples

Under the [standalone_examples](./01_standalone_examples/) folder are a set of examples that need to be run on their own. Some use the repository's Docker Compose file and extend it, and others are self-contained and use their own Dockerfile. 

* [Airflow (1)](./01_standalone_examples/airflow-01/) - Four examples of using lakeFS with Airflow: 
    * Versioning DAGs and running pipeline from hooks using a configurable version of DAGs 
    * Isolating Airflow job run and atomic promotion to production
    * Integration of lakeFS with Airflow via Hooks
    * Troubleshooting production issues
    * Integration of lakeFS with Airflow and Databricks
    * Integration of lakeFS with Airflow and Iceberg
* [Airflow (2)](./01_standalone_examples/airflow-02/) - lakeFS + Airflow
* [Azure Databricks](./01_standalone_examples/azure-databricks/)
* [AWS Databricks](./01_standalone_examples/aws-databricks/)
* [Databricks CI/CD](./01_standalone_examples/databricks-ci-cd/)
* [AWS Glue and Athena](./01_standalone_examples/aws-glue-athena/)
* [AWS Glue and Trino](./01_standalone_examples/aws-glue-trino/)
* [lakeFS Iceberg REST Catalog with Trino client](./01_standalone_examples/trino/)
* [lakeFS + Dagster](./01_standalone_examples/dagster-integration/)
* [lakeFS + Prefect](./01_standalone_examples/prefect-integration/)
* [lakeFS Mount Demo: Fast Data Loading and Reproducibility for Deep Learning Workloads with lakeFS Mount](./01_standalone_examples/lakefs-mount-demo/)
* [Reproducibility and Building an AI Agent by using lakeFS, **LangChain** and **LLM/OpenAI** Models](./01_standalone_examples/llm-openai-langchain-integration/)<br/>_See also the [accompanying blog](https://lakefs.io/blog/lakefs-langchain-loader/)_
* [Image Segmentation Demo: ML Data Version Control and Reproducibility at Scale](./01_standalone_examples/image-segmentation/)
* [Multimodal Data Demo: ML Data Version Control and Reproducibility of Multimodal Data](./01_standalone_examples/multimodal-data-demo-local/)
* [Labelbox integration](./01_standalone_examples/labelbox-integration/)
* [Kafka integration](./01_standalone_examples/kafka/)
* [Flink integration](./01_standalone_examples/flink/)
* [Red Hat OpenShift AI integration](./01_standalone_examples/red-hat-openshift-ai/)
* [How to backup, migrate or clone a repo](./01_standalone_examples/backup-migrate-or-clone-repo/)
* [Running lakeFS with PostgreSQL as K/V store](./01_standalone_examples/docker-compose-with-postgres/)

## Got Questions or Want to Chat?

👉🏻 Join the lakeFS Slack group - https://lakefs.io/slack


## lakeFS — Iceberg & Lakehouse


> Source: `docs/data_engineering/lakefs/iceberg/README.md`

# Iceberg Examples with lakeFS

This directory contains examples demonstrating Apache Iceberg integration with lakeFS for versioned data lakehouse workflows.

## Examples

| Example | Description | Enterprise Required |
|---------|-------------|---------------------|
| [spark-basic](./spark-basic/) | Basic Spark + lakeFS integration | No |
| [spark-medallion](./spark-medallion/) | Medallion architecture (bronze/silver/gold) with Iceberg | Yes |
| [trino](./trino/) | Trino SQL queries with Iceberg REST Catalog | Yes |
| [write-audit-publish](./write-audit-publish/) | Write-Audit-Publish (WAP) pattern for data quality | No |

## Prerequisites

- Docker and Docker Compose installed
- For Enterprise examples: lakeFS Enterprise license

## Quick Start

Navigate to any example directory and run:

```bash
# For examples without local lakeFS:
docker compose up

# For full local stack:
docker compose --profile local-lakefs up
```

## Architecture

These examples demonstrate how lakeFS provides Git-like version control for Iceberg tables:

- **Branching**: Create isolated branches for development/testing
- **Commits**: Track changes with immutable commits
- **Merging**: Safely promote changes to production
- **Time Travel**: Query data at any point in history

## More Resources

- [lakeFS Documentation](https://docs.lakefs.io/)
- [Apache Iceberg](https://iceberg.apache.org/)
- [lakeFS + Iceberg Guide](https://docs.lakefs.io/integrations/iceberg.html)


> Source: `docs/data_engineering/lakefs/iceberg/spark-medallion/README.md`

# Iceberg Medallion Architecture with lakeFS

This example demonstrates the medallion architecture (bronze/silver/gold) pattern using Apache Iceberg tables with lakeFS version control.

## Overview

The medallion architecture organizes data into three layers:

- **Bronze**: Raw ingested data (as-is from source)
- **Silver**: Cleaned and validated data
- **Gold**: Business-level aggregations and features

Combined with lakeFS branching, you can:
- Develop transformations on isolated branches
- Test data quality before promotion
- Roll back any layer independently

## Prerequisites

- Docker and Docker Compose installed
- lakeFS Enterprise (for Iceberg REST Catalog)
- ~4GB disk space

## Quick Start

```bash
# Start with local lakeFS stack
docker compose --profile local-lakefs up

# Or connect to existing lakeFS
docker compose up
```

Then open:
- Jupyter: http://localhost:8888
- lakeFS UI: http://localhost:8000

## Notebook

- **iceberg-books-spark-medallion.ipynb** - Full medallion architecture demo

## What You'll Learn

- Setting up bronze/silver/gold Iceberg tables
- Using lakeFS branches for layer isolation
- Atomic promotion between layers
- Data quality validation at each stage

## Note

This example requires **lakeFS Enterprise** for the Iceberg REST Catalog functionality.

## More Resources

- [lakeFS Documentation](https://docs.lakefs.io/)
- [Medallion Architecture](https://www.databricks.com/glossary/medallion-architecture)
- [lakeFS + Iceberg](https://docs.lakefs.io/integrations/iceberg.html)


> Source: `docs/data_engineering/lakefs/iceberg/write-audit-publish/README.md`

# Write-Audit-Publish (WAP) Pattern with lakeFS

This example demonstrates the Write-Audit-Publish pattern for data quality assurance using Apache Iceberg branches with lakeFS.

## Overview

The WAP pattern ensures data quality before publishing to production:

1. **Write**: Write new data to an isolated branch
2. **Audit**: Run validation and quality checks
3. **Publish**: Merge to production only if checks pass

This pattern is essential for:
- Preventing bad data from reaching production
- Enabling data quality gates in pipelines
- Supporting rollback when issues are detected

## Prerequisites

- Docker and Docker Compose installed
- ~4GB disk space

## Quick Start

```bash
# Start with local lakeFS stack
docker compose --profile local-lakefs up

# Or connect to existing lakeFS
docker compose up
```

Then open:
- Jupyter: http://localhost:8888
- lakeFS UI: http://localhost:8000

## Notebook

- **wap-iceberg.ipynb** - Write-Audit-Publish workflow demo

## What You'll Learn

- Creating isolated write branches
- Running data quality validations
- Conditional merging based on audit results
- Rolling back failed publishes

## WAP Workflow

```
main (production)
  │
  └── write-branch
        │
        ├── Write new data
        ├── Run quality checks
        │
        └── If pass: Merge to main
            If fail: Delete branch
```

## More Resources

- [lakeFS Documentation](https://docs.lakefs.io/)
- [Write-Audit-Publish Guide](https://docs.lakefs.io/use_cases/production_data.html)
- [Data Quality with lakeFS](https://docs.lakefs.io/use_cases/data_quality.html)


> Source: `docs/data_engineering/lakefs/iceberg/spark-basic/README.md`

# Integration of lakeFS with Spark and Python

## Prerequisites

* Docker installed on your local machine

## Setup

1. Start by cloning this repository:

   ```bash
   git clone https://github.com/treeverse/lakeFS-samples && cd lakeFS-samples/01_standalone_examples/spark
   ```

2. Run the following to provision the stack which includes Python, Spark, Jupyter Notebook, JDK, Hadoop binaries and lakeFS Python client


   ```bash
   docker compose up 
   ```

   Alternatively, if you want to provision a lakeFS server as well as MinIO for your object store, plus Jupyter then bring up the full stack:

   ```bash
   docker compose --profile local-lakefs up
   ```

3. Open JupyterLab UI [http://127.0.0.1:8888/](http://127.0.0.1:8888/) in your web browser.

## Demo Instructions

Once you have successfully completed setup then open spark-demo notebook from JupyterLab UI.

> Source: `docs/data_engineering/lakefs/iceberg/trino/README.md`

# Integration of lakeFS Iceberg REST Catalog with Trino client

## Prerequisites

* Docker installed on your local machine

## Setup

1. Start by cloning this repository:

   ```bash
   git clone https://github.com/treeverse/lakeFS-samples && cd lakeFS-samples/01_standalone_examples/trino
   ```

2. To configure the lakeFS Iceberg connector in Trino, this sample provides a catalog properties file `lakefs.properties` that references the lakeFS iceberg connector.

* **_If you're not using lakeFS Enterprise server provided as part of the lakeFS Samples then change configuration properties for `iceberg.rest-catalog.uri`, `iceberg.rest-catalog.oauth2.server-uri` & `iceberg.rest-catalog.oauth2.credential` in this `lakefs.properties` file to match your lakeFS Enterprise environment_**

* **_Also, if you're not using the provided MinIO storage then change `s3.endpoint` (e.g. http://s3.us-east-1.amazonaws.com) and S3 credentials in this `lakefs.properties` file to match your storage_**

3. Run the following to provision the stack which includes Trino:

   ```bash
   docker compose up 
   ```

## Demo Instructions

Once you have successfully completed setup then open `iceberg-books-trino` notebook provided with lakeFS Enterprise Samples from the JupyterLab UI and follow the instructions.

## lakeFS — ML & AI Integration


> Source: `docs/data_engineering/lakefs/ml/README.md`

# ML/AI Examples with lakeFS

This directory contains examples demonstrating machine learning and AI workflows with lakeFS for data versioning and reproducibility.

## Examples

| Example | Description | Requirements |
|---------|-------------|--------------|
| [llm-langchain](./llm-langchain/) | AI agents with LangChain + OpenAI | OpenAI API key |
| [image-segmentation](./image-segmentation/) | PyTorch + MLflow ML reproducibility | ~10GB disk |
| [ml-reproducibility](./ml-reproducibility/) | ML experimentation tracking | ~4GB disk |

## Why lakeFS for ML?

- **Data Versioning**: Track exact datasets used for each training run
- **Reproducibility**: Recreate any experiment by checking out the corresponding data version
- **Feature Store**: Version feature tables alongside model artifacts
- **A/B Testing**: Use branches to test different data preprocessing strategies
- **Lineage**: Track which data produced which model

## Quick Start

Navigate to any example directory and run:

```bash
docker compose --profile local-lakefs up
```

## Architecture

```
lakeFS Repository
├── main branch (production data)
├── experiment-1 branch (training data v1)
├── experiment-2 branch (training data v2)
└── feature-engineering branch (new features)
```

## More Resources

- [lakeFS Documentation](https://docs.lakefs.io/)
- [ML Reproducibility Guide](https://docs.lakefs.io/use_cases/ml.html)
- [lakeFS + MLflow](https://docs.lakefs.io/integrations/mlflow.html)


> Source: `docs/data_engineering/lakefs/ml/image-segmentation/README.md`

# Image Segmentation Demo - Run Locally

Start by ⭐️ starring [lakeFS open source](https://go.lakefs.io/oreilly-course) project.

This repository includes a Jupyter Notebook which you can run on your local machine. The notebook demonstrates ML Data Version Control and Reproducibility at Scale.

In the ever-evolving landscape of machine learning (ML), data stands as the cornerstone upon which triumphant models are built. However, as ML projects expand and encompass larger and more complex datasets, the challenge of efficiently managing and controlling data at scale becomes more pronounced.

* Breaking Down Conventional Approaches:
1. The Copy/Paste Predicament: In the world of data science, it's commonplace for data scientists to extract subsets of data to their local environments for model training. This method allows for iterative experimentation, but it introduces challenges that hinder the seamless evolution of ML projects.
2. Reproducibility Constraints: Traditional practices of copying and modifying data locally lack the version control and audit-ability crucial for reproducibility. Iterating on models with various data subsets becomes a daunting task.
3. Inefficient Data Transfer: Regularly shuttling data between the central repository and local environments strains resources and time, especially when choosing different subsets of data for each training run.

* In this demo, we will demonstrate:
1. How to use lakeFS to version control your data when working with your data locally.
3. We will be leveraging the technology stack of: MinIO, Delta Lake, PyTorch and MLflow


## Prerequisites
* Docker installed on your local machine

## Setup

1. Start by cloning this repository:

   ```bash
   git clone https://github.com/treeverse/lakeFS-samples && cd lakeFS-samples/01_standalone_examples/image-segmentation-local
   ```

2. Run the following to provision the full stack which includes lakeFS, MinIO, Python, Spark, Jupyter Notebook, JDK, Hadoop binaries and lakeFS Python client

   ```bash
   docker compose --profile local-lakefs up
   ```

   If any of the port numbers (8893, 4043, 5002, 8003, 9002 and 9003) are already in use then change the port numbers in docker-compose.yml file to any available ports.

3. Open JupyterLab UI [http://127.0.0.1:8893/](http://127.0.0.1:8893/) in your web browser.

## Demo Instructions

1. Once you have successfully completed setup then open "Image Segmentation" notebook from JupyterLab UI and follow the instructions.


> Source: `docs/data_engineering/lakefs/ml/llm-langchain/README.md`

# Reproducibility and Building an AI Agent by using lakeFS, LangChain and LLM/OpenAI Models

Start by ⭐️ starring [lakeFS open source](https://go.lakefs.io/oreilly-course) project.

This repository includes Jupyter Notebooks with LangChain and OpenAI libraries which you can run on your local machine.

## Let's Get Started 👩🏻‍💻

Clone this repository

   ```bash
   git clone https://github.com/treeverse/lakeFS-samples && cd lakeFS-samples/01_standalone_examples/llm-openai-langchain-integration
   ```

You now have two options: 

### **Run a Notebook server with your existing lakeFS Server**

If you have already [installed lakeFS](https://docs.lakefs.io/deploy/) or are utilizing [lakeFS cloud](https://lakefs.cloud/), all you need to run is the Jupyter notebook with LangChain and OpenAI libraries (Docker image size will be around 10GB):


   ```bash
   docker compose up 
   ```

### **Don't have a lakeFS Server or Object Store?**

If you want to provision a lakeFS server as well as MinIO for your object store, plus Jupyter with LangChain and OpenAI libraries then bring up the full stack:

   ```bash
   docker compose --profile local-lakefs up
   ```

### URLs and login details

* Jupyter http://localhost:8891/

If you've brought up the full stack you'll also have: 

* LakeFS http://localhost:48000/ (`AKIAIOSFOLKFSSAMPLES` / `wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY`)
* MinIO http://localhost:49001/ (`minioadmin`/`minioadmin`)


## Demo Instructions

Open Jupyter UI [http://localhost:8891](http://localhost:8891) in your web browser, open one of the provided notebooks from JupyterLab UI and follow the instructions:

1. AI Agent Demo: Build an AI Agent by using lakeFS, LangChain and OpenAI
2. LLM OpenAI LangChain Demo: Reproducibility and Data version control for LangChain and LLM/OpenAI Models


> Source: `docs/data_engineering/lakefs/lakeFS-samples/01_standalone_examples/llm-openai-langchain-integration/README.md`

# Reproducibility and Building an AI Agent by using lakeFS, LangChain and LLM/OpenAI Models

Start by ⭐️ starring [lakeFS open source](https://go.lakefs.io/oreilly-course) project.

This repository includes Jupyter Notebooks with LangChain and OpenAI libraries which you can run on your local machine.

## Let's Get Started 👩🏻‍💻

Clone this repository

   ```bash
   git clone https://github.com/treeverse/lakeFS-samples && cd lakeFS-samples/01_standalone_examples/llm-openai-langchain-integration
   ```

You now have two options: 

### **Run a Notebook server with your existing lakeFS Server**

If you have already [installed lakeFS](https://docs.lakefs.io/deploy/) or are utilizing [lakeFS cloud](https://lakefs.cloud/), all you need to run is the Jupyter notebook with LangChain and OpenAI libraries (Docker image size will be around 10GB):


   ```bash
   docker compose up 
   ```

### **Don't have a lakeFS Server or Object Store?**

If you want to provision a lakeFS server as well as MinIO for your object store, plus Jupyter with LangChain and OpenAI libraries then bring up the full stack:

   ```bash
   docker compose --profile local-lakefs up
   ```

### URLs and login details

* Jupyter http://localhost:8891/

If you've brought up the full stack you'll also have: 

* LakeFS http://localhost:48000/ (`AKIAIOSFOLKFSSAMPLES` / `wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY`)
* MinIO http://localhost:49001/ (`minioadmin`/`minioadmin`)


## Demo Instructions

Open Jupyter UI [http://localhost:8891](http://localhost:8891) in your web browser, open one of the provided notebooks from JupyterLab UI and follow the instructions:

1. AI Agent Demo: Build an AI Agent by using lakeFS, LangChain and OpenAI
2. LLM OpenAI LangChain Demo: Reproducibility and Data version control for LangChain and LLM/OpenAI Models


> Source: `docs/data_engineering/lakefs/lakeFS-samples/01_standalone_examples/image-segmentation/README.md`

# Image Segmentation Demo

Start by ⭐️ starring [lakeFS open source](https://go.lakefs.io/oreilly-course) project.

This repository includes a Jupyter Notebook which you can run on your local machine. The notebook demonstrates ML Data Version Control and Reproducibility at Scale.

In the ever-evolving landscape of machine learning (ML), data stands as the cornerstone upon which triumphant models are built. However, as ML projects expand and encompass larger and more complex datasets, the challenge of efficiently managing and controlling data at scale becomes more pronounced.

* Breaking Down Conventional Approaches:
1. The Copy/Paste Predicament: In the world of data science, it's commonplace for data scientists to extract subsets of data to their local environments for model training. This method allows for iterative experimentation, but it introduces challenges that hinder the seamless evolution of ML projects.
2. Reproducibility Constraints: Traditional practices of copying and modifying data locally lack the version control and audit-ability crucial for reproducibility. Iterating on models with various data subsets becomes a daunting task.
3. Inefficient Data Transfer: Regularly shuttling data between the central repository and local environments strains resources and time, especially when choosing different subsets of data for each training run.
4. Limited Compute Power: Operating within a local environment hampers the ability to harness the full power of parallel computing, as well as the distributed prowess of systems like Apache Spark.

* In this demo, we will demonstrate:
1. How to use lakeFS to version control your data when working with your data locally.
2. How to use lakeFS without the need to copy data and train your model at scale directly on the Cloud.
3. We will be leveraging the technology stack of: AWS S3, Databricks Delta Lake, PyTorch and MLflow


## Prerequisites
* Docker installed on your local machine
* This demo requires connecting to a lakeFS Server. You can spin up lakeFS Server for free on the lakeFS cloud (https://lakefs.cloud). 

## Setup

1. Start by cloning this repository:

   ```bash
   git clone https://github.com/treeverse/lakeFS-samples && cd lakeFS-samples/01_standalone_examples/image-segmentation
   ```

2. Run following commands to build and run Docker container which includes Python, Spark, Jupyter Notebook and required Python packages (Docker image size is around 10GB):

   ```bash
      docker build -t lakefs-image-segmentation-demo .

      docker run -d -p 8889:8888 -p 4041:4040 -p 5001:5000 --user root -e GRANT_SUDO=yes -v $PWD:/home/jovyan -v $PWD/jupyter_notebook_config.py:/home/jovyan/.jupyter/jupyter_notebook_config.py --name lakefs-image-segmentation-demo lakefs-image-segmentation-demo
   ```

If any of the port numbers (8889, 4041 and 5001) are already in use then change the port numbers to any available ports.

3. Open JupyterLab UI [http://127.0.0.1:8889/](http://127.0.0.1:8889/) in your web browser.

## Demo Instructions

1. Once you have successfully completed setup then open "Image Segmentation" notebook from JupyterLab UI and follow the instructions.
2. If you want to run same notebook on the Databricks cluster:
    * Use Databricks Runtime version "14.3 LTS ML". GPUs are not required for this demo.
    * Install pytorch-lightning==1.5.4, segmentation-models-pytorch==0.3.3 and lakefs==0.4.1 Python libraries on your Databricks Compute cluster. Also, install io.lakefs:hadoop-lakefs-assembly:0.2.3 library from [Maven repository](https://mvnrepository.com/artifact/io.lakefs/hadoop-lakefs-assembly).
    * Follow [Databricks and lakeFS Integration: Step-by-Step Configuration Tutorial](https://lakefs.io/blog/databricks-lakefs-integration-tutorial/) to configure your Databricks Compute cluster.
    * Import "Image Segmentation" and "ImageSegmentationSetup" notebooks to your Databricks environment.


> Source: `docs/data_engineering/lakefs/lakeFS-samples/01_standalone_examples/labelbox-integration/README.md`

# Labelbox Integration

Start by ⭐️ starring [lakeFS open source](https://go.lakefs.io/oreilly-course) project.

This repository includes a Jupyter Notebook which you can run on your local machine.

## Prerequisites
* Docker installed on your local machine
* This demo requires connecting to a lakeFS Server. You can either install lakeFS Server locally (https://docs.lakefs.io/quickstart.html), or spin up for free on the lakeFS cloud (https://lakefs.cloud). 
* This demo also requires connecting to Labelbox. You can signup for free for Labelbox (https://app.labelbox.com/signup)

## Setup

1. Start by cloning this repository:

   ```bash
   git clone https://github.com/treeverse/lakeFS-samples && cd lakeFS-samples/01_standalone_examples/labelbox-integration
   ```

2. Run following commands to download and run Docker container which includes Python, Spark, Jupyter Notebook, JDK, Hadoop binaries and lakeFS Python client (Docker image size is around 4GB):

   ```bash
      docker build -t lakefs-labelbox-integration-demo .

      docker run -d -p 38888:8888 -p 34040:4040 --user root -e GRANT_SUDO=yes -v $PWD:/home/jovyan -v $PWD/jupyter_notebook_config.py:/home/jovyan/.jupyter/jupyter_notebook_config.py --name lakefs-labelbox-integration-demo lakefs-labelbox-integration-demo
   ```

3. Open JupyterLab UI [http://127.0.0.1:38888/](http://127.0.0.1:38888/) in your web browser.

## Demo Instructions

Once you have successfully completed setup then open "Labelbox Demo" notebook from JupyterLab UI and follow the instructions.


## lakeFS — Workflow Orchestration


> Source: `docs/data_engineering/lakefs/dagster-integration/README.md`

# Integration of lakeFS with Dagster

## Prerequisites

* Docker installed on your local machine

## Setup

1. Start by cloning this repository:

   ```bash
   git clone https://github.com/treeverse/lakeFS-samples && cd lakeFS-samples/01_standalone_examples/dagster-integration
   ```

2. Run the following to provision the stack which includes Python, Spark, Jupyter Notebook, JDK, Hadoop binaries and lakeFS Python client


   ```bash
   docker compose up 
   ```

   Alternatively, if you want to provision a lakeFS server as well as MinIO for your object store, plus Jupyter then bring up the full stack:

   ```bash
   docker compose --profile local-lakefs up
   ```

3. Open JupyterLab UI [http://127.0.0.1:28888/](http://127.0.0.1:28888/) in your web browser.

## Demo Instructions

Once you have successfully completed setup then open one of the provided notebooks from JupyterLab UI: 

* Dagster Demo Existing DAG
* Dagster Demo New DAG

> Source: `docs/data_engineering/lakefs/lakeFS-samples/01_standalone_examples/airflow-01/README.md`

# Integration of lakeFS with Airflow and Hooks

Start by ⭐️ starring [lakeFS open source](https://go.lakefs.io/oreilly-course) project.

This repository includes following Jupyter Notebooks which you can run on your local machine:

1. Airflow Demo Existing DAG:
* Integration of lakeFS with Airflow
* Use Case: Isolating Airflow job run and atomic promotion to production

2. Airflow Demo New DAG:
* Integration of lakeFS with Airflow
* Use Case: Troubleshooting production issues

3. Hooks Airflow Demo:
* Integration of lakeFS with Airflow via Hooks
* Use Case: Isolated Ingestion & ETL Environment

4. Airflow DAG Versioning Demo:
* Integration of lakeFS with Airflow via Hooks
* Use Case: Versioning DAGs and running pipeline from hooks using a configurable version of DAGs

5. Databricks:
* Integration of lakeFS with Airflow and Databricks
* Use Case: Run Databricks notebook via Airflow DAG

6. Iceberg:
* Integration of lakeFS with Airflow and Iceberg
* Use Case: Isolating Airflow job run and atomic promotion to production

## Prerequisites
* Docker installed on your local machine
* lakeFS installed and running on your local machine or on a server or in the cloud. If you don't have lakeFS already running then either use [lakeFS Playground](https://demo.lakefs.io/) which provides lakeFS server on-demand with a single click or refer to [lakeFS Quickstart](https://docs.lakefs.io/quickstart/) doc.

## Setup

1. Start by cloning this repository:

   ```bash
   git clone https://github.com/treeverse/lakeFS-samples && cd lakeFS-samples/01_standalone_examples/airflow-01
   ```

2. Run following commands to download and run Docker container which includes Python, Spark, Jupyter Notebook, JDK, Hadoop binaries, lakeFS Python client and Airflow (Docker image size is around 4.5GB):

   ```bash
      docker build -t lakefs-airflow-integration-demo .

      docker run -d -p 18888:8888 -p 14040:4040 -p 8080:8080 --user root -e GRANT_SUDO=yes -v $PWD:/home/jovyan -v $PWD/jupyter_notebook_config.py:/home/jovyan/.jupyter/jupyter_notebook_config.py --name lakefs-airflow-integration-demo lakefs-airflow-integration-demo
   ```

3. Open JupyterLab UI [http://127.0.0.1:18888/](http://127.0.0.1:18888/) in your web browser.

## Demo Instructions

Once you have successfully completed setup then open any notebook from JupyterLab UI and follow the instructions.



> Source: `docs/data_engineering/lakefs/lakeFS-samples/01_standalone_examples/airflow-02/README.md`

## lakeFS + Github + Airflow - example

This sample will give you an idea of how you can use the [lakeFS Airflow provider](https://github.com/treeverse/airflow-provider-lakeFS) to:
* Version control your raw, intermediate and processed data.
* Link between code versions and the data generated by running them.

![](assets/git-lakefs-airflow.png)

### Run Instructions

1. Clone the sample: 

    ```
    git clone https://github.com/treeverse/lakeFS-samples
    cd lakeFS-samples
    git submodule init && git submodule update

1. Spin up the environment:
   `docker-compose up`

1. Browse to Airflow in [http://localhost:8080/](http://localhost:8080/). 

      * User: `airflow`
      * Password: `airflow`

1. Run the _etl_ DAG in Airflow

      ![](assets/airflow-ui-01.png)

1. Observe the results in lakeFS. Login to the lakeFS UI in [http://localhost:8080/](http://localhost:8080/)

      * User: `AKIAIOSFOLKFSSAMPLES`
      * Password: `wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY`

1. In the `airflow-example` repository's [`main` branch](http://localhost:8000/repositories/airflow-example/objects) you'll see the raw data alongside the transformed results

      ![](assets/lakefs-ui-01.png)

1. Drill down on any path to view the CSV file and get an understanding of the transform process

      ![](assets/lakefs-ui-02.png)

1. Click on the **Commits** tab to see the commit history for the branch. Change the branch from the dropdown menu to see the history for each branch. 

1. From the **Branches** tab note that each transform (by event type / month / user) was isolated on its own branch and only merged back into `main` once it was completed sucessfully. 

      ![](assets/lakefs-ui-03.png)

Here's the [DAG](./dags/dag.py) that's used: 

![](assets/airflow-ui-02.png)

## Containers

The Docker Compose in this folder extends the one in the root of this repository to add the necessary containers for Airflow:

![](./assets/containers.excalidraw.png)

> Source: `docs/data_engineering/lakefs/lakeFS-samples/01_standalone_examples/prefect-integration/README.md`

# Integration of lakeFS with Prefect

Start by ⭐️ starring [lakeFS open source](https://go.lakefs.io/oreilly-course) project.

This repository includes a Jupyter Notebook with Prefect which you can run on your local machine.

## Let's Get Started 👩🏻‍💻

Clone this repository

   ```bash
   git clone https://github.com/treeverse/lakeFS-samples && cd lakeFS-samples/01_standalone_examples/prefect-integration
   ```

You now have two options: 

### **Run a Notebook server with your existing lakeFS Server**

If you have already [installed lakeFS](https://docs.lakefs.io/deploy/) or are utilizing [lakeFS cloud](https://lakefs.cloud/), all you need to run is the Jupyter notebook and Prefect server:


   ```bash
   docker compose up 
   ```

### **Don't have a lakeFS Server or Object Store?**

If you want to provision a lakeFS server as well as MinIO for your object store, plus Jupyter and Prefect then bring up the full stack:

   ```bash
   docker compose --profile local-lakefs up
   ```

### URLs and login details

* Jupyter http://localhost:58888/
* Prefect UI http://localhost:4200/

If you've brought up the full stack you'll also have: 

* LakeFS http://localhost:58000/ (`AKIAIOSFOLKFSSAMPLES` / `wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY`)
* MinIO http://localhost:59001/ (`minioadmin`/`minioadmin`)


## Demo Instructions

Open Jupyter UI [http://localhost:58888](http://localhost:58888) in your web browser. Open either "Prefect Demo Existing DAG" or "Prefect Demo New DAG" notebook from Jupyter UI and follow the instructions.

## lakeFS — Standalone Examples


> Source: `docs/data_engineering/lakefs/delta-lake/README.md`

# Delta Lake with lakeFS

This example demonstrates Delta Lake integration with lakeFS for versioned data lake workflows.

## Overview

Delta Lake is an open-source storage layer that brings ACID transactions to Apache Spark and big data workloads. Combined with lakeFS, you get:

- **Git-like versioning** for Delta tables
- **Branch isolation** for safe experimentation
- **Atomic commits** across multiple tables
- **Time travel** at the repository level

## Prerequisites

- Docker and Docker Compose installed
- ~4GB disk space

## Quick Start

```bash
# Start with local lakeFS stack
docker compose --profile local-lakefs up

# Or connect to existing lakeFS
docker compose up
```

Then open:
- Jupyter: http://localhost:8888
- lakeFS UI: http://localhost:8000

## Notebook

- **delta-lake.ipynb** - Demonstrates Delta Lake versioning with lakeFS branching

## What You'll Learn

- Creating Delta tables on lakeFS
- Using branches for isolated development
- Merging changes safely to production
- Rolling back to previous versions

## More Resources

- [lakeFS Documentation](https://docs.lakefs.io/)
- [Delta Lake](https://delta.io/)
- [lakeFS + Delta Lake Guide](https://docs.lakefs.io/integrations/delta.html)


> Source: `docs/data_engineering/lakefs/lakeFS-samples/00_notebooks/write-audit-publish/README.md`

# Write-Audit-Publish (WAP)

Write-Audit-Publish (WAP) is a pattern in data engineering to give greater control over data quality. It was popularised by Netflix back in 2017 in a talk by [Michelle Winters](https://www.linkedin.com/in/mufford/) at the DataWorks Summit called "[*Whoops the Numbers are wrong! Scaling Data Quality @ Netflix*](https://www.youtube.com/watch?v=fXHdeBnpXrg)". 

These notebooks can be used to experiment with the pattern implementations in different technologies. 

Please see the accompanying blog series for more details: 

1. [Data Engineering Patterns: Write-Audit-Publish (WAP)](https://lakefs.io/blog/data-engineering-patterns-write-audit-publish)
1. [How to Implement Write-Audit-Publish (WAP)](https://lakefs.io/blog/how-to-implement-write-audit-publish)
1. [Putting the Write-Audit-Publish Pattern into Practice with lakeFS](https://lakefs.io/blog/write-audit-publish-with-lakefs/)

## Usage

All of the notebooks except Nessie will run using the existing docker-compose.yml file that's in the root of the repository. 

For the Project Nessie notebook use the provided `docker-compose-nessie.yml` file: 

```bash
docker compose -f docker-compose-nessie.yml up
```


> Source: `docs/data_engineering/lakefs/lakeFS-samples/01_standalone_examples/kafka/README.md`

# Integration of lakeFS with Apache Kafka

Start by ⭐️ starring [lakeFS open source](https://go.lakefs.io/oreilly-course) project.

This repository includes a Jupyter Notebook with Kafka which you can run on your local machine.

## Let's Get Started 👩🏻‍💻

Clone this repository

   ```bash
   git clone https://github.com/treeverse/lakeFS-samples && cd lakeFS-samples/01_standalone_examples/kafka
   ```

You now have two options: 

### **Run a Notebook server with your existing lakeFS Server**

If you have already [installed lakeFS](https://docs.lakefs.io/deploy/) or are utilizing [lakeFS cloud](https://lakefs.cloud/), all you need to run is the Jupyter notebook and Kafka:


   ```bash
   docker compose up 
   ```

### **Don't have a lakeFS Server or Object Store?**

If you want to provision a lakeFS server as well as MinIO for your object store, plus Jupyter and Kafka then bring up the full stack:

   ```bash
   docker compose --profile local-lakefs up
   ```

### URLs and login details

* Jupyter http://localhost:8890/

If you've brought up the full stack you'll also have: 

* LakeFS http://localhost:18000/ (`AKIAIOSFOLKFSSAMPLES` / `wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY`)
* MinIO http://localhost:19001/ (`minioadmin`/`minioadmin`)


## Demo Instructions

Open Jupyter UI [http://localhost:8890](http://localhost:8890) in your web browser. Open "Kafka Streaming Demo" notebook from Jupyter UI and follow the instructions.

> Source: `docs/data_engineering/lakefs/lakeFS-samples/01_standalone_examples/flink/README.md`

# Integration of lakeFS with Apache Flink

Start by ⭐️ starring [lakeFS open source](https://go.lakefs.io/oreilly-course) project.

This repository includes lakeFS with Flink which you can run on your local machine.

## Let's Get Started 👩🏻‍💻

Clone this repository

   ```bash
   git clone https://github.com/treeverse/lakeFS-samples && cd lakeFS-samples/01_standalone_examples/flink
   ```

You now have two options: 

### **Run a Flink server with your existing lakeFS Server**

If you have already [installed lakeFS](https://docs.lakefs.io/deploy/) or are utilizing [lakeFS cloud](https://lakefs.cloud/) then follow these steps:

   1. lakeFS uses [S3 Gateway](https://docs.lakefs.io/understand/architecture.html#s3-gateway) to communicate with Flink. So, change `fs.s3a.endpoint`, `fs.s3a.access.key` and `fs.s3a.secret.key` Flink properties for `jobmanager` and `taskmanager` services in `docker-compose.yml` file to lakeFS endpoint e.g. `https://username.aws_region_name.lakefscloud.io`(if you are using lakeFS Cloud), lakeFS Access Key and lakeFS Secret Key:

      ```bash
      FLINK_PROPERTIES=
      jobmanager.rpc.address: jobmanager  
      state.backend: filesystem 
      fs.s3a.path.style.access: true
      fs.s3a.endpoint: http://lakefs:8000
      fs.s3a.access.key: AKIAIOSFOLKFSSAMPLES
      fs.s3a.secret.key: wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY
      ```

   2. Run only Flink server:

      ```bash
      docker compose up 
      ```

### **Don't have a lakeFS Server or Object Store?**

If you want to provision a lakeFS server as well as MinIO for your object store, plus Flink then bring up the full stack:

   ```bash
   docker compose --profile local-lakefs up
   ```

### URLs and login details

* Flink Dashboard http://localhost:8081/

If you've brought up the full stack you'll also have: 

* LakeFS http://localhost:38000/ (`AKIAIOSFOLKFSSAMPLES` / `wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY`)
* MinIO http://localhost:39001/ (`minioadmin`/`minioadmin`)


## Demo Instructions

To deploy Flink's example Word Count job to the running Flink server, issue the following command. This job will read the `README.md` file from the `main` branch of `quickstart` lakeFS repository and will write the output back to `word-count` folder in the same lakeFS repository & branch. If you want to use another lakeFS repository/branch or another text file then change the command accordingly:

   ```bash
   docker exec -it lakefs-with-flink-jobmanager \
   ./bin/flink run examples/streaming/WordCount.jar \
   --input s3://quickstart/main/README.md \
   --output s3://quickstart/main/word-count 
   ```


> Source: `docs/data_engineering/lakefs/lakeFS-samples/01_standalone_examples/databricks-ci-cd/README.md`

# lakeFS-samples-ci-cd

Start by ⭐️ starring [lakeFS open source](https://go.lakefs.io/oreilly-course) project.

Data engineers typically don't develop against production data due to concerns regarding PII, time, and scale. Instead, they develop ETL jobs on a subset of data and promote code via Git. The challenge is that this code is not tested on production data until promotion. This process can lead to issues because the subset of data used will differ from the production environment.

### Solution with lakeFS: ###

-Git Action Integration: lakeFS can use a Git action during pull requests to import code to lakeFS

-Isolated Production Copy: Every promotion creates an isolated copy of the production data using a [zero-copy import](https://docs.lakefs.io/understand/performance-best-practices.html#use-zero-copy-import) to lakeFS

-Safe Testing: Code runs against this isolated copy, allowing testing in a production-like environment

-Safety Net: If anything fails, the code isn't promoted, providing a safety net

This demo shows how lakeFS uses Git actions to perform a zero-copy import of production data for ETL promotions in both Python and Scala. This allows testing against production-like data and only promotes successful code changes. In this demo, we’ll see how changing an ETL job can trigger a validation error through a Git action.

## Prerequisites
* lakeFS installed and running on a server or in the cloud. If you don't have lakeFS already running then either use [lakeFS Cloud](https://demo.lakefs.io/) which provides free lakeFS server on-demand with a single click or refer to [lakeFS Quickstart](https://docs.lakefs.io/quickstart/) doc.
* Databricks server with the ability to run compute clusters on top of it. 
* Configure your Databricks cluster to use the lakeFS Hadoop file system. Read this blog [Databricks and lakeFS Integration: Step-by-Step Configuration Tutorial](https://lakefs.io/blog/databricks-lakefs-integration-tutorial/) or [lakeFS documentation](https://docs.lakefs.io/integrations/spark.html#lakefs-hadoop-filesystem) for the configuration.
* Permissions to manage the cluster configuration, including adding libraries. 
* GitHub account. 

## Setup

1. Create [Databricks personal access token](https://docs.databricks.com/en/dev-tools/auth/pat.html).


1. Create Databricks secret scope e.g. **demos** or use an existing secret scope. Add following secrets in that secret scope by following [Secret management docs](https://docs.databricks.com/en/security/secrets/index.html): 

       lakefs_access_key_id e.g. 'AKIAIOSFOLKFSSAMPLES'

       lakefs_secret_access_key e.g. 'wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY'

    You can use following Databricks commands to create secrets:
   ```bash
   databricks secrets put-secret --json '{
     "scope": "demos",
     "key": "lakefs_access_key_id",
     "string_value": "AKIAIOSFOLKFSSAMPLES"
   }'

   databricks secrets put-secret --json '{
     "scope": "demos",
     "key": "lakefs_secret_access_key",
     "string_value": "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY"
   }'
   ```

1. Create a Git repository. It can be named **lakeFS-samples-ci-cd**.

1. Clone this repository:

   ```bash
   git clone https://github.com/treeverse/lakeFS-samples && cd lakeFS-samples/01_standalone_examples/databricks-ci-cd
   ```

1. Create folders **.github/workflows** and **databricks-notebooks** in your Git repo.

1. Upload **pr_commit_run_databricks_etl_job.yml** file in **lakeFS-samples/01_standalone_examples/databricks-ci-cd/.github/workflows** folder to **.github/workflows** folder in your Git repo.

1. Upload all files in **lakeFS-samples/01_standalone_examples/databricks-ci-cd/databricks-notebooks** folder to **databricks-notebooks** folder in your Git repo.

1. Add following secrets in your Git repo by following [Creating secrets for a repository docs](https://docs.github.com/en/actions/security-guides/using-secrets-in-github-actions#creating-secrets-for-a-repository). This is the Databricks token created in 1st step above. If you copy & paste the secret name then verify that there are no spaces before and after the secret name.

       DATABRICKS_TOKEN


1. Add following variables in your Git repo by following [Creating configuration variables for a repository docs](https://docs.github.com/en/actions/learn-github-actions/variables#creating-configuration-variables-for-a-repository):
* Variable to store your [Databricks host name or URL](https://docs.databricks.com/en/workspace/workspace-details.html#workspace-instance-names-urls-and-ids) e.g. https://cust-success.cloud.databricks.com

      DATABRICKS_HOST

* Variable to store your [Databricks Cluster ID](https://docs.databricks.com/en/workspace/workspace-details.html#cluster-url-and-id) e.g. 1115-164516-often242

      DATABRICKS_CLUSTER_ID

* Variable to store your [Databricks Workspace Folder path](https://docs.databricks.com/en/workspace/workspace-details.html#folder-id) e.g. /Shared/lakefs_demos/ci_cd_demo or /Users/me@example.com/MyFolder/lakefs_demos/ci_cd_demo

      DATABRICKS_WORKSPACE_NOTEBOOK_PATH

* Variable to store your Databricks Secret Scope created in 2nd step e.g. demos

      DATABRICKS_SECRET_SCOPE

* Variable to store your lakeFS Endpoint e.g. https://company.region.lakefscloud.io

      LAKEFS_END_POINT

* Variable to store your lakeFS repository name (which will be created by this demo) e.g. databricks-ci-cd-repo

      LAKFES_REPO_NAME

* Variable to store the storage namespace for the lakeFS repo. It is a location in the underlying storage where data for the lakeFS repository will be stored. e.g. s3://example

      LAKEFS_REPO_STORAGE_NAMESPACE

* Variable to store the storage namespace where Delta tables created by this demo will be stored e.g. s3://data-source/delta-tables. Do NOT use the same storage namespace as above.

  If it is not there then create Databricks [External Location](https://docs.databricks.com/en/sql/language-manual/sql-ref-external-locations.html) to write to s3://data-source URL and you should have **READ FILES** and **WRITES FILES** [permissions on and External Location](https://docs.databricks.com/en/connect/unity-catalog/manage-external-locations.html#grant-permissions-on-an-external-location)

      DATA_SOURCE_STORAGE_NAMESPACE

## Demo Instructions for Python ETL Jobs

1. Create a new branch in your Git repository. Select the newly created branch.
<img src="./files/images/1-CreateBranch.gif" width="534" height="303"/>
1. Remove the comment from the last 5 lines of code in **ETL Job.py** inside the **databricks-notebooks** folder and Commit your changes.
<img src="./files/images/2-remove Last 5 lines.gif" width="534" height="303"/>
1. Go to the **Pull requests** tab in your Git repo, create Pull Request.
<img src="./files/images/3-Create PR.gif" width="534" height="303"/>
1. Go to the **Actions** tab in your Git repo. Git Action will start running automatically and validation checks will fail.
<img src="./files/images/4-actions.gif" width="534" height="303"/>
1. Go back to the **Code** tab in your Git repo and select the branch created in 1st step. Comment back the last 5 lines of code in **ETL Job.py** and Commit your changes.

   <img src="./files/images/5-fixCode.gif" width="534" height="303"/>
1. Go back to the **Actions** tab in your Git repo. Git Action will start running again and validation checks will pass this time.
<img src="./files/images/6-PassedETL.gif" width="534" height="303"/>

We just safely promoted our ETL jobs using lakeFS and Git actions. By creating a branch, modifying code, and running validation checks, you ensured that changes are tested in an isolated environment. 

For a Scala ETL job demo, go to the "scala-demo" section. Below, find useful references for this demo, and for Git actions.

## Useful Information

1. Databricks [Continuous integration and delivery using GitHub Actions](https://docs.databricks.com/en/dev-tools/ci-cd/ci-cd-github.html).
1. Information on how to [run Databricks notebooks from GitHub Action](https://github.com/databricks/run-notebook/tree/main).
1. See [action.yml](https://github.com/databricks/run-notebook/blob/main/action.yml) for the latest interface and docs for databricks/run-notebook.
1. [Databricks REST API reference](https://docs.databricks.com/api/workspace/introduction).
1. GitHub [Events that trigger workflows](https://docs.github.com/en/actions/using-workflows/events-that-trigger-workflows).
1. GitHub [Webhook events and payloads](https://docs.github.com/en/webhooks/webhook-events-and-payloads).
1. GitHub [Payloads for Pull Request](https://docs.github.com/en/webhooks/webhook-events-and-payloads?actionType=closed#pull_request).
1. Documentation on [GitHub Action that uploads a file to Amazon S3](https://github.com/hkusu/s3-upload-action)
1. Documentation on [GitHub Action that uploads a file to Databricks DFBS](https://github.com/databricks/upload-dbfs-temp/)

## Additional Useful GitHub Action Code

1. Code to run the Action workflow only if any file changes in a specific folder e.g. databricks-notebooks. So, changing README file, which is outside the databricks-notebooks folder, will not run the workflow:

   ```bash
   name: Run Databricks ETL jobs in an isolated environment by using lakeFS

   on:
      pull_request:
         paths:
            - 'databricks-notebooks/**'
   ```

1. Upload a file to S3 e.g. upload Scala JAR file:

   ```bash
      - name: Upload JAR file to S3
        uses: hkusu/s3-upload-action@v2
        id: upload_file_to_s3
        with:
          aws-access-key-id: ${{secrets.AWS_ACCESS_KEY}}
          aws-secret-access-key: ${{secrets.AWS_SECRET_KEY}}
          aws-region: ${{ vars.AWS_REGION }}
          aws-bucket: ${{ vars.AWS_BUCKET_FOR_JARS }}
          bucket-root: ${{ vars.AWS_BUCKET_ROOT_FOLDER_FOR_JARS }}
          destination-dir: "jars/pr-${{ github.event.number }}"
          file-path: "${{ env.LOCAL_NOTEBOOK_PATH }}/scala_etl_jobs/target/scala-2.12/etl_jobs-assembly-0.1.0-SNAPSHOT.jar"
          output-file-url: 'true'
      - name: Print JAR file location on S3
        run: |
            echo "JAR location on S3: ${{ steps.upload_file_to_s3.outputs.file-url }}"
   ```
   
1. When creating a new Databricks cluster then install JAR file from S3:

   ```bash
          libraries-json: >
            [
              { "jar": "s3://${{ vars.AWS_BUCKET_FOR_JARS }}/${{ vars.AWS_BUCKET_ROOT_FOLDER_FOR_JARS }}/jars/pr-${{ github.event.number }}/etl_jobs-assembly-0.1.0-SNAPSHOT.jar" }
            ]
   ```

1. Upload a file to Databricks DBFS e.g. upload Scala JAR file:
   ```bash
      - name: Upload JAR file to DBFS
        uses: databricks/upload-dbfs-temp@v0
        with:
          local-path: ${{ env.LOCAL_NOTEBOOK_PATH }}/scala_etl_jobs/target/scala-2.12/etl_jobs-assembly-0.1.0-SNAPSHOT.jar
        id: upload_file_to_dbfs
      - name: Print JAR file location on DBFS
        run: |
            echo "JAR location on DBFS: ${{ steps.upload_file_to_dbfs.outputs.dbfs-file-path }}"
   ```

1. When creating a new Databricks cluster then install JAR file from Databricks DBFS:

   ```bash
          libraries-json: >
            [
              { "jar": "${{ steps.upload_file_to_dbfs.outputs.dbfs-file-path }}" }
            ]
   ```

1. Code to create a new Databricks cluster while triggering a Notebook and to install the libraries to the new cluster:

   ```bash
      - name: Trigger Databricks Scala ETL Job
        uses: databricks/run-notebook@v0.0.3
        id: trigger_databricks_notebook_scala_etl_job
        with:
          run-name: "GitHub Action - PR ${{ github.event.number }} - Scala ETL Job"
          local-notebook-path: "./scala_etl_jobs/Run Scala ETL Job.py"
          notebook-params-json:  >
            {
              "environment": "dev",
              "data_source_storage_namespace": "${{ vars.DATA_SOURCE_STORAGE_NAMESPACE }}",
              "lakefs_end_point": "${{ vars.LAKEFS_END_POINT }}",
              "lakefs_repo": "${{ vars.LAKFES_REPO_NAME }}",
              "lakefs_branch": "${{ env.LAKFES_BRANCH_NAME }}"
            }
          new-cluster-json: >
            {
              "num_workers": 1,
              "spark_version": "14.3.x-scala2.12",
              "node_type_id": "m5d.large",
              "spark_conf": {
                "spark.hadoop.fs.lakefs.access.mode": "presigned",
                "spark.hadoop.fs.lakefs.impl": "io.lakefs.LakeFSFileSystem",
                "spark.hadoop.fs.lakefs.endpoint": "${{ vars.LAKEFS_END_POINT }}/api/v1",
                "spark.hadoop.fs.lakefs.access.key": "${{secrets.LAKEFS_ACCESS_KEY}}",
                "spark.hadoop.fs.lakefs.secret.key": "${{secrets.LAKEFS_SECRET_KEY}}",
                "spark.hadoop.fs.s3a.access.key": "${{secrets.AWS_ACCESS_KEY}}",
                "spark.hadoop.fs.s3a.secret.key": "${{secrets.AWS_SECRET_KEY}}"
              }
            }
          libraries-json: >
            [
              { "jar": "s3://${{ vars.AWS_BUCKET_FOR_JARS }}/${{ vars.AWS_BUCKET_ROOT_FOLDER_FOR_JARS }}/jars/pr-${{ github.event.number }}/etl_jobs-assembly-0.1.0-SNAPSHOT.jar" },
              { "maven": {"coordinates": "io.lakefs:hadoop-lakefs-assembly:0.2.4"} },
              { "pypi": {"package": "lakefs==0.6.0"} }
            ]
          outputs: >
            run-url >> "$GITHUB_OUTPUT"
   ```

1. Code to checkout a folder from the repo instead of full repo:

   ```bash
      # Checkout project code
      # Use sparse checkout to only select files in a directory
      # Turning off cone mode ensures that files in the project root are not included during checkout
      - name: Checks out the repo
        uses: actions/checkout@v4
        with:
          sparse-checkout: 'scala_etl_jobs/src'
          sparse-checkout-cone-mode: false
   ```

1. Get list of branches in Git repo and store it in a GitHub multi-line environment variable:

   ```bash
      - name: Get branch list
        run: |
          {
           echo 'PR_BRANCHES<<EOF'
           git log -${{ env.PR_FETCH_DEPTH }} --pretty=format:'%H'
           echo ''
           echo 'EOF'
          } >> $GITHUB_ENV
   ```

1. Get Git branch name:

   ```bash
      - name: Extract branch name
        shell: bash
        run: echo "branch=${GITHUB_HEAD_REF:-${GITHUB_REF#refs/heads/}}" >> $GITHUB_OUTPUT
        id: extract_branch
   ```

1. Get date & timestamp:

   ```bash
      - name: Get current date
        id: date
        run: echo "::set-output name=date::$(date +'%Y-%m-%d-%H-%M-%S')"
   ```

> Source: `docs/data_engineering/lakefs/lakeFS-samples/01_standalone_examples/red-hat-openshift-ai/README.md`

# Overview

[lakeFS](https://lakefs.io/) is a data versioning application that brings git-like versioning to object storage. It can interface with many object storage applications on the backend, and provide a S3 API gateway for object storage clients to connect to. In this demo, we'll configure OpenShift AI to connect over S3 interace to lakeFS, which will version the data in a backend [MinIO](https://min.io/docs/minio/kubernetes/openshift/index.html) instance.

![lakefs](img/lakefsv3.png)

# lakeFS with OpenShift AI Demo

The following steps should be followed to perform the [Fraud Detection demo](https://docs.redhat.com/en/documentation/red_hat_openshift_ai_self-managed/2-latest/html/openshift_ai_tutorial_-_fraud_detection_example/index) on OpenShift AI, with lakeFS used for object storage management.

## Prerequisites

1. Bring up [OpenShift cluster](https://docs.redhat.com/en/documentation/openshift_container_platform/4.17#Install)
2. Install [OpenShift Service Mesh](https://docs.openshift.com/container-platform/4.16/service_mesh/v2x/installing-ossm.html#ossm-install-ossm-operator_installing-ossm), [OpenShift Serverless](https://docs.openshift.com/serverless/1.34/install/install-serverless-operator.html) and [OpenShift Pipelines](https://docs.openshift.com/pipelines/1.16/install_config/installing-pipelines.html) on the OpenShift cluster
3. Install [OpenShift AI](https://docs.redhat.com/en/documentation/red_hat_openshift_ai_self-managed/2.13/html/installing_and_uninstalling_openshift_ai_self-managed/index) on the OpenShift cluster
4. Install the `oc` OpenShift [CLI client](https://docs.openshift.com/container-platform/4.16/cli_reference/openshift_cli/getting-started-cli.html) on a machine thas access to the cluster

## Deploy and Configure the Environment
From the client machine, authenticate the `oc` client.

```
oc login <cluster_api_url> -u kubeadmin -p <admin_pw>
```

### Create a `lakefs` project in OpenShift.

```
oc new-project lakefs
```

### Clone the lakeFS samples repo
Clone the [lakeFS-samples.git](https://github.com/treeverse/lakeFS-samples.git) repository and change into the newly created directory.

```
git clone https://github.com/treeverse/lakeFS-samples.git

cd lakeFS-samples/01_standalone_examples/red-hat-openshift-ai/cluster-configuration
```

### Deploy MinIO
Deploy MinIO in the `lakefs` project using the `minio-via-lakefs.yaml` file.

```
oc apply -f minio-via-lakefs.yaml
```
A random MinIO root user and password will be generated, stored in a `secret`, and used to populate MinIO with three storage buckets:
* **my-storage** 
* **pipeline-artifacts**
* **quickstart**


### Deploy lakeFS
Deploy lakeFS in the **lakefs** project using the `lakefs-minio.yaml` file. This yaml will not only deploy lakefs but also:
* connect it with MinIO buckets created earlier
* create two lakeFS repo:
  * **quickstart:** as a sample data repo
  * **my-storage** which is connected to backend my-storage s3 bucket created earlier



```
oc apply -f lakefs-minio.yaml
```

### Access lakeFS UI
You can now log into the OpenShift cluster's web console as a regular user (ie. developer). Follow the arrows in the screenshot below to find the lakeFS `route`, which provides external access to the lakeFS administrator. Use the lakeFS route to access the lakeFS UI.

For this demo, you will use the following credentials to access the lakeFS UI.

* **Access Key**: something
* **Secret Access Key**: simple

  ![lakefs](img/lakefs-route.png)

NOTES:
- You can also follow above steps, but click on MinIO in the topology, to find the `route` to access MinIO's console or S3 interface. MinIO access credentials can be found in the `minio-root-user` secret within the OpenShift web console when logged in as an admin user (ie. kubeadmin).

  - Switch to the **Administrator** persona using the drop-down at the top left
  - Expand the **Workloads** navigation
  - Click on **Secrets**
  - Filter for 'minio' name
  - Click on the **minio-root-user** secret
  - Scroll down and click on **Reveal values** to see the MinIO root user and password

- If you don't see the visual layout as shown in the screenshot, then click on the icon highlighted below to change the view.

  ![lakefs](img/topology.png)

### Access OpenShift AI Console
From the OpenShift web console, you can now open the OpenShift AI web console as shown below.

![lakefs](img/oai-console.png)

## Fraud Detection Demo

You may now run through the [Fraud Detection demo](https://docs.redhat.com/en/documentation/red_hat_openshift_ai_self-managed/2-latest/html/openshift_ai_tutorial_-_fraud_detection_example/index) in the new **lakefs** data science project. Refer to following notes for the different sections of this demo:

2.2. Setting up your data science project:
* Use the `lakefs` data science project for the demo. You do not need to create a new project.

2.3. Storing data with data connections:
* When going through the demo, follow the steps to manually configure the storage data connections. **Do not** follow steps that use a script to automate the MinIO storage deployment, configuration and data connections. 

2.3.1. Creating data connections to your own S3-compatible object storage:
* When creating "My Storage" data connection, use lakeFS access key ("something"), secret key ("simple"), endpoint ("http://my-lakefs"), region ("us-east-1") and bucket ("my-storage") instead of MinIO access key and endpoint:

  ![My Storage data connection](img/data-connection-my-storage.png)

* When creating "Pipeline Artifacts" data connection, use MinIO access key, secret key, endpoint (the route to access MinIO's S3 interface), region ("us-east-1") and bucket ("pipeline-artifacts"):

  ![Pipeline Artifacts data connection](img/data-connection-pipeline-artifacts.png)

3.1. Creating a workbench and selecting a notebook image:
* While creating Workbench add environment variables to access lakeFS: 
  * LAKECTL_SERVER_ENDPOINT_URL = http://my-lakefs
  * LAKEFS_REPO_NAME = my-storage
  * LAKEFS_DEFAULT_REGION =us-east-1 
  * LAKECTL_CREDENTIALS_ACCESS_KEY_ID = something
  * LAKECTL_CREDENTIALS_SECRET_ACCESS_KEY = simple

  ![Workbench lakeFS Environment Variables](img/workbench-lakefs-env-variables.png)

3.2. Importing the tutorial files into the Jupyter environment:
* After cloning and selecting latest branch for the Fraud Detection tutorial repository (https://github.com/rh-aiservices-bu/fraud-detection.git), double-click the newly-created `fraud-detection` folder in the file browser and click on "Upload Files" icon:

  ![Fraud Detection Tutorial fraud-detection folder](img/fraud-detection-tutorial-image1.png)

* Select and upload tutorial notebooks changed for the lakeFS tutorial (ending with lakeFS) which are saved in `lakeFS-samples/red-hat-openshift-ai/fraud-detection` folder of `lakeFS-samples` repo (https://github.com/treeverse/lakeFS-samples.git):

  ![Fraud Detection Tutorial upload lakeFS Notebooks](img/fraud-detection-tutorial-image2.png)

* Double-click the `ray-scripts` subfolder inside `fraud-detection` folder in the file browser and click on "Upload Files" icon:

  ![Fraud Detection Tutorial ray-scripts subfolder](img/fraud-detection-tutorial-image3.png)

* Select and upload `train_tf_cpu_lakefs.py` changed for the lakeFS tutorial which is saved in `lakeFS-samples/red-hat-openshift-ai/fraud-detection/ray-scripts` folder of `lakeFS-samples` repo:

  ![Fraud Detection Tutorial upload ray script](img/fraud-detection-tutorial-image4.png)

* After uploading `train_tf_cpu_lakefs.py` file, file browser will show two Python programs:

  ![Fraud Detection Tutorial ray-scripts subfolder after uploading script](img/fraud-detection-tutorial-image5.png)

* Double-click the `pipeline` subfolder inside `fraud-detection` folder in the file browser and click on "Upload Files" icon:

  ![Fraud Detection Tutorial pipeline subfolder](img/fraud-detection-tutorial-image11.png)

* Select and upload `7_get_data_train_upload_lakefs.py` and `build_lakefs.sh` changed for the lakeFS tutorial which is saved in `lakeFS-samples/red-hat-openshift-ai/fraud-detection/pipeline` folder of `lakeFS-samples` repo:

  ![Fraud Detection Tutorial upload pipeline](img/fraud-detection-tutorial-image12.png)

3.4. Training a model:
* In your notebook environment, open the `1_experiment_train_lakefs.ipynb` file instead of `1_experiment_train.ipynb` and follow the instructions directly in the notebook. The instructions guide you through some simple data exploration, experimentation, and model training tasks.

4.1. Preparing a model for deployment:
* In your notebook environment, open the `2_save_model_lakefs.ipynb` file instead of `2_save_model.ipynb` and follow the instructions directly in the notebook.

4.2. Deploying a model:
* Use the lakeFS branch name in the path that leads to the version folder that contains your model file: `train01/models/fraud`:

  ![Fraud Detection Tutorial Deploy Model](img/fraud-detection-tutorial-image6.png)

4.3. Testing the model API:
* In your notebook environment, open the `3_rest_requests_multi_model_lakefs.ipynb` file instead of `3_rest_requests_multi_model.ipynb` and follow the instructions directly in the notebook.
* In your notebook environment, open the `4_grpc_requests_multi_model_lakefs.ipynb` file instead of `4_grpc_requests_multi_model.ipynb` and follow the instructions directly in the notebook.
* In your notebook environment, open the `5_rest_requests_single_model_lakefs.ipynb` file instead of `5_rest_requests_single_model.ipynb` and follow the instructions directly in the notebook.

5.1. Automating workflows with data science pipelines:
* Instead of creating Red Hat OpenShift AI pipeline from stratch, you can run already created pipeline called `6 Train Save lakefs.pipeline`. In your notebook environment, open `6 Train Save lakefs.pipeline` and click the play button in the toolbar of the pipeline editor to run the pipeline. If you want to create the pipeline from stratch then follow the tutorial instructions but make following changes in section 5.1.5:

5.1.5. Configure the data connection to the S3 storage bucket:
* Under Kubernetes Secrets, use the secret name for  `pipeline-artifacts` data connection for the following environment variables in **both nodes** of the pipeline:
  * AWS_ACCESS_KEY_ID
  * AWS_SECRET_ACCESS_KEY
  * AWS_S3_ENDPOINT
  * AWS_DEFAULT_REGION
  * AWS_S3_BUCKET

  ![Fraud Detection Tutorial Pipeline Kubernetes Secrets 1](img/fraud-detection-tutorial-image7.png)

  ![Fraud Detection Tutorial Pipeline Kubernetes Secrets 1](img/fraud-detection-tutorial-image8.png)

* Under Kubernetes Secrets, use the secret name for `my-storage` data connection when adding following lakeFS environment variables in **both nodes** of the pipeline: 
  * LAKECTL_SERVER_ENDPOINT_URL = AWS_S3_ENDPOINT
  * LAKECTL_CREDENTIALS_ACCESS_KEY_ID = AWS_ACCESS_KEY_ID
  * LAKECTL_CREDENTIALS_SECRET_ACCESS_KEY = AWS_SECRET_ACCESS_KEY
  * LAKEFS_REPO_NAME = AWS_S3_BUCKET
  * LAKEFS_DEFAULT_REGION =AWS_DEFAULT_REGION

  ![Fraud Detection Tutorial Pipeline Kubernetes Secrets 1](img/fraud-detection-tutorial-image9.png)

  ![Fraud Detection Tutorial Pipeline Kubernetes Secrets 1](img/fraud-detection-tutorial-image10.png)

5.2. Running a data science pipeline generated from Python code:
* Use `7_get_data_train_upload_lakefs.yaml` instead of `7_get_data_train_upload.yaml` when importing pipeline in OpenShift AI.

6.1. Distributing training jobs with Ray:
* In your notebook environment, open the `8_distributed_training_lakefs.ipynb` file instead of `8_distributed_training.ipynb`. Change MinIO Access and Secret keys in the 2nd code cell of the notebook and run the notebook.

  Optionally, if you want to view the Python code for this section, you can find it in the ray-scripts/train_tf_cpu_lakefs.py file.

See [lakeFS documentation](https://docs.lakefs.io/) and [MinIO documentation for OpenShift](https://min.io/docs/minio/kubernetes/openshift/index.html) for details.

# File Descriptions

- [lakefs-local.yaml](./cluster-configuration/lakefs-local.yaml): Bring up lakeFS using local object storage. This would be useful for a quick demo where MinIO is not included.
- [lakefs-minio.yaml](./cluster-configuration/lakefs-minio.yaml): Bring up lakeFS configured to use MinIO as backend object storage. This will be used in the lakeFS demo.
- [minio-direct.yaml](./cluster-configuration/minio-direct.yaml): This file would only be used if lakeFS is not in the picture and OpenShift AI will communicate directly with MinIO. It will bring up MinIO as it is in the default Fraud Detection demo, complete with configuring MinIO storage buckets and the OpenShift AI data connections. It may serve useful in debugging an issue.
- [minio-via-lakefs.yaml](./cluster-configuration/minio-via-lakefs.yaml): Bring up MinIO for the modified Fraud Detection demo that includes lakeFS, complete with configuring MinIO storage buckets, but do NOT configure the OpenShift AI data connections. This will be used in the lakeFS demo.


> Source: `docs/data_engineering/lakefs/lakeFS-samples/01_standalone_examples/parade-db-integration/README.md`

# Integration of lakeFS with ParadeDB

Start by ⭐️ starring [lakeFS open source](https://go.lakefs.io/oreilly-course) project.

This repository includes a Jupyter Notebook and ParadeDB which you can run on your local machine.

## Let's Get Started 👩🏻‍💻

Clone this repository

   ```bash
   git clone https://github.com/treeverse/lakeFS-samples && cd lakeFS-samples/01_standalone_examples/parade-db-integration
   ```

You now have two options: 

### **Run a Notebook server with your existing lakeFS Server**

If you have already [installed lakeFS](https://docs.lakefs.io/deploy/) or are utilizing [lakeFS cloud](https://lakefs.cloud/), all you need to run is the Jupyter notebook and ParadeDB:


   ```bash
   docker compose up 
   ```

### **Don't have a lakeFS Server or Object Store?**

If you want to provision a lakeFS server as well as MinIO for your object store, plus Jupyter and ParadeDB then bring up the full stack:

   ```bash
   docker compose --profile local-lakefs up
   ```

### URLs and login details

* Jupyter http://localhost:8895/

If you've brought up the full stack you'll also have: 

* LakeFS http://localhost:8007/ (`AKIAIOSFOLKFSSAMPLES` / `wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY`)
* MinIO http://localhost:9007/ (`minioadmin`/`minioadmin`)


## Demo Instructions

Open Jupyter UI [http://localhost:8895](http://localhost:8895) in your web browser. Open "ParadeDB Demo" notebook from Jupyter UI and follow the instructions.

## Original Sources

### ducklake/
- `docs/data_engineering/ducklake/DuckLake + SQLMesh Tutorial_ Build a Modern Data Lakehouse On Your Laptop.md`
- `docs/data_engineering/ducklake/DuckLake to MotherDuck_ Validate locally, deploy to cloud in minutes.md`
- `docs/data_engineering/ducklake/ducklake.md`
- `docs/data_engineering/ducklake/KCG_SUMMARY.md`
- `docs/data_engineering/ducklake/mlflow_kafka_ducklake/CHANGELOG.md`
- `docs/data_engineering/ducklake/mlflow_kafka_ducklake/README.md`
- `docs/data_engineering/ducklake/README.md`

### lakefs/
- `docs/data_engineering/lakefs/dagster-integration/README.md`
- `docs/data_engineering/lakefs/delta-lake/README.md`
- `docs/data_engineering/lakefs/iceberg/README.md`
- `docs/data_engineering/lakefs/iceberg/spark-basic/README.md`
- `docs/data_engineering/lakefs/iceberg/spark-medallion/README.md`
- `docs/data_engineering/lakefs/iceberg/trino/README.md`
- `docs/data_engineering/lakefs/iceberg/write-audit-publish/README.md`
- `docs/data_engineering/lakefs/KCG_SUMMARY.md`
- `docs/data_engineering/lakefs/lakefs-mount-demo/README.md`
- `docs/data_engineering/lakefs/lakeFS-samples/00_notebooks/write-audit-publish/README.md`
- `docs/data_engineering/lakefs/lakeFS-samples/01_standalone_examples/airflow-01/README.md`
- `docs/data_engineering/lakefs/lakeFS-samples/01_standalone_examples/airflow-02/README.md`
- `docs/data_engineering/lakefs/lakeFS-samples/01_standalone_examples/aws-databricks/README.md`
- `docs/data_engineering/lakefs/lakeFS-samples/01_standalone_examples/aws-glue-athena/README.md`
- `docs/data_engineering/lakefs/lakeFS-samples/01_standalone_examples/aws-glue-trino/README.md`
- `docs/data_engineering/lakefs/lakeFS-samples/01_standalone_examples/azure-databricks/README.md`
- `docs/data_engineering/lakefs/lakeFS-samples/01_standalone_examples/backup-migrate-or-clone-repo/README.md`
- `docs/data_engineering/lakefs/lakeFS-samples/01_standalone_examples/databricks-ci-cd/README.md`
- `docs/data_engineering/lakefs/lakeFS-samples/01_standalone_examples/databricks-ci-cd/scala-demo.md`
- `docs/data_engineering/lakefs/lakeFS-samples/01_standalone_examples/docker-compose-with-postgres/README.md`
- `docs/data_engineering/lakefs/lakeFS-samples/01_standalone_examples/flink/README.md`
- `docs/data_engineering/lakefs/lakeFS-samples/01_standalone_examples/image-segmentation-local/README.md`
- `docs/data_engineering/lakefs/lakeFS-samples/01_standalone_examples/image-segmentation/README.md`
- `docs/data_engineering/lakefs/lakeFS-samples/01_standalone_examples/kafka/README.md`
- `docs/data_engineering/lakefs/lakeFS-samples/01_standalone_examples/labelbox-integration/README.md`
- `docs/data_engineering/lakefs/lakeFS-samples/01_standalone_examples/llm-openai-langchain-integration/README.md`
- `docs/data_engineering/lakefs/lakeFS-samples/01_standalone_examples/multimodal-data-demo-local/README.md`
- `docs/data_engineering/lakefs/lakeFS-samples/01_standalone_examples/parade-db-integration/README.md`
- `docs/data_engineering/lakefs/lakeFS-samples/01_standalone_examples/prefect-integration/README.md`
- `docs/data_engineering/lakefs/lakeFS-samples/01_standalone_examples/red-hat-openshift-ai/README.md`
- `docs/data_engineering/lakefs/lakeFS-samples/01_standalone_examples/spark/README.md`
- `docs/data_engineering/lakefs/lakeFS-samples/01_standalone_examples/trino/README.md`
- `docs/data_engineering/lakefs/lakeFS-samples/02_lakefs_enterprise/README.md`
- `docs/data_engineering/lakefs/lakeFS-samples/README.md`
- `docs/data_engineering/lakefs/ml/image-segmentation/README.md`
- `docs/data_engineering/lakefs/ml/llm-langchain/README.md`
- `docs/data_engineering/lakefs/ml/README.md`
- `docs/data_engineering/lakefs/README.md`

---
*Generated by MERGE_PLAN.md Phase 1 — 2026-06-06*
