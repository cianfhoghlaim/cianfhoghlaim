"""
spaces/anam_tuatha/app.py
Space 4: Anam: Tuatha na nGaelscoil.

The integration Space. 7 features mapped to 5 elements + 2 cross-cutting:
  1. Talamh (Earth)        - Curriculum Map (lifted from Space 1)
  2. Uisce (Water)         - Chemistry Visual
  3. Tine (Fire)           - OCR Gaelscribhneoir
  4. Aer (Air)             - Languages (Focloir - lifted from Space 2)
  5. Anam (Spirit)         - Soulbound Token
  6. Mac Leinn             - Formative Assessment (Exit Cards)
  7. Fiosraigh             - Classroom Bridge (i18n)

Element/feature mapping is the connective tissue across all 4 Spaces.

Gradio components:
  - Top: 5-element badge (the Tuatha world)
  - Left: 7-feature tab nav
  - Right: feature panel
  - Bottom: Anam Bonneagar + Anam Soulbound badge
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
from spaces.anam_tuatha.chemistry_visual import (
    list_molecules,
    render_molecule_svg,
)
from spaces.anam_tuatha.gaelscribhneoir import (
    SAMPLE_BAD_TEXT,
    SAMPLE_GOOD_TEXT,
    check_irish_text,
    render_metrics_html,
)
from spaces.anam_tuatha.mac_leinn import (
    generate_exit_card,
    render_exit_card_html,
)
from spaces.anam_tuatha.soulbound_local import (
    create_initial_state,
    record_feat,
    render_badge_html,
)
from spaces.anam_tuatha.fiosraigh import (
    render_classroom_actions_html,
)


_log = logging.getLogger("anam_tuatha.app")
set_lang("en")


# ---------------------------------------------------------------------
# Talamh (Earth): Curriculum Map (lifted from Space 1)
# ---------------------------------------------------------------------


def _render_talamh() -> str:
    """Talamh feature: a small curriculum-map summary.

    In a fuller build this would call back to Space 1's heatmap.
    For the demo, we show a static summary of the LC Chemistry
    topics that Space 1's extraction would find.
    """
    return (
        f'<div class="talamh-panel" '
        f'style="background:#1a1d2e; padding:1.5em; '
        f'border:2px solid #28955e; border-radius:4px;">'
        f'<h3 style="color:#28955e; margin:0 0 0.5em 0; '
        f'font-family:Cinzel,serif;">'
        f"{translate('space4.elem_talamh')}</h3>"
        f'<p style="color:#d8d4cc; font-style:italic; margin:0 0 1em 0;">'
        f"Reference: see <code>spaces/an_scrudu/heatmap.py</code> "
        f"for the full heatmap renderer. This is a summary tile "
        f"embedded in the Anam Space."
        f"</p>"
        f'<table style="width:100%; border-collapse:collapse; '
        f'font-family:Inter,sans-serif; font-size:0.85em;">'
        f'<tr style="border-bottom:1px solid #28955e;">'
        f'<th style="text-align:left; padding:0.4em; color:#28955e;">Topic</th>'
        f'<th style="text-align:left; padding:0.4em; color:#28955e;">Label</th>'
        f'<th style="text-align:right; padding:0.4em; color:#28955e;">Marks</th>'
        f"</tr>"
        f'<tr style="border-bottom:1px solid #2a3a3a;">'
        f'<td style="padding:0.4em; color:#28955e; font-family:monospace;">CH3</td>'
        f'<td style="padding:0.4em; color:#d8d4cc;">Atomic Structure</td>'
        f'<td style="padding:0.4em; color:#d8d4cc; text-align:right;">50</td>'
        f"</tr>"
        f'<tr style="border-bottom:1px solid #2a3a3a;">'
        f'<td style="padding:0.4em; color:#28955e; font-family:monospace;">CH4</td>'
        f'<td style="padding:0.4em; color:#d8d4cc;">Chemical Bonding</td>'
        f'<td style="padding:0.4em; color:#d8d4cc; text-align:right;">50</td>'
        f"</tr>"
        f'<tr style="border-bottom:1px solid #2a3a3a;">'
        f'<td style="padding:0.4em; color:#28955e; font-family:monospace;">CH5</td>'
        f'<td style="padding:0.4em; color:#d8d4cc;">Stoichiometry</td>'
        f'<td style="padding:0.4em; color:#d8d4cc; text-align:right;">50</td>'
        f"</tr>"
        f"</table>"
        f'<div style="margin-top:0.8em; font-size:0.8em; color:#bcb8b0;">'
        f"Element: Talamh (Earth) - the curriculum map. See Space 1 "
        f"(an-scrudu) for the full interactive heatmap."
        f"</div>"
        f"</div>"
    )


# ---------------------------------------------------------------------
# Uisce (Water): Chemistry Visual
# ---------------------------------------------------------------------


def _render_uisce(mol_key: str) -> str:
    """Uisce feature: molecule SVG + description."""
    mols = list_molecules()
    mol_lookup = {m["key"]: m for m in mols}
    if mol_key not in mol_lookup:
        mol_key = "water"
    mol_info = mol_lookup[mol_key]
    svg = render_molecule_svg(mol_key, size=280)
    # Description
    from spaces.anam_tuatha.chemistry_visual import MOLECULES

    mol = MOLECULES[mol_key]
    return (
        f'<div class="uisce-panel" '
        f'style="background:#1a1d2e; padding:1.5em; '
        f'border:2px solid #1e80c6; border-radius:4px;">'
        f'<h3 style="color:#1e80c6; margin:0 0 0.5em 0; '
        f'font-family:Cinzel,serif;">'
        f"{translate('space4.elem_uisce')}</h3>"
        f'<div style="display:flex; gap:1em; align-items:flex-start;">'
        f'<div style="flex:0 0 280px;">{svg}</div>'
        f'<div style="flex:1; color:#d8d4cc; '
        f'font-family:Inter,sans-serif;">'
        f'<h4 style="color:#1e80c6; margin:0 0 0.3em 0;">'
        f"{mol_info['name']} ({mol_info['formula']})</h4>"
        f'<p style="color:#28955e; font-style:italic; margin:0 0 0.5em 0;">'
        f"As Gaeilge: {mol_info['name_ga']}</p>"
        f'<p style="color:#d8d4cc; margin:0;">{mol.description}</p>'
        f"</div>"
        f"</div>"
        f"</div>"
    )


# ---------------------------------------------------------------------
# Tine (Fire): OCR Gaelscríbhneoir
# ---------------------------------------------------------------------


def _render_tine(text: str) -> str:
    """Tine feature: check the Irish text and return the metrics card."""
    if not text.strip():
        text = SAMPLE_GOOD_TEXT
    metrics = check_irish_text(text)
    return render_metrics_html(metrics)


# ---------------------------------------------------------------------
# Aer (Air): Languages (lifted from Space 2)
# ---------------------------------------------------------------------


def _render_aer() -> str:
    """Aer feature: a small cognate summary lifted from Space 2."""
    from spaces.meaisin_cliste.cognates import COGNATES

    rows: list[str] = []
    for c in COGNATES[:10]:
        rows.append(
            f'<tr style="border-bottom:1px solid #2a3a3a;">'
            f'<td style="padding:0.3em; color:#5a4fcf; font-family:monospace;">'
            f"{c.proto_celtic}</td>"
            f'<td style="padding:0.3em; color:#d8d4cc;">{c.en}</td>'
            f'<td style="padding:0.3em; color:#28955e; font-style:italic;">'
            f"{c.ie}</td>"
            f'<td style="padding:0.3em; color:#cc9966; font-style:italic;">'
            f"{c.cy}</td>"
            f"</tr>"
        )
    return (
        f'<div class="aer-panel" '
        f'style="background:#1a1d2e; padding:1.5em; '
        f'border:2px solid #5a4fcf; border-radius:4px;">'
        f'<h3 style="color:#5a4fcf; margin:0 0 0.5em 0; '
        f'font-family:Cinzel,serif;">'
        f"{translate('space4.elem_aer')}</h3>"
        f'<p style="color:#d8d4cc; font-style:italic; margin:0 0 1em 0;">'
        f"First 10 cognates from the Focloir na Se Naisiun table. "
        f"See Space 2 (meaisin-cliste) for the full interactive lookup."
        f"</p>"
        f'<table style="width:100%; border-collapse:collapse; '
        f'font-family:Inter,sans-serif; font-size:0.85em;">'
        f'<tr style="border-bottom:1px solid #5a4fcf;">'
        f'<th style="text-align:left; padding:0.3em; color:#5a4fcf;">Proto</th>'
        f'<th style="text-align:left; padding:0.3em; color:#5a4fcf;">EN</th>'
        f'<th style="text-align:left; padding:0.3em; color:#5a4fcf;">GA</th>'
        f'<th style="text-align:left; padding:0.3em; color:#5a4fcf;">CY</th>'
        f"</tr>" + "".join(rows) + "</table>"
        f"</div>"
    )


# ---------------------------------------------------------------------
# Anam (Spirit): Soulbound Token
# ---------------------------------------------------------------------


def _on_feat_recorded(state_json: str, element: str) -> tuple[str, str]:
    """Record a feat and re-render the badge."""
    import json

    state_data = json.loads(state_json) if state_json else {}
    state = create_initial_state(state_data.get("session", "demo"))
    state.feats_completed = state_data.get("feats_completed", 0)
    state.elements_active = state_data.get("elements_active", [])
    state.current_stage = state_data.get("current_stage", "setanta")
    record_feat(state, element)
    badge_html = render_badge_html(state)
    new_json = json.dumps(
        {
            "session": state_data.get("session", "demo"),
            "feats_completed": state.feats_completed,
            "elements_active": state.elements_active,
            "current_stage": state.current_stage,
        }
    )
    return badge_html, new_json


def _render_anam_init() -> tuple[str, str]:
    """Render the initial soulbound badge and return the initial state JSON."""
    state = create_initial_state("hackathon-demo-session")
    badge_html = render_badge_html(state)
    import json

    state_json = json.dumps(
        {
            "session": "hackathon-demo-session",
            "feats_completed": 0,
            "elements_active": [],
            "current_stage": "setanta",
        }
    )
    return badge_html, state_json


# ---------------------------------------------------------------------
# Mac Léinn: Formative Assessment
# ---------------------------------------------------------------------


def _render_mac_leinn(subject: str, topic: str) -> str:
    """Mac Leinn feature: generate the exit card."""
    card = generate_exit_card(topic, subject, "Leaving Certificate", 4)
    return render_exit_card_html(card)


# ---------------------------------------------------------------------
# Fiosraigh: Classroom Bridge
# ---------------------------------------------------------------------


def _render_fiosraigh(lang: str) -> str:
    """Fiosraigh feature: bilingual classroom actions."""
    return render_classroom_actions_html(lang)


# ---------------------------------------------------------------------
# Gradio app
# ---------------------------------------------------------------------


def build_app() -> gr.Blocks:
    with gr.Blocks(theme=apply_celtic_theme(), css=GRADIO_CSS, title="Anam Tuatha") as demo:
        # Hidden state for the soulbound token
        anam_state = gr.State(value="")

        gr.Markdown(
            f"""# {translate("space4.title")}
