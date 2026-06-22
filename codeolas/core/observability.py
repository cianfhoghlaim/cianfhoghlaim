"""
Códeolas Observability Module.

Provides Langfuse and Datadog instrumentation for code analysis:
- Embedding generation tracking
- Search query monitoring
- Indexing performance metrics
- Cost estimation for API calls

Usage:
    from codeolas.core.observability import (
        trace_embedding, trace_search, trace_index, get_metrics
    )

    @trace_embedding
    def embed_batch(texts: list[str]) -> list[list[float]]:
        ...

    @trace_search
    async def search(query: str) -> list[SearchResult]:
        ...
"""

from __future__ import annotations

import functools
import logging
import os
import time
from contextlib import contextmanager
from dataclasses import dataclass, field
from datetime import datetime
from typing import Any, Callable

logger = logging.getLogger(__name__)

# Lazy imports
_langfuse_client = None
_datadog_tracer = None


def _get_langfuse():
    """Lazy load Langfuse client."""
    global _langfuse_client
    if _langfuse_client is None:
        try:
            from langfuse import Langfuse

            public_key = os.getenv("LANGFUSE_PUBLIC_KEY", "")
            secret_key = os.getenv("LANGFUSE_SECRET_KEY", "")

            if not public_key or not secret_key:
                logger.debug("Langfuse credentials not set")
                return None

            _langfuse_client = Langfuse(
                public_key=public_key,
                secret_key=secret_key,
                host=os.getenv("LANGFUSE_HOST", "http://localhost:3000"),
            )
        except ImportError:
            logger.debug("Langfuse not installed")
            return None
        except Exception as e:
            logger.warning(f"Failed to initialize Langfuse: {e}")
            return None
    return _langfuse_client


def _get_datadog_tracer():
    """Lazy load Datadog tracer."""
    global _datadog_tracer
    if _datadog_tracer is None:
        try:
            from ddtrace import tracer

            _datadog_tracer = tracer
        except ImportError:
            logger.debug("Datadog not installed")
            return None
    return _datadog_tracer


# Cost estimates (per 1K tokens or per batch)
EMBEDDING_COSTS = {
    "BAAI/bge-m3": {"per_1k_tokens": 0.0},  # Local model
    "text-embedding-3-small": {"per_1k_tokens": 0.00002},
    "text-embedding-3-large": {"per_1k_tokens": 0.00013},
    "text-embedding-ada-002": {"per_1k_tokens": 0.0001},
    "voyage-code-3": {"per_1k_tokens": 0.00018},
    "voyage-large-2": {"per_1k_tokens": 0.00012},
}


@dataclass
class EmbeddingMetrics:
    """Metrics for embedding operations."""

    model: str
    text_count: int
    total_chars: int
    latency_ms: float
    estimated_cost: float = 0.0

    def to_dict(self) -> dict[str, Any]:
        return {
            "model": self.model,
            "text_count": self.text_count,
            "total_chars": self.total_chars,
            "latency_ms": round(self.latency_ms, 2),
            "estimated_cost": round(self.estimated_cost, 6),
        }


@dataclass
class SearchMetrics:
    """Metrics for search operations."""

    query_length: int
    result_count: int
    latency_ms: float
    search_type: str = "semantic"

    def to_dict(self) -> dict[str, Any]:
        return {
            "query_length": self.query_length,
            "result_count": self.result_count,
            "latency_ms": round(self.latency_ms, 2),
            "search_type": self.search_type,
        }


@dataclass
class IndexMetrics:
    """Metrics for indexing operations."""

    file_count: int
    chunk_count: int
    total_chars: int
    latency_ms: float
    repo_path: str = ""

    def to_dict(self) -> dict[str, Any]:
        return {
            "file_count": self.file_count,
            "chunk_count": self.chunk_count,
            "total_chars": self.total_chars,
            "latency_ms": round(self.latency_ms, 2),
            "repo_path": self.repo_path,
        }


