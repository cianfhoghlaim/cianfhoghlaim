"""
FalkorDB Caching Patterns for Curriculum Graph.

Implements caching strategies for:
- Frequently accessed curriculum hierarchy paths
- Session-specific graph subsets
- Query result caching with TTL
- Interaction hot path optimization

Design Principles:
- FalkorDB for hot-path queries and session state
- Memgraph remains source of truth for full knowledge graph
- Cache-aside pattern with automatic invalidation
- Support for cache warming on popular queries
"""

import hashlib
import json
import logging
from collections.abc import Callable
from dataclasses import dataclass, field
from datetime import datetime
from functools import wraps
from typing import Any, TypeVar

logger = logging.getLogger(__name__)

T = TypeVar("T")


# ============================================================================
# Cache Configuration
# ============================================================================


@dataclass
class CacheConfig:
    """Configuration for graph caching behavior."""

    # TTL settings (in seconds)
    curriculum_hierarchy_ttl: int = 3600  # 1 hour for static curriculum
    query_result_ttl: int = 300  # 5 minutes for query results
    session_graph_ttl: int = 1800  # 30 minutes for session data
    hot_path_ttl: int = 900  # 15 minutes for hot paths

    # Size limits
    max_cached_queries: int = 1000
    max_session_nodes: int = 500
    max_hot_paths: int = 100

    # Feature flags
    enable_query_cache: bool = True
    enable_session_graphs: bool = True
    enable_hot_path_optimization: bool = True
    enable_cache_warming: bool = True


DEFAULT_CONFIG = CacheConfig()


# ============================================================================
# Cache Key Generators
# ============================================================================


def generate_query_key(query: str, params: dict | None = None) -> str:
    """Generate a unique cache key for a Cypher query."""
    normalized_query = " ".join(query.split()).lower()
    params_str = json.dumps(params or {}, sort_keys=True)
    content = f"{normalized_query}:{params_str}"
    return f"query:{hashlib.sha256(content.encode()).hexdigest()[:16]}"


def generate_path_key(start_id: str, end_id: str, max_depth: int = 3) -> str:
    """Generate a cache key for a graph path."""
    return f"path:{start_id}:{end_id}:{max_depth}"


def generate_hierarchy_key(
    subject_code: str | None = None,
    education_level: str | None = None,
) -> str:
    """Generate a cache key for curriculum hierarchy."""
    parts = ["hierarchy"]
    if subject_code:
        parts.append(subject_code)
    if education_level:
        parts.append(education_level)
    return ":".join(parts)


def generate_session_key(session_id: str) -> str:
    """Generate a cache key for session graph."""
    return f"session:{session_id}"


# ============================================================================
# Graph Cache Manager
# ============================================================================


@dataclass
class CacheEntry:
    """A cached value with metadata."""

    key: str
    value: Any
    created_at: datetime
    ttl_seconds: int
    hits: int = 0
    last_accessed: datetime = field(default_factory=datetime.utcnow)

    @property
    def is_expired(self) -> bool:
        """Check if this entry has expired."""
        age = (datetime.utcnow() - self.created_at).total_seconds()
        return age > self.ttl_seconds

    def touch(self) -> None:
        """Update access metadata."""
        self.hits += 1
        self.last_accessed = datetime.utcnow()


