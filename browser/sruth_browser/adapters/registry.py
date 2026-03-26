"""Unified tool registry for browser operations.

Provides a single source of truth for all browser operations,
adaptable to different agent frameworks.
"""

from typing import Any, Callable, Literal

from ..tools import (
    # Navigation
    navigate,
    go_back,
    go_forward,
    reload,
    click_coordinates,
    scroll_to_coordinates,
    hover_coordinates,
    # Extraction
    extract_page,
    extract_structured,
    batch_extract,
    # Screenshot
    capture_screenshot,
    analyze_screenshot,
    # Forms
    fill_form,
    submit_form,
    # Research
    deep_research,
    map_site,
    # Approval
    request_approval,
    handle_approval,
    get_pending_approvals,
    cancel_approval,
    wait_for_approval,
    # Z.AI Vision
    visual_grounding,
    analyze_vision,
    compare_ui_images,
    ui_to_code,
    ui_to_prompt,
    ui_to_spec,
    extract_text_ocr,
    diagnose_error,
    understand_diagram,
    analyze_chart,
    ui_diff,
    analyze_video,
    # Z.AI MCP
    web_search_prime,
    web_reader,
    search_github_docs,
    get_github_repo_structure,
    read_github_file,
)


class ToolDefinition:
    """Definition of a browser tool for adaptation to frameworks."""

    def __init__(
        self,
        name: str,
        func: Callable,
        description: str,
        category: str,
    ):
        self.name = name
        self.func = func
        self.description = description
        self.category = category


# Tool definitions with categories
TOOL_DEFINITIONS: list[ToolDefinition] = [
    # Navigation
    ToolDefinition(
        "browser.navigate",
        navigate,
        "Navigate to a URL",
        "navigation",
    ),
    ToolDefinition(
        "browser.go_back",
        go_back,
        "Go back in browser history",
        "navigation",
    ),
    ToolDefinition(
        "browser.go_forward",
        go_forward,
        "Go forward in browser history",
        "navigation",
    ),
    ToolDefinition(
        "browser.reload",
        reload,
        "Reload the current page",
        "navigation",
    ),
    ToolDefinition(
        "browser.click",
        click_coordinates,
        "Click at specific coordinates",
        "navigation",
    ),
    ToolDefinition(
        "browser.scroll",
        scroll_to_coordinates,
        "Scroll to specific coordinates",
        "navigation",
    ),
    ToolDefinition(
        "browser.hover",
        hover_coordinates,
        "Hover at specific coordinates",
        "navigation",
    ),
    # Extraction
    ToolDefinition(
        "browser.extract",
        extract_page,
        "Extract content from a web page",
        "extraction",
    ),
    ToolDefinition(
        "browser.extract_structured",
        extract_structured,
        "Extract structured data according to a JSON schema",
        "extraction",
    ),
    ToolDefinition(
        "browser.batch_extract",
        batch_extract,
        "Extract content from multiple URLs concurrently",
        "extraction",
    ),
    # Screenshot
    ToolDefinition(
        "browser.screenshot",
        capture_screenshot,
        "Capture a screenshot of the page",
        "screenshot",
    ),
    ToolDefinition(
        "browser.analyze_screenshot",
        analyze_screenshot,
        "Analyze a screenshot using vision",
        "screenshot",
    ),
    # Forms
    ToolDefinition(
        "browser.fill_form",
        fill_form,
        "Fill form fields",
        "forms",
    ),
    ToolDefinition(
        "browser.submit_form",
        submit_form,
        "Submit a form",
        "forms",
    ),
    # Research
    ToolDefinition(
        "browser.research",
        deep_research,
        "Perform deep research on a topic across multiple pages",
        "research",
    ),
    ToolDefinition(
        "browser.map_site",
        map_site,
        "Discover and map URLs on a website",
        "research",
    ),
    # Approval (Human-in-the-Loop)
    ToolDefinition(
        "browser.request_approval",
        request_approval,
        "Request human approval before proceeding",
        "approval",
    ),
    ToolDefinition(
        "browser.handle_approval",
        handle_approval,
        "Handle an approval response",
        "approval",
    ),
    ToolDefinition(
        "browser.get_pending_approvals",
        get_pending_approvals,
        "Get list of pending approval requests",
        "approval",
    ),
    ToolDefinition(
        "browser.cancel_approval",
        cancel_approval,
        "Cancel a pending approval request",
        "approval",
    ),
    ToolDefinition(
        "browser.wait_for_approval",
        wait_for_approval,
        "Wait for human approval with timeout",
        "approval",
    ),
    # Z.AI Vision
    ToolDefinition(
        "vision.grounding",
        visual_grounding,
        "Use GLM-4.6v for visual grounding - find elements by description",
        "vision",
    ),
    ToolDefinition(
        "vision.analyze",
        analyze_vision,
        "Analyze an image using vision AI",
        "vision",
    ),
    ToolDefinition(
        "vision.compare_ui",
        compare_ui_images,
        "Compare two UI images for differences",
        "vision",
    ),
    ToolDefinition(
        "vision.ui_to_code",
        ui_to_code,
        "Generate code from a UI screenshot",
        "vision",
    ),
    ToolDefinition(
        "vision.ui_to_prompt",
        ui_to_prompt,
        "Generate AI prompt to recreate UI",
        "vision",
    ),
    ToolDefinition(
        "vision.ui_to_spec",
        ui_to_spec,
        "Generate design specification from UI",
        "vision",
    ),
    ToolDefinition(
        "vision.ocr",
        extract_text_ocr,
        "Extract text from image using OCR",
        "vision",
    ),
    ToolDefinition(
        "vision.diagnose_error",
        diagnose_error,
        "Diagnose error from screenshot",
        "vision",
    ),
    ToolDefinition(
        "vision.understand_diagram",
        understand_diagram,
        "Understand a technical diagram",
        "vision",
    ),
    ToolDefinition(
        "vision.analyze_chart",
        analyze_chart,
        "Analyze a chart or graph",
        "vision",
    ),
    ToolDefinition(
        "vision.ui_diff",
        ui_diff,
        "Compare expected vs actual UI",
        "vision",
    ),
    ToolDefinition(
        "vision.analyze_video",
        analyze_video,
        "Analyze video content",
        "vision",
    ),
    # Z.AI MCP
    ToolDefinition(
        "zai.web_search",
        web_search_prime,
        "Search the web using Z.AI",
        "zai",
    ),
    ToolDefinition(
        "zai.web_reader",
        web_reader,
        "Read and summarize web content",
        "zai",
    ),
    ToolDefinition(
        "zai.search_github",
        search_github_docs,
        "Search GitHub documentation",
        "zai",
    ),
    ToolDefinition(
        "zai.github_structure",
        get_github_repo_structure,
        "Get GitHub repository structure",
        "zai",
    ),
    ToolDefinition(
        "zai.read_github_file",
        read_github_file,
        "Read a file from GitHub repository",
        "zai",
    ),
]


