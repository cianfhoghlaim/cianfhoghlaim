"""Shared fixtures for the uog_official_docs / nui_federation / students_union
test suites."""

from __future__ import annotations

import sys
from pathlib import Path

import pytest

_REPO_ROOT = Path(__file__).resolve().parents[2]
_SRUTH_BROWSER_ROOT = _REPO_ROOT / "bonneagar" / "stacks" / "browser"
_OFFICIAL_DOCS_PARENT = (
    _REPO_ROOT
    / "dlt_sources"
    / "british_isles"
    / "ireland"
    / "education"
    / "university"
)

for _path in (_SRUTH_BROWSER_ROOT, _OFFICIAL_DOCS_PARENT):
    if _path.is_dir() and str(_path) not in sys.path:
        sys.path.insert(0, str(_path))


@pytest.fixture(autouse=True)
def _fixture_only(monkeypatch):
    """Default to fixture-mode for every test in this package."""
    # Reset the lru_cache'd `get_default_secrets_resolver()` so each
    # test starts with a clean SecretsResolver.
    try:
        from sruth_browser.core.secrets import reset_default_secrets_resolver
        reset_default_secrets_resolver()
    except ImportError:
        pass

    monkeypatch.setenv("OOG_STUDENT_ID", "fixture-only")
    monkeypatch.setenv("OOG_STUDENT_PASSWORD", "fixture-only")
    monkeypatch.setenv("UNIVERSITY_SSO_STUDENT_ID", "fixture-only")
    monkeypatch.setenv("UNIVERSITY_SSO_PASSWORD", "fixture-only")
    # No real Firecrawl credentials — Stage 0 audit must short-circuit.
    for var in (
        "FIRECRAWL_API_KEY",
        "MOTHERDUCK_TOKEN",
        "BONNEAGAR_LAKEHOUSE_URI",
        "DUCKLAKE_POSTGRES_PASSWORD",
        "QUB_SSO_STUDENT_ID",
        "QUB_SSO_PASSWORD",
        "ULSTER_SSO_STUDENT_ID",
        "ULSTER_SSO_PASSWORD",
    ):
        monkeypatch.delenv(var, raising=False)
    monkeypatch.setenv("STAGE_0_MAX_CREDITS", "20")
