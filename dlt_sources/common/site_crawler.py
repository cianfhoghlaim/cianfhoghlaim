"""
site_crawler — the canonical 3-way web-scraper primitive for the
Cianfhoghlaim DLT layer.

Per the `2026-07-15-pipeline-architecture-clarity-v1` openspec change,
this module supersedes the three overlapping pre-existing primitives:

* `dlt/common/firecrawl_source.py:crawl_website`  (browser + firecrawl adapter)
* `dlt/common/incremental.py:crawl_source`        (URL discovery + crawl)
* `dlt/british_isles/ireland/education/curriculum.py:_crawl_source`
                                                    (private helper leaked
                                                     across packages)

Public API
----------

* `scrape_url(url, formats=None) -> CrawledPage`
    Single-page scrape. Returns a typed `CrawledPage` dataclass.

* `crawl_site(base_url, include_paths=None, exclude_paths=None,
              max_pages=100, max_depth=3, formats=None) -> Iterator[CrawledPage]`
    Discover + batch-scrape URLs starting from `base_url`.

* `map_urls(base_url, search=None, max_urls=1000) -> Iterator[str]`
    Discover URLs without scraping (cheap).

Backend priority (the first available backend wins):

1. **`BrowserClient`** (self-hosted, `$0` cost) — when the
   `BROWSER_API_URL` env var is set
2. **`FirecrawlApp`** (paid API fallback) — when the `FIRECRAWL_API_KEY`
   env var is set
3. **Local scrape cache** (`stedding/ingest_queue/<source_key>/`) — when
   `USE_LOCAL_SCRAPES=true` (the AGENTS.md "Respect the Ingestion Cache"
   rule)

The legacy helpers remain as thin re-export wrappers in their original
modules so existing call sites keep working during the deprecation
window.
"""

from __future__ import annotations

import asyncio
import json
import os
import re
from collections.abc import Iterator
from dataclasses import asdict, dataclass, field
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

import structlog

logger = structlog.get_logger(__name__)


# ---------------------------------------------------------------------------
# Configuration
# ---------------------------------------------------------------------------


# Local scrape cache root. Per the AGENTS.md "Respect the Ingestion Cache"
# rule, when `USE_LOCAL_SCRAPES=true` the primitive reads cached
# markdown/JSON files from this root instead of hitting the network.
LOCAL_CACHE_ROOT = Path(
    os.environ.get(
        "SCRAPE_CACHE_ROOT",
        str(Path(__file__).resolve().parents[3] / "stedding" / "ingest_queue"),
    )
)


# Valid output formats for the Firecrawl + BrowserClient scrape calls.
VALID_FORMATS = frozenset({"markdown", "html", "links", "json", "summary"})


# Default per-call budget (mirrors the archived firecrawl_source defaults).
DEFAULT_MAX_PAGES = 100
DEFAULT_MAX_DEPTH = 3
DEFAULT_MAX_URLS = 1000
DEFAULT_TIMEOUT_S = 60.0


# ---------------------------------------------------------------------------
# Typed result dataclass
# ---------------------------------------------------------------------------


@dataclass
class CrawledPage:
    """One scraped (or cache-read) page.

    Mirrors the dict shape that the legacy `firecrawl_source.py:crawl_website`
    used to return, but as a typed dataclass. Callers can still get a dict
    via `asdict()` for backwards compat.
    """

    url: str
    title: str | None = None
    description: str | None = None
    markdown: str | None = None
    html: str | None = None
    links: list[str] = field(default_factory=list)
    language: str | None = None
    status: str = "success"
    backend: str = "unknown"
    scraped_at: str = field(default_factory=lambda: datetime.now(UTC).isoformat())
    error: str | None = None
    metadata: dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> dict[str, Any]:
        """Serialize to a dict (backwards compat with the legacy helper)."""
        return asdict(self)


# ---------------------------------------------------------------------------
# PII / ZDR policy (per the 2026-08-14-firecrawl-corpus-and-examinations-ie-v1 change)
# ---------------------------------------------------------------------------


