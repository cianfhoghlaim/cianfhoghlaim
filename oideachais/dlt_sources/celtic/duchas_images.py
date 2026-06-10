"""
DLT Source for Dúchas.ie Manuscript Images and Transcriptions.

Extends the base duchas.py source with:
- IIIF image downloads from doras.gaois.ie
- TEI-XML transcription parsing with line breaks
- Meitheal Dúchas crowdsourced corrections
- Page-level metadata for OCR training

This source is designed for building OCR training datasets
from Irish handwriting samples.

Uses HttpClientFactory for resilient HTTP client with:
- Circuit breaker pattern
- Rate limiting
- Automatic retries

Usage:
    from oideachais.data_platform.dlt_sources.duchas_images import duchas_images_source

    source = duchas_images_source(
        collection="cbes",
        max_pages=100,
        download_images=True,
    )

    pipeline = dlt.pipeline(
        pipeline_name="duchas_images",
        destination="duckdb",
    )
    pipeline.run(source)
"""
from __future__ import annotations

import os
import re
import time
from collections.abc import Iterator
from dataclasses import dataclass
from datetime import UTC, datetime
from typing import Any
from xml.etree import ElementTree as ET

import dlt
from dlt.sources import DltResource
from dlt.sources.incremental import Incremental
from oideachais.observability.logging import get_logger
from shared.http import doras_client, duchas_client

logger = get_logger(__name__)

# Base URLs
DUCHAS_BASE = "https://www.duchas.ie"
DORAS_IIIF = "https://doras.gaois.ie/islandora/object"
MEITHEAL_BASE = "https://www.duchas.ie/meitheal"


def _get_duchas_factory():
    """Get HTTP client factory for Dúchas.ie."""
    return duchas_client()


def _get_doras_factory():
    """Get HTTP client factory for Doras GAOIS IIIF API."""
    return doras_client()


@dataclass
class TranscriptionLine:
    """A single line of transcription with position info."""

    line_number: int
    text: str
    x: float | None = None
    y: float | None = None
    width: float | None = None
    height: float | None = None


@dataclass
class PageTranscription:
    """Full page transcription with lines."""

    page_id: str
    volume_number: str
    page_number: int
    lines: list[TranscriptionLine]
    full_text: str
    transcriber: str | None = None
    transcription_date: str | None = None
    confidence: float | None = None




def _get_iiif_image_url(
    volume_number: str,
    page_number: int,
    collection: str = "cbes",
    size: str = "full",
    quality: str = "default",
    format: str = "jpg",
) -> str:
    """
    Construct IIIF image URL for a manuscript page.

    Args:
        volume_number: Volume identifier
        page_number: Page number within volume
        collection: Collection (cbes, cbe)
        size: IIIF size parameter (full, max, ^w,h, w,, ,h)
        quality: Image quality (default, color, gray)
        format: Image format (jpg, png, webp)

    Returns:
        IIIF Image API URL
    """
    # IIIF Image API pattern for doras.gaois.ie
    # Format: {base}/{identifier}/{region}/{size}/{rotation}/{quality}.{format}
    identifier = f"{collection}:{volume_number}:{page_number}"
    return f"{DORAS_IIIF}/{identifier}/full/{size}/0/{quality}.{format}"


def _download_iiif_image(
    volume_number: str,
    page_number: int,
    collection: str = "cbes",
    size: str = "full",
) -> bytes | None:
    """
    Download manuscript page image via IIIF.

    Args:
        volume_number: Volume identifier
        page_number: Page number
        collection: Collection identifier
        size: IIIF size (full, max, 1024,, etc.)

    Returns:
        Image bytes or None if failed
    """
    url = _get_iiif_image_url(volume_number, page_number, collection, size)
    factory = _get_doras_factory()

    with factory.create_client() as client:
        try:
            response = client.get(url)
            response.raise_for_status()
            return response.content
        except Exception as e:
            logger.warning(
                "duchas_iiif_error",
                volume=volume_number,
                page=page_number,
                error=str(e),
            )
            return None


