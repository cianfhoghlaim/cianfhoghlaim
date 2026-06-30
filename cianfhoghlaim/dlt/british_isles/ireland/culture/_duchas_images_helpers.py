"""
Shared helpers split from celtic/duchas_images.py

Phase 3D of openspec change.
"""

from __future__ import annotations

import re
from typing import Any
from xml.etree import ElementTree as ET

try:
    from dlt.sources.incremental import Incremental  # noqa: F401
except ImportError:
    pass  # dlt.sources.incremental moved; use dlt.sources.incremental.IncrementalCursorProvider instead

try:
    from shared.http import doras_client, duchas_client
except ImportError:
    pass  # shared.http is unavailable; functions must lazy-import at call-time


DORAS_IIIF = "https://doras.gaois.ie/islandora/object"

DUCHAS_BASE = "https://www.duchas.ie"

MEITHEAL_BASE = "https://www.duchas.ie/meitheal"

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

def _get_doras_factory():
    """Get HTTP client factory for Doras GAOIS IIIF API."""
    return doras_client()

def _get_duchas_factory():
    """Get HTTP client factory for Dúchas.ie."""
    return duchas_client()

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
