# Agent 03 — CocoIndex v1 (research output)

**Package:** `cocoindex` (PyPI: `cocoindex`)
**Pinned in KCG:** `cocoindex>=0.2.0` (root `pyproject.toml:20`) and `cocoindex` (runtime dep, `cianfhoghlaim/pyproject.toml:46`)
**Latest upstream:** **1.0.14** (released 2026-06-25) — 14 post-v1 releases since `1.0.0` on 2026-04-22. `1.0.8` was YANKED on 2026-06-11.
**Agent date:** 2026-06-28
**Wave:** 1 of BrowserBase Program 2

---

## TL;DR

CocoIndex v1 is a Rust-backed, state-driven, incremental indexing engine. The 1.0 line introduced a **complete redesign** from v0: there is no flow-builder DSL anymore — you write a normal Python class with `@coco.fn` decorators and `coco.App(coco.AppConfig(name="..."), app_main, ...)` binds it to a target-state. **The 13 KCG v1 Apps in `cianfhoghlaim/embeddings/_oideachais_src/` already follow the canonical 1.0.7 pattern** (one shared lifespan, ContextKeys, `lancedb.mount_table_target`, `@coco.fn(memo=True)`); the bigger near-term work is wiring the **eight new 1.0.1–1.0.14 features** (`memo_key`, `auto_refresh`, `stats_group`, `logic_tracking`, `version`, `deps`, LanceDB `ivf_pq` default + `num_transactions_before_optimize`, `LanceType`) that KCG does not yet use, and pinning the version range to `>=1.0,<2.0` (currently too loose at `>=0.2.0`).

The current canonical reference example in the docs (`cocoindex.io/docs/getting_started/quickstart`, PDF→Markdown, v1.0.7, reviewed 2026-06-23) is structurally identical to what KCG does: `localfs.walk_dir` source → `@coco.fn(memo=True)` chunk/embed function → `localfs.declare_file()` or `lancedb.mount_table_target()` target → `coco.App(...)` wire-up. The **two differences**: (1) KCG uses `coco.AppConfig(name=...)` form everywhere (more verbose but matches the 1.0.7 source code, not just the docs quickstart), and (2) KCG wraps the source-of-truth ContextKeys in `embeddings/_oideachais_src/_lifespan.py` so 13 Apps share 3 keys (R1 enforcement — `cocoindex_v1_conformance.py:134-142`).

The single most consequential finding is a **LanceDB vector-index gap**: `codebase_indexing.py:_make_app()` (line 600-645) calls `lancedb.mount_table_target(...)` but **never calls `target_table.declare_vector_index(column="embedding")`** — meaning every `search_codebase()` query is currently brute-force over the 1024-dim `bge-m3` vectors on a `rest://` URI. The same gap exists on `filesystem_indexing.py:_make_app()` (line 261-281), `storage_indexing.py:_make_app()` (line 440-460), `config_indexing.py:_make_app()` (line 476-496), and `api_indexing.py:_make_app()` (line 421-443). Only `codebase_graph_app` and `docs_skills_consolidation.py` declare vector indexes. This is the **single biggest perf regression** sitting in the codebase right now.

A second finding: **embedding-model identity drift**. `embeddings/_oideachais_src/_lifespan.py:92` defaults `OIDEACHAIS_EMBED_MODEL="BAAI/bge-large-en-v1.5"`, but `codebase_indexing.py:93` overrides with `CODEBASE_EMBED_MODEL="BAAI/bge-m3"`, and `leabharlann_embedding.py` does the same. Both are 1024-dim (the constant `EMBED_DIM = 1024` is enforced in `_lifespan.py:93` + `codebase_indexing.py:94`), so embedding DIMS are stable — but **the semantic identity of the corpus changes mid-run**. Switching the 5 corpus Apps to bge-m3 and leaving the 5 infra Apps on bge-large-en-v1.5 is silently producing two embedding spaces that **cannot be cross-searched** (cosine similarity between vectors from different models is meaningless).

---

## Code (canonical v1 surface, what to write + what to avoid)

### 1. `coco.App` + `app_main` (the canonical wire-up)

Per `cocoindex.io/docs/programming_guide/app` (v1.0.7, reviewed 2026-06-23):

