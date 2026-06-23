---
name: oideachais-storage
description: KCG storage mental model + Critical Constraints. Writes → DuckLake (Parquet on Garage S3, Postgres catalog). Reads → MotherDuck (`md:oideachais`). Long-tail catalogue → Apache Iceberg via Lakekeeper. Change-watching → ChangeDetection.io on `arm1-oci`. Use when writing any storage code, debugging segfaults, onboarding an analyst, or choosing the right destination for a new pipeline.
---

# Oideachais Storage

## When to use this skill

Use when you need to:

- "Choose the right destination for a new DLT pipeline"
- "Debug a segfault or memory corruption (DuckDB
  single-threaded!)"
- "Onboard a new analyst (MotherDuck read access)"
- "Wire the destination factory for a new stack"
- "Decide between Garage S3, R2, or local dev for storage"
- "Implement a merge_insert for idempotency"

## One-line mental model

- **Writes** → DuckLake (Parquet on Garage S3, Postgres catalog,
  Iceberg-compatible via Lakekeeper)
- **Reads** → MotherDuck (`md:oideachais`, managed DuckDB in the
  Cloud)
- **Long-tail catalogue** → Apache Iceberg via Lakekeeper (for
  PyIceberg / Spark / Trino access)
- **Change-watching** → ChangeDetection.io on `arm1-oci`
  (URL-level diffing for sources without sitemaps)

## Critical Constraints (with violation consequences)

| Constraint | Violation | Consequence |
|:--|:--|:--|
| DuckDB is **single-threaded** | Concurrent access from multiple processes | **Segfault** or silent corruption |
| LanceDB is **MVCC-safe** with `SerialDatabaseExecutor` | Use raw `lancedb.connect()` without the executor | Lost writes, phantom reads |
| Embeddings: **batch minimum 100** | Embed < 100 texts per call | 20× slower (per-call setup cost) |
| HNSW: **drop above 50k rows** | Bulk insert with HNSW index active | Hours (vs minutes without) |
| DuckLake: **zero-copy** | Materialise Parquet in Python | Wasted storage, lost ACID |

## The 4 layers

### 1. DuckLake (write substrate)

- **Storage backend**: Parquet on Garage S3 (dev: port 3900,
  prod: Hetzner Object Storage)
- **Catalog**: Postgres (`md:oideachais` as the metadata DB)
- **Schema convention**: `oideachais.{domain}.{nation}`
- **Writers**: Dagster assets in `oideachais/dagster_defs/assets/`
  and `tuatha/dagster_assets/`
- **Why DuckLake**: ACID transactions + time-travel queries +
  zero-copy Parquet + Iceberg metadata for downstream PyIceberg
  / Spark / Trino consumers

```python
import duckdb
con = duckdb.connect()
con.execute("INSTALL ducklake FROM core_nightly; LOAD ducklake;")
con.execute("""
    CREATE SECRET r2_secret (
        TYPE R2, KEY_ID '...', SECRET '...', ACCOUNT_ID '...'
    )
""")
con.execute("""
    ATTACH 'ducklake:md:oideachais' AS oideachais (
        TYPE ducklake, SECRET r2_secret, CATALOG postgres_catalog
    )
""")
```

### 2. MotherDuck (read substrate)

- **Endpoint**: `md:oideachais` (MotherDuck database)
- **Auth**: `MOTHERDUCK_TOKEN` env var (from mise/Infisical)
- **Use case**: analyst marimo notebooks, BI dashboards
- **Why separate from writes**: MotherDuck is **read-only**
  (no DML); DuckLake is the **write** substrate. The split
  enforces the read-after-write semantics without risking
  MotherDuck corruption

```python
import duckdb
con = duckdb.connect("md:oideachais")
df = con.execute(
    "SELECT subject, COUNT(*) AS n FROM education.ie.curriculum GROUP BY subject"
).df()
```

### 3. Apache Iceberg via Lakekeeper (long-tail catalogue)

- **Endpoint**: `https://lakekeeper.cianfhoghlaim.ie/catalog`
- **Auth**: OIDC via Pocket ID
- **Use case**: PyIceberg / Spark / Trino / Dremio access to
  the same data
- **Pattern**: DuckLake writes Parquet with Iceberg metadata
  (via Lakekeeper) — the same data is queryable from both
  DuckDB and PyIceberg

```python
from pyiceberg.catalog import load_catalog
catalog = load_catalog(
    "kcg",
    type="rest",
    uri="https://lakekeeper.cianfhoghlaim.ie/catalog",
    token=os.environ["LAKEKEEPER_TOKEN"],
)
table = catalog.load_table("oideachais.education.ie.curriculum")
df = table.scan().to_pandas()
```

### 4. ChangeDetection.io (change-watching)

- **Endpoint**: `https://changedetection.cianfhoghlaim.ie`
- **Use case**: URL-level diffing for sources without sitemaps
- **Pattern**: `sources.yaml` pairs each URL with a Dagster
  asset key; a webhook fires a `RunRequest` on change
- **Why not firecrawl `changeTracking`**: no history, costs
  credits, misses content outside the structured output

## DuckDB Patterns (KCG-specific)

### SerialDatabaseExecutor (with `_lock`)

The KCG variant of `lancedb.connections.SerialDatabaseExecutor`:

