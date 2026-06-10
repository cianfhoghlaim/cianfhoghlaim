"""
spaces/meaisin_cliste/scoil_map.py
Theme 2 of Space 2: Scoil ar an Léarscáil (School on the Map).

A small SVG school-density visualisation using the Pobal HP
Deprivation Index 2022 (a curated subset; the full index lives in
oideachais/data_platform/dlt_sources/geospatial/cso_small_areas.py:342-371).

The visualisation is a stylised Ireland map with ~20 county markers.
Each marker is coloured by Pobal HP score (red = most deprived, gold =
most affluent). Hovering reveals the school count.

No matplotlib / plotly - pure SVG for the Gradio container.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class SchoolMarker:
    county: str           # County name (Irish + EN)
    name_en: str
    name_ga: str
    svg_x: float          # 0-1000 SVG viewbox coord
    svg_y: float
    hp_score: float       # Pobal HP Deprivation Index 2022
    school_count: int     # Approx. number of primary + post-primary
    deis_pct: float       # % of schools that are DEIS (Delivering Equality
                          # of Opportunity in Schools)


# 20 counties - hand-curated subset of the 26 ROI counties + 6 NI counties
# for visual coverage of the whole island.
SCHOOL_MARKERS: list[SchoolMarker] = [
    SchoolMarker("Dublin", "Dublin", "Baile Átha Cliath", 530, 290, -9.8, 312, 24.0),
    SchoolMarker("Cork", "Cork", "Corcaigh", 240, 540, -2.1, 198, 19.5),
    SchoolMarker("Galway", "Galway", "Gaillimh", 175, 320, -3.2, 89, 17.8),
    SchoolMarker("Limerick", "Limerick", "Luimneach", 245, 430, -4.5, 67, 22.1),
    SchoolMarker("Waterford", "Waterford", "Port Láirge", 330, 540, -5.2, 45, 20.3),
    SchoolMarker("Kilkenny", "Kilkenny", "Cill Chainnigh", 340, 470, -1.8, 32, 12.4),
    SchoolMarker("Wexford", "Wexford", "Loch Garman", 400, 540, -4.1, 51, 18.9),
    SchoolMarker("Wicklow", "Wicklow", "Cill Mhantáin", 470, 380, -2.5, 38, 10.2),
    SchoolMarker("Carlow", "Carlow", "Ceatharlach", 360, 450, -3.0, 18, 15.6),
    SchoolMarker("Kildare", "Kildare", "Cill Dara", 430, 380, 0.5, 56, 8.9),
    SchoolMarker("Meath", "Meath", "An Mhí", 470, 280, 1.2, 48, 7.2),
    SchoolMarker("Louth", "Louth", "Lú", 530, 250, -1.4, 31, 13.1),
    SchoolMarker("Donegal", "Donegal", "Dún na nGall", 250, 100, -6.8, 67, 24.5),
    SchoolMarker("Mayo", "Mayo", "Maigh Eo", 120, 220, -4.9, 56, 19.8),
    SchoolMarker("Sligo", "Sligo", "Sligeach", 200, 180, -3.4, 22, 16.4),
    SchoolMarker("Kerry", "Kerry", "Ciarraí", 110, 480, -3.7, 61, 21.2),
    SchoolMarker("Clare", "Clare", "An Clár", 180, 360, -2.2, 44, 14.7),
    SchoolMarker("Tipperary", "Tipperary", "Tiobraid Árann", 290, 440, -3.8, 59, 17.3),
    SchoolMarker("Offaly", "Offaly", "Uíbh Fhailí", 330, 350, -2.6, 27, 14.1),
    SchoolMarker("Westmeath", "Westmeath", "An Iarmhí", 370, 290, -2.0, 31, 12.8),
    # Northern Ireland (6 counties)
    SchoolMarker("Antrim", "Antrim", "Aontroim", 580, 200, -1.5, 78, 13.0),
    SchoolMarker("Down", "Down", "An Dún", 590, 270, 0.3, 65, 9.8),
    SchoolMarker("Armagh", "Armagh", "Ard Mhacha", 540, 220, -4.2, 39, 16.7),
    SchoolMarker("Tyrone", "Tyrone", "Tír Eoghain", 470, 150, -5.7, 45, 19.4),
    SchoolMarker("Fermanagh", "Fermanagh", "Fear Manach", 420, 180, -5.1, 18, 17.6),
    SchoolMarker("Londonderry", "Londonderry", "Doire", 480, 110, -7.2, 32, 22.0),
]


def _hp_color(score: float) -> str:
    """Color the marker by HP deprivation score.

    Pobal HP: negative = more deprived, positive = more affluent.
    -9.8 (Dublin 8) -> crimson (most deprived)
    +1.2 (Meath)  -> emerald (most affluent)
    """
    if score <= -7.0:
        return "#a83a2a"  # Pobal crimson
    if score <= -4.0:
        return "#d68c1c"  # Tine amber
    if score <= -1.0:
        return "#cc9966"  # Anam gold
    if score <= 1.0:
        return "#5a4fcf"  # Aer indigo
    return "#28955e"      # Talamh emerald (affluent)


def _hp_size(score: float) -> int:
    """Marker radius based on HP score (more deprived = larger)."""
    # Map [-10, +2] -> [12, 4]
    score_clamped = max(-10.0, min(2.0, score))
    return int(12 - (score_clamped + 10) * (8 / 12))


def render_school_map() -> str:
    """Render the school-density map as a self-contained SVG string."""
    parts: list[str] = [
        '<svg xmlns="http://www.w3.org/2000/svg" '
        'viewBox="0 0 700 650" width="100%" height="auto" '
        'style="background:#1d1d2f; border:2px solid #1e80c6; border-radius:4px;">',
        # Title
        '<text x="350" y="40" text-anchor="middle" fill="#1e80c6" '
        'font-family="Cinzel,serif" font-size="22" font-style="italic">'
        'Scoil ar an Léarscáil - Uisce</text>',
        '<text x="350" y="60" text-anchor="middle" fill="#d8d4cc" '
        'font-family="Cormorant Garamond,serif" font-size="13">'
        '26 counties, Pobal HP 2022</text>',
    ]

    # Sea grid
    for gx in range(50, 700, 50):
        parts.append(
            f'<line x1="{gx}" y1="80" x2="{gx}" y2="600" '
            f'stroke="#a67c52" stroke-width="0.3" stroke-opacity="0.1" />'
        )

    # Land outline (very stylised Ireland)
    parts.append(
        '<path d="M 200,80 Q 300,60 500,80 L 580,160 '
        'L 620,280 L 600,400 L 540,520 L 440,580 L 320,600 '
        'L 220,560 L 130,460 L 100,360 L 120,240 L 200,80 Z" '
        'fill="#2a3a3a" fill-opacity="0.4" stroke="#1e80c6" stroke-width="1.5" />'
    )

    # Markers
    for m in SCHOOL_MARKERS:
        color = _hp_color(m.hp_score)
        r = _hp_size(m.hp_score)
        parts.append(
            f'<circle cx="{m.svg_x}" cy="{m.svg_y}" r="{r}" '
            f'fill="{color}" stroke="#1a1d2e" stroke-width="1" opacity="0.85">'
            f'<title>{m.name_en} - HP {m.hp_score:+.1f}, '
            f'{m.school_count} schools, {m.deis_pct:.0f}% DEIS</title>'
            f'</circle>'
        )
        parts.append(
            f'<text x="{m.svg_x + r + 2}" y="{m.svg_y + 4}" '
            f'fill="#d8d4cc" font-family="Inter,sans-serif" font-size="9">'
            f'{m.name_en}</text>'
        )

    # Legend
    parts.append(
        '<g transform="translate(20, 580)">'
        '<text x="0" y="0" fill="#1e80c6" font-family="Inter,sans-serif" '
        'font-size="11" font-weight="bold">Pobal HP 2022:</text>'
        '<circle cx="120" cy="-4" r="6" fill="#a83a2a" />'
        '<text x="130" y="0" fill="#d8d4cc" font-size="10">most deprived</text>'
        '<circle cx="230" cy="-4" r="5" fill="#d68c1c" />'
        '<text x="240" y="0" fill="#d8d4cc" font-size="10">deprived</text>'
        '<circle cx="295" cy="-4" r="4" fill="#cc9966" />'
        '<text x="305" y="0" fill="#d8d4cc" font-size="10">average</text>'
        '<circle cx="365" cy="-4" r="4" fill="#5a4fcf" />'
        '<text x="375" y="0" fill="#d8d4cc" font-size="10">affluent</text>'
        '<circle cx="430" cy="-4" r="4" fill="#28955e" />'
        '<text x="440" y="0" fill="#d8d4cc" font-size="10">most affluent</text>'
        '</g>'
    )

    parts.append("</svg>")
    return "".join(parts)


def get_summary() -> dict[str, float | int]:
    """Return summary stats for the school-density sidebar."""
    total_schools = sum(m.school_count for m in SCHOOL_MARKERS)
    avg_hp = sum(m.hp_score for m in SCHOOL_MARKERS) / len(SCHOOL_MARKERS)
    avg_deis = sum(m.deis_pct for m in SCHOOL_MARKERS) / len(SCHOOL_MARKERS)
    most_deprived = min(SCHOOL_MARKERS, key=lambda m: m.hp_score)
    most_affluent = max(SCHOOL_MARKERS, key=lambda m: m.hp_score)
    return {
        "total_schools": total_schools,
        "avg_hp": avg_hp,
        "avg_deis_pct": avg_deis,
        "most_deprived_county": most_deprived.name_en,
        "most_deprived_score": most_deprived.hp_score,
        "most_affluent_county": most_affluent.name_en,
        "most_affluent_score": most_affluent.hp_score,
        "counties_shown": len(SCHOOL_MARKERS),
    }
