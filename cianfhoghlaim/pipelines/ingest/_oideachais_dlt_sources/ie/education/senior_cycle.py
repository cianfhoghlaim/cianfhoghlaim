"""
Senior Cycle DLT source — extends the existing ireland/senior_cycle.py with
the lazy_extract_exam_paper resource that fires baml.LazyExtractExamPaper
on-demand from the SPA.
"""
from __future__ import annotations

import hashlib
from pathlib import Path

import dlt

# Reuse the existing senior_cycle_subjects resource from the existing
# ireland/senior_cycle.py if present. Otherwise define a minimal stub.
try:
    from .senior_cycle_existing import senior_cycle_subjects  # type: ignore
except ImportError:
    @dlt.resource(name="senior_cycle_subjects", write_disposition="merge", primary_key=["slug", "year"])
    def senior_cycle_subjects():
        """Stub: real subjects come from subjects/lc_subjects.json + baml.ExtractSubjectRubric."""
        for slug in ["mathematics", "irish", "english", "biology", "french", "history", "business",
                     "construction_studies", "german", "chemistry", "physics", "applied_mathematics"]:
            yield {
                "slug": slug,
                "subject_code": slug.upper()[:2],
                "year": 2025,
                "source": "subjects/lc_subjects.json",
            }


@dlt.resource(name="lazy_extract_exam_paper", write_disposition="merge", primary_key=["subject", "year", "level", "paper_number"])
def lazy_extract_exam_paper(
    subject: str,
    year: int,
    level: str,
    paper_number: int,
    session_id: str,
    pdf_path: str,
    extraction_budget_remaining: int,
):
    """Lazy on-demand BAML extraction of a single Senior Cycle exam paper.

    Called by the SPA via oRPC when a user opens a past paper. Respects the
    per-session ExtractionBudget (5 papers/day/session by default).

    The real implementation invokes:
        b.LazyExtractExamPaper(text, subject, year, level, paper_number)
    via the baml_client.sync_client. The BAML output is upserted into
    LanceDB exam_paper_extractions for memoisation.
    """
    if extraction_budget_remaining <= 0:
        yield {
            "subject": subject,
            "year": year,
            "level": level,
            "paper_number": paper_number,
            "status": "budget_exceeded",
            "message": "Come back tomorrow — the daily extraction budget is 5 papers/session.",
        }
        return

    text = Path(pdf_path).read_text(encoding="utf-8", errors="ignore")
    fingerprint = hashlib.sha256(text.encode("utf-8")).hexdigest()[:16]

    yield {
        "subject": subject,
        "year": year,
        "level": level,
        "paper_number": paper_number,
        "session_id": session_id,
        "status": "queued",
        "fingerprint": fingerprint,
        "baml_function": "LazyExtractExamPaper",
    }
    # The baml.LazyExtractExamPaper call + LanceDB write happens in
    # apps/api/src/routers/baml.ts (the oRPC procedure called by the SPA).


@dlt.source(name="senior_cycle_with_lazy_extract")
def senior_cycle_with_lazy_extract():
    """Senior Cycle DLT source — subjects + lazy exam paper extraction."""
    yield senior_cycle_subjects
    yield lazy_extract_exam_paper
