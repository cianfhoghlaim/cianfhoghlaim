"""
Pagination utilities for DLT REST API sources.

Supports all common pagination patterns:
- Cursor-based (next token in response)
- Offset-based (skip/limit)
- Page number (page/per_page)
- Header link (RFC 5988 Link header)
- JSON link (next URL in response body)

Based on patterns from taighde/dlt/ research.
"""

from __future__ import annotations

import re
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any, Generator, Iterator
from urllib.parse import parse_qs, urlencode, urlparse, urlunparse

import httpx


@dataclass
class PaginationState:
    """Current state of pagination."""
    has_more: bool = True
    next_cursor: str | None = None
    next_url: str | None = None
    current_page: int = 1
    current_offset: int = 0
    total_items: int | None = None
    total_pages: int | None = None


class PaginationStrategy(ABC):
    """Base class for pagination strategies."""

    @abstractmethod
    def get_next_request(
        self,
        base_url: str,
        response: httpx.Response,
        state: PaginationState,
    ) -> tuple[str | None, dict[str, Any]]:
        """
        Get the next request URL and params.

        Args:
            base_url: Original request URL
            response: Previous response
            state: Current pagination state

        Returns:
            Tuple of (next_url, params) or (None, {}) if no more pages
        """
        pass

    @abstractmethod
    def update_state(
        self,
        response: httpx.Response,
        data: Any,
        state: PaginationState,
    ) -> PaginationState:
        """
        Update pagination state from response.

        Args:
            response: HTTP response
            data: Parsed response data
            state: Current state

        Returns:
            Updated state
        """
        pass


@dataclass
class CursorPagination(PaginationStrategy):
    """
    Cursor-based pagination (next token in response).

    Common in APIs like Slack, Stripe, GitHub.

    Usage:
        paginator = CursorPagination(
            cursor_path="meta.next_cursor",
            cursor_param="cursor",
        )
    """
    cursor_path: str = "next_cursor"
    cursor_param: str = "cursor"
    has_more_path: str | None = None

    def _extract_value(self, data: Any, path: str) -> Any:
        """Extract value from nested dict using dot notation."""
        parts = path.split(".")
        current = data
        for part in parts:
            if isinstance(current, dict):
                current = current.get(part)
            elif isinstance(current, list) and part.isdigit():
                current = current[int(part)]
            else:
                return None
        return current

    def get_next_request(
        self,
        base_url: str,
        response: httpx.Response,
        state: PaginationState,
    ) -> tuple[str | None, dict[str, Any]]:
        if not state.has_more or not state.next_cursor:
            return None, {}

        return base_url, {self.cursor_param: state.next_cursor}

    def update_state(
        self,
        response: httpx.Response,
        data: Any,
        state: PaginationState,
    ) -> PaginationState:
        next_cursor = self._extract_value(data, self.cursor_path)
        has_more = bool(next_cursor)

        if self.has_more_path:
            has_more = bool(self._extract_value(data, self.has_more_path))

        return PaginationState(
            has_more=has_more,
            next_cursor=next_cursor,
        )


@dataclass
class OffsetPagination(PaginationStrategy):
    """
    Offset-based pagination (skip/limit).

    Common in SQL-backed APIs.

    Usage:
        paginator = OffsetPagination(
            limit=100,
            offset_param="offset",
            limit_param="limit",
        )
    """
    limit: int = 100
    offset_param: str = "offset"
    limit_param: str = "limit"
    total_path: str | None = "total"

    def _extract_value(self, data: Any, path: str) -> Any:
        """Extract value from nested dict using dot notation."""
        parts = path.split(".")
        current = data
        for part in parts:
            if isinstance(current, dict):
                current = current.get(part)
            else:
                return None
        return current

    def get_next_request(
        self,
        base_url: str,
        response: httpx.Response,
        state: PaginationState,
    ) -> tuple[str | None, dict[str, Any]]:
        if not state.has_more:
            return None, {}

        return base_url, {
            self.offset_param: state.current_offset,
            self.limit_param: self.limit,
        }

    def update_state(
        self,
        response: httpx.Response,
        data: Any,
        state: PaginationState,
    ) -> PaginationState:
        # Get items from response
        items = data if isinstance(data, list) else data.get("data", data.get("items", []))
        item_count = len(items) if isinstance(items, list) else 0

        new_offset = state.current_offset + item_count
        total = None

        if self.total_path:
            total = self._extract_value(data, self.total_path)

        # Determine if more pages exist
        has_more = item_count >= self.limit
        if total is not None:
            has_more = new_offset < total

        return PaginationState(
            has_more=has_more,
            current_offset=new_offset,
            total_items=total,
        )


