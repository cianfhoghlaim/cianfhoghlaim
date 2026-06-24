# `oideachais/cocoindex_flows/` — CocoIndex Embedding Flows

**Last updated:** 2026-06-16

CocoIndex flows that embed dlt-extracted documents into LanceDB for semantic search. **The venv has `cocoindex==1.0.9` (v1 API)**; the v0 DSL (`@cocoindex.flow_def`, `FlowBuilder`, `DataScope`, `cocoindex.sources.DuckDB`, `cocoindex.targets.lancedb`, `cocoindex.functions.SplitRecursively`, `cocoindex.functions.SentenceTransformerEmbed`) is removed and the v0 modules in this directory are broken at import time.

## v0 vs v1 status

| Flow | API | Status | Action |
|:--|:--|:--|:--|
| `leabharlann_embedding.py` | v1 | ✅ working | — |
| `author_archive_embedding.py` | v0 | ❌ broken on import | DEPRECATED 2026-06-24, archived at `_v0_archive/` |
| `curriculum_embedding.py` | v0 | ❌ broken on import | DEPRECATED 2026-06-24, archived at `_v0_archive/` |
| `curriculum_translation.py` | v0 | ❌ broken on import | DEPRECATED 2026-06-24, archived at `_v0_archive/` |
| `curriculum_specification_extraction.py` | v0 | ❌ broken on import | DEPRECATED 2026-06-24, archived at `_v0_archive/` |
| `geospatial_indexing.py` | v0 | ❌ broken on import | DEPRECATED 2026-06-24, archived at `_v0_archive/` |
| `learning_outcome_graph.py` | v0 | ❌ broken on import | DEPRECATED 2026-06-24, archived at `_v0_archive/` |
| `ocr_embedding.py` | v0 | ❌ broken on import | DEPRECATED 2026-06-24, archived at `_v0_archive/` |
| `pdf_embedding.py` | v0 | ❌ broken on import | DEPRECATED 2026-06-24, archived at `_v0_archive/` |
| `research_embedding.py` | v0 | ❌ broken on import | DEPRECATED 2026-06-24, archived at `_v0_archive/` |
| `site_analysis_embedding.py` | v0 | ❌ broken on import | DEPRECATED 2026-06-24, archived at `_v0_archive/` |

**`oideachais/cocoindex_flows/__init__.py` uses a guarded `try/except` import so the package loads despite the broken v0 modules. The v0 modules are not re-exported; only the v1 `leabharlann_embedding` module is.**

## The canonical v1 pattern (in `leabharlann_embedding.py`)

```python
# Shared context keys (per the v1 best practice)
LANCEDB_URI = os.getenv("LANCEDB_URI", "rest://lance-api.cianfhoghlaim.ie")
EMBED_MODEL = os.getenv("LEABHARLANN_EMBED_MODEL", "BAAI/bge-large-en-v1.5")
LANCE_DB = coco.ContextKey[lancedb.LanceAsyncConnection]("leabharlann_lance_db")
EMBEDDER = coco.ContextKey[SentenceTransformerEmbedder]("leabharlann_embedder", detect_change=True)

# Lifespan provides the shared connection + embedder
@coco.lifespan
async def leabharlann_lifespan(builder: coco.EnvironmentBuilder) -> AsyncIterator[None]:
    conn = await lancedb.connect_async(LANCEDB_URI)
    builder.provide(LANCE_DB, conn)
    builder.provide(EMBEDDER, SentenceTransformerEmbedder(EMBED_MODEL))
    yield

# App
app = coco.App(coco.AppConfig(name="..."), app_main, sourcedir=...)

# Source: local filesystem with live mode
files = localfs.walk_dir(
    sourcedir,
    recursive=True,
    path_matcher=PatternFilePathMatcher(included_patterns=["**/*.pdf"]),
    live=True,  # pass -L to `cocoindex update` to actually run live
)
await coco.mount_each(process_file, files.items(), target_table)

# Processing
@coco.fn(memo=True)
async def process_file(file: FileLike, table: Any) -> None:
    text = await file.read_text()
    chunks = _splitter.split(text, chunk_size=2000, chunk_overlap=500, language="markdown")
    id_gen = IdGenerator()
    await coco.map(process_chunk, chunks, file.file_path.path, id_gen, table)

@coco.fn
async def process_chunk(chunk: Chunk, filename: pathlib.PurePath, id_gen: IdGenerator, table: Any) -> None:
    embedder = coco.use_context(EMBEDDER)
    table.declare_row(row=DocEmbedding(
        id=await id_gen.next_id(chunk.text),
        filename=str(filename),
        text=chunk.text,
        embedding=await embedder.embed(chunk.text),
    ))

# Target: LanceDB
target_table = await lancedb.mount_table_target(
    LANCE_DB,
    table_name="...",
    table_schema=await lancedb.TableSchema.from_class(DocEmbedding, primary_key=["id"]),
)
```

