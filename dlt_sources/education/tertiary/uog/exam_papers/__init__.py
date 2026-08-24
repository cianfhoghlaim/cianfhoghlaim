"""dlt_sources.education.tertiary.uog.exam_papers — University of Galway exam papers.

DLT source for the UoG exam paper PDFs (VLM-extracted). The
`PipelineFactoryComponent` in
`orchestration/pipelines/education/tertiary/uog/exam_papers/defs.yaml`
declares this as a `pipeline_kind: exam_papers` pipeline.

Each exam paper is downloaded from the UoG exams office
(`https://www.universityofgalway.ie/exams/`), then VLM-extracted via
cognee (per the master plan: "UoG exam papers VLM extraction").

This is a placeholder module — the actual implementation will land in
Wave 2 follow-up PRs.
"""
from __future__ import annotations

import dlt


@dlt.source(name="uog_exam_papers")
def uog_exam_papers_source(
    base_url: str = "https://www.universityofgalway.ie/exams/",
    use_local_scrapes: bool = False,
):
    """Yield one DLT resource per UoG exam paper."""
    if use_local_scrapes:
        base = "stedding/ingest_queue/education/tertiary/uog/exam_papers"
    else:
        base = base_url

    @dlt.resource(name="exam_papers", write_disposition="replace")
    def exam_papers():
        """One row per UoG exam paper PDF."""
        # TODO(wave-2-followup): implement actual exam paper fetcher
        yield {
            "paper_id": "PHYS101_2024_S1",
            "title": "Physics I — Semester 1, 2024",
            "url": f"{base}/phys101_2024_s1.pdf",
            "course_code": "PHYS101",
            "year": 2024,
            "semester": 1,
            "language": "en",
        }

    return exam_papers
