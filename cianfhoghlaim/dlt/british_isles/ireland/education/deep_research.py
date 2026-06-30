"""
Education IE source: deep_research_source

Split from ireland/agentic_discovery.py in Phase 3D.
"""

from datetime import UTC, datetime

import dlt

from ._agentic_discovery_helpers import (
    _get_firecrawl_client,
)


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
                    "researched_at": datetime.now(UTC).isoformat(),
                    "status": "success",
                }
            else:
                yield {
                    "topic": topic,
                    "error": "No analysis produced",
                    "researched_at": datetime.now(UTC).isoformat(),
                    "status": "error",
                }
        except Exception as e:
            yield {
                "topic": topic,
                "error": str(e),
                "researched_at": datetime.now(UTC).isoformat(),
                "status": "error",
            }

    return research_reports
