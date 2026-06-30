"""
Applied Mathematics v1 CocoIndex Embedding App.

Embeds the NCCA Leaving Certificate Applied Mathematics (HL) quest
packs into LanceDB for semantic search. Same pattern as
`mathematics_embedding.py`.

LanceDB table: `oideachais.lc.applied_mathematics.hl_<language>`
"""
from __future__ import annotations

import asyncio
import os
import pathlib
from collections.abc import AsyncIterator
from typing import Any

import structlog

logger = structlog.get_logger(__name__)

try:
    import cocoindex as coco  # type: ignore[import-not-found]
    from cocoindex.connectors import lancedb  # type: ignore[import-not-found]
    from cocoindex.connectors import localfs  # type: ignore[import-not-found]
    from cocoindex.resources.id import IdGenerator  # type: ignore[import-not-found]

    COCOINDEX_AVAILABLE = True
except ImportError as e:
    logger.warning("cocoindex_v1_not_available: %s", e)
    COCOINDEX_AVAILABLE = False
    coco = None  # type: ignore[assignment]
    lancedb = None  # type: ignore[assignment]
    localfs = None  # type: ignore[assignment]
    IdGenerator = None  # type: ignore[assignment]


from ._lifespan import (  # noqa: E402
    EMBEDDER,
    EMBED_DIM,
    EMBED_MODEL,
    LANCEDB_URI,
    LANCE_DB,
    shared_lifespan,
)


DEFAULT_APPM_ROOT = pathlib.Path(
    os.getenv(
        "CIANFHOGHLAIM_APPM_ROOT",
        str(
            pathlib.Path(__file__).resolve().parents[2]
            / "leaving_certificate"
            / "applied_mathematics"
        ),
    )
)


if COCOINDEX_AVAILABLE:

    @coco.App(refresh_interval=300)
    async def applied_mathematics_embedding(
        level: str = "hl",
        language: str = "en",
    ) -> AsyncIterator[dict[str, Any]]:
        """APPM v1 CocoIndex embedding flow.

        Reads the DuckDB `applied_mathematics_<level>_<language>` dataset
        and embeds each quest item into the LanceDB table
        `oideachais.lc.applied_mathematics.<level>_<language>`.
        """
        appm_root = DEFAULT_APPM_ROOT / language
        if not appm_root.exists():
            logger.warning("appm_corpus_dir_not_found", path=str(appm_root))
            return

        file_records = localfs.walk_dir(
            appm_root, recursive=True, path_matcher=None, live=True
        )

        async for record in file_records:
            file_path = record["path"]
            file_name = pathlib.Path(file_path).name

            if not file_name.lower().endswith(".pdf"):
                continue

            try:
                import fitz

                doc = fitz.open(file_path)
                text = "\n".join(page.get_text() for page in doc)
                doc.close()
            except ImportError:
                logger.warning("pymupdf_not_available", file=file_name)
                continue

            chunks = _chunk_text(text, chunk_size=512, overlap=64)
            for i, chunk in enumerate(chunks):
                yield {
                    "id": IdGenerator(file_path + f"#{i}"),
                    "filename": file_name,
                    "chunk_index": i,
                    "text": chunk,
                    "level": level,
                    "language": language,
                    "subject": "applied_mathematics",
                    "embedding": EMBEDDER.encode(chunk),
                }


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


async def query_applied_mathematics(
    query: str,
    level: str = "hl",
    language: str = "en",
    top_k: int = 5,
) -> list[dict[str, Any]]:
    if not COCOINDEX_AVAILABLE:
        raise RuntimeError("cocoindex is not installed")

    from cianfhoghlaim.lancedb.search import semantic_search

    return await semantic_search(
        table=f"oideachais.lc.applied_mathematics.{level}_{language}",
        query=query,
        embed_model=EMBED_MODEL,
        top_k=top_k,
    )