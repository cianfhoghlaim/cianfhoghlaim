"""tests.biep_parity_lc.test_english — sister to test_mathematics."""
from __future__ import annotations

import asyncio
from pathlib import Path

from cocoindex_flows.british_isles.ireland.education.lc import (
    build_subject_fixture,
    pure_python_embed,
    python_baml_fallback_extract,
)
from cocoindex_flows.british_isles.ireland.education.lc.english import (
    EnglishChunk,
    _BAML_AVAILABLE,
    COCOINDEX_AVAILABLE,
    app,
    run_english_subject,
)

from .conftest import InMemoryLanceTable, query_in_memory_table


def test_english_module_imports() -> None:
    assert EnglishChunk is not None
    assert app is not None
    assert callable(run_english_subject)


def test_english_app_name() -> None:
    assert app._name == "ireland_lc_english_embedding"


def test_english_baml_fallback() -> None:
    assert _BAML_AVAILABLE is False
    text = "Leaving Certificate English — poetry, prose, drama. Higher Level. 2024."
    extraction = python_baml_fallback_extract("english", text)
    assert extraction["subject"] == "english"
    assert len(extraction["fields"]["topic"]) >= 1
    assert "Higher" in extraction["fields"]["level"]


def test_english_fixture_and_pipeline(tmp_path: Path) -> None:
    fixture = build_subject_fixture("english", num_rows=3)
    assert len(fixture) == 3
    rows = asyncio.run(run_english_subject(tmp_path))
    assert len(rows) == 3
    table = InMemoryLanceTable(table_name="english_table")
    for row in rows:
        table.declare_row(row)
    for row in table.rows:
        assert row["subject"] == "english"
        assert len(row["embedding"]) == 1024
        assert row["extracted_topic"]
    results = query_in_memory_table(
        table, query_text="poetry and drama", embed_fn=pure_python_embed, top_k=1
    )
    assert results[0][1]["subject"] == "english"
