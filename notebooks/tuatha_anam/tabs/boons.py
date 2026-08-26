"""Tab 2 — Boons. Searchable table of Hades boons → ANAM mapping."""
from __future__ import annotations

import marimo as mo
import polars as pl

from .helpers import open_db, query_via_lance_scan, TABLE_HADES, TABLE_ANAM


def render() -> mo.Html:
    db = open_db()
    try:
        boons_t = query_via_lance_scan(db, TABLE_HADES)
        anam_t = query_via_lance_scan(db, TABLE_ANAM)
    except Exception as exc:  # noqa: BLE001
        return mo.md(f"**Error loading tables:** `{exc}`")

    boons = pl.from_arrow(boons_t)
    anam = pl.from_arrow(anam_t).filter(pl.col("source") == "hades.boons")

    joined = boons.join(
        anam.select(["source_id", "celtic_deity", "anam_color_hex", "anam_motion"]),
        left_on="boon_id",
        right_on="source_id",
        how="left",
    )

    rows_html = "".join(
        f"<tr><td>{r['god']}</td><td>{r['tier']}</td>"
        f"<td>{r['slot']}</td><td>{r['effect_text']}</td>"
        f"<td><code>{r['color_hex']}</code></td>"
        f"<td>{r.get('celtic_deity', '—')}</td>"
        f"<td><code>{r.get('anam_color_hex', '—')}</code></td></tr>"
        for r in joined.head(50).to_dicts()
    )
    return mo.md(
        f"""
## Boons

Showing the first 50 boons from the `hades_boons` Lance table joined to
the `anam_particles_v1` table (where source = `hades.boons`).

<table>
<tr><th>God</th><th>Tier</th><th>Slot</th><th>Effect</th>
<th>Source color</th><th>Tuatha counterpart</th><th>ANAM color</th></tr>
{rows_html}
</table>
        """
    )
