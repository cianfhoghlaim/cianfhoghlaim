"""Tab 1 — Sources. Per-source capture health + raw asset counts."""
from __future__ import annotations

import marimo as mo

from .helpers import open_db, query_via_lance_scan, TABLE_HADES, TABLE_COMIC, TABLE_GBA


def render() -> mo.Html:
    db = open_db()
    counts = {}
    for label, tbl in [
        ("Hades boons", TABLE_HADES),
        ("Comic particles", TABLE_COMIC),
        ("GBA magic", TABLE_GBA),
    ]:
        try:
            t = query_via_lance_scan(db, tbl)
            counts[label] = len(t)
        except Exception as exc:  # noqa: BLE001
            counts[label] = f"err: {exc}"

    rows = "\n".join(
        f"| {lbl} | {val} |" for lbl, val in counts.items()
    )
    return mo.md(
        f"""
## Sources

| Source | Row count |
|:--|--:|
{rows}

(shippable=false invariant: thumbnails are intentionally not rendered
in this tab. Use tab **Join** + the `description_en` FTS for design
review.)
        """
    )
