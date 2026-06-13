"""Smoke test that `oideachais.dagster_defs.definitions:defs` constructs
without ImportError under the new toolchain.

Replaces the ad-hoc `try/except ImportError` in definitions.py with an
explicit pytest that asserts the import succeeds. The actual asset
materialization is exercised in test_curriculum_dlt_assets.py and the
Leaving Cert asset test.
"""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.integration


def test_definitions_module_imports() -> None:
    """Importing `oideachais.dagster_defs.definitions` must not raise."""
    import importlib

    mod = importlib.import_module("oideachais.dagster_defs.definitions")
    assert hasattr(mod, "defs")
    assert hasattr(mod, "all_jobs")
    assert hasattr(mod, "CONCURRENCY_LIMITS")
    # The legacy `try/except ImportError` block at module top must have
    # allowed every dependency to load.
    assert mod.all_jobs is not None
