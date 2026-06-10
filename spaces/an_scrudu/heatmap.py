"""
spaces/an_scrudu/heatmap.py
Topic-distribution heatmap renderer for Space 1 (An Scrudu).

Renders a 2D heatmap (topic x year) as inline HTML/CSS. The renderer
is self-contained (no matplotlib / plotly dep), so it works in any
Gradio Space container.

Color scale: emerald (Talamh) at low values, gold (Anam) at high.
"""

from __future__ import annotations

from spaces.an_scrudu.extraction import CircularExtraction


# Color stops for the heatmap (Talamh -> Anam gradient)
_HEAT_STOPS: list[tuple[float, str]] = [
    (0.0, "#1a3a2a"),   # darkest green
    (0.25, "#1e6644"),
    (0.5, "#28955e"),   # Talamh
    (0.75, "#a8924d"),
    (1.0, "#cc9966"),   # Anam
]


def _color_for(value: float, max_value: float) -> str:
    """Return a hex color from the Talamh->Anam gradient."""
    if max_value <= 0:
        return _HEAT_STOPS[0][1]
    ratio = max(0.0, min(1.0, value / max_value))
    for i in range(len(_HEAT_STOPS) - 1):
        r1, c1 = _HEAT_STOPS[i]
        r2, c2 = _HEAT_STOPS[i + 1]
        if r1 <= ratio <= r2:
            return _interpolate_color(c1, c2, (ratio - r1) / (r2 - r1))
    return _HEAT_STOPS[-1][1]


def _interpolate_color(c1: str, c2: str, t: float) -> str:
    """Linear-interpolate between two hex colors."""
    r1, g1, b1 = int(c1[1:3], 16), int(c1[3:5], 16), int(c1[5:7], 16)
    r2, g2, b2 = int(c2[1:3], 16), int(c2[3:5], 16), int(c2[5:7], 16)
    r = int(r1 + (r2 - r1) * t)
    g = int(g1 + (g2 - g1) * t)
    b = int(b1 + (b2 - b1) * t)
    return f"#{r:02x}{g:02x}{b:02x}"


def render_heatmap(extraction: CircularExtraction) -> str:
    """Render the topic distribution as an HTML heatmap.

    Args:
        extraction: The CircularExtraction to visualize.

    Returns:
        A self-contained HTML string for gr.HTML(value=...).
    """
    if not extraction.topics:
        return (
            '<div class="an-scrudu-heatmap" '
            'style="padding:1em; color:#bcb8b0;">'
            '<em>No topics found in extraction.</em></div>'
        )

    max_points = max(t.marking_points for t in extraction.topics)

    rows: list[str] = []
    rows.append(
        '<tr style="border-bottom:1px solid #a67c52;">'
        '<th style="text-align:left; padding:0.4em; color:#cc9966;">Topic</th>'
        '<th style="text-align:left; padding:0.4em; color:#cc9966;">Label</th>'
        '<th style="text-align:right; padding:0.4em; color:#cc9966;">Marks</th>'
        '<th style="text-align:right; padding:0.4em; color:#cc9966;">Section</th>'
        '<th style="text-align:left; padding:0.4em; color:#cc9966;">Heat</th>'
        '</tr>'
    )
    for topic in extraction.topics:
        heat_color = _color_for(topic.marking_points, max_points)
        rows.append(
            f'<tr style="border-bottom:1px solid #2a3a3a;">'
            f'<td style="padding:0.4em; color:#28955e; '
            f'font-family:monospace;">{topic.topic_code}</td>'
            f'<td style="padding:0.4em; color:#d8d4cc;">{topic.topic_label}</td>'
            f'<td style="padding:0.4em; color:#d8d4cc; text-align:right;">'
            f'{topic.marking_points}</td>'
            f'<td style="padding:0.4em; color:#bcb8b0; text-align:right;">'
            f'{topic.paper_section}</td>'
            f'<td style="padding:0.4em; min-width:200px;">'
            f'<div style="background:{heat_color}; height:18px; '
            f'width:{int(topic.marking_points / max_points * 100)}%; '
            f'border-radius:2px;"></div>'
            f'</td>'
            f'</tr>'
        )

    caption = (
        f'<div style="margin-top:1em; font-size:0.85em; color:#bcb8b0;">'
        f'<strong>Total:</strong> {extraction.total_marking_points} marks &middot; '
        f'<strong>Duration:</strong> {extraction.estimated_paper_duration_min} min &middot; '
        f'<strong>Source model:</strong> {extraction.source_model} &middot; '
        f'<strong>Confidence:</strong> {extraction.extraction_confidence:.2f}'
        f'</div>'
    )

    return (
        '<div class="an-scrudu-heatmap" '
        'style="background:#1a1d2e; padding:1.5em; border-radius:4px; '
        'border:2px solid #28955e;">'
        f'<h3 style="color:#28955e; margin:0 0 0.5em 0; '
        f'font-family:Cinzel,serif;">{extraction.subject} - {extraction.issued_year}</h3>'
        f'<p style="color:#d8d4cc; margin:0 0 1em 0; font-style:italic;">'
        f'"{extraction.title_en}"</p>'
        '<table style="width:100%; border-collapse:collapse; '
        'font-family:Inter,sans-serif;">'
        + "".join(rows)
        + "</table>"
        + caption
        + "</div>"
    )


def render_pclm_html(extraction: CircularExtraction) -> str:
    """Render a PCLM-PDF-style preview of the extracted scheme.

    This is a *preview* of the PCLM markup the Space would emit for
    download. The full PCLM emitter (with the actual PDF write) is
    in pclm.py; this HTML preview lets the user verify the extraction
    before committing to a download.
    """
    rows: list[str] = []
    for i, topic in enumerate(extraction.topics, 1):
        rows.append(
            f"<tr><td>{i}</td><td>{topic.topic_code}</td>"
            f"<td>{topic.topic_label}</td>"
            f"<td>{topic.marking_points}</td></tr>"
        )

    return (
        '<div class="pclm-preview" style="background:#f5f0e6; '
        'color:#1a1d2e; padding:1.5em; border:1px solid #bcb8b0; '
        'font-family:Georgia,serif;">'
        f"<h2>{extraction.subject} - {extraction.issued_year}</h2>"
        f"<h3>{extraction.title_en}</h3>"
        f"<p><em>{extraction.raw_text_excerpt}</em></p>"
        "<table style='width:100%; border-collapse:collapse;'>"
        "<tr><th>#</th><th>Code</th><th>Topic</th><th>Marks</th></tr>"
        + "".join(rows)
        + "</table>"
        "</div>"
    )
