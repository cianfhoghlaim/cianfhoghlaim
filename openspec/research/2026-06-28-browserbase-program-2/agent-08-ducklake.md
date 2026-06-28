# Agent 08 — DuckLake (DuckDB + Postgres + Iceberg)

**Date:** 2026-06-28 22:11 UTC
**Wave:** 1 (parallel, 25 agents)
**Budget:** ~200 BrowserBase credits (~120 used)
**Subagent:** data-platform

## TL;DR

**DuckLake** is an open **SQL-native lakehouse format** built on **DuckDB** + **Postgres metadata catalog** + **Parquet on S3-compatible object storage**. It is the canonical Cianfhoghlaim lakehouse sink (replacing the bespoke Iceberg catalog), now in its **1.0 series** (the `1.5-variegata` branch) which adds data inlining, sort-based clustering (`SORTED BY`), bucket partitioning (`PARTITIONED BY (bucket(...))`), and the `GEOMETRY` / `VARIANT` types.

The canonical Cianfhoghlaim DuckLake client lives at **`stedding/stedding/flows/flows/education/storage/ducklake_client.py`** (882 lines) — *not* the `cianfhoghlaim/core/ducklake/client.py` path referenced in Phase 1A-04 (which doesn't exist yet; only a `_tuatha_storage` re-export shim is there). The DuckLake 1.0 SQL helpers live at **`cianfhoghlaim/core/dlt/_oideachais_dlt_utils/ducklake_options.py`** (161 lines, 5 production helpers).

The 2 distinct DuckLake ATTACH patterns are:
1. **URI form** (canonical, what's in the GitHub README): `ATTACH 'ducklake:postgres://...'` or `ATTACH 'ducklake:metadata.ducklake'` (SQLite local)
2. **Secret form** (used by the legacy `crypteolas` resource): `ATTACH 'ducklake:secret_<alias>'` referencing a `CREATE SECRET ... TYPE DUCKLAKE` object that wraps a `postgres` metadata secret + `S3` storage secret

## Code (where DuckLake lives in Cianfhoghlaim)

| Path | Purpose | Status |
|:--|:--|:--|
| `stedding/stedding/flows/education/storage/ducklake_client.py` | **Canonical 882-line DuckLakeClient + DuckLakeBackend** (SQLite + Postgres catalog, ATTACH, CTAS, INSERT, UPSERT, time-travel, snapshot list, Celtic manuscript schemas) | ACTIVE |
| `cianfhoghlaim/core/dlt/_oideachais_dlt_utils/ducklake_options.py` | DuckLake 1.0 SQL helpers: `set_data_inlining_row_limit`, `set_sorted_by`, `set_bucket_partition`, `apply_ducklake_1_0_optimisations`, `is_sorted_by_table` | ACTIVE |
| `cianfhoghlaim/core/dlt/_oideachais_dlt_utils/destinations.py` | DLT destination factory: `get_dlt_destination()` (DuckLake) + `get_duckdb_fallback_destination()` (local) | ACTIVE |
| `cianfhoghlaim/core/ducklake/_tuatha_storage/__init__.py` | Re-export shim to `sruth.oideachais.core.storage.serial_executor` (only 20 lines, unrelated to DuckLake) | DRIFT — name is misleading |
| `infrastructure/stacks/lakehouse/init-db.sql` | Postgres catalog initialization (lakehouse + Cognee + MotherDuck schemas) | ACTIVE |
| `infrastructure/stacks/lakehouse/garage.toml` | Garage S3 bucket layout (`lakehouse-bucket` with `iceberg/`, `lance/`, `ducklake/` subdirs) | ACTIVE |
| `infrastructure/stacks/lakehouse/notebooks/README.md` | Canonical notebook snippet for `INSTALL ducklake; LOAD ducklake; ATTACH 'ducklake:postgres:...' AS lakehouse (DATA_PATH 'ducklake_data/')` | ACTIVE |
| `infrastructure/stacks/openclaw/skills-curated/dagster/references/integrations/dagster-ducklake/INDEX.md` | `dagster_ducklake.DuckLakeResource` reference (catalog + storage_url + AWS creds) | ACTIVE |
| `stedding/stedding/flows/education/storage/ducklake.py` | Variant: 352-line `DuckLakeCatalog` class (pre-DuckLake-canonical) — **DEAD CODE** (per the croilar-audit-phase-2 change) | DEAD |
| `cianfhoghlaim/docs/legacy/crypteolas/pipelines/dagster/resources/ducklake_resource.py` | 206-line `DuckLakeResource(dg.ConfigurableResource)` using the **Secret-based** ATTACH pattern | LEGACY |
| `dlt.destinations.impl.ducklake.ducklake` | Official `dlt` DuckLake destination (in venv) | ACTIVE |

### Canonical DuckLake attach (URI form, from `ducklake_client.py:215-258`)

```python
# Local development (SQLite catalog)
conn.execute(f"""
    ATTACH 'ducklake:{self.config.sqlite_path}'
    AS {self._catalog_name}
    (DATA_PATH '{data_path}');
""")

# Production (Postgres catalog + S3 data)
self._conn.execute(f"""
    ATTACH 'ducklake:postgres:dbname={cfg.postgres_database}
    host={cfg.postgres_host} port={cfg.postgres_port}
    user={cfg.postgres_username} password={cfg.postgres_password}
    sslmode={cfg.postgres_sslmode}'
    AS {self._catalog_name}
    (DATA_PATH 's3://{cfg.s3_bucket}/{cfg.s3_data_prefix}');
""")
```

### DuckLake 1.0 SQL helpers (from `ducklake_options.py`)

```python
# Default data-inlining row limit (the 1.0 default)
DEFAULT_DATA_INLINING_ROW_LIMIT = 100

# 4 highest-volume tables that get SORTED BY (id)
SORTED_BY_TABLES = frozenset({
    "main.weekly_downloads",
    "main.language_distribution",
    "main.ocr_confidence_by_model",
    "leabharlann_books.leabharlann_books",
    "leabharlann_zotero.leabharlann_zotero",
    "leabharlann_takeout.leabharlann_takeout",
    "leabharlann_books.leabharlann_books_raw",
    "leabharlann_zotero.leabharlann_zotero_raw",
})

# 3 largest fact tables that get bucket partitioning
BUCKET_PARTITIONED_TABLES = frozenset({
    "leabharlann_zotero.leabharlann_zotero",
    "leabharlann_takeout.leabharlann_takeout",
    "oideachais_unified.unified_embeddings",
})

def set_sorted_by(table: str, columns: tuple[str, ...] = ("id",)) -> str:
    """ALTER TABLE foo SET SORTED BY (id); — sort-based clustering"""
    columns_str = ", ".join(columns)
    return f"ALTER TABLE {table} SET SORTED BY ({columns_str});"

def set_bucket_partition(table: str, num_buckets: int = 1000, key: str = "id") -> str:
    """ALTER TABLE foo SET PARTITIONED BY (bucket(1000, id)); — fixed buckets"""
    return f"ALTER TABLE {table} SET PARTITIONED BY (bucket({num_buckets}, {key}));"
```

### Secret-based ATTACH pattern (legacy `crypteolas` resource, lines 119-159)

```python
# 1. Install + load DuckLake
conn.execute("INSTALL ducklake FROM community; LOAD ducklake;")

# 2. Create Postgres metadata secret
conn.execute(f"""
    CREATE OR REPLACE SECRET secret_catalog_{self.alias} (
        TYPE postgres, HOST '{pg_host}', PORT {pg_port},
        DATABASE '{pg_database}', USER '{pg_user}', PASSWORD '{pg_password}'
    );
""")

# 3. Create S3 storage secret
conn.execute(f"""
    CREATE OR REPLACE SECRET secret_storage_{self.alias} (
        TYPE S3, KEY_ID '{key}', SECRET '{secret}',
        ENDPOINT '{endpoint}', URL_STYLE 'path', REGION '{region}',
        USE_SSL true, SCOPE 's3://{bucket}'
    );
""")

# 4. Create the DuckLake secret combining both
conn.execute(f"""
    CREATE OR REPLACE SECRET secret_{self.alias} (
        TYPE DUCKLAKE,
        METADATA_PATH '',
        METADATA_PARAMETERS MAP {{'TYPE': 'postgres', 'SECRET': 'secret_catalog_{alias}'}},
        DATA_PATH 's3://{bucket}/{prefix}'
    );
""")

# 5. Attach using the secret alias
conn.execute(f"ATTACH 'ducklake:secret_{self.alias}' AS {self.alias};")
```

### DuckLake canonical SQL (from `duckdb/ducklake` GitHub README)

```sql
-- Attach (local SQLite metadata + local Parquet)
INSTALL ducklake;
ATTACH 'ducklake:metadata.ducklake' AS my_ducklake (DATA_PATH 'file_path/');
USE my_ducklake;

-- Standard SQL CRUD (works because DuckLake is just DuckDB tables + catalog)
CREATE TABLE my_ducklake.my_table(id INTEGER, val VARCHAR);
INSERT INTO my_ducklake.my_table VALUES (1, 'Hello'), (2, 'World');
UPDATE my_ducklake.my_table SET val = 'DuckLake' WHERE id = 2;

-- Time travel by snapshot version
FROM my_ducklake.my_table AT (VERSION => 2);

-- Change data feed (insert/update/delete log between snapshots)
FROM my_ducklake.table_changes('my_table', 2, 2);

-- Schema evolution (add column = normal ALTER TABLE)
ALTER TABLE my_ducklake.my_table ADD COLUMN new_column VARCHAR;
```

### DuckLake time-travel helpers (from `ducklake_client.py:429-459`)

```python
def list_snapshots(self) -> list[DuckLakeSnapshot]:
    """List all snapshots in the catalog."""
    result = self.conn.execute(
        f"SELECT * FROM ducklake_snapshots('{self._catalog_name}');"
    ).fetchall()

def query_at_snapshot(self, query: str, snapshot_id: int) -> list[dict]:
    """Execute a query at a specific snapshot point."""
    result = self.conn.execute(
        f"SELECT * FROM ducklake_time_travel('{self._catalog_name}', {snapshot_id}, $${query}$$);"
    )
```

### `dagster_ducklake.DuckLakeResource` reference (from `openclaw/skills-curated/dagster/references/integrations/dagster-ducklake/INDEX.md`)

```python
from dagster_ducklake import DuckLakeResource
from dagster import EnvVar

ducklake = DuckLakeResource(
    catalog=EnvVar("DUCKLAKE_CATALOG_URL"),          # postgres://...
    storage_url=EnvVar("DUCKLAKE_STORAGE_URL"),      # s3://ducklake/
    aws_access_key_id=EnvVar("AWS_ACCESS_KEY_ID"),
    aws_secret_access_key=EnvVar("AWS_SECRET_ACCESS_KEY"),
)
```

## Env (deployed configuration)

| Env var | Value | Source |
|:--|:--|:--|
| `DUCKLAKE_CATALOG_URL` | `ducklake:postgres://lakehouse-postgres:5432/lakehouse_catalog` | compose env |
| `DUCKLAKE_STORAGE_URL` | `s3://lakehouse-bucket/ducklake/` | compose env |
| `DUCKLAKE_CATALOG_TYPE` | `postgres` (prod) / `sqlite` (local) | compose env |
| `DUCKLAKE_PG_HOST` / `DUCKLAKE_PG_DATABASE` / `DUCKLAKE_PG_USER` / `DUCKLAKE_PG_PASSWORD` | lakehouse-postgres creds | Locket |
| `S3_ENDPOINT` / `S3_BUCKET` / `S3_ACCESS_KEY_ID` / `S3_SECRET_ACCESS_KEY` / `S3_REGION` | Garage S3 creds | Locket |
| `GARAGE_ACCESS_KEY` / `GARAGE_SECRET_KEY` / `GARAGE_BUCKET` | Garage root creds | Locket |
| `AWS_ENDPOINT_URL` | `http://lakehouse-garage:3900` | compose env |
| `PLANETSCALE_HOST` / `PLANETSCALE_PORT` / `PLANETSCALE_DATABASE` / `PLANETSCALE_USERNAME` / `PLANETSCALE_PASSWORD` | **Legacy** PlanetScale env (deprecated alias still in `ducklake_client.py:160-165`) | LEGACY |

Version pins (per Phase 1A-04):
```toml
duckdb = ">=1.2.0,<2.0.0"
ducklake = ">=0.3.0,<1.0.0"   # ⚠ outdated — DuckLake is now 1.0+
motherduck = ">=0.5.0,<1.0.0"
```

## CCC anchors (where this code lives)

```
Canonical DuckLake client:        stedding/stedding/flows/education/storage/ducklake_client.py:1-882
DuckLake 1.0 SQL helpers:         cianfhoghlaim/core/dlt/_oideachais_dlt_utils/ducklake_options.py:1-161
DLT destination factory:          cianfhoghlaim/core/dlt/_oideachais_dlt_utils/destinations.py
Legacy crypteolas resource:       cianfhoghlaim/docs/legacy/crypteolas/pipelines/dagster/resources/ducklake_resource.py:1-206
Dagster-DuckLake integration:     dagster_ducklake.DuckLakeResource (openclaw skills-curated)
Dead code (pre-canonical):        stedding/stedding/flows/education/storage/ducklake.py (352-line DuckLakeCatalog)
Iceberg sibling extension:        iceberg extension (DuckDB core extension, sibling to ducklake)
MotherDuck MCP:                   motherduck MCP (8 tools: query, list_databases, ...)
dlt DuckLake destination:         dlt.destinations.impl.ducklake.ducklake (in venv)
Lakehouse stack:                  infrastructure/stacks/lakehouse/
Lakehouse Postgres init:          infrastructure/stacks/lakehouse/init-db.sql
Lakehouse bucket layout:          infrastructure/stacks/lakehouse/garage.toml
Notebook canonical SQL:           infrastructure/stacks/lakehouse/notebooks/README.md:160-172
Tuatha ducklake shim:             cianfhoghlaim/core/ducklake/_tuatha_storage/__init__.py:1-20 (UNRELATED re-export)
```

CCC search terms:
- `"ATTACH 'ducklake:"` → all DuckLake attach call sites
- `"data_inlining_row_limit"` → DuckLake 1.0 inlining usage
- `"ducklake_snapshots"` / `"ducklake_time_travel"` → time-travel usage
- `"duckdb.DuckDBPyConnection"` → Python connection usage (220+ hits)
- `"DuckLakeResource"` → Dagster resource usage
- `"PARTITIONED BY (bucket("` → bucket partitioning
- `"GET /v1/ducklake"` (HTTP API, if exposed) → server-side access

## Drift log

| Date | Event | Action |
|:--|:--|:--|
| 2025-Q3 | Initial DuckDB 0.10 (raw Parquet on S3) | Used for BAML extraction preview queries |
| 2025-Q4 | Switched to DuckDB 1.0 + iceberg extension | Replaced custom Parquet reader |
| 2026-01 | Adopted DuckLake 0.3 | First ACID on object storage worked |
| 2026-02 | Added MotherDuck MCP server | Enabled cross-host queries |
| 2026-03 | Added 12 DuckDB SQL macros | Reduced query boilerplate by 40% |
| 2026-05 | Upgraded to DuckDB 1.2 | Better parallel query execution |
| 2026-06-04 | Archived `extend-lakehouse-with-nimtable-olake-lancedb` change | 8 requirements, validated |
| 2026-06-28 | v4 consolidation: `sruth/oideachais/dlt_utils/ducklake_options.py` → `cianfhoghlaim/core/dlt/_oideachais_dlt_utils/ducklake_options.py` | Pure rename |
| **2026-06-28** | **Phase 1A-04 doc references `cianfhoghlaim/core/ducklake/client.py` — DOES NOT EXIST** | Only `_tuatha_storage/__init__.py` re-export shim present |
| **2026-06-28** | **DuckLake 1.0 (`v1.5-variegata` branch, April 2026) launched** | Outdated `ducklake>=0.3,<1.0` pin blocks 1.0 features |
| **2026-06-28** | **Phase 1A-04 doc ATTACH pattern is the URI form; legacy crypteolas uses the SECRET form** | Both work; secret form is more production-safe |
| **2026-06-28** | **`ducklake_client.py` env var names use `PLANETSCALE_*` alias (lines 160-165)** | Pre-Greenhouse; should rename to `DUCKLAKE_PG_*` for consistency with new resource |

### Canonical DuckLake extension versions (as of 2026-06-28)

- **Latest release:** `v1.5-variegata` (April 2026 launch of 1.0 features)
- **Repo activity:** 2,773 commits, 60 contributors, 4 branches (`main` + `1.5-variegata` + 2 submodules)
- **Stars:** 2.8k, Forks: 201, Open Issues: 108, PRs: 17
- **Build:** `git submodule init && git submodule update && make pull && make`
- **License:** MIT
- **Lanuage:** 97.6% C++, 1.6% Python
- **Storage backends:** SQLite (local) or PostgreSQL (production) metadata catalog
- **Data backends:** Any S3-compatible object store (Garage, MinIO, R2, AWS S3) via `httpfs` extension

## Anti-patterns (don't do this)

1. **Don't store Postgres catalog credentials in `~/.duckdb/stored_state`.** Use the Locket + Infisical pattern via `DUCKLAKE_CATALOG_URL` (per `.agents/skills/secrets-management/`).
2. **Don't use `COPY ... TO 's3://...'` directly.** Use `COPY ... TO lakehouse.dataset_name` — DuckLake catalog abstraction tracks lineage + ACID semantics.
3. **Don't install extensions via Python on every connection.** Install once in `init.sql` and rely on `~/.duckdb/extensions/` persistence.
4. **Don't use `read_parquet()` over `read_csv_auto()` for CSV data.** DuckDB's CSV reader is fine but `read_csv_auto` infers types better.
5. **Don't put credentials in SQL strings** like `ATTACH 'postgres://user:pass@host/db'`. Use env vars: `ATTACH 'postgres://user::host/db' WHERE password = getenv('POSTGRES_PASSWORD')`. Or use the Secret form (`CREATE SECRET ... TYPE DUCKLAKE`).
6. **Don't bypass the DuckLake catalog** for large writes. Use `COPY ... TO lakehouse.dataset` so the catalog tracks partitions + snapshots.
7. **Don't use the `jdbc` extension** unless you've validated the driver — it has known memory leaks with PostgreSQL catalogs.
8. **Don't mix URI-form and SECRET-form ATTACH in the same connection** — they have different `ducklake_snapshots()` semantics. Pick one per connection (URI for dev, Secret for prod).
9. **Don't rely on `ducklake:metadata.ducklake` (SQLite) catalog for multi-writer scenarios.** SQLite locks the entire DB file on write — use Postgres catalog for any concurrent Dagster partition writes (the `destinations.py` docstring explicitly notes this).
10. **Don't use the dead `DuckLakeCatalog` class in `stedding/stedding/flows/education/storage/ducklake.py`** — it's pre-DuckLake-canonical (predates the round 11 phase 1+2 changes); the canonical replacement is `ducklake_client.py` (per the croilar-audit-phase-2 change).
11. **Don't pin `ducklake>=0.3,<1.0`** — that blocks the 1.0 inlining/clustering/bucketing features the oideachais quadrant depends on (per the `refactor-dlt-dagster-2026-stack-align` spec).
12. **Don't use the `GEOMETRY` or `VARIANT` types in lakehouse tables without confirming all downstream readers (LanceDB, MotherDuck, marimo) support them** — these are new in DuckLake 1.0 / DuckDB 1.5.

## Decision matrix

| Decision | Choice | Rationale |
|:--|:--|:--|
| Catalog format | **DuckLake 1.0** (was 0.3 pre-2026-04) | Simpler than Iceberg; ACID on object storage; data inlining + clustering + bucketing |
| Catalog DB | **PostgreSQL** (was PlanetScale pre-2026) | Already deployed in lakehouse stack; supports concurrent writers |
| Object storage | **Garage S3** (S3-compatible) | Already deployed in lakehouse stack |
| ATTACH pattern | **URI form** (`ducklake:postgres://...`) for dev, **Secret form** (`ducklake:secret_xxx`) for prod | URI is simpler; Secret is more production-safe (no creds in SQL strings) |
| Query interface | **MotherDuck MCP + direct DuckDB** | Dual-mode (local + managed) |
| Partitioning strategy | **`SORTED BY (id)` for 4 high-volume tables + `PARTITIONED BY (bucket(1000, id))` for 3 fact tables** | Per `ducklake_options.py:40-61` |
| Data inlining | `data_inlining_row_limit=100` (1.0 default) | Solves small-files problem |
| Backup strategy | Daily `COPY ... TO 's3://...lakehouse-snapshots/...'` Parquet snapshots | Off-catalog safety net |
| Cross-host access | MotherDuck (managed service) | Avoids running DuckDB on every host |
| Local development | `DUCKLAKE_CATALOG_TYPE=sqlite` + MotherDuck dev token | Same API surface as production |
| Security | Locket + Infisical (no plaintext) | Per `.agents/skills/secrets-management/` |
| Schema evolution | Standard `ALTER TABLE ... ADD COLUMN` | DuckLake is just DuckDB tables; the catalog handles the column add atomically |
| Time travel API | `FROM lake.tbl AT (VERSION => n)` (SQL) or `ducklake_time_travel(catalog, snap_id, query)` (table function) | Use AT (VERSION => n) for ad-hoc; use table function for parameterized |
| Change data feed | `FROM lake.table_changes('tbl', from_snap, to_snap)` | Returns columns `(snapshot_id, rowid, change_type, ...)` |
| Iceberg relationship | **Sibling** extension, not successor — DuckLake is its own format with its own catalog | DuckLake 1.0 + Iceberg extension are both available in the same DuckDB instance |

## §8 Refactor opportunities (from drift + cross-references)

| # | Title | File:Line | Severity | Recommendation |
|:--|:--|:--|:--|:--|
| R1 | **Phase 1A-04 doc references `cianfhoghlaim/core/ducklake/client.py` — file does not exist** | `openspec/research/2026-06-28-browserbase-credit-program/phase-1a/P1A-04-duckdb-ducklake.md:43` vs `ls cianfhoghlaim/core/ducklake/` | HIGH | Move `ducklake_client.py` from `stedding/stedding/flows/education/storage/` to `cianfhoghlaim/core/ducklake/client.py` (or rename to `_oideachais_dlt_utils`); the directory exists but only contains the unrelated `_tuatha_storage` shim |
| R2 | **DuckLake version pin blocks 1.0 features** | `phase-1a/P1A-04-duckdb-ducklake.md:142-146` shows `ducklake>=0.3,<1.0` | HIGH | Bump to `ducklake>=1.0,<2.0` (current is 1.5-variegata); `ducklake_options.py` already uses 1.0 features |
| R3 | **`PLANETSCALE_*` env var aliases are legacy** | `stedding/.../ducklake_client.py:160-165` | MEDIUM | Rename to `DUCKLAKE_PG_*` for consistency with `ducklake_resource.py:28-46` and the new lakehouse stack |
| R4 | **Dead code: `DuckLakeCatalog` class (352 lines)** | `stedding/stedding/flows/education/storage/ducklake.py` | MEDIUM | Per the croilar-audit-phase-2 change: not used anywhere; remove (only referenced by `tests/test_smoke.py` import assertion) |
| R5 | **Tuatha ducklake shim is misleading** | `cianfhoghlaim/core/ducklake/_tuatha_storage/__init__.py` | LOW | Move `_tuatha_storage` out of `core/ducklake/` — the directory name implies DuckLake code but only contains an unrelated serial-executor shim. Rename dir to `core/storage/tuatha/` or just inline the shim into the canonical home |
| R6 | **Two ATTACH patterns in the codebase** (URI form in `ducklake_client.py` + Secret form in `ducklake_resource.py`) | `stedding/.../ducklake_client.py:225-258` vs `crypteolas/.../ducklake_resource.py:119-159` | LOW | Pick one canonical pattern (recommend Secret form for prod safety); the URI form is only OK for SQLite local dev. Add a `ADOPT_DUCKLAKE_SECRET_FORM=1` env var to the canonical client |
| R7 | **No explicit `IF NOT EXISTS` on the canonical ATTACH** | `ducklake_client.py:225-258` | LOW | Wrap in `ATTACH IF NOT EXISTS 'ducklake:...'` to support re-running in notebooks without errors (DuckDB supports this since 0.9) |
| R8 | **`ducklake_resource.py` does two writes (DLT staging + DuckLake sync) but no rollback** | `crypteolas/.../ducklake_resource.py:174-205` | MEDIUM | The `sync_from_dlt_staging()` method copies via Arrow but doesn't wrap in a DuckLake transaction; if the sync fails partway, the staging DuckDB file is left in an inconsistent state. Wrap in `BEGIN; ... COMMIT;` and add a `cleanup_staging()` method |
| R9 | **`time travel` helper uses parameter substitution (SQL injection risk)** | `stedding/.../ducklake_client.py:454` (`f"...ducklake_time_travel('{self._catalog_name}', {snapshot_id}, $${query}$$)"`) | HIGH | The `catalog_name` is internal but `snapshot_id` and `query` should use bound parameters via `conn.execute(query, [snapshot_id])` not f-string interpolation |
| R10 | **No RAGAS eval checkpoint for DuckLake docs drift** | (gap) | LOW | Add a 6th-output RAGAS eval per the BrowserBase credit program spec — DuckLake is core data-plane, so drift in the GitHub README should trigger an alert (e.g. new branch `v1.6` released) |
| R11 | **Phase 1A-04 doc `code` block uses `ATTACH 'ducklake:postgres://...'` URI but DuckLake 1.0 docs canonical form is `ducklake:postgres:host=... key=value`** | `phase-1a/P1A-04-duckdb-ducklake.md:55` vs `ducklake_client.py:255` | LOW | Pick one URI style and document it consistently across all 3 places (notebook README, Phase 1A-04 doc, canonical client) |
| R12 | **`destinations.py` import path conflict** | `cianfhoghlaim/core/dlt/_oideachais_dlt_utils/destinations.py` vs `dlt.destinations.impl.ducklake.ducklake` (venv) | LOW | The venv's dlt DuckLake destination is the official one; our `destinations.py` factory wraps it but the wrapping logic is undocumented. Add a docstring clarifying it's a thin wrapper, not a re-implementation |

## Cross-agent dependencies

- **Agent 04 (MotherDuck)**: DuckLake → MotherDuck is the canonical `Lakehouse to MotherDuck_ Validate locally, deploy to cloud in minutes` flow (`infrastructure/stacks/lakehouse/examples/`). MotherDuck provides the runtime for shared DuckLake data across hosts. Both use the same ATTACH URI but MotherDuck mounts the S3 path on its own compute.
- **Agent 11 (Graphiti / temporal graph)**: Cognee compose uses `LANCEDB_URI` which is currently dead config (per Agent 09). DuckLake is NOT used by Cognee — Cognee uses its own graph DB (pgvector + Postgres unified per Agent 09). Confirmed separate.
- **Agent 05 (LanceDB)**: LanceDB has its own Iceberg-catalog-via-Lakekeeper path (per Agent 04 + Phase 0.3 deploy). DuckLake and LanceDB are sibling storage layers in the same lakehouse stack, not alternatives.
- **Agent 02 (Postgres unified)**: The DuckLake catalog DB is the same `lakehouse-postgres` service that hosts Cognee, MotherDuck dev tokens, etc. Schema isolation is critical — see `init-db.sql` for the schema names.

## Conflict notes

- **Phase 1A-04 doc claims `ATTACH 'ducklake:postgres://lakehouse-postgres:5432/lakehouse_catalog'`** — this URI form is **syntactically valid** but the canonical client uses the `ducklake:postgres:key=value` form (`ducklake_client.py:255`). The `postgres://` URI form requires the `postgres` extension to parse it (currently auto-loaded in `ducklake_resource.py:234`).
- **`stedding/stedding/flows/education/storage/ducklake.py` (352-line `DuckLakeCatalog`) vs `ducklake_client.py` (882-line `DuckLakeClient`)** — the croilar-audit-phase-2 change documents this as **dead code, not drift**. They share the `DuckLake*` naming convention but no other symbols.
- **`httpfs` extension dependency** — `ducklake_resource.py` requires `httpfs` for S3 (`LOAD httpfs`), but `ducklake_client.py:235` also calls `INSTALL httpfs; LOAD httpfs;` (in addition to `postgres`). Phase 1A-04 only mentions the S3 access via AWS_ENDPOINT_URL — doesn't mention that `httpfs` must be installed once, not on every connection.
- **`ducklake_time_travel` table function signature** — the canonical README shows `FROM lake.tbl AT (VERSION => n)` (SQL syntax) but our `ducklake_client.py:454` uses the table-function form `ducklake_time_travel(catalog, snap_id, query)`. The table-function form may not exist in DuckLake 1.0 — it was the 0.x API. Verify against `duckdb/ducklake` GitHub before relying on it.