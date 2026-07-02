"""ADK subject router — maps the 8 NCCA subjects to their ADK specialists.

Per the Brown Ajah theming (`docs/BROWN_AJAH_THEMING.md`), the 8 NCCA
subject ADK specialists are the 8 Brown Ajah members:
  - math_agent     ↔ The Dagda (cauldron of plenty)        ↔ Mathematics
  - appm_agent     ↔ Lugh (samildanach)                    ↔ Applied Mathematics
  - chem_agent     ↔ Dian Cecht (healing)                   ↔ Chemistry
  - comp_agent     ↔ — (modern subject)                     ↔ Computer Science
  - engl_agent     ↔ Brigid (poetry + healing)              ↔ English
  - gael_agent     ↔ Ogma (eloquence + learning)            ↔ Gaeilge
  - geog_agent     ↔ Manannán mac Lir (sea)                 ↔ Geography
  - hist_agent     ↔ The Morrígan (war + death)             ↔ History

The 8 agents live at `cianfhoghlaim.agents.tuatha.<slug>_agent.py`
(e.g. `math_agent.py`, `appm_agent.py`, ...). Each module exports
a single `<slug>_agent` LlmAgent instance with 5 FunctionTools
(syllabus / past paper / marking scheme / formative item / response score).

This router lazy-imports them to avoid pulling in `google.adk`,
`langfuse`, `letta`, etc. at import time. It also builds ADK
`SequentialAgent` "teams" that wrap a subject specialist together
with the cross-subject senior member so that a single `InMemoryRunner`
can dispatch to both.

Reference: openspec/changes/cianfhoghlaim-educational-mmo-v1 (D3).
"""

from __future__ import annotations

import importlib
from typing import Any

NCCA_SUBJECTS: tuple[str, ...] = (
    "mathematics",
    "applied_mathematics",
    "chemistry",
    "geography",
    "history",
    "english",
    "gaeilge",
    "computer_science",
)

# The NCCA subject slug → (module file slug, exported attribute name).
# The existing agents live at `cianfhoghlaim.agents.tuatha.<slug>_agent.py`
# and each exports a module-level `<slug>_agent` LlmAgent instance.
_SUBJECT_MODULE_SLUGS: dict[str, str] = {
    "mathematics": "math",
    "applied_mathematics": "appm",
    "chemistry": "chem",
    "geography": "geog",
    "history": "hist",
    "english": "engl",
    "gaeilge": "gael",
    "computer_science": "comp",
}

# Pretty display names for each NCCA subject (used in prompts + agent names).
SUBJECT_DISPLAY_NAMES: dict[str, str] = {
    "mathematics": "Mathematics",
    "applied_mathematics": "Applied Mathematics",
    "chemistry": "Chemistry",
    "geography": "Geography",
    "history": "History",
    "english": "English",
    "gaeilge": "Gaeilge",
    "computer_science": "Computer Science",
}

# Brown Ajah ↔ Tuatha Dé deity mapping
TUATHA_DE_MAPPING: dict[str, tuple[str, str]] = {
    "mathematics": ("The Dagda", "cauldron-of-plenty"),
    "applied_mathematics": ("Lugh", "samildanach"),
    "chemistry": ("Dian Cecht", "healing"),
    "computer_science": ("—", "modern-subject"),
    "english": ("Brigid", "poetry-healing"),
    "gaeilge": ("Ogma", "eloquence-learning"),
    "geography": ("Manannán mac Lir", "sea"),
    "history": ("The Morrígan", "war-death"),
}


def _require_subject(subject: str) -> str:
    """Validate `subject` and return it unchanged, raising ValueError on miss."""
    if subject not in NCCA_SUBJECTS:
        raise ValueError(
            f"Unknown subject: {subject!r}. Must be one of {NCCA_SUBJECTS}."
        )
    return subject


def _import_subject_agent_module(subject: str) -> Any:
    """Import the `<slug>_agent.py` module for `subject`.

    Returns `None` (not raising) when the module cannot be imported —
    e.g. when the optional ADK runtime (`google.adk`) is unavailable,
    which is the default in lightweight dev / test environments.

    This is the **single** import path used by `make_subject_agent`,
    `make_subject_team`, and `list_all_agents`, so they share
    consistent lazy-import semantics.
    """
    _require_subject(subject)
    slug = _SUBJECT_MODULE_SLUGS[subject]
    module_path = f"cianfhoghlaim.agents.tuatha.{slug}_agent"
    try:
        return importlib.import_module(module_path)
    except ImportError:
        return None


