"""dlt_sources.media_intel — Cross-medium media intelligence.

DLT source for the cross-medium media intel pipeline (compares
animation + comics + games + celtic_history_research).
"""
from __future__ import annotations

import dlt


@dlt.source(name="media_intel")
def media_intel_source():
    """Yield one DLT resource per cross-medium comparison."""

    @dlt.resource(name="media_intel", write_disposition="replace")
    def comparisons():
        """One row per cross-medium comparison result."""
        yield {
            "comparison_id": "MOCK_COMPARISON_01",
            "media_kinds": ["animation", "comics", "games"],
            "subject": "hades_wow_golden_sun_pokemon",
            "score": 0.85,
        }

    return comparisons
