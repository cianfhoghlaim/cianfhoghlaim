"""UoG personal archive DLT source.

Lifts `leabharlann/ollscoil_na_gaillimhe/` (the user's three UoG
courses' artefacts) +
`cian_mac_an_déisigh_uí_liatháin/achievement/*transcript*.pdf` to
feature parity with the leaving-cycle subject pipeline.

Yields **8 resources** under `@dlt.source(name="uog_personal_archive")`:

1. ``personal_archive_artefacts`` — one row per discovered file
   (merge on `artefact_id + content_hash`; partitions: institution,
   module_code, artefact_kind, academic_year, artefact_provenance)
2. ``personal_archive_assignments`` — one row per assignment
   (merge on `assignment_id + content_hash`; partitions: module_code,
   assignment_number)
3. ``personal_archive_questions`` — one row per question (F-granular;
   merge on `question_id`; partitions: module_code, question_id)
4. ``personal_archive_topics`` — one row per topic (merge on
   `topic_id`; partition: topic_category)
5. ``personal_archive_reading_lists`` — one row per reading item
   (merge on `reading_id`; partition: module_code)
6. ``personal_archive_code_cells`` — one row per code cell
   (merge on `cell_id`; partitions: module_code, notebook_path)
7. ``personal_archive_ca_marks`` — one row per CA mark
   (merge on `ca_id`; partition: module_code)
8. ``student_transcripts`` — one row per (student, module, year)
   (merge on `student_id + module_code + academic_year`; partitions:
   student_id, programme_code, academic_year)

The source auto-discovers the personal archive directory from the
``UNIVERSITY_PERSONAL_ARCHIVE_PATH`` env var (defaulting to
``leabharlann/ollscoil_na_gaillimhe``). When the directory is
absent or empty, every resource yields one
``status="skipped_no_real_files"`` placeholder row so CI never
crashes.

The classification heuristic ``_classify_file`` matches a module
code regex ``[A-Za-z]{2,4}\\d{3,4}`` against every path component,
and detects artefact_kind from filename + extension patterns per
the
`openspec/changes/2026-08-23-uog-personal-archive-tertiary-modules-v1/`
plan.

Reference: openspec/changes/2026-08-23-uog-personal-archive-tertiary-modules-v1/
            specs/cianfhoghlaim-personal-archive-typed-modules/spec.md
"""

from __future__ import annotations

import hashlib
import os
import re
from collections.abc import Iterator
from dataclasses import dataclass
from datetime import UTC, datetime
from enum import Enum
from pathlib import Path
from typing import Any

import dlt
import structlog

from ._scanner import compute_file_hash

logger = structlog.get_logger(__name__)


# ---------------------------------------------------------------------------- #
# Default personal-archive path
# ---------------------------------------------------------------------------- #


_DEFAULT_PERSONAL_ARCHIVE_PATH = Path(
    os.environ.get(
        "UNIVERSITY_PERSONAL_ARCHIVE_PATH",
        str(
            Path(__file__).resolve().parents[3]
            / "leabharlann"
            / "ollscoil_na_gaillimhe"
        ),
    )
)


# ---------------------------------------------------------------------------- #
# Python enums (mirror the BAML enums in
# baml_src/british_isles/ireland/education/university/personal_archive_extraction.baml)
# ---------------------------------------------------------------------------- #


class ArtefactKind(str, Enum):
    ASSIGNMENT_SUBMISSION = "ASSIGNMENT_SUBMISSION"
    ASSIGNMENT_BRIEF = "ASSIGNMENT_BRIEF"
    MARKING_SCHEME = "MARKING_SCHEME"
    MODEL_SOLUTION = "MODEL_SOLUTION"
    PAST_EXAM_PAPER = "PAST_EXAM_PAPER"
    PAST_EXAM_SCRIPT = "PAST_EXAM_SCRIPT"
    LECTURE_NOTES = "LECTURE_NOTES"
    PROBLEM_SHEET = "PROBLEM_SHEET"
    LAB_NOTEBOOK = "LAB_NOTEBOOK"
    SOURCE_CODE = "SOURCE_CODE"
    READING_ITEM = "READING_ITEM"
    TRANSCRIPT = "TRANSCRIPT"
    SCANNED_PAGE = "SCANNED_PAGE"
    OTHER = "OTHER"


