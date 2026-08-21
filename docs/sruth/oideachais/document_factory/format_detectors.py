"""
Format Detection for Curriculum Documents.

Automatically detects document source (NCCA, SEC, Circular) from content
and metadata, based on historical-document-analysis patterns.
"""
from __future__ import annotations

import logging
import re
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Optional

from .base import DocumentSource, DocumentFormat

logger = logging.getLogger(__name__)


@dataclass
class DetectionResult:
    """Result of document source detection."""

    source: DocumentSource
    confidence: float  # 0.0-1.0
    matches: list[str] = field(default_factory=list)
    metadata_extracted: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        return {
            "source": self.source.value,
            "confidence": self.confidence,
            "matches": self.matches,
            "metadata_extracted": self.metadata_extracted,
        }


class FormatDetector:
    """
    Detect curriculum document source from content and metadata.

    Uses pattern matching to identify:
    - NCCA: curriculumonline.ie, National Council for Curriculum
    - SEC: examinations.ie, State Examinations Commission
    - Circular: Department of Education circulars
    - Textbook: Publisher patterns
    """

    # Pattern definitions for each source type
    PATTERNS: dict[DocumentSource, list[str]] = {
        DocumentSource.NCCA: [
            r"curriculumonline\.ie",
            r"ncca\.ie",
            r"NCCA",
            r"National Council for Curriculum",
            r"Curriculum Specification",
            r"Junior Cycle Specification",
            r"Senior Cycle Specification",
            r"Learning Outcome[s]?",
            r"Strand Unit",
        ],
        DocumentSource.SEC: [
            r"examinations\.ie",
            r"State Examinations Commission",
            r"SEC",
            r"Leaving Certificate",
            r"Junior Certificate",
            r"Marking Scheme",
            r"Chief Examiner",
            r"Coimisiún na Scrúduithe Stáit",
            r"(?:Higher|Ordinary|Foundation) Level",
            r"Total Marks?:\s*\d+",
            r"Answer (?:all|any) \d+ questions?",
        ],
        DocumentSource.CIRCULAR: [
            r"Circular\s+\d+/\d+",
            r"Department of Education",
            r"gov\.ie/education",
            r"An Roinn Oideachais",
            r"To:\s*(?:Boards of Management|Principals)",
            r"CIRCULAR LETTER",
            r"This Circular",
        ],
        DocumentSource.TEXTBOOK: [
            r"(?:Gill|Folens|Edco|CJ Fallon|Educational Company)",
            r"ISBN\s*[\d-]+",
            r"Chapter\s+\d+",
            r"Textbook",
            r"Workbook",
            r"Student Edition",
            r"Teacher(?:'s)? Guide",
        ],
        DocumentSource.RESOURCE: [
            r"Lesson Plan",
            r"Teaching Resource",
            r"Worksheet",
            r"Activity Sheet",
            r"Assessment Task",
            r"Rubric",
        ],
    }

    # URL-based detection
    URL_PATTERNS: dict[str, DocumentSource] = {
        r"curriculumonline\.ie": DocumentSource.NCCA,
        r"ncca\.ie": DocumentSource.NCCA,
        r"examinations\.ie": DocumentSource.SEC,
        r"gov\.ie/(?:en/)?(?:circular|publication)": DocumentSource.CIRCULAR,
        r"gov\.ie/education": DocumentSource.CIRCULAR,
        r"education\.ie": DocumentSource.CIRCULAR,
    }

    # Filename-based detection
    FILENAME_PATTERNS: dict[str, DocumentSource] = {
        r"specification": DocumentSource.NCCA,
        r"syllabus": DocumentSource.NCCA,
        r"marking.?scheme": DocumentSource.SEC,
        r"exam.?paper": DocumentSource.SEC,
        r"chief.?examiner": DocumentSource.SEC,
        r"circular": DocumentSource.CIRCULAR,
        r"cl\d+_\d+": DocumentSource.CIRCULAR,
    }

    # Subject extraction patterns
    SUBJECT_PATTERNS: list[tuple[str, str]] = [
        # Irish patterns
        (r"(?:Mathematics|Mata(?:maitic)?)", "Mathematics"),
        (r"(?:English|Béarla)", "English"),
        (r"(?:Irish|Gaeilge)", "Irish"),
        (r"(?:History|Stair)", "History"),
        (r"(?:Geography|Tíreolaíocht)", "Geography"),
        (r"(?:Science|Eolaíocht)", "Science"),
        (r"(?:Physics|Fisic)", "Physics"),
        (r"(?:Chemistry|Ceimic)", "Chemistry"),
        (r"(?:Biology|Bitheolaíocht)", "Biology"),
        (r"(?:Business|Gnó)", "Business"),
        (r"(?:Accounting|Cuntasaíocht)", "Accounting"),
        (r"(?:Economics|Eacnamaíocht)", "Economics"),
        (r"(?:Art|Ealaín)", "Art"),
        (r"(?:Music|Ceol)", "Music"),
        (r"(?:French|Fraincis)", "French"),
        (r"(?:German|Gearmáinis)", "German"),
        (r"(?:Spanish|Spáinnis)", "Spanish"),
    ]

    # Level extraction patterns
    LEVEL_PATTERNS: dict[str, str] = {
        r"Junior\s+(?:Cycle|Certificate|Cert)": "junior",
        r"Senior\s+(?:Cycle|Certificate)": "senior",
        r"Leaving\s+Cert(?:ificate)?": "senior",
        r"Primary": "primary",
        r"Post-?Primary": "junior",  # Could be either, default junior
    }

    # Year patterns for SEC
    YEAR_PATTERNS: list[str] = [
        r"(?:20\d{2})\s*(?:Examination|Exam|Paper)",
        r"(?:Examination|Exam|Paper)\s*(?:20\d{2})",
        r"(?:June|Summer|Autumn|Winter)\s*(?:20\d{2})",
    ]

    def __init__(self):
        """Initialize detector with compiled patterns."""
        self._compiled_patterns: dict[DocumentSource, list[re.Pattern]] = {}

        for source, patterns in self.PATTERNS.items():
            self._compiled_patterns[source] = [
                re.compile(p, re.IGNORECASE) for p in patterns
            ]

    def detect(
        self,
        content: str,
        metadata: Optional[dict[str, Any]] = None,
        url: Optional[str] = None,
        filename: Optional[str] = None,
    ) -> DetectionResult:
        """
        Detect document source from content and metadata.

        Args:
            content: Document text content
            metadata: Optional metadata dictionary
            url: Optional source URL
            filename: Optional source filename

        Returns:
            DetectionResult with source type and confidence
        """
        metadata = metadata or {}
        scores: dict[DocumentSource, float] = {source: 0.0 for source in DocumentSource}
        all_matches: dict[DocumentSource, list[str]] = {source: [] for source in DocumentSource}

        # 1. URL-based detection (highest confidence)
        if url:
            for pattern, source in self.URL_PATTERNS.items():
                if re.search(pattern, url, re.IGNORECASE):
                    scores[source] += 0.5
                    all_matches[source].append(f"url:{pattern}")

        # 2. Filename-based detection
        if filename:
            for pattern, source in self.FILENAME_PATTERNS.items():
                if re.search(pattern, filename, re.IGNORECASE):
                    scores[source] += 0.3
                    all_matches[source].append(f"filename:{pattern}")

        # 3. Content pattern matching
        for source, patterns in self._compiled_patterns.items():
            for pattern in patterns:
                matches = pattern.findall(content[:10000])  # First 10k chars
                if matches:
                    # More matches = higher confidence
                    match_score = min(len(matches) * 0.1, 0.4)
                    scores[source] += match_score
                    all_matches[source].append(f"content:{pattern.pattern[:50]}")

        # 4. Find best match
        best_source = max(scores, key=scores.get)  # type: ignore
        best_score = scores[best_source]

        # Default to UNKNOWN if no strong matches
        if best_score < 0.2:
            best_source = DocumentSource.UNKNOWN
            best_score = 0.0

        # 5. Extract metadata
        extracted_metadata = self._extract_metadata(content, best_source)

        return DetectionResult(
            source=best_source,
            confidence=min(best_score, 1.0),
            matches=all_matches[best_source][:5],  # Top 5 matches
            metadata_extracted=extracted_metadata,
        )

    def _extract_metadata(
        self,
        content: str,
        source: DocumentSource,
    ) -> dict[str, Any]:
        """Extract metadata based on detected source type."""
        metadata: dict[str, Any] = {}

        # Extract subject
        for pattern, subject in self.SUBJECT_PATTERNS:
            if re.search(pattern, content, re.IGNORECASE):
                metadata["subject"] = subject
                break

        # Extract level
        for pattern, level in self.LEVEL_PATTERNS.items():
            if re.search(pattern, content, re.IGNORECASE):
                metadata["level"] = level
                break

        # Source-specific extraction
        if source == DocumentSource.SEC:
            # Extract exam year
            for pattern in self.YEAR_PATTERNS:
                match = re.search(pattern, content, re.IGNORECASE)
                if match:
                    year_match = re.search(r"20\d{2}", match.group())
                    if year_match:
                        metadata["exam_year"] = int(year_match.group())
                        break

            # Extract level (Higher/Ordinary/Foundation)
            level_match = re.search(
                r"(Higher|Ordinary|Foundation)\s*Level",
                content,
                re.IGNORECASE,
            )
            if level_match:
                metadata["exam_level"] = level_match.group(1).title()

            # Extract total marks
            marks_match = re.search(r"Total\s*Marks?:\s*(\d+)", content, re.IGNORECASE)
            if marks_match:
                metadata["total_marks"] = int(marks_match.group(1))

        elif source == DocumentSource.CIRCULAR:
            # Extract circular number
            circular_match = re.search(
                r"Circular\s+(\d+/\d+)",
                content,
                re.IGNORECASE,
            )
            if circular_match:
                metadata["circular_number"] = circular_match.group(1)

        elif source == DocumentSource.NCCA:
            # Extract strand
            strand_match = re.search(
                r"Strand:\s*([^\n]+)",
                content,
                re.IGNORECASE,
            )
            if strand_match:
                metadata["strand"] = strand_match.group(1).strip()

            # Count learning outcomes
            lo_matches = re.findall(
                r"Learning\s+Outcome\s+\d",
                content,
                re.IGNORECASE,
            )
            if lo_matches:
                metadata["learning_outcome_count"] = len(lo_matches)

        return metadata


