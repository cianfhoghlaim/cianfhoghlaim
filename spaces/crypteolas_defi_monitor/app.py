"""
spaces/crypteolas_defi_monitor/app.py

D2 of the spaces alignment plan. A 4-tab Gradio app for the
crypteolas Defi monitor.
"""

from __future__ import annotations

import gradio as gr
from spaces._common import (
    apply_celtic_theme,
    GRADIO_CSS,
    render_anam_bonneagar_footer,
)


def build_defi_monitor() -> gr.Blocks:
    """Build the 4-tab Gradio Defi monitor."""
    with gr.Blocks(title="Crypteolas — DeFi Monitor", css=GRADIO_CSS) as demo:
        gr.Markdown("# Crypteolas — DeFi Monitor")
        with gr.Tabs():
            with gr.Tab("GitHub"):
                gr.Markdown("Issues + PRs + commits + workflows. See `github_stream.py`.")
            with gr.Tab("DeFi"):
                gr.Markdown("DeFiLlama + CoinGecko + Binance + Aave/Pendle. See `defi_stream.py`.")
            with gr.Tab("Knowledge Graph"):
                gr.Markdown("Cognee + Graphiti. See `knowledge_graph.py`.")
            with gr.Tab("Marimo"):
                gr.Markdown("4 crypteolas notebooks. See `marimo_stream.py`.")
        gr.HTML(render_anam_bonneagar_footer())
    return demo


if __name__ == "__main__":
    apply_celtic_theme()
    build_defi_monitor().launch(server_name="0.0.0.0", server_port=7860)
