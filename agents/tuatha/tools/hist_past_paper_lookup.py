"""hist_past_paper_lookup — Look up NCCA History past paper questions."""
from __future__ import annotations

from typing import Any


async def lookup_hist_paper(
    topic: str,
    level: str = "lc_hl",
    year: int | None = None,
    limit: int = 5,
) -> list[dict[str, Any]]:
    try:
        import duckdb

        con = duckdb.connect("./data/history.duckdb", read_only=True)
        where = ["subject = 'history'", f"level = '{level}'", f"text ILIKE '%{topic}%'"]
        if year is not None:
            where.append(f"year = {year}")
        query = f"""
            SELECT item_id, lo_code, text, marks, year, source_pdf
            FROM hist_paper_items
            WHERE {' AND '.join(where)}
            LIMIT {limit}
        """
        rows = con.execute(query).fetchall()
        return [
            {"item_id": r[0], "lo_code": r[1], "text": r[2], "marks": r[3], "year": r[4], "source_pdf": r[5]}
            for r in rows
        ]
    except Exception:
        return []