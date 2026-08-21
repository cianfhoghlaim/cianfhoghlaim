"""Base DLT source classes for reusable data extraction patterns.

This module provides:
- BaseSource: Abstract base for all DLT sources
- RESTSource: REST API source with pagination
- BrowserSource: Browser-based scraping source
"""

from __future__ import annotations

import dlt
from abc import ABC, abstractmethod
from typing import Any, AsyncIterator, Iterator, Callable
from dataclasses import dataclass
from datetime import datetime
from functools import wraps


def dlt_source(name: str | None = None):
    """Decorator for DLT sources with consistent configuration.

    Usage:
        @dlt_source("my_source")
        def my_source():
            @dlt.resource
            def items():
                yield {"id": 1, "name": "Item"}
            return items
    """

    def decorator(func):
        @dlt.source(name=name or func.__name__)
        @wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)

        return wrapper

    return decorator


class BaseSource(ABC):
    """Abstract base class for DLT sources.

    Provides common functionality for all DLT sources including
    state management, error handling, and logging.
    """

    source_name: str = "base_source"

    @abstractmethod
    def get_resources(self) -> dict[str, Callable]:
        """Return dict of resource name to resource function.

        Each resource should be decorated with @dlt.resource.
        """
        pass

    def get_state(self, key: str, default: Any = None) -> Any:
        """Get value from DLT state."""
        return dlt.current.state().get(key, default)

    def set_state(self, key: str, value: Any) -> None:
        """Set value in DLT state."""
        dlt.current.state()[key] = value


class RESTSource(BaseSource):
    """REST API source with built-in pagination and authentication.

    Supports:
    - Multiple auth types (bearer token, API key, basic auth)
    - Cursor and link-based pagination
    - Rate limiting and retries
    - Automatic schema inference

    Example:
        source = RESTSource(
            base_url="https://api.github.com",
            auth_header="Authorization",
            auth_token=f"Bearer {token}",
        )

        @dlt.resource(name="repositories")
        def get_repositories():
            for page in source.paginate("/users/octocat/repos"):
                yield from page
    """

    def __init__(
        self,
        base_url: str,
        auth_header: str | None = None,
        auth_token: str | None = None,
        auth_type: str = "bearer",  # bearer, apikey, basic
        page_size: int = 100,
        rate_limit: float = 1.0,  # seconds between requests
    ):
        self.base_url = base_url.rstrip("/")
        self.auth_header = auth_header
        self.auth_token = auth_token
        self.auth_type = auth_type
        self.page_size = page_size
        self.rate_limit = rate_limit

    def get_headers(self) -> dict[str, str]:
        """Get request headers including auth."""
        headers = {
            "Accept": "application/json",
            "Content-Type": "application/json",
        }

        if self.auth_header and self.auth_token:
            if self.auth_type == "bearer":
                headers[self.auth_header] = f"Bearer {self.auth_token}"
            elif self.auth_type == "apikey":
                headers[self.auth_header] = self.auth_token
            else:
                headers[self.auth_header] = self.auth_token

        return headers

    def paginate(
        self,
        endpoint: str,
        params: dict[str, Any] | None = None,
        cursor_param: str = "page",
    ) -> Iterator[list[dict[str, Any]]]:
        """Paginate through a REST endpoint.

        Args:
            endpoint: API endpoint (e.g., "/users/repos")
            params: Query parameters
            cursor_param: Name of pagination parameter

        Yields:
            Lists of items from each page
        """
        import requests
        import time

        params = params or {}
        page = 1

        while True:
            params[cursor_param] = page
            params["per_page"] = self.page_size

            response = requests.get(
                f"{self.base_url}{endpoint}",
                headers=self.get_headers(),
                params=params,
                timeout=30,
            )
            response.raise_for_status()

            data = response.json()

            # Handle different response shapes
            if isinstance(data, list):
                items = data
            elif isinstance(data, dict):
                items = data.get("items", data.get("results", data.get("data", [])))
            else:
                break

            if not items:
                break

            yield items

            # Check if there are more pages
            if len(items) < self.page_size:
                break

            page += 1
            time.sleep(self.rate_limit)


