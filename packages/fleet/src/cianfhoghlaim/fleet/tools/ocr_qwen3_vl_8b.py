"""ocr_qwen3_vl_8b — Unsloth Studio Qwen3-VL-8B-Instruct OCR tool.

Per the 2026-08-21-meaisinfhoghlaim-unsloth-agents-integration-v1 change.
Routes through Hermes + litellm + Unsloth Studio (host.docker.internal:8888).

Usage:
    result = await ocr_qwen3_vl_8b(file_path="/path/to/paper.pdf", languages=["en", "ga"])
    # Returns {"text": str, "regions": list[dict]}
"""

from __future__ import annotations

import os
from typing import Any

import httpx


LITELLM_URL = os.environ.get("LITELLM_URL", "http://localhost:4000")
LITELLM_MASTER_KEY = os.environ.get("LITELLM_MASTER_KEY", "")
UNSLOTH_STUDIO_MODEL = os.environ.get("UNSLOTH_MODEL", "local/unsloth/qwen3-vl-8b-instruct")
TIMEOUT_SECONDS = int(os.environ.get("OCR_TIMEOUT_SECONDS", "300"))


async def ocr_qwen3_vl_8b(file_path: str, languages: list[str] | None = None) -> dict[str, Any]:
    """OCR a PDF using Qwen3-VL-8B-Instruct via Unsloth Studio.

    Args:
        file_path: Absolute path to the PDF file.
        languages: Optional list of expected languages (e.g., ["en", "ga"]).

    Returns:
        {"text": str, "regions": list[dict]} with per-region confidence.
    """
    if languages is None:
        languages = ["en"]

    with open(file_path, "rb") as fh:
        import base64
        b64_pdf = base64.b64encode(fh.read()).decode("ascii")

    payload = {
        "model": UNSLOTH_STUDIO_MODEL,
        "messages": [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": f"Extract all text from this PDF. Languages: {','.join(languages)}. Return as plain text with region bounding boxes."},
                    {"type": "file_b64", "data": b64_pdf, "media_type": "application/pdf"},
                ],
            }
        ],
        "max_tokens": 8192,
        "temperature": 0.0,
    }

    headers = {
        "Authorization": f"Bearer {LITELLM_MASTER_KEY}",
        "Content-Type": "application/json",
    }

    async with httpx.AsyncClient(timeout=TIMEOUT_SECONDS) as client:
        resp = await client.post(
            f"{LITELLM_URL}/v1/chat/completions",
            json=payload,
            headers=headers,
        )
        resp.raise_for_status()
        data = resp.json()

    text = data["choices"][0]["message"]["content"]

    # TODO: parse regions from text response (Qwen3-VL-8B doesn't return bounding boxes natively)
    return {"text": text, "regions": [{"page": 0, "bbox": [0, 0, 0, 0], "confidence": 1.0, "text": text}]}


__all__ = ["ocr_qwen3_vl_8b"]
