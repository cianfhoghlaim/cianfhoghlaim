"""
Vision Model Comparison Module.

Compares vision-language models for document OCR via LiteLLM.

Supported models:
- Qwen3-VL-30B (GGUF via llama-swap)
- GLM-4.6V-Flash (GGUF via llama-swap)
- Gemma-3-27B (GGUF via llama-swap)
- OlmOCR-7B (MLX via mlx-omni-server)
- Granite-Docling (MLX)

All models accessed through LiteLLM unified API.

Usage:
    from oideachas.ocr.vision_comparison import compare_vision_models

    results = await compare_vision_models(
        image_bytes,
        models=["qwen3-vl", "glm-4.6v-flash"],
        prompt="Extract all text from this document."
    )
"""

from __future__ import annotations

import asyncio
import base64
import os
import time
from dataclasses import dataclass, field
from enum import Enum
from pathlib import Path
from typing import Any

import httpx

# ============================================================================
# Configuration
# ============================================================================


class VisionModel(str, Enum):
    """Supported vision models."""

    QWEN3_VL = "qwen3-vl"
    QWEN3_VL_30B = "qwen3-vl-30b"
    GLM_4_6V_FLASH = "glm-4.6v-flash"
    GEMMA_3_27B = "gemma-3-27b"
    OLMOCR_7B = "olmocr-7b"
    GRANITE_DOCLING = "granite-docling"
    MOONDREAM2 = "moondream2"


# Model configuration mapping to LiteLLM model IDs
VISION_MODELS: dict[str, dict[str, Any]] = {
    "qwen3-vl": {
        "model_id": "local/vision/qwen3-vl",
        "display_name": "Qwen3-VL-30B",
        "backend": "llama-swap",
        "port": 8080,
        "max_tokens": 4096,
        "size_gb": 18.0,
        "capabilities": ["ocr", "grounding", "reasoning"],
    },
    "qwen3-vl-30b": {
        "model_id": "local/vision/qwen3-vl",
        "display_name": "Qwen3-VL-30B",
        "backend": "llama-swap",
        "port": 8080,
        "max_tokens": 4096,
        "size_gb": 18.0,
        "capabilities": ["ocr", "grounding", "reasoning"],
    },
    "glm-4.6v-flash": {
        "model_id": "local/vision/glm-4.6v-flash",
        "display_name": "GLM-4.6V-Flash",
        "backend": "llama-swap",
        "port": 8080,
        "max_tokens": 8192,
        "size_gb": 6.0,
        "capabilities": ["ocr", "function_calling", "128k_context"],
    },
    "gemma-3-27b": {
        "model_id": "local/vision/gemma-27b",
        "display_name": "Gemma-3-27B-IT",
        "backend": "llama-swap",
        "port": 8080,
        "max_tokens": 4096,
        "size_gb": 16.0,
        "capabilities": ["ocr", "general", "instruction_following"],
    },
    "olmocr-7b": {
        "model_id": "local/ocr/olmocr2-7b",
        "display_name": "OlmOCR-2-7B",
        "backend": "mlx-omni-server",
        "port": 10240,
        "max_tokens": 4096,
        "size_gb": 4.0,
        "capabilities": ["dense_ocr", "tables", "latex"],
    },
    "granite-docling": {
        "model_id": "local/document/granite-docling",
        "display_name": "Granite-Docling-258M",
        "backend": "mlx-omni-server",
        "port": 10240,
        "max_tokens": 2048,
        "size_gb": 0.5,
        "capabilities": ["layout", "tables", "structure"],
    },
    "moondream2": {
        "model_id": "local/vision/moondream2",
        "display_name": "Moondream2",
        "backend": "llama-swap",
        "port": 8080,
        "max_tokens": 2048,
        "size_gb": 1.5,
        "capabilities": ["ocr", "lightweight"],
    },
}


