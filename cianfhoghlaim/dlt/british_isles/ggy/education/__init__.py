"""Re-export shim: ggy/education (canonical path, Phase 3E).

Per Phase 3E, the canonical home for the Guernsey education source
is `ggy.education.channel_islands` (split from the deprecated
`crown_dependencies/` umbrella in Round 11).
"""
from __future__ import annotations

from dlt_sources.ggy.education.channel_islands import guernsey_source

__all__ = ["guernsey_source"]
