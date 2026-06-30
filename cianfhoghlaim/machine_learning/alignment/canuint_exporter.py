"""
Multi-format alignment exporter for Canuint.ie dataset.

Exports word/character/phoneme alignments to training formats:
- LJSpeech: TTS training (filename|raw|normalized)
- CTM: Kaldi/ESPnet ASR (recording channel start duration word)
- TextGrid: Praat/MFA analysis (interval tiers)
- HuggingFace: transformers-compatible dataset
- Character JSON: ElevenLabs-style fine-grained alignment

Supports dialect-based organization and train/val/test splits.
"""
from __future__ import annotations

import json
import random
from dataclasses import dataclass
from pathlib import Path

from cianfhoghlaim.observability.logging import get_logger

logger = get_logger(__name__)


@dataclass
class ExportConfig:
    """Configuration for dataset export."""

    output_dir: Path
    train_ratio: float = 0.8
    val_ratio: float = 0.1
    test_ratio: float = 0.1
    random_seed: int = 42
    dialect_balanced: bool = True
    min_duration_ms: int = 50
    max_duration_ms: int = 5000


@dataclass
class ExportStats:
    """Statistics from export operation."""

    total_items: int = 0
    train_count: int = 0
    val_count: int = 0
    test_count: int = 0
    dialects: dict = None
    total_duration_seconds: float = 0.0
    formats_exported: list = None

    def __post_init__(self):
        if self.dialects is None:
            self.dialects = {}
        if self.formats_exported is None:
            self.formats_exported = []


# =============================================================================
# LJSpeech Format Export
# =============================================================================

def export_ljspeech(
    alignments: list[dict],
    output_path: Path,
    use_relative_paths: bool = True,
    wavs_dir: Path | None = None,
) -> int:
    """
    Export alignments to LJSpeech metadata.csv format.

    Format: filename|raw_text|normalized_text

    Args:
        alignments: List of alignment dicts with audio_path, text fields
        output_path: Path to output metadata.csv
        use_relative_paths: Use relative paths for audio files
        wavs_dir: Base directory for relative path calculation

    Returns:
        Number of entries exported
    """
    output_path.parent.mkdir(parents=True, exist_ok=True)

    count = 0
    with open(output_path, "w", encoding="utf-8") as f:
        for alignment in alignments:
            audio_path = alignment.get("audio_path", "")
            text = alignment.get("text", "") or alignment.get("dialectal_text", "")

            if not audio_path or not text:
                continue

            # Get filename (without extension for LJSpeech)
            if use_relative_paths and wavs_dir:
                try:
                    audio_ref = Path(audio_path).relative_to(wavs_dir)
                    audio_ref = str(audio_ref.with_suffix(""))  # Remove .wav
                except ValueError:
                    audio_ref = Path(audio_path).stem
            else:
                audio_ref = Path(audio_path).stem

            # LJSpeech format: filename|raw_text|normalized_text
            normalized = text.lower().strip()
            f.write(f"{audio_ref}|{text}|{normalized}\n")
            count += 1

    logger.info("ljspeech_export_complete", path=str(output_path), count=count)
    return count


# =============================================================================
# CTM Format Export (Kaldi/ESPnet)
# =============================================================================

def export_ctm(
    alignments: list[dict],
    output_path: Path,
    channel: int = 1,
) -> int:
    """
    Export alignments to CTM format for Kaldi/ESPnet.

    Format: recording_id channel start_time duration word [confidence]

    Args:
        alignments: List of alignment dicts
        output_path: Path to output .ctm file
        channel: Audio channel (default 1 for mono)

    Returns:
        Number of entries exported
    """
    output_path.parent.mkdir(parents=True, exist_ok=True)

    count = 0
    with open(output_path, "w", encoding="utf-8") as f:
        for alignment in alignments:
            recording_id = alignment.get("recording_id", "")
            start_time = alignment.get("start_time", 0.0)
            end_time = alignment.get("end_time", 0.0)
            text = alignment.get("text", "") or alignment.get("dialectal_text", "")

            if not recording_id or not text:
                continue

            duration = end_time - start_time

            # CTM format: recording channel start duration word
            f.write(f"{recording_id} {channel} {start_time:.3f} {duration:.3f} {text}\n")
            count += 1

    logger.info("ctm_export_complete", path=str(output_path), count=count)
    return count


