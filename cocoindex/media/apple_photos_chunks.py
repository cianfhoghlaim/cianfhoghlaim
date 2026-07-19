"""
Apple Photos OCR Chunks CocoIndex v1 App — the canonical OCR text
discovery surface for Apple Photos.

Indexes the OCR'd text chunks from document scans + license plate
reads (populated by the `apple_photos_document_scan_route` and
`apple_photos_vehicle_route` Dagster assets) into a new
`apple_photos_chunks` LanceDB table. Embedded with BAAI/bge-m3
1024-dim.

Each row corresponds to one OCR chunk from one photo. The OCR
engine is `paddleocr` (for license plates), `dots-ocr` (for
VLM classification), or `docling-serve` (for full document
OCR).

This is one of the 4 v1 Apps added in the
`2026-06-30-agent-platform-cluster-hermes-cocoindex` change. Brings
the v1 App count from 13 → 17.

Source: the `apple_photos_ocr_chunks` DuckLake table (populated by
the 2 routing Dagster assets). IdGenerator() for stable IDs
across re-runs.
"""
from __future__ import annotations

import datetime
from collections.abc import AsyncIterator
from dataclasses import dataclass
from typing import Annotated

import structlog

from .._shared._lifespan import (
    COCOINDEX_AVAILABLE,
    EMBED_DIM,
    EMBED_MODEL,
    LANCEDB_URI,
    shared_lifespan,
)

logger = structlog.get_logger(__name__)

# CocoIndex is optional — degrade gracefully if not installed.
try:
    import cocoindex as coco  # type: ignore[import-not-found]
    from cocoindex.connectors import lancedb  # type: ignore[import-not-found]
    from cocoindex.resources.id import IdGenerator  # type: ignore[import-not-found]

    if COCOINDEX_AVAILABLE:
        from .._shared._lifespan import LANCE_DB  # type: ignore[assignment]
    else:
        LANCE_DB = None  # type: ignore[assignment]
except ImportError as e:
    logger.warning("apple_photos_chunks_v1_not_available: %s", e)
    COCOINDEX_AVAILABLE = False
    coco = None  # type: ignore[assignment]
    lancedb = None  # type: ignore[assignment]
    IdGenerator = None  # type: ignore[assignment]
    LANCE_DB = None  # type: ignore[assignment]


# =============================================================================
# Configuration
# =============================================================================


LANCEDB_TABLE = "apple_photos_chunks"
REFRESH_INTERVAL_SECS = 3600  # 1 hour


# =============================================================================
# Data model
# =============================================================================


@dataclass
class ApplePhotoChunkRecord:
    """One row per OCR chunk from one photo."""

    id: str
    photo_id: str  # FK to apple_photos_metadata
    chunk_index: int
    text: str
    ocr_engine: str  # "paddleocr" | "dots-ocr" | "docling-serve"
    confidence: float  # 0-1
    embedding: Annotated[list[float], "BAAI/bge-m3"]


# =============================================================================
# CocoIndex v1 App
# =============================================================================


if COCOINDEX_AVAILABLE:

    @coco.App(shared_lifespan)  # type: ignore[misc]
    def apple_photos_chunks_app(
        builder: coco.AppBuilder,  # type: ignore[valid-type]
    ) -> None:
        """Index the apple_photos_ocr_chunks DuckLake table into apple_photos_chunks."""
        builder.set_source(  # type: ignore[attr-defined]
            "chunks",
            coco.duckdb_source(  # type: ignore[attr-defined]
                table_name="apple_photos_ocr_chunks",
                database="lakehouse",
            ),
        )

        id_gen = IdGenerator()  # type: ignore[call-arg]

        @coco.function(  # type: ignore[misc]
            executor=coco.FunctionExecutor(parallelism=8),  # type: ignore[attr-defined]
        )
        async def index_chunk(row: dict) -> ApplePhotoChunkRecord:  # type: ignore[no-untyped-def,unused-ignore]
            return ApplePhotoChunkRecord(
                id=await id_gen.next_id(  # type: ignore[union-attr]
                    f"{row['photo_id']}::{row['chunk_index']}::{row['text'][:50]}"
                ),
                photo_id=row["photo_id"],
                chunk_index=int(row.get("chunk_index", 0)),
                text=row.get("text", ""),
                ocr_engine=row.get("ocr_engine", "docling-serve"),
                confidence=float(row.get("confidence", 0.0)),
                embedding=[],
            )

        _chunks_target = lancedb.mount_table_target(  # type: ignore[union-attr]
            LANCE_DB,  # type: ignore[arg-type]
            table_name=LANCEDB_TABLE,
            table_schema=ApplePhotoChunkRecord,
            primary_key="id",
        )
        _chunks_target.declare_vector_index(column="embedding")

        @coco.index(  # type: ignore[misc]
            target=_chunks_target,
            refresh_interval=datetime.timedelta(seconds=REFRESH_INTERVAL_SECS),
        )
        async def write_chunks(  # type: ignore[no-untyped-def,unused-ignore]
            records: AsyncIterator[ApplePhotoChunkRecord],
        ) -> AsyncIterator[ApplePhotoChunkRecord]:
            async for record in records:
                record.embedding = await _embed(record.text)  # type: ignore[attr-defined]
                yield record

    async def _embed(text: str) -> list[float]:  # type: ignore[no-untyped-def]
        from .._shared._lifespan import EMBEDDER  # type: ignore[assignment]

        return await EMBEDDER.embed(text)  # type: ignore[union-attr]
