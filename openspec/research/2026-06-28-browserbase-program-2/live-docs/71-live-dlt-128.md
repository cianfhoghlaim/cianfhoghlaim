# 71 — dlt 1.28.1 Live-Docs Verification

> Agent 71, BrowserBase program 2. Target: dlt (Data Load Tool).
> Verified via `webfetch` against `dlthub.com/docs`, `pypi.org/project/dlt/`,
> and `github.com/dlt-hub/dlt/releases` on 2026-06-29. No browserbase credits
> consumed.

## 1. TL;DR

- **dlt 1.28.1 is the current PyPI release** (Jun 19, 2026); drops Python 3.9
  and ships a dashboard default + 5 hotfixes over 1.28.0.
- Wave 2 (1.27.0 → 1.28.1) added **native Polars, Lance destination,
  Databricks Zerobus, dlt.Relation.join, multischema datasets, refresh>replace,
  write_encoding**, and **yanked both 1.27.0 and 1.27.1** for a data-loss bug
  (fixed in 1.27.2).
- Wave 1 SKILL.md is drifted in **6 places** — "5,000+ sources" → "8,000+",
  the `workspace` extra no longer exists (now `dlt[hub]`), `dlt ai` is now
  `dlthub ai`, the `replace` switch is deprecated for `refresh`, Python 3.9 is
  EOL, and Lance + Polars native are not mentioned.

## 2. Current version (verified live)

| Source | Version | Released | URL pattern |
|---|---|---|---|
| PyPI project page | **1.28.1** | **Jun 19, 2026** | `https://pypi.org/project/dlt/` |
| dlthub.com docs header | **1.28.1 (latest)** | — | `https://dlthub.com/docs/intro` |
| GitHub releases | **1.28.1** (`0955489`) | 19 Jun 19:48 | `https://github.com/dlt-hub/dlt/releases/tag/1.28.1` |

Verbatim quote (PyPI): **"dlt 1.28.1 — Latest release — Released: Jun 19,
2026 — Requires: Python <3.15, >=3.10"**.

Verbatim quote (dlthub.com/docs/intro): **"Version: 1.28.1 (latest) — To get
started with dlt, install the library using pip: `pip install dlt`"**.

Verbatim quote (GitHub release page): **"1.28.1 — 19 Jun 19:48 — Released 19
Jun 2026 — This commit was created on GitHub.com and signed with GitHub's
verified signature"**.

PyPI release history (May 2025 → Jun 2026 — selected):

| Version | Date | Status |
|---|---|---|
| 1.28.1 | Jun 19, 2026 | latest |
| 1.28.0 | Jun 15, 2026 | stable |
| 1.27.2 | May 29, 2026 | stable (hotfix) |
| 1.27.1 | May 27, 2026 | **yanked** — data-loss bug |
| 1.27.0 | May 18, 2026 | **yanked** — data-loss bug |
| 1.26.0 | Apr 28, 2026 | stable |
| 1.25.0 | Apr 15, 2026 | stable (multischema + lance) |

Yank notice verbatim (PyPI): **"Reason this release was yanked: Data-loss
bug: incremental merge truncates the destination table. Fixed in 1.27.2"** —
applies to **both 1.27.0 and 1.27.1**.

## 3. Verbatim code examples (extracted live)

All five below were copied verbatim from `https://dlthub.com/docs/intro` on
2026-06-29. (URL pattern observed: `https://dlthub.com/docs/intro.md` is the
"View Markdown" link in the docs sidebar.)

### 3.1 REST API source

```python
import dlt
from dlt.sources.rest_api import rest_api_source

source = rest_api_source({
    "client": {
        "base_url": "https://api.example.com/",
        "auth": {"token": dlt.secrets["your_api_token"]},
        "paginator": {"type": "json_link", "next_url_path": "paging.next"},
    },
    "resources": ["posts", "comments"],
})
pipeline = dlt.pipeline(
    pipeline_name="rest_api_example",
    destination="duckdb",
    dataset_name="rest_api_data",
)
load_info = pipeline.run(source)
print(load_info)
print(pipeline.dataset().posts.df())
```

### 3.2 SQL database source

```python
from dlt.sources.sql_database import sql_database

source = sql_database("mysql+pymysql://rfamro@mysql-rfam-public.ebi.ac.uk:4497/Rfam")
pipeline = dlt.pipeline(
    pipeline_name="sql_database_example",
    destination="duckdb",
    dataset_name="sql_data",
)
load_info = pipeline.run(source)
print(load_info)
print(pipeline.dataset().family.df())
```

