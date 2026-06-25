"""
Agent orchestration utilities for Aleyum.

Provides a router for selecting between Google ADK (sequential, production)
and Agno (multi-team, research) frameworks based on task characteristics.
"""

from .router import (
    ADKExecutor,
    AgentFramework,
    AgentRouter,
    AgnoExecutor,
    BaseAgentExecutor,
    TaskCharacteristics,
    TaskResult,
    create_code_analysis_task,
    create_extraction_task,
    create_research_task,
    select_framework,
)

__all__ = [
    "AgentFramework",
    "AgentRouter",
    "TaskCharacteristics",
    "TaskResult",
    "BaseAgentExecutor",
    "ADKExecutor",
    "AgnoExecutor",
    "select_framework",
    "create_code_analysis_task",
    "create_research_task",
    "create_extraction_task",
]
