"""
Knowledge graph assets for entity extraction and temporal tracking.

Assets:
- cognee_knowledge_graph: Cognee entity resolution → Memgraph
- graphiti_temporal_graph: Graphiti temporal episodes → FalkorDB
"""

from defs.knowledge.cognee_extraction import cognee_knowledge_graph
from defs.knowledge.graphiti_temporal import graphiti_temporal_graph

__all__ = [
    "cognee_knowledge_graph",
    "graphiti_temporal_graph",
]