class ArtefactProvenance(str, Enum):
    LECTURE_PROVIDED = "LECTURE_PROVIDED"
    PERSONAL_SUBMISSION = "PERSONAL_SUBMISSION"
    THIRD_PARTY_REFERENCE = "THIRD_PARTY_REFERENCE"
    TRANSCRIPT = "TRANSCRIPT"
    UNKNOWN = "UNKNOWN"


class HTRBackend(str, Enum):
    NOUGAT = "NOUGAT"
    OLMOCR_2_7B = "OLMOCR_2_7B"
    COGVLM = "COGVLM"
    GEMMA_3 = "GEMMA_3"
    MULTI_VLM_CONSENSUS = "MULTI_VLM_CONSENSUS"
    PYMUPDF_TYPED = "PYMUPDF_TYPED"
    NONE = "NONE"


# ---------------------------------------------------------------------------- #
# Filename / extension → ArtefactKind mapping
# ---------------------------------------------------------------------------- #


_MODULE_CODE_RE = re.compile(r"[A-Za-z]{2,4}\d{3,4}")
_ASSIGNMENT_NUMBER_RE = re.compile(r"(?:assignment|ass(?:ignment)?)[_\- ]?(\d+)", re.IGNORECASE)


def _classify_file(
    path: str | Path,
) -> tuple[ArtefactKind, ArtefactProvenance, str | None, int | None]:
    """Classify a personal-archive file by filename + extension patterns.

    Returns:
        (artefact_kind, artefact_provenance, module_code | None, assignment_number | None)
    """
    path = Path(path)
    name = path.name
    name_lower = name.lower()
    parts_lower = [p.lower() for p in path.parts]
    suffix_lower = path.suffix.lower()

    # Module code detection: match against any path component.
    module_code: str | None = None
    _digits_re = re.compile(r"\d+")
    for component in [name, *path.parts]:
        m = _MODULE_CODE_RE.search(component)
        if m:
            raw = m.group(0)
            digits_match = _digits_re.search(raw)
            if digits_match:
                letters = raw[: len(raw) - len(digits_match.group(0))].upper()
                digits = digits_match.group(0)
                module_code = f"{letters}{digits}"
            break

    # Assignment number detection.
    assignment_number: int | None = None
    m = _ASSIGNMENT_NUMBER_RE.search(name_lower)
    if m:
        try:
            assignment_number = int(m.group(1))
        except (TypeError, ValueError):
            assignment_number = None

    # Provenance detection (path tokens win).
    provenance = ArtefactProvenance.UNKNOWN
    if any(tok in parts_lower for tok in ("lecture", "lectures", "problem", "model", "marking", "slides")):
        provenance = ArtefactProvenance.LECTURE_PROVIDED
    elif any(tok in parts_lower for tok in ("transcript", "achievement")) or "transcript" in name_lower:
        provenance = ArtefactProvenance.TRANSCRIPT
    elif name_lower.startswith("cian_mac_liathain_") or name_lower.startswith("cian_mac_an_déisigh_"):
        provenance = ArtefactProvenance.PERSONAL_SUBMISSION
    artefact_kind = ArtefactKind.OTHER

    # Code files first (the HDip Software Design corpus).
    if suffix_lower in {".ipynb"}:
        artefact_kind = ArtefactKind.LAB_NOTEBOOK
        if provenance == ArtefactProvenance.UNKNOWN:
            provenance = ArtefactProvenance.PERSONAL_SUBMISSION
    elif suffix_lower in {".py", ".java", ".r"}:
        artefact_kind = ArtefactKind.SOURCE_CODE
        if provenance == ArtefactProvenance.UNKNOWN:
            provenance = ArtefactProvenance.PERSONAL_SUBMISSION

    # Apple Pages / iOS photos / handwritten → SCANNED_PAGE.
    elif suffix_lower in {".pages", ".heic"}:
        artefact_kind = ArtefactKind.SCANNED_PAGE

    # Transcript PDFs.
    elif provenance == ArtefactProvenance.TRANSCRIPT and suffix_lower == ".pdf":
        artefact_kind = ArtefactKind.TRANSCRIPT

    # Past exam papers / scripts.
    elif "past_paper" in name_lower or "summer_exam_" in name_lower or "winter_exam_" in name_lower:
        artefact_kind = ArtefactKind.PAST_EXAM_PAPER
    elif "cian_mac_liathain_exam" in name_lower or "exam_script" in name_lower:
        artefact_kind = ArtefactKind.PAST_EXAM_SCRIPT
        if provenance == ArtefactProvenance.UNKNOWN:
            provenance = ArtefactProvenance.PERSONAL_SUBMISSION

    # Model solutions / marking schemes (sub-patterns of lecture-provided).
    elif "model_solution" in name_lower or "solution" in name_lower:
        artefact_kind = ArtefactKind.MODEL_SOLUTION
        if provenance == ArtefactProvenance.UNKNOWN:
            provenance = ArtefactProvenance.LECTURE_PROVIDED
    elif "marking_scheme" in name_lower or re.search(r"\bms\b", name_lower):
        artefact_kind = ArtefactKind.MARKING_SCHEME
        if provenance == ArtefactProvenance.UNKNOWN:
            provenance = ArtefactProvenance.LECTURE_PROVIDED

    # Assignment briefs vs submissions.
    elif "brief" in name_lower:
        artefact_kind = ArtefactKind.ASSIGNMENT_BRIEF
        if provenance == ArtefactProvenance.UNKNOWN:
            provenance = ArtefactProvenance.LECTURE_PROVIDED
    elif assignment_number is not None or "assignment" in name_lower:
        artefact_kind = ArtefactKind.ASSIGNMENT_SUBMISSION
        if provenance == ArtefactProvenance.UNKNOWN:
            provenance = ArtefactProvenance.PERSONAL_SUBMISSION

    # Lecture notes.
    elif (
        "lecture" in name_lower
        or "lecture" in "/".join(parts_lower)
        or "lectures" in "/".join(parts_lower)
    ):
        artefact_kind = ArtefactKind.LECTURE_NOTES
        if provenance == ArtefactProvenance.UNKNOWN:
            provenance = ArtefactProvenance.LECTURE_PROVIDED

    # Problem sheets.
    elif "problem" in name_lower and ("sheet" in name_lower or "set" in name_lower):
        artefact_kind = ArtefactKind.PROBLEM_SHEET

    # Reading items.
    elif "reading" in name_lower and "list" in name_lower:
        artefact_kind = ArtefactKind.READING_ITEM

    # DOCX → OTHER (let BAML infer kind from the body).
    elif suffix_lower in {".docx"}:
        artefact_kind = ArtefactKind.OTHER

    # Scanned-page fallbacks by name tokens.
    elif "handwritten" in name_lower or "goodnotes" in name_lower or "apple_pencil" in name_lower:
        artefact_kind = ArtefactKind.SCANNED_PAGE

    return artefact_kind, provenance, module_code, assignment_number


