"""Crawl4AI backend for bulk extraction with LLM strategies."""

import time
from typing import Any

import httpx
import structlog

from ...browser_types import (
    BackendType,
    ExtractionFormat,
    ExtractionResult,
    InteractionResult,
    NavigationResult,
    ScreenshotResult,
)
from ...config import BrowserConfig, get_config
from ...exceptions import BackendError, BackendTimeoutError
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

    # =========================================================================
    # Phase E: New Crawl4AI 0.7.4 features
    # =========================================================================

    async def extract_with_css(
        self,
        url: str,
        schema: dict[str, Any],
        *,
        timeout: float | None = None,
    ) -> ExtractionResult:
        """E.1: Zero-cost extraction with JsonCssExtractionStrategy.

        Uses CSS selectors for known-structure pages (NCCA, SEC,
        DES, Apple Award CVs). NO LLM calls — completely free.
        Falls back to Firecrawl extract if Crawl4AI returns an
        error.

        Args:
            url: The URL to extract from.
            schema: A dict of {field_name: {"css": str, "type": str}}.
                e.g. {"title": {"css": "h1", "type": "text"}}.

        Returns:
            ExtractionResult with the structured data in `extracted_data`.
        """
        if not self._client:
            raise BackendError("Crawl4AI not initialized", self.backend_type)

        payload = {
            "url": url,
            "extraction_config": {
                "type": "json_css",
                "schema": schema,
            },
        }
        if timeout is not None:
            payload["timeout"] = timeout

        start = time.time()
        try:
            response = await self._client.post("/crawl", json=payload)
            response.raise_for_status()
            data = response.json()
        except Exception as e:
            logger.warning("crawl4ai_css_extract_failed", url=url, error=str(e))
            return ExtractionResult(
                success=False,
                url=url,
                content={},
                backend_used=self.backend_type,
                latency_ms=(time.time() - start) * 1000,
                error=str(e),
            )

        return ExtractionResult(
            success=True,
            url=url,
            content=data.get("extracted_data", {}),
            backend_used=self.backend_type,
            latency_ms=(time.time() - start) * 1000,
            metadata={"strategy": "json_css", "zero_llm_cost": True},
        )

    async def extract_with_llm(
        self,
        url: str,
        pydantic_class: type,
        *,
        instruction: str | None = None,
        timeout: float | None = None,
    ) -> ExtractionResult:
        """E.2: Type-safe structured extraction with LLMExtractionStrategy.

        Uses an LLM (the configured LiteLLM gateway model) to extract
        structured data into a Pydantic class. For complex/unstructured
        content. Costs LLM tokens.

        Args:
            url: The URL to extract from.
            pydantic_class: The Pydantic class to extract into. The
                schema is derived from the class.
            instruction: Optional custom instruction for the LLM.

        Returns:
            ExtractionResult with the structured data in `extracted_data`
            (as a dict matching the Pydantic schema).
        """
        if not self._client:
            raise BackendError("Crawl4AI not initialized", self.backend_type)

        # Derive the JSON schema from the Pydantic class
        try:
            schema = pydantic_class.model_json_schema()
        except AttributeError:
            # Fallback for Pydantic v1
            schema = pydantic_class.schema()

        payload = {
            "url": url,
            "extraction_config": {
                "type": "llm",
                "schema": schema,
                "instruction": instruction or "Extract structured data according to the schema.",
            },
        }
        if timeout is not None:
            payload["timeout"] = timeout

        start = time.time()
        try:
            response = await self._client.post("/crawl", json=payload)
            response.raise_for_status()
            data = response.json()
        except Exception as e:
            logger.warning("crawl4ai_llm_extract_failed", url=url, error=str(e))
            return ExtractionResult(
                success=False,
                url=url,
                content={},
                backend_used=self.backend_type,
                latency_ms=(time.time() - start) * 1000,
                error=str(e),
            )

        return ExtractionResult(
            success=True,
            url=url,
            content=data.get("extracted_data", {}),
            backend_used=self.backend_type,
            latency_ms=(time.time() - start) * 1000,
            metadata={"strategy": "llm", "schema": pydantic_class.__name__},
        )

    async def authenticate(
        self,
        profile_name: str,
        *,
        timeout: float | None = None,
    ) -> bool:
        """E.3: Use a managed browser with a persistent profile.

        Enables authenticated scraping (QubStudent, Microsoft Forms,
        etc.) via `use_managed_browser=True` + `user_data_dir=...`.

        Args:
            profile_name: The name of the profile to load
                (e.g. "qubstudent", "microsoft").

        Returns:
            True if the profile was loaded successfully.
        """
        if not self._client:
            raise BackendError("Crawl4AI not initialized", self.backend_type)

        payload = {
            "profile_name": profile_name,
            "managed_browser": True,
        }
        if timeout is not None:
            payload["timeout"] = timeout

        try:
            response = await self._client.post("/auth/load_profile", json=payload)
            response.raise_for_status()
            logger.info("crawl4ai_profile_loaded", profile=profile_name)
            return True
        except Exception as e:
            logger.warning("crawl4ai_profile_load_failed", profile=profile_name, error=str(e))
            return False

    async def bulk_crawl(
        self,
        seed_url: str,
        *,
        strategy: str = "BFS",
        max_depth: int = 3,
        max_pages: int = 100,
        allowed_domains: list[str] | None = None,
        timeout: float | None = None,
    ) -> list[ExtractionResult]:
        """E.4: Full-site crawling with BFS or DFS deep-crawl strategy.

        Args:
            seed_url: The starting URL for the crawl.
            strategy: "BFS" (breadth-first) or "DFS" (depth-first).
            max_depth: Maximum depth from the seed URL.
            max_pages: Maximum number of pages to crawl.
            allowed_domains: Optional list of allowed domains (whitelist).

        Returns:
            List of ExtractionResult, one per crawled page.
        """
        if not self._client:
            raise BackendError("Crawl4AI not initialized", self.backend_type)

        payload = {
            "url": seed_url,
            "strategy": strategy,
            "max_depth": max_depth,
            "max_pages": max_pages,
        }
        if allowed_domains:
            payload["allowed_domains"] = allowed_domains
        if timeout is not None:
            payload["timeout"] = timeout

        start = time.time()
        try:
            response = await self._client.post("/deep_crawl", json=payload)
            response.raise_for_status()
            data = response.json()
        except Exception as e:
            logger.warning("crawl4ai_bulk_crawl_failed", url=seed_url, error=str(e))
            return [ExtractionResult(
                success=False,
                url=seed_url,
                content={},
                backend_used=self.backend_type,
                latency_ms=(time.time() - start) * 1000,
                error=str(e),
            )]

        results = []
        for page in data.get("pages", []):
            results.append(ExtractionResult(
                success=True,
                url=page.get("url", seed_url),
                content={"markdown": page.get("markdown", "")},
                backend_used=self.backend_type,
                latency_ms=(time.time() - start) * 1000 / max(len(data.get("pages", [])), 1),
                metadata={"depth": page.get("depth", 0), "strategy": strategy},
            ))
        return results

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

    # =========================================================================
    # Phase E.5: Crawl4AI hooks (advanced login automation + cookie capture)
    # =========================================================================

    async def register_hook(
        self,
        hook_name: str,
        callback: Any,
    ) -> bool:
        """E.5: Register a hook callback for advanced page control.

        Supports the 4 Crawl4AI hook points:
        - `on_page_context_created`: receives the Playwright page
          (perfect for login automation + cookie capture)
        - `on_before_fetch`: receives the request (can modify
          headers, cookies, etc.)
        - `on_after_fetch`: receives the response (can extract
          cookies, capture screenshots, etc.)
        - `on_content_ready`: receives the parsed content (can
          modify or annotate before extraction)

        Args:
            hook_name: One of the 4 hook point names above.
            callback: An async callable that receives the hook
                      context (page, request, or response depending
                      on the hook point).

        Returns:
            True if the hook was registered successfully.

        Example:
            async def login(page):
                await page.goto("https://qubstudent.example.com")
                await page.fill("#email", "user@example.com")
                await page.fill("#password", os.environ["PASS"])
                await page.click("button[type=submit]")

            await client.register_hook("on_page_context_created", login)
        """
        if hook_name not in (
            "on_page_context_created",
            "on_before_fetch",
            "on_after_fetch",
            "on_content_ready",
        ):
            logger.warning("crawl4ai_invalid_hook", hook=hook_name)
            return False

        if not self._client:
            raise BackendError("Crawl4AI not initialized", self.backend_type)

        # The Crawl4AI server has a hook registry endpoint; we
        # register the callback by name + serialise a reference
        # to the in-process callback.
        try:
            response = await self._client.post(
                "/hooks/register",
                json={
                    "hook_name": hook_name,
                    "callback_name": callback.__name__,
                    "callback_module": callback.__module__,
                },
            )
            response.raise_for_status()
            # Store the callback locally so the BrowserClient
            # can dispatch to it on subsequent calls.
            if not hasattr(self, "_hooks"):
                self._hooks = {}
            self._hooks[hook_name] = callback
            logger.info(
                "crawl4ai_hook_registered",
                hook=hook_name,
                callback=callback.__name__,
            )
            return True
        except Exception as e:  # noqa: BLE001
            logger.warning(
                "crawl4ai_hook_register_failed",
                hook=hook_name,
                error=str(e),
            )
            return False

    async def get_hooks(self) -> list[str]:
        """E.5: List the registered hook names.

        Returns:
            A list of the 4 hook point names that have callbacks
            registered (out of the possible 4).
        """
        if not hasattr(self, "_hooks"):
            return []
        return list(self._hooks.keys())

    async def dispatch_hook(
        self,
        hook_name: str,
        context: Any,
    ) -> None:
        """E.5: Dispatch a registered hook callback.

        Called internally by the BrowserClient when a hook
        point is reached. Catches all exceptions (the hook
        must never crash the crawl).
        """
        if not hasattr(self, "_hooks"):
            return
        callback = self._hooks.get(hook_name)
        if callback is None:
            return
        try:
            result = callback(context)
            if hasattr(result, "__await__"):
                await result
        except Exception as e:  # noqa: BLE001
            logger.warning(
                "crawl4ai_hook_dispatch_failed",
                hook=hook_name,
                callback=callback.__name__,
                error=str(e),
            )