class GraphCacheManager:
    """
    Manages caching for graph queries using FalkorDB.

    Implements multiple caching strategies:
    1. Query Result Cache: Cache Cypher query results
    2. Hierarchy Cache: Pre-computed curriculum hierarchies
    3. Session Graphs: User-specific graph subsets
    4. Hot Path Cache: Frequently traversed paths
    """

    def __init__(self, config: CacheConfig = DEFAULT_CONFIG):
        self.config = config
        self._falkordb = None
        self._local_cache: dict[str, CacheEntry] = {}

    def _get_client(self):
        """Get FalkorDB client lazily."""
        if self._falkordb is None:
            from .falkordb_client import FalkorDBClient

            self._falkordb = FalkorDBClient()
        return self._falkordb

    # =========================================================================
    # Core Cache Operations
    # =========================================================================

    def get(self, key: str) -> Any | None:
        """Get a cached value by key."""
        # Check local cache first
        if key in self._local_cache:
            entry = self._local_cache[key]
            if not entry.is_expired:
                entry.touch()
                return entry.value
            else:
                del self._local_cache[key]

        # Check FalkorDB cache
        try:
            client = self._get_client()
            cached = client.get_cached_result(key)
            if cached:
                # Restore to local cache
                self._local_cache[key] = CacheEntry(
                    key=key,
                    value=cached,
                    created_at=datetime.utcnow(),
                    ttl_seconds=self.config.query_result_ttl,
                )
                return cached
        except Exception as e:
            logger.warning(f"Failed to get from FalkorDB cache: {e}")

        return None

    def set(
        self,
        key: str,
        value: Any,
        ttl: int | None = None,
    ) -> None:
        """Set a cached value."""
        ttl = ttl or self.config.query_result_ttl

        # Store locally
        self._local_cache[key] = CacheEntry(
            key=key,
            value=value,
            created_at=datetime.utcnow(),
            ttl_seconds=ttl,
        )

        # Store in FalkorDB
        try:
            client = self._get_client()
            client.cache_query_result(key, value, ttl=ttl)
        except Exception as e:
            logger.warning(f"Failed to set in FalkorDB cache: {e}")

        # Evict if over limit
        self._evict_if_needed()

    def delete(self, key: str) -> bool:
        """Delete a cached value."""
        deleted = False

        if key in self._local_cache:
            del self._local_cache[key]
            deleted = True

        try:
            client = self._get_client()
            client.invalidate_cache(key)
            deleted = True
        except Exception as e:
            logger.warning(f"Failed to delete from FalkorDB cache: {e}")

        return deleted

    def invalidate_pattern(self, pattern: str) -> int:
        """Invalidate all keys matching a pattern."""
        count = 0

        # Local cache
        keys_to_delete = [k for k in self._local_cache if pattern in k]
        for key in keys_to_delete:
            del self._local_cache[key]
            count += 1

        # FalkorDB - attempt pattern invalidation
        try:
            client = self._get_client()
            # FalkorDB doesn't have pattern delete, so we track and delete
            for key in keys_to_delete:
                client.invalidate_cache(key)
        except Exception as e:
            logger.warning(f"Failed to invalidate pattern in FalkorDB: {e}")

        return count

    def _evict_if_needed(self) -> None:
        """Evict entries if over the limit using LRU."""
        if len(self._local_cache) <= self.config.max_cached_queries:
            return

        # Sort by last_accessed and remove oldest
        sorted_entries = sorted(
            self._local_cache.items(),
            key=lambda x: x[1].last_accessed,
        )

        to_remove = len(self._local_cache) - self.config.max_cached_queries
        for key, _ in sorted_entries[:to_remove]:
            del self._local_cache[key]

    # =========================================================================
    # Query Cache
    # =========================================================================

    def cached_query(
        self,
        query: str,
        executor: Callable[[], T],
        params: dict | None = None,
        ttl: int | None = None,
    ) -> T:
        """Execute a query with caching."""
        if not self.config.enable_query_cache:
            return executor()

        key = generate_query_key(query, params)
        cached = self.get(key)

        if cached is not None:
            logger.debug(f"Cache hit for query: {key}")
            return cached

        logger.debug(f"Cache miss for query: {key}")
        result = executor()

        self.set(key, result, ttl or self.config.query_result_ttl)
        return result

    # =========================================================================
    # Hierarchy Cache
    # =========================================================================

    def get_cached_hierarchy(
        self,
        subject_code: str | None = None,
        education_level: str | None = None,
    ) -> dict | None:
        """Get cached curriculum hierarchy."""
        key = generate_hierarchy_key(subject_code, education_level)
        return self.get(key)

    def cache_hierarchy(
        self,
        hierarchy: dict,
        subject_code: str | None = None,
        education_level: str | None = None,
    ) -> None:
        """Cache a curriculum hierarchy."""
        key = generate_hierarchy_key(subject_code, education_level)
        self.set(key, hierarchy, self.config.curriculum_hierarchy_ttl)

    def invalidate_hierarchy(
        self,
        subject_code: str | None = None,
    ) -> None:
        """Invalidate cached hierarchy for a subject."""
        if subject_code:
            self.invalidate_pattern(f"hierarchy:{subject_code}")
        else:
            self.invalidate_pattern("hierarchy:")

    # =========================================================================
    # Session Graph Cache
    # =========================================================================

    def get_session_graph(self, session_id: str) -> dict | None:
        """Get the cached session graph."""
        if not self.config.enable_session_graphs:
            return None

        key = generate_session_key(session_id)
        return self.get(key)

    def update_session_graph(
        self,
        session_id: str,
        nodes: list[dict],
        relationships: list[dict],
    ) -> None:
        """Update session graph with new nodes and relationships."""
        if not self.config.enable_session_graphs:
            return

        key = generate_session_key(session_id)
        existing = self.get(key) or {"nodes": [], "relationships": []}

        # Merge nodes (deduplicate by id)
        existing_node_ids = {n["id"] for n in existing["nodes"]}
        for node in nodes:
            if node["id"] not in existing_node_ids:
                existing["nodes"].append(node)
                existing_node_ids.add(node["id"])

        # Limit session graph size
        if len(existing["nodes"]) > self.config.max_session_nodes:
            # Keep most recently added
            existing["nodes"] = existing["nodes"][-self.config.max_session_nodes :]

        # Merge relationships
        existing_rel_keys = {
            (r["source"], r["type"], r["target"])
            for r in existing["relationships"]
        }
        for rel in relationships:
            rel_key = (rel["source"], rel["type"], rel["target"])
            if rel_key not in existing_rel_keys:
                existing["relationships"].append(rel)

        self.set(key, existing, self.config.session_graph_ttl)

    def clear_session_graph(self, session_id: str) -> None:
        """Clear a session's cached graph."""
        key = generate_session_key(session_id)
        self.delete(key)

    # =========================================================================
    # Hot Path Cache
    # =========================================================================

    def get_cached_path(
        self,
        start_id: str,
        end_id: str,
        max_depth: int = 3,
    ) -> list[dict] | None:
        """Get a cached path between two nodes."""
        if not self.config.enable_hot_path_optimization:
            return None

        key = generate_path_key(start_id, end_id, max_depth)
        return self.get(key)

    def cache_path(
        self,
        start_id: str,
        end_id: str,
        path: list[dict],
        max_depth: int = 3,
    ) -> None:
        """Cache a path between two nodes."""
        if not self.config.enable_hot_path_optimization:
            return

        key = generate_path_key(start_id, end_id, max_depth)
        self.set(key, path, self.config.hot_path_ttl)

    # =========================================================================
    # Cache Statistics
    # =========================================================================

    def get_stats(self) -> dict:
        """Get cache statistics."""
        total = len(self._local_cache)
        expired = sum(1 for e in self._local_cache.values() if e.is_expired)
        total_hits = sum(e.hits for e in self._local_cache.values())

        return {
            "total_entries": total,
            "expired_entries": expired,
            "active_entries": total - expired,
            "total_hits": total_hits,
            "avg_hits_per_entry": total_hits / total if total > 0 else 0,
            "config": {
                "query_cache_enabled": self.config.enable_query_cache,
                "session_graphs_enabled": self.config.enable_session_graphs,
                "hot_path_enabled": self.config.enable_hot_path_optimization,
            },
        }

    def clear_all(self) -> int:
        """Clear all cached data."""
        count = len(self._local_cache)
        self._local_cache.clear()
        return count


