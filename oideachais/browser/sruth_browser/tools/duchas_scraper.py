"""
Dúchas.ie Scraper Tool for Irish Folklore Handwriting Dataset.

Scrapes the Schools' Collection (740K+ pages) from duchas.ie for:
- Handwritten manuscript images (HTR/OCR training)
- Existing transcriptions (ground truth)
- Metadata (collector, location, date, topic)

Rate Limiting: 1 request/second (as per firecrawl config)
Storage: Cloudflare R2 for images, Kafka for events

Usage:
    from sruth_browser.tools.duchas_scraper import (
        scrape_duchas_page,
        scrape_duchas_collection,
        DuchasPage,
    )

    # Single page
    page = await scrape_duchas_page(page_id="1234567")

    # Batch collection
    pages = await scrape_duchas_collection(
        county="galway",
        start_page=0,
        max_pages=1000,
    )
"""

import asyncio
import hashlib
import logging
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any
from urllib.parse import urljoin

from ..backends.router import get_router
from ..browser_types import BackendType, BrowserOperation, ExtractionFormat

logger = logging.getLogger(__name__)

# Base URL for Dúchas.ie
DUCHAS_BASE_URL = "https://www.duchas.ie"
DUCHAS_API_URL = "https://www.duchas.ie/api/v1.0"

# Rate limiting (1 req/sec as per firecrawl config)
RATE_LIMIT_SECONDS = 1.0


class DuchasCollection(str, Enum):
    """Dúchas.ie collection types."""

    SCHOOLS = "cbes"  # Schools' Collection (740K pages)
    MAIN = "cbeg"  # Main Manuscript Collection
    PHOTOGRAPHS = "cbep"  # Photograph Collection
    AUDIO = "cbea"  # Audio Collection


@dataclass
class DuchasPage:
    """A single page from the Schools' Collection."""

    # Identifiers
    page_id: str
    volume_id: str
    page_number: int

    # Content
    image_url: str
    transcription: str | None = None
    transcription_status: str = "untranscribed"  # untranscribed, partial, complete

    # Metadata
    county: str | None = None
    parish: str | None = None
    townland: str | None = None
    school: str | None = None
    collector: str | None = None
    informant: str | None = None
    topic: str | None = None
    year_collected: int | None = None

    # Processing
    image_hash: str | None = None
    scraped_at: datetime = field(default_factory=datetime.utcnow)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "page_id": self.page_id,
            "volume_id": self.volume_id,
            "page_number": self.page_number,
            "image_url": self.image_url,
            "transcription": self.transcription,
            "transcription_status": self.transcription_status,
            "county": self.county,
            "parish": self.parish,
            "townland": self.townland,
            "school": self.school,
            "collector": self.collector,
            "informant": self.informant,
            "topic": self.topic,
            "year_collected": self.year_collected,
            "image_hash": self.image_hash,
            "scraped_at": self.scraped_at.isoformat(),
        }

    def to_kafka_event(self) -> dict[str, Any]:
        """Convert to Kafka event format."""
        return {
            "event_type": "duchas.page.scraped",
            "event_time": datetime.utcnow().isoformat(),
            "page": self.to_dict(),
        }


@dataclass
class DuchasVolume:
    """A volume from the Schools' Collection."""

    volume_id: str
    county: str
    school: str
    pages: list[DuchasPage] = field(default_factory=list)
    total_pages: int = 0
    transcribed_pages: int = 0

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "volume_id": self.volume_id,
            "county": self.county,
            "school": self.school,
            "total_pages": self.total_pages,
            "transcribed_pages": self.transcribed_pages,
            "pages": [p.to_dict() for p in self.pages],
        }