### 3.3 Filesystem source

```python
from dlt.sources.filesystem import filesystem

resource = filesystem(bucket_url="s3://example-bucket", file_glob="*.csv")
pipeline = dlt.pipeline(
    pipeline_name="filesystem_example",
    destination="duckdb",
    dataset_name="filesystem_data",
)
load_info = pipeline.run(resource)
print(load_info)
print(pipeline.dataset().example.df())
```

### 3.4 Python generator resource (canonical "hello world")

```python
import dlt

@dlt.resource(table_name="foo_data")
def foo():
    for i in range(10):
        yield {"id": i, "name": f"This is item {i}"}

pipeline = dlt.pipeline(pipeline_name="python_data_example", destination="duckdb")
load_info = pipeline.run(foo)
print(load_info)
print(pipeline.dataset().foo_data.df())
```

### 3.5 PyPI Quick Start (chess.com → duckdb)

```python
import dlt
from dlt.sources.helpers import requests

pipeline = dlt.pipeline(
    pipeline_name='chess_pipeline',
    destination='duckdb',
    dataset_name='player_data'
)
data = []
for player in ['magnuscarlsen', 'rpragchess']:
    response = requests.get(f'https://api.chess.com/pub/player/{player}')
    response.raise_for_status()
    data.append(response.json())
pipeline.run(data, table_name='player')
```

### 3.6 1.27.0 native Polars (verbatim from release notes)

> "Polars DataFrames and LazyFrames can now be yielded directly from
> `@dlt.resource` without manual conversion. Auto-detected and routed through
> the Arrow extraction pipeline; LazyFrames are auto-collected before
> conversion."

```python
import polars as pl
import dlt

@dlt.resource
def users_lazy():
    return pl.scan_parquet("s3://bucket/users/*.parquet")  # LazyFrame
```

## 4. Live changelog since Wave 1 (dlt 1.27+)

### 1.28.1 (Jun 19, 2026) — `0955489`

