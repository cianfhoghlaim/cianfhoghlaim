"""
spaces/meaisin_cliste/app.py
Space 2: Meaisin Cliste - Celtic AI Tools (3 themes).

3 themes side-by-side as Gradio Tabs:
  1. Focloir na Se Naisiun (Aer)       - 6-nation cognate dictionary
  2. Scoil ar an Learscail (Uisce)     - School-density + Pobal HP map
  3. Curaclam Trasteorann (Aer)        - Cross-nation curriculum compare

Element: Uisce (Water) for theme 2, Aer (Air) for themes 1+3.
The Space title (Meaisin Cliste = "Smart Machine") covers all 3.

Gradio components:
  - Top: header + 5-element badge
  - Tabs: one per theme
  - Bottom: Anam Bonneagar footer
"""

from __future__ import annotations

import logging

import gradio as gr

from spaces._common import (
    apply_celtic_theme,
    GRADIO_CSS,
    render_anam_bonneagar_footer,
    translate,
    set_lang,
)
from spaces.meaisin_cliste.cognates import (
    COGNATES,
    search as cognate_search,
)
from spaces.meaisin_cliste.scoil_map import (
    render_school_map,
    get_summary as scoil_summary,
)
from spaces.meaisin_cliste.curaclam import (
    compare_curricula,
    render_comparison_html,
)


_log = logging.getLogger("meaisin_cliste.app")
set_lang("en")


# ---------------------------------------------------------------------
# Theme 1: Foclóir na Sé Náisiún
# ---------------------------------------------------------------------

def _render_cognate_table(query: str, lang: str) -> str:
    """Return an HTML table of cognate matches."""
    if not query.strip():
        results = COGNATES[:10]
    else:
        results = cognate_search(query, lang)
    if not results:
        return (
            f'<div style="padding:1em; color:#bcb8b0; font-style:italic;">'
            f'No cognates matching "{query}" in language "{lang}".</div>'
        )
    rows: list[str] = []
    for c in results:
        rows.append(
            f'<tr style="border-bottom:1px solid #2a3a3a;">'
            f'<td style="padding:0.4em; color:#5a4fcf; font-family:monospace;">'
            f'{c.proto_celtic}</td>'
            f'<td style="padding:0.4em; color:#d8d4cc;">{c.en}</td>'
            f'<td style="padding:0.4em; color:#28955e; font-style:italic;">'
            f'{c.ie}</td>'
            f'<td style="padding:0.4em; color:#1e80c6; font-style:italic;">'
            f'{c.gd}</td>'
            f'<td style="padding:0.4em; color:#cc9966; font-style:italic;">'
            f'{c.cy}</td>'
            f'<td style="padding:0.4em; color:#d68c1c; font-style:italic;">'
            f'{c.gv}</td>'
            f'<td style="padding:0.4em; color:#a83a2a; font-style:italic;">'
            f'{c.kw}</td>'
            f'<td style="padding:0.4em; color:#bcb8b0;">{c.br}</td>'
            f'</tr>'
        )
    return (
        f'<div class="focloir-table" style="background:#1a1d2e; '
        f'padding:1em; border:2px solid #5a4fcf; border-radius:4px;">'
        f'<table style="width:100%; border-collapse:collapse; '
        f'font-family:Inter,sans-serif; font-size:0.85em;">'
        f'<tr style="border-bottom:1px solid #5a4fcf;">'
        f'<th style="text-align:left; padding:0.4em; color:#5a4fcf;">Proto-Celtic</th>'
        f'<th style="text-align:left; padding:0.4em; color:#5a4fcf;">EN</th>'
        f'<th style="text-align:left; padding:0.4em; color:#5a4fcf;">Gaeilge</th>'
        f'<th style="text-align:left; padding:0.4em; color:#5a4fcf;">Gaidhlig</th>'
        f'<th style="text-align:left; padding:0.4em; color:#5a4fcf;">Cymraeg</th>'
        f'<th style="text-align:left; padding:0.4em; color:#5a4fcf;">Gaelg</th>'
        f'<th style="text-align:left; padding:0.4em; color:#5a4fcf;">Kernewek</th>'
        f'<th style="text-align:left; padding:0.4em; color:#5a4fcf;">Brezhoneg</th>'
        f'</tr>'
        + "".join(rows)
        + "</table>"
        f'<div style="margin-top:0.5em; font-size:0.8em; color:#bcb8b0;">'
        f'{len(results)} cognate(s) shown. Seed data; production uses the full '
        f'DLT pipeline at oideachais/language/cognates.py.</div>'
        f"</div>"
    )


# ---------------------------------------------------------------------
# Theme 2: Scoil ar an Léarscáil
# ---------------------------------------------------------------------

