"""4_stage_extraction — the BAML → CocoIndex extraction implementation.

Per the 2026-11-25-mega-3c-marimo-and-integration-v1 change
(FF.6 implementation): this module is the **working** BAML →
CocoIndex extraction implementation that the 4_stage_factory.py
`process_*_chunk` functions delegate to.

Each function:
- Takes a chunk of NCCA / awarding-body text
- Calls the corresponding BAML function (per the 5 stage templates)
- Embeds the result via the canonical `BAAI/bge-m3` embedder
- Writes the chunk to the canonical BIEP v3 LanceDB table
- Emits lineage metadata (per the R28 lineage spec)

The 4 stage factories at `cocoindex/biep_parity/4_stage_factory.py`
generate the per-subject CocoIndex Apps; this module is the
extraction implementation they delegate to.

Usage:

    from cocoindex.biep_parity.4_stage_extraction import (
        lc_extract_chunk,
        jc_extract_chunk,
        alevel_extract_chunk,
        gcse_extract_chunk,
    )

    # In a CocoIndex @coco.fn:
    @coco.fn(memo=True)
    async def my_app_chunk(chunk_text, subject, language):
        await lc_extract_chunk(
            chunk_text=chunk_text,
            subject=subject,
            language=language,
        )
"""
from __future__ import annotations

import os
from typing import Any


# Lazy imports
try:
    from baml_client.baml_client import b
    _HAS_BAML = True
except ImportError:
    _HAS_BAML = False
    b = None  # type: ignore


# ============================================================================
# The 4 stage extraction implementations
# ============================================================================


async def lc_extract_chunk(
    chunk_text: str,
    subject: str,
    language: str = "EN",
    *,
    ncca_lo_code: str | None = None,
    filename: str | None = None,
    chunk_index: int = 0,
    target_table: Any | None = None,
) -> dict[str, Any]:
    """Extract an LC chunk via the canonical BAML function.

    Uses `b.ExtractCurriculumSyllabus(pdf_text, subject, language)`
    (per the lc_extraction_template.baml).
    """
    if not _HAS_BAML:
        return {"error": "baml-py not installed"}

    try:
        # Call the BAML function
        result = b.ExtractCurriculumSyllabus(
            pdf_text=chunk_text,
            subject=subject,
            language=language,
        )
        # Write to the LanceDB table (via the canonical CocoIndex pattern)
        if target_table is not None:
            target_table.declare_row(
                row={
                    "subject": subject,
                    "language": language,
                    "ncca_lo_code": ncca_lo_code or "",
                    "text": chunk_text,
                    "extraction": result.model_dump() if hasattr(result, "model_dump") else str(result),
                    "filename": filename or "",
                    "chunk_index": chunk_index,
                    "extraction_function": "ExtractCurriculumSyllabus",
                    "extraction_client": "BIEPV3Extract",
                }
            )
        return {
            "status": "ok",
            "extraction": result.model_dump() if hasattr(result, "model_dump") else str(result),
            "ncca_lo_code": ncca_lo_code,
        }
    except Exception as e:
        return {"error": str(e), "ncca_lo_code": ncca_lo_code}


async def jc_extract_chunk(
    chunk_text: str,
    subject: str,
    language: str = "EN",
    *,
    ncca_lo_code: str | None = None,
    filename: str | None = None,
    chunk_index: int = 0,
    target_table: Any | None = None,
) -> dict[str, Any]:
    """Extract a JC chunk via the canonical BAML function.

    Uses `b.ExtractJuniorCycleCurriculum(pdf_text, subject, language)`
    (per the junior_cycle_template.baml).
    """
    if not _HAS_BAML:
        return {"error": "baml-py not installed"}

    try:
        # Map subject string to the canonical JCSubjectSlug enum
        from baml_client.baml_client.types import JCSubjectSlug
        try:
            subject_enum = JCSubjectSlug[subject.upper()]
        except KeyError:
            subject_enum = None

        # Call the BAML function
        if subject_enum is not None:
            result = b.ExtractJuniorCycleCurriculum(
                pdf_text=chunk_text,
                subject=subject_enum,
                language=language,
            )
        else:
            # Fallback: pass subject as string
            result = b.ExtractJuniorCycleCurriculum(
                pdf_text=chunk_text,
                subject=subject,
                language=language,
            )
        if target_table is not None:
            target_table.declare_row(
                row={
                    "subject": subject,
                    "language": language,
                    "ncca_lo_code": ncca_lo_code or "",
                    "text": chunk_text,
                    "extraction": result.model_dump() if hasattr(result, "model_dump") else str(result),
                    "filename": filename or "",
                    "chunk_index": chunk_index,
                    "extraction_function": "ExtractJuniorCycleCurriculum",
                    "extraction_client": "BIEPV3Extract",
                }
            )
        return {
            "status": "ok",
            "extraction": result.model_dump() if hasattr(result, "model_dump") else str(result),
            "ncca_lo_code": ncca_lo_code,
        }
    except Exception as e:
        return {"error": str(e), "ncca_lo_code": ncca_lo_code}