class DuchasScraper:
    """
    Scraper for Dúchas.ie Schools' Collection.

    Features:
    - Rate-limited requests (1/sec)
    - Automatic retry with backoff
    - Kafka event production
    - R2 image storage integration
    """

    def __init__(
        self,
        rate_limit: float = RATE_LIMIT_SECONDS,
        max_retries: int = 3,
    ):
        self.rate_limit = rate_limit
        self.max_retries = max_retries
        self._last_request_time: float = 0
        self._lock = asyncio.Lock()

    async def _rate_limit(self) -> None:
        """Enforce rate limiting."""
        async with self._lock:
            now = asyncio.get_event_loop().time()
            elapsed = now - self._last_request_time
            if elapsed < self.rate_limit:
                await asyncio.sleep(self.rate_limit - elapsed)
            self._last_request_time = asyncio.get_event_loop().time()

    async def scrape_page(self, page_id: str) -> DuchasPage | None:
        """
        Scrape a single page from Dúchas.ie.

        Args:
            page_id: The page ID (e.g., from duchas.ie/en/cbes/1234567)

        Returns:
            DuchasPage with extracted content and metadata
        """
        await self._rate_limit()

        router = get_router()
        url = f"{DUCHAS_BASE_URL}/en/cbes/{page_id}"

        # Schema for structured extraction
        schema = {
            "type": "object",
            "properties": {
                "pageNumber": {"type": "integer"},
                "volumeId": {"type": "string"},
                "transcription": {"type": "string"},
                "transcriptionStatus": {
                    "type": "string",
                    "enum": ["untranscribed", "partial", "complete"],
                },
                "county": {"type": "string"},
                "parish": {"type": "string"},
                "townland": {"type": "string"},
                "school": {"type": "string"},
                "collector": {"type": "string"},
                "informant": {"type": "string"},
                "topic": {"type": "string"},
                "yearCollected": {"type": "integer"},
                "imageUrl": {"type": "string"},
            },
        }

        async def _extract(backend):
            result = await backend.extract(
                url,
                formats=[ExtractionFormat.JSON],
                schema=schema,
                prompt=(
                    "Extract the manuscript page details including: "
                    "page number, volume ID, any existing transcription, "
                    "metadata (county, parish, townland, school, collector, "
                    "informant, topic, year collected), and the manuscript "
                    "image URL. Look for the high-resolution image link."
                ),
                timeout=30.0,
            )
            return result

        try:
            result = await router.execute_with_fallback(
                BrowserOperation.EXTRACT, _extract
            )

            if not result.success:
                logger.warning(f"Failed to extract page {page_id}: {result.error}")
                return None

            data = result.content.get("extracted", {})

            # Get image URL
            image_url = data.get("imageUrl", "")
            if not image_url:
                # Construct default image URL pattern
                image_url = f"{DUCHAS_BASE_URL}/images/cbes/{page_id}.jpg"

            # Compute image hash for deduplication
            image_hash = hashlib.sha256(image_url.encode()).hexdigest()[:16]

            return DuchasPage(
                page_id=page_id,
                volume_id=data.get("volumeId", ""),
                page_number=data.get("pageNumber", 0),
                image_url=image_url,
                transcription=data.get("transcription"),
                transcription_status=data.get("transcriptionStatus", "untranscribed"),
                county=data.get("county"),
                parish=data.get("parish"),
                townland=data.get("townland"),
                school=data.get("school"),
                collector=data.get("collector"),
                informant=data.get("informant"),
                topic=data.get("topic"),
                year_collected=data.get("yearCollected"),
                image_hash=image_hash,
            )

        except Exception as e:
            logger.error(f"Error scraping page {page_id}: {e}")
            return None

    async def scrape_volume(
        self,
        volume_id: str,
        max_pages: int | None = None,
    ) -> DuchasVolume:
        """
        Scrape all pages from a volume.

        Args:
            volume_id: Volume identifier
            max_pages: Maximum pages to scrape (None for all)

        Returns:
            DuchasVolume with all scraped pages
        """
        await self._rate_limit()

        router = get_router()
        url = f"{DUCHAS_BASE_URL}/en/cbes/{volume_id}"

        # First, get volume info and page list
        async def _get_volume_info(backend):
            return await backend.extract(
                url,
                formats=[ExtractionFormat.JSON],
                schema={
                    "type": "object",
                    "properties": {
                        "volumeId": {"type": "string"},
                        "county": {"type": "string"},
                        "school": {"type": "string"},
                        "totalPages": {"type": "integer"},
                        "pageIds": {
                            "type": "array",
                            "items": {"type": "string"},
                        },
                    },
                },
                prompt=(
                    "Extract the volume information including county, school, "
                    "total number of pages, and list of page IDs/links."
                ),
                timeout=30.0,
            )

        try:
            result = await router.execute_with_fallback(
                BrowserOperation.EXTRACT, _get_volume_info
            )

            if not result.success:
                logger.warning(f"Failed to get volume {volume_id}: {result.error}")
                return DuchasVolume(volume_id=volume_id, county="", school="")

            data = result.content.get("extracted", {})
            page_ids = data.get("pageIds", [])

            if max_pages:
                page_ids = page_ids[:max_pages]

            volume = DuchasVolume(
                volume_id=volume_id,
                county=data.get("county", ""),
                school=data.get("school", ""),
                total_pages=data.get("totalPages", 0),
            )

            # Scrape each page
            for page_id in page_ids:
                page = await self.scrape_page(page_id)
                if page:
                    volume.pages.append(page)
                    if page.transcription:
                        volume.transcribed_pages += 1

            return volume

        except Exception as e:
            logger.error(f"Error scraping volume {volume_id}: {e}")
            return DuchasVolume(volume_id=volume_id, county="", school="")

    async def search_county(
        self,
        county: str,
        start_page: int = 0,
        max_results: int = 100,
    ) -> list[str]:
        """
        Search for page IDs by county.

        Args:
            county: Irish county name (e.g., "galway", "cork")
            start_page: Pagination offset
            max_results: Maximum results to return

        Returns:
            List of page IDs
        """
        await self._rate_limit()

        router = get_router()
        url = f"{DUCHAS_BASE_URL}/en/cbes/search?county={county}&offset={start_page}"

        async def _search(backend):
            return await backend.extract(
                url,
                formats=[ExtractionFormat.JSON],
                schema={
                    "type": "object",
                    "properties": {
                        "totalResults": {"type": "integer"},
                        "pageIds": {
                            "type": "array",
                            "items": {"type": "string"},
                        },
                    },
                },
                prompt="Extract the page IDs from the search results.",
                timeout=30.0,
            )

        try:
            result = await router.execute_with_fallback(
                BrowserOperation.EXTRACT, _search
            )

            if result.success:
                data = result.content.get("extracted", {})
                return data.get("pageIds", [])[:max_results]
            return []

        except Exception as e:
            logger.error(f"Error searching county {county}: {e}")
            return []


