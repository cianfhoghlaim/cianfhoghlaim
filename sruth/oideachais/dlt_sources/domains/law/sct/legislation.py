"""
oideachais.dlt_sources.domains.law.sct.legislation — Scottish legislation.
Phase 7 of the openspec change.
"""
from __future__ import annotations

import dlt

from .._legislation_helper import _crawl_legislation  # type: ignore[import-not-found]


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
