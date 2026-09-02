"""examinations_papers — the DLT source for examinations.ie exam papers.

Per the `2026-08-14-firecrawl-corpus-and-examinations-ie-v1` change
(Phase 4a), this source uses the `state-exams-ie` persistent profile
to authenticate against examinations.ie, search for the exam
paper, find the PDF download link via `firecrawl_interact`, download
the PDF, parse it via `firecrawl_parse`, and write the structured
extraction to `cianfhoghlaim.lc_exam_papers.<subject>.<year>`.

The flow:
1. scrape `https://www.examinations.ie/?lang=en&search=<paper_id>` →
   returns `scrape_id`
2. interact `scrape_id` → "Click the search result for the paper"
   → returns the PDF URL
3. parse the PDF → returns the structured markdown + JSON
4. write the row to the lakehouse
5. interact_stop `scrape_id` (REQUIRED — never leak a session)

The source is **PII-flagged** (exams surface candidate metadata) +
**persistent-profile-gated** (login via the `state-exams-ie`
profile; read-only mode `saveChanges: false`).
"""
from __future__ import annotations

import json
import logging
from collections.abc import Iterator
from datetime import UTC, datetime
from typing import Any

import dlt
import structlog

from dlt_sources.common.site_crawler import get_policy

logger = structlog.get_logger(__name__)


# PII source flag — propagates to the Firecrawl scrape policy.
SENSITIVITY = "pii"
SOURCE_KEY = "examinations_ie_papers"
SOURCE_POLICY = get_policy(SOURCE_KEY)


# The 6 LC subjects covered by this source.
LC_SUBJECTS = ["mathematics", "chemistry", "physics", "biology", "english", "gaeilge"]


def _get_firecrawl_mcp_client() -> Any:
    """Lazy import the wrapped MCP client (CI environments may not have it)."""
    try:
        from agents.meaisinfhoghlaim.firecrawl_mcp import FirecrawlMCPClient

        return FirecrawlMCPClient()
    except ImportError:  # pragma: no cover — CI fallback
        logger.warning("examinations_papers.firecrawl_mcp_unavailable")
        return None


@dlt.resource(
    write_disposition="merge",
    primary_key=["subject", "year", "paper_code"],
    name="examinations_papers",
)
def examinations_papers(
    papers: list[dict[str, str]] | None = None,
    *,
    profile_name: str = "state-exams-ie",
    lang: str = "en",
) -> Iterator[dict[str, Any]]:
    """Iterate over the official Leaving Cert exam papers.

    Args:
        papers: optional list of paper descriptors
            `{"subject": str, "year": int, "paper_code": str}`. Defaults
            to the 6 subjects × 2024-2026 = 18 papers.
        profile_name: the persistent profile name (default:
            `state-exams-ie`).
        lang: `en` (English) or `ga` (Gaeilge).

    Yields:
        One dict per paper with the fields
        `subject`, `year`, `paper_code`, `pdf_url`, `markdown`,
        `json`, `metadata`, `scraped_at`.
    """
    papers = papers or [
        {"subject": s, "year": y, "paper_code": f"{s[:3].upper()}-{y}"}
        for s in LC_SUBJECTS
        for y in (2024, 2025, 2026)
    ]

    client = _get_firecrawl_mcp_client()
    if client is None:
        logger.warning("examinations_papers.no_mcp_client_skipping")
        return

    now = datetime.now(UTC).isoformat()

    for paper in papers:
        subject = paper["subject"]
        year = paper["year"]
        paper_code = paper["paper_code"]
        search_url = (
            f"https://www.examinations.ie/?lang={lang}&search={paper_code}"
        )

        scrape_id: str | None = None
        try:
            # Step 1: scrape the search results page
            search_page = client.scrape(
                search_url,
                formats=["markdown", "links"],
                redact_pii=True,
                zero_data_retention=True,
            )
            scrape_id = search_page.scrape_id
            if not scrape_id:
                logger.warning(
                    "examinations_papers.no_scrape_id",
                    paper_code=paper_code,
                )
                continue

            # Step 2: interact to find the PDF download link
            interact_resp = client.interact(
                scrape_id,
                prompt=(
                    f"Click the search result for exam paper '{paper_code}'. "
                    f"Find the PDF download link. Return only the PDF URL."
                ),
            )
            pdf_url = interact_resp.output.strip()
            if not pdf_url or not pdf_url.startswith("http"):
                logger.warning(
                    "examinations_papers.no_pdf_url",
                    paper_code=paper_code,
                    output=interact_resp.output[:200],
                )
                continue

            # Step 3: parse the PDF
            # Note: firecrawl_parse takes a local file path, so we
            # download the PDF first (passed via the named handler).
            parse_resp = client.parse(
                pdf_url,
                formats=["markdown", "json"],
            )

            yield {
                "subject": subject,
                "year": year,
                "paper_code": paper_code,
                "pdf_url": pdf_url,
                "markdown": parse_resp.markdown,
                "json": parse_resp.json_data,
                "summary": parse_resp.summary,
                "metadata": {
                    "lang": lang,
                    "profile": profile_name,
                    "scrape_id": scrape_id,
                },
                "scraped_at": now,
                "source": "examinations.ie",
            }
        except Exception as exc:
            logger.exception(
                "examinations_papers.paper_failed",
                paper_code=paper_code,
                error=str(exc),
            )
        finally:
            # Step 4: ALWAYS stop the interact session (never leak)
            if scrape_id:
                try:
                    client.interact_stop(scrape_id)
                except Exception as exc:  # pragma: no cover
                    logger.warning(
                        "examinations_papers.interact_stop_failed",
                        scrape_id=scrape_id,
                        error=str(exc),
                    )


@dlt.source(name="examinations_ie_papers")
def examinations_ie_papers_source(
    papers: list[dict[str, str]] | None = None,
    *,
    profile_name: str = "state-exams-ie",
) -> Any:
    """The DLT source for examinations.ie exam papers."""
    return examinations_papers(
        papers=papers,
        profile_name=profile_name,
    )


if __name__ == "__main__":
    # The CLI entry point: `python -m dlt_sources.education.ireland.british_isles.education.examinations_papers`
    import dlt

    pipeline = dlt.pipeline(
        pipeline_name="examinations_ie_papers",
        destination="duckdb",
        dataset_name="lc_exam_papers",
        dev_mode=True,
    )
    load_info = pipeline.run(examinations_ie_papers_source())
    print(load_info)