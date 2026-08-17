"""agents.adk.subjects — the 60 per-subject agent surface.

Per the 2026-08-13-web-monorepo-consolidation-and-agent-integration-v1 change
(Phase 8 - 60 per-subject agents).

The 60 per-subject agents are organized into 4 stages:
- 14 LC subjects (Ireland Leaving Certificate)
- 8 JC subjects (Ireland Junior Cycle)
- 9 GCSE subjects × 3 boards (England) = 27 GCSE agents
- 15 A-Level subjects × 3 boards (England) = 45 A-Level agents

Total: 14 + 8 + 27 + 45 = 94 per-subject agent instances
(46 unique subjects × {1, 3 boards} = 94 instances)

Each agent inherits from SubjectAgentBase (base.py) and provides:
- 13 CopilotKit actions (per the codegen Phase 7)
- BAML extraction wiring (per the 4-stage BAML files Phase 4)
- CocoIndex v1 embedding wiring (per the 4-stage factory Phase 6)
- DLT source wiring (per the 4-stage DLT registry Phase 5)
- per-subject marimo notebook (Phase 9)
- web_integration binding (per Phase M)
"""

from .base import (
    LC_SUBJECT_AGENTS,
    JC_SUBJECT_AGENTS,
    GCSE_SUBJECT_AGENTS,
    A_LEVEL_SUBJECT_AGENTS,
    SubjectAgentBase,
)
from ._factory import (
    ALL_SUBJECT_AGENTS,
    LC_AGENTS,
    JC_AGENTS,
    GCSE_AGENTS,
    A_LEVEL_AGENTS,
    build_all_subject_agents,
    build_subject_agent_config,
)


# Re-export the 8 LC sample agents
from .lc.mathematics import mathematics_agent
from .lc.chemistry import chemistry_agent
from .lc.geography import geography_agent
from .lc.english import english_agent
from .lc.gaeilge import gaeilge_agent
from .lc.physics import physics_agent
from .lc.biology import biology_agent
from .lc.applied_mathematics import applied_mathematics_agent


__all__ = [
    "SubjectAgentBase",
    "LC_SUBJECT_AGENTS",
    "JC_SUBJECT_AGENTS",
    "GCSE_SUBJECT_AGENTS",
    "A_LEVEL_SUBJECT_AGENTS",
    "ALL_SUBJECT_AGENTS",
    "LC_AGENTS",
    "JC_AGENTS",
    "GCSE_AGENTS",
    "A_LEVEL_AGENTS",
    "build_subject_agent_config",
    "build_all_subject_agents",
    "mathematics_agent",
    "chemistry_agent",
    "geography_agent",
    "english_agent",
    "gaeilge_agent",
    "physics_agent",
    "biology_agent",
    "applied_mathematics_agent",
]
