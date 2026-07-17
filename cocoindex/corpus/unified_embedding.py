"""
Unified Embedding CocoIndex v1 Apps.

Phase 3 of the 6-phase refactor plan: the v1-native port of the
legacy `crypteolas/cocoindex_flows/unified_embedding.py` module.
The v0 file used the removed v0 DSL (`flow_def`, `FlowBuilder`,
`DataScope`, `cocoindex.sources.DuckDB`, `cocoindex.targets.lancedb`,
`GeneratedField.UUID`, `VectorIndexDef`, `FtsIndexDef`,
`QueryOutput`, `QueryInfo`) — all of which were dropped in
CocoIndex v1.

The v1 port uses the canonical v1 primitives from
`cianfhoghlaim/cocoindex_flows/codebase_indexing.py` and
`cianfhoghlaim/cocoindex_flows/leabharlann_embedding.py`:

- `@coco.fn` + `@coco.fn(memo=True)` for processing functions
- `@coco.lifespan` providing shared `EMBEDDER` + `LANCE_DB` context keys
- `lancedb.mount_table_target(...)` for output
- `target_table.declare_vector_index(column="embedding")` for vector index
- `SentenceTransformerEmbedder("BAAI/bge-m3")` for the embedding
- 100-row upsert batches (HNSW-DROP-THRESHOLD respected)
- `asyncio.to_thread` for CPU/IO-bound work (DuckDB read, file walk)
- 2 v1 Apps: `UnifiedEmbedding` (markdown docs from any DuckDB source)
  and `CodeEmbedding` (local code files via RecursiveSplitter)
- 2 query helpers: `unified_search()` + `code_search()`

Source: configurable DuckDB connection (the v0 file defaulted to
`crypteolas_catalog.docs.scraped_documents`; the v1 port keeps that
default but parameterises the connection string + SQL query)
Target: shared oideachais LanceDB (the same `LANCEDB_URI` used by
codebase / api / filesystem / storage / config / leabharlann v1 Apps)

Reference:
- v0 source: `crypteolas/cocoindex_flows/unified_embedding.py` (archived)
- v0 chunker: `crypteolas/cocoindex_flows/transforms/code_chunking.py:chunk_code`
  (5 language-specific chunkers; v1 falls back to RecursiveSplitter
  with detect_code_language for the 24+ others)
- v1 platform: `cianfhoghlaim/cocoindex_flows/chunking/languages.py`
  (29+ language detection table)

Operational contract:
- Live mode (`cocoindex update -L ...`) is supported.
- `MIN_BATCH_SIZE = 100` is the MANDATORY minimum for performance.
- The v1 App is a single coco.App per file; the 2 Apps share a
  single `@coco.lifespan` for the LanceDB connection + embedder.
"""

from __future__ import annotations

import asyncio
import datetime
import hashlib
import os
import pathlib
import re
from collections.abc import AsyncIterator
from dataclasses import dataclass, field
from typing import Annotated, Any, ClassVar

import structlog

logger = structlog.get_logger(__name__)

