"""ocr_gemma4_26b — llama-swap Gemma 4 26B-A4B OCR tool (legacy fallback).

Per the 2026-08-21-meaisinfhoghlaim-unsloth-agents-integration-v1 change.
Routes through Hermes + litellm + llama-swap (http://llama-swap:8080).
Used as the fallback when Unsloth Studio is unavailable.
"""

from __future__ import annotations

import os
from typing import Any

import httpx


LITELLM_URL = os.environ.get("LITELLM_URL", "http://localhost:4000")
LITELLM_MASTER_KEY = os.environ.get("LITELLM_MASTER_KEY", "")
TIMEOUT_SECONDS = int(os.environ.get("OCR_TIMEOUT_SECONDS", "300"))


async def ocr_gemma4_26b(file_path: str, languages: list[str] | None = None) -> dict[str, Any]:
    """OCR a PDF using Gemma 4 26B-A4B via llama-swap (fallback)."""
    if languages is None:
        languages = ["en"]

    with open(file_path, "rb") as fh:
        import base64
        b64_pdf = base64.b64encode(fh.read()).decode("ascii")

    payload = {
        "model": "local/vision/gemma-4-26B-A4B",
        "messages": [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": f"Extract all text from this PDF. Languages: {','.join(languages)}."},
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
    return {"text": text, "regions": [{"page": 0, "bbox": [0, 0, 0, 0], "confidence": 1.0, "text": text}]}


__all__ = ["ocr_gemma4_26b"]