# =============================================================================
# TextGrid Format Export (Praat/MFA)
# =============================================================================

def _escape_textgrid_text(text: str) -> str:
    """Escape special characters for TextGrid format."""
    return text.replace('"', '""').replace("\\", "\\\\")


def export_textgrid(
    alignments: list[dict],
    output_dir: Path,
    include_phonemes: bool = True,
) -> int:
    """
    Export alignments to Praat TextGrid format.

    Creates one TextGrid file per recording with tiers:
    - Tier 1: Words
    - Tier 2: Phonemes (optional)

    Args:
        alignments: List of alignment dicts
        output_dir: Directory for .TextGrid files
        include_phonemes: Include phoneme tier if available

    Returns:
        Number of TextGrid files created
    """
    output_dir.mkdir(parents=True, exist_ok=True)

    # Group alignments by recording
    recordings = {}
    for alignment in alignments:
        rec_id = alignment.get("recording_id", "")
        if rec_id not in recordings:
            recordings[rec_id] = []
        recordings[rec_id].append(alignment)

    count = 0
    for recording_id, words in recordings.items():
        if not words:
            continue

        # Sort by start time
        words = sorted(words, key=lambda x: x.get("start_time", 0))

        # Calculate bounds
        xmin = min(w.get("start_time", 0) for w in words)
        xmax = max(w.get("end_time", 0) for w in words)

        # Check if phonemes available
        has_phonemes = include_phonemes and any(w.get("phonemes") for w in words)

        # Build TextGrid content
        num_tiers = 2 if has_phonemes else 1

        lines = [
            'File type = "ooTextFile"',
            'Object class = "TextGrid"',
            "",
            f"xmin = {xmin}",
            f"xmax = {xmax}",
            "tiers? <exists>",
            f"size = {num_tiers}",
            "item []:",
        ]

        # Tier 1: Words
        lines.extend([
            "    item [1]:",
            '        class = "IntervalTier"',
            '        name = "words"',
            f"        xmin = {xmin}",
            f"        xmax = {xmax}",
            f"        intervals: size = {len(words)}",
        ])

        for i, word in enumerate(words, 1):
            w_start = word.get("start_time", 0)
            w_end = word.get("end_time", 0)
            w_text = _escape_textgrid_text(word.get("text", "") or word.get("dialectal_text", ""))

            lines.extend([
                f"        intervals [{i}]:",
                f"            xmin = {w_start}",
                f"            xmax = {w_end}",
                f'            text = "{w_text}"',
            ])

        # Tier 2: Phonemes (optional)
        if has_phonemes:
            # Collect all phonemes with timestamps
            all_phonemes = []
            for word in words:
                phonemes = word.get("phonemes", [])
                p_starts = word.get("phoneme_start_times", []) or word.get("phonemeStartTimesSeconds", [])
                p_ends = word.get("phoneme_end_times", []) or word.get("phonemeEndTimesSeconds", [])

                for j, phoneme in enumerate(phonemes):
                    if j < len(p_starts) and j < len(p_ends):
                        all_phonemes.append({
                            "text": phoneme,
                            "start": p_starts[j],
                            "end": p_ends[j],
                        })

            lines.extend([
                "    item [2]:",
                '        class = "IntervalTier"',
                '        name = "phonemes"',
                f"        xmin = {xmin}",
                f"        xmax = {xmax}",
                f"        intervals: size = {len(all_phonemes)}",
            ])

            for i, p in enumerate(all_phonemes, 1):
                p_text = _escape_textgrid_text(p["text"])
                lines.extend([
                    f"        intervals [{i}]:",
                    f"            xmin = {p['start']}",
                    f"            xmax = {p['end']}",
                    f'            text = "{p_text}"',
                ])

        # Write TextGrid file
        output_path = output_dir / f"{recording_id}.TextGrid"
        with open(output_path, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))

        count += 1

    logger.info("textgrid_export_complete", path=str(output_dir), count=count)
    return count


# =============================================================================
# Character-Level JSON Export (ElevenLabs Style)
# =============================================================================

