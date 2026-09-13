"""Orchestrator - Main browser agent pipeline.

Combines Hunter, Operator, Gatherer, and Evaluator agents into a
complete browsing pipeline using Google ADK's SequentialAgent and LoopAgent.
"""

from collections.abc import AsyncGenerator
from typing import Literal

from google.adk.agents import BaseAgent, LlmAgent, LoopAgent, SequentialAgent
from google.adk.agents.invocation_context import InvocationContext
from google.adk.events import Event, EventActions
from google.adk.tools import FunctionTool
from google.adk.tools.agent_tool import AgentTool
from pydantic import BaseModel, Field

from .evaluator import evaluator_agent
from .gatherer import gatherer_agent
from .hunter import hunter_agent
from .operator import operator_agent


class BrowsingTask(BaseModel):
    """Model for a complete browsing task."""

    url: str = Field(description="Target URL or starting point")
    goal: str = Field(description="What to accomplish")
    extraction_schema: dict | None = Field(
        default=None,
        description="Schema for structured extraction",
    )
    interaction_needed: bool = Field(
        default=False,
        description="Whether UI interactions are needed",
    )
    multiple_pages: bool = Field(
        default=False,
        description="Whether to crawl multiple pages",
    )


class BrowsingResult(BaseModel):
    """Model for browsing task result."""

    success: bool
    url: str
    content: dict | None = None
    quality_score: float | None = None
    backend_used: str | None = None
    error: str | None = None


class QualityChecker(BaseAgent):
    """Checks evaluation result and escalates to stop loop if quality passes."""

    def __init__(self, name: str = "quality_checker"):
        super().__init__(name=name)

    async def _run_async_impl(
        self, ctx: InvocationContext
    ) -> AsyncGenerator[Event, None]:
        evaluation = ctx.session.state.get("evaluator_result")

        if evaluation:
            grade = evaluation.get("grade") if isinstance(evaluation, dict) else getattr(evaluation, "grade", None)

            if grade == "pass":
                yield Event(
                    author=self.name,
                    actions=EventActions(escalate=True),
                )
                return

        # Continue loop if not passing
        yield Event(author=self.name)


class FallbackEscalator(BaseAgent):
    """Triggers fallback to paid services when quality fails."""

    def __init__(self, name: str = "fallback_escalator"):
        super().__init__(name=name)

    async def _run_async_impl(
        self, ctx: InvocationContext
    ) -> AsyncGenerator[Event, None]:
        evaluation = ctx.session.state.get("evaluator_result")

        if evaluation:
            should_fallback = (
                evaluation.get("should_fallback")
                if isinstance(evaluation, dict)
                else getattr(evaluation, "should_fallback", False)
            )

            if should_fallback:
                # Store fallback flag for next iteration
                ctx.session.state["use_fallback"] = True
                yield Event(
                    author=self.name,
                    content=f"Escalating to paid fallback due to quality issues",
                )
                return

        yield Event(author=self.name)


# Browsing pipeline combining all agents
browser_pipeline = SequentialAgent(
    name="browser_pipeline",
    description="""Complete browsing pipeline:
    1. Hunter navigates to target
    2. Operator handles interactions
    3. Gatherer extracts content
    4. Evaluator validates quality (loops if fails)
    """,
    sub_agents=[
        hunter_agent,
        operator_agent,
        gatherer_agent,
        LoopAgent(
            name="quality_loop",
            max_iterations=2,
            sub_agents=[
                evaluator_agent,
                QualityChecker(name="quality_checker"),
                FallbackEscalator(name="fallback_escalator"),
            ],
        ),
    ],
)


# Quick extraction without full pipeline
async def quick_extract(
    url: str,
    format: str = "markdown",
) -> dict:
    """Quick single-page extraction without full pipeline.

    For simple extractions where navigation and interaction aren't needed.

    Args:
        url: URL to extract from
        format: Output format (markdown, html, json)

    Returns:
        Extracted content
    """
    from .gatherer import extract_page
    return await extract_page(url, formats=[format])


async def research_topic(
    topic: str,
    max_sources: int = 10,
) -> dict:
    """Research a topic across multiple sources.

    Uses Gemini Deep Research (preferred) or Firecrawl's autonomous
    research agent as fallback.

    Args:
        topic: Research topic or question
        max_sources: Maximum sources to consult

    Returns:
        Research results with sources
    """
    from .gatherer import deep_research
    return await deep_research(topic, max_urls=max_sources)


