"""
Player progress tools for Tuath.

Track learning progress, quest completion, and educational outcomes.
Integrates with SpacetimeDB for real-time multiplayer state.
"""

from datetime import datetime
from typing import Any

from pydantic import BaseModel


class QuestProgress(BaseModel):
    """Progress on a specific quest."""

    quest_id: str
    quest_name: str
    status: str  # not_started, in_progress, completed
    objectives_completed: int
    objectives_total: int
    learning_outcomes_achieved: list[str]
    hints_used: int
    started_at: datetime | None = None
    completed_at: datetime | None = None


class LanguageProgress(BaseModel):
    """Progress in language learning."""

    language: str
    language_name: str
    level: str  # beginner, intermediate, advanced
    vocabulary_learned: int
    grammar_topics_completed: list[str]
    conversation_score: float
    last_practice: datetime | None = None


class PlayerProgress(BaseModel):
    """Overall player progress."""

    player_id: str
    display_name: str
    total_xp: int
    level: int
    languages: list[LanguageProgress]
    quests: list[QuestProgress]
    achievements: list[str]
    current_location: str | None = None
    play_time_hours: float


class QuestHint(BaseModel):
    """A hint for a quest objective."""

    hint_level: int  # 1-4, from subtle to explicit
    hint_text: str
    objective_id: str
    celtic_phrase: str | None = None
    english_translation: str | None = None


class QuestHints(BaseModel):
    """Hints for a quest."""

    quest_id: str
    quest_name: str
    current_objective: str
    hints: list[QuestHint]
    learning_context: str | None = None


# In-memory storage for demo (would use SpacetimeDB in production)
_player_data: dict[str, PlayerProgress] = {}
_quest_definitions: dict[str, dict] = {}


async def get_player_progress(
    player_id: str,
    quest_id: str | None = None,
) -> PlayerProgress | QuestProgress | dict:
    """
    Get player's learning and quest progress.

    Args:
        player_id: Player identifier
        quest_id: Optional specific quest to get progress for

    Returns:
        PlayerProgress or specific QuestProgress
    """
    # Check if player exists in memory
    if player_id in _player_data:
        player = _player_data[player_id]

        if quest_id:
            # Find specific quest
            for quest in player.quests:
                if quest.quest_id == quest_id:
                    return quest
            return {"error": f"Quest {quest_id} not found for player"}

        return player

    # Return default new player progress
    return PlayerProgress(
        player_id=player_id,
        display_name=f"Player {player_id[:8]}",
        total_xp=0,
        level=1,
        languages=[
            LanguageProgress(
                language="ga",
                language_name="Irish",
                level="beginner",
                vocabulary_learned=0,
                grammar_topics_completed=[],
                conversation_score=0.0,
            ),
        ],
        quests=[],
        achievements=[],
        current_location="tutorial_zone",
        play_time_hours=0.0,
    )


