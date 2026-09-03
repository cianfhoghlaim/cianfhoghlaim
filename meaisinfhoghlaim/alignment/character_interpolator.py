"""
Character-level timestamp interpolation for Irish speech alignment.

Interpolates word-level timestamps to character boundaries for:
- ASR CTC training (character-level supervision)
- ElevenLabs-compatible alignment format
- Fine-grained speech synthesis control

Handles Irish-specific characters:
- Fada vowels: á, é, í, ó, ú
- Lenition combinations: bh, ch, dh, fh, gh, mh, ph, sh, th
- Eclipsis: mb, gc, nd, bhf, ng, bp, dt
"""
from __future__ import annotations

import json
from collections.abc import Iterator
from dataclasses import dataclass
from pathlib import Path

import structlog

logger = structlog.get_logger(__name__)


# Irish digraphs that should be treated as single phonological units
IRISH_DIGRAPHS = {
    # Lenition (séimhiú)
    "bh", "ch", "dh", "fh", "gh", "mh", "ph", "sh", "th",
    # Long vowels with fada are single characters, but common digraphs:
    "ae", "ao", "ea", "ei", "eo", "ia", "io", "iu", "oi", "ua", "ui",
}

# Eclipsis prefixes (urú) - these modify the following consonant
IRISH_ECLIPSIS = {"mb", "gc", "nd", "bhf", "ng", "bp", "dt", "n-", "t-"}


@dataclass
class CharacterAlignment:
    """Character-level alignment data."""

    word_id: str
    recording_id: str
    text: str
    characters: list[str]
    character_start_times: list[float]
    character_end_times: list[float]
    dialect: str = ""

    def to_elevenlabs_format(self) -> dict:
        """Export to ElevenLabs transcript alignment JSON format."""
        return {
            "characters": self.characters,
            "characterStartTimesSeconds": self.character_start_times,
            "characterEndTimesSeconds": self.character_end_times,
        }

    def to_dict(self) -> dict:
        """Export to full dictionary format."""
        return {
            "word_id": self.word_id,
            "recording_id": self.recording_id,
            "text": self.text,
            "dialect": self.dialect,
            "characters": self.characters,
            "characterStartTimesSeconds": self.character_start_times,
            "characterEndTimesSeconds": self.character_end_times,
            "character_count": len(self.characters),
            "duration_seconds": self.character_end_times[-1] - self.character_start_times[0] if self.characters else 0,
        }


def tokenize_irish_text(text: str, preserve_digraphs: bool = False) -> list[str]:
    """
    Tokenize Irish text into characters, optionally preserving digraphs.

    Args:
        text: Irish text to tokenize
        preserve_digraphs: If True, keep digraphs like 'bh', 'ch' as single units

    Returns:
        List of character tokens
    """
    if not preserve_digraphs:
        return list(text)

    tokens = []
    i = 0
    text_lower = text.lower()

    while i < len(text):
        # Check for 3-character eclipsis first (bhf)
        if i + 3 <= len(text) and text_lower[i:i+3] in IRISH_ECLIPSIS:
            tokens.append(text[i:i+3])
            i += 3
        # Check for 2-character digraphs
        elif i + 2 <= len(text) and text_lower[i:i+2] in IRISH_DIGRAPHS.union(IRISH_ECLIPSIS):
            tokens.append(text[i:i+2])
            i += 2
        else:
            tokens.append(text[i])
            i += 1

    return tokens


def interpolate_character_timestamps(
    text: str,
    start_time: float,
    end_time: float,
    preserve_digraphs: bool = False,
) -> tuple[list[str], list[float], list[float]]:
    """
    Interpolate timestamps for each character in a word.

    Uses linear interpolation assuming uniform character duration.
    For more accurate results, consider using a phoneme duration model.

    Args:
        text: Word text to interpolate
        start_time: Word start time in seconds
        end_time: Word end time in seconds
        preserve_digraphs: Keep Irish digraphs as single units

    Returns:
        Tuple of (characters, start_times, end_times)
    """
    characters = tokenize_irish_text(text, preserve_digraphs)

    if not characters:
        return [], [], []

    duration = end_time - start_time
    char_duration = duration / len(characters)

    start_times = []
    end_times = []

    for i in range(len(characters)):
        char_start = start_time + (i * char_duration)
        char_end = start_time + ((i + 1) * char_duration)
        start_times.append(round(char_start, 6))
        end_times.append(round(char_end, 6))

    return characters, start_times, end_times


def create_character_alignment(
    word_id: str,
    recording_id: str,
    text: str,
    start_time: float,
    end_time: float,
    dialect: str = "",
    preserve_digraphs: bool = False,
) -> CharacterAlignment:
    """
    Create a CharacterAlignment from word-level data.

    Args:
        word_id: Unique word identifier
        recording_id: Recording identifier
        text: Word text
        start_time: Word start time in seconds
        end_time: Word end time in seconds
        dialect: Irish dialect (connacht, munster, ulster)
        preserve_digraphs: Keep Irish digraphs as single units

    Returns:
        CharacterAlignment object
    """
    characters, start_times, end_times = interpolate_character_timestamps(
        text, start_time, end_time, preserve_digraphs
    )

    return CharacterAlignment(
        word_id=word_id,
        recording_id=recording_id,
        text=text,
        characters=characters,
        character_start_times=start_times,
        character_end_times=end_times,
        dialect=dialect,
    )


