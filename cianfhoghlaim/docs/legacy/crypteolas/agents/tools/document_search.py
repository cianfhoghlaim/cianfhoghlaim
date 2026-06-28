"""
Document Search Tools for Crypteolas agents.

Provides documentation search capabilities.

Note: CocoIndex flows are loaded lazily to avoid import-time issues.
"""

from typing import Any

# Lazy-loaded module reference
_document_embedding_module = None


def _get_document_embedding():
    """Lazy load document_embedding module."""
    global _document_embedding_module
    if _document_embedding_module is None:
        try:
            from cocoindex_flows import document_embedding  # type: ignore
            _document_embedding_module = document_embedding
        except Exception as e:
            import structlog
            logger = structlog.get_logger()
            logger.warning("Failed to load document_embedding", error=str(e))
            _document_embedding_module = None
    return _document_embedding_module


async def search_documents(
    query: str,
    protocol: str | None = None,
    doc_type: str | None = None,
    limit: int = 10,
) -> Any:
    """Search all protocol documentation."""
    module = _get_document_embedding()
    if module is None:
        class StubResult:
            results = []
        return StubResult()
    return await module.search_documents(query, protocol=protocol, doc_type=doc_type, limit=limit)


async def search_audits(
    query: str,
    protocol: str | None = None,
    limit: int = 5,
) -> list[dict]:
    """Search audit reports."""
    module = _get_document_embedding()
    if module is None:
        return []
    return await module.search_audits(query, protocol=protocol, limit=limit)


async def search_whitepapers(
    query: str,
    protocol: str | None = None,
    limit: int = 5,
) -> list[dict]:
    """Search whitepapers."""
    module = _get_document_embedding()
    if module is None:
        return []
    return await module.search_whitepapers(query, protocol=protocol, limit=limit)


async def search_api_docs(
    query: str,
    protocol: str | None = None,
    limit: int = 5,
) -> list[dict]:
    """Search API documentation."""
    results = await search_documents(query, protocol=protocol, doc_type="api_docs", limit=limit)
    return results.results if hasattr(results, "results") else []


__all__ = [
    "search_documents",
    "search_audits",
    "search_whitepapers",
    "search_api_docs",
]
