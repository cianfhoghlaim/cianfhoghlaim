"""MotherDuck Dive: nigeria_state_curriculum_matrix.

A read-only MotherDuck dashboard that surfaces the cross-state
curriculum coverage matrix for the Nigerian pipeline. Rows: state.
Columns: language. Cells: row count.
"""
from __future__ import annotations

from motherduck.dives import save_dive


DIVE_NAME = "nigeria_state_curriculum_matrix"
DIVE_DESCRIPTION = (
    "Cross-state curriculum coverage matrix for the Nigerian pipeline "
    "(37 sub-units × 5 languages)."
)


def build_nigeria_state_curriculum_matrix_dive() -> None:
    """Persist the MotherDuck Dive for the Nigerian pipeline."""
    save_dive(
        name=DIVE_NAME,
        sql="""
            SELECT state_code, language, COUNT(*) AS row_count
            FROM oideachais.education.commonwealth.nga
            GROUP BY state_code, language
        """,
    )


__all__ = [
    "DIVE_DESCRIPTION",
    "DIVE_NAME",
    "build_nigeria_state_curriculum_matrix_dive",
]
