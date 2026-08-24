"""
Heritage + Hidden Heritages — CocoIndex v1 App.

Embeds the heritage sites + hidden heritages records into LanceDB via
BGE-M3 (multilingual 1024-d, supports Irish place names).

LanceDB table: ``cianfhoghlaim.language.heritage_chunks``.

R1–R4 v1 conformance contract.

LlamaSwap routing per the shared routing table:
- Heritage → ``gemma-4-26B-A4B`` (multilingual MoE)

Reads from the canonical DuckLake tables:
- ``cianfhoghlaim.celtic.heritage.sites``
- ``cianfhoghlaim.celtic.heritage.hidden_sites``

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


from .._shared._lifespan import (  # noqa: E402
    EMBEDDER,
    EMBED_DIM,
    EMBED_MODEL,
    LANCE_DB,
    shared_lifespan,
)


HERITAGE_DUCKLAKE_TABLES = {
    "sites": "cianfhoghlaim.celtic.heritage.sites",
    "hidden_sites": "cianfhoghlaim.celtic.heritage.hidden_sites",
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
class HeritageChunk:
    """One chunked + embedded heritage site record."""

    chunk_id: str
    site_id: str
    site_name: str
    site_name_ga: str
    site_type: str  # "monument" | "castle" | "ringfort" | "church" | "hidden"
    county: str
    latitude: float
    longitude: float
    description: str
    embedding: Annotated[NDArray, EMBEDDER]


if COCOINDEX_AVAILABLE:

    @coco.fn(memo=True)
    async def process_heritage_site(
        row: dict[str, Any],
        is_hidden: bool = False,
    ) -> HeritageChunk | None:
        if not row:
            return None
        site_id = str(row.get("site_id", ""))
        return HeritageChunk(
            chunk_id=f"heritage:{site_id}",
            site_id=site_id,
            site_name=str(row.get("site_name", "")),
            site_name_ga=str(row.get("site_name_ga", "")),
            site_type="hidden" if is_hidden else str(row.get("site_type", "monument")),
            county=str(row.get("county", "")),
            latitude=float(row.get("latitude", 0.0)),
            longitude=float(row.get("longitude", 0.0)),
            description=str(row.get("description", "")),
            embedding=None,
        )

    @coco.App(
        coco.AppConfig(
            name="HeritageEmbeddingApp",
        )
    )
    class HeritageEmbeddingApp(coco.CompiledApp):
        @coco.lifespan
        async def _app_lifespan(self, builder: coco.EnvironmentBuilder) -> AsyncIterator[None]:
            async for _ in shared_lifespan(builder):
                yield

        @coco.flow
        async def embed_heritage_sites(self) -> list[HeritageChunk]:
            chunks: list[HeritageChunk] = []
            for row in _read_ducklake_table(HERITAGE_DUCKLAKE_TABLES["sites"]):
                chunk = await process_heritage_site(row, is_hidden=False)
                if chunk is not None:
                    chunks.append(chunk)
            return chunks

        @coco.flow
        async def embed_hidden_heritages(self) -> list[HeritageChunk]:
            chunks: list[HeritageChunk] = []
            for row in _read_ducklake_table(HERITAGE_DUCKLAKE_TABLES["hidden_sites"]):
                chunk = await process_heritage_site(row, is_hidden=True)
                if chunk is not None:
                    chunks.append(chunk)
            return chunks


def mount_heritage_chunks_table() -> None:
    if not COCOINDEX_AVAILABLE:
        return
    try:
        lancedb.mount_table_target(
            LANCE_DB,
            table_name="cianfhoghlaim.language.heritage_chunks",
            embedding_dim=EMBED_DIM,
        )
        logger.info("heritage_chunks_mounted", table="cianfhoghlaim.language.heritage_chunks", dim=EMBED_DIM)
    except Exception as exc:
        logger.warning("heritage_chunks_mount_failed: %s", exc)


__all__ = [
    "COCOINDEX_AVAILABLE",
    "HeritageChunk",
    "HeritageEmbeddingApp",
    "HERITAGE_DUCKLAKE_TABLES",
    "mount_heritage_chunks_table",
    "process_heritage_site",
]