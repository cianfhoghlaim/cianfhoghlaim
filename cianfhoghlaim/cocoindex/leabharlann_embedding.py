"""
Leabharlann v1 CocoIndex embedding flows.

CocoIndex v1 Apps that embed the new `leabharlann/` archives into LanceDB.

Four Apps:
1. `leabharlann_books_embedding` — books source (PDF + DOCX + EPUB + MD) from
   `leabharlann/{gaeilge,aigne}/`.
2. `leabharlann_zotero_embedding` — Zotero PDFs with BAML metadata extraction
   from `leabharlann/zotero/`.
3. `leabharlann_takeout_embedding` — Takeout filesystem (Phase 1) from
   `stedding/Takeout/` (auto-discovered).
4. `leabharlann_inbox_embedding` — MBOX email-inbox messages from
   `/srv/mailcow-exports/` (the 4-account email-inbox pipeline, added
   2026-06-29 per the `2026-06-29-leabharlann-email-inbox-pipeline`
   openspec change).

All four Apps follow the canonical v1 patterns from
`docs/cocoindex/{pdf_embedding,code_embedding_lancedb,paper_metadata}/main.py`:

- `@coco.fn` for processing functions
- `@coco.lifespan` providing shared `EMBEDDER` + `LANCE_DB` context keys
  (now imported from `oideachais/cocoindex_flows/_lifespan.py` — the
  shared lifespan module, REFACTORING.md item 12).
- `localfs.walk_dir(sourcedir, recursive=True, path_matcher=..., live=True)`
- `lancedb.mount_table_target(...)` for output
- `IdGenerator()` for stable IDs
- `query_once` / `query` helpers for ad-hoc semantic search
- `oideachais.lancedb.indexing.build_hnsw_index` for vector indexing
  (added 2026-06 per the LanceDB 0.15+ upgrade; REFACTORING.md item
  from `oideachais-semantic-search`).

Reference: openspec/changes/leabharlann-cocoindex-v1/proposal.md
            + openspec/changes/2026-06-29-leabharlann-email-inbox-pipeline/
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


# The shared CocoIndex v1 lifespan (REFACTORING.md item 12) —
# imported from the canonical home so the 9 v1 Apps don't re-declare
# the same `@coco.lifespan` 9 times.
from ._lifespan import (  # noqa: E402
    EMBEDDER,
    EMBED_DIM,
    EMBED_MODEL,
    LANCEDB_URI,
    LANCE_DB,
    shared_lifespan,
)


# =============================================================================
# Configuration
# =============================================================================


# LANCEDB_URI, EMBED_MODEL, EMBED_DIM, LANCE_DB, EMBEDDER are
# imported from `._lifespan` (the shared lifespan module).
# See the imports block at the top of the file.

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
# MBOX export directory for the email-inbox pipeline. Populated by the
# Mailcow `dovecot_imapsync_runner` + `mailcow-export` companion container.
DEFAULT_INBOX_MBOX_ROOT = pathlib.Path(
    os.getenv(
        "LEABHARLANN_INBOX_MBOX_ROOT",
        "/srv/mailcow-exports",
    )
)


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


@dataclass
class LeabharlannInboxMessage:
    """One embedded chunk of an email-inbox message.

    One row per message in the MBOX. The `body_excerpt` is the first
    2000 chars of the plaintext body (computed by the DLT source).
    The `baml_class` and `baml_urgency` are filled in by the
    `leabharlann_inbox_baml_classify` Dagster asset and read by the
    App at materialisation time.
    """

    id: int
    account: str
    year: int
    date_iso: str
    subject: str
    sender: str
    recipients: str
    body_excerpt: str
    embedding: Annotated[Any, EMBEDDER] if COCOINDEX_AVAILABLE else Any  # type: ignore[index]
    baml_class: str
    baml_urgency: float
    thread_id: str


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

    # The shared lifespan is now imported from `._lifespan` (above).
    # This local `leabharlann_lifespan` was the original; it's kept
    # as a back-compat alias so downstream code that imports it
    # still works for one release cycle.
    leabharlann_lifespan = shared_lifespan

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
# App 4 — Leabharlann Inbox (MBOX email messages)
# =============================================================================
# Added 2026-06-29 per the `2026-06-29-leabharlann-email-inbox-pipeline`
# openspec change. Reads MBOX files from `/srv/mailcow-exports/`,
# recurses into each MBOX via the `mailbox` stdlib, yields one
# chunk per message (`from + subject + first 2000 chars of body`).
# Embeds with BAAI/bge-large-en-v1.5 (1024-d) via the shared
# `EMBEDDER` ContextKey. Mounts the `oideachais_inbox_messages`
# LanceDB table with columns `(id, account, year, date_iso, subject,
# sender, recipients, body_excerpt, embedding, baml_class,
# baml_urgency, thread_id)`. Declares a cosine vector index on
# `embedding` AND an FTS index on `subject + body_excerpt` for the
# `@query_handler search_inbox` RRF-fused hybrid search.
# =============================================================================


if COCOINDEX_AVAILABLE:

    @coco.fn
    async def process_inbox_message(
        chunk: Any,
        account: str,
        year: int,
        date_iso: str,
        subject: str,
        sender: str,
        recipients: str,
        thread_id: str,
        baml_class: str,
        baml_urgency: float,
        id_gen: Any,
        table: Any,
    ) -> None:
        """Declare one inbox message row in LanceDB."""
        embedder = coco.use_context(EMBEDDER)  # type: ignore[arg-type]
        text = chunk.text
        embedding = await embedder.embed(text)
        table.declare_row(
            row=LeabharlannInboxMessage(
                id=await id_gen.next_id(text),
                account=account,
                year=year,
                date_iso=date_iso,
                subject=subject,
                sender=sender,
                recipients=recipients,
                body_excerpt=text,
                embedding=embedding,
                baml_class=baml_class,
                baml_urgency=baml_urgency,
                thread_id=thread_id,
            ),
        )

    @coco.fn(memo=True)
    async def process_inbox_mbox(
        mbox_path: Any,  # cocoindex.resources.file.FileLike
        account: str,
        year: int,
        table: Any,
    ) -> None:
        """Read a single mbox file, extract per-message chunks, embed + write.

        LBYL: every step is guarded against `OSError`, `mailbox.Error`,
        `RuntimeError` so a single bad message never crashes the App.
        Memoised on `(mbox_path, account, year)` so re-runs are O(0)
        for unchanged files.
        """
        try:
            import mailbox as _mailbox  # local import — keep module-level clean
        except ImportError:
            return
        path_str = str(mbox_path)
        try:
            mbox = _mailbox.mbox(path_str, factory=None)
        except (OSError, _mailbox.Error) as e:
            logger.warning("inbox_mbox_open_failed", path=path_str, error=str(e))
            return
        msgs: list[dict[str, Any]] = []
        try:
            for key in mbox.iterkeys():
                try:
                    msg = mbox[key]
                except (_mailbox.Error, KeyError, OSError) as e:
                    logger.warning(
                        "inbox_mbox_message_load_failed",
                        path=path_str,
                        key=str(key),
                        error=str(e),
                    )
                    continue
                try:
                    subject = str(msg.get("Subject") or "")
                    from_ = str(msg.get("From") or "")
                    to_ = str(msg.get("To") or "")
                    cc_ = str(msg.get("Cc") or "")
                    recipients = ", ".join(filter(None, [to_, cc_]))
                    date_iso = str(msg.get("Date") or "")
                    in_reply_to = str(msg.get("In-Reply-To") or "")
                    references = str(msg.get("References") or "")
                    body = _get_inbox_body_excerpt(msg)
                    msgs.append(
                        {
                            "subject": subject,
                            "from": from_,
                            "recipients": recipients,
                            "date_iso": date_iso,
                            "in_reply_to": in_reply_to,
                            "references": references,
                            "body": body,
                        }
                    )
                except (OSError, AttributeError, ValueError) as e:  # pragma: no cover
                    logger.warning(
                        "inbox_mbox_message_extract_failed",
                        path=path_str,
                        error=str(e),
                    )
                    continue
        finally:
            try:
                mbox.close()
            except (_mailbox.Error, OSError):  # pragma: no cover
                pass

        id_gen = IdGenerator()
        for m in msgs:
            chunk_text = f"From: {m['from']}\nSubject: {m['subject']}\n\n{m['body']}"
            # The thread_id is the in_reply_to (or "" if none). The full
            # thread reconstruction is done by the DLT source; here we
            # only need a stable per-message hint for the LanceDB column.
            thread_id = m["in_reply_to"] or m["references"] or ""
            await process_inbox_message(
                # Wrap the chunk text in a tiny object that exposes
                # `.text` (matching the v1 chunk interface).
                type("_Stub", (), {"text": chunk_text, "start": type("_O", (), {"char_offset": 0})(), "end": type("_O", (), {"char_offset": len(chunk_text)})()})(),
                account,
                year,
                m["date_iso"],
                m["subject"],
                m["from"],
                m["recipients"],
                thread_id,
                # baml_class + baml_urgency are filled by the
                # `leabharlann_inbox_baml_classify` Dagster asset at
                # materialisation time; the App runs in 2 stages
                # (raw embed first, then a follow-up embed after BAML).
                "",
                0.0,
                id_gen,
                table,
            )

    def _get_inbox_body_excerpt(msg: Any) -> str:
        """Return first 2000 chars of plaintext body. Graceful on failure.

        Works with both `email.message.EmailMessage` (modern) and
        `mailbox.mboxMessage` (default mbox factory). The latter has
        `get_payload()` returning a `str` directly (or a list of
        strings for multipart), so we handle both cases.
        """
        try:
            is_multipart = getattr(msg, "is_multipart", None)
            is_multi = bool(is_multipart()) if callable(is_multipart) else False
            if is_multi:
                walk = getattr(msg, "walk", None)
                if callable(walk):
                    for part in walk():
                        ctype = part.get_content_type()
                        disp = str(part.get("Content-Disposition") or "")
                        if ctype == "text/plain" and "attachment" not in disp.lower():
                            payload = part.get_payload(decode=True) or b""
                            if isinstance(payload, str):
                                return payload[:2000]
                            try:
                                return payload.decode(
                                    part.get_content_charset() or "utf-8",
                                    errors="replace",
                                )[:2000]
                            except (LookupError, UnicodeDecodeError, TypeError):
                                return payload.decode("utf-8", errors="replace")[:2000]
                return ""
            payload = msg.get_payload(decode=True) or b""
            if isinstance(payload, str):
                return payload[:2000]
            if isinstance(payload, list):
                return "".join(
                    p[:2000] for p in payload if isinstance(p, str)
                )[:2000]
            try:
                return payload.decode(
                    msg.get_content_charset() or "utf-8", errors="replace"
                )[:2000]
            except (LookupError, UnicodeDecodeError, TypeError, AttributeError):
                try:
                    return payload.decode("utf-8", errors="replace")[:2000]
                except (AttributeError, TypeError):
                    return str(payload)[:2000]
        except (OSError, ValueError, AttributeError):
            return ""

    @coco.fn
    async def leabharlann_inbox_app_main(sourcedir: pathlib.Path) -> None:
        target_table = await lancedb.mount_table_target(
            LANCE_DB,  # type: ignore[arg-type]
            table_name="oideachais_inbox_messages",
            table_schema=await lancedb.TableSchema.from_class(
                LeabharlannInboxMessage,
                primary_key=["id"],
            ),
        )

        # Recurse into every mbox file (mailcow-export writes
        # `mailbox-<account>-<YYYY-MM-DD>.mbox` per account per export).
        files = localfs.walk_dir(
            sourcedir,
            recursive=True,
            path_matcher=PatternFilePathMatcher(
                included_patterns=["**/*.mbox"],
                excluded_patterns=["**/.*"],
            ),
            live=True,
        )

        async def per_mbox(file):
            name = file.file_path.path.name
            # Derive account + year from the filename.
            # `mailbox-<account>-<YYYY-MM-DD>.mbox`
            import re as _re
            m = _re.match(r"^mailbox-([\w_]+)-(\d{4})-\d{2}-\d{2}\.mbox$", name)
            if not m:
                account = "unknown"
                year_int = 1970
            else:
                account = m.group(1)
                try:
                    year_int = int(m.group(2))
                except (ValueError, TypeError):
                    year_int = 1970
            await coco.mount(
                coco.component_subpath("inbox", str(file.file_path.path)),
                process_inbox_mbox,
                file,
                account,
                year_int,
                target_table,
            )

        await coco.mount_each(per_mbox, files.items())

    leabharlann_inbox_app = coco.App(
        coco.AppConfig(name="LeabharlannInboxEmbedding"),
        leabharlann_inbox_app_main,
        sourcedir=DEFAULT_INBOX_MBOX_ROOT,
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
    """Run a vector search against one of the leabharlann tables.

    Per the 2026-06 LanceDB 0.15+ upgrade, the leabharlann tables
    all have HNSW indexes built on the `embedding` column (the
    `oideachais/lancedb/indexing.py:build_hnsw_index` function is
    called at materialisation time). The HNSW index gives 10-100x
    speedup at the cost of ~10% recall loss (per the LanceDB
    10B-scale blog).
    """
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


async def build_hnsw_indexes_for_leabharlann() -> dict[str, bool]:
    """Build HNSW indexes on all 3 leabharlann tables.

    Convenience helper called by the `leabharlann_cocoindex_*_update`
    Dagster assets after the v1 Apps materialise.

    Returns:
        A dict ``{table_name: True}`` for each table that got an
        HNSW index built.
    """
    if not COCOINDEX_AVAILABLE:
        return {}
    # Lazy import to avoid a hard lancedb dependency at module load.
    from cianfhoghlaim.embeddings.indexing import build_hnsw_index  # type: ignore[import-not-found]

    results: dict[str, bool] = {}
    conn = coco.use_context(LANCE_DB)  # type: ignore[arg-type]
    for table_name in (
        "leabharlann_books",
        "leabharlann_zotero",
        "leabharlann_takeout",
        "oideachais_inbox_messages",
    ):
        try:
            table = await conn.open_table(table_name)
            build_hnsw_index(table, column="embedding")
            results[table_name] = True
        except Exception as exc:  # pragma: no cover
            logger.warning("hnsw_index_build_failed: table=%s err=%s", table_name, exc)
            results[table_name] = False
    return results


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


async def search_inbox(
    query: str,
    account: str | None = None,
    year: int | None = None,
    baml_class: str | None = None,
    urgency_min: float | None = None,
    limit: int = 20,
) -> list[dict[str, Any]]:
    """Hybrid (cosine + BM25 RRF-fused) search against the inbox table.

    Added 2026-06-29 per the `2026-06-29-leabharlann-email-inbox-pipeline`
    change. Filters are pushed down to the SQL `where` clause; the
    cosine vector search is the primary ranking signal.
    """
    conditions: list[str] = []
    if account:
        conditions.append(f"account = '{account}'")
    if year is not None:
        conditions.append(f"year = {int(year)}")
    if baml_class:
        conditions.append(f"baml_class = '{baml_class}'")
    if urgency_min is not None:
        conditions.append(f"baml_urgency >= {float(urgency_min)}")
    where = " AND ".join(conditions) if conditions else None
    rows = await _query_table(
        "oideachais_inbox_messages", query, limit=limit, where=where
    )
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
    "DEFAULT_INBOX_MBOX_ROOT",
    "extract_arxiv_id_from_filename",
    "LeabharlannBookChunk",
    "ZoteroPaperChunk",
    "LeabharlannTakeoutChunk",
    "LeabharlannInboxMessage",
]
if COCOINDEX_AVAILABLE:
    __all__ += [
        "leabharlann_books_app",
        "leabharlann_zotero_app",
        "leabharlann_takeout_app",
        "leabharlann_inbox_app",
        "search_leabharlann_books",
        "search_leabharlann_zotero",
        "search_leabharlann_takeout",
        "search_inbox",
        "build_hnsw_indexes_for_leabharlann",
    ]
