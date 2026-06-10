"""
spaces/cianfhoghlaim/app.py
Space 3: Cianfhoghlaim - Tuatha RPG.

Hades-style dialogue with 6 Celtic NPCs on a navigable British Isles
map. Each NPC is grounded in a cached Wikipedia article. The dialogue
model is the 3-tier HF Inference fallback chain.

The map is rendered as inline SVG (no Babylon.js / WebGPU - too heavy
for a Gradio Space). The visual is intentionally simple but on-theme:
Hades Shadow-First base + Celtic 5-element palette + Anam gold accents.

Gradio components:
  - Left: SVG map with clickable NPC markers
  - Right: NPC name + title + dialogue log + player input
  - Bottom: artifacts collected (gamification)
  - Footer: Anam Bonneagar (5 trust signals)
"""

from __future__ import annotations

import json
import logging
from pathlib import Path

import gradio as gr

from spaces._common import (
    apply_celtic_theme,
    GRADIO_CSS,
    render_anam_bonneagar_footer,
    translate,
    set_lang,
)
from spaces._common.baml_client import get_hackathon_client_config
from spaces.cianfhoghlaim.npcs import NPCS, get_npc
from spaces.cianfhoghlaim.dialogue import (
    ConversationState,
    get_npc_summary,
    speak_with_npc,
)


_log = logging.getLogger("cianfhoghlaim.app")
set_lang("en")  # default; toggle below flips to "ga"


# ---------------------------------------------------------------------
# Map rendering (inline SVG, no WebGL)
# ---------------------------------------------------------------------

_WORLD_MAP = json.loads(
    Path(__file__).parent.joinpath("world_map.json").read_text(encoding="utf-8")
)


def _render_map_svg(highlighted_npc_id: str = "") -> str:
    """Render the world map as a self-contained SVG string.

    Args:
        highlighted_npc_id: If non-empty, the matching NPC marker gets
            a gold ring (the "selected" state).
    """
    vp = _WORLD_MAP["viewport"]
    w, h = vp["width_units"], vp["height_units"]

    parts: list[str] = [
        f'<svg xmlns="http://www.w3.org/2000/svg" '
        f'viewBox="0 0 {w} {h}" '
        f'width="100%" height="auto" '
        f'style="background:{vp["background_color"]}; '
        f'border:2px solid #a67c52; border-radius:4px;">',
    ]

    # Sea grid (subtle, gold on the dark background)
    for gx in range(50, w, 50):
        parts.append(
            f'<line x1="{gx}" y1="0" x2="{gx}" y2="{h}" '
            f'stroke="{vp["grid_color"]}" stroke-width="0.3" '
            f'stroke-opacity="0.15" />'
        )
    for gy in range(50, h, 50):
        parts.append(
            f'<line x1="0" y1="{gy}" x2="{w}" y2="{gy}" '
            f'stroke="{vp["grid_color"]}" stroke-width="0.3" '
            f'stroke-opacity="0.15" />'
        )

    # Diegetic zones
    for zone in _WORLD_MAP["diegetic_zones"]:
        pts = " ".join(f"{x},{y}" for x, y in zone["polygon"])
        parts.append(
            f'<polygon points="{pts}" '
            f'fill="{zone["fill_color"]}" fill-opacity="{zone["fill_opacity"]}" '
            f'stroke="{zone["stroke_color"]}" stroke-width="{zone["stroke_width"]}" />'
        )
        # Zone label
        cx = sum(p[0] for p in zone["polygon"]) / len(zone["polygon"])
        cy = sum(p[1] for p in zone["polygon"]) / len(zone["polygon"])
        parts.append(
            f'<text x="{cx}" y="{cy}" text-anchor="middle" '
            f'fill="#d8d4cc" font-family="Cormorant Garamond, serif" '
            f'font-size="13" font-style="italic">{zone["label_en"]}</text>'
        )

    # NPC markers
    for marker in _WORLD_MAP["npc_markers"]:
        is_highlighted = marker["npc_id"] == highlighted_npc_id
        r = marker["radius"] + (4 if is_highlighted else 0)
        if is_highlighted:
            parts.append(
                f'<circle cx="{marker["x"]}" cy="{marker["y"]}" r="{r + 4}" '
                f'fill="none" stroke="#cc9966" stroke-width="2" '
                f'stroke-dasharray="3,3">'
                f'<animate attributeName="r" '
                f'values="{r};{r + 6};{r}" dur="2s" repeatCount="indefinite" />'
                f'<animate attributeName="stroke-opacity" '
                f'values="1;0.4;1" dur="2s" repeatCount="indefinite" />'
                f'</circle>'
            )
        parts.append(
            f'<circle cx="{marker["x"]}" cy="{marker["y"]}" r="{r}" '
            f'fill="{marker["color"]}" stroke="#1a1d2e" stroke-width="2" />'
        )
        # Icon glyph
        icon_glyph = {
            "triskelion": "*",
            "wave": "~",
            "horse": ">",
            "caduceus": "+",
            "boar": "^",
            "currach": "=",
        }.get(marker["icon"], "?")
        parts.append(
            f'<text x="{marker["x"]}" y="{marker["y"] + 5}" '
            f'text-anchor="middle" fill="#1a1d2e" font-size="14" '
            f'font-family="monospace" font-weight="bold">{icon_glyph}</text>'
        )

    # World labels
    for label in _WORLD_MAP["labels"]:
        parts.append(
            f'<text x="{label["x"]}" y="{label["y"]}" text-anchor="middle" '
            f'fill="{label["color"]}" font-family="{label["font"]}, serif" '
            f'font-size="{label["size"]}" font-style="italic">{label["text_en"]}</text>'
        )

    parts.append("</svg>")
    return "".join(parts)


