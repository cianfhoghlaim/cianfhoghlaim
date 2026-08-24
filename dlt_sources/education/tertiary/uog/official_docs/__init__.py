"""dlt_sources.education.tertiary.uog.official_docs — UoG official docs.

DLT source for the University of Galway's official documentation
(module pages + faculty pages + research outputs). The
`PipelineFactoryComponent` declares this as a
`pipeline_kind: official_docs` pipeline.
"""
from __future__ import annotations

import dlt


@dlt.source(name="uog_official_docs")
def uog_official_docs_source(
    base_url: str = "https://www.universityofgalway.ie/",
):
    """Yield one DLT resource per official documentation page."""

    @dlt.resource(name="official_docs", write_disposition="replace")
    def official_docs():
        """One row per official documentation page."""
        yield {
            "page_id": "PHYS101_MODULE",
            "title": "Physics I — Module Description",
            "url": f"{base_url}/science/physics/undergraduate/physics-i/",
            "department": "School of Physics",
            "course_code": "PHYS101",
        }

    return official_docs
