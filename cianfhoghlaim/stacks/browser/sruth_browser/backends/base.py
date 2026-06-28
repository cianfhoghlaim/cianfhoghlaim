"""Abstract base class for browser backends."""

from abc import ABC, abstractmethod
from typing import Any

from ..browser_types import (
    BackendType,
    ExtractionFormat,
    ExtractionResult,
    InteractionResult,
    NavigationResult,
    ScreenshotResult,
)


class BrowserBackend(ABC):
    """Abstract base class for all browser backends."""

    backend_type: BackendType

    @abstractmethod
    async def initialize(self) -> None:
        """Initialize the backend connection."""
        pass

    @abstractmethod
    async def close(self) -> None:
        """Close the backend connection and release resources."""
        pass

    @abstractmethod
    async def health_check(self) -> bool:
        """Check if the backend is healthy and available."""
        pass

    @abstractmethod
    async def navigate(
        self,
        url: str,
        *,
        wait_until: str = "load",
        timeout: float | None = None,
    ) -> NavigationResult:
        """Navigate to a URL."""
        pass

    @abstractmethod
    async def extract(
        self,
        url: str,
        *,
        formats: list[ExtractionFormat] | None = None,
        schema: dict[str, Any] | None = None,
        prompt: str | None = None,
        timeout: float | None = None,
    ) -> ExtractionResult:
        """Extract content from a page."""
        pass

    @abstractmethod
    async def interact(
        self,
        action: str,
        *,
        selector: str | None = None,
        value: str | None = None,
        timeout: float | None = None,
    ) -> InteractionResult:
        """Perform a browser interaction (click, type, etc.)."""
        pass

    @abstractmethod
    async def screenshot(
        self,
        *,
        url: str | None = None,
        full_page: bool = False,
        selector: str | None = None,
        timeout: float | None = None,
    ) -> ScreenshotResult:
        """Capture a screenshot."""
        pass

    async def fill_form(
        self,
        fields: dict[str, str],
        *,
        submit_selector: str | None = None,
        timeout: float | None = None,
    ) -> InteractionResult:
        """Fill a form with multiple fields."""
        # Default implementation uses interact for each field
        for selector, value in fields.items():
            result = await self.interact(
                "fill",
                selector=selector,
                value=value,
                timeout=timeout,
            )
            if not result.success:
                return result

        if submit_selector:
            return await self.interact(
                "click",
                selector=submit_selector,
                timeout=timeout,
            )

        return InteractionResult(
            success=True,
            action="fill_form",
            backend_used=self.backend_type,
            latency_ms=0,
        )


class ResearchCapableBackend(BrowserBackend):
    """Backend that supports multi-page research."""

    @abstractmethod
    async def research(
        self,
        query: str,
        *,
        max_urls: int = 15,
        schema: dict[str, Any] | None = None,
        timeout: float | None = None,
    ) -> dict[str, Any]:
        """Perform deep research across multiple pages."""
        pass
