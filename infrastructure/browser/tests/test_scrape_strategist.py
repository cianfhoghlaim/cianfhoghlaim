"""Tests for the high-level ``ScrapeStrategist`` and the new router methods.

These tests use mocked backends to avoid any network or container
dependency. They cover:

- :meth:`ScrapeStrategist.research_site` returns a typed ``ResearchSiteMap``
- :meth:`ScrapeStrategist.bulk_scrape` routes based on the hint's strategy
- :meth:`ScrapeStrategist.identify_ui` returns a ``UiIndicator`` with bbox
- :meth:`BackendRouter.pre_research` charges the credit budget
- :meth:`BackendRouter.pre_research` falls back when budget is exhausted
- :meth:`BackendRouter.map_site` prefers free backends
- :meth:`BackendRouter.visual_ground` returns a VisualGroundingResult
"""

from __future__ import annotations

import tempfile
from pathlib import Path
from typing import Any
from unittest.mock import AsyncMock, MagicMock

import pytest

from sruth_browser.backends.base import ResearchCapableBackend
from sruth_browser.backends.router import BackendRouter
from sruth_browser.browser_types import (
    BACKEND_COST,
    BACKEND_PRIORITY,
    BackendType,
    BrowserOperation,
    ExtractionFormat,
    ExtractionResult,
    ResearchResult,
    ScreenshotResult,
    VisualGroundingResult,
)
from sruth_browser.credit_budget import (
    BudgetExhaustedError,
    CreditBudget,
    get_budget,
    reset_budget_for_tests,
)
from sruth_browser.exceptions import NoBackendError
from sruth_browser.scrape_strategist import (
    BulkScrapeResult,
    ResearchSiteMap,
    ScrapeStrategist,
    UiIndicator,
)


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------


def make_mock_research_backend(
    backend_type: BackendType = BackendType.FIRECRAWL_MCP,
    response: dict[str, Any] | None = None,
) -> ResearchCapableBackend:
    """A ResearchCapableBackend mock that returns a canned research payload."""
    backend = MagicMock(spec=ResearchCapableBackend)
    backend.backend_type = backend_type
    backend.initialize = AsyncMock()
    backend.close = AsyncMock()
    backend.health_check = AsyncMock(return_value=True)
    backend.research = AsyncMock(
        return_value=response
        or {
            "success": True,
            "query": "test",
            "content": "# Sample\n\nPage content.",
            "sources": [
                {"url": "https://example.com/a"},
                {"url": "https://example.com/b"},
            ],
            "urls_visited": 2,
            "backend_used": backend_type.value,
            "latency_ms": 250.0,
            "creditsUsed": 2,
        }
    )
    return backend


def make_mock_map_backend(
    backend_type: BackendType = BackendType.CRAWL4AI_LOCAL,
    urls: list[str] | None = None,
) -> MagicMock:
    """A mock with map_site that returns canned URLs."""
    backend = MagicMock()
    backend.backend_type = backend_type
    backend.map_site = AsyncMock(return_value=urls or ["https://example.com/x"])
    return backend


def make_mock_scrape_backend(
    backend_type: BackendType = BackendType.CRAWL4AI_LOCAL,
    markdown: str = "# Hello\n\nWorld",
    links: list[str] | None = None,
) -> MagicMock:
    """A mock with extract/scrape that returns a canned page."""
    backend = MagicMock()
    backend.backend_type = backend_type
    result = ExtractionResult(
        success=True,
        url="https://example.com",
        content={"markdown": markdown, "links": links or ["https://example.com/a"]},
        format=ExtractionFormat.MARKDOWN,
        backend_used=backend_type,
        latency_ms=100.0,
    )
    backend.extract = AsyncMock(return_value=result)
    backend.scrape = AsyncMock(return_value=result)
    return backend


def make_mock_observe_backend(
    backend_type: BackendType = BackendType.STAGEHAND_LOCAL,
    observations: list[dict[str, Any]] | None = None,
) -> MagicMock:
    """A mock with observe() that returns a list of element observations."""
    backend = MagicMock()
    backend.backend_type = backend_type
    backend.observe = AsyncMock(
        return_value=observations
        or [
            {
                "label": "Search box",
                "bounding_box": [0.1, 0.2, 0.5, 0.3],
                "action": "type",
                "selector": "input#search",
                "confidence": 0.92,
            }
        ]
    )
    return backend


