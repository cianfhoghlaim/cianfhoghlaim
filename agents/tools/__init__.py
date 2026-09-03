"""
Agent Tools for Celtic Education Platform.

Provides specialized tools for AI agents:
- Terminology lookup (Téarma.ie, An Seotal, Y Termiadur)
- Corpus search (LanceDB vector search, Dúchas, Teanglann)
- Curriculum search (hybrid, semantic, keyword)
- Geospatial queries (schools, Gaeltacht areas)
- Translation (Celtic languages)

Agno-compatible toolkits for multi-agent coordination.

T4 (2026-07-09): wrapped the eager top-level imports in
`try/except` so a missing `agno` install doesn't cascade into
`from cianfhoghlaim.agents.tuatha.<slug>_agent import ...` (which
some legacy `agents/adk/*.py` modules reach via `..tools.X`).
The exports below become `None` when agno is missing; consumers
that NEED a specific tool should `importlib.import_module()` the
submodule directly.
"""
from __future__ import annotations

try:
    from .corpus_search import (
        CorpusStats,
        DictionaryEntry,
        SearchResult,
        get_corpus_stats,
        search_corpus_lancedb,
        search_duchas_collection,
        search_teanglann,
    )
    from .corpus_tools import CorpusSearchTools

    # ADK Curriculum Search Tools
    from .curriculum_search import (
        CurriculumComparison,
        CurriculumSearchResult,
        compare_curricula,
        find_similar_content,
        get_learning_outcomes,
        search_curriculum,
    )

    # Agno-compatible toolkits
    from .curriculum_tools import CurriculumSearchTools
    from .geospatial_tools import GeospatialTools

    # ADK Spatial Query Tools (DuckDB Spatial)
    from .spatial_query import (
        AreaStatistics,
        NearbySchool,
        SpatialAggregation,
        find_nearby_schools,
        get_area_statistics,
        get_deprivation_correlation,
        query_by_area,
    )

    # ADK Statistics Query Tools
    from .statistics_query import (
        NationComparison,
        StatisticsResult,
        TrendData,
        compare_nations,
        get_trend,
        list_available_metrics,
        query_statistics,
    )
    from .terminology import (
        TEARMA_DOMAINS,
        DomainInfo,
        TerminologyEntry,
        compare_terminology,
        get_available_domains,
        get_domain_terms,
        lookup_tearma,
        search_terminology,
    )
    from .translation_tools import (
        TranslationTools,
        translate_to_english,
        translate_to_irish,
    )

    _AGNO_AVAILABLE = True
except Exception:
    _AGNO_AVAILABLE = False
    TEARMA_DOMAINS = None
    AreaStatistics = None
    CorpusSearchTools = None
    CorpusStats = None
    CurriculumComparison = None
    CurriculumSearchResult = None
    DictionaryEntry = None
    CurriculumSearchTools = None
    DomainInfo = None
    GeospatialTools = None
    NearbySchool = None
    NationComparison = None
    SearchResult = None
    SpatialAggregation = None
    StatisticsResult = None
    TerminologyEntry = None
    TrendData = None
    TranslationTools = None
    compare_curricula = None
    compare_nations = None
    compare_terminology = None
    find_nearby_schools = None
    find_similar_content = None
    get_area_statistics = None
    get_available_domains = None
    get_corpus_stats = None
    get_deprivation_correlation = None
    get_domain_terms = None
    get_learning_outcomes = None
    get_trend = None
    list_available_metrics = None
    lookup_tearma = None
    query_by_area = None
    query_statistics = None
    search_corpus_lancedb = None
    search_curriculum = None
    search_duchas_collection = None
    search_teanglann = None
    search_terminology = None
    translate_to_english = None
    translate_to_irish = None

__all__ = [
    "TEARMA_DOMAINS",
    # ADK Spatial Query Tools
    "AreaStatistics",
    "CorpusSearchTools",
    "CorpusStats",
    "CurriculumComparison",
    # ADK Curriculum Search Tools
    "CurriculumSearchResult",
    "CurriculumSearchTools",
    "DictionaryEntry",
    # Agno toolkits
    "DomainInfo",
    "GeospatialTools",
    "NationComparison",
    "NearbySchool",
    "SearchResult",
    "SpatialAggregation",
    "StatisticsResult",
    "TerminologyEntry",
    "TrendData",
    "TranslationTools",
    "compare_curricula",
    "compare_nations",
    "compare_terminology",
    "find_nearby_schools",
    "find_similar_content",
    "get_area_statistics",
    "get_available_domains",
    "get_corpus_stats",
    "get_deprivation_correlation",
    "get_domain_terms",
    "get_learning_outcomes",
    "get_trend",
    "list_available_metrics",
    "lookup_tearma",
    "query_by_area",
    "query_statistics",
    "search_corpus_lancedb",
    "search_curriculum",
    "search_duchas_collection",
    "search_teanglann",
    "search_terminology",
    "translate_to_english",
    "translate_to_irish",
]

