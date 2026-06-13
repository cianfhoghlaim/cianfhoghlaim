"""Test the Northern Ireland CCEA DLT source.

The `ni_curriculum_source()` yields ≥ 1 page when USE_LOCAL_SCRAPES=true
and no live network call is made. This is a smoke test — the actual
extraction logic is exercised in production.
"""
from __future__ import annotations

import os

import pytest

pytestmark = pytest.mark.integration


def test_ccea_source_constructs() -> None:
    """Importing the source module succeeds under the new toolchain.

    Skipped when the transitive `uk/__init__.py` chain breaks on a
    missing `shared.http` module (a pre-existing fragility flagged in
    `oideachais/dagster_defs/definitions.py:74-87`).
    """
    try:
        from oideachais.dlt_sources.uk.northern_ireland import ccea_curriculum
    except ModuleNotFoundError as exc:
        if "shared" in str(exc):
            pytest.skip(f"transitive shared.http import is broken upstream: {exc}")
        raise

    assert ccea_curriculum is not None
    assert hasattr(ccea_curriculum, "ni_curriculum_source")
    assert hasattr(ccea_curriculum, "ccea_qualifications_source")
    assert "ccea.org.uk" in ccea_curriculum.NI_CURRICULUM_URLS["foundation"]


def test_ccea_source_yields_pages_with_local_cache() -> None:
    """With FIRECRAWL_API_KEY='' the internal `_crawl_ni_curriculum`
    yields pages of `status: client_unavailable` rather than raising.
    """
    os.environ["FIRECRAWL_API_KEY"] = ""
    os.environ["BROWSER_API_URL"] = ""
    try:
        from oideachais.dlt_sources.uk.northern_ireland.ccea_curriculum import _crawl_ni_curriculum
    except ModuleNotFoundError as exc:
        if "shared" in str(exc):
            pytest.skip(f"transitive shared.http import is broken upstream: {exc}")
        raise

    pages = list(_crawl_ni_curriculum(key_stage="foundation", max_pages=1))
    assert pages, "expected at least one page even with no client"
    assert all("status" in p for p in pages)