def make_mock_screenshot_backend(
    backend_type: BackendType = BackendType.STAGEHAND_LOCAL,
    success: bool = True,
) -> MagicMock:
    """A mock with screenshot() that returns a 1x1 PNG."""
    backend = MagicMock()
    backend.backend_type = backend_type
    # 1x1 transparent PNG, base64-encoded
    png_1x1 = "iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAYAAAAfFcSJAAAADUlEQVR42mNk+M9QDwADhgGAWjR9awAAAABJRU5ErkJggg=="
    backend.screenshot = AsyncMock(
        return_value=ScreenshotResult(
            success=success,
            url="https://example.com",
            image_data=png_1x1 if success else "",
            format="png",
            width=1,
            height=1,
            backend_used=backend_type,
            latency_ms=50.0,
            error=None if success else "no screenshot",
        )
    )
    return backend


@pytest.fixture(autouse=True)
def _clean_global_budget(monkeypatch, tmp_path: Path) -> None:
    """Reset the global credit budget before every test."""
    monkeypatch.setenv("BROWSER_CREDIT_DB", str(tmp_path / "budget.sqlite"))
    reset_budget_for_tests(total=20_000)


# ---------------------------------------------------------------------------
# ScrapeStrategist
# ---------------------------------------------------------------------------


class TestScrapeStrategistResearchSite:
    @pytest.mark.asyncio
    async def test_research_site_returns_typed_result(self) -> None:
        router = BackendRouter()
        router.register_backend(
            make_mock_research_backend(BackendType.FIRECRAWL_MCP)
        )
        strategist = ScrapeStrategist(router=router)

        result = await strategist.research_site(
            url="https://www.cps.gov.uk",
            goal="Identify press releases",
        )
        assert isinstance(result, ResearchSiteMap)
        assert result.url == "https://www.cps.gov.uk"
        assert result.goal == "Identify press releases"
        assert result.sitemap_urls == [
            "https://example.com/a",
            "https://example.com/b",
        ]
        assert "Sample" in result.sample_markdown
        assert result.estimated_pages == 2
        assert result.credits_spent == 2
        assert result.backend_used == "firecrawl_mcp"

    @pytest.mark.asyncio
    async def test_research_site_charges_credit_budget(self) -> None:
        router = BackendRouter()
        router.register_backend(
            make_mock_research_backend(BackendType.FIRECRAWL_MCP)
        )
        strategist = ScrapeStrategist(router=router)
        before = strategist.budget.used
        await strategist.research_site(
            url="https://x.com", goal="y", budget_hint=2
        )
        assert strategist.budget.used == before + 2

    @pytest.mark.asyncio
    async def test_research_site_prefer_free_skips_charge(self) -> None:
        router = BackendRouter()
        router.register_backend(
            make_mock_map_backend(
                BackendType.CRAWL4AI_LOCAL, urls=["https://x.com/a"]
            )
        )
        router.register_backend(
            make_mock_scrape_backend(BackendType.CRAWL4AI_LOCAL, markdown="x")
        )
        strategist = ScrapeStrategist(router=router)
        before = strategist.budget.used
        result = await strategist.research_site(
            url="https://x.com",
            goal="y",
            prefer_free=True,
        )
        assert result.backend_used == "crawl4ai_local"
        # No charge when prefer_free=True
        assert strategist.budget.used == before


class TestScrapeStrategistBulkScrape:
    @pytest.mark.asyncio
    async def test_bulk_scrape_crawl4ai_static(self) -> None:
        router = BackendRouter()
        router.register_backend(
            make_mock_scrape_backend(BackendType.CRAWL4AI_LOCAL)
        )
        strategist = ScrapeStrategist(router=router)

        result = await strategist.bulk_scrape(
            url="https://example.com/page",
            hint=ResearchSiteMap(
                url="https://example.com",
                goal="x",
                recommended_strategy="crawl4ai-static",
            ),
        )
        assert isinstance(result, BulkScrapeResult)
        assert result.success is True
        assert result.markdown.startswith("# Hello")
        assert result.bytes_in > 0
        assert result.bytes_out == len(result.markdown)
        assert result.backend_used == "crawl4ai_local"

    @pytest.mark.asyncio
    async def test_bulk_scrape_failure_returns_error(self) -> None:
        router = BackendRouter()
        bad = MagicMock()
        bad.backend_type = BackendType.CRAWL4AI_LOCAL
        bad.extract = AsyncMock(side_effect=RuntimeError("boom"))
        router.register_backend(bad)
        strategist = ScrapeStrategist(router=router)

        result = await strategist.bulk_scrape(url="https://x.com")
        assert result.success is False
        assert "boom" in (result.error or "")

    @pytest.mark.asyncio
    async def test_bulk_scrape_no_backends_raises(self) -> None:
        router = BackendRouter()
        strategist = ScrapeStrategist(router=router)
        with pytest.raises(NoBackendError):
            await strategist.bulk_scrape(url="https://x.com")


