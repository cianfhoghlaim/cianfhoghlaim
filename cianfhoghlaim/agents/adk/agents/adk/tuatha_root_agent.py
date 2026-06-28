"""
Root Agent for Tuath - Celtic Educational MMO Platform.

Orchestrates specialist agents for Celtic language learning,
mythology-based NPC interactions, and educational quests.
"""

import datetime

from google.adk.agents import LlmAgent
from google.adk.apps.app import App

from .celtic_tutor_agent import celtic_tutor_agent
from .mythology_narrator_agent import mythology_narrator_agent
from .quest_guide_agent import quest_guide_agent
from .research_assistant_agent import research_assistant_agent
from .tuatha_config import config

# Root orchestrator agent
root_agent = LlmAgent(
    name="tuath_agent",
    model=config.orchestrator_model,
    description="Main assistant for Celtic language learning and educational MMO.",
    instruction=f"""
    You are Tuath, an expert AI assistant for Celtic language learning and
    Celtic mythology exploration within an educational MMO environment.

    You help players:
    - Learn Celtic languages (Irish, Scottish Gaelic, Welsh)
    - Explore Celtic mythology and folklore
    - Complete educational quests tied to curriculum
    - Navigate the game world with cultural context

    **YOUR ROLE:**
    Route queries to the appropriate specialist agent and synthesize responses.
    Maintain an engaging, educational tone appropriate for an MMO setting.

    **SPECIALIST AGENTS:**

    1. **celtic_tutor_agent**
       - Language learning support
       - Grammar explanations
       - Vocabulary practice
       - Translation help
       - Use for: "How do I say...", "What does X mean...", "Explain the grammar..."

    2. **mythology_narrator_agent**
       - Celtic mythology and folklore
       - NPC character backgrounds
       - Story and lore queries
       - Use for: "Tell me about...", "Who is...", "What is the story of..."

    3. **quest_guide_agent**
       - Quest objectives and hints
       - Learning outcome tracking
       - Progress guidance
       - Use for: "How do I complete...", "What should I do next...", "Where can I find..."

    4. **research_assistant_agent**
       - Deep research on Celtic topics
       - Curriculum connections
       - Historical context
       - Use for: "Research...", "What is the history of...", "Compare..."

    **SUPPORTED LANGUAGES:**
    - Irish (Gaeilge) - ga
    - Scottish Gaelic (Gàidhlig) - gd
    - Welsh (Cymraeg) - cy
    - English (for explanations)

    **GAME WORLD CONTEXT:**
    The Tuath game world is divided into regions representing:
    - Gaeltacht zones (Irish-speaking areas of Ireland)
    - Alba Realm (Gaelic-speaking areas of Scotland)
    - Welsh Lands (Welsh-speaking areas of Wales)

    Players interact with NPCs based on Celtic mythology:
    - Tuatha Dé Danann (Irish divine race)
    - Fianna (Irish warrior band)
    - Characters from the Mabinogion (Welsh myths)

    **RESPONSE APPROACH:**
    1. Identify if query is language/mythology/quest related
    2. Use appropriate Celtic language when relevant
    3. Provide English explanations alongside Celtic text
    4. Connect responses to curriculum learning outcomes
    5. Maintain immersive MMO atmosphere

    Current date: {datetime.datetime.now().strftime("%Y-%m-%d")}

    Dia duit! (Hello in Irish) / Halò! (Hello in Scottish Gaelic) / Shwmae! (Hello in Welsh)
    """,
    sub_agents=[
        celtic_tutor_agent,
        mythology_narrator_agent,
        quest_guide_agent,
        research_assistant_agent,
    ],
    output_key="response",
)


# Create the app
app = App(
    root_agent=root_agent,
    name="tuath",
)


# Query classifier for routing
def classify_query(query: str) -> str:
    """Classify query to determine best agent."""
    query_lower = query.lower()

    # Language learning keywords
    if any(
        kw in query_lower
        for kw in [
            "translate",
            "how do you say",
            "what does",
            "mean",
            "grammar",
            "vocabulary",
            "word",
            "phrase",
            "pronunciation",
            "learn",
            "practice",
            "gaeilge",
            "gàidhlig",
            "cymraeg",
        ]
    ):
        return "tutor"

    # Quest keywords
    if any(
        kw in query_lower
        for kw in [
            "quest",
            "mission",
            "objective",
            "complete",
            "find",
            "where",
            "how do i",
            "next step",
            "hint",
            "help me",
            "stuck",
        ]
    ):
        return "quest"

    # Mythology keywords
    if any(
        kw in query_lower
        for kw in [
            "story",
            "legend",
            "myth",
            "who is",
            "tell me about",
            "lore",
            "character",
            "hero",
            "god",
            "goddess",
            "tuatha",
            "fianna",
            "mabinogion",
        ]
    ):
        return "mythology"

    # Default to research
    return "research"


# Export for use as library
__all__ = [
    "app",
    "celtic_tutor_agent",
    "classify_query",
    "mythology_narrator_agent",
    "quest_guide_agent",
    "research_assistant_agent",
    "root_agent",
]
