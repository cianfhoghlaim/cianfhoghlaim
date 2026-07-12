"""Z.AI GLM-4.6v backend for visual grounding and vision analysis."""

import base64
import re
import time
from pathlib import Path
from typing import Any

import httpx
import structlog

from ...config import BrowserConfig, get_config
from ...exceptions import BackendError, BackendTimeoutError
from ...browser_types import (
    BackendType,
    ExtractionFormat,
    ExtractionResult,
    InteractionResult,
    NavigationResult,
    ScreenshotResult,
    VisionAnalysisResult,
    VisualGroundingResult,
)
from ..base import BrowserBackend

logger = structlog.get_logger()


class ZAIVisionBackend(BrowserBackend):
    """Z.AI GLM-4.6v backend for visual grounding and vision analysis.

    GLM-4.6v provides:
    - Visual grounding (returns bounding box coordinates)
    - Native multimodal tool calling
    - 128K context window
    - Multi-image relational reasoning
    - Frontend replication & visual debugging
    """

    backend_type = BackendType.ZAI_VISION

    def __init__(self, config: BrowserConfig | None = None):
        self.config = config or get_config()
        self._client: httpx.AsyncClient | None = None

    async def initialize(self) -> None:
        """Initialize Z.AI client."""
        if not self.config.zai_api_key:
            raise BackendError(
                "Z.AI API key not configured",
                self.backend_type,
                retryable=False,
            )

        self._client = httpx.AsyncClient(
            base_url=self.config.zai_base_url,
            headers={
                "Authorization": f"Bearer {self.config.zai_api_key}",
                "Content-Type": "application/json",
            },
            timeout=httpx.Timeout(60.0),
        )
        logger.info("zai_vision_initialized", mode=self.config.zai_mode)

    async def close(self) -> None:
        """Close Z.AI client."""
        if self._client:
            await self._client.aclose()
            self._client = None

    async def health_check(self) -> bool:
        """Check Z.AI API connectivity."""
        try:
            if not self._client:
                return False
            response = await self._client.get("/models")
            return response.status_code == 200
        except Exception:
            return False

    def _encode_image(self, image_source: str) -> str:
        """Encode image to base64 from path or URL."""
        if image_source.startswith(("http://", "https://")):
            return image_source

        path = Path(image_source)
        if path.exists():
            with open(path, "rb") as f:
                image_data = base64.b64encode(f.read()).decode()
                suffix = path.suffix.lower()
                mime_type = {
                    ".png": "image/png",
                    ".jpg": "image/jpeg",
                    ".jpeg": "image/jpeg",
                    ".gif": "image/gif",
                    ".webp": "image/webp",
                }.get(suffix, "image/png")
                return f"data:{mime_type};base64,{image_data}"

        return image_source

    async def visual_grounding(
        self,
        image_source: str,
        prompt: str,
        *,
        timeout: float | None = None,
    ) -> VisualGroundingResult:
        """Find element coordinates in an image using GLM-4.6v.

        Visual grounding returns bounding box coordinates [xmin, ymin, xmax, ymax]
        where coordinates are normalized to 0-1000 range.

        Args:
            image_source: Path to image file, URL, or base64 data
            prompt: Description of element to find, e.g., "Find the login button"

        Returns:
            VisualGroundingResult with coordinates or bounding_box
        """
        if not self._client:
            raise BackendError("Z.AI not initialized", self.backend_type)

        start_time = time.perf_counter()

        try:
            image_content = self._encode_image(image_source)

            payload = {
                "model": self.config.zai_glm_model,
                "messages": [
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "image_url",
                                "image_url": {"url": image_content},
                            },
                            {
                                "type": "text",
                                "text": f"<|grounding|>{prompt}",
                            },
                        ],
                    }
                ],
                "max_tokens": 256,
            }

            response = await self._client.post(
                "/chat/completions",
                json=payload,
                timeout=timeout or 30.0,
            )
            response.raise_for_status()
            data = response.json()

            latency_ms = (time.perf_counter() - start_time) * 1000

            content = data["choices"][0]["message"]["content"]
            tokens_used = data.get("usage", {}).get("total_tokens")

            bbox = self._parse_bounding_box(content)
            if bbox:
                center_x = (bbox[0] + bbox[2]) / 2 / 1000
                center_y = (bbox[1] + bbox[3]) / 2 / 1000

                return VisualGroundingResult(
                    success=True,
                    prompt=prompt,
                    coordinates={"x": center_x, "y": center_y},
                    bounding_box=bbox,
                    backend_used=self.backend_type,
                    latency_ms=latency_ms,
                    tokens_used=tokens_used,
                )
            else:
                return VisualGroundingResult(
                    success=False,
                    prompt=prompt,
                    backend_used=self.backend_type,
                    latency_ms=latency_ms,
                    tokens_used=tokens_used,
                    error=f"Could not parse coordinates from response: {content[:200]}",
                )

        except httpx.TimeoutException as e:
            raise BackendTimeoutError(
                self.backend_type,
                timeout or 30.0,
            ) from e

        except Exception as e:
            latency_ms = (time.perf_counter() - start_time) * 1000
            return VisualGroundingResult(
                success=False,
                prompt=prompt,
                backend_used=self.backend_type,
                latency_ms=latency_ms,
                error=str(e),
            )

    def _parse_bounding_box(self, content: str) -> list[float] | None:
        """Parse bounding box from GLM-4.6v response.

        GLM-4.6v returns coordinates in format: [[xmin, ymin, xmax, ymax]]
        Coordinates are normalized to 0-1000 range.
        """
        patterns = [
            r"\[\[(\d+),\s*(\d+),\s*(\d+),\s*(\d+)\]\]",
            r"\[(\d+),\s*(\d+),\s*(\d+),\s*(\d+)\]",
            r"(\d+)\s*,\s*(\d+)\s*,\s*(\d+)\s*,\s*(\d+)",
        ]

        for pattern in patterns:
            match = re.search(pattern, content)
            if match:
                return [float(match.group(i)) for i in range(1, 5)]

        return None

    async def analyze_vision(
        self,
        image_source: str,
        prompt: str,
        analysis_type: str = "general",
        *,
        timeout: float | None = None,
    ) -> VisionAnalysisResult:
        """Analyze an image using GLM-4.6v.

        Supports various analysis types:
        - general: General image understanding
        - ui_to_artifact: Convert UI screenshot to code/specs
        - ocr: Extract text from image
        - error_diagnosis: Analyze error screenshots
        - diagram: Understand technical diagrams
        - chart: Analyze data visualizations
        """
        if not self._client:
            raise BackendError("Z.AI not initialized", self.backend_type)

        start_time = time.perf_counter()

        try:
            image_content = self._encode_image(image_source)

            system_prompts = {
                "general": "You are a helpful vision assistant. Analyze the image and respond to the user's request.",
                "ui_to_artifact": "You are a UI/UX expert. Analyze this UI screenshot and generate the requested artifact (code, prompt, spec, or description).",
                "ocr": "You are an OCR specialist. Extract all text from this image, preserving formatting where possible.",
                "error_diagnosis": "You are a debugging expert. Analyze this error screenshot and provide diagnosis with actionable solutions.",
                "diagram": "You are a technical architect. Analyze this diagram and explain its structure, components, and relationships.",
                "chart": "You are a data analyst. Analyze this visualization and extract key insights, trends, and metrics.",
            }

            payload = {
                "model": self.config.zai_glm_model,
                "messages": [
                    {
                        "role": "system",
                        "content": system_prompts.get(analysis_type, system_prompts["general"]),
                    },
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "image_url",
                                "image_url": {"url": image_content},
                            },
                            {
                                "type": "text",
                                "text": prompt,
                            },
                        ],
                    },
                ],
                "max_tokens": 4096,
            }

            response = await self._client.post(
                "/chat/completions",
                json=payload,
                timeout=timeout or 60.0,
            )
            response.raise_for_status()
            data = response.json()

            latency_ms = (time.perf_counter() - start_time) * 1000
            content_text = data["choices"][0]["message"]["content"]
            tokens_used = data.get("usage", {}).get("total_tokens")

            return VisionAnalysisResult(
                success=True,
                image_source=image_source,
                analysis_type=analysis_type,
                content={"text": content_text, "raw_response": data},
                backend_used=self.backend_type,
                latency_ms=latency_ms,
                tokens_used=tokens_used,
            )

        except httpx.TimeoutException as e:
            raise BackendTimeoutError(
                self.backend_type,
                timeout or 60.0,
            ) from e

        except Exception as e:
            latency_ms = (time.perf_counter() - start_time) * 1000
            return VisionAnalysisResult(
                success=False,
                image_source=image_source,
                analysis_type=analysis_type,
                content={},
                backend_used=self.backend_type,
                latency_ms=latency_ms,
                error=str(e),
            )

    async def compare_images(
        self,
        expected_image: str,
        actual_image: str,
        prompt: str | None = None,
        *,
        timeout: float | None = None,
    ) -> VisionAnalysisResult:
        """Compare two images (e.g., expected vs actual UI).

        Useful for UI diff checking and visual regression testing.
        """
        if not self._client:
            raise BackendError("Z.AI not initialized", self.backend_type)

        start_time = time.perf_counter()

        try:
            expected_content = self._encode_image(expected_image)
            actual_content = self._encode_image(actual_image)

            comparison_prompt = prompt or (
                "Compare these two UI screenshots. The first image is the expected design, "
                "the second is the actual implementation. Identify all visual differences "
                "including: layout, colors, typography, spacing, missing/extra elements, "
                "and alignment issues. Provide a detailed report."
            )

            payload = {
                "model": self.config.zai_glm_model,
                "messages": [
                    {
                        "role": "system",
                        "content": "You are a UI QA specialist comparing expected designs with actual implementations.",
                    },
                    {
                        "role": "user",
                        "content": [
                            {
                                "type": "text",
                                "text": "Expected design:",
                            },
                            {
                                "type": "image_url",
                                "image_url": {"url": expected_content},
                            },
                            {
                                "type": "text",
                                "text": "Actual implementation:",
                            },
                            {
                                "type": "image_url",
                                "image_url": {"url": actual_content},
                            },
                            {
                                "type": "text",
                                "text": comparison_prompt,
                            },
                        ],
                    },
                ],
                "max_tokens": 4096,
            }

            response = await self._client.post(
                "/chat/completions",
                json=payload,
                timeout=timeout or 90.0,
            )
            response.raise_for_status()
            data = response.json()

            latency_ms = (time.perf_counter() - start_time) * 1000
            content_text = data["choices"][0]["message"]["content"]
            tokens_used = data.get("usage", {}).get("total_tokens")

            return VisionAnalysisResult(
                success=True,
                image_source=f"{expected_image} vs {actual_image}",
                analysis_type="ui_diff",
                content={
                    "text": content_text,
                    "expected": expected_image,
                    "actual": actual_image,
                },
                backend_used=self.backend_type,
                latency_ms=latency_ms,
                tokens_used=tokens_used,
            )

        except Exception as e:
            latency_ms = (time.perf_counter() - start_time) * 1000
            return VisionAnalysisResult(
                success=False,
                image_source=f"{expected_image} vs {actual_image}",
                analysis_type="ui_diff",
                content={},
                backend_used=self.backend_type,
                latency_ms=latency_ms,
                error=str(e),
            )

    async def navigate(
        self,
        url: str,
        *,
        wait_until: str = "load",
        timeout: float | None = None,
    ) -> NavigationResult:
        """Z.AI doesn't support navigation. Use other backends."""
        raise BackendError(
            "Z.AI Vision is for image analysis, not navigation. Use CDP or Browserbase.",
            self.backend_type,
            retryable=False,
        )

    async def extract(
        self,
        url: str,
        *,
        formats: list[ExtractionFormat] | None = None,
        schema: dict[str, Any] | None = None,
        prompt: str | None = None,
        timeout: float | None = None,
    ) -> ExtractionResult:
        """Z.AI doesn't support web extraction. Use for image analysis only."""
        raise BackendError(
            "Z.AI Vision is for image analysis, not web extraction. Use Crawl4AI or Firecrawl.",
            self.backend_type,
            retryable=False,
        )

    async def interact(
        self,
        action: str,
        *,
        selector: str | None = None,
        value: str | None = None,
        timeout: float | None = None,
    ) -> InteractionResult:
        """Z.AI doesn't support interaction. Use other backends."""
        raise BackendError(
            "Z.AI Vision is for image analysis, not interaction. Use CDP or Stagehand.",
            self.backend_type,
            retryable=False,
        )

    async def screenshot(
        self,
        *,
        url: str | None = None,
        full_page: bool = False,
        selector: str | None = None,
        timeout: float | None = None,
    ) -> ScreenshotResult:
        """Z.AI doesn't capture screenshots. Use other backends."""
        raise BackendError(
            "Z.AI Vision is for image analysis, not screenshot capture. Use CDP or Browserbase.",
            self.backend_type,
            retryable=False,
        )
