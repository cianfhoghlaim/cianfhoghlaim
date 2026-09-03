"""CocoIndex that consumes the voted DuckLake output (BIEP v3 P2).

Per the 2026-08-08-biep-v3-production-readiness-v1 change.

The existing `cocoindex_flows/subjects/lc_subject_embedding.py` re-parses local
raw PDFs. This new app reads typed/voted output from DuckLake and exports
to consistent LanceDB tables matching the canonical
`cianfhoghlaim.education.<jurisdiction>.<stage>[.<board>].<subject>`
namespace.
"""
from __future__ import annotations

import logging
from pathlib import Path

logger = logging.getLogger(__name__)


def consume_voted_ducklake_to_lance(
    jurisdiction: str = "ireland",
    stage: str = "leaving_certificate",
    subject_slug: str = "mathematics",
    lance_table_name: str | None = None,
) -> dict[str, int]:
    """Read the voted-canonical rows from DuckLake and emit to LanceDB.

    Returns a stats dict {rows_read, rows_written, lance_table}.
    """
    import duckdb  # type: ignore[import-not-found]
    import lance  # type: ignore[import-not-found]

    canonical_table = (
        f"cianfhoghlaim.education.{jurisdiction}.{stage}.{subject_slug}"
    )
    lance_table = lance_table_name or canonical_table.replace(".", "_")

    rows_read = 0
    rows_written = 0

    try:
        con = duckdb.connect("md:cianfhoghlaim", read_only=True)
        rs = con.sql(f"SELECT * FROM {canonical_table}.voted_canonical").execute()
        rows = rs.fetchall()
        rows_read = len(rows)

        # Write to LanceDB
        db = lance.connect("http://localhost:8081")
        tbl = db.create_table(
            lance_table,
            [{"text": r[0]} for r in rows] if rows else [{"text": ""}],
            mode="overwrite",
        )
        rows_written = len(rows)

        logger.info(
            "consume_voted_ducklake_to_lance: read %d rows from %s → wrote to %s",
            rows_read, canonical_table, lance_table,
        )
        return {"rows_read": rows_read, "rows_written": rows_written, "lance_table": lance_table}

    except Exception as e:
        logger.warning(
            "consume_voted_ducklake_to_lance: %s — falling back to stub mode",
            e,
        )
        return {"rows_read": 0, "rows_written": 0, "lance_table": lance_table, "error": str(e)}


__all__ = ["consume_voted_ducklake_to_lance"]
