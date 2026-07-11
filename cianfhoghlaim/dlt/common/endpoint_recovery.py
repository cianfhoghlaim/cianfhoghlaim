"""Canonical endpoint-recovery helper for the Cianfhoghlaim DLT layer.

Every British Isles + EU institutional + EU nations + Commonwealth +
Americas DLT source routes its outbound network call through
``endpoint_recovery.fetch(url)``.

The helper tries three strategies in order:

1. **Plain HTTP crawl** via :func:`dlt.common.site_crawler.crawl_site`
   for endpoints that respond with 200 to a browser User-Agent.
2. **Firecrawl ``stealth`` proxy** for WAF-protected endpoints (403
   to plain HTTP). Implemented as a thin wrapper around the
   Firecrawl MCP ``firecrawl_scrape`` tool when available; falls
   back to the Firecrawl Python SDK otherwise.
3. **Wayback Machine fallback** (``web.archive.org/web/2024/<url>``)
   for endpoints that 403 even with stealth or that time-out.

Every call returns a :class:`RecoveredPage` dataclass and emits a
structlog ``endpoint_status{status, backend_used}`` event for
observability (the Dagster ``endpoint_health_sink`` L2 asset reads
the same module's :func:`probe_all_39` helper every 6 hours).

Per the
`2026-07-12-british-isles-endpoint-recovery-v1 <../../../openspec/changes/2026-07-12-british-isles-endpoint-recovery-v1/>`_
change, every DLT source that previously imported ``requests`` or
``httpx`` MUST migrate to this helper.
"""
from __future__ import annotations

import asyncio
import hashlib
import os
import time
from dataclasses import dataclass, field
from enum import Enum
from typing import Any

import structlog

logger = structlog.get_logger(__name__)


class EndpointRecoveryStrategy(str, Enum):
    """The recovery strategies the helper tries in order."""

    AUTO = "auto"
    STEALTH = "stealth"
    WAYBACK = "wayback"


class BackendUsed(str, Enum):
    """Which backend actually served the response."""

    DIRECT = "direct"
    FIRECRAWL_STEALTH = "firecrawl_stealth"
    FIRECRAWL_AUTO = "firecrawl_auto"
    WAYBACK = "wayback"
    NONE = "none"


