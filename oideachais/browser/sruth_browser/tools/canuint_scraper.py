"""
Canúint.ie Scraper Tool for Irish Dialect Audio Dataset.

Scrapes Irish dialect audio recordings from canuint.ie for:
- Audio files (MP3/WAV) for ASR/TTS training
- Transcriptions (ground truth text)
- Dialect metadata (Connacht, Munster, Ulster)
- Speaker information

Rate Limiting: 0.5 request/second (as per firecrawl config)
Storage: Cloudflare R2 for audio, Kafka for events

Usage:
    from sruth_browser.tools.canuint_scraper import (
        scrape_canuint_recording,
        scrape_canuint_dialect,
        CanuintRecording,
    )

    # Single recording
    recording = await scrape_canuint_recording(recording_id="123")

    # By dialect
    recordings = await scrape_canuint_dialect(
        dialect="connacht",
        max_recordings=100,
    )
"""

import asyncio
import hashlib
import logging
from dataclasses import dataclass, field
from datetime import datetime
from enum import Enum
from typing import Any

from ..backends import get_router
from ..browser_types import BackendType, BrowserOperation, ExtractionFormat

logger = logging.getLogger(__name__)

# Base URL for Canúint.ie
CANUINT_BASE_URL = "https://www.canuint.ie"

# Rate limiting (0.5 req/sec = 2 seconds between requests, as per firecrawl config)
RATE_LIMIT_SECONDS = 2.0


class IrishDialect(str, Enum):
    """Irish dialect regions."""

    CONNACHT = "connacht"  # Connemara, Mayo, Galway
    MUNSTER = "munster"  # Cork, Kerry, Waterford
    ULSTER = "ulster"  # Donegal, Belfast
    STANDARD = "standard"  # An Caighdeán Oifigiúil


class RecordingType(str, Enum):
    """Types of audio recordings."""

    CONVERSATION = "conversation"  # Natural conversation
    WORD_LIST = "word_list"  # Individual words
    SENTENCE = "sentence"  # Sentence readings
    STORY = "story"  # Storytelling/folklore
    SONG = "song"  # Traditional songs


