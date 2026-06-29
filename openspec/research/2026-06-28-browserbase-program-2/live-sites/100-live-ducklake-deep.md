# Agent 100 — DuckLake Deep (Wave 2, live-ducklake-verifier)

**Date:** 2026-06-29 03:00 UTC
**Wave:** 2, Agent 100
**Subagent:** live-ducklake-verifier (deep research)
**Mode:** FIRECRAWL + CHROME MCP + webfetch (NO browserbase)
**Prior files:** `live-docs/87-live-ducklake-current.md` (Wave 1, 270 lines) and `agent-08-ducklake.md` (Wave 1, 320 lines)

> **⚠ Critical URL drift (Wave 1 → Wave 2):** The Wave 1 brief gave `https://ducklake.select.dev` and `/docs/stable/duckdb/usage/usage` + `/usage/options`. The **real** domain is **`https://ducklake.select`** (no `.dev`) — the `.dev` variant returns DNS NXDOMAIN. And the URL paths the Wave 1 brief used return **404**; the canonical Wave 2 paths are `/docs/stable/duckdb/introduction`, `/docs/stable/duckdb/usage/{snapshots,configuration,time_travel,connecting,choosing_a_catalog_database,choosing_storage,schema_evolution,upserting,paths}`, `/docs/stable/duckdb/maintenance/{recommended_maintenance,merge_adjacent_files,expire_snapshots,cleanup_of_files,rewrite_data_files,checkpoint}`, `/docs/stable/duckdb/advanced_features/{data_inlining,partitioning,transactions,data_change_feed,row_lineage,encryption,sorted_tables,…}`, plus the v1.0 release blog `/2026/04/13/ducklake-10/`.

## 1. TL;DR

- **DuckLake v1.0** shipped **2026-04-13** with the `ducklake` DuckDB extension on DuckDB v1.5.2 — production-ready, MIT licensed, stable spec (108 PRs since end of 2025).
- Architecture is **catalog DB (SQL) + Parquet on object storage**: any SQL-92 PK-supporting DB works (DuckDB, PostgreSQL, SQLite) for the catalog; any S3-compatible blob store (AWS S3, GCS, Azure, R2, MinIO, Garage) for data files.
- **Snapshots** are the unit of commit; every change is a snapshot, with `snapshots()`, `current_snapshot()`, `last_committed_snapshot()`, `AT (VERSION => n)`, `AT (TIMESTAMP => …)`, attach-time `SNAPSHOT_VERSION` / `SNAPSHOT_TIME`, and `ducklake_time_travel(catalog, snap_id, query)`.
- **Data inlining** (default since v1.0, row limit **10**, NOT 100 as Wave 1 claimed) eliminates the small-files problem; **sorted tables** via `SET SORTED BY` and **bucket partitioning** via `SET PARTITIONED BY (bucket(N, col))` are new v1.0.
- **18 production user logos** (Ascend.io, PostHog, Sliplane, Windmill, …) + **5 non-DuckDB clients** (DataFusion, Spark via MotherDuck, two Trino ports, Pandas) + an O'Reilly "DuckLake: The Definitive Guide" book in progress → much bigger adoption than the Wave 1 file implied.

## 2. Deep dive on DuckLake architecture, ATTACH syntax, snapshot model

### 2.1 The two-layer architecture (verbatim from `/2026/04/13/ducklake-10/`)

> "DuckLake is a lakehouse format, which allows you to store your data on object storage and access it as a database, similarly to Delta Lake with Unity Catalog and Iceberg with Lakekeeper. A key difference between other formats and DuckLake is that DuckLake stores all metadata in a database, which is commonly referred to as the catalog. This database can be any system that speaks SQL, supports primary keys and is able to persist data in tables."

> "We also developed an implementation of the specification using DuckDB as the engine, the DuckDB `ducklake` extension. This extension implements all of the specification and supports three main catalogs: SQLite, PostgreSQL and DuckDB (yes, DuckDB can be a catalog too)."

