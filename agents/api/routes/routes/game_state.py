"""
Game State API Routes.

Player progress, quests, and game world state management.
Integrates with SpacetimeDB for real-time multiplayer state.
"""

from datetime import UTC, datetime

from fastapi import APIRouter, Header, HTTPException, Query, status
from pydantic import BaseModel

from .auth import get_session_from_header

router = APIRouter()


class PlayerState(BaseModel):
    """Player game state."""

    player_id: str
    display_name: str
    level: int
    xp: int
    current_zone: str
    languages: dict[str, dict]
    active_quests: list[str]
    completed_quests: list[str]
    achievements: list[str]
    inventory: list[dict]
    play_time_hours: float
    last_login: str


class QuestState(BaseModel):
    """Quest progress state."""

    quest_id: str
    quest_name: str
    status: str
    objectives_completed: int
    objectives_total: int
    hints_used: int
    xp_reward: int
    started_at: str | None
    completed_at: str | None


class LanguageProgress(BaseModel):
    """Language learning progress."""

    language: str
    language_name: str
    level: str
    vocabulary_count: int
    grammar_topics: list[str]
    last_practice: str | None


# In-memory player storage (use SpacetimeDB in production)
_players: dict[str, dict] = {}


@router.get("/player/{player_id}")
async def get_player_state(
    player_id: str,
    x_session_id: str | None = Header(None),
) -> PlayerState:
    """Get player's game state."""
    # Verify session matches player
    if x_session_id:
        session = get_session_from_header(x_session_id)
        if session and session.get("player_id") != player_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Cannot access other player's state",
            )

    if player_id in _players:
        return PlayerState(**_players[player_id])

    # Create new player
    new_player = {
        "player_id": player_id,
        "display_name": f"Laoch {player_id[:8]}",  # Laoch = Hero in Irish
        "level": 1,
        "xp": 0,
        "current_zone": "tutorial_zone",
        "languages": {
            "ga": {
                "level": "beginner",
                "vocabulary_count": 0,
                "grammar_topics": [],
            },
        },
        "active_quests": ["tutorial_greetings"],
        "completed_quests": [],
        "achievements": [],
        "inventory": [],
        "play_time_hours": 0.0,
        "last_login": datetime.now(UTC).isoformat(),
    }
    _players[player_id] = new_player

    return PlayerState(**new_player)


@router.patch("/player/{player_id}")
async def update_player_state(
    player_id: str,
    updates: dict,
    x_session_id: str | None = Header(None),
):
    """Update player's game state."""
    if x_session_id:
        session = get_session_from_header(x_session_id)
        if session and session.get("player_id") != player_id:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail="Cannot modify other player's state",
            )

    if player_id not in _players:
        await get_player_state(player_id, x_session_id)

    # Apply updates
    allowed_updates = ["display_name", "current_zone"]
    for key in allowed_updates:
        if key in updates:
            _players[player_id][key] = updates[key]

    return {"success": True, "player_id": player_id}


