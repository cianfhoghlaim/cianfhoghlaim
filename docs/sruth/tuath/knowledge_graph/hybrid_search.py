"""
Hybrid Search for Tuath Celtic Educational MMO.

Combines vector similarity search (LanceDB) with graph traversal (Graphiti)
to provide comprehensive search across curriculum and mythology content.

Search Modes:
- VECTOR: Pure semantic similarity using BGE-M3 embeddings
- GRAPH: Graph traversal for relationship-based queries
- HYBRID: Combined vector + graph with reciprocal rank fusion
"""

import os
from dataclasses import dataclass
from enum import Enum
from typing import Any

import lancedb
from pydantic import BaseModel, Field


class SearchMode(str, Enum):
    """Search strategy modes."""

    VECTOR = "vector"
    GRAPH = "graph"
    HYBRID = "hybrid"


class SearchResult(BaseModel):
    """Unified search result."""

    id: str
    content_type: str  # curriculum, mythology, character, story, location
    title: str
    content: str
    score: float
    source: str  # vector, graph, or hybrid
    metadata: dict = Field(default_factory=dict)
    related_entities: list[str] = Field(default_factory=list)


class HybridSearchConfig(BaseModel):
    """Configuration for hybrid search."""

    vector_weight: float = 0.6
    graph_weight: float = 0.4
    max_results: int = 20
    min_score: float = 0.1
    include_relationships: bool = True
    relationship_depth: int = 2


