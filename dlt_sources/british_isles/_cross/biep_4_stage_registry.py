"""4-stage DLT source registry — extends the canonical BIEP DLT pipeline
to all 60 subjects across 4 stages (LC + JC + GCSE + A-Level).

Per the 2026-08-13-web-monorepo-consolidation-and-agent-integration-v1
change (Phase 5 - extend DLT sources to all 60 subjects).

This module is the canonical registry that:
1. Maps each (stage, subject) pair to the canonical BAML extraction
   function (consumed from the 4 canonical BAML files)
2. Maps each (stage, subject) pair to the canonical CocoIndex embedding
   flow (consumed from the existing Ireland LC factory + the equivalent
   England factory)
3. Maps each (stage, subject) pair to the canonical PDF directory
4. Yields the canonical DLT resource rows for the BIEP DuckLake table

The 4 canonical BAML files (added in Phase 4):
- baml_src/british_isles/ireland/education/lc_extraction/curriculum_syllabus.baml
- baml_src/british_isles/ireland/education/jc_extraction/canonical_jc_per_subject.baml
- baml_src/british_isles/england/education/gcse_extraction/canonical_gcse_per_subject.baml
- baml_src/british_isles/england/education/a_level_extraction/canonical_a_level_per_subject.baml
"""

from __future__ import annotations

import hashlib
import os
from collections.abc import Iterator
from pathlib import Path
from typing import Any

import dlt


# ============================================================================
# The 60-subject per-stage coverage matrix
# ============================================================================

# 14 LC subjects (Ireland Leaving Certificate)
LC_SUBJECTS: tuple[str, ...] = (
    "mathematics", "applied_mathematics", "chemistry", "physics",
    "biology", "geography", "gaeilge", "english",
    "french", "history", "business", "accounting",
    "art", "music", "computer_science",
)

# 8 JC subjects (Ireland Junior Cycle — the 8 priority)
JC_SUBJECTS: tuple[str, ...] = (
    "mathematics", "english", "gaeilge", "science",
    "history", "geography", "french", "business",
)

# 9 GCSE subjects (England — the 9 priority)
GCSE_SUBJECTS: tuple[str, ...] = (
    "mathematics", "english_language", "english_literature",
    "biology", "chemistry", "physics", "computer_science",
    "history", "geography",
)

# 15 A-Level subjects (England — the 15 priority)
A_LEVEL_SUBJECTS: tuple[str, ...] = (
    "mathematics", "further_mathematics", "english_literature",
    "english_language", "biology", "chemistry", "physics",
    "psychology", "history", "geography", "economics", "business",
    "history_of_art", "politics", "sociology",
)

# 3 GCSE / 3 A-Level boards (per official UK awarding bodies)
BOARDS: tuple[str, ...] = ("aqa", "ocr", "edexcel")

# Total subjects across the 4 stages + 3 boards
# 14 LC + 8 JC + 9 GCSE × 3 boards + 15 A-Level × 3 boards = 14 + 8 + 27 + 45 = 94
TOTAL_SUBJECT_NAMES: int = 14 + 8 + 9 + 15
TOTAL_DLT_FLOWS: int = 14 + 8 + 27 + 45  # 94 DLT sources total


# ============================================================================
# PDF source directories (the canonical paths)
// ============================================================================

PDF_ROOT = Path("leaving_certificate")  # Ireland LC
JUNIOR_CYCLE_PDF_ROOT = Path("junior_cycle")  # Ireland JC — to be created
ENGLAND_GCSE_PDF_ROOT = Path(
    os.getenv("BIEP_GCSE_PDF_ROOT", "stedding/site_scrape_samples/england/gcse")
)
ENGLAND_A_LEVEL_PDF_ROOT = Path(
    os.getenv("BIEP_A_LEVEL_PDF_ROOT", "stedding/site_scrape_samples/england/a_level")
)

# JC PDF directory (per the 2026-08-13-web-monorepo-consolidation-and-agent-integration-v1 change)
JUNIOR_CYCLE_PDF_ROOT = Path(
    os.getenv("BIEP_JC_PDF_ROOT", "junior_cycle")
)


