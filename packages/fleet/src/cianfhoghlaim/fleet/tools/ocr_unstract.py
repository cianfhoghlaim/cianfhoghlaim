"""ocr_unstract — Unstract prompt-driven extraction tool.

Per the 2026-08-21-meaisinfhoghlaim-unsloth-agents-integration-v1 change.
Routes through Unstract at http://unstract:8002 for schema-driven extraction.
"""

from __future__ import annotations

import os
from typing import Any

import httpx


UNSTRACT_URL = os.environ.get("UNSTRACT_URL", "http://unstract:8002")
UNSTRACT_API_KEY = os.environ.get("UNSTRACT_API_KEY", "")
TIMEOUT_SECONDS = int(os.environ.get("OCR_TIMEOUT_SECONDS", "300"))


async def ocr_unstract(file_path: str, schema: dict | None = None) -> dict[str, Any]:
    """Extract structured data from a PDF using Unstract prompt-driven extraction.

    Args:
        file_path: Absolute path to the PDF file.
        schema: Optional extraction schema (Unstract prompt configuration).

    Returns:
        {"extracted": dict, "confidence": float}
    """
    if schema is None:
        schema = {"text": "string", "tables": "list[dict]"}

    with open(file_path, "rb") as fh:
        files = {"file": (file_path.split("/")[-1], fh, "application/pdf")}
        data = {"schema": str(schema)}

        headers = {"Authorization": f"Bearer {UNSTRACT_API_KEY}"} if UNSTRACT_API_KEY else {}

        async with httpx.AsyncClient(timeout=TIMEOUT_SECONDS) as client:
            resp = await client.post(
                f"{UNSTRACT_URL}/api/v1/extract",
                files=files,
                data=data,
                headers=headers,
            )
            resp.raise_for_status()
            result = resp.json()

    return {
        "extracted": result.get("data", result),
        "confidence": result.get("confidence", 0.85),
    }


__all__ = ["ocr_unstract"]
