"""baml_extract_uoa_portal — the BAML extraction tool for the UoA portal.

Per openspec/changes/2026-09-23-consolidate-uog-tertiary-pipeline-v1/.

Phase 2 stub — calls the ExtractUoAPortalContent BAML function (at
baml_src/british_isles/ireland/tertiary/uoa_portal_content.baml) to
extract the structured UoAPortalContent from the downloaded file's
markdown.

Licence: BUSL-1.1 Cianfhoghlaim edition (per LICENSE.md).
"""
from __future__ import annotations

import logging
from typing import Any

logger = logging.getLogger(__name__)


async def baml_extract_uoa_portal(
    markdown: str,
    source: str,
) -> list[dict[str, Any]]:
    """Extract UoAPortalContent from a markdown blob.

    Args:
        markdown: the markdown text extracted from the downloaded file
        source: 'regexam' or 'canvas'
    """
    try:
        from baml_client import b  # type: ignore[import-not-found]

        return [c.model_dump() for c in b.ExtractUoAPortalContent(markdown=markdown, source=source)]
    except Exception as exc:
        logger.warning("baml_extract_uoa_portal.baml_unavailable: %s", exc)
        return []


def baml_extract_uoa_portal_tool() -> Any:
    return baml_extract_uoa_portal


__all__ = ["baml_extract_uoa_portal", "baml_extract_uoa_portal_tool"]