async def deep_research_stream(
    topic: str,
    max_sources: int = 10,
) -> dict:
    """Stream a Gemini Deep Research session, yielding interactions.

    Used by the AG-UI adapter to stream Deep Research progress
    to CopilotKit consumers. Per the openspec change
    `2026-09-06-adk-gemini-deep-research-control-plane-v1`.

    Args:
        topic: Research topic or question
        max_sources: Maximum sources to consult

    Returns:
        Dict with ``interactions``, ``synthesized_report``, and
        ``backend_used`` keys.
    """
    from ..backends import get_router
    from ..browser_types import BackendType

    router = get_router()
    gemini_dr = router.get_backend(BackendType.GEMINI_DEEP_RESEARCH)
    if gemini_dr is None:
        raise RuntimeError("GeminiDeepResearchBackend not registered with router")

    interactions: list[dict] = []
    synthesized_chunks: list[str] = []
    async for event in gemini_dr.stream_interactions(topic, max_urls=max_sources):
        interactions.append(event)
        if event.get("kind") == "content_chunk" and event.get("text"):
            synthesized_chunks.append(event["text"])

    return {
        "success": True,
        "topic": topic,
        "interactions": interactions,
        "synthesized_report": "".join(synthesized_chunks),
        "backend_used": BackendType.GEMINI_DEEP_RESEARCH,
    }


async def interactive_browse(
    url: str,
    actions: list[dict],
) -> dict:
    """Perform interactive browsing with specified actions.

    Args:
        url: Starting URL
        actions: List of actions to perform

    Returns:
        Final page state after actions
    """
    from .hunter import navigate_to_goal
    from .operator import execute_sequence

    # Navigate first
    nav_result = await navigate_to_goal(url, goal="Navigate to page")

    if not nav_result.get("success"):
        return nav_result

    # Execute actions
    return await execute_sequence(actions)


# Create utility tools
quick_tool = FunctionTool(quick_extract)
research_tool = FunctionTool(research_topic)
deep_research_tool = FunctionTool(deep_research_stream)
interactive_tool = FunctionTool(interactive_browse)


# Root agent - main entry point
# Per the openspec change `2026-09-06-adk-gemini-deep-research-control-plane-v1`,
# the model is the `minimax` LiteLLM alias (7-tier fallback chain) instead of
# the hard-coded `gemini-2.0-flash`. The `gemini-deep-research` alias resolves
# to `gemini-2.5-pro-deep-research` via the canonical LiteLLM config.
root_agent = LlmAgent(
    name="browser_agent",
    model="minimax",
    description="""Intelligent browser automation agent.

    Capabilities:
    - Navigate websites with visual understanding
    - Extract content in various formats
    - Handle complex forms and interactions
    - Research topics across multiple sources (Gemini Deep Research preferred)
    - Quality-validated extraction with fallback

    Use for:
    - Web scraping and data extraction
    - Form automation
    - Research and information gathering
    - Interactive website testing
    """,
    instruction="""You are the Browser Agent, an intelligent web automation system.

    You have access to several specialized sub-agents and tools:

    **Full Pipeline (browser_pipeline)**:
    Use for complex tasks requiring navigation, interaction, and extraction.
    The pipeline automatically handles quality validation and fallback.

    **Quick Tools**:
    - quick_extract: Simple page extraction without navigation
    - research_topic: Deep research across multiple sources (prefers Gemini Deep Research)
    - deep_research_stream: Stream Gemini Deep Research interactions in real time
    - interactive_browse: Execute a sequence of browser actions

    **When to use what**:
    - Simple scraping: quick_extract
    - Need to click/fill: browser_pipeline or interactive_browse
    - Research question: research_topic
    - Streaming research: deep_research_stream
    - Complex multi-page: browser_pipeline

    Always report:
    - URLs visited
    - Content extracted
    - Quality assessment
    - Any errors encountered

    Be efficient:
    - Use quick_extract for single pages
    - Use batch operations when possible
    - Only use full pipeline when needed
    """,
    sub_agents=[browser_pipeline],
    tools=[
        quick_tool,
        research_tool,
        deep_research_tool,
        interactive_tool,
        AgentTool(browser_pipeline),
    ],
    output_key="final_result",
)