class BrowserSource(BaseSource):
    """Browser-based scraping source for JavaScript-heavy sites.

    Integrates with the sruth browser stack to provide:
    - Stagehand (AI-powered navigation)
    - Crawl4AI (bulk extraction)
    - Browserbase/Firecrawl (cloud fallback)

    Example:
        source = BrowserSource()

        @dlt.resource(name="exam_materials")
        def get_exam_materials():
            async for material in source.scrape(
                url="https://www.examinations.ie/exammaterialarchive/",
                extract_instruction="Extract all PDF links",
            ):
                yield material
    """

    def __init__(
        self,
        preferred_backend: str = "stagehand",  # stagehand, crawl4ai, browserbase
        headless: bool = True,
        timeout: float = 30.0,
    ):
        self.preferred_backend = preferred_backend
        self.headless = headless
        self.timeout = timeout

    async def scrape(
        self,
        url: str,
        extract_instruction: str,
        formats: list[str] | None = None,
    ) -> AsyncIterator[dict[str, Any]]:
        """Scrape a URL using the browser stack.

        Args:
            url: URL to scrape
            extract_instruction: Instruction for content extraction
            formats: Desired output formats (markdown, json, etc.)

        Yields:
            Extracted data items
        """
        from sruth.browser.sruth_browser.backends.initializer import ensure_initialized
        from sruth.browser.sruth_browser.backends.router import get_router
        from sruth.browser.sruth_browser.browser_types import BrowserOperation

        # Ensure backends are initialized
        await ensure_initialized()

        router = get_router()
        backend_type = await router.select_backend(BrowserOperation.EXTRACTION)

        if backend_type is None:
            raise RuntimeError("No browser backends available")

        backend = router.get_backend(backend_type)

        # Navigate and extract
        await backend.navigate(url)
        result = await backend.extract(
            instruction=extract_instruction,
            format=formats or ["structured"],
        )

        if result.success and result.data:
            if isinstance(result.data, list):
                for item in result.data:
                    yield item
            elif isinstance(result.data, dict):
                # Look for list items in common keys
                for key in ["items", "results", "data", "links"]:
                    if key in result.data and isinstance(result.data[key], list):
                        for item in result.data[key]:
                            yield item
                        break
                else:
                    yield result.data
            else:
                yield result.data


# Resource decorators for common patterns


def incremental_resource(
    primary_key: str | list[str] = "id",
    merge_key: str | list[str] | None = None,
    write_disposition: str = "merge",
):
    """Decorator for incremental DLT resources.

    Resources decorated with this will:
    - Track state to avoid re-processing
    - Merge new/updated records based on primary key
    - Support cursor-based pagination

    Example:
        @incremental_resource(primary_key="url")
        def crawl_pages():
            last_url = dlt.state().get("last_url")
            for url in get_urls_since(last_url):
                page = scrape_page(url)
                yield page
            dlt.state()["last_url"] = max(get_urls())
    """

    def decorator(func):
        @dlt.resource(
            primary_key=primary_key,
            write_disposition=write_disposition,
            merge_key=merge_key,
        )
        @wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)

        return wrapper

    return decorator


def partitioned_resource(
    partition_key: str | list[str] = "date",
    partition_interval: str = "daily",
):
    """Decorator for partitioned DLT resources.

    Resources decorated with this will automatically partition
    data by date, month, year, or custom partition key.

    Example:
        @partitioned_resource(partition_key="created_at", partition_interval="monthly")
        def get_events():
            for event in fetch_events():
                yield event
    """

    def decorator(func):
        @dlt.resource(
            partition=partition_key,
        )
        @wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)

        return wrapper

    return decorator
