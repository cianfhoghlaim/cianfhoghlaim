# Agent 85 — CocoIndex v1.0.14 (live docs verification, Wave 2)

**Source:** `https://cocoindex.io/docs/*` (live, `last-modified: Fri, 26 Jun 2026 06:51:05 GMT` on every page) + `https://github.com/cocoindex-io/cocoindex/releases`.
**Verified:** 2026-06-29 (Mon) 01:17–01:19 UTC (Browserbase sessions `31918973-…` and `451e55f8-…`; 6 navigates, 5 extracts).
**Per-page badge:** every docs page renders `v 1.0.7` / `Last reviewed Jun 23, 2026` — the review string is frozen even though 7 newer releases ship on GitHub.

---

## 1. TL;DR

1. **Latest pip release verified live: `v1.0.14`** tagged `25 Jun 07:31 UTC` on GitHub (`/cocoindex-io/cocoindex/releases/tag/v1.0.14`, commit `4667e56`).
2. **Docs site still reviews against v1.0.7** — docs review string is frozen; HTTP `last-modified` confirms a full site rebuild on 2026-06-26 (one day after 1.0.14 cut). The 7 newer releases are docs-light (engine + code-match + brand/agent-experience polish), so Wave 1's core-API synthesis is structurally still correct.
3. **`v1.0.8` is NOT yanked.** Wave 1's `agent-03-cocoindex.md` says "`1.0.8` was YANKED on 2026-06-11" — verified live 2026-06-29: full release page renders (commit `6080d89`) with no `yanked` flag. Recommend removing that claim.

---

## 2. Current version (verified live) + release date

| Source | Value | Evidence |
|:--|:--|:--|
| GitHub (canonical) | **`v1.0.14` — 25 Jun 07:31 UTC** | `https://github.com/cocoindex-io/cocoindex/releases` heading text: `## v1.0.14  25 Jun 07:31` |
| Diff | `compare/v1.0.13...v1.0.14` — 19 PRs | live |
| Docs display badge | `v 1.0.7` / `Last reviewed Jun 23, 2026` | identical on every page |
| HTTP `last-modified` | `Fri, 26 Jun 2026 06:51:05 GMT` (all pages) | site rebuilt in one batch |
| Old `/docs/getting_started` (no slash) | **`404`** — *"This coconut rolled off the tree."* PRO TIP *"Incremental indexing can't find what was never indexed."* | `cf-ray a13117b13c3f87ab` `status:404` |
| Real URL pattern | `https://cocoindex.io/docs/<section>/<topic>/` (always trailing slash) | verified on `/docs/connectors/lancedb/`, `/docs/advanced_topics/memoization_keys/`, `/docs/ops/entity_resolution/`, `/docs/common_resources/live_map/` |

---

## 3. Verbatim code examples from the live docs (10)

All quoted from pages with HTTP `last-modified: Fri, 26 Jun 2026 06:51:05 GMT`.

**Q1 — `coco.App` (both forms)** — `/docs/programming_guide/app/`
```python
import cocoindex as coco
@coco.fn
async def app_main(sourcedir: pathlib.Path) -> None: ...
app = coco.App(
    coco.AppConfig(name="MyPipeline"),
    app_main,
    sourcedir=pathlib.Path("./data"),
)
# string-shorthand (equivalent):
app = coco.App("MyPipeline", app_main, sourcedir=pathlib.Path("./data"))
```

> "You can also pass just a name string instead of `AppConfig`."

**Q2 — Lifespan + `COCOINDEX_DB` env precedence** — same page
```python
import pathlib
from typing import AsyncIterator
import cocoindex as coco
@coco.lifespan
async def coco_lifespan(builder: coco.EnvironmentBuilder) -> AsyncIterator[None]:
    # Configure CocoIndex's internal database location (overrides COCOINDEX_DB if set)
    builder.settings.db_path = pathlib.Path("./cocoindex.db")
    yield
    # Cleanup happens automatically when the context exits
```
> "Setting `db_path` in the lifespan takes precedence over the `COCOINDEX_DB` environment variable. If neither is provided, CocoIndex will raise an error."

