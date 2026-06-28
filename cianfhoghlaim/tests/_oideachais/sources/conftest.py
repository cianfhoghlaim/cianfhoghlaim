"""
Phase 1b test suite for oideachais.

Marker: integration (default per sources.yaml defaults).
USE_LOCAL_SCRAPES=true is set in the session fixture below so the
DLT sources use /stedding/ingest_queue/ instead of live network.

This conftest extends the existing one in oideachais/tests/conftest.py
with sources.yaml-specific fixtures.
"""
from __future__ import annotations

import os
import tempfile
from pathlib import Path

import pytest

# Force local-scrape cache for every test in this tree.
os.environ.setdefault("USE_LOCAL_SCRAPES", "true")
os.environ.setdefault("DAGSTER_HOME", tempfile.mkdtemp())
os.environ.setdefault("FIRECRAWL_API_KEY", "")  # None in tests
os.environ.setdefault("BROWSER_API_URL", "")   # None in tests


@pytest.fixture(scope="session")
def sources_factory():
    """Module-scoped SourceFactory loaded from oideachais/sources.yaml."""
    from oideachais.dlt_utils.source_factory import get_default_factory
    return get_default_factory()


@pytest.fixture
def temp_ducklake_dir(temp_dir: Path) -> Path:
    """Stand-in for the DuckLake S3 backend (local file path)."""
    path = temp_dir / "ducklake"
    path.mkdir(parents=True, exist_ok=True)
    return path
