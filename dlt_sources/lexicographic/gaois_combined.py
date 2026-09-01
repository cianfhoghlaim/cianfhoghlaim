"""
Culture IE source: gaois_combined_source

Split from celtic/gaois.py in Phase 3D.
"""

from __future__ import annotations

from collections.abc import Iterator

from dlt.sources import DltResource

from .ainm import ainm_source
from .logainm import logainm_source
from .tearma import tearma_source


def gaois_combined_source(
    logainm_county: str | None = None,
    max_placenames: int = 500,
    max_terms: int = 200,
    max_biographies: int = 100,
) -> list[DltResource]:
    """
    Combined source for all GAOIS databases.

    Args:
        logainm_county: Filter placenames by county
        max_placenames: Maximum placenames to fetch
        max_terms: Maximum terminology entries
        max_biographies: Maximum biographical entries

    Returns:
        Combined DLT resources from all GAOIS databases.

    Was previously a generator function that did
    `for resource in <sub_source>(): yield resource` for each of the 3
    sub-sources. That has two compounding bugs:
    1. `TypeError: Parametrized resource 'placenames' is not callable...`
       when the resulting bare generator was passed to `pipeline.run()` —
       fixed by returning a fully materialized `list[DltResource]`
       instead (same pattern `all_exam_boards_source()`/
       `leaving_cert_source.py` already use elsewhere in this repo).
    2. `tearma_source()` is `@dlt.source`-decorated, and iterating a
       `DltSource` directly (`for x in tearma_source()`) yields its
       *data rows*, not its `DltResource` objects — the loop variable
       named `resource` was actually holding raw term dicts. The
       correct accessor for a source's resource objects is
       `.resources.values()` (a `DltResourcesDict`). Confirmed live:
       without this, `pipeline.run()` raised `ResourceNameMissing`
       trying to auto-wrap a raw dict as a resource.
       `logainm_source()`/`ainm_source()` are plain generators that
       already yield `DltResource` objects directly, not `DltSource`s,
       so they don't need `.resources`.
    """
    resources: list[DltResource] = []
    resources.extend(logainm_source(county=logainm_county, max_results=max_placenames))

    # tearma_source() doesn't support a max_terms cap (it's a bulk-export
    # source, not a paginated query) — max_terms is accepted here for
    # API-compatibility with the other 2 sources but currently unused;
    # capping would need slicing the export itself.
    resources.extend(tearma_source().resources.values())

    resources.extend(ainm_source(max_entries=max_biographies))
    return resources
