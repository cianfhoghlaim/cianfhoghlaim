"""Land a small, real BAML-extracted sample into the silver layer.

Per the local-lakehouse plan's Phase 7
(/Users/cianmacandeisigh/.claude/plans/after-recent-plans-and-enumerated-cosmos.md):
reuse the proven chemistry-pilot extraction pattern (MiniMax primary via
BAML, Qwen secondary cross-check) for subjects beyond chemistry, using the
generic ExtractCurriculumSyllabus(pdf_text, subject, language) ->
SyllabusDocument BAML function (baml_src/british_isles/ireland/education/
lc_extraction/curriculum_syllabus.baml) rather than chemistry's dedicated
ExtractChemSyllabus.

Deliberately scoped to 2 subjects x 1 language (geography EN, mathematics
EN) rather than exhaustively processing all 13 subjects x 2 languages —
each MiniMax extraction call is real, billed, and takes ~1-2 minutes (the
chemistry pilot's own EN syllabus call took 118s for 79 pages), so this
proves the generalized pattern works rather than burning a large amount
of time/cost re-running it for every subject in one session.

Reuses:
- dlt_sources.british_isles.ireland.education._pdf_text.extract_pdf_text
  (pymupdf-based, already used elsewhere in this repo)
- dlt_sources.filesystem.lc6_cross_check._load_baml (already handles the
  known baml_client/baml_client packaging bug via a fallback import)
- the same ExtractQwenCrossCheck baml_options={"client": ...} pattern the
  chemistry pilot proved

Run: mise exec -- .venv/bin/python3 scripts/load_lc_silver_sample.py
"""

from __future__ import annotations

import hashlib
from pathlib import Path
from typing import Any

import dlt
import structlog

from dlt_sources.british_isles.ireland.education._pdf_text import extract_pdf_text
from dlt_sources.common.destinations_cianfhoghlaim import get_dlt_destination
from dlt_sources.filesystem.lc6_cross_check import SECONDARY_CLIENT, _load_baml

logger = structlog.get_logger(__name__)

REPO_ROOT = Path(__file__).resolve().parents[1]

# (subject, language, pdf path relative to repo root)
SAMPLE_PDFS: tuple[tuple[str, str, str], ...] = (
    ("geography", "en", "leaving_certificate/geography/en/SCSEC17_Geography_syllabus_eng.pdf"),
    (
        "mathematics",
        "en",
        "leaving_certificate/mathematics/en/SCSEC25_Maths_syllabus_examination-2015_English.pdf",
    ),
)


def _document_to_row(subject: str, language: str, pdf_path: Path, doc: Any) -> dict[str, Any]:
    """Flatten a SyllabusDocument pydantic object into a silver row."""
    return {
        "id": hashlib.sha256(f"{subject}:{language}:{pdf_path.name}".encode()).hexdigest()[:16],
        "subject": subject,
        "language": language,
        "source_pdf": str(pdf_path.relative_to(REPO_ROOT)),
        "extracted_subject": doc.subject,
        "extracted_language": str(doc.language),
        "stage": str(doc.stage),
        "source_pages": doc.source_pages,
        "topic_count": len(doc.module_topics) if doc.module_topics else 0,
        "total_learning_outcomes": doc.total_learning_outcomes,
        "cross_curricular_count": len(doc.cross_curricular) if doc.cross_curricular else 0,
        "assessment_objectives_count": (
            len(doc.assessment_objectives) if doc.assessment_objectives else 0
        ),
        "extraction_client": "ExtractEn",
    }


def _extract_one(subject: str, language: str, pdf_path: Path) -> tuple[dict[str, Any], str]:
    """Run primary (MiniMax) + best-effort secondary (Qwen) extraction.

    Returns (row, status) — status is "primary_only" or
    "cross_checked" or "primary_failed".
    """
    b = _load_baml()
    if b is None:
        return {}, "baml_client_unavailable"

    text = extract_pdf_text(pdf_path)
    logger.info("silver_extract_start", subject=subject, language=language, chars=len(text))

    try:
        primary = b.ExtractCurriculumSyllabus(text, subject, language)
    except Exception as e:  # noqa: BLE001 — BAML error types are not stable API
        logger.error("silver_extract_primary_failed", subject=subject, error=str(e)[:300])
        return {}, "primary_failed"

    row = _document_to_row(subject, language, pdf_path, primary)
    status = "primary_only"

    # Best-effort Qwen secondary — expected to fail cleanly pending
    # DASHSCOPE_API_KEY hydration (documented, known constraint, never
    # fabricated). Never blocks the primary result from landing.
    try:
        secondary = b.ExtractCurriculumSyllabus(
            text, subject, language, baml_options={"client": SECONDARY_CLIENT}
        )
        row["secondary_topic_count"] = len(secondary.module_topics) if secondary.module_topics else 0
        row["secondary_total_learning_outcomes"] = secondary.total_learning_outcomes
        status = "cross_checked"
        logger.info("silver_extract_secondary_ok", subject=subject)
    except Exception as e:  # noqa: BLE001
        logger.warning("silver_extract_secondary_failed", subject=subject, error=str(e)[:200])

    row["status"] = status
    return row, status


def main() -> int:
    pipeline = dlt.pipeline(
        pipeline_name="lc_silver_sample",
        destination=get_dlt_destination(use_ducklake=True),
        dataset_name="cianfhoghlaim.silver.ireland_leaving_cert_extracted",
    )

    rows: list[dict[str, Any]] = []
    for subject, language, rel_path in SAMPLE_PDFS:
        pdf_path = REPO_ROOT / rel_path
        if not pdf_path.exists():
            logger.error("silver_pdf_missing", path=str(pdf_path))
            continue
        row, status = _extract_one(subject, language, pdf_path)
        print(f"{subject} ({language}): {status}")
        if row:
            rows.append(row)

    if not rows:
        print("No rows extracted — nothing to load.")
        return 1

    load_info = pipeline.run(
        rows,
        table_name="syllabus_extractions",
        write_disposition="merge",
        primary_key="id",
    )
    print(load_info)

    with pipeline.sql_client() as client:
        for row in client.execute_sql(
            "SELECT subject, language, status, topic_count, total_learning_outcomes "
            "FROM syllabus_extractions ORDER BY subject"
        ):
            print(row)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
