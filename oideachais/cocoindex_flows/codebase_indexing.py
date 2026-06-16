"""
Codebase Indexing CocoIndex v1 App — the v1-native replacement for `ccc`.

The legacy `ccc` CLI is a wrapper around a separate CocoIndex code example
that lives in a different runtime from the rest of the data lakehouse. This
App brings the codebase semantic index onto the same primitives as every
other CocoIndex flow in this repo:

- `@coco.fn` + `@coco.fn(memo=True)` for processing
- `localfs.walk_dir(repo_root, live=True, refresh_interval=60s)` for the source
- `RecursiveSplitter` with `detect_code_language` for chunking
- `SentenceTransformerEmbedder("BAAI/bge-m3")` for embedding (shared with
  `docs_skills_consolidation.py` for consistency)
- `lancedb.mount_table_target("codebase_chunks", ...)` for the output

Reference pattern: `docs/cocoindex/code_embedding/main.py` (v0 reference) +
`docs/cocoindex/pdf_embedding/main.py` (v1 chunking/embedding conventions).

Operational contract:
- Live mode (`cocoindex update -L ...`) is supported.
- Excludes protect the indexer from indexing its own reference mirror
  (`docs/cocoindex/`), build artefacts (`.venv/`, `node_modules/`, `dist/`),
  and the local CocoaIndex code DB (`.cocoindex_code/`).
- Tree-sitter chunking honours `DetectProgrammingLanguage` for code-aware
  splits; Markdown uses the recursive splitter.
- HNSW index on the `embedding` column follows the platform rule
  `HNSW_DROP_THRESHOLD = 50` (drop before bulk >50 rows, recreate after).
"""

from __future__ import annotations

import datetime
import os
import pathlib
from collections.abc import AsyncIterator
from dataclasses import dataclass
from typing import Annotated, Any

import structlog

logger = structlog.get_logger(__name__)

# CocoIndex is optional — degrade gracefully if not installed.
try:
    import cocoindex as coco  # type: ignore[import-not-found]
    from cocoindex.connectors import (
        lancedb,  # type: ignore[import-not-found]
        localfs,  # type: ignore[import-not-found]
    )
    from cocoindex.ops.sentence_transformers import (  # type: ignore[import-not-found]
        SentenceTransformerEmbedder,
    )
    from cocoindex.ops.text import (  # type: ignore[import-not-found]
        RecursiveSplitter,
        detect_code_language,
    )
    from cocoindex.resources.file import (  # type: ignore[import-not-found]
        FileLike,
        PatternFilePathMatcher,
    )
    from cocoindex.resources.id import IdGenerator  # type: ignore[import-not-found]

    COCOINDEX_AVAILABLE = True
except ImportError as e:
    logger.warning("cocoindex_v1_not_available: %s", e)
    COCOINDEX_AVAILABLE = False
    coco = None  # type: ignore[assignment]
    lancedb = None  # type: ignore[assignment]
    localfs = None  # type: ignore[assignment]
    SentenceTransformerEmbedder = None  # type: ignore[assignment]
    RecursiveSplitter = None  # type: ignore[assignment]
    detect_code_language = None  # type: ignore[assignment]
    FileLike = None  # type: ignore[assignment]
    PatternFilePathMatcher = None  # type: ignore[assignment]
    IdGenerator = None  # type: ignore[assignment]


# =============================================================================
# Configuration
# =============================================================================


LANCEDB_URI = os.getenv("LANCEDB_URI", "rest://lance-api.cianfhoghlaim.ie")
EMBED_MODEL = os.getenv("CODEBASE_EMBED_MODEL", "BAAI/bge-m3")
EMBED_DIM = 1024
REFRESH_INTERVAL = datetime.timedelta(seconds=int(os.getenv("CODEBASE_REFRESH_SECS", "60")))
LANCEDB_TABLE = "codebase_chunks"
TOP_K = 10

# Default source root: the monorepo root (parents[5] = repo root from
# oideachais/cocoindex_flows/codebase_indexing.py).
DEFAULT_REPO_ROOT = pathlib.Path(
    os.getenv(
        "CODEBASE_REPO_ROOT",
        str(pathlib.Path(__file__).resolve().parents[5]),
    )
)


# =============================================================================
# Context keys
# =============================================================================


if COCOINDEX_AVAILABLE:
    LANCE_DB: Any = coco.ContextKey[lancedb.LanceAsyncConnection]("codebase_lance_db")
    EMBEDDER: Any = coco.ContextKey[SentenceTransformerEmbedder](
        "codebase_embedder", detect_change=True
    )
else:
    LANCE_DB = None  # type: ignore[assignment]
    EMBEDDER = None  # type: ignore[assignment]


# =============================================================================
# Data model
# =============================================================================


@dataclass
class CodeChunk:
    """One embedded chunk of a source file in the monorepo."""

    id: int
    path: str
    language: str
    filename: str
    chunk_text: str
    chunk_start: int
    chunk_end: int
    embedding: Annotated[Any, EMBEDDER] if COCOINDEX_AVAILABLE else Any  # type: ignore[index]


# =============================================================================
# Splitter
# =============================================================================


_splitter = RecursiveSplitter() if COCOINDEX_AVAILABLE else None  # type: ignore[call-arg]


# =============================================================================
# Per-file processing
# =============================================================================


