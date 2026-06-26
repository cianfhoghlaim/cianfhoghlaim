"""
oideachais.dlt_sources.ni.law.legislation — Northern Ireland legislation.

Source: `https://www.legislation.gov.uk/nisi` and `/nid`.
Phase 7 of the openspec change.
"""
from __future__ import annotations

import dlt

from dlt_sources.law._legislation_helper import _crawl_legislation


@dlt.source(name="ni_legislation")
def ni_legislation_source(max_pages: int = 50):
    @dlt.resource(
        name="acts",
        write_disposition="merge",
        primary_key=["url"],
    )
    def acts():
        yield from _crawl_legislation(
            jurisdiction_code="ni",
            include_paths=["/nisi/*", "/nid/*", "/nia/*"],
            max_pages=max_pages,
        )

    return acts