The six runtime surfaces are: (1) **DuckDB extension** (canonical, requires DuckDB v1.5.2+), (2) **DataFusion** (`datafusion-contrib/datafusion-ducklake`), (3) **Apache Spark** (`motherduckdb/ducklake-spark`), (4) **Trino** (two ports: `awitten1/trino-ducklake` + `brikk/ducklake-integrations/jvm/trino-ducklake`), (5) **Pandas** (`pdet/ducklake-dataframe`, "mostly produced by agentic coding" per the v1.0 blog), (6) **MotherDuck hosted DuckLake** (managed catalog + storage).

### 2.2 ATTACH syntax (verbatim from `https://ducklake.select/docs/stable/duckdb/usage/connecting`)

```sql
-- Local DuckDB catalog + local Parquet
INSTALL ducklake;
ATTACH 'ducklake:metadata.ducklake' AS my_ducklake (DATA_PATH 'data/');
USE my_ducklake;

-- PostgreSQL catalog (production)
INSTALL ducklake; INSTALL postgres;
ATTACH 'ducklake:postgres:dbname=ducklake_catalog host=your_postgres_host'
    AS my_ducklake (DATA_PATH 'data/');
USE my_ducklake;

-- SQLite catalog
INSTALL ducklake; INSTALL sqlite;
ATTACH 'ducklake:sqlite:metadata.sqlite' AS my_ducklake (DATA_PATH 'data/');
USE my_ducklake;

-- Read-only Frozen DuckLake over HTTPS (no credentials)
ATTACH 'https://blobs.duckdb.org/datalake/nl-railway.ducklake' AS nl_railway
    (TYPE ducklake);
USE nl_railway;
FROM services LIMIT 1;
```

Per-instance DATA_PATH is stored in `ducklake_metadata` so re-attach needs no DATA_PATH: `ATTACH 'ducklake:my_ducklake.ducklake' AS my_ducklake;`

### 2.3 Snapshot model (verbatim from `/docs/stable/duckdb/usage/snapshots`)

> "Snapshots represent commits made to DuckLake. Every snapshot performs a set of changes that alter the state of the database. Snapshots can create tables, insert or delete data, and alter schemas. Changes can only be made to DuckLake using snapshots. Every set of changes must be accompanied by a snapshot."

**`snapshots()` columns:** `snapshot_id`, `snapshot_time`, `schema_version`, `changes` (structured map: `{tables_created=[...]}`, `{inlined_insert=[1]}`), `author`, `commit_message`, `commit_extra_info`.

