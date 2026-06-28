"""
Celtic Tutor Agent for Tuath.

Language learning support for:
- Irish (Gaeilge)
- Scottish Gaelic (Gàidhlig)
- Welsh (Cymraeg)

Provides grammar explanations, vocabulary practice, and translation help.
"""

import datetime

from google.adk.agents import LlmAgent
from google.adk.tools import FunctionTool

from .tools.tuatha_curriculum_search import get_learning_outcomes, search_curriculum
from .tools.tuatha_translation import get_vocabulary, translate_text
from .tuatha_config import config


# Define tools
async def search_curriculum_tool(
    query: str,
    language: str | None = None,
    level: str | None = None,
) -> list[dict]:
    """
    Search curriculum content for teaching material.

    Args:
        query: Topic or concept to search for
        language: Target language (ga, gd, cy)
        level: Education level (primary, secondary)
    """
    try:
        results = await search_curriculum(query, language=language, level=level, limit=5)
        return results.results if hasattr(results, "results") else []
    except Exception:
        return []


async def get_vocabulary_tool(
    word: str,
    source_language: str = "en",
    target_language: str = "ga",
) -> dict:
    """
    Get vocabulary entry with translations and examples.

    Args:
        word: Word to look up
        source_language: Source language code
        target_language: Target language code
    """
    try:
        return await get_vocabulary(word, source_language, target_language)
    except Exception:
        return {"error": "Vocabulary lookup failed"}


async def translate_text_tool(
    text: str,
    source_language: str,
    target_language: str,
) -> dict:
    """
    Translate text between languages.

    Args:
        text: Text to translate
        source_language: Source language code (en, ga, gd, cy)
        target_language: Target language code
    """
    try:
        return await translate_text(text, source_language, target_language)
    except Exception:
        return {"error": "Translation failed"}


async def get_learning_outcomes_tool(
    topic: str,
    nation: str | None = None,
    level: str | None = None,
) -> list[dict]:
    """
    Get curriculum learning outcomes for a topic.

    Args:
        topic: Subject topic
        nation: Nation (ireland, scotland, wales)
        level: Education level
    """
    try:
        return await get_learning_outcomes(topic, nation=nation, level=level)
    except Exception:
        return []


# Create tools
curriculum_tool = FunctionTool(func=search_curriculum_tool)
vocabulary_tool = FunctionTool(func=get_vocabulary_tool)
translate_tool = FunctionTool(func=translate_text_tool)
outcomes_tool = FunctionTool(func=get_learning_outcomes_tool)


# Celtic Tutor Agent
celtic_tutor_agent = LlmAgent(
    name="celtic_tutor_agent",
    model=config.worker_model,
    description="Language learning tutor for Irish, Scottish Gaelic, and Welsh.",
    instruction=f"""
    You are a Celtic Language Tutor specializing in teaching:
    - Irish (Gaeilge) - Official language of Ireland
    - Scottish Gaelic (Gàidhlig) - Native language of Scotland
    - Welsh (Cymraeg) - Official language of Wales

    **YOUR EXPERTISE:**
    - Grammar explanations (mutations, verb conjugations, cases)
    - Vocabulary and phrases
    - Translation with context
    - Pronunciation guidance
    - Cultural context

    **AVAILABLE TOOLS:**
    1. search_curriculum_tool - Find teaching materials
    2. get_vocabulary_tool - Look up words
    3. translate_text_tool - Translate between languages
    4. get_learning_outcomes_tool - Get curriculum objectives

    **TEACHING APPROACH:**
    1. Always provide both Celtic text AND English translation
    2. Explain grammar points clearly
    3. Give multiple examples
    4. Connect to curriculum learning outcomes
    5. Use encouraging, supportive tone

    **CELTIC LANGUAGE FEATURES TO EXPLAIN:**

    **Irish (Gaeilge):**
    - Initial mutations (séimhiú, urú)
    - Word order (VSO)
    - Copula (is) vs. substantive verb (tá)
    - Cases (tuiseal)
    - Genitive constructions

    **Scottish Gaelic (Gàidhlig):**
    - Lenition and eclipsis
    - Definite article mutations
    - Verbal noun constructions
    - Periphrastic expressions

    **Welsh (Cymraeg):**
    - Soft, nasal, and aspirate mutations
    - Verb-subject-object order
    - Inflected prepositions
    - Colloquial vs. literary forms

    **RESPONSE FORMAT:**
    When teaching vocabulary:
    - Word in Celtic language
    - Pronunciation guide
    - English translation
    - Example sentence (Celtic + English)

    When explaining grammar:
    - Rule explanation
    - Examples showing the pattern
    - Common mistakes to avoid
    - Practice exercise suggestion

    Current date: {datetime.datetime.now().strftime("%Y-%m-%d")}

    Go n-éirí an t-ádh leat! (Good luck in Irish!)
    """,
    tools=[curriculum_tool, vocabulary_tool, translate_tool, outcomes_tool],
    output_key="teaching_response",
)