def batch_interpolate_alignments(
    word_alignments: list[dict],
    preserve_digraphs: bool = False,
    use_dialectal_text: bool = True,
) -> Iterator[CharacterAlignment]:
    """
    Batch interpolate character alignments from word-level data.

    Args:
        word_alignments: List of word alignment dictionaries from DLT
        preserve_digraphs: Keep Irish digraphs as single units
        use_dialectal_text: Use dialectal_text (True) or standardized_text (False)

    Yields:
        CharacterAlignment objects
    """
    for word in word_alignments:
        text_key = "dialectal_text" if use_dialectal_text else "standardized_text"
        text = word.get(text_key) or word.get("dialectal_text", "")

        if not text:
            continue

        yield create_character_alignment(
            word_id=word["word_id"],
            recording_id=word["recording_id"],
            text=text,
            start_time=word["start_time"],
            end_time=word["end_time"],
            dialect=word.get("dialect", ""),
            preserve_digraphs=preserve_digraphs,
        )


def export_elevenlabs_format(
    alignments: list[CharacterAlignment],
    output_path: Path,
) -> None:
    """
    Export alignments to ElevenLabs-compatible JSONL format.

    Each line contains one word's character alignment.

    Args:
        alignments: List of CharacterAlignment objects
        output_path: Output JSONL file path
    """
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, "w", encoding="utf-8") as f:
        for alignment in alignments:
            line = json.dumps(alignment.to_dict(), ensure_ascii=False)
            f.write(line + "\n")

    logger.info("character_alignment_export_complete",
                path=str(output_path),
                count=len(alignments))


def merge_word_alignments_to_sentence(
    word_alignments: list[CharacterAlignment],
    separator: str = " ",
) -> CharacterAlignment:
    """
    Merge multiple word alignments into a single sentence alignment.

    Useful for creating sentence-level training data from word-level data.

    Args:
        word_alignments: List of word CharacterAlignment objects (in order)
        separator: Character to insert between words (default: space)

    Returns:
        Single CharacterAlignment for the entire sentence
    """
    if not word_alignments:
        raise ValueError("No word alignments provided")

    merged_chars = []
    merged_starts = []
    merged_ends = []
    merged_text_parts = []

    for i, word_align in enumerate(word_alignments):
        # Add space before word (except first)
        if i > 0 and separator:
            # Insert separator with interpolated timestamp
            prev_end = merged_ends[-1] if merged_ends else word_align.character_start_times[0]
            curr_start = word_align.character_start_times[0]
            (prev_end + curr_start) / 2

            merged_chars.append(separator)
            merged_starts.append(prev_end)
            merged_ends.append(curr_start)

        # Add word characters
        merged_chars.extend(word_align.characters)
        merged_starts.extend(word_align.character_start_times)
        merged_ends.extend(word_align.character_end_times)
        merged_text_parts.append(word_align.text)

    return CharacterAlignment(
        word_id=word_alignments[0].recording_id + "_sentence",
        recording_id=word_alignments[0].recording_id,
        text=separator.join(merged_text_parts),
        characters=merged_chars,
        character_start_times=merged_starts,
        character_end_times=merged_ends,
        dialect=word_alignments[0].dialect,
    )


# Convenience function for pipeline usage
def process_word_alignments_to_characters(
    word_alignments_path: Path,
    output_path: Path,
    preserve_digraphs: bool = False,
    use_dialectal_text: bool = True,
) -> int:
    """
    Process word alignments JSONL file to character alignments.

    Args:
        word_alignments_path: Input JSONL path (word-level)
        output_path: Output JSONL path (character-level)
        preserve_digraphs: Keep Irish digraphs as single units
        use_dialectal_text: Use dialectal (True) or standardized (False) text

    Returns:
        Number of alignments processed
    """
    alignments = []

    with open(word_alignments_path, encoding="utf-8") as f:
        for line in f:
            if not line.strip():
                continue
            word = json.loads(line)

            text_key = "dialectal_text" if use_dialectal_text else "standardized_text"
            text = word.get(text_key) or word.get("dialectal_text", "")

            if not text:
                continue

            alignment = create_character_alignment(
                word_id=word["word_id"],
                recording_id=word["recording_id"],
                text=text,
                start_time=word["start_time"],
                end_time=word["end_time"],
                dialect=word.get("dialect", ""),
                preserve_digraphs=preserve_digraphs,
            )
            alignments.append(alignment)

    export_elevenlabs_format(alignments, output_path)
    return len(alignments)
