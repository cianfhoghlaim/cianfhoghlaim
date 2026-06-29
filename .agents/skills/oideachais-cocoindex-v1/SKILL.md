---
name: oideachais-cocoindex-v1
description: The canonical CocoIndex v1 App pattern in `sruth/oideachais/cocoindex_flows/`. Covers the 14 v1 Apps (leabharlann_books_embedding, leabharlann_zotero_embedding, leabharlann_takeout_embedding, codebase_indexing, api_indexing, filesystem_indexing, storage_indexing, config_indexing, unified_embedding, code_embeddings, docs_skills_consolidation, culture_heritage_embedding, upstream_blog_monitor, upstream_api_surface, cocoindex_v1_conformance), the `@coco.fn` + `@coco.lifespan` + `lancedb.mount_table_target` pattern, the 100-batch minimum + the HNSW-DROP-THRESHOLD=50 rule, the `IdGenerator()` stable-id pattern, the `Annotated[NDArray, EMBEDDER]` typing, the 4-rule v1 conformance contract (R1-R4) enforced by `cocoindex_v1_conformance`, the shared `_lifespan.py` (the canonical home for `LANCE_DB` + `EMBEDDER` + `RESOLVED_FILE_REGISTRY` per REFACTORING.md item 12), and the canonical add-a-new-v1-App workflow. Use when adding a new v1 CocoIndex App, debugging a v0→v1 migration, or running the conformance linter.
---

# Oideachais CocoIndex v1

## Purpose

The `sruth/oideachais/cocoindex_flows/` directory houses **14 v1
CocoIndex Apps** + 10 v0 broken modules (slated for v0-to-v1
migration in this round). This skill captures the canonical v1
pattern (`@coco.fn` + `@coco.lifespan` +
`lancedb.mount_table_target`), the 100-batch minimum, the
HNSW-DROP-THRESHOLD=50 rule, the `IdGenerator()` stable-id
pattern, the `Annotated[NDArray, EMBEDDER]` typing, the 4-rule
conformance contract enforced by `cocoindex_v1_conformance`, the
shared `_lifespan.py` canonical home (REFACTORING.md item 12), and
the add-a-new-v1-App workflow. The `cocoindex/` skill is generic;
this one is oideachais-specific.

## When to use this skill

Use when you need to:

- "Add a new v1 CocoIndex App"
- "Debug a v0→v1 migration"
- "Understand the 100-row upsert contract"
- "Choose between `BAAI/bge-m3` and `BAAI/bge-large-en-v1.5` for embedding"
- "Wire a new LanceDB table"
- "Run the v1 conformance check on all 14 Apps"
- "Fix an R1/R2/R3/R4 conformance failure"
- "Import the shared lifespan from `_lifespan.py`"

## The 14 v1 Apps (the registry)

