"""
Thin re-export shim (round 10, phase 5/6 of the 6-phase refactor plan).

Canonical home: oideachais.agents.adk.tools.tuatha_*

This module exists to preserve the historical
`from tuatha.agents.tools.curriculum_search import ...` import
pattern used by `tuatha/agents/mcp_server/server.py` lines 23-33.
The canonical implementations live in `oideachais/` (the
oideachais quadrant is the authoritative source for Celtic
curriculum + mythology content).
"""

from cianfhoghlaim.agents.adk.tools.tuatha_curriculum_search import (
    OIDEACHAIS_LANCEDB_PATH,
    CurriculumResult,
    CurriculumSearchResults,
    LearningOutcome,
    get_learning_outcomes,
    search_curriculum,
)
from cianfhoghlaim.agents.adk.tools.tuatha_mythology_query import (
    CharacterLore,
    LocationLore,
    MythologyResult,
    MythologySearchResults,
    get_character_lore,
    get_location_lore,
    search_mythology,
)

__all__ = [
    "OIDEACHAIS_LANCEDB_PATH",
    "CharacterLore",
    "CurriculumResult",
    "CurriculumSearchResults",
    "LearningOutcome",
    "LocationLore",
    "MythologyResult",
    "MythologySearchResults",
    "get_character_lore",
    "get_learning_outcomes",
    "get_location_lore",
    "search_curriculum",
    "search_mythology",
]
