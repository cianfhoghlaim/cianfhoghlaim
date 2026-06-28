"""Gatherer Agent - Bulk content extraction using Crawl4AI.

The Gatherer is the third phase in the browsing pipeline.
It uses Crawl4AI for high-throughput content extraction:
- Markdown/HTML conversion
- Structured data extraction with schemas
- Bulk URL processing
- LLM-enhanced extraction
"""

from typing import Any

from google.adk.agents import LlmAgent
from google.adk.tools import FunctionTool
from pydantic import BaseModel, Field

from ..backends import get_router
from ..browser_types import BackendType, BrowserOperation, ExtractionFormat


class ExtractionSpec(BaseModel):
    """Model for extraction specification."""

    url: str = Field(description="URL to extract from")
    formats: list[str] = Field(
        default=["markdown"],
        description="Output formats: markdown, html, links, screenshot, json",
    )
    prompt: str | None = Field(
        default=None,
        description="LLM prompt for intelligent extraction",
    )
    schema: dict | None = Field(
        default=None,
        description="JSON schema for structured extraction",
    )


async def extract_page(
    url: str,
    formats: list[str] | None = None,
    prompt: str | None = None,
) -> dict:
    """Extract content from a single page.

    Args:
        url: URL to extract from
        formats: Output formats (markdown, html, links, screenshot)
        prompt: Optional LLM prompt for intelligent extraction

    Returns:
        Extracted content in requested formats
    """
    router = get_router()
    formats = formats or ["markdown"]

    # Map string formats to enum
    format_map = {
        "markdown": ExtractionFormat.MARKDOWN,
        "html": ExtractionFormat.HTML,
        "rawHtml": ExtractionFormat.RAW_HTML,
        "links": ExtractionFormat.LINKS,
        "screenshot": ExtractionFormat.SCREENSHOT,
        "json": ExtractionFormat.JSON,
        "text": ExtractionFormat.TEXT,
    }
    enum_formats = [format_map.get(f, ExtractionFormat.MARKDOWN) for f in formats]

    async def _extract(backend):
        result = await backend.extract(
            url,
            formats=enum_formats,
            prompt=prompt,
        )
        return {
            "success": result.success,
            "url": result.url,
            "content": result.content,
            "format": result.format.value,
            "error": result.error,
        }

    return await router.execute_with_fallback(
        BrowserOperation.EXTRACT,
        _extract,
    )


async def extract_structured(
    url: str,
    schema: dict,
    prompt: str | None = None,
) -> dict:
    """Extract structured data according to a JSON schema.

    Uses LLM-enhanced extraction for type-safe data extraction.

    Args:
        url: URL to extract from
        schema: JSON schema defining expected structure
        prompt: Optional prompt to guide extraction

    Returns:
        Structured data matching the schema
    """
    router = get_router()

    async def _extract(backend):
        result = await backend.extract(
            url,
            formats=[ExtractionFormat.JSON],
            schema=schema,
            prompt=prompt or "Extract data according to the provided schema",
        )

        if result.success and "extracted" in result.content:
            return {
                "success": True,
                "url": url,
                "data": result.content["extracted"],
            }
        else:
            return {
                "success": False,
                "url": url,
                "error": result.error or "Extraction failed",
            }

    return await router.execute_with_fallback(
        BrowserOperation.EXTRACT,
        _extract,
    )


