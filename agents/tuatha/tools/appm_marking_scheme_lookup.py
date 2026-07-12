"""appm_marking_scheme_lookup — Look up the NCCA APPM marking scheme."""
from __future__ import annotations

from typing import Any


async def lookup_appm_marking_scheme(lo_code: str) -> dict[str, Any]:
    try:
        import duckdb

        con = duckdb.connect("./data/applied_mathematics.duckdb", read_only=True)
        row = con.execute(
            """
            SELECT lo_code, marks_per_step, text_en, text_ga, source_pdf
            FROM appm_marking_schemes
            WHERE lo_code = ?
            LIMIT 1
            """,
            [lo_code],
        ).fetchone()
        if row is None:
            return {"lo_code": lo_code, "error": "no marking scheme found"}
        return {
            "lo_code": row[0],
            "marks_per_step": row[1],
            "text_en": row[2],
            "text_ga": row[3],
            "source_pdf": row[4],
        }
    except Exception:
        return {"lo_code": lo_code, "error": "marking scheme lookup failed"}