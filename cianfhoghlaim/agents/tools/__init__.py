"""
Agent Tools for Celtic Education Platform.

Provides specialized tools for AI agents:
- Terminology lookup (Téarma.ie, An Seotal, Y Termiadur)
- Corpus search (LanceDB vector search, Dúchas, Teanglann)
- Curriculum search (hybrid, semantic, keyword)
- Geospatial queries (schools, Gaeltacht areas)
- Translation (Celtic languages)

Agno-compatible toolkits for multi-agent coordination.
"""

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
from .translation_tools import TranslationTools, translate_to_english, translate_to_irish

__all__ = [
    "TEARMA_DOMAINS",
    # ADK Spatial Query Tools
    "AreaStatistics",
    "CorpusSearchTools",
    "CorpusStats",
    "CurriculumComparison",
    # ADK Curriculum Search Tools
    "CurriculumSearchResult",
    # Agno Toolkits
    "CurriculumSearchTools",
    "DictionaryEntry",
    "DomainInfo",
    "GeospatialTools",
    "NationComparison",
    "NearbySchool",
    # Corpus Search
    "SearchResult",
    "SpatialAggregation",
    # ADK Statistics Query Tools
    "StatisticsResult",
    # Terminology
    "TerminologyEntry",
    "TranslationTools",
    "TrendData",
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