def export_character_json(
    alignments: list[dict],
    output_path: Path,
) -> int:
    """
    Export character-level alignments to JSON format.

    Compatible with ElevenLabs transcript alignment format.

    Args:
        alignments: List of alignment dicts with character data
        output_path: Path to output JSONL file

    Returns:
        Number of entries exported
    """
    output_path.parent.mkdir(parents=True, exist_ok=True)

    count = 0
    with open(output_path, "w", encoding="utf-8") as f:
        for alignment in alignments:
            characters = alignment.get("characters", [])
            if not characters:
                continue

            record = {
                "word_id": alignment.get("word_id", ""),
                "recording_id": alignment.get("recording_id", ""),
                "text": alignment.get("text", ""),
                "dialect": alignment.get("dialect", ""),
                "characters": characters,
                "characterStartTimesSeconds": alignment.get("character_start_times", []) or alignment.get("characterStartTimesSeconds", []),
                "characterEndTimesSeconds": alignment.get("character_end_times", []) or alignment.get("characterEndTimesSeconds", []),
            }

            f.write(json.dumps(record, ensure_ascii=False) + "\n")
            count += 1

    logger.info("character_json_export_complete", path=str(output_path), count=count)
    return count


# =============================================================================
# HuggingFace Dataset Export
# =============================================================================

def export_huggingface_dataset(
    alignments: list[dict],
    output_dir: Path,
    dataset_name: str = "canuint_irish_speech",
    audio_dir: Path | None = None,
) -> dict:
    """
    Export alignments to HuggingFace datasets format.

    Creates:
    - dataset_info.json
    - data/train.jsonl, data/validation.jsonl, data/test.jsonl
    - README.md (dataset card)

    Args:
        alignments: List of alignment dicts
        output_dir: Directory for dataset
        dataset_name: Name for the dataset
        audio_dir: Base directory for audio files

    Returns:
        Export statistics dict
    """
    output_dir.mkdir(parents=True, exist_ok=True)
    data_dir = output_dir / "data"
    data_dir.mkdir(exist_ok=True)

    # Prepare records with audio paths
    records = []
    for alignment in alignments:
        audio_path = alignment.get("audio_path", "")
        text = alignment.get("text", "") or alignment.get("dialectal_text", "")

        if not text:
            continue

        record = {
            "audio": str(audio_path) if audio_path else "",
            "text": text,
            "normalized_text": text.lower().strip(),
            "dialect": alignment.get("dialect", ""),
            "speaker_name": alignment.get("speaker_name", ""),
            "recording_id": alignment.get("recording_id", ""),
            "word_id": alignment.get("word_id", ""),
            "start_time": alignment.get("start_time", 0.0),
            "end_time": alignment.get("end_time", 0.0),
            "duration_ms": alignment.get("duration_ms", 0),
        }
        records.append(record)

    # Shuffle and split
    random.seed(42)
    random.shuffle(records)

    n = len(records)
    train_end = int(n * 0.8)
    val_end = int(n * 0.9)

    splits = {
        "train": records[:train_end],
        "validation": records[train_end:val_end],
        "test": records[val_end:],
    }

    # Write split files
    for split_name, split_records in splits.items():
        split_path = data_dir / f"{split_name}.jsonl"
        with open(split_path, "w", encoding="utf-8") as f:
            for record in split_records:
                f.write(json.dumps(record, ensure_ascii=False) + "\n")

    # Calculate dialect distribution
    dialect_counts = {}
    for record in records:
        dialect = record.get("dialect", "unknown")
        dialect_counts[dialect] = dialect_counts.get(dialect, 0) + 1

    # Write dataset_info.json
    dataset_info = {
        "dataset_name": dataset_name,
        "language": ["ga"],  # Irish
        "task_categories": ["automatic-speech-recognition", "text-to-speech"],
        "size_category": f"{len(records)} examples",
        "splits": {
            "train": {"num_examples": len(splits["train"])},
            "validation": {"num_examples": len(splits["validation"])},
            "test": {"num_examples": len(splits["test"])},
        },
        "features": {
            "audio": {"dtype": "string", "description": "Path to audio file"},
            "text": {"dtype": "string", "description": "Transcribed text (dialectal)"},
            "normalized_text": {"dtype": "string", "description": "Normalized lowercase text"},
            "dialect": {"dtype": "string", "description": "Irish dialect (connacht, munster, ulster)"},
            "speaker_name": {"dtype": "string", "description": "Speaker name"},
            "recording_id": {"dtype": "string", "description": "Source recording ID"},
            "word_id": {"dtype": "string", "description": "Unique word identifier"},
            "start_time": {"dtype": "float64", "description": "Start time in seconds"},
            "end_time": {"dtype": "float64", "description": "End time in seconds"},
            "duration_ms": {"dtype": "int64", "description": "Duration in milliseconds"},
        },
        "dialect_distribution": dialect_counts,
    }

    with open(output_dir / "dataset_info.json", "w", encoding="utf-8") as f:
        json.dump(dataset_info, f, indent=2, ensure_ascii=False)

    # Write README.md (dataset card)
    readme_content = f"""---
language:
  - ga
license: cc-by-4.0
task_categories:
  - automatic-speech-recognition
  - text-to-speech
pretty_name: {dataset_name}
size_categories:
  - 10K<n<100K
---

# {dataset_name}

Irish speech dataset with word-level alignment from Canuint.ie.

## Dataset Description

This dataset contains word-level audio clips from Canuint.ie, a collection of
transcribed Irish language recordings. Each example contains:

- Audio clip of a single word
- Dialectal transcription (as spoken)
- Normalized text
- Dialect label (Connacht, Munster, or Ulster)
- Speaker information
- Precise timestamps

## Dialect Distribution

{json.dumps(dialect_counts, indent=2)}

## Splits

- **Train**: {len(splits["train"])} examples
- **Validation**: {len(splits["validation"])} examples
- **Test**: {len(splits["test"])} examples

## Usage

```python
from datasets import load_dataset

dataset = load_dataset("{dataset_name}")
```

## Source

Data extracted from [Canuint.ie](https://www.canuint.ie), a resource for
transcribed Irish language audio recordings.

## License

CC-BY-4.0 (check original source for specific terms)
"""

    with open(output_dir / "README.md", "w", encoding="utf-8") as f:
        f.write(readme_content)

    stats = {
        "total": len(records),
        "train": len(splits["train"]),
        "validation": len(splits["validation"]),
        "test": len(splits["test"]),
        "dialects": dialect_counts,
    }

    logger.info("huggingface_dataset_export_complete",
                path=str(output_dir),
                total=len(records))

    return stats


