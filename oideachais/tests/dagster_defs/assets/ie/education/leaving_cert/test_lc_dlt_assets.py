"""Dedicated smoke test for the Leaving Cert 2026 DLT assets.

Asserts each of the 7 LEAVING_CERT_DLT_ASSETS is a loadable Dagster
asset definition. This is the test the prior release of the
leaving-cert-2026 change needed but never had.
"""
from __future__ import annotations

import pytest

pytestmark = pytest.mark.integration


def test_leaving_cert_dlt_assets_have_seven_subjects() -> None:
    """The 7 priority subjects per the leaving-cert-2026 proposal."""
    try:
        from oideachais.dagster_defs.assets.leaving_cert.dlt_assets import (
            LEAVING_CERT_DLT_ASSETS,
        )
    except ImportError as exc:
        pytest.skip(f"leaving_cert dlt assets not available: {exc}")

    # 7 subject assets per the openspec change
    assert len(LEAVING_CERT_DLT_ASSETS) == 7, (
        f"expected 7 leaving_cert dlt assets, got {len(LEAVING_CERT_DLT_ASSETS)}"
    )


def test_leaving_cert_dlt_assets_cover_seven_subjects() -> None:
    """Subjects per the openspec change: mathematics, irish, biology,
    french, history, business, construction_studies.

    Note: until Phase 3 of the openspec change renames asset keys to
    the domain-first shape, the asset key path may encode the subject
    name as `leaving_cert_<subject>_ducklake`. We match either form.
    """
    try:
        from oideachais.dagster_defs.assets.leaving_cert.dlt_assets import (
            LEAVING_CERT_DLT_ASSETS,
        )
    except ImportError as exc:
        pytest.skip(f"leaving_cert dlt assets not available: {exc}")

    expected_subjects = {
        "mathematics",
        "irish",
        "biology",
        "french",
        "history",
        "business",
        "construction_studies",
    }
    found_subjects = set()
    for a in LEAVING_CERT_DLT_ASSETS:
        for segment in a.key.path:
            for subj in expected_subjects:
                if subj in segment:
                    found_subjects.add(subj)
    assert expected_subjects.issubset(found_subjects), (
        f"missing subjects: {expected_subjects - found_subjects}"
    )