@dataclass
class PageNumberPagination(PaginationStrategy):
    """
    Page number pagination (page/per_page).

    Common in traditional web APIs.

    Usage:
        paginator = PageNumberPagination(
            per_page=50,
            page_param="page",
            per_page_param="per_page",
        )
    """
    per_page: int = 50
    page_param: str = "page"
    per_page_param: str = "per_page"
    total_pages_path: str | None = "total_pages"
    total_items_path: str | None = "total"

    def _extract_value(self, data: Any, path: str) -> Any:
        """Extract value from nested dict using dot notation."""
        parts = path.split(".")
        current = data
        for part in parts:
            if isinstance(current, dict):
                current = current.get(part)
            else:
                return None
        return current

    def get_next_request(
        self,
        base_url: str,
        response: httpx.Response,
        state: PaginationState,
    ) -> tuple[str | None, dict[str, Any]]:
        if not state.has_more:
            return None, {}

        return base_url, {
            self.page_param: state.current_page,
            self.per_page_param: self.per_page,
        }

    def update_state(
        self,
        response: httpx.Response,
        data: Any,
        state: PaginationState,
    ) -> PaginationState:
        items = data if isinstance(data, list) else data.get("data", data.get("items", []))
        item_count = len(items) if isinstance(items, list) else 0

        new_page = state.current_page + 1
        total_pages = None
        total_items = None

        if self.total_pages_path:
            total_pages = self._extract_value(data, self.total_pages_path)
        if self.total_items_path:
            total_items = self._extract_value(data, self.total_items_path)

        # Determine if more pages
        has_more = item_count >= self.per_page
        if total_pages is not None:
            has_more = new_page <= total_pages

        return PaginationState(
            has_more=has_more,
            current_page=new_page,
            total_pages=total_pages,
            total_items=total_items,
        )


@dataclass
class HeaderLinkPagination(PaginationStrategy):
    """
    RFC 5988 Link header pagination.

    Common in GitHub API, many REST APIs.

    Parses headers like:
    Link: <https://api.example.com/items?page=2>; rel="next"

    Usage:
        paginator = HeaderLinkPagination()
    """
    link_header: str = "Link"
    rel_next: str = "next"

    def _parse_link_header(self, header: str) -> dict[str, str]:
        """Parse RFC 5988 Link header."""
        links = {}
        for part in header.split(","):
            match = re.match(r'<([^>]+)>;\s*rel="([^"]+)"', part.strip())
            if match:
                url, rel = match.groups()
                links[rel] = url
        return links

    def get_next_request(
        self,
        base_url: str,
        response: httpx.Response,
        state: PaginationState,
    ) -> tuple[str | None, dict[str, Any]]:
        if not state.has_more or not state.next_url:
            return None, {}

        return state.next_url, {}

    def update_state(
        self,
        response: httpx.Response,
        data: Any,
        state: PaginationState,
    ) -> PaginationState:
        link_header = response.headers.get(self.link_header, "")
        links = self._parse_link_header(link_header)

        next_url = links.get(self.rel_next)

        return PaginationState(
            has_more=bool(next_url),
            next_url=next_url,
        )


@dataclass
class JSONLinkPagination(PaginationStrategy):
    """
    JSON body link pagination.

    Next URL is in response body.

    Usage:
        paginator = JSONLinkPagination(next_url_path="links.next")
    """
    next_url_path: str = "next"
    has_more_path: str | None = None

    def _extract_value(self, data: Any, path: str) -> Any:
        """Extract value from nested dict using dot notation."""
        parts = path.split(".")
        current = data
        for part in parts:
            if isinstance(current, dict):
                current = current.get(part)
            else:
                return None
        return current

    def get_next_request(
        self,
        base_url: str,
        response: httpx.Response,
        state: PaginationState,
    ) -> tuple[str | None, dict[str, Any]]:
        if not state.has_more or not state.next_url:
            return None, {}

        return state.next_url, {}

    def update_state(
        self,
        response: httpx.Response,
        data: Any,
        state: PaginationState,
    ) -> PaginationState:
        next_url = self._extract_value(data, self.next_url_path)
        has_more = bool(next_url)

        if self.has_more_path:
            has_more = bool(self._extract_value(data, self.has_more_path))

        return PaginationState(
            has_more=has_more,
            next_url=next_url,
        )


def get_pagination_strategy(
    strategy_type: str,
    **kwargs: Any,
) -> PaginationStrategy:
    """
    Factory function for pagination strategies.

    Args:
        strategy_type: One of 'cursor', 'offset', 'page', 'header_link', 'json_link'
        **kwargs: Strategy-specific configuration

    Returns:
        Configured pagination strategy
    """
    strategies = {
        "cursor": CursorPagination,
        "offset": OffsetPagination,
        "page": PageNumberPagination,
        "header_link": HeaderLinkPagination,
        "json_link": JSONLinkPagination,
    }

    if strategy_type not in strategies:
        raise ValueError(
            f"Unknown pagination strategy: {strategy_type}. "
            f"Choose from: {list(strategies.keys())}"
        )

    return strategies[strategy_type](**kwargs)
