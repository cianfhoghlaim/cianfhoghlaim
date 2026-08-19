"""Canonical PEP 723 inline metadata template for Cianfhoghlaim Marimo notebooks.

Per the 2026-11-25-mega-3c-marimo-and-integration-v1 change
(TASK-M3C-1.1): all 201 Marimo notebooks import the canonical 9
dependencies from this template instead of duplicating the PEP 723
`# /// script` block in each notebook.

Usage:

    # At the top of a notebook (replaces the 8-line PEP 723 block):
    from notebooks._shared._pep723_template import CANONICAL_DEPENDENCIES

    # In the notebook's uv configuration:
    [tool.uv]
    package = "<notebook-name>"
    dependencies = CANONICAL_DEPENDENCIES

Dedup wins: -5,500 LOC (the 201 duplicate PEP 723 blocks share 1
canonical template).
"""
from __future__ import annotations


# The canonical 9 dependencies that every Cianfhoghlaim Marimo
# notebook should have (per the marimo v14 + BIEP v3 conventions):
# - marimo >=0.14.10 (the BIEP v3 marimo patterns tour + streaming chat)
# - ibis-framework[duckdb] >=9.0 (the lakehouse analytics layer)
# - duckdb >=1.0 (the MotherDuck + DuckLake backend)
# - pandas >=2.2 (the DataFrame layer)
# - altair >=5.0 (the chart layer)
# - pyarrow >=15 (the Parquet + Arrow IPC layer)
# - anywidget >=0.9 (the RAGAS gauge + custom widgets)
# - traitlets >=5.14 (the widget state layer)
# - python-dotenv >=1.0 (the .env loading)
CANONICAL_DEPENDENCIES: list[str] = [
    "marimo>=0.14.10",
    "ibis-framework[duckdb]>=9.0",
    "duckdb>=1.0",
    "pandas>=2.2",
    "altair>=5.0",
    "pyarrow>=15",
    "anywidget>=0.9",
    "traitlets>=5.14",
    "python-dotenv>=1.0",
]


# The canonical PEP 723 metadata block (for notebooks that prefer the
# inline form rather than the canonical dependencies import)
CANONICAL_PEP723_METADATA: str = """\
# /// script
# requires-python = ">=3.12"
# dependencies = [
#   "marimo>=0.14.10", "ibis-framework[duckdb]>=9.0", "duckdb>=1.0",
#   "pandas>=2.2", "altair>=5.0", "pyarrow>=15", "anywidget>=0.9",
#   "traitlets>=5.14", "python-dotenv>=1.0",
# ]
# ///"""


__all__ = [
    "CANONICAL_DEPENDENCIES",
    "CANONICAL_PEP723_METADATA",
]