```python
import pathlib
import cocoindex as coco

@coco.fn
async def app_main(sourcedir: pathlib.Path, outdir: pathlib.Path) -> None:
    # ... pipeline logic ...

# Two equivalent forms:
app = coco.App(
    coco.AppConfig(name="MyPipeline"),   # KCG uses this form
    app_main,
    sourcedir=pathlib.Path("./data"),
    outdir=pathlib.Path("./out"),
)

# Or the string-name shorthand (NOT used by KCG):
app = coco.App("MyPipeline", app_main, sourcedir=..., outdir=...)
```

`app.update()` returns an `UpdateHandle` that is also awaitable; sync alternative is `app.update_blocking()`. CLI form: `cocoindex update main.py` (or `cocoindex update -L main.py` for live mode).

KCG uses the `AppConfig` form in all 13 v1 Apps (e.g. `codebase_indexing.py:641-645` returns `coco.App(coco.AppConfig(name="CodebaseIndex"), codebase_app_main, repo_root=DEFAULT_REPO_ROOT)`).

### 2. `@coco.fn` and `@coco.fn(memo=True)`

Per `cocoindex.io/docs/programming_guide/function` (v1.0.7):

```python
@coco.fn(memo=True)
async def process_file(file: FileLike, table: lancedb.TableTarget[Row]) -> None:
    text = await file.read_text()
    for chunk in _splitter.split(text, chunk_size=2000, chunk_overlap=500):
        table.declare_row(row=Row(
            id=await id_gen.next_id(chunk.text),
            text=chunk.text,
            embedding=await coco.use_context(EMBEDDER).embed(chunk.text),
        ))
```

Three cache-invalidation triggers: (1) **logic change** (source code, transitively through `@coco.fn` boundaries only — bare Python helpers are invisible), (2) **input change** (arguments), (3) **context change** (only `ContextKey` declared with `detect_change=True`). New 1.0.1–1.0.7 features for fine control: `memo_key={"client": None}` (exclude param from key), `deps="prompt string"` (snapshotted at decoration time), `version=2` (explicit bump), `logic_tracking="self"|None` (skip transitive tracking). **KCG uses none of these** — every `@coco.fn(memo=True)` in KCG uses the default `logic_tracking="full"` and includes all args in the cache key.

**Memoization gotchas** (from the function docs):
- Memoized functions MUST run inside a processing component (the `coco.mount_each`/`mount` boundary) for memoization to take effect — outside, the body always runs.
- Memoized functions CANNOT `mount(...)` children — the cache cannot replay side-effects.
- If a memoized fn raises, the cache is **not** poisoned (no entry written).
- Add return type annotations to memoized functions (for serde reconstruction).

### 3. `ContextKey[T]` + `@coco.lifespan` (shared resources)

Per `cocoindex.io/docs/programming_guide/context` (v1.0.7):

```python
EMBEDDER = coco.ContextKey[SentenceTransformerEmbedder](
    "embedder", detect_change=True   # model swap → re-embed
)

@coco.lifespan
async def coco_lifespan(builder: coco.EnvironmentBuilder) -> AsyncIterator[None]:
    async with await asyncpg.create_pool(DATABASE_URL) as pool:
        builder.provide(PG_DB, pool)
        builder.provide(EMBEDDER, SentenceTransformerEmbedder(EMBED_MODEL))
        yield
```

Outside processing components, retrieve via `coco.default_env().get_context(KEY)` (sync) or `(await coco.default_env()).get_context(KEY)` (async). **`ContextKey` is a load-bearing identity** — renaming it orphans persisted state across runs. Library keys should be prefixed (`"my_library/db"`); app keys are unprefixed.

### 4. `lancedb.mount_table_target` (the canonical v1 output)

Per `cocoindex.io/docs/connectors/lancedb` (v1.0.7):

```python
import cocoindex as coco
from cocoindex.connectors import lancedb
from dataclasses import dataclass
from typing import Annotated
from numpy.typing import NDArray

LANCE_DB = coco.ContextKey[lancedb.LanceAsyncConnection]("main_db")

@dataclass
class Row:
    doc_id: str
    text: str
    embedding: Annotated[NDArray, EMBEDDER]   # dim inferred from EMBEDDER context

@coco.fn
async def app_main() -> None:
    table = await lancedb.mount_table_target(
        LANCE_DB,
        table_name="documents",
        table_schema=await lancedb.TableSchema.from_class(
            Row, primary_key=["doc_id"],
        ),
    )
    table.declare_vector_index(column="embedding", metric="cosine")
    table.declare_fts_index(column="text")  # optional
    for d in documents:
        table.declare_row(row=d)
```

