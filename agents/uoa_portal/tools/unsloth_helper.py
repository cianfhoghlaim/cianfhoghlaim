"""uoa_portal_unsloth — Unsloth Studio integration for the UoA portal pipeline.

Per openspec/changes/2026-09-23-uog-tertiary-real-data-upgrade-v1/.

Calls the Unsloth Studio headless server at :8888 (Anthropic-compatible
`/v1/messages`) + llama-swap at :8080 (OpenAI-compatible `/v1/chat/completions`)
for the 5 Unsloth GGUF models registered in
`meaisinfhoghlaim/models/llama_swap_config.yaml`:

  1. qwen3-vl-8b        — vision-language for screenshot interpretation
  2. qwen3-vl-4b        — lightweight vision fallback
  3. qwen3-vl-30b-a3b   — MoE 12x vision heavy
  4. qwen3.6-27b-mtp    — long-context (128K) text extraction
  5. gemma-4-26B-A4B    — multilingual structured extraction
  6. olmocr-2-7b-1025   — dedicated OCR

Persists every inference result to the
`cianfhoghlaim.tertiary.uog.unsloth_inference_log` DuckLake table
for downstream RAGAS eval (via the centralised-registry spec).

Licence: BUSL-1.1 Cianfhoghlaim edition (per LICENSE.md).
"""
from __future__ import annotations

import logging
import os
import time
from typing import Any

import httpx

logger = logging.getLogger(__name__)


UNSLOTH_STUDIO_URL = os.environ.get("UNSLOTH_STUDIO_URL", "http://unsloth-serve:8888")
LLAMA_SWAP_URL = os.environ.get("LLAMA_SWAP_URL", "http://llama-swap:8080")


UNSLOTH_MODEL_ALIASES = {
    "qwen3-vl-8b": "vision_default",
    "qwen3-vl-4b": "vision_light",
    "qwen3-vl-30b-a3b": "vision_heavy",
    "qwen3.6-27b-mtp": "long_context",
    "gemma-4-26B-A4B": "extract_strong",
    "olmocr-2-7b-1025": "ocr",
}


async def unsloth_complete(
    model: str,
    messages: list[dict],
    *,
    max_tokens: int = 2048,
    temperature: float = 0.1,
) -> dict[str, Any]:
    """Call the Unsloth Studio (Anthropic-compatible) endpoint.

    Args:
        model: one of the 6 Unsloth model aliases (see UNSLOTH_MODEL_ALIASES)
        messages: Anthropic-format messages list
        max_tokens: max output tokens (default 2048)
        temperature: sampling temperature (default 0.1 for determinism)

    Returns:
        dict with keys: model, content, latency_ms, error
    """
    if model not in UNSLOTH_MODEL_ALIASES:
        return {"model": model, "content": None, "error": f"unknown_model: {model}"}

    started = time.time()
    payload = {
        "model": model,
        "messages": messages,
        "max_tokens": max_tokens,
        "temperature": temperature,
    }

    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            resp = await client.post(f"{UNSLOTH_STUDIO_URL}/v1/messages", json=payload)
            resp.raise_for_status()
            data = resp.json()
            content = data.get("content", [{}])[0].get("text", "") if data.get("content") else ""
            latency_ms = (time.time() - started) * 1000
            logger.info("unsloth_complete", model=model, latency_ms=latency_ms)
            return {"model": model, "content": content, "latency_ms": latency_ms, "error": None}
    except Exception as exc:
        latency_ms = (time.time() - started) * 1000
        logger.error("unsloth_complete_failed", model=model, error=str(exc), latency_ms=latency_ms)
        return {"model": model, "content": None, "latency_ms": latency_ms, "error": str(exc)}


async def llama_swap_complete(
    model: str,
    messages: list[dict],
    *,
    max_tokens: int = 2048,
    temperature: float = 0.1,
) -> dict[str, Any]:
    """Call llama-swap (OpenAI-compatible) endpoint — fallback for non-Anthropic models."""
    started = time.time()
    payload = {
        "model": model,
        "messages": messages,
        "max_tokens": max_tokens,
        "temperature": temperature,
    }
    try:
        async with httpx.AsyncClient(timeout=60.0) as client:
            resp = await client.post(f"{LLAMA_SWAP_URL}/v1/chat/completions", json=payload)
            resp.raise_for_status()
            data = resp.json()
            content = data.get("choices", [{}])[0].get("message", {}).get("content", "")
            latency_ms = (time.time() - started) * 1000
            return {"model": model, "content": content, "latency_ms": latency_ms, "error": None}
    except Exception as exc:
        latency_ms = (time.time() - started) * 1000
        return {"model": model, "content": None, "latency_ms": latency_ms, "error": str(exc)}


async def persist_inference_log(
    inference: dict[str, Any],
    duckdb_conn: Any,
) -> None:
    """Write the inference result to the DuckLake `unsloth_inference_log` table."""
    duckdb_conn.execute(
        """
        INSERT INTO cianfhoghlaim.tertiary.uog.unsloth_inference_log
            (model, content, latency_ms, error, scraped_at)
        VALUES (?, ?, ?, ?, ?)
        """,
        [
            inference.get("model"),
            inference.get("content", ""),
            inference.get("latency_ms", 0),
            inference.get("error", ""),
            datetime.now(UTC()).isoformat() if (UTC := __import__("datetime").timezone.utc) else None,
        ],
    )


__all__ = [
    "UNSLOTH_MODEL_ALIASES",
    "UNSLOTH_STUDIO_URL",
    "LLAMA_SWAP_URL",
    "unsloth_complete",
    "llama_swap_complete",
    "persist_inference_log",
]
