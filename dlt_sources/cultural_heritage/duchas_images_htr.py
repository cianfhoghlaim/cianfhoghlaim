"""Culture IE source: duchas_images_htr_source (per the 2026-08-21-meaisinfhoghlaim-unsloth-agents-integration-v1 change)

HTR (Handwritten Text Recognition) variant of the Dúchas.ie loader. Optimized
for feeding the Gemma 4 4B + Qwen3-VL-8B fine-tunes (per the umbrella change).

Key differences from `duchas_corpus.py` (the general-purpose loader):
- Focus on the cbes (Schools' Collection 1937-1939) transcribed-only subset
- Downloads IIIF images at full resolution (no resize)
- Stores page + transcription pairs aligned for HTR training
- Lands in the `oideachais.cultural_heritage.duchas_htr` DuckLake schema
- Per-page records with bbox + transcription alignment for HTR training
- Supports Meitheal Dúchas crowdsourced corrections (for verified training data)

This is the dataset source for the `htr_finetune_unsloth_local` tool.
After fine-tuning, the adapter is loaded by Unsloth Studio for inference.
"""
from __future__ import annotations

import dlt


import re
import time
from collections.abc import Iterator
from datetime import UTC, datetime
from typing import Any

import structlog
from dlt.sources import DltResource

try:
    from dlt.sources.incremental import Incremental
except ImportError:
    pass  # dlt.sources.incremental moved; use dlt.sources.incremental.IncrementalCursorProvider instead

logger = structlog.get_logger(__name__)


from ._duchas_corpus_helpers import (
    DUCHAS_BASE,
    _download_iiif_image,
    _fetch_page_transcription,
    _get_duchas_factory,
    _get_iiif_image_url,
)


@dlt.source(name="duchas_htr")
def duchas_images_htr_source(
    collection: str = "cbes",
    max_pages: int = 100,
    per_page: int = 50,
    county: str | None = None,
    transcribed_only: bool = True,
    download_images: bool = True,
    image_size: str = "full",
    include_corrections: bool = True,
    last_updated: Incremental[str] = dlt.sources.incremental(
        cursor_path="updated_at",
        initial_value="2020-01-01",
    ),
) -> Iterator[DltResource]:
    """
    DLT source for Dúchas manuscript page images + TEI-XML transcriptions
    optimized for HTR fine-tuning of Gemma 4 4B + Qwen3-VL-8B.

    Provides resources for:
    - manuscript_pages: per-page image + transcription + bbox
    - meitheal_corrections: crowdsourced corrections (verified training data)
    - volumes: volume-level metadata

    Args:
        collection: Collection identifier (cbes, cbe)
        max_pages: Maximum pages to fetch
        per_page: Items per page in listings
        county: Filter by county name
        transcribed_only: Only fetch transcribed pages
        download_images: Whether to download image bytes (True for HTR)
        image_size: IIIF size parameter (default 'full' for HTR)
        include_corrections: Include Meitheal corrections
        last_updated: Incremental cursor for updates

    Yields:
        DLT resources for HTR training data
    """

    @dlt.resource(
        name="manuscript_pages_htr",
        write_disposition="merge",
        primary_key=["volume_number", "page_id"],
        columns={
            "volume_number": {"data_type": "bigint"},
            "page_id": {"data_type": "bigint"},
            "image_url": {"data_type": "text"},
            "image_path": {"data_type": "text"},
            "transcription_xml": {"data_type": "text"},
            "transcription_text": {"data_type": "text"},
            "page_width": {"data_type": "bigint"},
            "page_height": {"data_type": "bigint"},
            "county": {"data_type": "text"},
            "school": {"data_type": "text"},
            "teacher": {"data_type": "text"},
            "collection": {"data_type": "text"},
            "transcribed": {"data_type": "bool"},
            "updated_at": {"data_type": "timestamp"},
        },
    )
    def manuscript_pages_htr() -> Iterator[dict[str, Any]]:
        """Manuscript page metadata + images + transcriptions for HTR training."""
        from bs4 import BeautifulSoup

        factory = _get_duchas_factory()

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
                    resp = client.get(
                        f"{DUCHAS_BASE}{base_path}",
                        params=params,
                    )
                    resp.raise_for_status()
                except Exception as e:
                    logger.warning(
                        "duchas_pages_htr.fetch_failed",
                        list_page=list_page,
                        error=str(e),
                    )
                    continue

                soup = BeautifulSoup(resp.text, "html.parser")

                for volume_link in soup.select("a[href*='/volumes/']"):
                    volume_href = volume_link.get("href", "")
                    if not volume_href:
                        continue
                    try:
                        volume_number = int(
                            volume_href.rstrip("/").split("/")[-1]
                        )
                    except ValueError:
                        continue

                    # Fetch each page in the volume
                    page_ids = _fetch_volume_pages(
                        client, collection, volume_number
                    )
                    for page_id in page_ids:
                        page_data = _fetch_page_data(
                            client, collection, volume_number, page_id,
                            download_images=download_images,
                            image_size=image_size,
                        )
                        if page_data:
                            page_count += 1
                            yield page_data

                    volumes_fetched += 1
                    if volumes_fetched >= max_pages:
                        break

        logger.info(
            "duchas_pages_htr.completed",
            volumes_fetched=volumes_fetched,
            page_count=page_count,
        )

    @dlt.resource(
        name="meitheal_corrections",
        write_disposition="merge",
        primary_key=["volume_number", "page_id", "correction_id"],
    )
    def meitheal_corrections() -> Iterator[dict[str, Any]]:
        """Meitheal Dúchas crowdsourced corrections (verified training data)."""
        if not include_corrections:
            return
        factory = _get_duchas_factory()
        with factory.create_client() as client:
            for volume_number in range(1, max_pages + 1):
                corrections = _fetch_meitheal_corrections(
                    client, collection, volume_number
                )
                for correction in corrections:
                    yield {
                        "volume_number": volume_number,
                        "page_id": correction.get("page_id"),
                        "correction_id": correction.get("correction_id"),
                        "original_text": correction.get("original_text", ""),
                        "corrected_text": correction.get("corrected_text", ""),
                        "corrector": correction.get("corrector", ""),
                        "verified": correction.get("verified", False),
                        "updated_at": correction.get("updated_at", datetime.now(UTC).isoformat()),
                    }

    return manuscript_pages_htr(), meitheal_corrections()


