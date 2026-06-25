"""
Quest Guide Agent for Tuath.

Helps players navigate educational quests tied to curriculum:
- Language learning quests
- Cultural exploration quests
- Mythology discovery quests

Tracks learning outcomes and provides hints.
"""

import datetime

from google.adk.agents import LlmAgent
from google.adk.tools import FunctionTool

from .tools.tuatha_curriculum_search import search_curriculum, get_learning_outcomes
from .tools.tuatha_player_progress import get_player_progress, get_quest_hints
from .tuatha_config import config


# Define tools
async def get_quest_hints_tool(
    quest_id: str,
    player_id: str | None = None,
) -> dict:
    """
    Get hints for a quest.

    Args:
        quest_id: Quest identifier
        player_id: Optional player ID for personalized hints
    """
    try:
        return await get_quest_hints(quest_id, player_id=player_id)
    except Exception:
        return {"error": "Could not get hints"}


async def get_player_progress_tool(
    player_id: str,
    quest_id: str | None = None,
) -> dict:
    """
    Get player's learning progress.

    Args:
        player_id: Player identifier
        quest_id: Optional specific quest
    """
    try:
        return await get_player_progress(player_id, quest_id=quest_id)
    except Exception:
        return {"error": "Could not get progress"}


async def search_related_curriculum(
    topic: str,
    level: str | None = None,
) -> list[dict]:
    """
    Find curriculum content related to quest topic.

    Args:
        topic: Quest topic
        level: Education level
    """
    try:
        results = await search_curriculum(topic, level=level, limit=5)
        return results.results if hasattr(results, "results") else []
    except Exception:
        return []


async def get_learning_outcomes_for_quest(
    topic: str,
    nation: str | None = None,
) -> list[dict]:
    """
    Get learning outcomes connected to quest.

    Args:
        topic: Quest topic
        nation: Target nation's curriculum
    """
    try:
        return await get_learning_outcomes(topic, nation=nation)
    except Exception:
        return []


# Create tools
hints_tool = FunctionTool(func=get_quest_hints_tool)
progress_tool = FunctionTool(func=get_player_progress_tool)
curriculum_tool = FunctionTool(func=search_related_curriculum)
outcomes_tool = FunctionTool(func=get_learning_outcomes_for_quest)


# Quest Guide Agent
quest_guide_agent = LlmAgent(
    name="quest_guide_agent",
    model=config.worker_model,
    description="Quest guidance with learning outcome tracking for educational quests.",
    instruction=f"""
    You are a Quest Guide for the Tuath educational MMO, helping players
    complete quests that teach Celtic languages and culture.

    **YOUR ROLE:**
    - Guide players through quest objectives
    - Provide hints without giving away answers
    - Track educational progress
    - Connect quests to learning outcomes

    **AVAILABLE TOOLS:**
    1. get_quest_hints_tool - Get quest hints
    2. get_player_progress_tool - Check player progress
    3. search_related_curriculum - Find related teaching content
    4. get_learning_outcomes_for_quest - Get curriculum connections

    **QUEST TYPES:**

    **Language Quests:**
    - Vocabulary collection quests
    - Grammar puzzle quests
    - Translation challenges
    - Conversation practice with NPCs

    **Cultural Quests:**
    - Visit mythological locations
    - Learn about Celtic festivals
    - Discover historical events
    - Explore traditional crafts

    **Story Quests:**
    - Follow mythological narratives
    - Make choices affecting story
    - Interact with legendary characters
    - Uncover ancient mysteries

    **GUIDANCE APPROACH:**
    1. Understand what the player is stuck on
    2. Check their current progress
    3. Provide graduated hints (subtle → explicit)
    4. Connect to learning objectives
    5. Encourage exploration and discovery

    **HINT LEVELS:**
    - Level 1: Subtle nudge in right direction
    - Level 2: More specific guidance
    - Level 3: Direct but not complete answer
    - Level 4: Clear step-by-step help

    **RESPONSE FORMAT:**
    - Acknowledge player's question
    - Check quest context
    - Provide appropriate hint level
    - Mention learning opportunity
    - Encourage continued exploration

    Current date: {datetime.datetime.now().strftime("%Y-%m-%d")}

    Your journey through the Celtic lands continues...
    """,
    tools=[hints_tool, progress_tool, curriculum_tool, outcomes_tool],
    output_key="guidance",
)
