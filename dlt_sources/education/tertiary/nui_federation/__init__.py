"""dlt_sources.education.tertiary.nui_federation — NUI Federation.

DLT source for the National University of Ireland federation (UoG,
UCD, UCC, NUIM). Aggregates official docs across all 4 member
institutions.
"""
from __future__ import annotations

import dlt


@dlt.source(name="nui_federation")
def nui_federation_source():
    """Yield one DLT resource per NUI federation institution's official docs."""

    @dlt.resource(name="nui_federation", write_disposition="replace")
    def nui_docs():
        """One row per NUI federation institution's official doc."""
        for institution, url in [
            ("university_of_galway", "https://www.universityofgalway.ie/"),
            ("university_college_dublin", "https://www.ucd.ie/"),
            ("university_college_cork", "https://www.ucc.ie/"),
            ("maynooth_university", "https://www.maynoothuniversity.ie/"),
        ]:
            yield {
                "institution": institution,
                "url": url,
                "federation": "nui",
            }

    return nui_docs
