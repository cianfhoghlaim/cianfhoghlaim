"""
Agentic Discovery DLT Source.

Uses Firecrawl agent for intelligent URL discovery and data extraction
across Irish educational websites.

Features:
- Autonomous web navigation and discovery
- Schema-driven structured extraction
- Multi-site coordination
- PDF and document discovery

Usage:
    from sources.agentic_discovery import agentic_discovery_source

    source = agentic_discovery_source(
        discovery_prompt="Find all 2024 exam papers for Irish",
        max_urls=50,
    )

    pipeline = dlt.pipeline(
        pipeline_name="agentic_discovery",
        destination="duckdb",
    )
    pipeline.run(source)
"""

import os
from datetime import datetime, timezone
from typing import Any, Iterator

import dlt

from ..constants.education_sources import EDUCATION_SITES


def _get_firecrawl_client() -> Any:
    """Get Firecrawl client instance."""
    from firecrawl import FirecrawlApp

    api_key = os.getenv("FIRECRAWL_API_KEY")
    if not api_key:
        raise ValueError("FIRECRAWL_API_KEY environment variable required")
    return FirecrawlApp(api_key=api_key)


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
                    "discovered_at": datetime.now(timezone.utc).isoformat(),
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
                "discovered_at": datetime.now(timezone.utc).isoformat(),
                "discovery_method": "agentic",
            }
    except Exception as e:
        yield {
            "error": str(e),
            "source": "examinations.ie",
            "discovered_at": datetime.now(timezone.utc).isoformat(),
            "status": "error",
        }


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
                "discovered_at": datetime.now(timezone.utc).isoformat(),
                "discovery_method": "agentic",
            }
    except Exception as e:
        yield {
            "error": str(e),
            "source": "curriculumonline.ie",
            "discovered_at": datetime.now(timezone.utc).isoformat(),
            "status": "error",
        }


@dlt.source(name="agentic_discovery")
def agentic_discovery_source(
    discovery_prompt: str | None = None,
    target_sites: list[str] | None = None,
    schema: dict[str, Any] | None = None,
    include_pdfs: bool = True,
    include_exam_papers: bool = True,
    include_curriculum: bool = True,
    exam_year: int | None = None,
    exam_subject: str | None = None,
    educational_stage: str | None = None,
    language: str = "en",
    max_results: int = 50,
):
    """
    DLT source for agentic web discovery.

    Uses Firecrawl agent for intelligent URL discovery and extraction
    across Irish educational websites.

    Args:
        discovery_prompt: Custom discovery prompt (overrides other filters)
        target_sites: Sites to target for custom prompt
        schema: Custom schema for structured extraction
        include_pdfs: Include PDF discovery
        include_exam_papers: Include exam paper discovery
        include_curriculum: Include curriculum content discovery
        exam_year: Filter exam papers by year
        exam_subject: Filter by subject
        educational_stage: Filter curriculum by stage
        language: Language (en or ga)
        max_results: Maximum results per resource

    Returns:
        DLT source with discovered content resources
    """

    @dlt.resource(
        name="custom_discovery",
        write_disposition="merge",
        primary_key=["url"],
    )
    def custom_discovery():
        """Custom agent-driven discovery."""
        if not discovery_prompt:
            return

        try:
            result = _discover_with_agent(
                prompt=discovery_prompt,
                urls=target_sites,
                schema=schema,
            )

            data = result.get("data", {})

            # Flatten nested data structures
            if isinstance(data, dict):
                for key, value in data.items():
                    if isinstance(value, list):
                        for item in value:
                            if isinstance(item, dict):
                                item["discovery_key"] = key
                                item["discovered_at"] = datetime.now(
                                    timezone.utc
                                ).isoformat()
                                yield item
                    else:
                        yield {
                            "discovery_key": key,
                            "data": value,
                            "discovered_at": datetime.now(timezone.utc).isoformat(),
                        }
            else:
                yield {
                    "data": data,
                    "discovered_at": datetime.now(timezone.utc).isoformat(),
                }

        except Exception as e:
            yield {
                "error": str(e),
                "prompt": discovery_prompt,
                "discovered_at": datetime.now(timezone.utc).isoformat(),
                "status": "error",
            }

    @dlt.resource(
        name="pdf_urls",
        write_disposition="merge",
        primary_key=["url"],
    )
    def pdf_urls():
        """Discovered PDF URLs."""
        if include_pdfs:
            yield from _discover_pdfs(sites=target_sites, max_per_site=max_results)

    @dlt.resource(
        name="exam_papers",
        write_disposition="merge",
        primary_key=["url"],
    )
    def exam_papers():
        """Discovered exam papers."""
        if include_exam_papers:
            yield from _discover_exam_papers(
                year=exam_year,
                subject=exam_subject,
                max_results=max_results,
            )

    @dlt.resource(
        name="curriculum_content",
        write_disposition="merge",
        primary_key=["url"],
    )
    def curriculum_content():
        """Discovered curriculum content."""
        if include_curriculum:
            yield from _discover_curriculum_content(
                educational_stage=educational_stage,
                subject=exam_subject,
                language=language,
                max_results=max_results,
            )

    return custom_discovery, pdf_urls, exam_papers, curriculum_content


@dlt.source(name="deep_research")
def deep_research_source(
    topic: str,
    max_depth: int = 5,
    time_limit: int = 180,
    max_urls: int = 15,
):
    """
    DLT source for deep research on educational topics.

    Args:
        topic: Research topic or question
        max_depth: Maximum research depth
        time_limit: Time limit in seconds
        max_urls: Maximum URLs to analyze

    Returns:
        DLT source with research results
    """

    @dlt.resource(
        name="research_reports",
        write_disposition="append",
    )
    def research_reports():
        """Deep research reports."""
        app = _get_firecrawl_client()

        try:
            result = app.deep_research(
                topic,
                max_depth=max_depth,
                time_limit=time_limit,
                max_urls=max_urls,
            )

            if "data" in result and "finalAnalysis" in result["data"]:
                yield {
                    "topic": topic,
                    "report": result["data"]["finalAnalysis"],
                    "sources": result["data"].get("sources", []),
                    "researched_at": datetime.now(timezone.utc).isoformat(),
                    "status": "success",
                }
            else:
                yield {
                    "topic": topic,
                    "error": "No analysis produced",
                    "researched_at": datetime.now(timezone.utc).isoformat(),
                    "status": "error",
                }
        except Exception as e:
            yield {
                "topic": topic,
                "error": str(e),
                "researched_at": datetime.now(timezone.utc).isoformat(),
                "status": "error",
            }

    return research_reports
