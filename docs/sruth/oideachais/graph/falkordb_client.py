"""
FalkorDB Graph Cache Client.

Redis-based graph database for:
- Hot path queries (frequent lookups)
- Session state caching
- Real-time interaction graphs
- Lower latency for simple traversals

Complements Memgraph (primary knowledge graph) with:
- Faster read access for cached data
- Session-scoped temporary graphs
- Query result caching
"""

import json
import logging
from contextlib import contextmanager
from dataclasses import dataclass
from datetime import datetime, timedelta
from typing import Any, Generator

from ..storage.config import FalkorDBConfig, get_config

logger = logging.getLogger(__name__)


@dataclass
class CachedQuery:
    """Cached query result."""

    query_hash: str
    result: list[dict]
    created_at: datetime
    ttl_seconds: int
    hit_count: int = 0


class FalkorDBClient:
    """
    Client for FalkorDB (Redis Graph) operations.

    Uses the FalkorDB Python client for graph operations
    on top of Redis.
    """

    def __init__(self, config: FalkorDBConfig | None = None):
        self.config = config or get_config().falkordb
        self._redis = None
        self._graph = None

    def _get_connection(self):
        """Get or create Redis connection."""
        if self._redis is None:
            try:
                from falkordb import FalkorDB
            except ImportError:
                try:
                    import redis
                    from redis.commands.graph import Graph
                except ImportError:
                    raise ImportError(
                        "Neither falkordb nor redis[graph] is installed. "
                        "Run: pip install falkordb or pip install redis[graph]"
                    )

            # Parse Redis URL
            url = self.config.url
            if url.startswith("redis://"):
                from urllib.parse import urlparse

                parsed = urlparse(url)
                host = parsed.hostname or "localhost"
                port = parsed.port or 6379
                password = parsed.password
            else:
                host = "localhost"
                port = 6379
                password = None

            try:
                # Try FalkorDB client first
                from falkordb import FalkorDB

                self._redis = FalkorDB(host=host, port=port, password=password)
                self._graph = self._redis.select_graph(self.config.graph_name)
            except ImportError:
                # Fall back to redis-py with RedisGraph
                import redis

                self._redis = redis.Redis(host=host, port=port, password=password)
                self._graph = self._redis.graph(self.config.graph_name)

            logger.info(f"Connected to FalkorDB at {host}:{port}")

        return self._graph

    @property
    def graph(self):
        """Get the graph connection."""
        return self._get_connection()

    @property
    def redis(self):
        """Get the raw Redis connection."""
        if self._redis is None:
            self._get_connection()
        return self._redis

    def close(self) -> None:
        """Close connections."""
        if hasattr(self._redis, "close"):
            self._redis.close()
        self._redis = None
        self._graph = None

    def health_check(self) -> bool:
        """Check FalkorDB connectivity."""
        try:
            self.graph.query("RETURN 1")
            return True
        except Exception as e:
            logger.error(f"FalkorDB health check failed: {e}")
            return False

    # =========================================================================
    # Generic Graph Operations
    # =========================================================================

    def query(self, cypher: str, params: dict | None = None) -> list[dict]:
        """Execute a Cypher query and return results."""
        result = self.graph.query(cypher, params or {})

        # Convert result to list of dicts
        records = []
        if result.result_set:
            headers = result.header
            for row in result.result_set:
                record = {}
                for i, value in enumerate(row):
                    key = headers[i][1] if isinstance(headers[i], tuple) else headers[i]
                    # Handle Node and Edge types
                    if hasattr(value, "properties"):
                        record[key] = dict(value.properties)
                    else:
                        record[key] = value
                records.append(record)

        return records

    def execute(self, cypher: str, params: dict | None = None) -> dict:
        """Execute a write query and return stats."""
        result = self.graph.query(cypher, params or {})

        return {
            "nodes_created": result.nodes_created,
            "relationships_created": result.relationships_created,
            "properties_set": result.properties_set,
            "nodes_deleted": result.nodes_deleted,
            "relationships_deleted": result.relationships_deleted,
        }

    # =========================================================================
    # Cache Operations
    # =========================================================================

    def cache_query_result(
        self,
        cache_key: str,
        result: list[dict],
        ttl_seconds: int = 300,
    ) -> None:
        """Cache a query result in Redis."""
        import hashlib

        cache_data = {
            "result": result,
            "created_at": datetime.utcnow().isoformat(),
            "ttl": ttl_seconds,
        }

        # Use raw Redis for simple key-value caching
        self.redis.setex(
            f"query_cache:{cache_key}",
            ttl_seconds,
            json.dumps(cache_data),
        )

    def get_cached_query(self, cache_key: str) -> list[dict] | None:
        """Get a cached query result."""
        data = self.redis.get(f"query_cache:{cache_key}")
        if data:
            parsed = json.loads(data)
            return parsed.get("result")
        return None

    def invalidate_cache(self, pattern: str = "*") -> int:
        """Invalidate cached queries matching pattern."""
        keys = self.redis.keys(f"query_cache:{pattern}")
        if keys:
            return self.redis.delete(*keys)
        return 0

    # =========================================================================
    # Session Graph (Temporary User Graphs)
    # =========================================================================

    def create_session_graph(self, session_id: str) -> str:
        """Create a temporary graph for a user session."""
        graph_name = f"session_{session_id}"

        # FalkorDB allows multiple graphs per Redis instance
        try:
            from falkordb import FalkorDB

            session_graph = self._redis.select_graph(graph_name)
        except (ImportError, AttributeError):
            session_graph = self._redis.graph(graph_name)

        # Initialize with session metadata
        session_graph.query(
            """
            CREATE (:Session {
                id: $session_id,
                created_at: $created_at
            })
            """,
            {
                "session_id": session_id,
                "created_at": datetime.utcnow().isoformat(),
            },
        )

        # Set TTL on the graph (24 hours)
        self.redis.expire(graph_name, 86400)

        return graph_name

    def add_to_session_graph(
        self,
        session_id: str,
        node_type: str,
        node_id: str,
        properties: dict,
    ) -> None:
        """Add a node to a session graph."""
        graph_name = f"session_{session_id}"

        try:
            from falkordb import FalkorDB

            session_graph = self._redis.select_graph(graph_name)
        except (ImportError, AttributeError):
            session_graph = self._redis.graph(graph_name)

        # Merge node
        props_str = ", ".join(f"{k}: ${k}" for k in properties.keys())
        query = f"""
            MERGE (n:{node_type} {{id: $node_id}})
            SET n += {{{props_str}}}
            RETURN n
        """

        session_graph.query(query, {"node_id": node_id, **properties})

    def delete_session_graph(self, session_id: str) -> None:
        """Delete a session graph."""
        graph_name = f"session_{session_id}"
        self.redis.delete(graph_name)

    # =========================================================================
    # Curriculum Cache Patterns
    # =========================================================================

    def cache_curriculum_tree(
        self,
        subject_code: str,
        tree_data: dict,
        ttl_seconds: int = 3600,
    ) -> None:
        """Cache a curriculum tree for fast access."""
        self.cache_query_result(
            f"curriculum_tree:{subject_code}",
            [tree_data],
            ttl_seconds,
        )

    def get_curriculum_tree(self, subject_code: str) -> dict | None:
        """Get cached curriculum tree."""
        result = self.get_cached_query(f"curriculum_tree:{subject_code}")
        return result[0] if result else None

    def cache_learning_outcomes(
        self,
        subject_code: str,
        outcomes: list[dict],
        ttl_seconds: int = 3600,
    ) -> None:
        """Cache learning outcomes for a subject."""
        # Store in graph for relationship queries
        for outcome in outcomes:
            self.execute(
                """
                MERGE (lo:LearningOutcome {code: $code})
                SET lo.description = $description,
                    lo.difficulty = $difficulty,
                    lo.subject = $subject,
                    lo.cached_at = $cached_at
                """,
                {
                    "code": outcome["code"],
                    "description": outcome.get("description_en", ""),
                    "difficulty": outcome.get("difficulty_level", ""),
                    "subject": subject_code,
                    "cached_at": datetime.utcnow().isoformat(),
                },
            )

        # Also store list in Redis for fast list access
        self.cache_query_result(
            f"outcomes:{subject_code}",
            outcomes,
            ttl_seconds,
        )

    def get_cached_outcomes(self, subject_code: str) -> list[dict] | None:
        """Get cached learning outcomes."""
        return self.get_cached_query(f"outcomes:{subject_code}")

    def cache_related_outcomes(
        self,
        outcome_code: str,
        related: list[dict],
        ttl_seconds: int = 1800,
    ) -> None:
        """Cache related outcomes for an outcome."""
        self.cache_query_result(
            f"related:{outcome_code}",
            related,
            ttl_seconds,
        )

    def get_related_outcomes(self, outcome_code: str) -> list[dict] | None:
        """Get cached related outcomes."""
        return self.get_cached_query(f"related:{outcome_code}")

    # =========================================================================
    # Search Result Caching
    # =========================================================================

    def cache_search_results(
        self,
        query_hash: str,
        results: list[dict],
        ttl_seconds: int = 600,
    ) -> None:
        """Cache search results."""
        self.cache_query_result(f"search:{query_hash}", results, ttl_seconds)

    def get_cached_search(self, query_hash: str) -> list[dict] | None:
        """Get cached search results."""
        return self.get_cached_query(f"search:{query_hash}")

    # =========================================================================
    # Real-time Interaction Graph
    # =========================================================================

    def record_interaction(
        self,
        user_id: str,
        document_id: str,
        interaction_type: str,
        metadata: dict | None = None,
    ) -> None:
        """Record a user-document interaction."""
        self.execute(
            """
            MERGE (u:User {id: $user_id})
            MERGE (d:Document {id: $document_id})
            CREATE (u)-[r:INTERACTED {
                type: $interaction_type,
                timestamp: $timestamp,
                metadata: $metadata
            }]->(d)
            """,
            {
                "user_id": user_id,
                "document_id": document_id,
                "interaction_type": interaction_type,
                "timestamp": datetime.utcnow().isoformat(),
                "metadata": json.dumps(metadata or {}),
            },
        )

    def get_user_interactions(
        self,
        user_id: str,
        limit: int = 10,
    ) -> list[dict]:
        """Get recent user interactions."""
        return self.query(
            """
            MATCH (u:User {id: $user_id})-[r:INTERACTED]->(d:Document)
            RETURN d.id as document_id, r.type as interaction_type, r.timestamp as timestamp
            ORDER BY r.timestamp DESC
            LIMIT $limit
            """,
            {"user_id": user_id, "limit": limit},
        )

    def get_similar_users(
        self,
        user_id: str,
        min_common_docs: int = 3,
    ) -> list[dict]:
        """Find users with similar interaction patterns."""
        return self.query(
            """
            MATCH (u1:User {id: $user_id})-[:INTERACTED]->(d:Document)<-[:INTERACTED]-(u2:User)
            WHERE u1 <> u2
            WITH u2, count(DISTINCT d) as common_docs
            WHERE common_docs >= $min_common
            RETURN u2.id as user_id, common_docs
            ORDER BY common_docs DESC
            LIMIT 10
            """,
            {"user_id": user_id, "min_common": min_common_docs},
        )

    # =========================================================================
    # PDF Document Caching
    # =========================================================================

    def cache_pdf_outcomes(
        self,
        document_id: str,
        outcome_codes: list[str],
        ttl_seconds: int = 3600,
    ) -> None:
        """
        Cache PDF-to-learning-outcome mappings.

        Args:
            document_id: PDF document ID
            outcome_codes: Learning outcome codes the PDF addresses
            ttl_seconds: Cache TTL (default 1 hour)
        """
        cache_key = f"pdf_outcomes:{document_id}"
        self.cache_query_result(
            cache_key=cache_key,
            result=[{"outcome_code": code} for code in outcome_codes],
            ttl_seconds=ttl_seconds,
        )

    def get_cached_pdf_outcomes(self, document_id: str) -> list[str] | None:
        """Get cached outcome codes for a PDF document."""
        result = self.get_cached_query(f"pdf_outcomes:{document_id}")
        if result:
            return [r["outcome_code"] for r in result]
        return None

    def cache_pdf_search_results(
        self,
        query_hash: str,
        subject: str,
        results: list[dict],
        ttl_seconds: int = 600,
    ) -> None:
        """
        Cache PDF vector search results.

        Args:
            query_hash: Hash of the search query
            subject: Subject filter used
            results: PDF search results from LanceDB
            ttl_seconds: Cache TTL (default 10 minutes)
        """
        cache_key = f"pdf_search:{subject}:{query_hash}"
        self.cache_query_result(
            cache_key=cache_key,
            result=results,
            ttl_seconds=ttl_seconds,
        )

    def get_cached_pdf_search(
        self,
        query_hash: str,
        subject: str,
    ) -> list[dict] | None:
        """Get cached PDF search results."""
        return self.get_cached_query(f"pdf_search:{subject}:{query_hash}")

    def cache_pdf_metadata(
        self,
        document_id: str,
        metadata: dict,
        ttl_seconds: int = 3600,
    ) -> None:
        """
        Cache PDF document metadata for fast lookup.

        Args:
            document_id: PDF document ID
            metadata: Document metadata dict
            ttl_seconds: Cache TTL (default 1 hour)
        """
        cache_key = f"pdf_meta:{document_id}"
        self.cache_query_result(
            cache_key=cache_key,
            result=[metadata],
            ttl_seconds=ttl_seconds,
        )

    def get_cached_pdf_metadata(self, document_id: str) -> dict | None:
        """Get cached PDF metadata."""
        result = self.get_cached_query(f"pdf_meta:{document_id}")
        if result and len(result) > 0:
            return result[0]
        return None


