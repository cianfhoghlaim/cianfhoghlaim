"""web_form_fill — Auto-fill forms online via Playwright MCP.

Per the 2026-08-21-meaisinfhoghlaim-unsloth-agents-integration-v1 change.
Routes through Playwright MCP for browser automation. Allows Hermes + OpenClaw
agents to fill out web forms (e.g., student registration, survey responses).
"""

from __future__ import annotations

import os
from typing import Any

import httpx


PLAYWRIGHT_MCP_URL = os.environ.get("PLAYWRIGHT_MCP_URL", "http://playwright-mcp:8080")
TIMEOUT_SECONDS = int(os.environ.get("PLAYWRIGHT_TIMEOUT_SECONDS", "60"))


async def web_form_fill(url: str, fields: dict[str, str]) -> dict[str, Any]:
    """Fill out a web form using Playwright browser automation.

    Args:
        url: The URL of the form to fill out.
        fields: Dict mapping field selectors (CSS/XPath) to values.

    Returns:
        {"screenshot": str, "submitted": bool}
    """
    payload = {
        "action": "fill_form",
        "url": url,
        "fields": fields,
        "wait_for": "networkidle",
        "screenshot": True,
    }

    async with httpx.AsyncClient(timeout=TIMEOUT_SECONDS) as client:
        resp = await client.post(
            f"{PLAYWRIGHT_MCP_URL}/v1/browser/fill_form",
            json=payload,
        )
        resp.raise_for_status()
        result = resp.json()

    return {
        "screenshot": result.get("screenshot", ""),  # base64-encoded PNG
        "submitted": result.get("submitted", True),
    }


__all__ = ["web_form_fill"]
