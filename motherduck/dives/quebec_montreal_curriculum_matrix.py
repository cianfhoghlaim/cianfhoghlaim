"""MotherDuck Dive: quebec_montreal_curriculum_matrix.

A read-only MotherDuck dashboard that surfaces the bilingual
curriculum coverage matrix for the Quebec + Montreal education
pipeline. Rows: school_board. Columns: language. Cells: row count.
"""
from __future__ import annotations

from motherduck.dives import save_dive


DIVE_NAME = "quebec_montreal_curriculum_matrix"
DIVE_DESCRIPTION = (
    "Bilingual (FR default, EN secondary) curriculum coverage matrix "
    "for the Quebec + Montreal education pipeline."
)


def build_quebec_montreal_curriculum_matrix_dive() -> None:
    """Persist the MotherDuck Dive for Quebec + Montreal education."""
    save_dive(
        name=DIVE_NAME,
        sql="""
            SELECT school_board, language, COUNT(*) AS row_count
            FROM cianfhoghlaim.education.commonwealth.can.qc
            GROUP BY school_board, language
        """,
    )


__all__ = [
    "DIVE_DESCRIPTION",
    "DIVE_NAME",
    "build_quebec_montreal_curriculum_matrix_dive",
]
