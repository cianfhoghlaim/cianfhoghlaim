"""cianfhoghlaim.cianfhoghlaim.dlt.british_isles.ireland.law — Ireland legal DLT sources.

Phase 6 of the openspec change. Covers both **statutory** law sources
(`irish_statute_book`, `doj`, `lawreform`) and the **operational** law
sources added in `2026-07-06-ireland-legal-pipeline` (`injuries_ie`,
`courts_ie`, `workplace_relations`, `citizensinformation`,
`gov_ie_law`).
"""
from __future__ import annotations

from cianfhoghlaim.dlt.british_isles.ireland.law import (
    citizensinformation,
    courts_ie,
    doj,
    gov_ie_law,
    injuries_ie,
    irish_statute_book,
    lawreform,
    workplace_relations,
)

__all__ = [
    "citizensinformation",
    "courts_ie",
    "doj",
    "gov_ie_law",
    "injuries_ie",
    "irish_statute_book",
    "lawreform",
    "workplace_relations",
]