```python
# oideachais/storage/serial_executor.py
import threading
from contextlib import contextmanager


class SerialDatabaseExecutor:
    """Non-negotiable wrapper for all DuckDB access in
    multi-threaded / async code. Without this, DuckDB segfaults.
    """

    def __init__(self, db_path=":memory:"):
        self.db_path = db_path
        self._lock = threading.RLock()  # RLock for re-entrancy

    @contextmanager
    def connection(self):
        with self._lock:
            conn = duckdb.connect(self.db_path)
            try:
                yield conn
            finally:
                conn.close()
```

**Usage**:

```python
executor = SerialDatabaseExecutor("/data/oideachais.duckdb")

# Threaded access — safe
with executor.connection() as con:
    con.execute("SELECT * FROM oideachais.education.ie.curriculum LIMIT 10")
```

### Connection scope (per-operation)

- **Per-request**: new connection (avoids connection-state
  leaks across requests)
- **Per-thread**: reuse connection within a request
- **Per-process**: a singleton connection (use only with
  SerialDatabaseExecutor + a single thread)

For Dagster assets: per-request.
For FastAPI: per-request.
For marimo: per-process (singleton notebook).

## LanceDB Patterns (KCG-specific)

### merge_insert for idempotency

```python
table.merge_insert(
    "id"
).when_matched_update_all().when_not_matched_insert_all().execute(
    rows
)
```

Use for any incremental ingestion (DLT sources, BAML
extractions). Idempotent: re-running the same input
produces the same state.

### Drop HNSW before bulk insert > 50k rows

```python
# See embedding-pipeline skill for the managed_bulk_insert
# context manager.
with managed_bulk_insert(table, drop_threshold=50_000) as t:
    t.add(rows)
```

The HNSW rebuild above 50k rows is **slow** (> 1 hour for
1M rows). Drop first, then rebuild.

## DuckLake Patterns (KCG-specific)

### Destination factory (the single entry point)

```python
# oideachais/dlt_utils/destinations.py
import dlt
import os


def get_dlt_destination(
    dataset_name: str = "oideachais",
    storage: str = "garage",  # "garage" | "r2" | "local"
):
    """The single entry point for DLT destinations.

    Returns the configured dlt.Destination for the KCG stack.
    """
    if storage == "garage":
        return dlt.destinations.filesystem(
            bucket_url=os.environ["GARAGE_BUCKET_URL"],
        )
    elif storage == "r2":
        return dlt.destinations.filesystem(
            bucket_url=os.environ["R2_BUCKET_URL"],
        )
    elif storage == "local":
        return dlt.destinations.duckdb(
            database=os.path.expanduser("~/oideachais.duckdb"),
        )
    else:
        raise ValueError(f"Unknown storage: {storage}")
```

**Usage** (in a DLT source):

```python
pipeline = dlt.pipeline(
    pipeline_name="ireland_curriculum",
    destination=get_dlt_destination("oideachais", storage="garage"),
    dataset_name="oideachais.education.ie",
)
```

### Local dev (Garage, port 3900) vs prod (R2)

| | Local dev | Prod |
|:--|:--|:--|
| **Object store** | Garage (Docker container) | Cloudflare R2 |
| **Endpoint** | `http://localhost:3900/oideachais` | `https://<account>.r2.cloudflarestorage.com/oideachais` |
| **Auth** | Local dev key | R2 access key (via Infisical) |
| **Size limit** | None (local) | 10 TB / month (R2 free tier) |

The dev Garage container is part of the
`infrastructure/stacks/garage/` Compose stack; runs
on port 3900.

### DuckLakeCredentials in dlt 1.x

In dlt 1.x, DuckLake is a first-class destination:

```python
pipeline = dlt.pipeline(
    pipeline_name="ireland_curriculum",
    destination=dlt.destinations.ducklake(
        catalog="postgres://...",
        storage="s3://oideachais/",
    ),
    dataset_name="oideachais.education.ie",
)
```

## MotherDuck Patterns (KCG-specific)

### Read-side attach

```python
import duckdb
con = duckdb.connect("md:oideachais")
```

The `md:oideachais` URL is the MotherDuck database name; the
`MOTHERDUCK_TOKEN` env var (from mise/Infisical) authenticates.

### Separation of concerns

| Concern | DuckLake | MotherDuck |
|:--|:--|:--|
| Schema definition | YES | mirror (read-only) |
| DML (INSERT, UPDATE) | YES | NO (read-only) |
| DQL (SELECT) | YES (slow) | YES (fast, managed) |
| DDL (CREATE TABLE) | YES | NO |
| Cost | S3 storage + compute | MotherDuck subscription |

## Cross-references

- `docs/02-data-platform/data-architecture.md` — the full
  lakehouse architecture (the source-of-truth doc; round 6
  deleted this; content absorbed into this skill)
- `.agents/skills/ducklake/SKILL.md` — upstream DuckLake
  reference (1013 lines; covers the upstream patterns)
- `.agents/skills/lancedb/SKILL.md` — upstream LanceDB
  reference (658 lines)
- `.agents/skills/cross-domain-registry/SKILL.md` — the
  `{nation}.{domain}.{entity}` asset-key contract
- `.agents/skills/oideachas-pipeline/SKILL.md` — the
  oideachais pipeline
- `.agents/skills/motherduck-ducklake/SKILL.md` — MotherDuck
  + DuckLake patterns
- `.agents/skills/embedding-pipeline/SKILL.md` — embedding
  pipeline (HNSW lifecycle)
- `.agents/skills/stack-ops/SKILL.md` — Garage stack
  (the dev-mode object store)
