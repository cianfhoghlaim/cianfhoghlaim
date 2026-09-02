"""
DLT source for Téarma.ie (Irish Terminology Database) — live API search.

Searches the Téarma.ie REST API for terms matching a list of queries.
The companion bulk-export source lives at
`dlt_sources.lexicographic.tearma`.

Usage:
    from dlt_sources.lexicographic.tearma_search import tearma_search_source

    pipeline = dlt.pipeline(
        pipeline_name="tearma_search",
        destination="duckdb",
    )
    pipeline.run(tearma_search_source(queries=["school", "scoil"]))

Split out of the legacy `dlt_sources/tearma.py` flat file in Phase 4
(oideachais-audit-phase-4-consolidate-legacy-dirs). Per the
**2026-08-24-wave-1-dlt-sources-domain-restructure-v1** openspec change,
this source moved from `dlt_sources/language/tearma_search.py` to
`dlt_sources/lexicographic/tearma_search.py` (master plan §3.2, §7.1).
Shared helpers + module constants + `TerminologyLinker` live at
`dlt_sources.lexicographic._tearma_helpers`.
"""
from __future__ import annotations
import dlt


from collections.abc import Iterator
from typing import Any

import dlt_sources
from ._tearma_helpers import _search_tearma_api


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
