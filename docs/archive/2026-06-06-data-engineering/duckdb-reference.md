# DuckDB Reference

> Merged from 9 source files in `duckdb/` — comprehensive DuckDB reference covering core concepts, SQL dialect, extensions, spatial/geospatial, SQLMesh, MotherDuck, and PlanetScale integration.

---

## Table of Contents

1. [Core Skill & API Reference](#core-skill--api-reference)
2. [Comprehensive Research](#comprehensive-research)
3. [SQLMesh Integration](#duckdb--sqlmesh)
4. [Spatial & Geospatial](#spatial--geospatial)
5. [Extensions: pg_duckdb](#extensions-pg_duckdb)
6. [Cloud: MotherDuck](#cloud-motherduck)
7. [Git-Inspired Data Workflow](#git-inspired-data-workflow)
8. [Original Sources](#original-sources)

---

## Core Skill & API Reference

> Source: `docs/data_engineering/duckdb/duckdb.md`

# DuckDB Expert Assistant

You are a DuckDB expert assistant. When this skill is invoked, help users with DuckDB-related tasks including query optimization, schema design, data loading, and best practices.

## Your Expertise

You have deep knowledge of:
- DuckDB architecture (columnar storage, vectorized execution, MVCC)
- SQL query optimization for analytical workloads
- File format selection (Parquet, CSV, JSON)
- Data loading patterns and ETL pipelines
- Integration with Python, Node.js, R, and other languages
- Extension system (spatial, delta, iceberg, etc.)
- Performance tuning and memory management
- Migration from other databases (SQLite, PostgreSQL)

## Key Reference Materials

You have access to comprehensive DuckDB documentation in:
- `/home/user/hackathon/DUCKDB_COMPREHENSIVE_RESEARCH.md` - Detailed research on all aspects
- `/home/user/hackathon/llms.txt` - Quick reference and best practices

## When Helping Users

### 1. Query Optimization
When users show you queries or ask for optimization help:
- Analyze their query structure
- Suggest using EXPLAIN ANALYZE to profile
- Recommend columnar-friendly patterns (avoid SELECT *)
- Ensure they're using Parquet for best performance
- Check if they're leveraging partition pruning
- Verify appropriate data types are being used

Example response pattern:
```
Let me analyze this query for optimization opportunities:

1. **File Format**: I notice you're using CSV. Converting to Parquet could give you up to 600x better performance.
2. **Column Selection**: You're selecting all columns. Try selecting only what you need.
3. **Filter Pushdown**: Your WHERE clause can benefit from early filtering.

Here's an optimized version:
[provide optimized query]
```

### 2. Schema Design
When helping with schema design:
- Recommend appropriate data types (use smallest that fits)
- Suggest columnar-friendly structures
- Consider partitioning strategies for large datasets
- Recommend complex types (ARRAY, STRUCT, MAP) when appropriate
- Explain when to use views vs materialized data

### 3. Data Loading
When helping with data loading:
- **Always recommend Parquet** for analytical workloads
- Show the pattern: CSV → Parquet conversion for repeated querying
- Demonstrate direct file querying (no need to load first)
- Explain bulk loading vs incremental patterns
- Show how to handle multiple files with glob patterns

Example code:
```sql
-- Convert CSV to Parquet (do this once)
COPY (SELECT * FROM 'data.csv') TO 'data.parquet' (FORMAT parquet);

-- Then query Parquet repeatedly
SELECT * FROM 'data.parquet' WHERE ...;
```

### 4. Performance Issues
When users report performance problems:
- Ask them to run EXPLAIN ANALYZE
- Check if they're reusing connections
- Verify memory_limit setting (default 80% RAM)
- Ensure they're using Parquet not CSV
- Look for missing filters or inappropriate joins
- Check if they need out-of-core processing

Diagnostic questions to ask:
- What file format are you using?
- Are you reusing the database connection?
- Have you tried EXPLAIN ANALYZE?
- How large is your dataset?
- What does your query pattern look like?

### 5. Integration Help
For different languages, provide idiomatic examples:

**Python:**
```python
import duckdb

# Best practice: reuse connection
con = duckdb.connect('database.db')

# Query to Pandas DataFrame
df = con.query("SELECT * FROM 'data.parquet'").to_df()

# Direct file querying
result = con.execute("SELECT * FROM 'data.parquet' WHERE value > 100").fetchall()

con.close()
```

**Node.js:**
```javascript
const duckdb = require('@duckdb/node-api');

const db = new duckdb.Database('database.db');
const conn = db.connect();

const result = await conn.run('SELECT * FROM read_parquet("data.parquet")');
```

**R:**
```r
library(duckplyr)  # Drop-in dplyr replacement, 20x faster

# Your existing dplyr code works automatically
df %>%
  filter(value > 100) %>%
  summarise(total = sum(amount))
```

### 6. Extension Recommendations
Know when to suggest extensions:

- **Spatial data?** → `INSTALL spatial; LOAD spatial;`
- **S3/Cloud storage?** → `INSTALL httpfs; LOAD httpfs;`
- **Delta Lake?** → `INSTALL delta; LOAD delta;`
- **Apache Iceberg?** → `INSTALL iceberg; LOAD iceberg;`
- **Full-text search?** → `INSTALL fts; LOAD fts;`
- **Excel files?** → `INSTALL excel; LOAD excel;`
- **Reading from PostgreSQL?** → `INSTALL postgres_scanner; LOAD postgres_scanner;`

### 7. Common Patterns to Share

**ETL Pipeline:**
```sql
COPY (
    SELECT
        user_id,
        DATE_TRUNC('day', timestamp) as date,
        COUNT(*) as events
    FROM read_json('logs/*.json', format='newline_delimited')
    WHERE timestamp >= CURRENT_DATE - INTERVAL 7 DAYS
    GROUP BY user_id, date
) TO 'processed/daily_summary.parquet' (FORMAT parquet);
```

**Multi-file Join:**
```sql
SELECT
    orders.order_id,
    customers.name,
    products.price
FROM 'orders/*.parquet' orders
JOIN 'customers.parquet' customers ON orders.customer_id = customers.id
JOIN 'products.parquet' products ON orders.product_id = products.id;
```

**Cloud Data:**
```sql
INSTALL httpfs; LOAD httpfs;

SET s3_region='us-east-1';
SET s3_access_key_id='...';
SET s3_secret_access_key='...';

SELECT * FROM 's3://bucket/data/*.parquet';
```

## Decision Frameworks to Use

### DuckDB vs Other Databases

**Use DuckDB when:**
- Single-machine analytics
- Local-first workflows
- Processing files (Parquet, CSV, JSON)
- Embedded analytics in applications
- Data science/ML pipelines
- ETL transformations
- Cost-sensitive workloads

**Don't use DuckDB when:**
- Multi-user concurrent writes needed
- Distributed architecture required
- High-frequency transactions (OLTP)
- Network database server needed

**DuckDB vs SQLite:**
- SQLite: transactional workloads, mobile apps, point queries
- DuckDB: analytical workloads, aggregations, data analysis
- Can use both together (SQLite for transactions, DuckDB for analytics)

**DuckDB vs PostgreSQL:**
- PostgreSQL: multi-user applications, network access, B2B SaaS
- DuckDB: local analytics, data exploration, single-user
- DuckDB uses PostgreSQL SQL dialect (familiar syntax)

### File Format Selection

**Always recommend in this order:**
1. **Parquet** (best performance, up to 600x faster than CSV)
2. **Arrow** (zero-copy integration)
3. **JSON** (semi-structured data)
4. **CSV** (only for initial ingestion, convert to Parquet)

## Code Generation Guidelines

When generating code:

1. **Use explicit file paths** in examples
2. **Show the full pattern** (not just fragments)
3. **Include error handling** where appropriate
4. **Demonstrate connection reuse**
5. **Use parameterized queries** to prevent SQL injection
6. **Show EXPLAIN ANALYZE** for performance checking
7. **Include comments** explaining key decisions

Example:
```python
import duckdb

def analyze_sales_data(data_path: str, start_date: str) -> pd.DataFrame:
    """
    Analyze sales data from Parquet files.

    Args:
        data_path: Path to Parquet files (supports glob patterns)
        start_date: ISO format date string (YYYY-MM-DD)

    Returns:
        DataFrame with daily sales summary
    """
    # Reuse connection for better performance
    con = duckdb.connect()

    # Use parameterized query to prevent SQL injection
    result = con.execute("""
        SELECT
            DATE_TRUNC('day', order_date) as date,
            SUM(amount) as total_sales,
            COUNT(*) as order_count,
            COUNT(DISTINCT customer_id) as unique_customers
        FROM read_parquet(?)
        WHERE order_date >= ?
        GROUP BY date
        ORDER BY date
    """, [data_path, start_date]).df()

    con.close()
    return result

# Usage
summary = analyze_sales_data('sales/*.parquet', '2024-01-01')
```

## Best Practices to Emphasize

1. **Parquet First**: Always convert CSV to Parquet for repeated queries
2. **Reuse Connections**: Don't create new connection for each query
3. **Select Specific Columns**: Avoid SELECT * in production code
4. **Use EXPLAIN ANALYZE**: Profile queries to find bottlenecks
5. **Leverage Partitioning**: Use partitioned Parquet for large datasets
6. **Configure Memory**: Adjust memory_limit based on workload
7. **Handle Errors**: Use TRY expressions for robust code
8. **Direct File Querying**: No need to load data first, query files directly

## Troubleshooting Guide

### Memory Issues
```sql
-- Check current memory limit
SELECT * FROM duckdb_settings() WHERE name = 'memory_limit';

-- Reduce if needed
SET memory_limit = '2GB';
```

### Performance Issues
```sql
-- Profile the query
EXPLAIN ANALYZE SELECT ...;

-- Check if using Parquet
-- Convert CSV to Parquet if not
COPY (SELECT * FROM 'data.csv') TO 'data.parquet' (FORMAT parquet);
```

### Connection Issues
```python
# Bad: Creating connection repeatedly
for file in files:
    con = duckdb.connect('db.db')
    con.execute(f"SELECT * FROM '{file}'")
    con.close()

# Good: Reuse connection
con = duckdb.connect('db.db')
for file in files:
    con.execute(f"SELECT * FROM '{file}'")
con.close()
```

## Example Interactions

### User asks: "How do I load a large CSV file into DuckDB?"

Your response:
```
You have several options for loading CSV files into DuckDB:

1. **Direct Querying** (recommended for one-time analysis):
```sql
SELECT * FROM read_csv('large_file.csv', AUTO_DETECT=TRUE)
WHERE ...;
```

2. **Convert to Parquet** (recommended for repeated querying):
```sql
-- Convert once
COPY (SELECT * FROM 'large_file.csv')
TO 'large_file.parquet' (FORMAT parquet);

-- Query many times (up to 600x faster)
SELECT * FROM 'large_file.parquet' WHERE ...;
```

3. **Create Table** (if you need persistence):
```sql
CREATE TABLE my_table AS
SELECT * FROM read_csv('large_file.csv', AUTO_DETECT=TRUE);
```

**Recommendation**: Use option 2 (convert to Parquet). The one-time conversion cost pays off immediately on the second query.

For very large files that don't fit in memory, DuckDB handles this automatically with out-of-core processing. You might want to set a memory limit:
```sql
SET memory_limit = '4GB';
```
```

### User asks: "My query is slow, what should I do?"

Your response:
```
Let's diagnose the performance issue:

1. **First, profile your query:**
```sql
EXPLAIN ANALYZE SELECT ...;
```

2. **Check these common issues:**

**File format**: Are you using CSV? Convert to Parquet:
```sql
COPY (SELECT * FROM 'data.csv') TO 'data.parquet' (FORMAT parquet);
```

**Column selection**: Avoid SELECT *:
```sql
-- Instead of: SELECT * FROM table
-- Use: SELECT col1, col2, col3 FROM table
```

**Connection reuse**: Are you creating a new connection for each query?
```python
# Reuse connection
con = duckdb.connect('db.db')
for query in queries:
    con.execute(query)
con.close()
```

**Memory limit**: Check if you need more memory:
```sql
SET memory_limit = '8GB';  -- Or '80%' for 80% of RAM
```

3. **Share the EXPLAIN ANALYZE output** and I can help optimize further.
```

## Advanced Topics

### Window Functions
```sql
SELECT
    user_id,
    order_date,
    amount,
    SUM(amount) OVER (PARTITION BY user_id ORDER BY order_date) as running_total,
    AVG(amount) OVER (PARTITION BY user_id) as user_avg,
    RANK() OVER (PARTITION BY DATE_TRUNC('month', order_date) ORDER BY amount DESC) as monthly_rank
FROM orders;
```

### Recursive CTEs
```sql
WITH RECURSIVE hierarchy AS (
    SELECT id, parent_id, name, 1 as level
    FROM categories
    WHERE parent_id IS NULL
    UNION ALL
    SELECT c.id, c.parent_id, c.name, h.level + 1
    FROM categories c
    JOIN hierarchy h ON c.parent_id = h.id
)
SELECT * FROM hierarchy ORDER BY level, name;
```

### Complex Types
```sql
-- Arrays
SELECT list_value(1, 2, 3) as numbers;
SELECT unnest([1, 2, 3]) as number;

-- Structs
SELECT {'name': 'John', 'age': 30} as person;
SELECT person.name FROM (SELECT {'name': 'John', 'age': 30} as person);

-- Maps
SELECT map(['a', 'b'], [1, 2]) as my_map;
```

### MERGE Statement (v1.4.0+)
```sql
MERGE INTO target
USING source
ON target.id = source.id
WHEN MATCHED THEN
    UPDATE SET value = source.value, updated_at = CURRENT_TIMESTAMP
WHEN NOT MATCHED THEN
    INSERT (id, value, created_at) VALUES (source.id, source.value, CURRENT_TIMESTAMP);
```

## Quick Reference Commands

```sql
-- System inspection
SHOW TABLES;
DESCRIBE table_name;
SELECT * FROM duckdb_settings();

-- Performance
EXPLAIN SELECT ...;
EXPLAIN ANALYZE SELECT ...;

-- Memory
SET memory_limit = '4GB';
SET threads = 4;

-- Extensions
INSTALL extension_name;
LOAD extension_name;

-- File formats
SELECT * FROM 'file.parquet';
SELECT * FROM read_csv('file.csv', AUTO_DETECT=TRUE);
SELECT * FROM read_json('file.json');

-- Export
COPY (SELECT ...) TO 'output.parquet' (FORMAT parquet);
COPY (SELECT ...) TO 'output.csv' (HEADER, DELIMITER ',');
```

## Your Approach

When users invoke this skill:

1. **Understand the context**: What are they trying to achieve?
2. **Ask clarifying questions** if needed (file format, data size, use case)
3. **Provide complete, runnable examples**
4. **Explain the "why"** behind recommendations
5. **Show performance implications** (e.g., CSV vs Parquet)
6. **Reference best practices** from the research materials
7. **Offer optimization tips** proactively
8. **Consider their tech stack** (Python, Node.js, R, CLI)

Remember: You're not just answering questions, you're teaching best practices and helping users get the most out of DuckDB's analytical capabilities.


## Comprehensive Research

> Source: `docs/data_engineering/duckdb/duckdb-comprehensive-research.md`

# DuckDB Comprehensive Research Report

**Report Generated:** 2025-11-17
**Latest DuckDB Version:** 1.4.2 LTS (Released November 12, 2025)

---

## Table of Contents

1. [Core Features & Capabilities](#1-core-features--capabilities)
2. [Architecture & Patterns](#2-architecture--patterns)
3. [APIs & Integration](#3-apis--integration)
4. [Ontologies & Data Models](#4-ontologies--data-models)
5. [Best Practices & Common Patterns](#5-best-practices--common-patterns)
6. [Real-World Use Cases](#6-real-world-use-cases)
7. [Extensions & Ecosystem](#7-extensions--ecosystem)

---

## 1. Core Features & Capabilities

### What is DuckDB?

**DuckDB** is an in-process SQL OLAP (Online Analytical Processing) database management system. It's often described as "SQLite for Analytics" due to its:
- Embedded, in-process nature (no separate server process)
- PostgreSQL-compatible SQL dialect
- Optimization for analytical workloads rather than transactional ones

### Key Features

#### Columnar Storage
- Stores data by columns rather than by rows
- Far more efficient for analytical queries that scan large portions of datasets
- Only relevant columns are read from disk into memory
- Uses PAX (Partition Attributes Across) columnar storage format
- Enables superior CPU cache utilization and vectorized operations
- Supports efficient compression on a per-column basis

#### Vectorized Query Execution
- Processes large batches of values (vectors) in single operations
- Takes advantage of modern CPU architectures and SIMD (Single Instruction, Multiple Data) instructions
- Greatly reduces overhead compared to row-by-row processing in traditional systems
- Processes data in dense, contiguous blocks for maximum CPU efficiency
- Leads to significantly better performance for OLAP queries

#### ACID Compliance
- Fully supports ACID transactions (Atomicity, Consistency, Isolation, Durability)
- Uses Multi-Version Concurrency Control (MVCC) based on HyPer's serializable variant
- Optimistic concurrency control approach
- Always uses Snapshot Isolation (similar to SERIALIZABLE)
- Transactions don't hold locks - conflicts result in transaction abort and retry
- Lock-free MVCC provides multiple consistent views on the same dataset

#### Performance Characteristics
- Can be 10-50 times faster than SQLite for analytical queries
- Up to 600 times faster when reading Parquet vs CSV files
- Automatic parallelization across all available CPU cores
- Morsel-driven parallelism for NUMA-aware execution
- Zone maps for selective scanning

#### File Format Support
- **Parquet** (highly optimized, recommended format)
- **CSV** (with auto-detection of settings)
- **JSON** (newline-delimited and regular JSON)
- **Apache Arrow** (zero-copy integration)
- **Data Lake Formats:**
  - Apache Iceberg (native support via extension)
  - Delta Lake (native support via delta extension)
  - DuckLake (DuckDB's own lakehouse format, released May 2025)

#### Cloud and Network Storage
- AWS S3
- Azure Blob Storage
- Google Cloud Storage
- HTTP/HTTPS URLs
- Can query remote files directly without downloading

#### SQL Dialect Features
- **PostgreSQL-compatible** SQL dialect with ANSI SQL compliance
- **Window Functions:** 14+ window-specific functions plus all aggregation functions
- **Common Table Expressions (CTEs):** Full support including recursive CTEs
- **Advanced Features:**
  - User-defined aggregates
  - MERGE statement (added in v1.4.0)
  - TRY expression for error handling
  - UUID v7 support
  - Complex subqueries and joins

#### Supported Data Types

**Numeric Types:**
- INTEGER, BIGINT, SMALLINT, TINYINT
- DOUBLE, FLOAT, REAL
- DECIMAL/NUMERIC (arbitrary precision)
- HUGEINT (128-bit integers)

**String Types:**
- VARCHAR, TEXT
- BLOB (binary data)

**Temporal Types:**
- DATE
- TIMESTAMP (with/without timezone)
- TIME
- INTERVAL

**Boolean:**
- BOOLEAN

**Complex Types:**
- ARRAY
- STRUCT
- MAP
- LIST
- JSON

**Geospatial:**
- GEOMETRY (via spatial extension)

#### Database Encryption
- Available starting with v1.4.0
- Industry-standard AES-256 encryption
- GCM mode by default
- Encrypts database files at rest

#### Local UI
- Full-featured local web UI available out-of-the-box (since v1.2.1)
- All queries run locally - data never leaves your computer
- No backend infrastructure required

---

## 2. Architecture & Patterns

### Embedded Architecture

**In-Process Design:**
- DuckDB does not run as a separate process
- Completely embedded within a host process
- No client-server architecture overhead
- No network latency
- Direct memory access to data

**Shared-Everything Architecture:**
- Compute and storage are not separated
- All components share the same memory space
- Optimal for single-machine analytical workloads

### Query Execution Model

#### Push-Based Vectorized Query Processing
- Operators are "parallelism-aware"
- Parallelism is managed dynamically within the query plan
- Not baked into the plan statically

#### Morsel-Driven Parallelism
- Pioneered in academic research
- NUMA-aware execution
- Work is divided into small chunks ("morsels")
- Enables efficient utilization of multiple CPU cores

#### Streaming Execution Engine
- Allows small chunks of data to flow through the system
- Entire datasets don't need to be materialized in memory
- Enables processing of larger-than-memory datasets

### Storage and Indexing Patterns

#### Persistent Storage
- Data stored on fixed-size pages
- Pages managed by buffer manager
- Supports durable persistence to disk
- Can also operate in pure in-memory mode

#### Indexing
- Zone maps for efficient data skipping
- Statistics-based query optimization
- Automatic index selection
- Support for explicit index creation

### Memory Management

#### Non-Traditional Buffer Management
- **Key Innovation:** DuckDB doesn't reserve a fixed portion of memory for a buffer pool
- All available memory can be used flexibly:
  - For persistent data when needed
  - For large hash tables during aggregations
  - For intermediate results

**Default Memory Limit:**
- Uses up to 80% of available system memory by default
- Configurable via pragmas

**Memory Allocation Strategy:**
- Buffer manager handles most data processed
- Some aggregate functions (list, mode, quantile, string_agg, approx functions) use memory outside buffer manager
- Actual memory consumption can exceed specified limit for complex aggregates

**Out-of-Core Processing:**
- Intermediate results can be spilled to disk
- Enables computation of complex queries exceeding available memory
- External aggregation support

#### Statistics Propagation
- Creates new filters by inspecting column statistics
- Enables filter pushdown optimizations
- Reduces unnecessary I/O

### Extension System

**Architecture:**
- Flexible extension mechanism for dynamic loading
- Extensions enhance functionality with:
  - Additional file formats
  - New data types
  - Domain-specific functionality

**Two-Phase Process:**
1. **Installation:** Downloads extension binary and verifies metadata
2. **Loading:** Dynamically loads binary into DuckDB instance

**Extension Types:**
- **Core Extensions:** Built and signed by DuckDB team
- **Community Extensions:** Third-party developed extensions

**Platform Support:**
- macOS, Windows, Linux
- Available across all clients (Python, R, Node.js, etc.)

**Extension Storage:**
- Downloaded to `~/.duckdb` directory
- Binaries matched to OS and processor architecture

---

## 3. APIs & Integration

### Client Libraries Overview

All DuckDB clients:
- Support the same SQL syntax
- Use the same on-disk database format
- Can share databases across different language clients
- Example: Create database in Python, query from Node.js

### Python API

**Installation:**
```bash
pip install duckdb
```

**Requirements:**
- Python 3.9 or newer

**API Styles:**
- **DB API:** Standard Python database interface (PEP 249)
- **Relational API:** DuckDB-specific fluent interface
- **Function API:** Direct function calls

**Example Usage:**
```python
import duckdb

# In-memory database
con = duckdb.connect()

# Persistent database
con = duckdb.connect('my_database.db')

# Query directly
result = con.execute("SELECT * FROM 'data.parquet'").fetchall()

# Relational API
result = con.table('my_table').filter('column > 10').aggregate('count(*)')
```

**Data Ingestion:**
- Direct Pandas DataFrame integration
- Apache Arrow integration (zero-copy)
- Read from Parquet, CSV, JSON files
- Query files directly without loading

### Node.js API

**Two Packages Available:**

1. **@duckdb/node-api (Node Neo - Recommended)**
   - High-level API for applications
   - Native Promise support
   - Lossless support for all DuckDB data types
   - Low-level bindings available as @duckdb/node-bindings

2. **duckdb (Deprecated)**
   - Legacy package
   - Use Node Neo instead

**Installation:**
```bash
npm install @duckdb/node-api
```

**Example Usage:**
```javascript
const duckdb = require('@duckdb/node-api');

const db = new duckdb.Database(':memory:');
const conn = db.connect();

const result = await conn.run('SELECT * FROM read_parquet("data.parquet")');
```

### R Client

**Two Integration Approaches:**

1. **duckplyr Package (Drop-in Replacement)**
   - Translates dplyr API to DuckDB's execution engine
   - Drop-in replacement for dplyr
   - Uses DuckDB's relational API (not SQL interface)
   - Bypasses SQL parser for better performance
   - Can be 20x faster than standard dplyr

   ```r
   install.packages("duckplyr")
   library(duckplyr)

   # Your existing dplyr code runs automatically on DuckDB
   df %>%
     filter(value > 100) %>%
     summarise(total = sum(amount))
   ```

2. **Standard DuckDB Client with dbplyr**
   - SQL backend for dbplyr
   - Programmatic query construction
   - Based on PostgreSQL backend with additional mapped functions

   ```r
   install.packages("duckdb")
   library(duckdb)
   library(dplyr)

   con <- dbConnect(duckdb::duckdb(), "my_database.db")
   ```

### Other Language Clients

- **Java/JDBC:** Full JDBC driver support
- **C/C++:** Native API
- **Go:** Go bindings
- **Rust:** Rust bindings
- **Julia:** Julia package

### WebAssembly (WASM)

**Browser Support:**
- Runs entirely in the browser
- No backend infrastructure needed
- Tested with Chrome, Firefox, Safari, Node.js

**Features:**
- Speaks Arrow fluently
- Reads Parquet, CSV, JSON
- Filesystem APIs or HTTP requests
- Extension support (WebAssembly modules)

**Installation:**
```bash
npm install @duckdb/duckdb-wasm
```

**Current Version:** 1.30.0

**Limitations:**
- Single-threaded by default (multithreading experimental)
- Sandboxed environment
- Limited out-of-core operations

**Use Cases:**
- In-browser analytics
- Client-side data exploration
- Offline-capable applications
- Data visualization tools

### Apache Arrow Integration

**Zero-Copy Integration:**
- Rapid analysis of larger-than-memory datasets
- Works in Python and R
- Supports SQL and relational APIs

**Supported Arrow Objects:**
- Tables
- Datasets
- RecordBatchReaders
- Scanners

**Optimization:**
- Pushdown of filters and projections
- Only relevant columns/partitions read
- Partition elimination in Parquet files
- No data copying between Arrow and DuckDB

---

## 4. Ontologies & Data Models

### Internal Data Modeling

#### Table Storage
- **Columnar Layout:** Data physically stored by column
- **Page-Based:** Fixed-size pages managed by buffer manager
- **Compression:** Per-column compression strategies
- **Statistics:** Maintained at column and segment level

#### Schema Management

**System Catalogs:**
- `information_schema.tables` - All tables and views
- `information_schema.columns` - Column details
- `information_schema.schemata` - Schema information
- `duckdb_tables()` - DuckDB-specific table info
- `duckdb_views()` - View information
- `duckdb_indexes()` - Index information
- `duckdb_schemas()` - Schema details

**Common Commands:**
```sql
-- List tables
SHOW TABLES;
SHOW ALL TABLES;  -- across all schemas

-- Table structure
DESCRIBE table_name;
PRAGMA table_info('table_name');

-- Indexes
SHOW INDEXES;
```

#### Views and Materialization
- Standard SQL views (virtual)
- Materialized views support
- CTEs for query-scoped temporary results
- Recursive CTEs for hierarchical data

### Relationship to Other Databases

#### vs SQLite

**Similarities:**
- Embedded, in-process architecture
- No separate server process
- Zero configuration
- Single-file database (optional)
- Cross-platform compatibility

**Differences:**

| Feature | DuckDB | SQLite |
|---------|--------|--------|
| **Storage Model** | Columnar | Row-based |
| **Workload Optimization** | OLAP (Analytics) | OLTP (Transactions) |
| **Best For** | Aggregations, scans, analytics | Point queries, transactional writes |
| **Performance** | 10-50x faster for analytics | Better for single-row operations |
| **Memory Usage** | Higher for better performance | Extremely lightweight |

**When to Use Each:**
- **SQLite:** Mobile apps, IoT devices, browser caching, transactional workloads
- **DuckDB:** Data analysis, aggregations, reporting, data science workflows

**Complementary Use:**
- Can use both in the same application
- SQLite for transactional data, DuckDB for analytics

#### vs PostgreSQL

**Similarities:**
- SQL dialect (DuckDB is PostgreSQL-compatible)
- ACID compliance
- Rich feature set
- Window functions, CTEs, advanced SQL

**Differences:**

| Feature | DuckDB | PostgreSQL |
|---------|--------|-----------|
| **Architecture** | Embedded, in-process | Client-server |
| **Deployment** | No installation needed | Server installation required |
| **Concurrency** | Single-writer, optimistic | Multi-user, pessimistic locking |
| **Network** | None | Network overhead present |
| **Analytics** | Optimized (columnar) | Good but row-based |

**Performance:**
- DuckDB outperforms PostgreSQL on analytical benchmarks
- Particularly with large, wide datasets
- Columnar storage allows skipping irrelevant data
- Faster for aggregation-heavy queries

**When to Use Each:**
- **PostgreSQL:** Multi-user applications, B2B SaaS, distributed systems
- **DuckDB:** Local-first workflows, data exploration, single-user analytics

#### DuckDB as "PostgreSQL Dialect + Columnar"
- Familiar PostgreSQL syntax
- Analytical performance of columnar storage
- Best of both worlds for single-machine analytics

---

## 5. Best Practices & Common Patterns

### File Format Selection

**Parquet (Strongly Recommended):**
- Up to 600x faster than CSV
- Smaller disk footprint
- Built-in compression
- Columnar format matches DuckDB's architecture
- Preserves data types and schema

**CSV:**
- Use only for initial data ingestion
- Auto-detection available but slower
- Convert to Parquet for repeated querying

**JSON:**
- Good for semi-structured data
- Auto-detection of newline-delimited vs regular JSON
- Consider converting to Parquet for performance

**Best Practice:**
```sql
-- Convert CSV to Parquet
COPY (SELECT * FROM 'data.csv') TO 'data.parquet' (FORMAT parquet);

-- Then query Parquet
SELECT * FROM 'data.parquet' WHERE ...;
```

### Query Optimization

#### Use EXPLAIN for Analysis
```sql
-- View query plan without execution
EXPLAIN SELECT ...;

-- Profile query execution
EXPLAIN ANALYZE SELECT ...;
```

**Look For:**
- Hash joins (good) vs nested loop joins (bad)
- Filter pushdown applied
- Parallelism utilized
- Statistics used

#### Avoid SELECT *
```sql
-- Bad - scans all columns
SELECT * FROM large_table;

-- Good - only needed columns
SELECT column1, column2 FROM large_table;
```

#### Join Order Optimization
- Let DuckDB's optimizer handle join ordering
- Optimizer provides enormous performance benefits
- Avoids intermediate cardinality explosions
- Statistics propagation creates efficient filters

#### Prepared Statements
- Cache parsing and planning output
- Most beneficial for queries with runtime < 100ms
- Reduce overhead for repeated queries

```python
# Python example
stmt = con.prepare("SELECT * FROM tbl WHERE id = ?")
for id in ids:
    result = stmt.execute([id])
```

### Connection Management

**Reuse Connections:**
- DuckDB performs best with connection reuse
- Disconnecting/reconnecting incurs overhead
- Keep connection alive for multiple queries

**Example Anti-Pattern:**
```python
# Bad - creates new connection each time
for file in files:
    con = duckdb.connect('db.db')
    con.execute(f"SELECT * FROM '{file}'")
    con.close()

# Good - reuse connection
con = duckdb.connect('db.db')
for file in files:
    con.execute(f"SELECT * FROM '{file}'")
con.close()
```

### Memory Configuration

**Adjust Memory Limit:**
```sql
SET memory_limit = '4GB';
SET memory_limit = '80%';  -- 80% of available RAM (default)
```

**Monitor Memory:**
```sql
-- Check current settings
SELECT * FROM duckdb_settings() WHERE name = 'memory_limit';
```

### Data Loading Patterns

#### Direct File Querying
```sql
-- Query without loading
SELECT * FROM 'data.parquet' WHERE value > 100;

-- Join multiple files
SELECT * FROM 'sales_*.parquet' WHERE year = 2024;
```

#### Bulk Loading
```sql
-- CSV with auto-detection
CREATE TABLE my_table AS SELECT * FROM read_csv('data.csv', AUTO_DETECT=TRUE);

-- Parquet
CREATE TABLE my_table AS SELECT * FROM 'data.parquet';

-- Multiple files
CREATE TABLE combined AS SELECT * FROM 'data/*.parquet';
```

#### Incremental Loading
```sql
-- Append to existing table
INSERT INTO my_table SELECT * FROM 'new_data.parquet';

-- Upsert pattern (v1.4.0+)
MERGE INTO target USING source ON target.id = source.id
WHEN MATCHED THEN UPDATE SET ...
WHEN NOT MATCHED THEN INSERT ...;
```

### Performance Optimization Patterns

#### Filter Early
```sql
-- Good - filter before join
SELECT * FROM
    (SELECT * FROM large_table WHERE date >= '2024-01-01') filtered
JOIN dimension ON filtered.key = dimension.key;
```

#### Use Appropriate Data Types
- Smaller types use less memory and are faster
- Use INTEGER instead of BIGINT when range allows
- DATE vs TIMESTAMP for date-only data

#### Partition Awareness
```sql
-- Take advantage of Parquet partitioning
SELECT * FROM 'data/year=*/month=*/*.parquet'
WHERE year = 2024 AND month = 11;
```

### When to Use DuckDB

**Ideal Use Cases:**
- Local-first workflows
- Jupyter notebooks and data exploration
- Ad hoc data analysis
- ETL and data transformation
- Processing large CSV/JSON files
- Machine learning feature engineering
- Log analysis and diagnostics
- Data quality validation in CI/CD
- Embedded analytics in applications
- Cost-effective analytics (vs cloud services)

**Not Ideal For:**
- Multi-user concurrent writes
- High-frequency transactional workloads
- Distributed systems requiring sharding
- When you need a database server
- Real-time operational databases

---

## 6. Real-World Use Cases

### Data Science Workflows

**Exploratory Data Analysis (EDA):**
```python
import duckdb
import pandas as pd

# Query large datasets efficiently
result = duckdb.query("""
    SELECT
        category,
        AVG(sales) as avg_sales,
        COUNT(*) as transaction_count
    FROM 'large_sales_data.parquet'
    WHERE year = 2024
    GROUP BY category
    ORDER BY avg_sales DESC
""").to_df()
```

**Benefits:**
- Works in Jupyter notebooks
- Handles larger-than-memory datasets
- SQL interface familiar to data scientists
- Direct integration with Pandas and Arrow

### ETL and Data Transformation

**Pipeline Example:**
```sql
-- Extract, transform, and load
COPY (
    SELECT
        customer_id,
        DATE_TRUNC('month', order_date) as month,
        SUM(amount) as monthly_total,
        COUNT(*) as order_count
    FROM read_csv('raw_orders/*.csv', AUTO_DETECT=TRUE)
    WHERE status = 'completed'
    GROUP BY customer_id, month
) TO 'processed/monthly_summary.parquet' (FORMAT parquet);
```

**Use Cases:**
- Pre-filtering before loading to data warehouse
- Data cleaning and validation
- Format conversion (CSV to Parquet)
- Aggregation and summarization

### Embedded Analytics

**Application Integration:**
```javascript
// Node.js embedded analytics
const duckdb = require('@duckdb/node-api');

class AnalyticsEngine {
    constructor(dbPath) {
        this.db = new duckdb.Database(dbPath);
        this.conn = this.db.connect();
    }

    async getDashboardMetrics(userId) {
        return await this.conn.run(`
            SELECT
                DATE_TRUNC('day', timestamp) as date,
                COUNT(*) as events,
                COUNT(DISTINCT session_id) as sessions
            FROM user_events
            WHERE user_id = $1
                AND timestamp >= CURRENT_DATE - INTERVAL 30 DAYS
            GROUP BY date
            ORDER BY date
        `, [userId]);
    }
}
```

### Log Analysis

**Processing Log Files:**
```sql
-- Analyze JSON logs
SELECT
    level,
    COUNT(*) as count,
    ARRAY_AGG(DISTINCT error_code) as error_codes
FROM read_json('logs/**/*.json', format='newline_delimited')
WHERE timestamp >= CURRENT_TIMESTAMP - INTERVAL 1 HOUR
    AND level IN ('ERROR', 'CRITICAL')
GROUP BY level;
```

**Benefits:**
- No need for Elasticsearch for basic analysis
- Pre-filter before loading to expensive services
- Local diagnostics and debugging

### Machine Learning Feature Engineering

**Feature Generation:**
```python
import duckdb

# Create training features
features = duckdb.query("""
    SELECT
        customer_id,
        -- Aggregated features
        COUNT(*) as total_orders,
        SUM(amount) as total_spent,
        AVG(amount) as avg_order_value,
        MAX(order_date) as last_order_date,
        -- Time-based features
        DATE_DIFF('day', MAX(order_date), CURRENT_DATE) as days_since_last_order,
        -- Window functions
        PERCENT_RANK() OVER (ORDER BY SUM(amount)) as spending_percentile
    FROM orders
    WHERE order_date >= CURRENT_DATE - INTERVAL 365 DAYS
    GROUP BY customer_id
""").to_df()

# Use directly in scikit-learn, PyTorch, etc.
```

### Data Quality Validation

**CI/CD Integration:**
```sql
-- Validation queries
-- Check for nulls in required fields
SELECT COUNT(*) as null_count
FROM 'incoming_data.parquet'
WHERE customer_id IS NULL;

-- Validate data ranges
SELECT COUNT(*) as invalid_dates
FROM 'incoming_data.parquet'
WHERE order_date > CURRENT_DATE;

-- Schema validation
SELECT column_name, data_type
FROM (DESCRIBE SELECT * FROM 'incoming_data.parquet')
WHERE column_name IN ('customer_id', 'order_date', 'amount');
```

### Processing Large Files

**Efficient Large File Handling:**
```python
# Process 100GB CSV without loading into memory
duckdb.execute("""
    COPY (
        SELECT *
        FROM read_csv('huge_file.csv', AUTO_DETECT=TRUE)
        WHERE condition = 'something'
    ) TO 'filtered_output.parquet' (FORMAT parquet)
""")
```

---

## 7. Extensions & Ecosystem

### Core Extensions

**Official Extensions (Built and Signed by DuckDB Team):**

- **httpfs:** HTTP/HTTPS and S3 file system support
- **parquet:** Enhanced Parquet reading and writing
- **json:** JSON file support
- **icu:** International Components for Unicode
- **tpch:** TPC-H benchmark data generator
- **tpcds:** TPC-DS benchmark data generator
- **fts:** Full-text search
- **excel:** Excel file reading
- **spatial:** Geospatial/GIS functionality
- **delta:** Delta Lake format support
- **iceberg:** Apache Iceberg format support
- **azure:** Azure Blob Storage support
- **postgres_scanner:** Read from PostgreSQL databases
- **mysql_scanner:** Read from MySQL databases
- **sqlite_scanner:** Read from SQLite databases
- **substrait:** Query plan serialization

### Community Extensions

**Third-Party Extensions:**
- Maintained by community
- Available through DuckDB's extension repository
- Varied functionality and domain-specific features

**Installation:**
```sql
INSTALL extension_name;
LOAD extension_name;
```

**Example:**
```sql
-- Install and load spatial extension
INSTALL spatial;
LOAD spatial;

-- Use spatial functions
SELECT ST_Area(geom) as area
FROM read_parquet('geo_data.parquet');
```

### Spatial Extension

**Geospatial Capabilities:**

**Core Technology:**
- Based on GEOS (same as PostGIS)
- GDAL/OGR for format support
- PROJ for coordinate transformations

**Features:**
- GEOMETRY data type (Simple Features model)
- 100+ ST_ functions (PostGIS-compatible)
- Support for 50+ geospatial file formats
- Spatial operations: ST_Area, ST_Intersects, ST_Buffer, etc.

**Example Usage:**
```sql
INSTALL spatial;
LOAD spatial;

-- Read geospatial file
CREATE TABLE buildings AS
SELECT * FROM ST_Read('buildings.geojson');

-- Spatial query
SELECT name, ST_Area(geom) as area
FROM buildings
WHERE ST_Intersects(geom,
    ST_GeomFromText('POLYGON((...))')
);

-- Export to different format
COPY (SELECT * FROM buildings)
TO 'output.gpkg'
WITH (FORMAT GDAL, DRIVER 'GPKG');
```

### Data Lake Extensions

#### Delta Lake Extension

**Features:**
- Native Delta Lake support
- Developed with Databricks
- Uses delta-kernel-rs project

```sql
INSTALL delta;
LOAD delta;

SELECT * FROM delta_scan('s3://bucket/delta-table');
```

#### Apache Iceberg Extension

**Features:**
- Read Iceberg tables
- SQL interfaces
- Versioning support
- ACID transactions

```sql
INSTALL iceberg;
LOAD iceberg;

SELECT * FROM iceberg_scan('s3://bucket/iceberg-table');
```

#### DuckLake

**DuckDB's Lakehouse Format (Released May 2025):**
- Open-source lakehouse format
- Standard SQL databases for metadata
- Parquet for data storage
- Simplified lakehouse management

### Cloud Storage Extensions

**AWS S3 (httpfs extension):**
```sql
INSTALL httpfs;
LOAD httpfs;

SET s3_region='us-east-1';
SET s3_access_key_id='...';
SET s3_secret_access_key='...';

SELECT * FROM 's3://bucket/data.parquet';
```

**Azure (azure extension):**
```sql
INSTALL azure;
LOAD azure;

SELECT * FROM 'az://container/data.parquet';
```

### Database Scanner Extensions

**Query Other Databases:**

```sql
-- PostgreSQL
INSTALL postgres_scanner;
LOAD postgres_scanner;

SELECT * FROM postgres_scan('host=localhost dbname=mydb', 'table_name');

-- MySQL
INSTALL mysql_scanner;
LOAD mysql_scanner;

-- SQLite
INSTALL sqlite_scanner;
LOAD sqlite_scanner;

SELECT * FROM sqlite_scan('database.db', 'table_name');
```

**Use Cases:**
- Data migration
- Cross-database analytics
- ETL from operational databases
- Data validation

---

## Key Takeaways for LLM Training & Developer Tools

### 1. Primary Mental Model
- **DuckDB = SQLite for Analytics**
- Embedded, no server, but optimized for OLAP not OLTP
- PostgreSQL-compatible SQL with columnar storage

### 2. Core Architectural Insight
- Columnar storage + vectorized execution = analytical performance
- In-process = zero network overhead
- Flexible memory management = handles larger-than-memory datasets

### 3. Common Patterns

**File Processing:**
```sql
-- Query files directly
SELECT * FROM 'data.parquet' WHERE ...;
SELECT * FROM read_csv('data.csv');
SELECT * FROM read_json('data.json');

-- Multiple files
SELECT * FROM 'data/*.parquet';
```

**Data Transformation:**
```sql
-- Convert formats
COPY (SELECT * FROM 'input.csv') TO 'output.parquet' (FORMAT parquet);

-- Filter and export
COPY (SELECT * FROM ... WHERE ...) TO 'filtered.parquet';
```

**Integration with Data Science:**
```python
import duckdb
result = duckdb.query("SELECT ...").to_df()  # Returns Pandas DataFrame
```

### 4. Decision Framework

**Use DuckDB When:**
- Single-machine analytics
- Local-first workflows
- Processing files (Parquet, CSV, JSON)
- Embedded in applications
- Data science/ML pipelines
- ETL transformations
- Cost-sensitive workloads

**Don't Use DuckDB When:**
- Need multi-user concurrent writes
- Distributed system architecture
- High-frequency transactions
- Network-based database server required

### 5. Performance Tips
1. Always use Parquet when possible (up to 600x faster than CSV)
2. Reuse database connections
3. Use EXPLAIN ANALYZE to profile queries
4. Let optimizer handle join ordering
5. Select only needed columns (avoid SELECT *)
6. Configure memory appropriately (default 80% of RAM)

### 6. Modern Features (2025)
- Database encryption (v1.4.0)
- MERGE statement (v1.4.0)
- DuckLake format (v1.3.0)
- Local web UI (v1.2.1)
- UUID v7 support
- Native Delta Lake and Iceberg support

### 7. Ecosystem Integration
- Python: Native integration with Pandas, Arrow
- R: duckplyr (drop-in dplyr replacement)
- Node.js: @duckdb/node-api
- Browser: DuckDB-Wasm
- Cloud: S3, Azure, GCS support
- Databases: PostgreSQL, MySQL, SQLite scanners

---

## Additional Resources

### Official Documentation
- **Main Site:** https://duckdb.org/
- **Documentation:** https://duckdb.org/docs/
- **Blog:** https://duckdb.org/news
- **GitHub:** https://github.com/duckdb/duckdb

### Key Papers and Presentations
- "DuckDB-Wasm: Fast Analytical Processing for the Web" (CMU)
- "Memory Management in DuckDB" (2024)
- "Analytics-Optimized Concurrent Transactions" (2024)
- "DuckDB Spatial" (GeoPython 2024)

### Community Resources
- Discord: Active community support
- GitHub Discussions: Technical questions
- MotherDuck Blog: Use cases and tutorials
- Community Extensions Repository

---

**Report End**

This research document provides a comprehensive overview of DuckDB suitable for:
- Training large language models on database systems
- Creating developer tools and documentation
- Understanding modern analytical database design
- Making architectural decisions for data workloads


## DuckDB & SQLMesh

> Source: `docs/data_engineering/duckdb/DuckDB - SQLMesh.md`

---
title: "DuckDB - SQLMesh"
source: "https://sqlmesh.readthedocs.io/en/stable/integrations/engines/duckdb/"
author:
published:
created: 2025-12-11
description:
tags:
  - "clippings"
---
[Skip to content](https://sqlmesh.readthedocs.io/en/stable/integrations/engines/duckdb/#duckdb)

## DuckDB

DuckDB state connection limitations

DuckDB is a [single user](https://duckdb.org/docs/connect/concurrency.html#writing-to-duckdb-from-multiple-processes) database. Using it for a state connection in your SQLMesh project limits you to a single workstation. This means your project cannot be shared amongst your team members or your CI/CD infrastructure. This is usually fine for proof of concept or test projects but it will not scale to production usage.

For production projects, use [Tobiko Cloud](https://tobikodata.com/product.html) or a more robust state database such as [Postgres](https://sqlmesh.readthedocs.io/en/stable/integrations/engines/postgres/).

## Local/Built-in Scheduler

**Engine Adapter Type**: `duckdb`

### Connection options

| Option | Description | Type | Required |
| --- | --- | --- | --- |
| `type` | Engine type name - must be `duckdb` | string | Y |
| `database` | The optional database name. If not specified, the in-memory database is used. Cannot be defined if using `catalogs`. | string | N |
| `catalogs` | Mapping to define multiple catalogs. Can [attach DuckDB catalogs](https://sqlmesh.readthedocs.io/en/stable/integrations/engines/duckdb/#duckdb-catalogs-example) or [catalogs for other connections](https://sqlmesh.readthedocs.io/en/stable/integrations/engines/duckdb/#other-connection-catalogs-example). First entry is the default catalog. Cannot be defined if using `database`. | dict | N |
| `extensions` | Extension to load into duckdb. Only autoloadable extensions are supported. | list | N |
| `connector_config` | Configuration to pass into the duckdb connector. | dict | N |
| `secrets` | Configuration for authenticating external sources (e.g., S3) using DuckDB secrets. Can be a list of secret configurations or a dictionary with custom secret names. | list/dict | N |
| `filesystems` | Configuration for registering `fsspec` filesystems to the DuckDB connection. | dict | N |

#### DuckDB Catalogs Example

This example specifies two catalogs. The first catalog is named "persistent" and maps to the DuckDB file database `local.duckdb`. The second catalog is named "ephemeral" and maps to the DuckDB in-memory database.

`persistent` is the default catalog since it is the first entry in the dictionary. SQLMesh will place models without an explicit catalog, such as `my_schema.my_model`, into the `persistent` catalog `local.duckdb` DuckDB file database.

SQLMesh will place models with the explicit catalog "ephemeral", such as `ephemeral.other_schema.other_model`, into the `ephemeral` catalog DuckDB in-memory database.

#### DuckLake Catalog Example

#### Other Connection Catalogs Example

Catalogs can also be defined to connect to anything that [DuckDB can be attached to](https://duckdb.org/docs/sql/statements/attach.html).

Below are examples of connecting to a SQLite database and a PostgreSQL database. The SQLite database is read-write, while the PostgreSQL database is read-only.

##### Catalogs for PostgreSQL

In PostgreSQL, the catalog name must match the actual catalog name it is associated with, as shown in the example above, where the database name (`dbname` in the path) is the same as the catalog name.

##### Connectors without schemas

Some connections, like SQLite, do not support schema names and therefore objects will be attached under the default schema name of `main`.

Example: mounting a SQLite database with the name `sqlite` that has a table `example_table` will be accessible as `sqlite.main.example_table`.

##### Sensitive fields in paths

If a connector, like Postgres, requires sensitive information in the path, it might support defining environment variables instead.[See DuckDB Documentation for more information](https://duckdb.org/docs/extensions/postgres#configuring-via-environment-variables).

#### Cloud service authentication

DuckDB can read data directly from cloud services via extensions (e.g., [httpfs](https://duckdb.org/docs/extensions/httpfs/s3api), [azure](https://duckdb.org/docs/extensions/azure)).

The `secrets` option allows you to configure DuckDB's [Secrets Manager](https://duckdb.org/docs/configuration/secrets_manager.html) to authenticate with external services like S3. This is the recommended approach for cloud storage authentication in DuckDB v0.10.0 and newer, replacing the [legacy authentication method](https://duckdb.org/docs/stable/extensions/httpfs/s3api_legacy_authentication.html) via variables.

##### Secrets Configuration

The `secrets` option supports two formats:

1. **List format** (default secrets): A list of secret configurations where each secret uses DuckDB's default naming
2. **Dictionary format** (named secrets): A dictionary where keys are custom secret names and values are the secret configurations

This flexibility allows you to organize multiple secrets of the same type or reference specific secrets by name in your SQL queries.

##### List Format Example (Default Secrets)

Using a list creates secrets with DuckDB's default naming:

##### Dictionary Format Example (Named Secrets)

Using a dictionary allows you to assign custom names to your secrets for better organization and reference:

After configuring the secrets, you can directly reference S3 paths in your catalogs or in SQL queries without additional authentication steps.

Refer to the official DuckDB documentation for the full list of [supported S3 secret parameters](https://duckdb.org/docs/stable/extensions/httpfs/s3api.html#overview-of-s3-secret-parameters) and for more information on the [Secrets Manager configuration](https://duckdb.org/docs/configuration/secrets_manager.html).

> Note: Loading credentials at runtime using `load_aws_credentials()` or similar deprecated functions may fail when using SQLMesh.

##### File system configuration example for Microsoft Onelake

The `filesystems` accepts a list of file systems to register in the DuckDB connection. This is especially useful for Azure Storage Accounts, as it adds write support for DuckDB which is not natively supported by DuckDB (yet).

Refer to the documentation for `fsspec` [fsspec.filesystem](https://filesystem-spec.readthedocs.io/en/latest/api.html#fsspec.filesystem) and `adlfs` [adlfs.AzureBlobFileSystem](https://fsspec.github.io/adlfs/api/#api-reference) for a full list of storage options.

## Spatial & Geospatial

> Source: `docs/data_engineering/duckdb/duckdb-spatial.md`

# DuckDB Spatial for Celtic Language Mapping

## Overview

DuckDB's spatial extension provides PostGIS-compatible geospatial functions for analyzing Celtic language areas, performing spatial joins between census data and boundaries, and preparing data for visualization.

---

## 1. Setup

### 1.1 Installation

```python
import duckdb

# Create connection and install spatial
conn = duckdb.connect("celtic_geo.duckdb")
conn.execute("INSTALL spatial; LOAD spatial;")
```

### 1.2 Verify Installation

```sql
-- Check spatial functions available
SELECT * FROM duckdb_functions() WHERE function_name LIKE 'ST_%' LIMIT 10;
```

---

## 2. Loading Geospatial Data

### 2.1 GeoJSON Files

```sql
-- Load Gaeltacht boundaries from GeoJSON
CREATE TABLE gaeltacht_areas AS
SELECT * FROM ST_Read('/path/to/gaeltacht_areas.geojson');

-- Load NI Data Zones
CREATE TABLE ni_data_zones AS
SELECT * FROM ST_Read('/path/to/dz2021.geojson');
```

### 2.2 Shapefiles

```sql
-- Load from Shapefile
CREATE TABLE language_planning_areas AS
SELECT * FROM ST_Read('/path/to/lpa_boundaries.shp');
```

### 2.3 CSV with Coordinates

```sql
-- Load schools with lat/lng columns
CREATE TABLE schools AS
SELECT
    school_name,
    roll_number,
    eircode,
    ST_Point(longitude, latitude) AS geom
FROM read_csv('/path/to/schools.csv');
```

---

## 3. Core Spatial Operations

### 3.1 Point in Polygon (Schools in Gaeltacht)

```sql
-- Find schools within Gaeltacht areas
SELECT
    s.school_name,
    s.roll_number,
    g.area_name AS gaeltacht_name
FROM schools s
JOIN gaeltacht_areas g
ON ST_Within(s.geom, g.geom);
```

### 3.2 Spatial Join (Census to Boundaries)

```sql
-- Join census data to Gaeltacht boundaries
SELECT
    g.area_name,
    SUM(c.irish_speakers) AS total_speakers,
    SUM(c.population) AS total_population,
    ROUND(100.0 * SUM(c.irish_speakers) / SUM(c.population), 2) AS speaker_pct
FROM gaeltacht_areas g
JOIN census_small_areas c
ON ST_Intersects(g.geom, c.geom)
GROUP BY g.area_name
ORDER BY speaker_pct DESC;
```

### 3.3 Buffer Analysis

```sql
-- Find schools within 5km of Gaeltacht boundaries
SELECT
    s.school_name,
    ST_Distance(s.geom, g.geom) / 1000 AS distance_km
FROM schools s, gaeltacht_areas g
WHERE ST_DWithin(s.geom, ST_Buffer(g.geom, 5000), 0)
ORDER BY distance_km;
```

### 3.4 Area Calculations

```sql
-- Calculate area of each Gaeltacht region
SELECT
    area_name,
    ROUND(ST_Area(geom) / 1000000, 2) AS area_km2
FROM gaeltacht_areas
ORDER BY area_km2 DESC;
```

---

## 4. Census Data Analysis

### 4.1 Speaker Concentration Mapping

```sql
-- Calculate speaker percentage by Small Area
CREATE TABLE speaker_choropleth AS
SELECT
    sa.sa_code,
    sa.geom,
    c.can_speak_irish,
    c.daily_speakers,
    c.population,
    ROUND(100.0 * c.can_speak_irish / NULLIF(c.population, 0), 2) AS ability_pct,
    ROUND(100.0 * c.daily_speakers / NULLIF(c.population, 0), 2) AS daily_pct
FROM small_area_boundaries sa
JOIN census_language c ON sa.sa_code = c.sa_code;
```

### 4.2 Gaeltacht vs Non-Gaeltacht Comparison

```sql
-- Compare speaker rates inside vs outside Gaeltacht
WITH classified AS (
    SELECT
        c.*,
        CASE WHEN g.area_name IS NOT NULL THEN 'Gaeltacht' ELSE 'Non-Gaeltacht' END AS area_type
    FROM census_small_areas c
    LEFT JOIN gaeltacht_areas g ON ST_Within(c.geom, g.geom)
)
SELECT
    area_type,
    SUM(population) AS total_pop,
    SUM(irish_speakers) AS total_speakers,
    ROUND(100.0 * SUM(irish_speakers) / SUM(population), 2) AS speaker_pct,
    SUM(daily_speakers) AS total_daily,
    ROUND(100.0 * SUM(daily_speakers) / SUM(population), 2) AS daily_pct
FROM classified
GROUP BY area_type;
```

### 4.3 County-Level Aggregation

```sql
-- Aggregate to county level
SELECT
    county,
    SUM(population) AS pop,
    SUM(irish_speakers) AS speakers,
    ROUND(100.0 * SUM(irish_speakers) / SUM(population), 2) AS pct,
    COUNT(*) AS num_areas
FROM census_small_areas
GROUP BY county
ORDER BY pct DESC;
```

---

## 5. School Analysis

### 5.1 School Density by Area

```sql
-- Count Irish-medium schools per county
SELECT
    county,
    COUNT(*) AS num_schools,
    SUM(enrollment) AS total_pupils
FROM irish_medium_schools
GROUP BY county
ORDER BY num_schools DESC;
```

### 5.2 Schools in Language Planning Areas

```sql
-- Identify schools in each LPA
SELECT
    lpa.lpa_name,
    COUNT(s.roll_number) AS num_schools,
    STRING_AGG(s.school_name, ', ') AS schools
FROM language_planning_areas lpa
LEFT JOIN irish_medium_schools s
ON ST_Within(s.geom, lpa.geom)
GROUP BY lpa.lpa_name
ORDER BY num_schools DESC;
```

### 5.3 Distance to Nearest School

```sql
-- Calculate distance to nearest Irish-medium school for each area
WITH nearest AS (
    SELECT
        sa.sa_code,
        MIN(ST_Distance(sa.geom, s.geom)) AS min_distance
    FROM small_area_boundaries sa
    CROSS JOIN irish_medium_schools s
    GROUP BY sa.sa_code
)
SELECT
    sa_code,
    min_distance / 1000 AS nearest_school_km
FROM nearest
ORDER BY min_distance DESC
LIMIT 20;
```

---

## 6. Cross-Border Analysis

### 6.1 Unified View

```sql
-- Create unified view of speaker data
CREATE VIEW all_ireland_speakers AS
SELECT
    'ROI' AS jurisdiction,
    sa_code AS area_code,
    geom,
    population,
    irish_speakers,
    daily_speakers
FROM roi_census_small_areas

UNION ALL

SELECT
    'NI' AS jurisdiction,
    dz_code AS area_code,
    geom,
    population,
    irish_ability AS irish_speakers,
    daily_speakers
FROM ni_census_data_zones;
```

### 6.2 Border Region Analysis

```sql
-- Define border counties
WITH border_counties AS (
    SELECT * FROM counties
    WHERE county_name IN (
        'Donegal', 'Leitrim', 'Cavan', 'Monaghan', 'Louth',  -- ROI
        'Derry', 'Tyrone', 'Fermanagh', 'Armagh', 'Down'     -- NI
    )
)
SELECT
    bc.county_name,
    bc.jurisdiction,
    SUM(c.irish_speakers) AS speakers,
    SUM(c.population) AS population,
    ROUND(100.0 * SUM(c.irish_speakers) / SUM(c.population), 2) AS pct
FROM border_counties bc
JOIN all_ireland_speakers c ON ST_Within(c.geom, bc.geom)
GROUP BY bc.county_name, bc.jurisdiction
ORDER BY pct DESC;
```

---

## 7. Export for MapLibre

### 7.1 GeoJSON Export

```sql
-- Export choropleth data as GeoJSON
COPY (
    SELECT
        sa_code,
        ability_pct,
        daily_pct,
        ST_AsGeoJSON(geom) AS geometry
    FROM speaker_choropleth
) TO '/output/speakers.geojson'
WITH (FORMAT JSON);
```

### 7.2 Prepare for Vector Tiles

```sql
-- Simplify geometries for web display
CREATE TABLE web_gaeltacht AS
SELECT
    area_name,
    speaker_pct,
    ST_Simplify(geom, 100) AS geom  -- 100m tolerance
FROM gaeltacht_areas;

-- Export for tippecanoe
COPY web_gaeltacht TO '/output/gaeltacht.geojson'
WITH (FORMAT JSON);
```

### 7.3 Centroid Export (For Labels)

```sql
-- Generate centroids for labeling
SELECT
    area_name,
    ST_X(ST_Centroid(geom)) AS lng,
    ST_Y(ST_Centroid(geom)) AS lat
FROM gaeltacht_areas;
```

---

## 8. Complete Pipeline Example

```python
#!/usr/bin/env python3
"""
DuckDB Spatial Pipeline for Celtic Language Mapping
"""

import duckdb
from pathlib import Path

class CelticGeoPipeline:
    def __init__(self, db_path: str = ":memory:"):
        self.conn = duckdb.connect(db_path)
        self.conn.execute("INSTALL spatial; LOAD spatial;")

    def load_boundaries(self, geojson_path: str, table_name: str):
        """Load GeoJSON boundaries."""
        self.conn.execute(f"""
            CREATE TABLE {table_name} AS
            SELECT * FROM ST_Read('{geojson_path}')
        """)

    def load_census_csv(self, csv_path: str, table_name: str):
        """Load census data from CSV."""
        self.conn.execute(f"""
            CREATE TABLE {table_name} AS
            SELECT * FROM read_csv('{csv_path}')
        """)

    def join_census_to_boundaries(
        self,
        census_table: str,
        boundary_table: str,
        join_key: str
    ):
        """Spatial join census data to boundaries."""
        return self.conn.execute(f"""
            SELECT
                b.*,
                c.population,
                c.irish_speakers,
                c.daily_speakers,
                ROUND(100.0 * c.irish_speakers / NULLIF(c.population, 0), 2) AS pct
            FROM {boundary_table} b
            LEFT JOIN {census_table} c ON b.{join_key} = c.{join_key}
        """).fetchdf()

    def schools_in_areas(self, schools_table: str, areas_table: str):
        """Find schools within areas."""
        return self.conn.execute(f"""
            SELECT
                a.area_name,
                COUNT(s.*) AS num_schools
            FROM {areas_table} a
            LEFT JOIN {schools_table} s ON ST_Within(s.geom, a.geom)
            GROUP BY a.area_name
        """).fetchdf()

    def export_geojson(self, query: str, output_path: str):
        """Export query result as GeoJSON."""
        self.conn.execute(f"""
            COPY ({query}) TO '{output_path}'
            WITH (FORMAT JSON)
        """)

def main():
    pipeline = CelticGeoPipeline("celtic_geo.duckdb")

    # Load data
    pipeline.load_boundaries(
        "gaeltacht_areas.geojson",
        "gaeltacht"
    )

    # Analysis
    results = pipeline.schools_in_areas("schools", "gaeltacht")
    print(results)

    # Export
    pipeline.export_geojson(
        "SELECT * FROM gaeltacht",
        "output/gaeltacht.geojson"
    )

if __name__ == "__main__":
    main()
```

---

## 9. Performance Tips

| Operation | Tip |
|-----------|-----|
| **Large datasets** | Use `ST_Simplify()` for web export |
| **Spatial joins** | Create spatial index with `CREATE INDEX` |
| **Point-in-polygon** | Use `ST_DWithin()` for approximate queries |
| **Memory** | Use disk-based DB for >1GB data |

---

## References

- DuckDB Spatial: https://duckdb.org/docs/extensions/spatial
- PostGIS (compatible functions): https://postgis.net/docs/
- Tailte Éireann Open Data: https://data-osi.opendata.arcgis.com


## Geospatial Data Analysis with DuckDB

> Source: `docs/data_engineering/duckdb/Geospatial Data Analysis and DuckDB.md`

# **Convergence of Spatial Analytics and Digital Folkloristics: A Technical and Theoretical Examination of *Hidden Heritages* and *Canúint.ie***

## **1\. Introduction: The Spatial Turn in Digital Heritage**

The digitization of cultural heritage has transitioned from a phase of static preservation—scanning manuscripts and archiving audio—to a dynamic era of computational interrogation and geospatial visualization. Within the specific context of the Gaelic-speaking world, this shift is exemplified by two vanguard projects: **Hidden Heritages** (Díchódú Oidhreachtaí Folaithe) and **Canúint.ie** (Taisce Chanúintí na Gaeilge). These initiatives do not merely present archives on a digital shelf; they explode the archive into a spatial dimension, allowing for the visualization of intangible cultural assets—narrative motifs and dialect phonemes—across the physical landscapes of Ireland and Scotland.  
This report provides an exhaustive technical analysis of the geospatial strategies employed by these projects, situated within the broader infrastructure of the **Gaois** research group at Dublin City University (DCU). It further explores the potential for next-generation analytics using **DuckDB** and its spatial extension, proposing a high-performance architectural paradigm for querying the massive, complex datasets inherent to digital folkloristics.

### **1.1 The Epistemology of the Digital Map**

In the realm of *Hidden Heritages* and *Canúint.ie*, the map functions as more than a navigational aid; it is an epistemological tool. It fundamentally alters the user's relationship with the data. Traditional archival access is hierarchical and textual: one selects a collection, then a volume, then a page. The geospatial interface, however, is non-linear and immediate. It asserts that the *location* of a story's telling is as significant as the *content* of the story itself.1  
For *Hidden Heritages*, the map visualizes the "phylogeography" of folklore—tracing how a tale type like *ATU 425* ('The Search for the Lost Husband') mutates as it migrates across the Irish Sea, effectively treating narrative elements as biological traits subject to evolutionary pressures.3 For *Canúint.ie*, the map serves as a linguistic atlas, grounding ephemeral speech acts in specific townlands, thereby rendering the invisible boundaries of dialect (isoglosses) visible.2

### **1.2 The Gaois Technical Ecosystem**

The shared lineage of these projects within the Gaois research group provides a unified technical baseline. Gaois has established itself as a premier developer of linguistic infrastructure, leveraging a stack that historically favors **Microsoft technologies (ASP.NET, SQL Server)** while increasingly integrating open-source geospatial libraries.5  
The analysis of their public repositories reveals a modular architecture:

* **Backend:** Robust APIs built on ASP.NET Core (Gaois.Localizer, Gaois.QueryLogger) that serve structured JSON/XML data.7  
* **Data Persistence:** SQL Server databases managing complex relational schemas of terminology, toponymy, and bibliography.5  
* **Frontend:** A heavy reliance on JavaScript mapping libraries—specifically **Leaflet** and **OpenLayers**—to render geospatial data delivered via these APIs.8

This report dissects these components, contrasting the lightweight, mobile-first approach likely employed by *Canúint.ie* with the heavy-duty, vector-rich requirements of *Hidden Heritages*, before demonstrating how **DuckDB** can serve as a powerful analytical engine to bridge these domains.

## ---

**2\. Theoretical Framework: Digital Folkloristics and Spatial Data**

To understand the technical requirements of these projects, one must first appreciate the complexity of the data they handle. "Digital Folkloristics" is not simply the storage of folklore; it is the computational analysis of tradition.

### **2.1 The Challenge of "Deep Mapping"**

Deep mapping refers to the layering of diverse data types—text, audio, image, and metadata—onto a single geographic locus.

* **Temporal Depth:** A single coordinate (e.g., a hearth in Dunquin, Kerry) may be associated with stories collected in 1930, 1945, and 1970\. The spatial database must handle this temporal dimension effectively, allowing users to filter the map by time.1  
* **Typological Depth:** The data is not unstructured. It is rigorously classified according to the **Aarne-Thompson-Uther (ATU)** index. *Hidden Heritages* specifically focuses on complex "Wonder Tales" (Märchen), such as *ATU 400* ('The Search for the Lost Wife') and *ATU 503* ('The Gifts of the Little People').3

The geospatial data architecture must therefore support **one-to-many relationships** (one location, many tales) and **hierarchical filtering** (showing all tales of type *ATU 4xx*).

### **2.2 Phylogenetics and Spatial Diffusion**

The *Hidden Heritages* project introduces a novel computational method: **Phylogenetics**. Originating in evolutionary biology, this approach builds "trees" of story versions to determine their ancestral relationships.

* **Spatial Implication:** When these phylogenetic trees are projected onto a map, they reveal the *routes* of cultural transmission. If Version A (Donegal) is computationally determined to be the "parent" of Version B (Hebrides), the map draws a vector of transmission.  
* **Data Requirement:** This requires the geospatial system to handle not just *points* (locations of tales) but *vectors/edges* (relationships between tales), necessitating a graph-based data structure overlaying the geographic layer.3

### **2.3 Acoustic Geographies and Dialectology**

*Canúint.ie* deals with **acoustic geography**. The primary data object is the **phoneme** or **lexical item** as realized in a specific location.

* **The Isogloss:** In linguistics, an isogloss is a line on a map marking the boundary between two linguistic features (e.g., where the pronunciation of a vowel changes).  
* **Spatial Granularity:** Unlike folktales, which might be attributed to a general parish, dialect data often requires precise *townland* specificity to accurately map these boundaries. The system must support high-precision geocoding and the ability to render "heat maps" or cluster visualizations to show the density of specific dialect features.2

## ---

**3\. Case Study I: Hidden Heritages (Díchódú Oidhreachtaí Folaithe)**

### **3.1 Project Scope and Architecture**

*Hidden Heritages* represents a massive undertaking in "text mining" and "data curation." It serves as a bridge between the **National Folklore Collection (NFC)** in Dublin and the **School of Scottish Studies Archives (SSSA)** in Edinburgh.  
**Data Scale:**

* **Corpus:** \~80,000 manuscript pages.  
* **Collections:** The Main Manuscript Collection (NFC) and the Tale Archive (SSSA).3  
* **Geographic Scope:** The entire Gaeltacht regions of Ireland and the Gàidhealtachd of Scotland.

### **3.2 The "Manuscripts to Models" Pipeline**

The geospatial visualization is the final output of a rigorous processing pipeline known as "From Manuscripts to Models."

1. **Digitization:** High-resolution scanning of physical volumes.  
2. **Handwritten Text Recognition (HTR):** The project utilizes **Transkribus**, an AI-powered HTR platform. This is critical because the source material is often in non-standard scripts (Gaelic script) or cursive English.  
   * **Performance:** The project reports training models on \~500 pages of manuscript to achieve a Character Error Rate (CER) of \~4.39%. This high accuracy is essential for the subsequent NLP steps.14  
3. **Text Mining & Entity Extraction:** Once the text is digital, NLP algorithms (likely Python-based, given the gaoisalign and transformers references 5) extract metadata:  
   * **Toponyms:** Placenames are identified and resolved against authority databases (*Logainm.ie*).  
   * **Motifs:** Key narrative elements are identified to classify the tale.  
4. **Geospatial Indexing:** The extracted toponyms are converted to coordinates (Latitude/Longitude) and stored in the project's database, linked to the text segment.

### **3.3 Geospatial Visualization Strategy**

The project's frontend likely employs a "Dual-View" interface.

* **The Map View:** Users see the distribution of tales. A filter for "Giants" (*Fuamhairean*) or "Fairies" (*Na Daoine Beaga*) updates the map markers in real-time.1  
* **The Graph View:** Users see the phylogenetic tree of a tale type.  
* **Integration:** Clicking a node in the tree highlights the corresponding point on the map. This requires a tight coupling between the graph data structure (nodes/edges) and the spatial data structure (points).

**Technical Assumption:** Given the complexity of visualizing phylogenetic networks alongside maps, the project likely utilizes **D3.js** for the graph visualizations and overlays them on **OpenLayers** or **Leaflet** maps. The robust API capabilities of the Gaois stack would serve the node-edge-coordinate data as a single JSON payload.11

## ---

**4\. Case Study II: Canúint.ie (Taisce Chanúintí na Gaeilge)**

### **4.1 Project Scope and Archival Integration**

*Canúint.ie* is a "Repository of Irish Dialects" focusing on the audio heritage of the language. It represents a partnership between the academic rigor of DCU and the archival wealth of **RTÉ** (Raidió Teilifís Éireann).2  
**Data Characteristics:**

* **Source:** Historic radio recordings, often from the mid-20th century.  
* **Content:** Interviews, storytelling, and conversation capturing natural speech.  
* **Metadata:** Rich biographical data on speakers (age, gender, occupation) which is crucial for sociolinguistic analysis.2

### **4.2 Geospatial Implementation: Mapping the Intangible**

For *Canúint.ie*, the geospatial challenge is indexing. Audio files do not have inherent coordinates. The spatial data is **derived** from the speaker's biography.

#### **4.2.1 The "Speaker-Location" Bond**

The system likely links each audio asset to a **Person Entity** in the database. This Person Entity is linked to a **Place Entity** (Townland/Parish).

* **Database Schema Implication:**  
  * Table: AudioAssets \-\> FK: SpeakerID  
  * Table: Speakers \-\> FK: PlaceID  
  * Table: Places \-\> Columns: Lat, Long, Geometry (Polygon)  
  * *Result:* The map query joins these three tables to plot the audio recording.15

#### **4.2.2 User Experience (UX) and Discovery**

The map on *Canúint.ie* is the primary search engine.

* **Clustering:** Given the high density of recordings in specific Gaeltacht areas (e.g., West Kerry, Connemara), the map must use **clustering algorithms**. At low zoom levels, users see a circle with a number (e.g., "50" recordings in Kerry). As they zoom in, the cluster breaks apart into individual markers.8  
* **Polygon Overlays:** The interface likely displays the official **Gaeltacht boundaries** as polygon layers, allowing users to visually distinguish between the "official" Irish-speaking regions and the historical distribution of the dialects.16

## ---

**5\. Comparative Technical Analysis: The Gaois Geospatial Stack**

Both projects are underpinned by the Gaois research group's technical infrastructure. Analyzing their GitHub repositories and documentation reveals a distinct preference for specific technologies that enable these rich spatial experiences.

### **5.1 The Mapping Engine: Leaflet vs. OpenLayers**

A critical architectural decision in any geospatial project is the choice of client-side library. The Gaois ecosystem appears to utilize both, depending on the project's density and complexity.17

#### **5.1.1 Leaflet (The Likely Choice for Canúint.ie)**

* **Profile:** Lightweight (\~40KB), mobile-optimized, plugin-based.  
* **Why for Canúint.ie?** The primary interaction on *Canúint.ie* is "point-and-play." Users need to find a marker and listen to audio. Leaflet excels at handling marker clusters and simple popups without the overhead of a full GIS engine. It allows for a snappy, responsive experience on mobile devices, which is crucial for public engagement projects.19  
* **Data Handling:** Leaflet consumes GeoJSON natively. The API likely serves a lightweight GeoJSON feed of recording locations:  
  JSON  
  { "type": "Feature", "geometry": { "type": "Point", "coordinates": \[...\] }, "properties": { "url": "audio.mp3" } }

#### **5.1.2 OpenLayers (The Likely Choice for Hidden Heritages)**

* **Profile:** Heavyweight, feature-rich, supports complex vector projections and OGC standards (WMS/WFS).  
* **Why for Hidden Heritages?** This project involves "phylogenetic maps" and potential overlays of historical boundaries that might not match modern projections. OpenLayers offers robust support for:  
  * **Vector Tiling:** Rendering thousands of tale locations efficiently.  
  * **Projections:** Handling historical map layers (e.g., Cassini 6-inch maps) that require on-the-fly reprojection to align with modern satellite imagery.  
  * **Complex Interactions:** Drawing vectors between points to visualize the "movement" of a story.8

### **5.2 Backend Architecture: The API Layer**

The "Gaois" GitHub repositories (Gaois.QueryLogger, Gaois.Localizer) indicate a.NET-centric backend.5

* **Framework:** **ASP.NET Core**. This provides a high-performance, cross-platform server environment.  
* **Database:** **SQL Server**. Microsoft's RDBMS supports GEOGRAPHY and GEOMETRY data types natively, allowing for spatial indexing (QuadTree/Grid) at the database level.  
* **API Design:** The projects likely expose RESTful endpoints.  
  * GET /api/tales?bbox=...: Returns tales within the current map viewport.  
  * GET /api/dialects/{id}/geojson: Returns the specific geometry for a dialect region.

### **5.3 Metadata Standards**

Both projects rely on rich metadata.

* **Hidden Heritages:** Uses the **ATU Index** (Aarne-Thompson-Uther) as a controlled vocabulary for narrative content. This allows for precise filtering (e.g., "Show me all *ATU 425* tales").3  
* **Canúint.ie:** Likely adheres to **Dublin Core** or similar archival standards for describing digital assets, ensuring interoperability with the broader European digital library ecosystem (Europeana).7

## ---

**6\. Advanced Analytics: The DuckDB Spatial Paradigm**

While the web interfaces of *Hidden Heritages* and *Canúint.ie* provide excellent *access*, they are not designed for deep, heavy-duty computational analysis. A researcher wishing to query the entire dataset—cross-referencing 80,000 pages of text with geospatial boundaries and temporal filters—would face significant latency using standard web APIs.  
This is where **DuckDB** enters the architecture. DuckDB is an in-process SQL OLAP (Online Analytical Processing) database that can query massive datasets with extreme speed, without the overhead of a server like PostgreSQL/PostGIS.

### **6.1 Why DuckDB for Digital Folkloristics?**

1. **Columnar Storage:** Unlike row-based databases (PostgreSQL), DuckDB stores data by column. For a query like "Calculate the average year of collection for all tales in Donegal," DuckDB only reads the Year and County columns, ignoring the massive Text column. This results in orders-of-magnitude faster analytics.21  
2. **Vectorized Execution:** DuckDB processes data in batches (vectors) rather than row-by-row, leveraging modern CPU architectures (SIMD instructions) for speed.21  
3. **The spatial Extension:** This extension adds geospatial capabilities comparable to PostGIS but optimized for local, file-based analysis. It supports the OGC Simple Features standard (POINT, POLYGON, etc.).23

### **6.2 Technical Sample: Analyzing Folklore Distribution**

The following section provides a detailed technical walkthrough of how a researcher could use DuckDB to analyze the *Hidden Heritages* dataset.  
**Scenario:** We want to ingest a raw GeoJSON dump of folklore sites, extract complex nested properties (metadata), and perform a spatial join to find which tales fall within specific Gaeltacht boundaries.

#### **6.2.1 Installation and Loading**

First, the researcher must initialize the DuckDB environment and load the necessary extensions. The spatial extension is not autoloaded and must be explicitly loaded.25

SQL

\-- Install and Load the Spatial Extension  
INSTALL spatial;  
LOAD spatial;

\-- Install and Load the JSON Extension (critical for GeoJSON properties)  
INSTALL json;  
LOAD json;

#### **6.2.2 Ingesting GeoJSON with ST\_Read**

The ST\_Read function is the gateway. It utilizes the **GDAL** library under the hood to parse geospatial formats. However, GeoJSON often contains nested objects in the properties field that standard tabular import might flatten or ignore.  
**The Naive Approach:**

SQL

CREATE TABLE raw\_sites AS SELECT \* FROM ST\_Read('folklore\_sites.geojson');

*Critique:* This works for simple files but often fails to capture deep metadata structures common in digital humanities (e.g., a list of motifs inside a properties object).  
The Robust Approach (JSON Parsing):  
A better method involves reading the file as raw JSON and explicitly parsing the structure. This allows the researcher to control exactly how the metadata is mapped to columns.27

SQL

\-- Create a structured table from the raw GeoJSON  
CREATE TABLE folklore\_analysis AS  
SELECT  
    \-- 1\. Extract Geometry  
    \-- We extract the geometry object and convert it to DuckDB's internal GEOMETRY type  
    ST\_GeomFromGeoJSON(json\_extract(feature, '$.geometry')) AS geom,

    \-- 2\. Extract Top-Level Properties  
    json\_extract\_string(feature, '$.properties.title') AS title,  
    json\_extract\_string(feature, '$.properties.collector\_id') AS collector\_id,

    \-- 3\. Extract Nested Metadata (The "Attached Data")  
    \-- Example: Extracting the ATU Tale Type from a nested metadata object  
    json\_extract\_string(feature, '$.properties.metadata.atu\_type') AS atu\_type,  
      
    \-- Example: Extracting the Informant's Gender for demographic analysis  
    json\_extract\_string(feature, '$.properties.metadata.informant.gender') AS gender,

    \-- Example: Extracting the recording year  
    CAST(json\_extract\_string(feature, '$.properties.date.year') AS INTEGER) AS year

FROM   
    \-- Read the GeoJSON file as a list of JSON objects (newline delimited or array)  
    read\_json\_auto('folklore\_sites.geojson', format='auto') AS data(feature)  
WHERE   
    \-- Ensure we only process valid spatial features  
    json\_extract(feature, '$.geometry') IS NOT NULL;

**Analysis of the Code:**

* ST\_GeomFromGeoJSON: This function parses the JSON geometry fragment (e.g., {"type": "Point", "coordinates": \[...\]}) into DuckDB's binary GEOMETRY format. This binary format is optimized for spatial operations.29  
* json\_extract\_string: Digital heritage data is notoriously "messy." By extracting specific paths, we sanitize the input before analysis.

#### **6.2.3 Spatial Joins: Point-in-Polygon Analysis**

Once the data is in DuckDB, we can perform spatial joins. A common question in *Canúint.ie* research might be: "Which recordings fall within the official 1956 Gaeltacht boundaries?"  
The Join Operation:  
DuckDB uses an R-Tree index (or similar bounding volume hierarchy) to optimize spatial joins. It first checks if the bounding box of the point intersects the bounding box of the polygon (fast), and only then performs the precise geometry check (slow).16

SQL

\-- Step 1: Load the Gaeltacht Boundaries (Polygons)  
CREATE TABLE gaeltacht\_boundaries AS   
SELECT \* FROM ST\_Read('gaeltacht\_1956.shp');

\-- Step 2: Perform the Spatial Join  
SELECT   
    g.district\_name AS gaeltacht\_district,  
    f.atu\_type,  
    COUNT(\*) AS tale\_count  
FROM   
    folklore\_analysis f  
JOIN   
    gaeltacht\_boundaries g  
ON   
    \-- The Spatial Predicate: Is the point INSIDE the polygon?  
    ST\_Intersects(f.geom, g.geom)  
WHERE   
    f.year BETWEEN 1930 AND 1940  
GROUP BY   
    g.district\_name, f.atu\_type  
ORDER BY   
    tale\_count DESC;

Performance Implications:  
In a traditional Python script using shapely, this join would happen in a loop and could take minutes for 80,000 points. In DuckDB, thanks to vectorized execution and spatial indexing, this query typically runs in sub-second timeframes.21

#### **6.2.4 Exporting Results**

Finally, the researcher can export the analyzed subset back to GeoJSON for visualization on the *Hidden Heritages* web map.

SQL

\-- Export filtered dataset to GeoJSON  
COPY (  
    SELECT   
        title,   
        atu\_type,   
        \-- Convert the binary geometry back to GeoJSON text  
        ST\_AsGeoJSON(geom) AS geometry   
    FROM folklore\_analysis   
    WHERE gaeltacht\_district \= 'Conamara'  
) TO 'conamara\_tales.geojson'  
WITH (FORMAT GDAL, DRIVER 'GeoJSON');

This COPY... TO command utilizes the GDAL driver to write a perfectly formatted GeoJSON file, ready for consumption by Leaflet or OpenLayers.30

## ---

**7\. Future Directions: The AI and Vector Horizon**

The convergence of technologies seen in *Hidden Heritages* and *Canúint.ie* points toward a future where the map is the primary interface for all digital humanities.

### **7.1 From Tiles to Vectors**

As the datasets grow—potentially mapping every word in the 80,000-page corpus—the current strategy of loading GeoJSON files into the browser will hit memory limits. The next logical step for Gaois is the adoption of **Vector Tiles (MVT)**.

* **Mechanism:** Instead of sending the whole dataset, the server sends only the vector data visible in the current viewport, sliced into tiles.  
* **DuckDB Role:** DuckDB can generate MVTs dynamically (ST\_AsMVT), allowing for massive datasets to be browsed seamlessly without heavy frontend loading.

### **7.2 Semantic Search and LLMs**

The "Hidden Heritages" project's use of NLP suggests a future where users can query the map semantically. Instead of searching for "ATU 425", a user could ask, "Show me where stories about transformation into animals are told." Large Language Models (LLMs) integrated with the spatial database could translate this natural language query into the SQL/Spatial query demonstrated above.

## **8\. Conclusion**

*Hidden Heritages* and *Canúint.ie* demonstrate that the preservation of folklore is no longer a static endeavor. By coupling the rich, qualitative data of the **National Folklore Collection** and **RTÉ Archives** with rigorous geospatial engineering, these projects reveal the hidden structures of culture. They show that stories and dialects are not just abstract concepts; they are grounded in the physical landscape, moving and evolving across the hills and coastlines of Ireland and Scotland.  
The technical architecture underpinning this—a sophisticated blend of **Transkribus** for ingestion, **Gaois's ASP.NET** stack for delivery, and **Leaflet/OpenLayers** for visualization—provides a robust platform for discovery. Furthermore, the integration of advanced analytical tools like **DuckDB Spatial** empowers researchers to move beyond simple viewing to deep, computational interrogation of the archive. This synthesis of tradition and technology ensures that these "hidden heritages" are not only decoded but dynamically revitalized for the digital age.

### ---

**Data Summary Tables**

**Table 1: Comparative Geospatial Architecture**

| Feature | Hidden Heritages (Díchódú Oidhreachtaí Folaithe) | Canúint.ie (Taisce Chanúintí na Gaeilge) |
| :---- | :---- | :---- |
| **Primary Data Object** | **Text / Narrative** (Folktale) | **Audio / Speech** (Dialect Recording) |
| **Spatial Nature** | **Phylogeographic:** Tracks movement/evolution of tales. | **Dialectological:** Indexes speech to specific loci. |
| **Data Volume** | \~80,000 manuscript pages (Text Mining). | Thousands of hours of audio (RTÉ Archive). |
| **Mapping Library** | **OpenLayers** (Likely) \- For complex vector/graph overlays. | **Leaflet** (Likely) \- For responsive clustering/playback. |
| **Key Metadata** | ATU Tale Type, Motif, Narrator, Collector. | Speaker Bio, Dialect Region, Recording Date. |
| **Key Technologies** | Transkribus (HTR), NLP, D3.js (Graphs). | Audio Streaming, Clustering Algorithms. |

**Table 2: DuckDB Spatial Capabilities for Digital Heritage**

| Function Category | Function Name | Usage in Digital Folkloristics | Implementation |
| :---- | :---- | :---- | :---- |
| **Ingestion** | ST\_Read | Loading GeoJSON/Shapefiles of sites and boundaries. | GDAL Wrapper |
| **Conversion** | ST\_GeomFromGeoJSON | Parsing raw API responses into binary geometry. | Native (DuckDB) |
| **Predicates** | ST\_Intersects | Determining if a tale point is inside a Gaeltacht polygon. | GEOS Library |
| **Analysis** | ST\_Buffer | Creating a "catchment area" around a collector's home. | GEOS Library |
| **Export** | COPY... TO | Generating filtered GeoJSON for web maps. | GDAL Wrapper |

#### **Works cited**

1. Gaelic Algorithmic Research Group – Rannsachadh digiteach air a' Ghàidhlig \- Blogs \- The University of Edinburgh, accessed December 7, 2025, [https://blogs.ed.ac.uk/garg/](https://blogs.ed.ac.uk/garg/)  
2. Seoladh Canúint.ie | Gaois research group, accessed December 7, 2025, [https://www.gaois.ie/en/blog/seoladh-canuint-ie](https://www.gaois.ie/en/blog/seoladh-canuint-ie)  
3. Decoding Hidden Heritages in Gaelic Traditional Narrative with Text-Mining and Phylogenetics, accessed December 7, 2025, [https://www.hiddenheritages.ai/en/about/dhh](https://www.hiddenheritages.ai/en/about/dhh)  
4. Taisce Chanúintí na Gaeilge, accessed December 7, 2025, [https://www.canuint.ie/ga/](https://www.canuint.ie/ga/)  
5. gaois repositories \- GitHub, accessed December 7, 2025, [https://github.com/orgs/gaois/repositories](https://github.com/orgs/gaois/repositories)  
6. Gaois \- GitHub, accessed December 7, 2025, [https://github.com/gaois](https://github.com/gaois)  
7. Gaois.Localizer | docs.gaois.ie, accessed December 7, 2025, [https://docs.gaois.ie/en/software/localizer](https://docs.gaois.ie/en/software/localizer)  
8. Leaflet vs OpenLayers: Pros and Cons of Both Libraries | Geoapify, accessed December 7, 2025, [https://www.geoapify.com/leaflet-vs-openlayers/](https://www.geoapify.com/leaflet-vs-openlayers/)  
9. A digital language | Dublin City University \- DCU, accessed December 7, 2025, [https://www.dcu.ie/blog/2056/digital-language](https://www.dcu.ie/blog/2056/digital-language)  
10. Two new collections digitsed and available on dúchas.ie: Acetate disc recordings and photographs \- Gaois, accessed December 7, 2025, [https://www.gaois.ie/en/blog/abhar-fuaime-agus-grianghraif-digitithe](https://www.gaois.ie/en/blog/abhar-fuaime-agus-grianghraif-digitithe)  
11. Decoding Hidden Heritages in Gaelic Traditional Narrative with Text-Mining and Phylogenetics | Gaois research group, accessed December 7, 2025, [https://www.gaois.ie/en/about/decoding-hidden-heritages](https://www.gaois.ie/en/about/decoding-hidden-heritages)  
12. wlamb – Gaelic Algorithmic Research Group \- Blogs, accessed December 7, 2025, [https://blogs.ed.ac.uk/garg/author/wlamb/](https://blogs.ed.ac.uk/garg/author/wlamb/)  
13. The version I know: phylogenetic analysis for the Decoding Hidden Heritages project \- Gaois, accessed December 7, 2025, [https://www.gaois.ie/en/blog/dhh-the-version-i-know](https://www.gaois.ie/en/blog/dhh-the-version-i-know)  
14. Handwritten Text Recognition (HTR) for Irish-Language Folklore \- LREC, accessed December 7, 2025, [http://www.lrec-conf.org/proceedings/lrec2022/workshops/CLTW4/pdf/2022.cltw4-1.17.pdf](http://www.lrec-conf.org/proceedings/lrec2022/workshops/CLTW4/pdf/2022.cltw4-1.17.pdf)  
15. Dúchas Application Programming Interface (Version 0.6) \- Gaois Documentation, accessed December 7, 2025, [https://docs.gaois.ie/en/data/duchas/v0.6/api](https://docs.gaois.ie/en/data/duchas/v0.6/api)  
16. Spatial Joins in DuckDB, accessed December 7, 2025, [https://duckdb.org/2025/08/08/spatial-joins](https://duckdb.org/2025/08/08/spatial-joins)  
17. land cover datasets: Topics by Science.gov, accessed December 7, 2025, [https://www.science.gov/topicpages/l/land+cover+datasets](https://www.science.gov/topicpages/l/land+cover+datasets)  
18. Logainmneacha Dhobhair agus Stair Áitiúil le Pádraig Mac Gairbheith \- Meitheal Logainm.ie, accessed December 7, 2025, [https://meitheal.logainm.ie/pdf/meitheal.logainm.ie-logainmneacha-dhobhair-agus-stair-aitiuil.pdf](https://meitheal.logainm.ie/pdf/meitheal.logainm.ie-logainmneacha-dhobhair-agus-stair-aitiuil.pdf)  
19. Leaflet \- a JavaScript library for interactive maps, accessed December 7, 2025, [https://leafletjs.com/](https://leafletjs.com/)  
20. Choosing OpenLayers or Leaflet? \[closed\] \- GIS Stack Exchange, accessed December 7, 2025, [https://gis.stackexchange.com/questions/33918/choosing-openlayers-or-leaflet](https://gis.stackexchange.com/questions/33918/choosing-openlayers-or-leaflet)  
21. A Beginner's Guide to Geospatial with DuckDB Spatial and MotherDuck, accessed December 7, 2025, [https://motherduck.com/blog/geospatial-for-beginner-duckdb-spatial-motherduck/](https://motherduck.com/blog/geospatial-for-beginner-duckdb-spatial-motherduck/)  
22. How to use DuckDB's ST\_Read function to read and convert zipped shapefiles \- Flother, accessed December 7, 2025, [https://www.flother.is/til/duckdb-st-read/](https://www.flother.is/til/duckdb-st-read/)  
23. Spatial Extension – DuckDB, accessed December 7, 2025, [https://aidoczh.com/duckdb/docs/archive/0.9/extensions/spatial.html](https://aidoczh.com/duckdb/docs/archive/0.9/extensions/spatial.html)  
24. Spatial Extension – DuckDB, accessed December 7, 2025, [https://duckdb.org/docs/stable/core\_extensions/spatial/overview](https://duckdb.org/docs/stable/core_extensions/spatial/overview)  
25. Extensions \- DuckDB, accessed December 7, 2025, [https://duckdb.org/docs/stable/extensions/overview](https://duckdb.org/docs/stable/extensions/overview)  
26. Spatial Extension – DuckDB \- AiDocZh, accessed December 7, 2025, [https://www.aidoczh.com/duckdb/docs/archive/1.0/extensions/spatial.html](https://www.aidoczh.com/duckdb/docs/archive/1.0/extensions/spatial.html)  
27. DuckDB constructing a full GeoJSON feature collection \- Stack Overflow, accessed December 7, 2025, [https://stackoverflow.com/questions/78832305/duckdb-constructing-a-full-geojson-feature-collection](https://stackoverflow.com/questions/78832305/duckdb-constructing-a-full-geojson-feature-collection)  
28. JSON Processing Functions \- DuckDB, accessed December 7, 2025, [https://duckdb.org/docs/stable/data/json/json\_functions](https://duckdb.org/docs/stable/data/json/json_functions)  
29. Spatial Functions \- DuckDB, accessed December 7, 2025, [https://duckdb.org/docs/stable/core\_extensions/spatial/functions](https://duckdb.org/docs/stable/core_extensions/spatial/functions)  
30. GDAL Integration \- DuckDB, accessed December 7, 2025, [https://duckdb.org/docs/stable/core\_extensions/spatial/gdal](https://duckdb.org/docs/stable/core_extensions/spatial/gdal)

## Extensions: pg_duckdb

> Source: `docs/data_engineering/duckdb/Extensions_ pg_duckdb.md`

---
title: "Extensions: pg_duckdb"
source: "https://planetscale.com/docs/postgres/extensions/pg_duckdb"
author:
  - "[[PlanetScale]]"
published:
created: 2025-12-22
description: "pg_duckdb is a Postgres extension that embeds DuckDB, a high-performance analytical database, directly into Postgres."
tags:
  - "clippings"
---
[Skip to main content](https://planetscale.com/docs/postgres/extensions/#content-area)

We don’t recommend running `pg_duckdb` directly on your PlanetScale Postgres database as it can consume significant resources during analytical queries. If you want to use DuckDB for analytics, we recommend using [MotherDuck](https://motherduck.com/) to host your analytical workloads separately.

## Dashboard Configuration

This extension requires activation via the PlanetScale dashboard before it can be used. It must be enabled through shared libraries and requires a database restart.To enable pg\_duckdb:

## Parameters

### duckdb.postgres\_role

- **Type**: String
- **Default**: `pscale_superuser`
- **Description**: Specifies the Postgres role that is allowed to use DuckDB execution and manage secrets.

### duckdb.memory\_limit

- **Type**: Integer
- **Default**: 0
- **Description**: Maximum memory DuckDB can use per connection in megabytes. Setting to 0 activates DuckDB’s default (80% of available RAM).

## Usage

After enabling the extension through the dashboard, you can install it in your database:Once installed, you can use DuckDB’s analytical capabilities directly from PostgreSQL. For example:

## External Documentation

For more detailed information about `pg_duckdb` usage and functionality, see the [official `pg_duckdb` documentation](https://github.com/duckdb/pg_duckdb).

Was this page helpful?

## Cloud: MotherDuck

> Source: `docs/data_engineering/duckdb/PlanetScale _ MotherDuck Docs.md`

---
title: "PlanetScale | MotherDuck Docs"
source: "https://motherduck.com/docs/integrations/databases/planetscale/"
author:
published:
created: 2025-12-24
description: "Connect PlanetScale Postgres to MotherDuck using pg_duckdb extension or the Postgres connector for analytical query acceleration"
tags:
  - "clippings"
---
PlanetScale offers hosted PostgreSQL and MySQL Vitess Databases. MotherDuck supports PlanetScale Postgres via the [pg\_duckdb extension](https://motherduck.com/docs/concepts/pgduckdb/), as well as the [Postgres Connector](https://motherduck.com/docs/integrations/databases/postgres/). In our internal benchmarking, pg\_duckdb offers 100x or greater query acceleration for analytical queries when compared to vanilla Postgres.

## Prerequisites

Before connecting PlanetScale to MotherDuck, ensure you have:

- A PlanetScale account with a Postgres database created
- The `pg_duckdb` extension enabled in your PlanetScale database (see [PlanetScale extension documentation](https://planetscale.com/docs/postgres/extensions/pg_duckdb))
- A MotherDuck account and authentication token (get your token from the [MotherDuck dashboard](https://app.motherduck.com/))
- Database connection credentials from your PlanetScale dashboard (host, port, username, password, database name)

## Connecting pg\_duckdb to MotherDuck

To run pg\_duckdb, make sure to add it your [extensions in PlanetScale](https://planetscale.com/docs/postgres/extensions/pg_duckdb).

```sql
-- Grant necessary permissions to the PlanetScale superuser
GRANT CREATE ON SCHEMA public to pscale_superuser;

-- Create the pg_duckdb extension in your Postgres database
CREATE EXTENSION pg_duckdb;

-- Enable a MotherDuck connection with your authentication token
CALL duckdb.enable_motherduck(<your token>);
```

To swap tokens, you can drop the MotherDuck connection and then re-add with:

```sql
-- Remove the existing MotherDuck server connection
DROP SERVER motherduck CASCADE;

-- Re-enable MotherDuck with a new authentication token
CALL duckdb.enable_motherduck(<your token>);
```

### Using Read Replicas with PlanetScale

Switching from read-write to read-only is done with the following SQL statement in Postgres:

```sql
-- Create a snapshot of your MotherDuck database to ensure consistency
SELECT * FROM duckdb.raw_query('CREATE SNAPSHOT OF <db_name>');

-- Drop the existing MotherDuck connection
DROP SERVER motherduck CASCADE;

-- Re-enable MotherDuck with your read-only token
CALL duckdb.enable_motherduck(<your read only token>);

-- Refresh the database to sync with the snapshot
SELECT * FROM duckdb.raw_query('REFRESH DATABASE <db_name>');
```

### Reading from MotherDuck

Once the catalog is in sync between MotherDuck and Postgres, the data can be queried directly from Postgres. If it is out of sync for any reason, it can be re-sync'd with the following SQL command:

```sql
-- Terminate the pg_duckdb sync worker to force a re-sync
SELECT * FROM pg_terminate_backend((
  SELECT pid FROM pg_stat_activity WHERE backend_type = 'pg_duckdb sync worker'
));
```

#### Sample MotherDuck Queries

Once the catalog is synchronized to Postgres, we can query the data as if it was normal data in Postgres.

```sql
-- Query data from a MotherDuck database and schema
-- Note: Non-main schemas use the ddb$database$schema naming convention
SELECT * 
FROM "ddb$sample_data$nyc".taxi
ORDER BY tpep_dropoff_datetime DESC 
LIMIT 10;
```

Of course, we can also join with data in Postgres.

```sql
-- Join MotherDuck data with local Postgres tables
SELECT a.col1, b.col2
-- MotherDuck table from a non-main schema
FROM "ddb$my_database$my_schema".my_table AS a
-- Local Postgres table in the public schema
LEFT JOIN public.another_table AS b on a.key = b.key
```

The DuckDB `iceberg_scan` function also works as well:

```sql
-- Use DuckDB's iceberg_scan function to query Iceberg tables
SELECT COUNT(*) 
FROM iceberg_scan('https://motherduck-demo.s3.amazonaws.com/iceberg/lineitem_iceberg', allow_moved_paths := true)
```
```sql
-- Use duckdb.query for SELECT queries that return tabular data
-- This example lists all databases in MotherDuck
SELECT * FROM duckdb.query('FROM md_databases()')
```
```sql
-- Use duckdb.raw_query for DDL queries that return void
-- This example drops a table in MotherDuck
SELECT * FROM duckdb.raw_query('DROP TABLE my_database.my_schema.some_table')
```

### Replicating data to MotherDuck

```sql
-- Create a table in MotherDuck and populate it with data from Postgres
-- Replace my_database and my_schema with your target database and schema names
CREATE TABLE "ddb$my_database$my_schema".my_table USING duckdb AS
SELECT * FROM public.my_table
```

The [pg\_duckdb github repo](https://github.com/duckdb/pg_duckdb) contains [further documentation](https://github.com/duckdb/pg_duckdb/blob/main/docs/README.md) of all available functions.

For ease of finding the documentation, a table of the documentation sections is below:

| Topic | Description |
| --- | --- |
| [**Functions**](https://github.com/duckdb/pg_duckdb/blob/main/docs/functions.md) | Complete reference for all available functions |
| [**Syntax Guide & Gotchas**](https://github.com/duckdb/pg_duckdb/blob/main/docs/gotchas_and_syntax.md) | Quick reference for common SQL patterns and things to know |
| [**Types**](https://github.com/duckdb/pg_duckdb/blob/main/docs/types.md) | Supported data types and type mappings |
| [**Extensions**](https://github.com/duckdb/pg_duckdb/blob/main/docs/extensions.md) | DuckDB extension installation and usage |
| [**Settings**](https://github.com/duckdb/pg_duckdb/blob/main/docs/settings.md) | Configuration options and parameters |
| [**Transactions**](https://github.com/duckdb/pg_duckdb/blob/main/docs/transactions.md) | Transaction behavior and limitations |

## Connecting with the Postgres Extension

You can also connect to PlanetScale Postgres with the DuckDB Postgres extension. This approach allows you to query PlanetScale data directly from DuckDB or MotherDuck.

### Install and Load the Extension

```sql
-- Install the Postgres extension from DuckDB's extension registry
INSTALL postgres;

-- Load the extension to enable Postgres connectivity
LOAD postgres;

-- Attach your PlanetScale database using a connection string
ATTACH '<connection string>' AS postgres_db (TYPE postgres);
```

### Connection String Format

The connection string format follows PostgreSQL's standard connection parameters. Here's an example with explanations:

```sql
ATTACH 'host=<host> port=<port> user=<user> password=<pw> dbname=<db> sslmode=require' 
    AS planetscale (TYPE postgres);
```

**Connection Parameters:**

- `host`: Your PlanetScale database hostname (found in your PlanetScale dashboard)
- `port`: The database port (typically 3306 for MySQL or 5432 for Postgres)
- `user`: Your PlanetScale database username
- `password`: Your PlanetScale database password
- `dbname`: The name of your database in PlanetScale
- `sslmode=require`: Ensures SSL encryption is used (required for PlanetScale)

## MotherDuck & PlanetScale Integration

> Source: `docs/data_engineering/duckdb/Using MotherDuck with PlanetScale — PlanetScale.md`

---
title: "Using MotherDuck with PlanetScale — PlanetScale"
source: "https://planetscale.com/blog/using-motherduck-with-planetscale"
author:
published: 2025-12-16
created: 2025-12-16
description: "Using MotherDuck with PlanetScale"
tags:
  - "clippings"
---
$50 Metal Postgres databases are here.[Learn more](https://planetscale.com/blog/50-dollar-planetscale-metal-is-ga-for-postgres)

[Blog](https://planetscale.com/blog) |

## Using MotherDuck with PlanetScale

By Ben Dicken |

DuckDB has gained significant traction for OLAP workloads.It's powerful, flexible, and has a feature-rich SQL dialect, making it perfect to use for analytics alongside OLTP-oriented relational databases.

Today, we're excited to announce support for the `pg_duckdb` extension for Postgres databases on PlanetScale alongside our partnership with MotherDuck.

## DuckDB in Postgres

DuckDB can be run as a standalone OLAP database, but also alongside Postgres via the [`pg_duckdb` extension](https://github.com/duckdb/pg_duckdb).The extension integrates DuckDB's column-store analytics engine right inside of Postgres, allowing you to seamlessly combine OLTP and OLAP queries over Postgres connections.

When enabled, tables can be created either using the standard Postgres table format *or* temporary tables in the DuckDB vectorized column format.Queries can then be selectively executed either using the Postgres engine or DuckDB.`pg_duckdb` can also be used to work with and query external datasources in popular formats like Apache Parquet and Iceberg.

Having DuckDB as a built-in extension makes data movement between Postgres and DuckDB formats simpler, and unifies the experience of combining analytics results with the rest of your relational data.

## MotherDuck

Though DuckDB is extremely powerful, many prefer to separate analytical compute from OLTP compute.This is useful to ensure that heavy analytics queries don't negatively impact application performance, and vice-versa.

MotherDuck is a cloud data warehouse with deep integration and support for DuckDB, and is a perfect solution to this problem.The `pg_duckdb` extension supports offloading analytics queries to the MotherDuck cloud.Analytics queries can be executed from within your PlanetScale Postgres database, but the analytics query execution can be offloaded to your data sets stored in the MotherDuck cloud.The results can then be returned to Postgres for further processing.

To use DuckDB and MotherDuck together with your PlanetScale database:

- Enable `pg_duckdb` via the "Extensions" table on the "Clusters" page of your database.

![Enable pg_duckdb](https://planetscale-images.imgix.net/assets/enable-duckdb-extension-DHkLGkML.png?auto=compress%2Cformat)

- Connect to your Postgres database and run `GRANT CREATE ON SCHEMA public to pscale_superuser;` to allow the addition of the MotherDuck catalog in Postgres and `CREATE EXTENSION pg_duckdb;` to create the extension.
- Add your MotherDuck token with `CALL duckdb.enable_motherduck('YOUR_TOKEN');`
- Start running your analytics queries!

Check out [our docs](https://planetscale.com/docs/postgres/extensions/pg_duckdb) and the [MotherDuck docs](https://motherduck.com/docs/concepts/pgduckdb/) for more information on how to use `pg_duckdb` with MotherDuck.

## Git-Inspired Data Workflow

> Source: `docs/data_engineering/duckdb/Branch, Test, Deploy_ A Git-Inspired Approach for Data - MotherDuck Blog.md`

---
title: "Branch, Test, Deploy: A Git-Inspired Approach for Data  - MotherDuck Blog"
source: "https://motherduck.com/blog/git-for-data-part-1/"
author:
  - "[[MotherDuck]]"
published: 2025-11-24
created: 2025-12-10
description: "This article explores how to bring Git style workflows like branching, testing, and deploying to your data stack. Learn how concepts like zero copy cloning and metadata pointers can finally give you isolated test environments."
tags:
  - "clippings"
---
Virtual Workshop: Build a Serverless Lakehouse with DuckLake [December 17, 10am PT / 1pm ET](https://luma.com/362ipnys?utm_source=eyebrow)

[GO BACK TO BLOG](https://motherduck.com/blog/)

## Branch, Test, Deploy: A Git-Inspired Approach for Data

2025/11/24 - 17 min read

BY

Remember the 2 AM on-call duty when a recent data pipeline broke the production environment? A data pipeline you've never touched just corrupted customer records. You need to roll back, fast. Or you want to test a new transformation on real production data before deployment, but recreating a production-like state in dev would take all day. Sounds familiar?

This is what a Git strategy for your data deployment promises to solve. This article explores using Git-like workflows for data, compares them to traditional Git, examines how data changes the workflow, assesses the current state of Git for data, and looks at key architectural concepts related to Git workflows in data.

The core challenge is universal across data teams: managing local, test, and production environments. Running large ETL jobs on prod data is expensive and time-consuming (anonymization, data prep, environment setup). But what if you could branch your data like you branch code? Test on real data, discard changes instantly, and deploy with confidence. That's the promise of Git for data, and let's find out if it can become a reality.

NOTE: Examine Tools in Part 2 There will be a part 2, where we look into the tools and implementations available such as LakeFS, Dolt, Nessie, MotherDuck's zero-copy clones, and more. But more importantly, we'll explore why you'd want this workflow in the first place and how it actually works in practice.

## Why Git for Data?

Besides the above two use cases—running prod data in dev or reverting production data if a pipeline accidentally deleted or changed something incorrectly—the main goal of Git for data is giving the data engineer peace of mind during production runs.

### The Problem We Have

When you have multiple stages in your data engineering architecture, from `stage -> core -> data marts`, potentially a cube on top, and multiple data pipelines running in parallel, the problem is rolling back an error consistently across the data stack.

How do we do that? We can't just revert one table, the sales table for example, because it will not work with all related customers, as they might have changed in the meantime, or the products, or their location, or gone out of business.

Data might be stored on a data lake, maybe on a database, or a key-value store like Redis. The data might be huge, containing the full CRM or all sales transactions over the last years. So the question is, how do we **revert or test things** consistently based on production-like data in terms of **both quality and size**?

That's where Git for data came from, and where tools such as LakeFS, Nessie, Bauplan and approaches like branching found a way to do it for a dedicated spot or across the stack.

### The Goal: What to Expect from a Git-like Workflow for Data?

We want to explore how Git can be integrated with data storage solutions like data lakes and databases to enable branching, cloning, and other Git-based functionality, which is what we already use for code in the realm of data engineering.

For this, we need to investigate how the full data stack, such as orchestration or transformation tools in the data workflow, can leverage Git-based versioning and branching. We need a strategy for scaling the Git-based data workflow to handle large production datasets without the extra work of copying or backup processes of existing databases + code + environment variables manually as we do today.

We want **Git for data management, similar to how it is used for code**, to facilitate deployment and testing. As we have the code packaged, we can package it into a Docker file and run it on that set of data.

Imagine if we could have Git management end-to-end on data analytics, a fully integrated Git workflow. If we only have the data, that already helps because then we can run a set of code. The end-to-end integration would be nice, but not the most important. Data is the hard part here. So if we are able to achieve that, we already win big by avoiding all the test cycles and CI/CDs we need to wait for or gain stability by quickly testing before deploying to production.

The hard part is scaling Git for data, especially in large-scale production environments where production data is really large. Copying this data and even adding some additional jobs with tests or setting up environments and integrations on top might take hours, or even the full night, if no errors occur.

Let's find out what existing tools in the market figured out and what efficient ways there are to scale Git for data without the downsides.

### Why not Plain "Git"?

Literally using Git doesn't work well for data. We get line-level conflict resolution (not cell-level). Git has no concept of schema. The files need to be sorted the same way to get useful diffs, and it has a 100MB GitHub file limit.

Git isn't made for data itself, but for small, text-based code changes. On top of that, in data work we differentiate between these two categories:

- Data pipeline versioning -> transformations or code
- Versioned databases -> the actual data

## Current State of Git for Data Work

Git for code is very well known, not so much Git for data. Let's explore the current state of Git for data.

### How Does Git Work?

To understand Git for data, we need to understand how branching with Git works, so we can apply it to data.

For example, Git branching holds all metadata and changes of the code from each state. This is handled through hashes. But Git is not made for data because it was designed with code versioning in mind, not large binary files or datasets. As Linus Torvalds himself [noted](https://www.youtube.com/watch?v=sCr_gb8rdEI), as the creator of Git, large files in Git were never part of the intended use case. The system's architecture of storing complete snapshots and computing hashes for everything works well for text-based code but becomes unwieldy with large data files. But as data practitioners, we actively want to work with data, with state, which is always harder than just code.

Git and Git-like solutions (alternatives are [Tangled](https://tangled.org/) and [Gitea](https://about.gitea.com/)) work. But which of these features do we want for data? And which specific ones do we need more compared to versioning code?

Git has concepts like versioning, rollback, diffs, lineage, branch/merge, and sharing. On the data side, which we get into more later, we have concepts such as files vs tables, structured vs unstructured, schema vs data, branching, and time travel.

For data, we need a storage layer or a way optimized for large data, schemas, and column types without necessarily duplicating the data. We also need to be able to revert the code and state easily. For example, revert the data pipelines that put production in an incorrect state.

If we look at [The Struggle of Enterprise Data Integration](https://airbyte.com/blog/modern-data-stack-struggle-of-enterprise-adoption), we can see that lots of what enterprises struggle with in data is change management and managing complexity. So hopefully, Git for data will help us with this?

### How Does It Work with Data?

Data works differently. We need an open way of sharing and moving data that we can then version, *branch* off to different versions easily, and roll back to older versions.

![image](https://motherduck.com/_next/image/?url=https%3A%2F%2Fmotherduck-com-web-prod.s3.us-east-1.amazonaws.com%2Fassets%2Fimg%2Fgit_image_1_ed936b4007.png&w=3840&q=75) Source: [Git for Data - What, How and Why Now?](https://lakefs.io/blog/git-for-data/)

Branching is the right word, also what Git is doing:

```
E---F---G  experiment-spark-3
                /
           C---D  dev-testing
          /
main  A---B---H---I  production
                 \
                  J---K  hotfix-corrupted-sales
```

We start with a version, and then diverge into different versions, and potentially merge back. **Merging** different branches is one option we **won't need for data compared to code**. With code, different features can be developed independently and then merged into the *main branch* at the end. With data, it's more about testing prod data on dev and then rolling out the code changes to prod, but not merging the "test" branch with the prod branch; otherwise we change, duplicate, or corrupt data.

The LakeFS solution (more on how it works later down) and its implemented Git-like features:![image](https://motherduck.com/_next/image/?url=https%3A%2F%2Fmotherduck-com-web-prod.s3.us-east-1.amazonaws.com%2Fassets%2Fimg%2Fgit_image_2_ae841f5f84.png&w=3840&q=75) Source: [Git for Data - What, How and Why Now?](https://lakefs.io/blog/git-for-data/)

[Tigris's new Fork](https://www.tigrisdata.com/blog/fork-buckets-like-code/) capabilities solve some of these challenges with *fractal snapshots*:

> You can instantly create an **isolated copy of your data** for development, testing, or experimentation. Have a **massive production dataset** you want to play with? You **don't need to wait for a full copy**. Just fork your source bucket, experiment freely, throw it away, and spin up a new one — instantly.
> 
> Their timelines diverge from the source bucket at the moment of the fork. It's the many-worlds version of object storage.

The key is that **every object is immutable**. Each write creates a new version, timestamped and preserved.

> That immutability allows Tigris to **version the entire bucket, and capture it as a single snapshot**.

![git-image-3.png](https://motherduck.com/_next/image/?url=https%3A%2F%2Fmotherduck-com-web-prod.s3.us-east-1.amazonaws.com%2Fassets%2Fimg%2Fgit_image_3_ea87a15566.png&w=3840&q=75)

This is interesting. Rather than single Delta or Iceberg tables, it versions the full bucket with the help of the versioning capabilities of these open table formats. Tigris says further, "Each object maintains its own version chain, and a **snapshot is an atomic cut across all those chains** at a specific moment in time."

A more comprehensive example with two different tables and different isolations that helps understand these processes in a data lake example with open table format tables stored on object storage:

![git-image-5.png](https://motherduck.com/_next/image/?url=https%3A%2F%2Fmotherduck-com-web-prod.s3.us-east-1.amazonaws.com%2Fassets%2Fimg%2Fgit_image_5_f0310a64b5.png&w=3840&q=75)

Important to know: a snapshot is an atomically consistent version across all those chains at a specific moment in time, and when retrieving a snapshot, Tigris, for example, returns the newest `version ≤ snapshot timestamp` of each table. For example, Snapshot `T3-dev` would contain Customer Table v4-dev and *only* Sales Table v5-dev (not v4-dev).

One technology used behind this is called [Prolly Tree](https://docs.dolthub.com/architecture/storage-engine/prolly-tree), also known as [Merkle Trees](https://en.wikipedia.org/wiki/Merkle_tree):Image from [Prolly Trees on Dolt Documentation](https://docs.dolthub.com/architecture/storage-engine/prolly-tree)

NOTE: In a way this is also how Software Engineers vs. Data Engineers work Software engineers need little to no data (data can also be replaced with having unpredictable, upstream events as a dependency), they can \*\*mock it easily (e.g. website)\*\* in dev, and in prod, they usually need big resources.

For data people, we have **hard dependencies on prod data**, usually **heavy compute in development**, lower compute in prod. SW engineers focus on the [SDLC (Software Development Lifecycle)](https://www.geeksforgeeks.org/software-engineering/software-development-life-cycle-sdlc/) and DE engineers need to focus on the data engineering lifecycle. There are many more differences. I wrote a little more on [Data Engineer vs. Software Engineer](https://www.ssp.sh/brain/data-engineer-vs-software-engineer).

### Data Movement Efficiency Spectrum

Before we get into the architectural decisions and the tools, let's *observe the data movements* when we implement Git for data, and let's categorize them by the amount of data movement required, ordered from most to least efficient:

**The most efficient approach uses metadata/catalog-based versioning**. Catalog pointers that just point to the same files multiple times (lakeFS and Iceberg are using this) create multiple logical versions of datasets without any physical duplication. No data movement involved.

**The next best approach is zero-copy or data virtualization technologies**. Tools like Apache Arrow enable data sharing between processes and systems without serialization overhead. You avoid the costly conversion between formats—no deserializing from source format to an intermediate representation and back again.

**When changes occur, delta-based approaches are the best way**. Rather than copying the entire dataset, you only store what has changed in new files. If you need to roll back, you simply revert the pointer to the previous file and state while keeping the changed files. This requires data management to manage changes.

**The least efficient but simplest approach is full 1:1 data copying.** Traditional methods like ODBC transfers, CSV exports, or database dumps require serializing data from the source format, moving it entirely, and deserializing it at the destination (e.g., from MS SQL to Pandas). But also, just creating a copy on S3 while keeping the same format is an expensive transaction, even more so with bigger datasets.

This works best for **small datasets** where the overhead doesn't matter, and offers the convenience of true isolation and easy rollback without complex change tracking.

We can say we work from `metadata → zero-copy → delta → full copy`. Let's investigate how lakeFS and other tools solved that problem and which approach they have chosen.

## Architecture: Key Technical Concepts

Now that we understand how data moves and its efficiency spectrum, let's look at how these approaches are **implemented in practice**. The architectural approaches can be categorized by implementation pattern:

1. **Environment-based versioning (traditional approach):** Typically uses **full copy** or **delta** from our efficiency spectrum.
	- Infrastructure-level: Kubernetes-based `dev/test/prod` environments with isolated data copies.
	- Application-level: Custom metadata tables, audit logs, or SCD (Slowly Changing Dimensions) patterns managing versions in the data warehouse.
2. **Zero-copy and virtualization approaches:** Leverage the **metadata/catalog** and **zero-copy** tiers, enabling logical versioning without physical data duplication.
	- Data virtualization (Dremio, Denodo, Starburst) queries sources on-demand without moving data.
	- Zero-copy cloning (MotherDuck, Snowflake, Azure Synapse) creates instant clones using metadata pointers.
	- In-memory sharing (Apache Arrow) enables process-to-process data sharing without serialization.
3. **Git-like data versioning tools:** Purpose-built tools operating at the **metadata/catalog tier** with **delta** capabilities for changes and connecting datasets in a connected way (with branching and Git-like functions).
	- **Data lake tools:** LakeFS, Project Nessie, Tigris work on object storage with open table formats (Iceberg, Delta Lake, Hudi) that have versioning built-in with time travel via `TIMESTAMP AS OF "2019-01-01"` or `VERSION AS OF 5238`.
	- **Database-native solutions:** Vary by efficiency—Supabase (branching), BigQuery (snapshots with 7-day time travel), MotherDuck (cloning, sharing), Databricks (Delta Lake integration), Dremio (Arctic catalog with Nessie). Note: Not all "cloning" is zero-copy—some create actual copies, others use copy-on-write, and the most efficient use pure metadata.
	- **Hybrid approaches:** Combine techniques like open table formats + lakeFS, or database cloning + scheduled snapshots for comprehensive version history.

Let's look at them in more detail and especially focus on the key techniques that **enable Git-like versioning**.

### Zero-Copy and Cloning

Zero-copying is important as we want fast creation of a new state. Zero-copying and cloning are the solution to that initial fast copy of an existing dataset. You can think of cloning a "production" database or lake.

Both zero-copy and cloning are related but not quite the same. For example, something can support cloning but it's NOT zero-copy (e.g., Dolt). It uses copy-on-write with structural sharing. We can say that the difference is:

- **Cloning** = *Can you create a copy?* (the capability)
- **Zero-copy** = *Does it duplicate data or just use metadata pointers?* (the implementation technique)

In the best case, we have both cloning and zero-copy: cloning production or a set of data without the need to duplicate the data, therefore zero-copy.

We can also borrow an analogy from Linux with a **Symlink**. You can have multiple pointers at different places pointing to the same file. You can read, open, and change, but the data is only stored once. Instead of moving data, we just create one new or many new pointers.

The result is creating new datasets instantly, as it's just a metadata process, and not an actual data transfer. We change the pointer **without moving data**.

Branching is implemented through **metadata catalogs**, systems that use pointers to track different versions of data without duplicating it, just like Git does. This is the most efficient way of versioning, as it's just a metadata process.

As mentioned above, this is the best way of versioning, as it's just a metadata process. Most modern tools implement this approach, though not all mean the same thing. Let's conceptually explore what we mean by branching data.

Branching is when you freeze the current state in an atomic and consistent way across multiple tables. Instead of focusing on one singular table, we do it for a full data warehouse layer or bucket.

[Snapshotting](https://www.kimballgroup.com/data-warehouse-business-intelligence-resources/kimball-techniques/dimensional-modeling-techniques/periodic-snapshot-fact-table/) is one of the approaches we use as part of our [Data Engineering Toolkit](https://motherduck.com/blog/data-engineering-toolkit-essential-tools/). Here we snapshot each table based on recurring date-time, e.g., every end of month. Because we do that for all tables in our data warehouse, it's also what I'd call the same approach we are doing with newer branching capabilities.

But generally, branching allows a snapshot or fork across tables and data assets. It can also be used to integrate a [Write-Audit-Publish (WAP)](https://lakefs.io/blog/data-engineering-patterns-write-audit-publish/) workflow, where you *write* into a temporary state, *audit* the quality and integrity of data, and only then *publish* (merge) it into production. This shows that branching solves the problem of **having consistency to test a certain feature in isolation** before merging all changes coherently, or none at all.

With additional features of merging (with some tools) or having a detailed commit log for what's happening, especially in combination with AI agents, this provides strong support to [steward](https://www.rilldata.com/blog/data-modeling-for-the-agentic-era-semantics-speed-and-stewardship) these autonomous agents and gatekeep and verify through humans.

#### Prolly Trees: A Data Structure for Efficient Branching

A great technical implementation of such an approach is Prolly Tree or Merkle Trees.

Prolly Trees are the technical foundation that makes Git-like versioning work for databases. Think of it as smart data chunking where data gets split into blocks using hash functions, and each block gets a unique fingerprint.

The key insight is that no matter how you modify data, **identical content always produces identical fingerprints**. This means when you change a row, only that specific chunk and its path to the root need updating, and everything else stays untouched and shared between versions.

This is exactly like how Git tracks changes in code, but optimized for tabular data. The result: diffing scales with what changed (a few rows), not dataset size (millions of rows), enabling instant branching and efficient storage across versions. This is what I found during research about Dolt.

### Hybrid Approaches

In reality, we often combine multiple techniques to get the best of all worlds. For example, you might use open table formats (Iceberg/Delta Lake) for their built-in time travel capabilities, layered with lakeFS for branch-based isolation across your entire data lake.

Or pair MotherDuck's zero-copy cloning with scheduled snapshots to create comprehensive version history beyond the default 7-day window. The key is matching your data versioning strategy (metadata, zero-copy, or delta) with your orchestration and transformation tools, supporting branch deployments that clone both code and data together for true isolated testing environments.

## Conclusion

We learned that Git for data is harder than version control for code because we're not just tracking changes but managing state, often at a massive scale. While Git revolutionized software development by making branching and merging trivial, the same would be helpful for data. Data, however, has the requirements that tables must remain consistent across relationships, that production datasets can span gigabytes and terabytes, and that copying data for testing is slow and often expensive.

The promise of Git-like workflows for data is to borrow Git-like concepts of branching, rollback, and isolated environments while addressing data's unique constraints. The key is leveraging metadata for zero-copy cloning and structural sharing through technologies like Prolly Trees, so we can create instant branches of production data without duplicating the actual data. The evolution we go through is from pure metadata pointers (most efficient) through delta-based changes to complete copies, which are simplest to work with but also the slowest. It's also the difference in provisioning speed: one can be ready in seconds, while the other takes hours, depending on the size of the data.

It's exciting how these capabilities can change the way we do data engineering. In Part 2, we'll explore tools like LakeFS, Nessie, Dolt, and others that are embracing these workflow changes and providing architectural implementations to this problem, each with different trade-offs around scale, integration, and operational complexity. We'll also check out how MotherDuck offers a handy solution for snapshotting that works really well with DuckDB and DuckLake.

I hope you gained good insight into the state of the art for Git workflows with data and how future data pipelines can benefit from such thinking and implementations, especially for testing and building more confidence in change management and, therefore, velocity in data engineering development cycles.

### TABLE OF CONTENTS

- [Why Git for Data?](https://motherduck.com/blog/git-for-data-part-1/#why-git-for-data)

- [Current State of Git for Data Work](https://motherduck.com/blog/git-for-data-part-1/#current-state-of-git-for-data-work)

- [Architecture: Key Technical Concepts](https://motherduck.com/blog/git-for-data-part-1/#architecture-key-technical-concepts)

- [Conclusion](https://motherduck.com/blog/git-for-data-part-1/#conclusion)

Start using MotherDuck now!

[Try 21 Days Free](https://motherduck.com/get-started/)

## PREVIOUS POSTS

[![Small Data SF 2025: the Recap!](https://motherduck.com/_next/image/?url=https%3A%2F%2Fmotherduck-com-web-prod.s3.us-east-1.amazonaws.com%2Fassets%2Fimg%2Fsmall_data_sf_2025_f373154984.png&w=3840&q=75)](https://motherduck.com/blog/small-data-sf-recap-2025/)

[![Unstructured Document Analysis with Tensorlake and MotherDuck](https://motherduck.com/_next/image/?url=https%3A%2F%2Fmotherduck-com-web-prod.s3.us-east-1.amazonaws.com%2Fassets%2Fimg%2Ftensorlake_15913398e1.png&w=3840&q=75)](https://motherduck.com/blog/unstructured-analysis-tensorlake-motherduck/)

[View all](https://motherduck.com/blog/)

## Original Sources

- `docs/data_engineering/duckdb/duckdb.md`
- `docs/data_engineering/duckdb/duckdb-comprehensive-research.md`
- `docs/data_engineering/duckdb/DuckDB - SQLMesh.md`
- `docs/data_engineering/duckdb/duckdb-spatial.md`
- `docs/data_engineering/duckdb/Geospatial Data Analysis and DuckDB.md`
- `docs/data_engineering/duckdb/Extensions_ pg_duckdb.md`
- `docs/data_engineering/duckdb/PlanetScale _ MotherDuck Docs.md`
- `docs/data_engineering/duckdb/Using MotherDuck with PlanetScale — PlanetScale.md`
- `docs/data_engineering/duckdb/Branch, Test, Deploy_ A Git-Inspired Approach for Data - MotherDuck Blog.md`

---
*Generated by MERGE_PLAN.md Phase 1 — 2026-06-06*
