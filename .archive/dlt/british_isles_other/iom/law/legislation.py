"""oideachais.dlt_sources.iom.law.legislation — Isle of Man Statute Books.

Source: `https://www.legislation.gov.im` (Isle of Man Government
legislation portal, hosted on legislation.gov.uk infrastructure).

Per
https://github.com/cianfhoghlaim/kings_college_galway/issues/19
(closed 2026-06-15) the lateralise change wired this as one of the
6 crown-dependencies (IOM/JEY/GGY) medicine + law DLT sources.
"""
from __future__ import annotations

from collections.abc import Iterator
from datetime import UTC, datetime
from typing import Any

import dlt
import structlog

from ....ireland.curriculum_source import _crawl_source  # type: ignore[import-not-found]

logger = structlog.get_logger(__name__)

IOM_LEGISLATION_URLS = {
    "acts": "https://www.legislation.gov.im/cms/legislation/acts-of-tynwald/",
    "statutory_documents": "https://www.legislation.gov.im/cms/legislation/statutory-documents/",
    "regulations": "https://www.legislation.gov.im/cms/legislation/regulations/",
    "bills": "https://www.legislation.gov.im/cms/legislation/bills/",
}


def _crawl_iom_legislation(max_pages: int = 50) -> Iterator[dict[str, Any]]:
    """Crawl the Isle of Man legislation portal."""
    for url_key, url in IOM_LEGISLATION_URLS.items():
        for page in _crawl_source(
            source_name=f"iom.legislation.{url_key}",
            base_url=url,
            include_paths=[
                "/cms/legislation/acts-of-tynwald/*",
                "/cms/legislation/statutory-documents/*",
                "/cms/legislation/regulations/*",
                "/cms/legislation/bills/*",
            ],
            max_pages=max_pages,
            max_depth=2,
        ):
            page["nation"] = "iom"
            page["domain"] = "law"
            page["entity"] = "iom_legislation"
            page["jurisdiction_path"] = url_key
            yield page


@dlt.source(name="iom_legislation")
def iom_legislation_source(max_pages: int = 50):
    """DLT source for Isle of Man legislation."""

    @dlt.resource(
        name="acts",
        write_disposition="merge",
        primary_key=["url"],
    )
    def acts():
        for page in _crawl_iom_legislation(max_pages=max_pages):
            page["fetched_at"] = datetime.now(UTC).isoformat()
            page["status"] = "success"
            yield page

    return acts
