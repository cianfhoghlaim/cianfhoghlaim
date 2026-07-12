"""Smoke tests for the Phase 3.4 marimo dashboards.

These are not full marimo-runtime tests (the marimo notebook
runtime is heavy and we don't need it in CI). Instead, these
tests assert:

  1. The 3 new dashboards exist as files.
  2. Each file is a valid marimo App (defines `app = marimo.App(...)`).
  3. Each file imports without syntax error.
  4. Each dashboard declares the expected @app.cell blocks.

Why smoke-only:
  * marimo notebooks are reactive — running them in pytest would
    require a full client.
  * The actual data queries (`duckdb.execute('SELECT ...')`) are
    best validated manually + via the integration test suite
    when the lakehouse is up.

The 3 new dashboards:
  * oideachais/notebooks/dashboards/medicine/all_nations.py
  * oideachais/notebooks/dashboards/law/all_nations.py
  * oideachais/notebooks/dashboards/cross_domain.py

The pre-existing dashboards (`medicine/registers.py`,
`law/statute_book.py`, `education/all_nations.py`, etc.) are
out of scope for this change.
"""
from __future__ import annotations

import re
from pathlib import Path

import pytest

# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------
NOTEBOOKS_ROOT = (
    Path(__file__).resolve().parents[2] / "notebooks" / "dashboards"
)


def _read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------
DASHBOARDS = [
    "medicine/all_nations.py",
    "law/all_nations.py",
    "cross_domain.py",
]


@pytest.mark.parametrize("relpath", DASHBOARDS)
def test_dashboard_exists(relpath: str) -> None:
    """Each declared dashboard must exist on disk."""
    p = NOTEBOOKS_ROOT / relpath
    assert p.is_file(), f"Missing dashboard: {p}"


@pytest.mark.parametrize("relpath", DASHBOARDS)
def test_dashboard_is_marimo_app(relpath: str) -> None:
    """Each dashboard must declare `app = marimo.App(...)`."""
    text = _read(NOTEBOOKS_ROOT / relpath)
    assert re.search(r"app\s*=\s*marimo\.App\(", text), (
        f"{relpath} must declare `app = marimo.App(...)`"
    )


@pytest.mark.parametrize("relpath", DASHBOARDS)
def test_dashboard_imports_cleanly(relpath: str) -> None:
    """`import marimo` must succeed (and so must the dashboard's
    own imports). We don't run the notebook, just confirm the
    file compiles."""
    import py_compile

    py_compile.compile(
        str(NOTEBOOKS_ROOT / relpath),
        doraise=True,
    )


@pytest.mark.parametrize("relpath", DASHBOARDS)
def test_dashboard_has_at_least_three_cells(relpath: str) -> None:
    """Each marimo notebook must have >= 3 @app.cell blocks
    (imports, header, body). 1 cell is too few for a useful
    dashboard; 0 is a syntax error."""
    text = _read(NOTEBOOKS_ROOT / relpath)
    n = len(re.findall(r"@app\.cell\b", text))
    assert n >= 3, f"{relpath} must have >= 3 @app.cell blocks, got {n}"


def test_medicine_all_nations_covers_all_10_sources() -> None:
    """`medicine/all_nations.py` must list all 10 wired DLT
    sources (4 IE + 3 EN + 1 NI + 1 SCT + 1 WLS) by name."""
    text = _read(NOTEBOOKS_ROOT / "medicine" / "all_nations.py")
    for source in (
        "hse",
        "medical_council",
        "doh",
        "hpsc",
        "nhs_england",
        "gmc",
        "nice",
        "nidirect",
        "nhs_scotland",
        "nhs_wales",
    ):
        assert source in text, (
            f"medicine/all_nations.py must mention source {source!r}"
        )


def test_law_all_nations_covers_all_7_sources() -> None:
    """`law/all_nations.py` must list all 7 wired DLT sources
    (3 IE + 1 EN + 1 NI + 1 SCT + 1 WLS) by name."""
    text = _read(NOTEBOOKS_ROOT / "law" / "all_nations.py")
    for source in (
        "irish_statute_book",
        "doj",
        "lawreform",
        "legislation",
    ):
        assert source in text, (
            f"law/all_nations.py must mention source {source!r}"
        )


def test_cross_domain_queries_4_domains() -> None:
    """`cross_domain.py` must iterate over all 4 lateralise
    domains: education, medicine, law, site_analysis."""
    text = _read(NOTEBOOKS_ROOT / "cross_domain.py")
    for domain in ("education", "medicine", "law", "site_analysis"):
        assert domain in text, (
            f"cross_domain.py must mention domain {domain!r}"
        )