# ---------------------------------------------------------------------
# Gradio app
# ---------------------------------------------------------------------

_NPC_CHOICES: list[tuple[str, str]] = [
    (f"{n.name_en} ({n.nation_name})", n.npc_id) for n in NPCS
]


def _on_npc_select(
    npc_id: str,
    history: list[list[str]] | None,
    state_json: str,
):
    """When the user picks a new NPC, reset the conversation and render."""
    npc = get_npc(npc_id)
    if npc is None:
        return gr.update(), gr.update(), state_json
    # Reset state
    state = ConversationState(
        history=[],
        current_npc_id=npc_id,
        turn_count=0,
        artifacts_collected=[],
    )
    intro = (
        f"*{npc.name_en}* — {npc.title}\n\n"
        f"_{npc.diegetic_zone}_\n\n"
        f"*{translate('space3.diegetic_zone', zone=npc.diegetic_zone)}*\n\n"
        f"**Quest:** {npc.quest_hook}\n\n"
        f"*Say something to {npc.name_en}...*"
    )
    return (
        gr.update(value=intro),
        gr.update(value=_render_map_svg(highlighted_npc_id=npc_id)),
        _state_to_json(state),
    )


def _state_to_json(state: ConversationState) -> str:
    return json.dumps({
        "history": state.history,
        "current_npc_id": state.current_npc_id,
        "turn_count": state.turn_count,
        "artifacts_collected": state.artifacts_collected,
    })


def _state_from_json(s: str) -> ConversationState:
    if not s:
        return ConversationState()
    data = json.loads(s)
    return ConversationState(
        history=data.get("history", []),
        current_npc_id=data.get("current_npc_id", ""),
        turn_count=data.get("turn_count", 0),
        artifacts_collected=data.get("artifacts_collected", []),
    )


def _on_player_send(
    player_msg: str,
    state_json: str,
):
    """When the player sends a message, call the BAML chain and update the log."""
    if not player_msg.strip():
        return "", state_json
    state = _state_from_json(state_json)
    if not state.current_npc_id:
        return "Pick an NPC first.", state_json

    state, response, model_used = speak_with_npc(
        state, state.current_npc_id, player_msg
    )

    npc = get_npc(state.current_npc_id)
    assert npc is not None

    # Render the new turn as Markdown
    artifact_text = ""
    if "artifact_granted" in response:
        artifact_text = (
            f"\n\n**Artifact granted:** {response['artifact_granted']}"
        )
    quest_text = ""
    if "quest_offered" in response:
        quest_text = f"\n\n*Quest:* {response['quest_offered']}"

    rendered = (
        f"**{npc.name_en}** _(tone: {response['emotional_tone']})_\n\n"
        f"> {response['utterance_en']}\n\n"
        f"*As Gaeilge:* {response['utterance_ga']}\n\n"
        f"<sub>Scholarly footnote: {response['scholarly_footnote_en']}</sub>\n\n"
        f"*{response['asks_player_about']}*"
        f"{quest_text}{artifact_text}"
        f"\n\n---\n\n*Model used: {model_used or 'offline-fallback'}*"
    )

    return rendered, _state_to_json(state)


