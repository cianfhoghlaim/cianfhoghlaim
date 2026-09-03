# Agent 01 — dlt (Data Load Tool) v1.7+ — Phase 2 Pass-2 Research

**Date:** 2026-06-28 (23:08 UTC, ~10 min wall clock)
**Phase:** Wave 1 of 25 — Agent 01 / package: `dlt`
**Budget consumed:** ~110 of 200 BrowserBase credits + 1 GitHub API call
**BrowserBase session:** `d347444b-ebb3-431d-a427-af4aea0ab13b` (initial) → `a6c4c0ea-d083-45f9-8f96-e8fd6627de6c`
**Authoritative sources:** GitHub API `repos/dlt-hub/dlt/releases` (5 most recent), PyPI JSON `pypi.org/pypi/dlt/json`, `dlthub.com/docs` (extract), CCC semantic search over `cianfhoghlaim/`

---

## 1. TL;DR

We pin **`dlt>=1.0.0`** (`cianfhoghlaim/pyproject.toml:39`) and the lock currently resolves to **`dlt v1.25.0`** (`uv tree` output). The latest upstream release is **`dlt 1.28.1`** (2026-06-19, released ~9 days before this research). That puts us **3 minor versions behind** and therefore missing every dlt 1.26 / 1.27 / 1.28 feature below.

Three release lines matter for Cianfhoghlaim:

| Release | Date | Headline impact |
|:--|:--|:--|
| **1.28.1** | 2026-06-19 | Dataset browser default in dashboard; connectorx temporal fix; Python 3.9 EOL |
| **1.28.0** | 2026-06-15 | **BREAKING** `refresh="drop_data"` no longer frees storage on Delta/Iceberg; **BREAKING** `replace` now fully truncates empty/orphaned tables; Lance destination write optimisations; refreshable cloud credentials for long-running loads |
| **1.27.0** | 2026-05-19 | **BREAKING** `workspace` extra removed + `dlthub` command split out — `dlt dashboard`, `dlt pipeline … show/mcp`, `dlt ai` now require `pip install "dlt[hub]"`; **native Polars DataFrame/LazyFrame in `@dlt.resource`**; Databricks Zerobus loading; incremental filtering on `dlt.Relation` |
| 1.26.0 | (earlier) | SCD2 + Lance destination REST Namespace experimental |

The **single most consequential gap** for our code is the 1.27 `workspace` split: any `dlt dashboard` / `dlt pipeline … show` invocation in our stack will fail with `ModuleNotFoundError` because `pyproject.toml` has plain `dlt>=1.0.0`, not `"dlt[hub]>=1.27.0"`. Our installed 1.25.0 still ships `dashboard` in the base wheel, which masks the bug today.

> **Drift correction** — the first-pass file `P1A-01-dlt-dlthub-pro.md` claims dlt sources live at `cianfhoghlaim/dlt_sources/`. **They do not.** The post-v4-consolidation path is `cianfhoghlaim/pipelines/ingest/_oideachais_dlt_sources/` (190 `.py` files, 12 nation/domain subdirs). The first pass also under-counts "28 sources" — there are 190 Python files in that directory tree.

---

## 2. Code (where dlt lives in Cianfhoghlaim)

