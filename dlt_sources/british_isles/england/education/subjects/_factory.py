"""27 per-subject England DLT sources (BIEP v2).

Per the 2026-07-21-biep-v2-england-aqa-ocr-baml-pipeline-v1 change.

3 awarding bodies (AQA, OCR, Edexcel) × 9 priority subjects
(mathematics, english_language, english_literature, chemistry,
biology, physics, computer_science, history, geography) = 27 sources.

Each source emits rows tagged with:
- `country_code = "england"`
- `jurisdiction = "england"`
- `exam_board ∈ {aqa, ocr, edexcel}`
- `qualification_level ∈ {gcse, a_level}`
- `source_id = "british_isles.england.education.{board}_{subject}"`

The destination DuckLake namespace is:
    cianfhoghlaim.education.british_isles.england.<board>.<subject>.<qualification_level>
"""
from __future__ import annotations

import hashlib
import os
import re
from datetime import UTC, datetime
from pathlib import Path

import dlt
import structlog

logger = structlog.get_logger(__name__)

EXAM_BOARDS: tuple[str, ...] = ("aqa", "ocr", "edexcel")
PRIORITY_SUBJECTS: tuple[str, ...] = (
    "mathematics",
    "english_language",
    "english_literature",
    "chemistry",
    "biology",
    "physics",
    "computer_science",
    "history",
    "geography",
)
QUALIFICATION_LEVELS: tuple[str, ...] = ("gcse", "a_level")

ENGLAND_CACHE_ROOT = Path(
    os.getenv("STEDDING_INGEST_QUEUE", "/stedding/ingest_queue")
) / "england"


def list_england_source_ids() -> list[str]:
    """Return the canonical 27 England source IDs (board × subject)."""
    return [
        f"british_isles.england.education.{board}_{subject}"
        for board in EXAM_BOARDS
        for subject in PRIORITY_SUBJECTS
    ]


def _file_hash(path: Path) -> str:
    sha = hashlib.sha256()
    with open(path, "rb") as f:
        for chunk in iter(lambda: f.read(8192), b""):
            sha.update(chunk)
    return sha.hexdigest()


def _pdf_text_stub(path: Path) -> str:
    return f"[PDF_TEXT_STUB] file={path.name} size={path.stat().st_size}"


def build_england_subject_source(
    exam_board: str,
    subject: str,
    qualification_level: str,
    cache_dir: Path | None = None,
):
    """Build a DLT source for one (board, subject, qualification_level) triple.

    Parameters
    ----------
    exam_board : str
        One of `{"aqa", "ocr", "edexcel"}`.
    subject : str
        One of the 9 priority subjects (`PRIORITY_SUBJECTS`).
    qualification_level : str
        One of `{"gcse", "a_level"}`.
    cache_dir : Path | None
        Override the default cache dir.

    Returns
    -------
    dlt.Source
        A DLT source with 2 resources:
        - `eng_<board>_<subject>_qualifications` — per-PDF qualification rows
        - `eng_<board>_<subject>_metadata` — per-(board, subject) metadata row
    """
    if exam_board not in EXAM_BOARDS:
        raise ValueError(
            f"Unknown exam board '{exam_board}'. Must be one of {EXAM_BOARDS}."
        )
    if subject not in PRIORITY_SUBJECTS:
        raise ValueError(
            f"Unknown subject '{subject}'. Must be one of {PRIORITY_SUBJECTS}."
        )
    if qualification_level not in QUALIFICATION_LEVELS:
        raise ValueError(
            f"Unknown qualification level '{qualification_level}'. "
            f"Must be one of {QUALIFICATION_LEVELS}."
        )

    effective_cache_dir = (
        cache_dir
        if cache_dir is not None
        else ENGLAND_CACHE_ROOT / exam_board / subject / qualification_level
    )
    source_id = (
        f"british_isles.england.education."
        f"{exam_board}_{subject}_{qualification_level.replace('_', '')}"
    )

    @dlt.resource(
        name=f"eng_{exam_board}_{subject}_{qualification_level}_qualifications",
        write_disposition="merge",
        primary_key=["content_hash"],
    )
    def eng_qualifications():
        if not effective_cache_dir.exists():
            logger.warning(
                "england_cache_dir_missing",
                exam_board=exam_board,
                subject=subject,
                qualification_level=qualification_level,
                path=str(effective_cache_dir),
            )
            return
        for pdf_path in sorted(effective_cache_dir.glob("*.pdf")):
            content_hash = _file_hash(pdf_path)
            m = re.search(r"(20\d{2}|19\d{2})", pdf_path.name)
            spec_year = int(m.group(1)) if m else None
            yield {
                "source_id": source_id,
                "exam_board": exam_board,
                "subject": subject,
                "qualification_level": qualification_level,
                "language": "en",
                "filename": pdf_path.name,
                "file_path": str(pdf_path),
                "file_size_bytes": pdf_path.stat().st_size,
                "content_hash": content_hash,
                "pdf_text": _pdf_text_stub(pdf_path),
                "specification_year": spec_year,
                "ingested_at": datetime.now(UTC).isoformat(),
                "country_code": "england",
                "jurisdiction": "england",
                "education_stage": qualification_level,
                "namespace": (
                    "cianfhoghlaim.education.british_isles.england."
                    f"{exam_board}.{subject}.{qualification_level}"
                ),
            }

    @dlt.resource(
        name=f"eng_{exam_board}_{subject}_{qualification_level}_metadata",
        write_disposition="merge",
        primary_key=["exam_board", "subject", "qualification_level"],
    )
    def eng_metadata():
        yield {
            "source_id": source_id,
            "exam_board": exam_board,
            "subject": subject,
            "qualification_level": qualification_level,
            "country_code": "england",
            "jurisdiction": "england",
            "namespace": (
                "cianfhoghlaim.education.british_isles.england."
                f"{exam_board}.{subject}.{qualification_level}"
            ),
            "uses_local_scrapes": os.getenv("USE_LOCAL_SCRAPES", "true").lower() == "true",
            "first_ingested_at": datetime.now(UTC).isoformat(),
        }

    return eng_qualifications, eng_metadata


# Generate the 27 board × subject factories at import time.
# The 54 = 27 boards × 2 qualification levels is the full surface.
__all__: list[str] = []
for _board in EXAM_BOARDS:
    for _subject in PRIORITY_SUBJECTS:
        for _qualification_level in QUALIFICATION_LEVELS:
            _name = f"{_board}_{_subject}_{_qualification_level.replace('_', '')}_source"

            def _make(
                b: str = _board,
                s: str = _subject,
                ql: str = _qualification_level,
            ):
                return build_england_subject_source(b, s, ql)

            globals()[_name] = _make
            __all__.append(_name)
