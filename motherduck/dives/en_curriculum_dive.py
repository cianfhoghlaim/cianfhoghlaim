"""MotherDuck Dive: en_curriculum_dive.

A read-only MotherDuck dashboard that surfaces the per-subject
curriculum coverage matrix for the England BIEP parity layer.
"""
from __future__ import annotations

from motherduck.dives import save_dive


DIVE_NAME = "en_curriculum_dive"
DIVE_DESCRIPTION = (
    "Per-subject curriculum coverage matrix for the England BIEP "
    "parity layer. Rows: subject. Columns: language. Cells: row count."
)


def build_en_curriculum_dive() -> None:
    """Persist the MotherDuck Dive for England."""
    save_dive(
        name=DIVE_NAME,
        sql="""
            SELECT subject, language, COUNT(*) AS row_count
            FROM cianfhoghlaim.education.british_isles.en
            GROUP BY subject, language
        """,
    )


__all__ = [
    "DIVE_DESCRIPTION",
    "DIVE_NAME",
    "build_en_curriculum_dive",
]