def _parse_tei_transcription(xml_content: str) -> list[TranscriptionLine]:
    """
    Parse TEI-XML transcription into lines.

    Handles:
    - <lb/> line breaks
    - <pb/> page breaks
    - <gap/> for illegible text
    - <unclear> for uncertain text
    - <corr> for corrections

    Args:
        xml_content: TEI-XML string

    Returns:
        List of TranscriptionLine objects
    """
    lines = []

    try:
        root = ET.fromstring(xml_content)
    except ET.ParseError:
        # Try to extract text without full XML parsing
        text = re.sub(r"<[^>]+>", "\n", xml_content)
        for i, line in enumerate(text.split("\n"), 1):
            line = line.strip()
            if line:
                lines.append(TranscriptionLine(line_number=i, text=line))
        return lines

    # Find text body
    body = root.find(".//{http://www.tei-c.org/ns/1.0}body")
    if body is None:
        body = root.find(".//body")
    if body is None:
        body = root

    current_line = []
    line_number = 1

    def process_element(elem):
        nonlocal current_line, line_number

        # Handle line breaks
        if elem.tag in ("{http://www.tei-c.org/ns/1.0}lb", "lb"):
            if current_line:
                lines.append(
                    TranscriptionLine(
                        line_number=line_number,
                        text=" ".join(current_line),
                    )
                )
                current_line = []
                line_number += 1

        # Handle page breaks (start new page)
        elif elem.tag in ("{http://www.tei-c.org/ns/1.0}pb", "pb"):
            if current_line:
                lines.append(
                    TranscriptionLine(
                        line_number=line_number,
                        text=" ".join(current_line),
                    )
                )
                current_line = []
                line_number = 1

        # Handle gap (illegible text)
        elif elem.tag in ("{http://www.tei-c.org/ns/1.0}gap", "gap"):
            current_line.append("[...]")

        # Handle unclear text
        elif elem.tag in ("{http://www.tei-c.org/ns/1.0}unclear", "unclear"):
            text = "".join(elem.itertext())
            if text:
                current_line.append(f"[{text}?]")

        # Add text content
        if elem.text:
            current_line.append(elem.text.strip())

        # Process children
        for child in elem:
            process_element(child)

        # Add tail text
        if elem.tail:
            current_line.append(elem.tail.strip())

    process_element(body)

    # Add final line
    if current_line:
        lines.append(
            TranscriptionLine(
                line_number=line_number,
                text=" ".join(current_line),
            )
        )

    return lines


def _fetch_page_transcription(
    volume_number: str,
    page_id: str,
    collection: str = "cbes",
) -> PageTranscription | None:
    """
    Fetch transcription for a specific page.

    Args:
        volume_number: Volume identifier
        page_id: Page identifier
        collection: Collection identifier

    Returns:
        PageTranscription or None if not available
    """
    factory = _get_duchas_factory()

    with factory.create_client() as client:
        # Try TEI-XML endpoint first
        xml_path = f"/xml/{collection}/{volume_number}/pages/{page_id}"

        try:
            response = client.get(xml_path)
            response.raise_for_status()
            lines = _parse_tei_transcription(response.text)

            return PageTranscription(
                page_id=page_id,
                volume_number=volume_number,
                page_number=int(page_id) if page_id.isdigit() else 0,
                lines=lines,
                full_text="\n".join(line.text for line in lines),
            )
        except Exception as e:
            logger.debug(
                "duchas_xml_fallback",
                volume=volume_number,
                page=page_id,
                error=str(e),
            )

        # Fallback: try HTML page
        html_path = f"/en/{collection}/{volume_number}/{page_id}"

        try:
            response = client.get(html_path)
            response.raise_for_status()
            from bs4 import BeautifulSoup

            soup = BeautifulSoup(response.text, "html.parser")

            # Find transcription div
            trans_div = soup.select_one(".transcription, .page-text, #transcription")
            if trans_div:
                text = trans_div.get_text(strip=True)
                lines = [
                    TranscriptionLine(line_number=i + 1, text=line.strip())
                    for i, line in enumerate(text.split("\n"))
                    if line.strip()
                ]

                return PageTranscription(
                    page_id=page_id,
                    volume_number=volume_number,
                    page_number=int(page_id) if page_id.isdigit() else 0,
                    lines=lines,
                    full_text=text,
                )
        except Exception as e:
            logger.warning(
                "duchas_transcription_error",
                volume=volume_number,
                page=page_id,
                error=str(e),
            )

    return None


