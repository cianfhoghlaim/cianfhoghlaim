"""
Education IE source: agentic_discovery_source

Split from ireland/agentic_discovery.py in Phase 3D.
"""

import os
from collections.abc import Iterator
from datetime import UTC, datetime
from typing import Any
import dlt

from ._agentic_discovery_helpers import (
    _discover_curriculum_content,
    _discover_exam_papers,
    _discover_pdfs,
    _discover_with_agent,
)

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
                                    UTC
                                ).isoformat()
                                yield item
                    else:
                        yield {
                            "discovery_key": key,
                            "data": value,
                            "discovered_at": datetime.now(UTC).isoformat(),
                        }
            else:
                yield {
                    "data": data,
                    "discovered_at": datetime.now(UTC).isoformat(),
                }

        except Exception as e:
            yield {
                "error": str(e),
                "prompt": discovery_prompt,
                "discovered_at": datetime.now(UTC).isoformat(),
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
