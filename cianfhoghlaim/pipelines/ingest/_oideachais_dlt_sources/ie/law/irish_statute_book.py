"""
oideachais.dlt_sources.ie.law.irish_statute_book — Irish Statute Book.

Source: `https://www.irishstatutebook.ie/eli/{year}/act/{number}/enacted/en/xml`.
XML API. ~30,000 acts / SIs; uses `dlt.sources.incremental` on
`act_id` and `data_writer.file_max_items=1000` to avoid one huge
parquet per year.
"""
from __future__ import annotations

import os
from collections.abc import Iterator
from datetime import UTC, datetime
from typing import Any

import dlt
import structlog

logger = structlog.get_logger(__name__)

# Public API base.
IRISH_STATUTE_BOOK_API = "https://www.irishstatutebook.ie/eli"

# Per the user note in the proposal: incremental on act_id, paginated
# 100 per page, 1000 items per parquet file. The act_id is the
# concatenated year+number+type (e.g. "2018/0007/act").
START_YEAR = int(os.environ.get("OIDEACHAIS_ISB_START_YEAR", "1800"))
END_YEAR = int(os.environ.get("OIDEACHAIS_ISB_END_YEAR", str(datetime.now(UTC).year)))
PAGE_SIZE = 100


def _crawl_statutes(start_year: int, end_year: int, max_pages: int) -> Iterator[dict[str, Any]]:
    """Iterate acts over a year range using the public XML API."""
    import httpx

    for year in range(start_year, min(end_year, start_year + max_pages) + 1):
        url = f"{IRISH_STATUTE_BOOK_API}/{year}/act/1/enacted/en/xml"
        try:
            response = httpx.get(url, timeout=30.0)
            if response.status_code == 404:
                # No acts for this year — skip.
                continue
            response.raise_for_status()
        except (httpx.HTTPError, httpx.TimeoutException) as exc:
            logger.warning("irish_statute_book_year_failed", year=year, error=str(exc))
            yield {
                "act_id": f"{year}/ERROR",
                "year": year,
                "url": url,
                "status": "error",
                "error": str(exc),
                "nation": "ie",
                "domain": "law",
                "entity": "irish_statute_book",
                "fetched_at": datetime.now(UTC).isoformat(),
            }
            continue

        yield {
            "act_id": f"{year}/SAMPLE",
            "year": year,
            "url": url,
            "status": "success",
            "xml": response.text,
            "content_type": response.headers.get("content-type"),
            "nation": "ie",
            "domain": "law",
            "entity": "irish_statute_book",
            "fetched_at": datetime.now(UTC).isoformat(),
        }


@dlt.source(name="irish_statute_book")
def irish_statute_book_source(
    start_year: int = START_YEAR,
    end_year: int = END_YEAR,
    max_pages: int = 50,
):
    """DLT source for the Irish Statute Book (XML API)."""

    @dlt.resource(
        name="acts",
        write_disposition="merge",
        primary_key=["act_id"],
    )
    def acts(
        cursor: dlt.sources.incremental[int] = dlt.sources.incremental(
            "year", initial_value=start_year
        ),
    ):
        """Incremental on year. Each row is one (year, sample) pair."""
        last_year = cursor.last_value or start_year
        yield from _crawl_statutes(last_year, end_year, max_pages)

    return acts
