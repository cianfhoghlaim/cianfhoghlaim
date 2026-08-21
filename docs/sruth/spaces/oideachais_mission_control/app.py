"""
spaces/oideachais_mission_control/app.py

D1 of the spaces alignment plan. A Gradio app that surfaces
the 5 educational stages of the oideachais quadrant as
marimo notebooks over the canonical MotherDuck lakehouse,
plus Cognee cognify + BAML extraction buttons per stage.
"""

from __future__ import annotations

import gradio as gr
import marimo

from spaces._common import (
    apply_celtic_theme,
    GRADIO_CSS,
    render_anam_bonneagar_footer,
)


def build_mission_control() -> gr.Blocks:
    """Build the 5-tab Gradio mission control."""
    with gr.Blocks(title="Oideachais — Mission Control", css=GRADIO_CSS) as demo:
        gr.Markdown("# Oideachais — Mission Control")
        with gr.Tabs():
            with gr.Tab("Aistear"):
                gr.Markdown("Early Childhood (0-6). See `oideachais/notebooks/aistear.py`.")
            with gr.Tab("Primary"):
                gr.Markdown("Primary (Stages 1-4). See `oideachais/notebooks/primary.py`.")
            with gr.Tab("Junior Cycle"):
                gr.Markdown("Junior Cycle (Years 1-3). See `oideachais/notebooks/junior_cycle.py`.")
            with gr.Tab("Senior Cycle"):
                gr.Markdown("Senior Cycle (Years 4-6). See `oideachais/notebooks/senior_cycle.py`.")
            with gr.Tab("Tertiary"):
                gr.Markdown(
                    "Tertiary (CAO + NUI/HEI + QQI-FET). See `oideachais/notebooks/tertiary.py`."
                )
        gr.HTML(render_anam_bonneagar_footer())
    return demo


if __name__ == "__main__":
    apply_celtic_theme()
    build_mission_control().launch(server_name="0.0.0.0", server_port=7860)