| Path | Purpose | Notes |
|:--|:--|:--|
| `cianfhoghlaim/pyproject.toml:39` | `dlt>=1.0.0` pin | Too wide — should be `"dlt[hub]>=1.27.0,<2.0.0"` post-1.27 split |
| `cianfhoghlaim/pipelines/ingest/_oideachais_dlt_sources/` | **190 dlt source `.py` files** across 12 subdirs (`ie`, `ni`, `sct`, `wls`, `ggy`, `iom`, `jey`, `en`, `cross`, `official_media`, `leabharlann`, `law`, `common`, `constants`, `site_analysis`) | This is the **real** location post-v4 |
| `cianfhoghlaim/pipelines/ingest/_oideachais_dlt_sources/ie/education/primary.py:133-163` | Canonical `@dlt.resource(name=…, write_disposition="merge", primary_key=[...])` pattern | Two-PK composite `[file_hash, document_id]` |
| `cianfhoghlaim/pipelines/ingest/_oideachais_dlt_sources/ie/education/curriculum.py:19` | `pipeline = dlt.pipeline(pipeline_name="curriculum", destination="duckdb")` | Default destination is duckdb |
| `cianfhoghlaim/pipelines/ingest/_oideachais_dlt_sources/ie/education/curriculum.py:705-717` | `source_provenance` resource with explicit `columns={...data_type...}` schema hints | Good pattern — pre-declares schema for BAML extractions |
| `cianfhoghlaim/pipelines/ingest/_oideachais_dlt_sources/official_media/instagram_export/` | `profiles` resource with `write_disposition="merge"` | Tested at `tests/test_instagram_export.py:224-239` |
| `cianfhoghlaim/pipelines/ingest/_oideachais_dlt_sources/leabharlann/zotero.py:279` | Leabharlann zotero pipeline | SHA-256 primary key for dedup |
| `cianfhoghlaim/pipelines/ingest/common/incremental.py` | Shared incremental helper: `compute_content_hash()`, `make_deduplication_key()`, `with_change_detection()` | Uses `dlt.sources.incremental` (still on 1.25 API, see drift) |
| `cianfhoghlaim/pipelines/ingest/_oideachais_dlt_sources/common/incremental.py:176` | `last_crawl: dlt.sources.incremental[datetime] = dlt.sources.incremental(...)` | Same pattern, different copy under `_oideachais_dlt_sources/` |
| `cianfhoghlaim/pipelines/ingest/_oideachais_dlt_sources/cross/upstream/blog_post.py:152` | `cursor: dlt.sources.incremental[str] = dlt.sources.incremental(...)` | Source-level cursor |
| `cianfhoghlaim/pipelines/ingest/_oideachais_dlt_sources/ie/law/irish_statute_book.py:87` | `cursor: dlt.sources.incremental[int] = dlt.sources.incremental(...)` | Int-typed cursor for act numbering |
| `cianfhoghlaim/pipelines/ingest/_oideachais_dlt_sources/ie/culture/duchas_images.py:415` | `last_updated: Incremental[str] = dlt.sources.incremental(...)` | Has the **stale TODO comment** at line 22 |
| `cianfhoghlaim/pipelines/ingest/_oideachais_dlt_sources/cross/bunchloch/_filesystem_source_helpers.py:67-71` | `dlt.pipeline(pipeline_name="bunchloch_pipeline", destination=destination, dataset_name=dataset_name)` | Generic helper; `dataset_name="research_bunchloch"` (line 55) namespaced under research |
| `cianfhoghlaim/docs/legacy/crypteolas/dlt_utils/destinations.py` | Destination factory: `dlt.destinations.ducklake(credentials=config.to_credentials())` | Lives under `docs/legacy/` — needs migration to `dlt_utils/destinations.py` per `web/apps/_oideachais_apps/CHANGELOG.md` line 177 |
| `cianfhoghlaim/tests/_oideachais/dlt_sources/domains/uk/test_crown_deps.py:121-140` | **Anti-pattern** — asserts `res._hints.get("primary_key")` (private `_hints`) and `getattr(res, "write_disposition")` | Uses internal `_hints` dict; will break if dlt renames internals |
| `cianfhoghlaim/pipelines/ingest/_oideachais_dlt_sources/official_media/tests/test_instagram_export.py:236-239` | Tests `resource.write_disposition == "merge"` (public attr) + `hasattr(resource, "apply_hints")` | Good pattern (public attrs only) |
| `cianfhoghlaim/core/curriculum/celtic/duchas_images.py:46` | `from dlt.sources.incremental import Incremental` | Another consumer of `dlt.sources.incremental` (under `core/curriculum/celtic/`, not `pipelines/ingest/`) |
| `cianfhoghlaim/docs/legacy/crypteolas/pipelines/github_api/transformations.py:26, 46, 67, 85` | The **only** uses of `@dlt.hub.transformation` in the whole repo — all in legacy crypteolas | Uses ibis-backed aggregations over `dataset.table("issues").to_ibis()` |

