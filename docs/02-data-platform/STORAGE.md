---
title: 'Storage Architecture & Patterns (DuckDB, LanceDB, DuckLake, MotherDuck)'
domain: 'data_platform'
status: 'stable'
description: 'Pattern reference for DuckDB (single-threaded) + LanceDB (MVCC) + DuckLake (write substrate) + MotherDuck (read substrate). The mental model is: writes go to DuckLake, reads go to MotherDuck, Iceberg is the long-tail catalogue. All KCG storage constraints, patterns, and runtime examples in one place.'
read_when:
  - writing any storage code
  - debugging a database segfault
  - deciding where a new asset reads from
  - onboarding a new analyst
updated: 2026-06-13
merged_from:
  - docs/02-data-platform/STORAGE.md
  - docs/02-data-platform/storage-mental-model.md
  - docs/02-data-platform/ducklake.md
truth: sole
ccc_query_hints:
  - storage pattern duckdb lancedb ducklake
  - storage mental model ducklake motherduck iceberg
  - serial database executor
  - duckdb single threaded
  - ducklake lakehouse garage s3
---

# Storage Architecture & Patterns (DuckDB, LanceDB, DuckLake, MotherDuck)

> **Merged from 3 sources**: `STORAGE.md` (pattern reference, 175 lines) + `storage-mental-model.md` (one-liner + three-layer overview, 119 lines) + `ducklake.md` (KCG-specific DuckLake brief, 52 lines). The originals are now `.superseded`.

## One-line mental model

> - **Writes** go to **DuckLake** (Parquet on Garage S3, Postgres catalog)
> - **Reads** (marimo, SPA, public) go to **MotherDuck** (`md:oideachais`)
> - **Long-tail catalogue** is **Apache Iceberg** via Lakekeeper (not written to today; exists for future parity)
> - **Change watching** is **ChangeDetection.io** at `infrastructure/stacks/tools/changedetection` and on `arm1-oci`

The full architecture is in [`data-architecture.md`](data-architecture.md). The constraint list is in [`../00-core/CONSTRAINTS.md`](../00-core/CONSTRAINTS.md).

---

## Critical Constraints

| Constraint | Description | Violation Consequence |
|---|---|---|
| **DuckDB: SINGLE_THREADED_ONLY** | Never access DuckDB concurrently | Segfault, data corruption |
| **LanceDB: MVCC safe** | Multi-process safe, single-threaded within process | Use `SerialDatabaseExecutor` |
| **HNSW indexes: DROP before bulk insert** | Drop index for >50 rows | 20× slower inserts, timeouts |
| **DuckLake: zero-copy registration** | Register Parquet files, do not copy data | Wasted storage, slow ingestion |
| **Snapshots before mutations** | Always snapshot before data changes | No time-travel recovery |

---

## Three layers

### 1. DuckLake (write substrate)

- **What**: SQL table format on Parquet files; ACID on object storage via a Postgres catalog.
- **Where it lives in this monorepo**:
  - `s3://ducklake/oideachais/{domain}/{nation}/{table}/*.parquet`
  - Catalog: Postgres at `localhost:5433` (local) or PlanetScale (prod)
  - Concrete code: `oideachais/dlt_utils/destinations.py:get_dlt_destination()`
