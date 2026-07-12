"""Durable Orchestrator - Restate-backed browser agent pipeline.

Wraps the standard browser pipeline with Restate durable execution,
providing:
- Checkpointing between Hunter/Operator/Gatherer/Evaluator
- Resume from any point after crashes/restarts
- Human-in-the-loop approval for risky operations
- Journaled state for circuit breaker decisions
- Parallel execution with gather/select patterns
"""

import uuid
from collections.abc import AsyncGenerator
from dataclasses import dataclass
from datetime import timedelta
from typing import Any

import structlog
from google.adk.agents import BaseAgent
from google.adk.agents.invocation_context import InvocationContext
from google.adk.events import Event, EventActions
from pydantic import BaseModel, Field

from ..config import get_config
from ..core import RestateContext, get_restate_plugin, init_restate
from .evaluator import evaluator_agent
from .gatherer import gatherer_agent
from .hunter import hunter_agent
from .operator import operator_agent
from .orchestrator import BrowsingResult, BrowsingTask

logger = structlog.get_logger()


class DurableTask(BaseModel):
    """Enhanced task model with durability metadata."""

    task_id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    url: str = Field(description="Target URL")
    goal: str = Field(description="What to accomplish")
    extraction_schema: dict | None = Field(default=None)
    interaction_needed: bool = Field(default=False)
    multiple_pages: bool = Field(default=False)
    requires_approval: bool = Field(
        default=False,
        description="Whether to request human approval before execution",
    )
    resume_from: str | None = Field(
        default=None,
        description="Step name to resume from (if resuming)",
    )
    max_retries: int = Field(default=3)


class PipelineCheckpoint(BaseModel):
    """Checkpoint state between pipeline steps."""

    step: str
    task_id: str
    timestamp: float
    input_data: dict[str, Any] | None = None
    output_data: dict[str, Any] | None = None
    error: str | None = None
    attempt: int = 1


@dataclass
class AgentStep:
    """Represents a step in the durable pipeline."""

    name: str
    agent: BaseAgent
    requires_approval: bool = False


