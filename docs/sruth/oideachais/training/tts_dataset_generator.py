"""
TTS Dataset Generator for Irish.

Creates training data for Irish TTS models from:
- Canuint dialect recordings (existing DLT source)
- New commissioned recordings
- Transcribed audio from educational content

Based on /taighde/teanga/tts-dataset-generator/ patterns.
Output format: LJSpeech compatible for Chatterbox fine-tuning.

Usage:
    from training.tts_dataset_generator import TTSDatasetGenerator

    generator = TTSDatasetGenerator(output_dir="./datasets/irish_tts")
    generator.process_audio("recording.wav", language="ga")
"""

from __future__ import annotations

import asyncio
import csv
import hashlib
import logging
import os
import re
import shutil
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Iterator

logger = logging.getLogger(__name__)


@dataclass
class TTSSegment:
    """A segment of audio with transcription for TTS training."""

    audio_path: str
    transcript: str
    duration_ms: float
    speaker_id: str
    language: str = "ga"
    dialect: str | None = None  # connacht, munster, ulster
    metadata: dict[str, Any] = field(default_factory=dict)

    @property
    def segment_id(self) -> str:
        """Generate unique segment ID from content hash."""
        content = f"{self.audio_path}:{self.transcript}"
        return hashlib.md5(content.encode()).hexdigest()[:12]

    def to_ljspeech_row(self) -> tuple[str, str, str]:
        """Convert to LJSpeech format: (filename, text, normalized_text)."""
        # Normalize transcript for TTS
        normalized = self._normalize_irish_text(self.transcript)
        return (self.segment_id, self.transcript, normalized)

    def _normalize_irish_text(self, text: str) -> str:
        """Normalize Irish text for TTS training."""
        # Preserve fadas but normalize other characters
        text = text.strip()
        # Remove multiple spaces
        text = re.sub(r"\s+", " ", text)
        # Ensure consistent quotation marks
        text = text.replace(""", '"').replace(""", '"')
        text = text.replace("'", "'").replace("'", "'")
        return text


@dataclass
class TTSDatasetConfig:
    """Configuration for TTS dataset generation."""

    output_dir: Path
    min_duration_ms: float = 3000  # 3 seconds minimum
    max_duration_ms: float = 10000  # 10 seconds maximum
    sample_rate: int = 22050  # Standard for TTS
    language: str = "ga"
    whisper_model: str = "large-v3"
    split_on_silence: bool = True
    silence_thresh_db: int = -40
    min_silence_len_ms: int = 500

    def to_dict(self) -> dict[str, Any]:
        """Convert to dictionary."""
        return {
            "output_dir": str(self.output_dir),
            "min_duration_ms": self.min_duration_ms,
            "max_duration_ms": self.max_duration_ms,
            "sample_rate": self.sample_rate,
            "language": self.language,
            "whisper_model": self.whisper_model,
        }