# Default prompts for different tasks
OCR_PROMPTS = {
    "default": "Extract all text from this document image. Preserve the original layout and formatting.",
    "structured": "Extract all text from this document. Output in markdown format preserving structure, headings, lists, and tables.",
    "tables_only": "Extract all tables from this document. Output each table in markdown format.",
    "irish": "Extract all text from this document. This may contain Irish (Gaeilge) text - preserve all fadas (á, é, í, ó, ú) accurately.",
    "math": "Extract all text from this document including mathematical formulas. Use LaTeX notation for equations.",
}


# ============================================================================
# Data Classes
# ============================================================================


@dataclass
class VisionResult:
    """Result from a vision model comparison."""

    text: str
    model_id: str
    model_name: str
    elapsed_seconds: float
    tokens_used: int = 0
    prompt_tokens: int = 0
    completion_tokens: int = 0
    status: str = "success"
    error: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "text": self.text,
            "model_id": self.model_id,
            "model_name": self.model_name,
            "elapsed_seconds": self.elapsed_seconds,
            "tokens_used": self.tokens_used,
            "status": self.status,
            "error": self.error,
        }


# ============================================================================
# Vision Model Client
# ============================================================================


class VisionModelClient:
    """
    Client for vision model inference via LiteLLM.

    Uses the LiteLLM gateway for unified access to all vision models.
    """

    def __init__(
        self,
        litellm_url: str | None = None,
        api_key: str | None = None,
        timeout: float = 120.0,
    ):
        self.litellm_url = litellm_url or os.getenv("LITELLM_BASE_URL", "http://localhost:4000")
        self.api_key = api_key or os.getenv("LITELLM_API_KEY", "sk-1234")
        self.timeout = timeout
        self._client: httpx.AsyncClient | None = None

    async def _get_client(self) -> httpx.AsyncClient:
        if self._client is None:
            self._client = httpx.AsyncClient(timeout=self.timeout)
        return self._client

    async def close(self) -> None:
        if self._client is not None:
            await self._client.aclose()
            self._client = None

    async def run_inference(
        self,
        model_key: str,
        image: bytes,
        prompt: str,
        temperature: float = 0.1,
    ) -> VisionResult:
        """
        Run inference on a single vision model.

        Args:
            model_key: Key from VISION_MODELS dict
            image: Image bytes
            prompt: Text prompt for the model
            temperature: Generation temperature

        Returns:
            VisionResult with extracted text
        """
        start_time = time.time()

        if model_key not in VISION_MODELS:
            return VisionResult(
                text="",
                model_id=model_key,
                model_name=model_key,
                elapsed_seconds=0.0,
                status="error",
                error=f"Unknown model: {model_key}. Available: {list(VISION_MODELS.keys())}",
            )

        model_config = VISION_MODELS[model_key]
        model_id = model_config["model_id"]
        model_name = model_config["display_name"]

        try:
            image_b64 = base64.b64encode(image).decode("utf-8")
            client = await self._get_client()

            # LiteLLM OpenAI-compatible API
            response = await client.post(
                f"{self.litellm_url}/v1/chat/completions",
                headers={"Authorization": f"Bearer {self.api_key}"},
                json={
                    "model": model_id,
                    "messages": [
                        {
                            "role": "user",
                            "content": [
                                {"type": "text", "text": prompt},
                                {
                                    "type": "image_url",
                                    "image_url": {"url": f"data:image/png;base64,{image_b64}"},
                                },
                            ],
                        }
                    ],
                    "max_tokens": model_config.get("max_tokens", 4096),
                    "temperature": temperature,
                },
            )
            response.raise_for_status()
            result = response.json()

            text = result["choices"][0]["message"]["content"]
            usage = result.get("usage", {})

            return VisionResult(
                text=text,
                model_id=model_id,
                model_name=model_name,
                elapsed_seconds=time.time() - start_time,
                tokens_used=usage.get("total_tokens", 0),
                prompt_tokens=usage.get("prompt_tokens", 0),
                completion_tokens=usage.get("completion_tokens", 0),
                metadata={
                    "backend": model_config["backend"],
                    "capabilities": model_config.get("capabilities", []),
                },
            )

        except httpx.TimeoutException:
            return VisionResult(
                text="",
                model_id=model_id,
                model_name=model_name,
                elapsed_seconds=time.time() - start_time,
                status="error",
                error="Request timed out",
            )
        except Exception as e:
            return VisionResult(
                text="",
                model_id=model_id,
                model_name=model_name,
                elapsed_seconds=time.time() - start_time,
                status="error",
                error=str(e),
            )


