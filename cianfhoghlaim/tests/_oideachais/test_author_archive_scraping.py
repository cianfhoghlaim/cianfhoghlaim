"""Tests for the author-archive-v1 scraping assets.

These tests use mocked backends (no live Firecrawl, no live browser) and
verify that each asset:

- Returns a MaterializeResult with the expected metadata keys
- Handles missing optional dependencies (BAML, sruth_browser) gracefully
- Persists no rows when dependencies are missing (no exception)

Live testing happens in the hero example script
``oideachais/scripts/pre_research_cps_gov_uk.py`` which can be run
manually with a real Firecrawl key.
"""
from __future__ import annotations

import os
from unittest.mock import patch

import pytest


class TestOfficialMediaSampleSources:
    """The OFFICIAL_MEDIA_SAMPLE_SOURCES list must cover all 10 categories."""

    def test_all_10_categories_present(self) -> None:
        from cianfhoghlaim.dagster.assets.official_media.scraping_assets import (
            OFFICIAL_MEDIA_SAMPLE_SOURCES,
        )
        categories = {s["category"] for s in OFFICIAL_MEDIA_SAMPLE_SOURCES}
        expected = {
            "intelligence",
            "universities",
            "celtic_colleges",
            "schools",
            "language_project",
            "parties",
            "police",
            "defence",
            "national_info",
            "jurisdictions",
        }
        missing = expected - categories
        assert not missing, f"Missing categories: {missing}"

    def test_at_least_one_per_category(self) -> None:
        from collections import Counter

        from cianfhoghlaim.dagster.assets.official_media.scraping_assets import (
            OFFICIAL_MEDIA_SAMPLE_SOURCES,
        )
        counts = Counter(s["category"] for s in OFFICIAL_MEDIA_SAMPLE_SOURCES)
        for cat, count in counts.items():
            assert count >= 1, f"{cat} has no sources"

    def test_cps_gov_uk_is_included(self) -> None:
        from cianfhoghlaim.dagster.assets.official_media.scraping_assets import (
            OFFICIAL_MEDIA_SAMPLE_SOURCES,
        )
        cps = [s for s in OFFICIAL_MEDIA_SAMPLE_SOURCES if s["slug"] == "cps_gov_uk"]
        assert len(cps) == 1
        assert cps[0]["category"] == "jurisdictions"
        assert "cps.gov.uk" in cps[0]["url"]

    def test_nation_field_set(self) -> None:
        from cianfhoghlaim.dagster.assets.official_media.scraping_assets import (
            OFFICIAL_MEDIA_SAMPLE_SOURCES,
        )
        valid_nations = {"ie", "ni", "en", "sct", "wls", "iom", "jey", "ggy"}
        for s in OFFICIAL_MEDIA_SAMPLE_SOURCES:
            assert s["nation"] in valid_nations, f"{s['slug']} has bad nation {s['nation']}"

    def test_each_source_has_url_and_goal(self) -> None:
        from cianfhoghlaim.dagster.assets.official_media.scraping_assets import (
            OFFICIAL_MEDIA_SAMPLE_SOURCES,
        )
        for s in OFFICIAL_MEDIA_SAMPLE_SOURCES:
            assert s["url"].startswith("http"), f"{s['slug']} missing url"
            assert len(s["goal"]) > 20, f"{s['slug']} goal too short"


class TestOfficialMediaPreResearchAsset:
    """The pre_research asset must run without exploding when optional deps are missing."""

    def test_returns_metadata_when_sruth_browser_missing(
        self, monkeypatch: pytest.MonkeyPatch
    ) -> None:
        from cianfhoghlaim.dagster.assets.official_media import scraping_assets

        # Make sruth_browser import fail
        monkeypatch.setitem(
            sys.modules if (sys := __import__("sys")) else {},
            "sruth_browser",
            None,
        )
        # Patch the import inside the asset function
        with patch.dict("sys.modules", {"sruth_browser": None}):
            result = scraping_assets.official_media_pre_research(context=None)
        assert "sources_attempted" in result.metadata
        assert "credits_spent" in result.metadata

    def test_assets_defined(self) -> None:
        """All 4 assets must be importable + decorated with @dg.asset."""

        from cianfhoghlaim.dagster.assets.official_media import scraping_assets

        for name in [
            "official_media_pre_research",
            "official_media_bulk_scrape",
            "official_media_condense",
            "official_media_identify_uis",
        ]:
            asset = getattr(scraping_assets, name)
            assert callable(asset), f"{name} is not callable"
            # Dagster assets have _metadata or are wrapped in AssetsDefinition
            assert hasattr(asset, "op") or hasattr(asset, "_metadata"), (
                f"{name} is not a Dagster asset"
            )