class DurableOrchestrator(BaseAgent):
    """Orchestrator with Restate durable execution.

    Each step in the pipeline is checkpointed. If the process crashes,
    execution resumes from the last successful checkpoint.

    Human approval can be required for sensitive operations via
    Restate awakeables.
    """

    def __init__(
        self,
        name: str = "durable_orchestrator",
        max_quality_retries: int = 2,
    ):
        super().__init__(name=name)
        self.max_quality_retries = max_quality_retries
        self.config = get_config()

        # Define pipeline steps with approval requirements
        self.steps = [
            AgentStep(name="hunter", agent=hunter_agent),
            AgentStep(name="operator", agent=operator_agent),
            AgentStep(name="gatherer", agent=gatherer_agent, requires_approval=True),
            AgentStep(name="evaluator", agent=evaluator_agent),
        ]

    async def _run_async_impl(
        self,
        ctx: InvocationContext,
    ) -> AsyncGenerator[Event, None]:
        """Execute the durable pipeline with checkpointing."""
        task_data = ctx.session.state.get("task", {})
        task = DurableTask(**task_data) if task_data else None

        if not task:
            yield Event(
                author=self.name,
                content="No task provided",
                actions=EventActions(escalate=True),
            )
            return

        # Initialize Restate plugin
        plugin = get_restate_plugin()
        if self.config.has_restate:
            await init_restate()

        # Create execution context
        restate_ctx = plugin.create_context(
            workflow_id=f"browsing_{task.task_id}",
        )

        logger.info(
            "durable_pipeline_started",
            task_id=task.task_id,
            url=task.url,
            resume_from=task.resume_from,
        )

        yield Event(
            author=self.name,
            content=f"Starting durable pipeline for {task.url}",
        )

        try:
            # Execute pipeline with checkpoints
            result = await self._execute_pipeline(ctx, task, restate_ctx, plugin)

            # Store final result
            ctx.session.state["final_result"] = result.model_dump()

            yield Event(
                author=self.name,
                content=f"Pipeline completed: {result.success}",
                actions=EventActions(escalate=True),
            )

        except Exception as e:
            logger.error(
                "durable_pipeline_failed",
                task_id=task.task_id,
                error=str(e),
            )

            yield Event(
                author=self.name,
                content=f"Pipeline failed: {e}",
                actions=EventActions(escalate=True),
            )

    async def _execute_pipeline(
        self,
        ctx: InvocationContext,
        task: DurableTask,
        restate_ctx: RestateContext,
        plugin,
    ) -> BrowsingResult:
        """Execute all pipeline steps with checkpointing."""
        # Determine starting point
        start_step = 0
        if task.resume_from:
            for i, step in enumerate(self.steps):
                if step.name == task.resume_from:
                    start_step = i
                    break
            logger.info("resuming_from_step", step=task.resume_from)

        # Store task in context
        ctx.session.state["task_url"] = task.url
        ctx.session.state["task_goal"] = task.goal
        ctx.session.state["extraction_schema"] = task.extraction_schema

        # Execute steps
        for i, step in enumerate(self.steps[start_step:], start=start_step):
            # Check if approval is needed
            if step.requires_approval and task.requires_approval:
                approved = await plugin.request_approval(
                    session_id=task.task_id,
                    action=f"Execute {step.name} step for {task.url}",
                    details={
                        "step": step.name,
                        "url": task.url,
                        "goal": task.goal,
                    },
                )

                if not approved:
                    logger.warning("step_rejected", step=step.name)
                    return BrowsingResult(
                        success=False,
                        url=task.url,
                        error=f"Human rejected {step.name} step",
                    )

            # Execute step with checkpoint
            step_result = await restate_ctx.run(
                step_name=step.name,
                action=lambda: self._execute_step(ctx, step, task),
            )

            # Store step result in session
            ctx.session.state[f"{step.name}_result"] = step_result

            # Store checkpoint
            restate_ctx.set(
                f"checkpoint_{step.name}",
                {
                    "step": step.name,
                    "task_id": task.task_id,
                    "result": step_result,
                },
            )

            logger.info(
                "step_completed",
                step=step.name,
                success=step_result.get("success", True),
            )

        # Quality retry loop
        for attempt in range(self.max_quality_retries):
            restate_ctx.set("quality_attempt", attempt)

            evaluation = ctx.session.state.get("evaluator_result", {})
            grade = (
                evaluation.get("grade")
                if isinstance(evaluation, dict)
                else getattr(evaluation, "grade", None)
            )

            if grade == "pass":
                logger.info("quality_passed", attempt=attempt)
                break

            if attempt < self.max_quality_retries - 1:
                # Escalate to fallback
                logger.info("escalating_to_fallback", attempt=attempt)
                ctx.session.state["use_fallback"] = True

                # Re-run gatherer with fallback
                await restate_ctx.run(
                    step_name=f"fallback_gather_{attempt}",
                    action=lambda: self._execute_step(
                        ctx,
                        AgentStep(name="gatherer", agent=gatherer_agent),
                        task,
                    ),
                )

                # Re-evaluate
                await restate_ctx.run(
                    step_name=f"fallback_evaluate_{attempt}",
                    action=lambda: self._execute_step(
                        ctx,
                        AgentStep(name="evaluator", agent=evaluator_agent),
                        task,
                    ),
                )

        # Build final result
        gatherer_result = ctx.session.state.get("gatherer_result", {})
        evaluator_result = ctx.session.state.get("evaluator_result", {})

        return BrowsingResult(
            success=evaluator_result.get("grade") == "pass",
            url=task.url,
            content=gatherer_result.get("content"),
            quality_score=evaluator_result.get("score"),
            backend_used=gatherer_result.get("backend"),
            error=evaluator_result.get("error"),
        )

    async def _execute_step(
        self,
        ctx: InvocationContext,
        step: AgentStep,
        task: DurableTask,
    ) -> dict[str, Any]:
        """Execute a single pipeline step."""
        try:
            # Run the agent
            async for event in step.agent._run_async_impl(ctx):
                pass  # Consume events

            # Get result from session state
            result_key = f"{step.name}_result"
            result = ctx.session.state.get(result_key, {})

            return {"success": True, **result} if isinstance(result, dict) else {"success": True}

        except Exception as e:
            logger.error("step_failed", step=step.name, error=str(e))
            return {"success": False, "error": str(e)}


