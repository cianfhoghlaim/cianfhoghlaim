"""
Graph Database Integration for Irish Education Pipeline.

Provides clients for:
- Memgraph: Primary temporal knowledge graph
- FalkorDB: Redis-based graph caching
- Cache: Unified caching layer with hot path optimization
- Temporal: Bi-temporal edge model (Graphiti-style)
- Research: LightRAG + Cognee for bunchloch document retrieval
"""

from .cache import (
    CacheConfig,
    GraphCacheManager,
    CacheWarmer,
    get_cache_manager,
    get_cache_warmer,
    cached_graph_query,
)

from .temporal import (
    EdgeStatus,
    EpisodeSourceType,
    TemporalEdge,
    Episode,
    TemporalQuery,
    CurriculumChange,
)

from .temporal_client import (
    TemporalGraphClient,
    TemporalCurriculumGraph,
    get_temporal_graph,
)

from .research import (
    ResearchLightRAG,
    ResearchMemory,
    ResearchMemgraph,
    ResearchGraph,
    QueryMode,
    BackendType,
)

__all__ = [
    # Cache
    "CacheConfig",
    "GraphCacheManager",
    "CacheWarmer",
    "get_cache_manager",
    "get_cache_warmer",
    "cached_graph_query",
    # Temporal Types
    "EdgeStatus",
    "EpisodeSourceType",
    "TemporalEdge",
    "Episode",
    "TemporalQuery",
    "CurriculumChange",
    # Temporal Client
    "TemporalGraphClient",
    "TemporalCurriculumGraph",
    "get_temporal_graph",
    # Research (migrated from taighde.knowledge_graph)
    "ResearchLightRAG",
    "ResearchMemory",
    "ResearchMemgraph",
    "ResearchGraph",
    "QueryMode",
    "BackendType",
]