# ============================================================================
# The canonical BIEP subject → BAML extraction map
// ============================================================================

# Each subject maps to the canonical BAML extraction function
# (the schema-driven codegen pipeline in Phase 7 emits these mappings)
BIEP_BAML_FUNCTIONS: dict[str, dict[str, str]] = {
    "lc": {
        subject: f"ExtractCurriculumSyllabus(text, subject='{subject}')"
        for subject in LC_SUBJECTS
    },
    "jc": {
        subject: f"ExtractJCCurriculumSyllabus(pdf_text, subject=JuniorCycleSubjectSlug.{subject.upper()}, language=JuniorCycleLanguage.EN)"
        for subject in JC_SUBJECTS
    },
    "gcse": {
        subject: f"ExtractGCSECurriculumSyllabus(pdf_text, subject=GCSEPrioritySubjectSlug.{subject.upper()}, exam_board=GCSEExamBoard.AQA)"
        for subject in GCSE_SUBJECTS
    },
    "a_level": {
        subject: f"ExtractALevelCurriculumSyllabus(pdf_text, subject=ALevelPrioritySubjectSlug.{subject.upper()}, exam_board=ALevelExamBoard.AQA)"
        for subject in A_LEVEL_SUBJECTS
    },
}


# ============================================================================
# The DLT resource generator — emits per-subject canonical rows
// ============================================================================

@dlt.resource(
    table_name="biep_subject_extraction_runs",
    write_disposition="merge",
    primary_key=["stage", "subject", "pdf_sha256"],
)
def biep_subject_extraction_runs(
    stage: str = dlt.config.value,
    subject: str = dlt.config.value,
    pdf_root: str = dlt.config.value,
) -> Iterator[dict[str, Any]]:
    """Yield the canonical per-PDF extraction runs for the BIEP pipeline.

    The 4-path OCR/VLM ensemble + RAGAS consensus produces the canonical
    row. Each row records:
    - stage: "lc" | "jc" | "gcse" | "a_level"
    - subject: the subject slug
    - pdf_path: the PDF path
    - pdf_sha256: the PDF hash (deterministic)
    - pdf_size_bytes: the PDF size
    - language: "en" | "ga" | mixed
    - baml_function: the canonical BAML extraction function (per the 4-stage BAML files)
    - status: "pending" | "extracted" | "ragas_consensus"
    - extracted_at: ISO 8601 datetime
    - ragas_consensus_score: 0.0-1.0

    Yields:
        Iterator[dict[str, Any]]: one dict per PDF
    """
    pdf_root_path = Path(pdf_root)
    if not pdf_root_path.exists():
        return

    for pdf_path in sorted(pdf_root_path.rglob("*.pdf")):
        rel_path = pdf_path.relative_to(Path("."))
        size_bytes = pdf_path.stat().st_size
        sha256 = hashlib.sha256()
        with open(pdf_path, "rb") as f:
            for chunk in iter(lambda: f.read(8192), b""):
                sha256.update(chunk)

        # Detect language from path (e.g. "en" vs "ga" subdirectory)
        language = "en"
        if "ga" in str(rel_path).lower():
            language = "ga"

        yield {
            "stage": stage,
            "subject": subject,
            "pdf_path": str(rel_path),
            "pdf_sha256": sha256.hexdigest(),
            "pdf_size_bytes": size_bytes,
            "language": language,
            "baml_function": BIEP_BAML_FUNCTIONS.get(stage, {}).get(subject, ""),
            "status": "pending",
            "extracted_at": None,
            "ragas_consensus_score": None,
        }


# ============================================================================
# The 4 DLT sources (one per stage)
// ============================================================================

@dlt.resource(
    table_name="ireland_lc_extractions",
    write_disposition="merge",
    primary_key=["subject", "pdf_sha256"],
)
def ireland_lc_extraction_summaries(
    pdf_root: str = str(PDF_ROOT),
) -> Iterator[dict[str, Any]]:
    """Yield the Ireland LC per-subject extraction summaries."""
    for subject in LC_SUBJECTS:
        yield from biep_subject_extraction_runs(
            stage="lc", subject=subject, pdf_root=pdf_root
        )


