"""
oideachais.dlt_sources.en.law.legislation — UK legislation (England & Wales).
Phase 7 of the openspec change.
"""
from __future__ import annotations

import dlt
from cianfhoghlaim.dlt.law._legislation_helper import _crawl_legislation


@dlt.source(name="en_legislation")
def en_legislation_source(max_pages: int = 50):
    @dlt.resource(
        name="acts",
        write_disposition="merge",
        primary_key=["url"],
    )
    def acts():
        yield from _crawl_legislation(
            jurisdiction_code="en",
            include_paths=["/uksi/*", "/ukpga/*", "/ukla/*", "/uksro/*"],
            max_pages=max_pages,
        )

    return acts
