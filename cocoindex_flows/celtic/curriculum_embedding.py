"""
Celtic curriculum + mythology + grammar + morphology — CocoIndex v1 App.

Embeds the 6 Celtic-language curricula (Irish, Scottish Gaelic, Welsh,
Manx, Cornish, Breton) into LanceDB.

LanceDB table: ``cianfhoghlaim.celtic.curriculum_chunks``.

R1–R4 v1 conformance.

LlamaSwap routing per the shared table:
- celtic_curriculum ga → ``uccix-mistral-24b``
- celtic_curriculum cy/gd/br/gv/kw → ``gemma-4-26B-A4B``

Reads from:
- ``cianfhoghlaim.celtic.curriculum.{irish,scottish_gaelic,welsh,breton,manx,cornish}``

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


CELTIC_CURRICULUM_DUCKLAKE_TABLES = {
    "irish": "cianfhoghlaim.celtic.curriculum.irish",
    "scottish_gaelic": "cianfhoghlaim.celtic.curriculum.scottish_gaelic",
    "welsh": "cianfhoghlaim.celtic.curriculum.welsh",
    "breton": "cianfhoghlaim.celtic.curriculum.breton",
    "manx": "cianfhoghlaim.celtic.curriculum.manx",
    "cornish": "cianfhoghlaim.celtic.curriculum.cornish",
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
class CelticCurriculumChunk:
    """One chunked + embedded Celtic curriculum spec."""

    chunk_id: str
    language: str  # "irish" | "scottish_gaelic" | "welsh" | "breton" | "manx" | "cornish"
    nation_code: str
    education_level: str  # "primary" | "secondary" | "higher"
    year_levels: str  # comma-separated
    curriculum_body: str
    framework_name: str
    framework_name_native: str | None
    content_text: str
    embedding: Annotated[NDArray, EMBEDDER]


if COCOINDEX_AVAILABLE:

    @coco.fn(memo=True)
    async def process_celtic_curriculum(
        row: dict[str, Any],
        language: str,
    ) -> CelticCurriculumChunk | None:
        if not row:
            return None
        return CelticCurriculumChunk(
            chunk_id=f"celtic_curriculum:{language}:{row.get('framework_name', '')}",
            language=language,
            nation_code=str(row.get("nation_code", "")),
            education_level=str(row.get("education_level", "primary")),
            year_levels=str(row.get("year_levels", "")),
            curriculum_body=str(row.get("curriculum_body", "")),
            framework_name=str(row.get("framework_name", "")),
            framework_name_native=row.get("framework_name_native"),
            content_text=str(row.get("content_text", ""))[:5000],
            embedding=None,
        )

    @coco.App(
        coco.AppConfig(
            name="CelticCurriculumEmbeddingApp",
            description="Embeds the 6 Celtic-language curricula (Irish, Scottish Gaelic, Welsh, Breton, Manx, Cornish) into LanceDB.",
        )
    )
    class CelticCurriculumEmbeddingApp(coco.CompiledApp):
        @coco.lifespan
        async def _app_lifespan(self, builder: coco.EnvironmentBuilder) -> AsyncIterator[None]:
            async for _ in shared_lifespan(builder):
                yield

        @coco.flow
        async def embed_celtic_curricula(self) -> list[CelticCurriculumChunk]:
            chunks: list[CelticCurriculumChunk] = []
            for language, table in CELTIC_CURRICULUM_DUCKLAKE_TABLES.items():
                for row in _read_ducklake_table(table):
                    chunk = await process_celtic_curriculum(row, language)
                    if chunk is not None:
                        chunks.append(chunk)
            return chunks


def mount_celtic_curriculum_chunks_table() -> None:
    if not COCOINDEX_AVAILABLE:
        return
    try:
        lancedb.mount_table_target(
            LANCE_DB,
            table_name="cianfhoghlaim.celtic.curriculum_chunks",
            embedding_dim=EMBED_DIM,
        )
        logger.info(
            "celtic_curriculum_chunks_mounted",
            table="cianfhoghlaim.celtic.curriculum_chunks",
            dim=EMBED_DIM,
        )
    except Exception as exc:
        logger.warning("celtic_curriculum_chunks_mount_failed: %s", exc)


__all__ = [
    "COCOINDEX_AVAILABLE",
    "CelticCurriculumChunk",
    "CelticCurriculumEmbeddingApp",
    "CELTIC_CURRICULUM_DUCKLAKE_TABLES",
    "mount_celtic_curriculum_chunks_table",
    "process_celtic_curriculum",
]