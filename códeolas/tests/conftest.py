"""Shared test fixtures for códeolas."""

import os
from pathlib import Path

import pytest


@pytest.fixture
def repo_path():
    """Path to códeolas package for testing."""
    return Path(__file__).parent.parent / "codeolas"


@pytest.fixture
def cianfhoghlaim_path():
    """Path to full cianfhoghlaim repo for integration tests."""
    return Path("/Users/cliste/dev/cianfhoghlaim")


@pytest.fixture
def codesola_root():
    """Root path of códeolas project."""
    return Path(__file__).parent.parent


@pytest.fixture
def analyzer(repo_path, tmp_path):
    """Pre-configured analyzer with temp storage."""
    os.environ["LANCEDB_URI"] = str(tmp_path / "lancedb")
    os.environ["CODEOLAS_REPO_PATH"] = str(repo_path)

    from codeolas import CodebaseAnalyzer

    return CodebaseAnalyzer(repo_path)


@pytest.fixture
async def indexed_analyzer(analyzer):
    """Analyzer with indexed codebase."""
    await analyzer.index()
    return analyzer


# Markers
def pytest_configure(config):
    """Configure custom markers."""
    config.addinivalue_line("markers", "slow: marks tests as slow (deselect with '-m \"not slow\"')")
    config.addinivalue_line("markers", "integration: marks tests as integration tests")