- **Who writes**:
  - `oideachais/dagster_defs/assets/*` (the unified asset graph)
  - `oideachais/dlt_sources/domains/*` (the 43 registered sources)
  - `tuatha/dagster_assets/*` (tuath's curriculum-in-game assets)
- **Schema convention**: `oideachais.{domain}.{nation}` — e.g. `oideachais.education.ie.ncca_pages`. Each DLT run auto-creates the schema on first write.

#### Why DuckLake matters for KCG

DuckLake is the analytical backbone of the curriculum data platform. Every DLT ingestion pipeline writes Parquet files to Garage S3, and DuckLake registers them as versioned tables with time-travel capability. This means curriculum researchers can query "what did the syllabus look like before the 2023 reform?" without maintaining separate database snapshots. The Lance Namespace sidecar bridges DuckLake's SQL tables with LanceDB's vector indexes, enabling hybrid SQL+semantic search across the same curriculum data.

#### Key DuckLake features

- **ACID on S3** — Snapshot isolation, time travel, schema evolution via Iceberg
- **DuckDB-powered** — Same SQL engine, same extensions, same performance
- **Zero-copy branching** — Create branches of data without duplicating storage
- **Schema evolution** — Add/drop/rename columns without rewriting data
- **Garage S3 native** — Designed for self-hosted S3-compatible storage

#### Installation

```bash
uv add ducklake
```

#### Integration with the stack

DuckLake sits between Garage S3 (storage) and Lakekeeper (Iceberg catalog). Dagster jobs write to DuckLake tables; marimo notebooks query them; the Lance Namespace registers them as Iceberg tables for unified catalog discovery.

#### Upstream

- **Documentation**: Project-specific — built on DuckDB + Iceberg + Garage S3 integration
- **Latest**: Active development as part of the Kings' College Galway infrastructure
- **Screenshot**: DuckLake is a programmatic library with no UI. Query results appear in Dagster materialization logs, marimo notebook cells, and DuckDB's SQL shell. The Lakekeeper catalog UI (Nimtable) provides graphical table discovery for DuckLake-managed tables.

### 2. MotherDuck (read substrate)

- **What**: Managed DuckDB-compatible service; attaches a remote catalog over HTTPS. Used for analyst-facing reads.
- **Where it lives**:
  - `md:oideachais` (the canonical public database)
  - Concrete code: `oideachais/api/ducklake_reader.py` (the API reader)
- **Who reads**:
  - `oideachais/notebooks/dashboards/*` (marimo dashboards)
  - `oideachais/api/` (the SPA backend)
  - agents (ADK / AGNO via the motherduck MCP at `opencode.json`)
- **Why a separate read path**:
  - MotherDuck handles many concurrent readers (no single-threaded segfault risk on the read side).
  - Public analyst queries don't touch the local Postgres catalog.

### 3. Apache Iceberg via Lakekeeper (long-tail catalogue)

- **What**: Open-source Iceberg REST catalog. Stays in the stack on port 8181 (Lakekeeper) + 8182 (Lance Namespace sidecar).
- **Why we don't write to it today**:
  - DuckLake is sufficient for the current data volume.
  - Iceberg's value is cross-engine compatibility (Spark, Trino, Athena). We don't run those.
- **When it gets used** (future):
  - If we need a second query engine (e.g. Athena for public analytics).
  - If we need cross-region replication at the catalog level.
- **Concrete code**: `infrastructure/stacks/storage/lakehouse/` — the Lakekeeper + Lance Namespace sidecar running at 8181/8182.

### 4. ChangeDetection.io (change-watching)

- **What**: Stand-alone service that watches sitemaps and detects changes on public sources.
- **Where**:
  - Compose: `infrastructure/stacks/tools/changedetection/compose.yaml`
  - Deployed on: `arm1-oci` (the control-plane host)
  - Local checkout: `/Users/cianmacandeisigh/dev/kings_college_galway/infrastructure/stacks/tools/changedetection`
- **Why we use it** (vs firecrawl's `changeTracking`):
  - ChangeDetection.io is the canonical change-watcher for `oideachais/sources.yaml` — it has a UI, history, and webhooks.
  - It is one of the 88 stacks; it's already paid for in our infrastructure budget.
  - firecrawl's `changeTracking` is a single-shot endpoint; we don't get history without re-running.

---

## How the layers interact

```
                  ┌──────────────┐
   DLT sources ───▶│   DuckLake   │──┐
                  │  (writes)    │  │
                  └──────────────┘  │  ┌────────────┐
                                     ├─▶│ MotherDuck │
                  ┌──────────────┐  │  │  (reads)   │
   Sitemap sensors ┤ Lakehouse ┤──┘  └────────────┘
   ───▶ 8181/8182  │  (Iceberg) │
                  └──────────────┘
                          ▲
                          │ long-tail catalogue
                          │ (future)

   ChangeDetection.io ────▶ sitemap sensors
       (deployed on arm1-oci)
```

---

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

**Anti-pattern**: keeping a long-lived DuckDB connection across function boundaries in async code.

---

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

---

## DuckLake Patterns

### Pattern 1: Destination factory (the only entry point)

**Never** instantiate `dlt.destinations.ducklake` directly. Use the factory in `oideachais/dlt_utils/destinations.py`:

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

> **Note:** the `DuckLakeCredentials` constructor kwargs changed in dlt 1.x. If you're on a newer dlt release, re-run the `oideachais/tests/dlt_utils/test_destinations.py` smoke test to confirm the kwargs match.

---

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

In CI, the `MOTHERDUCK_TOKEN` env var (hydrated by mise + Infisical) authenticates the attach.

---

## See also

- [`data-architecture.md`](data-architecture.md) — full lakehouse architecture
- [`dagster.md`](dagster.md) — Dagster + storage
- [`dlt.md`](dlt.md) — DLT patterns
- [`../00-core/CONSTRAINTS.md`](../00-core/CONSTRAINTS.md) — the constraint checklist
- [`cross-domain-registry.md`](cross-domain-registry.md) — asset-key contract
- [`../01-platform-architecture/infrastructure-stacks.md`](../01-platform-architecture/infrastructure-stacks.md) — stack index
- [`../03-agents/change-detection.md`](../03-agents/change-detection.md) — sensor patterns
