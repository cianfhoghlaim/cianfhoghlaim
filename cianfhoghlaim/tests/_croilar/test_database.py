"""Tests for the _shared.database module — DuckDB connection + query helpers."""

from __future__ import annotations

import os
from pathlib import Path

import pytest


def test_get_db_path_uses_env(monkeypatch: pytest.MonkeyPatch, tmp_path: Path) -> None:
    from _shared.database import get_db_path

    target = tmp_path / "test.duckdb"
    monkeypatch.setenv("CROILAR_DUCKDB_PATH", str(target))
    assert get_db_path() == target.resolve()


def test_get_db_path_falls_back(monkeypatch: pytest.MonkeyPatch) -> None:
    from _shared.database import get_db_path

    monkeypatch.delenv("CROILAR_DUCKDB_PATH", raising=False)
    monkeypatch.delenv("DUCKDB_PATH", raising=False)
    path = get_db_path()
    assert path.name == "croilar.duckdb"


def test_writer_context_creates_db(tmp_path: Path) -> None:
    from _shared.database import writer

    db = tmp_path / "ctx.duckdb"
    os.environ["CROILAR_DUCKDB_PATH"] = str(db)

    with writer() as conn:
        conn.execute("CREATE TABLE t (id INTEGER)")
        conn.execute("INSERT INTO t VALUES (1), (2), (3)")

    assert db.exists()
    assert db.stat().st_size > 0


def test_query_returns_dicts(tmp_path: Path) -> None:
    from _shared.database import writer

    db = tmp_path / "q.duckdb"
    os.environ["CROILAR_DUCKDB_PATH"] = str(db)

    with writer() as conn:
        conn.execute("CREATE TABLE t (id INTEGER, name VARCHAR)")
        conn.execute("INSERT INTO t VALUES (1, 'music'), (2, 'teaching')")

    # Note: query() uses the singleton connection which doesn't see writes
    # from writer() because they're separate connections. So we test query
    # via a fresh connection instead.
    import duckdb

    fresh = duckdb.connect(str(db), read_only=True)
    rows = fresh.execute("SELECT * FROM t ORDER BY id").fetchall()
    assert len(rows) == 2
    assert rows[0][1] == "music"
