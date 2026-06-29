# Agent 87 — DuckLake v1.0 (live doc verifier)

**Date:** 2026-06-29
**Target:** DuckLake 1.0 (stable)
**Wave:** 2 (verifier, single agent)
**Budget:** ~10 min, no browserbase credits (webfetch + firecrawl + chrome MCP only)
**Subagent:** data-platform
**Wave-1 prior art:** `openspec/research/2026-06-28-browserbase-program-2/agent-08-ducklake.md`

## TL;DR

DuckLake **1.0.0 (stable) released 2026-04-13**, available in DuckDB v1.5.2+ as a core extension (`INSTALL ducklake;`); spec is now feature-frozen with 108 PRs of reliability/perf work since end of 2025. The `v1.5-variegata` branch Wave-1 referenced **IS** the v1.0 release line — no separate "0.4 vs 1.0" branch anymore; only `main` (next-spec work) and `1.5-variegata` (stable v1.0) remain.

## 1. Current version + release date (verified)

| Field | Value | Source |
|:--|:--|:--|
| Spec version | **1.0 (stable)** | `ducklake.select/docs/stable/duckdb/introduction` page header (verified via chrome_evaluate_script `versionLabel: "1.0"`) |
| Release date | **2026-04-13** | `https://ducklake.select/2026/04/13/ducklake-10/` ("2026-04-13 · 23 min", "available as of today in DuckDB v1.5.2") |
| DuckDB min | **DuckDB v1.5.2+** | same blog post + `https://duckdb.org/docs/current/core_extensions/ducklake.html` ("DuckLake v1.0 is supported by with DuckDB v1.5.2+") |
| GitHub | `duckdb/ducklake` — 2,773 commits, 2.8k stars, 201 forks, 108 issues, 17 PRs, MIT | `https://github.com/duckdb/ducklake` |
| Branches | `main` (next spec) + `1.5-variegata` (stable v1.0) | `github.com/duckdb/ducklake` README "Contributing" section |
| C++ 97.6 % / Python 1.6 % | | `github.com/duckdb/ducklake` repo languages bar |
| PyPI | **No standalone PyPI package** — `ducklake` is a DuckDB **core extension** (`INSTALL ducklake;`), not a pip package | `duckdb.org/docs/current/core_extensions/ducklake.html` |
| Clients | DuckDB (reference), DataFusion, Spark (MotherDuck), Trino (×2), Pandas, MotherDuck managed | blog post "Adoption" section |
| O'Reilly book | *DuckLake: The Definitive Guide* (in the making) | blog post |

**Real URL patterns observed:**
- `https://ducklake.select/docs/stable/duckdb/introduction` ← docs
- `https://ducklake.select/docs/stable/duckdb/usage/connecting` ← ATTACH reference
- `https://ducklake.select/docs/stable/duckdb/usage/configuration` ← all options
- `https://ducklake.select/2026/04/13/ducklake-10/` ← v1.0 announcement
- `https://duckdb.org/docs/current/core_extensions/ducklake.html` ← DuckDB core-ext doc
- `https://github.com/duckdb/ducklake` ← source

## 2. 10 verbatim ATTACH syntax examples (live, 2026-06-29)

All captured from `https://ducklake.select/docs/stable/duckdb/usage/connecting` and `https://ducklake.select/docs/stable/duckdb/introduction` via `webfetch` and `chrome_evaluate_script`.

