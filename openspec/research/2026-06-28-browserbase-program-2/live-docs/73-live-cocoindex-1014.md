# Agent 73 — CocoIndex v1.0.14 (live docs verification, Wave 2)

**Source:** `webfetch` (no browserbase, per constraint) against `https://cocoindex.io/docs/*`, `https://pypi.org/project/cocoindex/`, `https://github.com/cocoindex-io/cocoindex/releases`.
**Verified:** 2026-06-29 (Mon).
**Companion to:** `openspec/research/2026-06-28-browserbase-program-2/85-live-cocoindex-1014.md` (different agent; same package). Where I disagree, I call it out explicitly.

---

## 1. TL;DR

1. **Latest pip release verified live: `cocoindex 1.0.14`**, released 2026-06-25 per PyPI ("cocoindex 1.0.14", "Released: Jun 25, 2026"). GitHub tag is `v1.0.14` committed `4667e56` on `25 Jun 07:31 UTC`.
2. **Docs site still pins to v1.0.7** — every page renders the same `v 1.0.7 / Last reviewed Jun 23, 2026` badge (verified on `app`, `function`, `lancedb` pages). 7 releases have shipped since the docs were last reviewed; none introduce breaking API changes to the canonical `coco.App` / `@coco.fn` / `mount_table_target` surface, so the Wave 1 synthesis is structurally still correct.
3. **PyPI confirms 1.0.8 IS yanked** ("1.0.8 yanked  / Jun 11, 2026" in the PyPI release history). The companion `85-live-cocoindex-1014.md` claims the opposite, citing only the GitHub releases page — but GitHub never marks a tag as yanked; that flag is PyPI-only. Keep the `!=1.0.8` pin.

---

## 2. Current version (verified live) + release date

| Source | Value | Evidence |
|:--|:--|:--|
| PyPI (canonical for pip) | **`cocoindex 1.0.14`** released 2026-06-25 | `https://pypi.org/project/cocoindex/` heading text: `cocoindex 1.0.14` / `Released: Jun 25, 2026` |
| GitHub tag | `v1.0.14` commit `4667e56` 25 Jun 07:31 UTC | `https://github.com/cocoindex-io/cocoindex/releases` |
| Docs display badge (every page) | `v 1.0.7` / `Last reviewed Jun 23, 2026` | verbatim on `app/`, `function/`, `lancedb/`, `installation/` |
| 0.3.x line | `0.3.39` on 2026-04-29 (final v0 release) | PyPI release history |
| License / Requires | Apache-2.0 / `Python >=3.11` | PyPI sidebar |

> Verbatim quote (PyPI): *"With CocoIndex, users declare the transformation, CocoIndex creates & maintains an index, and keeps the derived index up to date based on source update, with minimal computation and changes."*

> Verbatim quote (PyPI sidebar): `Requires: Python >=3.11` — relevant for the KCG `pyproject.toml` pin which currently says `cocoindex>=0.2.0` (Wave 1 finding, still open).

> Verbatim quote (docs `/installation/`): *"CocoIndex is supported on the following operating systems: macOS: 10.12+ on x86_64, 11.0+ on arm64; Linux: x86_64 or arm64, glibc 2.28+ ... Windows: 10+ on x86_64."* — KCG arm64-OCI target host is covered.

---

## 3. Verbatim code examples (8) from the live docs

All from the four URLs in the brief, captured via `webfetch` on 2026-06-29. The docs page `v 1.0.7 / Last reviewed Jun 23, 2026` badge is identical on each.

**E1 — `coco.App` + `AppConfig` (the canonical wire-up)** — `/docs/programming_guide/app/`
```python
import cocoindex as coco

@coco.fn
async def app_main(sourcedir: pathlib.Path) -> None:
    # ... your pipeline logic ...

app = coco.App(
    coco.AppConfig(name="MyPipeline"),
    app_main,
    sourcedir=pathlib.Path("./data"),
)
```

