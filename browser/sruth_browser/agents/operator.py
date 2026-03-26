"""Operator Agent - Precision browser interactions using Stagehand.

The Operator is the second phase in the browsing pipeline.
It uses Stagehand's AI-powered interactions to:
- Click specific elements
- Fill form fields precisely
- Expand accordions and tabs
- Handle pagination
- Execute repetitive interaction sequences
"""

from typing import Any

from google.adk.agents import LlmAgent
from google.adk.tools import FunctionTool
from pydantic import BaseModel, Field

from ..backends import get_router
from ..browser_types import BackendType, BrowserOperation


class InteractionAction(BaseModel):
    """Model for browser interaction action."""

    action: str = Field(description="Action type: click, fill, scroll, hover, wait")
    target: str = Field(description="Natural language description of target element")
    value: str | None = Field(default=None, description="Value for fill actions")


class InteractionResult(BaseModel):
    """Model for interaction result."""

    success: bool
    action: str
    target: str | None = None
    screenshot_after: str | None = None
    error: str | None = None


async def perform_action(
    action: str,
    target: str,
    value: str | None = None,
) -> dict:
    """Perform a precise browser interaction.

    Uses Stagehand's AI-powered action execution for natural language
    element targeting.

    Args:
        action: Action type (click, fill, scroll, hover, press, wait)
        target: Natural language description of target element
        value: Optional value for fill/type actions

    Returns:
        Interaction result with success status
    """
    router = get_router()

    async def _interact(backend):
        result = await backend.interact(
            action=f"{action} on {target}" if action != "wait" else f"wait for {target}",
            selector=None,  # Use natural language
            value=value,
        )
        return {
            "success": result.success,
            "action": action,
            "target": target,
            "error": result.error,
        }

    return await router.execute_with_fallback(
        BrowserOperation.INTERACT,
        _interact,
    )


async def observe_elements(
    instruction: str,
) -> list[dict]:
    """Observe and identify interactive elements on the page.

    Returns elements matching the instruction with their descriptions
    and suggested actions.

    Args:
        instruction: What elements to look for

    Returns:
        List of observed elements with descriptions
    """
    router = get_router()

    # Try Stagehand first for observe capability
    stagehand = router.get_backend(BackendType.STAGEHAND_LOCAL)
    if stagehand and hasattr(stagehand, "observe"):
        return await stagehand.observe(instruction)

    # Try Browserbase
    browserbase = router.get_backend(BackendType.BROWSERBASE_MCP)
    if browserbase and hasattr(browserbase, "observe"):
        return await browserbase.observe(instruction)

    return []


async def execute_sequence(
    actions: list[dict],
) -> dict:
    """Execute a sequence of interactions in order.

    Useful for multi-step workflows like:
    - Pagination (click next, wait, extract)
    - Accordion expansion (click each section)
    - Tab navigation (click tab, wait for content)

    Args:
        actions: List of action dictionaries with 'action', 'target', 'value'

    Returns:
        Sequence execution result with per-action status
    """
    results = []

    for i, action_spec in enumerate(actions):
        result = await perform_action(
            action=action_spec.get("action", "click"),
            target=action_spec.get("target", ""),
            value=action_spec.get("value"),
        )
        results.append({
            "step": i + 1,
            **result,
        })

        if not result.get("success"):
            return {
                "success": False,
                "completed_steps": i,
                "total_steps": len(actions),
                "results": results,
                "error": f"Failed at step {i + 1}: {result.get('error')}",
            }

    return {
        "success": True,
        "completed_steps": len(actions),
        "total_steps": len(actions),
        "results": results,
    }


async def expand_all_content(
    expansion_pattern: str = "accordion",
) -> dict:
    """Expand all collapsible content on the page.

    Automatically finds and expands:
    - Accordions
    - Collapsible sections
    - "Show more" buttons
    - Read more links

    Args:
        expansion_pattern: Type of content to expand

    Returns:
        Expansion result with count of expanded items
    """
    router = get_router()

    # First observe expandable elements
    elements = await observe_elements(
        f"Find all collapsed or expandable {expansion_pattern} elements"
    )

    if not elements:
        return {
            "success": True,
            "expanded_count": 0,
            "message": "No expandable content found",
        }

    # Click each one
    expanded = 0
    for element in elements:
        result = await perform_action(
            action="click",
            target=element.get("description", str(element)),
        )
        if result.get("success"):
            expanded += 1

    return {
        "success": True,
        "expanded_count": expanded,
        "total_found": len(elements),
    }


async def paginate_and_collect(
    next_button: str,
    max_pages: int = 10,
    wait_time: float = 1.0,
) -> dict:
    """Navigate through paginated content.

    Clicks the next button repeatedly to load all pages.

    Args:
        next_button: Description of next page button
        max_pages: Maximum pages to navigate
        wait_time: Seconds to wait between pages

    Returns:
        Pagination result with page count
    """
    pages_visited = 0

    for _ in range(max_pages):
        # Check if next button exists
        elements = await observe_elements(next_button)
        if not elements:
            break

        # Click next
        result = await perform_action("click", next_button)
        if not result.get("success"):
            break

        # Wait for content
        await perform_action("wait", str(wait_time))
        pages_visited += 1

    return {
        "success": True,
        "pages_visited": pages_visited + 1,  # +1 for initial page
        "max_pages": max_pages,
    }


# Create function tools for ADK
action_tool = FunctionTool(perform_action)
observe_tool = FunctionTool(observe_elements)
sequence_tool = FunctionTool(execute_sequence)
expand_tool = FunctionTool(expand_all_content)
paginate_tool = FunctionTool(paginate_and_collect)

# Operator Agent Definition
operator_agent = LlmAgent(
    name="operator",
    model="gemini-2.0-flash",
    description="""Precision interaction agent for browser automation.

    Capabilities:
    - Click, fill, scroll, hover on specific elements
    - Observe and identify interactive elements
    - Execute multi-step interaction sequences
    - Expand collapsible content (accordions, tabs)
    - Handle pagination

    Use this agent when:
    - Specific UI elements need to be interacted with
    - Content is hidden behind clicks (accordions, tabs)
    - Pagination needs to be navigated
    - Form fields need precise filling
    """,
    instruction="""You are the Operator agent, specialized in precise browser interactions.

    Your role in the pipeline:
    1. Receive interaction tasks from Hunter or Orchestrator
    2. Observe page elements to understand the UI
    3. Execute precise interactions (click, fill, scroll)
    4. Handle dynamic content (expand, paginate)
    5. Prepare the page state for Gatherer extraction

    Guidelines:
    - Always observe elements before interacting
    - Use natural language to describe targets
    - For multi-step workflows, use execute_sequence
    - Expand all content before extraction
    - Report successful interactions and any failures

    Common patterns:
    - Accordion: observe -> click each header -> wait
    - Pagination: click next -> wait -> repeat
    - Forms: observe fields -> fill each -> submit
    """,
    tools=[action_tool, observe_tool, sequence_tool, expand_tool, paginate_tool],
    output_key="operator_result",
)