class ParallelExtractor(BaseAgent):
    """Extract from multiple URLs in parallel using Restate gather.

    Respects rate limits and provides checkpointing for each URL.
    """

    def __init__(
        self,
        name: str = "parallel_extractor",
        max_parallel: int = 5,
    ):
        super().__init__(name=name)
        self.max_parallel = max_parallel

    async def _run_async_impl(
        self,
        ctx: InvocationContext,
    ) -> AsyncGenerator[Event, None]:
        """Extract from multiple URLs in parallel."""
        urls = ctx.session.state.get("urls", [])

        if not urls:
            yield Event(
                author=self.name,
                content="No URLs provided for parallel extraction",
            )
            return

        config = get_config()
        plugin = get_restate_plugin()

        # Create execution context
        restate_ctx = plugin.create_context(
            workflow_id=f"parallel_extract_{uuid.uuid4()}",
        )

        yield Event(
            author=self.name,
            content=f"Extracting from {len(urls)} URLs in parallel",
        )

        # Process in batches
        results = []
        for i in range(0, len(urls), self.max_parallel):
            batch = urls[i : i + self.max_parallel]

            batch_results = await restate_ctx.run(
                step_name=f"batch_{i // self.max_parallel}",
                action=lambda: self._extract_batch(ctx, batch),
            )

            results.extend(batch_results)

            yield Event(
                author=self.name,
                content=f"Completed batch {i // self.max_parallel + 1}",
            )

        # Store results
        ctx.session.state["extraction_results"] = results

        yield Event(
            author=self.name,
            content=f"Parallel extraction complete: {len(results)} results",
            actions=EventActions(escalate=True),
        )

    async def _extract_batch(
        self,
        ctx: InvocationContext,
        urls: list[str],
    ) -> list[dict[str, Any]]:
        """Extract from a batch of URLs concurrently."""
        import asyncio
        from .gatherer import extract_page

        tasks = [extract_page(url) for url in urls]
        results = await asyncio.gather(*tasks, return_exceptions=True)

        processed = []
        for url, result in zip(urls, results):
            if isinstance(result, Exception):
                processed.append({"url": url, "success": False, "error": str(result)})
            else:
                processed.append({"url": url, "success": True, **result})

        return processed


class BackendRacer(BaseAgent):
    """Race multiple backends using Restate select pattern.

    Returns the first successful result, cancelling others.
    """

    def __init__(self, name: str = "backend_racer"):
        super().__init__(name=name)

    async def _run_async_impl(
        self,
        ctx: InvocationContext,
    ) -> AsyncGenerator[Event, None]:
        """Race backends and return first success."""
        url = ctx.session.state.get("target_url")

        if not url:
            yield Event(
                author=self.name,
                content="No URL provided for backend racing",
            )
            return

        yield Event(
            author=self.name,
            content=f"Racing backends for {url}",
        )

        result = await self._race_backends(url)

        ctx.session.state["race_result"] = result

        yield Event(
            author=self.name,
            content=f"Winner: {result.get('backend', 'unknown')}",
            actions=EventActions(escalate=True),
        )

    async def _race_backends(self, url: str) -> dict[str, Any]:
        """Race self-hosted vs paid backends."""
        import asyncio

        from ..backends import get_router

        router = get_router()

        # Create extraction tasks for each backend
        async def try_backend(backend_type):
            try:
                backend = router.get_backend(backend_type)
                if not backend:
                    return None
                result = await backend.extract(url)
                if result.success:
                    return {
                        "success": True,
                        "backend": backend_type.value,
                        "content": result.content,
                    }
                return None
            except Exception:
                return None

        from ..browser_types import BackendType

        # Race all available backends
        backends = [
            BackendType.CRAWL4AI_LOCAL,
            BackendType.FIRECRAWL_MCP,
            BackendType.BROWSERBASE_MCP,
        ]

        tasks = [try_backend(bt) for bt in backends]

        # Wait for first success
        done, pending = await asyncio.wait(
            [asyncio.create_task(t) for t in tasks],
            return_when=asyncio.FIRST_COMPLETED,
        )

        # Cancel pending tasks
        for task in pending:
            task.cancel()

        # Get result
        for task in done:
            result = task.result()
            if result and result.get("success"):
                return result

        return {"success": False, "error": "All backends failed"}


# Create the durable orchestrator instance
durable_orchestrator = DurableOrchestrator()
parallel_extractor = ParallelExtractor()
backend_racer = BackendRacer()
