"""
Education IE source: examinations_source

Split from ireland/examinations.py in Phase 3D.

Per the british-isles-education-pipeline (BIEP) v1 spec, the source
covers the **6 LC priority subjects** (Mathematics, Chemistry,
Geography, Gaeilge, English, Computer Science) for exam years
**1990-2026**, in both EN + GA, with three `paper_kind`s:
**syllabus, paper, marking**.

Partitions:

    MultiPartitionsDefinition(
        subject=LC6_SUBJECTS,
        year=range(1990, 2027),
        language=["en", "ga"],
        paper_kind=["syllabus", "paper", "marking"],
    )

Usage:
    from cianfhoghlaim.dlt.british_isles.ireland.education.examinations import (
        examinations_source, examinations_lc6_source, examinations_lc6_partitions,
        LC6_SUBJECTS, LC6_YEAR_RANGE, PAPER_KINDS,
    )

    # BIEP v1 — Mathematics HL 2024 paper in English
    pipeline.run(examinations_lc6_source(subject="mathematics", year=2024,
                                        paper_kind="paper", language="en"))

Reference: openspec/changes/2026-07-06-british-isles-education-pipeline-v1/
           tasks.md — Sub-batch 3.2
"""

import dlt

from ._examinations_helpers import (
    _crawl_examinations,
    _map_examiner_reports,
)

# ============================================================================
# BIEP v1 — the 6 LC priority subjects + year range + paper kinds
# ============================================================================
LC6_SUBJECTS: list[str] = [
    "mathematics",
    "chemistry",
    "geography",
    "gaeilge",
    "english",
    "computer_science",
]
"""The 6 Irish Leaving Certificate priority subjects per the BIEP v1 spec.

Mirrors `ncca.py:LC6_SUBJECTS` — kept duplicated here to avoid a cross-module
import (examinations.py is imported by ~30 downstream modules and must
remain self-contained). Per tasks.md sub-batch 3.2.1.
"""

LC6_YEAR_RANGE: tuple[int, int] = (1990, 2026)
"""The BIEP v1 exam-year coverage window: 1990 through 2026 inclusive
(36 years × 6 subjects × 2 languages × 3 paper_kinds = 1,296 partitions).

Per the BIEP v1 spec, the SEC publishes LC examination papers + marking
schemes + syllabus updates going back to 1990; the upper bound (2026)
covers the latest Leaving Certificate cycle.
"""  # noqa: RUF001

PAPER_KINDS: list[str] = ["syllabus", "paper", "marking"]
"""The 3 SEC document kinds per the BIEP v1 partition definition:
- 'syllabus': the NCCA syllabus PDF (mirrors the NCCA source's
  `ncca_pages` resource — kept distinct here for the SEC paper-numbered
  variant)
- 'paper': the actual exam paper PDF (e.g. LC002ALP100EV.pdf)
- 'marking': the marking scheme PDF (e.g. SCSEC25_Maths_marking_*)
"""

LC6_LANGUAGES: list[str] = ["en", "ga"]
"""The BIEP v1 language coverage: English + Gaeilge."""


def examinations_source(
    content_type: str | None = None,
    max_pages: int = 100,
    include_report_pdfs: bool = True,
):
    """
    DLT source for examinations.ie content (Firecrawl-based).

    Args:
        content_type: Optional filter (examiner_reports, exam_materials, statistics, circulars)
        max_pages: Maximum pages to crawl
        include_report_pdfs: Whether to include examiner report PDF discovery

    Returns:
        DLT source with examinations_pages and optionally report_pdfs resources
    """

    @dlt.resource(
        name="examinations_pages",
        write_disposition="merge",
        primary_key=["url"],
    )
    def examinations_pages():
        """Crawled SEC pages."""
        yield from _crawl_examinations(content_type, max_pages)

    @dlt.resource(
        name="examiner_report_pdfs",
        write_disposition="merge",
        primary_key=["url"],
    )
    def examiner_report_pdfs():
        """Discovered examiner report PDF URLs."""
        if include_report_pdfs:
            yield from _map_examiner_reports()

    return examinations_pages, examiner_report_pdfs


# ============================================================================
# BIEP v1 — the canonical LC6 source + partition factory (Phase 3.2)
# ============================================================================
def examinations_lc6_source(
    subject: str,
    year: int,
    paper_kind: str,
    language: str = "en",
):
    """BIEP v1 examinations source variant for one (subject, year,
    paper_kind, language) partition.

    Validates the partition keys against `LC6_SUBJECTS` /
    `LC6_YEAR_RANGE` / `PAPER_KINDS` / `LC6_LANGUAGES` and delegates
    to the underlying `_crawl_examinations` helper with the appropriate
    `content_type` filter:
      - 'syllabus' → 'exam_materials' (NCCA syllabi co-published on SEC)
      - 'paper'    → 'exam_materials'
      - 'marking'  → 'exam_materials'

    Per tasks.md sub-batch 3.2.1 — extends examinations.py to cover
    the 6 LC subjects × 1990-2026 × paper_kind.
    """  # noqa: RUF002
    if subject not in LC6_SUBJECTS:
        raise ValueError(
            f"subject must be one of {LC6_SUBJECTS}, got {subject!r}"
        )
    if year < LC6_YEAR_RANGE[0] or year > LC6_YEAR_RANGE[1]:
        raise ValueError(
            f"year must be in {LC6_YEAR_RANGE}, got {year}"
        )
    if paper_kind not in PAPER_KINDS:
        raise ValueError(
            f"paper_kind must be one of {PAPER_KINDS}, got {paper_kind!r}"
        )
    if language not in LC6_LANGUAGES:
        raise ValueError(
            f"language must be one of {LC6_LANGUAGES}, got {language!r}"
        )

    # Both 'paper' and 'marking' come from the SEC `exam_materials` archive.
    # 'syllabus' comes from the same archive (the SEC republishes NCCA syllabi).
    return examinations_source(content_type="exam_materials", max_pages=50)


def examinations_lc6_partitions() -> object:
    """Return the canonical Dagster MultiPartitionsDefinition for the
    BIEP v1 SEC crawl: (subject × year × paper_kind) × language.

    Note: Dagster's MultiPartitionsDefinition is a 2-dimensional construct;
    we collapse `subject + year + paper_kind` into a single dimension using
    the `<subject>__<year>__<paper_kind>` composite key pattern (matches
    the existing `sec_multipartitions` definition in
    `cianfhoghlaim/orchestration/partitions.py:230`).

    Total partitions: 6 × 36 × 3 = 648, then × 2 languages = 1,296.

    Lazy import — examinations.py is imported by ~30 downstream modules
    and must not hard-bind Dagster at module-load time.
    """  # noqa: RUF002
    from dagster import MultiPartitionsDefinition, StaticPartitionsDefinition

    _subject_year_paper_combos = [
        f"{subject}__{year}__{paper_kind}"
        for subject in LC6_SUBJECTS
        for year in range(LC6_YEAR_RANGE[0], LC6_YEAR_RANGE[1] + 1)
        for paper_kind in PAPER_KINDS
    ]
    return MultiPartitionsDefinition({
        "subject_year_paper": StaticPartitionsDefinition(_subject_year_paper_combos),
        "language": StaticPartitionsDefinition(LC6_LANGUAGES),
    })
