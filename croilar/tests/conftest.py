"""Pytest configuration for the croilar subproject.

Sets up:
- USE_LOCAL_SCRAPES=true so DLT pipelines route to the curated cache
  instead of live API/scraper calls (per AGENTS.md critical rule #2)
- DLT_ENVIRONMENT=local so DuckLake factory picks Garage + local Postgres
- A clean data/ directory under tmp_path for every test
"""

from __future__ import annotations

import os
import sys
from pathlib import Path

import pytest

# Repo root (this file lives at croilar/tests/conftest.py)
CROILAR_ROOT = Path(__file__).resolve().parent.parent
REPO_ROOT = CROILAR_ROOT.parent


def pytest_configure(config: pytest.Config) -> None:
    """Set up env vars before any test imports the pipelines."""
    # Honour AGENTS.md rule: never execute live scrapes in tests
    os.environ.setdefault("USE_LOCAL_SCRAPES", "true")
    # Local DuckLake stack
    os.environ.setdefault("DLT_ENVIRONMENT", "local")
    os.environ.setdefault("USE_DUCKLAKE", "false")  # use plain DuckDB for tests
    # No telemetry noise
    os.environ.setdefault("DLT_DISABLE_TELEMETRY", "true")
    # DLT destination default — point at a tmp dir we'll create
    os.environ.setdefault("DUCKDB_PATH", str(CROILAR_ROOT / "data" / "test.duckdb"))

    # Make the croilar subproject importable as a package
    croilar_str = str(CROILAR_ROOT)
    if croilar_str not in sys.path:
        sys.path.insert(0, croilar_str)

    # The repo root contains the author dir + sibling packages
    repo_str = str(REPO_ROOT)
    if repo_str not in sys.path:
        sys.path.insert(0, repo_str)


@pytest.fixture(scope="session", autouse=True)
def ensure_data_dir() -> Path:
    """Make sure croilar/data/ exists for any pipeline that writes there."""
    data_dir = CROILAR_ROOT / "data"
    data_dir.mkdir(parents=True, exist_ok=True)
    return data_dir


@pytest.fixture(autouse=True)
def isolate_data_dir(tmp_path: Path, monkeypatch: pytest.MonkeyPatch) -> Path:
    """Redirect every pipeline to a per-test tmp data dir.

    This prevents parallel test runs from clobbering the same DuckDB
    and keeps each test fully isolated.
    """
    test_data = tmp_path / "data"
    test_data.mkdir(parents=True, exist_ok=True)
    monkeypatch.setenv("DUCKDB_PATH", str(test_data / "test.duckdb"))
    monkeypatch.setenv("CROILAR_REPO_ROOT", str(REPO_ROOT))
    return test_data
