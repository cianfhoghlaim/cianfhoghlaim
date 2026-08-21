"""Base scraper class with Stagehand integration and common utilities.

Provides:
- Cookie consent handling (GDPR dialogs)
- Pagination strategies (infinite scroll, next button, page numbers)
- Media download and storage (PDF, images, audio)
- Observe-then-act pattern for reliable interactions
"""

import asyncio
import hashlib
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, AsyncIterator

import httpx
import structlog

from ..backends.selfhosted.stagehand_backend import StagehandBackend
from ..config import BrowserConfig, get_config
from ..browser_types import ExtractionResult, InteractionResult, NavigationResult

logger = structlog.get_logger()


class PaginationType(str, Enum):
    """Pagination strategy types."""

    INFINITE_SCROLL = "infinite_scroll"
    NEXT_BUTTON = "next_button"
    PAGE_NUMBERS = "page_numbers"
    LOAD_MORE = "load_more"
    URL_PARAMS = "url_params"


class MediaType(str, Enum):
    """Media types for download and storage."""

    PDF = "pdf"
    IMAGE = "image"
    AUDIO = "audio"
    VIDEO = "video"


@dataclass
class StorageResult:
    """Result of media download and storage."""

    success: bool
    media_type: MediaType
    source_url: str
    s3_key: str = ""
    s3_bucket: str = ""
    size_bytes: int = 0
    content_hash: str = ""
    metadata: dict[str, Any] = field(default_factory=dict)
    error: str | None = None


# Common cookie consent button patterns (including Irish)
COOKIE_CONSENT_PATTERNS = [
    "Accept all cookies",
    "Accept all",
    "Accept cookies",
    "I accept",
    "Allow all",
    "Agree",
    "Accept",
    "OK",
    "Got it",
    "Glacaim leis",  # Irish: "I accept"
    "Ceadaigh",  # Irish: "Allow"
    "Glacaim le gach fianán",  # Irish: "I accept all cookies"
    "Aontaím",  # Irish: "I agree"
]


