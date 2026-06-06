"""
Agent Framework Router for Aleyum.

Provides intelligent routing between Google ADK (production sequential pipelines)
and Agno (multi-agent research teams) based on task characteristics.

Selection Criteria:
- ADK: Sequential pipelines, production tasks, single-agent work
- Agno: Research tasks, multi-source analysis, team coordination

Usage:
    router = AgentRouter()
    framework = router.select(task)
    result = await router.execute(task)
"""

import logging
from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional

logger = logging.getLogger(__name__)


class AgentFramework(Enum):
    """Available agent frameworks."""
    ADK = "adk"      # Google ADK - Sequential, production
    AGNO = "agno"    # Agno - Multi-team, research


@dataclass
class TaskCharacteristics:
    """
    Characteristics of a task used for framework selection.

    The router analyzes these characteristics to determine the best
    framework for execution.
    """
    # Core task properties
    description: str = ""
    task_type: str = "general"  # code_analysis, research, extraction, generation

    # Complexity indicators (0-1 scale)
    complexity: float = 0.5

    # Execution requirements
    requires_research: bool = False      # Multi-source analysis needed
    is_sequential: bool = True           # Linear pipeline vs parallel
    concurrency_needed: bool = False     # Multiple parallel agents
    requires_coordination: bool = False  # Agent-to-agent communication

    # Resource hints
    estimated_steps: int = 1
    tools_needed: List[str] = field(default_factory=list)

    # Override (if set, bypasses automatic selection)
    force_framework: Optional[AgentFramework] = None


@dataclass
class TaskResult:
    """Result from agent execution."""
    success: bool
    data: Any = None
    error: Optional[str] = None
    framework_used: AgentFramework = AgentFramework.ADK
    steps_completed: int = 0
    metadata: Dict[str, Any] = field(default_factory=dict)


class BaseAgentExecutor(ABC):
    """Base class for agent framework executors."""

    @abstractmethod
    async def execute(self, task: TaskCharacteristics) -> TaskResult:
        """Execute a task and return the result."""
        pass

    @abstractmethod
    def supports_task(self, task: TaskCharacteristics) -> bool:
        """Check if this executor supports the given task."""
        pass


class ADKExecutor(BaseAgentExecutor):
    """
    Google ADK executor for sequential production pipelines.

    Best for:
    - Linear multi-step workflows
    - Production deployments
    - Single-agent tasks with clear steps
    - Tool-heavy operations
    """

    async def execute(self, task: TaskCharacteristics) -> TaskResult:
        """Execute task using ADK sequential pipeline."""
        logger.info(f"ADK executing task: {task.description}")

        try:
            # ADK execution would be implemented here
            # For now, return a placeholder result
            return TaskResult(
                success=True,
                data={"message": "ADK execution placeholder"},
                framework_used=AgentFramework.ADK,
                steps_completed=task.estimated_steps,
                metadata={"executor": "adk", "task_type": task.task_type},
            )
        except Exception as e:
            logger.exception("ADK execution failed")
            return TaskResult(
                success=False,
                error=str(e),
                framework_used=AgentFramework.ADK,
            )

    def supports_task(self, task: TaskCharacteristics) -> bool:
        """ADK supports sequential, production tasks."""
        return task.is_sequential and not task.requires_coordination


class AgnoExecutor(BaseAgentExecutor):
    """
    Agno executor for multi-agent research teams.

    Best for:
    - Research and analysis tasks
    - Multi-source information gathering
    - Tasks requiring agent coordination
    - Complex, non-linear workflows
    """

    async def execute(self, task: TaskCharacteristics) -> TaskResult:
        """Execute task using Agno multi-agent team."""
        logger.info(f"Agno executing task: {task.description}")

        try:
            # Agno execution would be implemented here
            # For now, return a placeholder result
            return TaskResult(
                success=True,
                data={"message": "Agno execution placeholder"},
                framework_used=AgentFramework.AGNO,
                steps_completed=task.estimated_steps,
                metadata={"executor": "agno", "task_type": task.task_type},
            )
        except Exception as e:
            logger.exception("Agno execution failed")
            return TaskResult(
                success=False,
                error=str(e),
                framework_used=AgentFramework.AGNO,
            )

    def supports_task(self, task: TaskCharacteristics) -> bool:
        """Agno supports research and coordination tasks."""
        return task.requires_research or task.requires_coordination


