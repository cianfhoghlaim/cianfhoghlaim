"""
spaces/_common/theme.py
Celtic 5-element palette + Hades Shadow-First palette for Gradio.

Per doc/hackathons/build-small-2026-plan.md design tokens:
  --celtic-emerald  #28955e  (Talamh / Space 1)
  --celtic-azure    #1e80c6  (Uisce / Space 2 themes)
  --celtic-amber    #d68c1c  (Tine / Space 4)
  --celtic-indigo   #5a4fcf  (Aer / Space 2+3)
  --celtic-gold     #cc9966  (Anam / Space 3+4)
  --hades-base      #1d1d2f  (background)
  --hades-ink       #1a1d2e  (deepest)
  --ncca-stone      #bcb8b0  (borders)
  --pobal-crimson   #a83a2a  (DEIS accents)
  --celtic-bronze   #a67c52  (Anam wallet badge)
"""

from __future__ import annotations

import gradio as gr


# 5-element palette - the connective tissue
CELTIC_PALETTE: dict[str, str] = {
    "emerald": "#28955e",  # Talamh (Earth)
    "azure": "#1e80c6",    # Uisce (Water)
    "amber": "#d68c1c",    # Tine (Fire)
    "indigo": "#5a4fcf",   # Aer (Air)
    "gold": "#cc9966",     # Anam (Spirit)
    "bronze": "#a67c52",   # Anam wallet badge
    "stone": "#bcb8b0",    # NCCA stone gray
    "crimson": "#a83a2a",  # Pobal DEIS crimson
}

# Hades Shadow-First base
HADES_PALETTE: dict[str, str] = {
    "base": "#1d1d2f",
    "ink": "#1a1d2e",
    "blood": "#ff6e61",
    "bone": "#d8d4cc",
}


# Combined token map
ALL_TOKENS: dict[str, str] = {**CELTIC_PALETTE, **HADES_PALETTE}


# Gradio CSS injection - applied via gr.Blocks(css=...)
GRADIO_CSS: str = """
/* 5-element palette (Celtic + Hades) */
:root {
    --celtic-emerald: #28955e;
    --celtic-azure:   #1e80c6;
    --celtic-amber:   #d68c1c;
    --celtic-indigo:  #5a4fcf;
    --celtic-gold:    #cc9966;
    --celtic-bronze:  #a67c52;
    --ncca-stone:     #bcb8b0;
    --pobal-crimson:  #a83a2a;
    --hades-base:     #1d1d2f;
    --hades-ink:      #1a1d2e;
    --hades-bone:     #d8d4cc;
}

/* Hades shadow-first base */
.dark {
    --body-background-fill: var(--hades-base);
    --body-text-color: var(--hades-bone);
    --block-background-fill: var(--hades-ink);
    --block-border-color: var(--celtic-bronze);
    --primary-button-background-fill: var(--celtic-gold);
    --primary-button-text-color: var(--hades-ink);
    --secondary-button-background-fill: var(--celtic-indigo);
    --secondary-button-border-color: var(--celtic-emerald);
}

/* Talamh (Earth) - emerald accent for Space 1 */
.elem-talamh {
    border-left: 4px solid var(--celtic-emerald);
    background: linear-gradient(90deg, rgba(40,149,94,0.08), transparent);
}
.elem-talamh h2, .elem-talamh h3 { color: var(--celtic-emerald); }

/* Uisce (Water) - azure accent for Space 2 */
.elem-uisce {
    border-left: 4px solid var(--celtic-azure);
    background: linear-gradient(90deg, rgba(30,128,198,0.08), transparent);
}
.elem-uisce h2, .elem-uisce h3 { color: var(--celtic-azure); }

/* Tine (Fire) - amber accent for Space 4 */
.elem-tine {
    border-left: 4px solid var(--celtic-amber);
    background: linear-gradient(90deg, rgba(214,140,28,0.08), transparent);
}
.elem-tine h2, .elem-tine h3 { color: var(--celtic-amber); }

/* Aer (Air) - indigo accent for Space 2+3 */
.elem-aer {
    border-left: 4px solid var(--celtic-indigo);
    background: linear-gradient(90deg, rgba(90,79,207,0.08), transparent);
}
.elem-aer h2, .elem-aer h3 { color: var(--celtic-indigo); }

/* Anam (Spirit) - gold accent for Space 3+4 */
.elem-anam {
    border-left: 4px solid var(--celtic-gold);
    background: linear-gradient(90deg, rgba(204,153,102,0.12), transparent);
}
.elem-anam h2, .elem-anam h3 { color: var(--celtic-gold);
    text-shadow: 0 0 8px rgba(204,153,102,0.4);
}

/* Bilingual EN/GA label */
.lang-toggle {
    font-family: 'Cormorant Garamond', 'Cinzel', serif;
    color: var(--celtic-gold);
    cursor: pointer;
    font-size: 0.9em;
}

/* Anam Bonneagar footer */
.anam-bonneagar-footer {
    font-size: 0.75em;
    color: var(--ncca-stone);
    border-top: 1px solid var(--celtic-bronze);
    padding-top: 0.5em;
    margin-top: 2em;
    font-family: 'JetBrains Mono', monospace;
}
.anam-bonneagar-footer .label { color: var(--celtic-gold); }
.anam-bonneagar-footer .value { color: var(--celtic-emerald); }

/* Celtic knotwork borders (decorative) */
.celtic-border {
    border: 2px solid var(--celtic-bronze);
    border-radius: 4px;
    box-shadow:
        inset 0 0 8px rgba(204,153,102,0.2),
        0 0 4px rgba(204,153,102,0.1);
    padding: 1em;
}

/* Headings use Cinzel serif; body uses Inter */
.gradio-container h1, .gradio-container h2 {
    font-family: 'Cinzel', 'Cormorant Garamond', serif;
    color: var(--celtic-gold);
    letter-spacing: 0.05em;
}
"""


def apply_celtic_theme() -> gr.Theme:
    """Return a Gradio Theme configured with the Celtic 5-element palette.

    Usage:
        with gr.Blocks(theme=apply_celtic_theme(), css=GRADIO_CSS) as demo:
            ...
    """
    theme = gr.themes.Soft(
        primary_hue="green",
        secondary_hue="stone",
        neutral_hue="dark",
    )
    # Override specific tokens via the .set() method if available
    try:
        theme = theme.set(
            body_background_fill="#1d1d2f",
            body_text_color="#d8d4cc",
            block_background_fill="#1a1d2e",
            block_border_color="#a67c52",
            button_primary_background_fill="#cc9966",
            button_primary_text_color="#1a1d2e",
            button_secondary_background_fill="#5a4fcf",
            input_background_fill="#1a1d2e",
        )
    except Exception:
        # Older Gradio API - fallback
        pass
    return theme