| # | App | Module | Output table | Embedding model |
|:--|:--|:--|:--|:--|
| 1 | `leabharlann_books_embedding` | `leabharlann_embedding.py` | `leabharlann_books` | `BAAI/bge-large-en-v1.5` |
| 2 | `leabharlann_zotero_embedding` | `leabharlann_embedding.py` | `leabharlann_zotero` | `BAAI/bge-large-en-v1.5` |
| 3 | `leabharlann_takeout_embedding` | `leabharlann_embedding.py` | `leabharlann_takeout` | `BAAI/bge-large-en-v1.5` |
| 3a | `leabharlann_inbox_embedding` | `leabharlann_embedding.py` | `oideachais_inbox_messages` (NEW 2026-06-29; the 4th leabharlann App — see [`oideachais-email-triage`](../oideachais-email-triage/SKILL.md)) | `BAAI/bge-large-en-v1.5` |
| 4 | `codebase_indexing` | `codebase_indexing.py` | `codebase_chunks` (the 7-node/7-edge code graph) | `BAAI/bge-large-en-v1.5` |
| 5 | `api_indexing` | `api_indexing.py` | `api_endpoints` (the 4-framework HTTP route surface) | `BAAI/bge-large-en-v1.5` |
| 6 | `filesystem_indexing` | `filesystem_indexing.py` | `filesystem_layout` (depth 1-4 dirs) | `BAAI/bge-large-en-v1.5` |
| 7 | `storage_indexing` | `storage_indexing.py` | `storage_backends` (9 backend kinds) | `BAAI/bge-large-en-v1.5` |
| 8 | `config_indexing` | `config_indexing.py` | `config_files` (12 config kinds) | `BAAI/bge-large-en-v1.5` |
| 9 | `unified_embedding` | `unified_embedding.py` | `unified_embeddings` (DuckDB source) | `BAAI/bge-large-en-v1.5` |
| 10 | `code_embeddings` | `unified_embedding.py` | `code_embeddings` (LocalFile source) | `BAAI/bge-large-en-v1.5` |
| 11 | `docs_skills_consolidation` | `docs_skills_consolidation.py` | `docs_skills` (BAML-driven extraction → LanceDB + FalkorDB) | `BAAI/bge-large-en-v1.5` |
| 12 | `culture_heritage_embedding` | `culture_heritage_embedding.py` | `culture_heritage_chunks` | `BAAI/bge-large-en-v1.5` |
| 13 | `upstream_blog_monitor` | `upstream_blog_monitor.py` | `upstream_blog_chunks` (NEW 2026-06) | `BAAI/bge-large-en-v1.5` |
| 14 | `upstream_api_surface` | `upstream_api_surface.py` | (FalkorDB-only graph publish) (NEW 2026-06) | `BAAI/bge-large-en-v1.5` |
| - | `cocoindex_v1_conformance` | `cocoindex_v1_conformance.py` | `conformance_check_history` (NEW 2026-06) | n/a (linter) |

The 14 Apps are all `coco.App` instances with `@coco.lifespan` +
`@coco.fn` decorators (per the canonical v1 pattern).

**Embedder model note**: as of 2026-06, the value actually exported by
`sruth/oideachais/cocoindex_flows/_lifespan.py:70` is
`BAAI/bge-large-en-v1.5` (English-only, 1024-dim). Several docstrings
claim `BAAI/bge-m3` (multilingual, 1024-dim). Both are 1024-dim so the
discrepancy is latent, but `BAAI/bge-large-en-v1.5` is the canonical
value. Apps whose docstring claim `bge-m3` will be updated in a
follow-up openspec change.

## The canonical v1 pattern (the 6-field shape)

```python
# Canonical sruth/oideachais/cocoindex_flows/leabharlann_embedding.py
@coco.lifespan
async def leabharlann_lifespan(builder):
    from cocoindex.connectors.lancedb import LanceAsyncConnection
    conn = await LanceAsyncConnection.connect(LANCEDB_URI)
    builder.provide(LANCE_DB, conn)
    builder.provide(EMBEDDER, SentenceTransformerEmbedder(EMBED_MODEL))
    yield

@coco.fn
async def process_leabharlann_book_chunk(
    chunk: cocoindex.resources.chunk.Chunk,
    filename: pathlib.PurePath,
    id_gen: cocoindex.resources.id.IdGenerator,
    table: Any,
) -> None:
    """Declare one book chunk row in LanceDB."""
    embedder = coco.use_context(EMBEDDER)
    text = chunk.text
    embedding = await embedder.embed(text)
    table.declare_row(
        row=LeabharlannBookChunk(
            id=await id_gen.next_id(text),
            filename=str(filename),
            chunk_text=text,
            chunk_start=chunk.start.char_offset,
            chunk_end=chunk.end.char_offset,
            embedding=embedding,
        ),
    )

@coco.fn
async def leabharlann_books_app_main(sourcedir: pathlib.Path) -> None:
    target_table = await lancedb.mount_table_target(
        LANCE_DB,
        table_name="leabharlann_books",
        table_schema=await lancedb.TableSchema.from_class(
            LeabharlannBookChunk, primary_key=["id"]
        ),
    )
    files = localfs.walk_dir(
        sourcedir,
        recursive=True,
        path_matcher=PatternFilePathMatcher(
            included_patterns=["*.pdf", "*.epub", "*.docx", "*.md"],
            excluded_patterns=["**/.*", "**/node_modules/**", "**/__pycache__/**"],
        ),
        live=True,
        refresh_interval=datetime.timedelta(seconds=60),
    )
    await coco.mount_each(process_leabharlann_book_chunk, files.items(), target_table)

leabharlann_books_app = coco.App(
    coco.AppConfig(name="LeabharlannBooksEmbedding"),
    leabharlann_books_app_main,
    sourcedir=DEFAULT_LEABHARLANN_BOOKS_ROOT,
)
```

