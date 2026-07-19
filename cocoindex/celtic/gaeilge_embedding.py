"""
Gaeilge v1 CocoIndex Embedding App (BIEP v1 canonical).

Embeds the NCCA Leaving Certificate Gaeilge (Irish-medium)
syllabuses, exam papers, and marking schemes into LanceDB.

Gaeilge is Irish-only — no English sibling per the BIEP v1 spec
requirement "gaeilge-only syllabuses (no English sibling)".

R1–R4 v1 conformance contract per `_lifespan.py`:
- R1 — `from .._shared._lifespan import shared_lifespan`
- R2 — Imports the canonical `LANCE_DB` + `EMBEDDER` from `_lifespan`
- R3 — `app = coco.App(coco.AppConfig(name=...))` at module scope
- R4 — `@coco.fn` decorator + `lancedb.mount_table_target(LANCE_DB, ...)`

Embedder: `BAAI/bge-m3` (multilingual 1024-dim, supports Irish).
LanceDB table: `cianfhoghlaim.lc.gaeilge.<level>_ga`.

Reference: openspec/changes/2026-07-06-british-isles-education-pipeline-v1/
"""

from __future__ import annotations

import os
import pathlib
from dataclasses import dataclass
from typing import Annotated

import structlog
from numpy.typing import NDArray

logger = structlog.get_logger(__name__)

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


from .._shared._lifespan import (  # noqa: E402
    EMBEDDER,
    LANCE_DB,
    shared_lifespan,
)


DEFAULT_GAEL_ROOT = pathlib.Path(
    os.getenv(
        "CIANFHOGHLAIM_GAEL_ROOT",
        str(
            pathlib.Path(__file__).resolve().parents[2]
            / "leaving_certificate"
            / "gaeilge"
        ),
    )
)

# Gaeilge is Irish-only — no `en` sibling. Always `ga`.
GAEILGE_LANGUAGE = "ga"


if COCOINDEX_AVAILABLE:

    @dataclass
    class GaelChunk:
        """One chunked + embedded paragraph from a Gaeilge PDF (Irish-only)."""

        chunk_id: str
        subject: str
        level: str
        language: str
        filename: str
        chunk_index: int
        text: str
        embedding: Annotated[NDArray, EMBEDDER]

    def _chunk_text(text: str, chunk_size: int = 512, overlap: int = 64) -> list[str]:
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
    async def process_gaeilge_pdf(
        file_path: pathlib.PurePath,
        text: str,
        level: str,
        target_table: lancedb.TableTarget[GaelChunk],  # type: ignore[type-var]
    ) -> None:
        embedder = await coco.use_context(EMBEDDER)  # type: ignore[arg-type]
        filename = file_path.name
        chunks = _chunk_text(text)
        for i, chunk in enumerate(chunks):
            vec = await embedder.embed(chunk)  # type: ignore[attr-defined]
            target_table.declare_row(
                row=GaelChunk(
                    chunk_id=f"{file_path}#{i}",
                    subject="gaeilge",
                    level=level,
                    language=GAEILGE_LANGUAGE,  # always `ga`
                    filename=filename,
                    chunk_index=i,
                    text=chunk,
                    embedding=vec,
                )
            )

    @coco.fn
    async def gaeilge_app_main(
        sourcedir: pathlib.Path,
        level: str,
    ) -> None:
        target_table = await lancedb.mount_table_target(
            LANCE_DB,  # type: ignore[arg-type]
            table_name=f"cianfhoghlaim.lc.gaeilge.{level}_{GAEILGE_LANGUAGE}",
            table_schema=await lancedb.TableSchema.from_class(
                GaelChunk, primary_key=["chunk_id"]
            ),
        )
        target_table.declare_vector_index(column="embedding")

        if not sourcedir.exists():
            logger.warning(
                "gaeilge_corpus_dir_not_found", path=str(sourcedir)
            )
            return

        files = localfs.walk_dir(  # type: ignore[attr-defined]
            sourcedir, recursive=True, path_matcher=None, live=True
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
            await process_gaeilge_pdf(file_path, text, level, target_table)

    app = coco.App(
        coco.AppConfig(name="GaeilgeEmbedding"),
        gaeilge_app_main,
        sourcedir=DEFAULT_GAEL_ROOT,
        level="hl",
    )


async def query_gaeilge(
    query: str,
    level: str = "hl",
    top_k: int = 5,
) -> list[dict]:
    """Semantic search over the Gaeilge LanceDB table (Irish-only)."""
    if not COCOINDEX_AVAILABLE:
        raise RuntimeError("cocoindex is not installed")

    from cianfhoghlaim.lancedb.search import semantic_search

    return await semantic_search(
        table=f"cianfhoghlaim.lc.gaeilge.{level}_{GAEILGE_LANGUAGE}",
        query=query,
        top_k=top_k,
    )