class TTSDatasetGenerator:
    """
    Generate LJSpeech-format TTS training datasets from Irish audio.

    Features:
    - Whisper-based transcription with Irish language support
    - Automatic silence-based segmentation
    - Duration filtering (3-10 seconds optimal for Chatterbox)
    - Dialect tagging (Connacht, Munster, Ulster)
    - LJSpeech format output for Chatterbox fine-tuning
    """

    def __init__(
        self, config: TTSDatasetConfig | None = None, output_dir: Path | str | None = None
    ):
        """
        Initialize TTS dataset generator.

        Args:
            config: Full configuration object
            output_dir: Shortcut to set just output directory
        """
        if config:
            self.config = config
        else:
            output_path = Path(output_dir) if output_dir else Path("./datasets/irish_tts")
            self.config = TTSDatasetConfig(output_dir=output_path)

        self._whisper_model = None
        self._segments: list[TTSSegment] = []

        # Create output directory structure
        self._setup_directories()

    def _setup_directories(self) -> None:
        """Create LJSpeech-compatible directory structure."""
        self.config.output_dir.mkdir(parents=True, exist_ok=True)
        (self.config.output_dir / "wavs").mkdir(exist_ok=True)

    def _load_whisper(self):
        """Load Whisper model for transcription."""
        if self._whisper_model is None:
            try:
                import whisper

                logger.info(f"Loading Whisper model: {self.config.whisper_model}")
                self._whisper_model = whisper.load_model(self.config.whisper_model)
            except ImportError:
                logger.warning("Whisper not installed, transcription unavailable")
        return self._whisper_model

    async def transcribe_audio(self, audio_path: Path | str) -> str:
        """
        Transcribe audio file using Whisper.

        Args:
            audio_path: Path to audio file

        Returns:
            Transcribed text
        """
        model = self._load_whisper()
        if model is None:
            return ""

        try:
            import whisper

            # Force Irish language
            result = model.transcribe(
                str(audio_path),
                language="ga",
                task="transcribe",
            )
            return result["text"].strip()

        except Exception as e:
            logger.error(f"Transcription failed: {e}")
            return ""

    def split_on_silence(
        self,
        audio_path: Path | str,
    ) -> list[tuple[Path, float, float]]:
        """
        Split audio on silence for optimal segment lengths.

        Args:
            audio_path: Path to audio file

        Returns:
            List of (segment_path, start_ms, end_ms)
        """
        try:
            from pydub import AudioSegment
            from pydub.silence import split_on_silence as pydub_split

            audio = AudioSegment.from_file(str(audio_path))

            # Split on silence
            chunks = pydub_split(
                audio,
                min_silence_len=self.config.min_silence_len_ms,
                silence_thresh=self.config.silence_thresh_db,
                keep_silence=200,  # Keep 200ms of silence at edges
            )

            segments = []
            current_pos = 0

            for i, chunk in enumerate(chunks):
                duration = len(chunk)

                # Filter by duration
                if duration < self.config.min_duration_ms:
                    current_pos += duration
                    continue
                if duration > self.config.max_duration_ms:
                    # Could split further, but skip for now
                    current_pos += duration
                    continue

                # Export segment
                segment_path = self.config.output_dir / "wavs" / f"segment_{i:05d}.wav"
                chunk.export(
                    str(segment_path),
                    format="wav",
                    parameters=["-ar", str(self.config.sample_rate)],
                )

                segments.append((segment_path, current_pos, current_pos + duration))
                current_pos += duration

            logger.info(f"Split into {len(segments)} segments")
            return segments

        except ImportError:
            logger.error("pydub required for silence splitting")
            return []
        except Exception as e:
            logger.error(f"Splitting failed: {e}")
            return []

    async def process_audio(
        self,
        audio_path: Path | str,
        speaker_id: str = "default",
        dialect: str | None = None,
        transcript: str | None = None,
    ) -> list[TTSSegment]:
        """
        Process audio file into TTS training segments.

        Args:
            audio_path: Path to audio file
            speaker_id: Speaker identifier
            dialect: Irish dialect (connacht, munster, ulster)
            transcript: Optional pre-existing transcript

        Returns:
            List of processed segments
        """
        audio_path = Path(audio_path)
        segments = []

        if self.config.split_on_silence:
            # Split into segments
            segment_info = self.split_on_silence(audio_path)

            for seg_path, start_ms, end_ms in segment_info:
                # Transcribe each segment
                seg_transcript = await self.transcribe_audio(seg_path)
                if not seg_transcript:
                    continue

                segment = TTSSegment(
                    audio_path=str(seg_path),
                    transcript=seg_transcript,
                    duration_ms=end_ms - start_ms,
                    speaker_id=speaker_id,
                    language=self.config.language,
                    dialect=dialect,
                    metadata={
                        "source": str(audio_path),
                        "start_ms": start_ms,
                        "end_ms": end_ms,
                    },
                )
                segments.append(segment)
                self._segments.append(segment)

        else:
            # Process as single file
            if transcript is None:
                transcript = await self.transcribe_audio(audio_path)

            if transcript:
                # Get duration
                try:
                    from pydub import AudioSegment

                    audio = AudioSegment.from_file(str(audio_path))
                    duration_ms = len(audio)
                except Exception:
                    duration_ms = 0

                segment = TTSSegment(
                    audio_path=str(audio_path),
                    transcript=transcript,
                    duration_ms=duration_ms,
                    speaker_id=speaker_id,
                    language=self.config.language,
                    dialect=dialect,
                )
                segments.append(segment)
                self._segments.append(segment)

        logger.info(f"Processed {len(segments)} segments from {audio_path}")
        return segments

    def add_segment(
        self,
        audio_path: Path | str,
        transcript: str,
        speaker_id: str = "default",
        dialect: str | None = None,
        duration_ms: float | None = None,
    ) -> TTSSegment:
        """
        Manually add a segment with known transcription.

        Args:
            audio_path: Path to audio file
            transcript: Text transcription
            speaker_id: Speaker identifier
            dialect: Irish dialect
            duration_ms: Duration in milliseconds

        Returns:
            Created segment
        """
        audio_path = Path(audio_path)

        # Get duration if not provided
        if duration_ms is None:
            try:
                from pydub import AudioSegment

                audio = AudioSegment.from_file(str(audio_path))
                duration_ms = len(audio)
            except Exception:
                duration_ms = 0

        segment = TTSSegment(
            audio_path=str(audio_path),
            transcript=transcript,
            duration_ms=duration_ms,
            speaker_id=speaker_id,
            language=self.config.language,
            dialect=dialect,
        )
        self._segments.append(segment)
        return segment

    def export_ljspeech(self) -> Path:
        """
        Export dataset in LJSpeech format.

        Creates:
        - wavs/: Directory with WAV files named by segment ID
        - metadata.csv: ID|text|normalized_text format

        Returns:
            Path to metadata.csv
        """
        metadata_path = self.config.output_dir / "metadata.csv"
        wavs_dir = self.config.output_dir / "wavs"

        with open(metadata_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f, delimiter="|")

            for segment in self._segments:
                # Copy/rename audio to wavs directory
                src_path = Path(segment.audio_path)
                dst_path = wavs_dir / f"{segment.segment_id}.wav"

                if src_path != dst_path and src_path.exists():
                    shutil.copy2(src_path, dst_path)

                # Write metadata row
                row = segment.to_ljspeech_row()
                writer.writerow(row)

        logger.info(f"Exported {len(self._segments)} segments to {metadata_path}")
        return metadata_path

    def get_stats(self) -> dict[str, Any]:
        """Get dataset statistics."""
        if not self._segments:
            return {"count": 0}

        durations = [s.duration_ms for s in self._segments]
        dialects = {}
        speakers = {}

        for s in self._segments:
            dialects[s.dialect or "unknown"] = dialects.get(s.dialect or "unknown", 0) + 1
            speakers[s.speaker_id] = speakers.get(s.speaker_id, 0) + 1

        return {
            "count": len(self._segments),
            "total_duration_ms": sum(durations),
            "total_duration_hours": sum(durations) / 3600000,
            "avg_duration_ms": sum(durations) / len(durations),
            "min_duration_ms": min(durations),
            "max_duration_ms": max(durations),
            "dialects": dialects,
            "speakers": speakers,
        }


