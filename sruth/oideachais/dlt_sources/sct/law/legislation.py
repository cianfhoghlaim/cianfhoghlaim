"""
oideachais.dlt_sources.sct.law.legislation — Scottish legislation.
Phase 7 of the openspec change.
"""
from __future__ import annotations

import dlt

from dlt_sources.law._legislation_helper import _crawl_legislation


@dlt.source(name="sct_legislation")
def sct_legislation_source(max_pages: int = 50):
    @dlt.resource(
        name="acts",
        write_disposition="merge",
        primary_key=["url"],
    )
    def acts():
        yield from _crawl_legislation(
            jurisdiction_code="sct",
            include_paths=["/asp/*", "/ssi/*", "/sdsi/*"],
            max_pages=max_pages,
        )

    return acts