# =============================================================================
# Phoneme-Level Export
# =============================================================================

def export_phoneme_alignments(
    alignments: list[dict],
    output_path: Path,
) -> int:
    """
    Export phoneme-level alignments to JSONL format.

    Args:
        alignments: List of alignment dicts with phoneme data
        output_path: Path to output JSONL file

    Returns:
        Number of entries exported
    """
    output_path.parent.mkdir(parents=True, exist_ok=True)

    count = 0
    with open(output_path, "w", encoding="utf-8") as f:
        for alignment in alignments:
            phonemes = alignment.get("phonemes", [])
            if not phonemes:
                continue

            record = {
                "word_id": alignment.get("word_id", ""),
                "recording_id": alignment.get("recording_id", ""),
                "text": alignment.get("text", ""),
                "dialect": alignment.get("dialect", ""),
                "phonemes": phonemes,
                "phoneme_format": alignment.get("phoneme_format", "ipa"),
                "phonemeStartTimesSeconds": alignment.get("phoneme_start_times", []) or alignment.get("phonemeStartTimesSeconds", []),
                "phonemeEndTimesSeconds": alignment.get("phoneme_end_times", []) or alignment.get("phonemeEndTimesSeconds", []),
                "phoneme_count": len(phonemes),
            }

            f.write(json.dumps(record, ensure_ascii=False) + "\n")
            count += 1

    logger.info("phoneme_alignment_export_complete", path=str(output_path), count=count)
    return count


# =============================================================================
# Combined Multi-Format Export
# =============================================================================

