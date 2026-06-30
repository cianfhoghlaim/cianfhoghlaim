"""History v1 CocoIndex Embedding App."""
from __future__ import annotations

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
except ImportError:
    COCOINDEX_AVAILABLE = False

from ._lifespan import EMBEDDER  # noqa: E402

DEFAULT_HIST_ROOT = pathlib.Path(
    os.getenv("CIANFHOGHLAIM_HIST_ROOT", str(pathlib.Path(__file__).resolve().parents[2] / "leaving_certificate" / "history"))
)


if COCOINDEX_AVAILABLE:
    @coco.App(refresh_interval=300)
    async def history_embedding(level: str = "hl", language: str = "en") -> AsyncIterator[dict[str, Any]]:
        if not DEFAULT_HIST_ROOT.exists():
            return
        file_records = localfs.walk_dir(DEFAULT_HIST_ROOT / language, recursive=True, path_matcher=None, live=True)
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
                continue
            chunks = _chunk_text(text)
            for i, chunk in enumerate(chunks):
                yield {
                    "id": IdGenerator(file_path + f"#{i}"),
                    "filename": file_name,
                    "chunk_index": i,
                    "text": chunk,
                    "level": level,
                    "language": language,
                    "subject": "history",
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