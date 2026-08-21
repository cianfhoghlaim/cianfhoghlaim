"""Cognee AI memory service for knowledge graph extraction.

Cognee provides:
- Entity extraction from text
- Knowledge graph construction
- Semantic clustering
- Integration with graph databases (FalkorDB) and vector stores

Usage:
    from sruth.shared.memory.cognee_service import CogneeService

    service = CogneeService()
    await service.extract_and_store(document_text)
"""

from __future__ import annotations

import os
from dataclasses import dataclass, field
from typing import Any

try:
    import cognee
    from cognee.api.v1.cognee import cognee as cognee_module
    from cognee.modules.graph.database import GraphDBAdapter

    COGNEE_AVAILABLE = True
except ImportError:
    COGNEE_AVAILABLE = False
    cognee = None
    GraphDBAdapter = None


@dataclass
class CogneeConfig:
    """Configuration for Cognee service."""

    # Graph database
    graph_provider: str = "falkordb"  # falkordb, neo4j, postgres
    graph_uri: str = "redis://localhost:6379"
    graph_username: str | None = None
    graph_password: str | None = None

    # Vector database
    vector_provider: str = "lancedb"  # lancedb, qdrant, pgvector
    vector_uri: str = "./lancedb_data"

    # LLM for extraction
    llm_provider: str = "openai"
    llm_model: str = "gpt-4o"
    llm_api_key: str | None = None

    # Data directory
    data_directory: str = "./cognee_data"

    @classmethod
    def from_env(cls) -> CogneeConfig:
        """Create configuration from environment variables."""
        return cls(
            graph_provider=os.getenv("COGNEE_GRAPH_PROVIDER", "falkordb"),
            graph_uri=os.getenv("FALKORDB_URI", os.getenv("GRAPH_URI", "redis://localhost:6379")),
            graph_username=os.getenv("FALKORDB_USER", os.getenv("GRAPH_USERNAME")),
            graph_password=os.getenv("FALKORDB_PASSWORD", os.getenv("GRAPH_PASSWORD")),
            vector_provider=os.getenv("COGNEE_VECTOR_PROVIDER", "lancedb"),
            vector_uri=os.getenv("LANCEDB_URI", os.getenv("VECTOR_URI", "./lancedb_data")),
            llm_provider=os.getenv("COGNEE_LLM_PROVIDER", "openai"),
            llm_model=os.getenv("COGNEE_LLM_MODEL", "gpt-4o"),
            llm_api_key=os.getenv("OPENAI_API_KEY", os.getenv("LLM_API_KEY")),
            data_directory=os.getenv("COGNEE_DATA_DIR", "./cognee_data"),
        )