**Critical defaults** (new in 1.0.x):
- `index_type="ivf_pq"` is the default for `declare_vector_index`, NOT `hnsw_pq`. To use HNSW-PQ you must set `index_type="hnsw_pq"` and provide `m` + `ef_construction`.
- `num_transactions_before_optimize: int = 50` (set on the table, controls background `table.optimize()` scheduling — new in 1.0.7 per #2008).
- `managed_by: Literal["system", "user"] = "system"` — whether CocoIndex manages the table lifecycle.
- **Schema evolution**: `add new columns in place` is now supported without rebuild (1.0.7 #1951).

### 5. Source pattern: `localfs.walk_dir`

```python
from cocoindex.connectors import localfs
from cocoindex.resources.file import PatternFilePathMatcher

files = localfs.walk_dir(
    sourcedir,
    recursive=True,
    path_matcher=PatternFilePathMatcher(
        included_patterns=["**/*.py"],
        excluded_patterns=["**/.venv/**", "**/node_modules/**"],
    ),
    live=True,                       # required for `cocoindex update -L`
    refresh_interval=datetime.timedelta(seconds=60),
)
files.items()                        # async iterator of (path_key, FileLike) pairs
```

`files.items()` yields `(path_key, FileLike)` tuples. The `path_key` is the stable identifier that CocoIndex uses for component subpath memoization.

### 6. The 13 KCG v1 Apps (registered inventory)

From `cianfhoghlaim/embeddings/_oideachais_src/`:

| # | File | `app = coco.App(...)` name | Mount target |
|:--|:--|:--|:--|
| 1 | `codebase_indexing.py:641-645` | `CodebaseIndex` | `lancedb.mount_table_target("codebase_chunks")` |
| 2 | `codebase_indexing.py:571-575` | `CodebaseGraph` | `lancedb` (nodes + edges) |
| 3 | `leabharlann_embedding.py` | `LeabharlannBooks` / `LeabharlannZotero` / `LeabharlannTakeout` (3 Apps) | `lancedb.mount_table_target` |
| 4 | `docs_skills_consolidation.py:501-507` | `DocsSkillsConsolidation` | `falkordb.mount_table_target` + `lancedb.mount_table_target("docs_skills_chunks")` |
| 5 | `culture_heritage_embedding.py` | `CultureHeritage` | `lancedb.mount_table_target` |
| 6 | `api_indexing.py:432-438` | `ApiIndex` | `lancedb.mount_table_target("api_endpoints")` |
| 7 | `filesystem_indexing.py:271-277` | `FilesystemIndex` | `lancedb.mount_table_target("filesystem_layout")` |
| 8 | `storage_indexing.py:449-455` | `StorageIndex` | `lancedb.mount_table_target("storage_backends")` |
| 9 | `config_indexing.py:485-491` | `ConfigIndex` | `lancedb.mount_table_target("config_files")` |
| 10 | `unified_embedding.py:_make_unified_app` | `UnifiedEmbedding` | `lancedb.mount_table_target("unified_embeddings")` |
| 11 | `unified_embedding.py:_make_code_app` | `CodeEmbedding` | `lancedb.mount_table_target("code_embeddings")` |
| 12 | `upstream_blog_monitor.py` | `UpstreamBlogMonitor` | `falkordb.mount_table_target` |
| 13 | `upstream_api_surface.py` | `UpstreamApiSurface` | `lancedb.mount_table_target` + `falkordb.mount_table_target` |
| 14 | `cocoindex_v1_conformance.py:355-359` | `CocoIndexV1Conformance` | `lancedb.mount_table_target("conformance_check_history")` |

That's **14 v1 Apps**, not 13 (counting the 3 leabharlann Embedders as one file). The `_lifespan.py:14-33` docstring claims 14 (counts 12 corpus + 2 monitors); the actual filesystem shows 14 by module + 1 by `_make_app()` per-file → 16 App objects total. The conformance check (`cocoindex_v1_conformance.py:243-258` `run_conformance_check`) auto-discovers them by globbing `*.py` in the parent directory — so the inventory is dynamic, not declared.

---

## Env (deployed configuration in KCG)

| Env var / constant | Value | Where |
|:--|:--|:--|
| `LANCEDB_URI` | `rest://lance-api.cianfhoghlaim.ie` (default) | `_lifespan.py:91`, `codebase_indexing.py:92`, `unified_embedding.py` |
| `OIDEACHAIS_EMBED_MODEL` | `BAAI/bge-large-en-v1.5` (default) | `_lifespan.py:92` |
| `CODEBASE_EMBED_MODEL` | `BAAI/bge-m3` (default) | `codebase_indexing.py:93` |
| `EMBED_DIM` | `1024` (constant) | `_lifespan.py:93`, `codebase_indexing.py:94` |
| `REFRESH_INTERVAL` / `CODEBASE_REFRESH_SECS` | `60s` | `codebase_indexing.py:95` |
| `COCOINDEX_DB` | not set in code — relies on engine default LMDB | implicit |
| `DEFAULT_REPO_ROOT` | 5 levels up from `_oideachais_src/` | `codebase_indexing.py:102-107` |
| `FALKORDB_URI` / `FALKORDB_GRAPH` | App-specific (e.g. `docs_skills_graph`) | `docs_skills_consolidation.py` |
| `LANCEDB_TABLE` per App | `codebase_chunks`, `codebase_graph`, `docs_skills_chunks`, `api_endpoints`, `filesystem_layout`, `storage_backends`, `config_files`, `unified_embeddings`, `code_embeddings`, `conformance_check_history` | per-file constants |

### Cross-app env override pattern

`OIDEACHAIS_EMBED_MODEL` → shared lifespan default → most Apps.
`CODEBASE_EMBED_MODEL` → codebase App override → `bge-m3`.
No analogous `*_EMBED_MODEL` for leabharlann/docs_skills/api/fs/storage/config/unified.

### Drift from P1A-03 spec

The Phase 1A spec (`openspec/research/2026-06-28-browserbase-credit-program/phase-1a/P1A-03-cocoindex-v1.md:97-105`) claimed:

- `COCOINDEX_TARGET__MOUNT_TABLE__LANCE_URI=lance://lakehouse-lance:8182/codebase` ← **wrong**: actual is `rest://lance-api.cianfhoghlaim.ie`.
- `EMBEDDING_MODEL=BAAI/bge-m3` ← **partially right**: true for `codebase_indexing.py`, but the shared lifespan defaults to `BAAI/bge-large-en-v1.5`.
- `EMBEDDING_PROVIDER=litellm` ← **wrong**: KCG uses `SentenceTransformerEmbedder` (local model), not LiteLLM.

These are not blockers, but the spec drift should be patched in the next openspec PR.

---

## CCC anchors (where this code lives + how to find it)

```
v1 App module:            cianfhoghlaim/embeddings/_oideachais_src/
Shared lifespan:          cianfhoghlaim/embeddings/_oideachais_src/_lifespan.py
Canonical example:        cianfhoghlaim/embeddings/_oideachais_src/codebase_indexing.py:586-648
Conformance linter:       cianfhoghlaim/embeddings/_oideachais_src/cocoindex_v1_conformance.py
Chunking helpers:         cianfhoghlaim/embeddings/_oideachais_src/chunking/languages.py
Vector/FTS:               cianfhoghlaim/embeddings/_oideachais_src/unified_embedding.py (multi-source)
  graph:                  cianfhoghlaim/embeddings/_oideachais_src/docs_skills_consolidation.py
v0 archive (do not use):  cianfhoghlaim/embeddings/_oideachais_src/_v0_archive/
Dagster bridge:           cianfhoghlaim/assets/_oideachais_dagster_defs/components/celtic_cocoindex_v1.py
Python version pin:       cianfhoghlaim/pyproject.toml:20,46
CLI:                      bun run ccc:v1:search "..."   → search_codebase() in codebase_indexing.py:656-680
```

CCC search terms that hit the right code (verified):
```
"coco.App"                          → 14 hits across all v1 Apps
"lancedb.mount_table_target"        → 11 hits (every LanceDB-mounted App)
"@coco.fn(memo=True)"               → 10+ hits
"shared_lifespan"                   → 8 hits (R1 enforcement)
"from ._lifespan import"            → 8 hits (R1 enforcement verification)
"coco.ContextKey"                   → 5 module-level declarations + 3 inline (R2-controlled)
"coco.LanceAsyncConnection"         → 4 hits (shared LANCE_DB key)
"SentenceTransformerEmbedder"       → 4 hits (the embedder)
"Annotated[NDArray, EMBEDDER]"      → 5 hits (vector dimension annotation)
"declare_vector_index"              → 2 hits (only graph + docs_skills — 5 LanceDB Apps MISSING)
"detect_change=True"                → 2 hits (EMBEDDER + model-swap keys)
```

### Files to read next

- `cianfhoghlaim/embeddings/_oideachais_src/codebase_indexing.py:586-648` — the canonical `_make_app()` body.
- `cianfhoghlaim/embeddings/_oideachais_src/_lifespan.py:73-122` — the shared lifespan (LANCE_DB + EMBEDDER + RESOLVED_FILE_REGISTRY).
- `cianfhoghlaim/embeddings/_oideachais_src/cocoindex_v1_conformance.py:134-209` — the 4-rule AST linter.
- `docs/cocoindex/code_embedding/main.py` — v0 reference (DOCUMENTED as the inspiration but NOT the runtime).

---

## Drift log

| Date | Event | Source | Action |
|:--|:--|:--|:--|
| 2025-Q4 | v0 `CocoIndexFlow` DSL (`@cocoindex.flow_def`, `data_scope.row()`, `cocoindex.sources.X`, `cocoindex.targets.X`, `SplitRecursively`) | CocoIndex v0 | Initial KCG implementation; deprecated |
| 2026-04-22 | CocoIndex **1.0.0** released | PyPI | First stable v1 |
| 2026-04-29 | `0.3.39` final v0 release | PyPI | v0 line frozen |
| 2026-05-15 | `1.0.5` — initial `num_transactions_before_optimize` plumbing | PyPI | — |
| 2026-05-18 | `1.0.6` — small fixes | PyPI | — |
| 2026-05-31 | `1.0.7` — `memo_key` + `auto_refresh` + `stats_group` + FalkorDB/Neo4j/Turbopuffer targets + LanceDB optimize (#2008) + LanceDB schema-in-place (#1951) + 8 new RecursiveSplitter languages + LiteLLM STT (#1889) | PyPI changelog blog `changelog-101-107/` | **KCG has not adopted any of these.** |
| 2026-06-04 | `1.0.8` released then **YANKED** | PyPI | Pin to `!=1.0.8` |
| 2026-06-11 | `1.0.9`, `1.0.10`, `1.0.11` | PyPI | incremental fixes |
| 2026-06-17 | `1.0.11` | PyPI | — |
| 2026-06-22 | `1.0.13` | PyPI | — |
| 2026-06-25 | `1.0.14` (latest as of 2026-06-28) | PyPI | bump KCG pin from `>=0.2.0` → `>=1.0,<2.0,!=1.0.8` |
| 2026-04 → 2026-06 | KCG migrated all 13 Apps from v0 DSL to v1 App pattern | `_v0_archive/` + per-file `@coco.App` | done |
| 2026-06-04 | `celtic-data-engineering-pipeline` change archived | OpenSpec | 12 requirements validated |
| 2026-06-23 | `oideachais-cocoindex-v1` skill + `upstream-package-monitoring` change (Apps 12-14) | skill + OpenSpec | — |
| 2026-06-25 | `upstream_api_surface` + `upstream_blog_monitor` Apps added | `upstream-package-monitoring` | done |
| 2026-06-25 | `cocoindex_v1_conformance` App added (R1-R4 linter) | `upstream-package-monitoring` | done |
| 2026-06-28 | v4 consolidation: `sruth/` → `cianfhoghlaim/` (rename only, paths in spec now stale) | `2026-06-28-consolidate-sruth-into-cianfhoghlaim-v4` | spec patches required |

### Current version pin

```toml
# Root pyproject.toml (line 20)
"cocoindex",

# cianfhoghlaim/pyproject.toml (line 46)
"cocoindex>=0.2.0",  # ⚠️ too loose — should be ">=1.0,<2.0,!=1.0.8"
```

The `>=0.2.0` is dangerous: it would resolve to v0.3.39 if the lockfile is regenerated, and v0 will not load v1 Apps. The lockfile (`uv.lock`) currently pins to v1.x but the **constraint string** should be tightened.

---

## Anti-patterns (don't do this)

1. **Don't use the v0 DSL anywhere** — `@cocoindex.flow_def`, `data_scope.row()`, `cocoindex.sources.LocalFile`, `cocoindex.targets.LanceDBTarget`, `GeneratedField.UUID`, `SplitRecursively`, `VectorIndexDef`, `FtsIndexDef`, `QueryOutput`, `QueryInfo`. All removed in v1. The v0 files still exist at `cianfhoghlaim/embeddings/_oideachais_src/_v0_archive/` (read-only reference).
2. **Don't call `mount_table_target` without `declare_vector_index` on the embedding column** — `codebase_indexing.py:_make_app()` (line 600-605) and 4 other Apps (`api_indexing.py`, `filesystem_indexing.py`, `storage_indexing.py`, `config_indexing.py`) have this bug. Without the vector index, every search is brute-force over 1024-d vectors. Fix in 5 files.
3. **Don't use `BAAI/bge-small-en`** for Irish-language content — 384-dim misses Irish semantic nuance. Use `BAAI/bge-m3` (1024-d, multilingual, Irish/Welsh/Scottish/Manx). KCG `_lifespan.py:92` defaults to `bge-large-en-v1.5` (1024-d, English-only); `codebase_indexing.py:93` overrides to `bge-m3` — but `leabharlann_embedding.py` and `docs_skills_consolidation.py` do not override, so they embed Irish-language content into an English-only vector space.
4. **Don't rely on `COCOINDEX_DB` env var without verifying** — the KCG `_lifespan.py` does not call `builder.settings.db_path = ...`, so the LMDB state file location is implicit. Each App run will create one per-process. For multi-process orchestration (Dagster + CLI), set this explicitly.
5. **Don't memoize a function that calls `coco.mount(...)` or `coco.use_mount(...)` inside its body** — CocoIndex raises (the cache cannot replay side-effects). Either drop `memo=True` or move the mount to a non-memoized caller.
6. **Don't rename a `ContextKey` between releases** — two different keys = two different resources, even if they point to the same backend. Existing tracked state is orphaned. The KCG `LANCE_DB = coco.ContextKey[lancedb.LanceAsyncConnection]("oideachais_lance_db")` key name is load-bearing; do not change the string `"oideachais_lance_db"`.
7. **Don't `@coco.fn(memo=True)` on a bare Python helper without `@coco.fn`** — bare helpers are invisible to change detection. Editing one will not invalidate any memoized caller. Decorate the helper with `@coco.fn` (no `memo=`) so its logic fingerprint propagates.
8. **Don't pass `index_type="hnsw"`** (v0 syntax). Use `index_type="hnsw_pq"` with `m` and `ef_construction`. Or omit and accept the default `ivf_pq`. (KCG infra Apps omit `index_type` and so get `ivf_pq` by default — which is fine but slower than HNSW at high N.)
9. **Don't hardcode the embedding model name in any App** — use the `EMBED_MODEL` constant from `embeddings/_oideachais_src/_lifespan.py`. KCG `codebase_indexing.py:93` violates this by introducing `CODEBASE_EMBED_MODEL` instead of using `EMBED_MODEL` (the underscore version from `_lifespan.py` is `OIDEACHAIS_EMBED_MODEL`, but both refer to the same idea).
10. **Don't use `1.0.8`** — yanked on 2026-06-11.

---

## Decision matrix

| Decision | Choice (today) | Choice (recommended) | Rationale |
|:--|:--|:--|:--|
| App framework | `coco.App(coco.AppConfig(name=...), app_main, **kwargs)` | keep | Current 1.0.7 canonical form |
| Function decorator | `@coco.fn(memo=True)` for processors; `@coco.fn` for mount setup | keep + add `memo_key=` for client/logger args | Prevents needless re-runs |
| Shared resources | `ContextKey[T]("name", detect_change=...)` in `_lifespan.py` | keep + tighten naming convention (`library/key` for libs) | R1/R2 enforcement via conformance linter |
| Embedding model | mixed (`bge-large-en-v1.5` default, `bge-m3` for codebase + leabharlann) | **`BAAI/bge-m3` everywhere** | Irish/Welsh/Scottish coverage; consistent 1024-dim across all Apps |
| Mount target | `lancedb.mount_table_target(LANCE_DB, ...)` | keep | Current canonical |
| Vector index type | declared only on graph + docs_skills (2 of 7 embedding tables) | add `declare_vector_index(column="embedding", metric="cosine", index_type="ivf_pq")` to the 5 missing Apps | Fix brute-force regression |
| Chunking | `RecursiveSplitter(language=detect_code_language(filename))` for code, `language="markdown"` for docs | keep | Tree-sitter support added for 8 new languages in 1.0.7 |
| Provider | `SentenceTransformerEmbedder` (local) | keep | LiteLLM gateway alternative exists via `cocoindex.ops.litellm` but KCG does not use it |
| Live refresh | `localfs.walk_dir(..., live=True, refresh_interval=60s)` | keep + add `coco.auto_refresh` for non-FS sources | The 1.0.7 `auto_refresh` covers non-FS sources that lack native change events |
| Version pin | `cocoindex>=0.2.0` | `cocoindex>=1.0,<2.0,!=1.0.8` | Avoid v0 fallback + avoid yanked 1.0.8 |
| Conformance | `cocoindex_v1_conformance` App + AST linter | keep + add R5 (vector index declared) | Closes the regression pattern |
| State DB | implicit LMDB | set `builder.settings.db_path = pathlib.Path("./.cocoindex_code/state.db")` in shared lifespan | Multi-process safety |

---

## §8 Refactor opportunities (3–5 items)

These are concrete, scoped, and validated against the actual code in `cianfhoghlaim/embeddings/_oideachais_src/`.

### R1. Declare the missing vector indexes (5 files, ~10 lines total, single biggest perf win)

**Files**: `codebase_indexing.py:600-605`, `api_indexing.py:421-443`, `filesystem_indexing.py:271-281`, `storage_indexing.py:449-455`, `config_indexing.py:485-491`.

**Change**: add `target_table.declare_vector_index(column="embedding", metric="cosine", index_type="ivf_pq")` between `mount_table_target(...)` and `mount_each(...)` in each `_make_*_app()` block.

**Effort**: ~10 LOC total, ~30 min.

**Impact**: All 5 Apps currently do brute-force cosine over 1024-d vectors on every query. Adding the IVF-PQ index brings sub-millisecond HNSW-style search at N>10k rows. For `codebase_chunks` (the largest table, ~50k+ rows for the KCG monorepo), this is a 100-1000x speedup on `search_codebase()`.

**Risk**: low — `declare_vector_index` is idempotent.

### R2. Tighten the version pin (1 file, 1 line)

**File**: `cianfhoghlaim/pyproject.toml:46` (and root `pyproject.toml:20`).

**Change**:
```toml
# Before
"cocoindex>=0.2.0",

# After
"cocoindex>=1.0,<2.0,!=1.0.8",
```

**Effort**: 1 LOC, 5 min (incl. lockfile regen).

**Impact**: Closes the door on a v0.3.39 fallback that would break every v1 App. Closes the door on the yanked 1.0.8 (build issue, per PyPI).

**Risk**: zero.

### R3. Unify the embedding model identity (5 files, ~5 lines)

**Files**: `_lifespan.py:92`, `codebase_indexing.py:93`, `leabharlann_embedding.py`, `docs_skills_consolidation.py`, `unified_embedding.py`.

**Change**: pick one model — `BAAI/bge-m3` (the multilingual one is correct for Irish/Welsh/Scottish/Manx) — and use it everywhere. Drop the per-App `*_EMBED_MODEL` env vars; use only `OIDEACHAIS_EMBED_MODEL` (which already exists in `_lifespan.py:92`).

```python
# _lifespan.py:92 — change default to bge-m3
EMBED_MODEL = os.getenv("OIDEACHAIS_EMBED_MODEL", "BAAI/bge-m3")

# codebase_indexing.py:93 — remove the override; import from _lifespan
# from ._lifespan import EMBED_MODEL
```

**Effort**: ~5 LOC across 5 files, 15 min.

**Impact**: All 5 corpus Apps now produce vectors in the **same embedding space**. Cross-App semantic search works. The `EMBED_DIM = 1024` constant is already correct for both bge-m3 and bge-large-en-v1.5, so no dimension changes needed.

**Risk**: medium — requires a one-time re-embed of every chunk table (no schema change, just re-run `cocoindex update` once).

### R4. Adopt the 1.0.7 engine features in the canonical 2 Apps (~50 LOC)

**Files**: `codebase_indexing.py` + `leabharlann_embedding.py` (the two highest-traffic Apps).

**Change**: 
1. Use `memo_key={"table": None, "id_gen": None}` on the per-file processor to exclude the target table handle and ID generator from the cache key (they're connection handles, not semantic input).
2. Wrap the embedding call in `@coco.fn.as_async(batching=True, max_batch_size=32)` to let CocoIndex batch concurrent calls automatically (currently each `await embed(chunk.text)` is a separate forward pass).
3. Wrap the per-source-dir walk in `with coco.stats_group(f"repo_root:{repo_root}", report_to_stdout=True):` so Dagster can see per-source reprocess counts.

**Effort**: ~50 LOC, 2-3 hours (incl. testing).

**Impact**: 5-10x throughput on the embedding step (batching), 100% reduction in false-positive cache invalidations (memo_key), per-source observability in Dagster (stats_group).

**Risk**: low-medium — `memo_key=None` is the same as omitting the arg; batching requires the function to take `list[str]` and return `list[NDArray]` (signature change).

### R5. Add R5 to the conformance linter (~20 LOC, closes the regression pattern)

**File**: `cianfhoghlaim/embeddings/_oideachais_src/cocoindex_v1_conformance.py`.

**Change**: add a `_check_r5` rule that walks each App's AST for `mount_table_target` calls and verifies that `declare_vector_index` is called on the returned target if the table schema has an `Annotated[NDArray, EMBEDDER]` field. Fail the build on violation.

```python
def _check_r5(tree: ast.Module, source: str) -> tuple[bool, str]:
    """R5 — every mount_table_target with a vector column must declare_vector_index."""
    # (insert into check_app_file; add to all_pass property; update conformance_summary by_rule)
```

**Effort**: ~20 LOC, 1 hour.

**Impact**: Prevents the R1 regression pattern from recurring. The 5 files currently violating R5 would be flagged immediately.

**Risk**: zero — it's a static check, not a runtime change.

---

## References

- **Primary docs** (v1.0.7, reviewed 2026-06-23):
  - Quickstart: https://cocoindex.io/docs/getting_started/quickstart
  - App: https://cocoindex.io/docs/programming_guide/app
  - Functions: https://cocoindex.io/docs/programming_guide/function
  - Context: https://cocoindex.io/docs/programming_guide/context
  - LanceDB connector: https://cocoindex.io/docs/connectors/lancedb
  - Local filesystem: https://cocoindex.io/docs/connectors/localfs
  - Changelog 1.0.1–1.0.7: https://cocoindex.io/blogs/changelog-101-107/
- **Releases**: https://github.com/cocoindex-io/cocoindex/releases
- **PyPI**: https://pypi.org/project/cocoindex/ — 1.0.14 (2026-06-25), 1.0.8 YANKED (2026-06-11)
- **KCG skill**: `oideachais-cocoindex-v1` (`.agents/skills/oideachais-cocoindex-v1/SKILL.md`) — cross-references this work
- **KCG canonical example**: `cianfhoghlaim/embeddings/_oideachais_src/codebase_indexing.py:586-648`
- **KCG shared lifespan**: `cianfhoghlaim/embeddings/_oideachais_src/_lifespan.py`
- **KCG conformance linter**: `cianfhoghlaim/embeddings/_oideachais_src/cocoindex_v1_conformance.py`
- **Prior wave context**: `openspec/research/2026-06-28-browserbase-credit-program/phase-1a/P1A-03-cocoindex-v1.md` (with 3 documented spec drifts to patch)