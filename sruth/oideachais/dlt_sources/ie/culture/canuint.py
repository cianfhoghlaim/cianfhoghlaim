"""
Culture IE source: canuint_source

Split from celtic/canuint.py in Phase 3D.
"""

from __future__ import annotations
import re
from collections.abc import Iterator
import dlt
from bs4 import BeautifulSoup
from dlt.sources import DltResource
from observability.logging import get_logger
try:
    from shared.http import canuint_client  # noqa: F401
except ImportError:
    pass  # shared.http is unavailable; functions must lazy-import at call-time


from ._canuint_helpers import (
    CANUINT_BASE,
    _get_canuint_factory,
    _safe_float,
)

def canuint_source(
    language: str = "ga",
    max_locations: int = 50,
    transcribed_only: bool = False,
    max_recordings_per_location: int = 100,
) -> Iterator[DltResource]:
    """
    Source for Canuint.ie Irish pronunciation database.

    Args:
        language: Interface language ('ga' or 'en')
        max_locations: Maximum locations to process
        transcribed_only: Only fetch transcribed recordings
        max_recordings_per_location: Max recordings per location

    Yields:
        DLT resources for locations, recordings, and transcripts
    """

    @dlt.resource(
        name="areas",
        write_disposition="merge",
        primary_key="area_id",
    )
    def areas_resource() -> Iterator[dict]:
        """Extract geographic areas from homepage."""
        factory = _get_canuint_factory()
        with factory.create_client() as client:
            try:
                response = client.get(f"/{language}/")
                response.raise_for_status()
            except Exception as e:
                logger.warning("canuint_areas_error", error=str(e))
                return

            soup = BeautifulSoup(response.text, "html.parser")

        # Extract location links from homepage
        location_pattern = re.compile(rf"https://www\.canuint\.ie/{language}/(\d+)")
        seen_ids = set()

        for link in soup.find_all("a", href=location_pattern):
            match = location_pattern.search(link["href"])
            if not match:
                continue

            area_id = match.group(1)
            if area_id in seen_ids:
                continue
            seen_ids.add(area_id)

            if len(seen_ids) > max_locations:
                break

            area_name = link.get_text(strip=True)

            # Get province from parent container if available
            province = None
            province_elem = link.find_parent(class_="province-section")
            if province_elem:
                province_header = province_elem.find(class_="province")
                if province_header:
                    province = province_header.get_text(strip=True)

            yield {
                "area_id": area_id,
                "area_name": area_name,
                "province": province,
                "source_url": url,
            }

    @dlt.resource(
        name="recordings",
        write_disposition="merge",
        primary_key="recording_id",
    )
    def recordings_resource() -> Iterator[dict]:
        """Extract recordings from location pages."""
        factory = _get_canuint_factory()

        # First get all area IDs
        area_ids = []
        with factory.create_client() as client:
            try:
                response = client.get(f"/{language}/")
                response.raise_for_status()
                soup = BeautifulSoup(response.text, "html.parser")

                location_pattern = re.compile(rf"https://www\.canuint\.ie/{language}/(\d+)")
                for link in soup.find_all("a", href=location_pattern):
                    match = location_pattern.search(link["href"])
                    if match:
                        area_ids.append(match.group(1))
                    if len(area_ids) >= max_locations:
                        break
            except Exception as e:
                logger.warning("canuint_recordings_list_error", error=str(e))
                return

            # Fetch recordings from each area
            for area_id in set(area_ids):
                try:
                    response = client.get(f"/{language}/{area_id}")
                    response.raise_for_status()
                    soup = BeautifulSoup(response.text, "html.parser")
                except Exception as e:
                    logger.warning("canuint_area_error", area_id=area_id, error=str(e))
                    continue

                # Extract area metadata
                area_name = None
                province = None
                hometown_elem = soup.find(attrs={"data-hometown-name": True})
                if hometown_elem:
                    area_name = hometown_elem.get("data-hometown-name")

                province_elem = soup.find(class_="province")
                if province_elem:
                    province = province_elem.get_text(strip=True)

                # Extract recordings
                recording_count = 0
                for recording_elem in soup.find_all("li", class_="recording"):
                    if recording_count >= max_recordings_per_location:
                        break

                    # Check transcription status
                    is_transcribed = recording_elem.get("data-is-transcribed") == "1"
                    if transcribed_only and not is_transcribed:
                        continue

                    # Extract recording ID from link
                    recording_link = recording_elem.find("a", href=re.compile(r"/[A-Z]+\d+c\d+"))
                    if not recording_link:
                        continue

                    recording_id_match = re.search(r"([A-Z]+\d+c\d+)", recording_link["href"])
                    if not recording_id_match:
                        continue

                    recording_id = recording_id_match.group(1)

                    # Extract year
                    year = None
                    year_elem = recording_elem.find("span", class_="year")
                    if year_elem:
                        year_text = year_elem.get_text(strip=True)
                        if year_text.isdigit():
                            year = int(year_text)

                    # Extract speaker name
                    speaker_name = None
                    speaker_elem = recording_elem.find("i", class_="fa-user-circle")
                    if speaker_elem and speaker_elem.next_sibling:
                        speaker_name = str(speaker_elem.next_sibling).strip()

                    recording_count += 1

                    yield {
                        "recording_id": recording_id,
                        "area_id": area_id,
                        "area_name": area_name,
                        "province": province,
                        "speaker_name": speaker_name,
                        "year": year,
                        "is_transcribed": is_transcribed,
                        "audio_url": f"{CANUINT_BASE}/sounds/{recording_id}.mp3",
                        "source_url": f"{CANUINT_BASE}/{language}/{area_id}",
                    }

    @dlt.resource(
        name="transcripts",
        write_disposition="merge",
        primary_key="segment_id",
    )
    def transcripts_resource() -> Iterator[dict]:
        """Extract transcription segments from transcribed recordings."""
        factory = _get_canuint_factory()
        recording_ids = []

        with factory.create_client() as client:
            # Get area IDs from homepage
            try:
                response = client.get(f"/{language}/")
                response.raise_for_status()
                soup = BeautifulSoup(response.text, "html.parser")

                location_pattern = re.compile(rf"https://www\.canuint\.ie/{language}/(\d+)")
                area_ids = []
                for link in soup.find_all("a", href=location_pattern):
                    match = location_pattern.search(link["href"])
                    if match and len(area_ids) < max_locations:
                        area_ids.append(match.group(1))
            except Exception as e:
                logger.warning("canuint_transcripts_list_error", error=str(e))
                return

            # Collect transcribed recording IDs from each area
            for area_id in set(area_ids):
                try:
                    response = client.get(f"/{language}/{area_id}")
                    response.raise_for_status()
                    soup = BeautifulSoup(response.text, "html.parser")

                    for recording_elem in soup.find_all("li", class_="recording"):
                        if recording_elem.get("data-is-transcribed") != "1":
                            continue

                        recording_link = recording_elem.find("a", href=re.compile(r"/[A-Z]+\d+c\d+"))
                        if recording_link:
                            match = re.search(r"([A-Z]+\d+c\d+)", recording_link["href"])
                            if match:
                                recording_ids.append(match.group(1))
                except Exception as e:
                    logger.warning("canuint_transcript_area_error", area_id=area_id, error=str(e))
                    continue

            # Fetch transcripts for each recording
            for recording_id in set(recording_ids):
                try:
                    response = client.get(f"/{language}/{recording_id}")
                    response.raise_for_status()
                    soup = BeautifulSoup(response.text, "html.parser")
                except Exception as e:
                    logger.warning("canuint_transcript_fetch_error", recording_id=recording_id, error=str(e))
                    continue

                # Extract area info
                area_id = None
                area_name = None
                area_link = soup.find("a", class_="area")
                if area_link:
                    area_match = re.search(r"/(\d+)$", area_link.get("href", ""))
                    if area_match:
                        area_id = area_match.group(1)
                    area_name = area_link.get_text(strip=True)

                # Extract transcript segments
                transcript_container = soup.find(class_="transcript")
                if not transcript_container:
                    continue

                segment_index = 0
                for segment in transcript_container.find_all("span", class_="segment"):
                    start_time = _safe_float(segment.get("data-start"))
                    end_time = _safe_float(segment.get("data-end"))

                    # Extract dialectal text
                    text_elem = segment.find("span", class_="text")
                    text = text_elem.get_text(strip=True) if text_elem else None

                    # Extract standardized form
                    standardized_form = None
                    stext_elem = segment.find("span", class_="stext")
                    if stext_elem:
                        stext_link = stext_elem.find("a")
                        if stext_link:
                            standardized_form = stext_link.get_text(strip=True)

                    if text:
                        yield {
                            "segment_id": f"{recording_id}_{segment_index}",
                            "recording_id": recording_id,
                            "area_id": area_id,
                            "area_name": area_name,
                            "segment_index": segment_index,
                            "start_time": start_time,
                            "end_time": end_time,
                            "text": text,
                            "standardized_form": standardized_form,
                            "source_url": f"{CANUINT_BASE}/{language}/{recording_id}",
                        }
                        segment_index += 1

    yield areas_resource
    yield recordings_resource
    yield transcripts_resource
