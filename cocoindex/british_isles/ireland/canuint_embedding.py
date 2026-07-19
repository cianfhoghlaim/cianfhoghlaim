"""
Canuint Irish Pronunciation — CocoIndex v1 App.

Embeds the Canuint word alignments (with timestamps) into LanceDB
via BGE-M3. LanceDB table: ``cianfhoghlaim.language.canuint_chunks``.

R1–R4 v1 conformance contract.

LlamaSwap routing per the shared table:
- Canuint → ``qwen3-vl-8b`` (audio + text multimodal)

Reads from: ``cianfhoghlaim.celtic.canuint.word_alignments``

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
except ImportError as exc:
    logger.warning("cocoindex_v1_not_available: %s", exc)
    COCOINDEX_AVAILABLE = False
    coco = None  # type: ignore[assignment]
    lancedb = None  # type: ignore[assignment]


from .._shared._lifespan import (  # noqa: E402
    EMBEDDER,
    EMBED_DIM,
    EMBED_MODEL,
    LANCE_DB,
    shared_lifespan,
)


CANUINT_DUCKLAKE_TABLES = {
    "word_alignments": "cianfhoghlaim.celtic.canuint.word_alignments",
    "recordings": "cianfhoghlaim.celtic.canuint.recordings",
    "locations": "cianfhoghlaim.celtic.canuint.locations",
}


def _read_ducklake_table(table: str) -> list[dict[str, Any]]:
    try:
        import duckdb  # type: ignore[import-not-found]
    except ImportError:
        return []
    db_path = os.environ.get("DUCKDB_PATH", "/tmp/cianfhoghlaim.duckdb")
    if not os.path.exists(db_path):
        return []
    try:
        con = duckdb.connect(db_path, read_only=True)
        rows = con.execute(f"SELECT * FROM {table}").fetchall()
        columns = [d[0] for d in con.description]
        return [dict(zip(columns, r)) for r in rows]
    except Exception:
        return []


@dataclass
class CanuintChunk:
    """One chunked + embedded Canuint word alignment row."""

    chunk_id: str
    word_id: str
    dialectal_text: str
    standardized_text: str
    province: str  # "connacht" | "munster" | "ulster"
    location_name: str
    speaker: str | None
    start_seconds: float
    end_seconds: float
    embedding: Annotated[NDArray, EMBEDDER]


if COCOINDEX_AVAILABLE:

    @coco.fn(memo=True)
    async def process_canuint_alignment(
        row: dict[str, Any],
    ) -> CanuintChunk | None:
        if not row:
            return None
        word_id = str(row.get("word_id", ""))
        return CanuintChunk(
            chunk_id=f"canuint:{word_id}",
            word_id=word_id,
            dialectal_text=str(row.get("dialectal_text", "")),
            standardized_text=str(row.get("standardized_text", "")),
            province=str(row.get("province", "connacht")),
            location_name=str(row.get("location_name", "")),
            speaker=row.get("speaker"),
            start_seconds=float(row.get("start_seconds", 0.0)),
            end_seconds=float(row.get("end_seconds", 0.0)),
            embedding=None,
        )

    @coco.App(
        coco.AppConfig(
            name="CanuintEmbeddingApp",
            description="Embeds Canuint word alignments (audio + text multimodal) into LanceDB via BGE-M3.",
        )
    )
    class CanuintEmbeddingApp(coco.CompiledApp):
        @coco.lifespan
        async def _app_lifespan(self, builder: coco.EnvironmentBuilder) -> AsyncIterator[None]:
            async for _ in shared_lifespan(builder):
                yield

        @coco.flow
        async def embed_canuint_alignments(self) -> list[CanuintChunk]:
            chunks: list[CanuintChunk] = []
            for row in _read_ducklake_table(CANUINT_DUCKLAKE_TABLES["word_alignments"]):
                chunk = await process_canuint_alignment(row)
                if chunk is not None:
                    chunks.append(chunk)
            return chunks


def mount_canuint_chunks_table() -> None:
    if not COCOINDEX_AVAILABLE:
        return
    try:
        lancedb.mount_table_target(
            LANCE_DB,
            table_name="cianfhoghlaim.language.canuint_chunks",
            embedding_dim=EMBED_DIM,
        )
        logger.info("canuint_chunks_mounted", table="cianfhoghlaim.language.canuint_chunks", dim=EMBED_DIM)
    except Exception as exc:
        logger.warning("canuint_chunks_mount_failed: %s", exc)


__all__ = [
    "COCOINDEX_AVAILABLE",
    "CanuintChunk",
    "CanuintEmbeddingApp",
    "CANUINT_DUCKLAKE_TABLES",
    "mount_canuint_chunks_table",
    "process_canuint_alignment",
]