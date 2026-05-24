"""
DLT Source for Canuint.ie Irish Pronunciation Database.

Extracts:
- Geographic areas (Gaeltacht regions)
- Audio recordings with speaker metadata
- Timestamped transcription segments

Based on API documentation in canuint.json.

Uses HttpClientFactory for resilient HTTP client with:
- Circuit breaker pattern
- Rate limiting
- Automatic retries
"""
from __future__ import annotations

import re
from collections.abc import Iterator

import dlt
from bs4 import BeautifulSoup
from dlt.sources import DltResource
from observability.logging import get_logger
from sruth.shared.http import canuint_client

logger = get_logger(__name__)

# Base URL
CANUINT_BASE = "https://www.canuint.ie"


def _get_canuint_factory():
    """Get HTTP client factory for Canúint.ie."""
    return canuint_client()


@dlt.source(name="canuint_pronunciation")
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


@dlt.source(name="canuint_search")
def canuint_search_source(
    query: str,
    language: str = "ga",
    max_results: int = 100,
) -> Iterator[DltResource]:
    """
    Search Canuint.ie for specific words or phrases.

    Args:
        query: Search term
        language: Interface language ('ga' or 'en')
        max_results: Maximum results to return

    Yields:
        DLT resource for search results
    """

    @dlt.resource(
        name="search_results",
        write_disposition="append",
        primary_key="result_id",
    )
    def search_results_resource() -> Iterator[dict]:
        """Search for pronunciation recordings."""
        factory = _get_canuint_factory()
        search_path = "cuardach" if language == "ga" else "search"

        with factory.create_client() as client:
            try:
                response = client.get(f"/{language}/{search_path}", params={"t": query})
                response.raise_for_status()
            except Exception as e:
                logger.warning("canuint_search_error", query=query, error=str(e))
                return

            soup = BeautifulSoup(response.text, "html.parser")

            result_count = 0
            for result in soup.find_all("li", class_="recording"):
                if result_count >= max_results:
                    break

                # Extract recording ID
                recording_link = result.find("a", href=re.compile(r"/[A-Z]+\d+c\d+"))
                if not recording_link:
                    continue

                match = re.search(r"([A-Z]+\d+c\d+)", recording_link["href"])
                if not match:
                    continue

                recording_id = match.group(1)

                # Extract metadata
                is_transcribed = result.get("data-is-transcribed") == "1"

                year = None
                year_elem = result.find("span", class_="year")
                if year_elem:
                    year_text = year_elem.get_text(strip=True)
                    if year_text.isdigit():
                        year = int(year_text)

                # Extract area info
                area_link = result.find("a", class_="area")
                area_name = area_link.get_text(strip=True) if area_link else None

                result_count += 1

                yield {
                    "result_id": f"{query}_{recording_id}",
                    "query": query,
                    "recording_id": recording_id,
                    "area_name": area_name,
                    "year": year,
                    "is_transcribed": is_transcribed,
                    "audio_url": f"{CANUINT_BASE}/sounds/{recording_id}.mp3",
                    "source_url": f"{CANUINT_BASE}/{language}/{search_path}?t={query}",
                }

    yield search_results_resource


def _safe_float(value: str | None) -> float | None:
    """Safely convert to float."""
    if value:
        try:
            return float(value)
        except ValueError:
            pass
    return None


# =============================================================================
# Audio Download and TTS Dataset Sources
# =============================================================================

@dlt.source(name="canuint_audio_download")
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


@dlt.source(name="canuint_dialect_summary")
def canuint_dialect_summary_source() -> Iterator[DltResource]:
    """
    Source for Canúint.ie dialect statistics.

    Aggregates:
    - Total recordings per dialect
    - Transcription coverage
    - Speaker diversity
    - Duration statistics
    """

    @dlt.resource(
        name="dialect_stats",
        write_disposition="replace",
        primary_key="dialect",
    )
    def dialect_stats_resource() -> Iterator[dict]:
        """Generate dialect statistics for training planning."""
        factory = _get_canuint_factory()
        dialects = {
            "connacht": "Cúige Connacht",
            "munster": "Cúige Mumhan",
            "ulster": "Cúige Uladh",
        }

        with factory.create_client() as client:
            try:
                response = client.get("/ga/")
                response.raise_for_status()
                soup = BeautifulSoup(response.text, "html.parser")
            except Exception as e:
                logger.warning("canuint_dialect_stats_error", error=str(e))
                return

            for dialect, province in dialects.items():
                location_pattern = re.compile(r"https://www\.canuint\.ie/ga/(\d+)")
                area_count = 0
                recording_estimate = 0

                for link in soup.find_all("a", href=location_pattern):
                    province_elem = link.find_parent(class_="province-section")
                    if province_elem:
                        province_header = province_elem.find(class_="province")
                        if province_header and province in province_header.get_text():
                            area_count += 1
                            recording_estimate += 10  # Rough estimate

                yield {
                    "dialect": dialect,
                    "province": province,
                    "area_count": area_count,
                    "estimated_recordings": recording_estimate,
                    "priority": "high" if dialect == "connacht" else "medium",
                }

    yield dialect_stats_resource


# =============================================================================
# Word-Level Alignment Source for ASR/TTS Training
# =============================================================================

@dlt.source(name="canuint_word_alignment")
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
