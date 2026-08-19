"""
Mythology Narrator Agent for Tuath.

NPC dialogue and lore generation based on Celtic mythology:
- Irish mythology (Tuatha Dé Danann, Fianna, Ulster Cycle)
- Welsh mythology (Mabinogion)
- Scottish folklore

Generates immersive NPC interactions and story content.
"""

import datetime

from .litellm_agent import litellm_model
from google.adk.agents import LlmAgent
from google.adk.tools import FunctionTool

from .tools.tuatha_mythology_query import (
    get_character_lore,
    get_location_lore,
    search_mythology,
)
from .tuatha_config import config


# Define tools
async def search_mythology_tool(
    query: str,
    tradition: str | None = None,
    cycle: str | None = None,
) -> list[dict]:
    """
    Search mythology and folklore content.

    Args:
        query: Topic, character, or story to search
        tradition: Celtic tradition (irish, welsh, scottish)
        cycle: Mythological cycle (tuatha_de_danann, fianna, ulster, mabinogion)
    """
    try:
        results = await search_mythology(query, tradition=tradition, cycle=cycle, limit=5)
        return results.results if hasattr(results, "results") else []
    except Exception:
        return []


async def get_character_info(
    character_name: str,
) -> list[dict]:
    """
    Get lore for a mythological character.

    Args:
        character_name: Name of the character
    """
    try:
        return await get_character_lore(character_name)
    except Exception:
        return []


async def get_location_info(
    location_name: str,
    tradition: str | None = None,
) -> list[dict]:
    """
    Get lore for a mythological location.

    Args:
        location_name: Name of the place
        tradition: Celtic tradition
    """
    try:
        return await get_location_lore(location_name, tradition=tradition)
    except Exception:
        return []


# Create tools
mythology_tool = FunctionTool(func=search_mythology_tool)
character_tool = FunctionTool(func=get_character_info)
location_tool = FunctionTool(func=get_location_info)


# Mythology Narrator Agent
mythology_narrator_agent = LlmAgent(
    name="mythology_narrator_agent",
    model=config.worker_model,
    description="Celtic mythology narrator for NPC dialogue and lore generation.",
    instruction=f"""
    You are a Celtic Mythology Narrator, bringing ancient stories to life
    in an immersive MMO setting. You channel the voice of mythological
    characters and narrate Celtic legends.

    **YOUR EXPERTISE:**
    - Irish mythology and folklore
    - Welsh mythology (Mabinogion)
    - Scottish folklore and legends
    - Character backstories and motivations
    - Location lore and significance

    **AVAILABLE TOOLS:**
    1. search_mythology_tool - Find mythology content
    2. get_character_info - Get character backstory
    3. get_location_info - Get location lore

    **MAJOR MYTHOLOGICAL CYCLES:**

    **Irish - Tuatha Dé Danann:**
    - Lugh Lámhfhada (god of skills)
    - Dagda (father god)
    - Brigid (goddess of poetry)
    - Manannán mac Lir (god of the sea)
    - Nuada Airgetlám (king with silver arm)

    **Irish - Fianna:**
    - Fionn mac Cumhaill (leader)
    - Oisín (poet-warrior)
    - Oscar (Oisín's son)
    - Diarmuid Ó Duibhne (lover of Gráinne)
    - Caílte mac Rónáin (swift runner)

    **Irish - Ulster Cycle:**
    - Cú Chulainn (champion of Ulster)
    - Medb (Queen of Connacht)
    - Conchobar mac Nessa (King of Ulster)
    - Deirdre (tragic heroine)

    **Welsh - Mabinogion:**
    - Pwyll (Lord of Dyfed)
    - Rhiannon (horse goddess)
    - Pryderi (son of Pwyll)
    - Branwen (tragic heroine)
    - Taliesin (legendary bard)

    **NARRATION STYLE:**
    - Speak as the character when in dialogue mode
    - Use archaic but understandable language
    - Include Celtic phrases with translations
    - Reference mythological events and relationships
    - Create immersive, evocative descriptions

    **RESPONSE FORMAT:**
    For character dialogue:
    - Character name in bold
    - Dialogue in quotes
    - English translation if using Celtic phrases
    - Atmospheric description

    For lore explanation:
    - Story context
    - Key characters involved
    - Significance in mythology
    - Connection to game world

    Current date: {datetime.datetime.now().strftime("%Y-%m-%d")}

    *The mist parts to reveal ancient wisdom...*
    """,
    tools=[mythology_tool, character_tool, location_tool],
    output_key="narration",
)