The 6-field shape is:

1. **`@coco.lifespan`** — provides the LANCE_DB connection + the EMBEDDER (shared)
2. **`@coco.fn`** — the per-chunk processor (memoized for text-deterministic operations)
3. **`@coco.fn`** — the app entry point (the `xxx_app_main` function)
4. **`lancedb.mount_table_target`** — the output table (primary_key=["id"])
5. **`localfs.walk_dir`** — the source (recursive=True, live=True, refresh_interval=60s)
6. **`coco.App`** — the App instance (the entry point for `cocoindex update`)

## The 100-batch minimum + the HNSW-DROP-THRESHOLD=50 rule

Per `sruth/oideachais/AGENTS.md` + the embedding-pipeline skill:

- **Embeddings batched at minimum 100 per call** (100× performance difference vs unbatched)
- **HNSW indexes dropped before bulk inserts > 50 rows and recreated after** (the 20× speedup rule)

The 2 rules are enforced by the canonical v1 `@coco.fn` pattern
(the `SentenceTransformerEmbedder` from
`cocoindex.ops.sentence_transformers` handles the batching
internally; the `mount_table_target` handles the HNSW
re-creation).

## The `IdGenerator()` stable-id pattern

```python
# Per chunk in @coco.fn
id_gen = IdGenerator()
row_id = await id_gen.next_id(chunk.text)  # stable across re-materialisations
```

The `IdGenerator` returns the **same ID for the same text** across
re-materialisations. This is critical for incremental updates
(CocoIndex uses the ID to detect changes).

## The `Annotated[NDArray, EMBEDDER]` typing

```python
from typing import Annotated
from cocoindex.typing import NDArray

@dataclass
class LeabharlannBookChunk:
    id: str
    filename: str
    chunk_text: str
    chunk_start: int
    chunk_end: int
    embedding: Annotated[NDArray, EMBEDDER]
```

The `Annotated[NDArray, EMBEDDER]` typing tells CocoIndex that the
`embedding` field is computed by the `EMBEDDER` context key. The
embedding is auto-filled by the v1 runtime (no manual
`embedder.embed(text)` call needed).

## The 29-language Tree-sitter chunking

`sruth/oideachais/cocoindex_flows/chunking/languages.py` defines the
29-language detection table. The 29 languages are:
python, typescript, javascript, tsx, jsx, rust, go, java, kotlin,
ruby, swift, c, cpp, csharp, php, scala, haskell, ocaml, lua,
shell, sql, html, css, yaml, toml, json, markdown, dockerfile,
makefile.

The chunking uses `RecursiveSplitter` with
`detect_code_language` for code-aware splits and plain
`RecursiveSplitter` for non-code files.

## The 4 v0-to-v1 migration patterns