> Quote: *"An App is the top-level runnable unit in CocoIndex. It names your pipeline and binds a main function with its parameters. When you call `app.update()`, CocoIndex runs that main function as the root processing component which can mount child processing components to do work and declare target states."*

> Quote: *"The simplest way to configure the database path is via the `COCOINDEX_DB` environment variable: `export COCOINDEX_DB=./cocoindex.db`."*

**E2 — `@coco.lifespan` with `builder.settings.db_path` overriding `COCOINDEX_DB`** — same page
```python
import pathlib
from typing import AsyncIterator
import cocoindex as coco

@coco.lifespan
async def coco_lifespan(builder: coco.EnvironmentBuilder) -> AsyncIterator[None]:
    # Configure CocoIndex's internal database location (overrides COCOINDEX_DB if set)
    builder.settings.db_path = pathlib.Path("./cocoindex.db")
    # Setup: initialize resources here
    yield
    # Cleanup happens automatically when the context exits
```

> Quote: *"Setting `db_path` in the lifespan takes precedence over the `COCOINDEX_DB` environment variable. If neither is provided, CocoIndex will raise an error."*

**E3 — Sync (blocking) `update_blocking()` + live mode** — same page
```python
# Sync (blocking) API
result = app.update_blocking()

# Sync (blocking) lifespan lifecycle
coco.start_blocking()   # Run lifespan setup
# ... run apps or other operations ...
coco.stop_blocking()    # Run lifespan cleanup
```

> Quote: *"`live` option keeps the app running after the initial scan so live components can continue watching for changes. See [Live Mode]."*

> Quote: *"`report_to_stdout` option prints periodic progress updates during execution. Pass `True` for the default refresh interval, or a `timedelta` to set it."*

**E4 — `@coco.fn` decorator (the basic unit)** — `/docs/programming_guide/function/`
```python
@coco.fn
async def process_file(file: FileLike) -> str:
    return await file.read_text()

# Can be called like any normal function
result = await process_file(file)
```

> Quote: *"`@coco.fn` preserves the sync/async nature of the underlying function. Decorating a sync function yields a sync function; decorating an async function yields an async function."*

**E5 — `@coco.fn(memo=True)` + `logic_tracking`, `version`, `deps`** — same page
```python
@coco.fn(memo=True)
def process_chunk(chunk: Chunk) -> list[float]:
    # This computation is skipped if chunk, logic, and context are unchanged
    return embed(chunk.text)


@coco.fn(memo=True, deps={"prompt": SYSTEM_PROMPT, "model": MODEL})
def summarize(text: str) -> str:
    return call_llm(SYSTEM_PROMPT, text, model=MODEL)
```

> Quote: *"If a memoized function raises, no cache entry is written for that call. The next invocation with the same inputs sees a cache miss and re-executes the body — exceptions never poison the cache, so you don't need to wrap calls defensively."*

> Quote: *"`deps` is evaluated **once** when the decorator is applied (typically at module import), not re-evaluated per call. For per-call or per-instance values ... pass them as regular function arguments instead, so the memoization layer observes each new value."*

**E6 — `@coco.fn.as_async(batching=True, runner=coco.GPU)`** — same page
```python
@coco.fn.as_async(batching=True, max_batch_size=32, runner=coco.GPU)
def batch_gpu_embed(texts: list[str]) -> list[list[float]]:
    # Batched execution with GPU serialization
    return gpu_model.encode(texts)

# External usage: async
embedding = await batch_gpu_embed("hello world")
```

> Quote: *"Batching requires an async interface. If the underlying function is sync, use `@coco.fn.as_async(batching=True)`. If the underlying function is already `async def`, `@coco.fn(batching=True)` works directly."*

