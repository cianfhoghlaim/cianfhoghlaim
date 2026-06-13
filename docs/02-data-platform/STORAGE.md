---
title: 'Storage Pattern (DuckDB, LanceDB, DuckLake)'
domain: 'data_platform'
status: 'stable'
description: 'Pattern reference for DuckDB (single-threaded) + LanceDB (MVCC) + DuckLake (write substrate). For the one-liner mental model see docs/02-data-platform/storage-mental-model.md.'
read_when:
  - writing any storage code
  - debugging a database segfault
updated: '2026-06-13'
supersedes:
  - docs/STORAGE.md
truth: sole
ccc_query_hints:
  - storage pattern duckdb lancedb ducklake
  - serial database executor
  - duckdb single threaded
---

# Pattern: Storage (DuckDB, LanceDB, DuckLake)

## Critical Constraints

| Constraint | Description | Violation Consequence |
|---|---|---|
| **DuckDB: SINGLE_THREADED_ONLY** | Never access DuckDB concurrently | Segfault, data corruption |
| **LanceDB: MVCC safe** | Multi-process safe, single-threaded within process | Use `SerialDatabaseExecutor` |
| **HNSW indexes: DROP before bulk insert** | Drop index for >50 rows | 20× slower inserts, timeouts |
| **DuckLake: zero-copy registration** | Register Parquet files, do not copy data | Wasted storage, slow ingestion |
| **Snapshots before mutations** | Always snapshot before data changes | No time-travel recovery |

> **One-liner mental model:**
> - **Writes** go to DuckLake (Parquet on Garage S3, Postgres catalog).
> - **Reads** (marimo, SPA, public) go through MotherDuck (`md:oideachais`).
> - **Long-tail catalogue** lives in Apache Iceberg via Lakekeeper (not written to today).
> - See [`docs/02-data-platform/storage-mental-model.md`](storage-mental-model.md) for the full picture.

## DuckDB Patterns

### Pattern 1: `SerialDatabaseExecutor` (MANDATORY)

**When to use**: ALL DuckDB operations in multi-threaded/async applications.

**Implementation**:
```python
import threading
from concurrent.futures import ThreadPoolExecutor
from typing import Callable, TypeVar

T = TypeVar("T")

class SerialDatabaseExecutor:
    def __init__(self, max_workers: int = 1):
        self._executor = ThreadPoolExecutor(max_workers=max_workers)
        self._lock = threading.Lock()

    def run(self, fn: Callable[..., T], *args, **kwargs) -> T:
        with self._lock:
            future = self._executor.submit(fn, *args, **kwargs)
            return future.result()

# WRONG: direct concurrent access
# conn1.execute("SELECT * FROM table")
# conn2.execute("INSERT INTO table")
```

**Where it lives**:
- `oideachais/storage/serial_executor.py` (runtime impl)
- Tests: `oideachais/tests/conftest.py::serial_executor`

### Pattern 2: Connection scope (per-operation)

```python
with duckdb.connect(db_path) as conn:
    conn.execute("SELECT * FROM table")
# Connection closed automatically
```

**Anti-pattern**: keeping a long-lived DuckDB connection across
function boundaries in async code.

## LanceDB Patterns

### Pattern 1: `merge_insert` for idempotency

```python
# CORRECT: idempotent write, conflicts resolved via MVCC
table.merge_insert("id") \
    .when_matched_update_all() \
    .when_not_matched_insert_all() \
    .execute(rows)

# WRONG: plain add() on a duplicate id
table.add(row)  # creates a duplicate, not idempotent
```

### Pattern 2: Drop HNSW before bulk insert

```python
index_name = "vector_idx"
if len(rows_to_insert) > 50:
    table.drop_index(index_name)
table.add(rows_to_insert)
if dropped:
    table.create_index(num_partitions=..., num_sub_vectors=...)
```

## DuckLake Patterns

### Pattern 1: Destination factory (the only entry point)

**Never** instantiate `dlt.destinations.ducklake` directly. Use the
factory in `oideachais/dlt_utils/destinations.py`:

```python
from oideachais.dlt_utils import get_dlt_destination

dest = get_dlt_destination()  # local: Garage S3; prod: Cloudflare R2
```

### Pattern 2: Local dev vs prod

| Env | Storage | Catalog |
|---|---|---|
| Local (`DLT_ENVIRONMENT=local`) | `s3://ducklake/oideachais/` (Garage, port 3900) | Postgres at `localhost:5433` |
| Prod (`DLT_ENVIRONMENT=production`) | `s3://r2.ducklake/oideachais/` (Cloudflare R2) | PlanetScale Postgres |

Both write the same `oideachais.{domain}.{nation}` schema.

### Pattern 3: DuckLakeCredentials in dlt 1.x

```python
from dlt.destinations.impl.ducklake.configuration import DuckLakeCredentials

credentials = DuckLakeCredentials(
    ducklake_name="oideachais",
    catalog="postgresql://lakekeeper:devpassword@localhost:5433/ducklake_oideachais",
    storage={
        "bucket_url": "s3://ducklake/oideachais/",
        "credentials": {"aws_access_key_id": "...", "aws_secret_access_key": "..."},
    },
)
```

> **Note:** the `DuckLakeCredentials` constructor kwargs changed in
> dlt 1.x. If you're on a newer dlt release, re-run the
> `oideachais/tests/dlt_utils/test_destinations.py` smoke test to
> confirm the kwargs match.

## MotherDuck Patterns

### Pattern 1: Read-side attach

```python
import duckdb

con = duckdb.connect(":memory:")
con.execute("INSTALL motherduck; LOAD motherduck;")
con.execute("ATTACH 'md:oideachais' (TYPE MOTHERDUCK);")
con.execute("USE oideachais;")

rows = con.execute(
    "SELECT * FROM oideachais.education.ie.ncca_pages LIMIT 10"
).fetchall()
```

In CI, the `MOTHERDUCK_TOKEN` env var (hydrated by mise + Infisical)
authenticates the attach.

## See also

- [`docs/02-data-platform/storage-mental-model.md`](storage-mental-model.md) — one-liner
- [`docs/02-data-platform/data-architecture.md`](data-architecture.md) — full lakehouse architecture
- [`docs/02-data-platform/dagster-orchestration.md`](dagster-orchestration.md) — Dagster + storage
- [`docs/02-data-platform/dlt-pipelines.md`](dlt-pipelines.md) — DLT patterns
- [`docs/00-core/CONSTRAINTS.md`](../00-core/CONSTRAINTS.md) — the constraint checklist
