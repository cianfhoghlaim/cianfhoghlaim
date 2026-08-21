"""
Temporal Knowledge Graph using Graphiti for Tuath.

Tracks Celtic mythology and curriculum evolution:
- Mythology interpretations across sources
- Curriculum updates from national bodies
- Player learning progressions
- Character relationship changes

Uses FalkorDB as the graph database backend.
"""

import os
from datetime import datetime, timezone
from typing import Any

from graphiti_core import Graphiti
from graphiti_core.nodes import EpisodeType


def get_graphiti_client() -> Graphiti:
    """Get configured Graphiti client for Celtic knowledge."""
    neo4j_uri = os.environ.get("NEO4J_URI", "bolt://localhost:7687")
    neo4j_user = os.environ.get("NEO4J_USER", "neo4j")
    neo4j_password = os.environ.get("NEO4J_PASSWORD", "password")

    return Graphiti(
        neo4j_uri=neo4j_uri,
        neo4j_user=neo4j_user,
        neo4j_password=neo4j_password,
    )


# Entity types for Celtic mythology domain
CELTIC_ENTITY_TYPES = [
    "Character",  # Mythological characters (gods, heroes, monsters)
    "Location",  # Mythological and real locations
    "Story",  # Tales, sagas, cycles
    "Artifact",  # Magical items, treasures
    "Tradition",  # Irish, Welsh, Scottish, etc.
    "Cycle",  # Ulster, Fenian, Mythological, etc.
    "CurriculumUnit",  # Educational content
    "LearningOutcome",  # Educational objectives
    "Player",  # Game players
    "Quest",  # In-game quests
]

# Relation types
CELTIC_RELATION_TYPES = [
    "APPEARS_IN",  # Character -> Story
    "LOCATED_AT",  # Character -> Location
    "RELATED_TO",  # Character -> Character (family, allies, enemies)
    "POSSESSES",  # Character -> Artifact
    "PART_OF",  # Story -> Cycle
    "TEACHES",  # CurriculumUnit -> LearningOutcome
    "REFERENCES",  # CurriculumUnit -> Story/Character
    "COMPLETED",  # Player -> Quest
    "LEARNED",  # Player -> LearningOutcome
    "BELONGS_TO",  # Location/Character -> Tradition
]


async def add_mythology_episode(
    client: Graphiti,
    entity_name: str,
    entity_type: str,
    event_type: str,
    description: str,
    metadata: dict[str, Any] | None = None,
    source_url: str | None = None,
) -> str:
    """
    Add a temporal episode for Celtic mythology content.

    Episodes track interpretations and changes over time.
    """
    timestamp = datetime.now(timezone.utc)

    episode_content = f"""
    Entity: {entity_name}
    Type: {entity_type}
    Event: {event_type}
    Description: {description}
    Timestamp: {timestamp.isoformat()}
    """

    if metadata:
        episode_content += f"\nMetadata: {metadata}"

    episode = await client.add_episode(
        name=f"{entity_type}_{entity_name}_{event_type}_{timestamp.strftime('%Y%m%d')}",
        episode_body=episode_content,
        source_description=source_url or "Tuath Knowledge Base",
        reference_time=timestamp,
        episode_type=EpisodeType.json,
    )

    return episode.uuid


async def add_character(
    client: Graphiti,
    name: str,
    native_name: str,
    tradition: str,
    cycle: str,
    character_type: str,
    description: str,
    powers: list[str] | None = None,
    relationships: list[dict[str, str]] | None = None,
    source_url: str | None = None,
) -> str:
    """Add a mythological character to the knowledge graph."""
    metadata = {
        "native_name": native_name,
        "tradition": tradition,
        "cycle": cycle,
        "character_type": character_type,
        "powers": powers or [],
        "relationships": relationships or [],
    }

    return await add_mythology_episode(
        client,
        name,
        "Character",
        "CHARACTER_ADDED",
        description,
        metadata,
        source_url,
    )


async def add_story(
    client: Graphiti,
    title: str,
    english_title: str,
    tradition: str,
    cycle: str,
    summary: str,
    themes: list[str] | None = None,
    main_characters: list[str] | None = None,
    source_url: str | None = None,
) -> str:
    """Add a mythological story to the knowledge graph."""
    metadata = {
        "english_title": english_title,
        "tradition": tradition,
        "cycle": cycle,
        "themes": themes or [],
        "main_characters": main_characters or [],
    }

    return await add_mythology_episode(
        client,
        title,
        "Story",
        "STORY_ADDED",
        summary,
        metadata,
        source_url,
    )