| v0 pattern | v1 replacement |
|:--|:--|
| `@cocoindex.flow_def(name=...)` | `@coco.App(coco.AppConfig(name=...))` |
| `flow_builder.add_source(cocoindex.sources.DuckDB(...))` | `localfs.walk_dir(...)` (no DuckDB source in v1) |
| `data_scope["x"] = ...` | `builder.provide(KEY, value)` (via `@coco.lifespan`) |
| `embeddings_collector.collect(id=GeneratedField.UUID, ...)` | `table.declare_row(row=Dataclass(...))` (no `collector` in v1) |

The 4 patterns are documented in the `oideachais-v0-to-v1-migration`
openspec change (round 9 of the multi-quadrant refactor plan).

## The 10 v0 broken modules (the migration backlog)

| Module | Lines | Migration status |
|:--|--:|:--|
| `author_archive_embedding.py` | 600+ | DEFERRED (the BAML `AuthorArchive` schema is still in design) |
| `curriculum_embedding.py` | 400+ | DEFERRED (the v1 `curriculum_embedding_v1` module is in design) |
| `curriculum_translation.py` | 350+ | DEFERRED (the BAML `Translation` schema is in `_archive`) |
| `curriculum_specification_extraction.py` | 300+ | DEFERRED |
| `geospatial_indexing.py` | 400+ | DEFERRED (the v1 geospatial indexer is in design) |
| `learning_outcome_graph.py` | 350+ | DEFERRED (the v1 learning-outcome graph is in design) |
| `ocr_embedding.py` | 300+ | DEFERRED (the v1 OCR embedder is in design) |
| `pdf_embedding.py` | 250+ | DEFERRED (the v1 PDF embedder is in design) |
| `research_embedding.py` | 500+ | DEFERRED (the v1 `research_embedding_v1` module is in design) |
| `site_analysis_embedding.py` | 400+ | DEFERRED (the v1 site analyser is in design) |

The 10 v0 modules live at their original paths for back-compat
but are NOT re-exported via `__init__.py` (the v1 module
hierarchy takes precedence). Migration is a 6-week project per
the oideachais-STATUS.md.

## Worked example: add a new v1 App

1. Create the new file at `sruth/oideachais/cocoindex_flows/xxx_embedding.py`:

2. Define the dataclass:

   ```python
   from dataclasses import dataclass
   from typing import Annotated
   from cocoindex.typing import NDArray

   @dataclass
   class XxxChunk:
       id: str
       source: str
       text: str
       embedding: Annotated[NDArray, EMBEDDER]
   ```

3. Define the v1 App:

   ```python
   @coco.lifespan
   async def xxx_lifespan(builder):
       # (shared with leabharlann_lifespan)
       yield

   @coco.fn
   async def process_xxx_chunk(chunk, source, id_gen, table):
       embedder = coco.use_context(EMBEDDER)
       embedding = await embedder.embed(chunk.text)
       table.declare_row(row=XxxChunk(
           id=await id_gen.next_id(chunk.text),
           source=str(source),
           text=chunk.text,
           embedding=embedding,
       ))

   @coco.fn
   async def xxx_app_main(sourcedir: pathlib.Path) -> None:
       target_table = await lancedb.mount_table_target(
           LANCE_DB, table_name="xxx_chunks",
           table_schema=await lancedb.TableSchema.from_class(XxxChunk, primary_key=["id"]),
       )
       files = localfs.walk_dir(sourcedir, recursive=True, ...)
       await coco.mount_each(process_xxx_chunk, files.items(), target_table)

   xxx_app = coco.App(
       coco.AppConfig(name="XxxEmbedding"),
       xxx_app_main,
       sourcedir=DEFAULT_XXX_ROOT,
   )
   ```

4. Add the App to `sruth/oideachais/cocoindex_flows/__init__.py`:

   ```python
   try:
       from .xxx_embedding import xxx_app
       __all__ += ["xxx_app"]
   except ImportError:
       pass  # CocoIndex not available
   ```

5. Add a Dagster asset at `sruth/oideachais/dagster_defs/assets/xxx_assets.py:xxx_chunks`.