> **The `_hints` vs `apply_hints` distinction** is critical: dlt 1.x exposes `write_disposition` as a public attribute and stores `primary_key` in the internal `_hints` dict. The new public way (1.27+) is to use `resource._hints["primary_key"]` or `resource.apply_hints({"primary_key": "..."})`. Our test at `test_crown_deps.py:138` uses the internal form.

---

## 3. Env (Infisical-backed config keys needed)

| Key | Where | Purpose | Source / Notes |
|:--|:--|:--|:--|
| `DESTINATION__DUCKDB__CREDENTIALS__DATABASE` | Lakehouse stack env | DuckDB destination fallback (`.dlt/<pipeline>/<dataset>.duckdb`) | `USE_DUCKLAKE=false` per `_oideachais_apps/CHANGELOG.md:183` |
| `DESTINATION__DUCKLAKE__CREDENTIALS__CATALOG` | DuckLake via PostgreSQL | `postgres://lakehouse.lakehouse:5433/ducklake_catalog` | `dlt.destinations.ducklake(credentials=...)` |
| `DESTINATION__DUCKLAKE__CREDENTIALS__STORAGE__BUCKET_URL` | DuckLake via Garage S3 | `s3://ducklake/<dataset>/` (path-style for Garage) | path-style S3 per CHANGELOG line 181 |
| `DESTINATION__MOTHERDUCK__CREDENTIALS__DATABASE` | MotherDuck | `md:${MOTHERDUCK_DATABASE}` | `infrastructure/stacks/motherduck/blueprint.yaml:62` |
| `DLTHUB_API_KEY` | dltHub platform | Required for `dlt dashboard` (post-1.27 split) | `infisical://dev-baile/dlthub/api_key` |
| `DLT_ENVIRONMENT` | crypteolas legacy | `"local"` or `"production"` switch | `dlt_utils/destinations.py:101` |
| `USE_DUCKLAKE` | All dlt sources | `"true"` (default) or `"false"` | `dlt_utils/destinations.py:84` |
| `USE_LOCAL_SCRAPES` | All firecrawl-using sources | `"true"` for offline stedding/ingest_queue | From AGENTS.md protocol 2 |
| `OIDEACHAIS_IG_EXPORT_DIR` | official_media/instagram_export | Local export dir | `test_instagram_export.py:243` |

**Per 1.27 split**, the canonical install for the *whole monorepo* becomes `dlt[hub]>=1.27.0`. The `[hub]` extra pulls in `marimo`, `pyarrow`, `ibis`, `fastmcp`, etc. (release notes 1.27.0 §Breaking Changes). If we want to stay on base `dlt` only (and lose dashboard/MCP/AI), we must drop the `dlthub` command references in any pipeline README that mentions them.

---

## 4. CCC anchors (semantic-code-search queries)

```
@dlt.resource primary_key content_hash write_disposition=merge
   → 30+ source files under cianfhoghlaim/pipelines/ingest/_oideachais_dlt_sources/

dlt.sources.incremental
   → 11 occurrences (pre-1.27 API; see drift)

dlt.pipeline(pipeline_name=, destination=
   → ~50 call sites, all use plain string destination ("duckdb" most common)

dlt.destinations.ducklake / .motherduck
   → 4 occurrences, all in docs/legacy/crypteolas/ or stacks/ configs

res._hints.get("primary_key")      ← ANTI-PATTERN, uses internal API
   → test_crown_deps.py:138

@dlt.hub.transformation
   → 4 occurrences, all in docs/legacy/crypteolas/pipelines/github_api/transformations.py

dlt.Relation / polars yield       ← NOT FOUND in our code
   → opportunity (dlt 1.27+ native Polars support)
```