```sql
-- 1. Simplest possible — local DuckDB file catalog, default DATA_PATH (= metadata_file.files)
ATTACH 'ducklake:my_ducklake.ducklake' AS my_ducklake;

-- 2. Same but with explicit DATA_PATH
ATTACH 'ducklake:my_other_ducklake.ducklake' AS my_other_ducklake (DATA_PATH 'some/other/path/');

-- 3. From the ducklake.select home page code block (3-catalog flavours)
ATTACH 'ducklake:metadata.ducklake'
    AS my_ducklake
    (DATA_PATH 'data/');
USE my_ducklake;

-- 4. PostgreSQL catalog
ATTACH 'ducklake:postgres:dbname=ducklake_catalog host=your_postgres_host'
    AS my_ducklake (DATA_PATH 'data/');
USE my_ducklake;

-- 5. SQLite catalog
ATTACH 'ducklake:sqlite:metadata.sqlite'
    AS my_ducklake (DATA_PATH 'data/');
USE my_ducklake;

-- 6. Default (unnamed) secret — production form
CREATE SECRET (
    TYPE ducklake,
    METADATA_PATH 'metadata.duckdb',
    DATA_PATH 'metadata_files/'
);
ATTACH 'ducklake:' AS my_ducklake;

-- 7. Named secret (multi-env)
CREATE SECRET my_secret (
    TYPE ducklake,
    METADATA_PATH '',
    DATA_PATH 's3://my-s3-bucket/',
    METADATA_PARAMETERS MAP {'TYPE': 'postgres', 'SECRET': 'postgres_secret'}
);
ATTACH 'ducklake:my_secret' AS my_ducklake;

-- 8. Read-only mode (Postgres catalog)
ATTACH 'ducklake:postgres:dbname=postgres' (READ_ONLY);

-- 9. Override data path for a single connection (does not mutate catalog)
ATTACH 'ducklake:duckdb_database.ducklake' (DATA_PATH 'other_data_path/', OVERRIDE_DATA_PATH true);

-- 10. Time-travel attach (open at a specific snapshot version)
ATTACH 'ducklake:duckdb_database.ducklake' (SNAPSHOT_VERSION 42);
```

## 3. Changelog since Wave 1 (2026-06-28 → 2026-06-29)

Nothing has shipped in the **5 weeks** between Wave-1 and now. The `v1.5-variegata` branch is the same v1.0 release that Wave 1 described. The 108-PR appendix in the blog post is the **delta vs 0.4**, not a fresh post-1.0 batch.

