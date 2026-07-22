"""
Re-export shim. See __init__.py for the canonical home
(`oideachais.agents.adk.tools.tuatha_mythology_query`).
"""

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
    "CharacterLore",
    "LocationLore",
    "MythologyResult",
    "MythologySearchResults",
    "get_character_lore",
    "get_location_lore",
    "search_mythology",
]
