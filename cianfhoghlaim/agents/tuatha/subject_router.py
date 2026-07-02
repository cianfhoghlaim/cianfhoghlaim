"""ADK subject router — maps the 8 NCCA subjects to their ADK specialists.

Per the Brown Ajah theming (docs/BROWN_AJAH_THEMING.md), the 8 NCCA
subject ADK specialists are the 8 Brown Ajah members:
  - math_agent     ↔ The Dagda (cauldron of plenty)        ↔ Mathematics
  - appm_agent     ↔ Lugh (samildanach)                    ↔ Applied Mathematics
  - chem_agent     ↔ Dian Cecht (healing)                   ↔ Chemistry
  - comp_agent     ↔ — (modern subject)                     ↔ Computer Science
  - engl_agent     ↔ Brigid (poetry + healing)             ↔ English
  - gael_agent     ↔ Ogma (eloquence + learning)           ↔ Gaeilge
  - geog_agent     ↔ Manannán mac Lir (sea)                ↔ Geography
  - hist_agent     ↔ The Morrígan (war + death)             ↔ History

The existing 8 agents live at `cianfhoghlaim.agents.tuatha.<subject>_agent`
(they predate the v4 consolidation). This router lazy-imports them
to avoid pulling in google.adk + langfuse + letta at import time.
"""

from __future__ import annotations

import importlib
from typing import Any

NCCA_SUBJECTS = (
    "mathematics",
    "applied_mathematics",
    "chemistry",
    "geography",
    "history",
    "english",
    "gaeilge",
    "computer_science",
)

# The Brown Ajah ↔ Tuatha Dé deity mapping
TUATHA_DE_MAPPING = {
    "mathematics": ("The Dagda", "cauldron-of-plenty"),
    "applied_mathematics": ("Lugh", "samildanach"),
    "chemistry": ("Dian Cecht", "healing"),
    "computer_science": ("—", "modern-subject"),
    "english": ("Brigid", "poetry-healing"),
    "gaeilge": ("Ogma", "eloquence-learning"),
    "geography": ("Manannán mac Lir", "sea"),
    "history": ("The Morrígan", "war-death"),
}


def make_subject_agent(subject: str) -> Any:
    """Return the ADK LlmAgent for the given NCCA subject.

    Lazy-imports the agent module to avoid pulling in google.adk at import time.
    Returns None if the agent module is unavailable (e.g., in tests).
    """
    if subject not in NCCA_SUBJECTS:
        raise ValueError(f"Unknown subject: {subject}. Must be one of {NCCA_SUBJECTS}.")

    # The existing agent modules live at cianfhoghlaim.agents.tuatha.<slug>_agent
    module_path = f"cianfhoghlaim.agents.tuatha.{subject}_agent"
    try:
        module = importlib.import_module(module_path)
        return getattr(module, f"{subject}_agent", None) or getattr(module, "subject_agent", None)
    except (ImportError, AttributeError):
        return None


def make_cross_subject_agent() -> Any:
    """Return the cross_subject_agent (the Brown Ajah's senior member)."""
    try:
        from cianfhoghlaim.agents.tuatha.agents.cross_subject_agent import cross_subject_agent
        return cross_subject_agent
    except ImportError:
        return None


def get_tuatha_de_mapping(subject: str) -> tuple[str, str]:
    """Return (Tuatha Dé deity, lore context) for the given subject."""
    return TUATHA_DE_MAPPING.get(subject, ("—", ""))


__all__ = [
    "NCCA_SUBJECTS",
    "TUATHA_DE_MAPPING",
    "make_subject_agent",
    "make_cross_subject_agent",
    "get_tuatha_de_mapping",
]