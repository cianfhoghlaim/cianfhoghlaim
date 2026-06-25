"""Tests for the UK medicine + UK law DLT assets.

Phase 3.3 of the lateralise change. These are pure smoke
tests — they assert the DLT sources import cleanly, expose the
expected resource names, and the 10 new assets are registered
in the oideachais defs asset graph.

The 3 crown dependencies (IOM, JEY, GGY) have DLT source
placeholders only (`__init__.py`); no real implementation. The
tests for crown deps will be added in a follow-up change once
the source modules are implemented.

Network-dependent row-level tests are deselected by default
(they only run with `pytest -k first_row` and a live network).
"""
from __future__ import annotations

import pytest

# ---------------------------------------------------------------------------
# UK medicine sources
# ---------------------------------------------------------------------------
from dlt_sources.domains.medicine.en.gmc import gmc_source
from dlt_sources.domains.medicine.en.nhs_england import (
    nhs_england_source,
)
from dlt_sources.domains.medicine.en.nice import nice_source
from dlt_sources.domains.medicine.ni.nidirect import (
    nidirect_medicine_source,
)
from dlt_sources.domains.medicine.sct.nhs_scotland import (
    nhs_scotland_source,
)
from dlt_sources.domains.medicine.wls.nhs_wales import (
    nhs_wales_source,
)

# ---------------------------------------------------------------------------
# UK law sources
# ---------------------------------------------------------------------------
from dlt_sources.domains.law.en.legislation import (
    en_legislation_source,
)
from dlt_sources.domains.law.ni.legislation import (
    ni_legislation_source,
)
from dlt_sources.domains.law.sct.legislation import (
    sct_legislation_source,
)
from dlt_sources.domains.law.wls.legislation import (
    wls_legislation_source,
)


# ---------------------------------------------------------------------------
# Parametrised source table — (label, source_fn, expected_resource)
# ---------------------------------------------------------------------------
UK_MEDICINE_SOURCES = [
    ("gmc", gmc_source, "pages"),
    ("nhs_england", nhs_england_source, "pages"),
    ("nice", nice_source, "guidelines_pages"),
    ("nidirect", nidirect_medicine_source, "pages"),
    ("nhs_scotland", nhs_scotland_source, "pages"),
    ("nhs_wales", nhs_wales_source, "pages"),
]

UK_LAW_SOURCES = [
    ("en_legislation", en_legislation_source, "acts"),
    ("ni_legislation", ni_legislation_source, "acts"),
    ("sct_legislation", sct_legislation_source, "acts"),
    ("wls_legislation", wls_legislation_source, "acts"),
]


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------
@pytest.mark.parametrize("name,source,expected_resource", UK_MEDICINE_SOURCES)
def test_uk_medicine_source_has_expected_resource(
    name: str, source, expected_resource: str
) -> None:
    src = source()
    assert expected_resource in src.resources, (
        f"{name}_source() must expose a {expected_resource!r} resource; "
        f"got {list(src.resources)!r}"
    )


@pytest.mark.parametrize("name,source,expected_resource", UK_LAW_SOURCES)
def test_uk_law_source_has_expected_resource(
    name: str, source, expected_resource: str
) -> None:
    src = source()
    assert expected_resource in src.resources, (
        f"{name}_source() must expose a {expected_resource!r} resource; "
        f"got {list(src.resources)!r}"
    )


def test_uk_medicine_assets_are_registered() -> None:
    """The 6 UK medicine assets must be in the oideachais defs asset graph."""
    from dagster_defs.definitions import defs

    ag = defs.resolve_asset_graph()
    names = {k.path[-1] for k in ag.get_all_asset_keys()}
    for name in (
        "medicine_en_gmc",
        "medicine_en_nhs_england",
        "medicine_en_nice",
        "medicine_ni_nidirect",
        "medicine_sct_nhs_scotland",
        "medicine_wls_nhs_wales",
    ):
        assert name in names, f"Asset {name!r} missing from defs"


def test_uk_law_assets_are_registered() -> None:
    """The 4 UK law assets must be in the oideachais defs asset graph."""
    from dagster_defs.definitions import defs

    ag = defs.resolve_asset_graph()
    names = {k.path[-1] for k in ag.get_all_asset_keys()}
    for name in (
        "law_en_legislation",
        "law_ni_legislation",
        "law_sct_legislation",
        "law_wls_legislation",
    ):
        assert name in names, f"Asset {name!r} missing from defs"


def test_asset_graph_has_at_least_225_assets() -> None:
    """Phase 3.3 floor: 218 (pre-Phase-3.3) + 10 (UK) = 228."""
    from dagster_defs.definitions import defs

    ag = defs.resolve_asset_graph()
    n = sum(1 for _ in ag.get_all_asset_keys())
    assert n >= 225, (
        f"Expected >= 225 assets (Phase 3.3 floor), got {n}. "
        "Did the 10 UK medicine/law assets fail to register?"
    )
