"""
Code Search Tools for Crypteolas agents.

Provides semantic code search capabilities.

Note: CocoIndex flows are loaded lazily to avoid import-time issues.
"""

from typing import Any

# Lazy-loaded module references
_code_embedding_module = None


def _get_code_embedding():
    """Lazy load code_embedding module."""
    global _code_embedding_module
    if _code_embedding_module is None:
        try:
            from cocoindex_flows import code_embedding  # type: ignore
            _code_embedding_module = code_embedding
        except Exception as e:
            # Return a stub module for development
            import structlog
            logger = structlog.get_logger()
            logger.warning("Failed to load code_embedding", error=str(e))
            _code_embedding_module = None
    return _code_embedding_module


async def search_code(
    query: str,
    repo: str | None = None,
    language: str | None = None,
    limit: int = 10,
) -> Any:
    """Search code semantically."""
    module = _get_code_embedding()
    if module is None:
        # Return empty results if module not available
        class StubResult:
            results = []
        return StubResult()
    return await module.search_code(query, repo=repo, language=language, limit=limit)


async def find_similar_code(
    code_snippet: str,
    exclude_file: str | None = None,
    limit: int = 5,
) -> list[dict]:
    """Find similar code patterns."""
    module = _get_code_embedding()
    if module is None:
        return []
    return await module.find_similar_code(code_snippet, exclude_file=exclude_file, limit=limit)


async def search_by_function_name(
    function_name: str,
    repo: str | None = None,
) -> list[dict]:
    """Find function implementations by name."""
    query = f"function {function_name}"
    results = await search_code(query, repo=repo, limit=10)
    return results.results if hasattr(results, "results") else []


async def search_by_pattern(
    pattern: str,
    repo: str | None = None,
    language: str | None = None,
) -> list[dict]:
    """Find code matching a pattern."""
    results = await search_code(pattern, repo=repo, language=language, limit=10)
    return results.results if hasattr(results, "results") else []


__all__ = [
    "search_code",
    "find_similar_code",
    "search_by_function_name",
    "search_by_pattern",
]