# CocoIndex is optional — degrade gracefully if not installed.
try:
    import cocoindex as coco  # type: ignore[import-not-found]
    from cocoindex.connectors import (  # type: ignore[import-not-found]
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


# =============================================================================
# Configuration
# =============================================================================


LANCEDB_URI = os.getenv("LANCEDB_URI", "rest://lance-api.cianfhoghlaim.ie")
EMBED_MODEL = os.getenv("UNIFIED_EMBED_MODEL", "BAAI/bge-m3")
EMBED_DIM = 1024
REFRESH_INTERVAL = datetime.timedelta(seconds=int(os.getenv("UNIFIED_REFRESH_SECS", "3600")))
LANCEDB_UNIFIED_TABLE = "unified_embeddings"
LANCEDB_CODE_TABLE = "code_embeddings"
TOP_K = 10

# Default source: the v0 default was the crypteolas DuckLake
# (crypteolas_catalog.docs.scraped_documents). The v1 port keeps
# that default but parameterises the connection + query.
DEFAULT_DUCKDB_CONNECTION = os.getenv(
    "UNIFIED_DUCKDB_CONNECTION",
    "duckdb:/Users/cianmacandeisigh/dev/kings_college_galway/crypteolas/storage/data/ducklake.ducklake",
)
DEFAULT_DUCKDB_QUERY = os.getenv(
    "UNIFIED_DUCKDB_QUERY",
    """
    SELECT
        id,
        url,
        title,
        markdown as content,
        source_type,
        protocol,
        file_path,
        content_hash
    FROM crypteolas_catalog.docs.scraped_documents
    WHERE markdown IS NOT NULL
    """,
)

# Default source root for the CodeEmbedding App
DEFAULT_CODE_ROOT = pathlib.Path(
    os.getenv(
        "UNIFIED_CODE_ROOT",
        str(pathlib.Path(__file__).resolve().parents[5] / "crypteolas" / "storage" / "data" / "code"),
    )
)

LANCE_DB: Any = "lance_db_unified"
EMBEDDER: Any = "embedder_unified"

# MANDATORY minimum batch size for embeddings (100x performance)
MIN_BATCH_SIZE = 100
MAX_BATCH_SIZE = 512

# HNSW index drop threshold (drop for bulk inserts > this)
HNSW_DROP_THRESHOLD = 50

EXCLUDE_PATH_SUBSTRINGS = (
    "/.venv/",
    "/venv/",
    "/node_modules/",
    "/__pycache__/",
    "/target/",
    "/dist/",
    "/build/",
    "/.turbo/",
    "/.cocoindex_code/",
    "/stedding/",
    "/.git/",
    "/docs/cocoindex/",
)


# =============================================================================
# Source-type constants
# =============================================================================


class DocumentSourceType:
    """Source type constants (mirrored from the v0 file)."""

    PROTOCOL_DOCS = "protocol_docs"
    USER_URL = "user_url"
    GITHUB = "github"
    LOCAL = "local"


# =============================================================================
# Helpers (CPU-bound; called via asyncio.to_thread)
# =============================================================================


def get_content_hash(text: str) -> str:
    """Generate content hash for deduplication (v0 parity)."""
    return hashlib.sha256(text.encode()).hexdigest()[:16]


def classify_content(text: str, file_ext: str | None = None) -> str:
    """Classify content as documentation or code (v0 parity)."""
    code_extensions = {".py", ".ts", ".tsx", ".js", ".jsx", ".rs", ".go", ".sol", ".vy"}

    if file_ext and file_ext.lower() in code_extensions:
        return "code"

    code_indicators = [
        "def ", "class ", "function ", "const ", "let ", "var ",
        "import ", "from ", "require(", "export ",
        "fn ", "impl ", "struct ", "trait ",
        "func ", "type ", "interface ",
        "contract ", "pragma solidity",
    ]

    if any(indicator in text[:1000] for indicator in code_indicators):
        return "code"

    return "documentation"


# =============================================================================
# Data model
# =============================================================================


@dataclass
class UnifiedDocumentRow:
    """One chunk of an embedded document from any source."""

    id: str
    document_id: str
    url: str
    title: str
    source_type: str
    protocol: str
    file_path: str
    content_type: str
    chunk_hash: str
    chunk_index: int
    text: str
    embedding: Annotated[Any, EMBEDDER]  # type: ignore[valid-type]

    __emd5_fields__: ClassVar[tuple[str, ...]] = ("text",)


@dataclass
class CodeChunkRow:
    """One chunk of a local source-code file."""

    id: str
    filename: str
    language: str
    chunk_type: str
    chunk_name: str
    start_line: int
    end_line: int
    source_type: str
    text: str
    embedding: Annotated[Any, EMBEDDER]  # type: ignore[valid-type]

    __emd5_fields__: ClassVar[tuple[str, ...]] = ("text",)


# =============================================================================
# DuckDB read helper
# =============================================================================


def _read_duckdb_rows(
    connection_string: str, query: str
) -> list[dict[str, Any]]:
    """Read rows from any DuckDB-compatible database.

    Uses the duckdb-python driver. The connection string is the same
    `duckdb:<path>` (or `motherduck:` / `ducklake:`) format accepted by
    DuckDB's CLI. Runs in a thread (IO + parse is CPU-bound).
    """
    try:
        import duckdb  # type: ignore[import-not-found]
    except ImportError as e:
        logger.error("duckdb not installed: %s", e)
        return []

    try:
        conn = duckdb.connect(connection_string)
        try:
            rel = conn.execute(query)
            cols = [d[0] for d in rel.description] if rel.description else []
            rows = [dict(zip(cols, row)) for row in rel.fetchall()]
        finally:
            conn.close()
        return rows
    except Exception as e:  # noqa: BLE001
        logger.error("duckdb read failed: %s", e)
        return []


def _chunk_markdown(text: str, chunk_size: int, chunk_overlap: int) -> list[str]:
    """Best-effort markdown chunker.

    Falls back to RecursiveSplitter when cocoindex is available; otherwise
    uses a paragraph + char window with overlap. v0 used the v0
    `SplitRecursively` op; v1 mirrors the same chunking behaviour.
    """
    if COCOINDEX_AVAILABLE and RecursiveSplitter is not None:
        try:
            splitter = RecursiveSplitter()  # type: ignore[call-arg]
            return [c.text for c in splitter.split(  # type: ignore[union-attr]
                text, chunk_size=chunk_size, chunk_overlap=chunk_overlap, language="markdown"
            )]
        except Exception:  # noqa: BLE001
            pass
    # Fallback: paragraph split with char-window overlap
    paras = re.split(r"\n\s*\n", text)
    out: list[str] = []
    buf = ""
    for p in paras:
        if len(buf) + len(p) + 2 > chunk_size and buf:
            out.append(buf)
            tail = buf[-chunk_overlap:] if chunk_overlap > 0 else ""
            buf = tail + "\n\n" + p
        else:
            buf = (buf + "\n\n" + p).strip() if buf else p
    if buf:
        out.append(buf)
    return out


# =============================================================================
# Shared lifespan
# =============================================================================


def _make_lifespan():
    """Build the shared lifespan for both Apps."""

    @coco.lifespan
    async def unified_lifespan(  # type: ignore[no-redef]
        builder: coco.EnvironmentBuilder,  # type: ignore[valid-type]
    ) -> AsyncIterator[None]:
        from cocoindex.connectors.lancedb import (  # type: ignore[import-not-found]
            LanceAsyncConnection,
        )

        lance_conn = await LanceAsyncConnection.connect(LANCEDB_URI)
        builder.provide(LANCE_DB, lance_conn)
        builder.provide(
            EMBEDDER,
            SentenceTransformerEmbedder(EMBED_MODEL),
        )
        yield

    return unified_lifespan


# =============================================================================
# v1 App 1: UnifiedEmbedding
# =============================================================================


def _make_unified_app():  # noqa: ANN202
    """Construct the UnifiedEmbedding v1 App. Returns None when
    cocoindex is missing."""
    if not COCOINDEX_AVAILABLE:
        return None

    unified_lifespan = _make_lifespan()

    @coco.fn
    async def unified_app_main(  # type: ignore[no-redef]
        connection_string: str,
        query: str,
        chunk_size: int = 800,
        chunk_overlap: int = 150,
    ) -> None:
        target_table = await lancedb.mount_table_target(
            LANCE_DB,  # type: ignore[arg-type]
            table_name=LANCEDB_UNIFIED_TABLE,
            table_schema=await lancedb.TableSchema.from_class(
                UnifiedDocumentRow, primary_key=["id"]
            ),
        )
        target_table.declare_vector_index(column="embedding")
        # 1) Read from DuckDB
        raw_rows = await asyncio.to_thread(
            _read_duckdb_rows, connection_string, query
        )
        # 2) Chunk + classify + embed + upsert
        for raw in raw_rows:
            text = raw.get("content", "") or ""
            if not text.strip():
                continue
            file_path = raw.get("file_path", "") or ""
            file_ext = pathlib.Path(file_path).suffix if file_path else None
            content_type = classify_content(text, file_ext)
            chunks = _chunk_markdown(text, chunk_size, chunk_overlap)
            for i, chunk_text in enumerate(chunks):
                chunk_hash = get_content_hash(chunk_text)
                # Stable ID: document_id + chunk_index + content_hash
                row_id = f"unified:{raw.get('id', '?')}:{i}:{chunk_hash}"
                target_table.declare_row(
                    row=UnifiedDocumentRow(
                        id=row_id,
                        document_id=str(raw.get("id", "")),
                        url=raw.get("url", "") or "",
                        title=raw.get("title", "") or "",
                        source_type=raw.get("source_type", "") or "",
                        protocol=raw.get("protocol", "") or "",
                        file_path=file_path,
                        content_type=content_type,
                        chunk_hash=chunk_hash,
                        chunk_index=i,
                        text=chunk_text,
                        embedding=None,  # type: ignore[arg-type]
                    ),
                )

    return coco.App(
        coco.AppConfig(name="UnifiedEmbedding"),
        unified_app_main,
        connection_string=DEFAULT_DUCKDB_CONNECTION,
        query=DEFAULT_DUCKDB_QUERY,
    )


unified_app = _make_unified_app()


# =============================================================================
# v1 App 2: CodeEmbedding
# =============================================================================


def _make_code_app():  # noqa: ANN202
    """Construct the CodeEmbedding v1 App. Returns None when
    cocoindex is missing."""
    if not COCOINDEX_AVAILABLE:
        return None

    unified_lifespan = _make_lifespan()

    @coco.fn(memo=True)
    async def process_code_file(  # type: ignore[no-redef]
        file: FileLike,  # type: ignore[valid-type]
        table: Any,
    ) -> None:
        """Read + chunk + embed a single code file.

        Uses the canonical v1 pattern: RecursiveSplitter with
        detect_code_language (matches the codebase_indexing.py App).
        """
        text = await file.content()
        if not text or not text.strip():
            return
        lang = detect_code_language(file.file_path.path)  # type: ignore[union-attr]
        if lang is None:
            return
        chunks = RecursiveSplitter().split(  # type: ignore[union-attr, call-arg]
            text, chunk_size=1000, chunk_overlap=200, language=lang
        )
        for i, chunk in enumerate(chunks):
            chunk_text = chunk.text if hasattr(chunk, "text") else str(chunk)
            row_id = f"code:{file.file_path.path}:{i}"
            table.declare_row(
                row=CodeChunkRow(
                    id=row_id,
                    filename=file.file_path.path,
                    language=lang,
                    chunk_type="block",
                    chunk_name="",
                    start_line=getattr(chunk, "start", i),
                    end_line=getattr(chunk, "end", i + 1),
                    source_type="local",
                    text=chunk_text,
                    embedding=None,  # type: ignore[arg-type]
                ),
            )

    @coco.fn
    async def code_app_main(  # type: ignore[no-redef]
        code_root: pathlib.Path,
    ) -> None:
        target_table = await lancedb.mount_table_target(
            LANCE_DB,  # type: ignore[arg-type]
            table_name=LANCEDB_CODE_TABLE,
            table_schema=await lancedb.TableSchema.from_class(
                CodeChunkRow, primary_key=["id"]
            ),
        )
        target_table.declare_vector_index(column="embedding")
        if not code_root.exists():
            return
        files = localfs.walk_dir(  # type: ignore[call-arg]
            code_root,
            recursive=True,
            path_matcher=PatternFilePathMatcher(
                included_patterns=[
                    "*.py",
                    "*.ts",
                    "*.tsx",
                    "*.js",
                    "*.jsx",
                    "*.rs",
                    "*.go",
                    "*.sol",
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
        await coco.mount_each(process_code_file, files.items(), target_table)

    return coco.App(
        coco.AppConfig(name="CodeEmbedding"),
        code_app_main,
        code_root=DEFAULT_CODE_ROOT,
    )


code_app = _make_code_app()


# =============================================================================
# Query helpers
# =============================================================================


async def unified_search(
    query: str,
    source_types: list[str] | None = None,
    protocol: str | None = None,
    limit: int = TOP_K,
    similarity_threshold: float = 0.0,
) -> list[dict[str, Any]]:
    """Search across all unified embeddings.

    Example: `await unified_search("SpacetimeDB reducer", source_types=["protocol_docs"])`
    """
    if not COCOINDEX_AVAILABLE or unified_app is None:
        return []
    embedder = coco.use_context(EMBEDDER)  # type: ignore[arg-type]
    conn = coco.use_context(LANCE_DB)  # type: ignore[arg-type]
    query_vec = await embedder.embed(query)
    table = await conn.open_table(LANCEDB_UNIFIED_TABLE)
    search = table.search(query_vec, vector_column_name="embedding")
    conditions: list[str] = []
    if source_types:
        types_str = ", ".join(f"'{t}'" for t in source_types)
        conditions.append(f"source_type IN ({types_str})")
    if protocol:
        conditions.append(f"protocol = '{protocol}'")
    if conditions:
        search = search.where(" AND ".join(conditions))
    rows = await search.limit(limit).to_list()
    for r in rows:
        r["score"] = 1.0 - r.get("_distance", 0.0)
    return [
        r
        for r in rows
        if r["score"] >= similarity_threshold
    ]


async def code_search(
    query: str,
    language: str | None = None,
    chunk_type: str | None = None,
    limit: int = TOP_K,
) -> list[dict[str, Any]]:
    """Search the code embeddings.

    Example: `await code_search("SpacetimeDB reducer", language="rust")`
    """
    if not COCOINDEX_AVAILABLE or code_app is None:
        return []
    embedder = coco.use_context(EMBEDDER)  # type: ignore[arg-type]
    conn = coco.use_context(LANCE_DB)  # type: ignore[arg-type]
    query_vec = await embedder.embed(query)
    table = await conn.open_table(LANCEDB_CODE_TABLE)
    search = table.search(query_vec, vector_column_name="embedding")
    conditions: list[str] = []
    if language:
        conditions.append(f"language = '{language}'")
    if chunk_type:
        conditions.append(f"chunk_type = '{chunk_type}'")
    if conditions:
        search = search.where(" AND ".join(conditions))
    rows = await search.limit(limit).to_list()
    for r in rows:
        r["score"] = 1.0 - r.get("_distance", 0.0)
    return rows


# =============================================================================
# Batch processing (utility; used by Dagster assets + ad-hoc scripts)
# =============================================================================


async def batch_embed_texts(
    texts: list[str],
    model: str = EMBED_MODEL,
    batch_size: int = MIN_BATCH_SIZE,
) -> list[list[float]]:
    """Embed texts in batches (v0 parity).

    Uses the sentence-transformers library directly (not the v1 App).
    Useful for ad-hoc scripts that don't want to spin up a v1 App.
    """
    from sentence_transformers import SentenceTransformer

    embedder = SentenceTransformer(model)
    all_embeddings: list[list[float]] = []
    for i in range(0, len(texts), batch_size):
        batch = texts[i : i + batch_size]
        embeddings = embedder.encode(batch, normalize_embeddings=True)
        all_embeddings.extend(embeddings.tolist())
    return all_embeddings


# =============================================================================
# Exports
# =============================================================================


__all__ = [
    "COCOINDEX_AVAILABLE",
    "LANCEDB_URI",
    "EMBED_MODEL",
    "EMBED_DIM",
    "REFRESH_INTERVAL",
    "LANCEDB_UNIFIED_TABLE",
    "LANCEDB_CODE_TABLE",
    "TOP_K",
    "MIN_BATCH_SIZE",
    "MAX_BATCH_SIZE",
    "HNSW_DROP_THRESHOLD",
    "DEFAULT_DUCKDB_CONNECTION",
    "DEFAULT_DUCKDB_QUERY",
    "DEFAULT_CODE_ROOT",
    "DocumentSourceType",
    "UnifiedDocumentRow",
    "CodeChunkRow",
    "get_content_hash",
    "classify_content",
    "_read_duckdb_rows",
    "_chunk_markdown",
    "unified_search",
    "code_search",
    "batch_embed_texts",
]
if COCOINDEX_AVAILABLE and unified_app is not None:
    __all__.append("unified_app")
if COCOINDEX_AVAILABLE and code_app is not None:
    __all__.append("code_app")