def select_framework(task: TaskCharacteristics) -> AgentFramework:
    """
    Select the appropriate agent framework based on task characteristics.

    Selection Logic:
    1. If force_framework is set, use it
    2. If sequential and no research, use ADK
    3. If research or coordination needed, use Agno
    4. If high complexity (>0.5), prefer Agno
    5. Default to ADK for simple tasks

    Args:
        task: Task characteristics to analyze

    Returns:
        Selected AgentFramework
    """
    # Honor explicit override
    if task.force_framework:
        logger.info(f"Using forced framework: {task.force_framework}")
        return task.force_framework

    # ADK for production sequential pipelines
    if task.is_sequential and not task.requires_research:
        logger.info("Selected ADK: sequential, no research")
        return AgentFramework.ADK

    # Agno for research and multi-agent coordination
    if task.requires_research or task.concurrency_needed:
        logger.info("Selected Agno: research or concurrency needed")
        return AgentFramework.AGNO

    # Agno for coordination requirements
    if task.requires_coordination:
        logger.info("Selected Agno: coordination required")
        return AgentFramework.AGNO

    # High complexity tasks benefit from Agno's team approach
    if task.complexity > 0.5:
        logger.info(f"Selected Agno: high complexity ({task.complexity})")
        return AgentFramework.AGNO

    # Default to ADK for simple tasks
    logger.info("Selected ADK: default for simple tasks")
    return AgentFramework.ADK


class AgentRouter:
    """
    Routes tasks to the appropriate agent framework.

    The router maintains executors for each framework and handles
    task analysis, framework selection, and execution.

    Usage:
        router = AgentRouter()

        # Analyze task and get recommendation
        task = TaskCharacteristics(
            description="Analyze codebase and generate documentation",
            requires_research=True,
            complexity=0.7,
        )
        framework = router.select(task)

        # Execute with selected framework
        result = await router.execute(task)
    """

    def __init__(self):
        """Initialize router with framework executors."""
        self._executors: Dict[AgentFramework, BaseAgentExecutor] = {
            AgentFramework.ADK: ADKExecutor(),
            AgentFramework.AGNO: AgnoExecutor(),
        }

    def select(self, task: TaskCharacteristics) -> AgentFramework:
        """
        Select the best framework for a task.

        Args:
            task: Task to analyze

        Returns:
            Selected AgentFramework
        """
        return select_framework(task)

    async def execute(
        self,
        task: TaskCharacteristics,
        framework: Optional[AgentFramework] = None,
    ) -> TaskResult:
        """
        Execute a task using the appropriate framework.

        Args:
            task: Task to execute
            framework: Optional override for framework selection

        Returns:
            TaskResult from execution
        """
        # Select framework if not provided
        if framework is None:
            framework = self.select(task)

        executor = self._executors[framework]

        if not executor.supports_task(task):
            logger.warning(
                f"Framework {framework} may not optimally support this task type"
            )

        return await executor.execute(task)

    def register_executor(
        self,
        framework: AgentFramework,
        executor: BaseAgentExecutor,
    ) -> None:
        """
        Register a custom executor for a framework.

        Args:
            framework: Framework to register for
            executor: Executor instance
        """
        self._executors[framework] = executor


# Task type presets for common scenarios
def create_code_analysis_task(
    description: str,
    **kwargs: Any,
) -> TaskCharacteristics:
    """Create a task optimized for code analysis."""
    return TaskCharacteristics(
        description=description,
        task_type="code_analysis",
        is_sequential=True,
        complexity=0.4,
        tools_needed=["codeolas", "chunkhound"],
        **kwargs,
    )


def create_research_task(
    description: str,
    **kwargs: Any,
) -> TaskCharacteristics:
    """Create a task optimized for research."""
    return TaskCharacteristics(
        description=description,
        task_type="research",
        requires_research=True,
        is_sequential=False,
        concurrency_needed=True,
        complexity=0.7,
        tools_needed=["firecrawl", "cognee", "qdrant"],
        **kwargs,
    )


def create_extraction_task(
    description: str,
    **kwargs: Any,
) -> TaskCharacteristics:
    """Create a task optimized for data extraction."""
    return TaskCharacteristics(
        description=description,
        task_type="extraction",
        is_sequential=True,
        complexity=0.3,
        tools_needed=["firecrawl", "browserbase"],
        **kwargs,
    )