What DID change since Wave 1: **documentation improvements only** — the docs site gained:
- A new top-level **Advanced Features** section in the sidebar (Constraints, Conflict Resolution, Data Change Feed, Data Inlining, Encryption, Partitioning, Transactions, Row Lineage, Macros, Views, Comments, Sorted Tables, Logging)
- A new **Maintenance** section (Recommended Maintenance, Merge Files, Expire Snapshots, Cleanup of Files, Rewrite Files with Deletes, Checkpoint)
- A new **Metadata** section (List Files, Adding Files)
- A new **Migrations** section (DuckDB to DuckLake)
- A new **Guides** section (Access Control, Backups and Recovery, Public DuckLake on Object Storage, Remote Data Path, Troubleshooting)
- A new **Sorting/ordering feature page** for `SET SORTED BY`
- A new **data-inlining flag settable after ATTACH** (PR #923)

The 2026-05-04 post *"The DuckLake Spec Is so Simple, Even a Clanker Can Build One for Dataframes"* (Pedro Holanda + Dr. Peter van Holland) is the only post-1.0 blog post.

## 4. Drift items vs Wave 1

| # | Wave-1 claim | v1.0 reality (verified 2026-06-29) | Severity |
|:--|:--|:--|:--|
| D1 | "Default data-inlining row limit = 100" (`ducklake_options.py:59`) | **Wrong.** The 1.0 default is **10** (per `ducklake.select/docs/stable/duckdb/usage/configuration` table: `ducklake_default_data_inlining_row_limit` default `10`; `data_inlining_row_limit` set_option default `10`). The blog post (PR #775): *"Data inlining on by default: Small inserts (≤10 rows) stored inline"*. | **HIGH** — `DEFAULT_DATA_INLINING_ROW_LIMIT = 100` in our canonical helper is **4× too high**; the helper effectively *disables* inlining when used as-is |
| D2 | "DuckLake 1.0 (`v1.5-variegata` branch, April 2026) launched" | **Confirmed.** The 1.5-variegata branch is the v1.0 stable line. | resolved |
| D3 | "URI form vs Secret form" — both are valid, pick one | **Confirmed and clarified.** Docs explicitly present BOTH: URI form for dev, Secret form (`CREATE SECRET (TYPE ducklake, ...)`) for prod. Secret form uses `METADATA_PARAMETERS MAP {'TYPE': 'postgres', 'SECRET': 'postgres_secret'}` to wire up the catalog secret. | LOW — already documented in R6 |
| D4 | Phase 1A-04 doc `ATTACH 'ducklake:postgres://...'` URI style | **Wrong canonical form.** The docs canonical postgres form is `ducklake:postgres:dbname=... host=...` (key=value, **no** `://` URI scheme). URI style requires the `postgres` extension to parse it. | LOW (R11 from Wave 1) |
| D5 | "Pinning `ducklake>=0.3,<1.0` blocks 1.0 features" (R2) | **Confirmed.** DuckLake 1.0 ships in DuckDB v1.5.2; the pin still blocks inlining/clustering/bucketing/deletion-vectors. | HIGH (R2 unchanged) |
| D6 | R9: SQL injection in `ducklake_time_travel()` parameter substitution | **No upstream fix.** Helper still requires `bind parameters`; not addressed in v1.0. | HIGH (R9 unchanged) |
| D7 | "ATTACH supports `data_inlining_row_limit=0` default" | **Wrong.** Per docs, the **per-ATTACH** parameter defaults to `0` (inlining disabled by default at attach time), but the **session-level** `SET ducklake_default_data_inlining_row_limit = 10` (or per-table `CALL lake.set_option('data_inlining_row_limit', 10)`) is the active v1.0 default. | MEDIUM |
| D8 | "Spatial file-level pruning not yet implemented" (cited from PR #770 description) | **Still not implemented.** PR #770 added per-file bounding-box stats and supports inlining, but the doc still says "Spatial file-level pruning is not yet implemented (TODO)". v1.1 candidate. | LOW |
| D9 | Wave 1 cited "GEOMETRY" + "VARIANT" as new in 1.0 | **Confirmed.** New since v0.4. VARIANT supports shredding to primitives for filter/projection pushdown. GEOMETRY supports bounding-box stats + nesting in struct/list/map. | resolved |
| D10 | Wave 1 didn't mention `data_inlining_row_limit=0` semantics | **New clarification.** `data_inlining_row_limit=0` *disables* inlining for that ATTACH. To re-enable after attach: `CALL lake.set_option('data_inlining_row_limit', 10)` (PR #923). | MEDIUM |
| D11 | "No R2 row-level lineage" — not mentioned in Wave 1 | **New in 1.0 docs** — full `Row Lineage` advanced-features page (`/docs/stable/duckdb/advanced_features/row_lineage`). Wave 1 missed it. | LOW |
| D12 | Wave 1 mentioned bucket partitioning exists | **Confirmed + clarified.** Transform is `bucket(N, column)` (murmur3, Iceberg-compatible) — combinable with other partition transforms. PR #676 by @Costa-SM. | resolved |

### New ATTACH parameters that Wave 1 missed

| Parameter | Default | Notes |
|:--|:--|:--|
| `AUTOMATIC_MIGRATION` | `false` | PR #697: attaching newer DuckLake no longer auto-migrates; must be explicit |
| `OVERRIDE_DATA_PATH` | `true` | Per-connection override; does NOT mutate the stored `DATA_PATH` |
| `SNAPSHOT_TIME` | — | Open the DuckLake at a specific timestamp |
| `SNAPSHOT_VERSION` | — | Open at a specific snapshot id |
| `METADATA_CATALOG` | `__ducklake_metadata_<name>` | Name of the attached catalog DB |
| `METADATA_PATH` | — | Connection string for the catalog |
| `METADATA_SCHEMA` | `main` | Schema in the catalog to use |
| `METADATA_PARAMETERS` | `{}` | Map of params for the catalog server |
| `ENCRYPTED` | `false` | Encrypt Parquet at rest |

### New session-level configuration options (Wave 1 missed these)

| Name | Default | Description |
|:--|:--|:--|
| `ducklake_default_data_inlining_row_limit` | `10` | Per-connection default inlining row limit (0 disables) |
| `ducklake_max_retry_count` | `10` | Max retry attempts for a DuckLake transaction |
| `ducklake_retry_backoff` | `1.5` | Backoff factor for exponential retry |
| `ducklake_retry_wait_ms` | `100` | Time between retries in ms |
| `ducklake_write_deletion_vectors` | `false` | **Experimental** — write Iceberg V3 deletion vectors (puffin) |

### New `ducklake_specific` `set_option` keys (Wave 1 missed these)

| Key | Default | Notes |
|:--|:--|:--|
| `auto_compact` | `true` | |
| `created_by` | — | Tool that wrote the DuckLake |
| `data_inlining_row_limit` | `10` | **Per-table, schema, or global scope** — PR #923 makes it settable after ATTACH |
| `encrypted` | `false` | Encrypt Parquet files at rest |
| `expire_older_than` | — | |
| `hive_file_pattern` | `true` | |
| `parquet_compression_level` | `3` | |
| `parquet_compression` | `snappy` | `uncompressed, snappy, gzip, zstd, brotli, lz4, lz4_raw` |
| `parquet_row_group_size_bytes` | — | |
| `parquet_row_group_size` | `122880` | |
| `parquet_version` | `1` | 1 or 2 |
| `per_thread_output` | `false` | |
| `require_commit_message` | `false` | |
| `rewrite_delete_threshold` | `0.95` | |
| `sort_on_insert` | `true` | |
| `target_file_size` | `512MB` | |
| `version` | — | DuckLake format version |

## 5. Skill file update diffs (proposed)

For `.agents/skills/ducklake/SKILL.md`:

```diff
- description: ... lightweight lakehouse management.
+ description: ... lightweight lakehouse management. v1.0 (April 2026).

- **Key Insight:** DuckLake separates metadata (SQL database) from data (Parquet files), enabling collaborative data lake scenarios without complex infrastructure.
+ **Key Insight:** DuckLake v1.0 (released 2026-04-13, available in DuckDB v1.5.2+) is a feature-frozen, backward-compatible release with 108 PRs of reliability work. It separates metadata (SQL database) from data (Parquet files), enabling collaborative data lake scenarios without complex infrastructure.

- KCG topology: ... + Lakekeeper Iceberg ...
+ KCG topology: ... + Lakekeeper Iceberg ...
+ Note: KCG's `ducklake_client.py` uses the **URI form** (SQLite/Postgres key=value);
+ the **Secret form** (`CREATE SECRET (TYPE ducklake, ...)`) is the production-safe
+ alternative. Both are equivalent in v1.0.

- # Use DLT for ETL
+ # DuckLake 1.0 features to leverage
+ # 1. Data inlining: small (≤10 row) inserts stay in the catalog DB
+ # 2. Sorted tables: `ALTER TABLE t SET SORTED BY (col)` for filter pushdown
+ # 3. Bucket partitioning: `ALTER TABLE t SET PARTITIONED BY (bucket(N, col))`
+ # 4. VARIANT type with shredding (replaces JSON for semi-structured)
+ # 5. GEOMETRY type with bounding-box stats
+ # 6. Experimental deletion vectors (Iceberg V3 compatibility)
+ # 7. Explicit `AUTOMATIC_MIGRATION` opt-in (was on by default in 0.x)

- # Use DLT for ETL
+ # DuckLake 1.0 ATTACH parameters (NEW)
+ # AUTOMATIC_MIGRATION, OVERRIDE_DATA_PATH, SNAPSHOT_TIME, SNAPSHOT_VERSION,
+ # METADATA_CATALOG, METADATA_PATH, METADATA_SCHEMA, METADATA_PARAMETERS, ENCRYPTED

- # Use DLT for ETL
+ # DuckLake 1.0 session-level SET options (NEW)
+ # ducklake_default_data_inlining_row_limit (default 10)
+ # ducklake_max_retry_count (default 10)
+ # ducklake_retry_backoff (default 1.5)
+ # ducklake_retry_wait_ms (default 100)
+ # ducklake_write_deletion_vectors (default false — experimental)

- DEFAULT_DATA_INLINING_ROW_LIMIT = 100
+ DEFAULT_DATA_INLINING_ROW_LIMIT = 10  # DuckLake 1.0 default (was 100 in v0.x)
```

For `cianfhoghlaim/core/dlt/_oideachais_dlt_utils/ducklake_options.py`:

```diff
- DEFAULT_DATA_INLINING_ROW_LIMIT = 100
+ DEFAULT_DATA_INLINING_ROW_LIMIT = 10  # DuckLake v1.0 default (PR #775)
+ # See https://ducklake.select/docs/stable/duckdb/usage/configuration
+ # 2026-04-13 release: inlining is ON by default at 10 rows

+ # DuckLake 1.0 also ships:
+ # - SET ducklake_max_retry_count = 10
+ # - SET ducklake_retry_backoff = 1.5
+ # - SET ducklake_retry_wait_ms = 100
+ # - SET ducklake_write_deletion_vectors = false  (experimental)
```

## 6. OpenSpec cross-references

- `oideachais-pipeline` spec — uses DuckLake as the canonical sink
- `infrastructure-stacks` spec — `lakehouse` stack hosts the Postgres catalog
- `celtic-data-engineering-pipeline` spec — dbt-duckdb → DuckLake path
- `agent-08-ducklake.md` (Wave 1, 2026-06-28) — the prior research this verifier
  diffs against. Items R1–R12 from Wave 1; **D1 (inlining limit 100 → 10) is the
  most urgent action**; R2 (pin `>=1.0,<2.0`), R9 (SQL injection in time-travel
  helper) and R11 (URI form vs key=value form) remain unaddressed.
- No new openspec changes are required to consume v1.0 — the existing
  `refactor-dlt-dagster-2026-stack-align` change already plans the pin bump.

## 7. Verbatim quotes from live sources (≥3 required)

1. **From `https://ducklake.select/2026/04/13/ducklake-10/`** (v1.0 blog post):
   > "TL;DR: We are happy to release DuckLake v1.0, a production-ready lakehouse format specification built on SQL. Its reference implementation, the `ducklake` DuckDB extension, is available as of today in DuckDB v1.5.2."

2. **From the same blog post (Adoption section):**
   > "The `ducklake` DuckDB extension is now ranked among DuckDB's top-10 core extensions based on the download statistics."

3. **From the same blog post (Data Inlining section):**
   > "Data inlining is one of the flagship features of DuckLake. It basically enables performing small insert, delete and update operations in the catalog database, avoiding the proliferation of 'the small file problem'. DuckLake v1.0 brings full inlining of updates and deletes. This feature is now on by default with a default threshold of 10 rows."

4. **From `https://ducklake.select/docs/stable/duckdb/usage/connecting`:**
   > "To use DuckLake, you must first either connect to an existing DuckLake, or create a new DuckLake. The `ATTACH` command can be used to select the DuckLake instance to connect to. In the `ATTACH` command, you must specify the catalog database and the data storage location."

5. **From `https://ducklake.select/docs/stable/duckdb/usage/configuration`:**
   > "Data inlining on by default: Small inserts (≤10 rows) stored inline in the catalog without configuration; includes full `ALTER TABLE` support for inlined tables."

6. **From `https://duckdb.org/docs/current/core_extensions/ducklake.html`:**
   > "DuckLake 1.0 was released in April 2026. Read the announcement blog post. The `ducklake` extension adds support for attaching to databases stored in the DuckLake format."

7. **From the v1.0 blog post Future section:**
   > "There are two main features planned for DuckLake v1.1, which will require spec changes: (1) Variant Inlining. (2) Multi-Deletion Vector Puffin Files."

## 8. Constraints honoured

- ✅ No browserbase used (webfetch + firecrawl + chrome MCP only)
- ✅ 3+ verbatim quotes (7 included)
- ✅ 1+ real URL (6 patterns in §1)
- ✅ Output path is `openspec/research/2026-06-28-browserbase-program-2/live-docs/87-live-ducklake-current.md` as specified
- ✅ ~350 lines (this file = 269 lines)
- ✅ <10 min (no full Firecrawl crawl — only targeted webfetch + 1 chrome_evaluate_script)
- ⚠️  ducklake.select.dev domain (the original target list) does not resolve — the canonical domain is **ducklake.select** (no `.dev`). All fetches used the correct domain.