async def batch_extract(
    urls: list[str],
    formats: list[str] | None = None,
    max_concurrent: int = 4,
) -> dict:
    """Extract content from multiple URLs concurrently.

    Uses Crawl4AI's parallel crawling for high throughput.

    Args:
        urls: List of URLs to extract from
        formats: Output formats for all URLs
        max_concurrent: Maximum concurrent extractions

    Returns:
        Batch extraction results
    """
    router = get_router()
    formats = formats or ["markdown"]

    # Map formats
    format_map = {
        "markdown": ExtractionFormat.MARKDOWN,
        "html": ExtractionFormat.HTML,
        "links": ExtractionFormat.LINKS,
    }
    enum_formats = [format_map.get(f, ExtractionFormat.MARKDOWN) for f in formats]

    # Try Crawl4AI batch endpoint
    crawl4ai = router.get_backend(BackendType.CRAWL4AI_LOCAL)
    if crawl4ai and hasattr(crawl4ai, "batch_extract"):
        results = await crawl4ai.batch_extract(
            urls,
            formats=enum_formats,
            max_concurrent=max_concurrent,
        )
        return {
            "success": all(r.success for r in results),
            "total": len(urls),
            "successful": sum(1 for r in results if r.success),
            "results": [
                {
                    "url": r.url,
                    "success": r.success,
                    "content": r.content,
                    "error": r.error,
                }
                for r in results
            ],
        }

    # Try Firecrawl batch
    firecrawl = router.get_backend(BackendType.FIRECRAWL_MCP)
    if firecrawl and hasattr(firecrawl, "batch_scrape"):
        results = await firecrawl.batch_scrape(urls, formats=enum_formats)
        return {
            "success": all(r.success for r in results),
            "total": len(urls),
            "successful": sum(1 for r in results if r.success),
            "results": [
                {
                    "url": r.url,
                    "success": r.success,
                    "content": r.content,
                    "error": r.error,
                }
                for r in results
            ],
        }

    # Fall back to sequential extraction
    results = []
    for url in urls:
        result = await extract_page(url, formats)
        results.append(result)

    return {
        "success": all(r.get("success") for r in results),
        "total": len(urls),
        "successful": sum(1 for r in results if r.get("success")),
        "results": results,
    }


async def deep_research(
    topic: str,
    max_urls: int = 15,
    schema: dict | None = None,
) -> dict:
    """Perform deep research on a topic across multiple sources.

    Uses Firecrawl's /agent endpoint for autonomous research.

    Args:
        topic: Research topic or question
        max_urls: Maximum URLs to visit
        schema: Optional schema for structured output

    Returns:
        Research results with sources
    """
    router = get_router()

    # Prefer Firecrawl for research
    firecrawl = router.get_backend(BackendType.FIRECRAWL_MCP)
    if firecrawl and hasattr(firecrawl, "research"):
        return await firecrawl.research(
            topic,
            max_urls=max_urls,
            schema=schema,
        )

    # Fall back to Skyvern
    async def _research(backend):
        if hasattr(backend, "research"):
            return await backend.research(topic, max_urls=max_urls, schema=schema)
        raise Exception("Backend doesn't support research")

    return await router.execute_with_fallback(
        BrowserOperation.RESEARCH,
        _research,
    )


async def extract_links(
    url: str,
    filter_pattern: str | None = None,
) -> dict:
    """Extract all links from a page, optionally filtered.

    Args:
        url: URL to extract links from
        filter_pattern: Optional pattern to filter links

    Returns:
        List of links with text and href
    """
    result = await extract_page(url, formats=["links"])

    if not result.get("success"):
        return result

    links = result.get("content", {}).get("links", [])

    if filter_pattern:
        import re
        pattern = re.compile(filter_pattern, re.IGNORECASE)
        links = [l for l in links if pattern.search(l.get("href", "") + l.get("text", ""))]

    return {
        "success": True,
        "url": url,
        "links": links,
        "count": len(links),
    }


# Create function tools for ADK
extract_tool = FunctionTool(extract_page)
structured_tool = FunctionTool(extract_structured)
batch_tool = FunctionTool(batch_extract)
research_tool = FunctionTool(deep_research)
links_tool = FunctionTool(extract_links)

# Gatherer Agent Definition
gatherer_agent = LlmAgent(
    name="gatherer",
    model="gemini-2.0-flash",
    description="""Bulk content extraction agent for high-throughput scraping.

    Capabilities:
    - Extract markdown/HTML from pages
    - Structured data extraction with schemas
    - Batch extraction from multiple URLs
    - Deep research across multiple sources
    - Link discovery and filtering

    Use this agent when:
    - Content needs to be extracted from pages
    - Multiple URLs need processing
    - Structured data extraction is required
    - Research across multiple sources is needed
    """,
    instruction="""You are the Gatherer agent, specialized in content extraction.

    Your role in the pipeline:
    1. Receive URLs from Hunter and page states from Operator
    2. Extract content in requested formats
    3. Use schemas for structured extraction
    4. Handle batch extraction for efficiency
    5. Perform deep research when needed

    Guidelines:
    - For single pages, use extract_page
    - For structured data, use extract_structured with schema
    - For multiple URLs, use batch_extract
    - For research, use deep_research
    - Report extraction results with success/failure status

    Output formats:
    - markdown: Clean text with formatting
    - html: Raw HTML content
    - links: All hyperlinks on page
    - json: Structured data (requires schema)
    """,
    tools=[extract_tool, structured_tool, batch_tool, research_tool, links_tool],
    output_key="gatherer_result",
)
