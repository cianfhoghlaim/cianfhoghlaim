"""
DLT Source for SEC Aural Exam Transcript Parsing.

Extracts structured transcript data from SEC exam aural scripts:
- Irish LC Aural (with dialect tags: Connacht, Munster, Ulster)
- French/German/Spanish LC Listening Comprehension
- Junior Cycle aural components

Output schema aligns with Canuint word-level alignments for unified training.

PDF parsing uses:
- PyMuPDF4LLM for simple text extraction
- BAML for structured entity extraction
"""
from __future__ import annotations

import hashlib
import re
from collections.abc import Iterator
from dataclasses import dataclass, field
from datetime import UTC, datetime
from enum import Enum
from pathlib import Path
from typing import Any

import dlt
from dlt.sources import DltResource
from sruth.oideachais.observability.logging import get_logger

logger = get_logger(__name__)


class IrishDialect(str, Enum):
    """Irish dialect identifiers."""

    CONNACHT = "connacht"
    MUNSTER = "munster"
    ULSTER = "ulster"
    STANDARD = "standard"
    UNKNOWN = "unknown"


class TranscriptType(str, Enum):
    """Types of aural transcripts."""

    AURAL_SCRIPT = "aural_script"  # Full exam script
    LISTENING_COMPREHENSION = "listening_comprehension"
    ORAL_PREP = "oral_prep"  # Practice materials
    SAMPLE_PAPER = "sample_paper"


@dataclass
class SpeakerSegment:
    """A single speaker segment in a transcript."""

    segment_id: str
    speaker_id: str | None = None
    speaker_role: str | None = None  # e.g., "Narrator", "Person A", "Sraith Pictiúr"
    text: str = ""
    dialect: str | None = None
    start_marker: str | None = None  # e.g., "Track 1", "Question 1"
    duration_hint: str | None = None  # e.g., "2 minutes"
    section: str | None = None  # e.g., "Cuid A", "Section B"
    question_number: int | None = None


@dataclass
class AuralTranscript:
    """Parsed aural exam transcript."""

    transcript_id: str
    source_pdf: str
    exam_type: str  # "LC" or "JC"
    subject: str  # "irish", "french", etc.
    year: int | None = None
    level: str | None = None  # "higher", "ordinary"
    paper_type: str | None = None  # "paper_1", "paper_2"
    language: str = "ga"
    segments: list[SpeakerSegment] = field(default_factory=list)
    raw_text: str = ""
    parsed_at: str = field(default_factory=lambda: datetime.now(UTC).isoformat())


# Irish dialect markers found in SEC scripts
DIALECT_PATTERNS = {
    IrishDialect.CONNACHT: [
        r"\(Conamara\)",
        r"\(Cois Fharraige\)",
        r"\(Gaeltacht Chonamara\)",
        r"\(Connacht\)",
        r"Canúint Chonnacht",
    ],
    IrishDialect.MUNSTER: [
        r"\(Corca Dhuibhne\)",
        r"\(Gaeltacht na Mumhan\)",
        r"\(Munster\)",
        r"\(Ciarraí\)",
        r"Canúint na Mumhan",
    ],
    IrishDialect.ULSTER: [
        r"\(Gaoth Dobhair\)",
        r"\(Rann na Feirste\)",
        r"\(Tír Chonaill\)",
        r"\(Ulster\)",
        r"\(Dún na nGall\)",
        r"Canúint Uladh",
    ],
}

# Section markers in Irish LC aural
SECTION_PATTERNS = [
    r"Cuid\s+([A-D])",
    r"Section\s+([A-D])",
    r"Roinn\s+(\d+)",
    r"Track\s+(\d+)",
    r"Mír\s+(\d+)",
]

# Speaker role patterns
SPEAKER_PATTERNS = [
    r"^(Narrator|Inseoir):",
    r"^(Person\s+[A-Z]|Duine\s+[A-Z]):",
    r"^(Speaker\s+\d+|Cainteoir\s+\d+):",
    r"^(Man|Woman|Fear|Bean):",
    r"^(Interviewer|Agallóir):",
]


def _detect_dialect(text: str) -> IrishDialect:
    """Detect Irish dialect from text markers."""
    text_lower = text.lower()

    for dialect, patterns in DIALECT_PATTERNS.items():
        for pattern in patterns:
            if re.search(pattern, text, re.IGNORECASE):
                return dialect

    return IrishDialect.UNKNOWN


def _extract_year(text: str, filename: str) -> int | None:
    """Extract exam year from text or filename."""
    # Check filename first
    year_match = re.search(r"20\d{2}", filename)
    if year_match:
        return int(year_match.group())

    # Check text content
    year_match = re.search(r"(?:20[12]\d|199\d)", text[:1000])
    if year_match:
        return int(year_match.group())

    return None


