"""
Shared helpers split from ireland/agentic_discovery.py

Phase 3D of openspec change.
"""

import os
from collections.abc import Iterator
from datetime import UTC, datetime
from typing import Any
import dlt

def _discover_curriculum_content(
    educational_stage: str | None = None,
    subject: str | None = None,
    language: str = "en",
    max_results: int = 50,
) -> Iterator[dict[str, Any]]:
    """
    Discover curriculum content using Firecrawl agent.

    Args:
        educational_stage: Stage filter (primary, junior_cycle, senior_cycle)
        subject: Subject filter
        language: Language (en or ga)
        max_results: Maximum results

    Yields:
        Curriculum content records
    """
    prompt_parts = ["Find curriculum specifications and resources"]

    if educational_stage:
        prompt_parts.append(f"for {educational_stage.replace('_', ' ')}")
    if subject:
        prompt_parts.append(f"in {subject}")

    prompt_parts.append(
        "Include title, educational stage, subject, description, and URL"
    )

    prompt = " ".join(prompt_parts)

    schema = {
        "type": "object",
        "properties": {
            "curriculum_items": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "title": {"type": "string"},
                        "educational_stage": {"type": "string"},
                        "subject": {"type": "string"},
                        "description": {"type": "string"},
                        "url": {"type": "string"},
                        "content_type": {"type": "string"},
                    },
                },
            },
        },
    }

    # Determine base URL based on language
    base_url = "https://www.curriculumonline.ie"
    if language == "ga":
        base_url += "/ga-ie"

    try:
        result = _discover_with_agent(
            prompt=prompt,
            urls=[base_url],
            schema=schema,
        )

        items = result.get("data", {}).get("curriculum_items", [])

        for item in items[:max_results]:
            yield {
                "title": item.get("title", ""),
                "educational_stage": item.get("educational_stage", ""),
                "subject": item.get("subject", ""),
                "description": item.get("description", ""),
                "url": item.get("url", ""),
                "content_type": item.get("content_type", ""),
                "language": language,
                "source": "curriculumonline.ie",
                "discovered_at": datetime.now(UTC).isoformat(),
                "discovery_method": "agentic",
            }
    except Exception as e:
        yield {
            "error": str(e),
            "source": "curriculumonline.ie",
            "discovered_at": datetime.now(UTC).isoformat(),
            "status": "error",
        }

def _discover_exam_papers(
    year: int | None = None,
    subject: str | None = None,
    level: str | None = None,
    max_results: int = 50,
) -> Iterator[dict[str, Any]]:
    """
    Discover exam papers using Firecrawl agent.

    Args:
        year: Exam year filter
        subject: Subject filter (e.g., "Irish", "Mathematics")
        level: Level filter (e.g., "Higher", "Ordinary", "Foundation")
        max_results: Maximum results to return

    Yields:
        Exam paper discovery records
    """
    # Build discovery prompt
    prompt_parts = ["Find exam papers on examinations.ie"]

    if year:
        prompt_parts.append(f"from {year}")
    if subject:
        prompt_parts.append(f"for {subject}")
    if level:
        prompt_parts.append(f"at {level} level")

    prompt_parts.append(
        "Include the paper title, year, subject, level, and download URL"
    )

    prompt = " ".join(prompt_parts)

    # Define extraction schema
    schema = {
        "type": "object",
        "properties": {
            "exam_papers": {
                "type": "array",
                "items": {
                    "type": "object",
                    "properties": {
                        "title": {"type": "string"},
                        "year": {"type": "integer"},
                        "subject": {"type": "string"},
                        "level": {"type": "string"},
                        "paper_number": {"type": "string"},
                        "url": {"type": "string"},
                    },
                },
            },
        },
    }

    try:
        result = _discover_with_agent(
            prompt=prompt,
            urls=["https://www.examinations.ie"],
            schema=schema,
        )

        papers = result.get("data", {}).get("exam_papers", [])

        for paper in papers[:max_results]:
            yield {
                "title": paper.get("title", ""),
                "year": paper.get("year"),
                "subject": paper.get("subject", ""),
                "level": paper.get("level", ""),
                "paper_number": paper.get("paper_number", ""),
                "url": paper.get("url", ""),
                "source": "examinations.ie",
                "discovered_at": datetime.now(UTC).isoformat(),
                "discovery_method": "agentic",
            }
    except Exception as e:
        yield {
            "error": str(e),
            "source": "examinations.ie",
            "discovered_at": datetime.now(UTC).isoformat(),
            "status": "error",
        }

def _discover_pdfs(
    sites: list[str] | None = None,
    max_per_site: int = 100,
) -> Iterator[dict[str, Any]]:
    """
    Discover PDF documents across educational sites.

    Args:
        sites: Sites to search (default: all education sites)
        max_per_site: Maximum PDFs per site

    Yields:
        PDF discovery records
    """
    target_sites = sites or [
        "https://www.curriculumonline.ie",
        "https://www.examinations.ie",
        "https://www.ncca.ie",
    ]

    for site in target_sites:
        urls = _map_education_urls(site, search_term=".pdf", max_urls=max_per_site)

        for url in urls:
            if ".pdf" in url.lower():
                yield {
                    "url": url,
                    "source_site": site,
                    "content_type": "pdf",
                    "discovered_at": datetime.now(UTC).isoformat(),
                }

def _discover_with_agent(
    prompt: str,
    urls: list[str] | None = None,
    schema: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """
    Use Firecrawl agent for autonomous discovery.

    Args:
        prompt: Natural language discovery prompt
        urls: Optional URLs to focus on
        schema: Optional JSON schema for structured output

    Returns:
        Agent discovery result
    """
    app = _get_firecrawl_client()

    agent_params: dict[str, Any] = {"prompt": prompt}

    if urls:
        agent_params["urls"] = urls
    if schema:
        agent_params["schema"] = schema

    return app.agent(**agent_params)

def _get_firecrawl_client() -> Any:
    """Get Firecrawl client instance."""
    from firecrawl import FirecrawlApp

    api_key = os.getenv("FIRECRAWL_API_KEY")
    if not api_key:
        raise ValueError("FIRECRAWL_API_KEY environment variable required")
    return FirecrawlApp(api_key=api_key)

def _map_education_urls(
    base_url: str,
    search_term: str | None = None,
    max_urls: int = 500,
) -> list[str]:
    """
    Map URLs from an educational website.

    Args:
        base_url: Base URL to map
        search_term: Optional search filter
        max_urls: Maximum URLs to return

    Returns:
        List of discovered URLs
    """
    app = _get_firecrawl_client()

    map_params: dict[str, Any] = {"limit": max_urls}
    if search_term:
        map_params["search"] = search_term

    try:
        result = app.map_url(base_url, params=map_params)
        return result.get("links", [])
    except Exception:
        return []
