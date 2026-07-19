"""
DLT source for Téarma.ie (Irish Terminology Database) — live API search.

Searches the Téarma.ie REST API for terms matching a list of queries.
The companion bulk-export source lives at
`cianfhoghlaim.dlt.british_isles.ireland.culture.tearma`.

Usage:
    from dlt_sources.british_isles.ireland.culture.tearma_search import tearma_search_source

    pipeline = dlt.pipeline(
        pipeline_name="tearma_search",
        destination="duckdb",
    )
    pipeline.run(tearma_search_source(queries=["school", "scoil"]))

Split out of the legacy `dlt_sources/tearma.py` flat file in Phase 4
(oideachais-audit-phase-4-consolidate-legacy-dirs). Shared helpers +
module constants + `TerminologyLinker` live at
`cianfhoghlaim.dlt.british_isles.ireland.culture._tearma_helpers`.
"""
from __future__ import annotations
import dlt


from collections.abc import Iterator
from typing import Any

import dlt_sources
from dlt_sources.british_isles.ireland.culture._tearma_helpers import _search_tearma_api


@dlt.source(name="tearma_search")
def tearma_search_source(
    queries: list[str],
    domains: list[str] | None = None,
):
    """
    DLT source for searching Téarma API.

    Args:
        queries: List of search queries
        domains: Optional list of domains to filter

    Returns:
        DLT source with search results
    """

    @dlt.resource(
        name="tearma_search_results",
        write_disposition="append",
        primary_key=["term_id", "query"],
    )
    def tearma_search_results() -> Iterator[dict[str, Any]]:
        """Search results from Téarma API."""
        for query in queries:
            if domains:
                for domain in domains:
                    yield from _search_tearma_api(query, domain)
            else:
                yield from _search_tearma_api(query)

    return tearma_search_results


__all__ = ["tearma_search_source"]
