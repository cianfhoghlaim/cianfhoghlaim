"""Browser tool adapters for different agent frameworks.

Provides unified tool access for:
- Google ADK (native FunctionTool support)
- Agno (tool decorators)
- PydanticAI (Agent tools)

Usage:
    from sruth_browser.adapters import BrowserToolRegistry

    registry = BrowserToolRegistry()

    # Get tools for ADK
    adk_tools = registry.get_for_framework("adk")

    # Get tools for Agno
    agno_tools = registry.get_for_framework("agno")

    # Get tools for PydanticAI
    pydantic_tools = registry.get_for_framework("pydantic_ai")
"""

from .registry import BrowserToolRegistry

__all__ = [
    "BrowserToolRegistry",
]