class CodeolasObservability:
    """
    Observability wrapper for códeolas operations.

    Provides:
    - Langfuse cost tracking for embeddings
    - Datadog APM tracing
    - Aggregated metrics
    """

    def __init__(
        self,
        project_name: str = "codeolas",
        service_name: str = "code-analysis",
    ):
        self.project_name = project_name
        self.service_name = service_name
        self._session_id = f"codeolas_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        self._embedding_metrics: list[EmbeddingMetrics] = []
        self._search_metrics: list[SearchMetrics] = []
        self._index_metrics: list[IndexMetrics] = []

    @contextmanager
    def trace_embedding(
        self,
        model: str,
        text_count: int,
        total_chars: int,
    ):
        """
        Context manager for tracing embedding generation.

        Args:
            model: Embedding model name
            text_count: Number of texts being embedded
            total_chars: Total character count

        Yields:
            Trace context
        """
        start_time = time.time()

        # Start Datadog span
        dd_tracer = _get_datadog_tracer()
        dd_span = None
        if dd_tracer:
            dd_span = dd_tracer.trace(
                "codeolas.embedding",
                service=self.service_name,
                resource=model,
            )
            dd_span.set_tag("embedding.model", model)
            dd_span.set_tag("embedding.text_count", text_count)
            dd_span.set_tag("embedding.total_chars", total_chars)

        try:
            yield

        finally:
            latency_ms = (time.time() - start_time) * 1000

            # Calculate cost (approximate tokens as chars/4)
            estimated_tokens = total_chars / 4
            model_costs = EMBEDDING_COSTS.get(model, {"per_1k_tokens": 0.0})
            estimated_cost = (estimated_tokens / 1000) * model_costs["per_1k_tokens"]

            # Create metrics
            metrics = EmbeddingMetrics(
                model=model,
                text_count=text_count,
                total_chars=total_chars,
                latency_ms=latency_ms,
                estimated_cost=estimated_cost,
            )
            self._embedding_metrics.append(metrics)

            # Log to Langfuse
            self._log_embedding_to_langfuse(metrics)

            # Complete Datadog span
            if dd_span:
                dd_span.set_tag("embedding.latency_ms", latency_ms)
                dd_span.set_tag("embedding.estimated_cost", estimated_cost)
                dd_span.finish()

    @contextmanager
    def trace_search(
        self,
        query: str,
        search_type: str = "semantic",
    ):
        """
        Context manager for tracing search operations.

        Args:
            query: Search query
            search_type: Type of search (semantic, keyword, hybrid)

        Yields:
            Search context that can record results
        """
        start_time = time.time()
        ctx = _SearchContext(query, search_type)

        # Start Datadog span
        dd_tracer = _get_datadog_tracer()
        dd_span = None
        if dd_tracer:
            dd_span = dd_tracer.trace(
                "codeolas.search",
                service=self.service_name,
                resource=search_type,
            )
            dd_span.set_tag("search.type", search_type)
            dd_span.set_tag("search.query_length", len(query))

        try:
            yield ctx

        finally:
            latency_ms = (time.time() - start_time) * 1000

            # Create metrics
            metrics = SearchMetrics(
                query_length=len(query),
                result_count=ctx.result_count,
                latency_ms=latency_ms,
                search_type=search_type,
            )
            self._search_metrics.append(metrics)

            # Log to Langfuse
            self._log_search_to_langfuse(metrics, query)

            # Complete Datadog span
            if dd_span:
                dd_span.set_tag("search.result_count", ctx.result_count)
                dd_span.set_tag("search.latency_ms", latency_ms)
                dd_span.finish()

    @contextmanager
    def trace_index(
        self,
        repo_path: str,
    ):
        """
        Context manager for tracing indexing operations.

        Args:
            repo_path: Path to repository being indexed

        Yields:
            Index context that can record stats
        """
        start_time = time.time()
        ctx = _IndexContext(repo_path)

        # Start Datadog span
        dd_tracer = _get_datadog_tracer()
        dd_span = None
        if dd_tracer:
            dd_span = dd_tracer.trace(
                "codeolas.index",
                service=self.service_name,
                resource="indexing",
            )
            dd_span.set_tag("index.repo_path", repo_path)

        try:
            yield ctx

        finally:
            latency_ms = (time.time() - start_time) * 1000

            # Create metrics
            metrics = IndexMetrics(
                file_count=ctx.file_count,
                chunk_count=ctx.chunk_count,
                total_chars=ctx.total_chars,
                latency_ms=latency_ms,
                repo_path=repo_path,
            )
            self._index_metrics.append(metrics)

            # Log to Langfuse
            self._log_index_to_langfuse(metrics)

            # Complete Datadog span
            if dd_span:
                dd_span.set_tag("index.file_count", ctx.file_count)
                dd_span.set_tag("index.chunk_count", ctx.chunk_count)
                dd_span.set_tag("index.latency_ms", latency_ms)
                dd_span.finish()

    def _log_embedding_to_langfuse(self, metrics: EmbeddingMetrics) -> None:
        """Log embedding operation to Langfuse."""
        langfuse = _get_langfuse()
        if langfuse is None:
            return

        try:
            trace = langfuse.trace(
                name=f"embedding_{metrics.model}",
                session_id=self._session_id,
                metadata={
                    "project": self.project_name,
                    **metrics.to_dict(),
                },
                tags=["embedding", "codeolas", metrics.model],
            )

            langfuse.score(
                trace_id=trace.id,
                name="latency_ms",
                value=metrics.latency_ms,
            )

            langfuse.score(
                trace_id=trace.id,
                name="cost_usd",
                value=metrics.estimated_cost,
            )

            langfuse.flush()

        except Exception as e:
            logger.warning(f"Failed to log embedding to Langfuse: {e}")

    def _log_search_to_langfuse(self, metrics: SearchMetrics, query: str) -> None:
        """Log search operation to Langfuse."""
        langfuse = _get_langfuse()
        if langfuse is None:
            return

        try:
            trace = langfuse.trace(
                name=f"search_{metrics.search_type}",
                session_id=self._session_id,
                input=query,
                metadata={
                    "project": self.project_name,
                    **metrics.to_dict(),
                },
                tags=["search", "codeolas", metrics.search_type],
            )

            langfuse.score(
                trace_id=trace.id,
                name="result_count",
                value=float(metrics.result_count),
            )

            langfuse.score(
                trace_id=trace.id,
                name="latency_ms",
                value=metrics.latency_ms,
            )

            langfuse.flush()

        except Exception as e:
            logger.warning(f"Failed to log search to Langfuse: {e}")

    def _log_index_to_langfuse(self, metrics: IndexMetrics) -> None:
        """Log indexing operation to Langfuse."""
        langfuse = _get_langfuse()
        if langfuse is None:
            return

        try:
            trace = langfuse.trace(
                name="indexing",
                session_id=self._session_id,
                metadata={
                    "project": self.project_name,
                    **metrics.to_dict(),
                },
                tags=["indexing", "codeolas"],
            )

            langfuse.score(
                trace_id=trace.id,
                name="chunk_count",
                value=float(metrics.chunk_count),
            )

            langfuse.score(
                trace_id=trace.id,
                name="latency_ms",
                value=metrics.latency_ms,
            )

            langfuse.flush()

        except Exception as e:
            logger.warning(f"Failed to log indexing to Langfuse: {e}")

    def get_session_summary(self) -> dict[str, Any]:
        """Get summary of all operations in this session."""
        embedding_count = len(self._embedding_metrics)
        search_count = len(self._search_metrics)
        index_count = len(self._index_metrics)

        embedding_cost = sum(m.estimated_cost for m in self._embedding_metrics)
        embedding_latency = sum(m.latency_ms for m in self._embedding_metrics)
        search_latency = sum(m.latency_ms for m in self._search_metrics)
        index_latency = sum(m.latency_ms for m in self._index_metrics)

        return {
            "session_id": self._session_id,
            "embeddings": {
                "count": embedding_count,
                "total_cost": round(embedding_cost, 6),
                "avg_latency_ms": embedding_latency / embedding_count if embedding_count else 0,
            },
            "searches": {
                "count": search_count,
                "avg_latency_ms": search_latency / search_count if search_count else 0,
            },
            "indexing": {
                "count": index_count,
                "avg_latency_ms": index_latency / index_count if index_count else 0,
            },
        }