6. Update `openspec/specs/oideachais-pipeline/spec.md` to add the
   new V1 App requirement.

## Common failure modes

| Symptom | Cause | Fix |
|:--|:--|:--|
| `cocoindex update` fails with `ModuleNotFoundError: No module named 'cocoindex.flow_def'` | The v0 module is being imported | Add the module to the `try/except` guard in `__init__.py` |
| The LanceDB table is empty after the App runs | The `mount_table_target` is missing the `primary_key` | Add `primary_key=["id"]` to the `TableSchema.from_class` call |
| The embeddings are wrong shape | The `Annotated[NDArray, EMBEDDER]` typing is missing | Add the typing to the dataclass field |
| The App hangs on startup | The `@coco.lifespan` is missing the `yield` | Add `yield` at the end of the lifespan function |
| The IDs are unstable across re-materialisations | The `IdGenerator` is not used | Use `await id_gen.next_id(chunk.text)` instead of `uuid.uuid4()` |
| The HNSW index is slow on bulk inserts | The index is being created at insert time | Drop the index, insert, recreate the index (the canonical 50-row threshold) |
| `cocoindex_v1_conformance` reports `R1 FAIL — no shared_lifespan import` | The App has its own `@coco.lifespan` instead of delegating | Import `shared_lifespan` from `._lifespan` and delegate (REFACTORING.md item 12) |
| `cocoindex_v1_conformance` reports `R2 FAIL` | The App declared a non-canonical ContextKey without an `# R2-exempt:` comment | Add the `# R2-exempt: <reason>` comment OR remove the ContextKey declaration in favour of the canonical one |
| `cocoindex_v1_conformance` reports `R3 FAIL` | The `coco.App(...)` is inside a function body | Move the `coco.App(...)` construction to module scope |
| `cocoindex_v1_conformance` reports `R4 FAIL` | No `@coco.fn(` decorator | Add `@coco.fn(memo=True)` to the processing function |

## The 4-rule conformance contract (NEW 2026-06)

`cocoindex_v1_conformance.py` is the 14th v1 App. It's a static AST
linter that checks every other v1 App against 4 rules:

- **R1** — `from ._lifespan import shared_lifespan` (delegates to the
  canonical shared lifespan).
- **R2** — Either imports the canonical ContextKeys (`LANCE_DB`,
  `EMBEDDER`, `RESOLVED_FILE_REGISTRY`) from `._lifespan`, OR
  declares additional ones with a sibling `# R2-exempt: <reason>`
  comment on the line above.
- **R3** — `coco.App(...)` is at module scope (NOT inside a function
  body or class definition).
- **R4** — At least one `@coco.fn(` decorator (for processing
  functions).

Run it via:

```bash
mise run upstream:conformance
# or equivalently:
uv run python -c 'import asyncio; from sruth.oideachais.cocoindex_flows.cocoindex_v1_conformance import run_conformance_check; report = asyncio.run(run_conformance_check()); print(report.summary())'
```

The Dagster asset `cocoindex_v1_conformance_check`
(`sruth/oideachais/dagster_defs/assets/upstream_monitoring_assets.py`)
runs this on every materialisation and writes a
`conformance_check_history` row to LanceDB so we can detect regressions
in CI.

## The shared lifespan (REFACTORING.md item 12)

Every v1 App MUST import `shared_lifespan` from
`sruth/oideachais/cocoindex_flows/_lifespan.py` and delegate to it
inside its own `@coco.lifespan` function:

