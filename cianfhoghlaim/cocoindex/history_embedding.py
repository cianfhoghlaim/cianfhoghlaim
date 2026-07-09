"""History v1 CocoIndex Embedding App (BIEP v1 canonical).

Embeds the NCCA Leaving Certificate History syllabuses, exam papers,
and marking schemes into LanceDB for semantic search.

Follows the canonical v1 pattern (R1–R4 conformance contract):

- **R1** — `from ._lifespan import shared_lifespan` (delegates to the
  shared lifespan in `_lifespan.py`)
- **R2** — Imports the canonical `LANCE_DB` + `EMBEDDER` from `_lifespan`
- **R3** — `app = coco.App(coco.AppConfig(name=...))` at module scope
- **R4** — `@coco.fn` decorator + `lancedb.mount_table_target(LANCE_DB, ...)`
  + `target_table.declare_vector_index(column="embedding")`

Embedder: `BAAI/bge-m3` (multilingual 1024-dim) per the BIEP v1 spec.
LanceDB table: `oideachais.lc.history.<level>_<language>`.

Driven by Dagster assets in
`cianfhoghlaim/orchestration/defs/3_model_lifecycle/cocoindex_v1/history_embedding/`.

Reference: openspec/changes/2026-07-06-british-isles-education-pipeline-v1/
(the canonical Mathematics template) + openspec/changes/2026-07-09-cocoindex-v1-remaining-apps-v1/
(this file's migration to R1-R4 conformance).
"""

from __future__ import annotations

import os
import pathlib
from dataclasses import dataclass
from typing import Annotated

import structlog
from numpy.typing import NDArray

logger = structlog.get_logger(__name__)

# CocoIndex is optional — degrade gracefully if not installed.
try:
    import cocoindex as coco  # type: ignore[import-not-found]
    from cocoindex.connectors import lancedb  # type: ignore[import-not-found]
    from cocoindex.connectors import localfs  # type: ignore[import-not-found]

    COCOINDEX_AVAILABLE = True
except ImportError as e:
    logger.warning("cocoindex_v1_not_available: %s", e)
    COCOINDEX_AVAILABLE = False
    coco = None  # type: ignore[assignment]
    lancedb = None  # type: ignore[assignment]
    localfs = None  # type: ignore[assignment]


# The shared CocoIndex v1 lifespan (R1 — REFACTORING.md item 12)
from ._lifespan import (  # noqa: E402
    EMBEDDER,
    LANCE_DB,
    shared_lifespan,
)


# ============================================================================
# Configuration
# ============================================================================

DEFAULT_HIST_ROOT = pathlib.Path(
    os.getenv(
        "CIANFHOGHLAIM_HIST_ROOT",
        str(
            pathlib.Path(__file__).resolve().parents[2]
            / "leaving_certificate"
            / "history"
        ),
    )
)

# The 3 BIEP v1 levels + 2 languages = 6 LanceDB tables.
LC_LEVELS: tuple[str, ...] = ("hl", "ol", "fl")
LC_LANGUAGES: tuple[str, ...] = ("en", "ga")


# ============================================================================
# Row schema (the @dataclass that drives the LanceDB target table)
# ============================================================================

if COCOINDEX_AVAILABLE:

    @dataclass
    class HistoryChunk:
        """One chunked + embedded paragraph from a History PDF."""

        chunk_id: str
        subject: str
        level: str
        language: str
        filename: str
        chunk_index: int
        text: str
        embedding: Annotated[NDArray, EMBEDDER]


# ============================================================================
# v1 App: HistoryEmbedding
# ============================================================================

if COCOINDEX_AVAILABLE:

    def _chunk_text(text: str, chunk_size: int = 512, overlap: int = 64) -> list[str]:
        """Naive sliding-window chunker (overlap-friendly)."""
        chunks: list[str] = []
        if not text:
            return chunks
        step = chunk_size - overlap
        for i in range(0, len(text), step):
            chunk = text[i : i + chunk_size]
            if chunk.strip():
                chunks.append(chunk)
            if i + chunk_size >= len(text):
                break
        return chunks

    @coco.fn(memo=True)
    async def process_history_pdf(
        file_path: pathlib.PurePath,
        text: str,
        level: str,
        language: str,
        target_table: lancedb.TableTarget[HistoryChunk],  # type: ignore[type-var]
    ) -> None:
        """Process one History PDF into chunked + embedded LanceDB rows."""
        embedder = await coco.use_context(EMBEDDER)  # type: ignore[arg-type]
        filename = file_path.name
        chunks = _chunk_text(text)
        for i, chunk in enumerate(chunks):
            vec = await embedder.embed(chunk)  # type: ignore[attr-defined]
            target_table.declare_row(
                row=HistoryChunk(
                    chunk_id=f"{file_path}#{i}",
                    subject="history",
                    level=level,
                    language=language,
                    filename=filename,
                    chunk_index=i,
                    text=chunk,
                    embedding=vec,
                )
            )

    @coco.fn
    async def history_app_main(
        sourcedir: pathlib.Path,
        level: str,
        language: str,
    ) -> None:
        """History v1 CocoIndex App: walks the corpus + embeds each PDF."""
        target_table = await lancedb.mount_table_target(
            LANCE_DB,  # type: ignore[arg-type]
            table_name=f"oideachais.lc.history.{level}_{language}",
            table_schema=await lancedb.TableSchema.from_class(
                HistoryChunk, primary_key=["chunk_id"]
            ),
        )
        target_table.declare_vector_index(column="embedding")

        if not sourcedir.exists():
            logger.warning(
                "history_corpus_dir_not_found",
                path=str(sourcedir),
                level=level,
                language=language,
            )
            return

        files = localfs.walk_dir(  # type: ignore[attr-defined]
            sourcedir,
            recursive=True,
            path_matcher=None,
            live=True,
        )
        async for record in files.items():
            file_path = pathlib.PurePath(record["path"])
            if not str(file_path).lower().endswith(".pdf"):
                continue
            try:
                import fitz  # PyMuPDF

                doc = fitz.open(str(file_path))
                text = "\n".join(page.get_text() for page in doc)
                doc.close()
            except ImportError:
                logger.warning("pymupdf_not_available", file=str(file_path))
                continue
            await process_history_pdf(
                file_path, text, level, language, target_table
            )

    app = coco.App(
        coco.AppConfig(name="HistoryEmbedding"),
        history_app_main,
        sourcedir=DEFAULT_HIST_ROOT,
        level="hl",
        language="en",
    )


# ============================================================================
# Ad-hoc query helper (unchanged from pre-v4)
# ============================================================================


async def query_history(
    query: str,
    level: str = "hl",
    language: str = "en",
    top_k: int = 5,
) -> list[dict]:
    """Semantic search over the History LanceDB table."""
    if not COCOINDEX_AVAILABLE:
        raise RuntimeError("cocoindex is not installed")

    from cianfhoghlaim.lancedb.search import semantic_search

    return await semantic_search(
        table=f"oideachais.lc.history.{level}_{language}",
        query=query,
        top_k=top_k,
    )