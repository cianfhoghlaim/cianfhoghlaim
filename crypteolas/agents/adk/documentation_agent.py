"""
Documentation Agent for Crypteolas.

Protocol documentation search and analysis including:
- Documentation RAG
- Whitepaper analysis
- Audit report queries
- API documentation
"""

import datetime

from google.adk.agents import LlmAgent
from google.adk.tools import FunctionTool

from ..config import config
from ..tools.document_search import (
    search_documents,
    search_audits,
    search_whitepapers,
    search_api_docs,
)


# Define tools
async def search_all_docs(
    query: str,
    protocol: str | None = None,
    doc_type: str | None = None,
    limit: int = 10,
) -> list[dict]:
    """
    Search all protocol documentation.

    Args:
        query: Search query
        protocol: Filter by protocol name
        doc_type: Filter by type (documentation, whitepaper, audit, api_docs)
        limit: Maximum results
    """
    try:
        results = await search_documents(
            query, protocol=protocol, doc_type=doc_type, limit=limit
        )
        return results.results if hasattr(results, "results") else []
    except Exception:
        return []


async def search_audit_reports(
    query: str,
    protocol: str | None = None,
    severity: str | None = None,
) -> list[dict]:
    """
    Search security audit reports.

    Args:
        query: Search query (e.g., 'reentrancy', 'access control')
        protocol: Filter by protocol
        severity: Filter by severity (critical, high, medium, low)
    """
    try:
        return await search_audits(query, protocol=protocol)
    except Exception:
        return []


async def search_protocol_whitepapers(
    query: str,
    protocol: str | None = None,
) -> list[dict]:
    """
    Search protocol whitepapers for specific information.

    Args:
        query: Search query (e.g., 'tokenomics', 'consensus')
        protocol: Filter by protocol
    """
    try:
        return await search_whitepapers(query, protocol=protocol)
    except Exception:
        return []


async def search_api_documentation(
    query: str,
    protocol: str | None = None,
) -> list[dict]:
    """
    Search API and developer documentation.

    Args:
        query: Search query (e.g., 'swap endpoint', 'authentication')
        protocol: Filter by protocol
    """
    try:
        return await search_api_docs(query, protocol=protocol)
    except Exception:
        return []


# Create tools
docs_tool = FunctionTool(func=search_all_docs)
audit_tool = FunctionTool(func=search_audit_reports)
whitepaper_tool = FunctionTool(func=search_protocol_whitepapers)
api_tool = FunctionTool(func=search_api_documentation)


# Documentation Agent
documentation_agent = LlmAgent(
    name="documentation_agent",
    model=config.worker_model,
    description="Protocol documentation search including whitepapers, audits, and API docs.",
    instruction=f"""
    You are a Documentation specialist for crypto protocols.

    **YOUR EXPERTISE:**
    - Protocol documentation search
    - Whitepaper analysis
    - Security audit findings
    - API documentation

    **AVAILABLE TOOLS:**
    1. search_all_docs - Search all documentation
    2. search_audit_reports - Search security audits
    3. search_protocol_whitepapers - Search whitepapers
    4. search_api_documentation - Search API docs

    **DOCUMENT TYPES:**
    - documentation: General protocol docs
    - whitepaper: Technical whitepapers
    - audit: Security audit reports
    - api_docs: API/developer documentation

    **SEARCH APPROACH:**
    1. Start with general docs search
    2. Use specific tools for targeted queries
    3. Cross-reference multiple sources
    4. Verify information currency

    **OUTPUT FORMAT:**
    - Quote relevant passages
    - Cite document sources
    - Note document date/version
    - Summarize key findings

    Current date: {datetime.datetime.now().strftime("%Y-%m-%d")}
    """,
    tools=[docs_tool, audit_tool, whitepaper_tool, api_tool],
    output_key="documentation",
)
