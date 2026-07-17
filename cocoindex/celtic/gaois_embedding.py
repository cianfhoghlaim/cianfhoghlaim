"""
Gaois + Celtic Language Pipeline — Gaois APIs CocoIndex v1 App.

Embeds the 3 Gaois linguistic API sources (Téarma + Logainm + Ainm) into
LanceDB via BGE-M3 (multilingual 1024-d, supports Irish).

LanceDB table: ``cianfhoghlaim.language.gaois_chunks``.

R1–R4 v1 conformance contract per ``_lifespan.py``:
- R1 — ``from ._lifespan import shared_lifespan``
- R2 — Imports the canonical ``LANCE_DB`` + ``EMBEDDER`` from ``_lifespan``
- R3 — ``app = coco.App(coco.AppConfig(name=...))`` at module scope
- R4 — ``@coco.fn`` decorator + ``lancedb.mount_table_target(LANCE_DB, ...)``

LlamaSwap routing (per the shared routing table at
``cianfhoghlaim.meaisinfhoghlaim.models.routing``):
- Irish (ga) → ``uccix-mistral-24b`` (UCCIX)
- English (en) → ``gemma-4-26B-A4B``
- Default → ``gemma-4-26B-A4B``

Reads from the canonical DuckLake tables:
- ``cianfhoghlaim.celtic.gaois.tearma_terms`` (Téarma)
- ``cianfhoghlaim.celtic.gaois.logainm_places`` (Logainm)
- ``cianfhoghlaim.celtic.gaois.ainm_biographies`` (Ainm)

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

# CocoIndex is optional — degrade gracefully if not installed.
try:
    import cocoindex as coco  # type: ignore[import-not-found]
    from cocoindex.connectors import lancedb  # type: ignore[import-not-found]

    COCOINDEX_AVAILABLE = True
except ImportError as exc:  # pragma: no cover - defensive
    logger.warning("cocoindex_v1_not_available: %s", exc)
    COCOINDEX_AVAILABLE = False
    coco = None  # type: ignore[assignment]
    lancedb = None  # type: ignore[assignment]


# Shared lifespan (REFACTORING.md item 12).
from ._lifespan import (  # noqa: E402
    EMBEDDER,
    EMBED_DIM,
    EMBED_MODEL,
    LANCE_DB,
    shared_lifespan,
)


# =============================================================================
# DuckLake source tables (the 3 Gaois sources)
# =============================================================================

GAOIS_DUCKLAKE_TABLES = {
    "tearma_terms": "cianfhoghlaim.celtic.gaois.tearma_terms",
    "tearma_education": "cianfhoghlaim.celtic.gaois.tearma_education",
    "logainm_places": "cianfhoghlaim.celtic.gaois.logainm_places",
    "ainm_biographies": "cianfhoghlaim.celtic.gaois.ainm_biographies",
}


def _read_ducklake_table(table: str) -> list[dict[str, Any]]:
    """Read rows from a Gaois DuckLake table via the local DuckDB destination."""
    try:
        import duckdb  # type: ignore[import-not-found]
    except ImportError:
        logger.warning("duckdb_not_available_for_gaois_embedding")
        return []

    db_path = os.environ.get("DUCKDB_PATH", "/tmp/cianfhoghlaim.duckdb")
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
# Data model — one chunked + embedded Gaois terminology row
# =============================================================================


@dataclass
class GaoisChunk:
    """One chunked + embedded Gaois terminology row (Téarma + Logainm + Ainm)."""

    chunk_id: str
    source_kind: str  # "tearma" | "logainm" | "ainm"
    term_en: str
    term_ga: str
    domain: str
    language: str  # "ga" | "en" | "both"
    category: str | None
    description: str
    embedding: Annotated[NDArray, EMBEDDER]


# =============================================================================
# CocoIndex v1 App — GaoisEmbeddingApp
# =============================================================================


if COCOINDEX_AVAILABLE:

    @coco.fn(memo=True)
    async def process_gaois_row(
        row: dict[str, Any],
        source_kind: str,
    ) -> GaoisChunk | None:
        """Process one Gaois source row into a chunked + embedded GaoisChunk."""
        if not row:
            return None
        chunk_id = f"{source_kind}:{row.get('term_en', row.get('place_name', row.get('ainm_id', 'unknown')))}"
        text = (
            f"{row.get('term_en', '')} / {row.get('term_ga', '')} — "
            f"{row.get('description', row.get('place_name', row.get('full_name', '')))}"
        )
        # BGE-M3 multilingual embedder (handles both ga + en)
        return GaoisChunk(
            chunk_id=chunk_id,
            source_kind=source_kind,
            term_en=str(row.get("term_en", row.get("place_name", row.get("full_name", "")))),
            term_ga=str(row.get("term_ga", row.get("place_name_ga", row.get("name_ga", "")))),
            domain=str(row.get("domain", row.get("category", ""))),
            language=str(row.get("language", "both")),
            category=row.get("category"),
            description=text,
            embedding=None,  # populated by the embedder at App materialization
        )

    @coco.App(
        coco.AppConfig(
            name="GaoisEmbeddingApp",
            description="Embeds the 3 Gaois linguistic API sources (Téarma + Logainm + Ainm) into LanceDB via BGE-M3 (1024-d, multilingual).",
        )
    )
    class GaoisEmbeddingApp(coco.CompiledApp):
        """The Gaois v1 CocoIndex App.

        Reads from the 3 Gaois DuckLake tables (Téarma terms + Logainm
        places + Ainm biographies), chunks each row, embeds with BGE-M3,
        and mounts the chunks into ``cianfhoghlaim.language.gaois_chunks``.
        """

        @coco.lifespan
        async def _app_lifespan(self, builder: coco.EnvironmentBuilder) -> AsyncIterator[None]:
            async for _ in shared_lifespan(builder):
                yield

        @coco.flow
        async def embed_gaois_sources(self) -> list[GaoisChunk]:
            """Embed all 3 Gaois sources into LanceDB."""
            chunks: list[GaoisChunk] = []
            for source_kind, table in [
                ("tearma", GAOIS_DUCKLAKE_TABLES["tearma_terms"]),
                ("logainm", GAOIS_DUCKLAKE_TABLES["logainm_places"]),
                ("ainm", GAOIS_DUCKLAKE_TABLES["ainm_biographies"]),
            ]:
                for row in _read_ducklake_table(table):
                    chunk = await process_gaois_row(row, source_kind)
                    if chunk is not None:
                        chunks.append(chunk)
            return chunks


# =============================================================================
# LanceDB mount (R4 — the only persistent side-effect)
# =============================================================================


def mount_gaois_chunks_table() -> None:
    """Mount the Gaois chunks LanceDB table on App startup.

    Called by the Dagster L3 component (per
    ``orchestration/defs/3_model_lifecycle/cocoindex_v1/gaois_embedding/defs.yaml``).
    """
    if not COCOINDEX_AVAILABLE:
        logger.warning("cocoindex_v1_not_available: gaois_chunks_mount_skipped")
        return
    try:
        lancedb.mount_table_target(
            LANCE_DB,
            table_name="cianfhoghlaim.language.gaois_chunks",
            embedding_dim=EMBED_DIM,
        )
        logger.info("gaois_chunks_mounted", table="cianfhoghlaim.language.gaois_chunks", dim=EMBED_DIM)
    except Exception as exc:  # noqa: BLE001 - defensive
        logger.warning("gaois_chunks_mount_failed: %s", exc)


__all__ = [
    "COCOINDEX_AVAILABLE",
    "GaoisChunk",
    "GaoisEmbeddingApp",
    "GAOIS_DUCKLAKE_TABLES",
    "mount_gaois_chunks_table",
    "process_gaois_row",
]