class TestScrapeStrategistIdentifyUi:
    @pytest.mark.asyncio
    async def test_no_ui_when_hint_says_so(self) -> None:
        router = BackendRouter()
        strategist = ScrapeStrategist(router=router)
        result = await strategist.identify_ui(
            url="https://x.com",
            hint=ResearchSiteMap(
                url="https://x.com",
                goal="y",
                primary_content_types=["press_release", "policy"],
            ),
        )
        assert isinstance(result, UiIndicator)
        assert result.has_ui is False

    @pytest.mark.asyncio
    async def test_yes_ui_when_hint_says_form(self) -> None:
        router = BackendRouter()
        # Single backend that has both screenshot and observe methods
        backend = make_mock_screenshot_backend(BackendType.STAGEHAND_LOCAL)
        backend.observe = AsyncMock(
            return_value=[
                {
                    "label": "Search box",
                    "bounding_box": [0.1, 0.2, 0.5, 0.3],
                    "action": "type",
                    "selector": "input#search",
                    "confidence": 0.92,
                }
            ]
        )
        router.register_backend(backend)
        strategist = ScrapeStrategist(router=router)
        result = await strategist.identify_ui(
            url="https://x.com",
            hint=ResearchSiteMap(
                url="https://x.com",
                goal="y",
                primary_content_types=["form"],
            ),
        )
        assert result.has_ui is True
        assert result.bounding_box == [0.1, 0.2, 0.5, 0.3]


class TestScrapeStrategistCredit:
    def test_credit_summary_shape(self) -> None:
        strategist = ScrapeStrategist()
        summary = strategist.credit_summary()
        assert summary["total"] == 20_000
        assert summary["used"] == 0
        assert summary["remaining"] == 20_000
        assert "by_backend" in summary


# ---------------------------------------------------------------------------
# BackendRouter.pre_research
# ---------------------------------------------------------------------------


class TestRouterPreResearch:
    @pytest.mark.asyncio
    async def test_charges_paid_backend(self) -> None:
        router = BackendRouter()
        router.register_backend(
            make_mock_research_backend(BackendType.FIRECRAWL_MCP)
        )
        budget = router._budget
        before = budget.used
        result = await router.pre_research(
            url="https://x.com", goal="y", budget_hint=3
        )
        assert result.success is True
        assert result.backend_used == BackendType.FIRECRAWL_MCP
        assert budget.used == before + 3

    @pytest.mark.asyncio
    async def test_falls_back_to_free_when_budget_exhausted(self) -> None:
        router = BackendRouter()
        router.register_backend(
            make_mock_research_backend(BackendType.FIRECRAWL_MCP)
        )
        router.register_backend(
            make_mock_map_backend(
                BackendType.CRAWL4AI_LOCAL, urls=["https://x.com/a"]
            )
        )
        router.register_backend(
            make_mock_scrape_backend(BackendType.CRAWL4AI_LOCAL, markdown="x")
        )
        # Drain the budget so the pre_research call must fall back
        router._budget.charge(router._budget.total, backend="setup")
        result = await router.pre_research(url="https://x.com", goal="y", budget_hint=2)
        assert result.backend_used == BackendType.CRAWL4AI_LOCAL
        # Free fallback should not have charged any more credits
        # (the drain was the only charge)
        assert result.metadata.get("fallback") == "free_pre_research"

    @pytest.mark.asyncio
    async def test_prefer_free_skips_paid(self) -> None:
        router = BackendRouter()
        router.register_backend(
            make_mock_research_backend(BackendType.FIRECRAWL_MCP)
        )
        router.register_backend(
            make_mock_map_backend(
                BackendType.CRAWL4AI_LOCAL, urls=["https://x.com/a"]
            )
        )
        router.register_backend(
            make_mock_scrape_backend(BackendType.CRAWL4AI_LOCAL, markdown="x")
        )
        budget = router._budget
        before = budget.used
        result = await router.pre_research(
            url="https://x.com", goal="y", prefer_free=True
        )
        assert result.backend_used == BackendType.CRAWL4AI_LOCAL
        assert budget.used == before  # no charge

    @pytest.mark.asyncio
    async def test_falls_back_when_paid_backend_raises(self) -> None:
        router = BackendRouter()
        bad = MagicMock(spec=ResearchCapableBackend)
        bad.backend_type = BackendType.FIRECRAWL_MCP
        bad.research = AsyncMock(side_effect=RuntimeError("API down"))
        router.register_backend(bad)
        router.register_backend(
            make_mock_map_backend(
                BackendType.CRAWL4AI_LOCAL, urls=["https://x.com/a"]
            )
        )
        router.register_backend(
            make_mock_scrape_backend(BackendType.CRAWL4AI_LOCAL, markdown="x")
        )
        result = await router.pre_research(url="https://x.com", goal="y")
        assert result.backend_used == BackendType.CRAWL4AI_LOCAL
        # The bad backend should have its circuit breaker failure count incremented
        assert router._circuits[BackendType.FIRECRAWL_MCP]._failure_count == 1


