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

T4 (2026-07-09): wrapped the unconditional `from .education_team`
import in `try/except` so the `cianfhoghlaim.agents` package can be
imported in environments without `agno` (most CI runs + the
`test_subject_router_smoke` acceptance test). The exports below
become `None` when agno is missing.
"""
from __future__ import annotations

try:
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
    _AGNO_AVAILABLE = True
except Exception:
    _AGNO_AVAILABLE = False
    STORAGE_DIR = None
    CorpusSearchResult = None
    CurriculumSearchResult = None
    EducationResponse = None
    GeospatialResult = None
    ResearchReport = None
    StatisticsResult = None
    TranslationResult = None
    ask_education_team = None
    corpus_agent = None
    curriculum_agent = None
    education_team = None
    geospatial_agent = None
    research_agent = None
    search_corpus = None
    search_curriculum = None
    statistics_agent = None
    team_storage = None
    translate_content = None
    translation_agent = None

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
    "team_storage",
    "translate_content",
    "translation_agent",
]
