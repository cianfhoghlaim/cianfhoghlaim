"""
Re-export shim. See __init__.py for the canonical home
(`oideachais.agents.adk.tools.tuatha_curriculum_search`).
"""

from oideachais.agents.adk.tools.tuatha_curriculum_search import (
    CurriculumResult,
    CurriculumSearchResults,
    LearningOutcome,
    OIDEACHAIS_DATA_PATH,
    OIDEACHAIS_LANCEDB_PATH,
    get_learning_outcomes,
    search_curriculum,
)

__all__ = [
    "CurriculumResult",
    "CurriculumSearchResults",
    "LearningOutcome",
    "OIDEACHAIS_DATA_PATH",
    "OIDEACHAIS_LANCEDB_PATH",
    "get_learning_outcomes",
    "search_curriculum",
]
