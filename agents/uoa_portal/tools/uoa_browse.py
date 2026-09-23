"""uoa_browse — the Patchright browser tool for the UoA portal pipeline.

Per openspec/changes/2026-09-23-consolidate-uog-tertiary-pipeline-v1/.

The browser tool navigates regexam.nuigalway.ie or
canvas.universityofgalway.ie, takes a screenshot, and returns the
screenshot + the page URL + the relevant DOM for the vision agent to
interpret.

Licence: BUSL-1.1 Cianfhoghlaim edition (per LICENSE.md).
"""
from __future__ import annotations

import asyncio
import logging
import os
from typing import Any

logger = logging.getLogger(__name__)


async def uoa_browse_and_select(
    url: str,
    service: str,
    user_id: str | None = None,
    module_codes: list[str] | None = None,
) -> dict[str, Any]:
    """Navigate a UoG portal page, screenshot, and return the result.

    Args:
        url: the URL to navigate (regexam or canvas)
        service: 'regexam' or 'canvas'
        user_id: the per-user identifier (default: UO_PORTAL_USER env)
        module_codes: optional list of module codes to filter on
            (e.g. ['CS203', 'MA101'])

    Returns:
        dict with keys: page_url, screenshot_b64, dom_snippet, hint
    """
    user_id = user_id or os.environ.get("UO_PORTAL_USER", "default")

    cookies_path = (
        f"/stedding/user_profiles/{user_id}/{service}/cookies.json"
    )
    if not os.path.exists(cookies_path):
        logger.warning(
            "uoa_browse.no_cookies",
            user_id=user_id,
            service=service,
            path=cookies_path,
            hint="Run komodo unlock-uo-portal-profile first",
        )
        return {
            "page_url": url,
            "screenshot_b64": None,
            "dom_snippet": None,
            "hint": "No cookies found; run the 1-time M365 unlock first.",
        }

    return {
        "page_url": url,
        "screenshot_b64": None,
        "dom_snippet": None,
        "hint": f"Phase 2: Patchright will navigate + screenshot. user_id={user_id}, service={service}, modules={module_codes}",
    }


def uoa_browse_and_select_tool() -> Any:
    """FunctionTool wrapper for ADK registration."""
    return uoa_browse_and_select


__all__ = ["uoa_browse_and_select", "uoa_browse_and_select_tool"]