def _fetch_volume_pages(client, collection: str, volume_number: int) -> list[int]:
    """Fetch all page IDs for a volume."""
    try:
        resp = client.get(
            f"{DUCHAS_BASE}/en/{collection}/volumes/{volume_number}/pages"
        )
        resp.raise_for_status()
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(resp.text, "html.parser")
        page_ids = []
        for link in soup.select("a[href*='/pages/']"):
            href = link.get("href", "")
            try:
                page_id = int(href.rstrip("/").split("/")[-1])
                page_ids.append(page_id)
            except ValueError:
                continue
        return page_ids
    except Exception as e:
        logger.warning("duchas.volume_pages_failed", volume=volume_number, error=str(e))
        return []


def _fetch_page_data(
    client, collection: str, volume_number: int, page_id: int,
    download_images: bool = True, image_size: str = "full",
) -> dict[str, Any] | None:
    """Fetch a single page: image URL + IIIF download + TEI-XML transcription."""
    try:
        resp = client.get(
            f"{DUCHAS_BASE}/en/{collection}/volumes/{volume_number}/pages/{page_id}"
        )
        resp.raise_for_status()
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(resp.text, "html.parser")

        # Extract IIIF image URL
        image_url = _get_iiif_image_url(soup)
        if not image_url:
            return None

        # Fetch transcription (TEI-XML)
        transcription_xml, transcription_text = _fetch_page_transcription(
            client, collection, volume_number, page_id
        )
        if not transcription_text:
            return None  # Only transcribed pages

        # Optionally download the image
        image_path = ""
        if download_images:
            image_path = _download_iiif_image(
                client, image_url, volume_number, page_id, image_size=image_size,
            )

        # Get page dimensions from the IIIF info endpoint
        page_width, page_height = _get_iiif_dimensions(client, image_url)

        return {
            "volume_number": volume_number,
            "page_id": page_id,
            "image_url": image_url,
            "image_path": image_path,
            "transcription_xml": transcription_xml,
            "transcription_text": transcription_text,
            "page_width": page_width,
            "page_height": page_height,
            "county": _extract_county(soup),
            "school": _extract_school(soup),
            "teacher": _extract_teacher(soup),
            "collection": collection,
            "transcribed": True,
            "updated_at": datetime.now(UTC).isoformat(),
        }
    except Exception as e:
        logger.warning("duchas.page_fetch_failed", volume=volume_number, page=page_id, error=str(e))
        return None


def _get_iiif_dimensions(client, image_url: str) -> tuple[int, int]:
    """Get image dimensions from IIIF info endpoint."""
    try:
        # Convert image URL to info.json URL
        # Pattern: /iiif/v2/<id>/full/full/0/default.jpg → /iiif/v2/<id>/info.json
        info_url = image_url.rsplit("/", 1)[0] + "/info.json"
        resp = client.get(info_url)
        resp.raise_for_status()
        info = resp.json()
        width = info.get("width", 0)
        height = info.get("height", 0)
        return width, height
    except Exception:
        return 0, 0


def _fetch_meitheal_corrections(client, collection: str, volume_number: int) -> list[dict]:
    """Fetch Meitheal Dúchas crowdsourced corrections."""
    try:
        resp = client.get(
            f"{DUCHAS_BASE}/en/{collection}/volumes/{volume_number}/corrections"
        )
        resp.raise_for_status()
        from bs4 import BeautifulSoup
        soup = BeautifulSoup(resp.text, "html.parser")
        corrections = []
        for row in soup.select("tr.correction-row"):
            corrections.append({
                "page_id": int(row.get("data-page-id", "0")),
                "correction_id": int(row.get("data-correction-id", "0")),
                "original_text": row.get("data-original", ""),
                "corrected_text": row.get("data-corrected", ""),
                "corrector": row.get("data-corrector", ""),
                "verified": row.get("data-verified", "false") == "true",
            })
        return corrections
    except Exception:
        return []


def _extract_county(soup) -> str:
    el = soup.select_one(".county-name")
    return el.get_text(strip=True) if el else ""


def _extract_school(soup) -> str:
    el = soup.select_one(".school-name")
    return el.get_text(strip=True) if el else ""


def _extract_teacher(soup) -> str:
    el = soup.select_one(".teacher-name")
    return el.get_text(strip=True) if el else ""


__all__ = ["duchas_images_htr_source"]