def _render_scoil_panel() -> str:
    """Return the scoil panel (map + summary stats)."""
    svg = render_school_map()
    summary = scoil_summary()
    stats_html = (
        f'<div style="background:#1a1d2e; padding:1em; border:2px solid #1e80c6; '
        f'border-radius:4px; margin-top:1em;">'
        f'<h4 style="color:#1e80c6; margin:0 0 0.5em 0; '
        f'font-family:Cinzel,serif;">Summary</h4>'
        f'<ul style="color:#d8d4cc; font-family:Inter,sans-serif; '
        f'list-style:none; padding:0;">'
        f'<li>Counties shown: <strong>{summary["counties_shown"]}</strong></li>'
        f'<li>Total schools: <strong>{summary["total_schools"]:,}</strong></li>'
        f'<li>Avg Pobal HP: <strong>{summary["avg_hp"]:+.2f}</strong></li>'
        f'<li>Avg DEIS %: <strong>{summary["avg_deis_pct"]:.1f}%</strong></li>'
        f'<li>Most deprived: <strong>{summary["most_deprived_county"]}</strong> '
        f'(HP {summary["most_deprived_score"]:+.1f})</li>'
        f'<li>Most affluent: <strong>{summary["most_affluent_county"]}</strong> '
        f'(HP {summary["most_affluent_score"]:+.1f})</li>'
        f'</ul></div>'
    )
    return svg + stats_html


# ---------------------------------------------------------------------
# Theme 3: Curaclam Trasteorann
# ---------------------------------------------------------------------

def _on_compare_curricula(topic_query: str) -> str:
    """Run the comparison and return the rendered HTML."""
    if not topic_query.strip():
        topic_query = "atomic structure"
    cmp = compare_curricula(topic_query)
    return render_comparison_html(cmp)


# ---------------------------------------------------------------------
# Gradio app
# ---------------------------------------------------------------------

def build_app() -> gr.Blocks:
    with gr.Blocks(theme=apply_celtic_theme(), css=GRADIO_CSS, title="Meaisin Cliste") as demo:
        gr.Markdown(
            f"""# {translate("space2.title")}
### *{translate("app.subtitle")}*

3 themes for Celtic AI: a 6-nation cognate dictionary, a school-density
map, and a cross-nation curriculum comparison. Elements: **Aer** (Air,
themes 1+3) and **Uisce** (Water, theme 2).""",
            elem_classes="elem-aer",
        )

        with gr.Tabs():
            # Theme 1: Foclóir na Sé Náisiún (Aer)
            with gr.Tab(translate("space2.focloir_tab"), elem_classes="elem-aer"):
                gr.Markdown(
                    "**6-nation Celtic cognate dictionary.** "
                    "Type a word in any language or in proto-Celtic. "
                    "Returns matches across all 6 Celtic nations."
                )
                with gr.Row():
                    cognate_input = gr.Textbox(
                        label="Search (proto-Celtic or any language)",
                        placeholder="e.g. 'sea', '*windo-', 'fionn'",
                    )
                    cognate_lang = gr.Dropdown(
                        choices=[
                            ("Proto-Celtic", "proto_celtic"),
                            ("Gaeilge", "ie"),
                            ("Gàidhlig", "gd"),
                            ("Cymraeg", "cy"),
                            ("Gaelg", "gv"),
                            ("Kernewek", "kw"),
                        ],
                        value="proto_celtic",
                        label="Search in language",
                    )
                cognate_output = gr.HTML(
                    value=_render_cognate_table("", "proto_celtic"),
                    label="Cognate results",
                )
                cognate_input.change(
                    fn=_render_cognate_table,
                    inputs=[cognate_input, cognate_lang],
                    outputs=[cognate_output],
                )

            # Theme 2: Scoil ar an Léarscáil (Uisce)
            with gr.Tab(translate("space2.scoil_tab"), elem_classes="elem-uisce"):
                gr.Markdown(
                    "**School-density map of Ireland (26 counties).** "
                    "Marker size and colour are by the Pobal HP "
                    "Deprivation Index 2022. Hover for school counts."
                )
                scoil_html = gr.HTML(
                    value=_render_scoil_panel(),
                    label="Scoil ar an Léarscáil",
                )

            # Theme 3: Curaclam Trasteorann (Aer)
            with gr.Tab(translate("space2.curaclam_tab"), elem_classes="elem-aer"):
                gr.Markdown(
                    "**Cross-nation curriculum comparison.** "
                    "Type a topic to see how it's taught in 5 Celtic-nation "
                    "curricula (NCCA, CCEA, WJEC, DESC, SQA). "
                    "Try: 'atomic structure', 'calculus', 'photosynthesis', "
                    "'irish language', 'norman invasion', 'music composition'."
                )
                with gr.Row():
                    curaclam_input = gr.Textbox(
                        label="Topic query",
                        placeholder="e.g. 'atomic structure'",
                    )
                    compare_btn = gr.Button(
                        translate("common.submit"),
                        variant="primary",
                    )
                curaclam_output = gr.HTML(
                    value=_on_compare_curricula("atomic structure"),
                    label="Cross-nation comparison",
                )
                compare_btn.click(
                    fn=_on_compare_curricula,
                    inputs=[curaclam_input],
                    outputs=[curaclam_output],
                )

        render_anam_bonneagar_footer(
            space_id="cianfhoghlaim/meaisin-cliste",
            pobal_hp="Dublin 8 (-9.8 HP 2022)",
        )

    return demo


if __name__ == "__main__":
    app = build_app()
    app.launch(server_name="0.0.0.0", server_port=7860)
