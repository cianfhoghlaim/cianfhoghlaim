"""
Graphiti integration for Tuath.

Temporal knowledge graph for Celtic mythology and curriculum content.
"""

from .celtic_knowledge import (
    add_character,
    add_curriculum_unit,
    add_location,
    add_mythology_episode,
    add_story,
    find_story_connections,
    get_curriculum_for_mythology,
    get_graphiti_client,
    get_player_knowledge_graph,
    query_character_timeline,
    record_player_progress,
)

__all__ = [
    "get_graphiti_client",
    "add_mythology_episode",
    "add_character",
    "add_story",
    "add_location",
    "add_curriculum_unit",
    "record_player_progress",
    "query_character_timeline",
    "find_story_connections",
    "get_curriculum_for_mythology",
    "get_player_knowledge_graph",
]
