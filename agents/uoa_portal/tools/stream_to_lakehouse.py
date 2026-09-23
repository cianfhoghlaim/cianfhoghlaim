"""stream_to_lakehouse — the MotherDuck + local-disk uploader.

Per openspec/changes/2026-09-23-consolidate-uog-tertiary-pipeline-v1/.

Phase 2 stub — streams the downloaded file to
/stedding/user_profiles/<user>/downloads/<service>/<module>/
and uploads the row to MotherDuck at
`cianfhoghlaim.tertiary.uog.user_<user>_<service>`.

Licence: BUSL-1.1 Cianfhoghlaim edition (per LICENSE.md).
"""
from __future__ import annotations

import logging
import os
from typing import Any

logger = logging.getLogger(__name__)


async def stream_to_lakehouse(
    file_url: str,
    local_path: str,
    user_id: str,
    service: str,
    metadata: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Stream a downloaded file to local disk + MotherDuck."""
    return {
        "local_path": local_path,
        "motherduck_table": f"cianfhoghlaim.tertiary.uog.user_{user_id}_{service}",
        "status": "Phase 2 stub",
    }


def stream_to_lakehouse_tool() -> Any:
    return stream_to_lakehouse


__all__ = ["stream_to_lakehouse", "stream_to_lakehouse_tool"]