@dataclass(frozen=True)
class ScrapePolicy:
    """The per-source scrape policy.

    The policy propagates to every Firecrawl scrape call. The 3 PII
    sources (HSE + Scottish NHS + Welsh health) set
    `sensitivity="pii"` to flip `redact_pii` + `zero_data_retention`
    on. All other sources default to `sensitivity="none"`.
    """

    sensitivity: str = "none"  # "none" | "pii" | "phi" | "secret"
    redact_pii: bool = False
    zero_data_retention: bool = False
    cache_max_age_ms: int = 7 * 86_400_000  # 7 days for non-PII; 24h for PII
    requires_interact: bool = False  # examinations.ie login-gated
    persistent_profile: str | None = None  # e.g. "state-exams-ie"

    def __post_init__(self) -> None:
        # Auto-derive redact_pii + zero_data_retention from sensitivity
        if self.sensitivity != "none":
            object.__setattr__(self, "redact_pii", True)
            object.__setattr__(self, "zero_data_retention", True)
        # PII sources use a shorter cache window (24h)
        if self.sensitivity != "none" and self.cache_max_age_ms == 7 * 86_400_000:
            object.__setattr__(self, "cache_max_age_ms", 86_400_000)

    def to_firecrawl_params(self) -> dict[str, Any]:
        """Convert to Firecrawl scrape params."""
        params: dict[str, Any] = {"maxAge": self.cache_max_age_ms}
        if self.redact_pii:
            params["redactPII"] = True
        if self.zero_data_retention:
            params["zeroDataRetention"] = True
        if self.persistent_profile:
            params["profile"] = {
                "name": self.persistent_profile,
                "saveChanges": False,
            }
        return params


# Per-source policy table (the canonical 3 PII sources + the 1
# login-gated persistent profile).
SOURCE_POLICIES: dict[str, ScrapePolicy] = {
    "hse": ScrapePolicy(sensitivity="pii"),
    "gov_scot_statistics": ScrapePolicy(sensitivity="pii"),
    "welsh_medium": ScrapePolicy(sensitivity="pii"),
    "examinations_ie_papers": ScrapePolicy(
        sensitivity="pii",
        persistent_profile="state-exams-ie",
    ),
    "examinations_ie_marking": ScrapePolicy(
        sensitivity="pii",
        persistent_profile="state-exams-ie",
    ),
}


def get_policy(source_key: str) -> ScrapePolicy:
    """Return the policy for a source (default: non-PII, 7-day cache)."""
    return SOURCE_POLICIES.get(source_key, ScrapePolicy())


# ---------------------------------------------------------------------------
# Backend selection
# ---------------------------------------------------------------------------


@dataclass
class BackendChoice:
    """The result of `_pick_backend()`.

    `client` is either a `BrowserClient` instance, a `FirecrawlApp` instance,
    a sentinel `_LocalCacheClient` for the offline path, or `None` if no
    backend is available (caller emits a `CrawledPage` with
    `status="client_unavailable"`).
    """

    client: Any
    backend_name: str  # "browser" | "firecrawl" | "local_cache" | "none"


# Module-level sentinel — we can't import a class for the offline cache
# path because each domain has its own cache layout. The cache helper is a
# function (`_scrape_via_local_cache`), not a client object.
class _LocalCacheClient:
    """Sentinel: a successful backend_choice with `backend_name="local_cache"`.

    The real cache-reading logic is `_scrape_via_local_cache()`. We keep
    this sentinel so `_pick_backend()` can return a uniform value.
    """

    pass


def _get_browser_client() -> Any:
    """Return a BrowserClient if `BROWSER_API_URL` is set and sruth-browser is installed."""
    browser_url = os.environ.get("BROWSER_API_URL")
    if not browser_url:
        return None
    try:
        # The BrowserClient lives in the bonneagar repo (separate worktree).
        from bonneagar.stacks.browser.sruth_browser import BrowserClient  # type: ignore[import-not-found]

        return BrowserClient(base_url=browser_url)
    except ImportError:
        logger.debug("site_crawler.sruth_browser_not_installed")
        return None


def _get_firecrawl_client() -> Any:
    """Return a FirecrawlApp if `FIRECRAWL_API_KEY` is set and firecrawl is installed."""
    api_key = os.environ.get("FIRECRAWL_API_KEY")
    if not api_key:
        return None
    try:
        from firecrawl import FirecrawlApp  # type: ignore[import-not-found]

        return FirecrawlApp(api_key=api_key)
    except ImportError:
        logger.debug("site_crawler.firecrawl_not_installed")
        return None


