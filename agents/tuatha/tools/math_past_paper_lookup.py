"""math_past_paper_lookup — Look up NCCA Mathematics past paper questions.

Backed by the DuckDB table produced by the `math_past_papers` DLT
resource (yielded by `dlt/subjects/mathematics/sources.py`).

Used by `math_agent` tool #2.
"""
from __future__ import annotations

from typing import Any


async def lookup_math_paper(
    topic: str,
    level: str = "hl",
    year: int | None = None,
    limit: int = 5,
) -> list[dict[str, Any]]:
    """Return past paper questions matching `topic` for the given level."""
    try:
        import duckdb

        con = duckdb.connect("./data/mathematics.duckdb", read_only=True)
        where = ["subject = 'mathematics'", f"level = '{level}'", f"text ILIKE '%{topic}%'"]
        if year is not None:
            where.append(f"year = {year}")
        query = f"""
            SELECT item_id, lo_code, text, marks, year, source_pdf
            FROM math_paper_items
            WHERE {' AND '.join(where)}
            LIMIT {limit}
        """
        rows = con.execute(query).fetchall()
        return [
            {
                "item_id": r[0],
                "lo_code": r[1],
                "text": r[2],
                "marks": r[3],
                "year": r[4],
                "source_pdf": r[5],
            }
            for r in rows
        ]
    except Exception:
        return []