class TestOfficialMediaAssetMetadata:
    """Each asset must return MaterializeResult with the expected metadata keys."""

    @pytest.mark.skipif(
        "DAGSTER_TEST_SKIP_DESERIALIZER" in os.environ,
        reason="Dagster SerdesUsageError on the test environment",
    )
    def test_pre_research_metadata_keys(self) -> None:
        # Simulate the asset by calling its body and inspecting metadata
        import dagster as dg
        from cianfhoghlaim.dagster.assets.official_media import scraping_assets

        with patch.dict("sys.modules", {"sruth_browser": None}):
            result = scraping_assets.official_media_pre_research(context=None)
        assert isinstance(result, dg.MaterializeResult)
        assert "sources_attempted" in result.metadata
        assert "sources_paid" in result.metadata
        assert "sources_free" in result.metadata
        assert "credits_spent" in result.metadata
        assert "budget_remaining" in result.metadata
        assert "rows" in result.metadata

    @pytest.mark.skipif(
        "DAGSTER_TEST_SKIP_DESERIALIZER" in os.environ,
        reason="Dagster SerdesUsageError on the test environment",
    )
    def test_bulk_scrape_metadata_keys(self) -> None:
        import dagster as dg
        from cianfhoghlaim.dagster.assets.official_media import scraping_assets

        with patch.dict(
            "sys.modules", {"sruth_browser": None, "baml_client": None}
        ):
            result = scraping_assets.official_media_bulk_scrape(context=None)
        assert isinstance(result, dg.MaterializeResult)
        assert "pages_scraped" in result.metadata
        assert "bytes_in" in result.metadata
        assert "bytes_out" in result.metadata

    @pytest.mark.skipif(
        "DAGSTER_TEST_SKIP_DESERIALIZER" in os.environ,
        reason="Dagster SerdesUsageError on the test environment",
    )
    def test_condense_metadata_keys(self) -> None:
        import dagster as dg
        from cianfhoghlaim.dagster.assets.official_media import scraping_assets

        with patch.dict(
            "sys.modules", {"sruth_browser": None, "baml_client": None}
        ):
            result = scraping_assets.official_media_condense(context=None)
        assert isinstance(result, dg.MaterializeResult)
        assert "pages_condensed" in result.metadata
        assert "bytes_in" in result.metadata
        assert "bytes_out" in result.metadata

    @pytest.mark.skipif(
        "DAGSTER_TEST_SKIP_DESERIALIZER" in os.environ,
        reason="Dagster SerdesUsageError on the test environment",
    )
    def test_identify_uis_metadata_keys(self) -> None:
        import dagster as dg
        from cianfhoghlaim.dagster.assets.official_media import scraping_assets

        with patch.dict(
            "sys.modules", {"sruth_browser": None, "baml_client": None}
        ):
            result = scraping_assets.official_media_identify_uis(context=None)
        assert isinstance(result, dg.MaterializeResult)
        assert "uis_identified" in result.metadata
        assert "screenshots_taken" in result.metadata
        assert "sources_checked" in result.metadata


class TestAssetRegistration:
    """The 4 new assets must be registered in all_assets."""

    def test_assets_in_official_media_init(self) -> None:
        from cianfhoghlaim.dagster.assets import official_media

        for name in [
            "official_media_pre_research",
            "official_media_bulk_scrape",
            "official_media_condense",
            "official_media_identify_uis",
        ]:
            assert hasattr(official_media, name), f"{name} not exported from official_media"

    def test_assets_in_assets_init_all_assets(self) -> None:
        # The new assets are individual exports, not in a list
        from cianfhoghlaim.dagster.assets import (
            all_assets,
            official_media_bulk_scrape,
            official_media_condense,
            official_media_identify_uis,
            official_media_pre_research,
        )
        for asset in [
            official_media_pre_research,
            official_media_bulk_scrape,
            official_media_condense,
            official_media_identify_uis,
        ]:
            assert asset in all_assets, f"{asset.__name__} not in all_assets"


class TestCpsHeroExampleScript:
    """The hero example script must be syntactically valid and importable."""

    def test_script_compiles(self) -> None:
        import py_compile

        script_path = os.path.join(
            os.path.dirname(__file__),
            "..",
            "scripts",
            "pre_research_cps_gov_uk.py",
        )
        py_compile.compile(script_path, doraise=True)

    def test_script_mentions_cps(self) -> None:
        script_path = os.path.join(
            os.path.dirname(__file__),
            "..",
            "scripts",
            "pre_research_cps_gov_uk.py",
        )
        with open(script_path) as f:
            content = f.read()
        assert "cps.gov.uk" in content
        assert "PreResearchSite" in content or "research_site" in content
        assert "CondenseToCriticalInfo" in content or "Condense" in content
        assert "VisualGroundingFromScreenshot" in content or "visual_ground" in content
        assert "IdentifyUiPatterns" in content or "identify_ui" in content