### *{translate("space4.subtitle")}*

The integration Space. 5 elements + 2 cross-cutting features = 7 panels.
Each panel maps to one element of the connective tissue that runs
through all 4 Spaces.""",
            elem_classes="elem-anam",
        )

        with gr.Tabs():
            # Talamh
            with gr.Tab(translate("space4.elem_talamh"), elem_classes="elem-talamh"):
                gr.HTML(value=_render_talamh())

            # Uisce
            with gr.Tab(translate("space4.elem_uisce"), elem_classes="elem-uisce"):
                mols = list_molecules()
                mol_choices = [(f"{m['name']} ({m['formula']})", m["key"]) for m in mols]
                mol_dropdown = gr.Dropdown(
                    choices=mol_choices,
                    value="methane",
                    label="Choose a molecule",
                )
                mol_html = gr.HTML(value=_render_uisce("methane"))
                mol_dropdown.change(
                    fn=_render_uisce,
                    inputs=[mol_dropdown],
                    outputs=[mol_html],
                )

            # Tine
            with gr.Tab(translate("space4.elem_tine"), elem_classes="elem-tine"):
                tine_text = gr.Textbox(
                    label="Paste Irish text to check",
                    value=SAMPLE_GOOD_TEXT,
                    lines=8,
                )
                tine_html = gr.HTML(value=_render_tine(SAMPLE_GOOD_TEXT))
                tine_text.change(
                    fn=_render_tine,
                    inputs=[tine_text],
                    outputs=[tine_html],
                )
                with gr.Row():
                    gr.Button("Use good sample").click(
                        fn=lambda: SAMPLE_GOOD_TEXT,
                        inputs=[],
                        outputs=[tine_text],
                    )
                    gr.Button("Use bad sample").click(
                        fn=lambda: SAMPLE_BAD_TEXT,
                        inputs=[],
                        outputs=[tine_text],
                    )

            # Aer
            with gr.Tab(translate("space4.elem_aer"), elem_classes="elem-aer"):
                gr.HTML(value=_render_aer())

            # Anam
            with gr.Tab(translate("space4.elem_anam"), elem_classes="elem-anam"):
                gr.Markdown(
                    "Click an element to record a feat. 5 feats unlocks "
                    "the Riastrad (warp spasm) stage."
                )
                anam_badge = gr.HTML(value="")
                with gr.Row():
                    for elem in ["talamh", "uisce", "tine", "aer", "anam"]:
                        gr.Button(elem.capitalize()).click(
                            fn=lambda e=elem: _on_feat_recorded(anam_state.value, e),
                            inputs=[],
                            outputs=[anam_badge, anam_state],
                        )

            # Mac Léinn
            with gr.Tab(translate("space4.mac_leinn"), elem_classes="elem-anam"):
                with gr.Row():
                    mac_subject = gr.Dropdown(
                        choices=[
                            "Chemistry",
                            "Mathematics",
                            "Irish",
                            "English",
                            "Biology",
                            "History",
                            "Physics",
                            "Geography",
                        ],
                        value="Chemistry",
                        label="Subject",
                    )
                    mac_topic = gr.Textbox(
                        label="Lesson topic",
                        value="Atomic Structure",
                    )
                mac_btn = gr.Button(translate("common.submit"), variant="primary")
                mac_html = gr.HTML(value=_render_mac_leinn("Chemistry", "Atomic Structure"))
                mac_btn.click(
                    fn=_render_mac_leinn,
                    inputs=[mac_subject, mac_topic],
                    outputs=[mac_html],
                )

            # Fiosraigh
            with gr.Tab(translate("space4.fiosraigh"), elem_classes="elem-aer"):
                fiosraigh_lang = gr.Radio(
                    choices=[("English", "en"), ("Gaeilge", "ga")],
                    value="en",
                    label="Active language",
                )
                fiosraigh_html = gr.HTML(value=_render_fiosraigh("en"))
                fiosraigh_lang.change(
                    fn=_render_fiosraigh,
                    inputs=[fiosraigh_lang],
                    outputs=[fiosraigh_html],
                )

        # Initial Anam badge load (no .then() needed; rendered at app start)
        demo.load(
            fn=_render_anam_init,
            inputs=[],
            outputs=[anam_badge, anam_state],
        )

        render_anam_bonneagar_footer(
            space_id="cianfhoghlaim/anam-tuatha",
            pobal_hp="Dublin 8 (-9.8 HP 2022)",
        )

    return demo


if __name__ == "__main__":
    app = build_app()
    app.launch(server_name="0.0.0.0", server_port=7860)
