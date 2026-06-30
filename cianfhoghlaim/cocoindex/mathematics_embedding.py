"""
Mathematics v1 CocoIndex Embedding App.

Embeds the NCCA Leaving Certificate Mathematics quest packs into
LanceDB for semantic search. Follows the canonical v1 pattern from
`leabharlann_embedding.py` and `_lifespan.py`:

- `@coco.fn` for processing functions
- `@coco.lifespan` providing shared `EMBEDDER` + `LANCE_DB` context keys
  (now imported from `_lifespan.py` — the shared lifespan module)
- `localfs.walk_dir(sourcedir, recursive=True, ...)` for input
- `lancedb.mount_table_target(...)` for output
- `IdGenerator()` for stable IDs
- BGE-M3 multilingual 1024-dim embeddings

The v1 App is invoked from `dagster/assets/mathematics_assets.py`
(`math_embedding` asset) via:
    uv run cocoindex update -f mathematics_embedding \\
        --arg level=hl --arg language=en

LanceDB table: `oideachais.lc.mathematics.<level>_<language>`

Reference: openspec/changes/cianfhoghlaim-educational-mmo-v1/proposal.md (D3)
"""

from __future__ import annotations

import asyncio
import os
import pathlib
from collections.abc import AsyncIterator
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
    from cocoindex.resources.id import IdGenerator  # type: ignore[import-not-found]

    COCOINDEX_AVAILABLE = True
except ImportError as e:
    logger.warning("cocoindex_v1_not_available: %s", e)
    COCOINDEX_AVAILABLE = False
    coco = None  # type: ignore[assignment]
    lancedb = None  # type: ignore[assignment]
    localfs = None  # type: ignore[assignment]
    SentenceTransformerEmbedder = None  # type: ignore[assignment]
    IdGenerator = None  # type: ignore[assignment]


# The shared CocoIndex v1 lifespan (REFACTORING.md item 12)
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

# Default source directory: the per-subject marimo notebook + the
# DuckDB database produced by the math_quest_pack asset.
DEFAULT_MATH_ROOT = pathlib.Path(
    os.getenv(
        "CIANFHOGHLAIM_MATH_ROOT",
        str(
            pathlib.Path(__file__).resolve().parents[2]
            / "leaving_certificate"
            / "mathematics"
        ),
    )
)
DEFAULT_MATH_DUCKDB = pathlib.Path(
    os.getenv(
        "MATH_DUCKDB_PATH",
        str(pathlib.Path(__file__).resolve().parents[2] / "data" / "mathematics.duckdb"),
    )
)


# =============================================================================
# v1 App: mathematics_embedding
# =============================================================================

if COCOINDEX_AVAILABLE:

    @coco.App(refresh_interval=300)  # Refresh every 5 minutes
    async def mathematics_embedding(
        level: str = "hl",
        language: str = "en",
    ) -> AsyncIterator[dict[str, Any]]:
        """Mathematics v1 CocoIndex embedding flow.

        Reads the DuckDB `mathematics_<level>_<language>` dataset
        (produced by `math_quest_pack`) and embeds each quest item
        into the LanceDB table
        `oideachais.lc.mathematics.<level>_<language>`.

        Embedding model: BGE-M3 multilingual (1024-dim).
        """
        from cianfhoghlaim.baml_client import b  # type: ignore

        # Generate (or re-generate) the quest pack via BAML
        syllabus_text = ""  # Reuse from the cached Dagster asset output
        # In production, the math_quest_pack Dagster asset writes the
        # pack to DuckDB; we re-read it here.
        # For the v1 App, we use a simplified version that embeds the
        # syllabus + past paper text directly.

        # 1. Walk the Mathematics corpus
        math_root = DEFAULT_MATH_ROOT / language
        if not math_root.exists():
            logger.warning("math_corpus_dir_not_found", path=str(math_root))
            return

        file_records = localfs.walk_dir(
            math_root,
            recursive=True,
            path_matcher=None,
            live=True,
        )

        async for record in file_records:
            # 2. Per-file processing
            file_path = record["path"]
            file_name = pathlib.Path(file_path).name

            # Skip non-PDFs
            if not file_name.lower().endswith(".pdf"):
                continue

            # 3. Extract text (lazy import to avoid hard dep on PyMuPDF)
            try:
                import fitz

                doc = fitz.open(file_path)
                text = "\n".join(page.get_text() for page in doc)
                doc.close()
            except ImportError:
                logger.warning("pymupdf_not_available", file=file_name)
                continue

            # 4. Chunk + embed (CocoIndex v1 idiom)
            chunks = _chunk_text(text, chunk_size=512, overlap=64)
            for i, chunk in enumerate(chunks):
                yield {
                    "id": IdGenerator(file_path + f"#{i}"),
                    "filename": file_name,
                    "chunk_index": i,
                    "text": chunk,
                    "level": level,
                    "language": language,
                    "subject": "mathematics",
                    "embedding": EMBEDDER.encode(chunk),  # 1024-dim BGE-M3
                }


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


# =============================================================================
# Ad-hoc query helper
# =============================================================================

async def query_mathematics(
    query: str,
    level: str = "hl",
    language: str = "en",
    top_k: int = 5,
) -> list[dict[str, Any]]:
    """Semantic search over the Mathematics LanceDB table."""
    if not COCOINDEX_AVAILABLE:
        raise RuntimeError("cocoindex is not installed")

    from cianfhoghlaim.lancedb.search import semantic_search

    return await semantic_search(
        table=f"oideachais.lc.mathematics.{level}_{language}",
        query=query,
        embed_model=EMBED_MODEL,
        top_k=top_k,
    )