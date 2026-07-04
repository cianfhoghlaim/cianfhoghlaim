"""
Celtic Education Agents.

Provides AI agents for the Celtic Education Platform:

ADK-based agents (Google Agent Development Kit) - DEPRECATED:
- RootAgent: Unified orchestrator routing to specialized agents
- CurriculumAgent: Education content search and Q&A
- GeospatialAgent: Map queries and location search
- TranslationAgent: Celtic language translation
- CorpusAgent: Folklore and cultural content
- StatisticsAgent: Education statistics and comparisons
- ResearchAgent: Academic discovery with citation grounding

Agno-based agents (Multi-agent coordination) - ACTIVE:
- EducationTeam: Coordinated team with shared context
- Individual agents: curriculum, research, translation, corpus, geospatial, statistics

All agents integrate with:
- Datadog LLMObs for tracing
- Langfuse for cost tracking
- MLflow for experiments
- Kafka for event streaming
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
from .agno import (
    corpus_agent,
    curriculum_agent,
    education_team,
    geospatial_agent,
    research_agent,
    statistics_agent,
    translation_agent,
)

__all__ = [
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
]
