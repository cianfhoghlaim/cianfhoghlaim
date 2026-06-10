"""
Audio download and slicing pipeline for Canuint.ie word-level alignment.

Downloads full MP3 recordings and slices them at word boundaries to create:
- Individual word audio clips (16kHz mono WAV)
- LJSpeech-format metadata
- R2 storage upload support

Uses pydub for audio processing with ffmpeg backend.
"""
from __future__ import annotations

import json
import tempfile
from collections.abc import Iterator
from dataclasses import dataclass
from pathlib import Path

import httpx
from pydub import AudioSegment
from oideachais.observability.logging import get_logger

logger = get_logger(__name__)

# Audio processing constants
TARGET_SAMPLE_RATE = 16000  # 16kHz for ASR
TARGET_CHANNELS = 1  # Mono
WORD_PADDING_MS = 25  # Padding around word boundaries
MIN_DURATION_MS = 50
MAX_DURATION_MS = 10000  # 10 seconds max


@dataclass
class AudioSlice:
    """Represents a sliced audio segment."""

    word_id: str
    recording_id: str
    audio_path: Path
    start_time: float
    end_time: float
    duration_ms: int
    text: str
    dialect: str
    speaker_name: str | None = None
    sample_rate: int = TARGET_SAMPLE_RATE


@dataclass
class SlicingStats:
    """Statistics for audio slicing operation."""

    total_recordings: int = 0
    successful_downloads: int = 0
    failed_downloads: int = 0
    total_slices: int = 0
    total_duration_seconds: float = 0.0
    skipped_too_short: int = 0
    skipped_too_long: int = 0


