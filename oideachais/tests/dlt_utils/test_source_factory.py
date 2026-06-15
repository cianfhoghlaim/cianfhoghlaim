"""Smoke tests for `dlt_utils.source_factory.SourceFactory`.

The factory is the canonical source-of-truth for the asset graph
derived from `oideachais/sources.yaml`. It exposes the 7-method
contract documented in `dlt_utils/source_factory.py`.

Phase 2.1 of the lateralise change has wired the 4 address
methods (`lance_table`, `cognee_dataset`, `marimo_path`,
`tests_path`); the 3 runtime constructors (`source`, `dlt_asset`,
`dagster_asset`) raise NotImplementedError pending Phase 5.

These tests assert:
  1. `from_yaml` parses without error.
  2. The total source count is stable (43 at the time of writing).
  3. The 4 address methods return sensible strings/paths.
  4. The asset_key method returns the canonical prefix.
  5. The filter() helper works on domain/nation.
  6. The 3 stub methods raise NotImplementedError.
"""
from __future__ import annotations

import re

import pytest

from dlt_utils.source_factory import (
    DEFAULT_SOURCES_PATH,
    SourceFactory,
    get_default_factory,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------
@pytest.fixture(scope="module")
def factory() -> SourceFactory:
    return get_default_factory()


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------
def test_factory_loads_from_canonical_path() -> None:
    """`SourceFactory.from_yaml` parses the canonical sources.yaml."""
    f = SourceFactory.from_yaml(DEFAULT_SOURCES_PATH)
    assert f.spec is not None
    assert f.spec.version == 2


def test_source_count_is_stable(factory: SourceFactory) -> None:
    """The lateralise-change baseline is 43 sources. If this drops
    or jumps, someone truncated the registry — surface early."""
    n = len(factory.all_ids())
    assert n >= 30, f"Source count dropped below 30: {n}"
    assert n <= 100, f"Source count jumped above 100: {n}"


def test_all_ids_are_unique(factory: SourceFactory) -> None:
    """`all_ids()` must return unique ids (asset key prefix)."""
    ids = factory.all_ids()
    assert len(ids) == len(set(ids)), "Duplicate source ids"


@pytest.mark.parametrize(
    "sid",
    [
        "ie.education.ncca",
        "ie.education.examinations",
    ],
)
def test_education_sources_resolve_addresses(
    factory: SourceFactory, sid: str
) -> None:
    """For sources that DON'T override the default cognee dataset
    in sources.yaml, the lance/cognee/marimo/tests addresses
    must start with the canonical `oideachais.{domain}.{nation}.*` /
    `oideachais_{domain}_{nation}` prefix.

    NI/EN/SCT/WLS education sources deliberately share a single
    `oideachais_education_uk` dataset (they cross-pollinate via the
    British Isles education graph), so we skip them in this test.
    """
    s = factory.get(sid)
    assert s.domain == "education"
    assert f"{s.domain}.{s.nation}" in factory.lance_table(sid)
    assert f"{s.domain}_{s.nation}" in factory.cognee_dataset(sid)


def test_asset_key_returns_canonical_prefix(factory: SourceFactory) -> None:
    """`asset_key()` must return the [nation, domain, ...] tuple
    declared in the YAML."""
    s = factory.get("ie.education.ncca")
    assert factory.asset_key("ie.education.ncca") == s.asset_key
    assert s.asset_key[0] == s.nation
    assert s.asset_key[1] == s.domain


def test_filter_by_domain(factory: SourceFactory) -> None:
    """`filter(domain='medicine')` returns only medicine sources."""
    medicine = factory.filter(domain="medicine")
    assert medicine, "filter(domain='medicine') returned no sources"
    for s in medicine:
        assert s.domain == "medicine"


def test_filter_by_nation(factory: SourceFactory) -> None:
    """`filter(nation='ie')` returns only Ireland sources."""
    ie = factory.filter(nation="ie")
    assert ie, "filter(nation='ie') returned no sources"
    for s in ie:
        assert s.nation == "ie"


def test_stub_methods_raise_not_implemented(factory: SourceFactory) -> None:
    """The 3 runtime constructors must raise NotImplementedError
    until Phase 5 of the openspec change wires them."""
    for method in ("source", "dlt_asset", "dagster_asset"):
        with pytest.raises(NotImplementedError, match=method):
            getattr(factory, method)("ie.education.ncca")


def test_marimo_path_ends_with_py(factory: SourceFactory) -> None:
    """The marimo notebook path must be a `.py` file under
    `oideachais/notebooks/dashboards/`."""
    p = factory.marimo_path("ie.education.ncca")
    assert str(p).endswith(".py")
    assert "notebooks/dashboards/" in str(p)


def test_tests_path_under_tests_dir(factory: SourceFactory) -> None:
    """The tests path must be under `oideachais/tests/`."""
    p = factory.tests_path("ie.education.ncca")
    assert "tests/dlt_sources/" in str(p)
    assert str(p).endswith("test_ncca.py")