@dataclass
class HybridSearchEngine:
    """
    Hybrid search engine combining vector and graph search.

    Uses:
    - LanceDB for vector similarity (BGE-M3 embeddings)
    - Graphiti/FalkorDB for graph traversal
    """

    lance_uri: str
    graphiti_client: Any | None = None

    def __post_init__(self):
        self.lance_db = lancedb.connect(self.lance_uri)

    async def search(
        self,
        query: str,
        mode: SearchMode = SearchMode.HYBRID,
        content_types: list[str] | None = None,
        config: HybridSearchConfig | None = None,
    ) -> list[SearchResult]:
        """
        Perform hybrid search across curriculum and mythology content.

        Args:
            query: Search query text
            mode: Search strategy (vector, graph, or hybrid)
            content_types: Filter to specific content types
            config: Search configuration

        Returns:
            List of SearchResult objects ranked by relevance
        """
        config = config or HybridSearchConfig()

        if mode == SearchMode.VECTOR:
            return await self._vector_search(query, content_types, config)
        elif mode == SearchMode.GRAPH:
            return await self._graph_search(query, content_types, config)
        else:
            return await self._hybrid_search(query, content_types, config)

    async def _vector_search(
        self,
        query: str,
        content_types: list[str] | None,
        config: HybridSearchConfig,
    ) -> list[SearchResult]:
        """Perform vector similarity search using LanceDB."""
        from sentence_transformers import SentenceTransformer

        model = SentenceTransformer("BAAI/bge-m3")
        query_embedding = model.encode(query, normalize_embeddings=True)

        results: list[SearchResult] = []

        # Search curriculum embeddings
        if not content_types or "curriculum" in content_types:
            try:
                table = self.lance_db.open_table("curriculum_embeddings")
                curriculum_results = (
                    table.search(query_embedding).limit(config.max_results).to_list()
                )

                for r in curriculum_results:
                    score = 1 - r.get("_distance", 0)  # Convert distance to similarity
                    if score >= config.min_score:
                        results.append(
                            SearchResult(
                                id=r.get("id", ""),
                                content_type="curriculum",
                                title=r.get("title", ""),
                                content=r.get("text", "")[:500],
                                score=score,
                                source="vector",
                                metadata={
                                    "nation": r.get("nation"),
                                    "level": r.get("level"),
                                    "subject": r.get("subject"),
                                },
                            )
                        )
            except Exception as e:
                pass  # Table may not exist yet

        # Search mythology embeddings
        if not content_types or any(
            t in ["mythology", "character", "story", "location"] for t in (content_types or [])
        ):
            try:
                table = self.lance_db.open_table("mythology_embeddings")
                mythology_results = (
                    table.search(query_embedding).limit(config.max_results).to_list()
                )

                for r in mythology_results:
                    score = 1 - r.get("_distance", 0)
                    if score >= config.min_score:
                        results.append(
                            SearchResult(
                                id=r.get("id", ""),
                                content_type=r.get("content_type", "mythology"),
                                title=r.get("name", ""),
                                content=r.get("text", "")[:500],
                                score=score,
                                source="vector",
                                metadata={
                                    "tradition": r.get("tradition"),
                                    "cycle": r.get("cycle"),
                                    "entity_type": r.get("entity_type"),
                                },
                            )
                        )
            except Exception as e:
                pass

        # Sort by score and limit
        results.sort(key=lambda x: x.score, reverse=True)
        return results[: config.max_results]

    async def _graph_search(
        self,
        query: str,
        content_types: list[str] | None,
        config: HybridSearchConfig,
    ) -> list[SearchResult]:
        """Perform graph-based search using Graphiti."""
        if not self.graphiti_client:
            return []

        try:
            graph_results = await self.graphiti_client.search(
                query=query,
                num_results=config.max_results,
            )

            results: list[SearchResult] = []
            for r in graph_results:
                # Extract related entities from graph
                related = (
                    await self._get_related_entities(r.fact, config.relationship_depth)
                    if config.include_relationships
                    else []
                )

                results.append(
                    SearchResult(
                        id=r.episode_uuid if hasattr(r, "episode_uuid") else "",
                        content_type="knowledge",
                        title=r.fact[:100] if hasattr(r, "fact") else "",
                        content=r.fact if hasattr(r, "fact") else str(r),
                        score=r.score if hasattr(r, "score") else 0.5,
                        source="graph",
                        metadata={
                            "valid_at": str(r.valid_at) if hasattr(r, "valid_at") else None,
                        },
                        related_entities=related,
                    )
                )

            return results
        except Exception as e:
            return []

    async def _hybrid_search(
        self,
        query: str,
        content_types: list[str] | None,
        config: HybridSearchConfig,
    ) -> list[SearchResult]:
        """
        Perform hybrid search combining vector and graph results.

        Uses Reciprocal Rank Fusion (RRF) to combine rankings.
        """
        # Get results from both sources
        vector_results = await self._vector_search(query, content_types, config)
        graph_results = await self._graph_search(query, content_types, config)

        # Combine using Reciprocal Rank Fusion
        k = 60  # RRF constant
        fused_scores: dict[str, tuple[float, SearchResult]] = {}

        # Add vector results with RRF score
        for rank, result in enumerate(vector_results):
            rrf_score = config.vector_weight * (1 / (k + rank + 1))
            key = f"{result.content_type}:{result.id}"
            if key in fused_scores:
                existing_score, existing_result = fused_scores[key]
                fused_scores[key] = (existing_score + rrf_score, existing_result)
            else:
                fused_scores[key] = (rrf_score, result)

        # Add graph results with RRF score
        for rank, result in enumerate(graph_results):
            rrf_score = config.graph_weight * (1 / (k + rank + 1))
            key = f"{result.content_type}:{result.id}"
            if key in fused_scores:
                existing_score, existing_result = fused_scores[key]
                # Merge related entities
                merged = existing_result.model_copy()
                merged.related_entities = list(
                    set(existing_result.related_entities + result.related_entities)
                )
                merged.source = "hybrid"
                fused_scores[key] = (existing_score + rrf_score, merged)
            else:
                result.source = "hybrid"
                fused_scores[key] = (rrf_score, result)

        # Sort by fused score
        sorted_results = sorted(
            fused_scores.values(),
            key=lambda x: x[0],
            reverse=True,
        )

        # Update scores and return
        results = []
        for fused_score, result in sorted_results[: config.max_results]:
            result.score = fused_score
            results.append(result)

        return results

    async def _get_related_entities(
        self,
        entity: str,
        depth: int,
    ) -> list[str]:
        """Get related entities from the graph."""
        if not self.graphiti_client:
            return []

        try:
            related = await self.graphiti_client.search(
                query=f"entities related to {entity}",
                num_results=10,
            )
            return [r.fact for r in related if hasattr(r, "fact")]
        except Exception:
            return []

    async def search_curriculum(
        self,
        query: str,
        nation: str | None = None,
        level: str | None = None,
        subject: str | None = None,
        limit: int = 20,
    ) -> list[SearchResult]:
        """Search curriculum content with filters."""
        results = await self.search(
            query=query,
            mode=SearchMode.VECTOR,
            content_types=["curriculum"],
            config=HybridSearchConfig(max_results=limit * 2),
        )

        # Apply filters
        filtered = []
        for r in results:
            if nation and r.metadata.get("nation") != nation:
                continue
            if level and r.metadata.get("level") != level:
                continue
            if subject and r.metadata.get("subject") != subject:
                continue
            filtered.append(r)

        return filtered[:limit]

    async def search_mythology(
        self,
        query: str,
        tradition: str | None = None,
        cycle: str | None = None,
        content_type: str | None = None,  # character, story, location
        limit: int = 20,
    ) -> list[SearchResult]:
        """Search mythology content with filters."""
        content_types = None
        if content_type:
            content_types = [content_type]
        else:
            content_types = ["character", "story", "location", "mythology"]

        results = await self.search(
            query=query,
            mode=SearchMode.HYBRID,
            content_types=content_types,
            config=HybridSearchConfig(
                max_results=limit * 2,
                include_relationships=True,
            ),
        )

        # Apply filters
        filtered = []
        for r in results:
            if tradition and r.metadata.get("tradition") != tradition:
                continue
            if cycle and r.metadata.get("cycle") != cycle:
                continue
            filtered.append(r)

        return filtered[:limit]

    async def find_related_content(
        self,
        entity_id: str,
        content_type: str,
        max_depth: int = 2,
    ) -> list[SearchResult]:
        """Find content related to a specific entity."""
        if not self.graphiti_client:
            # Fallback to vector similarity
            # Get the entity's embedding and find similar
            return []

        results = await self._graph_search(
            query=f"content related to {entity_id}",
            content_types=None,
            config=HybridSearchConfig(
                relationship_depth=max_depth,
                include_relationships=True,
            ),
        )

        return results


# Singleton instance
_search_engine: HybridSearchEngine | None = None


def get_search_engine() -> HybridSearchEngine:
    """Get or create the hybrid search engine instance."""
    global _search_engine

    if _search_engine is None:
        lance_uri = os.environ.get("LANCEDB_URI", "storage/lance/tuath")

        # Try to get Graphiti client if available
        graphiti_client = None
        try:
            from .graphiti.celtic_knowledge import get_graphiti_client

            graphiti_client = get_graphiti_client()
        except ImportError:
            pass

        _search_engine = HybridSearchEngine(
            lance_uri=lance_uri,
            graphiti_client=graphiti_client,
        )

    return _search_engine


async def hybrid_search(
    query: str,
    mode: str = "hybrid",
    content_types: list[str] | None = None,
    limit: int = 20,
) -> list[dict[str, Any]]:
    """
    Convenience function for hybrid search.

    Returns results as dictionaries for API responses.
    """
    engine = get_search_engine()

    search_mode = SearchMode(mode)
    results = await engine.search(
        query=query,
        mode=search_mode,
        content_types=content_types,
        config=HybridSearchConfig(max_results=limit),
    )

    return [r.model_dump() for r in results]
