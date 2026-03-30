"""
Search Routes for Crypteolas API.

Provides code and document search endpoints.
"""

from fastapi import APIRouter, Query
from pydantic import BaseModel
import structlog

from agents.tools.code_search import search_code, find_similar_code  # type: ignore
from agents.tools.document_search import (  # type: ignore
    search_documents,
    search_audits,
    search_whitepapers,
)

logger = structlog.get_logger()

router = APIRouter()


class SearchRequest(BaseModel):
    """Search request model."""

    query: str
    limit: int = 10


class CodeSearchRequest(SearchRequest):
    """Code search request model."""

    repo: str | None = None
    language: str | None = None


class DocSearchRequest(SearchRequest):
    """Document search request model."""

    protocol: str | None = None
    doc_type: str | None = None


@router.post("/code")
async def search_code_endpoint(request: CodeSearchRequest):
    """
    Search code semantically.

    Supports natural language queries and code snippets.
    """
    try:
        results = await search_code(
            query=request.query,
            repo=request.repo,
            language=request.language,
            limit=request.limit,
        )
        return {
            "results": results.results if hasattr(results, "results") else [],
            "query": request.query,
            "status": "success",
        }
    except Exception as e:
        logger.error("Code search error", error=str(e))
        return {"error": str(e), "status": "error"}


@router.post("/code/similar")
async def find_similar_code_endpoint(request: SearchRequest):
    """
    Find similar code patterns.

    Useful for detecting duplicates and related implementations.
    """
    try:
        results = await find_similar_code(request.query, limit=request.limit)
        return {
            "results": results,
            "status": "success",
        }
    except Exception as e:
        logger.error("Similar code search error", error=str(e))
        return {"error": str(e), "status": "error"}


@router.post("/documents")
async def search_documents_endpoint(request: DocSearchRequest):
    """
    Search protocol documentation.

    Includes docs, whitepapers, audits, and API documentation.
    """
    try:
        results = await search_documents(
            query=request.query,
            protocol=request.protocol,
            doc_type=request.doc_type,
            limit=request.limit,
        )
        return {
            "results": results.results if hasattr(results, "results") else [],
            "query": request.query,
            "status": "success",
        }
    except Exception as e:
        logger.error("Document search error", error=str(e))
        return {"error": str(e), "status": "error"}


@router.post("/audits")
async def search_audits_endpoint(request: DocSearchRequest):
    """
    Search security audit reports.

    Find vulnerability patterns and audit findings.
    """
    try:
        results = await search_audits(
            query=request.query,
            protocol=request.protocol,
            limit=request.limit,
        )
        return {
            "results": results,
            "query": request.query,
            "status": "success",
        }
    except Exception as e:
        logger.error("Audit search error", error=str(e))
        return {"error": str(e), "status": "error"}


@router.post("/whitepapers")
async def search_whitepapers_endpoint(request: DocSearchRequest):
    """
    Search protocol whitepapers.

    Find tokenomics, technical specs, and design docs.
    """
    try:
        results = await search_whitepapers(
            query=request.query,
            protocol=request.protocol,
            limit=request.limit,
        )
        return {
            "results": results,
            "query": request.query,
            "status": "success",
        }
    except Exception as e:
        logger.error("Whitepaper search error", error=str(e))
        return {"error": str(e), "status": "error"}


@router.get("/code")
async def search_code_get(
    q: str = Query(..., description="Search query"),
    repo: str | None = Query(None, description="Repository filter"),
    language: str | None = Query(None, description="Language filter"),
    limit: int = Query(10, description="Result limit"),
):
    """GET endpoint for code search."""
    return await search_code_endpoint(
        CodeSearchRequest(query=q, repo=repo, language=language, limit=limit)
    )


@router.get("/documents")
async def search_documents_get(
    q: str = Query(..., description="Search query"),
    protocol: str | None = Query(None, description="Protocol filter"),
    doc_type: str | None = Query(None, description="Document type filter"),
    limit: int = Query(10, description="Result limit"),
):
    """GET endpoint for document search."""
    return await search_documents_endpoint(
        DocSearchRequest(query=q, protocol=protocol, doc_type=doc_type, limit=limit)
    )
