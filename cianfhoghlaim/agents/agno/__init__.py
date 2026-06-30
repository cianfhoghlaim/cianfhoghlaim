"""
Agno Team Agents for Celtic Education Platform.

Multi-agent teams with shared context coordination for:
- Curriculum search and navigation
- Research discovery across Celtic resources
- Translation between Celtic languages
- Corpus search (folklore, historical texts)
- Geospatial education queries
- Education statistics analysis

Supports session persistence via SqliteDb.
"""

from .education_team import (
    STORAGE_DIR,
    CorpusSearchResult,
    CurriculumSearchResult,
    # Output models
    EducationResponse,
    GeospatialResult,
    ResearchReport,
    StatisticsResult,
    TranslationResult,
    # Convenience functions
    ask_education_team,
    corpus_agent,
    curriculum_agent,
    # Team and agents
    education_team,
    geospatial_agent,
    research_agent,
    search_corpus,
    search_curriculum,
    statistics_agent,
    # Storage
    team_storage,
    translate_content,
    translation_agent,
)

__all__ = [
    "STORAGE_DIR",
    "CorpusSearchResult",
    "CurriculumSearchResult",
    # Output models
    "EducationResponse",
    "GeospatialResult",
    "ResearchReport",
    "StatisticsResult",
    "TranslationResult",
    # Convenience functions
    "ask_education_team",
    "corpus_agent",
    "curriculum_agent",
    # Team and agents
    "education_team",
    "geospatial_agent",
    "research_agent",
    "search_corpus",
    "search_curriculum",
    "statistics_agent",
    # Storage
    "team_storage",
    "translate_content",
    "translation_agent",
]