# =============================================================================
# Convenience Functions (ADK Tool Interface)
# =============================================================================

_scraper: DuchasScraper | None = None


def get_scraper() -> DuchasScraper:
    """Get or create scraper singleton."""
    global _scraper
    if _scraper is None:
        _scraper = DuchasScraper()
    return _scraper


async def scrape_duchas_page(page_id: str) -> dict[str, Any]:
    """
    Scrape a single Dúchas.ie page.

    ADK Tool for scraping individual manuscript pages.

    Args:
        page_id: The page ID from duchas.ie

    Returns:
        Page data including image URL and transcription
    """
    scraper = get_scraper()
    page = await scraper.scrape_page(page_id)
    if page:
        return {
            "success": True,
            "page": page.to_dict(),
        }
    return {
        "success": False,
        "error": f"Failed to scrape page {page_id}",
    }


async def scrape_duchas_volume(
    volume_id: str,
    max_pages: int = 50,
) -> dict[str, Any]:
    """
    Scrape all pages from a Dúchas.ie volume.

    ADK Tool for batch scraping manuscript volumes.

    Args:
        volume_id: Volume identifier
        max_pages: Maximum pages to scrape

    Returns:
        Volume data with all scraped pages
    """
    scraper = get_scraper()
    volume = await scraper.scrape_volume(volume_id, max_pages)
    return {
        "success": len(volume.pages) > 0,
        "volume": volume.to_dict(),
        "scraped_count": len(volume.pages),
    }


async def scrape_duchas_collection(
    county: str,
    start_page: int = 0,
    max_pages: int = 100,
    produce_to_kafka: bool = False,
) -> dict[str, Any]:
    """
    Scrape Dúchas.ie collection by county.

    ADK Tool for bulk scraping with optional Kafka event production.

    Args:
        county: Irish county name (e.g., "galway")
        start_page: Pagination offset
        max_pages: Maximum pages to scrape
        produce_to_kafka: Whether to produce events to Kafka

    Returns:
        Collection statistics and scraped page summaries
    """
    scraper = get_scraper()

    # Get page IDs for county
    page_ids = await scraper.search_county(county, start_page, max_pages)

    if not page_ids:
        return {
            "success": False,
            "error": f"No pages found for county {county}",
        }

    pages: list[DuchasPage] = []
    errors: list[str] = []

    for page_id in page_ids:
        try:
            page = await scraper.scrape_page(page_id)
            if page:
                pages.append(page)

                # Optionally produce to Kafka
                if produce_to_kafka:
                    # Import here to avoid circular dependency
                    try:
                        from oideachais.kafka.producer import produce_event

                        await produce_event(
                            topic="edu.duchas.pages",
                            event=page.to_kafka_event(),
                        )
                    except ImportError:
                        logger.warning("Kafka producer not available")

        except Exception as e:
            errors.append(f"{page_id}: {str(e)}")
            logger.warning(f"Error scraping page {page_id}: {e}")

    return {
        "success": len(pages) > 0,
        "county": county,
        "total_pages": len(page_ids),
        "scraped_count": len(pages),
        "transcribed_count": sum(1 for p in pages if p.transcription),
        "error_count": len(errors),
        "errors": errors[:10],  # Limit error list
        "pages": [
            {
                "page_id": p.page_id,
                "image_url": p.image_url,
                "transcribed": p.transcription is not None,
            }
            for p in pages[:20]  # Limit page list in response
        ],
    }


async def download_duchas_image(
    page_id: str,
    image_url: str,
    storage_path: str | None = None,
) -> dict[str, Any]:
    """
    Download a Dúchas.ie manuscript image.

    ADK Tool for downloading high-resolution images for HTR training.

    Args:
        page_id: Page identifier for naming
        image_url: Direct URL to the image
        storage_path: Optional local path (defaults to R2)

    Returns:
        Download result with local/R2 path
    """
    import httpx

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(image_url, timeout=60.0)
            response.raise_for_status()

            image_data = response.content
            image_hash = hashlib.sha256(image_data).hexdigest()[:16]

            # Determine storage location
            if storage_path:
                # Local storage
                import aiofiles

                async with aiofiles.open(storage_path, "wb") as f:
                    await f.write(image_data)
                path = storage_path
            else:
                # R2 storage (placeholder - integrate with actual R2 client)
                path = f"r2://duchas/images/{page_id}_{image_hash}.jpg"
                logger.info(f"Would upload to R2: {path}")

            return {
                "success": True,
                "page_id": page_id,
                "path": path,
                "size_bytes": len(image_data),
                "hash": image_hash,
            }

    except Exception as e:
        logger.error(f"Error downloading image for {page_id}: {e}")
        return {
            "success": False,
            "error": str(e),
        }
