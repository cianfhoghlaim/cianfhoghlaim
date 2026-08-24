"""dlt_sources.education.tertiary.british_isles — British Isles tertiary.

DLT source for the British Isles (UK + IE) tertiary education sector.
Aggregates official docs across all universities.
"""
from __future__ import annotations

import dlt


@dlt.source(name="british_isles_tertiary")
def british_isles_tertiary_source():
    """Yield one DLT resource per UK/IE university."""

    @dlt.resource(name="british_isles_tertiary", write_disposition="replace")
    def unis():
        """One row per British Isles university."""
        yield {
            "institution": "university_of_galway",
            "country": "ie",
            "url": "https://www.universityofgalway.ie/",
        }

    return unis