async def add_location(
    client: Graphiti,
    name: str,
    english_name: str,
    tradition: str,
    location_type: str,
    description: str,
    coordinates: tuple[float, float] | None = None,
    associated_stories: list[str] | None = None,
    source_url: str | None = None,
) -> str:
    """Add a mythological location to the knowledge graph."""
    metadata = {
        "english_name": english_name,
        "tradition": tradition,
        "location_type": location_type,
        "coordinates": coordinates,
        "associated_stories": associated_stories or [],
    }

    return await add_mythology_episode(
        client,
        name,
        "Location",
        "LOCATION_ADDED",
        description,
        metadata,
        source_url,
    )


async def add_curriculum_unit(
    client: Graphiti,
    title: str,
    nation: str,
    level: str,
    subject: str,
    content: str,
    learning_outcomes: list[str] | None = None,
    related_mythology: list[str] | None = None,
    source_url: str | None = None,
) -> str:
    """Add a curriculum unit to the knowledge graph."""
    metadata = {
        "nation": nation,
        "level": level,
        "subject": subject,
        "learning_outcomes": learning_outcomes or [],
        "related_mythology": related_mythology or [],
    }

    return await add_mythology_episode(
        client,
        title,
        "CurriculumUnit",
        "CURRICULUM_ADDED",
        content[:500],  # Truncate for episode
        metadata,
        source_url,
    )


async def record_player_progress(
    client: Graphiti,
    player_id: str,
    event_type: str,  # quest_complete, vocabulary_learned, level_up
    details: str,
    metadata: dict[str, Any] | None = None,
) -> str:
    """Record player learning progress."""
    return await add_mythology_episode(
        client,
        player_id,
        "Player",
        event_type.upper(),
        details,
        metadata,
    )


async def query_character_timeline(
    client: Graphiti,
    character_name: str,
    include_relationships: bool = True,
) -> list[dict[str, Any]]:
    """Query the temporal history of a character."""
    results = await client.search(
        query=f"timeline for character {character_name}",
        num_results=50,
    )

    timeline = [
        {
            "event": r.fact,
            "timestamp": r.valid_at if hasattr(r, "valid_at") else None,
            "source": r.episode_uuid if hasattr(r, "episode_uuid") else None,
        }
        for r in results
    ]

    if include_relationships:
        # Add relationship data
        rel_results = await client.search(
            query=f"relationships of {character_name}",
            num_results=20,
        )
        for r in rel_results:
            timeline.append(
                {
                    "event": f"Relationship: {r.fact}",
                    "timestamp": r.valid_at if hasattr(r, "valid_at") else None,
                    "type": "relationship",
                }
            )

    return sorted(timeline, key=lambda x: x.get("timestamp") or "", reverse=True)


async def find_story_connections(
    client: Graphiti,
    story_title: str,
) -> list[dict[str, Any]]:
    """Find connections between stories (shared characters, locations, themes)."""
    results = await client.search(
        query=f"stories connected to {story_title}",
        num_results=20,
    )

    return [
        {
            "story": r.fact,
            "connection_type": "shared_element",
            "confidence": r.score if hasattr(r, "score") else None,
        }
        for r in results
    ]


async def get_curriculum_for_mythology(
    client: Graphiti,
    mythology_element: str,
) -> list[dict[str, Any]]:
    """Find curriculum content related to a mythology element."""
    results = await client.search(
        query=f"curriculum that teaches {mythology_element}",
        num_results=10,
    )

    return [
        {
            "curriculum": r.fact,
            "relevance": r.score if hasattr(r, "score") else None,
        }
        for r in results
    ]


async def get_player_knowledge_graph(
    client: Graphiti,
    player_id: str,
) -> dict[str, Any]:
    """Get a player's learned knowledge as a graph."""
    # Get completed quests
    quests = await client.search(
        query=f"quests completed by player {player_id}",
        num_results=50,
    )

    # Get learned vocabulary
    vocabulary = await client.search(
        query=f"vocabulary learned by player {player_id}",
        num_results=100,
    )

    # Get encountered mythology
    mythology = await client.search(
        query=f"mythology encountered by player {player_id}",
        num_results=50,
    )

    return {
        "player_id": player_id,
        "quests_completed": [r.fact for r in quests if hasattr(r, "fact")],
        "vocabulary_learned": [r.fact for r in vocabulary if hasattr(r, "fact")],
        "mythology_encountered": [r.fact for r in mythology if hasattr(r, "fact")],
    }
