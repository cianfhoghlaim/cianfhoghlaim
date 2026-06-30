"""
Irish Grapheme-to-Phoneme (G2P) conversion for alignment.

Converts Irish text to phoneme sequences using:
1. espeak-ng backend (primary)
2. Rule-based fallback for Irish-specific patterns

Supports multiple output formats:
- IPA (International Phonetic Alphabet)
- X-SAMPA (Extended Speech Assessment Methods Phonetic Alphabet)
- SAMPA (Speech Assessment Methods Phonetic Alphabet)

Dialect-aware processing for:
- Connacht (Galway, Mayo)
- Munster (Kerry, Cork)
- Ulster (Donegal)
"""
from __future__ import annotations

import contextlib
import json
import re
import subprocess
from collections.abc import Iterator
from dataclasses import dataclass
from enum import Enum
from pathlib import Path

from sruth.oideachais.observability.logging import get_logger

logger = get_logger(__name__)


class PhonemeFormat(Enum):
    """Supported phoneme output formats."""
    IPA = "ipa"
    XSAMPA = "x-sampa"
    SAMPA = "sampa"


class IrishDialect(Enum):
    """Irish dialect variants."""
    CONNACHT = "connacht"
    MUNSTER = "munster"
    ULSTER = "ulster"
    STANDARD = "standard"


@dataclass
class PhonemeAlignment:
    """Phoneme-level alignment data."""

    word_id: str
    recording_id: str
    text: str
    phonemes: list[str]
    phoneme_start_times: list[float]
    phoneme_end_times: list[float]
    phoneme_format: str = "ipa"
    dialect: str = ""

    def to_dict(self) -> dict:
        """Export to dictionary format."""
        return {
            "word_id": self.word_id,
            "recording_id": self.recording_id,
            "text": self.text,
            "phonemes": self.phonemes,
            "phonemeStartTimesSeconds": self.phoneme_start_times,
            "phonemeEndTimesSeconds": self.phoneme_end_times,
            "phoneme_format": self.phoneme_format,
            "dialect": self.dialect,
            "phoneme_count": len(self.phonemes),
        }


# Irish-specific phoneme mappings (Standard Irish)
# Based on: https://en.wikipedia.org/wiki/Irish_phonology
IRISH_PHONEME_RULES = {
    # Broad consonants (velarized)
    "b": "bˠ",
    "c": "k",
    "d": "d̪ˠ",
    "f": "fˠ",
    "g": "ɡ",
    "l": "l̪ˠ",
    "m": "mˠ",
    "n": "n̪ˠ",
    "p": "pˠ",
    "r": "ɾˠ",
    "s": "sˠ",
    "t": "t̪ˠ",

    # Slender consonants (palatalized) - context-dependent
    # (before/after i, e, í, é)

    # Lenited consonants
    "bh": "w",  # or v in some dialects
    "ch": "x",  # or χ
    "dh": "ɣ",  # broad, ʝ slender
    "fh": "",   # silent
    "gh": "ɣ",  # broad, ʝ slender
    "mh": "w",  # or v
    "ph": "fˠ",
    "sh": "h",
    "th": "h",

    # Vowels - short
    "a": "a",
    "e": "ɛ",
    "i": "ɪ",
    "o": "ɔ",
    "u": "ʊ",

    # Vowels - long (with fada)
    "á": "ɑː",
    "é": "eː",
    "í": "iː",
    "ó": "oː",
    "ú": "uː",

    # Common digraphs
    "ao": "iː",   # or eː in some dialects
    "ea": "a",
    "ei": "ɛ",
    "eo": "oː",
    "ia": "iə",
    "io": "ɪ",
    "iu": "uː",
    "oi": "ɛ",
    "ua": "uə",
    "ui": "ɪ",
}

# Dialect-specific variations
DIALECT_VARIATIONS = {
    IrishDialect.ULSTER: {
        "ao": "eː",    # Ulster uses /eː/ for "ao"
        "á": "æː",     # Ulster "á" more fronted
    },
    IrishDialect.MUNSTER: {
        "ao": "eː",    # Munster also uses /eː/
        "ia": "iːə",   # Longer diphthong
    },
    IrishDialect.CONNACHT: {
        # Connacht closest to standard
    },
}


