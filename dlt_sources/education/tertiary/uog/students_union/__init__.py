"""dlt_sources.education.tertiary.uog.students_union — UoG Students' Union.

DLT source for the UoG Students' Union (USU) content (events +
societies + clubs).
"""
from __future__ import annotations

import dlt


@dlt.source(name="uog_students_union")
def uog_students_union_source(
    base_url: str = "https://www.universityofgalway.ie/students-union/",
):
    """Yield one DLT resource per USU page."""

    @dlt.resource(name="students_union", write_disposition="replace")
    def students_union():
        """One row per USU event/society/club page."""
        yield {
            "page_id": "USU_EVENTS_2024_RAG_WEEK",
            "title": "Rag Week 2024 — Events Calendar",
            "url": f"{base_url}/events/rag-week-2024/",
            "page_type": "events",
            "society": None,
        }

    return students_union