class _SearchContext:
    """Internal context for tracking search results."""

    def __init__(self, query: str, search_type: str):
        self.query = query
        self.search_type = search_type
        self.result_count = 0

    def set_results(self, count: int) -> None:
        """Set result count."""
        self.result_count = count


class _IndexContext:
    """Internal context for tracking indexing stats."""

    def __init__(self, repo_path: str):
        self.repo_path = repo_path
        self.file_count = 0
        self.chunk_count = 0
        self.total_chars = 0

    def set_stats(
        self,
        file_count: int,
        chunk_count: int,
        total_chars: int = 0,
    ) -> None:
        """Set indexing statistics."""
        self.file_count = file_count
        self.chunk_count = chunk_count
        self.total_chars = total_chars


# Global instance for convenience
_default_obs: CodeolasObservability | None = None


def get_observability() -> CodeolasObservability:
    """Get or create the default observability instance."""
    global _default_obs
    if _default_obs is None:
        _default_obs = CodeolasObservability()
    return _default_obs


def trace_embedding(func: Callable) -> Callable:
    """
    Decorator to trace embedding functions.

    The decorated function should accept texts as first argument
    and return embeddings.
    """

    @functools.wraps(func)
    def wrapper(self, texts: list[str], *args, **kwargs):
        obs = get_observability()
        model = getattr(self, "model_name", "unknown")
        total_chars = sum(len(t) for t in texts)

        with obs.trace_embedding(model, len(texts), total_chars):
            return func(self, texts, *args, **kwargs)

    return wrapper


def trace_search(func: Callable) -> Callable:
    """
    Decorator to trace search functions.

    The decorated function should accept query as first argument
    and return results.
    """

    @functools.wraps(func)
    async def async_wrapper(self, query: str, *args, **kwargs):
        obs = get_observability()
        search_type = kwargs.get("search_type", "semantic")

        with obs.trace_search(query, search_type) as ctx:
            results = await func(self, query, *args, **kwargs)
            ctx.set_results(len(results) if hasattr(results, "__len__") else 0)
            return results

    @functools.wraps(func)
    def sync_wrapper(self, query: str, *args, **kwargs):
        obs = get_observability()
        search_type = kwargs.get("search_type", "semantic")

        with obs.trace_search(query, search_type) as ctx:
            results = func(self, query, *args, **kwargs)
            ctx.set_results(len(results) if hasattr(results, "__len__") else 0)
            return results

    import asyncio

    if asyncio.iscoroutinefunction(func):
        return async_wrapper
    return sync_wrapper