# ============================================================================
# Decorator for Cached Queries
# ============================================================================


def cached_graph_query(
    ttl: int | None = None,
    key_prefix: str = "",
):
    """
    Decorator for caching graph query results.

    Usage:
        @cached_graph_query(ttl=300)
        def get_subject_hierarchy(subject_code: str) -> dict:
            # expensive query
            return result
    """

    def decorator(func: Callable[..., T]) -> Callable[..., T]:
        @wraps(func)
        def wrapper(*args, **kwargs) -> T:
            # Build cache key from function name and arguments
            func_name = func.__name__
            args_str = json.dumps(
                {"args": [str(a) for a in args], "kwargs": kwargs},
                sort_keys=True,
            )
            key = f"{key_prefix}{func_name}:{hashlib.sha256(args_str.encode()).hexdigest()[:12]}"

            manager = get_cache_manager()
            cached = manager.get(key)

            if cached is not None:
                return cached

            result = func(*args, **kwargs)
            manager.set(key, result, ttl)
            return result

        return wrapper

    return decorator


# ============================================================================
# Cache Warming
# ============================================================================


class CacheWarmer:
    """
    Pre-populates cache with frequently accessed data.

    Run during low-traffic periods or on startup.
    """

    def __init__(self, cache_manager: GraphCacheManager):
        self.cache = cache_manager
        self._memgraph = None

    def _get_memgraph(self):
        """Get Memgraph client lazily."""
        if self._memgraph is None:
            from .memgraph_client import CurriculumGraph

            self._memgraph = CurriculumGraph()
        return self._memgraph

    def warm_curriculum_hierarchies(
        self,
        education_levels: list[str] | None = None,
    ) -> int:
        """Pre-cache curriculum hierarchies."""
        if not self.cache.config.enable_cache_warming:
            return 0

        levels = education_levels or ["primary", "junior_cycle", "senior_cycle"]
        count = 0

        graph = self._get_memgraph()

        for level in levels:
            try:
                subjects = graph.get_subjects_by_level(level)

                for subject in subjects:
                    hierarchy = graph.get_subject_hierarchy(subject["code"])
                    self.cache.cache_hierarchy(
                        hierarchy,
                        subject_code=subject["code"],
                        education_level=level,
                    )
                    count += 1

                logger.info(f"Warmed {len(subjects)} hierarchies for {level}")
            except Exception as e:
                logger.error(f"Failed to warm hierarchies for {level}: {e}")

        return count

    def warm_popular_paths(
        self,
        popular_pairs: list[tuple[str, str]],
    ) -> int:
        """Pre-cache frequently traversed paths."""
        if not self.cache.config.enable_cache_warming:
            return 0

        count = 0
        graph = self._get_memgraph()

        for start_id, end_id in popular_pairs:
            try:
                path = graph.find_path(start_id, end_id, max_depth=3)
                if path:
                    self.cache.cache_path(start_id, end_id, path)
                    count += 1
            except Exception as e:
                logger.warning(f"Failed to warm path {start_id} -> {end_id}: {e}")

        logger.info(f"Warmed {count} paths")
        return count


# ============================================================================
# Singleton Access
# ============================================================================

_cache_manager: GraphCacheManager | None = None


def get_cache_manager(config: CacheConfig | None = None) -> GraphCacheManager:
    """Get the global cache manager instance."""
    global _cache_manager
    if _cache_manager is None:
        _cache_manager = GraphCacheManager(config or DEFAULT_CONFIG)
    return _cache_manager


def get_cache_warmer() -> CacheWarmer:
    """Get a cache warmer instance."""
    return CacheWarmer(get_cache_manager())
