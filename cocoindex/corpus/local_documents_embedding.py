"""
Local documents by subject — CocoIndex v1 App.

Embeds the local PDF documents (per subject: comp_science, gaeilge,
mata, oideachas) from bunchloch into LanceDB.

LanceDB table: ``cianfhoghlaim.language.local_documents_chunks``.

R1–R4 v1 conformance.

LlamaSwap routing per the shared table:
- local_documents * → ``qwen3-vl-8b`` (OCR workhorse)

Reads from: ``cianfhoghlaim.celtic.local_documents.{subject}_documents``

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


from ._lifespan import (  # noqa: E402
    EMBEDDER,
    EMBED_DIM,
    EMBED_MODEL,
    LANCE_DB,
    shared_lifespan,
)


LOCAL_DOCUMENTS_DUCKLAKE_TABLES = {
    "comp_science": "cianfhoghlaim.celtic.local_documents.comp_science_documents",
    "gaeilge": "cianfhoghlaim.celtic.local_documents.gaeilge_documents",
    "mata": "cianfhoghlaim.celtic.local_documents.mata_documents",
    "oideachas": "cianfhoghlaim.celtic.local_documents.oideachas_documents",
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
class LocalDocumentChunk:
    """One chunked + embedded local document row."""

    chunk_id: str
    file_name: str
    file_path: str
    subject: str
    extension: str
    size_bytes: int
    content_text: str
    embedding: Annotated[NDArray, EMBEDDER]


if COCOINDEX_AVAILABLE:

    @coco.fn(memo=True)
    async def process_local_document(
        row: dict[str, Any],
        subject: str,
    ) -> LocalDocumentChunk | None:
        if not row:
            return None
        file_path = str(row.get("file_path", ""))
        return LocalDocumentChunk(
            chunk_id=f"local_documents:{subject}:{file_path}",
            file_name=str(row.get("file_name", "")),
            file_path=file_path,
            subject=subject,
            extension=str(row.get("extension", "")),
            size_bytes=int(row.get("size_bytes", 0)),
            content_text=str(row.get("content_text", ""))[:5000],
            embedding=None,
        )

    @coco.App(
        coco.AppConfig(
            name="LocalDocumentsEmbeddingApp",
            description="Embeds local PDF documents (per subject: comp_science, gaeilge, mata, oideachas) into LanceDB via BGE-M3.",
        )
    )
    class LocalDocumentsEmbeddingApp(coco.CompiledApp):
        @coco.lifespan
        async def _app_lifespan(self, builder: coco.EnvironmentBuilder) -> AsyncIterator[None]:
            async for _ in shared_lifespan(builder):
                yield

        @coco.flow
        async def embed_local_documents(self) -> list[LocalDocumentChunk]:
            chunks: list[LocalDocumentChunk] = []
            for subject, table in LOCAL_DOCUMENTS_DUCKLAKE_TABLES.items():
                for row in _read_ducklake_table(table):
                    chunk = await process_local_document(row, subject)
                    if chunk is not None:
                        chunks.append(chunk)
            return chunks


def mount_local_documents_chunks_table() -> None:
    if not COCOINDEX_AVAILABLE:
        return
    try:
        lancedb.mount_table_target(
            LANCE_DB,
            table_name="cianfhoghlaim.language.local_documents_chunks",
            embedding_dim=EMBED_DIM,
        )
        logger.info(
            "local_documents_chunks_mounted",
            table="cianfhoghlaim.language.local_documents_chunks",
            dim=EMBED_DIM,
        )
    except Exception as exc:
        logger.warning("local_documents_chunks_mount_failed: %s", exc)


__all__ = [
    "COCOINDEX_AVAILABLE",
    "LocalDocumentChunk",
    "LocalDocumentsEmbeddingApp",
    "LOCAL_DOCUMENTS_DUCKLAKE_TABLES",
    "mount_local_documents_chunks_table",
    "process_local_document",
]