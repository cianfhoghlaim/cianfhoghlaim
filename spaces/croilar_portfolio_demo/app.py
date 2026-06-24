"""
spaces/croilar_portfolio_demo/app.py

D4 of the spaces alignment plan. A 4-tab Gradio demo of the
Croílár multi-persona portfolio.
"""

from __future__ import annotations

import gradio as gr
from spaces._common import (
    apply_celtic_theme,
    GRADIO_CSS,
    render_anam_bonneagar_footer,
)


def build_portfolio_demo() -> gr.Blocks:
    """Build the 4-tab Gradio portfolio demo."""
    with gr.Blocks(title="Croílár — Portfolio Demo", css=GRADIO_CSS) as demo:
        gr.Markdown("# Croílár — Portfolio Demo")
        with gr.Tabs():
            with gr.Tab("Aleyum (music)"):
                gr.Markdown("Spotify + SoundCloud + GitHub. See `aleyum.py`.")
            with gr.Tab("Cianfhoghlaim (teaching)"):
                gr.Markdown("CV PDFs + teaching records. See `cianfhoghlaim.py`.")
            with gr.Tab("Carlcashman (research)"):
                gr.Markdown("ResearchGate + LinkedIn + GitHub. See `carlcashman.py`.")
            with gr.Tab("Bilingual EN/GA"):
                gr.Markdown("Celtic language toggle. See `bilingual.py`.")
        gr.HTML(render_anam_bonneagar_footer())
    return demo


if __name__ == "__main__":
    apply_celtic_theme()
    build_portfolio_demo().launch(server_name="0.0.0.0", server_port=7860)