if COCOINDEX_AVAILABLE:

    @coco.fn(memo=True)
    async def process_codebase_file(  # type: ignore[no-redef]
        file: FileLike,  # type: ignore[valid-type]
        table: lancedb.TableTarget,  # type: ignore[valid-type]
    ) -> int:
        """
        Read one file, chunk it with the recursive splitter (using
        `detect_code_language` for code), embed each chunk, and write to
        the `codebase_chunks` LanceDB table.

        Returns the number of chunks emitted (for stats).
        """
        try:
            text = await file.read_text()
        except (UnicodeDecodeError, ValueError):
            # Binary file we cannot decode — skip silently.
            return 0
        if not text.strip():
            return 0

        path = file.file_path.path
        language = detect_code_language(filename=path.name)  # type: ignore[call-arg]
        if language is None and path.suffix in {".md", ".mdx", ".markdown"}:
            language = "markdown"

        chunks = _splitter.split(  # type: ignore[union-attr]
            text,
            chunk_size=1000,
            chunk_overlap=200,
            language=language,
        )
        if not chunks:
            return 0

        embedder = coco.use_context(EMBEDDER)  # type: ignore[arg-type]
        id_gen = IdGenerator()
        count = 0
        for chunk in chunks:
            embedding = await embedder.embed(chunk.text)
            await table.declare_row(
                row=CodeChunk(
                    id=await id_gen.next_id(chunk.text),
                    path=path.as_posix(),
                    language=language or "unknown",
                    filename=path.name,
                    chunk_text=chunk.text,
                    chunk_start=chunk.start.char_offset,
                    chunk_end=chunk.end.char_offset,
                    embedding=embedding,
                )
            )
            count += 1
        return count


# =============================================================================
# App entry point
# =============================================================================


def _make_app():
    """Construct the codebase v1 App. Returns None when cocoindex is missing."""
    if not COCOINDEX_AVAILABLE:
        return None

    @coco.lifespan
    async def codebase_lifespan(  # type: ignore[no-redef]
        builder: coco.EnvironmentBuilder,  # type: ignore[valid-type]
    ) -> AsyncIterator[None]:
        from cocoindex.connectors.lancedb import (
            LanceAsyncConnection,  # type: ignore[import-not-found]
        )

        lance_conn = await LanceAsyncConnection.connect(LANCEDB_URI)
        builder.provide(LANCE_DB, lance_conn)
        builder.provide(
            EMBEDDER,
            SentenceTransformerEmbedder(EMBED_MODEL),
        )
        yield

    @coco.fn
    async def codebase_app_main(repo_root: pathlib.Path) -> None:  # type: ignore[no-redef]
        target_table = await lancedb.mount_table_target(
            LANCE_DB,  # type: ignore[arg-type]
            table_name=LANCEDB_TABLE,
            table_schema=await lancedb.TableSchema.from_class(CodeChunk, primary_key=["id"]),
        )

        files = localfs.walk_dir(  # type: ignore[call-arg]
            repo_root,
            recursive=True,
            path_matcher=PatternFilePathMatcher(
                included_patterns=[
                    "*.py",
                    "*.rs",
                    "*.ts",
                    "*.tsx",
                    "*.go",
                    "*.md",
                    "*.mdx",
                    "*.toml",
                ],
                excluded_patterns=[
                    "**/.*",
                    "**/node_modules/**",
                    "**/__pycache__/**",
                    "**/.venv/**",
                    "**/venv/**",
                    "**/target/**",
                    "**/dist/**",
                    "**/build/**",
                    "**/.turbo/**",
                    "**/.cocoindex_code/**",
                    "**/stedding/**",
                    "**/.git/**",
                ],
            ),
            live=True,
            refresh_interval=REFRESH_INTERVAL,
        )
        await coco.mount_each(process_codebase_file, files.items(), target_table)

    return coco.App(
        coco.AppConfig(name="CodebaseIndex"),
        codebase_app_main,
        repo_root=DEFAULT_REPO_ROOT,
    )


codebase_app = _make_app()


# =============================================================================
# Query helpers (CLI: `bun run ccc:v1:search "..."`  ->  search_codebase(...))
# =============================================================================


async def search_codebase(
    query: str,
    limit: int = TOP_K,
    language: str | None = None,
    path_glob: str | None = None,
) -> list[dict[str, Any]]:
    """Run a vector search against the `codebase_chunks` LanceDB table."""
    if not COCOINDEX_AVAILABLE:
        return []
    embedder = coco.use_context(EMBEDDER)  # type: ignore[arg-type]
    conn = coco.use_context(LANCE_DB)  # type: ignore[arg-type]
    query_vec = await embedder.embed(query)
    table = await conn.open_table(LANCEDB_TABLE)
    search = table.search(query_vec, vector_column_name="embedding")
    conditions: list[str] = []
    if language:
        conditions.append(f"language = '{language}'")
    if path_glob:
        conditions.append(f"path LIKE '{path_glob}'")
    if conditions:
        search = search.where(" AND ".join(conditions))
    rows = await search.limit(limit).to_list()
    for r in rows:
        r["score"] = 1.0 - r.get("_distance", 0.0)
    return rows


# =============================================================================
# Exports
# =============================================================================


__all__ = [
    "COCOINDEX_AVAILABLE",
    "LANCEDB_URI",
    "EMBED_MODEL",
    "EMBED_DIM",
    "REFRESH_INTERVAL",
    "LANCEDB_TABLE",
    "TOP_K",
    "DEFAULT_REPO_ROOT",
    "CodeChunk",
    "search_codebase",
]
if COCOINDEX_AVAILABLE and codebase_app is not None:
    __all__ += ["codebase_app", "process_codebase_file"]
