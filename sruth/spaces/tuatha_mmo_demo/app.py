"""
spaces/tuatha_mmo_demo/app.py

D3 of the spaces alignment plan. A 4-tab Gradio demo of the
Tuatha Celtic Educational MMO.
"""

from __future__ import annotations

import gradio as gr
from spaces._common import (
    apply_celtic_theme,
    GRADIO_CSS,
    render_anam_bonneagar_footer,
)


def build_mmo_demo() -> gr.Blocks:
    """Build the 4-tab Gradio MMO demo."""
    with gr.Blocks(title="Tuatha — MMO Demo", css=GRADIO_CSS) as demo:
        gr.Markdown("# Tuatha — MMO Demo")
        with gr.Tabs():
            with gr.Tab("Map"):
                gr.Markdown("Babylon.js 7 + WebGPU British Isles map. See `babylon_scene.py`.")
            with gr.Tab("Quest"):
                gr.Markdown("BCS topic quest with the 4-feedback-channel agents. See `quest.py`.")
            with gr.Tab("Achievement Ledger"):
                gr.Markdown("5-feat progression (0 → Setanta, 2 → Cúchulainn, 5 → Ríastrad). See `achievement_ledger.py`.")
            with gr.Tab("Knowledge Graph"):
                gr.Markdown("Cognee + Graphiti. See `knowledge_graph.py`.")
        gr.HTML(render_anam_bonneagar_footer())
    return demo


if __name__ == "__main__":
    apply_celtic_theme()
    build_mmo_demo().launch(server_name="0.0.0.0", server_port=7860)
