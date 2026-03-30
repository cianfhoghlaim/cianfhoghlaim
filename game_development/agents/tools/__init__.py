"""
Agent tools for Tuath Celtic Educational MMO.

Provides search, translation, and game state tools for ADK agents.
"""

from .curriculum_search import search_curriculum, get_learning_outcomes
from .mythology_query import search_mythology, get_character_lore, get_location_lore
from .translation import translate_text, get_vocabulary
from .player_progress import get_player_progress, get_quest_hints, update_player_progress
from .spatial_query import query_celtic_regions, get_gaeltacht_info

__all__ = [
    "search_curriculum",
    "get_learning_outcomes",
    "search_mythology",
    "get_character_lore",
    "get_location_lore",
    "translate_text",
    "get_vocabulary",
    "get_player_progress",
    "get_quest_hints",
    "update_player_progress",
    "query_celtic_regions",
    "get_gaeltacht_info",
]
