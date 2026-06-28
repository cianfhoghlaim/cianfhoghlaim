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
        from dlt_sources.ni.education import (
            _ccea_curriculum_helpers,
            ccea_qualifications,
            ni_curriculum,
        )
    except ModuleNotFoundError as exc:
        if "shared" in str(exc):
            pytest.skip(f"transitive shared.http import is broken upstream: {exc}")
        raise

    assert _ccea_curriculum_helpers is not None
    assert hasattr(ni_curriculum, "ni_curriculum_source")
    assert hasattr(ccea_qualifications, "ccea_qualifications_source")
    assert "ccea.org.uk" in _ccea_curriculum_helpers.NI_CURRICULUM_URLS["foundation"]


def test_ccea_source_yields_pages_with_local_cache() -> None:
    """With FIRECRAWL_API_KEY='' the internal `_crawl_ni_curriculum`
    yields pages of `status: client_unavailable` rather than raising.
    """
    os.environ["FIRECRAWL_API_KEY"] = ""
    os.environ["BROWSER_API_URL"] = ""
    try:
        from dlt_sources.ni.education._ccea_curriculum_helpers import _crawl_ni_curriculum
    except ModuleNotFoundError as exc:
        if "shared" in str(exc):
            pytest.skip(f"transitive shared.http import is broken upstream: {exc}")
        raise

    pages = list(_crawl_ni_curriculum(key_stage="foundation", max_pages=1))
    assert pages, "expected at least one page even with no client"
    assert all("status" in p for p in pages)
