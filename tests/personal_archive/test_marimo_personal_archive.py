"""Tests for the Marimo notebook `notebooks/15_personal_archive.py`.

Per the 2026-08-23-uog-personal-archive-tertiary-modules-v1 change
(WS12 — Tests + observability + thesis figures).

The notebook implements the canonical 8-tab BIEP pattern (Health /
Filters / Materials / URL Health / Heatmap / Recent / Lance Search /
SQL Console) plus a CS4423 worked-example sidebar. This test pins
down the parseability contract.
"""
from __future__ import annotations

import os
from pathlib import Path

import ast


_CIANFHOGHLAIM_ROOT = Path(os.environ.get("CIANFHOGHLAIM_ROOT", os.path.expanduser("~/dev/cianfhoghlaim")))
_NOTEBOOK = _CIANFHOGHLAIM_ROOT / "notebooks/15_personal_archive.py"


def test_personal_archive_notebook_parses_as_valid_python() -> None:
    """`notebooks/15_personal_archive.py` must parse as valid Python."""
    assert _NOTEBOOK.exists(), f"Notebook not found at {_NOTEBOOK}"
    text = _NOTEBOOK.read_text(encoding="utf-8")
    ast.parse(text)


def test_personal_archive_notebook_uses_marimo_app() -> None:
    """The notebook must use `marimo.App(width=...)` and an
    `if __name__ == \"__main__\"` entrypoint."""
    text = _NOTEBOOK.read_text(encoding="utf-8")
    assert "marimo.App" in text
    assert 'if __name__ == "__main__":' in text