def _use_local_cache() -> bool:
    """True when the AGENTS.md cache rule is active."""
    return os.environ.get("USE_LOCAL_SCRAPES", "").lower().strip() in {
        "1",
        "true",
        "yes",
        "on",
    }


def _pick_backend() -> BackendChoice:
    """Pick the highest-priority available backend.

    Priority (per the `site-crawler` spec + the AGENTS.md "Respect the
    Ingestion Cache" rule):

      1. Local cache    (when `USE_LOCAL_SCRAPES=true`) — the cache flag
         OVERRIDES paid backends so dev / CI never hits a paid API when
         the user explicitly asked for offline mode
      2. BrowserClient  (when `BROWSER_API_URL` is set + importable)
      3. FirecrawlApp   (when `FIRECRAWL_API_KEY` is set + importable)

    Falls through to `(client=None, backend_name="none")` when no
    backend is available; callers should emit a `CrawledPage` with
    `status="client_unavailable"` in that case.
    """
    if _use_local_cache():
        return BackendChoice(client=_LocalCacheClient(), backend_name="local_cache")

    browser = _get_browser_client()
    if browser is not None:
        return BackendChoice(client=browser, backend_name="browser")

    firecrawl = _get_firecrawl_client()
    if firecrawl is not None:
        return BackendChoice(client=firecrawl, backend_name="firecrawl")

    return BackendChoice(client=None, backend_name="none")


# ---------------------------------------------------------------------------
# Per-backend scrape implementations
# ---------------------------------------------------------------------------


def _scrape_via_browser(
    browser: Any,
    url: str,
    formats: list[str] | None = None,
    timeout: float = DEFAULT_TIMEOUT_S,
) -> CrawledPage:
    """Scrape a single URL via the BrowserClient (async wrapper)."""
    try:
        from bonneagar.stacks.browser.sruth_browser import (  # type: ignore[import-not-found]
            ExtractionFormat,
        )
    except ImportError as e:
        raise RuntimeError(
            "BrowserClient is configured but sruth-browser is not importable."
        ) from e

    format_map = {
        "markdown": ExtractionFormat.MARKDOWN,
        "html": ExtractionFormat.HTML,
        "links": ExtractionFormat.LINKS,
        "json": ExtractionFormat.JSON,
    }
    extraction_formats = [
        format_map.get(f, ExtractionFormat.MARKDOWN) for f in (formats or ["markdown", "links"])
    ]

    async def _scrape() -> Any:
        async with browser:
            return await asyncio.wait_for(
                browser.scrape(url, formats=extraction_formats),
                timeout=timeout,
            )

    try:
        result = asyncio.run(_scrape())
    except (RuntimeError, ConnectionError, TimeoutError, ValueError) as e:
        logger.warning("site_crawler.browser_scrape_failed", url=url, error=str(e))
        return CrawledPage(
            url=url,
            status="error",
            backend="browser",
            error=str(e),
        )

    return CrawledPage(
        url=getattr(result, "url", url),
        title=(result.metadata or {}).get("title"),
        description=(result.metadata or {}).get("description"),
        markdown=(result.content or {}).get("markdown"),
        html=(result.content or {}).get("html"),
        links=list((result.content or {}).get("links", [])),
        language=(result.metadata or {}).get("language"),
        status="success",
        backend="browser",
        metadata=dict(result.metadata or {}),
    )


def _scrape_via_firecrawl(
    firecrawl: Any,
    url: str,
    formats: list[str] | None = None,
    policy: ScrapePolicy | None = None,
) -> CrawledPage:
    """Scrape a single URL via the Firecrawl Python SDK.

    Per the 2026-08-14-firecrawl-corpus-and-examinations-ie-v1 change,
    the `:policy` argument propagates the per-source PII flags
    (`redact_pii`, `zero_data_retention`, `cache_max_age_ms`, ...)
    into the Firecrawl params.
    """
    formats = formats or ["markdown", "links"]
    policy = policy or ScrapePolicy()
    params: dict[str, Any] = {"formats": formats}
    params.update(policy.to_firecrawl_params())
    try:
        result = firecrawl.scrape_url(url, params=params)
        metadata = result.get("metadata") or {}
        # Merge the policy flags into the metadata for downstream
        # logging (the firecrawl_meta.scrapes row records them).
        policy_metadata = {
            "redact_pii": policy.redact_pii,
            "zero_data_retention": policy.zero_data_retention,
            "sensitivity": policy.sensitivity,
            "cache_max_age_ms": policy.cache_max_age_ms,
        }
        if policy.persistent_profile:
            policy_metadata["persistent_profile"] = policy.persistent_profile
        metadata = {**metadata, "_policy": policy_metadata}
        return CrawledPage(
            url=metadata.get("sourceURL", url),
            title=metadata.get("title"),
            description=metadata.get("description"),
            markdown=result.get("markdown"),
            html=result.get("html"),
            links=list(result.get("links", [])),
            language=metadata.get("language"),
            status="success",
            backend="firecrawl",
            metadata=dict(metadata),
        )
    except (RuntimeError, ConnectionError, TimeoutError, ValueError) as e:
        logger.warning("site_crawler.firecrawl_scrape_failed", url=url, error=str(e))
        return CrawledPage(
            url=url,
            status="error",
            backend="firecrawl",
            error=str(e),
        )


