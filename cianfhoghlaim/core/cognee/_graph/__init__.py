"""
Graph Database Integration for Irish Education Pipeline.

Provides clients for:
- Memgraph: Primary temporal knowledge graph
- FalkorDB: Redis-based graph caching
- Cache: Unified caching layer with hot path optimization
- Graphiti 0.5: Real temporal knowledge graph client
  (FalkorDB-backed, with FalkorDB Lite fallback for local dev)
- Research: LightRAG + Cognee for bunchloch document retrieval

The 2026-06 refactor: the hand-rolled `oideachais/graph/temporal.py`
(Graphiti-in-pure-Python) has been retained as a *type-only* module
(REFACTORING.md item 7); production code now uses the real
`graphiti_client` here.
"""

from .cache import (
    CacheConfig,
    CacheWarmer,
    GraphCacheManager,
    cached_graph_query,
    get_cache_manager,
    get_cache_warmer,
)
from .graphiti_client import (
    DEFAULT_FALKORDB_LITE_PATH,
    DEFAULT_FALKORDB_URI,
    GRAPHITI_AVAILABLE,
    GraphitiClient,
    graphiti_client,
)
from .research import (
    BackendType,
    QueryMode,
    ResearchGraph,
    ResearchLightRAG,
    ResearchMemgraph,
    ResearchMemory,
)
from .temporal import (
    CurriculumChange,
    EdgeStatus,
    Episode,
    EpisodeSourceType,
    TemporalEdge,
    TemporalQuery,
)
from .temporal_client import (
    TemporalCurriculumGraph,
    TemporalGraphClient,
    get_temporal_graph,
)

__all__ = [
    "DEFAULT_FALKORDB_LITE_PATH",
    "DEFAULT_FALKORDB_URI",
    "GRAPHITI_AVAILABLE",
    "BackendType",
    # Cache
    "CacheConfig",
    "CacheWarmer",
    "CurriculumChange",
    # Temporal Types
    "EdgeStatus",
    "Episode",
    "EpisodeSourceType",
    "GraphCacheManager",
    # Graphiti 0.5 (the real client; supersedes the hand-rolled
    # `oideachais/graph/temporal.py` for production code paths)
    "GraphitiClient",
    "QueryMode",
    "ResearchGraph",
    # Research (migrated from taighde.knowledge_graph)
    "ResearchLightRAG",
    "ResearchMemgraph",
    "ResearchMemory",
    "TemporalCurriculumGraph",
    "TemporalEdge",
    # Temporal Client
    "TemporalGraphClient",
    "TemporalQuery",
    "cached_graph_query",
    "get_cache_manager",
    "get_cache_warmer",
    "get_temporal_graph",
    "graphiti_client",
]