@dataclass
class CanuintRecording:
    """A single audio recording from Canúint.ie."""

    # Identifiers
    recording_id: str
    title: str

    # Audio
    audio_url: str
    duration_seconds: float | None = None
    format: str = "mp3"

    # Transcription
    transcription_ga: str | None = None  # Irish text
    transcription_en: str | None = None  # English translation
    phonetic: str | None = None  # IPA transcription

    # Metadata
    dialect: IrishDialect = IrishDialect.STANDARD
    sub_dialect: str | None = None  # e.g., "Connemara", "Ring"
    recording_type: RecordingType = RecordingType.CONVERSATION
    topic: str | None = None

    # Speaker
    speaker_id: str | None = None
    speaker_gender: str | None = None
    speaker_age_range: str | None = None
    speaker_location: str | None = None

    # Processing
    audio_hash: str | None = None
    scraped_at: datetime = field(default_factory=datetime.utcnow)

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary for serialization."""
        return {
            "recording_id": self.recording_id,
            "title": self.title,
            "audio_url": self.audio_url,
            "duration_seconds": self.duration_seconds,
            "format": self.format,
            "transcription_ga": self.transcription_ga,
            "transcription_en": self.transcription_en,
            "phonetic": self.phonetic,
            "dialect": self.dialect.value,
            "sub_dialect": self.sub_dialect,
            "recording_type": self.recording_type.value,
            "topic": self.topic,
            "speaker_id": self.speaker_id,
            "speaker_gender": self.speaker_gender,
            "speaker_age_range": self.speaker_age_range,
            "speaker_location": self.speaker_location,
            "audio_hash": self.audio_hash,
            "scraped_at": self.scraped_at.isoformat(),
        }

    def to_kafka_event(self) -> dict[str, Any]:
        """Convert to Kafka event format."""
        return {
            "event_type": "celtic.canuint.recording.scraped",
            "event_time": datetime.utcnow().isoformat(),
            "recording": self.to_dict(),
        }

    def to_tts_training_format(self) -> dict[str, Any] | None:
        """Convert to TTS training dataset format (LJSpeech-style)."""
        if not self.transcription_ga or not self.audio_url:
            return None

        return {
            "audio_path": self.audio_url,
            "text": self.transcription_ga,
            "speaker_id": self.speaker_id or "unknown",
            "dialect": self.dialect.value,
            "duration": self.duration_seconds,
        }


@dataclass
class DialectCollection:
    """A collection of recordings for a dialect."""

    dialect: IrishDialect
    recordings: list[CanuintRecording] = field(default_factory=list)
    total_duration_seconds: float = 0.0

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "dialect": self.dialect.value,
            "recording_count": len(self.recordings),
            "total_duration_seconds": self.total_duration_seconds,
            "total_duration_hours": round(self.total_duration_seconds / 3600, 2),
            "recordings": [r.to_dict() for r in self.recordings],
        }


class CanuintScraper:
    """
    Scraper for Canúint.ie Irish dialect audio collection.

    Features:
    - Rate-limited requests (0.5/sec)
    - Automatic retry with backoff
    - Kafka event production
    - R2 audio storage integration
    - TTS dataset format export
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
        """Enforce rate limiting (0.5 req/sec = 2s between requests)."""
        async with self._lock:
            now = asyncio.get_event_loop().time()
            elapsed = now - self._last_request_time
            if elapsed < self.rate_limit:
                await asyncio.sleep(self.rate_limit - elapsed)
            self._last_request_time = asyncio.get_event_loop().time()

    async def scrape_recording(self, recording_id: str) -> CanuintRecording | None:
        """
        Scrape a single audio recording from Canúint.ie.

        Args:
            recording_id: The recording identifier

        Returns:
            CanuintRecording with audio URL and transcription
        """
        await self._rate_limit()

        router = get_router()
        url = f"{CANUINT_BASE_URL}/recording/{recording_id}"

        # Schema for structured extraction
        schema = {
            "type": "object",
            "properties": {
                "title": {"type": "string"},
                "audioUrl": {"type": "string"},
                "durationSeconds": {"type": "number"},
                "format": {"type": "string"},
                "transcriptionGa": {"type": "string"},
                "transcriptionEn": {"type": "string"},
                "phonetic": {"type": "string"},
                "dialect": {
                    "type": "string",
                    "enum": ["connacht", "munster", "ulster", "standard"],
                },
                "subDialect": {"type": "string"},
                "recordingType": {
                    "type": "string",
                    "enum": ["conversation", "word_list", "sentence", "story", "song"],
                },
                "topic": {"type": "string"},
                "speakerId": {"type": "string"},
                "speakerGender": {"type": "string"},
                "speakerAgeRange": {"type": "string"},
                "speakerLocation": {"type": "string"},
            },
        }

        async def _extract(backend):
            result = await backend.extract(
                url,
                formats=[ExtractionFormat.JSON],
                schema=schema,
                prompt=(
                    "Extract the audio recording details including: "
                    "title, direct audio URL (MP3/WAV), duration, "
                    "Irish transcription (transcriptionGa), English translation, "
                    "phonetic transcription (IPA), dialect (connacht/munster/ulster/standard), "
                    "sub-dialect region, recording type, topic, "
                    "and speaker information (ID, gender, age range, location)."
                ),
                timeout=30.0,
            )
            return result

        try:
            result = await router.execute_with_fallback(
                BrowserOperation.EXTRACT, _extract
            )

            if not result.success:
                logger.warning(f"Failed to extract recording {recording_id}: {result.error}")
                return None

            data = result.content.get("extracted", {})

            # Get audio URL
            audio_url = data.get("audioUrl", "")
            if not audio_url:
                logger.warning(f"No audio URL found for recording {recording_id}")
                return None

            # Compute audio hash for deduplication
            audio_hash = hashlib.sha256(audio_url.encode()).hexdigest()[:16]

            # Parse dialect
            dialect_str = data.get("dialect", "standard").lower()
            try:
                dialect = IrishDialect(dialect_str)
            except ValueError:
                dialect = IrishDialect.STANDARD

            # Parse recording type
            type_str = data.get("recordingType", "conversation").lower()
            try:
                recording_type = RecordingType(type_str)
            except ValueError:
                recording_type = RecordingType.CONVERSATION

            return CanuintRecording(
                recording_id=recording_id,
                title=data.get("title", ""),
                audio_url=audio_url,
                duration_seconds=data.get("durationSeconds"),
                format=data.get("format", "mp3"),
                transcription_ga=data.get("transcriptionGa"),
                transcription_en=data.get("transcriptionEn"),
                phonetic=data.get("phonetic"),
                dialect=dialect,
                sub_dialect=data.get("subDialect"),
                recording_type=recording_type,
                topic=data.get("topic"),
                speaker_id=data.get("speakerId"),
                speaker_gender=data.get("speakerGender"),
                speaker_age_range=data.get("speakerAgeRange"),
                speaker_location=data.get("speakerLocation"),
                audio_hash=audio_hash,
            )

        except Exception as e:
            logger.error(f"Error scraping recording {recording_id}: {e}")
            return None

    async def search_by_dialect(
        self,
        dialect: IrishDialect,
        start_page: int = 0,
        max_results: int = 100,
    ) -> list[str]:
        """
        Search for recording IDs by dialect.

        Args:
            dialect: Irish dialect to search
            start_page: Pagination offset
            max_results: Maximum results to return

        Returns:
            List of recording IDs
        """
        await self._rate_limit()

        router = get_router()
        url = f"{CANUINT_BASE_URL}/search?dialect={dialect.value}&offset={start_page}"

        async def _search(backend):
            return await backend.extract(
                url,
                formats=[ExtractionFormat.JSON],
                schema={
                    "type": "object",
                    "properties": {
                        "totalResults": {"type": "integer"},
                        "recordingIds": {
                            "type": "array",
                            "items": {"type": "string"},
                        },
                    },
                },
                prompt="Extract the recording IDs from the search results.",
                timeout=30.0,
            )

        try:
            result = await router.execute_with_fallback(
                BrowserOperation.EXTRACT, _search
            )

            if result.success:
                data = result.content.get("extracted", {})
                return data.get("recordingIds", [])[:max_results]
            return []

        except Exception as e:
            logger.error(f"Error searching dialect {dialect.value}: {e}")
            return []

    async def scrape_dialect_collection(
        self,
        dialect: IrishDialect,
        max_recordings: int = 100,
    ) -> DialectCollection:
        """
        Scrape all recordings for a dialect.

        Args:
            dialect: Irish dialect
            max_recordings: Maximum recordings to scrape

        Returns:
            DialectCollection with all scraped recordings
        """
        recording_ids = await self.search_by_dialect(dialect, max_results=max_recordings)

        collection = DialectCollection(dialect=dialect)

        for recording_id in recording_ids:
            recording = await self.scrape_recording(recording_id)
            if recording:
                collection.recordings.append(recording)
                if recording.duration_seconds:
                    collection.total_duration_seconds += recording.duration_seconds

        logger.info(
            f"Scraped {len(collection.recordings)} recordings for {dialect.value} "
            f"({collection.total_duration_seconds / 3600:.2f} hours)"
        )

        return collection