Reference: `docs/cocoindex/AGENTS.md` and the 5 canonical examples:
- `docs/cocoindex/pdf_embedding/main.py` — PDFs → markdown → chunks → embed → pgvector
- `docs/cocoindex/code_embedding_lancedb/main.py` — code → chunks → embed → LanceDB
- `docs/cocoindex/paper_metadata/main.py` — PDFs → LLM extract → embed title/abstract → pgvector
- `docs/cocoindex/multi_format_indexing/main.py` — multi-MIME dispatch
- `docs/cocoindex/live_updates/main.py` — long-running watcher

## Per-flow catalogue

### `leabharlann_embedding.py` (v1, working)

Three v1 Apps + three search handlers:

| App | LanceDB table | Source | Embed model | Status |
|:--|:--|:--|:--|:--|
| `LeabharlannBooksEmbedding` | `leabharlann_books` | `leabharlann/{gaeilge,aigne}/` | BGE-large-en-v1.5 (1024-d) | ✅ |
| `LeabharlannZoteroEmbedding` | `leabharlann_zotero` | `leabharlann/zotero/` | BGE-large-en-v1.5 (1024-d) | ✅ |
| `LeabharlannTakeoutEmbedding` | `leabharlann_takeout` | `stedding/Takeout/` | BGE-large-en-v1.5 (1024-d) | ✅ |

Search handlers: `search_leabharlann_books`, `search_leabharlann_zotero`, `search_leabharlann_takeout` (each async, top-K cosine similarity with column-level filters).

### `author_archive_embedding.py` (v0, broken)

Legacy v0 flow for the UoG + Gemini Deep Research + Google Takeout pipeline. Imports `@cocoindex.flow_def` which was removed in cocoindex==1.0.9. **Needs migration to v1** (deferred to a follow-up change).

### `curriculum_embedding.py` (v0, broken)

Legacy v0 flow for the Ireland primary/JC/SC curriculum. `CurriculumEmbeddingFlow` class with `TextChunker`, `EmbeddingEngine`, `LanceDBEmbeddingSink`. Imports `@cocoindex.flow_def`. **Needs migration to v1.**

### `curriculum_translation.py` (v0, broken)

Legacy v0 flow for Celtic language translation. **Needs migration to v1.**

### `curriculum_specification_extraction.py` (v0, broken)

Legacy v0 flow for extracting curriculum specification chunks. **Needs migration to v1.**

### `geospatial_indexing.py` (v0, broken)

Legacy v0 flow for H3 spatial indexing. **Needs migration to v1.**

### `learning_outcome_graph.py` (v0, broken)

Legacy v0 flow for the learning outcome knowledge graph. **Needs migration to v1.**

### `ocr_embedding.py` (v0, broken)

Legacy v0 flow for OCR result embeddings. **Needs migration to v1.**

### `pdf_embedding.py` (v0, broken)

Legacy v0 flow for PDF embeddings. **Needs migration to v1.**

### `research_embedding.py` (v0, broken)

Legacy v0 flow for the BUNCHLOCH research archive. `BunchlochDocumentEmbedding` + `BunchlochCodeEmbedding`. Imports `@cocoindex.flow_def`. **Needs migration to v1.**

### `site_analysis_embedding.py` (v0, broken)

Legacy v0 flow for site analysis (URL → embedding). **Needs migration to v1.**

## How to run the v1 flows

```bash
# One-shot catch-up
cocoindex update oideachais.cocoindex_flows.leabharlann_embedding:LeabharlannBooksEmbedding
cocoindex update oideachais.cocoindex_flows.leabharlann_embedding:LeabharlannZoteroEmbedding
cocoindex update oideachais.cocoindex_flows.leabharlann_embedding:LeabharlannTakeoutEmbedding

# Live mode (continuous monitoring)
cocoindex update -L oideachais.cocoindex_flows.leabharlann_embedding:LeabharlannBooksEmbedding
```

The Dagster assets `oideachais_cocoindex_books_update`, `oabharlann_cocoindex_zotero_update`, `oideachann_cocoindex_takeout_update` invoke these via `subprocess.run(["cocoindex", "update", ...])`.

## How the v0 modules are currently imported

`oideachais/cocoindex_flows/__init__.py`:

```python
try:
    from .leabharlann_embedding import (
        leabharlann_books_app, leabharlann_zotero_app, leabharlann_takeout_app,
        search_leabharlann_books, search_leabharlann_zotero, search_leabharlann_takeout,
        # ... 14 symbols
    )
    _leabharlann_imported = True
except ImportError as e:
    _sl.get_logger().warning("leabharlann_embedding_import_failed: %s", e)
    _leabharlann_imported = False
```

The v0 modules are NOT re-exported. To use them, import them directly:

```python
from oideachais.cocoindex_flows.research_embedding import (
    document_embedding_flow, code_embedding_flow, search_documents,
)
```

This will raise `AttributeError` on cocoindex==1.0.9. **The migration is the queued work in `oideachais/REFACTORING.md` #6.**

## Related

- `oideachais/STATUS.md` § 3 — CocoIndex v0 vs v1 status.
- `oideachais/REFACTORING.md` — refactor backlog including the v0 → v1 migration.
- `docs/cocoindex/AGENTS.md` — the canonical v1 patterns.
- `.agents/skills/cocoindex/SKILL.md` — the v1 skill with the v0→v1 mapping table.
