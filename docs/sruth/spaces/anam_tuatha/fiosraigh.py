"""
spaces/anam_tuatha/fiosraigh.py
Fiosraigh feature: Classroom Bridge - i18n-aware workspace.

A simple i18n switcher that flips the visible text of the Space
between English and Gaeilge. Uses the spaces/_common/i18n module's
translate() function and a small set of "classroom action" strings
that are specific to the Anam Space.

This is the "classroom bridge" because it lets a single Gradio app
serve both English-medium and Irish-medium schools without code
duplication.
"""

from __future__ import annotations

from dataclasses import dataclass
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
import sys as _sys


@dataclass
class ClassroomAction:
    action_id: str
    en: str
    ga: str


# 10 common classroom actions for the demo
ACTIONS: list[ClassroomAction] = [
    ClassroomAction("submit", "Submit", "Seol"),
    ClassroomAction("save", "Save", "Sábháil"),
    ClassroomAction("next", "Next", "Ar aghaidh"),
    ClassroomAction("previous", "Previous", "Siar"),
    ClassroomAction("hint", "Hint", "Leid"),
    ClassroomAction("explain", "Explain", "Mínigh"),
    ClassroomAction("check", "Check answer", "Seiceáil an freagra"),
    ClassroomAction("restart", "Start over", "Tosaigh arís"),
    ClassroomAction("share", "Share", "Comhroinn"),
    ClassroomAction("print", "Print", "Priontáil"),
]


def _get_translate():
    """Lazy import to avoid the gradio import in __init__."""
    # Direct import of i18n.py (bypasses the gradio import)
    i18n_path = Path(__file__).parent.parent / "_common" / "i18n.py"
    spec = spec_from_file_location("spaces._common._i18n_direct", i18n_path)
    mod = module_from_spec(spec)
    _sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    return mod.translate, mod.set_lang, mod.I18N_STRINGS


def render_classroom_actions_html(lang: str = "en") -> str:
    """Render the 10 classroom actions as bilingual button labels.

    Args:
        lang: "en" or "ga". Returns both columns regardless.
    """
    translate, set_lang, _ = _get_translate()
    set_lang(lang)
    items: list[str] = []
    for action in ACTIONS:
        items.append(
            f'<div class="classroom-action" '
            f'style="display:flex; gap:0.5em; padding:0.4em; '
            f'border-bottom:1px solid #2a3a3a;">'
            f'<span style="color:#5a4fcf; font-family:monospace; '
            f'flex:0 0 100px;">{action.action_id}</span>'
            f'<span style="color:#d8d4cc; flex:1;">{action.en}</span>'
            f'<span style="color:#28955e; font-style:italic; flex:1;">'
            f"{action.ga}</span>"
            f"</div>"
        )
    return (
        f'<div class="fiosraigh-classroom" '
        f'style="background:#1a1d2e; padding:1.5em; '
        f'border:2px solid #5a4fcf; border-radius:4px;">'
        f'<h3 style="color:#5a4fcf; margin:0 0 0.5em 0; '
        f'font-family:Cinzel,serif;">Fiosraigh - Classroom Bridge</h3>'
        f'<p style="color:#d8d4cc; font-style:italic; margin:0 0 1em 0;">'
        f"10 common classroom actions, bilingual EN + GA. "
        f'Active language: <strong style="color:#5a4fcf;">{lang.upper()}</strong>.'
        f"</p>" + "".join(items) + "</div>"
    )
