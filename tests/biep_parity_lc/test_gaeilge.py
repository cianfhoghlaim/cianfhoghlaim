"""tests.biep_parity_lc.test_gaeilge — sister to test_mathematics.

Gaeilge has only the GA variant (no EN — the canonical BIEP v3
Gaeilge table is `cianhoghlaim.lc.gaeilge.hl_ga`).
"""
from __future__ import annotations

import asyncio
from pathlib import Path

from cocoindex_flows.british_isles.ireland.education.lc import (
    build_subject_fixture,
    pure_python_embed,
    python_baml_fallback_extract,
)
from cocoindex_flows.british_isles.ireland.education.lc.gaeilge import (
    GaeilgeChunk,
    _BAML_AVAILABLE,
    COCOINDEX_AVAILABLE,
    app,
    run_gaeilge_subject,
)

from .conftest import InMemoryLanceTable, query_in_memory_table


def test_gaeilge_module_imports() -> None:
    assert GaeilgeChunk is not None
    assert app is not None
    assert callable(run_gaeilge_subject)


def test_gaeilge_app_name() -> None:
    assert app._name == "ireland_lc_gaeilge_embedding"


def test_gaeilge_baml_fallback_picks_irish_keywords() -> None:
    """The fallback regex matches Irish-language keywords (gramadach, litríocht, …)."""
    assert _BAML_AVAILABLE is False
    text = "Ardleibhéal Gaeilge — Gramadach, Litríocht, Filíocht. Scrúdú 2024."
    extraction = python_baml_fallback_extract("gaeilge", text)
    assert extraction["subject"] == "gaeilge"
    fields = extraction["fields"]
    assert len(fields["topic"]) >= 1, f"no Irish topics extracted: {text}"
    assert any("Gramadach" in t for t in fields["topic"])
    assert "Ardleibhéal" in fields["level"]
    assert "2024" in fields["year"]


def test_gaeilge_fixture_and_pipeline(tmp_path: Path) -> None:
    fixture = build_subject_fixture("gaeilge", num_rows=3)
    assert len(fixture) == 3
    # Gaeilge fixture rows have language="ga" (Irish only)
    assert all(r["language"] == "ga" for r in fixture)
    rows = asyncio.run(run_gaeilge_subject(tmp_path))
    assert len(rows) == 3
    table = InMemoryLanceTable(table_name="gaeilge_table")
    for row in rows:
        table.declare_row(row)
    for row in table.rows:
        assert row["subject"] == "gaeilge"
        assert row["language"] == "ga"
        assert len(row["embedding"]) == 1024
        assert row["extracted_topic"]
    results = query_in_memory_table(
        table, query_text="gramadach agus litríocht", embed_fn=pure_python_embed, top_k=1
    )
    assert results[0][1]["subject"] == "gaeilge"