- **Dropped Python 3.9** (#4074, EOL 2025-10-31); **dataset browser default
  in dashboard** (#4068); fixes for connectorx temporal precision (#3996),
  ISO week/year in `detect_datetime_format` (#4061), postgres 0x0 chars
  (#4086), `sql_database` metadata caching (#4067), codex skill desc 1024
  cap (#4072). CI: 27 parallel jobs, Python 3.14 enabled, `blacksmith-*`.

### 1.28.0 (Jun 15, 2026) — `7901349`

**Breaking:** `refresh="drop_data"` no longer frees Delta/Iceberg storage
(transactional delete; explicit `vacuum` needed); `replace` now truncates
empty / orphaned tables (nested, dynamic, variant).

**Highlights:** Lance write optimizations (namespace pooling, atomic single-
commit `Overwrite`, `ExpiredToken` fix); **`refresh` > `replace`** (switch
deprecated); `write_encoding` (`utf-8-sig`, `latin-1`, `cp1252`);
refreshable cloud credentials; **DuckDB 1.5.3**, **DuckLake 1.0**; `REFRESH
auto` for DuckDB credential chain (#4021); `Retry-After: 0` no longer loops.

### 1.27.2 (May 29, 2026) — `18fc91f` (hotfix)

> "Hotfix: fixes #3998 (`merge` with empty data after `replace` on
> incremental truncates the destination table). Upgrade for anyone on
> 1.27.0/1.27.1." **Both 1.27.0 and 1.27.1 YANKED from PyPI.**

### 1.27.0 (May 19, 2026) — `6f570c7` (YANKED)

**Breaking:** `workspace` extra removed; `dlthub` command split out — dev
tooling (`dlt dashboard`, `dlt pipeline ... show`, `dlt pipeline ... mcp`)
now requires `pip install dlt[hub]`. `dlt ai` → `dlthub ai`.

**Highlights:** Native Polars DataFrame / LazyFrame in `@dlt.resource`
(#3837); Databricks Zerobus — `databricks_adapter(..., insert_api="zerobus")`
(#3904); incremental filtering on `dlt.Relation` (#3889); `lance` REST
Namespace experimental (#3908); `-y` / `--yes` `ALWAYS_CONFIRM` flag
(#3910); Pydantic 2.13 annotation metadata handling (#3863).

### 1.26.0 (Apr 28, 2026) — `b3fc4a9`

**Breaking:** incremental external scheduler now **raises** (`JoinSchedulerError`
/ `ExternalSchedulerNotAvailable`) instead of silently warning (#3877).
`dlt.Relation.join(...)` (#3590); `dlt.current.interval()` returns active
`(start, end)` with `allow_external_schedulers` override (#3877); extended
Snowflake `TQueryTags` with `operation` field beyond load jobs (#3759).

### 1.25.0 (Apr 15, 2026) — `a50ab06`

**Breaking:** **Multischema datasets** — pass list to `dataset()` (or
`pipeline.default_schema` to revert). `lance` destination (local + s3/az/gs,
branching, optional `lancedb` embeddings) (#3810); load metrics persist
across restarts (#3768).

## 5. Drift items vs Wave 1 SKILL.md

The Wave 1 SKILL.md (`.agents/skills/dlt/SKILL.md`, 312 lines) was last
synthesised when dlt was on the **1.20.x / 1.21.x** track. Drift summary:

| # | Wave 1 text | Wave 2 reality | Status |
|---|---|---|---|
| 1 | "5,000+ sources" (appears 2×) | dlthub.com/docs/intro: **"8,000+ sources"** (and "10k+ AI Context assets" in sidebar) | **stale** |
| 2 | `dlt dashboard` / `dlt pipeline ... show` / `dlt pipeline ... mcp` mentioned as part of core CLI | 1.27.0: **"require `pip install dlt[hub]`"** | **stale** |
| 3 | `dlt ai` is referenced as a dlt command | 1.27.0: **"`dlt ai` was moved to `dlthub ai`"** | **stale** |
| 4 | No mention of **Lance destination** | 1.25.0 added a first-class `lance` destination; 1.27.0 added REST Namespace | **missing** |
| 5 | No mention of **Polars native** in resources | 1.27.0 added Polars DataFrame/LazyFrame in `@dlt.resource` | **missing** |
| 6 | No mention of **`dlt.Relation.join(...)`** or **`dlt.current.interval()`** | 1.26.0 added both | **missing** |
| 7 | No mention of **Databricks Zerobus** | 1.27.0: `databricks_adapter(..., insert_api="zerobus")` | **missing** |
| 8 | `write_disposition="replace"` used freely | 1.28.0: **"the `replace` switch is deprecated. Use `refresh`"** | **stale** |
| 9 | No mention of **Python 3.9 EOL** | 1.28.1: **"Dropped Python 3.9 support"**; `requires-python = ">=3.10, <3.15"` | **stale** |
| 10 | `dlt.Relation` mentioned generically | 1.27.0 added incremental filtering on `dlt.Relation`; 1.26.0 added `join(...)` | **stale** |

## 6. Skill file update recommendation (`.agents/skills/dlt/SKILL.md`)

Four targeted diffs. Apply as a single `openspec` change
(`update-dlt-skill-to-1.28.1`).

### Change A — frontmatter description

```diff
- description: Master routing skill for data load tool (dlt). Use this to understand dlt rules, decide which sub-skill to invoke, and apply the Cianfhoghlaim dlt conventions (DuckLake/DuckDB destination, USE_LOCAL_SCRAPES offline fallback, relative imports only, type-safe BAML-driven pipelines, multi-destination fan-out to LanceDB / Memgraph / Graphiti, and Dagster dlt_assets wrapping).
+ description: Master routing skill for data load tool (dlt 1.28.1, June 2026). Use this to understand dlt rules, decide which sub-skill to invoke, and apply the Cianfhoghlaim dlt conventions (DuckLake/DuckDB destination, USE_LOCAL_SCRAPES offline fallback, relative imports only, type-safe BAML-driven pipelines, multi-destination fan-out to LanceDB / Memgraph / Graphiti, and Dagster dlt_assets wrapping). Notes the 1.27 `dlt[hub]` plugin split and the 1.28 `refresh` > `replace` deprecation.
```

### Change B — new §1.1 "Live version" block (after §1)

```markdown
## 1.1 Live version (verified 2026-06-29)

- **Latest**: `dlt 1.28.1` (released **Jun 19, 2026**) on PyPI.
- **Python**: `requires-python = ">=3.10, <3.15"` — Python 3.9 dropped in
  1.28.1; Python 3.14 supported (experimental).
- **Source count**: **8,000+ sources** (was 5,000+ in Wave 1).
- **Yanked**: 1.27.0 and 1.27.1 — data-loss bug ("incremental merge
  truncates destination table"). Pin `dlt>=1.27.2,<1.28` if you must, or
  upgrade to 1.28.1.
- **CLI split (1.27.0)**: `pip install dlt[hub]` is now required for
  `dlt dashboard`, `dlt pipeline ... show`, `dlt pipeline ... mcp`. `dlt ai`
  is now `dlthub ai`.
- **`refresh` > `replace` (1.28.0)**: the `replace` write-disposition
  switch is deprecated; use the `refresh` parameter instead.
- **Lance destination (1.25.0)** + **Lance REST Namespace (1.27.0)**: a
  `lance` destination now exists alongside `lancedb` — use the former
  for local/S3/Az/GCS Lance files, the latter for LanceDB Cloud.
- **Native Polars (1.27.0)**: `@dlt.resource` can yield Polars DataFrame
  or LazyFrame directly (auto-routed through Arrow).
- **Databricks Zerobus (1.27.0)**: `databricks_adapter(...,
  insert_api="zerobus")`.
- **`dlt.Relation.join(...)` (1.26.0)** and **`dlt.current.interval()`
  (1.26.0)** for relational composition and time-windowed incrementals.
```

### Change C — extend §4 anti-patterns

```diff
  ❌ **Don't**:
  - Fetch all data in a single `fetch_all()` call (OOM risk for > 1M rows)
  - Use `write_disposition="merge"` without a `primary_key` (silently
    appends duplicates)
  - Import `oideachais.data_platform.dlt_sources` from within
    `sruth/oideachais/` (use relative imports)
  - Hand-write DDL for the destination (let dlt infer the schema from
    the resource yield)
  - Run live web scraping without `USE_LOCAL_SCRAPES=true` first
    (drains API credits and risks rate limits)
  - Add a BAML client inline in a function (use a named client in
    `baml_src/clients.baml`)
+ - Pin `dlt==1.27.0` or `dlt==1.27.1` — both YANKED from PyPI for a
+   data-loss bug; the fix is 1.27.2 (or upgrade to ≥ 1.28.1).
+ - Use `write_disposition="replace"` (deprecated in 1.28.0) — use the
+   `refresh` parameter instead.
+ - Call `dlt ai ...` (moved to `dlthub ai ...` in 1.27.0).
+ - Call `dlt dashboard` without `pip install dlt[hub]` (1.27.0 split).
```

### Change D — add a verified-sources bullet in §2

```diff
  - **`dlt-init-openapi`** (3rd-party): Use to auto-generate a verified
    dlt source from any OpenAPI spec
+ - **`dlt init <verified-source>`** (1.28+ recommended): For any of the
+   28 verified sources listed at
+   `https://dlthub.com/docs/dlt-ecosystem/verified-sources` (Airtable,
+   GitHub, Stripe, Notion, Postgres replication, MongoDB, Salesforce,
+   HubSpot, Kafka, Slack, etc.). Verified sources are downloaded into
+   the working directory.
```

No other file edits are required. The existing `references/` index
(`destinations-lancedb.md`, `dagster-dlt-assets.md`, `type-safe-pipeline.md`,
etc.) is still correct because those sub-patterns were all GA before Wave 1
and remain GA in 1.28.1.

## 7. URLs verified

- `https://dlthub.com/docs/intro` — header "1.28.1 (latest)"
- `https://dlthub.com/docs/dlt-ecosystem/verified-sources` — 28 verified
  sources indexed; sidebar advertises **"10k+ AI Context assets"** vs the
  **"8,000+ sources"** in the intro paragraph
- `https://pypi.org/project/dlt/` — latest = 1.28.1, released Jun 19, 2026
- `https://github.com/dlt-hub/dlt/releases/tag/1.28.1` — commit `0955489`
- `https://github.com/dlt-hub/dlt/releases/tag/1.28.0` — commit `7901349`
- `https://github.com/dlt-hub/dlt/releases/tag/1.27.2` — hotfix `18fc91f`

Real URL pattern observed: **`https://dlthub.com/docs/intro.md`** — the
"View Markdown" link in the docs sidebar (canonical Markdown source for the
intro page).
