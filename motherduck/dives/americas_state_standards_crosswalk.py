"""MotherDuck Dive: americas_state_standards_crosswalk.

A read-only MotherDuck dashboard that surfaces the cross-state
standards cross-reference for the Americas pilot jurisdictions (US-CA
+ Brazil + Mexico + Venezuela).
"""
from __future__ import annotations

from motherduck.dives import save_dive


DIVE_NAME = "americas_state_standards_crosswalk"
DIVE_DESCRIPTION = (
    "Cross-jurisdiction standards cross-reference for the Americas "
    "pilot jurisdictions (California / Brazil / Mexico / Venezuela). "
    "Rows: jurisdiction + subject. Columns: language. Cells: row count."
)


def build_americas_state_standards_crosswalk_dive() -> None:
    """Persist the MotherDuck Dive for the Americas pipeline."""
    save_dive(
        name=DIVE_NAME,
        sql="""
            SELECT jurisdiction, language, COUNT(*) AS row_count
            FROM cianfhoghlaim.education.americas.California
            GROUP BY jurisdiction, language

            UNION ALL
            SELECT jurisdiction, language, COUNT(*) AS row_count
            FROM cianfhoghlaim.education.americas.Brazil
            GROUP BY jurisdiction, language

            UNION ALL
            SELECT jurisdiction, language, COUNT(*) AS row_count
            FROM cianfhoghlaim.education.americas.Mexico
            GROUP BY jurisdiction, language

            UNION ALL
            SELECT jurisdiction, language, COUNT(*) AS row_count
            FROM cianfhoghlaim.education.americas.Venezuela
            GROUP BY jurisdiction, language
        """,
    )


__all__ = [
    "DIVE_DESCRIPTION",
    "DIVE_NAME",
    "build_americas_state_standards_crosswalk_dive",
]