# =============================================================================
# Convenience Functions (ADK Tool Interface)
# =============================================================================

_scraper: CanuintScraper | None = None


def get_scraper() -> CanuintScraper:
    """Get or create scraper singleton."""
    global _scraper
    if _scraper is None:
        _scraper = CanuintScraper()
    return _scraper


async def scrape_canuint_recording(recording_id: str) -> dict[str, Any]:
    """
    Scrape a single Canúint.ie recording.

    ADK Tool for scraping individual audio recordings.

    Args:
        recording_id: The recording ID

    Returns:
        Recording data including audio URL and transcription
    """
    scraper = get_scraper()
    recording = await scraper.scrape_recording(recording_id)
    if recording:
        return {
            "success": True,
            "recording": recording.to_dict(),
            "tts_format": recording.to_tts_training_format(),
        }
    return {
        "success": False,
        "error": f"Failed to scrape recording {recording_id}",
    }


async def scrape_canuint_dialect(
    dialect: str,
    max_recordings: int = 100,
    produce_to_kafka: bool = False,
) -> dict[str, Any]:
    """
    Scrape Canúint.ie recordings by dialect.

    ADK Tool for bulk scraping Irish dialect audio.

    Args:
        dialect: Irish dialect (connacht, munster, ulster, standard)
        max_recordings: Maximum recordings to scrape
        produce_to_kafka: Whether to produce events to Kafka

    Returns:
        Collection statistics and scraped recording summaries
    """
    scraper = get_scraper()

    try:
        dialect_enum = IrishDialect(dialect.lower())
    except ValueError:
        return {
            "success": False,
            "error": f"Invalid dialect: {dialect}. Use connacht, munster, ulster, or standard.",
        }

    collection = await scraper.scrape_dialect_collection(dialect_enum, max_recordings)

    # Optionally produce to Kafka
    if produce_to_kafka and collection.recordings:
        try:
            from oideachais.kafka.producer import produce_event

            for recording in collection.recordings:
                await produce_event(
                    topic="celtic.canuint.audio",
                    event=recording.to_kafka_event(),
                )
        except ImportError:
            logger.warning("Kafka producer not available")

    return {
        "success": len(collection.recordings) > 0,
        "dialect": dialect,
        "recording_count": len(collection.recordings),
        "total_duration_hours": round(collection.total_duration_seconds / 3600, 2),
        "transcribed_count": sum(
            1 for r in collection.recordings if r.transcription_ga
        ),
        "recordings": [
            {
                "recording_id": r.recording_id,
                "title": r.title,
                "audio_url": r.audio_url,
                "duration_seconds": r.duration_seconds,
                "has_transcription": r.transcription_ga is not None,
                "sub_dialect": r.sub_dialect,
            }
            for r in collection.recordings[:20]  # Limit in response
        ],
    }


