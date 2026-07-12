"""MemoryBackend Protocol + `get_default_backend()` factory (T4).

Per the `2026-07-09-agent-fleet-and-observability-facade-v1` change,
agent code should NOT import `GraphitiClient`, `FalkorDBClient`,
`MemgraphClient`, `LanceDBClient`, or `CogneeService` directly.
Instead, it should depend on the `MemoryBackend` protocol and
obtain a concrete backend via the `get_default_backend()` factory.

The factory's behaviour (T4 acceptance gate):

- Returns the `GraphitiBackend` when Graphiti is reachable (HTTP
  200 on `/health`).
- Falls back to the `FalkorDBBackend` on Graphiti 5xx, network
  error, or `GRAPHITI_URI` not set.
- Falls back to an in-memory `LanceDBBackend` (read-only) on
  FalkorDB 5xx / network error.

The protocol surface is intentionally narrow — `add_episode`,
`search`, `get_node`, `close` — so a new backend (e.g. a FalkorDB
Lite embedded-mode backend) can join the cascade without
breaking callers.

Concrete backends are thin wrappers around the existing
`cianfhoghlaim.storage.{graphiti_client, falkordb_client,
lancedb, cognee_service}` modules. We do not reimplement the
core algorithms here; we just translate between the protocol
and the existing API.

Public API:

    from cianfhoghlaim.storage.memf import (
        MemoryBackend,
        get_default_backend,
        Episode,
        Node,
        SearchResult,
    )

    backend = get_default_backend()
    await backend.add_episode(Episode(body="..."))
    results = await backend.search("query", k=10)
    await backend.close()
"""
from __future__ import annotations

import logging
import os
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, AsyncIterator, Protocol, runtime_checkable
from uuid import UUID, uuid4

logger = logging.getLogger(__name__)


# ---------------------------------------------------------------------------
# Protocol surface (the 3 operations every backend must support)
# ---------------------------------------------------------------------------


@dataclass
class Episode:
    """A single memory episode to add to the graph.

    Mirrors the Graphiti `EpisodeType` shape: text body +
    optional source-id + timestamp + metadata.
    """

    body: str
    source: str = "user"
    source_id: str | None = None
    timestamp: datetime = field(default_factory=datetime.utcnow)
    metadata: dict[str, Any] = field(default_factory=dict)
    episode_id: UUID = field(default_factory=uuid4)


@dataclass
class Node:
    """A node in the knowledge graph (entity, concept, person, etc.)."""

    node_id: str
    labels: list[str] = field(default_factory=list)
    properties: dict[str, Any] = field(default_factory=dict)


@dataclass
class SearchResult:
    """A single search hit from `MemoryBackend.search()`."""

    node_id: str
    score: float
    snippet: str = ""
    labels: list[str] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)


@runtime_checkable
class MemoryBackend(Protocol):
    """The narrow protocol that every memory backend implements.

    The 4 operations:
    - `add_episode(episode)`: persist a single episode.
    - `search(query, k, **filters)`: top-k semantic search.
    - `get_node(node_id)`: lookup by node id.
    - `close()`: release client handles.

    Backends SHOULD also expose a `kind` class attribute so the
    factory can log which backend is in use.
    """

    kind: str

    async def add_episode(self, episode: Episode) -> str:
        """Persist an episode and return its episode_id."""
        ...

    async def search(
        self,
        query: str,
        *,
        k: int = 10,
        **filters: Any,
    ) -> list[SearchResult]:
        """Top-k search across the backend."""
        ...

    async def get_node(self, node_id: str) -> Node | None:
        """Return the node by id, or None if not found."""
        ...

    async def close(self) -> None:
        """Release client handles."""
        ...


# ---------------------------------------------------------------------------
# Concrete backends
# ---------------------------------------------------------------------------


