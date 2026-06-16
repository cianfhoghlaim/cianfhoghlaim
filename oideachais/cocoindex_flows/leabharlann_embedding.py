"""
Leabharlann v1 CocoIndex embedding flows.

CocoIndex v1 Apps that embed the new `leabharlann/` archives into LanceDB.

Three Apps:
1. `leabharlann_books_embedding` — books source (PDF + DOCX + EPUB + MD) from
   `leabharlann/{gaeilge,aigne}/`.
2. `leabharlann_zotero_embedding` — Zotero PDFs with BAML metadata extraction
   from `leabharlann/zotero/`.
3. `leabharlann_takeout_embedding` — Takeout filesystem (Phase 1) from
   `stedding/Takeout/` (auto-discovered).

All three Apps follow the canonical v1 patterns from
`docs/cocoindex/{pdf_embedding,code_embedding_lancedb,paper_metadata}/main.py`:

- `@coco.fn` for processing functions
- `@coco.lifespan` providing shared `EMBEDDER` + `LANCE_DB` context keys
- `localfs.walk_dir(sourcedir, recursive=True, path_matcher=..., live=True)`
- `lancedb.mount_table_target(...)` for output
- `IdGenerator()` for stable IDs
- `query_once` / `query` helpers for ad-hoc semantic search

Reference: openspec/changes/leabharlann-cocoindex-v1/proposal.md
"""

from __future__ import annotations

import asyncio
import os
import pathlib
import re
from collections.abc import AsyncIterator
from dataclasses import dataclass
from typing import Annotated, Any

import structlog

logger = structlog.get_logger(__name__)