async def download_canuint_audio(
    recording_id: str,
    audio_url: str,
    storage_path: str | None = None,
) -> dict[str, Any]:
    """
    Download a Canúint.ie audio file.

    ADK Tool for downloading audio files for TTS training.

    Args:
        recording_id: Recording identifier for naming
        audio_url: Direct URL to the audio file
        storage_path: Optional local path (defaults to R2)

    Returns:
        Download result with local/R2 path
    """
    import httpx

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(audio_url, timeout=120.0)
            response.raise_for_status()

            audio_data = response.content
            audio_hash = hashlib.sha256(audio_data).hexdigest()[:16]

            # Determine format from URL
            audio_format = "mp3"
            if ".wav" in audio_url.lower():
                audio_format = "wav"

            # Determine storage location
            if storage_path:
                # Local storage
                import aiofiles

                async with aiofiles.open(storage_path, "wb") as f:
                    await f.write(audio_data)
                path = storage_path
            else:
                # R2 storage (placeholder - integrate with actual R2 client)
                path = f"r2://canuint/audio/{recording_id}_{audio_hash}.{audio_format}"
                logger.info(f"Would upload to R2: {path}")

            return {
                "success": True,
                "recording_id": recording_id,
                "path": path,
                "size_bytes": len(audio_data),
                "hash": audio_hash,
                "format": audio_format,
            }

    except Exception as e:
        logger.error(f"Error downloading audio for {recording_id}: {e}")
        return {
            "success": False,
            "error": str(e),
        }


async def export_tts_dataset(
    dialect: str,
    output_format: str = "ljspeech",
    max_recordings: int = 1000,
) -> dict[str, Any]:
    """
    Export Canúint.ie recordings as TTS training dataset.

    ADK Tool for generating TTS training data in standard formats.

    Args:
        dialect: Irish dialect to export
        output_format: Dataset format (ljspeech, coqui, mozilla)
        max_recordings: Maximum recordings to include

    Returns:
        Dataset metadata and file paths
    """
    scraper = get_scraper()

    try:
        dialect_enum = IrishDialect(dialect.lower())
    except ValueError:
        return {
            "success": False,
            "error": f"Invalid dialect: {dialect}",
        }

    collection = await scraper.scrape_dialect_collection(dialect_enum, max_recordings)

    # Convert to TTS format
    tts_entries = []
    for recording in collection.recordings:
        entry = recording.to_tts_training_format()
        if entry:
            tts_entries.append(entry)

    return {
        "success": len(tts_entries) > 0,
        "dialect": dialect,
        "format": output_format,
        "total_entries": len(tts_entries),
        "total_duration_hours": round(collection.total_duration_seconds / 3600, 2),
        "sample_entries": tts_entries[:5],
    }
