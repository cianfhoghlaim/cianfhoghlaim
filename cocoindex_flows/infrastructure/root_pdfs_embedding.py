
"""root_pdfs_embedding — Wave 3 stub.

Root PDFs (NCCA / SEC) embedding. The actual implementation lands
in Wave 3 follow-up PRs.
"""
from __future__ import annotations

from collections.abc import AsyncIterator
from typing import Annotated, Any

try:
    import cocoindex as coco  # type: ignore[import-not-found]
    COCOINDEX_AVAILABLE = True
except ImportError:
    COCOINDEX_AVAILABLE = False
    coco = None  # type: ignore[assignment]


if COCOINDEX_AVAILABLE:

    @coco.fn  # type: ignore[misc]
    async def root_pdfs_embedding(  # type: ignore[no-untyped-def,unused-ignore]
        file_path: str,
    ) -> AsyncIterator[dict[str, Any]]:
        """Stub: yield one dummy row."""
        yield {{"file_path": file_path, "kind": "root_pdfs_stub"}}

    app = coco.App(
        coco.AppConfig(name="root_pdfs_embedding"),
        root_pdfs_embedding,
        shared_lifespan=None,  # type: ignore[arg-type]
    )
else:
    app = None  # type: ignore[assignment]