def _local_cache_path_for(url: str) -> Path | None:
    """Map a URL to its local cache file path (if any).

    Convention: `stedding/ingest_queue/<host>/<path-without-leading-slash>.json`.
    Returns None when the cache file does not exist.
    """
    match = re.match(r"^https?://([^/]+)(/.*)?$", url)
    if not match:
        return None
    host = match.group(1)
    path = (match.group(2) or "/").lstrip("/") or "index"
    safe_path = path.replace("/", "__") + ".json"
    candidate = LOCAL_CACHE_ROOT / host / safe_path
    return candidate if candidate.exists() else None


def _scrape_via_local_cache(url: str) -> CrawledPage:
    """Read a cached page from `stedding/ingest_queue/<host>/<path>.json`."""
    cached = _local_cache_path_for(url)
    if cached is None:
        return CrawledPage(
            url=url,
            status="cache_miss",
            backend="local_cache",
        )
    try:
        data = json.loads(cached.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, OSError) as e:
        return CrawledPage(
            url=url,
            status="cache_corrupt",
            backend="local_cache",
            error=str(e),
        )
    return CrawledPage(
        url=data.get("url", url),
        title=data.get("title"),
        description=data.get("description"),
        markdown=data.get("markdown"),
        html=data.get("html"),
        links=list(data.get("links", [])),
        language=data.get("language"),
        status="success",
        backend="local_cache",
        metadata=dict(data.get("metadata", {})),
    )


# ---------------------------------------------------------------------------
# Public API
# ---------------------------------------------------------------------------


def scrape_url(
    url: str,
    formats: list[str] | None = None,
    *,
    policy: ScrapePolicy | None = None,
    source_key: str | None = None,
) -> CrawledPage:
    """Scrape a single page. Dispatches to the first available backend.

    Args:
        url: the URL to scrape.
        formats: optional list of output formats (default: `["markdown",
            "links"]`). Valid values: `"markdown"`, `"html"`, `"links"`,
            `"json"`, `"summary"`.
        policy: optional `ScrapePolicy` for PII flags. If None, the
            policy is resolved from `source_key` via `get_policy()`.
        source_key: optional source key (e.g. `"hse"`) for policy lookup.

    Returns:
        A `CrawledPage` instance with `status="success"` on success or
        `status="error"` / `status="client_unavailable"` on failure.
    """
    # Validate formats early — fail loud before hitting the network.
    if formats is not None:
        bad = [f for f in formats if f not in VALID_FORMATS]
        if bad:
            raise ValueError(
                f"Invalid format(s): {bad}. Valid: {sorted(VALID_FORMATS)}"
            )

    # Resolve the policy
    if policy is None and source_key is not None:
        policy = get_policy(source_key)
    policy = policy or ScrapePolicy()

    choice = _pick_backend()

    if choice.backend_name == "browser":
        return _scrape_via_browser(choice.client, url, formats)
    if choice.backend_name == "firecrawl":
        return _scrape_via_firecrawl(choice.client, url, formats, policy=policy)
    if choice.backend_name == "local_cache":
        return _scrape_via_local_cache(url)

    return CrawledPage(
        url=url,
        status="client_unavailable",
        backend="none",
    )


