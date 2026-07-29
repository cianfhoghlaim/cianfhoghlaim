"""Shared helper for crawling legislation.gov.uk XML / HTML endpoints.

The UK has a single legislation.gov.uk domain with sub-paths for
each jurisdiction (``/uksi``, ``/ukpga``, ``/nisi``, ``/asc``,
``/ssi``, ``/wsi``, etc.). This module exposes a single
``_crawl_legislation`` generator that the per-nation sub-packages
call with the right ``include_paths`` filter.

Path-drift history: this helper was previously at
``dlt_sources/law/_legislation_helper.py`` (per-nation legislation
files import from that path) and at
``dlt_sources/british_isles/_legislation_helper.py`` (where it
actually lives). Both import paths are now supported — per-nation
legislation files import ``dlt_sources.british_isles._legislation_helper``
directly (no shim required), and the helper is self-contained
(uses the canonical ``crawl_site`` primitive).
"""
from __future__ import annotations

from collections.abc import Iterator
from typing import Any

import structlog

# Self-contained: use the modern ``crawl_site`` primitive from the
# ``dlt_sources.common`` helpers instead of importing a missing
# ``_crawl_source`` from ``dlt_sources.british_isles.ireland.curriculum_source``.
from dlt_sources.common.site_crawler import crawl_site

logger = structlog.get_logger(__name__)


def _crawl_source(
    source_name: str,
    base_url: str,
    include_paths: list[str] | None = None,
    exclude_paths: list[str] | None = None,
    max_pages: int = 50,
    max_depth: int = 2,
) -> Iterator[dict[str, Any]]:
    """Local shim around ``crawl_site`` that preserves the legacy
    ``_crawl_source(source_name, base_url, ...)`` signature used by
    per-nation legislation fallbacks.

    Per-nation sources (england/medicine, wales/medicine, jersey/law,
    jersey/medicine, etc.) define their own local ``_crawl_source``
    shim with the same signature so they degrade gracefully if the
    shared legislation helper is unavailable.
    """
    logger.debug("_crawl_source: %s %s", source_name, base_url)
    for page in crawl_site(
        base_url=base_url,
        include_paths=include_paths,
        exclude_paths=exclude_paths,
        max_pages=max_pages,
        max_depth=max_depth,
    ):
        yield page.to_dict()


def _crawl_legislation(
    jurisdiction_code: str,
    include_paths: list[str],
    max_pages: int = 50,
) -> Iterator[dict[str, Any]]:
    """Crawl the legislation.gov.uk jurisdiction sub-tree.

    ``jurisdiction_code`` is one of ``ni | en | sct | wls`` (the
    nation code) and is added to each page dict as the ``nation``
    field.
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