def _extract_level(text: str, filename: str) -> str | None:
    """Extract exam level (Higher/Ordinary) from text or filename."""
    combined = f"{filename} {text[:500]}".lower()

    if "higher" in combined or "hl" in combined or "ardleibhéal" in combined:
        return "higher"
    elif "ordinary" in combined or "ol" in combined or "gnáthleibhéal" in combined:
        return "ordinary"

    return None


def _parse_segments(text: str) -> Iterator[dict[str, Any]]:
    """
    Parse transcript text into speaker segments.

    Yields dict with:
        - text: Segment text
        - speaker_role: Identified speaker role
        - dialect: Detected dialect (for Irish)
        - section: Exam section if identified
        - question_number: Question number if identified
    """
    lines = text.split("\n")
    current_segment: dict[str, Any] = {
        "text": "",
        "speaker_role": None,
        "dialect": None,
        "section": None,
        "question_number": None,
        "start_marker": None,
    }

    for line in lines:
        line = line.strip()
        if not line:
            continue

        # Check for section markers
        for pattern in SECTION_PATTERNS:
            match = re.search(pattern, line, re.IGNORECASE)
            if match:
                # Yield current segment if it has content
                if current_segment["text"]:
                    yield current_segment.copy()
                    current_segment = {
                        "text": "",
                        "speaker_role": None,
                        "dialect": None,
                        "section": None,
                        "question_number": None,
                        "start_marker": None,
                    }

                current_segment["section"] = match.group(1) if match.groups() else line
                current_segment["start_marker"] = line
                continue

        # Check for speaker roles
        for pattern in SPEAKER_PATTERNS:
            match = re.match(pattern, line, re.IGNORECASE)
            if match:
                # Yield current segment if it has content
                if current_segment["text"]:
                    yield current_segment.copy()
                    current_segment = {
                        "text": "",
                        "speaker_role": None,
                        "dialect": None,
                        "section": current_segment.get("section"),
                        "question_number": current_segment.get("question_number"),
                        "start_marker": None,
                    }

                current_segment["speaker_role"] = match.group(1)
                # Get text after speaker label
                remaining = line[match.end():].strip()
                if remaining:
                    current_segment["text"] = remaining
                continue

        # Check for question numbers
        q_match = re.match(r"(?:Question|Ceist|Q)\s*(\d+)", line, re.IGNORECASE)
        if q_match:
            if current_segment["text"]:
                yield current_segment.copy()
            current_segment["question_number"] = int(q_match.group(1))
            current_segment["text"] = ""
            continue

        # Check for dialect markers
        dialect = _detect_dialect(line)
        if dialect != IrishDialect.UNKNOWN:
            current_segment["dialect"] = dialect.value

        # Append text
        if current_segment["text"]:
            current_segment["text"] += " " + line
        else:
            current_segment["text"] = line

    # Yield final segment
    if current_segment["text"]:
        yield current_segment


def _extract_pdf_text(pdf_path: Path) -> str:
    """
    Extract text from PDF using pymupdf4llm.

    Falls back to basic PyMuPDF if pymupdf4llm not available.
    """
    try:
        import pymupdf4llm

        return pymupdf4llm.to_markdown(str(pdf_path))
    except ImportError:
        pass

    try:
        import fitz  # PyMuPDF

        doc = fitz.open(str(pdf_path))
        text = ""
        for page in doc:
            text += page.get_text()
        doc.close()
        return text
    except ImportError:
        logger.warning("pdf_extraction_no_library", path=str(pdf_path))
        return ""


def _parse_aural_transcript(
    pdf_path: Path,
    subject: str = "irish",
    exam_type: str = "LC",
) -> AuralTranscript:
    """
    Parse an SEC aural exam transcript PDF.

    Args:
        pdf_path: Path to the PDF file
        subject: Subject code (irish, french, german, spanish)
        exam_type: Exam type (LC, JC)

    Returns:
        Parsed AuralTranscript with segments
    """
    # Extract text
    raw_text = _extract_pdf_text(pdf_path)

    if not raw_text:
        return AuralTranscript(
            transcript_id=hashlib.md5(str(pdf_path).encode()).hexdigest()[:16],
            source_pdf=str(pdf_path),
            exam_type=exam_type,
            subject=subject,
            raw_text="",
        )

    # Extract metadata
    filename = pdf_path.name
    year = _extract_year(raw_text, filename)
    level = _extract_level(raw_text, filename)

    # Determine language from subject
    language_map = {
        "irish": "ga",
        "french": "fr",
        "german": "de",
        "spanish": "es",
    }
    language = language_map.get(subject.lower(), "unknown")

    # Generate transcript ID
    content_hash = hashlib.md5(raw_text.encode()).hexdigest()[:12]
    transcript_id = f"SEC_{exam_type}_{subject}_{year or 'unknown'}_{content_hash}"

    # Parse segments
    segments = []
    for idx, seg_data in enumerate(_parse_segments(raw_text)):
        segment = SpeakerSegment(
            segment_id=f"{transcript_id}_seg{idx:04d}",
            speaker_role=seg_data.get("speaker_role"),
            text=seg_data.get("text", ""),
            dialect=seg_data.get("dialect"),
            section=seg_data.get("section"),
            question_number=seg_data.get("question_number"),
            start_marker=seg_data.get("start_marker"),
        )
        segments.append(segment)

    return AuralTranscript(
        transcript_id=transcript_id,
        source_pdf=str(pdf_path),
        exam_type=exam_type,
        subject=subject,
        year=year,
        level=level,
        language=language,
        segments=segments,
        raw_text=raw_text,
    )


