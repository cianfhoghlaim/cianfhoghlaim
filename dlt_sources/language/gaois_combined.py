"""
Culture IE source: gaois_combined_source

Split from celtic/gaois.py in Phase 3D.
"""

from __future__ import annotations

from collections.abc import Iterator

from dlt.sources import DltResource

try:
    from dlt_sources.common.http_client import ainm_client, logainm_client, tearma_client  # noqa: F401
except ImportError:
    pass  # shared.http is unavailable; functions must lazy-import at call-time


def gaois_combined_source(
    logainm_county: str | None = None,
    max_placenames: int = 500,
    max_terms: int = 200,
    max_biographies: int = 100,
) -> Iterator[DltResource]:
    """
    Combined source for all GAOIS databases.

    Args:
        logainm_county: Filter placenames by county
        max_placenames: Maximum placenames to fetch
        max_terms: Maximum terminology entries
        max_biographies: Maximum biographical entries

    Yields:
        Combined DLT resources from all GAOIS databases
    """
    # Yield placenames
    for resource in logainm_source(
        county=logainm_county, max_results=max_placenames
    ):
        yield resource

    # Yield terminology
    for resource in tearma_source(max_terms=max_terms):
        yield resource

    # Yield biographies
    for resource in ainm_source(max_entries=max_biographies):
        yield resource
