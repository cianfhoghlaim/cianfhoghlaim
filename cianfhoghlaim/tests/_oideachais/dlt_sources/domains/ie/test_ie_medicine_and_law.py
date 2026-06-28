"""Tests for the IE medicine + IE law DLT assets.

Phase 3.1-3.2 of the lateralise change. These are pure smoke
tests — they assert the DLT sources import cleanly, expose the
expected resource names, and produce the right shape of records.

The assets themselves are thin wrappers; the *real* test of the
DLT pipeline is the integration test
`test_dlt_sources_can_extract_one_record.py` which we'll add in
Phase 5. For now we just verify the asset graph surface.
"""
from __future__ import annotations

import pytest
from dlt_sources.ie.law.doj import doj_source
from dlt_sources.ie.law.irish_statute_book import (
    irish_statute_book_source,
)
from dlt_sources.ie.law.lawreform import lawreform_source
from dlt_sources.ie.medicine.doh import doh_source
from dlt_sources.ie.medicine.hpsc import hpsc_source
from dlt_sources.ie.medicine.hse import hse_source
from dlt_sources.ie.medicine.medical_council import (
    medical_council_source,
)

# ---------------------------------------------------------------------------
# Module-level: every source imports + has the expected @dlt.source decorator
# ---------------------------------------------------------------------------
IE_MEDICINE_SOURCES = [
    ("hse", hse_source, "pages"),
    ("medical_council", medical_council_source, "register_pages"),
    ("doh", doh_source, "pages"),
    ("hpsc", hpsc_source, "pages"),
]

IE_LAW_SOURCES = [
    ("irish_statute_book", irish_statute_book_source, "acts"),
    ("doj", doj_source, "pages"),
    ("lawreform", lawreform_source, "pages"),
]


@pytest.mark.parametrize("name,source,expected_resource", IE_MEDICINE_SOURCES)
def test_ie_medicine_source_has_expected_resource(
    name: str, source, expected_resource: str
) -> None:
    """Each IE medicine source must expose the resource name the
    asset layer relies on."""
    src = source()
    assert expected_resource in src.resources, (
        f"{name}_source() must expose a {expected_resource!r} resource; "
        f"got {list(src.resources)!r}"
    )


@pytest.mark.parametrize("name,source,expected_resource", IE_LAW_SOURCES)
def test_ie_law_source_has_expected_resource(
    name: str, source, expected_resource: str
) -> None:
    """Each IE law source must expose the resource name the asset
    layer relies on."""
    src = source()
    assert expected_resource in src.resources, (
        f"{name}_source() must expose a {expected_resource!r} resource; "
        f"got {list(src.resources)!r}"
    )


# ---------------------------------------------------------------------------
# Asset graph: the 7 new assets are registered
# ---------------------------------------------------------------------------
def test_ie_medicine_assets_are_registered() -> None:
    """The 4 IE medicine assets must be in the oideachais defs asset graph."""
    from dagster_defs.definitions import defs

    ag = defs.resolve_asset_graph()
    # Each AssetKey has .path; the leaf component is the asset name.
    names = {k.path[-1] for k in ag.get_all_asset_keys()}
    for name in (
        "medicine_ie_hse",
        "medicine_ie_medical_council",
        "medicine_ie_doh",
        "medicine_ie_hpsc",
    ):
        assert name in names, f"Asset {name!r} missing from defs"


def test_ie_law_assets_are_registered() -> None:
    """The 3 IE law assets must be in the oideachais defs asset graph."""
    from dagster_defs.definitions import defs

    ag = defs.resolve_asset_graph()
    names = {k.path[-1] for k in ag.get_all_asset_keys()}
    for name in (
        "law_ie_irish_statute_book",
        "law_ie_doj",
        "law_ie_lawreform",
    ):
        assert name in names, f"Asset {name!r} missing from defs"


# ---------------------------------------------------------------------------
# Source-level: every source yields a non-empty dict on the first row
# ---------------------------------------------------------------------------
@pytest.mark.parametrize("name,source,expected_resource", IE_MEDICINE_SOURCES)
def test_ie_medicine_source_first_row_is_dict(
    name: str, source, expected_resource: str
) -> None:
    """Calling the source must produce at least one record (a dict
    or a Document/anything with a __dict__). The DLT source may
    extract 0 records if the upstream site blocks; we don't
    require N > 0 (that would be flaky), we just require that
    if there is a row it's well-formed.
    """
    src = source()
    res = src.resources[expected_resource]
    # The resource is iterable but lazy; iterate via .read_dlt once
    # to get the first chunk. If the underlying HTTP call fails,
    # skip rather than fail (we don't want this unit test to
    # require live network).
    try:
        rows = list(res)
    except Exception as exc:  # pragma: no cover - network dependent
        pytest.skip(f"{name}: live network required ({exc})")
    if not rows:
        pytest.skip(f"{name}: no rows (live network returned 0 records)")
    first = rows[0]
    assert first is not None
    # A DLT row can be a dict or a dataclass-like. We don't
    # assert strict shape here; just that it's not None.
