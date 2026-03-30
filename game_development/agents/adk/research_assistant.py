"""
Research Assistant Agent for Tuath.

Deep research on Celtic topics:
- Language history and evolution
- Comparative linguistics
- Historical context
- Cultural connections
"""

import datetime

from google.adk.agents import LlmAgent
from google.adk.tools import FunctionTool

from ..config import config
from ..tools.curriculum_search import search_curriculum
from ..tools.mythology_query import search_mythology


# Define tools
async def research_curriculum(
    topic: str,
    nations: list[str] | None = None,
    languages: list[str] | None = None,
) -> list[dict]:
    """
    Research curriculum content across nations.

    Args:
        topic: Research topic
        nations: Nations to search (ireland, scotland, wales)
        languages: Language codes (ga, gd, cy, en)
    """
    results = []
    nations = nations or ["ireland", "scotland", "wales"]
    for nation in nations:
        try:
            nation_results = await search_curriculum(topic, nation=nation, limit=5)
            if hasattr(nation_results, "results"):
                results.extend(nation_results.results)
        except Exception:
            continue
    return results


async def research_mythology(
    topic: str,
    traditions: list[str] | None = None,
) -> list[dict]:
    """
    Research mythology across traditions.

    Args:
        topic: Research topic
        traditions: Traditions to search (irish, welsh, scottish)
    """
    results = []
    traditions = traditions or ["irish", "welsh", "scottish"]
    for tradition in traditions:
        try:
            tradition_results = await search_mythology(topic, tradition=tradition, limit=5)
            if hasattr(tradition_results, "results"):
                results.extend(tradition_results.results)
        except Exception:
            continue
    return results


async def compare_languages(
    feature: str,
) -> dict:
    """
    Compare linguistic features across Celtic languages.

    Args:
        feature: Grammatical or linguistic feature
    """
    # Search for the feature in each language's curriculum
    results = {"feature": feature, "comparisons": {}}

    languages = {"ga": "Irish", "gd": "Scottish Gaelic", "cy": "Welsh"}
    for code, name in languages.items():
        try:
            search_results = await search_curriculum(feature, language=code, limit=3)
            results["comparisons"][name] = (
                search_results.results if hasattr(search_results, "results") else []
            )
        except Exception:
            results["comparisons"][name] = []

    return results


# Create tools
curriculum_research = FunctionTool(func=research_curriculum)
mythology_research = FunctionTool(func=research_mythology)
language_comparison = FunctionTool(func=compare_languages)


# Research Assistant Agent
research_assistant_agent = LlmAgent(
    name="research_assistant_agent",
    model=config.worker_model,
    description="Deep research on Celtic languages, culture, and history.",
    instruction=f"""
    You are a Celtic Studies Research Assistant, providing scholarly
    yet accessible information on Celtic languages and cultures.

    **YOUR EXPERTISE:**
    - Celtic linguistics and language evolution
    - Comparative Celtic studies
    - Historical context of Celtic nations
    - Cultural traditions and practices
    - Academic sources and references

    **AVAILABLE TOOLS:**
    1. research_curriculum - Search educational content
    2. research_mythology - Search folklore and mythology
    3. compare_languages - Compare linguistic features

    **CELTIC LANGUAGE FAMILY:**

    **Goidelic (Q-Celtic):**
    - Irish (Gaeilge) - ~1.7 million speakers
    - Scottish Gaelic (Gàidhlig) - ~57,000 speakers
    - Manx (Gaelg) - revived language

    **Brythonic (P-Celtic):**
    - Welsh (Cymraeg) - ~560,000 speakers
    - Breton (Brezhoneg) - ~200,000 speakers
    - Cornish (Kernewek) - revived language

    **KEY RESEARCH AREAS:**

    **Language Evolution:**
    - Proto-Celtic origins
    - Sound changes (P-Celtic vs Q-Celtic split)
    - Medieval manuscript traditions
    - Modern standardization

    **Cultural Connections:**
    - Shared mythological themes
    - Celtic Christianity
    - Bardic traditions
    - Music and poetry

    **Historical Context:**
    - Celtic Iron Age
    - Roman influence
    - Medieval kingdoms
    - Language decline and revival

    **RESEARCH APPROACH:**
    1. Identify the research question
    2. Search relevant curriculum and mythology
    3. Compare across Celtic traditions
    4. Synthesize findings
    5. Cite sources where available

    **RESPONSE FORMAT:**
    - Clear section headings
    - Comparative tables when useful
    - Celtic terms with translations
    - Academic but accessible language

    Current date: {datetime.datetime.now().strftime("%Y-%m-%d")}

    Let us explore the rich tapestry of Celtic heritage...
    """,
    tools=[curriculum_research, mythology_research, language_comparison],
    output_key="research",
)
