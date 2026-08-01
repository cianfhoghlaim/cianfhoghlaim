"""Dagster Component for Browser automation resources.

Provides browser scraping resources with circuit breaker fallback.

Example YAML:
    type: sruth.shared.dagster.components.BrowserResourceComponent
    attributes:
      name: "browser"
      preferred_backend: "stagehand"
      headless: true
      timeout: 30.0
"""

from __future__ import annotations

from dataclasses import dataclass, field

import dagster as dg


@dataclass
class BrowserResourceComponent(dg.Component, dg.Resolvable, dg.Model):
    """
    Dagster component for browser automation resources.

    Integrates with the sruth browser stack to provide:
    - Stagehand (AI-powered navigation)
    - Crawl4AI (bulk extraction)
    - Browserbase/Firecrawl (cloud fallback)

    Automatic backend selection based on operation type and cost.
    """

    # Resource name
    name: str = "browser"

    # Backend preferences
    preferred_backend: str = "stagehand"  # "stagehand", "crawl4ai", "browserbase", "auto"
    headless: bool = True
    timeout: float = 30.0

    # Backend enablement
    enable_cdp: bool = True
    enable_crawl4ai: bool = True
    enable_stagehand: bool = True
    enable_skyvern: bool = False
    enable_browserbase: bool = False
    enable_firecrawl: bool = False

    # Stagehand configuration
    stagehand_model: str = "glm-4.6"
    stagehand_api_key: str = ""

    def build_defs(self, context: dg.ComponentLoadContext) -> dg.Definitions:
        """Build browser resource."""
        from sruth.shared.dagster.resources import BrowserResource

        resource = BrowserResource(
            preferred_backend=self.preferred_backend,
            headless=self.headless,
            timeout=self.timeout,
        )

        return dg.Definitions(
            resources={
                self.name: resource,
                "browser": resource,  # Also register as default
            }
        )


@dataclass
class BrowserScrapeComponent(dg.Component, dg.Resolvable, dg.Model):
    """
    Dagster component for browser scraping assets.

    Creates assets that scrape web pages using the browser stack.
    """

    # Asset identification
    asset_key: list[str] = field(default_factory=list)
    asset_name: str = ""
    group_name: str = "scraping"
    description: str = ""

    # URLs to scrape
    urls: list[str] = field(default_factory=list)
    url_pattern: str = ""  # For dynamic URL generation

    # Scraping configuration
    extract_instruction: str = ""
    extract_formats: list[str] = field(default_factory=lambda: ["markdown"])

    # Browser settings
    browser_backend: str = "stagehand"
    headless: bool = True
    screenshot: bool = False

    # Partitioning (for multi-URL scraping)
    partition_by_url: bool = False

    def build_defs(self, context: dg.ComponentLoadContext) -> dg.Definitions:
        """Build scraping assets."""
        asset_name = self.asset_name or self.asset_key[-1] if self.asset_key else "scraped_data"

        if self.partition_by_url and self.urls:
            # Create partitioned asset by URL
            partitions_def = dg.StaticPartitionsDefinition(self.urls)

            @dg.asset(
                key=self.asset_key or [asset_name],
                name=asset_name,
                group_name=self.group_name,
                partitions_def=partitions_def,
                description=self.description or f"Scraped from {len(self.urls)} URLs",
                compute_kind="browser",
            )
            def scraped_asset(context: dg.AssetExecutionContext) -> dg.MaterializeResult:
                """Scrape data for a single URL partition."""
                from sruth.shared.dagster.resources import BrowserResource
                import asyncio

                url = context.partition_key

                async def scrape():
                    browser = BrowserResource(
                        preferred_backend=self.browser_backend,
                        headless=self.headless,
                    )
                    return await browser.scrape(
                        url=url,
                        instruction=self.extract_instruction,
                        formats=self.extract_formats,
                    )

                results = asyncio.run(scrape())

                return dg.MaterializeResult(
                    metadata={
                        "url": url,
                        "items_extracted": len(results),
                    }
                )

        else:
            # Single asset for all URLs
            @dg.asset(
                key=self.asset_key or [asset_name],
                name=asset_name,
                group_name=self.group_name,
                description=self.description or f"Scraped from {len(self.urls)} URLs",
                compute_kind="browser",
            )
            def scraped_asset(context: dg.AssetExecutionContext) -> dg.MaterializeResult:
                """Scrape data from all configured URLs."""
                from sruth.shared.dagster.resources import BrowserResource
                import asyncio

                async def scrape_all():
                    browser = BrowserResource(
                        preferred_backend=self.browser_backend,
                        headless=self.headless,
                    )
                    all_results = []
                    for url in self.urls:
                        results = await browser.scrape(
                            url=url,
                            instruction=self.extract_instruction,
                            formats=self.extract_formats,
                        )
                        all_results.extend(results)
                    return all_results

                results = asyncio.run(scrape_all())

                return dg.MaterializeResult(
                    metadata={
                        "urls_scraped": len(self.urls),
                        "items_extracted": len(results),
                    }
                )

        return dg.Definitions(assets=[scraped_asset])