# ---------------------------------------------------------------------------
# BackendRouter.map_site
# ---------------------------------------------------------------------------


class TestRouterMapSite:
    @pytest.mark.asyncio
    async def test_prefers_free_backend(self) -> None:
        router = BackendRouter()
        router.register_backend(
            make_mock_map_backend(
                BackendType.CRAWL4AI_LOCAL, urls=["https://x.com/a", "https://x.com/b"]
            )
        )
        result = await router.map_site(url="https://x.com")
        assert result == ["https://x.com/a", "https://x.com/b"]

    @pytest.mark.asyncio
    async def test_prefer_free_false_uses_any(self) -> None:
        router = BackendRouter()
        router.register_backend(
            make_mock_map_backend(
                BackendType.CRAWL4AI_LOCAL, urls=["https://x.com/a"]
            )
        )
        result = await router.map_site(url="https://x.com", prefer_free=False)
        assert result == ["https://x.com/a"]

    @pytest.mark.asyncio
    async def test_no_backend_raises(self) -> None:
        router = BackendRouter()
        with pytest.raises(NoBackendError):
            await router.map_site(url="https://x.com")

    @pytest.mark.asyncio
    async def test_backend_without_map_raises(self) -> None:
        router = BackendRouter()
        # Register a backend in the priority list that doesn't have map_site
        no_map = MagicMock()
        no_map.backend_type = BackendType.CRAWL4AI_LOCAL
        # Deliberately no map_site attribute
        del no_map.map_site
        router.register_backend(no_map)
        # The priority list also includes FIRECRAWL_MCP for MAP_SITE; if not
        # registered, the free path should pick CRAWL4AI but it has no
        # map_site, so we expect BackendError.
        from sruth_browser.exceptions import BackendError
        with pytest.raises(BackendError):
            await router.map_site(url="https://x.com")


# ---------------------------------------------------------------------------
# BackendRouter.visual_ground
# ---------------------------------------------------------------------------


class TestRouterVisualGround:
    @pytest.mark.asyncio
    async def test_uses_free_observe_backend(self) -> None:
        router = BackendRouter()
        router.register_backend(
            make_mock_observe_backend(BackendType.STAGEHAND_LOCAL)
        )
        result = await router.visual_ground(
            image_data="aGVsbG8=",
            query="the search box",
        )
        assert isinstance(result, VisualGroundingResult)
        assert result.success is True
        assert result.bounding_box == [0.1, 0.2, 0.5, 0.3]
        assert result.backend_used == BackendType.STAGEHAND_LOCAL

    @pytest.mark.asyncio
    async def test_no_backend_raises(self) -> None:
        router = BackendRouter()
        with pytest.raises(NoBackendError):
            await router.visual_ground(image_data="x", query="y")

    @pytest.mark.asyncio
    async def test_no_observations_returns_failure(self) -> None:
        router = BackendRouter()
        empty_backend = MagicMock()
        empty_backend.backend_type = BackendType.STAGEHAND_LOCAL
        empty_backend.observe = AsyncMock(return_value=[])
        router.register_backend(empty_backend)
        result = await router.visual_ground(
            image_data="x", query="y"
        )
        assert result.success is False
        assert result.bounding_box is None


# ---------------------------------------------------------------------------
# BackendOperation enum coverage
# ---------------------------------------------------------------------------


class TestNewOperations:
    def test_map_site_in_enum(self) -> None:
        assert BrowserOperation.MAP_SITE.value == "map_site"
        assert BrowserOperation.MAP_SITE in BACKEND_PRIORITY

    def test_visual_grounding_in_enum(self) -> None:
        assert BrowserOperation.VISUAL_GROUNDING.value == "visual_grounding"
        assert BrowserOperation.VISUAL_GROUNDING in BACKEND_PRIORITY

    def test_map_site_prefers_free(self) -> None:
        # CRAWL4AI is $0 and listed first
        priority = BACKEND_PRIORITY[BrowserOperation.MAP_SITE]
        assert priority[0] == BackendType.CRAWL4AI_LOCAL
        # The paid Firecrawl is the fallback
        assert BackendType.FIRECRAWL_MCP in priority
        assert BACKEND_COST[BackendType.CRAWL4AI_LOCAL] == 0

    def test_visual_grounding_prefers_free(self) -> None:
        priority = BACKEND_PRIORITY[BrowserOperation.VISUAL_GROUNDING]
        # First entry should be a free backend
        assert BACKEND_COST[priority[0]] == 0
        # Paid ZAI is the last-resort fallback
        assert priority[-1] == BackendType.ZAI_VISION