class CanuintAudioSlicer:
    """
    Download and slice Canuint.ie audio recordings at word boundaries.

    Usage:
        slicer = CanuintAudioSlicer(output_dir=Path("./wavs"))
        slices = slicer.process_recording(
            recording_id="QQTRIN016177",
            word_alignments=[...],
        )
    """

    def __init__(
        self,
        output_dir: Path,
        cache_dir: Path | None = None,
        target_sample_rate: int = TARGET_SAMPLE_RATE,
        word_padding_ms: int = WORD_PADDING_MS,
        min_duration_ms: int = MIN_DURATION_MS,
        max_duration_ms: int = MAX_DURATION_MS,
    ):
        """
        Initialize the audio slicer.

        Args:
            output_dir: Directory for output WAV files
            cache_dir: Directory for caching downloaded MP3s (optional)
            target_sample_rate: Target sample rate (default 16kHz)
            word_padding_ms: Padding around word boundaries
            min_duration_ms: Minimum word duration to include
            max_duration_ms: Maximum word duration to include
        """
        self.output_dir = output_dir
        self.cache_dir = cache_dir or Path(tempfile.gettempdir()) / "canuint_cache"
        self.target_sample_rate = target_sample_rate
        self.word_padding_ms = word_padding_ms
        self.min_duration_ms = min_duration_ms
        self.max_duration_ms = max_duration_ms

        # Create directories
        self.output_dir.mkdir(parents=True, exist_ok=True)
        self.cache_dir.mkdir(parents=True, exist_ok=True)

        self.stats = SlicingStats()

    def _download_audio(
        self,
        audio_url: str,
        recording_id: str,
    ) -> Path | None:
        """
        Download audio file from Canuint.ie.

        Args:
            audio_url: URL to download
            recording_id: Recording identifier for caching

        Returns:
            Path to downloaded file or None on failure
        """
        cache_path = self.cache_dir / f"{recording_id}.mp3"

        # Check cache first
        if cache_path.exists():
            logger.debug("audio_cache_hit", recording_id=recording_id)
            return cache_path

        try:
            with httpx.Client(timeout=60.0) as client:
                response = client.get(audio_url)
                response.raise_for_status()

                # Write to cache
                cache_path.write_bytes(response.content)
                logger.info("audio_download_success",
                           recording_id=recording_id,
                           size_bytes=len(response.content))

                self.stats.successful_downloads += 1
                return cache_path

        except Exception as e:
            logger.warning("audio_download_error",
                          recording_id=recording_id,
                          url=audio_url,
                          error=str(e))
            self.stats.failed_downloads += 1
            return None

    def _load_audio(self, audio_path: Path) -> AudioSegment | None:
        """
        Load audio file into pydub AudioSegment.

        Args:
            audio_path: Path to audio file

        Returns:
            AudioSegment or None on failure
        """
        try:
            audio = AudioSegment.from_file(str(audio_path))

            # Convert to target format
            audio = audio.set_frame_rate(self.target_sample_rate)
            audio = audio.set_channels(TARGET_CHANNELS)

            return audio

        except Exception as e:
            logger.warning("audio_load_error",
                          path=str(audio_path),
                          error=str(e))
            return None

    def _slice_word(
        self,
        audio: AudioSegment,
        word_alignment: dict,
        dialect_subdir: str,
    ) -> AudioSlice | None:
        """
        Slice a word from the full audio.

        Args:
            audio: Full recording AudioSegment
            word_alignment: Word alignment dict with timestamps
            dialect_subdir: Subdirectory for this dialect

        Returns:
            AudioSlice or None if skipped
        """
        start_time = word_alignment["start_time"]
        end_time = word_alignment["end_time"]
        duration_ms = int((end_time - start_time) * 1000)

        # Duration filtering
        if duration_ms < self.min_duration_ms:
            self.stats.skipped_too_short += 1
            return None

        if duration_ms > self.max_duration_ms:
            self.stats.skipped_too_long += 1
            return None

        # Calculate slice boundaries with padding
        start_ms = max(0, int(start_time * 1000) - self.word_padding_ms)
        end_ms = min(len(audio), int(end_time * 1000) + self.word_padding_ms)

        # Extract word audio
        word_audio = audio[start_ms:end_ms]

        # Prepare output path
        word_id = word_alignment["word_id"]
        dialect = word_alignment.get("dialect", "unknown")

        # Create dialect subdirectory
        dialect_dir = self.output_dir / dialect
        dialect_dir.mkdir(parents=True, exist_ok=True)

        output_path = dialect_dir / f"{word_id}.wav"

        try:
            # Export as WAV
            word_audio.export(
                str(output_path),
                format="wav",
                parameters=["-ar", str(self.target_sample_rate), "-ac", "1"],
            )

            self.stats.total_slices += 1
            self.stats.total_duration_seconds += (end_ms - start_ms) / 1000.0

            return AudioSlice(
                word_id=word_id,
                recording_id=word_alignment["recording_id"],
                audio_path=output_path,
                start_time=start_time,
                end_time=end_time,
                duration_ms=end_ms - start_ms,
                text=word_alignment.get("dialectal_text", ""),
                dialect=dialect,
                speaker_name=word_alignment.get("speaker_name"),
                sample_rate=self.target_sample_rate,
            )

        except Exception as e:
            logger.warning("word_slice_error",
                          word_id=word_id,
                          error=str(e))
            return None

    def process_recording(
        self,
        recording_id: str,
        audio_url: str,
        word_alignments: list[dict],
    ) -> list[AudioSlice]:
        """
        Process a single recording: download and slice all words.

        Args:
            recording_id: Recording identifier
            audio_url: URL to download audio
            word_alignments: List of word alignment dicts

        Returns:
            List of AudioSlice objects
        """
        self.stats.total_recordings += 1

        # Download audio
        audio_path = self._download_audio(audio_url, recording_id)
        if not audio_path:
            return []

        # Load audio
        audio = self._load_audio(audio_path)
        if audio is None:
            return []

        # Filter alignments for this recording
        recording_words = [
            w for w in word_alignments
            if w.get("recording_id") == recording_id
        ]

        # Slice each word
        slices = []
        for word_alignment in recording_words:
            dialect = word_alignment.get("dialect", "unknown")
            slice_result = self._slice_word(audio, word_alignment, dialect)
            if slice_result:
                slices.append(slice_result)

        logger.info("recording_processed",
                   recording_id=recording_id,
                   word_count=len(recording_words),
                   slice_count=len(slices))

        return slices

    def process_all_alignments(
        self,
        word_alignments: list[dict],
    ) -> Iterator[AudioSlice]:
        """
        Process all word alignments, downloading audio as needed.

        Args:
            word_alignments: List of all word alignment dicts

        Yields:
            AudioSlice objects
        """
        # Group alignments by recording
        recordings = {}
        for alignment in word_alignments:
            rec_id = alignment.get("recording_id")
            if rec_id not in recordings:
                recordings[rec_id] = {
                    "audio_url": alignment.get("audio_url"),
                    "words": [],
                }
            recordings[rec_id]["words"].append(alignment)

        # Process each recording
        for recording_id, data in recordings.items():
            slices = self.process_recording(
                recording_id=recording_id,
                audio_url=data["audio_url"],
                word_alignments=data["words"],
            )
            yield from slices

    def get_stats(self) -> dict:
        """Get processing statistics."""
        return {
            "total_recordings": self.stats.total_recordings,
            "successful_downloads": self.stats.successful_downloads,
            "failed_downloads": self.stats.failed_downloads,
            "total_slices": self.stats.total_slices,
            "total_duration_seconds": self.stats.total_duration_seconds,
            "skipped_too_short": self.stats.skipped_too_short,
            "skipped_too_long": self.stats.skipped_too_long,
        }


