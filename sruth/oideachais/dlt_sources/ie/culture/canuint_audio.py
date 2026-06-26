"""
Culture IE source: canuint_audio_source

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

def canuint_audio_source(
    dialect: str = "connacht",
    max_recordings: int = 100,
    transcribed_only: bool = True,
) -> Iterator[DltResource]:
    """
    Source for downloading Canúint.ie audio files for TTS training.

    Downloads audio files and creates TTS training pairs:
    - Audio segments with transcriptions
    - Dialect metadata for multi-voice training
    - Standardized and dialectal text pairs

    Args:
        dialect: Irish dialect (connacht, munster, ulster)
        max_recordings: Maximum recordings to download
        transcribed_only: Only download transcribed recordings

    Yields:
        DLT resources for audio metadata and training pairs
    """
    import hashlib

    dialect_provinces = {
        "connacht": "Cúige Connacht",
        "munster": "Cúige Mumhan",
        "ulster": "Cúige Uladh",
    }

    province = dialect_provinces.get(dialect, dialect)

    @dlt.resource(
        name="audio_files",
        write_disposition="merge",
        primary_key="audio_id",
    )
    def audio_files_resource() -> Iterator[dict]:
        """Extract audio file metadata for download."""
        factory = _get_canuint_factory()

        with factory.create_client() as client:
            try:
                response = client.get("/ga/")
                response.raise_for_status()
                soup = BeautifulSoup(response.text, "html.parser")
            except Exception as e:
                logger.warning("canuint_audio_list_error", error=str(e))
                return

            # Find areas in the target dialect region
            location_pattern = re.compile(r"https://www\.canuint\.ie/ga/(\d+)")
            area_ids = []

            for link in soup.find_all("a", href=location_pattern):
                # Check if this area is in the target province
                province_elem = link.find_parent(class_="province-section")
                if province_elem:
                    province_header = province_elem.find(class_="province")
                    if province_header and province in province_header.get_text():
                        match = location_pattern.search(link["href"])
                        if match:
                            area_ids.append(match.group(1))

            recording_count = 0
            for area_id in set(area_ids):
                if recording_count >= max_recordings:
                    break

                try:
                    response = client.get(f"/ga/{area_id}")
                    response.raise_for_status()
                    soup = BeautifulSoup(response.text, "html.parser")
                except Exception as e:
                    logger.warning("canuint_audio_area_error", area_id=area_id, error=str(e))
                    continue

                # Extract area metadata
                area_name = None
                hometown_elem = soup.find(attrs={"data-hometown-name": True})
                if hometown_elem:
                    area_name = hometown_elem.get("data-hometown-name")

                for recording_elem in soup.find_all("li", class_="recording"):
                    if recording_count >= max_recordings:
                        break

                    is_transcribed = recording_elem.get("data-is-transcribed") == "1"
                    if transcribed_only and not is_transcribed:
                        continue

                    recording_link = recording_elem.find("a", href=re.compile(r"/[A-Z]+\d+c\d+"))
                    if not recording_link:
                        continue

                    match = re.search(r"([A-Z]+\d+c\d+)", recording_link["href"])
                    if not match:
                        continue

                    recording_id = match.group(1)
                    audio_url = f"{CANUINT_BASE}/sounds/{recording_id}.mp3"
                    audio_hash = hashlib.sha256(audio_url.encode()).hexdigest()[:16]

                    # Extract speaker info
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

                    recording_count += 1

                    yield {
                        "audio_id": f"{dialect}_{recording_id}",
                        "recording_id": recording_id,
                        "audio_url": audio_url,
                        "audio_hash": audio_hash,
                        "dialect": dialect,
                        "province": province,
                        "area_id": area_id,
                        "area_name": area_name,
                        "speaker_name": speaker_name,
                        "year": year,
                        "is_transcribed": is_transcribed,
                        "storage_path": f"r2://canuint/audio/{dialect}/{recording_id}_{audio_hash}.mp3",
                    }

    @dlt.resource(
        name="tts_pairs",
        write_disposition="append",
        primary_key="pair_id",
    )
    def tts_training_pairs_resource() -> Iterator[dict]:
        """Generate TTS training pairs (audio segment + text)."""
        factory = _get_canuint_factory()

        with factory.create_client() as client:
            # Get transcribed recording IDs from the dialect region
            try:
                response = client.get("/ga/")
                response.raise_for_status()
                soup = BeautifulSoup(response.text, "html.parser")
            except Exception as e:
                logger.warning("canuint_tts_list_error", error=str(e))
                return

            # Find areas in target province
            location_pattern = re.compile(r"https://www\.canuint\.ie/ga/(\d+)")
            area_ids = []

            for link in soup.find_all("a", href=location_pattern):
                province_elem = link.find_parent(class_="province-section")
                if province_elem:
                    province_header = province_elem.find(class_="province")
                    if province_header and province in province_header.get_text():
                        match = location_pattern.search(link["href"])
                        if match:
                            area_ids.append(match.group(1))

            recording_ids = []
            for area_id in set(area_ids):
                try:
                    response = client.get(f"/ga/{area_id}")
                    response.raise_for_status()
                    soup = BeautifulSoup(response.text, "html.parser")

                    for recording_elem in soup.find_all("li", class_="recording"):
                        if recording_elem.get("data-is-transcribed") != "1":
                            continue

                        recording_link = recording_elem.find("a", href=re.compile(r"/[A-Z]+\d+c\d+"))
                        if recording_link:
                            match = re.search(r"([A-Z]+\d+c\d+)", recording_link["href"])
                            if match and len(recording_ids) < max_recordings:
                                recording_ids.append(match.group(1))
                except Exception as e:
                    logger.warning("canuint_tts_area_error", area_id=area_id, error=str(e))
                    continue

            # Extract TTS pairs from transcripts
            pair_count = 0
            for recording_id in set(recording_ids):
                try:
                    response = client.get(f"/ga/{recording_id}")
                    response.raise_for_status()
                    soup = BeautifulSoup(response.text, "html.parser")
                except Exception as e:
                    logger.warning("canuint_tts_recording_error", recording_id=recording_id, error=str(e))
                    continue

                # Get area info
                area_name = None
                area_link = soup.find("a", class_="area")
                if area_link:
                    area_name = area_link.get_text(strip=True)

                transcript_container = soup.find(class_="transcript")
                if not transcript_container:
                    continue

                for segment in transcript_container.find_all("span", class_="segment"):
                    start_time = _safe_float(segment.get("data-start"))
                    end_time = _safe_float(segment.get("data-end"))

                    if start_time is None or end_time is None:
                        continue

                    duration = end_time - start_time
                    if duration < 0.5 or duration > 30:  # Filter by duration
                        continue

                    text_elem = segment.find("span", class_="text")
                    text = text_elem.get_text(strip=True) if text_elem else None

                    standardized_form = None
                    stext_elem = segment.find("span", class_="stext")
                    if stext_elem:
                        stext_link = stext_elem.find("a")
                        if stext_link:
                            standardized_form = stext_link.get_text(strip=True)

                    if text and len(text) >= 3:  # Minimum text length
                        pair_count += 1
                        yield {
                            "pair_id": f"{dialect}_{recording_id}_{pair_count}",
                            "recording_id": recording_id,
                            "dialect": dialect,
                            "area_name": area_name,
                            "audio_url": f"{CANUINT_BASE}/sounds/{recording_id}.mp3",
                            "start_time": start_time,
                            "end_time": end_time,
                            "duration": duration,
                            "text": text,
                            "standardized_form": standardized_form,
                            # LJSpeech-style format
                            "ljspeech_id": f"{dialect}_{recording_id}_{pair_count:04d}",
                            "ljspeech_text": standardized_form or text,
                        }

    yield audio_files_resource
    yield tts_training_pairs_resource
