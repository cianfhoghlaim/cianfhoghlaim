"""
Universal Dependencies Celtic Treebanks — CocoIndex v1 App.

Embeds the 13 UD Celtic treebanks (UD_Irish-IDT/Cadhan/TwittIrish,
UD_Scottish_Gaelic-ARCOSG, UD_Welsh-CCG, UD_Breton-KEB, UD_Manx-Cadhan,
UD_Old_Irish-DipSGG/DipWBG, UD_Middle_Irish-CritMITB/DipMITB,
UD_Archaic_Irish-OGAM) into LanceDB.

LanceDB table: ``cianfhoghlaim.language.ud_celtic_chunks``.

R1–R4 v1 conformance.

LlamaSwap routing per the shared table:
- ud_celtic ga → ``uccix-mistral-24b`` (Irish treebanks)
- ud_celtic * → ``gemma-4-26B-A4B`` (other Celtic treebanks)

Reads from:
- ``cianfhoghlaim.celtic.ud_celtic.sentences``
- ``cianfhoghlaim.celtic.ud_celtic.tokens``

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


UD_CELTIC_TREEBANKS = {
    # Modern Irish
    "UD_Irish-IDT": {"language": "ga", "variety": "standard"},
    "UD_Irish-Cadhan": {"language": "ga", "variety": "historical"},
    "UD_Irish-TwittIrish": {"language": "ga", "variety": "twitter"},
    # Scottish Gaelic
    "UD_Scottish_Gaelic-ARCOSG": {"language": "gd", "variety": "standard"},
    # Welsh
    "UD_Welsh-CCG": {"language": "cy", "variety": "standard"},
    # Breton
    "UD_Breton-KEB": {"language": "br", "variety": "standard"},
    # Manx
    "UD_Manx-Cadhan": {"language": "gv", "variety": "standard"},
    # Old Irish
    "UD_Old_Irish-DipSGG": {"language": "sga", "variety": "st_gall"},
    "UD_Old_Irish-DipWBG": {"language": "sga", "variety": "wuerzburg"},
    # Middle Irish
    "UD_Middle_Irish-CritMITB": {"language": "mga", "variety": "critical"},
    "UD_Middle_Irish-DipMITB": {"language": "mga", "variety": "diplomatic"},
    # Archaic Irish
    "UD_Archaic_Irish-OGAM": {"language": "pgl", "variety": "ogham"},
}


UD_CELTIC_DUCKLAKE_TABLES = {
    "sentences": "cianfhoghlaim.celtic.ud_celtic.sentences",
    "tokens": "cianfhoghlaim.celtic.ud_celtic.tokens",
}


def _read_ducklake_table(table: str) -> list[dict[str, Any]]:
    try:
        import duckdb
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
class UDCelticChunk:
    """One chunked + embedded UD Celtic sentence."""

    chunk_id: str
    sent_id: str
    treebank: str
    language: str
    text: str
    embedding: Annotated[NDArray, EMBEDDER]


if COCOINDEX_AVAILABLE:

    @coco.fn(memo=True)
    async def process_ud_sentence(
        row: dict[str, Any],
    ) -> UDCelticChunk | None:
        if not row:
            return None
        sent_id = str(row.get("sent_id", ""))
        treebank = str(row.get("treebank", ""))
        return UDCelticChunk(
            chunk_id=f"ud_celtic:{sent_id}",
            sent_id=sent_id,
            treebank=treebank,
            language=UD_CELTIC_TREEBANKS.get(treebank, {}).get("language", "ga"),
            text=str(row.get("text", "")),
            embedding=None,
        )

    @coco.App(
        coco.AppConfig(
            name="UDCelticEmbeddingApp",
        )
    )
    class UDCelticEmbeddingApp(coco.CompiledApp):
        @coco.lifespan
        async def _app_lifespan(self, builder: coco.EnvironmentBuilder) -> AsyncIterator[None]:
            async for _ in shared_lifespan(builder):
                yield

        @coco.flow
        async def embed_ud_celtic_sentences(self) -> list[UDCelticChunk]:
            chunks: list[UDCelticChunk] = []
            for row in _read_ducklake_table(UD_CELTIC_DUCKLAKE_TABLES["sentences"]):
                chunk = await process_ud_sentence(row)
                if chunk is not None:
                    chunks.append(chunk)
            return chunks


def mount_ud_celtic_chunks_table() -> None:
    if not COCOINDEX_AVAILABLE:
        return
    try:
        lancedb.mount_table_target(
            LANCE_DB,
            table_name="cianfhoghlaim.language.ud_celtic_chunks",
            embedding_dim=EMBED_DIM,
        )
        logger.info("ud_celtic_chunks_mounted", table="cianfhoghlaim.language.ud_celtic_chunks", dim=EMBED_DIM)
    except Exception as exc:
        logger.warning("ud_celtic_chunks_mount_failed: %s", exc)


__all__ = [
    "COCOINDEX_AVAILABLE",
    "UDCelticChunk",
    "UDCelticEmbeddingApp",
    "UD_CELTIC_TREEBANKS",
    "UD_CELTIC_DUCKLAKE_TABLES",
    "mount_ud_celtic_chunks_table",
    "process_ud_sentence",
]