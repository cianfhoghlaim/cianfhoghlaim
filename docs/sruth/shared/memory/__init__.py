"""Memory services for AI knowledge graphs and temporal tracking.

Provides:
- Cognee: Entity extraction and knowledge graph construction
- Graphiti: Bi-temporal knowledge graphs for version tracking
- FalkorDB: Graph database for caching and hot-path queries

Usage:
    from sruth.shared.memory import (
        CogneeService,
        GraphitiService,
        extract_knowledge_graph,
    )
"""

from .cognee_service import (
    CogneeConfig,
    CogneeService,
    COGNEE_AVAILABLE,
    extract_knowledge_graph,
    query_entity_graph,
)
from .graphiti_service import (
    GraphitiConfig,
    GraphitiService,
    GRAPHITI_AVAILABLE,
    GraphitiService,
    TemporalEntity,
    TemporalRelation,
    create_curriculum_entity,
)

__all__ = [
    # Cognee
    "CogneeConfig",
    "CogneeService",
    "COGNEE_AVAILABLE",
    "extract_knowledge_graph",
    "query_entity_graph",
    # Graphiti
    "GraphitiConfig",
    "GraphitiService",
    "GRAPHITI_AVAILABLE",
    "TemporalEntity",
    "TemporalRelation",
    "create_curriculum_entity",
]
