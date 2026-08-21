"""
Crawl utilities for DLT web sources.

Provides URL pattern matching, content extraction strategies,
and crawl configuration management.

Based on patterns from taighde/crawl4ai/ research.
"""

from __future__ import annotations

import fnmatch
import re
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Callable, Pattern
from urllib.parse import urljoin, urlparse

import structlog

logger = structlog.get_logger(__name__)


class ExtractionStrategy(Enum):
    """Content extraction strategies."""
    MARKDOWN = "markdown"
    HTML = "html"
    TEXT = "text"
    JSON_CSS = "json_css"
    LLM = "llm"


@dataclass
class CrawlPattern:
    """
    Pattern for matching and processing URLs.

    Usage:
        pattern = CrawlPattern(
            url_pattern="https://curriculumonline.ie/*/specifications/*",
            extraction_strategy=ExtractionStrategy.MARKDOWN,
            selectors={"content": "div.main-content"},
        )
    """
    url_pattern: str
    extraction_strategy: ExtractionStrategy = ExtractionStrategy.MARKDOWN
    selectors: dict[str, str] = field(default_factory=dict)
    exclude_patterns: list[str] = field(default_factory=list)
    metadata_extractors: dict[str, str] = field(default_factory=dict)
    follow_links: bool = True
    max_depth: int = 3
    priority: int = 0

    def matches(self, url: str) -> bool:
        """Check if URL matches this pattern."""
        # Check exclusions first
        for exclude in self.exclude_patterns:
            if fnmatch.fnmatch(url, exclude):
                return False

        return fnmatch.fnmatch(url, self.url_pattern)


@dataclass
class CrawlConfig:
    """
    Configuration for a crawl job.

    Usage:
        config = CrawlConfig(
            base_url="https://curriculumonline.ie",
            patterns=[
                CrawlPattern(url_pattern="*/Junior-Cycle/*"),
                CrawlPattern(url_pattern="*/Senior-Cycle/*"),
            ],
        )
    """
    base_url: str
    patterns: list[CrawlPattern] = field(default_factory=list)
    default_strategy: ExtractionStrategy = ExtractionStrategy.MARKDOWN
    max_pages: int = 1000
    max_depth: int = 5
    delay_seconds: float = 1.0
    concurrent_requests: int = 5
    user_agent: str = "oideachais-crawler/1.0"
    respect_robots: bool = True
    headers: dict[str, str] = field(default_factory=dict)

    def get_pattern_for_url(self, url: str) -> CrawlPattern | None:
        """Get the matching pattern for a URL, or None if no match."""
        # Sort by priority (higher first)
        sorted_patterns = sorted(
            self.patterns,
            key=lambda p: p.priority,
            reverse=True,
        )

        for pattern in sorted_patterns:
            if pattern.matches(url):
                return pattern

        return None


class URLMatcher:
    """
    Flexible URL pattern matching.

    Supports:
    - Glob patterns (fnmatch)
    - Regex patterns
    - Domain matching
    - Path prefix matching
    """

    def __init__(
        self,
        include_patterns: list[str] | None = None,
        exclude_patterns: list[str] | None = None,
        include_domains: list[str] | None = None,
        exclude_domains: list[str] | None = None,
        path_prefixes: list[str] | None = None,
    ):
        self.include_patterns = include_patterns or []
        self.exclude_patterns = exclude_patterns or []
        self.include_domains = include_domains or []
        self.exclude_domains = exclude_domains or []
        self.path_prefixes = path_prefixes or []

        # Compile regex patterns
        self._compiled_include: list[Pattern[str]] = []
        self._compiled_exclude: list[Pattern[str]] = []

        for pattern in self.include_patterns:
            if pattern.startswith("regex:"):
                self._compiled_include.append(re.compile(pattern[6:]))
        for pattern in self.exclude_patterns:
            if pattern.startswith("regex:"):
                self._compiled_exclude.append(re.compile(pattern[6:]))

    def matches(self, url: str) -> bool:
        """Check if URL matches the configured patterns."""
        parsed = urlparse(url)

        # Check domain exclusions
        if self.exclude_domains:
            for domain in self.exclude_domains:
                if parsed.netloc == domain or parsed.netloc.endswith(f".{domain}"):
                    return False

        # Check domain inclusions
        if self.include_domains:
            domain_match = False
            for domain in self.include_domains:
                if parsed.netloc == domain or parsed.netloc.endswith(f".{domain}"):
                    domain_match = True
                    break
            if not domain_match:
                return False

        # Check path prefixes
        if self.path_prefixes:
            prefix_match = False
            for prefix in self.path_prefixes:
                if parsed.path.startswith(prefix):
                    prefix_match = True
                    break
            if not prefix_match:
                return False

        # Check exclusion patterns
        for pattern in self.exclude_patterns:
            if pattern.startswith("regex:"):
                continue  # Handled separately
            if fnmatch.fnmatch(url, pattern):
                return False

        for regex in self._compiled_exclude:
            if regex.search(url):
                return False

        # Check inclusion patterns
        if self.include_patterns:
            for pattern in self.include_patterns:
                if pattern.startswith("regex:"):
                    continue
                if fnmatch.fnmatch(url, pattern):
                    return True

            for regex in self._compiled_include:
                if regex.search(url):
                    return True

            return False

        return True


