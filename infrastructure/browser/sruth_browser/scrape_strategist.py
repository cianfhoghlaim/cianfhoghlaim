"""Thin wrapper around ``BackendRouter`` for the ``author-archive-v1`` pipeline.

The :class:`ScrapeStrategist` is the single entry point used by the
oideachais Dagster assets. It:

- picks the cheapest viable backend for each call (Crawl4AI for bulk
  scraping, Firecrawl only for pre-research and anti-bot pages)
- guards every paid call with the global :class:`~sruth_browser.CreditBudget`
- returns plain dataclasses (``ResearchSiteMap``, ``BulkScrapeResult``,
  ``UiIndicator``) that map 1:1 to the BAML classes in
  ``baml_src/author_archive.baml``
- never raises :class:`~sruth_browser.BudgetExhaustedError` to the
  caller; instead it falls back to a free backend

Usage::

    from sruth_browser import ScrapeStrategist

    strategist = ScrapeStrategist()
    sitemap = await strategist.research_site(
        url="https://www.cps.gov.uk",
        goal="Identify all press releases, prosecution guidance, "
             "and case decision databases published 2020-2026.",
    )
    page = await strategist.bulk_scrape(
        url="https://www.cps.gov.uk/news/...",
        hint=sitemap,
    )
    ui = await strategist.identify_ui(
        url="https://www.cps.gov.uk/search",
        hint=sitemap,
    )
    print(strategist.credit_summary())
"""

from __future__ import annotations

import time
from dataclasses import dataclass, field
from typing import Any

import structlog

from .backends.router import BackendRouter, get_router
from .browser_types import (
    BackendType,
    BrowserOperation,
    ExtractionFormat,
    ResearchResult,
    VisualGroundingResult,
)
from .credit_budget import CreditBudget, get_budget
from .exceptions import NoBackendError

logger = structlog.get_logger()


@dataclass
class ResearchSiteMap:
    """Structured pre-research record. Mirrors the BAML class.

    This is the type stored in the ``official_media.research_sitemap`` table
    by the Dagster asset.
    """

    url: str
    goal: str
    sitemap_urls: list[str] = field(default_factory=list)
    site_structure_summary: str = ""
    primary_content_types: list[str] = field(default_factory=list)
    recommended_strategy: str = "crawl4ai-static"
    recommended_schema: dict[str, Any] = field(default_factory=dict)
    estimated_pages: int = 0
    estimated_credits: int = 0
    pre_researched_at: str = ""
    backend_used: str = ""
    credits_spent: int = 0
    sample_markdown: str = ""
    raw_sources: list[dict[str, Any]] = field(default_factory=list)
    metadata: dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_research_result(
        cls,
        url: str,
        goal: str,
        result: ResearchResult,
    ) -> ResearchSiteMap:
        """Build a ResearchSiteMap from a router-level ResearchResult.

        The BAML ``SummarizeSite`` function is expected to run downstream
        to fill in ``site_structure_summary``, ``primary_content_types``,
        ``recommended_schema``. This constructor just transcribes what
        the router already knows.
        """
        return cls(
            url=url,
            goal=goal,
            sitemap_urls=[s.get("url", "") for s in result.sources if s.get("url")],
            sample_markdown=result.content,
            backend_used=(
                result.backend_used.value
                if result.backend_used is not None
                else "unknown"
            ),
            pre_researched_at=time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
            raw_sources=list(result.sources),
            estimated_pages=result.urls_visited,
            credits_spent=int(
                result.metadata.get("credits_spent_this_call", 0)
            )
            if result.metadata
            else 0,
            metadata=result.metadata or {},
        )


@dataclass
class BulkScrapeResult:
    """The result of a single bulk scrape call."""

    url: str
    markdown: str
    html: str
    links: list[str]
    screenshot_b64: str | None
    backend_used: str
    latency_ms: float
    bytes_in: int
    bytes_out: int
    success: bool
    error: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


@dataclass
class UiIndicator:
    """Mirrors the BAML ``UiIndicator`` class."""

    has_ui: bool
    ui_type: str | None = None
    visual_screenshot_path: str | None = None
    grounding_prompt: str | None = None
    bounding_box: list[float] | None = None
    backend_used: str = ""
    confidence: float | None = None
    metadata: dict[str, Any] = field(default_factory=dict)


