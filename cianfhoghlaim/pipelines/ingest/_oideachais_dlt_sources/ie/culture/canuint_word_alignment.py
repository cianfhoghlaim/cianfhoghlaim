"""
Culture IE source: canuint_word_alignment_source

Split from celtic/canuint.py in Phase 3D.
"""

from __future__ import annotations

import re
from collections.abc import Iterator

import dlt
from bs4 import BeautifulSoup
from dlt.sources import DltResource

try:
    from shared.http import canuint_client  # noqa: F401
except ImportError:
    pass  # shared.http is unavailable; functions must lazy-import at call-time


from ._canuint_helpers import (
    CANUINT_BASE,
    _get_canuint_factory,
    _safe_float,
)


def canuint_word_alignment_source(
    language: str = "ga",
    max_recordings: int = 1000,
    min_duration_ms: int = 50,
    max_duration_ms: int = 2000,
) -> Iterator[DltResource]:
    """
    Extract word-level forced alignment data from Canuint.ie.

    Each word has precise timestamps from the Canuint transcription system.
    This data can be used for:
    - ASR (Automatic Speech Recognition) fine-tuning
    - TTS (Text-to-Speech) training
    - Forced alignment model training

    Args:
        language: Interface language ('ga' or 'en')
        max_recordings: Maximum transcribed recordings to process
        min_duration_ms: Minimum word duration in milliseconds
        max_duration_ms: Maximum word duration in milliseconds

    Yields:
        DLT resources for word alignments and recording metadata
    """

    # Province to dialect mapping
    PROVINCE_DIALECT_MAP = {
        "Cúige Connacht": "connacht",
        "Cúige Mumhan": "munster",
        "Cúige Uladh": "ulster",
    }

    @dlt.resource(
        name="word_alignments",
        write_disposition="merge",
        primary_key="word_id",
    )
    def word_alignments_resource() -> Iterator[dict]:
        """
        Extract word-level alignment data with timestamps.

        Each word contains:
        - Precise start/end timestamps (float seconds)
        - Dialectal text (as spoken)
        - Standardized text (official spelling)
        - Speaker and location metadata
        """
        factory = _get_canuint_factory()

        with factory.create_client() as client:
            # First, get all transcribed recording IDs from homepage
            try:
                response = client.get(f"/{language}/")
                response.raise_for_status()
                homepage_soup = BeautifulSoup(response.text, "html.parser")
            except Exception as e:
                logger.warning("canuint_word_alignment_homepage_error", error=str(e))
                return

            # Find all area IDs and their provinces
            location_pattern = re.compile(rf"https://www\.canuint\.ie/{language}/(\d+)")
            area_provinces = {}  # area_id -> province

            for link in homepage_soup.find_all("a", href=location_pattern):
                match = location_pattern.search(link["href"])
                if not match:
                    continue
                area_id = match.group(1)

                # Get province from parent container
                province = None
                province_elem = link.find_parent(class_="province-section")
                if province_elem:
                    province_header = province_elem.find(class_="province")
                    if province_header:
                        province = province_header.get_text(strip=True)
                area_provinces[area_id] = province

            # Collect transcribed recording IDs
            recording_ids = []
            recording_metadata = {}  # recording_id -> metadata dict

            for area_id, province in area_provinces.items():
                if len(recording_ids) >= max_recordings:
                    break

                try:
                    response = client.get(f"/{language}/{area_id}")
                    response.raise_for_status()
                    area_soup = BeautifulSoup(response.text, "html.parser")
                except Exception as e:
                    logger.warning("canuint_word_alignment_area_error", area_id=area_id, error=str(e))
                    continue

                # Get area name
                area_name = None
                hometown_elem = area_soup.find(attrs={"data-hometown-name": True})
                if hometown_elem:
                    area_name = hometown_elem.get("data-hometown-name")

                # Find transcribed recordings
                for recording_elem in area_soup.find_all("li", class_="recording"):
                    if len(recording_ids) >= max_recordings:
                        break

                    if recording_elem.get("data-is-transcribed") != "1":
                        continue

                    recording_link = recording_elem.find("a", href=re.compile(r"/[A-Z]+\d+"))
                    if not recording_link:
                        continue

                    match = re.search(r"([A-Z]+\d+(?:c\d+)?)", recording_link["href"])
                    if not match:
                        continue

                    recording_id = match.group(1)
                    if recording_id in recording_metadata:
                        continue

                    # Extract speaker name
                    speaker_name = None
                    speaker_elem = recording_elem.find("i", class_="fa-user-circle")
                    if speaker_elem and speaker_elem.next_sibling:
                        speaker_name = str(speaker_elem.next_sibling).strip()

                    # Extract year
                    year = None
                    year_elem = recording_elem.find("span", class_="year")
                    if year_elem:
                        year_text = year_elem.get_text(strip=True)
                        if year_text.isdigit():
                            year = int(year_text)

                    recording_ids.append(recording_id)
                    recording_metadata[recording_id] = {
                        "area_id": area_id,
                        "area_name": area_name,
                        "province": province,
                        "dialect": PROVINCE_DIALECT_MAP.get(province, "unknown"),
                        "speaker_name": speaker_name,
                        "year": year,
                    }

            logger.info("canuint_word_alignment_recordings_found", count=len(recording_ids))

            # Extract word-level alignments from each recording
            total_words = 0
            for recording_id in recording_ids:
                try:
                    response = client.get(f"/{language}/{recording_id}")
                    response.raise_for_status()
                    recording_soup = BeautifulSoup(response.text, "html.parser")
                except Exception as e:
                    logger.warning("canuint_word_alignment_recording_error", recording_id=recording_id, error=str(e))
                    continue

                metadata = recording_metadata[recording_id]

                # Find transcript container with word segments
                transcript_container = recording_soup.find(class_="transcript")
                if not transcript_container:
                    continue

                # Extract each word segment
                word_index = 0
                for segment in transcript_container.find_all("span", class_="segment"):
                    start_time = _safe_float(segment.get("data-start"))
                    end_time = _safe_float(segment.get("data-end"))

                    if start_time is None or end_time is None:
                        continue

                    duration_ms = int((end_time - start_time) * 1000)

                    # Filter by duration
                    if duration_ms < min_duration_ms or duration_ms > max_duration_ms:
                        continue

                    # Extract dialectal text
                    text_elem = segment.find("span", class_="text")
                    dialectal_text = text_elem.get_text(strip=True) if text_elem else None

                    if not dialectal_text:
                        continue

                    # Extract standardized form
                    standardized_text = None
                    stext_elem = segment.find("span", class_="stext")
                    if stext_elem:
                        stext_link = stext_elem.find("a")
                        if stext_link:
                            standardized_text = stext_link.get_text(strip=True)

                    word_id = f"{recording_id}_{word_index:05d}"
                    word_index += 1
                    total_words += 1

                    yield {
                        "word_id": word_id,
                        "recording_id": recording_id,
                        "word_index": word_index - 1,
                        "start_time": start_time,
                        "end_time": end_time,
                        "duration_ms": duration_ms,
                        "dialectal_text": dialectal_text,
                        "standardized_text": standardized_text,
                        "speaker_name": metadata["speaker_name"],
                        "dialect": metadata["dialect"],
                        "province": metadata["province"],
                        "area_id": metadata["area_id"],
                        "area_name": metadata["area_name"],
                        "year": metadata["year"],
                        "audio_url": f"{CANUINT_BASE}/sounds/{recording_id}.mp3",
                    }

            logger.info("canuint_word_alignment_total_words", count=total_words)

    @dlt.resource(
        name="recording_metadata",
        write_disposition="merge",
        primary_key="recording_id",
    )
    def recording_metadata_resource() -> Iterator[dict]:
        """Extract recording-level metadata for audio downloads."""
        factory = _get_canuint_factory()

        with factory.create_client() as client:
            try:
                response = client.get(f"/{language}/")
                response.raise_for_status()
                homepage_soup = BeautifulSoup(response.text, "html.parser")
            except Exception as e:
                logger.warning("canuint_recording_metadata_error", error=str(e))
                return

            # Find all areas
            location_pattern = re.compile(rf"https://www\.canuint\.ie/{language}/(\d+)")
            area_provinces = {}

            for link in homepage_soup.find_all("a", href=location_pattern):
                match = location_pattern.search(link["href"])
                if match:
                    area_id = match.group(1)
                    province_elem = link.find_parent(class_="province-section")
                    if province_elem:
                        province_header = province_elem.find(class_="province")
                        if province_header:
                            area_provinces[area_id] = province_header.get_text(strip=True)

            recording_count = 0
            for area_id, province in area_provinces.items():
                if recording_count >= max_recordings:
                    break

                try:
                    response = client.get(f"/{language}/{area_id}")
                    response.raise_for_status()
                    area_soup = BeautifulSoup(response.text, "html.parser")
                except Exception:
                    continue

                area_name = None
                hometown_elem = area_soup.find(attrs={"data-hometown-name": True})
                if hometown_elem:
                    area_name = hometown_elem.get("data-hometown-name")

                for recording_elem in area_soup.find_all("li", class_="recording"):
                    if recording_count >= max_recordings:
                        break

                    is_transcribed = recording_elem.get("data-is-transcribed") == "1"
                    if not is_transcribed:
                        continue

                    recording_link = recording_elem.find("a", href=re.compile(r"/[A-Z]+\d+"))
                    if not recording_link:
                        continue

                    match = re.search(r"([A-Z]+\d+(?:c\d+)?)", recording_link["href"])
                    if not match:
                        continue

                    recording_id = match.group(1)
                    recording_count += 1

                    speaker_name = None
                    speaker_elem = recording_elem.find("i", class_="fa-user-circle")
                    if speaker_elem and speaker_elem.next_sibling:
                        speaker_name = str(speaker_elem.next_sibling).strip()

                    year = None
                    year_elem = recording_elem.find("span", class_="year")
                    if year_elem:
                        year_text = year_elem.get_text(strip=True)
                        if year_text.isdigit():
                            year = int(year_text)

                    yield {
                        "recording_id": recording_id,
                        "area_id": area_id,
                        "area_name": area_name,
                        "province": province,
                        "dialect": PROVINCE_DIALECT_MAP.get(province, "unknown"),
                        "speaker_name": speaker_name,
                        "year": year,
                        "is_transcribed": True,
                        "audio_url": f"{CANUINT_BASE}/sounds/{recording_id}.mp3",
                        "source_url": f"{CANUINT_BASE}/{language}/{recording_id}",
                    }

    yield word_alignments_resource
    yield recording_metadata_resource