def extract_links(html: str, base_url: str) -> list[str]:
    """
    Extract links from HTML content.

    Args:
        html: HTML content
        base_url: Base URL for resolving relative links

    Returns:
        List of absolute URLs
    """
    from html.parser import HTMLParser

    class LinkExtractor(HTMLParser):
        def __init__(self) -> None:
            super().__init__()
            self.links: list[str] = []

        def handle_starttag(
            self, tag: str, attrs: list[tuple[str, str | None]]
        ) -> None:
            if tag == "a":
                for attr, value in attrs:
                    if attr == "href" and value:
                        # Resolve relative URLs
                        absolute_url = urljoin(base_url, value)
                        self.links.append(absolute_url)

    parser = LinkExtractor()
    try:
        parser.feed(html)
    except (ValueError, TypeError, UnicodeDecodeError) as e:
        logger.warning("html_link_parsing_failed", error=str(e))

    return parser.links


def normalize_url(url: str) -> str:
    """
    Normalize URL for deduplication.

    - Removes fragments
    - Removes trailing slashes
    - Lowercases scheme and host
    """
    parsed = urlparse(url)

    # Reconstruct without fragment
    normalized = parsed._replace(
        scheme=parsed.scheme.lower(),
        netloc=parsed.netloc.lower(),
        fragment="",
    )

    result = normalized.geturl()

    # Remove trailing slash (unless it's the root)
    if result.endswith("/") and len(parsed.path) > 1:
        result = result[:-1]

    return result


# ============================================================================
# Pre-configured patterns for Irish education sources
# ============================================================================


CURRICULUM_ONLINE_PATTERNS = [
    CrawlPattern(
        url_pattern="https://curriculumonline.ie/Junior-Cycle/*",
        extraction_strategy=ExtractionStrategy.MARKDOWN,
        selectors={"content": "div.content-main"},
        metadata_extractors={
            "subject": "h1.page-title",
            "level": "nav.breadcrumb",
        },
        priority=10,
    ),
    CrawlPattern(
        url_pattern="https://curriculumonline.ie/Senior-Cycle/*",
        extraction_strategy=ExtractionStrategy.MARKDOWN,
        selectors={"content": "div.content-main"},
        metadata_extractors={
            "subject": "h1.page-title",
            "level": "nav.breadcrumb",
        },
        priority=10,
    ),
    CrawlPattern(
        url_pattern="https://curriculumonline.ie/*",
        extraction_strategy=ExtractionStrategy.MARKDOWN,
        priority=1,
    ),
]


NCCA_PATTERNS = [
    CrawlPattern(
        url_pattern="https://ncca.ie/*/curriculum/*",
        extraction_strategy=ExtractionStrategy.MARKDOWN,
        selectors={"content": "article.content"},
        priority=10,
    ),
    CrawlPattern(
        url_pattern="https://ncca.ie/*/resources/*",
        extraction_strategy=ExtractionStrategy.MARKDOWN,
        selectors={"content": "article.content"},
        priority=10,
    ),
]


SEC_PATTERNS = [
    CrawlPattern(
        url_pattern="https://examinations.ie/archive/*/*",
        extraction_strategy=ExtractionStrategy.MARKDOWN,
        exclude_patterns=["*.pdf", "*.zip"],
        priority=10,
    ),
]


def get_ireland_education_config() -> CrawlConfig:
    """Get crawl configuration for Irish education sources."""
    return CrawlConfig(
        base_url="https://curriculumonline.ie",
        patterns=[
            *CURRICULUM_ONLINE_PATTERNS,
            *NCCA_PATTERNS,
            *SEC_PATTERNS,
        ],
        max_pages=5000,
        max_depth=5,
        delay_seconds=1.0,
        concurrent_requests=3,
    )