# The 39 canonical British Isles endpoints. Mirrors
# `docs/agents/british_isles_endpoint_health_audit.md`.
PROBE_LIST: tuple[tuple[str, str], ...] = (
    # Ireland — education
    ("dlt.british_isles.ireland.education.ncca", "https://ncca.ie/en/"),
    ("dlt.british_isles.ireland.education.curriculumonline_syllabi", "https://www.curriculumonline.ie/en/senior-cycle/senior-cycle-subjects"),
    ("dlt.british_isles.ireland.education.examinations", "https://www.examinations.ie/"),
    ("dlt.british_isles.ireland.education.gov_ie_circulars", "https://www.gov.ie/en/circulars/"),
    # Ireland — law
    ("dlt.british_isles.ireland.law.courts_ie", "https://www.courts.ie/"),
    ("dlt.british_isles.ireland.law.irish_statute_book", "https://www.irishstatutebook.ie/"),
    ("dlt.british_isles.ireland.law.justice", "https://www.justice.ie/"),
    ("dlt.british_isles.ireland.law.workplace_relations", "https://www.workplacerelations.ie/en/"),
    ("dlt.british_isles.ireland.law.citizensinformation", "https://www.citizensinformation.ie/en/"),
    # Ireland — medicine
    ("dlt.british_isles.ireland.medicine.hse", "https://www.hse.ie/eng/"),
    ("dlt.british_isles.ireland.medicine.hpsc", "https://www.hpsc.ie/"),
    ("dlt.british_isles.ireland.medicine.medical_council", "https://www.medicalcouncil.ie/"),
    # Ireland — statistics
    ("dlt.british_isles.ireland.statistics.cso", "https://www.cso.ie/en/index.html"),
    ("dlt.british_isles.ireland.statistics.met_office", "https://www.met.ie/"),
    # Scotland
    ("dlt.british_isles.scotland.education.sqa", "https://www.sqa.org.uk/supporting-others/"),
    ("dlt.british_isles.scotland.education.curriculum_for_excellence", "https://education.gov.scot/curriculum-for-excellence/"),
    ("dlt.british_isles.scotland.law.legislation", "https://www.legislation.gov.uk/asp"),
    ("dlt.british_isles.scotland.medicine.nhs_scotland", "https://www.nhsinform.scot/"),
    # Wales
    ("dlt.british_isles.wales.education.wjec", "https://www.wjec.co.uk/"),
    ("dlt.british_isles.wales.law.legislation", "https://www.legislation.gov.uk/anaw"),
    ("dlt.british_isles.wales.medicine.nhs_wales", "https://phw.nhs.wales/"),
    # England
    ("dlt.british_isles.england.education.aqa", "https://www.aqa.org.uk/find-past-papers-and-mark-schemes"),
    ("dlt.british_isles.england.education.pearson", "https://qualifications.pearson.com/en/qualifications/edexcel-gcses.html"),
    ("dlt.british_isles.england.law.legislation", "https://www.legislation.gov.uk/ukpga"),
    ("dlt.british_isles.england.medicine.nhs_england", "https://www.nhs.uk/"),
    ("dlt.british_isles.england.medicine.nice", "https://www.nice.org.uk/"),
    ("dlt.british_isles.england.medicine.gmc", "https://www.gmc-uk.org/"),
    # Northern Ireland
    ("dlt.british_isles.northern_ireland.education.ccea", "https://ccea.org.uk/"),
    ("dlt.british_isles.northern_ireland.education.education_ni", "https://www.education-ni.gov.uk/"),
    ("dlt.british_isles.northern_ireland.medicine.nidirect", "https://www.nidirect.gov.uk/"),
    ("dlt.british_isles.northern_ireland.law.legislation", "https://www.legislation.gov.uk/nisr"),
    # Crown Dependencies
    ("dlt.british_isles.isle_of_man.education.isle_of_man", "https://www.gov.im/categories/education-training-and-careers/"),
    ("dlt.british_isles.isle_of_man.law.legislation", "https://legislation.gov.im/"),
    ("dlt.british_isles.jersey.education.channel_islands", "https://www.gov.je/Pages/default.aspx"),
    ("dlt.british_isles.jersey.law.legislation", "https://www.jerseylaw.je/Pages/default.aspx"),
    ("dlt.british_isles.guernsey.education.channel_islands", "https://www.gov.gg/education"),
    ("dlt.british_isles.guernsey.law.legislation", "https://www.guernseylegalresources.gg/legislation"),
    ("dlt.british_isles.guernsey.medicine.health_social_care", "https://www.gov.gg/health-social-care"),
)


@dataclass
class RecoveredPage:
    """The result of a single ``endpoint_recovery.fetch`` call."""

    url: str
    status: int = 0
    backend_used: BackendUsed = BackendUsed.NONE
    content: str | None = None
    content_hash: str = ""
    language: str | None = None
    response_time_ms: int = 0
    wayback_snapshot_url: str | None = None
    firecrawl_metadata: dict[str, Any] = field(default_factory=dict)
    error: str | None = None

    @property
    def ok(self) -> bool:
        return self.status in (200, 201, 204)

    def to_dict(self) -> dict[str, Any]:
        return {
            "url": self.url,
            "status": self.status,
            "backend_used": self.backend_used.value,
            "content_hash": self.content_hash,
            "language": self.language,
            "response_time_ms": self.response_time_ms,
            "wayback_snapshot_url": self.wayback_snapshot_url,
            "error": self.error,
        }


def _browser_user_agent() -> str:
    return (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 13_0) "
        "AppleWebKit/605.1.15 (KHTML, like Gecko) Version/17.0 "
        "Safari/605.1.15"
    )


def _hash_content(content: str) -> str:
    return f"sha256:{hashlib.sha256(content.encode('utf-8')).hexdigest()[:16]}"


