"""ocr_docling — Docling DocTags XML extraction tool.

Per the 2026-08-21-meaisinfhoghlaim-unsloth-agents-integration-v1 change.
Routes through Docling Serve at http://docling-serve:5001 for layout-aware extraction.
"""

from __future__ import annotations

import os
from typing import Any

import httpx


DOCLING_URL = os.environ.get("DOCLING_URL", "http://docling-serve:5001")
TIMEOUT_SECONDS = int(os.environ.get("OCR_TIMEOUT_SECONDS", "300"))


async def ocr_docling(file_path: str) -> dict[str, Any]:
    """OCR a PDF using Docling DocTags XML output.

    Returns:
        {"text": str, "doctags_xml": str} with layout-aware structure.
    """
    with open(file_path, "rb") as fh:
        files = {"file": (file_path.split("/")[-1], fh, "application/pdf")}

        async with httpx.AsyncClient(timeout=TIMEOUT_SECONDS) as client:
            resp = await client.post(
                f"{DOCLING_URL}/v1/ocr/file",
                files=files,
                data={"output_format": "doctags"},
            )
            resp.raise_for_status()
            result = resp.json()

    return {
        "text": result.get("text", ""),
        "doctags_xml": result.get("doctags", ""),
    }


__all__ = ["ocr_docling"]
