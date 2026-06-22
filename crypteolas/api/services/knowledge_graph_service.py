"""
Knowledge Graph Service for Crypteolas.

Provides unified access to Graphiti (temporal) and Cognee (static) knowledge graphs.
"""

from datetime import datetime
from typing import Any


class KnowledgeGraphService:
    """Service for knowledge graph operations."""

    def __init__(
        self,
        graphiti_url: str | None = None,
        memgraph_url: str | None = None,
    ):
        """Initialize knowledge graph connections."""
        self.graphiti_url = graphiti_url or "bolt://localhost:6379"
        self.memgraph_url = memgraph_url or "bolt://localhost:7687"
        self._graphiti = None
        self._memgraph = None

    @property
    def graphiti(self):
        """Get or create Graphiti client for temporal graph."""
        if self._graphiti is None:
            try:
                from graphiti_core import Graphiti
                self._graphiti = Graphiti(url=self.graphiti_url)
            except ImportError:
                self._graphiti = None
        return self._graphiti

    @property
    def memgraph(self):
        """Get or create Memgraph connection for static graph."""
        if self._memgraph is None:
            try:
                from neo4j import GraphDatabase
                self._memgraph = GraphDatabase.driver(self.memgraph_url)
            except ImportError:
                self._memgraph = None
        return self._memgraph

    def close(self):
        """Close connections."""
        if self._memgraph:
            self._memgraph.close()
            self._memgraph = None

    # --- Temporal Graph (Graphiti) ---

    async def add_episode(
        self,
        content: str,
        source: str,
        source_type: str,
        metadata: dict | None = None,
    ) -> dict:
        """Add an episode to the temporal knowledge graph."""
        try:
            if not self.graphiti:
                return {"success": False, "error": "Graphiti not available"}

            episode = await self.graphiti.add_episode(
                content=content,
                source=source,
                source_type=source_type,
                metadata=metadata or {},
            )
            return {
                "success": True,
                "episode_id": episode.id,
                "entities_extracted": len(episode.entities),
                "relations_extracted": len(episode.relations),
            }
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def temporal_search(
        self,
        query: str,
        reference_time: datetime | None = None,
        limit: int = 10,
    ) -> list[dict]:
        """Search with optional temporal context."""
        try:
            if not self.graphiti:
                return []

            results = await self.graphiti.search(
                query=query,
                reference_time=reference_time,
                limit=limit,
            )
            return [
                {
                    "content": r.content,
                    "source": r.source,
                    "valid_at": str(r.valid_at) if r.valid_at else None,
                    "score": r.score,
                    "entities": [e.name for e in r.entities[:5]],
                }
                for r in results
            ]
        except Exception:
            return []

    async def get_entity_history(
        self,
        entity_name: str,
        entity_type: str | None = None,
    ) -> list[dict]:
        """Get temporal history of an entity."""
        try:
            if not self.graphiti:
                return []

            history = await self.graphiti.get_entity_history(
                name=entity_name,
                entity_type=entity_type,
            )
            return [
                {
                    "content": h.content,
                    "valid_at": str(h.valid_at) if h.valid_at else None,
                    "invalid_at": str(h.invalid_at) if h.invalid_at else None,
                    "source": h.source,
                }
                for h in history
            ]
        except Exception:
            return []

    # --- Static Graph (Memgraph/Cognee) ---

    async def query_graph(
        self,
        cypher_query: str,
        parameters: dict | None = None,
    ) -> list[dict]:
        """Execute a Cypher query on the static graph."""
        try:
            if not self.memgraph:
                return []

            with self.memgraph.session() as session:
                result = session.run(cypher_query, parameters or {})
                return [dict(record) for record in result]
        except Exception:
            return []

    async def get_protocol_relationships(
        self,
        protocol: str,
        depth: int = 2,
    ) -> dict:
        """Get relationships for a protocol."""
        query = """
        MATCH (p:Protocol {name: $protocol})-[r*1..$depth]-(related)
        RETURN p, r, related
        LIMIT 50
        """
        try:
            results = await self.query_graph(query, {"protocol": protocol, "depth": depth})
            return {
                "protocol": protocol,
                "relationships": results,
                "depth": depth,
            }
        except Exception:
            return {"protocol": protocol, "relationships": [], "depth": depth}

    async def get_token_ecosystem(
        self,
        token_symbol: str,
    ) -> dict:
        """Get ecosystem relationships for a token."""
        query = """
        MATCH (t:Token {symbol: $symbol})-[r]-(related)
        RETURN t, type(r) as relationship, related
        LIMIT 50
        """
        try:
            results = await self.query_graph(query, {"symbol": token_symbol.upper()})
            return {
                "token": token_symbol.upper(),
                "relationships": results,
            }
        except Exception:
            return {"token": token_symbol.upper(), "relationships": []}

    async def find_connected_protocols(
        self,
        protocol: str,
        relationship_type: str | None = None,
    ) -> list[dict]:
        """Find protocols connected to a given protocol."""
        if relationship_type:
            query = """
            MATCH (p1:Protocol {name: $protocol})-[r:$rel_type]-(p2:Protocol)
            RETURN p2.name as protocol, type(r) as relationship, r.since as since
            """
        else:
            query = """
            MATCH (p1:Protocol {name: $protocol})-[r]-(p2:Protocol)
            RETURN p2.name as protocol, type(r) as relationship, r.since as since
            """
        try:
            results = await self.query_graph(query, {"protocol": protocol, "rel_type": relationship_type})
            return results
        except Exception:
            return []

    # --- Hybrid Search ---

    async def hybrid_search(
        self,
        query: str,
        reference_time: datetime | None = None,
        include_temporal: bool = True,
        include_static: bool = True,
        limit: int = 10,
    ) -> dict:
        """Perform hybrid search across both graphs."""
        results = {
            "query": query,
            "temporal_results": [],
            "static_results": [],
            "reference_time": str(reference_time) if reference_time else None,
        }

        if include_temporal:
            results["temporal_results"] = await self.temporal_search(
                query=query,
                reference_time=reference_time,
                limit=limit,
            )

        if include_static:
            static_query = """
            CALL text_search.search('$query', 'entities') YIELD node, score
            RETURN node, score
            ORDER BY score DESC
            LIMIT $limit
            """
            try:
                static = await self.query_graph(static_query, {"query": query, "limit": limit})
                results["static_results"] = static
            except Exception:
                pass

        return results

    # --- Entity Management ---

    async def add_entity(
        self,
        name: str,
        entity_type: str,
        properties: dict,
    ) -> dict:
        """Add an entity to the static graph."""
        query = f"""
        MERGE (e:{entity_type} {{name: $name}})
        SET e += $properties
        RETURN e
        """
        try:
            result = await self.query_graph(query, {"name": name, "properties": properties})
            return {"success": True, "entity": result[0] if result else None}
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def add_relationship(
        self,
        from_entity: str,
        from_type: str,
        to_entity: str,
        to_type: str,
        relationship_type: str,
        properties: dict | None = None,
    ) -> dict:
        """Add a relationship between entities."""
        query = f"""
        MATCH (a:{from_type} {{name: $from_name}})
        MATCH (b:{to_type} {{name: $to_name}})
        MERGE (a)-[r:{relationship_type}]->(b)
        SET r += $properties
        RETURN a, r, b
        """
        try:
            result = await self.query_graph(
                query,
                {
                    "from_name": from_entity,
                    "to_name": to_entity,
                    "properties": properties or {},
                },
            )
            return {"success": True, "relationship": result[0] if result else None}
        except Exception as e:
            return {"success": False, "error": str(e)}

    async def get_graph_stats(self) -> dict:
        """Get statistics about the knowledge graph."""
        try:
            node_count = await self.query_graph("MATCH (n) RETURN count(n) as count")
            edge_count = await self.query_graph("MATCH ()-[r]->() RETURN count(r) as count")
            labels = await self.query_graph("CALL db.labels() YIELD label RETURN label")

            return {
                "nodes": node_count[0]["count"] if node_count else 0,
                "edges": edge_count[0]["count"] if edge_count else 0,
                "labels": [l["label"] for l in labels] if labels else [],
            }
        except Exception:
            return {"nodes": 0, "edges": 0, "labels": []}