Path anchors:
- `cianfhoghlaim/pipelines/ingest/_oideachais_dlt_sources/` — all 190 source files
- `cianfhoghlaim/pipelines/ingest/common/incremental.py` — incremental helper (shared)
- `cianfhoghlaim/pipelines/ingest/_oideachais_dlt_sources/common/incremental.py` — same code, dual location
- `cianfhoghlaim/tests/_oideachais/dlt_sources/` — test harness
- `cianfhoghlaim/docs/legacy/crypteolas/dlt_utils/destinations.py` — destination factory
- `cianfhoghlaim/web/apps/_oideachais_apps/CHANGELOG.md:177` — destination consolidation story

---

## 5. Drift log (what changed since 2026-06-28 first pass)

| Date | Event | Drift vs first pass |
|:--|:--|:--|
| 2026-05-19 | dlt **1.27.0** released: `workspace` extra removed, `dlthub` command split, Polars native | First-pass mentions `@dlt.hub.transformation` working — that's still true but needs `[hub]` extra |
| 2026-06-15 | dlt **1.28.0** released: Lance destination write optimisations; **BREAKING** `refresh="drop_data"` no longer frees Delta/Iceberg storage; **BREAKING** `replace` truncates empty/orphaned tables | Not mentioned in first pass — affects any pipeline that calls `pipeline.run(..., refresh="drop_data")` or relies on stale data surviving a `replace` |
| 2026-06-19 | dlt **1.28.1** released: Python 3.9 EOL, dataset browser default | Not mentioned in first pass |
| 2026-06-19 | dlt **1.28.1**: `connectorx` temporal columns now use `timestamp[ns]` / `time64[ns]` from `arrow_stream` — `cast_connectorx_temporal_columns` normalises to µs | Affects any future `sql_database()` use of connectorx — none currently in our code |
| 2026-06-15 | dlt 1.28.0: bump `duckdb` → 1.5.3, `ducklake` → 1.0 | We pin `duckdb` somewhere — need to verify in `stacks/lakehouse/pyproject.toml` |
| 2026-06-15 | dlt 1.28.0: `ducklake` DuckDB-backed catalog attach — splits duckdb/sqlite branch in attach (`META_TYPE 'sqlite'` bug fix) | Not mentioned; relevant to our `dlt.destinations.ducklake` path |
| 2026-05-29 | dlt 1.27.2 hotfix: `merge` with empty data after `replace` on incremental truncates the destination table | Affects our `merge`+`replace` patterns — we must NOT do `replace` then immediately `merge` on the same incremental table without a no-data branch |
| 2026-06-28 | v4 consolidation renamed `sruth/oideachais/dlt_sources/` → `cianfhoghlaim/pipelines/ingest/_oideachais_dlt_sources/` | **First-pass file is wrong** — points to `cianfhoghlaim/dlt_sources/` (404) |
| 2026-06-28 | First-pass file under-counts: claims "28 sources"; we actually have **190 `.py` files** in `_oideachais_dlt_sources/` (and a separate `tests/_oideachais/dlt_sources/` test harness) | First-pass is off by ~7× |

**dlt.sources.incremental → IncrementalCursorProvider migration**: the lazy-load fallback comments at three locations:
- `cianfhoghlaim/pipelines/ingest/_oideachais_dlt_sources/ie/culture/_duchas_images_helpers.py:14-17`
- `cianfhoghlaim/pipelines/ingest/_oideachais_dlt_sources/ie/culture/duchas_images.py:20-23`
- `cianfhoghlaim/pipelines/ingest/_oideachais_dlt_sources/ie/culture/hidden_heritages.py:18-21`

…all say `# dlt.sources.incremental moved; use dlt.sources.incremental.IncrementalCursorProvider instead`. We are still on the old API (the import succeeds on 1.25 but the comment predicts the move). On 1.27+ this becomes a hard import error if anyone lifts the try/except wrapper.

---

## 6. Anti-patterns (DON'T do this — and 6 we have in our code today)

