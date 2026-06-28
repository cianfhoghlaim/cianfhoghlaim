"""Extraction tools for content retrieval."""

from typing import Any

from google.adk.tools import FunctionTool

from ..backends.router import get_router
from ..core.types import BackendType, BrowserOperation, ExtractionFormat


async def extract_page(
    url: str,
    formats: list[str] | None = None,
    prompt: str | None = None,
    timeout: float | None = None,
) -> dict:
    """Extract content from a web page.

    Args:
        url: URL to extract from
        formats: Output formats (markdown, html, links, screenshot, json)
        prompt: Optional LLM prompt for intelligent extraction
        timeout: Extraction timeout in seconds

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
        "summary": ExtractionFormat.SUMMARY,
    }
    enum_formats = [format_map.get(f, ExtractionFormat.MARKDOWN) for f in formats]

    async def _extract(backend):
        result = await backend.extract(
            url,
            formats=enum_formats,
            prompt=prompt,
            timeout=timeout,
        )
        return {
            "success": result.success,
            "url": result.url,
            "content": result.content,
            "format": result.format.value,
            "backend": result.backend_used.value,
            "latency_ms": result.latency_ms,
            "error": result.error,
        }

    return await router.execute_with_fallback(BrowserOperation.EXTRACT, _extract)


async def extract_structured(
    url: str,
    schema: dict[str, Any],
    prompt: str | None = None,
    timeout: float | None = None,
) -> dict:
    """Extract structured data according to a JSON schema.

    Args:
        url: URL to extract from
        schema: JSON schema defining expected structure
        prompt: Optional extraction prompt
        timeout: Extraction timeout

    Returns:
        Structured data matching schema
    """
    router = get_router()

    async def _extract(backend):
        result = await backend.extract(
            url,
            formats=[ExtractionFormat.JSON],
            schema=schema,
            prompt=prompt or "Extract data according to the provided schema",
            timeout=timeout,
        )

        if result.success and "extracted" in result.content:
            return {
                "success": True,
                "url": url,
                "data": result.content["extracted"],
                "backend": result.backend_used.value,
            }
        else:
            return {
                "success": False,
                "url": url,
                "error": result.error or "Extraction failed",
            }

    return await router.execute_with_fallback(BrowserOperation.EXTRACT, _extract)


async def batch_extract(
    urls: list[str],
    formats: list[str] | None = None,
    max_concurrent: int = 4,
) -> dict:
    """Extract content from multiple URLs concurrently.

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

    # Try batch-capable backends first
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

    # Fall back to sequential
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


# Create ADK tools
extract_tool = FunctionTool(extract_page)
structured_tool = FunctionTool(extract_structured)
batch_tool = FunctionTool(batch_extract)