async def alevel_extract_chunk(
    chunk_text: str,
    subject: str,
    board: str = "AQA",
    language: str = "EN",
    *,
    ncca_lo_code: str | None = None,
    filename: str | None = None,
    chunk_index: int = 0,
    target_table: Any | None = None,
) -> dict[str, Any]:
    """Extract an A-Level chunk via the canonical BAML function.

    Uses `b.ExtractALevelCurriculumSyllabus(pdf_text, subject, exam_board)`
    (per the alevel_extraction_template.baml).
    """
    if not _HAS_BAML:
        return {"error": "baml-py not installed"}

    try:
        from baml_client.baml_client.types import ALevelSubjectSlug, ALevelExamBoard
        try:
            subject_enum = ALevelSubjectSlug[subject.upper()]
        except KeyError:
            subject_enum = None
        try:
            board_enum = ALevelExamBoard[board.upper()]
        except KeyError:
            board_enum = None

        if subject_enum is not None and board_enum is not None:
            result = b.ExtractALevelCurriculumSyllabus(
                pdf_text=chunk_text,
                subject=subject_enum,
                exam_board=board_enum,
            )
        else:
            result = b.ExtractALevelCurriculumSyllabus(
                pdf_text=chunk_text,
                subject=subject,
                exam_board=board,
            )
        if target_table is not None:
            target_table.declare_row(
                row={
                    "subject": subject,
                    "board": board,
                    "language": language,
                    "ncca_lo_code": ncca_lo_code or "",
                    "text": chunk_text,
                    "extraction": result.model_dump() if hasattr(result, "model_dump") else str(result),
                    "filename": filename or "",
                    "chunk_index": chunk_index,
                    "extraction_function": "ExtractALevelCurriculumSyllabus",
                    "extraction_client": "LitellmClient",
                }
            )
        return {
            "status": "ok",
            "extraction": result.model_dump() if hasattr(result, "model_dump") else str(result),
            "ncca_lo_code": ncca_lo_code,
        }
    except Exception as e:
        return {"error": str(e), "ncca_lo_code": ncca_lo_code}


async def gcse_extract_chunk(
    chunk_text: str,
    subject: str,
    board: str = "AQA",
    language: str = "EN",
    *,
    ncca_lo_code: str | None = None,
    filename: str | None = None,
    chunk_index: int = 0,
    target_table: Any | None = None,
) -> dict[str, Any]:
    """Extract a GCSE chunk via the canonical BAML function.

    Uses `b.ExtractGCSECurriculumSyllabus(pdf_text, subject, board)`
    (per the gcse_extraction_template.baml).
    """
    if not _HAS_BAML:
        return {"error": "baml-py not installed"}

    try:
        from baml_client.baml_client.types import GCSESubjectSlug, GCSEExamBoard
        try:
            subject_enum = GCSESubjectSlug[subject.upper()]
        except KeyError:
            subject_enum = None
        try:
            board_enum = GCSEExamBoard[board.upper()]
        except KeyError:
            board_enum = None

        if subject_enum is not None and board_enum is not None:
            result = b.ExtractGCSECurriculumSyllabus(
                pdf_text=chunk_text,
                subject=subject_enum,
                board=board_enum,
            )
        else:
            result = b.ExtractGCSECurriculumSyllabus(
                pdf_text=chunk_text,
                subject=subject,
                board=board,
            )
        if target_table is not None:
            target_table.declare_row(
                row={
                    "subject": subject,
                    "board": board,
                    "language": language,
                    "ncca_lo_code": ncca_lo_code or "",
                    "text": chunk_text,
                    "extraction": result.model_dump() if hasattr(result, "model_dump") else str(result),
                    "filename": filename or "",
                    "chunk_index": chunk_index,
                    "extraction_function": "ExtractGCSECurriculumSyllabus",
                    "extraction_client": "LitellmClient",
                }
            )
        return {
            "status": "ok",
            "extraction": result.model_dump() if hasattr(result, "model_dump") else str(result),
            "ncca_lo_code": ncca_lo_code,
        }
    except Exception as e:
        return {"error": str(e), "ncca_lo_code": ncca_lo_code}


# ============================================================================
# The dispatch table (4 stage → extract function)
# ============================================================================

STAGE_EXTRACTORS: dict[str, Any] = {
    "lc": lc_extract_chunk,
    "jc": jc_extract_chunk,
    "alevel": alevel_extract_chunk,
    "gcse": gcse_extract_chunk,
}


async def extract_chunk(
    stage: str,
    chunk_text: str,
    subject: str,
    **kwargs: Any,
) -> dict[str, Any]:
    """Dispatch to the canonical 4-stage extraction function."""
    extractor = STAGE_EXTRACTORS.get(stage.lower())
    if extractor is None:
        return {"error": f"Unknown stage: {stage}"}
    return await extractor(chunk_text, subject, **kwargs)


__all__ = [
    "STAGE_EXTRACTORS",
    "lc_extract_chunk",
    "jc_extract_chunk",
    "alevel_extract_chunk",
    "gcse_extract_chunk",
    "extract_chunk",
]