async def _fetch_direct(url: str, timeout: float = 12.0) -> RecoveredPage:
    """Strategy 1: plain HTTP via curl-style GET."""
    loop = asyncio.get_event_loop()
    start = time.monotonic()

    def _do_request() -> tuple[int, str, dict[str, str]]:
        try:
            import httpx  # type: ignore[import-not-found]

            response = httpx.get(
                url,
                timeout=timeout,
                follow_redirects=True,
                headers={
                    "User-Agent": _browser_user_agent(),
                    "Accept": "text/html,application/xhtml+xml",
                    "Accept-Language": "en-GB,en;q=0.9",
                },
            )
            return response.status_code, response.text, dict(response.headers)
        except Exception as exc:
            return 0, "", {"error": str(exc)}

    status, content, headers = await loop.run_in_executor(None, _do_request)
    elapsed_ms = int((time.monotonic() - start) * 1000)
    return RecoveredPage(
        url=url,
        status=status,
        backend_used=BackendUsed.DIRECT if status else BackendUsed.NONE,
        content=content if content else None,
        content_hash=_hash_content(content) if content else "",
        language=headers.get("content-language") or headers.get("Content-Language"),
        response_time_ms=elapsed_ms,
        error=headers.get("error"),
    )


async def _fetch_firecrawl(
    url: str,
    *,
    strategy: EndpointRecoveryStrategy,
    wait_for: float = 8.0,
) -> RecoveredPage:
    """Strategy 2: Firecrawl (stealth or auto) via the MCP or SDK."""
    proxy = "stealth" if strategy == EndpointRecoveryStrategy.STEALTH else "auto"
    backend = (
        BackendUsed.FIRECRAWL_STEALTH if proxy == "stealth" else BackendUsed.FIRECRAWL_AUTO
    )
    start = time.monotonic()
    content = ""
    metadata: dict[str, Any] = {}

    try:
        # Try the Firecrawl Python SDK first (deterministic, testable).
        from firecrawl import FirecrawlApp  # type: ignore[import-not-found]

        api_key = os.environ.get("FIRECRAWL_API_KEY")
        if api_key:
            app = FirecrawlApp(api_key=api_key)
            result = app.scrape_url(
                url,
                params={
                    "formats": ["markdown", "links"],
                    "waitFor": int(wait_for * 1000),
                    "proxy": proxy,
                    "onlyMainContent": True,
                },
            )
            if isinstance(result, dict):
                content = (result.get("markdown") or "") + (result.get("html") or "")
                metadata = result.get("metadata") or {}
        else:
            return RecoveredPage(
                url=url,
                status=0,
                backend_used=backend,
                error="FIRECRAWL_API_KEY not set",
            )
    except ImportError:
        # Firecrawl SDK unavailable — defer to the MCP via the structured
        # FirecrawlMCPClient pattern documented in the firecrawl skill.
        try:
            from firecrawl_mcp import FirecrawlMCPClient  # type: ignore[import-not-found]

            async with FirecrawlMCPClient() as client:
                result = await client.scrape(
                    url,
                    formats=["markdown", "links"],
                    wait_for=int(wait_for * 1000),
                    proxy=proxy,
                )
            if isinstance(result, dict):
                content = result.get("markdown", "") + result.get("html", "")
                metadata = result.get("metadata", {})
        except ImportError:
            return RecoveredPage(
                url=url,
                status=0,
                backend_used=backend,
                error="firecrawl Python SDK and MCP client both unavailable",
            )

    elapsed_ms = int((time.monotonic() - start) * 1000)
    return RecoveredPage(
        url=url,
        status=200 if content else 0,
        backend_used=backend,
        content=content or None,
        content_hash=_hash_content(content) if content else "",
        language=metadata.get("language") if isinstance(metadata, dict) else None,
        response_time_ms=elapsed_ms,
        firecrawl_metadata=metadata if isinstance(metadata, dict) else {},
    )


