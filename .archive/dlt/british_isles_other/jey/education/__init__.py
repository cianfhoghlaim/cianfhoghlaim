"""Re-export shim: jey/education (canonical path, Phase 3E).

Per Phase 3E, the canonical home for the Jersey education source
is `jey.education.channel_islands` (split from the deprecated
`crown_dependencies/` umbrella in Round 11).
"""
from __future__ import annotations

from dlt_sources.jey.education.channel_islands import jersey_source

__all__ = ["jersey_source"]