```python
from ._lifespan import (
    EMBEDDER,
    LANCE_DB,
    LANCEDB_URI,
    EMBED_MODEL,
    EMBED_DIM,
    RESOLVED_FILE_REGISTRY,
    shared_lifespan,
)

@coco.lifespan
async def my_app_lifespan(builder: coco.EnvironmentBuilder) -> AsyncIterator[None]:
    async with shared_lifespan(builder):
        # Only add App-specific ContextKeys here. The shared lifespan
        # provides LANCE_DB + EMBEDDER + RESOLVED_FILE_REGISTRY.
        if COCOINDEX_AVAILABLE:
            # R2-exempt: KG_DB is bound to the <my_app>_graph FalkorDB
            # graph, which is App-specific (this App declares <MyNode>
            # schemas that only this App uses). Sharing it across Apps
            # would couple this surface to others.
            builder.provide(KG_DB, falkordb.ConnectionFactory(...))
        yield
```

**What `_lifespan.py` provides** (the canonical home for the 3
ContextKeys):

- `LANCE_DB` — `coco.ContextKey[lancedb.LanceAsyncConnection]`
- `EMBEDDER` — `coco.ContextKey[SentenceTransformerEmbedder]`
- `RESOLVED_FILE_REGISTRY` — the dict of `{source_path: sha256}`
  keys used by the file-graph Apps

Plus 3 module-level constants (`LANCEDB_URI`, `EMBED_MODEL`,
`EMBED_DIM`) that every App reads via `from ._lifespan import ...`.

The `cocoindex_v1_conformance` linter enforces that every App
delegates to this shared lifespan (R1) and that additional
ContextKeys are flagged as `# R2-exempt` (R2).

## Cross-references

- `.agents/skills/cocoindex/SKILL.md` — the generic v1 patterns
- `.agents/skills/dagster/SKILL.md` — the Dagster asset + sensor patterns
- `.agents/skills/lancedb/SKILL.md` — the vector search + HNSW indexing
- `.agents/skills/oideachais-leabharlann/SKILL.md` — the 3 v1 Apps for the leabharlann pipeline
- `.agents/skills/oideachais-baml-schemas/SKILL.md` — the 9 + 4 + 6 BAML files
- `.agents/skills/embedding-pipeline/SKILL.md` — the 100-batch minimum + the HNSW-DROP-THRESHOLD=50 rule
- `sruth/oideachais/cocoindex_flows/leabharlann_embedding.py` — the canonical v1 home (the 4 leabharlann Apps)
- `sruth/oideachais/cocoindex_flows/codebase_indexing.py` — the canonical v1 home (the codebase 7-node/7-edge graph)
- `sruth/oideachais/cocoindex_flows/__init__.py` — the v0-vs-v1 guard
- `sruth/oideachais/cocoindex_flows/README.md` — the v0 vs v1 status table
- `sruth/oideachais/cocoindex_flows/chunking/languages.py` — the 29-language detection table
- `openspec/specs/oideachais-cocoindex-v1-migration/spec.md` — the canonical spec

## Leabharlann inbox App (App 3a — 2026-06-29)

Added in the `2026-06-29-leabharlann-email-inbox-pipeline` change.
The 4th leabharlann App, `leabharlann_inbox_embedding`, lives in the
same `leabharlann_embedding.py` file as Apps 1-3 and shares the
same `EMBEDDER` + `LANCE_DB` ContextKeys. It reads MBOX files from
`/srv/mailcow-exports/` (populated by Mailcow's
`dovecot_imapsync_runner` + the `mailcow-export` companion
container), recurses into each MBOX via the `mailbox` stdlib,
yields one chunk per message (`from + subject + first 2000 chars
of body`), and writes to the `oideachais_inbox_messages` LanceDB
table with the columns `(id, account, year, date_iso, subject,
sender, recipients, body_excerpt, embedding, baml_class,
baml_urgency, thread_id)`. A cosine vector index on `embedding` +
an FTS index on `subject + body_excerpt` power the
`search_inbox(query, account=None, year=None, baml_class=None,
urgency_min=None, limit=20)` hybrid search handler.

The full pipeline (DLT + BAML + Dagster + marimo + cognify) is
documented in
[`.agents/skills/oideachais-email-triage/SKILL.md`](../oideachais-email-triage/SKILL.md).