def _glob_to_regex(pattern: str) -> str:
    """Convert a Firecrawl-style glob pattern to a regex.

    Supports `*` as a wildcard (matches any chars including `/`) and
    `?` as a single-char wildcard. Other characters are escaped.

    Matches the legacy `firecrawl_source.py` substring-matching
    semantics: the pattern is treated as a substring (not anchored),
    so `/news/*` matches any URL containing `/news/<anything>`.
    """
    import re as _re

    out = []
    i = 0
    while i < len(pattern):
        c = pattern[i]
        if c == "*":
            out.append(".*")
        elif c == "?":
            out.append(".")
        else:
            out.append(_re.escape(c))
        i += 1
    return ".*".join([""] + out + [""])


def _url_matches_pattern(url: str, pattern: str) -> bool:
    """True if `url` matches a Firecrawl-style glob pattern (substring)."""
    import re as _re

    return bool(_re.search(_glob_to_regex(pattern), url))


def _filter_urls(
    urls: list[str],
    include_paths: list[str] | None,
    exclude_paths: list[str] | None,
) -> list[str]:
    """Apply include/exclude path filters to a list of URLs.

    Each pattern is a Firecrawl-style glob (`*` = any chars, `?` =
    single char). `include_paths` matches if ANY pattern matches;
    `exclude_paths` matches if ANY pattern matches.
    """
    out: list[str] = []
    for url in urls:
        if include_paths:
            if not any(_url_matches_pattern(url, p) for p in include_paths):
                continue
        if exclude_paths:
            if any(_url_matches_pattern(url, p) for p in exclude_paths):
                continue
        out.append(url)
    return out


def _browser_discover_and_scrape(
    browser: Any,
    base_url: str,
    include_paths: list[str] | None,
    exclude_paths: list[str] | None,
    max_pages: int,
    max_depth: int,
    formats: list[str] | None,
    timeout: float,
) -> Iterator[CrawledPage]:
    """Discover via BrowserClient + batch scrape (async wrapper)."""
    try:
        from bonneagar.stacks.browser.sruth_browser import (  # type: ignore[import-not-found]
            ExtractionFormat,
        )
    except ImportError as e:
        raise RuntimeError(
            "BrowserClient is configured but sruth-browser is not importable."
        ) from e

    format_map = {
        "markdown": ExtractionFormat.MARKDOWN,
        "html": ExtractionFormat.HTML,
        "links": ExtractionFormat.LINKS,
        "json": ExtractionFormat.JSON,
    }
    extraction_formats = [
        format_map.get(f, ExtractionFormat.MARKDOWN) for f in (formats or ["markdown", "links"])
    ]

    async def _do_crawl() -> list[Any]:
        async with browser:
            # `max_depth` is supported via `crawl_url` on BrowserClient; if
            # the client doesn't support it (older versions) we fall
            # back to discovery + batch scrape.
            try:
                results = await asyncio.wait_for(
                    browser.crawl_url(
                        base_url,
                        max_urls=max_pages,
                        max_depth=max_depth,
                        formats=extraction_formats,
                    ),
                    timeout=timeout * (max_pages / 10 + 1),
                )
            except (AttributeError, TypeError):
                # Fallback: discover first, then batch scrape.
                urls = await asyncio.wait_for(
                    browser.discover_site(base_url, max_urls=max_pages),
                    timeout=timeout,
                )
                urls = _filter_urls(urls, include_paths, exclude_paths)[:max_pages]
                results = await asyncio.wait_for(
                    browser.batch_scrape(urls, formats=extraction_formats),
                    timeout=timeout * (max_pages / 10 + 1),
                )
            return list(results)

    try:
        results = asyncio.run(_do_crawl())
    except (RuntimeError, ConnectionError, TimeoutError, ValueError) as e:
        logger.warning(
            "site_crawler.browser_crawl_failed", base_url=base_url, error=str(e)
        )
        yield CrawledPage(
            url=base_url,
            status="error",
            backend="browser",
            error=str(e),
        )
        return

    for result in results:
        yield CrawledPage(
            url=getattr(result, "url", base_url),
            title=(result.metadata or {}).get("title"),
            description=(result.metadata or {}).get("description"),
            markdown=(result.content or {}).get("markdown"),
            html=(result.content or {}).get("html"),
            links=list((result.content or {}).get("links", [])),
            language=(result.metadata or {}).get("language"),
            status="success",
            backend="browser",
            metadata=dict(result.metadata or {}),
        )