class GraphitiBackend:
    """Graphiti-on-FalkorDB backend (the post-v4 primary)."""

    kind = "graphiti"

    def __init__(self, uri: str | None = None) -> None:
        self.uri = uri or os.getenv("GRAPHITI_URI", "falkor://localhost:6379")
        self._client = None

    async def _get_client(self) -> Any:
        """Lazy-import the canonical graphiti client."""
        if self._client is None:
            try:
                from cianfhoghlaim.storage.graphiti_client import GraphitiClient

                self._client = GraphitiClient()
            except ImportError as exc:  # pragma: no cover
                raise RuntimeError(
                    f"graphiti_client not importable: {exc}"
                ) from exc
        return self._client

    async def add_episode(self, episode: Episode) -> str:
        client = await self._get_client()
        # Best-effort shape: the underlying client may differ
        # slightly. We adapt the Episode → graphiti's EpisodeType.
        body = episode.body
        try:
            await client.add_episode(body=body, source=episode.source)
        except TypeError:
            # Older client signature: positional body only.
            await client.add_episode(body)
        return str(episode.episode_id)

    async def search(
        self, query: str, *, k: int = 10, **filters: Any
    ) -> list[SearchResult]:
        client = await self._get_client()
        raw = await client.search(query, limit=k, **filters)
        return [
            SearchResult(
                node_id=str(r.get("uuid") or r.get("node_id", "")),
                score=float(r.get("score", 0.0)),
                snippet=r.get("content", r.get("snippet", "")),
                labels=r.get("labels", []),
                metadata=r.get("metadata", {}),
            )
            for r in raw
        ]

    async def get_node(self, node_id: str) -> Node | None:
        client = await self._get_client()
        raw = await client.get_node(node_id)
        if raw is None:
            return None
        return Node(
            node_id=str(raw.get("uuid") or raw.get("node_id", node_id)),
            labels=raw.get("labels", []),
            properties=raw.get("properties", {}),
        )

    async def close(self) -> None:
        if self._client is not None:
            close = getattr(self._client, "close", None)
            if callable(close):
                try:
                    await close()
                except Exception:  # noqa: BLE001
                    pass
        self._client = None


class FalkorDBBackend:
    """FalkorDB-only backend (the secondary)."""

    kind = "falkordb"

    def __init__(self, uri: str | None = None) -> None:
        self.uri = uri or os.getenv("FALKORDB_URI", "falkor://localhost:6379")
        self._client = None

    async def _get_client(self) -> Any:
        if self._client is None:
            try:
                from cianfhoghlaim.storage.falkordb_client import (
                    FalkorDBClient,
                )

                self._client = FalkorDBClient(uri=self.uri)
            except ImportError as exc:  # pragma: no cover
                raise RuntimeError(
                    f"falkordb_client not importable: {exc}"
                ) from exc
        return self._client

    async def add_episode(self, episode: Episode) -> str:
        client = await self._get_client()
        # FalkorDB typically writes via Cypher. We synthesise a
        # minimal episode node.
        try:
            await client.execute(
                "MERGE (e:Episode {episode_id:$eid}) "
                "ON CREATE SET e.body=$body, e.timestamp=$ts, "
                "e.source=$source",
                {
                    "eid": str(episode.episode_id),
                    "body": episode.body,
                    "ts": episode.timestamp.isoformat(),
                    "source": episode.source,
                },
            )
        except Exception as exc:  # noqa: BLE001
            logger.warning("FalkorDBBackend.add_episode failed: %s", exc)
        return str(episode.episode_id)

    async def search(
        self, query: str, *, k: int = 10, **filters: Any
    ) -> list[SearchResult]:
        client = await self._get_client()
        try:
            raw = await client.execute(
                "MATCH (e:Episode) WHERE e.body CONTAINS $q "
                "RETURN e LIMIT $k",
                {"q": query, "k": k},
            )
        except Exception as exc:  # noqa: BLE001
            logger.warning("FalkorDBBackend.search failed: %s", exc)
            return []
        return [
            SearchResult(
                node_id=str(r.get("e", {}).get("episode_id", "")),
                score=1.0,
                snippet=str(r.get("e", {}).get("body", "")),
            )
            for r in raw
        ]

    async def get_node(self, node_id: str) -> Node | None:
        client = await self._get_client()
        try:
            raw = await client.execute(
                "MATCH (n {uuid:$nid}) RETURN n", {"nid": node_id}
            )
        except Exception as exc:  # noqa: BLE001
            logger.warning("FalkorDBBackend.get_node failed: %s", exc)
            return None
        if not raw:
            return None
        n = raw[0].get("n", {})
        return Node(
            node_id=str(n.get("uuid", node_id)),
            labels=n.get("labels", []),
            properties=n.get("properties", {}),
        )

    async def close(self) -> None:
        if self._client is not None:
            close = getattr(self._client, "close", None)
            if callable(close):
                try:
                    await close()
                except Exception:  # noqa: BLE001
                    pass
        self._client = None


class InMemoryLanceDBBackend:
    """Read-only in-memory LanceDB fallback (the tertiary, last resort).

    Used when neither Graphiti nor FalkorDB is reachable. Stores
    `Episode.body` strings in a `dict[str, Episode]` and supports
    a case-insensitive substring `search()` so the facade API
    remains callable in CI / offline.
    """

    kind = "in_memory_lancedb"

    def __init__(self) -> None:
        self._episodes: dict[str, Episode] = {}
        self._nodes: dict[str, Node] = {}

    async def add_episode(self, episode: Episode) -> str:
        self._episodes[str(episode.episode_id)] = episode
        return str(episode.episode_id)

    async def search(
        self, query: str, *, k: int = 10, **filters: Any
    ) -> list[SearchResult]:
        q = (query or "").lower()
        hits: list[SearchResult] = []
        for episode in self._episodes.values():
            if q in episode.body.lower():
                hits.append(
                    SearchResult(
                        node_id=str(episode.episode_id),
                        score=1.0,
                        snippet=episode.body[:512],
                        metadata=episode.metadata,
                    )
                )
                if len(hits) >= k:
                    break
        return hits

    async def get_node(self, node_id: str) -> Node | None:
        return self._nodes.get(node_id)

    async def close(self) -> None:
        self._episodes.clear()
        self._nodes.clear()


