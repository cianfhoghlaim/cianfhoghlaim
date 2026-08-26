"""Shared helpers for the Tuatha ANAM Dashboard notebook tabs."""

from __future__ import annotations

import lancedb
import pyarrow as pa

LANCE_URI = "s3://garage/lance"  # resolved via Infisical in prod

TABLE_HADES = "cianfhoghlaim.tuatha.hades.boons"
TABLE_COMIC = "cianfhoghlaim.tuatha.comic.particles"
TABLE_GBA = "cianfhoghlaim.tuatha.gba.magic"
TABLE_ANAM = "cianfhoghlaim.tuatha.anam_particles"


def open_db() -> "lancedb.DBConnection":
    """Open the Lance connection (s3:// in prod; file:// in dev)."""
    return lancedb.connect(LANCE_URI)


def query_via_lance_scan(db, table: str) -> pa.Table:
    """Federate a Lance table through DuckDB lance_scan().

    Per the lancedb skill "Ibis + DuckDB lance_scan()" — the canonical
    federated SQL pattern.
    """
    import duckdb

    con = duckdb.connect()
    con.execute("INSTALL lance; LOAD lance;")
    safe = table.replace(".", "_")
    con.execute(
        f"CREATE OR REPLACE VIEW {safe} AS "
        f"SELECT * FROM lance_scan('s3://garage/lance/{table}')"
    )
    return con.execute(f"SELECT * FROM {safe}").arrow_table()


def hex_to_rgb(hex_color: str) -> tuple[int, int, int]:
    h = hex_color.lstrip("#")
    return int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)


def rgb_to_lab(rgb: tuple[int, int, int]) -> tuple[float, float, float]:
    """sRGB → CIE-Lab (D65). Used by the color scatter plot."""
    r, g, b = (c / 255.0 for c in rgb)
    # sRGB → linear
    def lin(c: float) -> float:
        return c / 12.92 if c <= 0.04045 else ((c + 0.055) / 1.055) ** 2.4

    rl, gl, bl = lin(r), lin(g), lin(b)

    # linear RGB → XYZ (D65)
    x = (rl * 0.4124564 + gl * 0.3575761 + bl * 0.1804375) / 0.95047
    y = rl * 0.2126729 + gl * 0.7151522 + bl * 0.0721750
    z = (rl * 0.0193339 + gl * 0.1191920 + bl * 0.9503041) / 1.08883

    def f(t: float) -> float:
        return t ** (1.0 / 3.0) if t > 0.008856 else (7.787 * t) + (16.0 / 116.0)

    L = 116.0 * f(y) - 16.0
    A = 500.0 * (f(x) - f(y))
    B = 200.0 * (f(y) - f(z))
    return L, A, B


def delta_e(c1: str, c2: str) -> float:
    """CIE76 ΔE between two #RRGGBB colors."""
    L1, a1, b1 = rgb_to_lab(hex_to_rgb(c1))
    L2, a2, b2 = rgb_to_lab(hex_to_rgb(c2))
    return ((L1 - L2) ** 2 + (a1 - a2) ** 2 + (b1 - b2) ** 2) ** 0.5