# CocoIndex is optional — degrade gracefully if not installed.
try:
    import cocoindex as coco  # type: ignore[import-not-found]
    from cocoindex.connectors import lancedb  # type: ignore[import-not-found]
    from cocoindex.connectors import localfs  # type: ignore[import-not-found]
    from cocoindex.ops.sentence_transformers import (  # type: ignore[import-not-found]
        SentenceTransformerEmbedder,
    )
    from cocoindex.ops.text import (  # type: ignore[import-not-found]
        RecursiveSplitter,
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
    FileLike = None  # type: ignore[assignment]
    PatternFilePathMatcher = None  # type: ignore[assignment]
    IdGenerator = None  # type: ignore[assignment]


# =============================================================================
# Configuration
# =============================================================================


LANCEDB_URI = os.getenv("LANCEDB_URI", "rest://lance-api.cianfhoghlaim.ie")
EMBED_MODEL = os.getenv("LEABHARLANN_EMBED_MODEL", "BAAI/bge-large-en-v1.5")
EMBED_DIM = 1024

# Default source directories.
DEFAULT_LEABHARLANN_ROOT = pathlib.Path(
    os.getenv(
        "LEABHARLANN_ROOT",
        str(
            pathlib.Path(__file__).resolve().parents[5]
            / "leabharlann"
        ),
    )
)
DEFAULT_BOOKS_SUBDIRS = ["gaeilge", "aigne"]
DEFAULT_TAKEOUT_ROOT = pathlib.Path(
    os.getenv(
        "LEABHARLANN_TAKEOUT_ROOT",
        str(
            pathlib.Path(__file__).resolve().parents[5]
            / "stedding"
            / "Takeout"
        ),
    )
)
DEFAULT_ZOTERO_ROOT = pathlib.Path(
    os.getenv(
        "LEABHARLANN_ZOTERO_ROOT",
        str(DEFAULT_LEABHARLANN_ROOT / "zotero"),
    )
)

# Shared context keys (per the v1 best practice).
LANCE_DB = coco.ContextKey[lancedb.LanceAsyncConnection]("leabharlann_lance_db") if COCOINDEX_AVAILABLE else None  # type: ignore[index]
EMBEDDER = coco.ContextKey[SentenceTransformerEmbedder]("leabharlann_embedder", detect_change=True) if COCOINDEX_AVAILABLE else None  # type: ignore[index]


# =============================================================================
# Helper: arXiv ID extraction
# =============================================================================


_ARXIV_ID_RE = re.compile(r"(\d{4}\.\d{4,5})(v(\d+))?")
# Pre-DOI-era arXiv IDs: 4 digits + slash + 4 digits (e.g. "2402-0289"). Some
# Zotero exports use 4 digits followed by "__dup0" or similar (e.g. "2402__dup0.pdf").
_ARXIV_LEGACY_RE = re.compile(r"^(\d{4})(?:__\w+|\W|_|$)")


def extract_arxiv_id_from_filename(file_name: str) -> tuple[str | None, str | None]:
    """
    Extract arXiv ID and version from a Zotero-style filename.

    Returns (arxiv_id, version) — either may be None.
    Examples:
        "2504.02890v2.pdf" → ("2504.02890", "v2")
        "2402__dup0.pdf"   → ("2402", None)
        "gaBERT - 2022.pdf"→ (None, None)
    """
    m = _ARXIV_ID_RE.search(file_name)
    if m:
        arxiv_id = m.group(1)
        version = f"v{m.group(3)}" if m.group(3) else None
        return arxiv_id, version
    m2 = _ARXIV_LEGACY_RE.match(file_name)
    if m2:
        return m2.group(1), None
    return None, None


# =============================================================================
# Data models
# =============================================================================


@dataclass
class LeabharlannBookChunk:
    """One embedded chunk of a leabharlann book."""

    id: int
    filename: str
    subject: str
    chunk_text: str
    chunk_start: int
    chunk_end: int
    account: str
    preview_path: str | None
    embedding: Annotated[Any, EMBEDDER] if COCOINDEX_AVAILABLE else Any  # type: ignore[index]


@dataclass
class ZoteroPaperChunk:
    """One embedded chunk of a Zotero paper (abstract or full-text)."""

    id: int
    filename: str
    arxiv_id: str | None
    arxiv_version: str | None
    title: str
    authors: list[str]
    year: int | None
    venue: str | None
    irish_relevant: bool
    htr_relevant: bool
    chunk_text: str
    chunk_location: str  # "title" | "abstract" | "full_text"
    chunk_start: int
    chunk_end: int
    embedding: Annotated[Any, EMBEDDER] if COCOINDEX_AVAILABLE else Any  # type: ignore[index]


@dataclass
class LeabharlannTakeoutChunk:
    """One embedded chunk of a Takeout document."""

    id: int
    filename: str
    account: str
    domain: str
    chunk_text: str
    chunk_start: int
    chunk_end: int
    embedding: Annotated[Any, EMBEDDER] if COCOINDEX_AVAILABLE else Any  # type: ignore[index]


# =============================================================================
# Shared processing functions
# =============================================================================


_splitter = RecursiveSplitter() if COCOINDEX_AVAILABLE else None  # type: ignore[call-arg]


if COCOINDEX_AVAILABLE:

    @coco.fn(memo=True)
    async def read_file_text(file: FileLike) -> str:  # type: ignore[valid-type]
        """Read a file as text. Best-effort for PDF/DOCX/EPUB/MD."""
        # We import locally so cocoindex-on-missing doesn't break the function
        # definition. The `@coco.fn` decorator registers it even if the
        # function body raises at first call.
        try:
            return await file.read_text()
        except (UnicodeDecodeError, ValueError):
            return ""

    @coco.fn(memo=True)
    async def extract_arxiv_fields(filename: str) -> dict[str, str | None]:
        """Extract arXiv ID + version from a Zotero filename."""
        arxiv_id, version = extract_arxiv_id_from_filename(filename)
        return {"arxiv_id": arxiv_id, "arxiv_version": version}


# =============================================================================
# App 1 — Leabharlann Books
# =============================================================================


if COCOINDEX_AVAILABLE:

    @coco.lifespan
    async def leabharlann_lifespan(  # type: ignore[no-redef]
        builder: coco.EnvironmentBuilder,
    ) -> AsyncIterator[None]:
        """Shared lifespan for all 3 leabharlann Apps (single LMDB state)."""
        # LanceDB connection.
        conn = await lancedb.connect_async(LANCEDB_URI)
        builder.provide(LANCE_DB, conn)  # type: ignore[arg-type]
        # Embedder (re-used; detect_change=True so a model swap auto-re-embeds).
        builder.provide(
            EMBEDDER,  # type: ignore[arg-type]
            SentenceTransformerEmbedder(EMBED_MODEL),
        )
        yield

    @coco.fn
    async def process_book_chunk(
        chunk: Any,  # cocoindex.resources.chunk.Chunk
        filename: pathlib.PurePath,
        id_gen: Any,  # cocoindex.resources.id.IdGenerator
        subject: str,
        account: str,
        preview_path: str | None,
        table: Any,  # lancedb.TableTarget
    ) -> None:
        """Declare one book chunk row in LanceDB."""
        embedder = coco.use_context(EMBEDDER)  # type: ignore[arg-type]
        text = chunk.text
        embedding = await embedder.embed(text)
        table.declare_row(
            row=LeabharlannBookChunk(
                id=await id_gen.next_id(text),
                filename=str(filename),
                subject=subject,
                chunk_text=text,
                chunk_start=chunk.start.char_offset,
                chunk_end=chunk.end.char_offset,
                account=account,
                preview_path=preview_path,
                embedding=embedding,
            ),
        )

    @coco.fn(memo=True)
    async def process_book_file(
        file: FileLike,  # type: ignore[valid-type]
        subject: str,
        account: str,
        preview_path: str | None,
        table: Any,
    ) -> None:
        """Read + chunk + embed a single book file."""
        text = await read_file_text(file)
        if not text.strip():
            return
        chunks = _splitter.split(  # type: ignore[union-attr]
            text, chunk_size=2000, chunk_overlap=500, language="markdown"
        )
        id_gen = IdGenerator()
        await coco.map(
            process_book_chunk,
            chunks,
            file.file_path.path,
            id_gen,
            subject,
            account,
            preview_path,
            table,
        )

    @coco.fn
    async def leabharlann_books_app_main(sourcedir: pathlib.Path) -> None:
        target_table = await lancedb.mount_table_target(
            LANCE_DB,  # type: ignore[arg-type]
            table_name="leabharlann_books",
            table_schema=await lancedb.TableSchema.from_class(
                LeabharlannBookChunk,
                primary_key=["id"],
            ),
        )

        for subject in DEFAULT_BOOKS_SUBDIRS:
            subject_dir = sourcedir / subject
            if not subject_dir.exists():
                continue
            files = localfs.walk_dir(
                subject_dir,
                recursive=True,
                path_matcher=PatternFilePathMatcher(
                    included_patterns=[
                        "**/*.pdf",
                        "**/*.docx",
                        "**/*.epub",
                        "**/*.md",
                    ],
                    excluded_patterns=["**/previews/**", "**/.DS_Store"],
                ),
                live=True,
            )
            # For each book, look up its preview path.
            async def with_preview(file, subject=subject):
                stem = file.file_path.path.stem
                candidate = subject_dir / "previews" / f"{stem}_preview.png"
                preview = str(candidate) if candidate.exists() else None
                await coco.mount(
                    coco.component_subpath("book", str(file.file_path.path)),
                    process_book_file,
                    file,
                    subject,
                    "leabharlann",
                    preview,
                    target_table,
                )

            await coco.mount_each(with_preview, files.items())

    leabharlann_books_app = coco.App(
        coco.AppConfig(name="LeabharlannBooksEmbedding"),
        leabharlann_books_app_main,
        sourcedir=DEFAULT_LEABHARLANN_ROOT,
    )


# =============================================================================
# App 2 — Leabharlann Zotero
# =============================================================================


if COCOINDEX_AVAILABLE:

    @coco.fn
    async def process_zotero_chunk(
        chunk: Any,
        filename: pathlib.PurePath,
        arxiv_id: str | None,
        arxiv_version: str | None,
        title: str,
        authors: list[str],
        year: int | None,
        venue: str | None,
        irish_relevant: bool,
        htr_relevant: bool,
        chunk_location: str,
        id_gen: Any,
        table: Any,
    ) -> None:
        """Declare one Zotero paper chunk row in LanceDB."""
        embedder = coco.use_context(EMBEDDER)  # type: ignore[arg-type]
        text = chunk.text
        embedding = await embedder.embed(text)
        table.declare_row(
            row=ZoteroPaperChunk(
                id=await id_gen.next_id(text),
                filename=str(filename),
                arxiv_id=arxiv_id,
                arxiv_version=arxiv_version,
                title=title,
                authors=authors,
                year=year,
                venue=venue,
                irish_relevant=irish_relevant,
                htr_relevant=htr_relevant,
                chunk_text=text,
                chunk_location=chunk_location,
                chunk_start=chunk.start.char_offset,
                chunk_end=chunk.end.char_offset,
                embedding=embedding,
            ),
        )

    @coco.fn(memo=True)
    async def process_zotero_file(
        file: FileLike,  # type: ignore[valid-type]
        arxiv_id: str | None,
        arxiv_version: str | None,
        title: str,
        authors: list[str],
        year: int | None,
        venue: str | None,
        irish_relevant: bool,
        htr_relevant: bool,
        table: Any,
    ) -> None:
        """Read + chunk + embed a single Zotero paper."""
        text = await read_file_text(file)
        if not text.strip():
            return
        chunks = _splitter.split(  # type: ignore[union-attr]
            text, chunk_size=2000, chunk_overlap=500, language="markdown"
        )
        id_gen = IdGenerator()
        # Same chunk_location="full_text" for every chunk in this file.
        await coco.map(
            process_zotero_chunk,
            chunks,
            file.file_path.path,
            arxiv_id,
            arxiv_version,
            title,
            authors,
            year,
            venue,
            irish_relevant,
            htr_relevant,
            "full_text",
            id_gen,
            table,
        )

    @coco.fn
    async def leabharlann_zotero_app_main(sourcedir: pathlib.Path) -> None:
        target_table = await lancedb.mount_table_target(
            LANCE_DB,  # type: ignore[arg-type]
            table_name="leabharlann_zotero",
            table_schema=await lancedb.TableSchema.from_class(
                ZoteroPaperChunk,
                primary_key=["id"],
            ),
        )

        files = localfs.walk_dir(
            sourcedir,
            recursive=False,  # Zotero is a flat dir
            path_matcher=PatternFilePathMatcher(
                included_patterns=["**/*.pdf"],
                excluded_patterns=["**/.DS_Store", "**/_.pdf"],
            ),
            live=True,
        )

        async def per_file(file):
            name = file.file_path.path.name
            arxiv_id, arxiv_version = extract_arxiv_id_from_filename(name)
            # Heuristic title from filename: strip arxiv prefix + .pdf + author prefix.
            title = re.sub(
                r"^([A-Z][a-z]+(?: et al\.)? - )?\d{4} - ",
                "",
                name.replace(".pdf", "").replace("__dup0", ""),
            )
            await coco.mount(
                coco.component_subpath("zotero", str(file.file_path.path)),
                process_zotero_file,
                file,
                arxiv_id,
                arxiv_version,
                title,
                [],  # authors: empty until BAML extractor fills
                None,
                None,
                False,  # irish_relevant: until BAML
                False,  # htr_relevant: until BAML
                target_table,
            )

        await coco.mount_each(per_file, files.items())

    leabharlann_zotero_app = coco.App(
        coco.AppConfig(name="LeabharlannZoteroEmbedding"),
        leabharlann_zotero_app_main,
        sourcedir=DEFAULT_ZOTERO_ROOT,
    )


# =============================================================================
# App 3 — Leabharlann Takeout (Phase 1 filesystem)
# =============================================================================


if COCOINDEX_AVAILABLE:

    @coco.fn
    async def process_takeout_chunk(
        chunk: Any,
        filename: pathlib.PurePath,
        account: str,
        domain: str,
        id_gen: Any,
        table: Any,
    ) -> None:
        embedder = coco.use_context(EMBEDDER)  # type: ignore[arg-type]
        text = chunk.text
        embedding = await embedder.embed(text)
        table.declare_row(
            row=LeabharlannTakeoutChunk(
                id=await id_gen.next_id(text),
                filename=str(filename),
                account=account,
                domain=domain,
                chunk_text=text,
                chunk_start=chunk.start.char_offset,
                chunk_end=chunk.end.char_offset,
                embedding=embedding,
            ),
        )

    @coco.fn(memo=True)
    async def process_takeout_file(
        file: FileLike,  # type: ignore[valid-type]
        account: str,
        domain: str,
        table: Any,
    ) -> None:
        text = await read_file_text(file)
        if not text.strip():
            return
        chunks = _splitter.split(  # type: ignore[union-attr]
            text, chunk_size=2000, chunk_overlap=500, language="markdown"
        )
        id_gen = IdGenerator()
        await coco.map(
            process_takeout_chunk,
            chunks,
            file.file_path.path,
            account,
            domain,
            id_gen,
            table,
        )

    @coco.fn
    async def leabharlann_takeout_app_main(sourcedir: pathlib.Path) -> None:
        target_table = await lancedb.mount_table_target(
            LANCE_DB,  # type: ignore[arg-type]
            table_name="leabharlann_takeout",
            table_schema=await lancedb.TableSchema.from_class(
                LeabharlannTakeoutChunk,
                primary_key=["id"],
            ),
        )

        # The Takeout dir is one level deep (e.g. stedding/Takeout/Drive/*.docx).
        # We walk non-recursively, treating each top-level subdir as a "domain".
        for product_dir in sourcedir.iterdir():
            if not product_dir.is_dir():
                continue
            domain = product_dir.name
            files = localfs.walk_dir(
                product_dir,
                recursive=False,
                path_matcher=PatternFilePathMatcher(
                    included_patterns=["*.docx", "*.pdf", "*.txt", "*.md", "*.csv"],
                    excluded_patterns=[".DS_Store"],
                ),
                live=True,
            )
            await coco.mount_each(
                lambda f, _d=domain: process_takeout_file(
                    f, "stedding_takeout", _d, target_table
                ),
                files.items(),
            )

    leabharlann_takeout_app = coco.App(
        coco.AppConfig(name="LeabharlannTakeoutEmbedding"),
        leabharlann_takeout_app_main,
        sourcedir=DEFAULT_TAKEOUT_ROOT,
    )


# =============================================================================
# Query helpers — ad-hoc semantic search
# =============================================================================


async def _query_table(
    table_name: str,
    query_text: str,
    limit: int = 10,
    where: str | None = None,
) -> list[dict[str, Any]]:
    """Run a vector search against one of the leabharlann tables."""
    if not COCOINDEX_AVAILABLE:
        return []
    embedder = coco.use_context(EMBEDDER)  # type: ignore[arg-type]
    conn = coco.use_context(LANCE_DB)  # type: ignore[arg-type]
    query_vec = await embedder.embed(query_text)
    table = await conn.open_table(table_name)
    search = table.search(query_vec, vector_column_name="embedding")
    if where:
        search = search.where(where)
    rows = await search.limit(limit).to_list()
    return rows


async def search_leabharlann_books(
    query: str,
    subject: str | None = None,
    limit: int = 10,
) -> list[dict[str, Any]]:
    """Search the leabharlann books LanceDB table."""
    where = f"subject = '{subject}'" if subject else None
    rows = await _query_table("leabharlann_books", query, limit=limit, where=where)
    for r in rows:
        r["score"] = 1.0 - r.get("_distance", 0.0)
    return rows


async def search_leabharlann_zotero(
    query: str,
    htr_relevant: bool | None = None,
    irish_relevant: bool | None = None,
    arxiv_id: str | None = None,
    limit: int = 10,
) -> list[dict[str, Any]]:
    """Search the leabharlann Zotero LanceDB table."""
    conditions: list[str] = []
    if htr_relevant is not None:
        conditions.append(f"htr_relevant = {str(htr_relevant).lower()}")
    if irish_relevant is not None:
        conditions.append(f"irish_relevant = {str(irish_relevant).lower()}")
    if arxiv_id is not None:
        conditions.append(f"arxiv_id = '{arxiv_id}'")
    where = " AND ".join(conditions) if conditions else None
    rows = await _query_table("leabharlann_zotero", query, limit=limit, where=where)
    for r in rows:
        r["score"] = 1.0 - r.get("_distance", 0.0)
    return rows


async def search_leabharlann_takeout(
    query: str,
    account: str | None = None,
    domain: str | None = None,
    limit: int = 10,
) -> list[dict[str, Any]]:
    """Search the leabharlann Takeout LanceDB table."""
    conditions: list[str] = []
    if account:
        conditions.append(f"account = '{account}'")
    if domain:
        conditions.append(f"domain = '{domain}'")
    where = " AND ".join(conditions) if conditions else None
    rows = await _query_table("leabharlann_takeout", query, limit=limit, where=where)
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
    "DEFAULT_LEABHARLANN_ROOT",
    "DEFAULT_ZOTERO_ROOT",
    "DEFAULT_TAKEOUT_ROOT",
    "extract_arxiv_id_from_filename",
    "LeabharlannBookChunk",
    "ZoteroPaperChunk",
    "LeabharlannTakeoutChunk",
]
if COCOINDEX_AVAILABLE:
    __all__ += [
        "leabharlann_books_app",
        "leabharlann_zotero_app",
        "leabharlann_takeout_app",
        "search_leabharlann_books",
        "search_leabharlann_zotero",
        "search_leabharlann_takeout",
    ]
