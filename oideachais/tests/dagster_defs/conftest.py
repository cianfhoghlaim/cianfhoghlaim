"""Pytest fixtures for `oideachais/tests/dagster_defs/`.

The `temp_ducklake` autouse fixture:

  * Sets up a per-test DUCKLAKE_* env (all values point to a
    throwaway local Postgres + a tempdir-backed S3 stand-in).
  * Imports from `dagster_defs.definitions` use bare module names
    (cwd = /app/oideachais) — see AGENTS.md "Zero Absolute Namespaces".
  * Auto-cleans up the temp DuckLake config after the test.

The conftest is intentionally tiny: it does not spin up a real
DuckLake instance. Dagster defs *construction* (the only thing
test_definitions_loads.py exercises) does not need an active
DuckLake — that comes in test_curriculum_dlt_assets.py where
`@pytest.mark.integration` runs against the lakehouse stack.
"""
from __future__ import annotations

import os
import shutil
import tempfile
from collections.abc import Generator
from pathlib import Path

import pytest


# ---------------------------------------------------------------------------
# Autouse: per-test DuckLake environment
# ---------------------------------------------------------------------------
@pytest.fixture(autouse=True)
def temp_ducklake(
    tmp_path: Path, monkeypatch: pytest.MonkeyPatch
) -> Generator[Path, None, None]:
    """Give every test a clean DUCKLAKE_* environment.

    The defaults below point at a *fake* Postgres + a *tempdir* S3
    stand-in. The defs construction test never actually talks to
    these — it only checks that `defs` builds and has >=100
    assets. Integration tests that need a real lakehouse live in
    test_curriculum_dlt_assets.py and are marked
    `@pytest.mark.integration` (skipped unless the stack is up).
    """
    s3_root = tmp_path / "s3"
    s3_root.mkdir()
    monkeypatch.setenv("DUCKLAKE_POSTGRES_HOST", "localhost")
    monkeypatch.setenv("DUCKLAKE_POSTGRES_PORT", "5432")
    monkeypatch.setenv("DUCKLAKE_POSTGRES_DB", "ducklake_test")
    monkeypatch.setenv("DUCKLAKE_POSTGRES_USER", "test")
    monkeypatch.setenv("DUCKLAKE_POSTGRES_PASSWORD", "test")
    monkeypatch.setenv("AWS_ENDPOINT_URL", f"http://localhost:9000")
    monkeypatch.setenv("AWS_ACCESS_KEY_ID", "test")
    monkeypatch.setenv("AWS_SECRET_ACCESS_KEY", "test")
    monkeypatch.setenv("AWS_REGION", "garage")
    monkeypatch.setenv("OIDEACHAIS_ENV", "test")
    yield s3_root
    # tmp_path is auto-cleaned by pytest


# ---------------------------------------------------------------------------
# Optional: skip-integration marker (the test directory imports nothing
# from the live lakehouse; this is here for downstream test files).
# ---------------------------------------------------------------------------
def pytest_collection_modifyitems(config, items):
    for item in items:
        if "integration" in item.keywords:
            if not os.environ.get("LAKEHOUSE_UP"):
                item.add_marker(pytest.mark.skip(reason="set LAKEHOUSE_UP=1 to run"))
