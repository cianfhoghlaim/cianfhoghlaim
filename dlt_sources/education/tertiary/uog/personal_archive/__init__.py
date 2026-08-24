"""dlt_sources.education.tertiary.uog.personal_archive — UoG personal archive.

DLT source for the UoG student's personal archive (assignments +
notes + transcripts). The `PipelineFactoryComponent` declares this as
a `pipeline_kind: personal_archive` pipeline.

This is a placeholder — the actual implementation will land in
Wave 2 follow-up PRs (the legacy flat files `uog_personal_archive.py`
+ `uog_personal_archive_figures.py` at `orchestration/defs/` are the
first targets for content migration).
"""
from __future__ import annotations

import dlt


@dlt.source(name="uog_personal_archive")
def uog_personal_archive_source(
    base_path: str = "stedding/ingest_queue/education/tertiary/uog/personal_archive",
):
    """Yield one DLT resource per personal archive file."""

    @dlt.resource(name="personal_archive", write_disposition="replace")
    def personal_archive():
        """One row per personal archive file (PDF, docx, md, etc.)."""
        # TODO(wave-2-followup): implement actual archive scanner
        yield {
            "file_id": "PHYS101_ASSIGNMENT_01",
            "title": "Physics I — Assignment 1",
            "file_path": f"{base_path}/phys101_assignment_01.pdf",
            "course_code": "PHYS101",
            "file_type": "pdf",
            "submitted_at": "2024-10-15",
        }

    return personal_archive
