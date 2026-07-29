"""
Celtic Education Agents — the 12-agent fleet.

Provides AI agents for the Celtic Education Platform, organized as
a 12-agent fleet spanning 5 frameworks (Custom + ADK + Agno +
Pipecat + CopilotKit).

Framework split:

- **Custom** (1): ``root_agent`` — the query router + orchestrator
- **ADK** (8): ``curriculum_agent`` + ``translation_agent`` +
  ``corpus_agent`` + ``research_agent`` + ``geospatial_agent`` +
  ``statistics_agent`` + ``curriculum_comparison_agent`` +
  ``mcp_curriculum_agent``
- **Agno** (3): ``education_research_agent`` +
  ``bunchloch_research_agent`` + ``agui_curriculum_agent``
- **Pipecat** (deferred — voice channel)
- **CopilotKit** (deferred — consumer agent)

Sub-packages:

- :mod:`agents.adk` — the 8 ADK agents + the canonical root_agent
- :mod:`agents.agno` — the 3 Agno agents + the EducationTeam
- :mod:`agents.tuatha` — the 8 NCCA subject specialists (gael +
  math + appm + chem + comp + engl + geog + hist)
- :mod:`agents.api` — the Hono API routes for the agent fleet
- :mod:`agents.tools` — the 9 tool modules (curriculum, corpus,
  geospatial, statistics, terminology, etc.)
- :mod:`agents.meaisinfhoghlaim` — the OCR/HTR/alignment sub-package

Centralized wiring (added by the
``2026-08-14-agents-fleet-wiring-parity-v1`` change):

- :mod:`agents.wiring` — ``AgentFleetWiring`` dataclass + ``wire_agent``
- :mod:`agents.agent_registry` — ``AGENT_REGISTRY`` dict (the single
  source of truth for the 12 main agents)
- :mod:`agents._workflow_handlers` — 4 shared async dispatchers
- :mod:`agents.observability_hooks` — the 5-layer observability
  wiring (Langfuse + Logfire + MLflow + RAGAS + structlog)
- :mod:`agents.memory_layer` — ``MemoryLayer`` Protocol + 5
  concrete backends (Cognee + Graphiti + LanceDB + FalkorDB +
  Memgraph)
- :mod:`agents.exceptions` — canonical ``AgentError`` hierarchy +
  ``with_retry`` decorator + ``graceful_degradation`` context
- :mod:`agents.pydantic_models` — standardized Pydantic v2 base
  models (``AgentRequest`` + ``AgentResponse`` + ``AgentContext``
  + ``AgentTrace``)

All agents integrate with:

- Langfuse (cost tracking) + Logfire (Python tracing) + MLflow
  (experiment tracking) + RAGAS (RAG evaluation) + structlog
  (structured JSON logging) — the 5-layer observability stack
- Cognee + Graphiti + LanceDB + FalkorDB + Memgraph — the
  5-backend memory stack
- Letta Cloud — conversation memory
"""
from __future__ import annotations

# ADK imports are optional (deprecated, migrating to Agno)
# Catch all exceptions since ADK has pydantic/validation issues with newer versions
try:
    from .adk.root_agent import (
        AgentContext,
        AgentDomain,
        AgentResponse,
        GeneralAgent,
        QueryRouter,
        RootAgent,
        create_root_agent,
    )
    _ADK_AVAILABLE = True
except Exception:
    _ADK_AVAILABLE = False
    RootAgent = None
    AgentContext = None
    AgentResponse = None
    AgentDomain = None
    QueryRouter = None
    GeneralAgent = None
    create_root_agent = None

# ROUTING_KEYWORDS lives in a standalone module so it can be imported
# independently of the (optional) ADK dependency. Used by the L5
# CelticAgentOpsComponent in cianfhoghlaim.orchestration/components/layer5_agent_ops.py
from .routing_keywords import ROUTING_KEYWORDS

# Agno team exports (primary framework)
# T4 (2026-07-09): wrap in try/except so importing
# `cianfhoghlaim.agents.tuatha.<slug>_agent` works in environments
# where `agno` is not installed (most CI runs). The Agno exports
# below the guard are `None` when agno is missing; consumers
# that NEED agno explicitly should call `from cianfhoghlaim.agents
# import _AGNO_AVAILABLE` first.
try:
    from .agno import (
        corpus_agent,
        curriculum_agent,
        education_team,
        geospatial_agent,
        research_agent,
        statistics_agent,
        translation_agent,
    )
    _AGNO_AVAILABLE = True
