"""
spaces/cianfhoghlaim/dialogue.py
Turn-by-turn dialogue handler for the 6 NPCs.

Manages the conversation state for the current session (per-NPC) and
calls the BAML chain via chat_complete_json. Falls back to a templated
response if all 3 models fail (offline demo mode).
"""

from __future__ import annotations

import json
import logging
from dataclasses import dataclass, field

from spaces._common import chat_complete_json, HACKATHON_PRIMARY_MODEL
from spaces.cianfhoghlaim.npcs import (
    Npc,
    NPCS,
    build_dialogue_messages,
    get_npc,
)


_log = logging.getLogger("cianfhoghlaim")


@dataclass
class ConversationState:
    """The full conversation state for a single Space session."""
    history: list[dict[str, str]] = field(default_factory=list)
    current_npc_id: str = ""
    turn_count: int = 0
    artifacts_collected: list[str] = field(default_factory=list)


def _offline_response(npc: Npc, player_utterance: str) -> dict[str, str]:
    """A templated response used when all 3 models fail (offline demo)."""
    return {
        "utterance_en": (
            f"[Offline mode] I am {npc.name_en}, {npc.title}. "
            f"You said: '{player_utterance}'. "
            f"I would have answered, but the wind cut the thread."
        ),
        "utterance_ga": (
            f"[Mód as líne] Is mise {npc.name_ga}, {npc.title}. "
            f"Duirt tú: '{player_utterance}'. "
            f"Bhfreagróinn, ach ghearr an ghaoth an tsnáithe."
        ),
        "scholarly_footnote_en": (
            f"Source: {npc.wikipedia_source} (cached in doc/hackathons/wikipedia-sources/)."
        ),
        "scholarly_footnote_ga": (
            f"Foinse: {npc.wikipedia_source} (i dtaisce i doc/hackathons/wikipedia-sources/)."
        ),
        "emotional_tone": npc.emotional_default,
        "asks_player_about": f"What would you ask of {npc.name_en}?",
    }


def _validate_npc_response(parsed: dict[str, str], npc: Npc) -> dict[str, str]:
    """Validate a parsed NPC response, filling in missing keys with defaults."""
    required = [
        "utterance_en", "utterance_ga",
        "scholarly_footnote_en", "scholarly_footnote_ga",
        "emotional_tone", "asks_player_about",
    ]
    out = dict(parsed)
    for key in required:
        if key not in out or not out[key]:
            out[key] = _offline_response(npc, "")[key]
    if "quest_offered" in out and out["quest_offered"]:
        out["quest_offered"] = str(out["quest_offered"])[:300]
    return out


def speak_with_npc(
    state: ConversationState,
    npc_id: str,
    player_utterance: str,
) -> tuple[ConversationState, dict[str, str], str]:
    """Send a player utterance to the chosen NPC and return the response.

    Args:
        state: The current conversation state.
        npc_id: The NPC to speak with.
        player_utterance: What the player said.

    Returns:
        (new_state, response_dict, model_used). model_used is "" if the
        offline fallback was used.
    """
    npc = get_npc(npc_id)
    if npc is None:
        raise ValueError(f"Unknown NPC: {npc_id}. Choose from: {[n.npc_id for n in NPCS]}")

    # Update the active NPC
    if state.current_npc_id != npc_id:
        # Switching NPCs — reset history
        state.history = []
        state.current_npc_id = npc_id
        state.turn_count = 0

    messages = build_dialogue_messages(
        npc, player_utterance, state.history
    )

    model_used = ""
    try:
        parsed, model_used = chat_complete_json(
            messages, max_tokens=512, temperature=0.7
        )
        response = _validate_npc_response(parsed, npc)
    except (ValueError, RuntimeError) as e:
        _log.warning("BAML chain failed for NPC %s: %s", npc_id, e)
        response = _offline_response(npc, player_utterance)

    # Update history
    state.history.append({"role": "user", "content": player_utterance})
    state.history.append({
        "role": "assistant",
        "content": response["utterance_en"],
    })
    state.turn_count += 1

    # Award artifact on every 3rd turn (gamification)
    if state.turn_count % 3 == 0:
        if npc.artifact_offered not in state.artifacts_collected:
            state.artifacts_collected.append(npc.artifact_offered)
            response["artifact_granted"] = npc.artifact_offered
    # Always offer the quest hook on the first turn
    if state.turn_count == 1:
        response["quest_offered"] = npc.quest_hook

    return state, response, model_used


def get_npc_summary() -> list[dict[str, str]]:
    """Return a summary of all 6 NPCs for the Space's intro panel."""
    return [
        {
            "npc_id": npc.npc_id,
            "name_en": npc.name_en,
            "name_ga": npc.name_ga,
            "title": npc.title,
            "nation": npc.nation_name,
            "one_line": npc.one_line_summary,
            "color": npc.color_token,
        }
        for npc in NPCS
    ]