class ScrapeStrategist:
    """Single entry point for the author-archive-v1 scraping pipeline.

    Wraps :class:`BackendRouter` and adds:
    - credit-budget-aware routing
    - typed return values that match the BAML schema
    - a thin convenience API for the Dagster assets
    """

    def __init__(
        self,
        router: BackendRouter | None = None,
        budget: CreditBudget | None = None,
    ):
        self.router = router or get_router()
        self.budget = budget or get_budget()

    async def research_site(
        self,
        url: str,
        goal: str,
        *,
        budget_hint: int = 2,
        prefer_free: bool = False,
    ) -> ResearchSiteMap:
        """Run a pre-research pass for ``url``.

        Returns a :class:`ResearchSiteMap` ready to be upserted into the
        ``official_media.research_sitemap`` LanceDB table.
        """
        result = await self.router.pre_research(
            url=url,
            goal=goal,
            budget_hint=budget_hint,
            prefer_free=prefer_free,
        )
        return ResearchSiteMap.from_research_result(url, goal, result)

    async def bulk_scrape(
        self,
        url: str,
        hint: ResearchSiteMap | None = None,
        *,
        formats: list[ExtractionFormat] | None = None,
        schema: dict[str, Any] | None = None,
        prefer_free: bool = True,
    ) -> BulkScrapeResult:
        """Scrape a single page using the strategy from ``hint``."""
        formats = formats or [ExtractionFormat.MARKDOWN]

        if hint is not None and hint.recommended_strategy == "stagehand-interactive":
            prefer_free = False
        if hint is not None and hint.recommended_strategy == "firecrawl-agent":
            prefer_free = False

        backend_type = await self.router.select_backend(BrowserOperation.SCRAPE)
        if backend_type is None:
            raise NoBackendError(BrowserOperation.SCRAPE.value)

        backend = self.router._backends[backend_type]
        start_time = time.perf_counter()
        try:
            extract_fn = getattr(backend, "extract", None) or getattr(backend, "scrape", None)
            if extract_fn is None:
                raise RuntimeError(
                    f"Backend {backend_type.value} has no extract/scrape method"
                )
            result = await extract_fn(
                url,
                formats=formats,
                schema=schema,
            )
            await self.router._circuits[backend_type].record_success(
                (time.perf_counter() - start_time) * 1000
            )
        except Exception as e:
            await self.router._circuits[backend_type].record_failure(str(e))
            logger.warning(
                "bulk_scrape_failed",
                url=url,
                backend=backend_type.value,
                error=str(e),
            )
            return BulkScrapeResult(
                url=url,
                markdown="",
                html="",
                links=[],
                screenshot_b64=None,
                backend_used=backend_type.value,
                latency_ms=(time.perf_counter() - start_time) * 1000,
                bytes_in=0,
                bytes_out=0,
                success=False,
                error=str(e),
            )

        content = result.content if hasattr(result, "content") else {}
        markdown = content.get("markdown", "")
        html = content.get("html", "") or content.get("rawHtml", "")
        links = content.get("links", [])
        screenshot = content.get("screenshot")
        return BulkScrapeResult(
            url=url,
            markdown=markdown,
            html=html,
            links=links,
            screenshot_b64=screenshot,
            backend_used=backend_type.value,
            latency_ms=getattr(result, "latency_ms", 0.0),
            bytes_in=len(markdown) + len(html),
            bytes_out=len(markdown),
            success=getattr(result, "success", True),
            error=getattr(result, "error", None),
            metadata=getattr(result, "metadata", {}),
        )

    async def identify_ui(
        self,
        url: str,
        *,
        hint: ResearchSiteMap | None = None,
        query: str = "any interactive element on the page",
    ) -> UiIndicator:
        """Identify the dominant UI on a page."""
        ui_types = {"form", "search_box", "dashboard", "map", "login_wall"}
        if hint is not None and not any(
            t in ui_types for t in hint.primary_content_types
        ):
            return UiIndicator(has_ui=False, backend_used="heuristic")

        screenshot = await self.router.screenshot(url=url)
        if not screenshot.success or not screenshot.image_data:
            return UiIndicator(
                has_ui=True,
                ui_type="unknown",
                backend_used="screenshot_failed",
            )

        grounding = await self.router.visual_ground(
            image_data=screenshot.image_data,
            query=query,
        )
        return UiIndicator(
            has_ui=grounding.success,
            ui_type="form" if grounding.success else None,
            visual_screenshot_path=f"memory://{url}",
            grounding_prompt=query,
            bounding_box=list(grounding.bounding_box) if grounding.bounding_box else None,
            backend_used=(
                grounding.backend_used.value
                if grounding.backend_used is not None
                else "unknown"
            ),
            confidence=grounding.confidence,
            metadata=grounding.metadata or {},
        )

    def credit_summary(self) -> dict[str, Any]:
        """Return the current credit budget state for dashboards."""
        return self.budget.get_summary()

    def recent_charges(self, limit: int = 50) -> list[dict[str, Any]]:
        """Return the most recent credit charges for debugging."""
        return self.budget.recent_charges(limit=limit)


__all__ = [
    "ScrapeStrategist",
    "ResearchSiteMap",
    "BulkScrapeResult",
    "UiIndicator",
]
