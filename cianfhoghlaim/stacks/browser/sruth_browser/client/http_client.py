"""HTTP client for browser agent service.

Provides async/sync interface for other sruth projects to call browser operations
without needing to know about backend routing or circuit breakers.
"""

from typing import Any, Literal
from urllib.parse import urljoin

import httpx
from pydantic import BaseModel, Field

from .types import (
    BackendType,
    ExtractionFormat,
    ExtractionResult,
    InteractionResult,
    NavigationResult,
    ResearchResult,
    ScreenshotResult,
    VisionAnalysisResult,
)


class BrowserClientConfig(BaseModel):
    """Configuration for browser HTTP client."""

    base_url: str = Field(
        default="http://localhost:3001",
        description="Browser agent service URL",
    )
    timeout: float = Field(
        default=120.0,
        description="Request timeout in seconds",
    )
    prefer_backend: BackendType | None = Field(
        default=None,
        description="Preferred backend (optional hint, router decides)",
    )


class BrowserClient:
    """HTTP client for browser agent service.

    Usage:
        client = BrowserClient()

        # Scrape a page
        result = await client.scrape("https://example.com")

        # Navigate with interaction
        await client.navigate("https://login.example.com")
        await client.interact("click", selector="#login-button")

        # Deep research
        research = await client.research("Find pricing for X")
    """

    def __init__(
        self,
        base_url: str = "http://localhost:3001",
        timeout: float = 120.0,
        prefer_backend: BackendType | None = None,
    ):
        self.config = BrowserClientConfig(
            base_url=base_url,
            timeout=timeout,
            prefer_backend=prefer_backend,
        )
        self._client: httpx.AsyncClient | None = None

    async def __aenter__(self) -> "BrowserClient":
        self._client = httpx.AsyncClient(
            base_url=self.config.base_url,
            timeout=self.config.timeout,
        )
        return self

    async def __aexit__(self, *args: Any) -> None:
        if self._client:
            await self._client.aclose()
            self._client = None

    @property
    def client(self) -> httpx.AsyncClient:
        if self._client is None:
            self._client = httpx.AsyncClient(
                base_url=self.config.base_url,
                timeout=self.config.timeout,
            )
        return self._client

    async def close(self) -> None:
        """Close the HTTP client."""
        if self._client:
            await self._client.aclose()
            self._client = None

    async def scrape(
        self,
        url: str,
        formats: list[ExtractionFormat] | None = None,
        only_main_content: bool = True,
        include_tags: list[str] | None = None,
        exclude_tags: list[str] | None = None,
    ) -> ExtractionResult:
        """Scrape content from a URL.

        Args:
            url: URL to scrape
            formats: Output formats (default: markdown)
            only_main_content: Extract only main content
            include_tags: HTML tags to include
            exclude_tags: HTML tags to exclude

        Returns:
            ExtractionResult with content in requested formats
        """
        response = await self.client.post(
            "/api/scrape",
            json={
                "url": url,
                "formats": [f.value for f in (formats or [ExtractionFormat.MARKDOWN])],
                "only_main_content": only_main_content,
                "include_tags": include_tags,
                "exclude_tags": exclude_tags,
                "prefer_backend": (
                    self.config.prefer_backend.value
                    if self.config.prefer_backend
                    else None
                ),
            },
        )
        response.raise_for_status()
        return ExtractionResult.model_validate(response.json())

    async def navigate(
        self,
        url: str,
        wait_for: str | None = None,
        timeout: float | None = None,
    ) -> NavigationResult:
        """Navigate to a URL.

        Args:
            url: URL to navigate to
            wait_for: Optional selector or text to wait for
            timeout: Optional navigation timeout

        Returns:
            NavigationResult with page info
        """
        response = await self.client.post(
            "/api/navigate",
            json={
                "url": url,
                "wait_for": wait_for,
                "timeout": timeout,
            },
        )
        response.raise_for_status()
        return NavigationResult.model_validate(response.json())

    async def interact(
        self,
        action: Literal["click", "type", "scroll", "hover", "fill", "press"],
        selector: str | None = None,
        text: str | None = None,
        key: str | None = None,
        direction: Literal["up", "down"] | None = None,
    ) -> InteractionResult:
        """Perform browser interaction.

        Args:
            action: Type of interaction
            selector: CSS selector or element description
            text: Text to type (for type/fill actions)
            key: Key to press (for press action)
            direction: Scroll direction (for scroll action)

        Returns:
            InteractionResult with action outcome
        """
        response = await self.client.post(
            "/api/interact",
            json={
                "action": action,
                "selector": selector,
                "text": text,
                "key": key,
                "direction": direction,
            },
        )
        response.raise_for_status()
        return InteractionResult.model_validate(response.json())

    async def screenshot(
        self,
        full_page: bool = False,
        selector: str | None = None,
        format: Literal["png", "jpeg", "webp"] = "png",
        quality: int | None = None,
    ) -> ScreenshotResult:
        """Take a screenshot.

        Args:
            full_page: Capture full page
            selector: Optional element to screenshot
            format: Image format
            quality: JPEG/WebP quality (0-100)

        Returns:
            ScreenshotResult with base64 image data
        """
        response = await self.client.post(
            "/api/screenshot",
            json={
                "full_page": full_page,
                "selector": selector,
                "format": format,
                "quality": quality,
            },
        )
        response.raise_for_status()
        return ScreenshotResult.model_validate(response.json())

    async def research(
        self,
        query: str,
        max_urls: int = 10,
        schema: dict[str, Any] | None = None,
    ) -> ResearchResult:
        """Perform deep research on a topic.

        Uses Firecrawl agent or Skyvern for multi-page exploration.

        Args:
            query: Research question
            max_urls: Maximum URLs to visit
            schema: Optional schema for structured output

        Returns:
            ResearchResult with aggregated findings
        """
        response = await self.client.post(
            "/api/research",
            json={
                "query": query,
                "max_urls": max_urls,
                "schema": schema,
            },
        )
        response.raise_for_status()
        return ResearchResult.model_validate(response.json())

    async def extract(
        self,
        url: str,
        prompt: str,
        schema: dict[str, Any] | None = None,
    ) -> ExtractionResult:
        """Extract structured data from a URL.

        Args:
            url: URL to extract from
            prompt: Extraction prompt
            schema: JSON schema for output

        Returns:
            ExtractionResult with structured content
        """
        response = await self.client.post(
            "/api/extract",
            json={
                "url": url,
                "prompt": prompt,
                "schema": schema,
            },
        )
        response.raise_for_status()
        return ExtractionResult.model_validate(response.json())

    async def fill_form(
        self,
        fields: dict[str, str],
        submit_selector: str | None = None,
    ) -> InteractionResult:
        """Fill and optionally submit a form.

        Args:
            fields: Field name/selector to value mapping
            submit_selector: Optional submit button selector

        Returns:
            InteractionResult with form outcome
        """
        response = await self.client.post(
            "/api/form",
            json={
                "fields": fields,
                "submit_selector": submit_selector,
            },
        )
        response.raise_for_status()
        return InteractionResult.model_validate(response.json())

    async def analyze_image(
        self,
        image_source: str,
        analysis_type: Literal[
            "ui_to_artifact",
            "ocr",
            "error_diagnosis",
            "diagram",
            "chart",
            "diff",
            "general",
        ],
        prompt: str,
        output_type: str | None = None,
    ) -> VisionAnalysisResult:
        """Analyze an image using Z.AI vision.

        Args:
            image_source: Path or URL to image
            analysis_type: Type of analysis
            prompt: Analysis prompt
            output_type: Output type for ui_to_artifact

        Returns:
            VisionAnalysisResult with analysis
        """
        response = await self.client.post(
            "/api/vision/analyze",
            json={
                "image_source": image_source,
                "analysis_type": analysis_type,
                "prompt": prompt,
                "output_type": output_type,
            },
        )
        response.raise_for_status()
        return VisionAnalysisResult.model_validate(response.json())

    async def health(self) -> dict[str, Any]:
        """Check service health and backend status.

        Returns:
            Health status including backend availability
        """
        response = await self.client.get("/health")
        response.raise_for_status()
        return response.json()

    async def batch_scrape(
        self,
        urls: list[str],
        formats: list[ExtractionFormat] | None = None,
        max_concurrency: int = 5,
    ) -> list[ExtractionResult]:
        """Scrape multiple URLs in parallel.

        Args:
            urls: URLs to scrape
            formats: Output formats
            max_concurrency: Maximum parallel requests

        Returns:
            List of ExtractionResults
        """
        response = await self.client.post(
            "/api/batch/scrape",
            json={
                "urls": urls,
                "formats": [f.value for f in (formats or [ExtractionFormat.MARKDOWN])],
                "max_concurrency": max_concurrency,
            },
        )
        response.raise_for_status()
        return [ExtractionResult.model_validate(r) for r in response.json()["results"]]

    async def discover_site(
        self,
        url: str,
        max_urls: int = 100,
        include_subdomains: bool = False,
    ) -> list[str]:
        """Discover URLs on a website (sitemap).

        Args:
            url: Base URL to discover
            max_urls: Maximum URLs to return
            include_subdomains: Include subdomain URLs

        Returns:
            List of discovered URLs
        """
        response = await self.client.post(
            "/api/map",
            json={
                "url": url,
                "limit": max_urls,
                "include_subdomains": include_subdomains,
            },
        )
        response.raise_for_status()
        return response.json()["urls"]
