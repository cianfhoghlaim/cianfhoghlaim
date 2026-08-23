"""tuatha.agents.educational — the 3 educational agents.

The canonical re-export surface. The 3 educational agents
form the academic + Celtic-language specialty layer on top
of the 8 NCCA subject agents.
"""
from __future__ import annotations

try:
    from .academic_history_agent import (  # type: ignore
        academic_history_agent,
    )
    from .celtic_grammar_agent import (  # type: ignore
        celtic_grammar_agent,
    )
    from .celtic_morphology_agent import (  # type: ignore
        celtic_morphology_agent,
    )

    AGENTS = {
        "academic_history": academic_history_agent,
        "celtic_grammar": celtic_grammar_agent,
        "celtic_morphology": celtic_morphology_agent,
    }
except ImportError:
    AGENTS = {}


__all__ = [
    "AGENTS",
    "academic_history_agent",
    "celtic_grammar_agent",
    "celtic_morphology_agent",
]
