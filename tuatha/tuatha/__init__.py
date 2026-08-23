"""tuatha — the British Isles Formative Assessment MMO.

The canonical Python sub-namespace for the new
`/Users/cianmacandeisigh/dev/kings_college_galway/tuatha/`
independent sub-project (will become
`github.com/cianmacandeisigh/tuatha.git`).

The 4 agent types:
- The 8 NCCA subject agents (mathematics / applied_mathematics
  / chemistry / geography / history / english / gaeilge /
  computer_science) at `tuatha.subjects.*`
- The 3 educational agents (academic_history_agent +
  celtic_grammar_agent + celtic_morphology_agent) at
  `tuatha.agents.educational.*`
- The 4 BIEP hackathon features (marking_grader +
  adaptive_tutor + equivalency_generator +
  curriculum_change_sensor) at `tuatha.agents.hackathon.*`
- The 1 media_intel pipeline (the 10-tool ADK agent) at
  `tuatha.agents.media_intel.*`

The 7 orchestrator modules (this package):
- `tuatha.config` — LiteLLM + Langfuse + Cognee + Letta + BAML
  clients config
- `tuatha.routing` — the SubjectAgentWiring factory
- `tuatha.orchestrator` — the TuathaOrchestrator
- `tuatha.operator` — the CianfhoghlaimOperator
- `tuatha.cross_subject` — the cross-subject specialist
- `tuatha.workflows` — the 4 per-subject workflow handlers
"""
from __future__ import annotations

# Per the centralized-model-registry contract: every model
# string routes through MODEL_REGISTRY.resolve(family, role)
# — no hardcoded model strings.
try:
    from meaisinfhoghlaim.models import (  # type: ignore[import-not-found]
        MODEL_REGISTRY,
        model_for,
    )
except ImportError:
    MODEL_REGISTRY = None  # type: ignore[assignment, misc]
    model_for = None  # type: ignore[assignment, misc]

# Per the centralized-schema-registry contract: BAML is the
# single source of truth.
try:
    from baml_client import b  # type: ignore[import-not-found]
    _BAML_AVAILABLE = True
except ImportError:
    _BAML_AVAILABLE = False
    b = None  # type: ignore[assignment]

__all__ = [
    "MODEL_REGISTRY",
    "b",
    "model_for",
]


# Lazy-import pattern: the 4 agent types + the 7 orchestrator
# modules are NOT imported at package load time (per the
# BAML / model-registry graceful-degradation pattern). Callers
# use the explicit sub-imports:
#
#   from tuatha.subjects.mathematics import math_agent
#   from tuatha.agents.educational.academic_history_agent import academic_history_agent
#   from tuatha.agents.hackathon.marking_grader import marking_grader_agent
#   from tuatha.agents.media_intel.media_descriptor_agent import media_descriptor_agent
#   from tuatha.config import LiteLlmConfig, LangfuseConfig, CogneeConfig
#   from tuatha.routing import SubjectAgentWiring, build_wire
#   from tuatha.orchestrator import TuathaOrchestrator
#   from tuatha.operator import CianfhoghlaimOperator
#   from tuatha.cross_subject import cross_subject_agent
#   from tuatha.workflows import (
#       study_plan_workflow, exam_paper_workflow,
#       marking_scheme_workflow, curriculum_change_workflow,
#   )
