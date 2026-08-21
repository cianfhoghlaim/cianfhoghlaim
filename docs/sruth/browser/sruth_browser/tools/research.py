"""Research tools for deep web research."""

from typing import Any

from google.adk.tools import FunctionTool

from ..backends.router import get_router
from ..core.types import BackendType, BrowserOperation


async def deep_research(
    topic: str,
    max_sources: int = 15,
    schema: dict[str, Any] | None = None,
) -> dict:
    """Perform deep research on a topic across multiple sources.

    Uses Firecrawl's autonomous research agent for comprehensive
    information gathering.

    Args:
        topic: Research topic or question
        max_sources: Maximum number of sources to consult
        schema: Optional schema for structured output

    Returns:
        Research results with content and sources
    """
    router = get_router()

    # Prefer Firecrawl for research
    firecrawl = router.get_backend(BackendType.FIRECRAWL_MCP)
    if firecrawl and hasattr(firecrawl, "research"):
        result = await firecrawl.research(
            topic,
            max_urls=max_sources,
            schema=schema,
        )
        return result

    # Fall back to Skyvern
    async def _research(backend):
        if hasattr(backend, "research"):
            return await backend.research(topic, max_urls=max_sources, schema=schema)
        return {
            "success": False,
            "error": "Backend doesn't support research",
        }

    return await router.execute_with_fallback(BrowserOperation.RESEARCH, _research)


async def map_site(
    url: str,
    search: str | None = None,
    limit: int = 100,
) -> dict:
    """Map all URLs on a website.

    Discovers the structure of a website by crawling and
    collecting all accessible URLs.

    Args:
        url: Starting URL
        search: Optional search term to filter URLs
        limit: Maximum URLs to return

    Returns:
        List of discovered URLs
    """
    router = get_router()

    # Try Firecrawl map endpoint
    firecrawl = router.get_backend(BackendType.FIRECRAWL_MCP)
    if firecrawl and hasattr(firecrawl, "map_site"):
        links = await firecrawl.map_site(url, search=search, limit=limit)
        return {
            "success": True,
            "url": url,
            "links": links,
            "count": len(links),
            "search": search,
        }

    # Fall back to extraction-based discovery
    from .extraction import extract_page

    result = await extract_page(url, formats=["links"])
    if not result.get("success"):
        return result

    links = result.get("content", {}).get("links", [])

    # Filter if search provided
    if search:
        import re
        pattern = re.compile(search, re.IGNORECASE)
        links = [l for l in links if pattern.search(str(l))]

    return {
        "success": True,
        "url": url,
        "links": links[:limit],
        "count": len(links[:limit]),
        "search": search,
    }


async def research_with_sources(
    topic: str,
    required_sources: list[str] | None = None,
    excluded_domains: list[str] | None = None,
) -> dict:
    """Research a topic with source requirements.

    Args:
        topic: Research topic
        required_sources: Domains that must be included
        excluded_domains: Domains to exclude

    Returns:
        Research results filtered by source requirements
    """
    result = await deep_research(topic, max_sources=20)

    if not result.get("success"):
        return result

    sources = result.get("sources", [])

    # Filter by requirements
    if excluded_domains:
        sources = [
            s for s in sources
            if not any(d in s.get("url", "") for d in excluded_domains)
        ]

    if required_sources:
        # Check if required sources are present
        found_required = []
        for req in required_sources:
            for s in sources:
                if req in s.get("url", ""):
                    found_required.append(req)
                    break

        if len(found_required) < len(required_sources):
            missing = set(required_sources) - set(found_required)
            result["warnings"] = [f"Missing required sources: {missing}"]

    result["sources"] = sources
    return result


# Create ADK tools
research_tool = FunctionTool(deep_research)
map_tool = FunctionTool(map_site)
research_sources_tool = FunctionTool(research_with_sources)
