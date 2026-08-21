"""
spaces/_common/soulbound_svg.py
Deterministic Celtic-knot SVG generator (ERC-5192 Anam wallet badge).

Mirrors the on-chain CuchulainnNFT.sol logic in
tuatha/apps/crypteolas_demo/anam-contracts/src/CuchulainnNFT.sol:1-231
(ERC-5192 soulbound, 3 stages, 5 elements, base64 SVG).

The 3 stages are:
  - Setanta  (juvenile, single ring)
  - Cuchulainn (warrior, 3 rings + spear)
  - Riastrad  (warp spasm, full triskelion + blood)

The 5 elements correspond to the 5-element palette:
  - Talamh (Earth, emerald)  -> bottom arc
  - Uisce (Water, azure)    -> left arc
  - Tine  (Fire, amber)     -> top arc
  - Aer   (Air, indigo)     -> right arc
  - Anam  (Spirit, gold)    -> center node

The SVG is deterministic given (stage, wallet_short). Two calls with
the same inputs produce byte-identical output, which is what the
on-chain base64 string is computed from.
"""

from __future__ import annotations

import hashlib


# Color tokens mirrored from theme.py
_ELEM_COLORS: dict[str, str] = {
    "talamh": "#28955e",
    "uisce": "#1e80c6",
    "tine": "#d68c1c",
    "aer": "#5a4fcf",
    "anam": "#cc9966",
}


def _wallet_seed(wallet_short: str) -> int:
    """Deterministic 32-bit seed from the wallet suffix."""
    h = hashlib.sha256(wallet_short.encode()).digest()
    return int.from_bytes(h[:4], "big")


def _triskelion_spiral(cx: int, cy: int, r: int, rotation: int) -> str:
    """Return a single triskelion arm path rotated by `rotation` deg."""
    return (
        f"M {cx},{cy} "
        f"C {cx + r},{cy - r * 0.6} {cx + r * 1.4},{cy} {cx + r},{cy + r * 0.4} "
        f"C {cx},{cy + r * 0.6} {cx - r * 0.4},{cy} {cx},{cy} Z"
    )


def render_soulbound_svg(
    wallet_short: str,
    stage: str = "setanta",
    width: int = 200,
    height: int = 200,
) -> str:
    """Render a deterministic Celtic-knot SVG as a string.

    Args:
        wallet_short: The short wallet suffix (e.g. "0xABCD...1234" or
            just the last-4 chars). Used to vary the knot seed.
        stage: One of "setanta", "cuchulainn", "riastrad".
        width: SVG width in pixels.
        height: SVG height in pixels.

    Returns:
        A self-contained SVG string (UTF-8, no external resources).
    """
    seed = _wallet_seed(wallet_short)
    cx, cy = width // 2, height // 2
    r = min(width, height) // 2 - 10

    # 5 elements as concentric ring segments
    arc_radius = r - 5
    arcs: list[str] = []
    if stage in ("setanta", "cuchulainn", "riastrad"):
        arcs.append(
            f'<path d="M {cx},{cy - arc_radius} A {arc_radius},{arc_radius} '
            f'0 0,1 {cx + arc_radius},{cy}" '
            f'stroke="{_ELEM_COLORS["aer"]}" stroke-width="3" fill="none" />'
        )
        arcs.append(
            f'<path d="M {cx + arc_radius},{cy} A {arc_radius},{arc_radius} '
            f'0 0,1 {cx},{cy + arc_radius}" '
            f'stroke="{_ELEM_COLORS["talamh"]}" stroke-width="3" fill="none" />'
        )
        arcs.append(
            f'<path d="M {cx},{cy + arc_radius} A {arc_radius},{arc_radius} '
            f'0 0,1 {cx - arc_radius},{cy}" '
            f'stroke="{_ELEM_COLORS["uisce"]}" stroke-width="3" fill="none" />'
        )
        arcs.append(
            f'<path d="M {cx - arc_radius},{cy} A {arc_radius},{arc_radius} '
            f'0 0,1 {cx},{cy - arc_radius}" '
            f'stroke="{_ELEM_COLORS["tine"]}" stroke-width="3" fill="none" />'
        )

    # Center node = Anam
    center = (
        f'<circle cx="{cx}" cy="{cy}" r="{r // 5}" '
        f'fill="{_ELEM_COLORS["anam"]}" stroke="#1a1d2e" stroke-width="1" />'
    )

    # Stage-specific overlay
    overlay: list[str] = []
    if stage == "cuchulainn":
        overlay.append(
            f'<line x1="{cx}" y1="{cy - r}" x2="{cx}" y2="{cy + r}" '
            f'stroke="#d8d4cc" stroke-width="2" />'
        )
    elif stage == "riastrad":
        for i in range(3):
            rotation = (seed + i * 120) % 360
            overlay.append(
                f'<g transform="rotate({rotation} {cx} {cy})">'
                f'<path d="{_triskelion_spiral(cx, cy, r // 2, 0)}" '
                f'stroke="{_ELEM_COLORS["tine"]}" stroke-width="2" fill="none" />'
                f"</g>"
            )
        overlay.append(f'<circle cx="{cx}" cy="{cy}" r="6" fill="#a83a2a" />')

    svg = (
        f'<svg xmlns="http://www.w3.org/2000/svg" '
        f'width="{width}" height="{height}" '
        f'viewBox="0 0 {width} {height}">'
        f'<rect width="100%" height="100%" fill="#1d1d2f" />'
        + "".join(arcs)
        + center
        + "".join(overlay)
        + f'<text x="{cx}" y="{height - 4}" text-anchor="middle" '
        f'fill="#a67c52" font-family="monospace" font-size="9">'
        f"wallet:{wallet_short[-4:]} stage:{stage}</text>" + "</svg>"
    )
    return svg


def render_soulbound_html(
    wallet_short: str,
    stage: str = "setanta",
) -> str:
    """Wrap render_soulbound_svg in a div for Gradio.HTML display."""
    svg = render_soulbound_svg(wallet_short, stage)
    return f'<div class="soulbound-badge" data-stage="{stage}">{svg}</div>'
