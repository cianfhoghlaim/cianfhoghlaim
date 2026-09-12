"""tests.biep_parity_lc.test_chemistry — sister to test_mathematics.
Same template, parameterised for Chemistry.
"""
from __future__ import annotations

import asyncio
from pathlib import Path

import pytest

from cocoindex_flows.british_isles.ireland.education.lc import (
    build_subject_fixture,
    pure_python_embed,
    python_baml_fallback_extract,
)
from cocoindex_flows.british_isles.ireland.education.lc.chemistry import (
    ChemistryChunk,
    _BAML_AVAILABLE,
    COCOINDEX_AVAILABLE,
    app,
    run_chemistry_subject,
)

from .conftest import InMemoryLanceTable, query_in_memory_table


def test_chemistry_module_imports() -> None:
    assert ChemistryChunk is not None
    assert app is not None
    assert callable(run_chemistry_subject)
    assert COCOINDEX_AVAILABLE is True


def test_chemistry_app_name() -> None:
    assert app._name == "ireland_lc_chemistry_embedding"


def test_chemistry_baml_fallback() -> None:
    assert _BAML_AVAILABLE is False
    text = "Leaving Certificate Chemistry — atomic structure and periodic table. Higher Level. 2024."
    extraction = python_baml_fallback_extract("chemistry", text)
    assert extraction["subject"] == "chemistry"
    assert len(extraction["fields"]["topic"]) >= 1
    assert "Higher" in extraction["fields"]["level"]


def test_chemistry_fixture_and_pipeline(tmp_path: Path) -> None:
    fixture = build_subject_fixture("chemistry", num_rows=3)
    assert len(fixture) == 3
    rows = asyncio.run(run_chemistry_subject(tmp_path))
    assert len(rows) == 3
    table = InMemoryLanceTable(table_name="chemistry_table")
    for row in rows:
        table.declare_row(row)
    for row in table.rows:
        assert row["subject"] == "chemistry"
        assert len(row["embedding"]) == 1024
        assert row["extracted_topic"]
        assert row["extracted_level"]
    results = query_in_memory_table(
        table, query_text="periodic table and bonding", embed_fn=pure_python_embed, top_k=1
    )
    assert len(results) == 1
    assert results[0][1]["subject"] == "chemistry"
