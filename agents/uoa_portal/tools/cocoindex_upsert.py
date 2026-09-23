"""cocoindex_upsert — the LanceDB embedder for the UoA portal.

Per openspec/changes/2026-09-23-consolidate-uog-tertiary-pipeline-v1/.

Phase 2 stub — embeds the extracted UoAPortalContent via
BAAI/bge-m3 (1024-d multilingual) + writes to
`uog_user_<user>_<service>_chunks` LanceDB table.

Licence: BUSL-1.1 Cianfhoghlaim edition (per LICENSE.md).
"""
from __future__ import annotations

import logging
from typing import Any

logger = logging.getLogger(__name__)


async def cocoindex_upsert(
    user_id: str,
    service: str,
    chunks: list[dict[str, Any]],
) -> dict[str, Any]:
    """Upsert chunks into the LanceDB table for the user's service."""
    return {
        "table": f"uog_user_{user_id}_{service}_chunks",
        "rows_upserted": len(chunks),
        "status": "Phase 2 stub",
    }


def cocoindex_upsert_tool() -> Any:
    return cocoindex_upsert


__all__ = ["cocoindex_upsert", "cocoindex_upsert_tool"]