def _firecrawl_crawl(
    firecrawl: Any,
    base_url: str,
    include_paths: list[str] | None,
    exclude_paths: list[str] | None,
    max_pages: int,
    max_depth: int,
    formats: list[str] | None,
) -> Iterator[CrawledPage]:
    """Crawl via Firecrawl's `crawl_url` API.

    Per the Firecrawl v2 SDK, `crawl_url(url, **kwargs)` takes arbitrary
    kwargs directly (the v1 SDK wrapped them in a `params` dict — that
    signature was removed in v2). The legacy `firecrawl_source.py`
    carried the v1 `params={...}` call which raises `TypeError` against
    the v2 SDK; this implementation spreads the kwargs directly.
    """
    formats = formats or ["markdown", "links"]
    crawl_kwargs: dict[str, Any] = {
        "limit": max_pages,
        "maxDepth": max_depth,
        "scrapeOptions": {"formats": formats},
    }
    if include_paths:
        crawl_kwargs["includePaths"] = include_paths
    if exclude_paths:
        crawl_kwargs["excludePaths"] = exclude_paths

    try:
        # Note: poll_interval was a v1 SDK option; v2's `crawl_url`
        # doesn't accept it (the SDK polls internally). We drop it.
        result = firecrawl.crawl_url(base_url, **crawl_kwargs)
    except (RuntimeError, ConnectionError, TimeoutError, ValueError) as e:
        logger.warning(
            "site_crawler.firecrawl_crawl_failed", base_url=base_url, error=str(e)
        )
        yield CrawledPage(
            url=base_url,
            status="error",
            backend="firecrawl",
            error=str(e),
        )
        return

    # The v2 SDK's `crawl_url` returns a coroutine / crawl-handle object,
    # not a `{data: [...]}` dict. Inspect what we got and iterate over
    # the pages. When `result` is a dict with `data` (legacy v1 shape),
    # use that; when it's a `Crawl` object, iterate its `.data` attribute.
    pages: list[dict[str, Any]] = []
    if isinstance(result, dict):
        pages = list(result.get("data", []))
    else:
        # v2 SDK returns a `Crawl` handle with a `.data` attribute (or
        # we may need to call `.get_data()` depending on version).
        if hasattr(result, "data") and result.data is not None:
            pages = list(result.data)
        elif hasattr(result, "get_data"):
            pages = list(result.get_data())

    for page in pages:
        metadata = page.get("metadata") or {} if isinstance(page, dict) else {}
        yield CrawledPage(
            url=metadata.get("sourceURL", base_url) if metadata else base_url,
            title=metadata.get("title") if metadata else None,
            description=metadata.get("description") if metadata else None,
            markdown=page.get("markdown") if isinstance(page, dict) else None,
            html=page.get("html") if isinstance(page, dict) else None,
            links=list(page.get("links", [])) if isinstance(page, dict) else [],
            language=metadata.get("language") if metadata else None,
            status="success",
            backend="firecrawl",
            metadata=dict(metadata) if metadata else {},
        )


def _local_cache_crawl(
    base_url: str,
    include_paths: list[str] | None,
    exclude_paths: list[str] | None,
) -> Iterator[CrawledPage]:
    """Read all cached pages under the base_url's host directory."""
    # Parse the host from base_url.
    match = re.match(r"^https?://([^/]+)(/.*)?$", base_url)
    if not match:
        return
    host = match.group(1)
    host_dir = LOCAL_CACHE_ROOT / host
    if not host_dir.exists():
        return

    for cached in sorted(host_dir.glob("*.json")):
        # Reconstruct the URL from the cached filename.
        rel = cached.stem.replace("__", "/")
        url = (
            f"https://{host}/{rel.lstrip('/')}" if rel != "index" else f"https://{host}/"
        )
        if include_paths and not any(_url_matches_pattern(url, p) for p in include_paths):
            continue
        if exclude_paths and any(_url_matches_pattern(url, p) for p in exclude_paths):
            continue
        page = _scrape_via_local_cache(url)
        if page.status == "success":
            yield page


