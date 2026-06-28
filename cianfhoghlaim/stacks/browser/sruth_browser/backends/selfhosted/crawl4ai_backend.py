"""Crawl4AI backend for bulk extraction with LLM strategies."""

import time
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
)
from ..base import BrowserBackend

logger = structlog.get_logger()


class Crawl4AIBackend(BrowserBackend):
    """Crawl4AI API backend for high-throughput extraction."""

    backend_type = BackendType.CRAWL4AI_LOCAL

    def __init__(self, config: BrowserConfig | None = None):
        self.config = config or get_config()
        self._client: httpx.AsyncClient | None = None

    async def initialize(self) -> None:
        """Initialize HTTP client for Crawl4AI API."""
        self._client = httpx.AsyncClient(
            base_url=self.config.crawl4ai_url,
            timeout=httpx.Timeout(self.config.extraction_timeout),
        )
        logger.info("crawl4ai_initialized", url=self.config.crawl4ai_url)

    async def close(self) -> None:
        """Close HTTP client."""
        if self._client:
            await self._client.aclose()
            self._client = None

    async def health_check(self) -> bool:
        """Check Crawl4AI health endpoint."""
        try:
            if not self._client:
                return False
            response = await self._client.get("/health")
            return response.status_code == 200
        except Exception:
            return False

    async def navigate(
        self,
        url: str,
        *,
        wait_until: str = "load",
        timeout: float | None = None,
    ) -> NavigationResult:
        """Crawl4AI doesn't support stateful navigation. Use extract instead."""
        raise BackendError(
            "Crawl4AI is stateless. Use extract() for page content.",
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
        """Extract content using Crawl4AI.

        Supports:
        - Markdown/HTML extraction
        - LLM-based structured extraction with schema
        - Magic mode for anti-bot bypass
        """
        if not self._client:
            raise BackendError("Crawl4AI not initialized", self.backend_type)

        formats = formats or [ExtractionFormat.MARKDOWN]
        start_time = time.perf_counter()

        try:
            # Build request payload
            payload: dict[str, Any] = {
                "url": url,
                "magic": True,  # Enable anti-detection
                "bypass_cache": False,
            }

            # Configure extraction strategy
            if schema:
                payload["extraction_config"] = {
                    "type": "json",
                    "schema": schema,
                    "prompt": prompt or "Extract structured data according to the schema.",
                }
            elif prompt:
                payload["extraction_config"] = {
                    "type": "llm",
                    "prompt": prompt,
                }

            # Set output formats
            output_formats = []
            for fmt in formats:
                if fmt == ExtractionFormat.MARKDOWN:
                    output_formats.append("markdown")
                elif fmt == ExtractionFormat.HTML:
                    output_formats.append("html")
                elif fmt == ExtractionFormat.RAW_HTML:
                    output_formats.append("rawHtml")
                elif fmt == ExtractionFormat.SCREENSHOT:
                    output_formats.append("screenshot")
                elif fmt == ExtractionFormat.LINKS:
                    output_formats.append("links")

            if output_formats:
                payload["output_formats"] = output_formats

            response = await self._client.post(
                "/crawl",
                json=payload,
                timeout=timeout or self.config.extraction_timeout,
            )
            response.raise_for_status()
            data = response.json()

            latency_ms = (time.perf_counter() - start_time) * 1000

            # Parse response
            content: dict[str, Any] = {}
            if "markdown" in data:
                content["markdown"] = data["markdown"]
            if "html" in data:
                content["html"] = data["html"]
            if "rawHtml" in data:
                content["rawHtml"] = data["rawHtml"]
            if "links" in data:
                content["links"] = data["links"]
            if "screenshot" in data:
                content["screenshot"] = data["screenshot"]
            if "extracted_content" in data:
                content["extracted"] = data["extracted_content"]

            return ExtractionResult(
                success=True,
                url=url,
                content=content,
                format=formats[0],
                backend_used=self.backend_type,
                latency_ms=latency_ms,
                metadata=data.get("metadata", {}),
            )

        except httpx.TimeoutException as e:
            raise BackendTimeoutError(
                self.backend_type,
                timeout or self.config.extraction_timeout,
            ) from e

        except httpx.HTTPStatusError as e:
            latency_ms = (time.perf_counter() - start_time) * 1000
            return ExtractionResult(
                success=False,
                url=url,
                content={},
                format=formats[0] if formats else ExtractionFormat.MARKDOWN,
                backend_used=self.backend_type,
                latency_ms=latency_ms,
                error=f"HTTP {e.response.status_code}: {e.response.text[:200]}",
            )

        except Exception as e:
            latency_ms = (time.perf_counter() - start_time) * 1000
            return ExtractionResult(
                success=False,
                url=url,
                content={},
                format=formats[0] if formats else ExtractionFormat.MARKDOWN,
                backend_used=self.backend_type,
                latency_ms=latency_ms,
                error=str(e),
            )

    async def interact(
        self,
        action: str,
        *,
        selector: str | None = None,
        value: str | None = None,
        timeout: float | None = None,
    ) -> InteractionResult:
        """Crawl4AI doesn't support interactive operations."""
        raise BackendError(
            "Crawl4AI doesn't support interactions. Use CDP or Stagehand.",
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
        """Capture screenshot via Crawl4AI extraction."""
        if not url:
            raise BackendError(
                "URL required for Crawl4AI screenshot",
                self.backend_type,
                retryable=False,
            )

        result = await self.extract(
            url,
            formats=[ExtractionFormat.SCREENSHOT],
            timeout=timeout,
        )

        if not result.success or "screenshot" not in result.content:
            return ScreenshotResult(
                success=False,
                url=url,
                image_data="",
                width=0,
                height=0,
                backend_used=self.backend_type,
                latency_ms=result.latency_ms,
                error=result.error or "No screenshot in response",
            )

        return ScreenshotResult(
            success=True,
            url=url,
            image_data=result.content["screenshot"],
            format="png",
            width=1920,  # Default viewport
            height=1080,
            backend_used=self.backend_type,
            latency_ms=result.latency_ms,
        )

    async def batch_extract(
        self,
        urls: list[str],
        *,
        formats: list[ExtractionFormat] | None = None,
        schema: dict[str, Any] | None = None,
        prompt: str | None = None,
        max_concurrent: int = 4,
    ) -> list[ExtractionResult]:
        """Extract from multiple URLs concurrently.

        Leverages Crawl4AI's parallel crawling capability.
        """
        if not self._client:
            raise BackendError("Crawl4AI not initialized", self.backend_type)

        formats = formats or [ExtractionFormat.MARKDOWN]
        start_time = time.perf_counter()

        try:
            # Build batch request
            payload: dict[str, Any] = {
                "urls": urls,
                "magic": True,
                "max_concurrent": max_concurrent,
            }

            if schema:
                payload["extraction_config"] = {
                    "type": "json",
                    "schema": schema,
                    "prompt": prompt,
                }

            response = await self._client.post(
                "/crawl/batch",
                json=payload,
                timeout=self.config.extraction_timeout * len(urls) / max_concurrent,
            )
            response.raise_for_status()
            data = response.json()

            latency_ms = (time.perf_counter() - start_time) * 1000

            results = []
            for item in data.get("results", []):
                results.append(
                    ExtractionResult(
                        success=item.get("success", False),
                        url=item.get("url", ""),
                        content=item.get("content", {}),
                        format=formats[0],
                        backend_used=self.backend_type,
                        latency_ms=latency_ms / len(urls),
                        error=item.get("error"),
                    )
                )

            return results

        except Exception as e:
            latency_ms = (time.perf_counter() - start_time) * 1000
            return [
                ExtractionResult(
                    success=False,
                    url=url,
                    content={},
                    format=formats[0] if formats else ExtractionFormat.MARKDOWN,
                    backend_used=self.backend_type,
                    latency_ms=latency_ms,
                    error=str(e),
                )
                for url in urls
            ]