def _get_subject_agent_attr(module: Any, subject: str) -> Any:
    """Return `<slug>_agent` from `module`, falling back to `subject_agent`."""
    if module is None:
        return None
    slug = _SUBJECT_MODULE_SLUGS[subject]
    primary = f"{slug}_agent"
    if hasattr(module, primary):
        return getattr(module, primary)
    if hasattr(module, "subject_agent"):
        return getattr(module, "subject_agent")
    return None


def make_subject_agent(subject: str) -> Any:
    """Return the ADK `LlmAgent` for the given NCCA subject.

    Lazy-imports the agent module to avoid pulling in `google.adk`,
    `langfuse`, `letta`, and the rest of the BAML runtime at module
    import time. Returns `None` if the underlying module is
    unavailable (e.g. `google.adk` is not installed in the venv).
    """
    try:
        module = _import_subject_agent_module(subject)
    except ValueError:
        raise
    return _get_subject_agent_attr(module, subject)


def make_cross_subject_agent() -> Any:
    """Return the cross-subject master agent (the Brown Ajah's senior member).

    The cross-subject agent sits above the 8 NCCA specialists and uses
    `b.ExtractKeyCompetencies` output to bridge across the 8 subjects
    via the 5 NCCA Key Competencies.
    """
    try:
        from cianfhoghlaim.agents.tuatha.agents.cross_subject_agent import (
            cross_subject_agent,
        )
        return cross_subject_agent
    except ImportError:
        return None


def make_subject_team(subject: str) -> Any:
    """Return an ADK `SequentialAgent` "team" for the given NCCA subject.

    A team is `[cross_subject_agent, subject_agent]` executed in
    sequence — the cross-subject senior member sees the query first
    (handing off cross-subject context if needed), then the subject
    specialist answers the NCCA LO-level work.

    Returns `None` if either the subject agent or the ADK runtime
    is unavailable. The team name is e.g. `mathematics_team`.
    """
    _require_subject(subject)
    subject_agent = make_subject_agent(subject)
    if subject_agent is None:
        return None
    cross_subject = make_cross_subject_agent()
    if cross_subject is None:
        return None

    try:
        from google.adk.agents import SequentialAgent
    except ImportError:
        return None

    display = SUBJECT_DISPLAY_NAMES[subject]
    sub_agents: list[Any] = [cross_subject, subject_agent]
    return SequentialAgent(
        name=f"{_SUBJECT_MODULE_SLUGS[subject]}_team",
        description=(
            f"ADK team for NCCA {display}: cross-subject reasoning "
            f"first, then the {display} specialist. Brown Ajah ↔ "
            f"{TUATHA_DE_MAPPING[subject][0]}."
        ),
        sub_agents=sub_agents,
    )


def list_all_agents() -> list[dict[str, Any]]:
    """Return all 8 NCCA subject agents + the cross-subject master + mapping.

    Each entry is a dict with:
      - `subject`: canonical NCCA slug (e.g. `"mathematics"`)
      - `display_name`: e.g. `"Mathematics"`
      - `module_slug`: file-name slug (e.g. `"math"`)
      - `agent`: the lazy-loaded `LlmAgent` (or `None` if unavailable)
      - `tuatha_de`: the Tuatha Dé deity mapped to this subject
      - `lore`: short lore context (e.g. `"cauldron-of-plenty"`)
      - `brown_ajah_member`: same as `module_slug` (each agent is
        exactly one Brown Ajah member)

    Use this for the Brown Ajah status display + the
    cross-quadrant observability probe that the root_agent calls
    once per session to enumerate the 8 specialists.
    """
    out: list[dict[str, Any]] = []
    for subject in NCCA_SUBJECTS:
        module = _import_subject_agent_module(subject)
        agent = _get_subject_agent_attr(module, subject)
        deity, lore = TUATHA_DE_MAPPING[subject]
        out.append(
            {
                "subject": subject,
                "display_name": SUBJECT_DISPLAY_NAMES[subject],
                "module_slug": _SUBJECT_MODULE_SLUGS[subject],
                "agent": agent,
                "tuatha_de": deity,
                "lore": lore,
                "brown_ajah_member": _SUBJECT_MODULE_SLUGS[subject],
            }
        )
    return out


def get_tuatha_de_mapping(subject: str) -> tuple[str, str]:
    """Return `(Tuatha Dé deity, lore context)` for the given subject."""
    return TUATHA_DE_MAPPING.get(subject, ("—", ""))


__all__ = [
    "NCCA_SUBJECTS",
    "SUBJECT_DISPLAY_NAMES",
    "TUATHA_DE_MAPPING",
    "make_subject_agent",
    "make_cross_subject_agent",
    "make_subject_team",
    "list_all_agents",
    "get_tuatha_de_mapping",
]
