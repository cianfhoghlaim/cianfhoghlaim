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

Per cianfhoghlaim/agents/tuatha/agents/ — the agents are imported
lazily at runtime to avoid pulling in google.adk + langfuse + letta
at import time.
"""

from __future__ import annotations

from typing import TYPE_CHECKING, Any

if TYPE_CHECKING:
    from cianfhoghlaim.agents.tuatha.agents.math_agent import math_agent
    from cianfhoghlaim.agents.tuatha.agents.appm_agent import appm_agent
    from cianfhoghlaim.agents.tuatha.agents.chem_agent import chem_agent
    from cianfhoghlaim.agents.tuatha.agents.comp_agent import comp_agent
    from cianfhoghlaim.agents.tuatha.agents.engl_agent import engl_agent
    from cianfhoghlaim.agents.tuatha.agents.gael_agent import gael_agent
    from cianfhoghlaim.agents.tuatha.agents.geog_agent import geog_agent
    from cianfhoghlaim.agents.tuatha.agents.hist_agent import hist_agent
    from cianfhoghlaim.agents.tuatha.agents.cross_subject_agent import cross_subject_agent


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


def make_subject_agent(subject: str) -> Any:
    """Return the ADK LlmAgent for the given NCCA subject.

    Lazy-imports the agent module to avoid pulling in google.adk at import time.
    Returns None if the agent module is unavailable (e.g., in tests).
    """
    if subject not in NCCA_SUBJECTS:
        raise ValueError(f"Unknown subject: {subject}. Must be one of {NCCA_SUBJECTS}.")

    agent_modules = {
        "mathematics": ".math_agent",
        "applied_mathematics": ".appm_agent",
        "chemistry": ".chem_agent",
        "geography": ".geog_agent",
        "history": ".hist_agent",
        "english": ".engl_agent",
        "gaeilge": ".gael_agent",
        "computer_science": ".comp_agent",
    }
    module_name = agent_modules[subject]
    try:
        import importlib
        module = importlib.import_module(module_name, package=__package__)
        return module.subject_agent
    except (ImportError, AttributeError):
        return None


def make_cross_subject_agent() -> Any:
    """Return the cross_subject_agent (the Brown Ajah's senior member)."""
    try:
        from cianfhoghlaim.agents.tuatha.agents.cross_subject_agent import cross_subject_agent
        return cross_subject_agent
    except ImportError:
        return None


__all__ = [
    "NCCA_SUBJECTS",
    "make_subject_agent",
    "make_cross_subject_agent",
]