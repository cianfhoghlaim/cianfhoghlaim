"""Gemini Deep Research API DLT source.

Per the openspec change
`2026-09-06-adk-gemini-deep-research-control-plane-v1`, this DLT source
wraps the live Gemini Deep Research API
(https://ai.google.dev/gemini-api/docs/deep-research) and yields
`gemini_deep_research_report` rows.

The companion filesystem source lives at
`dlt_sources/filesystem/gemini_deep_research.py` and reads the
on-disk `leabharlann/gemini_deep_research/` PDFs (the corpus of past
Deep Research output). This `_shared` source wraps the API itself.

Usage:

```python
import dlt
from dlt_sources._shared.gemini_deep_research import gemini_deep_research_source

pipeline = dlt.pipeline(
    pipeline_name="gemini_deep_research_pipeline",
    destination="duckdb",
    dataset_name="oideachais_gemini_deep_research",
)

load_info = pipeline.run(
    gemini_deep_research_source(
        queries=[
            "British Isles Junior Cycle Mathematics syllabus",
            "Scottish Gaelic CfE Higher Gaelic literacy outcomes",
        ],
        max_reports_per_query=5,
    )
)
```
"""

from __future__ import annotations

import os
from collections.abc import Iterator
from datetime import datetime, timezone
from typing import Any

import dlt
import structlog

logger = structlog.get_logger(__name__)


GOOGLE_API_KEY_ENV = "GOOGLE_API_KEY"
DEFAULT_DEEP_RESEARCH_MODEL = "gemini-2.5-pro-deep-research"


@dlt.source(name="gemini_deep_research_api")
def gemini_deep_research_source(
    queries: list[str],
    *,
    max_reports_per_query: int = 5,
    max_urls_per_report: int = 10,
    model: str = DEFAULT_DEEP_RESEARCH_MODEL,
    api_key: str | None = None,
):
    """DLT source that calls the Gemini Deep Research API.

    For each query, the source submits a long-form research request and
    yields one row per synthesized report with the structured
    ``synthesized_report``, ``interactions``, ``citations``, and
    ``key_findings`` fields.

    Args:
        queries: List of long-form research queries.
        max_reports_per_query: Cap on rows yielded per query.
        max_urls_per_report: Forwarded to the Deep Research API.
        model: The Gemini model alias. Defaults to
            ``gemini-2.5-pro-deep-research``.
        api_key: API key. Falls back to the ``GOOGLE_API_KEY`` env var.
    """
    api_key = api_key or os.environ.get(GOOGLE_API_KEY_ENV)
    if not api_key:
        raise ValueError(
            "GOOGLE_API_KEY env var must be set for gemini_deep_research_source. "
            "Wire it via the Infisical vault (infisical://dev-baile/browser/google_api_key)."
        )

    @dlt.resource(
        name="gemini_deep_research_report",
        write_disposition="merge",
        primary_key=["report_id"],
        columns={
            "model": {"partition": True},
            "query_hash": {"partition": True},
        },
    )
    def reports() -> Iterator[dict[str, Any]]:
        """One row per Gemini Deep Research synthesized report."""
        try:
            from google import genai
        except ImportError as exc:
            raise RuntimeError(
                "google-genai package not installed. Install with: uv add google-genai"
            ) from exc

        client = genai.Client(api_key=api_key)

        for query in queries:
            logger.info(
                "gemini_deep_research_source.query_start",
                query=query[:100],
                model=model,
            )

            try:
                response = await_run(client, query, max_urls_per_report, model)
            except Exception as exc:
                logger.error(
                    "gemini_deep_research_source.query_failed",
                    query=query[:100],
                    error=str(exc),
                )
                continue

            row = _response_to_row(query, response, model)
            if row is None:
                continue
            yield row

    return reports


def await_run(client: Any, query: str, max_urls: int, model: str) -> dict[str, Any]:
    """Run the Deep Research call synchronously and return a normalised dict.

    The google-genai client exposes both sync + async APIs; we use the
    sync path here because DLT sources iterate synchronously.
    """
    response = client.deep_research(
        model=model,
        query=query,
        max_urls=max_urls,
    )

    interactions: list[dict[str, Any]] = []
    citations: list[dict[str, Any]] = []
    key_findings: list[str] = []
    synthesized_chunks: list[str] = []
    urls_visited = 0
    error: str | None = None

    for event in response:
        kind = getattr(event, "kind", None)
        if kind == "interaction":
            interactions.append({
                "interaction_id": getattr(event, "interaction_id", None),
                "action": getattr(event, "action", None),
                "target": getattr(event, "target", None),
                "rationale": getattr(event, "rationale", None),
            })
        elif kind == "url_visited":
            urls_visited += 1
        elif kind == "content_chunk":
            synthesized_chunks.append(getattr(event, "text", ""))
        elif kind == "citation":
            citations.append({
                "url": getattr(event, "url", None),
                "title": getattr(event, "title", None),
                "claim": getattr(event, "claim", None),
            })
        elif kind == "key_finding":
            key_findings.append(getattr(event, "text", ""))
        elif kind == "error":
            error = getattr(event, "message", "unknown error")

    return {
        "interactions": interactions,
        "citations": citations,
        "key_findings": key_findings,
        "synthesized_chunks": synthesized_chunks,
        "urls_visited": urls_visited,
        "error": error,
    }


def _response_to_row(query: str, response: dict[str, Any], model: str) -> dict[str, Any] | None:
    """Convert a normalised response to a DLT row, or return None to skip."""
    synthesized_report = "".join(response["synthesized_chunks"])
    if not synthesized_report and response["error"] is None:
        return None

    import hashlib

    report_id = hashlib.sha256(
        f"{query}:{synthesized_report}".encode("utf-8")
    ).hexdigest()[:16]

    query_hash = hashlib.sha256(query.encode("utf-8")).hexdigest()[:16]

    return {
        "report_id": report_id,
        "query": query,
        "query_hash": query_hash,
        "synthesized_report": synthesized_report,
        "interactions": response["interactions"],
        "citations": response["citations"],
        "key_findings": response["key_findings"],
        "urls_visited": response["urls_visited"],
        "model": model,
        "created_at": datetime.now(timezone.utc).isoformat(),
        "error": response["error"],
        "extraction_status": "success" if response["error"] is None else "error",
    }