**Q3 — `@coco.fn(memo=True)`** — `/docs/programming_guide/function/`
```python
@coco.fn(memo=True)
def process_chunk(chunk: Chunk) -> list[float]:
    # Skipped if chunk, logic, and context are unchanged
    return embed(chunk.text)
```
> "If a memoized function raises, no cache entry is written for that call. The next invocation with the same inputs sees a cache miss and re-executes the body — exceptions never poison the cache, so you don't need to wrap calls defensively."

**Q4 — `deps=` snapshotted at decoration time** — same page
```python
SYSTEM_PROMPT = "You are a helpful assistant. Be concise."
MODEL = "claude-haiku-4-5"
@coco.fn(memo=True, deps={"prompt": SYSTEM_PROMPT, "model": MODEL})
def summarize(text: str) -> str:
    return call_llm(SYSTEM_PROMPT, text, model=MODEL)
```
> "`deps` is evaluated **once** when the decorator is applied (typically at module import), not re-evaluated per call. For per-call or per-instance values — instance attributes in a bound method, request-scoped config, anything that changes at runtime — pass them as regular function arguments instead."

**Q5 — `@coco.fn.as_async(batching=True)`** — same page
```python
@coco.fn.as_async(batching=True, max_batch_size=32)
def embed(texts: list[str]) -> list[list[float]]:
    return model.encode(texts)

embedding = await embed("hello world")   # list[float]
embeddings = await asyncio.gather(embed("text1"), embed("text2"), embed("text3"))
```

**Q6 — `lancedb.mount_table_target` end-to-end** — `/docs/connectors/lancedb/`
```python
import cocoindex as coco
from cocoindex.connectors import lancedb

LANCEDB_URI = "./lancedb_data"
LANCE_DB = coco.ContextKey[lancedb.LanceAsyncConnection]("main_db")

@dataclass
class OutputDocument:
    doc_id: str
    title: str
    content: str
    embedding: Annotated[NDArray, embedder]

@coco.lifespan
async def coco_lifespan(builder: coco.EnvironmentBuilder) -> AsyncIterator[None]:
    conn = await lancedb.connect_async(LANCEDB_URI)
    builder.provide(LANCE_DB, conn)
    yield

@coco.fn
async def app_main() -> None:
    table = await lancedb.mount_table_target(
        LANCE_DB,
        "documents",
        await lancedb.TableSchema.from_class(OutputDocument, primary_key=["doc_id"]),
    )
    table.declare_vector_index(column="embedding", metric="cosine")
    for doc in documents:
        table.declare_row(row=doc)
```
> "The key name is load-bearing across runs — it's the stable identity CocoIndex uses to track managed tables."

**Q7 — `declare_vector_index` full signature (NEW: `index_type="ivf_pq"`, `m`, `ef_construction`)** — same page
```python
def TableTarget.declare_vector_index(
    self, *,
    name: str | None = None,
    column: str,
    metric: Literal["cosine", "l2", "dot"] = "cosine",
    index_type: Literal["ivf_pq", "hnsw_pq"] = "ivf_pq",   # NEW DEFAULT
    num_partitions: int | None = None,
    num_sub_vectors: int | None = None,
    num_bits: int | None = None,
    m: int | None = None,                                  # HNSW-PQ only
    ef_construction: int | None = None,                   # HNSW-PQ only
) -> None
```
> "Parameters left as `None` fall back to LanceDB's defaults."

**Q8 — `LanceType` typed override (NEW 1.0.12)** — same page
```python
from typing import Annotated
from cocoindex.connectors.lancedb import LanceType
import pyarrow as pa
@dataclass
class MyRow:
    id:    Annotated[int,   LanceType(pa.int32())]
    value: Annotated[float, LanceType(pa.float32())]
```