def export_all_formats(
    word_alignments: list[dict],
    character_alignments: list[dict],
    phoneme_alignments: list[dict],
    output_dir: Path,
    config: ExportConfig | None = None,
) -> ExportStats:
    """
    Export alignments to all supported formats.

    Creates directory structure:
    ```
    output_dir/
    ├── ljspeech/
    │   └── metadata.csv
    ├── ctm/
    │   └── alignments.ctm
    ├── textgrid/
    │   └── {recording_id}.TextGrid
    ├── character_json/
    │   └── alignments.jsonl
    ├── phoneme_json/
    │   └── alignments.jsonl
    └── huggingface/
        ├── data/
        ├── dataset_info.json
        └── README.md
    ```

    Args:
        word_alignments: Word-level alignment dicts
        character_alignments: Character-level alignment dicts
        phoneme_alignments: Phoneme-level alignment dicts
        output_dir: Base output directory
        config: Export configuration

    Returns:
        ExportStats with counts and metadata
    """
    if config is None:
        config = ExportConfig(output_dir=output_dir)

    output_dir.mkdir(parents=True, exist_ok=True)
    stats = ExportStats()

    # LJSpeech format
    ljspeech_dir = output_dir / "ljspeech"
    export_ljspeech(
        word_alignments,
        ljspeech_dir / "metadata.csv",
    )
    stats.formats_exported.append("ljspeech")

    # CTM format
    ctm_dir = output_dir / "ctm"
    export_ctm(
        word_alignments,
        ctm_dir / "alignments.ctm",
    )
    stats.formats_exported.append("ctm")

    # TextGrid format
    textgrid_dir = output_dir / "textgrid"
    export_textgrid(
        phoneme_alignments if phoneme_alignments else word_alignments,
        textgrid_dir,
        include_phonemes=bool(phoneme_alignments),
    )
    stats.formats_exported.append("textgrid")

    # Character-level JSON
    if character_alignments:
        char_dir = output_dir / "character_json"
        export_character_json(
            character_alignments,
            char_dir / "alignments.jsonl",
        )
        stats.formats_exported.append("character_json")

    # Phoneme-level JSON
    if phoneme_alignments:
        phoneme_dir = output_dir / "phoneme_json"
        export_phoneme_alignments(
            phoneme_alignments,
            phoneme_dir / "alignments.jsonl",
        )
        stats.formats_exported.append("phoneme_json")

    # HuggingFace dataset
    hf_dir = output_dir / "huggingface"
    hf_stats = export_huggingface_dataset(
        word_alignments,
        hf_dir,
        dataset_name="canuint_irish_speech",
    )
    stats.formats_exported.append("huggingface")

    # Aggregate stats
    stats.total_items = len(word_alignments)
    stats.train_count = hf_stats.get("train", 0)
    stats.val_count = hf_stats.get("validation", 0)
    stats.test_count = hf_stats.get("test", 0)
    stats.dialects = hf_stats.get("dialects", {})

    # Calculate total duration
    for alignment in word_alignments:
        duration = alignment.get("end_time", 0) - alignment.get("start_time", 0)
        stats.total_duration_seconds += duration

    logger.info("multi_format_export_complete",
                output_dir=str(output_dir),
                total_items=stats.total_items,
                formats=stats.formats_exported,
                total_duration_hours=stats.total_duration_seconds / 3600)

    return stats


# =============================================================================
# Convenience Pipeline Functions
# =============================================================================

def load_alignments_from_jsonl(path: Path) -> list[dict]:
    """Load alignments from JSONL file."""
    alignments = []
    with open(path, encoding="utf-8") as f:
        for line in f:
            if line.strip():
                alignments.append(json.loads(line))
    return alignments


def export_canuint_dataset(
    word_alignments_path: Path,
    character_alignments_path: Path | None,
    phoneme_alignments_path: Path | None,
    output_dir: Path,
) -> ExportStats:
    """
    Export complete Canuint dataset from alignment JSONL files.

    Args:
        word_alignments_path: Path to word alignments JSONL
        character_alignments_path: Path to character alignments JSONL (optional)
        phoneme_alignments_path: Path to phoneme alignments JSONL (optional)
        output_dir: Output directory for all formats

    Returns:
        ExportStats
    """
    word_alignments = load_alignments_from_jsonl(word_alignments_path)

    character_alignments = []
    if character_alignments_path and character_alignments_path.exists():
        character_alignments = load_alignments_from_jsonl(character_alignments_path)

    phoneme_alignments = []
    if phoneme_alignments_path and phoneme_alignments_path.exists():
        phoneme_alignments = load_alignments_from_jsonl(phoneme_alignments_path)

    return export_all_formats(
        word_alignments=word_alignments,
        character_alignments=character_alignments,
        phoneme_alignments=phoneme_alignments,
        output_dir=output_dir,
    )