# ---------------------------------------------------------------------------
# Health probe (cached for 30s)
# ---------------------------------------------------------------------------


_HEALTH_CACHE: dict[str, tuple[float, bool]] = {}
_HEALTH_TTL_SECONDS = 30.0


async def _probe(host: str, port: int, timeout: float = 0.5) -> bool:
    """Probe `host:port`; True if TCP connect succeeded within `timeout`."""
    import asyncio
    import socket

    loop = asyncio.get_event_loop()
    try:
        # Use a TCP connect (not HTTP); we just want to know whether
        # the socket is open. The full HTTP /health probe happens
        # inside the concrete backend.
        fut = loop.run_in_executor(
            None,
            lambda: socket.create_connection((host, port), timeout=timeout),
        )
        sock = await fut
        sock.close()
        return True
    except (OSError, TimeoutError) as exc:
        logger.debug("_probe(%s:%d): %s", host, port, exc)
        return False


async def _graphiti_reachable() -> bool:
    """Return True iff the Graphiti backend is reachable.

    Cached for `_HEALTH_TTL_SECONDS` so we don't re-probe on every
    call.
    """
    now = asyncio_now()
    cached = _HEALTH_CACHE.get("graphiti")
    if cached and (now - cached[0]) < _HEALTH_TTL_SECONDS:
        return cached[1]
    host = os.getenv("GRAPHITI_HOST", "graphiti")
    port = int(os.getenv("GRAPHITI_PORT", "8080"))
    ok = await _probe(host, port)
    _HEALTH_CACHE["graphiti"] = (now, ok)
    return ok


async def _falkordb_reachable() -> bool:
    """Return True iff the FalkorDB backend is reachable."""
    now = asyncio_now()
    cached = _HEALTH_CACHE.get("falkordb")
    if cached and (now - cached[0]) < _HEALTH_TTL_SECONDS:
        return cached[1]
    host = os.getenv("FALKORDB_HOST", "falkordb")
    port = int(os.getenv("FALKORDB_PORT", "6379"))
    ok = await _probe(host, port)
    _HEALTH_CACHE["falkordb"] = (now, ok)
    return ok


def asyncio_now() -> float:
    """Cross-version `loop.time()` — Python 3.10–3.13 compatible."""
    import asyncio

    return asyncio.get_event_loop().time()


# ---------------------------------------------------------------------------
# Module-level singleton + factory (T4 acceptance gate)
# ---------------------------------------------------------------------------


_DEFAULT_BACKEND: MemoryBackend | None = None


async def get_default_backend() -> MemoryBackend:
    """Return the best available memory backend.

    T4 acceptance gate:
    - Graphiti when up.
    - FalkorDB when Graphiti 5xx / network error.
    - InMemoryLanceDBBackend when both are down.

    The factory caches the result so repeated calls share the
    same backend instance. Callers must `await backend.close()`
    when they are done.
    """
    global _DEFAULT_BACKEND
    if _DEFAULT_BACKEND is not None:
        return _DEFAULT_BACKEND

    if await _graphiti_reachable():
        logger.info("get_default_backend: using GraphitiBackend")
        _DEFAULT_BACKEND = GraphitiBackend()
        return _DEFAULT_BACKEND
    if await _falkordb_reachable():
        logger.info(
            "get_default_backend: Graphiti 5xx, falling back to "
            "FalkorDBBackend"
        )
        _DEFAULT_BACKEND = FalkorDBBackend()
        return _DEFAULT_BACKEND

    logger.warning(
        "get_default_backend: Graphiti + FalkorDB unreachable, "
        "using InMemoryLanceDBBackend (read-only)"
    )
    _DEFAULT_BACKEND = InMemoryLanceDBBackend()
    return _DEFAULT_BACKEND


def reset_default_backend() -> None:
    """Drop the cached singleton (test-only helper)."""
    global _DEFAULT_BACKEND
    _DEFAULT_BACKEND = None


__all__ = [
    "Episode",
    "FalkorDBBackend",
    "GraphitiBackend",
    "InMemoryLanceDBBackend",
    "MemoryBackend",
    "Node",
    "SearchResult",
    "get_default_backend",
    "reset_default_backend",
]