def crawl_site(
    base_url: str,
    include_paths: list[str] | None = None,
    exclude_paths: list[str] | None = None,
    max_pages: int = DEFAULT_MAX_PAGES,
    max_depth: int = DEFAULT_MAX_DEPTH,
    formats: list[str] | None = None,
    timeout: float = DEFAULT_TIMEOUT_S,
) -> Iterator[CrawledPage]:
    """Discover + batch-scrape URLs starting from `base_url`.

    Args:
        base_url: the starting URL for the crawl.
        include_paths: optional list of URL substring patterns to
            include.
        exclude_paths: optional list of URL substring patterns to
            exclude.
        max_pages: cap on returned pages (default 100).
        max_depth: max crawl depth for the browser/Firecrawl crawlers
            (default 3; ignored on the local-cache backend).
        formats: optional output formats list (default
            `["markdown", "links"]`).
        timeout: per-call timeout in seconds.

    Yields:
        `CrawledPage` instances, one per scraped URL.
    """
    choice = _pick_backend()

    if choice.backend_name == "browser":
        yield from _browser_discover_and_scrape(
            choice.client,
            base_url,
            include_paths,
            exclude_paths,
            max_pages,
            max_depth,
            formats,
            timeout,
        )
    elif choice.backend_name == "firecrawl":
        yield from _firecrawl_crawl(
            choice.client,
            base_url,
            include_paths,
            exclude_paths,
            max_pages,
            max_depth,
            formats,
        )
    elif choice.backend_name == "local_cache":
        yield from _local_cache_crawl(base_url, include_paths, exclude_paths)
    else:
        yield CrawledPage(
            url=base_url,
            status="client_unavailable",
            backend="none",
        )


def _browser_discover(
    browser: Any,
    base_url: str,
    max_urls: int,
    timeout: float,
) -> list[str]:
    """BrowserClient-only: discover URLs without scraping."""
    async def _do_discover() -> list[str]:
        async with browser:
            return await asyncio.wait_for(
                browser.discover_site(base_url, max_urls=max_urls),
                timeout=timeout,
            )

    return asyncio.run(_do_discover())


def _firecrawl_map(firecrawl: Any, base_url: str, max_urls: int, search: str | None) -> list[str]:
    """Firecrawl-only: map URLs without scraping."""
    params: dict[str, Any] = {"limit": max_urls}
    if search:
        params["search"] = search
    result = firecrawl.map_url(base_url, params=params)
    return list(result.get("links", []))


def map_urls(
    base_url: str,
    search: str | None = None,
    max_urls: int = DEFAULT_MAX_URLS,
) -> Iterator[str]:
    """Discover URLs without scraping.

    Args:
        base_url: the root URL to map.
        search: optional substring filter (passed to Firecrawl; the
            BrowserClient backend ignores it).
        max_urls: cap on returned URLs (default 1000).

    Yields:
        URL strings.
    """
    choice = _pick_backend()

    if choice.backend_name == "browser":
        try:
            urls = _browser_discover(choice.client, base_url, max_urls, DEFAULT_TIMEOUT_S)
        except (RuntimeError, ConnectionError, TimeoutError, ValueError) as e:
            logger.warning(
                "site_crawler.browser_discover_failed", base_url=base_url, error=str(e)
            )
            return
        if search:
            urls = [u for u in urls if search.lower() in u.lower()]
        yield from urls
    elif choice.backend_name == "firecrawl":
        try:
            urls = _firecrawl_map(choice.client, base_url, max_urls, search)
        except (RuntimeError, ConnectionError, TimeoutError, ValueError) as e:
            logger.warning(
                "site_crawler.firecrawl_map_failed", base_url=base_url, error=str(e)
            )
            return
        yield from urls
    elif choice.backend_name == "local_cache":
        # Synthesize URLs from the cached file paths.
        match = re.match(r"^https?://([^/]+)(/.*)?$", base_url)
        if not match:
            return
        host = match.group(1)
        host_dir = LOCAL_CACHE_ROOT / host
        if not host_dir.exists():
            return
        for cached in sorted(host_dir.glob("*.json")):
            rel = cached.stem.replace("__", "/")
            url = (
                f"https://{host}/{rel.lstrip('/')}" if rel != "index" else f"https://{host}/"
            )
            if search and search.lower() not in url.lower():
                continue
            yield url
    # else: nothing to discover.


__all__ = [
    "BackendChoice",
    "CrawledPage",
    "DEFAULT_MAX_PAGES",
    "DEFAULT_MAX_DEPTH",
    "DEFAULT_MAX_URLS",
    "DEFAULT_TIMEOUT_S",
    "LOCAL_CACHE_ROOT",
    "VALID_FORMATS",
    "crawl_site",
    "map_urls",
    "scrape_url",
]