except Exception:
    _AGNO_AVAILABLE = False
    corpus_agent = None
    curriculum_agent = None
    education_team = None
    geospatial_agent = None
    research_agent = None
    statistics_agent = None
    translation_agent = None

# ---------------------------------------------------------------------------
# Centralized wiring (2026-08-14-agents-fleet-wiring-parity-v1).
# ---------------------------------------------------------------------------

# The single source of truth for the 12 main agents.
from .agent_registry import (
    AGENT_REGISTRY,
    FRAMEWORK_AVAILABLE,
    framework_summary,
    list_agent_names,
    register_agent,
    unregister_agent,
)

# The wiring dataclass + wire_agent function.
from .wiring import (
    AgentFleetWiring,
    AgentFramework,
    WireAgent,
    get_wiring,
    wire_agent,
    wiring_for_module_slug,
)

# The 4 shared async dispatchers.
from ._workflow_handlers import (
    LiteratureReviewQuery,
    ResearchQuery,
    StudyPlanContext,
    SummaryRequest,
    dispatch_deep_research,
    dispatch_literature_review,
    dispatch_study_plan,
    dispatch_summary,
)

# The 5-layer observability stack.
from .observability_hooks import (
    LangfuseLogger,
    LogfireSpan,
    MLflowTracker,
    RAGASScorer,
    attach_observability,
    structlogLogger,
    verify_5_layer_contract,
)

# The 5-backend memory layer.
from .memory_layer import (
    MEMORY_LAYERS,
    MemoryLayer,
    get_default_memory_layer,
    reset_default_memory_layer,
)

# The canonical exception hierarchy + retry + graceful degradation.
from .exceptions import (
    AgentConfigError,
    AgentDependencyMissingError,
    AgentError,
    AgentMemoryError,
    AgentObservabilityError,
    AgentRuntimeError,
    AgentTimeoutError,
    graceful_degradation,
    with_retry,
)

# The Pydantic v2 base models.
from .pydantic_models import (
    AgentContext as AgentContextModel,
    AgentRequest,
    AgentResponse as AgentResponseModel,
    AgentTrace,
)

__all__ = [
    # Original ADK exports
    "AgentContext",
    "AgentDomain",
    "AgentResponse",
    "GeneralAgent",
    "QueryRouter",
    # ADK Core agent classes (deprecated, optional)
    "RootAgent",
    "corpus_agent",
    "create_root_agent",
    "curriculum_agent",
    # Agno Team (primary)
    "education_team",
    "geospatial_agent",
    "research_agent",
    "statistics_agent",
    "translation_agent",
    # AGENT_REGISTRY (the 12 main agents)
    "AGENT_REGISTRY",
    "AgentFleetWiring",
    # Framework enum
    "AgentFramework",
    "WireAgent",
    # 4 dispatchers
    "LiteratureReviewQuery",
    "ResearchQuery",
    "StudyPlanContext",
    "SummaryRequest",
    "dispatch_deep_research",
    "dispatch_literature_review",
    "dispatch_study_plan",
    "dispatch_summary",
    # 5-layer observability
    "LangfuseLogger",
    "LogfireSpan",
    "MLflowTracker",
    "RAGASScorer",
    "attach_observability",
    "structlogLogger",
    "verify_5_layer_contract",
    # 5-backend memory
    "MEMORY_LAYERS",
    "MemoryLayer",
    "get_default_memory_layer",
    "reset_default_memory_layer",
    # Exceptions
    "AgentConfigError",
    "AgentDependencyMissingError",
    "AgentError",
    "AgentMemoryError",
    "AgentObservabilityError",
    "AgentRuntimeError",
    "AgentTimeoutError",
    "graceful_degradation",
    "with_retry",
    # Pydantic v2 base models
    "AgentContextModel",
    "AgentRequest",
    "AgentResponseModel",
    "AgentTrace",
    # Wiring helpers
    "FRAMEWORK_AVAILABLE",
    "framework_summary",
    "get_wiring",
    "list_agent_names",
    "register_agent",
    "unregister_agent",
    "wire_agent",
    "wiring_for_module_slug",
    # Routing keywords (T4 seed)
    "ROUTING_KEYWORDS",
]