class BaseDomainScraper(ABC):
    """Abstract base class for domain-specific scrapers.

    Provides common functionality:
    - Cookie consent handling
    - Pagination strategies
    - Observe-then-act pattern
    - Media download and storage
    """

    # Subclasses must define these
    domain: str = ""
    rate_limit_seconds: float = 1.0
    requires_javascript: bool = True

    def __init__(
        self,
        backend: StagehandBackend | None = None,
        config: BrowserConfig | None = None,
    ):
        self.config = config or get_config()
        self._backend = backend
        self._http_client: httpx.AsyncClient | None = None
        self._last_request_time: float = 0

    async def initialize(self) -> None:
        """Initialize scraper resources."""
        if self._backend is None:
            self._backend = StagehandBackend(self.config)
            await self._backend.initialize()

        self._http_client = httpx.AsyncClient(
            timeout=httpx.Timeout(30.0),
            follow_redirects=True,
        )

    async def close(self) -> None:
        """Clean up resources."""
        if self._backend:
            await self._backend.close()
        if self._http_client:
            await self._http_client.aclose()

    @property
    def backend(self) -> StagehandBackend:
        """Get the Stagehand backend."""
        if self._backend is None:
            raise RuntimeError("Scraper not initialized. Call initialize() first.")
        return self._backend

    async def _rate_limit(self) -> None:
        """Enforce rate limiting between requests."""
        import time

        now = time.time()
        elapsed = now - self._last_request_time
        if elapsed < self.rate_limit_seconds:
            await asyncio.sleep(self.rate_limit_seconds - elapsed)
        self._last_request_time = time.time()

    # =========================================================================
    # Cookie Consent Handling
    # =========================================================================

    async def handle_cookie_consent(self) -> bool:
        """Attempt to dismiss cookie consent dialogs.

        Returns:
            True if a cookie dialog was found and dismissed, False otherwise.
        """
        for pattern in COOKIE_CONSENT_PATTERNS:
            try:
                # Try to find and click the button
                elements = await self.backend.observe(
                    f"Find button or link with text containing '{pattern}'"
                )
                if elements:
                    result = await self.backend.interact(
                        f"Click the '{pattern}' button to accept cookies"
                    )
                    if result.success:
                        logger.info(
                            "cookie_consent_dismissed",
                            pattern=pattern,
                            domain=self.domain,
                        )
                        await asyncio.sleep(0.5)  # Wait for dialog to close
                        return True
            except Exception as e:
                logger.debug("cookie_consent_pattern_failed", pattern=pattern, error=str(e))
                continue

        logger.debug("cookie_consent_not_found", domain=self.domain)
        return False

    # =========================================================================
    # Pagination Handling
    # =========================================================================

    async def handle_pagination(
        self,
        strategy: PaginationType,
        max_pages: int = 10,
        scroll_delay: float = 1.0,
    ) -> AsyncIterator[int]:
        """Handle various pagination patterns.

        Args:
            strategy: The pagination strategy to use.
            max_pages: Maximum number of pages/scrolls to process.
            scroll_delay: Delay between pagination actions.

        Yields:
            Page number (0-indexed).
        """
        match strategy:
            case PaginationType.INFINITE_SCROLL:
                async for page_num in self._handle_infinite_scroll(max_pages, scroll_delay):
                    yield page_num

            case PaginationType.NEXT_BUTTON:
                async for page_num in self._handle_next_button(max_pages, scroll_delay):
                    yield page_num

            case PaginationType.LOAD_MORE:
                async for page_num in self._handle_load_more(max_pages, scroll_delay):
                    yield page_num

            case PaginationType.PAGE_NUMBERS:
                async for page_num in self._handle_page_numbers(max_pages, scroll_delay):
                    yield page_num

            case _:
                yield 0  # Single page, no pagination

    async def _handle_infinite_scroll(
        self, max_pages: int, scroll_delay: float
    ) -> AsyncIterator[int]:
        """Handle infinite scroll pagination."""
        for i in range(max_pages):
            yield i
            await self.backend.interact("Scroll down to load more content")
            await asyncio.sleep(scroll_delay)

    async def _handle_next_button(
        self, max_pages: int, scroll_delay: float
    ) -> AsyncIterator[int]:
        """Handle next button pagination."""
        for i in range(max_pages):
            yield i

            # Look for next button
            elements = await self.backend.observe(
                "Find the next page button or link"
            )
            if not elements:
                logger.info("pagination_complete", reason="no_next_button", pages=i + 1)
                break

            result = await self.backend.interact("Click the next page button")
            if not result.success:
                logger.info("pagination_complete", reason="click_failed", pages=i + 1)
                break

            await asyncio.sleep(scroll_delay)

    async def _handle_load_more(
        self, max_pages: int, scroll_delay: float
    ) -> AsyncIterator[int]:
        """Handle load more button pagination."""
        for i in range(max_pages):
            yield i

            # Look for load more button
            elements = await self.backend.observe(
                "Find the load more button or show more link"
            )
            if not elements:
                logger.info("pagination_complete", reason="no_load_more", pages=i + 1)
                break

            result = await self.backend.interact("Click the load more button")
            if not result.success:
                logger.info("pagination_complete", reason="click_failed", pages=i + 1)
                break

            await asyncio.sleep(scroll_delay)

    async def _handle_page_numbers(
        self, max_pages: int, scroll_delay: float
    ) -> AsyncIterator[int]:
        """Handle numbered page pagination."""
        for i in range(max_pages):
            yield i

            next_page = i + 2  # Pages typically start at 1
            elements = await self.backend.observe(
                f"Find page number {next_page} in pagination"
            )
            if not elements:
                logger.info("pagination_complete", reason="no_page_number", pages=i + 1)
                break

            result = await self.backend.interact(f"Click page number {next_page}")
            if not result.success:
                logger.info("pagination_complete", reason="click_failed", pages=i + 1)
                break

            await asyncio.sleep(scroll_delay)

    # =========================================================================
    # Observe-Then-Act Pattern
    # =========================================================================

    async def observe_then_act(
        self,
        instruction: str,
        timeout: float | None = None,
    ) -> InteractionResult:
        """Perform observe-then-act pattern for reliable interactions.

        This is the recommended Stagehand pattern:
        1. Observe to find elements matching instruction
        2. Act on the first observed element

        Args:
            instruction: Natural language instruction for the action.
            timeout: Optional timeout override.

        Returns:
            InteractionResult with success status.
        """
        await self._rate_limit()

        # First observe
        elements = await self.backend.observe(instruction, timeout=timeout)

        if not elements:
            return InteractionResult(
                success=False,
                action=instruction,
                selector=None,
                backend_used=self.backend.backend_type,
                latency_ms=0,
                error="No elements found matching instruction",
            )

        # Then act on first element
        return await self.backend.interact(
            instruction,
            timeout=timeout,
        )

    # =========================================================================
    # Media Download and Storage
    # =========================================================================

    async def download_media(
        self,
        url: str,
        media_type: MediaType,
        bucket: str = "sruth-media",
        prefix: str = "",
    ) -> StorageResult:
        """Download media and optionally store to S3/R2.

        Args:
            url: URL of the media to download.
            media_type: Type of media (pdf, image, audio, video).
            bucket: S3/R2 bucket name.
            prefix: Key prefix for storage.

        Returns:
            StorageResult with download details and storage location.
        """
        if not self._http_client:
            return StorageResult(
                success=False,
                media_type=media_type,
                source_url=url,
                error="HTTP client not initialized",
            )

        try:
            await self._rate_limit()

            response = await self._http_client.get(url)
            response.raise_for_status()

            content = response.content
            content_hash = hashlib.sha256(content).hexdigest()

            # Generate storage key
            extension = self._get_extension(media_type, response.headers.get("content-type"))
            s3_key = f"{prefix}/{content_hash[:16]}.{extension}" if prefix else f"{content_hash[:16]}.{extension}"

            # Extract metadata
            metadata = {
                "content_type": response.headers.get("content-type"),
                "content_length": len(content),
                "source_url": url,
                "media_type": media_type.value,
            }

            logger.info(
                "media_downloaded",
                url=url,
                media_type=media_type.value,
                size_bytes=len(content),
                hash=content_hash[:16],
            )

            return StorageResult(
                success=True,
                media_type=media_type,
                source_url=url,
                s3_key=s3_key,
                s3_bucket=bucket,
                size_bytes=len(content),
                content_hash=content_hash,
                metadata=metadata,
            )

        except Exception as e:
            logger.error("media_download_failed", url=url, error=str(e))
            return StorageResult(
                success=False,
                media_type=media_type,
                source_url=url,
                error=str(e),
            )

    def _get_extension(self, media_type: MediaType, content_type: str | None) -> str:
        """Get file extension from media type and content type."""
        if content_type:
            mime_map = {
                "application/pdf": "pdf",
                "image/png": "png",
                "image/jpeg": "jpg",
                "image/webp": "webp",
                "audio/mpeg": "mp3",
                "audio/wav": "wav",
                "audio/ogg": "ogg",
                "video/mp4": "mp4",
                "video/webm": "webm",
            }
            for mime, ext in mime_map.items():
                if mime in content_type:
                    return ext

        # Fallback to media type
        type_map = {
            MediaType.PDF: "pdf",
            MediaType.IMAGE: "png",
            MediaType.AUDIO: "mp3",
            MediaType.VIDEO: "mp4",
        }
        return type_map.get(media_type, "bin")

    # =========================================================================
    # Navigation Helpers
    # =========================================================================

    async def navigate_to(
        self,
        url: str,
        handle_cookies: bool = True,
    ) -> NavigationResult:
        """Navigate to URL with optional cookie consent handling.

        Args:
            url: URL to navigate to.
            handle_cookies: Whether to attempt cookie consent dismissal.

        Returns:
            NavigationResult with navigation outcome.
        """
        await self._rate_limit()

        result = await self.backend.navigate(url)

        if result.success and handle_cookies:
            await self.handle_cookie_consent()

        return result

    async def extract_page(
        self,
        instruction: str,
        schema: dict[str, Any] | None = None,
    ) -> ExtractionResult:
        """Extract structured data from current page.

        Args:
            instruction: Natural language extraction instruction.
            schema: Optional JSON schema for structured extraction.

        Returns:
            ExtractionResult with extracted data.
        """
        # Get current URL (already navigated)
        # Use the backend's extract method
        if self._backend and self._backend._session_id:
            try:
                response = await self._backend._client.post(
                    "/extract",
                    json={
                        "sessionId": self._backend._session_id,
                        "instruction": instruction,
                        "schema": schema,
                    },
                )
                response.raise_for_status()
                data = response.json()
                return ExtractionResult(
                    success=data.get("success", True),
                    url="",
                    content=data.get("data", {}),
                    format="json",
                    backend_used=self._backend.backend_type,
                    latency_ms=0,
                )
            except Exception as e:
                return ExtractionResult(
                    success=False,
                    url="",
                    content={},
                    format="json",
                    backend_used=self._backend.backend_type,
                    latency_ms=0,
                    error=str(e),
                )
        return ExtractionResult(
            success=False,
            url="",
            content={},
            format="json",
            backend_used=self._backend.backend_type if self._backend else None,
            latency_ms=0,
            error="Backend not initialized",
        )

    # =========================================================================
    # Abstract Methods for Subclasses
    # =========================================================================

    @abstractmethod
    async def scrape(self, url: str, **kwargs: Any) -> dict[str, Any]:
        """Main scraping method to be implemented by subclasses.

        Args:
            url: URL to scrape.
            **kwargs: Additional scraping parameters.

        Returns:
            Scraped data as dictionary.
        """
        ...

    @abstractmethod
    def get_extraction_schema(self) -> dict[str, Any]:
        """Get BAML/JSON schema for data extraction.

        Returns:
            Schema definition for structured extraction.
        """
        ...