| # | Anti-pattern | Where we have it |
|:--|:--|:--|
| 1 | **Access `res._hints.get("primary_key")`** — uses private `_hints` dict. Use `resource.apply_hints({"primary_key": "..."})` or wait for the dlt 1.27 public getter. | `cianfhoghlaim/tests/_oideachais/dlt_sources/domains/uk/test_crown_deps.py:138` |
| 2 | **Plain `dlt>=1.0.0` without `[hub]` extra** — will break `dlt dashboard`, `dlt pipeline … show/mcp`, `dlthub ai` after upgrading to 1.27+ | `cianfhoghlaim/pyproject.toml:39` |
| 3 | **`@dlt.resource(write_disposition="merge")` with no `primary_key`** — every merge upserts on every column, explodes the row count | Sanity-check: spot-check `leabharlann/zotero.py` and the 11 `dlt.sources.incremental` callers |
| 4 | **`pipeline.run(source, refresh="drop_data")` after upgrading to 1.28.0** — silently keeps the data files (you must add an explicit `vacuum`) | Hypothetical; not yet in our code, but `crypteolas/dlt_utils/destinations.py` and `_filesystem_source_helpers.py` are likely places this would land |
| 5 | **`replace` then immediately `merge` on the same incremental table** — 1.27.2 hotfix truncates the destination after a no-data `merge` run | Need to audit our 50+ `dlt.pipeline()` calls |
| 6 | **`dlt.sources.incremental(...)` after upgrading to 1.27** without migrating to `IncrementalCursorProvider` | 11 call sites including `core/curriculum/celtic/duchas_images.py:46` (outside `_oideachais_dlt_sources/`) |
| 7 | **`@dlt.resource` yielding raw `requests.Response`** without `dlt.sources.helpers.requests` (first-pass rule, still valid) | Need to audit; `firecrawl_source.py` likely candidate |
| 8 | **`destination="duckdb"` hard-coded** instead of routing through `dlt_utils/destinations.py` | 50+ call sites use the string directly; only `dlt_utils/destinations.py` switches destinations |
| 9 | **Yielding `polars.DataFrame` / `polars.LazyFrame`** without reading the 1.27 release notes — fine on 1.25 but performance anti-pattern | Not in our code today, but missing the 1.27 native support |
| 10 | **Polling `connect_resource._hints` (the whole `_hints` dict)** rather than calling `apply_hints` | Tests at `test_crown_deps.py:138` |

---

## 7. Decision matrix (conclusions + next research priority)

| Decision | Choice | Rationale |
|:--|:--|:--|
| **Upgrade path** | Bump to **`dlt[hub]>=1.27.0,<1.29.0`** in `cianfhoghlaim/pyproject.toml:39` | Closes the 3-minor gap, enables dashboard/MCP/AI commands, unlocks Polars + native incremental filtering |
| **Incremental API migration** | Migrate the **11** `dlt.sources.incremental` callers to `IncrementalCursorProvider` lazily (next time each source is touched) | Avoids mass-rewrite; the lazy-load fallback in 3 culture sources already documents the migration |
| **Breaking-change audit** | Schedule a 1-day spike to audit `replace`+`merge` interaction per the 1.27.2 hotfix | Risk = silent table truncation on no-data runs |
| **Drop `destination="duckdb"` strings** | Push `dlt_utils/destinations.py` from `docs/legacy/crypteolas/` to `cianfhoghlaim/pipelines/ingest/` (per `_oideachais_apps/CHANGELOG.md:177`) and adopt | One canonical factory: `local | production | duckdb-fallback` |
| **Polars adoption** | Adopt dlt 1.27 native Polars in 1–2 high-volume sources (`leabharlann/zotero.py` is the strongest candidate — 2,395 PDFs) | Demonstrates the upgrade and gives a perf baseline |
| **Test API surface** | Replace `res._hints.get("primary_key")` with the public `apply_hints` round-trip | Removes the only test in our suite that depends on a private attribute |
| **New refactor item for REFACTORING.md** | Add a §13 "dlt 1.27+ feature adoption" | See §8 below |