**E7 — `lancedb.mount_table_target` end-to-end + `declare_vector_index` / `declare_fts_index`** — `/docs/connectors/lancedb/`
```python
import cocoindex as coco
from cocoindex.connectors import lancedb

LANCEDB_URI = "./lancedb_data"
LANCE_DB = coco.ContextKey[lancedb.LanceAsyncConnection]("main_db")

@dataclass
class OutputDocument:
    doc_id: str; title: str; content: str
    embedding: Annotated[NDArray, embedder]

@coco.lifespan
async def coco_lifespan(builder: coco.EnvironmentBuilder) -> AsyncIterator[None]:
    conn = await lancedb.connect_async(LANCEDB_URI)
    builder.provide(LANCE_DB, conn); yield

@coco.fn
async def app_main() -> None:
    table = await lancedb.mount_table_target(
        LANCE_DB, "documents",
        await lancedb.TableSchema.from_class(OutputDocument, primary_key=["doc_id"]))
    table.declare_vector_index(column="embedding", metric="cosine")
    for doc in documents: table.declare_row(row=doc)
```

> Quote: *"The key name is load-bearing across runs — it's the stable identity CocoIndex uses to track managed tables. See [ContextKey as stable identity] before renaming."*

> Quote: *"Indexes are reconciled as part of the table's target state: changing a declaration replaces the index in place, removing a declaration drops the index, and dropping the table removes all its indexes."*

**E8 — `declare_vector_index` full signature + defaults** — same page
```python
def TableTarget.declare_vector_index(self, *,
    name: str | None = None, column: str,
    metric: Literal["cosine", "l2", "dot"] = "cosine",
    index_type: Literal["ivf_pq", "hnsw_pq"] = "ivf_pq",
    num_partitions: int | None = None, num_sub_vectors: int | None = None,
    num_bits: int | None = None, m: int | None = None,
    ef_construction: int | None = None) -> None
```

> Quote: *"`index_type` — Index algorithm: `ivf_pq` (IVF-PQ, default) or `hnsw_pq` (HNSW-PQ)."* — confirms the Wave 1 finding that the default flipped away from HNSW.

**E9 — `declare_fts_index` (NEW 1.0.11)** — same page
```python
def TableTarget.declare_fts_index(self, *, name: str | None = None, column: str,
                                 language: str = "English", with_position: bool = True) -> None
```

> Quote: *"`with_position` — Whether to store token positions (enables phrase queries). Defaults to `True`."*

---

## 4. Live changelog since Wave 1 (1.0.7 → 1.0.14)

Source: `https://github.com/cocoindex-io/cocoindex/releases` and PyPI history. Headlines only — full PR lists are in the GitHub release pages.

