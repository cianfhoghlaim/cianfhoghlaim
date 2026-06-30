"""
Re-export shim. See __init__.py for the canonical home
(`oideachais.agents.adk.tools.tuatha_curriculum_search`).
"""

from cianfhoghlaim.agents.adk.tools.tuatha_curriculum_search import (
    OIDEACHAIS_DATA_PATH,
    OIDEACHAIS_LANCEDB_PATH,
    CurriculumResult,
    CurriculumSearchResults,
    LearningOutcome,
    get_learning_outcomes,
    search_curriculum,
)

__all__ = [
    "OIDEACHAIS_DATA_PATH",
    "OIDEACHAIS_LANCEDB_PATH",
    "CurriculumResult",
    "CurriculumSearchResults",
    "LearningOutcome",
    "get_learning_outcomes",
    "search_curriculum",
]
