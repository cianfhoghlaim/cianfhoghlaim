"""Test `oideachais.dagster_defs.asset_checks.check_duchas_pages`.

The check returns `passed=True` if the count of pages is positive and
exposes transcription-rate metadata. We seed a tiny in-memory DuckDB
with the `celtic.duchas_pages` table.
"""
from __future__ import annotations

from pathlib import Path

import pytest

pytestmark = pytest.mark.integration


def test_check_duchas_pages_returns_passed_for_nonempty_table(temp_dir: Path) -> None:
    """A non-empty `celtic.duchas_pages` table makes the check pass."""
    import duckdb
    from cianfhoghlaim.dagster.asset_checks import check_duchas_pages

    db_path = temp_dir / "duchas.duckdb"
    conn = duckdb.connect(str(db_path))
    conn.execute("CREATE SCHEMA IF NOT EXISTS celtic;")
    conn.execute("""
        CREATE TABLE celtic.duchas_pages (
            url VARCHAR,
            county VARCHAR,
            transcription VARCHAR
        );
    """)
    conn.execute(
        "INSERT INTO celtic.duchas_pages VALUES "
        "('https://duchas.ie/1', 'Galway', 'transcribed'),"
        "('https://duchas.ie/2', 'Cork', NULL);"
    )
    conn.close()

    from cianfhoghlaim.dagster.resources import DuckDBResource

    resource = DuckDBResource(database_path=str(db_path))
    result = check_duchas_pages(context=None, duckdb=resource)  # type: ignore[arg-type]
    assert result.passed is True
    metadata = result.metadata
    # metadata is a dict[str, MetadataValue]
    assert "total_pages" in metadata
    assert "transcription_rate" in metadata
