"""Firecrawl MCP backend for web scraping and research."""

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
    ResearchResult,
    ScreenshotResult,
)
from ..base import ResearchCapableBackend

logger = structlog.get_logger()


class FirecrawlBackend(ResearchCapableBackend):
    """Firecrawl API backend for web scraping and deep research.

    Firecrawl provides:
    - High-quality markdown conversion
    - Structured data extraction with schemas
    - Autonomous research agent (/agent endpoint)
    - Anti-bot handling
    """

    backend_type = BackendType.FIRECRAWL_MCP

    def __init__(self, config: BrowserConfig | None = None):
        self.config = config or get_config()
        self._client: httpx.AsyncClient | None = None

    async def initialize(self) -> None:
        """Initialize Firecrawl client."""
        if not self.config.firecrawl_api_key:
            raise BackendError(
                "Firecrawl API key not configured",
                self.backend_type,
                retryable=False,
            )

        self._client = httpx.AsyncClient(
            base_url="https://api.firecrawl.dev/v1",
            headers={
                "Authorization": f"Bearer {self.config.firecrawl_api_key}",
                "Content-Type": "application/json",
            },
            timeout=httpx.Timeout(self.config.extraction_timeout * 2),
        )
        logger.info("firecrawl_initialized")

    async def close(self) -> None:
        """Close Firecrawl client."""
        if self._client:
            await self._client.aclose()
            self._client = None

    async def health_check(self) -> bool:
        """Check Firecrawl API connectivity."""
        try:
            if not self._client:
                return False
            # Simple scrape test
            response = await self._client.post(
                "/scrape",
                json={"url": "https://example.com", "formats": ["markdown"]},
            )
            return response.status_code in (200, 201)
        except Exception:
            return False

    async def navigate(
        self,
        url: str,
        *,
        wait_until: str = "load",
        timeout: float | None = None,
    ) -> NavigationResult:
        """Firecrawl doesn't support stateful navigation. Use extract instead."""
        raise BackendError(
            "Firecrawl is stateless. Use extract() for page content.",
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
        """Extract content using Firecrawl /scrape endpoint.

        Supports:
        - markdown, html, rawHtml, screenshot, links, summary
        - Structured JSON extraction with schema
        """
        if not self._client:
            raise BackendError("Firecrawl not initialized", self.backend_type)

        formats = formats or [ExtractionFormat.MARKDOWN]
        start_time = time.perf_counter()

        try:
            # Build payload
            payload: dict[str, Any] = {"url": url}

            # Map formats
            fc_formats = []
            for fmt in formats:
                if fmt == ExtractionFormat.MARKDOWN:
                    fc_formats.append("markdown")
                elif fmt == ExtractionFormat.HTML:
                    fc_formats.append("html")
                elif fmt == ExtractionFormat.RAW_HTML:
                    fc_formats.append("rawHtml")
                elif fmt == ExtractionFormat.SCREENSHOT:
                    fc_formats.append("screenshot")
                elif fmt == ExtractionFormat.LINKS:
                    fc_formats.append("links")
                elif fmt == ExtractionFormat.SUMMARY:
                    fc_formats.append("summary")
                elif fmt == ExtractionFormat.JSON and schema:
                    # Add JSON format with schema
                    fc_formats.append({
                        "type": "json",
                        "schema": schema,
                        "prompt": prompt,
                    })

            payload["formats"] = fc_formats if fc_formats else ["markdown"]

            response = await self._client.post(
                "/scrape",
                json=payload,
                timeout=timeout or self.config.extraction_timeout,
            )
            response.raise_for_status()
            data = response.json()

            latency_ms = (time.perf_counter() - start_time) * 1000

            # Parse response
            content: dict[str, Any] = {}
            result_data = data.get("data", {})

            if "markdown" in result_data:
                content["markdown"] = result_data["markdown"]
            if "html" in result_data:
                content["html"] = result_data["html"]
            if "rawHtml" in result_data:
                content["rawHtml"] = result_data["rawHtml"]
            if "screenshot" in result_data:
                content["screenshot"] = result_data["screenshot"]
            if "links" in result_data:
                content["links"] = result_data["links"]
            if "summary" in result_data:
                content["summary"] = result_data["summary"]
            if "json" in result_data:
                content["extracted"] = result_data["json"]

            return ExtractionResult(
                success=True,
                url=url,
                content=content,
                format=formats[0],
                backend_used=self.backend_type,
                latency_ms=latency_ms,
                metadata=result_data.get("metadata", {}),
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
        """Firecrawl doesn't support interactive operations."""
        raise BackendError(
            "Firecrawl doesn't support interactions. Use Browserbase or CDP.",
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
        """Capture screenshot via Firecrawl."""
        if not url:
            raise BackendError(
                "URL required for Firecrawl screenshot",
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
            width=1920,
            height=1080,
            backend_used=self.backend_type,
            latency_ms=result.latency_ms,
        )

    async def research(
        self,
        query: str,
        *,
        max_urls: int = 15,
        schema: dict[str, Any] | None = None,
        timeout: float | None = None,
    ) -> dict[str, Any]:
        """Perform autonomous research using Firecrawl /agent endpoint.

        The agent will:
        1. Search the web for relevant pages
        2. Navigate and extract content
        3. Synthesize findings
        """
        if not self._client:
            raise BackendError("Firecrawl not initialized", self.backend_type)

        start_time = time.perf_counter()

        try:
            payload: dict[str, Any] = {
                "prompt": query,
            }

            if schema:
                payload["schema"] = schema

            response = await self._client.post(
                "/agent",
                json=payload,
                timeout=timeout or self.config.extraction_timeout * 3,
            )
            response.raise_for_status()
            data = response.json()

            # Check if we got an async job ID
            if "id" in data and data.get("status") == "processing":
                # Poll for completion
                job_id = data["id"]
                import asyncio

                while True:
                    await asyncio.sleep(2)
                    status_response = await self._client.get(f"/agent/{job_id}")
                    status_data = status_response.json()

                    if status_data.get("status") in ("completed", "failed"):
                        data = status_data
                        break

            latency_ms = (time.perf_counter() - start_time) * 1000

            if data.get("status") == "completed":
                return {
                    "success": True,
                    "query": query,
                    "content": data.get("data", {}).get("content", ""),
                    "sources": data.get("data", {}).get("sources", []),
                    "urls_visited": len(data.get("data", {}).get("sources", [])),
                    "backend_used": self.backend_type.value,
                    "latency_ms": latency_ms,
                    "credits_used": data.get("creditsUsed"),
                }
            else:
                return {
                    "success": False,
                    "query": query,
                    "content": "",
                    "sources": [],
                    "backend_used": self.backend_type.value,
                    "latency_ms": latency_ms,
                    "error": data.get("error", "Agent task failed"),
                }

        except httpx.TimeoutException as e:
            raise BackendTimeoutError(
                self.backend_type,
                timeout or self.config.extraction_timeout * 3,
            ) from e

        except Exception as e:
            latency_ms = (time.perf_counter() - start_time) * 1000
            return {
                "success": False,
                "query": query,
                "content": "",
                "sources": [],
                "backend_used": self.backend_type.value,
                "latency_ms": latency_ms,
                "error": str(e),
            }

    async def map_site(
        self,
        url: str,
        *,
        search: str | None = None,
        limit: int = 100,
    ) -> list[str]:
        """Map all URLs on a website using Firecrawl /map endpoint."""
        if not self._client:
            raise BackendError("Firecrawl not initialized", self.backend_type)

        try:
            payload: dict[str, Any] = {
                "url": url,
                "limit": limit,
            }

            if search:
                payload["search"] = search

            response = await self._client.post("/map", json=payload)
            response.raise_for_status()
            data = response.json()

            return data.get("links", [])

        except Exception as e:
            logger.warning("firecrawl_map_failed", error=str(e))
            return []

    async def batch_scrape(
        self,
        urls: list[str],
        *,
        formats: list[ExtractionFormat] | None = None,
    ) -> list[ExtractionResult]:
        """Batch scrape multiple URLs using Firecrawl /batch/scrape endpoint."""
        if not self._client:
            raise BackendError("Firecrawl not initialized", self.backend_type)

        formats = formats or [ExtractionFormat.MARKDOWN]
        start_time = time.perf_counter()

        try:
            # Map formats
            fc_formats = []
            for fmt in formats:
                if fmt == ExtractionFormat.MARKDOWN:
                    fc_formats.append("markdown")
                elif fmt == ExtractionFormat.HTML:
                    fc_formats.append("html")
                elif fmt == ExtractionFormat.LINKS:
                    fc_formats.append("links")

            payload = {
                "urls": urls,
                "formats": fc_formats if fc_formats else ["markdown"],
            }

            response = await self._client.post(
                "/batch/scrape",
                json=payload,
                timeout=self.config.extraction_timeout * 2,
            )
            response.raise_for_status()
            data = response.json()

            # Check for async job
            if "id" in data:
                job_id = data["id"]
                import asyncio

                while True:
                    await asyncio.sleep(2)
                    status_response = await self._client.get(f"/batch/scrape/{job_id}")
                    status_data = status_response.json()

                    if status_data.get("status") in ("completed", "failed"):
                        data = status_data
                        break

            latency_ms = (time.perf_counter() - start_time) * 1000

            results = []
            for item in data.get("data", []):
                results.append(
                    ExtractionResult(
                        success=item.get("success", True),
                        url=item.get("url", ""),
                        content=item,
                        format=formats[0],
                        backend_used=self.backend_type,
                        latency_ms=latency_ms / len(urls),
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
