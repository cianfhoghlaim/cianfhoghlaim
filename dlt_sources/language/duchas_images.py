"""
Culture IE source: duchas_images_source

Split from celtic/duchas_images.py in Phase 3D.
"""

from __future__ import annotations
import dlt


import re
import time
from collections.abc import Iterator
from datetime import UTC, datetime
from typing import Any
from xml.etree import ElementTree as ET

import structlog
from dlt.sources import DltResource

try:
    from dlt.sources.incremental import Incremental
except ImportError:
    pass  # dlt.sources.incremental moved; use dlt.sources.incremental.IncrementalCursorProvider instead

logger = structlog.get_logger(__name__)


from ._duchas_images_helpers import (
    DUCHAS_BASE,
    _download_iiif_image,
    _fetch_page_transcription,
    _get_duchas_factory,
    _get_iiif_image_url,
)


def duchas_images_source(
    collection: str = "cbes",
    max_pages: int = 100,
    per_page: int = 50,
    county: str | None = None,
    transcribed_only: bool = True,
    download_images: bool = False,
    image_size: str = "1024,",
    include_corrections: bool = True,
    last_updated: Incremental[str] = dlt.sources.incremental(
        cursor_path="updated_at",
        initial_value="2020-01-01",
    ),
) -> Iterator[DltResource]:
    """
    DLT source for Dúchas manuscript images and transcriptions.

    Provides resources for:
    - Manuscript page images (via IIIF)
    - TEI-XML transcriptions with line breaks
    - Meitheal Dúchas crowdsourced corrections

    Args:
        collection: Collection identifier (cbes, cbe)
        max_pages: Maximum pages to fetch
        per_page: Items per page in listings
        county: Filter by county name
        transcribed_only: Only fetch transcribed pages
        download_images: Whether to download image bytes
        image_size: IIIF size parameter (full, 1024,, 512,, etc.)
        include_corrections: Include Meitheal corrections
        last_updated: Incremental cursor for updates

    Yields:
        DLT resources for images, transcriptions, and corrections
    """

    @dlt.resource(
        name="manuscript_pages",
        write_disposition="merge",
        primary_key=["volume_number", "page_id"],
    )
    def manuscript_pages() -> Iterator[dict[str, Any]]:
        """Manuscript page metadata and images."""
        from bs4 import BeautifulSoup

        factory = _get_duchas_factory()

        # First get list of volumes
        base_path = "/en/cbes/volumes" if collection == "cbes" else f"/en/{collection}/volumes"

        volumes_fetched = 0
        page_count = 0

        with factory.create_client() as client:
            for list_page in range(1, max_pages + 1):
                params = {
                    "Page": list_page,
                    "PerPage": per_page,
                }
                if transcribed_only:
                    params["Transcribed"] = "true"
                if county:
                    params["County"] = county

                try:
                    response = client.get(base_path, params=params)
                    response.raise_for_status()
                    soup = BeautifulSoup(response.text, "html.parser")
                except Exception as e:
                    logger.warning(
                        "duchas_volumes_error",
                        list_page=list_page,
                        error=str(e),
                    )
                    break

                # Extract volume links
                volume_links = soup.select(f'a[href*="/{collection}/"]')
                if not volume_links:
                    break

                for link in volume_links:
                    match = re.search(rf"/{collection}/(\d+)", link.get("href", ""))
                    if not match:
                        continue

                    volume_number = match.group(1)

                    # Fetch volume pages
                    try:
                        vol_path = f"/en/{collection}/{volume_number}"
                        vol_response = client.get(vol_path)
                        vol_response.raise_for_status()
                        vol_soup = BeautifulSoup(vol_response.text, "html.parser")
                    except Exception as e:
                        logger.warning(
                            "duchas_volume_pages_error",
                            volume=volume_number,
                            error=str(e),
                        )
                        continue

                    # Extract page links
                    page_links = vol_soup.select(
                        f'a[href*="/{collection}/{volume_number}/"]'
                    )

                    for page_link in page_links:
                        page_match = re.search(
                            rf"/{collection}/{volume_number}/(\d+)",
                            page_link.get("href", ""),
                        )
                        if not page_match:
                            continue

                        page_id = page_match.group(1)
                        page_count += 1

                        record = {
                            "volume_number": volume_number,
                            "page_id": page_id,
                            "page_number": int(page_id) if page_id.isdigit() else None,
                            "collection": collection,
                            "iiif_url": _get_iiif_image_url(
                                volume_number, int(page_id), collection, image_size
                            ),
                            "page_url": f"{DUCHAS_BASE}/en/{collection}/{volume_number}/{page_id}",
                            "updated_at": datetime.now(UTC).isoformat(),
                        }

                        # Download image if requested
                        if download_images:
                            image_bytes = _download_iiif_image(
                                volume_number,
                                int(page_id),
                                collection,
                                image_size,
                            )
                            if image_bytes:
                                record["image_bytes"] = image_bytes
                                record["image_size_bytes"] = len(image_bytes)

                        yield record

                        # Rate limiting
                        time.sleep(0.1)

                    volumes_fetched += 1

                    if page_count >= max_pages * per_page:
                        return

    @dlt.resource(
        name="transcriptions",
        write_disposition="merge",
        primary_key=["volume_number", "page_id"],
    )
    def transcriptions() -> Iterator[dict[str, Any]]:
        """Page transcriptions with line breaks."""
        factory = _get_duchas_factory()

        # Get transcribed pages from XML API
        if collection == "cbes":
            # Schools' Collection has XML API
            xml_path = "/xml/cbes"

            with factory.create_client() as client:
                try:
                    response = client.get(xml_path)
                    response.raise_for_status()
                    root = ET.fromstring(response.text)

                    for volume in root.findall(".//volume"):
                        volume_number = volume.get("id")
                        if not volume_number:
                            continue

                        for page in volume.findall(".//page"):
                            page_id = page.get("id")
                            if not page_id:
                                continue

                            transcription = _fetch_page_transcription(
                                volume_number, page_id, collection
                            )

                            if transcription:
                                yield {
                                    "volume_number": volume_number,
                                    "page_id": page_id,
                                    "page_number": transcription.page_number,
                                    "full_text": transcription.full_text,
                                    "lines": [
                                        {
                                            "line_number": line.line_number,
                                            "text": line.text,
                                            "x": line.x,
                                            "y": line.y,
                                            "width": line.width,
                                            "height": line.height,
                                        }
                                        for line in transcription.lines
                                    ],
                                    "line_count": len(transcription.lines),
                                    "char_count": len(transcription.full_text),
                                    "transcriber": transcription.transcriber,
                                    "transcription_date": transcription.transcription_date,
                                    "updated_at": datetime.now(UTC).isoformat(),
                                }

                            time.sleep(0.1)
                except ET.ParseError as e:
                    logger.error("duchas_xml_index_parse_error", error=str(e))
                except Exception as e:
                    logger.warning("duchas_xml_index_error", error=str(e))

    @dlt.resource(
        name="meitheal_corrections",
        write_disposition="merge",
        primary_key=["volume_number", "page_id", "original_text"],
    )
    def meitheal_corrections() -> Iterator[dict[str, Any]]:
        """Crowdsourced transcription corrections."""
        if not include_corrections:
            return

        # This would typically iterate through pages with known corrections
        # For now, yield a placeholder structure
        yield {
            "volume_number": "placeholder",
            "page_id": "placeholder",
            "original_text": "",
            "corrected_text": "",
            "contributor": "",
            "status": "placeholder",
            "fetched_at": datetime.now(UTC).isoformat(),
        }

    @dlt.resource(
        name="training_samples",
        write_disposition="merge",
        primary_key=["sample_id"],
    )
    def training_samples() -> Iterator[dict[str, Any]]:
        """
        Pre-processed samples for OCR training.

        Combines images and transcriptions into training-ready format.
        """
        # This resource joins images with transcriptions
        # It would be populated during CocoIndex processing
        yield {
            "sample_id": "placeholder",
            "volume_number": "",
            "page_id": "",
            "image_path": "",
            "transcription": "",
            "line_count": 0,
            "has_gaelic_script": False,
            "dialect": "",
            "quality_score": 0.0,
            "created_at": datetime.now(UTC).isoformat(),
        }

    yield manuscript_pages
    yield transcriptions
    if include_corrections:
        yield meitheal_corrections
    yield training_samples