**Q9 — `declare_fts_index` (NEW 1.0.11)** — same page
```python
def TableTarget.declare_fts_index(
    self, *,
    name: str | None = None,
    column: str,
    language: str = "English",
    with_position: bool = True,
) -> None
```
> "Indexes are reconciled as part of the table's target state: changing a declaration replaces the index in place, removing a declaration drops the index, and dropping the table removes all its indexes."

**Q10 — PDF → Markdown quickstart** — `/docs/getting_started/quickstart/`
```python
import pathlib
import cocoindex as coco
from cocoindex.connectors import localfs
from cocoindex.resources.file import PatternFilePathMatcher

@coco.fn(memo=True)
def process_file(file: localfs.File, outdir: pathlib.Path) -> None:
    markdown = _converter.convert(file.file_path.resolve()).document.export_to_markdown()
    outname = file.file_path.path.stem + ".md"
    localfs.declare_file(outdir / outname, markdown, create_parent_dirs=True)

@coco.fn
async def app_main(sourcedir: pathlib.Path, outdir: pathlib.Path) -> None:
    files = localfs.walk_dir(
        sourcedir,
        recursive=True,
        path_matcher=PatternFilePathMatcher(included_patterns=["**/*.pdf"]),
    )
    await coco.mount_each(process_file, files.items(), outdir)

app = coco.App("PdfToMarkdown", app_main,
               sourcedir=pathlib.Path("./pdf_files"),
               outdir=pathlib.Path("./out"))
```

CLI: `cocoindex update main.py` (batch) or `cocoindex update -L main.py` (live).

---

## 4. Live changelog entries since Wave 1 (1.0.7 → 1.0.14)

All bullets verbatim from `https://github.com/cocoindex-io/cocoindex/releases`.