### Next research priority

**Agent 02 (Dagster)** should:
- Verify whether `dagster-dlt`'s latest 0.25+ supports `dlt.hub.transformation` natively (the `@dlt.hub.transformation` decorators in legacy `crypteolas/.../transformations.py` may or may not auto-register as Dagster assets).
- Check whether `dlt_assets` decorator handles `apply_hints` from inside the resource or needs the hints pre-baked into the `@dlt.resource(...)` decorator (matters for test_crown_deps' lazy-hint pattern).

**Agent 04 (DuckDB / DuckLake)** should:
- Cross-check whether the `ducklake` 1.0 bump in dlt 1.28.0 is compatible with our pin in `stacks/lakehouse/pyproject.toml`.

**Agent 05 (MotherDuck)** should:
- Cross-check whether the new `dlt.destinations.motherduck(credentials="md:...")` path string in `infrastructure/stacks/motherduck/blueprint.yaml:62` still works in dlt 1.27+ (the dlt 1.27 release notes mention EU static egress IPs for MotherDuck via the dltHub platform).

---

## 8. Refactor opportunities (5 concrete items with `file:line` + 1-line justification)

1. **`cianfhoghlaim/pyproject.toml:39`** — change `dlt>=1.0.0` to `"dlt[hub]>=1.27.0,<1.29.0"`. The `[hub]` extra is required since dlt 1.27 for any `dlt dashboard`, `dlt pipeline … show/mcp`, or `dlthub ai` command; without it we silently lose the dashboard.

2. **`cianfhoghlaim/tests/_oideachais/dlt_sources/domains/uk/test_crown_deps.py:138`** — replace `res._hints.get("primary_key")` (private API) with a call to `resource.apply_hints({"primary_key": ["url"]})` then re-read via the documented public surface. Reduces coupling to dlt internals.

3. **`cianfhoghlaim/pipelines/ingest/_oideachais_dlt_sources/ie/culture/duchas_images.py:20-23` (+ `_duchas_images_helpers.py:14-17`, `hidden_heritages.py:18-21`)** — drop the `try/except` fallback wrapper around `from dlt.sources.incremental import Incremental` once we land on 1.27+; the three `pass  # dlt.sources.incremental moved` comments are documented TODOs that should be tracked in REFACTORING.md.

4. **`cianfhoghlaim/docs/legacy/crypteolas/dlt_utils/destinations.py`** — promote the file to `cianfhoghlaim/pipelines/ingest/dlt_utils/destinations.py` (per `_oideachais_apps/CHANGELOG.md:177-187`) and refactor the 50+ `dlt.pipeline(pipeline_name=…, destination="duckdb")` call sites to use the factory. Today every source hard-codes `"duckdb"` and bypasses the local/production switch.

5. **`cianfhoghlaim/pipelines/ingest/_oideachais_dlt_sources/leabharlann/zotero.py`** — adopt the **dlt 1.27 native Polars LazyFrame** pattern: yield `pl.scan_parquet(...)` instead of yielding `dict` rows one-by-one. The 2,395-PDF corpus will get ~2× faster extract per the release notes (row conversion uses a pure-Arrow fast path; pandas/numpy removed from the conversion).

6. **Bonus (small): `cianfhoghlaim/pipelines/ingest/_oideachais_dlt_sources/official_media/tests/test_instagram_export.py:238-239`** — extend the test to also assert `resource.compute_table_schema()` returns the expected `profile_id` PK column. Locks in the schema contract and forces the resource definition to declare it explicitly.

7. **Bonus (largest scope): `cianfhoghlaim/pipelines/ingest/_oideachais_dlt_sources/ie/law/irish_statute_book.py:87`** — migrate `dlt.sources.incremental[int]` to `IncrementalCursorProvider[int]` and add a regression test for the **1.27.2 hotfix** (`merge` after `replace` on no-data incremental). This is the highest-risk code path we have against the 1.27+ release line.
