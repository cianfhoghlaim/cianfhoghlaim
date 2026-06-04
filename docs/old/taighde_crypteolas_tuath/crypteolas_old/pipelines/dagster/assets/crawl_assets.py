"""Web crawling assets using Firecrawl or Crawl4AI.

Creates Dagster assets for crawling documentation websites and
ingesting the content into DuckDB.

Example:
    Assets are built from config/repos.yaml for repositories
    with `modes.crawl: true` and a configured `crawl_config.docs_url`.
"""

from __future__ import annotations

import os
from pathlib import Path
from typing import TYPE_CHECKING, Any

import dlt
import yaml
from dagster import AssetExecutionContext
from dagster_embedded_elt.dlt import DagsterDltResource, dlt_assets

if TYPE_CHECKING:
    pass


def load_repos_config() -> dict[str, Any]:
    """Load repository configuration from repos.yaml."""
    config_path = Path(__file__).parent.parent.parent / "config" / "repos.yaml"
    with open(config_path) as f:
        return yaml.safe_load(f)


def create_firecrawl_source(
    docs_url: str,
    crawl_depth: int = 3,
    max_pages: int = 100,
):
    """Create a DLT source for Firecrawl.

    Args:
        docs_url: Base URL to crawl
        crawl_depth: Maximum crawl depth
        max_pages: Maximum pages to crawl

    Returns:
        DLT source generator
    """
    @dlt.source(name="firecrawl_docs")
    def firecrawl_source():
        """Firecrawl documentation source."""

        @dlt.resource(name="pages", write_disposition="merge", primary_key="url")
        def crawl_pages():
            """Crawl documentation pages."""
            try:
                from firecrawl import FirecrawlApp

                api_key = os.getenv("FIRECRAWL_API_KEY")
                if not api_key:
                    raise ValueError("FIRECRAWL_API_KEY environment variable not set")

                app = FirecrawlApp(api_key=api_key)

                result = app.crawl_url(
                    docs_url,
                    params={
                        "crawlerOptions": {
                            "maxDepth": crawl_depth,
                            "limit": max_pages,
                        },
                        "pageOptions": {
                            "onlyMainContent": True,
                        }
                    },
                    wait_until_done=True,
                )

                import pendulum
                for page in result.get("data", []):
                    yield {
                        "url": page.get("metadata", {}).get("sourceURL", ""),
                        "title": page.get("metadata", {}).get("title", ""),
                        "content": page.get("markdown", ""),
                        "html": page.get("html", ""),
                        "start_url": docs_url,
                        "crawled_at": pendulum.now().to_iso8601_string(),
                    }

            except ImportError:
                raise RuntimeError(
                    "firecrawl-py not installed. Run: pip install firecrawl-py"
                )

        yield crawl_pages

    return firecrawl_source()


def make_crawl_asset(repo_key: str, repo_config: dict[str, Any]):
    """Factory function to create crawl asset for a repository.

    Args:
        repo_key: Configuration key for the repository
        repo_config: Repository configuration from repos.yaml

    Returns:
        Dagster asset or None if crawl not configured
    """
    owner = repo_config["owner"]
    repo = repo_config["repo"]
    crawl_config = repo_config.get("crawl_config", {})
    docs_url = crawl_config.get("docs_url")

    if not docs_url:
        return None

    crawl_depth = crawl_config.get("crawl_depth", 3)
    max_pages = crawl_config.get("max_pages", 100)

    source = create_firecrawl_source(docs_url, crawl_depth, max_pages)

    @dlt_assets(
        dlt_source=source,
        dlt_pipeline=dlt.pipeline(
            pipeline_name=f"crawl_{owner}_{repo}",
            dataset_name=f"docs_{owner}_{repo}",
            destination="duckdb",
            progress="log",
        ),
        name=f"crawl_{repo_key}",
        group_name=f"crawl_{repo_key}",
    )
    def _crawl_asset(context: AssetExecutionContext, dlt: DagsterDltResource):
        context.log.info(f"Crawling docs for {owner}/{repo} from {docs_url}")
        yield from dlt.run(context=context)

    return _crawl_asset


def build_all_crawl_assets() -> list:
    """Build all crawl assets from configuration.

    Returns:
        List of crawl assets
    """
    try:
        config = load_repos_config()
    except FileNotFoundError:
        return []

    all_assets = []

    for repo_key, repo_config in config.get("repositories", {}).items():
        modes = repo_config.get("modes", {})

        # Only create crawl assets if crawl mode is enabled
        if modes.get("crawl", False):
            asset_def = make_crawl_asset(repo_key, repo_config)
            if asset_def:
                all_assets.append(asset_def)

    return all_assets


# Build assets at module load time
crawl_assets = build_all_crawl_assets()
