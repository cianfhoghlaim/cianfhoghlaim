"""Re-export shim: iom/education (canonical path, Phase 3E).

Per Phase 3E, the canonical home for the Isle of Man education source
is `iom.education.isle_of_man` (split from the deprecated
`crown_dependencies/` umbrella in Round 11).
"""
from __future__ import annotations

from dlt_sources.iom.education.isle_of_man import isle_of_man_source

__all__ = ["isle_of_man_source"]
