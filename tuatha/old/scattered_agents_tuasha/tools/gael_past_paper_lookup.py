"""gael_past_paper_lookup — Look up NCCA Gaeilge past paper questions.

Backed by the DuckDB table produced by the `gael_past_papers` DLT
resource (yielded by `dlt/subjects/gaeilge/sources.py`).
"""
from __future__ import annotations

from typing import Any


async def lookup_gael_paper(
    topic: str,
    level: str = "lc_hl",
    year: int | None = None,
    limit: int = 5,
) -> list[dict[str, Any]]:
    """Return NCCA Gaeilge past paper questions matching `topic`."""
    try:
        import duckdb

        con = duckdb.connect("./data/gaeilge.duckdb", read_only=True)
        where = ["subject = 'gaeilge'", f"level = '{level}'", f"text_ga ILIKE '%{topic}%'"]
        if year is not None:
            where.append(f"year = {year}")
        query = f"""
            SELECT item_id, lo_code, text_ga, text_en, marks, year, source_pdf
            FROM gael_paper_items
            WHERE {' AND '.join(where)}
            LIMIT {limit}
        """
        rows = con.execute(query).fetchall()
        return [
            {
                "item_id": r[0],
                "lo_code": r[1],
                "text_ga": r[2],
                "text_en": r[3],
                "marks": r[4],
                "year": r[5],
                "source_pdf": r[6],
            }
            for r in rows
        ]
    except Exception:
        return []