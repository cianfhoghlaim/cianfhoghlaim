"""Tests for `meaisinfhoghlaim.marimo` — verifies the 2 notebook skeletons parse
and that the SQL cells reference valid table names.

The full data-binding (Phase 4 of the `celtic-data-engineering-patterns`
change) is deferred to a follow-up commit. These tests only check that the
notebooks are syntactically valid marimo files and that the SQL snippets
do not reference any obviously-wrong tables (e.g. typos in `leabharlann_books`
or `ocr_materialization_lags`).
"""

from __future__ import annotations

import pathlib
import py_compile

import pytest

MARIMO_DIR = pathlib.Path(__file__).resolve().parents[1] / "marimo"


@pytest.mark.parametrize(
    "notebook",
    ["01_leabharlann_descriptive.py", "02_dpre_lag_analysis.py"],
)
def test_marimo_notebook_parses(notebook: str) -> None:
    """Every marimo notebook must be syntactically valid Python."""
    path = MARIMO_DIR / notebook
    assert path.exists(), f"missing {path}"
    py_compile.compile(str(path), doraise=True)


def test_marimo_package_importable() -> None:
    """The `meaisinfhoghlaim.marimo` package must be importable and expose NOTEBOOKS."""
    from meaisinfhoghlaim.marimo import NOTEBOOKS

    assert NOTEBOOKS == ["01_leabharlann_descriptive", "02_dpre_lag_analysis"]


@pytest.mark.parametrize(
    "notebook,expected_tables",
    [
        (
            "01_leabharlann_descriptive.py",
            ["oideachais_dbt.weekly_downloads"],
        ),
        (
            "02_dpre_lag_analysis.py",
            [
                "oideachais.ocr_materialization_lags",
                "oideachais_dbt.ocr_confidence_by_model",
            ],
        ),
    ],
)
def test_marimo_sql_references_valid_tables(
    notebook: str, expected_tables: list[str]
) -> None:
    """Every SQL cell in the notebook must reference one of the expected tables.

    Catches typos like `leabharlann_book` (missing 's') before they propagate
    to a marimo render-time error.
    """
    text = (MARIMO_DIR / notebook).read_text(encoding="utf-8")
    for table in expected_tables:
        assert table in text, f"{notebook} should reference table {table}"


def test_descriptive_notebook_has_four_charts() -> None:
    """The descriptive notebook must declare 4 altair charts (per spaces/README.md §1.1)."""
    text = (MARIMO_DIR / "01_leabharlann_descriptive.py").read_text(encoding="utf-8")
    chart_count = text.count("alt.Chart(")
    assert chart_count == 4, f"expected 4 altair charts, found {chart_count}"


def test_lag_notebook_has_two_charts() -> None:
    """The lag notebook must declare 2 charts (line + scatter/heatmap)."""
    text = (MARIMO_DIR / "02_dpre_lag_analysis.py").read_text(encoding="utf-8")
    chart_count = text.count("alt.Chart(")
    assert chart_count == 2, f"expected 2 altair charts, found {chart_count}"