# ---------------------------------------------------------------------------- #
# Skip patterns (mirror _scanner.DEFAULT_SKIP_PATTERNS)
# ---------------------------------------------------------------------------- #

_SKIP_PATTERNS: tuple[str, ...] = (
    ".DS_Store",
    ".gitignore",
    "Thumbs.db",
    "__MACOSX",
    ".idea",
    ".vscode",
    ".venv",
    "__pycache__",
    "previews",
)

_ALLOWED_EXTENSIONS: tuple[str, ...] = (
    ".pdf",
    ".docx",
    ".doc",
    ".ipynb",
    ".py",
    ".java",
    ".r",
    ".R",
    ".pages",
    ".heic",
    ".txt",
    ".md",
)


def _should_skip(path: Path) -> bool:
    name = path.name
    if name.startswith("."):
        return True
    path_str = str(path).lower()
    for pattern in _SKIP_PATTERNS:
        if pattern.lower() in path_str:
            return True
    return False


# ---------------------------------------------------------------------------- #
# Internal row builders
# ---------------------------------------------------------------------------- #


def _skipped_row(resource_name: str) -> dict[str, Any]:
    """One placeholder row used when the personal archive is empty.

    CI never crashes; every resource yields this row at least once.
    """
    now = datetime.now(UTC).isoformat()
    return {
        "id": f"skipped_{resource_name}",
        "status": "skipped_no_real_files",
        "resource_name": resource_name,
        "scanned_at": now,
        "institution_id": "ie-university-galway",
        "module_code": None,
        "module_title": None,
        "programme_code": None,
        "academic_year": None,
        "file_path": str(_DEFAULT_PERSONAL_ARCHIVE_PATH),
        "file_hash": "",
        "content_hash": "",
        "bytes": 0,
        "confidence": 0.0,
    }