class CogneeService:
    """Cognee AI memory service.

    Extracts entities, relationships, and knowledge graphs from text.
    Integrates with FalkorDB for graph storage.
    """

    def __init__(self, config: CogneeConfig | None = None):
        """Initialize Cognee service.

        Args:
            config: Service configuration
        """
        if not COGNEE_AVAILABLE:
            raise ImportError("Cognee is not installed. Install with: pip install cognee")

        self.config = config or CogneeConfig.from_env()
        self._initialized = False

    async def initialize(self) -> None:
        """Initialize Cognee with configured graph and vector databases."""
        if self._initialized:
            return

        # Configure Cognee
        cognee.config.set_graph_db_config(
            provider=self.config.graph_provider,
            uri=self.config.graph_uri,
            username=self.config.graph_username,
            password=self.config.graph_password,
        )

        cognee.config.set_vector_db_config(
            provider=self.config.vector_provider,
            uri=self.config.vector_uri,
        )

        cognee.config.set_llm_config(
            provider=self.config.llm_provider,
            model=self.config.llm_model,
            api_key=self.config.llm_api_key,
        )

        cognee.config.data_directory = self.config.data_directory

        # Initialize
        await cognee.prune.prune_data()
        await cognee.config.set_config()

        self._initialized = True

    async def extract_and_store(
        self,
        text: str,
        dataset_name: str = "default",
    ) -> dict[str, Any]:
        """Extract entities and relationships from text and store in graph.

        Args:
            text: Input text to process
            dataset_name: Dataset name for organization

        Returns:
            Extraction results with entity and relationship counts
        """
        await self.initialize()

        # Add text to Cognee
        await cognee.add(text, dataset_name=dataset_name)

        # Extract entities and relationships
        await cognee.extract(payload=dataset_name)

        # Store in graph database
        graph_results = await cognee.graph_db.get()

        # Cluster and classify
        await cognee.cluster_data()

        return {
            "entities": graph_results.get("entities", []),
            "relationships": graph_results.get("relationships", []),
            "entity_count": len(graph_results.get("entities", [])),
            "relationship_count": len(graph_results.get("relationships", [])),
        }

    async def query_graph(
        self,
        query: str,
        limit: int = 10,
    ) -> list[dict[str, Any]]:
        """Query the knowledge graph.

        Args:
            query: Graph query (Cypher, etc.)
            limit: Result limit

        Returns:
            Query results
        """
        await self.initialize()

        # For FalkorDB, use RedisGraph query
        if self.config.graph_provider == "falkordb":
            return await self._query_falkordb(query, limit)

        # Generic query through Cognee
        results = await cognee.graph_db.get(query)
        return results if isinstance(results, list) else [results]

    async def _query_falkordb(
        self,
        query: str,
        limit: int,
    ) -> list[dict[str, Any]]:
        """Query FalkorDB graph database.

        Args:
            query: Cypher query
            limit: Result limit

        Returns:
            Query results
        """
        # FalkorDB uses RedisGraph with Cypher syntax
        try:
            from redis import Redis
            from redis.asyncio import Redis as AsyncRedis

            # Connect to FalkorDB
            client = AsyncRedis.from_url(self.config.graph_uri)

            # Execute graph query
            result = await client.graphquery(
                "cognee_graph",
                query,
            )

            await client.close()
            return result

        except Exception as e:
            # Fall back to Cognee's query
            return await cognee.graph_db.get(query)

    async def get_entity_graph(
        self,
        entity_name: str | None = None,
        depth: int = 2,
    ) -> dict[str, Any]:
        """Get entity graph centered on an entity.

        Args:
            entity_name: Center entity (None for all)
            depth: Traversal depth

        Returns:
            Graph data with nodes and edges
        """
        await self.initialize()

        if entity_name:
            query = f"""
            MATCH (n {{name: '{entity_name}'}})-[r]-(m)
            RETURN n, r, m
            LIMIT {limit}
            """
        else:
            query = f"""
            MATCH (n)-[r]-(m)
            RETURN n, r, m
            LIMIT {depth * 100}
            """

        results = await self.query_graph(query)

        return {
            "nodes": self._extract_nodes(results),
            "edges": self._extract_edges(results),
        }

    def _extract_nodes(self, results: list[dict]) -> list[dict]:
        """Extract unique nodes from query results."""
        nodes = {}
        for result in results:
            for key in result:
                if key.startswith("n") or key.startswith("m"):
                    entity = result[key]
                    if entity and "id" in entity:
                        nodes[entity["id"]] = entity
        return list(nodes.values())

    def _extract_edges(self, results: list[dict]) -> list[dict]:
        """Extract edges from query results."""
        edges = []
        for result in results:
            for key in result:
                if key.startswith("r") and result[key]:
                    edges.append(result[key])
        return edges

    async def search_similar(
        self,
        text: str,
        limit: int = 10,
    ) -> list[dict[str, Any]]:
        """Search for similar content using vector embeddings.

        Args:
            text: Query text
            limit: Result limit

        Returns:
            Similar documents/entities
        """
        await self.initialize()

        # Add query as temporary document
        await cognee.add(text, dataset_name="query")

        # Extract and search
        await cognee.extract(payload="query")

        # Vector search
        results = await cognee.search.search(text, limit=limit)

        # Clean up query dataset
        await cognee.prune.prune_data("query")

        return results

    async def get_entity_summary(
        self,
        entity_name: str,
    ) -> dict[str, Any]:
        """Get summary of an entity with its connections.

        Args:
            entity_name: Entity name

        Returns:
            Entity summary with properties and connections
        """
        await self.initialize()

        query = f"""
        MATCH (n {{name: '{entity_name}'}})
        OPTIONAL MATCH (n)-[r]-(m)
        RETURN n, count(r) as connection_count
        """

        results = await self.query_graph(query)

        if results:
            return {
                "entity": results[0].get("n", {}),
                "connection_count": results[0].get("connection_count", 0),
            }

        return {}

    async def close(self) -> None:
        """Close connections and cleanup."""
        if self._initialized:
            await cognee.close()
            self._initialized = False


# ============================================================================
# Convenience Functions
# ============================================================================


async def extract_knowledge_graph(
    text: str,
    config: CogneeConfig | None = None,
) -> dict[str, Any]:
    """Convenience function for knowledge graph extraction.

    Args:
        text: Input text
        config: Optional Cognee configuration

    Returns:
        Extraction results
    """
    service = CogneeService(config)
    result = await service.extract_and_store(text)
    await service.close()
    return result


async def query_entity_graph(
    query: str,
    config: CogneeConfig | None = None,
) -> list[dict[str, Any]]:
    """Convenience function for querying the graph.

    Args:
        query: Graph query
        config: Optional Cognee configuration

    Returns:
        Query results
    """
    service = CogneeService(config)
    results = await service.query_graph(query)
    await service.close()
    return results
