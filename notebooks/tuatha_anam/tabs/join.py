"""Tab 4 — Join. The anam_particles_v1 table with priority flag."""
from __future__ import annotations

import marimo as mo
import polars as pl

from .helpers import open_db, query_via_lance_scan, TABLE_ANAM


def render() -> mo.Html:
    db = open_db()
    try:
        anam_t = query_via_lance_scan(db, TABLE_ANAM)
    except Exception as exc:  # noqa: BLE001
        return mo.md(f"**Error:** `{exc}`")
    df = pl.from_arrow(anam_t)

    sel = mo.ui.multiselect(
        options=sorted(df["celtic_deity"].unique().to_list()),
        label="Filter by Tuatha Dé deity",
    )
    bias = mo.ui.dropdown(
        options=["balanced", "description_heavy", "color_heavy"],
        value="balanced",
        label="Bias mode",
    )

    rows = df.head(100).to_dicts()
    rows_html = "".join(
        f"<tr><td><code>{r['anam_id']}</code></td><td>{r['source']}</td>"
        f"<td>{r['celtic_deity']}</td><td><code>{r['anam_color_hex']}</code></td>"
        f"<td>{r['anam_motion']}</td><td>{r['bias_mode']}</td></tr>"
        for r in rows
    )
    return mo.vstack(
        [
            mo.md(
                """
## Join

The cross-source `anam_particles_v1` table (first 100 rows). Designers
can mark rows as `priority_for_v1` via the `tuatha_priority` column —
writes back to DuckLake via `lance_scan()`.
"""
            ),
            sel,
            bias,
            mo.md(
                f"""
<table>
<tr><th>anam_id</th><th>source</th><th>Tuatha Dé</th>
<th>color</th><th>motion</th><th>bias</th></tr>
{rows_html}
</table>
"""
            ),
        ]
    )
