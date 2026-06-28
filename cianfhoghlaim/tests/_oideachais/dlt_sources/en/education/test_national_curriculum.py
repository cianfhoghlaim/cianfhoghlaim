"""Test the England National Curriculum DLT source.

Mirrors the CCEA test: assert the module imports and the internal
crawl function yields pages (with `status: client_unavailable` when no
backend is configured).

Skipped when the transitive `uk/__init__.py` chain breaks on a
missing `shared.http` module (a pre-existing fragility flagged in
`oideachais/dagster_defs/definitions.py:74-87`).
"""
from __future__ import annotations

import os

import pytest

pytestmark = pytest.mark.integration


def test_national_curriculum_source_constructs() -> None:
    try:
        from dlt_sources.en.education._national_curriculum_helpers import (
            EXAM_BOARD_URLS,
            GOV_UK_CURRICULUM_URLS,
        )
    except ModuleNotFoundError as exc:
        if "shared" in str(exc):
            pytest.skip(f"transitive shared.http import is broken upstream: {exc}")
        raise

    assert GOV_UK_CURRICULUM_URLS is not None
    assert "gov.uk" in GOV_UK_CURRICULUM_URLS["key_stage_1"]
    assert "aqa.org.uk" in EXAM_BOARD_URLS["aqa"]["gcse"]


def test_national_curriculum_yields_pages_with_local_cache() -> None:
    os.environ["FIRECRAWL_API_KEY"] = ""
    os.environ["BROWSER_API_URL"] = ""
    try:
        from dlt_sources.en.education._national_curriculum_helpers import _crawl_gov_uk_curriculum
    except ModuleNotFoundError as exc:
        if "shared" in str(exc):
            pytest.skip(f"transitive shared.http import is broken upstream: {exc}")
        raise

    pages = list(_crawl_gov_uk_curriculum(key_stage="key_stage_1", max_pages=1))
    assert pages
    assert all("status" in p for p in pages)