@dlt.resource(
    table_name="ireland_jc_extractions",
    write_disposition="merge",
    primary_key=["subject", "pdf_sha256"],
)
def ireland_jc_extraction_summaries(
    pdf_root: str = str(JUNIOR_CYCLE_PDF_ROOT),
) -> Iterator[dict[str, Any]]:
    """Yield the Ireland JC per-subject extraction summaries."""
    for subject in JC_SUBJECTS:
        yield from biep_subject_extraction_runs(
            stage="jc", subject=subject, pdf_root=pdf_root
        )


@dlt.resource(
    table_name="england_gcse_extractions",
    write_disposition="merge",
    primary_key=["subject", "board", "pdf_sha256"],
)
def england_gcse_extraction_summaries(
    pdf_root: str = str(ENGLAND_GCSE_PDF_ROOT),
) -> Iterator[dict[str, Any]]:
    """Yield the England GCSE per-subject × per-board extraction summaries."""
    for subject in GCSE_SUBJECTS:
        for board in BOARDS:
            yield from biep_subject_extraction_runs(
                stage="gcse", subject=f"{subject}_{board}",
                pdf_root=f"{pdf_root}/{board}",
            )


@dlt.resource(
    table_name="england_a_level_extractions",
    write_disposition="merge",
    primary_key=["subject", "board", "pdf_sha256"],
)
def england_a_level_extraction_summaries(
    pdf_root: str = str(ENGLAND_A_LEVEL_PDF_ROOT),
) -> Iterator[dict[str, Any]]:
    """Yield the England A-Level per-subject × per-board extraction summaries."""
    for subject in A_LEVEL_SUBJECTS:
        for board in BOARDS:
            yield from biep_subject_extraction_runs(
                stage="a_level", subject=f"{subject}_{board}",
                pdf_root=f"{pdf_root}/{board}",
            )


# ============================================================================
# The summary manifest (the canonical artifact that the codegen consumes)
// ============================================================================

def get_biep_stage_summary() -> dict[str, Any]:
    """Return the canonical BIEP 4-stage summary manifest.

    Returns:
        Dict with the 4-stage coverage matrix.
    """
    return {
        "lc": {
            "stage": "lc",
            "subjects": list(LC_SUBJECTS),
            "subject_count": len(LC_SUBJECTS),
            "baml_source": "baml_src/british_isles/ireland/education/lc_extraction/curriculum_syllabus.baml",
            "pdf_root": str(PDF_ROOT),
        },
        "jc": {
            "stage": "jc",
            "subjects": list(JC_SUBJECTS),
            "subject_count": len(JC_SUBJECTS),
            "baml_source": "baml_src/british_isles/ireland/education/jc_extraction/canonical_jc_per_subject.baml",
            "pdf_root": str(JUNIOR_CYCLE_PDF_ROOT),
        },
        "gcse": {
            "stage": "gcse",
            "subjects": list(GCSE_SUBJECTS),
            "subject_count": len(GCSE_SUBJECTS),
            "boards": list(BOARDS),
            "board_count": len(BOARDS),
            "per_subject_per_board_count": len(GCSE_SUBJECTS) * len(BOARDS),
            "baml_source": "baml_src/british_isles/england/education/gcse_extraction/canonical_gcse_per_subject.baml",
            "pdf_root": str(ENGLAND_GCSE_PDF_ROOT),
        },
        "a_level": {
            "stage": "a_level",
            "subjects": list(A_LEVEL_SUBJECTS),
            "subject_count": len(A_LEVEL_SUBJECTS),
            "boards": list(BOARDS),
            "board_count": len(BOARDS),
            "per_subject_per_board_count": len(A_LEVEL_SUBJECTS) * len(BOARDS),
            "baml_source": "baml_src/british_isles/england/education/a_level_extraction/canonical_a_level_per_subject.baml",
            "pdf_root": str(ENGLAND_A_LEVEL_PDF_ROOT),
        },
        "total_subjects": len(LC_SUBJECTS) + len(JC_SUBJECTS) + len(GCSE_SUBJECTS) + len(A_LEVEL_SUBJECTS),
        "total_dlt_flows": 14 + 8 + (9 * 3) + (15 * 3),
    }
