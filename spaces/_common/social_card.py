"""
spaces/_common/social_card.py
HF social card auto-renderer (1200x630 PNG, 5-element palette).

Each Space gets a 1200x630 PNG social card showing:
  - Space name (EN + GA, bilingual)
  - 5-element badge (the same Celtic-knot ring from soulbound_svg.py)
  - Tagline (one-line, BAML-generated or hand-crafted)
  - Footer with model alias + 32B assertion
  - Build small 2026 hackathon badge

The card is what Twitter / LinkedIn / blog previews show when the Space
is linked. It must be visible in the Space README and as a static
`social_card.png` next to `app.py` in each Space repo.
"""

from __future__ import annotations

import io
from typing import Final

import gradio as gr

try:
    from PIL import Image, ImageDraw, ImageFont  # type: ignore[import-not-found]
    _HAS_PIL: bool = True
except ImportError:  # pragma: no cover
    _HAS_PIL = False


_CARD_W: Final[int] = 1200
_CARD_H: Final[int] = 630
_BG: Final[str] = "#1d1d2f"
_INK: Final[str] = "#1a1d2e"
_BONE: Final[str] = "#d8d4cc"
_GOLD: Final[str] = "#cc9966"
_BRONZE: Final[str] = "#a67c52"
_EMERALD: Final[str] = "#28955e"
_AZURE: Final[str] = "#1e80c6"
_AMBER: Final[str] = "#d68c1c"
_INDIGO: Final[str] = "#5a4fcf"
_CRIMSON: Final[str] = "#a83a2a"


def _arc_path(
    cx: int, cy: int, r: int, start_deg: float, end_deg: float
) -> list[tuple[float, float]]:
    """Return a list of (x, y) points along a circular arc."""
    import math
    pts: list[tuple[float, float]] = []
    for i in range(int(start_deg), int(end_deg) + 1, 2):
        rad = math.radians(i)
        pts.append((cx + r * math.cos(rad), cy + r * math.sin(rad)))
    return pts


def _draw_knot(draw: ImageDraw.ImageDraw, cx: int, cy: int, r: int) -> None:
    """Draw a 5-element Celtic-knot ring at the given center."""
    arc_specs = [
        (_AZURE, 0, 90),
        (_EMERALD, 90, 180),
        (_AMBER, 180, 270),
        (_INDIGO, 270, 360),
    ]
    for color, s, e in arc_specs:
        pts = _arc_path(cx, cy, r, s, e)
        if len(pts) > 1:
            draw.line(pts, fill=color, width=6)
    draw.ellipse(
        (cx - r // 5, cy - r // 5, cx + r // 5, cy + r // 5),
        fill=_GOLD, outline=_INK, width=2,
    )


def _load_font(size: int) -> ImageFont.ImageFont:
    """Try to load a serif font. Fall back to PIL's default bitmap."""
    font_paths = [
        "/System/Library/Fonts/Supplemental/Georgia.ttf",
        "/System/Library/Fonts/Supplemental/Times New Roman.ttf",
        "/usr/share/fonts/truetype/dejavu/DejaVuSerif.ttf",
        "/Library/Fonts/Georgia.ttf",
    ]
    for path in font_paths:
        try:
            return ImageFont.truetype(path, size)
        except (OSError, FileNotFoundError):
            continue
    return ImageFont.load_default()


def render_social_card(
    space_name_en: str,
    space_name_ga: str,
    tagline: str,
    model_alias: str,
    output_path: str = "social_card.png",
) -> str:
    """Render a 1200x630 social card PNG.

    Args:
        space_name_en: English name (e.g. "An Scrudu").
        space_name_ga: Irish name (e.g. "Cianfhoghlaim").
        tagline: One-line tagline.
        model_alias: Model alias string (e.g. "Qwen2.5-7B-Instruct").
        output_path: Where to write the PNG.

    Returns:
        The output_path on success, or empty string if PIL is unavailable.
    """
    if not _HAS_PIL:
        return ""

    img = Image.new("RGB", (_CARD_W, _CARD_H), _BG)
    draw = ImageDraw.Draw(img)

    # Inset border (Celtic bronze)
    draw.rectangle(
        (10, 10, _CARD_W - 10, _CARD_H - 10),
        outline=_BRONZE, width=3,
    )
    draw.rectangle(
        (16, 16, _CARD_W - 16, _CARD_H - 16),
        outline=_GOLD, width=1,
    )

    # Hackathon badge (top-left)
    badge_font = _load_font(20)
    draw.text(
        (40, 30), "BUILD SMALL 2026", fill=_GOLD, font=badge_font,
    )
    draw.text(
        (40, 56), "cianfhoghlaim / 4 Spaces", fill=_BONE, font=badge_font,
    )

    # Bilingual title (center-left)
    title_font = _load_font(72)
    draw.text(
        (40, 200), space_name_en, fill=_BONE, font=title_font,
    )
    ga_font = _load_font(48)
    draw.text(
        (40, 290), space_name_ga, fill=_GOLD, font=ga_font,
    )

    # Tagline
    tag_font = _load_font(28)
    draw.text(
        (40, 380), tagline[:90], fill=_BONE, font=tag_font,
    )

    # Knot badge (right side)
    _draw_knot(draw, cx=980, cy=300, r=160)

    # Footer (model + 32B)
    foot_font = _load_font(22)
    draw.text(
        (40, 560),
        f"Model: {model_alias} (<=32B)  *  Bun + uv + Turbo  "
        f"*  1 typed pipeline  *  Anam Bonneagar",
        fill=_BRONZE, font=foot_font,
    )
    draw.text(
        (40, 590),
        "6-file linter: 97.2%  *  Pobal HP: Dublin 8 (-9.8)",
        fill=_BRONZE, font=foot_font,
    )

    img.save(output_path, "PNG", optimize=True)
    return output_path


def render_social_card_html(
    space_name_en: str,
    space_name_ga: str,
    tagline: str,
    model_alias: str,
) -> str:
    """Return a Gradio-friendly HTML preview of the social card (no PNG render).

    Used when PIL is not installed in the Space container (e.g. lightweight
    L4 CPU Space). The actual social_card.png is still committed to the
    Space repo at build time.
    """
    return f"""
    <div class="social-card-preview" style="
        background: {_BG};
        color: {_BONE};
        border: 3px solid {_BRONZE};
        border-radius: 4px;
        padding: 2em;
        font-family: 'Cinzel', serif;
    ">
        <div style="color: {_GOLD}; font-size: 0.9em;">
            BUILD SMALL 2026 &middot; cianfhoghlaim / 4 Spaces
        </div>
        <h1 style="color: {_BONE}; font-size: 2.8em; margin: 0.3em 0 0;">
            {space_name_en}
        </h1>
        <h2 style="color: {_GOLD}; font-size: 1.8em; margin: 0;">
            {space_name_ga}
        </h2>
        <p style="color: {_BONE}; margin-top: 1.5em;">{tagline}</p>
        <div style="color: {_BRONZE}; font-size: 0.8em; margin-top: 1.5em;
                    font-family: monospace;">
            Model: {model_alias} (<=32B) &middot; 1 typed pipeline &middot;
            Anam Bonneagar
        </div>
    </div>
    """