def check_espeak_available() -> bool:
    """Check if espeak-ng is available on the system."""
    try:
        result = subprocess.run(
            ["espeak-ng", "--version"],
            capture_output=True,
            text=True,
            timeout=5,
        )
        return result.returncode == 0
    except (subprocess.SubprocessError, FileNotFoundError):
        return False


def espeak_g2p(
    text: str,
    language: str = "ga",
    phoneme_format: PhonemeFormat = PhonemeFormat.IPA,
) -> list[str]:
    """
    Convert text to phonemes using espeak-ng.

    Args:
        text: Text to convert
        language: Language code (default: 'ga' for Irish)
        phoneme_format: Output format (IPA, X-SAMPA, SAMPA)

    Returns:
        List of phonemes
    """
    if not check_espeak_available():
        logger.warning("espeak_ng_not_available", fallback="rule_based")
        return rule_based_g2p(text)

    # espeak-ng phoneme output flags
    flags = ["-q", "--ipa"]  # quiet mode, IPA output

    if phoneme_format == PhonemeFormat.XSAMPA:
        flags = ["-q", "-x"]  # X-SAMPA output

    try:
        result = subprocess.run(
            ["espeak-ng", "-v", language, *flags, text],
            capture_output=True,
            text=True,
            timeout=10,
        )

        if result.returncode != 0:
            logger.warning("espeak_ng_error", stderr=result.stderr)
            return rule_based_g2p(text)

        # Parse output - espeak returns phonemes with spaces
        phoneme_str = result.stdout.strip()
        # Split on spaces and filter empty
        phonemes = [p for p in phoneme_str.split() if p]

        # Further split compound phonemes
        expanded = []
        for p in phonemes:
            # Split on phoneme boundaries (simplified)
            expanded.extend(re.findall(r"[ˈˌ]?[a-zɑɛɪɔʊəæœøʏ][ːˠʲ̪]*|[^a-zɑɛɪɔʊəæœøʏ]+", p, re.IGNORECASE))

        return [p for p in expanded if p.strip()]

    except subprocess.SubprocessError as e:
        logger.warning("espeak_ng_subprocess_error", error=str(e))
        return rule_based_g2p(text)


def rule_based_g2p(
    text: str,
    dialect: IrishDialect = IrishDialect.STANDARD,
) -> list[str]:
    """
    Rule-based G2P fallback for Irish.

    Uses lookup tables and basic rules when espeak-ng is unavailable.

    Args:
        text: Text to convert
        dialect: Irish dialect for regional variations

    Returns:
        List of phonemes (IPA)
    """
    phonemes = []
    text_lower = text.lower()
    i = 0

    # Get dialect-specific rules
    rules = IRISH_PHONEME_RULES.copy()
    if dialect in DIALECT_VARIATIONS:
        rules.update(DIALECT_VARIATIONS[dialect])

    while i < len(text_lower):
        matched = False

        # Try 3-character sequences first
        if i + 3 <= len(text_lower):
            trigraph = text_lower[i:i+3]
            if trigraph in rules:
                phoneme = rules[trigraph]
                if phoneme:  # Skip empty (silent letters)
                    phonemes.append(phoneme)
                i += 3
                matched = True

        # Try 2-character sequences
        if not matched and i + 2 <= len(text_lower):
            digraph = text_lower[i:i+2]
            if digraph in rules:
                phoneme = rules[digraph]
                if phoneme:
                    phonemes.append(phoneme)
                i += 2
                matched = True

        # Single character
        if not matched:
            char = text_lower[i]
            if char in rules:
                phoneme = rules[char]
                if phoneme:
                    phonemes.append(phoneme)
            elif char.isalpha():
                # Unknown character - keep as-is
                phonemes.append(char)
            # Skip non-alphabetic characters (spaces, punctuation)
            i += 1

    return phonemes


def interpolate_phoneme_timestamps(
    phonemes: list[str],
    start_time: float,
    end_time: float,
) -> tuple[list[float], list[float]]:
    """
    Interpolate timestamps for phonemes (linear distribution).

    Args:
        phonemes: List of phonemes
        start_time: Word start time
        end_time: Word end time

    Returns:
        Tuple of (start_times, end_times) lists
    """
    if not phonemes:
        return [], []

    duration = end_time - start_time
    phoneme_duration = duration / len(phonemes)

    start_times = []
    end_times = []

    for i in range(len(phonemes)):
        p_start = start_time + (i * phoneme_duration)
        p_end = start_time + ((i + 1) * phoneme_duration)
        start_times.append(round(p_start, 6))
        end_times.append(round(p_end, 6))

    return start_times, end_times