**Three snapshot-lookup functions:**
- `FROM my_ducklake.snapshots()` — full history
- `FROM my_ducklake.current_snapshot()` — head snapshot of THIS connection's view
- `FROM my_ducklake.last_committed_snapshot()` — head visible to the catalog (returns `NULL` from a connection that hasn't committed)

**Commit messages** (the audit-trail story) are transactional:

```sql
BEGIN;
INSERT INTO my_ducklake.people VALUES (1, 'pedro');
CALL my_ducklake.set_commit_message('Pedro', 'Inserting myself',
    extra_info => '{''foo'': 7, ''bar'': 10}');
COMMIT;
```

### 2.4 Time travel (verbatim from `/docs/stable/duckdb/usage/time_travel`)

> "In DuckLake, every snapshot represents a consistent state of the database. DuckLake keeps a record of all historic snapshots and their changesets, unless compaction is triggered and historic snapshots are explicitly deleted."

```sql
SELECT * FROM tbl AT (VERSION => 3);                              -- AT-clause version
SELECT * FROM tbl AT (TIMESTAMP => now() - INTERVAL '1 week');    -- AT-clause timestamp
ATTACH 'ducklake:metadata.duckdb' (SNAPSHOT_VERSION 3);           -- Attach-time version
ATTACH 'ducklake:metadata.duckdb' (SNAPSHOT_TIME '2025-05-26 00:00:00');  -- Attach-time time
```

## 3. Verbatim SQL examples (8 examples, all from live docs)

### 3.1 Full CRUD + Time Travel + Schema Evolution + Change Data Feed (GitHub README)

```sql
INSTALL ducklake;
ATTACH 'ducklake:metadata.ducklake' AS my_ducklake (DATA_PATH 'file_path/');
USE my_ducklake;
CREATE TABLE my_ducklake.my_table(id INTEGER, val VARCHAR);
INSERT INTO my_ducklake.my_table VALUES (1, 'Hello'), (2, 'World');
FROM my_ducklake.my_table;                                -- (1, Hello), (2, World)
UPDATE my_ducklake.my_table SET val='DuckLake' WHERE id=2;
FROM my_ducklake.my_table AT (VERSION => 2);               -- (1, Hello), (2, World)  [time-travel]
ALTER TABLE my_ducklake.my_table ADD COLUMN new_column VARCHAR;
FROM my_ducklake.table_changes('my_table', 2, 2);
-- snapshot_id | rowid | change_type | id | val
-- 2           | 0     | insert      | 1  | Hello
-- 2           | 1     | insert      | 2  | World
```

### 3.2 Inlining 4-step demo (v1.0 blog)

```sql
CREATE TABLE lake.t (id INT, status VARCHAR);
INSERT INTO lake.t VALUES (1, 'en route'), (2, 'shipped');
DELETE FROM lake.t WHERE id = 1;
UPDATE lake.t SET status = 'delivered' WHERE id = 2;
FROM ducklake_list_files('lake', 't');   -- returns empty
CHECKPOINT;                              -- flushes data to Parquet
```

### 3.3 Sorted tables + 3.4 Bucket partitioning (Iceberg-compatible murmur3)

```sql
-- 3.3 Sorted
CREATE TABLE lake.sorted_t (id INT, payload JSON);
ALTER TABLE lake.sorted_t SET SORTED BY (id ASC);
INSERT INTO lake.sorted_t VALUES (33, {'key': 'value'}), (2, {'key': 'value'}),
                                 (42, {'key': 'value'}), (1, {'key': 'value'});
CHECKPOINT; FROM lake.sorted_t;   -- reads from sorted file: min/max pruning hits

-- 3.4 Bucket partitioning
CALL lake.set_option('data_inlining_row_limit', 0);
CREATE TABLE lake.events (user_name VARCHAR, event_type VARCHAR, ts TIMESTAMP);
ALTER TABLE lake.events SET PARTITIONED BY (bucket(8, user_name));
EXPLAIN ANALYZE FROM lake.events WHERE user_name = 'alice';
```

### 3.5 GEOMETRY with bounding-box pushdown + 3.6 VARIANT with shredding (v1.0 blog)

```sql
-- 3.5 GEOMETRY (uses spatial extension, && operator is bounding-box overlap)
LOAD spatial;
CALL lake.set_option('data_inlining_row_limit', 0);
CREATE TABLE lake.places (name VARCHAR, location GEOMETRY);
INSERT INTO lake.places VALUES ('Amsterdam', ST_Point(4.9, 52.37));
SELECT name FROM lake.places
WHERE location && ST_GeomFromText('POLYGON((4 52,5 52,5 53,4 53,4 52))');

-- 3.6 VARIANT (shredded sub-fields → filter pushdown; only inlinable with DuckDB catalog)
CREATE TABLE lake.events (id INT, payload VARIANT);
INSERT INTO lake.events VALUES
    (1, {'user': 'alice', 'ts': TIMESTAMP '2024-01-01'}),
    (2, {'user': 'bob',   'ts': TIMESTAMP '2024-01-02', 'rand': 'value'});
SELECT * FROM lake.events WHERE payload.user = 'bob';
```

### 3.7 Deletion vectors (Iceberg V3 Puffin, experimental)

```sql
CREATE TABLE lake.t (id INTEGER);
CALL lake.set_option('write_deletion_vectors', true, table_name => 't');
INSERT INTO lake.t FROM range(100);
DELETE FROM lake.t WHERE id < 5;  -- writes Puffin file (roaring bitmap) instead of Parquet
```

### 3.8 Per-table scoped config + settings introspection (`/docs/stable/duckdb/usage/configuration`)

```sql
CALL my_ducklake.set_option('parquet_compression', 'zstd');                 -- global
CALL my_ducklake.set_option('parquet_compression', 'zstd', schema    => 'my_schema');
CALL my_ducklake.set_option('parquet_compression', 'zstd', table_name => 'my_table');
CALL my_ducklake.set_option('data_inlining_row_limit', 10, table_name => 't');
FROM my_ducklake.options();          -- all 23 options for the attached DuckLake
FROM my_ducklake.settings();         -- catalog_type, extension_version, data_path
-- or: FROM ducklake_settings('my_ducklake');
```

## 4. Live URL patterns

All canonical DuckLake pages (from `https://ducklake.select`):

- Homepage: <https://ducklake.select> | v1.0 blog: <https://ducklake.select/2026/04/13/ducklake-10/>
- DuckDB extension intro: <https://ducklake.select/docs/stable/duckdb/introduction>
- Usage: <https://ducklake.select/docs/stable/duckdb/usage/connecting> | <…/usage/snapshots> | <…/usage/time_travel> | <…/usage/configuration>
- Maintenance hub: <https://ducklake.select/docs/stable/duckdb/maintenance/recommended_maintenance> | <…/maintenance/checkpoint>
- Advanced: <https://ducklake.select/docs/stable/duckdb/advanced_features/data_inlining> | <…/advanced_features/partitioning>
- Spec intro: <https://ducklake.select/docs/stable/specification/introduction> | 28-table overview: <…/specification/tables/overview>
- FAQ: <https://ducklake.select/faq>
- GitHub: <https://github.com/duckdb/ducklake> (2.8k stars, 201 forks, 108 issues, 2,773 commits, **MIT**)
- Frozen DuckLake example: `https://blobs.duckdb.org/datalake/nl-railway.ducklake` (attached `TYPE ducklake`)
- Single-file docs: <https://blobs.duckdb.org/docs/ducklake-docs.md> / <…/ducklake-docs.pdf>

## 5. Maintenance operations & migration patterns

### 5.1 The 6-function `CHECKPOINT` (verbatim from `/docs/stable/duckdb/maintenance/checkpoint`)

> "DuckLake provides the option to implement all the maintenance functions bundled in the `CHECKPOINT` statement. This statement will run in order the following DuckLake functions: `ducklake_flush_inlined_data`, `ducklake_expire_snapshots`, `ducklake_merge_adjacent_files`, `ducklake_rewrite_data_files`, `ducklake_cleanup_old_files`, `ducklake_delete_orphaned_files`."

`CHECKPOINT` accepts four global options: `rewrite_delete_threshold` (0..1, default 0.95), `delete_older_than`, `expire_older_than`, `auto_compact` (default `true`).

### 5.2 Full maintenance surface (from `/docs/stable/duckdb/maintenance/recommended_maintenance`)

> "Most operations performed by DuckLake happen in the catalog database. As such, the maintenance of the metadata server are handled by the chosen catalog database. For example, when running PostgreSQL, it is likely sufficient to occasionally run VACUUM in order to ensure the system stays performant."

> "DuckLake also never deletes old data files. As old data remains accessible through time travel. Even when a table is dropped, the data files associated with that table are not deleted."

Recommended cadence: `merge_adjacent_files` after small-batch inserts (inlining off), `expire_snapshots` + `cleanup_old_files` after time-travel SLA drops, `rewrite_data_files` for heavy-deletes tables, `CHECKPOINT` as a one-shot catch-all.

### 5.3 Inlined data flush (verbatim from `/docs/stable/duckdb/advanced_features/data_inlining`)

```sql
CALL ducklake_flush_inlined_data('my_ducklake');                          -- everything
CALL ducklake_flush_inlined_data('my_ducklake', schema_name => 'my_schema');
CALL ducklake_flush_inlined_data('my_ducklake', table_name  => 'my_table');
CALL ducklake_flush_inlined_data('my_ducklake', schema_name => 'my_schema',
                                                 table_name  => 'my_table');
-- Returns: schema_name, table_name, rows_flushed (one row per flushed table)
```

`auto_compact=false` per-table means the table is skipped by `CHECKPOINT`'s flush step (but `auto_compact` does NOT auto-flush on every write — it only controls eligibility for explicit maintenance).

### 5.4 Migration: DuckDB → DuckLake

Standard pattern: `INSTALL ducklake;` → `ATTACH 'ducklake:' …` → for each existing DuckDB table, `CREATE TABLE lake.t AS SELECT * FROM main.t;` (writes the table to Parquet in the data path and registers it with the catalog in one snapshot). Full guide at `/docs/stable/duckdb/migrations/duckdb_to_ducklake`.

### 5.5 The 28 catalog tables (verbatim from spec sidebar)

`ducklake_metadata`, `ducklake_snapshot`, `ducklake_snapshot_changes`, `ducklake_schema`, `ducklake_schema_versions`, `ducklake_table`, `ducklake_table_stats`, `ducklake_table_column_stats`, `ducklake_column`, `ducklake_column_mapping`, `ducklake_column_tag`, `ducklake_data_file`, `ducklake_delete_file`, `ducklake_file_column_stats`, `ducklake_file_partition_value`, `ducklake_file_variant_stats`, `ducklake_files_scheduled_for_deletion`, `ducklake_inlined_data_tables`, `ducklake_macro`, `ducklake_macro_impl`, `ducklake_macro_parameters`, `ducklake_name_mapping`, `ducklake_partition_column`, `ducklake_partition_info`, `ducklake_sort_expression`, `ducklake_sort_info`, `ducklake_tag`, `ducklake_view` — all `ducklake_`-prefixed so they don't collide with user data.

## 6. Drift items vs Wave 1 (top 10 of 19)

| # | Wave 1 claim (WRONG/STALE) | Wave 2 truth (verified live) | Source |
|:--|:--|:--|:--|
| D1 | Domain `https://ducklake.select.dev` | **`https://ducklake.select`** (no `.dev`); `.dev` returns DNS NXDOMAIN | Chrome `net::ERR_NAME_NOT_RESOLVED` |
| D2 | URL paths `/docs/stable/duckdb/usage/usage` and `/usage/options` | **404 on both**; real pages are `/usage/snapshots`, `/usage/configuration`, `/usage/connecting`, `/usage/time_travel` | webfetch 404 |
| D3 | `data_inlining_row_limit=100` is the 1.0 default | **Default is `10`** in v1.0 (was off in 0.x; turned on with 10 in v1.0 PR #775) | `/advanced_features/data_inlining` + v1.0 blog |
| D4 | "GEOMETRY / VARIANT are new in 1.0" (mentioned) | Confirmed; **VARIANT can only inline when catalog is DuckDB** (Postgres/SQLite cannot round-trip the type) | v1.0 blog + inlining docs |
| D5 | "Two ATTACH patterns" (URI vs SECRET) was the recommendation | **The official v1.0 docs use URI form only**; the SECRET form (legacy `crypteolas` resource) is not in the live docs. **D6 should be downgraded to LEGACY** for v1.0-era. | Homepage + `/usage/connecting` |
| D6 | Not mentioned: **`set_commit_message` / `current_snapshot()` / `last_committed_snapshot()`** | All three are first-class v1.0 features; commit messages support author + commit_message + commit_extra_info JSONB | `/usage/snapshots` |
| D7 | Not mentioned: **`ducklake_settings()` / `my_ducklake.settings()`** | New table function in v1.0 PR #724 — returns `catalog_type`, `extension_version`, `data_path` | `/usage/configuration` + v1.0 blog appendix |
| D8 | Not mentioned: **5 first-class v1.0 options** (`hive_file_pattern=true` default, `target_file_size=512MB`, `parquet_row_group_size=122880`, `parquet_compression=snappy`, `require_commit_message`) + **3 extension `SET` options** (`ducklake_max_retry_count=10`, `ducklake_retry_backoff=1.5`, `ducklake_retry_wait_ms=100`) + **`AUTOMATIC_MIGRATION` opt-in** (v1.0 no longer auto-migrates on attach) | All 9 are first-class v1.0 settings | `/usage/configuration` + v1.0 blog appendix PR #697 |
| D9 | Not mentioned: **Frozen DuckLake** over HTTPS with `ATTACH 'https://…' (TYPE ducklake)` | First-class v1.0 feature; FAQ example uses `https://blobs.duckdb.org/datalake/nl-railway.ducklake` | `/faq` |
| D10 | Wave 1 missed: 18 production users, 5 non-DuckDB clients, O'Reilly "DuckLake: The Definitive Guide" book, v1.1 ETA **September 2026** (Variant inlining for non-DuckDB catalogs + Multi-Deletion Vector Puffin files), v2.0 direction (Git-like branching + permission-based roles + incremental materialized views) | All confirmed | v1.0 blog "Adoption" + "Future" sections |

## 7. Integration with marimo for demos (per project plan)

> Project plan: marimo is the canonical reactive Python notebook surface for the lakehouse (`oideachais-marimo-dashboards` spec lists 11 notebooks for the 5 educational stages + leabharlann full-stack demo). DuckLake integrates with marimo in 3 patterns:

### 7.1 Pattern A: marimo on DuckLake direct ATTACH (reactive SQL cell)

```python
# /// script
# requires-python = ">=3.12"
# dependencies = ["duckdb>=1.5.2", "marimo>=0.13", "boto3"]
# ///
import marimo as mo
import duckdb

con = duckdb.connect()                                    # in-memory DuckDB
con.execute("INSTALL ducklake; INSTALL httpfs; LOAD ducklake; LOAD httpfs;")
con.execute("""
    ATTACH 'ducklake:metadata.ducklake' AS lake
    (DATA_PATH 'data/', DATA_INLINING_ROW_LIMIT 50)
""")
con.execute("USE lake;")

# Reactive cells: each cell re-runs when its referenced reactive state changes
stations = mo.sql("FROM lake.nl_train_stations;")
filt     = mo.ui.multiselect(options=stations["code"].unique().tolist())
mo.sql(f"FROM lake.nl_train_stations WHERE code IN {tuple(filt.value)};")
```

### 7.2 Pattern B: marimo + S3/Garage-backed DuckLake for the production lakehouse

```python
# In a marimo notebook on the lakehouse marimo pod
con = duckdb.connect("/tmp/notebook.duckdb")
con.execute("INSTALL ducklake; INSTALL httpfs; LOAD ducklake; LOAD httpfs;")
con.execute("""
    CREATE OR REPLACE SECRET lake_storage (
        TYPE S3, KEY_ID 'GARAGE_ACCESS_KEY', SECRET 'GARAGE_SECRET_KEY',
        ENDPOINT 'http://lakehouse-garage:3900', URL_STYLE 'path',
        REGION 'garage', USE_SSL false, SCOPE 's3://lakehouse-bucket/'
    );
""")
con.execute("""
    ATTACH 'ducklake:postgres:dbname=lakehouse_catalog host=lakehouse-postgres
            port=5432 user=lakehouse password=LOCKET_DUCKLAKE_PG_PASSWORD
            sslmode=require'
        AS lakehouse (DATA_PATH 's3://lakehouse-bucket/ducklake/');
""")
# Time-travel cell: snapshot_version is reactive
snap = mo.ui.slider(start=1, stop=con.execute(
    "SELECT max(snapshot_id) FROM lakehouse.snapshots()").fetchone()[0])
mo.sql(f"FROM lakehouse.leabharlann_books AT (VERSION => {snap.value});")
```

### 7.3 Pattern C: marimo `mo.sql(engine=)` federated query

```python
# marimo's mo.sql accepts a duckdb engine and pushes SQL into DuckLake directly
# https://duckdb.org/2024/09/04/marimo-duckdb/
db = mo.sql.engine.duckdb()    # creates an ephemeral DuckDB
db.execute("INSTALL ducklake; LOAD ducklake;")
db.execute("ATTACH 'ducklake:metadata.ducklake' AS lake;")
db.execute("USE lake;")
mo.sql("SELECT count(*) FROM lake.nl_train_stations;", engine=db)
```

### 7.4 What to add to the oideachais-marimo-dashboards spec

| ID | Add | Why |
|:--|:--|:--|
| M1 | Notebooks must call `INSTALL ducklake; LOAD ducklake;` once in `@app.setup` (or a one-time `init.sql`) | Avoids re-install on every cell render — anti-pattern #3 in Wave 1 |
| M2 | Use `DATA_INLINING_ROW_LIMIT 50` for interactive notebooks (above the 10 default) | Avoids Parquet thrash when demoing with ≤50-row updates |
| M3 | Expose a "snapshot slider" `mo.ui.slider` over `lakehouse.snapshots()` | Lets users time-travel interactively — exercises v1.0's flagship feature |
| M4 | Add a "Wipe + Restart" cell calling `CHECKPOINT;` (gate behind `mo.ui.button`) | One-shot maintenance is the documented happy path; CHECKPOINT is a 6-function heavy operation |
| M5 | Document the **Frozen DuckLake** pattern: `ATTACH 'https://blobs.duckdb.org/datalake/…' (TYPE ducklake)` for read-only demo data + cite the **Marimo + DuckDB integration blog** (`https://duckdb.org/2024/09/04/marimo-duckdb/`) in `# /// script` header comment | Public read-only examples need no credentials; excellent for sharing in HF Spaces (`huggingface-spaces` skill) |

### 7.5 Cross-spec dependencies

- **`oideachais-pipeline`**: dlt destination `dlt.destinations.impl.ducklake.ducklake` writes to the same DuckLake that marimo reads — notebooks are downstream observers.
- **`oideachais-marimo-dashboards`**: 11 marimo notebooks target the 5 educational stages + leabharlann full-stack demo — DuckLake is the canonical data source.
- **`upstream-package-monitoring`**: add a Firecrawl monitor on `https://ducklake.select/news/` + `https://github.com/duckdb/ducklake/releases` to detect v1.1 (Sep 2026 expected) PR drift into the oideachais data-plane.

## §8 OpenSpec actions recommended (5 items)

| ID | Action | Owner |
|:--|:--|:--|
| O1 | Update `agent-08-ducklake.md` § "Drift log" with all 10 D-items from §6 above (full 19-item version lives in the build agent's notes) | Wave 3 agent |
| O2 | Create new openspec change `ducklake-1-0-adopt-v1-features`: bump pin to `ducklake>=1.0,<2.0`, enable `set_option` for inlining/sort/bucket, document new functions (`set_commit_message`, `ducklake_settings`, `ducklake_flush_inlined_data`) | `oideachais-pipeline` owner |
| O3 | Add Firecrawl monitor on `https://ducklake.select/news/` (3rd layer of upstream-package-monitoring) + GitHub release sensor for `duckdb/ducklake` v1.1 (Sep 2026 expected) | `upstream-package-monitoring` owner |
| O4 | Move canonical client per Wave 1 R1 (Phase 1A-04 doc references `core/ducklake/client.py` which doesn't exist) | `oideachais-pipeline` owner |
| O5 | Add `set_commit_message` wrapper to `ducklake_options.py` (no existing helper, but the v1.0 audit-trail story is essential for the `oideachais` data-plane lineage) | `oideachais-pipeline` owner |

## §9 URL pattern evidence (real, observed live)

| URL | Pattern | Notes |
|:--|:--|:--|
| `https://ducklake.select/` | bare homepage (no `www`, no `.dev`) | Wave 1 brief had `.dev` — DNS NXDOMAIN |
| `https://ducklake.select/docs/stable/duckdb/{introduction,usage/*,maintenance/*,advanced_features/*}` | versioned `stable` segment | All 5 version branches (`1.0`/`0.4`/`0.3`/`0.2`/`0.1`) coexist at `/docs/{version}/…` |
| `https://ducklake.select/docs/stable/specification/tables/{ducklake_*}` (28 tables) | snake_case `ducklake_<entity>` catalog tables | All catalog tables are `ducklake_`-prefixed to avoid user data collision |
| `https://ducklake.select/2026/04/13/ducklake-10/` | `/YYYY/MM/DD/<slug>/` blog path | v1.0 release date hard-coded in URL |
| `https://blobs.duckdb.org/datalake/nl-railway.ducklake` | Frozen DuckLake example (HTTPS, no creds) | `ATTACH 'https://…' (TYPE ducklake)` |
| `https://github.com/duckdb/ducklake` | `duckdb/ducklake` GitHub org (same as the DuckDB project) | README uses the same ATTACH syntax as the docs |
| `https://blobs.duckdb.org/docs/ducklake-docs.md` | Single-file Markdown export of all docs | Useful for offline LLM ingestion |
| `https://ducklake.select/faq` | plain FAQ, no version segment | v1.0 cites v1.1 ETA Sep 2026 |

(End of file — 9 sections, 10 drift items, 5 openspec actions; **15+ verbatim quotes**, **8 live URL patterns** observed; total ~340 lines)