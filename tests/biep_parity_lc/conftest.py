"""tests.biep_parity_lc.conftest — shared pytest fixtures for the
BIEP v3 per-subject pytest suite.

Provides:
- `lc_subject_specs` — the canonical 6 LCSubjectSpec rows
- `baml_status` — the BAML availability probe (parametrized)
- `in_memory_table` — a drop-in "LanceDB table" substitute (a
  Python list) that the per-subject pipeline writes to.
"""
from __future__ import annotations

import asyncio
from pathlib import Path
from typing import Any

import pytest

from cocoindex_flows.british_isles.ireland.education.lc import (
    LC_SUBJECTS,
    SUBJECT_SLUGS,
    baml_available,
    build_subject_fixture,
    pure_python_embed,
)


# ----------------------------------------------------------------------------
# Subject specs
# ----------------------------------------------------------------------------

@pytest.fixture(scope="session")
def lc_subject_specs():
    """The canonical 6 LCSubjectSpec rows."""
    return LC_SUBJECTS


@pytest.fixture(scope="session")
def lc_subject_slugs():
    """The canonical 6 subject slugs."""
    return SUBJECT_SLUGS


# ----------------------------------------------------------------------------
# BAML availability probe
# ----------------------------------------------------------------------------

@pytest.fixture(scope="session")
def baml_status() -> bool:
    """True iff `baml_client.baml_client` imports successfully."""
    return baml_available()


# ----------------------------------------------------------------------------
# In-memory "LanceDB table" substitute
# ----------------------------------------------------------------------------

class InMemoryLanceTable:
    """A drop-in `lancedb.TableTarget` substitute for pytests.

    Implements the same surface the per-subject CocoIndex
    `process_*_file` function uses:
    - `declare_vector_index(column=...)` (no-op)
    - `declare_row(row=...)` (appends the row to an in-memory list)
    - `to_list()` (returns the list of rows)

    Not actually persistent; not searchable via ANN — but the
    per-subject pytests only need the load → embed → store leg to
    work, which this satisfies. The query leg is tested via a
    brute-force cosine similarity over the in-memory list.
    """

    def __init__(self, table_name: str):
        self.table_name = table_name
        self.rows: list[Any] = []
        self._indexed_columns: list[str] = []

    def declare_vector_index(self, column: str) -> None:
        self._indexed_columns.append(column)

    def declare_row(self, row: Any) -> None:
        self.rows.append(row)

    def to_list(self) -> list[Any]:
        return list(self.rows)


@pytest.fixture
def in_memory_table() -> InMemoryLanceTable:
    """An empty in-memory LanceDB substitute."""
    return InMemoryLanceTable(table_name="pytest_table")


# ----------------------------------------------------------------------------
# Brute-force cosine similarity (for the query leg)
# ----------------------------------------------------------------------------

def cosine_similarity(a: list[float], b: list[float]) -> float:
    """Pure-Python cosine similarity (no numpy required).

    Used by the query leg of the per-subject pytests to verify
    that semantically-similar fixtures produce higher scores
    than dissimilar ones (since `pure_python_embed` is not
    semantically meaningful, we use the chunk text length + a
    shared-keyword check as the proxy).
    """
    if len(a) != len(b):
        return 0.0
    dot = sum(x * y for x, y in zip(a, b))
    norm_a = sum(x * x for x in a) ** 0.5
    norm_b = sum(y * y for y in b) ** 0.5
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return dot / (norm_a * norm_b)


def query_in_memory_table(
    table: InMemoryLanceTable,
    query_text: str,
    embed_fn,
    top_k: int = 3,
) -> list[tuple[float, Any]]:
    """Brute-force top-k cosine-similarity search over the table."""
    query_vec = embed_fn(query_text)

    def _embed(row: Any) -> list[float]:
        if hasattr(row, "embedding"):
            return row.embedding  # type: ignore[attr-defined]
        return row["embedding"]  # dict-style access

    scored = [(cosine_similarity(query_vec, _embed(row)), row) for row in table.rows]
    scored.sort(key=lambda x: x[0], reverse=True)
    return scored[:top_k]


# ----------------------------------------------------------------------------
# Convenience: build the per-subject fixture (3 rows) + embed each
# ----------------------------------------------------------------------------

def _build_embedded_rows(
    subject_slug: str,
    embed_fn,
    num_rows: int = 3,
) -> list[dict[str, Any]]:
    """Build the 3-row fixture + embed each row (sync, for pytest)."""
    fixture = build_subject_fixture(subject_slug, num_rows=num_rows)
    out = []
    for row in fixture:
        out.append({
            **row,
            "embedding": embed_fn(row["text"]),
        })
    return out
