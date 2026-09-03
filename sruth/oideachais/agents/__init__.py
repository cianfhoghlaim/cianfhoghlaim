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
        RootAgent,
        AgentContext,
        AgentResponse,
        AgentDomain,
        QueryRouter,
        GeneralAgent,
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

# Agno team exports (primary framework)
from .agno import (
    education_team,
    curriculum_agent,
    research_agent,
    translation_agent,
    corpus_agent,
    geospatial_agent,
    statistics_agent,
)

__all__ = [
    # Agno Team (primary)
    "education_team",
    "curriculum_agent",
    "research_agent",
    "translation_agent",
    "corpus_agent",
    "geospatial_agent",
    "statistics_agent",
    # ADK Core agent classes (deprecated, optional)
    "RootAgent",
    "AgentContext",
    "AgentResponse",
    "AgentDomain",
    "QueryRouter",
    "GeneralAgent",
    "create_root_agent",
]
