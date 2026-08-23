"""tuatha.subjects — the 8 NCCA subject agents.

The canonical re-export surface. Each subject agent is an
ADK LlmAgent with 5 per-subject tools (syllabus / past_paper /
marking_scheme / formative_item / response_score).
"""
from __future__ import annotations

# Per the BAML/Letta graceful-degradation pattern: this is the
# canonical mount point. The 8 subject agents are imported
# lazily (not at package load time) so the BAML client +
# Langfuse + Cognee + Letta imports don't crash on import.
try:
    from .applied_mathematics import appm_agent  # type: ignore
    from .chemistry import chem_agent  # type: ignore
    from .computer_science import comp_agent  # type: ignore
    from .english import engl_agent  # type: ignore
    from .gaeilge import gael_agent  # type: ignore
    from .geography import geog_agent  # type: ignore
    from .history import hist_agent  # type: ignore
    from .mathematics import math_agent  # type: ignore

    SUBJECTS = {
        "mathematics": math_agent,
        "applied_mathematics": appm_agent,
        "chemistry": chem_agent,
        "geography": geog_agent,
        "history": hist_agent,
        "english": engl_agent,
        "gaeilge": gael_agent,
        "computer_science": comp_agent,
    }
except ImportError:
    # Graceful degradation for unit tests in isolation.
    SUBJECTS = {}


__all__ = [
    "SUBJECTS",
    "appm_agent",
    "chem_agent",
    "comp_agent",
    "engl_agent",
    "gael_agent",
    "geog_agent",
    "hist_agent",
    "math_agent",
]