class BrowserToolRegistry:
    """Unified registry for browser tools across frameworks.

    Usage:
        registry = BrowserToolRegistry()

        # Get all tools for a framework
        tools = registry.get_for_framework("adk")

        # Get tools by category
        nav_tools = registry.get_by_category("navigation")

        # Get a specific tool
        extract = registry.get_tool("browser.extract")
    """

    def __init__(self):
        self._tools: dict[str, ToolDefinition] = {
            t.name: t for t in TOOL_DEFINITIONS
        }

    def get_tool(self, name: str) -> ToolDefinition | None:
        """Get a tool by name."""
        return self._tools.get(name)

    def get_by_category(self, category: str) -> list[ToolDefinition]:
        """Get all tools in a category."""
        return [t for t in self._tools.values() if t.category == category]

    def list_categories(self) -> list[str]:
        """List all available categories."""
        return list(set(t.category for t in self._tools.values()))

    def list_tools(self) -> list[str]:
        """List all tool names."""
        return list(self._tools.keys())

    def get_for_framework(
        self,
        framework: Literal["adk", "agno", "pydantic_ai", "raw"],
        categories: list[str] | None = None,
    ) -> list[Any]:
        """Get tools adapted for a specific framework.

        Args:
            framework: Target framework
            categories: Optional list of categories to include

        Returns:
            List of tools in framework-specific format
        """
        tools = list(self._tools.values())
        if categories:
            tools = [t for t in tools if t.category in categories]

        if framework == "raw":
            return [t.func for t in tools]
        elif framework == "adk":
            return self._adapt_for_adk(tools)
        elif framework == "agno":
            return self._adapt_for_agno(tools)
        elif framework == "pydantic_ai":
            return self._adapt_for_pydantic_ai(tools)
        else:
            raise ValueError(f"Unknown framework: {framework}")

    def _adapt_for_adk(self, tools: list[ToolDefinition]) -> list[Any]:
        """Adapt tools for Google ADK."""
        try:
            from google.adk.tools import FunctionTool
            return [FunctionTool(t.func) for t in tools]
        except ImportError:
            # Return raw functions if ADK not installed
            return [t.func for t in tools]

    def _adapt_for_agno(self, tools: list[ToolDefinition]) -> list[Any]:
        """Adapt tools for Agno.

        Agno uses function tools directly with @tool decorator or via Function.
        """
        try:
            from agno.tools.function import Function
            return [
                Function(
                    name=t.name.replace(".", "_"),
                    entrypoint=t.func,
                    description=t.description,
                )
                for t in tools
            ]
        except ImportError:
            # Return raw functions if Agno not installed
            return [t.func for t in tools]

    def _adapt_for_pydantic_ai(self, tools: list[ToolDefinition]) -> list[Any]:
        """Adapt tools for PydanticAI.

        PydanticAI uses Tool or plain callables.
        """
        try:
            from pydantic_ai import Tool
            return [
                Tool(
                    function=t.func,
                    name=t.name.replace(".", "_"),
                    description=t.description,
                )
                for t in tools
            ]
        except ImportError:
            # Return raw functions if PydanticAI not installed
            return [t.func for t in tools]


# Default registry instance
_default_registry: BrowserToolRegistry | None = None


def get_registry() -> BrowserToolRegistry:
    """Get the default tool registry instance."""
    global _default_registry
    if _default_registry is None:
        _default_registry = BrowserToolRegistry()
    return _default_registry