def _fetch_meitheal_corrections(
    volume_number: str,
    page_id: str,
) -> list[dict[str, Any]]:
    """
    Fetch crowdsourced corrections from Meitheal Dúchas.

    Args:
        volume_number: Volume identifier
        page_id: Page identifier

    Returns:
        List of correction records
    """
    corrections = []
    factory = _get_duchas_factory()

    # Meitheal is under the main duchas.ie domain
    path = f"/meitheal/corrections/{volume_number}/{page_id}"

    with factory.create_client() as client:
        try:
            response = client.get(path)
            response.raise_for_status()
            from bs4 import BeautifulSoup

            soup = BeautifulSoup(response.text, "html.parser")

            for correction in soup.select(".correction-item, .edit-item"):
                corrections.append(
                    {
                        "original_text": correction.select_one(".original")
                        .get_text(strip=True)
                        if correction.select_one(".original")
                        else None,
                        "corrected_text": correction.select_one(".corrected")
                        .get_text(strip=True)
                        if correction.select_one(".corrected")
                        else None,
                        "contributor": correction.select_one(".contributor")
                        .get_text(strip=True)
                        if correction.select_one(".contributor")
                        else None,
                        "date": correction.select_one(".date").get_text(strip=True)
                        if correction.select_one(".date")
                        else None,
                        "status": "approved"
                        if "approved" in correction.get("class", [])
                        else "pending",
                    }
                )
        except Exception as e:
            logger.warning(
                "meitheal_corrections_error",
                volume=volume_number,
                page=page_id,
                error=str(e),
            )

    return corrections


@dlt.source(name="duchas_images")
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
        if collection == "cbes":
            base_path = "/en/cbes/volumes"
        else:
            base_path = f"/en/{collection}/volumes"

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


@dlt.source(name="hidden_heritages")
def hidden_heritages_source(
    language: str = "ga",
    collection: str = "nfc",
    max_tales: int = 100,
) -> Iterator[DltResource]:
    """
    DLT source for HiddenHeritages.ai transcribed manuscripts.

    Collections:
    - nfc: National Folklore Collection
    - sss: School of Scottish Studies

    Args:
        language: Language filter (ga, gd, en)
        collection: Collection (nfc, sss)
        max_tales: Maximum tales to fetch

    Yields:
        DLT resources for tales and transcriptions
    """

    @dlt.resource(
        name="tales",
        write_disposition="merge",
        primary_key="tale_id",
    )
    def tales() -> Iterator[dict[str, Any]]:
        """HiddenHeritages tales with HTR transcriptions."""
        # HiddenHeritages.ai API endpoints
        base_url = "https://hiddenheritages.ai/api"

        try:
            # Use Firecrawl agent for discovery if available
            api_key = os.getenv("FIRECRAWL_API_KEY")
            if api_key:
                from firecrawl import FirecrawlApp

                app = FirecrawlApp(api_key=api_key)

                result = app.agent(
                    prompt=f"Find tales from the {collection.upper()} collection "
                    f"in {language} language. Extract tale ID, title, "
                    "transcription text, and image URLs.",
                    urls=[f"https://hiddenheritages.ai/{collection}"],
                    schema={
                        "type": "object",
                        "properties": {
                            "tales": {
                                "type": "array",
                                "items": {
                                    "type": "object",
                                    "properties": {
                                        "tale_id": {"type": "string"},
                                        "title": {"type": "string"},
                                        "transcription": {"type": "string"},
                                        "image_url": {"type": "string"},
                                        "collector": {"type": "string"},
                                        "informant": {"type": "string"},
                                        "location": {"type": "string"},
                                        "date": {"type": "string"},
                                    },
                                },
                            },
                        },
                    },
                )

                for tale in result.get("data", {}).get("tales", [])[:max_tales]:
                    yield {
                        "tale_id": tale.get("tale_id", ""),
                        "title": tale.get("title", ""),
                        "transcription": tale.get("transcription", ""),
                        "image_url": tale.get("image_url", ""),
                        "collector": tale.get("collector", ""),
                        "informant": tale.get("informant", ""),
                        "location": tale.get("location", ""),
                        "date": tale.get("date", ""),
                        "language": language,
                        "collection": collection,
                        "source": "hiddenheritages.ai",
                        "fetched_at": datetime.now(UTC).isoformat(),
                    }
            else:
                # Fallback: direct scraping
                yield {
                    "tale_id": "placeholder",
                    "title": "",
                    "transcription": "",
                    "language": language,
                    "collection": collection,
                    "source": "hiddenheritages.ai",
                    "status": "firecrawl_not_available",
                    "fetched_at": datetime.now(UTC).isoformat(),
                }

        except Exception as e:
            yield {
                "tale_id": "error",
                "error": str(e),
                "language": language,
                "collection": collection,
                "source": "hiddenheritages.ai",
                "fetched_at": datetime.now(UTC).isoformat(),
            }

    yield tales