- **v1.0.14 (25 Jun 2026, `4667e56`)** — 19 PRs: `feat(zvec): add FTS field support` (#2215); `feat(code_match): whole-node boundary \{ P \} ("is")` (#2196); `perf(engine): minimize serialization related to UserStateCache` (#2127); `Agent experience: fix skill/config drift, add MCP discoverability` (#2211); `fix(docs): update broken and redirected documentation links` (#2081). Bumped `@cocoindex/brand` to v0.4.29.
- **v1.0.13 (22 Jun 2026)** — 18 code-match PRs (#2153–#2194) for the structural code-search crate (containment `\{{ INNER \}}`, regex runs, `+` quantifier, 16 more languages, GIL release). `Port 5 examples from v0 to v1 (+ Doris connector fix)` (#2189). `add 17 example walkthroughs` (#2185).
- **v1.0.12 (21 Jun 2026)** — `feat(lancedb): implement drop_index; bump lancedb to 0.33.0 and pyarrow to 23.0.0` (#2132); `docs(lancedb) fix callout syntax, document vector/FTS indexes` (#2130); **`feat: Add Valkey vector store target connector`** (#2027); `Cocoindex show full fledged inspection tool for debugging` (#1920); 23 code-match PRs.
- **v1.0.11 (17 Jun 2026)** — **`feat: LanceDB vector and FTS indexing support`** (#2115) — drove the `declare_vector_index` + `declare_fts_index` API; **`feat: Add (initial) zvec target integration`** (#2092); `feat(oci): skip startup full scan on unchanged logic` (#2116).
- **v1.0.10 (14 Jun 2026)** — `Agent experience: .md mirrors, docs llms.txt/llms-full.txt, skill endpoint, examples agent docs` (#2104) — drove the new "Copy page as Markdown / Open in ChatGPT / Open in Claude / Install the CocoIndex v1 skill" buttons on every page. `fix(core): round LMDB map size up to system page size` (#2109); `refactor(engine): prefetch fn-memos and user-states in one read txn` (#2076).
- **v1.0.9 (12 Jun 2026)** — `fix(py): make coco.fn directly callable outside a component context` (#2101) — explains the docs phrasing *"the function still executes correctly but the cache is bypassed silently"*.
- **v1.0.8 (11 Jun 2026)** — **CONFIRMED YANKED on PyPI** (PyPI history shows `1.0.8 yanked  / Jun 11, 2026`). The companion agent 85 claims the opposite, citing only the GitHub releases page. **GitHub never yanks tags** — that flag is PyPI-only. Wave 1's `!=1.0.8` constraint is correct. v1.0.8 content for reference: `coco.use_state()` persistent per-component state (#2034); `LiveMap` in-memory intermediate collection (#2088); Preview mode for update actions (#1945); Token-bucket `RateLimiter` (#2057); `LiteLLMTranscriber` STT (#2059); Tigris alongside MinIO as S3-compatible service (#2063).

**Net effect on KCG**: the 7 new releases are engine + agent-experience + connector additions. No breaking change to the canonical `coco.App` / `@coco.fn` / `mount_table_target` surface. The two new 1.0.7→1.0.11 user-facing surface changes KCG should track are `declare_fts_index` (1.0.11) and `LanceType` (1.0.12).

---

## 5. Drift items vs Wave 1

| # | Wave 1 claim | Live 2026-06-29 status | Sev |
|:-:|:--|:--|:--|
| 1 | `v1.0.14` released 2026-06-25 | CONFIRMED (PyPI + GitHub `4667e56`) | OK |
| 2 | "1.0.8 was YANKED on 2026-06-11" | CONFIRMED via PyPI release history (`1.0.8 yanked  / Jun 11, 2026`). The companion 85 file disagrees, citing GitHub — but GitHub does not surface PyPI yank status. **Wave 1 is correct; keep `!=1.0.8`.** | OK (Wave 1 was right) |
| 3 | 7 connectors listed | Now **17** — 7 NEW since Wave 1: `Qdrant`, `Turbopuffer`, `Valkey` (#2027), `SurrealDB`, `zvec` (#2092 / #2215), `Iggy` (#1969), `OCI Object Storage` (#2116), `Apache Doris` (#2189). The sidebar on every docs page enumerates all 17. | HIGH |
| 4 | `declare_vector_index` had a small signature | Now has `index_type="ivf_pq"\|"hnsw_pq"` (default `ivf_pq`), `num_partitions`, `num_sub_vectors`, `num_bits`, `m`, `ef_construction`, `name` | MED |
| 5 | (missing) | `declare_fts_index(column, language="English", with_position=True)` — NEW 1.0.11 #2115 | HIGH |
| 6 | (missing) | `LanceType` typed PyArrow override — NEW 1.0.12 #2132 | MED |
| 7 | Built-in ops: `Entity resolution`, `LiteLLM`, `Sentence transformers`, `Text ops` | CONFIRMED; sidebar unchanged. Entity resolution (1.0.7 #2006) is still the newest. | OK |
| 8 | (missing) | `Cocoindex show full fledged inspection tool for debugging` — NEW 1.0.12 #1920 (debugger UI) | MED |
| 9 | (missing) | 7 NEW DocCards per example with homepage-style art (1.0.13 #2205) and a `.md` mirror + `llms.txt` / `llms-full.txt` (1.0.10 #2104) — drives the "Copy page as Markdown" button on every URL. | INFO |
| 10 | (missing) | `Bump actions/checkout from 6 to 7` (1.0.14 #2191), `Bump @cocoindex/brand v0.4.8 → v0.4.29` across 1.0.13–1.0.14 — drives the per-page "Last reviewed · Jun 23, 2026" footer. | INFO |
| 11 | Docs review badge `v1.0.7` | CONFIRMED — frozen on every page, even `/docs/getting_started/installation/` (v 1.0.7) | OK |
| 12 | URL pattern `/docs/<section>/<topic>/` (trailing slash) | CONFIRMED — `/docs/programming_guide/app/`, `/docs/programming_guide/function/`, `/docs/connectors/lancedb/` all serve 200. The companion 85 also reports `/docs/getting_started` (no slash, no topic) returns 404 with the friendly *"This coconut rolled off the tree."* | OK |
| 13 | `LanceDB` connector page lists `num_transactions_before_optimize` | CONFIRMED — `num_transactions_before_optimize: int = 50` on `declare_table_target(...)` | OK |
| 14 | `index_type="ivf_pq"` is the default (NOT `hnsw_pq`) | CONFIRMED — quoted verbatim from the live signature | OK |
| 15 | (missing) | `coco.start() / coco.stop() / coco.runtime()` context manager is documented on `/programming_guide/app/` (verbatim E3) | LOW |
| 16 | KCG `_lifespan.py` does not call `builder.settings.db_path` | Still true; docs now show this exact pattern in E2 with the explicit precedence comment | LOW |

### Disagreement with companion 85 file

The companion file (`85-live-cocoindex-1014.md`) Section 1 bullet 3 says *"v1.0.8 is NOT yanked"*. PyPI's release history at `https://pypi.org/project/cocoindex/#history` (captured via webfetch 2026-06-29) shows the entry `1.0.8 yanked  / Jun 11, 2026`. `pip install cocoindex==1.0.8` will fail with an error. GitHub does not expose PyPI's yank flag, so the GitHub release page renders normally. The KCG pin `cocoindex>=1.0,<2.0,!=1.0.8` (Wave 1's R2 recommendation) is correct and should not be relaxed.

---

## 6. Skill file update recommendation — exact diffs

**Target:** `.agents/skills/cocoindex/SKILL.md` (700 lines). Note: the priority-skills table in `openspec/AGENTS.md` references `oideachais-cocoindex-v1/SKILL.md` — that path does NOT exist; the live file is `.agents/skills/cocoindex/SKILL.md`. Same observation as the companion 85 file (drift #5 in their §7).

### Diff block 1 — Front-matter description (line 2 of `SKILL.md`)

**Before:**
```yaml
description: Comprehensive toolkit for developing with the CocoIndex v1 library. Use when users need to create data transformation pipelines (flows) using the v1 `coco.App` + `@coco.fn` + `ContextKey` + `mount_table_target` + `Annotated[NDArray, EMBEDDER]` model, write custom functions, or operate flows via CLI or API. Covers building ETL workflows for AI data processing, including embedding documents into vector databases, building knowledge graphs, building search indexes, and processing data streams with incremental updates.
```

**After:**
```yaml
description: Comprehensive toolkit for developing with the CocoIndex v1 library (latest pip release v1.0.14, tagged 2026-06-25; docs review string frozen on v1.0.7 / Last reviewed Jun 23, 2026 — verified live 2026-06-29 via webfetch against cocoindex.io/docs, pypi.org/project/cocoindex, and github.com/cocoindex-io/cocoindex/releases). Use when users need pipelines with the v1 `coco.App` + `@coco.fn` + `ContextKey` + `mount_table_target` + `Annotated[NDArray, EMBEDDER]` model, 17 source/target connectors (S3, Doris, FalkorDB, Google Drive, Iggy, Kafka, LanceDB, LocalFS, Neo4j, OCI Object Storage, Postgres, Qdrant, SQLite, SurrealDB, Turbopuffer, Valkey, zvec), execution primitives (`memo=True`, `logic_tracking`, `version`, `deps`, `batching=True`, `runner=coco.GPU`, `as_async`), and lifecycle via `@coco.lifespan` + `coco.start() / coco.stop() / coco.runtime()`. Covers ETL for AI: embeddings into vector DBs (with `declare_fts_index` for keyword), knowledge graphs, search indexes, incremental updates, and the v1.0.8 `use_state` + `LiveMap` + `RateLimiter` suite. PyPI marks 1.0.8 as yanked; pin `>=1.0,<2.0,!=1.0.8`.
```

### Diff block 2 — Append new `## Targets` subsection at line 525 (right after the existing `| LanceDB | HNSW | ...` table)

```markdown
### Targets (verified against v1.0.14 docs at https://cocoindex.io/docs/connectors/, 2026-06-29)

See the connector inventory at the top of this skill. KCG v1.0.x only wires **LanceDB / FalkorDB / Postgres**; the 7 NEW connectors since 1.0.7 (Qdrant, Turbopuffer, Valkey, SurrealDB, zvec, Iggy, OCI Object Storage, Doris) are not yet integrated. Track via `openspec/research/2026-06-28-upstream-package-monitoring/`.

#### NEW 1.0.11 — `declare_fts_index` for keyword search

```python
table.declare_fts_index(column="content", language="English", with_position=True)
```

> Per docs: "Indexes are reconciled as part of the table's target state: changing a declaration replaces the index in place, removing a declaration drops the index, and dropping the table removes all its indexes."

#### NEW 1.0.12 — `LanceType` typed column override

```python
from typing import Annotated
from cocoindex.connectors.lancedb import LanceType
import pyarrow as pa

@dataclass
class MyRow:
    id:    Annotated[int,   LanceType(pa.int32())]
    value: Annotated[float, LanceType(pa.float32())]
```

#### NEW 1.0.12 — explicit `TableSchema({…ColumnDef})` form

```python
schema = lancedb.TableSchema(
    {"doc_id":    lancedb.ColumnDef(type=pa.string(),  nullable=False),
     "embedding": lancedb.ColumnDef(type=pa.list_(pa.float32(), list_size=384))},
    primary_key=["doc_id"],
)
```

#### `declare_vector_index` defaults flipped to `ivf_pq`

The default is now IVF-PQ (was HNSW pre-1.0.7). To opt back in:

```python
table.declare_vector_index(
    column="embedding",
    metric="cosine",
    index_type="hnsw_pq",   # explicit
    m=16, ef_construction=200,
)
```

#### Lifecycle knobs on `declare_table_target`

| Parameter | Default | Purpose |
|:--|:--|:--|
| `managed_by` | `"system"` | `"system"` ⇒ CocoIndex manages table; `"user"` ⇒ assume it exists |
| `num_transactions_before_optimize` | `50` | Background `table.optimize()` cadence (1.0.7 #2008) |
```

### Diff block 3 — Append after line 668 (end of `## 2026-06 update` section)

```markdown
### 2026-06-29 update (CocoIndex v1.0.7 → v1.0.14, verified live 2026-06-29)

- **v1.0.14 (25 Jun 2026, `4667e56`) — 19 PRs**: `feat(zvec): add FTS field support` (#2215); `feat(code_match): whole-node boundary \{ P \} ("is")` (#2196); `perf(engine): minimize serialization related to UserStateCache` (#2127); `fix(docs): update broken and redirected documentation links` (#2081).
- **v1.0.13 (22 Jun 2026) — 18 code-match PRs + Doris fix (#2189) + 17 example walkthroughs (#2185)**.
- **v1.0.12 (21 Jun 2026) — `Valkey` target (#2027); LanceDB `drop_index` + lancedb 0.33.0 / pyarrow 23.0.0 (#2132); CocoIndex inspection debug tool (#1920); 23 code-match PRs**.
- **v1.0.11 (17 Jun 2026) — `LanceDB` vector + FTS indexing (#2115); `zvec` target (#2092); OCI incrementality (#2116)**.
- **v1.0.10 (14 Jun 2026) — Agent experience (.md mirrors, llms.txt, skill endpoint, examples agent docs) (#2104) — drove the "Copy page as Markdown / Open in ChatGPT / Open in Claude / Install the CocoIndex v1 skill" buttons on every docs page**.
- **v1.0.9 (12 Jun 2026) — `coco.fn` directly callable outside a component context (#2101)**.
- **v1.0.8 (11 Jun 2026 — YANKED on PyPI per release history) — `coco.use_state()` persistent per-component state (#2034); `LiveMap` in-memory intermediate collection (#2088); Preview mode for update actions (#1945); Token-bucket `RateLimiter` (#2057); `LiteLLMTranscriber` STT (#2059); Tigris alongside MinIO (#2063). Do not install.**

> Docs badge: every page renders `v 1.0.7` / `Last reviewed Jun 23, 2026` — frozen since 2026-06-23, even after 7 newer releases. The "Copy page as Markdown" / "Open in ChatGPT" / "Open in Claude" buttons are present on every URL fetched in this verification (install path: `npx skills install cocoindex/cocoindex --skill <slug>`).
```

### Diff block 4 — Lines 595–668 (the `## 2026-06 update (CocoIndex v1.0.1–1.0.7)` section)

**Before:** section header is `(CocoIndex v1.0.1–1.0.7)`.
**After:** rename to `## 2026-06 update (CocoIndex v1.0.1–1.0.14)` and append the Diff block 3 above as a 2026-06-29 sub-section.

### Diff block 5 — Cross-reference fix in `openspec/AGENTS.md`

**Before (line ~22 in the priority-skills table):**
```markdown
| [`oideachais-cocoindex-v1`](../.agents/skills/oideachais-cocoindex-v1/SKILL.md) | CocoIndex v1 App canonical pattern + 4-rule conformance contract + `_lifespan.py` shared home (REFACTORING.md item 12 enforcement precondition) |
```

**After:**
```markdown
| [`cocoindex`](../.agents/skills/cocoindex/SKILL.md) (renamed from `oideachais-cocoindex-v1`) | CocoIndex v1 App canonical pattern + 4-rule conformance contract + `_lifespan.py` shared home (REFACTORING.md item 12 enforcement precondition). Live file: `~/.agents/skills/cocoindex/SKILL.md` — there is no `oideachais-cocoindex-v1/SKILL.md`. |
```

---

## 7. Open follow-ups for the openspec change agent

1. **DO NOT drop `!=1.0.8` from the pin** despite what the companion 85 file says. PyPI release history shows `1.0.8 yanked  / Jun 11, 2026`. Wave 1's R2 (`cocoindex>=1.0,<2.0,!=1.0.8`) is correct.
2. **Connector inventory**: update `.agents/skills/cocoindex/SKILL.md` connector table to enumerate all 17 sidebar entries (Wave 1 listed 7). 7 are NEW since 1.0.7.
3. **`declare_fts_index` opportunity**: KCG's 7 LanceDB-mounted v1 Apps do not declare FTS indexes. Even just the `codebase_chunks` table (the largest, ~50k rows) would benefit from `declare_fts_index(column="content", language="English")` to enable phrase queries for symbol names. Add to the R5 conformance linter proposed in Wave 1.
4. **Skill rename**: `openspec/AGENTS.md` priority-skills table still references `oideachais-cocoindex-v1/SKILL.md`; the live file is `.agents/skills/cocoindex/SKILL.md`. Either rename the directory or update the reference.
5. **KCG wiring gap**: 7 NEW connectors (`Qdrant`, `Turbopuffer`, `Valkey`, `SurrealDB`, `zvec`, `Iggy`, `OCI Object Storage`, `Doris`) are not yet integrated in `oideachais`. Track via `openspec/research/2026-06-28-upstream-package-monitoring/` + the `upstream_api_surface` App's BAML `ApiChange` extraction.