def generate_ljspeech_metadata(
    slices: list[AudioSlice],
    output_path: Path,
    use_relative_paths: bool = True,
    base_path: Path | None = None,
) -> None:
    """
    Generate LJSpeech-format metadata.csv.

    Format: filename|raw_text|normalized_text

    Args:
        slices: List of AudioSlice objects
        output_path: Path to output metadata.csv
        use_relative_paths: Use relative paths in metadata
        base_path: Base path for relative path calculation
    """
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, "w", encoding="utf-8") as f:
        for slice_obj in slices:
            if use_relative_paths and base_path:
                audio_path = slice_obj.audio_path.relative_to(base_path)
            else:
                audio_path = slice_obj.audio_path.stem  # Just filename without extension

            # LJSpeech format: filename|raw_text|normalized_text
            f.write(f"{audio_path}|{slice_obj.text}|{slice_obj.text.lower()}\n")

    logger.info("ljspeech_metadata_generated",
               path=str(output_path),
               count=len(slices))


def generate_extended_metadata(
    slices: list[AudioSlice],
    output_path: Path,
) -> None:
    """
    Generate extended metadata JSONL with full details.

    Args:
        slices: List of AudioSlice objects
        output_path: Path to output metadata.jsonl
    """
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, "w", encoding="utf-8") as f:
        for slice_obj in slices:
            record = {
                "word_id": slice_obj.word_id,
                "recording_id": slice_obj.recording_id,
                "audio_path": str(slice_obj.audio_path),
                "start_time": slice_obj.start_time,
                "end_time": slice_obj.end_time,
                "duration_ms": slice_obj.duration_ms,
                "text": slice_obj.text,
                "dialect": slice_obj.dialect,
                "speaker_name": slice_obj.speaker_name,
                "sample_rate": slice_obj.sample_rate,
            }
            f.write(json.dumps(record, ensure_ascii=False) + "\n")

    logger.info("extended_metadata_generated",
               path=str(output_path),
               count=len(slices))


# Convenience function for pipeline usage
def slice_canuint_audio(
    word_alignments_path: Path,
    output_dir: Path,
    cache_dir: Path | None = None,
) -> dict:
    """
    Slice Canuint audio from word alignments file.

    Args:
        word_alignments_path: Path to word alignments JSONL
        output_dir: Output directory for WAV files
        cache_dir: Cache directory for downloaded MP3s

    Returns:
        Processing statistics dict
    """
    # Load word alignments
    word_alignments = []
    with open(word_alignments_path, encoding="utf-8") as f:
        for line in f:
            if line.strip():
                word_alignments.append(json.loads(line))

    # Create slicer
    slicer = CanuintAudioSlicer(
        output_dir=output_dir,
        cache_dir=cache_dir,
    )

    # Process all alignments
    slices = list(slicer.process_all_alignments(word_alignments))

    # Generate metadata files
    generate_ljspeech_metadata(
        slices,
        output_dir / "metadata.csv",
        use_relative_paths=True,
        base_path=output_dir,
    )

    generate_extended_metadata(
        slices,
        output_dir / "metadata.jsonl",
    )

    return slicer.get_stats()
