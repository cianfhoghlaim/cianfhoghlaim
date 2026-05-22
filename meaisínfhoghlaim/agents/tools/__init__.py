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
    # Terminology
    "TerminologyEntry",
    "DomainInfo",
    "lookup_tearma",
    "search_terminology",
    "get_domain_terms",
    "get_available_domains",
    "compare_terminology",
    "TEARMA_DOMAINS",
    # Corpus Search
    "SearchResult",
    "CorpusStats",
    "DictionaryEntry",
    "search_corpus_lancedb",
    "search_duchas_collection",
    "search_teanglann",
    "get_corpus_stats",
    # Agno Toolkits
    "CurriculumSearchTools",
    "CorpusSearchTools",
    "GeospatialTools",
    "TranslationTools",
    "translate_to_irish",
    "translate_to_english",
    # ADK Spatial Query Tools
    "AreaStatistics",
    "NearbySchool",
    "SpatialAggregation",
    "query_by_area",
    "get_area_statistics",
    "find_nearby_schools",
    "get_deprivation_correlation",
    # ADK Statistics Query Tools
    "StatisticsResult",
    "NationComparison",
    "TrendData",
    "query_statistics",
    "compare_nations",
    "get_trend",
    "list_available_metrics",
    # ADK Curriculum Search Tools
    "CurriculumSearchResult",
    "CurriculumComparison",
    "search_curriculum",
    "find_similar_content",
    "compare_curricula",
    "get_learning_outcomes",
]