class GraphCache:
    """
    High-level caching interface for curriculum graph data.

    Provides automatic cache management and fallback to Memgraph.
    """

    def __init__(self, config: FalkorDBConfig | None = None):
        self.client = FalkorDBClient(config)

    def close(self) -> None:
        """Close the client."""
        self.client.close()

    def get_or_fetch_curriculum_tree(
        self,
        subject_code: str,
        fetch_fn,
    ) -> dict:
        """Get curriculum tree from cache or fetch from source."""
        cached = self.client.get_curriculum_tree(subject_code)
        if cached:
            logger.debug(f"Cache hit for curriculum tree: {subject_code}")
            return cached

        logger.debug(f"Cache miss for curriculum tree: {subject_code}")
        tree = fetch_fn(subject_code)
        self.client.cache_curriculum_tree(subject_code, tree)
        return tree

    def get_or_fetch_related(
        self,
        outcome_code: str,
        fetch_fn,
    ) -> list[dict]:
        """Get related outcomes from cache or fetch."""
        cached = self.client.get_related_outcomes(outcome_code)
        if cached:
            return cached

        related = fetch_fn(outcome_code)
        self.client.cache_related_outcomes(outcome_code, related)
        return related

    def get_or_fetch_search(
        self,
        query_hash: str,
        search_fn,
    ) -> list[dict]:
        """Get search results from cache or execute search."""
        cached = self.client.get_cached_search(query_hash)
        if cached:
            return cached

        results = search_fn()
        self.client.cache_search_results(query_hash, results)
        return results


# Singleton instance
_graph_cache: GraphCache | None = None


def get_graph_cache() -> GraphCache:
    """Get the graph cache singleton."""
    global _graph_cache
    if _graph_cache is None:
        _graph_cache = GraphCache()
    return _graph_cache