def _on_show_artifacts(state_json: str) -> str:
    """Return a Markdown list of artifacts the player has collected."""
    state = _state_from_json(state_json)
    if not state.artifacts_collected:
        return "_No artifacts yet. Speak to a champion._"
    lines = [f"- {a}" for a in state.artifacts_collected]
    return "**Artifacts collected:**\n\n" + "\n".join(lines)


def _on_show_client_config() -> str:
    """Return a Markdown summary of the BAML client config."""
    cfg = get_hackathon_client_config()
    lines = [
        f"- **Primary:** {cfg['primary']}",
        f"- **Fallback 1:** {cfg['fallback_1']}",
        f"- **Fallback 2:** {cfg['fallback_2']}",
        f"- **Base URL:** {cfg['base_url']}",
        f"- **HF_TOKEN set:** {cfg['hf_token_set']}",
    ]
    return "**Hackathon model layer (3-tier fallback, <=32B):**\n\n" + "\n".join(lines)


def build_app() -> gr.Blocks:
    """Build and return the Gradio Blocks app."""
    cfg = get_hackathon_client_config()
    npc_summary = get_npc_summary()

    with gr.Blocks(theme=apply_celtic_theme(), css=GRADIO_CSS, title="Cianfhoghlaim") as demo:
        # Hidden state
        state_json = gr.State(value="")

        # Header
        gr.Markdown(
            f"""# {translate("space3.title")}
### *{translate("space3.subtitle")}*

A navigable map of the British Isles. Six champions stand in the wind.
Choose one to speak with. They are grounded in cached Wikipedia sources
and answer via the 3-tier HF Inference fallback (Qwen 7B -> Llama 8B
-> Gemma 9b, all <=32B).""",
            elem_classes="elem-anam",
        )

        with gr.Row():
            with gr.Column(scale=3):
                # Map (SVG, clickable via the NPC selector below)
                map_html = gr.HTML(
                    value=_render_map_svg(),
                    label="Tuatha - the navigable world",
                )
                # NPC selector
                npc_dropdown = gr.Dropdown(
                    choices=_NPC_CHOICES,
                    value=NPCS[0].npc_id,
                    label=translate("space3.choose_npc"),
                )
            with gr.Column(scale=4):
                # NPC intro / dialogue log
                dialogue_log = gr.Markdown(
                    value=(
                        f"*{NPCS[0].name_en}* — {NPCS[0].title}\n\n"
                        f"_{NPCS[0].diegetic_zone}_\n\n"
                        f"{NPCS[0].one_line_summary}\n\n"
                        f"*Say something to {NPCS[0].name_en}...*"
                    ),
                    label="Dialogue",
                )
                with gr.Row():
                    player_input = gr.Textbox(
                        label="Your utterance",
                        placeholder="Say something to the champion...",
                        scale=4,
                    )
                    send_btn = gr.Button(
                        translate("common.submit"),
                        scale=1,
                        variant="primary",
                    )
                model_badge = gr.Markdown(
                    value=f"_{cfg['primary']} (with 2 fallbacks)_",
                    label="Active model",
                )

        with gr.Row():
            with gr.Column():
                artifacts_panel = gr.Markdown(
                    value="_No artifacts yet._",
                    label="Anam - the soulbound token",
                )
                show_artifacts_btn = gr.Button(
                    "Show artifacts",
                    size="sm",
                )
            with gr.Column():
                client_config_panel = gr.Markdown(
                    value=_on_show_client_config(),
                    label="Model layer",
                )

        # Wire up events
        npc_dropdown.change(
            fn=_on_npc_select,
            inputs=[npc_dropdown, dialogue_log, state_json],
            outputs=[dialogue_log, map_html, state_json],
        )
        send_btn.click(
            fn=_on_player_send,
            inputs=[player_input, state_json],
            outputs=[dialogue_log, state_json],
        ).then(
            fn=lambda: "",
            inputs=[],
            outputs=[player_input],
        )
        player_input.submit(
            fn=_on_player_send,
            inputs=[player_input, state_json],
            outputs=[dialogue_log, state_json],
        ).then(
            fn=lambda: "",
            inputs=[],
            outputs=[player_input],
        )
        show_artifacts_btn.click(
            fn=_on_show_artifacts,
            inputs=[state_json],
            outputs=[artifacts_panel],
        )

        # Footer
        render_anam_bonneagar_footer(space_id="cianfhoghlaim/cianfhoghlaim")

    return demo


if __name__ == "__main__":
    app = build_app()
    app.launch(server_name="0.0.0.0", server_port=7860)