# =============================================================================
# Canuint Integration
# =============================================================================


async def generate_from_canuint(
    canuint_dir: Path | str,
    output_dir: Path | str,
    dialect: str | None = None,
) -> TTSDatasetGenerator:
    """
    Generate TTS dataset from Canuint dialect recordings.

    Args:
        canuint_dir: Directory with Canuint audio files
        output_dir: Output dataset directory
        dialect: Filter to specific dialect

    Returns:
        Configured generator with processed segments
    """
    generator = TTSDatasetGenerator(output_dir=output_dir)
    canuint_dir = Path(canuint_dir)

    # Process audio files
    for audio_file in canuint_dir.glob("**/*.wav"):
        # Extract dialect from path if not specified
        file_dialect = dialect
        if not file_dialect:
            path_str = str(audio_file).lower()
            if "connacht" in path_str or "conamara" in path_str:
                file_dialect = "connacht"
            elif "munster" in path_str or "mumhan" in path_str:
                file_dialect = "munster"
            elif "ulster" in path_str or "ulaidh" in path_str:
                file_dialect = "ulster"

        await generator.process_audio(
            audio_file,
            speaker_id=audio_file.stem,
            dialect=file_dialect,
        )

    return generator


# =============================================================================
# CLI Entry Point
# =============================================================================

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Generate Irish TTS training dataset")
    parser.add_argument("audio", help="Audio file or directory to process")
    parser.add_argument("--output", "-o", default="./datasets/irish_tts", help="Output directory")
    parser.add_argument("--speaker", "-s", default="default", help="Speaker ID")
    parser.add_argument("--dialect", "-d", choices=["connacht", "munster", "ulster"])
    parser.add_argument("--no-split", action="store_true", help="Don't split on silence")
    parser.add_argument("--stats", action="store_true", help="Show dataset statistics")
    args = parser.parse_args()

    logging.basicConfig(level=logging.INFO)

    config = TTSDatasetConfig(
        output_dir=Path(args.output),
        split_on_silence=not args.no_split,
    )
    generator = TTSDatasetGenerator(config)

    audio_path = Path(args.audio)

    if audio_path.is_dir():
        # Process all audio files in directory
        for audio_file in audio_path.glob("**/*.wav"):
            asyncio.run(
                generator.process_audio(
                    audio_file,
                    speaker_id=args.speaker,
                    dialect=args.dialect,
                )
            )
    else:
        asyncio.run(
            generator.process_audio(
                audio_path,
                speaker_id=args.speaker,
                dialect=args.dialect,
            )
        )

    # Export
    metadata_path = generator.export_ljspeech()
    print(f"Exported to: {metadata_path}")

    if args.stats:
        stats = generator.get_stats()
        print(f"\nDataset Statistics:")
        print(f"  Segments: {stats['count']}")
        print(f"  Total Duration: {stats.get('total_duration_hours', 0):.2f} hours")
        print(f"  Avg Duration: {stats.get('avg_duration_ms', 0):.0f} ms")
        print(f"  Dialects: {stats.get('dialects', {})}")
        print(f"  Speakers: {stats.get('speakers', {})}")