async def _fetch_wayback(url: str) -> RecoveredPage:
    """Strategy 3: Wayback Machine fallback."""
    wayback_url = f"https://web.archive.org/web/2024/{url}"
    start = time.monotonic()
    loop = asyncio.get_event_loop()

    def _do_request() -> tuple[int, str]:
        try:
            import httpx  # type: ignore[import-not-found]

            response = httpx.get(
                wayback_url,
                timeout=15.0,
                follow_redirects=True,
                headers={
                    "User-Agent": _browser_user_agent(),
                    "Accept": "text/html,application/xhtml+xml",
                },
            )
            return response.status_code, response.text
        except Exception:
            return 0, ""

    status, content = await loop.run_in_executor(None, _do_request)
    elapsed_ms = int((time.monotonic() - start) * 1000)
    return RecoveredPage(
        url=url,
        status=status,
        backend_used=BackendUsed.WAYBACK if status else BackendUsed.NONE,
        content=content or None,
        content_hash=_hash_content(content) if content else "",
        response_time_ms=elapsed_ms,
        wayback_snapshot_url=wayback_url,
    )


async def fetch(
    url: str,
    *,
    strategy: EndpointRecoveryStrategy = EndpointRecoveryStrategy.AUTO,
    wait_for: float = 8.0,
    max_attempts: int = 3,
) -> RecoveredPage:
    """Fetch a URL with the 3-strategy recovery ladder.

    Args:
        url: The canonical endpoint URL.
        strategy: One of ``"auto"``, ``"stealth"``, or ``"wayback"``.
            ``"auto"`` tries direct → stealth → wayback in sequence.
            ``"stealth"`` skips direct and starts at Firecrawl stealth.
            ``"wayback"`` skips the first two strategies.
        wait_for: Seconds to wait for the page to render (Firecrawl only).
        max_attempts: Maximum number of strategies to attempt (1-3).

    Returns:
        :class:`RecoveredPage` with the result of the first successful
        strategy (or the last-failed strategy if all attempts 403 / time-out).
    """
    strategies: list[EndpointRecoveryStrategy]
    if strategy == EndpointRecoveryStrategy.AUTO:
        strategies = [
            EndpointRecoveryStrategy.AUTO,
            EndpointRecoveryStrategy.STEALTH,
            EndpointRecoveryStrategy.WAYBACK,
        ][:max_attempts]
    elif strategy == EndpointRecoveryStrategy.STEALTH:
        strategies = [
            EndpointRecoveryStrategy.STEALTH,
            EndpointRecoveryStrategy.WAYBACK,
        ][:max_attempts]
    else:
        strategies = [EndpointRecoveryStrategy.WAYBACK][:max_attempts]

    last = RecoveredPage(url=url)
    for strat in strategies:
        if strat == EndpointRecoveryStrategy.AUTO:
            last = await _fetch_direct(url)
        elif strat == EndpointRecoveryStrategy.STEALTH:
            last = await _fetch_firecrawl(
                url, strategy=EndpointRecoveryStrategy.STEALTH, wait_for=wait_for
            )
        else:
            last = await _fetch_wayback(url)
        logger.info(
            "endpoint_status",
            url=url,
            status=last.status,
            backend_used=last.backend_used.value,
            response_time_ms=last.response_time_ms,
            strategy=strat.value,
        )
        if last.ok:
            return last

    logger.warning(
        "endpoint_all_strategies_failed",
        url=url,
        last_status=last.status,
        last_backend=last.backend_used.value,
    )
    return last


async def probe_all_39() -> dict[str, int]:
    """Probe every canonical British Isles endpoint and return
    ``{source_id: status_code}``. Used by the
    ``endpoint_health_sink`` Dagster L2 asset + the audit doc.
    """
    results: dict[str, int] = {}
    for source_id, url in PROBE_LIST:
        page = await fetch(url, strategy=EndpointRecoveryStrategy.AUTO)
        results[source_id] = page.status
    return results


def declare_asset_check(source_id: str, url: str) -> dict[str, Any]:
    """Return the asset-check descriptor for a fixed source.

    Dagster @asset_check factory helper. Returns a dict with
    ``name``, ``url``, ``source_id`` keys; the actual check function
    is wired in ``orchestration/defs/2_materials/endpoint_health/checks.py``.
    """
    return {
        "name": f"{source_id.replace('.', '_')}_endpoint_alive",
        "source_id": source_id,
        "url": url,
    }


__all__ = [
    "BackendUsed",
    "EndpointRecoveryStrategy",
    "PROBE_LIST",
    "RecoveredPage",
    "declare_asset_check",
    "fetch",
    "probe_all_39",
]