def create_phoneme_alignment(
    word_id: str,
    recording_id: str,
    text: str,
    start_time: float,
    end_time: float,
    dialect: str = "",
    phoneme_format: PhonemeFormat = PhonemeFormat.IPA,
    use_espeak: bool = True,
) -> PhonemeAlignment:
    """
    Create PhonemeAlignment from word-level data.

    Args:
        word_id: Unique word identifier
        recording_id: Recording identifier
        text: Word text
        start_time: Word start time
        end_time: Word end time
        dialect: Irish dialect name
        phoneme_format: Output format
        use_espeak: Try espeak-ng first

    Returns:
        PhonemeAlignment object
    """
    # Map dialect string to enum
    dialect_enum = IrishDialect.STANDARD
    if dialect:
        with contextlib.suppress(ValueError):
            dialect_enum = IrishDialect(dialect.lower())

    # Get phonemes
    if use_espeak and check_espeak_available():
        phonemes = espeak_g2p(text, phoneme_format=phoneme_format)
    else:
        phonemes = rule_based_g2p(text, dialect=dialect_enum)

    # Interpolate timestamps
    start_times, end_times = interpolate_phoneme_timestamps(
        phonemes, start_time, end_time
    )

    return PhonemeAlignment(
        word_id=word_id,
        recording_id=recording_id,
        text=text,
        phonemes=phonemes,
        phoneme_start_times=start_times,
        phoneme_end_times=end_times,
        phoneme_format=phoneme_format.value,
        dialect=dialect,
    )


def batch_convert_to_phonemes(
    word_alignments: list[dict],
    phoneme_format: PhonemeFormat = PhonemeFormat.IPA,
    use_espeak: bool = True,
    use_dialectal_text: bool = True,
) -> Iterator[PhonemeAlignment]:
    """
    Batch convert word alignments to phoneme alignments.

    Args:
        word_alignments: List of word alignment dicts
        phoneme_format: Output format
        use_espeak: Try espeak-ng first
        use_dialectal_text: Use dialectal (True) or standardized (False) text

    Yields:
        PhonemeAlignment objects
    """
    for word in word_alignments:
        text_key = "dialectal_text" if use_dialectal_text else "standardized_text"
        text = word.get(text_key) or word.get("dialectal_text", "")

        if not text:
            continue

        yield create_phoneme_alignment(
            word_id=word["word_id"],
            recording_id=word["recording_id"],
            text=text,
            start_time=word["start_time"],
            end_time=word["end_time"],
            dialect=word.get("dialect", ""),
            phoneme_format=phoneme_format,
            use_espeak=use_espeak,
        )


def export_phoneme_alignments(
    alignments: list[PhonemeAlignment],
    output_path: Path,
) -> None:
    """
    Export phoneme alignments to JSONL format.

    Args:
        alignments: List of PhonemeAlignment objects
        output_path: Output file path
    """
    output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(output_path, "w", encoding="utf-8") as f:
        for alignment in alignments:
            line = json.dumps(alignment.to_dict(), ensure_ascii=False)
            f.write(line + "\n")

    logger.info("phoneme_alignment_export_complete",
                path=str(output_path),
                count=len(alignments))


def process_word_alignments_to_phonemes(
    word_alignments_path: Path,
    output_path: Path,
    phoneme_format: PhonemeFormat = PhonemeFormat.IPA,
    use_espeak: bool = True,
    use_dialectal_text: bool = True,
) -> int:
    """
    Process word alignments file to phoneme alignments.

    Args:
        word_alignments_path: Input JSONL path
        output_path: Output JSONL path
        phoneme_format: Phoneme output format
        use_espeak: Use espeak-ng when available
        use_dialectal_text: Use dialectal text

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

            alignment = create_phoneme_alignment(
                word_id=word["word_id"],
                recording_id=word["recording_id"],
                text=text,
                start_time=word["start_time"],
                end_time=word["end_time"],
                dialect=word.get("dialect", ""),
                phoneme_format=phoneme_format,
                use_espeak=use_espeak,
            )
            alignments.append(alignment)

    export_phoneme_alignments(alignments, output_path)
    return len(alignments)