def detect_document_source(
    content: str,
    url: Optional[str] = None,
    filename: Optional[str] = None,
    metadata: Optional[dict[str, Any]] = None,
) -> DetectionResult:
    """
    Convenience function to detect document source.

    Args:
        content: Document text content
        url: Optional source URL
        filename: Optional source filename
        metadata: Optional metadata dictionary

    Returns:
        DetectionResult with source type and confidence
    """
    detector = FormatDetector()
    return detector.detect(
        content=content,
        metadata=metadata,
        url=url,
        filename=filename,
    )


def detect_format(file_path: Path) -> DocumentFormat:
    """Detect document format from file extension."""
    suffix = file_path.suffix.lower()

    format_map = {
        ".pdf": DocumentFormat.PDF,
        ".html": DocumentFormat.HTML,
        ".htm": DocumentFormat.HTML,
        ".docx": DocumentFormat.DOCX,
        ".doc": DocumentFormat.DOCX,
        ".pptx": DocumentFormat.PPTX,
        ".ppt": DocumentFormat.PPTX,
        ".xml": DocumentFormat.XML,
        ".json": DocumentFormat.JSON,
        ".md": DocumentFormat.MARKDOWN,
        ".markdown": DocumentFormat.MARKDOWN,
        ".txt": DocumentFormat.TEXT,
    }

    return format_map.get(suffix, DocumentFormat.UNKNOWN)
