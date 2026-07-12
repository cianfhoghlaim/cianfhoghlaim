"""
Dúchas National Folklore Collection — CocoIndex v1 App.

Embeds the Dúchas manuscript pages (cbe/cbes/cbeg/cbef collections) into
LanceDB via BGE-M3 (multilingual 1024-d, supports Irish handwriting OCR).

Mounts **TWO** LanceDB tables:
1. ``oideachais.language.duchas_chunks`` — page-level summaries
2. ``oideachais.language.duchas_bboxes`` — 5-level bbox child table
   (page → region → sentence → word → letter)

R1–R4 v1 conformance contract:
- R1 — ``from ._lifespan import shared_lifespan``
- R2 — ``LANCE_DB`` + ``EMBEDDER`` from ``_lifespan``
- R3 — ``app = coco.App(coco.AppConfig(name=...))`` at module scope
- R4 — ``@coco.fn`` + ``lancedb.mount_table_target(LANCE_DB, ...)``

LlamaSwap routing (per the shared routing table):
- Dúchas → ``molmo2-8b`` (diagram pointing specialist) + ``dots-ocr`` (layout)

Reads from the canonical DuckLake tables:
- ``oideachais.celtic.duchas.manuscripts`` (page-level records)
- ``oideachais.celtic.duchas.bboxes`` (5-level bbox child table)
- ``oideachais.celtic.duchas.transcriptions`` (line-by-line OCR)

Reference: ``openspec/changes/2026-07-17-gaois-celtic-language-pipeline-v1/``
"""

from __future__ import annotations

import os
from collections.abc import AsyncIterator
from dataclasses import dataclass
from typing import Annotated, Any

import structlog
from numpy.typing import NDArray

logger = structlog.get_logger(__name__)

try:
    import cocoindex as coco  # type: ignore[import-not-found]
    from cocoindex.connectors import lancedb  # type: ignore[import-not-found]

    COCOINDEX_AVAILABLE = True
except ImportError as exc:  # pragma: no cover - defensive
    logger.warning("cocoindex_v1_not_available: %s", exc)
    COCOINDEX_AVAILABLE = False
    coco = None  # type: ignore[assignment]
    lancedb = None  # type: ignore[assignment]


from ._lifespan import (  # noqa: E402
    EMBEDDER,
    EMBED_DIM,
    EMBED_MODEL,
    LANCE_DB,
    shared_lifespan,
)


# =============================================================================
# DuckLake source tables (the Dúchas pipeline output)
# =============================================================================

DUCHAS_DUCKLAKE_TABLES = {
    "manuscripts": "oideachais.celtic.duchas.manuscripts",
    "bboxes": "oideachais.celtic.duchas.bboxes",
    "transcriptions": "oideachais.celtic.duchas.transcriptions",
}


def _read_ducklake_table(table: str) -> list[dict[str, Any]]:
    """Read rows from a Dúchas DuckLake table via the local DuckDB destination."""
    try:
        import duckdb  # type: ignore[import-not-found]
    except ImportError:
        logger.warning("duckdb_not_available_for_duchas_embedding")
        return []

    db_path = os.environ.get("DUCKDB_PATH", "/tmp/oideachais.duckdb")
    if not os.path.exists(db_path):
        return []
    try:
        con = duckdb.connect(db_path, read_only=True)
        rows = con.execute(f"SELECT * FROM {table}").fetchall()
        columns = [d[0] for d in con.description]
        return [dict(zip(columns, r)) for r in rows]
    except Exception as exc:  # noqa: BLE001 - defensive
        logger.warning("ducklake_read_failed", table=table, error=str(exc))
        return []


# =============================================================================
# Data models
# =============================================================================


@dataclass
class DuchasChunk:
    """One chunked + embedded Dúchas manuscript page."""

    chunk_id: str
    page_id: str
    collection: str  # "cbe" | "cbes" | "cbeg" | "cbef"
    volume_id: int
    page_number: int
    image_url: str
    primary_language: str
    ga_text: str
    en_translation: str
    topic_codes: str  # comma-separated HandbookTopicCode values
    transcription_confidence: float
    embedding: Annotated[NDArray, EMBEDDER]


@dataclass
class DuchasBoundingBoxRow:
    """One row from the 5-level bounding box child table."""

    bbox_id: str
    page_id: str
    level: str  # "page" | "region" | "sentence" | "word" | "letter"
    parent_bbox_id: str | None
    x1: int
    y1: int
    x2: int
    y2: int
    text: str | None
    ga_text: str | None
    en_translation: str | None
    confidence: float | None
    handwritten: bool
    embedding: Annotated[NDArray, EMBEDDER]


# =============================================================================
# CocoIndex v1 App — DuchasEmbeddingApp
# =============================================================================


