"""
DLT source for Téarma.ie (Irish Terminology Database) — bulk export.

Provides access to the official Irish terminology export from Foras na
Gaeilge's terminology database, for linking curriculum content to
standardised terms.

API: https://www.tearma.ie/api/
Download: https://www.tearma.ie/ioslodail/

Usage:
    from dlt_sources.language.tearma import tearma_source

    pipeline = dlt.pipeline(
        pipeline_name="tearma",
        destination="duckdb",
    )
    pipeline.run(tearma_source())

Split out of the legacy `dlt_sources/tearma.py` flat file in Phase 4
(oideachais-audit-phase-4-consolidate-legacy-dirs). The companion
search source lives at `dlt_sources.language.tearma_search`.
Shared helpers + module constants + `TerminologyLinker` live at
`dlt_sources.language._tearma_helpers`.
"""
from __future__ import annotations
import dlt


from collections.abc import Iterator
from typing import Any

import dlt_sources
from dlt_sources.language._tearma_helpers import _load_tearma_terms


@dlt.source(name="tearma")
def tearma_source(
    use_api: bool = False,
    domain_filter: str | None = None,
):
    """
    DLT source for Téarma.ie Irish terminology database.

    Args:
        use_api: Use API for real-time queries (requires specific searches)
        domain_filter: Filter to specific domain (e.g., "education", "computing")

    Returns:
        DLT source with tearma_terms resource
    """

    @dlt.resource(
        name="tearma_terms",
        write_disposition="merge",
        primary_key=["term_en", "term_ga"],
    )
    def tearma_terms() -> Iterator[dict[str, Any]]:
        """All Téarma terms from the export."""
        yield from _load_tearma_terms(use_api, domain_filter)

    @dlt.resource(
        name="tearma_education",
        write_disposition="merge",
        primary_key=["term_en", "term_ga"],
    )
    def tearma_education() -> Iterator[dict[str, Any]]:
        """Téarma terms filtered to education domain."""
        for entry in _load_tearma_terms(use_api=False):
            if "status" in entry:
                yield entry
                continue
            domain = entry.get("domain", "").lower()
            if any(
                d in domain
                for d in ["education", "oideachas", "school", "scoil", "curriculum"]
            ):
                yield entry

    return tearma_terms, tearma_education


__all__ = ["tearma_source"]
