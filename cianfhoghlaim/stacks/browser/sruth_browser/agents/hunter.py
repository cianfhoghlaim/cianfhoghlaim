"""Hunter Agent - Vision-based semantic navigation using Skyvern.

The Hunter is the first phase in the browsing pipeline.
It uses Skyvern's vision-based navigation to:
- Navigate complex websites
- Handle legacy forms and dependent dropdowns
- Discover URLs and site structure
- Map navigation paths
"""

from typing import Literal

from google.adk.agents import LlmAgent
from google.adk.tools import FunctionTool
from pydantic import BaseModel, Field

from ..backends import get_router
from ..browser_types import BackendType, BrowserOperation


class NavigationGoal(BaseModel):
    """Model for navigation goal specification."""

    url: str = Field(description="Target URL to navigate to")
    goal: str = Field(description="Natural language description of navigation goal")
    expected_elements: list[str] = Field(
        default_factory=list,
        description="Elements expected on the target page",
    )


class NavigationResult(BaseModel):
    """Model for navigation result."""

    success: bool = Field(description="Whether navigation succeeded")
    final_url: str = Field(description="Final URL after navigation")
    page_title: str | None = Field(default=None, description="Page title")
    discovered_links: list[str] = Field(
        default_factory=list,
        description="Links discovered on the page",
    )
    error: str | None = Field(default=None, description="Error message if failed")


async def navigate_to_goal(
    url: str,
    goal: str,
    expected_elements: list[str] | None = None,
) -> dict:
    """Navigate to a URL with a specific goal using vision-based navigation.

    Uses Skyvern for complex navigation that requires understanding
    visual layout and semantics.

    Args:
        url: Target URL to navigate to
        goal: Natural language description of the navigation goal
        expected_elements: Optional list of elements expected on target page

    Returns:
        Navigation result with final URL and discovered links
    """
    router = get_router()

    async def _navigate(backend):
        # First navigate to the URL
        nav_result = await backend.navigate(url)
        if not nav_result.success:
            return {
                "success": False,
                "final_url": url,
                "error": nav_result.error,
            }

        # If we have a goal, use Skyvern's task-based navigation
        if goal and hasattr(backend, "fill_form"):
            # Skyvern can interpret goals
            pass

        return {
            "success": True,
            "final_url": nav_result.url,
            "page_title": nav_result.title,
            "discovered_links": [],
        }

    return await router.execute_with_fallback(
        BrowserOperation.NAVIGATE,
        _navigate,
    )


async def discover_site_structure(
    url: str,
    max_depth: int = 2,
) -> dict:
    """Discover the structure of a website.

    Maps out the navigation paths and key pages.

    Args:
        url: Starting URL
        max_depth: Maximum depth to crawl

    Returns:
        Site structure with pages and navigation paths
    """
    router = get_router()

    # Try to use Firecrawl's map endpoint first
    firecrawl = router.get_backend(BackendType.FIRECRAWL_MCP)
    if firecrawl and hasattr(firecrawl, "map_site"):
        links = await firecrawl.map_site(url, limit=100)
        return {
            "success": True,
            "url": url,
            "pages": links,
            "depth": max_depth,
        }

    # Fall back to basic navigation
    async def _discover(backend):
        nav_result = await backend.navigate(url)
        if not nav_result.success:
            return {"success": False, "url": url, "pages": [], "error": nav_result.error}

        # Extract links from page
        extract_result = await backend.extract(
            url,
            formats=["links"],
        )

        links = extract_result.content.get("links", [])
        return {
            "success": True,
            "url": url,
            "pages": [l.get("href") for l in links if isinstance(l, dict)],
            "depth": 1,
        }

    return await router.execute_with_fallback(
        BrowserOperation.NAVIGATE,
        _discover,
    )


async def handle_complex_form(
    url: str,
    form_goal: str,
    field_values: dict[str, str],
) -> dict:
    """Handle complex forms with dependent fields using vision-based automation.

    Skyvern excels at forms with:
    - Dependent dropdowns (selecting one changes others)
    - Dynamic field visibility
    - Ambiguous labels
    - Legacy form designs

    Args:
        url: URL containing the form
        form_goal: Natural language description of form submission goal
        field_values: Dictionary of field names/labels to values

    Returns:
        Form submission result
    """
    router = get_router()

    # Prefer Skyvern for complex forms
    async def _fill_form(backend):
        # Navigate first
        nav_result = await backend.navigate(url)
        if not nav_result.success:
            return {"success": False, "error": nav_result.error}

        # Use form filling
        result = await backend.fill_form(
            field_values,
            submit_selector=None,  # Let Skyvern find submit button
        )

        return {
            "success": result.success,
            "error": result.error,
        }

    return await router.execute_with_fallback(
        BrowserOperation.FORM,
        _fill_form,
    )


# Create function tools for ADK
navigate_tool = FunctionTool(navigate_to_goal)
discover_tool = FunctionTool(discover_site_structure)
form_tool = FunctionTool(handle_complex_form)

# Hunter Agent Definition
hunter_agent = LlmAgent(
    name="hunter",
    model="gemini-2.0-flash",
    description="""Vision-based navigation agent for complex websites.

    Capabilities:
    - Navigate to URLs with specific goals
    - Discover site structure and navigation paths
    - Handle complex forms with dependent fields
    - Map out website architecture

    Use this agent when:
    - Target page requires understanding visual layout
    - Forms have dynamic or dependent fields
    - Site structure needs to be mapped
    - Navigation requires semantic understanding
    """,
    instruction="""You are the Hunter agent, specialized in vision-based web navigation.

    Your role in the pipeline:
    1. Receive a navigation goal (URL + objective)
    2. Navigate to the target using semantic understanding
    3. Discover relevant pages and links
    4. Handle any complex forms encountered
    5. Report back discovered URLs and navigation results

    Guidelines:
    - Always start by navigating to the base URL
    - Use discover_site_structure for unfamiliar sites
    - For forms, use handle_complex_form with clear field descriptions
    - Report all discovered URLs for the Gatherer agent

    Output your navigation results clearly:
    - Final URL reached
    - Page title
    - Discovered links relevant to the goal
    - Any forms encountered and their status
    """,
    tools=[navigate_tool, discover_tool, form_tool],
    output_key="hunter_result",
)