- **v1.0.14 (25 Jun 2026, `4667e56`)** — 19 PRs: `feat(zvec): add FTS field support to zvec target connector` (#2215); `feat(code_match): whole-node boundary \{ P \} ("is")` (#2196); `perf(engine): minimize serialization related to UserStateCache` (#2127); `Agent experience: fix skill/config drift, add MCP discoverability` (#2211); `fix(docs): update broken and redirected documentation links` (#2081); +11 docs/brand PRs.
- **v1.0.13 (22 Jun 2026)** — 18 `feat(code_match)` / `perf(code_match)` PRs (#2153–#2194) — structural code-search crate, 16 languages, `+` quantifier, regex runs, containment `\{{ INNER \}}`; `Port 5 examples from v0 to v1 (+ Doris connector fix)` (#2189).
- **v1.0.12 (21 Jun 2026)** — `LanceDB improvements: docs(lancedb) fix callout syntax, document vector/FTS indexes, tighten prose` (#2130); `feat(lancedb): implement drop_index; bump lancedb to 0.33.0 and pyarrow to 23.0.0` (#2132); `feat: Add Valkey vector store target connector` (#2027); 23 code-match PRs.
- **v1.0.11 (17 Jun 2026)** — `feat: LanceDB vector and FTS indexing support` (#2115) — the implementation behind `declare_vector_index` + `declare_fts_index`; `feat(zvec): Add (initial) zvec target integration` (#2092); `feat(oci): skip startup full scan on unchanged logic` (#2116).
- **v1.0.10 (14 Jun 2026)** — `Agent experience: .md mirrors, docs llms.txt/llms-full.txt, skill endpoint, examples agent docs` (#2104) — drove the new "Copy page as Markdown / Open in ChatGPT / Claude / Install the CocoIndex v1 skill" buttons on every page; `fix(core): round LMDB map size up to system page size` (#2109); `refactor(engine): prefetch fn-memos and user-states in one read txn` (#2076).
- **v1.0.9 (12 Jun 2026)** — `fix(py): make coco.fn directly callable outside a component context` (#2101) — drove the docs phrasing "the function still executes correctly but the cache is bypassed silently".
- **v1.0.8 (11 Jun 2026 — NOT YANKED)** — `coco.use_state()` persistent per-component user-defined state (#2034); `LiveMap` in-memory intermediate collection (#2088); Preview mode (#1945); Token-bucket `RateLimiter` (#2057); `LiteLLMTranscriber` speech-to-text (#2059); Tigris alongside MinIO (#2063).

> Wave 1's claim "`1.0.8` was YANKED on 2026-06-11" is **WRONG** — verified live 2026-06-29: full release page renders, no `yanked` badge.

---

## 5. Drift items vs Wave 1 text synthesis

| # | Wave 1 claim | Live 2026-06-29 status | Sev |
|:-:|:--|:--|:--|
| 1 | `v1.0.14` released 2026-06-25 | CONFIRMED (commit `4667e56`) | OK |
| 2 | "`1.0.8` was YANKED on 2026-06-11" | INCORRECT — full release page renders | MED |
| 3 | 7 connectors | Now 17 — 7 NEW: Qdrant, Turbopuffer, Valkey, SurrealDB, zvec, Iggy, OCI Object Storage + Apache Doris | HIGH |
| 4 | `declare_vector_index(column, metric)` only | Now `index_type="ivf_pq"\|"hnsw_pq"` (default `ivf_pq`) + `num_partitions/num_sub_vectors/num_bits/m/ef_construction/name` | MED |
| 5 | (missing) | `declare_fts_index(column=…, language="English", with_position=True)` (NEW 1.0.11) | HIGH |
| 6 | (missing) | `LanceType` typed override; `VectorSchemaProvider` annotation; `TableSchema({…ColumnDef})` explicit form | MED |
| 7 | Built-in ops: LiteLLM, Sentence transformers, Text ops | Now 4 — adds `Entity resolution` (1.0.7 #2006) | MED |
| 8 | Advanced topics: 5 entries | Now 7 — adds `Memoization keys`, `Multiple environments`, `Custom target connector` | HIGH |
| 9 | (missing) | `/docs/common_resources/live_map/` (1.0.8 `LiveMap`) | MED |
| 10 | `memo_key` excludes param from key | CONFIRMED via `/advanced_topics/memoization_keys/` (the `/programming_guide/function/` page only paraphrases) | LOW |
| 11 | (missing) | Each docs page carries a "Copy skill install" button (per 1.0.10 #2104) | LOW |
| 12 | `/docs/getting_started` URL pattern | 404 — canonical is `/docs/getting_started/overview/` or `…/installation/` | HIGH |
| 16 | (missing) | Every page now carries an `Open in Claude` button with embedded prompt: "*Note: CocoIndex v1 is a redesign from v0; ignore any v0 flow-builder DSL or deprecated APIs.*" | INFO |
| 13 | Docs review badge `v1.0.7` | CONFIRMED — frozen on every page | OK |
| 14 | (missing) | HTTP `last-modified: Fri, 26 Jun 2026 06:51:05 GMT` (all pages) | INFO |
| 15 | (missing) | `coco.start() / coco.stop() / coco.runtime()` context manager (new in app.md) | LOW |

---

## 6. Skill file update recommendation — exact diffs

**Target:** `.agents/skills/cocoindex/SKILL.md` (700 lines). Note: `openspec/AGENTS.md` references `oideachais-cocoindex-v1/SKILL.md` — that path does NOT exist; the live file is `.agents/skills/cocoindex/SKILL.md`. Recommend cross-linking.

### Diff block 1 — Lines 30–32 (Targets table; stale 8-row inventory)
**Before:** the 8-row `| LanceDB | HNSW | Postgres+pgvector | Qdrant | Turbopuffer | Neo4j | FalkorDB | Kafka | localfs |` table.

**After (replace with this 12-row superset):**
```markdown
| Connector | Direction | Index support | Added in |
|:--|:--|:--|:--|
| `LanceDB` | target | vector (ivf_pq default; hnsw_pq opt-in) + FTS (1.0.11) | v1.0.0; FTS in 1.0.11 #2115 |
| `Postgres+pgvector` | src + tgt | vector (halfvec since 1.0.7) | v1.0.0; halfvec in 1.0.7 #2029 |
| `Amazon S3` / `Google Drive` / `Kafka` / `Local filesystem` / `Neo4j` / `FalkorDB` / `SQLite` | various | — | pre-1.0.x |
| `Apache Doris` | target | — | 1.0.12 #2189 |
| `Iggy` | src (stream) | — | 1.0.7 #1969 |
| `OCI Object Storage` | src | — | 1.0.7; optimised in 1.0.11 #2116 |
| `Qdrant` | target | vector | stable since 1.0.x; unit tests 1.0.13 #1952 |
| `SurrealDB` | src + tgt | — | 1.0.x |
| `Turbopuffer` | target | vector + FTS | 1.0.x |
| `Valkey` | target | vector | 1.0.12 #2027 |
| `zvec` | target | vector + FTS (1.0.14) | 1.0.11 #2092; FTS in 1.0.14 #2215 |

> KCG note: only LanceDB / FalkorDB / Postgres are wired in the Wave 1/2 `oideachais` tree. The 7 NEW connectors (1.0.7–1.0.14) are NOT integrated. Track via `openspec/research/2026-06-28-upstream-package-monitoring/` and the `upstream_api_surface` App's BAML `ApiChange` extraction.
```

### Diff block 2 — Lines 522–525 (`## Targets` block) — replace with breaking-change call-out
**Before:** `| LanceDB | HNSW | ... | localfs.declare_file | No |` table.
**After:**
```markdown
## Targets (verified against v1.0.14 docs at https://cocoindex.io/docs/connectors/, 2026-06-29)

See the connector table at the top of this skill. KCG v1.0.x only wires LanceDB / FalkorDB / Postgres.

### Breaking change: `declare_vector_index` default is now `ivf_pq`

```python
table.declare_vector_index(
    column="embedding",
    metric="cosine",
    # DEFAULTS TO IVF_PQ (was HNSW pre-1.0.7)
    # index_type="hnsw_pq",  # uncomment to opt back in
    # m=16, ef_construction=200,
)
```

### NEW: `declare_fts_index` for keyword search (1.0.11+)

```python
table.declare_fts_index(column="content", language="English", with_position=True)
```

### NEW: typed column override via `LanceType` (1.0.12+)

```python
from typing import Annotated
from cocoindex.connectors.lancedb import LanceType
import pyarrow as pa

@dataclass
class MyRow:
    id:    Annotated[int,   LanceType(pa.int32())]
    value: Annotated[float, LanceType(pa.float32())]
```

### NEW: explicit `TableSchema({…ColumnDef})` form

```python
schema = lancedb.TableSchema(
    {"doc_id":    lancedb.ColumnDef(type=pa.string(), nullable=False),
     "embedding": lancedb.ColumnDef(type=pa.list_(pa.float32(), list_size=384))},
    primary_key=["doc_id"],
)
```

### NEW table lifecycle knobs on `declare_table_target`

| Parameter | Default | Purpose |
|:--|:--|:--|
| `managed_by` | `"system"` | `"system"` ⇒ CocoIndex manages table; `"user"` ⇒ assume it exists |
| `num_transactions_before_optimize` | `50` | Background `table.optimize()` cadence (1.0.7 #2008) |
```

### Diff block 3 — Append after line 668 (end of `## 2026-06 update` section)
```markdown
### 2026-06-25 to 2026-06-29 update (CocoIndex v1.0.7 → v1.0.14, verified live 2026-06-29)

**v1.0.14 (25 Jun 2026, `4667e56`) — 19 PRs**: `feat(zvec): add FTS field support` (#2215); `feat(code_match): whole-node boundary \{ P \} ("is")` (#2196); `perf(engine): minimize serialization related to UserStateCache` (#2127); `fix(docs): update broken and redirected documentation links` (#2081). **v1.0.13 (22 Jun 2026) — 18 code-match PRs + Doris fix (#2189)**. **v1.0.12 (21 Jun 2026) — Valkey target (#2027) + LanceDB docs polish (#2130) + drop_index (#2132)**. **v1.0.11 (17 Jun 2026) — LanceDB vector + FTS (#2115) + zvec (#2092) + OCI incrementality (#2116)**. **v1.0.10 (14 Jun 2026) — Agent experience (.md mirrors / llms.txt / skill endpoint) (#2104) — drove the "Copy page as Markdown" / "Open in ChatGPT / Claude" / "Install the CocoIndex v1 skill" buttons on every page**. **v1.0.9 (12 Jun 2026) — `coco.fn` directly callable outside a component context (#2101)**. **v1.0.8 (11 Jun 2026 — NOT YANKED) — `use_state` (#2034) + `LiveMap` (#2088) + Preview mode (#1945) + `RateLimiter` (#2057) + `LiteLLMTranscriber` (#2059)**.

> Wave 1 correction: drop "`1.0.8` was YANKED on 2026-06-11" from `agent-03-cocoindex.md`. Verified live 2026-06-29: full release page renders, no `yanked` flag.
```

### Diff block 4 — Lines 644–651 (the 6-bullet "New connectors (2026-06 cycle)" list)
**Before:** 6 bullets, all pre-1.0.12.
**After:** point at the connector table from Diff block 1, e.g. *"See the 12-row connectors table at the top of this skill for the full 2026-06 cycle (Doris #2189, Iggy #1969, OCI #2116, Qdrant #1952, SurrealDB, Turbopuffer, Valkey #2027, zvec #2092 / #2215)."*

### Diff block 5 — Top-of-skill front-matter description
**Before (line 2):**
```yaml
description: Comprehensive toolkit for developing with the CocoIndex v1 library. ...
```
**After:**
```yaml
description: Comprehensive toolkit for developing with the CocoIndex v1 library (latest pip release v1.0.14, tagged 2026-06-25; docs review string frozen on v1.0.7 / Last reviewed Jun 23, 2026 — verified live 2026-06-29). Use when users need pipelines with the v1 `coco.App` + `@coco.fn` + `ContextKey` + `mount_table_target` model across 17 source/target connectors (S3, Doris, FalkorDB, Google Drive, Iggy, Kafka, LanceDB, LocalFS, Neo4j, OCI Object Storage, Postgres, Qdrant, SQLite, SurrealDB, Turbopuffer, Valkey, zvec), execution primitives (`memo=True`, `logic_tracking`, `version`, `deps`, `batching=True`, `runner=coco.GPU`, `as_async`), and lifecycle via `@coco.lifespan` + `coco.start() / coco.stop() / coco.runtime()`. Covers ETL for AI: embeddings into vector DBs (with `declare_fts_index` for keyword), knowledge graphs, search indexes, incremental updates with the `use_state` + `LiveMap` + `RateLimiter` 1.0.8 suite. KCG-conformant via the 4-rule contract (see the placeholder `oideachais-cocoindex-v1` openspec skill — the live file is this one).
```

---

## 7. Open follow-ups for the openspec change agent

1. **Fact correction** to `agent-03-cocoindex.md`: drop "`1.0.8` was YANKED on 2026-06-11" (drift #2). 2. **Connector inventory** in `agent-03-cocoindex.md`: replace 7-line list with the 17-line Wave 2 inventory (drift #3–9). 3. **URL fix**: `/docs/getting_started` returns 404 — replace with `/docs/getting_started/overview/` or `…/installation/` (drift #12). 4. **`upstream_api_surface` App monitoring baseline**: add `/docs/common_resources/live_map/` (drift #9). 5. **Skill rename**: openspec/AGENTS.md references `oideachais-cocoindex-v1/SKILL.md` but the live file is `.agents/skills/cocoindex/SKILL.md`. 6. **KCG wiring gap**: 7 NEW connectors (`Qdrant`, `Turbopuffer`, `Valkey`, `SurrealDB`, `zvec`, `Iggy`, `OCI Object Storage`, `Doris`) not integrated in oideachais. Track via `openspec/research/2026-06-28-upstream-package-monitoring/`.---