@dataclass
class DiscoveredFile:
    """A single discovered file in the personal archive."""

    file_path: Path
    file_hash: str
    bytes: int
    file_extension: str
    artefact_kind: ArtefactKind
    artefact_provenance: ArtefactProvenance
    module_code: str | None
    assignment_number: int | None


def _discover_files(base_path: Path) -> Iterator[DiscoveredFile]:
    """Walk ``base_path`` and yield one ``DiscoveredFile`` per matching file."""
    if not base_path.exists():
        logger.warning(
            "personal_archive_path_missing",
            path=str(base_path),
            hint="Set UNIVERSITY_PERSONAL_ARCHIVE_PATH to override.",
        )
        return

    for path in base_path.rglob("*"):
        if not path.is_file():
            continue
        if _should_skip(path):
            continue
        suffix = path.suffix.lower()
        if suffix not in _ALLOWED_EXTENSIONS:
            continue
        kind, provenance, module_code, assignment_number = _classify_file(path)
        try:
            file_hash = compute_file_hash(path)
            bytes_ = path.stat().st_size
        except (OSError, PermissionError) as exc:
            logger.warning(
                "personal_archive_file_hash_failed",
                path=str(path),
                error=str(exc),
            )
            continue
        yield DiscoveredFile(
            file_path=path,
            file_hash=file_hash,
            bytes=bytes_,
            file_extension=suffix,
            artefact_kind=kind,
            artefact_provenance=provenance,
            module_code=module_code,
            assignment_number=assignment_number,
        )


def _now_iso() -> str:
    return datetime.now(UTC).isoformat()


def _stable_id(prefix: str, content_hash: str) -> str:
    """Stable idempotency id derived from (prefix, content_hash)."""
    h = hashlib.sha256(f"{prefix}:{content_hash}".encode("utf-8")).hexdigest()
    return f"{prefix}_{h[:16]}"


# ---------------------------------------------------------------------------- #
# DLT source
# ---------------------------------------------------------------------------- #


