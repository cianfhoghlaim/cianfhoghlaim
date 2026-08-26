"""Tab 3 — Particles. Color palette histogram + LAB scatter plot."""
from __future__ import annotations

import marimo as mo
import altair as alt
import polars as pl

from .helpers import (
    open_db,
    query_via_lance_scan,
    rgb_to_lab,
    hex_to_rgb,
    TABLE_HADES,
    TABLE_COMIC,
    TABLE_GBA,
    TABLE_ANAM,
)


def render() -> mo.Html:
    db = open_db()
    frames = {}
    for label, tbl in [
        ("hades", TABLE_HADES),
        ("comic", TABLE_COMIC),
        ("gba", TABLE_GBA),
        ("anam", TABLE_ANAM),
    ]:
        try:
            frames[label] = pl.from_arrow(query_via_lance_scan(db, tbl))
        except Exception as exc:  # noqa: BLE001
            return mo.md(f"**Error:** `{exc}`")

    def _lab_points(df, color_col):
        if color_col not in df.columns:
            return []
        return [
            {
                "source": s,
                "L": rgb_to_lab(hex_to_rgb(c))[0],
                "A": rgb_to_lab(hex_to_rgb(c))[1],
                "B": rgb_to_lab(hex_to_rgb(c))[2],
                "color": c,
            }
            for s, tbl in frames.items()
            for c in tbl[color_col].to_list()
            if isinstance(c, str) and c.startswith("#")
        ]

    pts = (
        _lab_points(frames["hades"], "color_hex")
        + _lab_points(frames["comic"], "color_hex")
        + _lab_points(frames["gba"], "color_hex")
        + _lab_points(frames["anam"], "anam_color_hex")
    )
    df = pl.DataFrame(pts)
    if df.is_empty():
        return mo.md("No rows yet — run the pipeline to populate the Lance tables.")

    chart = (
        alt.Chart(df)
        .mark_circle(size=60)
        .encode(
            x=alt.X("A:Q", title="a* (LAB)"),
            y=alt.Y("B:Q", title="b* (LAB)"),
            color=alt.Color("source:N"),
            tooltip=["source", "L", "A", "B", "color"],
        )
        .properties(width=600, height=400, title="Color palette in LAB space")
    )

    return mo.vstack(
        [
            mo.md(
                f"""
## Particles

Color points across all 4 Lance tables in CIE-Lab space. The ANAM
turquoise/blue palette should cluster toward the cyan/green L-axis side
of the diagram.
"""
            ),
            mo.ui.altair_chart(chart),
        ]
    )
