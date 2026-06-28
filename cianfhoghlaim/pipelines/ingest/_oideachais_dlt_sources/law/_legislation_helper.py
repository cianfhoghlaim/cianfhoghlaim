"""
oideachais.dlt_sources.law._legislation_helper — Shared
helper for crawling legislation.gov.uk XML / HTML endpoints.

The UK has a single legislation.gov.uk domain with sub-paths for
each jurisdiction (`/uksi`, `/ukpga`, `/nisi`, `/asc`, `/ssi`,
`/wsi`, etc.). This module exposes a single `_crawl_legislation`
generator that the per-nation sub-packages call with the right
`include_paths` filter.
"""
from __future__ import annotations

from collections.abc import Iterator
from typing import Any

import structlog

from ...ireland.curriculum_source import _crawl_source  # type: ignore[import-not-found]

logger = structlog.get_logger(__name__)


def _crawl_legislation(
    jurisdiction_code: str,
    include_paths: list[str],
    max_pages: int = 50,
) -> Iterator[dict[str, Any]]:
    """Crawl the legislation.gov.uk jurisdiction sub-tree.

    `jurisdiction_code` is one of `ni | en | sct | wls` (the nation
    code) and is added to each page dict as the `nation` field.
    """
    base_url = "https://www.legislation.gov.uk"
    for page in _crawl_source(
        source_name=f"legislation.{jurisdiction_code}",
        base_url=base_url,
        include_paths=include_paths,
        max_pages=max_pages,
        max_depth=2,
    ):
        page["nation"] = jurisdiction_code
        page["domain"] = "law"
        page["entity"] = "legislation"
        page["jurisdiction_path"] = include_paths[0] if include_paths else None
        yield page