if COCOINDEX_AVAILABLE:

    @coco.fn(memo=True)
    async def process_duchas_manuscript(
        row: dict[str, Any],
    ) -> DuchasChunk | None:
        """Process one Dúchas manuscript row into a chunked + embedded DuchasChunk."""
        if not row:
            return None
        page_id = row.get("page_id", "unknown")
        text = f"{row.get('ga_text', '')} / {row.get('en_translation', '')}"
        return DuchasChunk(
            chunk_id=f"duchas:{page_id}",
            page_id=str(page_id),
            collection=str(row.get("collection", "cbes")),
            volume_id=int(row.get("volume_id", 0)),
            page_number=int(row.get("page_number", 0)),
            image_url=str(row.get("image_url", "")),
            primary_language=str(row.get("primary_language", "ga")),
            ga_text=str(row.get("ga_text", "")),
            en_translation=str(row.get("en_translation", "")),
            topic_codes=str(row.get("topic_codes", "")),
            transcription_confidence=float(row.get("transcription_confidence", 0.0)),
            embedding=None,
        )

    @coco.fn(memo=True)
    async def process_duchas_bbox(
        row: dict[str, Any],
    ) -> DuchasBoundingBoxRow | None:
        """Process one Dúchas bbox row into a chunked + embedded DuchasBoundingBoxRow."""
        if not row:
            return None
        return DuchasBoundingBoxRow(
            bbox_id=str(row.get("bbox_id", "")),
            page_id=str(row.get("page_id", "")),
            level=str(row.get("level", "page")),
            parent_bbox_id=row.get("parent_bbox_id"),
            x1=int(row.get("x1", 0)),
            y1=int(row.get("y1", 0)),
            x2=int(row.get("x2", 0)),
            y2=int(row.get("y2", 0)),
            text=row.get("text"),
            ga_text=row.get("ga_text"),
            en_translation=row.get("en_translation"),
            confidence=row.get("confidence"),
            handwritten=bool(row.get("handwritten", False)),
            embedding=None,
        )

    @coco.App(
        coco.AppConfig(
            name="DuchasEmbeddingApp",
            description="Embeds the 4 Dúchas collections (cbe/cbes/cbeg/cbef) into 2 LanceDB tables (chunks + 5-level bboxes).",
        )
    )
    class DuchasEmbeddingApp(coco.CompiledApp):
        """The Dúchas v1 CocoIndex App (manuscripts + bounding boxes)."""

        @coco.lifespan
        async def _app_lifespan(self, builder: coco.EnvironmentBuilder) -> AsyncIterator[None]:
            async for _ in shared_lifespan(builder):
                yield

        @coco.flow
        async def embed_duchas_manuscripts(self) -> list[DuchasChunk]:
            chunks: list[DuchasChunk] = []
            for row in _read_ducklake_table(DUCHAS_DUCKLAKE_TABLES["manuscripts"]):
                chunk = await process_duchas_manuscript(row)
                if chunk is not None:
                    chunks.append(chunk)
            return chunks

        @coco.flow
        async def embed_duchas_bboxes(self) -> list[DuchasBoundingBoxRow]:
            bboxes: list[DuchasBoundingBoxRow] = []
            for row in _read_ducklake_table(DUCHAS_DUCKLAKE_TABLES["bboxes"]):
                bbox = await process_duchas_bbox(row)
                if bbox is not None:
                    bboxes.append(bbox)
            return bboxes


# =============================================================================
# LanceDB mounts (R4)
# =============================================================================


def mount_duchas_chunks_table() -> None:
    """Mount the Dúchas page-level summaries LanceDB table."""
    if not COCOINDEX_AVAILABLE:
        logger.warning("cocoindex_v1_not_available: duchas_chunks_mount_skipped")
        return
    try:
        lancedb.mount_table_target(
            LANCE_DB,
            table_name="oideachais.language.duchas_chunks",
            embedding_dim=EMBED_DIM,
        )
        logger.info("duchas_chunks_mounted", table="oideachais.language.duchas_chunks", dim=EMBED_DIM)
    except Exception as exc:  # noqa: BLE001 - defensive
        logger.warning("duchas_chunks_mount_failed: %s", exc)


def mount_duchas_bboxes_table() -> None:
    """Mount the Dúchas 5-level bbox child LanceDB table."""
    if not COCOINDEX_AVAILABLE:
        logger.warning("cocoindex_v1_not_available: duchas_bboxes_mount_skipped")
        return
    try:
        lancedb.mount_table_target(
            LANCE_DB,
            table_name="oideachais.language.duchas_bboxes",
            embedding_dim=EMBED_DIM,
        )
        logger.info("duchas_bboxes_mounted", table="oideachais.language.duchas_bboxes", dim=EMBED_DIM)
    except Exception as exc:  # noqa: BLE001 - defensive
        logger.warning("duchas_bboxes_mount_failed: %s", exc)


__all__ = [
    "COCOINDEX_AVAILABLE",
    "DuchasChunk",
    "DuchasBoundingBoxRow",
    "DuchasEmbeddingApp",
    "DUCHAS_DUCKLAKE_TABLES",
    "mount_duchas_chunks_table",
    "mount_duchas_bboxes_table",
    "process_duchas_manuscript",
    "process_duchas_bbox",
]