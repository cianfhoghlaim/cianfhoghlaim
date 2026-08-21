"""Skyvern backend for vision-based navigation and form automation."""

import asyncio
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
from ..base import BrowserBackend, ResearchCapableBackend

logger = structlog.get_logger()


class SkyvernBackend(ResearchCapableBackend):
    """Skyvern API backend for vision-based browser automation."""

    backend_type = BackendType.SKYVERN_LOCAL

    def __init__(self, config: BrowserConfig | None = None):
        self.config = config or get_config()
        self._client: httpx.AsyncClient | None = None

    async def initialize(self) -> None:
        """Initialize HTTP client for Skyvern API."""
        self._client = httpx.AsyncClient(
            base_url=self.config.skyvern_api_url,
            timeout=httpx.Timeout(self.config.navigation_timeout * 2),
        )
        logger.info("skyvern_initialized", url=self.config.skyvern_api_url)

    async def close(self) -> None:
        """Close HTTP client."""
        if self._client:
            await self._client.aclose()
            self._client = None

    async def health_check(self) -> bool:
        """Check Skyvern health."""
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
        """Navigate using Skyvern task."""
        if not self._client:
            raise BackendError("Skyvern not initialized", self.backend_type)

        start_time = time.perf_counter()

        try:
            # Create a simple navigation task
            task_payload = {
                "url": url,
                "navigation_goal": f"Navigate to {url} and wait for page to load",
                "data_extraction_goal": None,
            }

            response = await self._client.post(
                "/tasks",
                json=task_payload,
                timeout=timeout or self.config.navigation_timeout,
            )
            response.raise_for_status()
            task_data = response.json()

            task_id = task_data.get("task_id")

            # Poll for task completion
            while True:
                status_response = await self._client.get(f"/tasks/{task_id}")
                status_data = status_response.json()
                status = status_data.get("status")

                if status in ("completed", "failed", "terminated"):
                    break

                await asyncio.sleep(1)

            latency_ms = (time.perf_counter() - start_time) * 1000

            if status == "completed":
                return NavigationResult(
                    success=True,
                    url=status_data.get("current_url", url),
                    title=status_data.get("page_title"),
                    backend_used=self.backend_type,
                    latency_ms=latency_ms,
                )
            else:
                return NavigationResult(
                    success=False,
                    url=url,
                    backend_used=self.backend_type,
                    latency_ms=latency_ms,
                    error=status_data.get("failure_reason", "Task failed"),
                )

        except httpx.TimeoutException as e:
            raise BackendTimeoutError(
                self.backend_type,
                timeout or self.config.navigation_timeout,
            ) from e

        except Exception as e:
            latency_ms = (time.perf_counter() - start_time) * 1000
            return NavigationResult(
                success=False,
                url=url,
                backend_used=self.backend_type,
                latency_ms=latency_ms,
                error=str(e),
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
        """Extract data using Skyvern's vision-based extraction."""
        if not self._client:
            raise BackendError("Skyvern not initialized", self.backend_type)

        formats = formats or [ExtractionFormat.JSON]
        start_time = time.perf_counter()

        try:
            # Create extraction task
            task_payload = {
                "url": url,
                "navigation_goal": f"Navigate to {url}",
                "data_extraction_goal": prompt or "Extract all visible data from the page",
            }

            if schema:
                task_payload["extracted_information_schema"] = schema

            response = await self._client.post(
                "/tasks",
                json=task_payload,
                timeout=timeout or self.config.extraction_timeout,
            )
            response.raise_for_status()
            task_data = response.json()

            task_id = task_data.get("task_id")

            # Poll for completion
            while True:
                status_response = await self._client.get(f"/tasks/{task_id}")
                status_data = status_response.json()
                status = status_data.get("status")

                if status in ("completed", "failed", "terminated"):
                    break

                await asyncio.sleep(1)

            latency_ms = (time.perf_counter() - start_time) * 1000

            if status == "completed":
                extracted = status_data.get("extracted_information", {})
                return ExtractionResult(
                    success=True,
                    url=url,
                    content={"extracted": extracted},
                    format=ExtractionFormat.JSON,
                    backend_used=self.backend_type,
                    latency_ms=latency_ms,
                )
            else:
                return ExtractionResult(
                    success=False,
                    url=url,
                    content={},
                    format=ExtractionFormat.JSON,
                    backend_used=self.backend_type,
                    latency_ms=latency_ms,
                    error=status_data.get("failure_reason", "Task failed"),
                )

        except Exception as e:
            latency_ms = (time.perf_counter() - start_time) * 1000
            return ExtractionResult(
                success=False,
                url=url,
                content={},
                format=formats[0] if formats else ExtractionFormat.JSON,
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
        """Skyvern uses natural language goals, not selectors.

        For selector-based interactions, use CDP or Stagehand.
        """
        raise BackendError(
            "Skyvern uses goal-based navigation. Use fill_form() or create a task.",
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
        """Get screenshot from Skyvern task artifacts."""
        # Skyvern stores screenshots in artifacts
        # This would require fetching from the artifact server
        raise BackendError(
            "Use CDP backend for direct screenshots",
            self.backend_type,
            retryable=False,
        )

    async def fill_form(
        self,
        fields: dict[str, str],
        *,
        submit_selector: str | None = None,
        timeout: float | None = None,
    ) -> InteractionResult:
        """Fill form using Skyvern's vision-based automation.

        Skyvern excels at complex forms with dependent dropdowns,
        dynamic fields, and ambiguous labels.
        """
        if not self._client:
            raise BackendError("Skyvern not initialized", self.backend_type)

        start_time = time.perf_counter()

        try:
            # Build navigation goal from fields
            field_descriptions = [f"{k}: {v}" for k, v in fields.items()]
            goal = f"Fill in the form with the following values:\n" + "\n".join(field_descriptions)

            if submit_selector:
                goal += f"\nThen submit the form."

            # This assumes we're on the page already
            # In practice, you'd include the URL in a full task
            task_payload = {
                "navigation_goal": goal,
            }

            response = await self._client.post(
                "/tasks",
                json=task_payload,
                timeout=timeout or self.config.navigation_timeout,
            )
            response.raise_for_status()
            task_data = response.json()

            task_id = task_data.get("task_id")

            # Poll for completion
            while True:
                status_response = await self._client.get(f"/tasks/{task_id}")
                status_data = status_response.json()
                status = status_data.get("status")

                if status in ("completed", "failed", "terminated"):
                    break

                await asyncio.sleep(1)

            latency_ms = (time.perf_counter() - start_time) * 1000

            return InteractionResult(
                success=status == "completed",
                action="fill_form",
                backend_used=self.backend_type,
                latency_ms=latency_ms,
                error=status_data.get("failure_reason") if status != "completed" else None,
            )

        except Exception as e:
            latency_ms = (time.perf_counter() - start_time) * 1000
            return InteractionResult(
                success=False,
                action="fill_form",
                backend_used=self.backend_type,
                latency_ms=latency_ms,
                error=str(e),
            )

    async def research(
        self,
        query: str,
        *,
        max_urls: int = 15,
        schema: dict[str, Any] | None = None,
        timeout: float | None = None,
    ) -> dict[str, Any]:
        """Perform multi-page research using Skyvern workflows.

        Note: Skyvern is better for navigation than research.
        Consider using Firecrawl /agent for deep research.
        """
        if not self._client:
            raise BackendError("Skyvern not initialized", self.backend_type)

        start_time = time.perf_counter()

        try:
            # Create a workflow-style task for research
            task_payload = {
                "url": "https://google.com",  # Start with search
                "navigation_goal": f"Search for: {query}. Visit the top {max_urls} results and gather information.",
                "data_extraction_goal": f"Extract key information about: {query}",
            }

            if schema:
                task_payload["extracted_information_schema"] = schema

            response = await self._client.post(
                "/tasks",
                json=task_payload,
                timeout=timeout or self.config.extraction_timeout * 2,
            )
            response.raise_for_status()
            task_data = response.json()

            task_id = task_data.get("task_id")

            # Poll for completion
            while True:
                status_response = await self._client.get(f"/tasks/{task_id}")
                status_data = status_response.json()
                status = status_data.get("status")

                if status in ("completed", "failed", "terminated"):
                    break

                await asyncio.sleep(2)

            latency_ms = (time.perf_counter() - start_time) * 1000

            return {
                "success": status == "completed",
                "query": query,
                "content": status_data.get("extracted_information", {}),
                "urls_visited": status_data.get("urls_visited", []),
                "backend_used": self.backend_type.value,
                "latency_ms": latency_ms,
                "error": status_data.get("failure_reason") if status != "completed" else None,
            }

        except Exception as e:
            latency_ms = (time.perf_counter() - start_time) * 1000
            return {
                "success": False,
                "query": query,
                "content": {},
                "backend_used": self.backend_type.value,
                "latency_ms": latency_ms,
                "error": str(e),
            }