def _transcript_to_training_segments(
    transcript: AuralTranscript,
) -> Iterator[dict[str, Any]]:
    """
    Convert transcript segments to training-ready format.

    Yields dicts compatible with Canuint word alignment schema for unified dataset.
    """
    for segment in transcript.segments:
        if not segment.text or len(segment.text.strip()) < 5:
            continue

        yield {
            "segment_id": segment.segment_id,
            "transcript_id": transcript.transcript_id,
            "source": "sec_aural",
            "language": transcript.language,
            "dialect": segment.dialect or "standard",
            "text": segment.text.strip(),
            "speaker_role": segment.speaker_role,
            "section": segment.section,
            "question_number": segment.question_number,
            "exam_type": transcript.exam_type,
            "subject": transcript.subject,
            "year": transcript.year,
            "level": transcript.level,
            "source_pdf": transcript.source_pdf,
            "parsed_at": transcript.parsed_at,
        }


@dlt.source(name="sec_aural_transcripts")
def sec_aural_transcripts_source(
    pdf_dir: str | None = None,
    pdf_urls: list[str] | None = None,
    subjects: list[str] | None = None,
    exam_type: str = "LC",
) -> Iterator[DltResource]:
    """
    DLT source for SEC aural exam transcripts.

    Args:
        pdf_dir: Directory containing transcript PDFs
        pdf_urls: List of PDF URLs to download and parse
        subjects: Filter by subjects (default: all language subjects)
        exam_type: Exam type (LC, JC)

    Yields:
        DLT resources for transcripts, segments, and training data

    Examples:
        # Parse local PDFs
        pipeline.run(sec_aural_transcripts_source(
            pdf_dir="./downloads/sec_transcripts",
            subjects=["irish"],
        ))

        # Parse from URLs
        pipeline.run(sec_aural_transcripts_source(
            pdf_urls=["https://...pdf"],
        ))
    """
    target_subjects = subjects or ["irish", "french", "german", "spanish"]

    logger.info(
        "sec_aural_transcripts_init",
        pdf_dir=pdf_dir,
        subjects=target_subjects,
        exam_type=exam_type,
    )

    @dlt.resource(
        name="transcripts",
        write_disposition="merge",
        primary_key=["transcript_id"],
    )
    def transcripts_resource() -> Iterator[dict[str, Any]]:
        """Extract full transcript metadata."""
        pdf_paths = []

        # Collect PDFs from directory
        if pdf_dir:
            pdf_path = Path(pdf_dir)
            if pdf_path.exists():
                pdf_paths.extend(pdf_path.glob("**/*.pdf"))

        # Download PDFs from URLs
        if pdf_urls:
            import tempfile

            import httpx

            for url in pdf_urls:
                try:
                    response = httpx.get(url, timeout=60.0, follow_redirects=True)
                    response.raise_for_status()

                    # Save to temp file
                    filename = url.split("/")[-1]
                    if not filename.endswith(".pdf"):
                        filename = f"transcript_{hashlib.md5(url.encode()).hexdigest()[:8]}.pdf"

                    temp_path = Path(tempfile.gettempdir()) / filename
                    temp_path.write_bytes(response.content)
                    pdf_paths.append(temp_path)

                except Exception as e:
                    logger.warning("sec_transcript_download_error", url=url, error=str(e))

        # Parse each PDF
        for pdf_path in pdf_paths:
            # Detect subject from filename
            subject = "unknown"
            filename_lower = pdf_path.name.lower()
            for s in target_subjects:
                if s in filename_lower or s[:2] in filename_lower:
                    subject = s
                    break

            # Also check for "gaeilge"
            if subject == "unknown" and "gaeilge" in filename_lower:
                subject = "irish"

            try:
                transcript = _parse_aural_transcript(
                    pdf_path,
                    subject=subject,
                    exam_type=exam_type,
                )

                yield {
                    "transcript_id": transcript.transcript_id,
                    "source_pdf": transcript.source_pdf,
                    "exam_type": transcript.exam_type,
                    "subject": transcript.subject,
                    "year": transcript.year,
                    "level": transcript.level,
                    "language": transcript.language,
                    "segment_count": len(transcript.segments),
                    "total_text_length": len(transcript.raw_text),
                    "parsed_at": transcript.parsed_at,
                }
            except Exception as e:
                logger.warning(
                    "sec_transcript_parse_error",
                    path=str(pdf_path),
                    error=str(e),
                )

    @dlt.resource(
        name="segments",
        write_disposition="merge",
        primary_key=["segment_id"],
        columns={
            "segment_id": {"data_type": "text"},
            "transcript_id": {"data_type": "text"},
            "source": {"data_type": "text"},
            "language": {"data_type": "text"},
            "dialect": {"data_type": "text"},
            "text": {"data_type": "text"},
            "speaker_role": {"data_type": "text"},
            "section": {"data_type": "text"},
            "question_number": {"data_type": "bigint"},
            "exam_type": {"data_type": "text"},
            "subject": {"data_type": "text"},
            "year": {"data_type": "bigint"},
            "level": {"data_type": "text"},
            "source_pdf": {"data_type": "text"},
            "parsed_at": {"data_type": "timestamp"},
        },
    )
    def segments_resource() -> Iterator[dict[str, Any]]:
        """Extract individual segments for training."""
        pdf_paths = []

        if pdf_dir:
            pdf_path = Path(pdf_dir)
            if pdf_path.exists():
                pdf_paths.extend(pdf_path.glob("**/*.pdf"))

        if pdf_urls:
            import tempfile

            import httpx

            for url in pdf_urls:
                try:
                    response = httpx.get(url, timeout=60.0, follow_redirects=True)
                    response.raise_for_status()

                    filename = url.split("/")[-1]
                    if not filename.endswith(".pdf"):
                        filename = f"transcript_{hashlib.md5(url.encode()).hexdigest()[:8]}.pdf"

                    temp_path = Path(tempfile.gettempdir()) / filename
                    temp_path.write_bytes(response.content)
                    pdf_paths.append(temp_path)
                except Exception as e:
                    logger.warning("sec_transcript_download_error", url=url, error=str(e))

        for pdf_path in pdf_paths:
            subject = "unknown"
            filename_lower = pdf_path.name.lower()
            for s in target_subjects:
                if s in filename_lower or s[:2] in filename_lower:
                    subject = s
                    break

            if subject == "unknown" and "gaeilge" in filename_lower:
                subject = "irish"

            try:
                transcript = _parse_aural_transcript(pdf_path, subject=subject, exam_type=exam_type)
                yield from _transcript_to_training_segments(transcript)
            except Exception as e:
                logger.warning("sec_segment_parse_error", path=str(pdf_path), error=str(e))

    @dlt.resource(
        name="dialect_tagged_segments",
        write_disposition="merge",
        primary_key=["segment_id"],
    )
    def dialect_tagged_resource() -> Iterator[dict[str, Any]]:
        """Extract only Irish segments with dialect tags for TTS training."""
        pdf_paths = []

        if pdf_dir:
            pdf_path = Path(pdf_dir)
            if pdf_path.exists():
                pdf_paths.extend(pdf_path.glob("**/*.pdf"))

        for pdf_path in pdf_paths:
            filename_lower = pdf_path.name.lower()
            if "irish" not in filename_lower and "gaeilge" not in filename_lower:
                continue

            try:
                transcript = _parse_aural_transcript(pdf_path, subject="irish", exam_type=exam_type)

                for segment_data in _transcript_to_training_segments(transcript):
                    # Only yield if dialect is identified
                    if segment_data.get("dialect") and segment_data["dialect"] != "unknown":
                        yield segment_data
            except Exception as e:
                logger.warning("sec_dialect_parse_error", path=str(pdf_path), error=str(e))

    return transcripts_resource, segments_resource, dialect_tagged_resource


# Convenience functions


def irish_lc_transcripts_source(
    pdf_dir: str | None = None,
    pdf_urls: list[str] | None = None,
):
    """DLT source for Irish LC aural transcripts only."""
    return sec_aural_transcripts_source(
        pdf_dir=pdf_dir,
        pdf_urls=pdf_urls,
        subjects=["irish"],
        exam_type="LC",
    )


def languages_lc_transcripts_source(
    pdf_dir: str | None = None,
    pdf_urls: list[str] | None = None,
):
    """DLT source for all LC language aural transcripts."""
    return sec_aural_transcripts_source(
        pdf_dir=pdf_dir,
        pdf_urls=pdf_urls,
        subjects=["irish", "french", "german", "spanish"],
        exam_type="LC",
    )
