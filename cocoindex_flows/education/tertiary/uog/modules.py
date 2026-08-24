"""modules — Wave 3 stub.

UoG tertiary pipeline stub. Per Wave 2, the real implementation
lives under `dlt_sources/education/tertiary/uog/modules/`.
"""
from __future__ import annotations

from collections.abc import AsyncIterator
from typing import Any

try:
    import cocoindex as coco  # type: ignore[import-not-found]
    COCOINDEX_AVAILABLE = True
except ImportError:
    COCOINDEX_AVAILABLE = False
    coco = None  # type: ignore[assignment]


if COCOINDEX_AVAILABLE:

    @coco.fn  # type: ignore[misc]
    async def modules_flow() -> AsyncIterator[dict[str, Any]]:
        """Stub: yield one dummy row."""
        yield {"kind": "modules_stub"}

    app = coco.App(
        coco.AppConfig(name="modules"),
        modules_flow,
        shared_lifespan=None,  # type: ignore[arg-type]
    )
else:
    app = None  # type: ignore[assignment]
