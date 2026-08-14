"""examinations_marking_schemes — the DLT source for examinations.ie marking schemes.

Per the `2026-08-14-firecrawl-corpus-and-examinations-ie-v1` change
(Phase 4a), this source uses the same `state-exams-ie` persistent
profile as `examinations_papers.py` but targets the marking scheme
PDFs instead of the exam papers.

The marking scheme URLs follow the pattern
`https://www.examinations.ie/?lang=en&search=<scheme_code>` where
`<scheme_code>` is `MS-<subject>-<year>`.

The flow is identical to `examinations_papers.py` (scrape → interact
→ parse → yield → interact_stop).
"""
from __future__ import annotations

from collections.abc import Iterator
from datetime import UTC, datetime
from typing import Any

import dlt
import structlog

from dlt_sources.common.site_crawler import get_policy

logger = structlog.get_logger(__name__)


# PII source flag — propagates to the Firecrawl scrape policy.
SENSITIVITY = "pii"
SOURCE_KEY = "examinations_ie_marking"
SOURCE_POLICY = get_policy(SOURCE_KEY)


# The 6 LC subjects covered by this source.
LC_SUBJECTS = ["mathematics", "chemistry", "physics", "biology", "english", "gaeilge"]


def _get_firecrawl_mcp_client() -> Any:
    """Lazy import the wrapped MCP client."""
    try:
        from agents.meaisinfhoghlaim.firecrawl_mcp import FirecrawlMCPClient

        return FirecrawlMCPClient()
    except ImportError:  # pragma: no cover — CI fallback
        logger.warning("examinations_marking_schemes.firecrawl_mcp_unavailable")
        return None


@dlt.resource(
    write_disposition="merge",
    primary_key=["subject", "year", "scheme_code"],
    name="examinations_marking_schemes",
)
def examinations_marking_schemes(
    schemes: list[dict[str, str]] | None = None,
    *,
    profile_name: str = "state-exams-ie",
    lang: str = "en",
) -> Iterator[dict[str, Any]]:
    """Iterate over the official Leaving Cert marking schemes.

    Args:
        schemes: optional list of scheme descriptors
            `{"subject": str, "year": int, "scheme_code": str}`. Defaults
            to the 6 subjects × 2024-2026 = 18 schemes.
        profile_name: the persistent profile name (default:
            `state-exams-ie`).
        lang: `en` (English) or `ga` (Gaeilge).

    Yields:
        One dict per scheme with the fields
        `subject`, `year`, `scheme_code`, `pdf_url`, `markdown`,
        `json`, `metadata`, `scraped_at`.
    """
    schemes = schemes or [
        {"subject": s, "year": y, "scheme_code": f"MS-{s[:3].upper()}-{y}"}
        for s in LC_SUBJECTS
        for y in (2024, 2025, 2026)
    ]

    client = _get_firecrawl_mcp_client()
    if client is None:
        logger.warning("examinations_marking_schemes.no_mcp_client_skipping")
        return

    now = datetime.now(UTC).isoformat()

    for scheme in schemes:
        subject = scheme["subject"]
        year = scheme["year"]
        scheme_code = scheme["scheme_code"]
        search_url = (
            f"https://www.examinations.ie/?lang={lang}&search={scheme_code}"
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
                    "examinations_marking_schemes.no_scrape_id",
                    scheme_code=scheme_code,
                )
                continue

            # Step 2: interact to find the PDF download link
            interact_resp = client.interact(
                scrape_id,
                prompt=(
                    f"Click the search result for marking scheme '{scheme_code}'. "
                    f"Find the PDF download link. Return only the PDF URL."
                ),
            )
            pdf_url = interact_resp.output.strip()
            if not pdf_url or not pdf_url.startswith("http"):
                logger.warning(
                    "examinations_marking_schemes.no_pdf_url",
                    scheme_code=scheme_code,
                    output=interact_resp.output[:200],
                )
                continue

            # Step 3: parse the PDF
            parse_resp = client.parse(
                pdf_url,
                formats=["markdown", "json"],
            )

            yield {
                "subject": subject,
                "year": year,
                "scheme_code": scheme_code,
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
                "examinations_marking_schemes.scheme_failed",
                scheme_code=scheme_code,
                error=str(exc),
            )
        finally:
            # Step 4: ALWAYS stop the interact session (never leak)
            if scrape_id:
                try:
                    client.interact_stop(scrape_id)
                except Exception as exc:  # pragma: no cover
                    logger.warning(
                        "examinations_marking_schemes.interact_stop_failed",
                        scrape_id=scrape_id,
                        error=str(exc),
                    )


@dlt.source(name="examinations_ie_marking")
def examinations_ie_marking_source(
    schemes: list[dict[str, str]] | None = None,
    *,
    profile_name: str = "state-exams-ie",
) -> Any:
    """The DLT source for examinations.ie marking schemes."""
    return examinations_marking_schemes(
        schemes=schemes,
        profile_name=profile_name,
    )


if __name__ == "__main__":
    import dlt

    pipeline = dlt.pipeline(
        pipeline_name="examinations_ie_marking",
        destination="duckdb",
        dataset_name="lc_exam_papers",
        dev_mode=True,
    )
    load_info = pipeline.run(examinations_ie_marking_source())
    print(load_info)