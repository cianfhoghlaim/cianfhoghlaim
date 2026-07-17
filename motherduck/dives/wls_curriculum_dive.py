"""MotherDuck Dive: wls_curriculum_dive.

A read-only MotherDuck dashboard that surfaces the per-subject
curriculum coverage matrix for the Wales BIEP parity layer.
"""
from __future__ import annotations

from motherduck.dives import save_dive


DIVE_NAME = "wls_curriculum_dive"
DIVE_DESCRIPTION = (
    "Per-subject curriculum coverage matrix for the Wales BIEP "
    "parity layer. Rows: subject. Columns: language. Cells: row count."
)


def build_wls_curriculum_dive() -> None:
    """Persist the MotherDuck Dive for Wales."""
    save_dive(
        name=DIVE_NAME,
        sql="""
            SELECT subject, language, COUNT(*) AS row_count
            FROM cianfhoghlaim.education.british_isles.wls
            GROUP BY subject, language
        """,
    )


__all__ = [
    "DIVE_DESCRIPTION",
    "DIVE_NAME",
    "build_wls_curriculum_dive",
]