# ============================================================================
# Comparison Functions
# ============================================================================


async def compare_vision_models(
    image: bytes | Path,
    models: list[str] | None = None,
    prompt: str | None = None,
    prompt_key: str = "default",
    litellm_url: str | None = None,
    parallel: bool = True,
) -> dict[str, VisionResult]:
    """
    Compare vision models on the same image.

    Args:
        image: Image bytes or path
        models: List of model keys (defaults to qwen3-vl, glm-4.6v-flash, moondream2)
        prompt: Custom prompt (overrides prompt_key)
        prompt_key: Key from OCR_PROMPTS for predefined prompts
        litellm_url: LiteLLM gateway URL
        parallel: Run models in parallel (True) or sequential (False)

    Returns:
        Dictionary mapping model key to VisionResult
    """
    # Default models for comparison
    models = models or ["qwen3-vl", "glm-4.6v-flash", "moondream2"]

    # Get prompt
    prompt = prompt or OCR_PROMPTS.get(prompt_key, OCR_PROMPTS["default"])

    # Load image if path
    if isinstance(image, Path):
        with open(image, "rb") as f:
            image_bytes = f.read()
    else:
        image_bytes = image

    client = VisionModelClient(litellm_url=litellm_url)
    results: dict[str, VisionResult] = {}

    try:
        if parallel:
            # Run all models in parallel
            tasks = [
                client.run_inference(model_key, image_bytes, prompt)
                for model_key in models
            ]
            model_results = await asyncio.gather(*tasks, return_exceptions=True)

            for model_key, result in zip(models, model_results):
                if isinstance(result, Exception):
                    results[model_key] = VisionResult(
                        text="",
                        model_id=model_key,
                        model_name=VISION_MODELS.get(model_key, {}).get("display_name", model_key),
                        elapsed_seconds=0.0,
                        status="error",
                        error=str(result),
                    )
                else:
                    results[model_key] = result
        else:
            # Run models sequentially
            for model_key in models:
                result = await client.run_inference(model_key, image_bytes, prompt)
                results[model_key] = result

    finally:
        await client.close()

    return results


async def compare_vision_models_batch(
    images: list[bytes | Path],
    models: list[str] | None = None,
    prompt: str | None = None,
    prompt_key: str = "default",
    litellm_url: str | None = None,
) -> list[dict[str, VisionResult]]:
    """
    Compare vision models on multiple images.

    Args:
        images: List of image bytes or paths
        models: List of model keys
        prompt: Custom prompt
        prompt_key: Key from OCR_PROMPTS
        litellm_url: LiteLLM gateway URL

    Returns:
        List of result dictionaries, one per image
    """
    tasks = [
        compare_vision_models(img, models, prompt, prompt_key, litellm_url)
        for img in images
    ]
    return await asyncio.gather(*tasks)


def list_vision_models() -> list[dict[str, Any]]:
    """List all available vision models with their configurations."""
    return [
        {
            "key": key,
            "model_id": config["model_id"],
            "display_name": config["display_name"],
            "backend": config["backend"],
            "size_gb": config["size_gb"],
            "capabilities": config.get("capabilities", []),
        }
        for key, config in VISION_MODELS.items()
    ]


def get_model_config(model_key: str) -> dict[str, Any] | None:
    """Get configuration for a specific model."""
    return VISION_MODELS.get(model_key)


# ============================================================================
# Synchronous Wrappers
# ============================================================================


def compare_vision_models_sync(
    image: bytes | Path,
    models: list[str] | None = None,
    prompt: str | None = None,
    prompt_key: str = "default",
) -> dict[str, VisionResult]:
    """
    Synchronous wrapper for compare_vision_models.

    For use in non-async contexts (e.g., Marimo notebooks).
    """
    return asyncio.run(
        compare_vision_models(image, models, prompt, prompt_key)
    )