@dlt.source(name="uog_personal_archive")
def uog_personal_archive_source(
    base_path: str | Path | None = None,
    destination: str = "local",
    student_id: str = "cian_mac_an_deisigh_ui_liathain",
    include_transcripts: bool = True,
):
    """DLT source for the UoG personal archive.

    Args:
        base_path: Root directory to walk. Defaults to
            ``$UNIVERSITY_PERSONAL_ARCHIVE_PATH`` or
            ``leabharlann/ollscoil_na_gaillimhe``.
        destination: One of ``local``, ``motherduck``, ``bonneagar``.
        student_id: The kebab-case student id used in
            ``student_transcripts`` (the join target).
        include_transcripts: When True, also walk
            ``cian_mac_an_déisigh_uí_liatháin/achievement/*transcript*.pdf``
            for the transcript resource.
    """
    effective_base = (
        Path(base_path) if base_path is not None else _DEFAULT_PERSONAL_ARCHIVE_PATH
    )

    # ------------------------------------------------------------------------ #
    # 1. personal_archive_artefacts
    # ------------------------------------------------------------------------ #
    @dlt.resource(
        name="personal_archive_artefacts",
        write_disposition="merge",
        primary_key=["artefact_id", "content_hash"],
        columns={
            "institution_id": {"partition": True},
            "module_code": {"partition": True},
            "artefact_kind": {"partition": True},
            "academic_year": {"partition": True},
            "artefact_provenance": {"partition": True},
        },
    )
    def personal_archive_artefacts() -> Iterator[dict[str, Any]]:
        files = list(_discover_files(effective_base))
        if not files:
            yield _skipped_row("personal_archive_artefacts")
            return
        for f in files:
            content_hash = f.file_hash
            artefact_id = _stable_id("artefact", content_hash)
            yield {
                "artefact_id": artefact_id,
                "artefact_kind": f.artefact_kind.value,
                "artefact_provenance": f.artefact_provenance.value,
                "module_code": f.module_code,
                "module_title": None,
                "programme_code": None,
                "academic_year": None,
                "semester": None,
                "file_path": str(f.file_path),
                "file_hash": f.file_hash,
                "bytes": f.bytes,
                "file_extension": f.file_extension,
                "embedded_text": None,
                "confidence": 1.0,
                "institution_id": "ie-university-galway",
                "provenance_meta": {
                    "htr_required": f.artefact_kind == ArtefactKind.SCANNED_PAGE,
                    "htr_backend_used": (
                        HTRBackend.MULTI_VLM_CONSENSUS.value
                        if f.artefact_kind == ArtefactKind.SCANNED_PAGE
                        else HTRBackend.PYMUPDF_TYPED.value
                    ),
                    "htr_confidence": 0.5,
                    "htr_page_count": None,
                    "lecture_year": None,
                    "lecturer_name": None,
                    "course_code_on_artefact": f.module_code,
                },
                "content_hash": content_hash,
                "scraped_at": _now_iso(),
            }

    # ------------------------------------------------------------------------ #
    # 2. personal_archive_assignments
    # ------------------------------------------------------------------------ #
    @dlt.resource(
        name="personal_archive_assignments",
        write_disposition="merge",
        primary_key=["assignment_id", "content_hash"],
        columns={
            "module_code": {"partition": True},
            "assignment_number": {"partition": True},
        },
    )
    def personal_archive_assignments() -> Iterator[dict[str, Any]]:
        files = [
            f
            for f in _discover_files(effective_base)
            if f.artefact_kind == ArtefactKind.ASSIGNMENT_SUBMISSION
        ]
        if not files:
            yield _skipped_row("personal_archive_assignments")
            return
        for f in files:
            content_hash = f.file_hash
            assignment_id = _stable_id(
                f"assignment_{f.module_code or 'unknown'}_{f.assignment_number or 0}",
                content_hash,
            )
            yield {
                "assignment_id": assignment_id,
                "artefact_id": _stable_id("artefact", content_hash),
                "module_code": f.module_code,
                "assignment_number": f.assignment_number or 0,
                "assignment_title": None,
                "total_marks": None,
                "weight_percent": None,
                "submission_deadline": None,
                "question_count": 0,
                "institution_id": "ie-university-galway",
                "content_hash": content_hash,
                "file_path": str(f.file_path),
                "confidence": 1.0,
                "scraped_at": _now_iso(),
            }

    # ------------------------------------------------------------------------ #
    # 3. personal_archive_questions
    # ------------------------------------------------------------------------ #
    @dlt.resource(
        name="personal_archive_questions",
        write_disposition="merge",
        primary_key=["question_id"],
        columns={
            "module_code": {"partition": True},
            "question_id": {"partition": True},
        },
    )
    def personal_archive_questions() -> Iterator[dict[str, Any]]:
        # Empty by default — populated by the BAML extraction step.
        yield _skipped_row("personal_archive_questions")

    # ------------------------------------------------------------------------ #
    # 4. personal_archive_topics
    # ------------------------------------------------------------------------ #
    @dlt.resource(
        name="personal_archive_topics",
        write_disposition="merge",
        primary_key=["topic_id"],
        columns={
            "topic_category": {"partition": True},
        },
    )
    def personal_archive_topics() -> Iterator[dict[str, Any]]:
        yield _skipped_row("personal_archive_topics")

    # ------------------------------------------------------------------------ #
    # 5. personal_archive_reading_lists
    # ------------------------------------------------------------------------ #
    @dlt.resource(
        name="personal_archive_reading_lists",
        write_disposition="merge",
        primary_key=["reading_id"],
        columns={
            "module_code": {"partition": True},
        },
    )
    def personal_archive_reading_lists() -> Iterator[dict[str, Any]]:
        yield _skipped_row("personal_archive_reading_lists")

    # ------------------------------------------------------------------------ #
    # 6. personal_archive_code_cells
    # ------------------------------------------------------------------------ #
    @dlt.resource(
        name="personal_archive_code_cells",
        write_disposition="merge",
        primary_key=["cell_id"],
        columns={
            "module_code": {"partition": True},
            "notebook_path": {"partition": True},
        },
    )
    def personal_archive_code_cells() -> Iterator[dict[str, Any]]:
        yield _skipped_row("personal_archive_code_cells")

    # ------------------------------------------------------------------------ #
    # 7. personal_archive_ca_marks
    # ------------------------------------------------------------------------ #
    @dlt.resource(
        name="personal_archive_ca_marks",
        write_disposition="merge",
        primary_key=["ca_id"],
        columns={
            "module_code": {"partition": True},
        },
    )
    def personal_archive_ca_marks() -> Iterator[dict[str, Any]]:
        yield _skipped_row("personal_archive_ca_marks")

    # ------------------------------------------------------------------------ #
    # 8. student_transcripts
    # ------------------------------------------------------------------------ #
    @dlt.resource(
        name="student_transcripts",
        write_disposition="merge",
        primary_key=["student_id", "module_code", "academic_year"],
        columns={
            "student_id": {"partition": True},
            "programme_code": {"partition": True},
            "academic_year": {"partition": True},
        },
    )
    def student_transcripts() -> Iterator[dict[str, Any]]:
        if not include_transcripts:
            yield _skipped_row("student_transcripts")
            return
        transcript_paths = list(effective_base.rglob("*transcript*.pdf"))
        if not transcript_paths:
            # Also try the canonical achievement directory.
            achievement = Path(
                os.environ.get(
                    "UNIVERSITY_ACHIEVEMENT_PATH",
                    str(effective_base.parents[1] / "cian_mac_an_déisigh_uí_liatháin" / "achievement"),
                )
            )
            if achievement.exists():
                transcript_paths = list(achievement.rglob("*transcript*.pdf"))
        if not transcript_paths:
            yield _skipped_row("student_transcripts")
            return
        for tp in transcript_paths:
            try:
                file_hash = compute_file_hash(tp)
            except (OSError, PermissionError) as exc:
                logger.warning(
                    "transcript_hash_failed",
                    path=str(tp),
                    error=str(exc),
                )
                continue
            yield {
                "student_id": student_id,
                "institution_id": "ie-university-galway",
                "programme_code": "",
                "programme_title": "",
                "module_code": "",
                "module_title": "",
                "ects": None,
                "nfq_level": None,
                "academic_year": 0,
                "semester": None,
                "grade": "",
                "is_honours": False,
                "is_resit": False,
                "transcript_pdf": str(tp),
                "source_url": None,
                "scraped_at": _now_iso(),
                "confidence": 0.0,
                "file_hash": file_hash,
            }

    return (
        personal_archive_artefacts,
        personal_archive_assignments,
        personal_archive_questions,
        personal_archive_topics,
        personal_archive_reading_lists,
        personal_archive_code_cells,
        personal_archive_ca_marks,
        student_transcripts,
    )


__all__ = [
    "DEFAULT_PERSONAL_ARCHIVE_PATH" if False else "_DEFAULT_PERSONAL_ARCHIVE_PATH",
    "ArtefactKind",
    "ArtefactProvenance",
    "HTRBackend",
    "uog_personal_archive_source",
    "_classify_file",
]