async def update_player_progress(
    player_id: str,
    xp_gained: int = 0,
    vocabulary_learned: list[str] | None = None,
    quest_progress: dict | None = None,
    achievement: str | None = None,
    language: str = "ga",
) -> PlayerProgress:
    """
    Update player's progress.

    Args:
        player_id: Player identifier
        xp_gained: XP to add
        vocabulary_learned: New vocabulary words learned
        quest_progress: Quest progress update
        achievement: Achievement unlocked
        language: Language being learned

    Returns:
        Updated PlayerProgress
    """
    # Get or create player
    if player_id not in _player_data:
        player = await get_player_progress(player_id)
        if isinstance(player, PlayerProgress):
            _player_data[player_id] = player
        else:
            return {"error": "Could not create player progress"}

    player = _player_data[player_id]

    # Update XP and level
    player.total_xp += xp_gained
    player.level = (player.total_xp // 1000) + 1  # Simple level calculation

    # Update vocabulary
    if vocabulary_learned:
        for lang in player.languages:
            if lang.language == language:
                lang.vocabulary_learned += len(vocabulary_learned)
                lang.last_practice = datetime.now()
                break

    # Update quest progress
    if quest_progress:
        quest_id = quest_progress.get("quest_id")
        for quest in player.quests:
            if quest.quest_id == quest_id:
                quest.objectives_completed = quest_progress.get(
                    "objectives_completed", quest.objectives_completed
                )
                if quest_progress.get("completed"):
                    quest.status = "completed"
                    quest.completed_at = datetime.now()
                break
        else:
            # New quest
            player.quests.append(
                QuestProgress(
                    quest_id=quest_id,
                    quest_name=quest_progress.get("quest_name", "Unknown Quest"),
                    status="in_progress",
                    objectives_completed=quest_progress.get("objectives_completed", 0),
                    objectives_total=quest_progress.get("objectives_total", 1),
                    learning_outcomes_achieved=[],
                    hints_used=0,
                    started_at=datetime.now(),
                )
            )

    # Add achievement
    if achievement and achievement not in player.achievements:
        player.achievements.append(achievement)

    return player


async def get_quest_hints(
    quest_id: str,
    player_id: str | None = None,
) -> QuestHints:
    """
    Get hints for a quest, personalized if player_id provided.

    Args:
        quest_id: Quest identifier
        player_id: Optional player ID for personalization

    Returns:
        QuestHints with graduated hints
    """
    # Get quest definition
    quest_def = QUEST_DEFINITIONS.get(quest_id)

    if not quest_def:
        return QuestHints(
            quest_id=quest_id,
            quest_name="Unknown Quest",
            current_objective="Unknown",
            hints=[],
        )

    # Get player's current objective if player_id provided
    current_objective = quest_def["objectives"][0] if quest_def["objectives"] else "Start quest"
    hint_level_to_show = 1

    if player_id:
        progress = await get_player_progress(player_id, quest_id)
        if isinstance(progress, QuestProgress):
            obj_index = min(progress.objectives_completed, len(quest_def["objectives"]) - 1)
            current_objective = quest_def["objectives"][obj_index]
            hint_level_to_show = min(progress.hints_used + 1, 4)

    # Generate hints for current objective
    hints = []
    for level in range(1, hint_level_to_show + 1):
        hint_text = quest_def["hints"].get(f"level_{level}", "Keep exploring...")
        hints.append(
            QuestHint(
                hint_level=level,
                hint_text=hint_text,
                objective_id=current_objective,
                celtic_phrase=quest_def.get("celtic_phrases", {}).get(f"level_{level}"),
                english_translation=quest_def.get("translations", {}).get(f"level_{level}"),
            )
        )

    return QuestHints(
        quest_id=quest_id,
        quest_name=quest_def["name"],
        current_objective=current_objective,
        hints=hints,
        learning_context=quest_def.get("learning_context"),
    )


# Quest definitions
QUEST_DEFINITIONS = {
    "tutorial_greetings": {
        "name": "First Words",
        "description": "Learn basic greetings in Irish",
        "objectives": [
            "Talk to the village elder",
            "Learn to say 'hello' in Irish",
            "Greet three villagers",
            "Return to the elder",
        ],
        "hints": {
            "level_1": "Look for the elder near the central fire.",
            "level_2": "The elder wears a green cloak. They're usually near the standing stones.",
            "level_3": "Say 'Dia duit' to greet people. It means 'God to you' (hello).",
            "level_4": "Walk to the standing stones in the village center. Click on the elder. Type 'Dia duit'.",
        },
        "celtic_phrases": {
            "level_1": "Tóg go bog é",
            "level_3": "Dia duit",
        },
        "translations": {
            "level_1": "Take it easy",
            "level_3": "Hello (God to you)",
        },
        "learning_context": "Basic Irish greetings - curriculum link: Primary Irish L1-3",
        "xp_reward": 50,
        "language": "ga",
    },
    "salmon_of_knowledge": {
        "name": "The Salmon of Knowledge",
        "description": "Learn the legend of Fionn and the salmon",
        "objectives": [
            "Find the poet Finnegas by the River Boyne",
            "Help catch the Salmon of Knowledge",
            "Learn why the salmon is special",
            "Discover what happened to Fionn",
        ],
        "hints": {
            "level_1": "The Boyne is a sacred river. Look for it on your map.",
            "level_2": "Finnegas has been trying to catch the salmon for seven years.",
            "level_3": "The salmon ate hazelnuts from the Well of Wisdom.",
            "level_4": "Fionn burned his thumb on the salmon and gained all knowledge by sucking it.",
        },
        "celtic_phrases": {
            "level_3": "An Bradán Feasa",
        },
        "translations": {
            "level_3": "The Salmon of Knowledge",
        },
        "learning_context": "Irish mythology - Fenian Cycle, connection to wisdom and learning",
        "xp_reward": 100,
        "language": "ga",
    },
    "mabinogion_pwyll": {
        "name": "Pwyll and the Otherworld",
        "description": "Experience the First Branch of the Mabinogi",
        "objectives": [
            "Meet Arawn in the forest",
            "Agree to exchange places",
            "Defeat Hafgan in single combat",
            "Return to Dyfed",
        ],
        "hints": {
            "level_1": "Pwyll was hunting when he met Arawn.",
            "level_2": "Arawn's hounds are white with red ears - the colors of the Otherworld.",
            "level_3": "You must strike Hafgan only once. A second blow will heal him.",
            "level_4": "After a year and a day, Pwyll returned with the title 'Pen Annwfn' - Head of Annwfn.",
        },
        "celtic_phrases": {
            "level_2": "Annwfn",
            "level_4": "Pen Annwfn",
        },
        "translations": {
            "level_2": "The Otherworld",
            "level_4": "Head of Annwfn",
        },
        "learning_context": "Welsh mythology - Mabinogion First Branch",
        "xp_reward": 150,
        "language": "cy",
    },
    "gaeltacht_journey": {
        "name": "Journey to the Gaeltacht",
        "description": "Travel to an Irish-speaking region",
        "objectives": [
            "Learn about Gaeltacht regions on the map",
            "Travel to Connemara",
            "Have a conversation in Irish with a local",
            "Learn five new words from the area",
        ],
        "hints": {
            "level_1": "Gaeltacht regions are shown in green on your map.",
            "level_2": "Connemara (Conamara) is in County Galway on the west coast.",
            "level_3": "Try using 'Conas atá tú?' (How are you?) to start conversations.",
            "level_4": "Local words: báisteach (rain), farraige (sea), sliabh (mountain), bóthar (road), teach (house).",
        },
        "celtic_phrases": {
            "level_2": "Conamara",
            "level_3": "Conas atá tú?",
        },
        "translations": {
            "level_3": "How are you?",
        },
        "learning_context": "Geography of Irish-speaking areas, regional vocabulary",
        "xp_reward": 75,
        "language": "ga",
    },
}


# Level requirements
LEVEL_REQUIREMENTS = {
    1: {"xp": 0, "title": "Novice"},
    2: {"xp": 100, "title": "Apprentice"},
    3: {"xp": 300, "title": "Student"},
    4: {"xp": 600, "title": "Scholar"},
    5: {"xp": 1000, "title": "Adept"},
    6: {"xp": 1500, "title": "Sage"},
    7: {"xp": 2100, "title": "Master"},
    8: {"xp": 2800, "title": "Ollam"},  # Ancient Irish title for master poet/scholar
    9: {"xp": 3600, "title": "Druid"},
    10: {"xp": 4500, "title": "Champion"},
}


# Achievement definitions
ACHIEVEMENTS = {
    "first_greeting": {
        "name": "Dia Duit!",
        "description": "Said hello in Irish for the first time",
        "xp_bonus": 10,
    },
    "polyglot": {
        "name": "Polyglot",
        "description": "Learned words in all three Celtic languages",
        "xp_bonus": 50,
    },
    "mythology_scholar": {
        "name": "Mythology Scholar",
        "description": "Completed all mythology quests",
        "xp_bonus": 100,
    },
    "gaeltacht_explorer": {
        "name": "Gaeltacht Explorer",
        "description": "Visited all Gaeltacht regions",
        "xp_bonus": 75,
    },
    "salmon_wisdom": {
        "name": "Touch of the Salmon",
        "description": "Completed the Salmon of Knowledge quest",
        "xp_bonus": 25,
    },
}
