"""tests.biep_parity_lc.test_computer_science — sister to test_mathematics."""
from __future__ import annotations

import asyncio
from pathlib import Path

from cocoindex_flows.british_isles.ireland.education.lc import (
    build_subject_fixture,
    pure_python_embed,
    python_baml_fallback_extract,
)
from cocoindex_flows.british_isles.ireland.education.lc.computer_science import (
    ComputerScienceChunk,
    _BAML_AVAILABLE,
    COCOINDEX_AVAILABLE,
    app,
    run_computer_science_subject,
)

from .conftest import InMemoryLanceTable, query_in_memory_table


def test_computer_science_module_imports() -> None:
    assert ComputerScienceChunk is not None
    assert app is not None
    assert callable(run_computer_science_subject)


def test_computer_science_app_name() -> None:
    assert app._name == "ireland_lc_computer_science_embedding"


def test_computer_science_baml_fallback() -> None:
    assert _BAML_AVAILABLE is False
    text = "Leaving Certificate Computer Science — algorithms, data structures, programming. Higher Level. 2024."
    extraction = python_baml_fallback_extract("computer_science", text)
    assert extraction["subject"] == "computer_science"
    assert len(extraction["fields"]["topic"]) >= 1
    assert "Higher" in extraction["fields"]["level"]


def test_computer_science_fixture_and_pipeline(tmp_path: Path) -> None:
    fixture = build_subject_fixture("computer_science", num_rows=3)
    assert len(fixture) == 3
    rows = asyncio.run(run_computer_science_subject(tmp_path))
    assert len(rows) == 3
    table = InMemoryLanceTable(table_name="computer_science_table")
    for row in rows:
        table.declare_row(row)
    for row in table.rows:
        assert row["subject"] == "computer_science"
        assert len(row["embedding"]) == 1024
        assert row["extracted_topic"]
    results = query_in_memory_table(
        table, query_text="algorithms and data structures", embed_fn=pure_python_embed, top_k=1
    )
    assert results[0][1]["subject"] == "computer_science"