@router.post("/player/{player_id}/xp")
async def add_xp(
    player_id: str,
    amount: int = Query(..., ge=1, le=1000),
    source: str = Query("quest"),
    x_session_id: str | None = Header(None),
):
    """Add XP to player and check for level up."""
    if player_id not in _players:
        await get_player_state(player_id, x_session_id)

    player = _players[player_id]
    old_level = player["level"]

    player["xp"] += amount
    new_level = (player["xp"] // 1000) + 1
    player["level"] = new_level

    leveled_up = new_level > old_level

    return {
        "player_id": player_id,
        "xp_added": amount,
        "total_xp": player["xp"],
        "level": new_level,
        "leveled_up": leveled_up,
        "source": source,
    }


@router.get("/player/{player_id}/quests")
async def get_player_quests(
    player_id: str,
    x_session_id: str | None = Header(None),
):
    """Get player's quest progress."""
    if player_id not in _players:
        await get_player_state(player_id, x_session_id)

    player = _players[player_id]

    # Build quest states
    quests = []
    for quest_id in player["active_quests"]:
        quests.append(
            QuestState(
                quest_id=quest_id,
                quest_name=QUEST_NAMES.get(quest_id, quest_id),
                status="in_progress",
                objectives_completed=0,
                objectives_total=4,
                hints_used=0,
                xp_reward=QUEST_XP.get(quest_id, 50),
                started_at=datetime.now(UTC).isoformat(),
                completed_at=None,
            )
        )

    for quest_id in player["completed_quests"]:
        quests.append(
            QuestState(
                quest_id=quest_id,
                quest_name=QUEST_NAMES.get(quest_id, quest_id),
                status="completed",
                objectives_completed=4,
                objectives_total=4,
                hints_used=0,
                xp_reward=QUEST_XP.get(quest_id, 50),
                started_at=None,
                completed_at=datetime.now(UTC).isoformat(),
            )
        )

    return {
        "player_id": player_id,
        "active": [q for q in quests if q.status == "in_progress"],
        "completed": [q for q in quests if q.status == "completed"],
    }


@router.post("/player/{player_id}/quests/{quest_id}/start")
async def start_quest(
    player_id: str,
    quest_id: str,
    x_session_id: str | None = Header(None),
):
    """Start a new quest."""
    if player_id not in _players:
        await get_player_state(player_id, x_session_id)

    player = _players[player_id]

    if quest_id in player["active_quests"]:
        return {"success": False, "message": "Quest already active"}

    if quest_id in player["completed_quests"]:
        return {"success": False, "message": "Quest already completed"}

    player["active_quests"].append(quest_id)

    return {
        "success": True,
        "quest_id": quest_id,
        "message": "Tús maith leath na hoibre! (A good start is half the work!)",
    }


@router.post("/player/{player_id}/quests/{quest_id}/complete")
async def complete_quest(
    player_id: str,
    quest_id: str,
    x_session_id: str | None = Header(None),
):
    """Complete a quest and award XP."""
    if player_id not in _players:
        await get_player_state(player_id, x_session_id)

    player = _players[player_id]

    if quest_id not in player["active_quests"]:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Quest not active",
        )

    # Complete quest
    player["active_quests"].remove(quest_id)
    player["completed_quests"].append(quest_id)

    # Award XP
    xp_reward = QUEST_XP.get(quest_id, 50)
    player["xp"] += xp_reward
    player["level"] = (player["xp"] // 1000) + 1

    return {
        "success": True,
        "quest_id": quest_id,
        "xp_awarded": xp_reward,
        "total_xp": player["xp"],
        "level": player["level"],
        "message": "Maith thú! (Well done!)",
    }


@router.get("/player/{player_id}/languages")
async def get_language_progress(
    player_id: str,
    x_session_id: str | None = Header(None),
):
    """Get player's language learning progress."""
    if player_id not in _players:
        await get_player_state(player_id, x_session_id)

    player = _players[player_id]
    languages = []

    language_names = {
        "ga": "Irish",
        "gd": "Scottish Gaelic",
        "cy": "Welsh",
    }

    for lang_code, data in player["languages"].items():
        languages.append(
            LanguageProgress(
                language=lang_code,
                language_name=language_names.get(lang_code, lang_code),
                level=data.get("level", "beginner"),
                vocabulary_count=data.get("vocabulary_count", 0),
                grammar_topics=data.get("grammar_topics", []),
                last_practice=data.get("last_practice"),
            )
        )

    return {
        "player_id": player_id,
        "languages": languages,
    }


@router.post("/player/{player_id}/languages/{language}/vocabulary")
async def add_vocabulary(
    player_id: str,
    language: str,
    words: list[str],
    x_session_id: str | None = Header(None),
):
    """Add learned vocabulary words."""
    if player_id not in _players:
        await get_player_state(player_id, x_session_id)

    player = _players[player_id]

    if language not in player["languages"]:
        player["languages"][language] = {
            "level": "beginner",
            "vocabulary_count": 0,
            "grammar_topics": [],
        }

    player["languages"][language]["vocabulary_count"] += len(words)
    player["languages"][language]["last_practice"] = datetime.now(UTC).isoformat()

    # Check for level up
    vocab_count = player["languages"][language]["vocabulary_count"]
    if vocab_count >= 500:
        player["languages"][language]["level"] = "advanced"
    elif vocab_count >= 200:
        player["languages"][language]["level"] = "intermediate"

    return {
        "success": True,
        "language": language,
        "words_added": len(words),
        "total_vocabulary": vocab_count,
        "level": player["languages"][language]["level"],
    }


@router.get("/quests")
async def get_available_quests(
    zone: str | None = Query(None),
    language: str | None = Query(None),
    min_level: int = Query(1, ge=1),
    max_level: int = Query(50, le=100),
):
    """Get available quests."""
    quests = [
        {
            "id": "tutorial_greetings",
            "name": "First Words",
            "native_name": "Na Chéad Focail",
            "description": "Learn basic greetings in Irish",
            "zone": "tutorial_zone",
            "language": "ga",
            "level_required": 1,
            "xp_reward": 50,
            "type": "language_learning",
        },
        {
            "id": "salmon_of_knowledge",
            "name": "The Salmon of Knowledge",
            "native_name": "An Bradán Feasa",
            "description": "Learn the legend of Fionn and the salmon",
            "zone": "conamara_realm",
            "language": "ga",
            "level_required": 5,
            "xp_reward": 100,
            "type": "mythology_discovery",
        },
        {
            "id": "mabinogion_pwyll",
            "name": "Pwyll and the Otherworld",
            "native_name": "Pwyll a'r Annwfn",
            "description": "Experience the First Branch of the Mabinogi",
            "zone": "gwynedd_kingdom",
            "language": "cy",
            "level_required": 15,
            "xp_reward": 150,
            "type": "mythology_discovery",
        },
        {
            "id": "gaeltacht_journey",
            "name": "Journey to the Gaeltacht",
            "native_name": "Turas go dtí an Ghaeltacht",
            "description": "Travel to an Irish-speaking region",
            "zone": "conamara_realm",
            "language": "ga",
            "level_required": 3,
            "xp_reward": 75,
            "type": "cultural_exploration",
        },
        {
            "id": "hebridean_tales",
            "name": "Tales of the Hebrides",
            "native_name": "Sgeulachdan nan Eilean",
            "description": "Discover Scottish Gaelic folklore",
            "zone": "hebridean_realm",
            "language": "gd",
            "level_required": 15,
            "xp_reward": 100,
            "type": "mythology_discovery",
        },
    ]

    # Apply filters
    if zone:
        quests = [q for q in quests if q["zone"] == zone]
    if language:
        quests = [q for q in quests if q["language"] == language]
    quests = [q for q in quests if min_level <= q["level_required"] <= max_level]

    return {
        "quests": quests,
        "total": len(quests),
    }


@router.get("/achievements")
async def get_achievements():
    """Get list of available achievements."""
    return {
        "achievements": [
            {
                "id": "first_greeting",
                "name": "Dia Duit!",
                "description": "Said hello in Irish for the first time",
                "xp_bonus": 10,
                "icon": "wave",
            },
            {
                "id": "polyglot",
                "name": "Polyglot",
                "description": "Learned words in all three Celtic languages",
                "xp_bonus": 50,
                "icon": "languages",
            },
            {
                "id": "mythology_scholar",
                "name": "Mythology Scholar",
                "description": "Completed all mythology quests",
                "xp_bonus": 100,
                "icon": "book",
            },
            {
                "id": "gaeltacht_explorer",
                "name": "Gaeltacht Explorer",
                "description": "Visited all Gaeltacht regions",
                "xp_bonus": 75,
                "icon": "map",
            },
            {
                "id": "salmon_wisdom",
                "name": "Touch of the Salmon",
                "description": "Completed the Salmon of Knowledge quest",
                "xp_bonus": 25,
                "icon": "fish",
            },
            {
                "id": "bard_level_1",
                "name": "Apprentice Bard",
                "description": "Learned 100 vocabulary words",
                "xp_bonus": 30,
                "icon": "music",
            },
            {
                "id": "bard_level_2",
                "name": "Journeyman Bard",
                "description": "Learned 500 vocabulary words",
                "xp_bonus": 75,
                "icon": "music",
            },
            {
                "id": "ollam",
                "name": "Ollam",
                "description": "Reached master level in a Celtic language",
                "xp_bonus": 200,
                "icon": "crown",
            },
        ],
    }


# Quest metadata
QUEST_NAMES = {
    "tutorial_greetings": "First Words",
    "salmon_of_knowledge": "The Salmon of Knowledge",
    "mabinogion_pwyll": "Pwyll and the Otherworld",
    "gaeltacht_journey": "Journey to the Gaeltacht",
    "hebridean_tales": "Tales of the Hebrides",
}

QUEST_XP = {
    "tutorial_greetings": 50,
    "salmon_of_knowledge": 100,
    "mabinogion_pwyll": 150,
    "gaeltacht_journey": 75,
    "hebridean_tales": 100,
}
