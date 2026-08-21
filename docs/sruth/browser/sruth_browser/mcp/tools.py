"""MCP tool definitions for browser agent."""

from typing import Any

# MCP tool schemas
BROWSER_TOOLS = [
    {
        "name": "browser_extract",
        "description": "Extract content from a web page. Supports markdown, HTML, links, and structured JSON extraction.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "url": {
                    "type": "string",
                    "description": "URL to extract content from",
                },
                "formats": {
                    "type": "array",
                    "items": {"type": "string", "enum": ["markdown", "html", "links", "json", "screenshot"]},
                    "default": ["markdown"],
                    "description": "Output formats to return",
                },
                "prompt": {
                    "type": "string",
                    "description": "Optional LLM prompt for intelligent extraction",
                },
                "schema": {
                    "type": "object",
                    "description": "Optional JSON schema for structured extraction",
                },
            },
            "required": ["url"],
        },
    },
    {
        "name": "browser_navigate",
        "description": "Navigate to a URL and return page info.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "url": {
                    "type": "string",
                    "description": "URL to navigate to",
                },
                "waitUntil": {
                    "type": "string",
                    "enum": ["load", "domcontentloaded", "networkidle"],
                    "default": "load",
                    "description": "When to consider navigation complete",
                },
            },
            "required": ["url"],
        },
    },
    {
        "name": "browser_screenshot",
        "description": "Capture a screenshot of a web page.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "url": {
                    "type": "string",
                    "description": "URL to screenshot",
                },
                "fullPage": {
                    "type": "boolean",
                    "default": False,
                    "description": "Capture the full scrollable page",
                },
                "selector": {
                    "type": "string",
                    "description": "CSS selector to screenshot specific element",
                },
            },
            "required": ["url"],
        },
    },
    {
        "name": "browser_interact",
        "description": "Perform a browser interaction (click, fill, scroll, etc.).",
        "inputSchema": {
            "type": "object",
            "properties": {
                "action": {
                    "type": "string",
                    "description": "Action to perform or natural language instruction",
                },
                "selector": {
                    "type": "string",
                    "description": "CSS selector for target element",
                },
                "value": {
                    "type": "string",
                    "description": "Value for fill/type actions",
                },
            },
            "required": ["action"],
        },
    },
    {
        "name": "browser_research",
        "description": "Perform deep research on a topic across multiple web sources.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "topic": {
                    "type": "string",
                    "description": "Research topic or question",
                },
                "maxSources": {
                    "type": "integer",
                    "default": 15,
                    "description": "Maximum number of sources to consult",
                },
                "schema": {
                    "type": "object",
                    "description": "Optional schema for structured output",
                },
            },
            "required": ["topic"],
        },
    },
    {
        "name": "browser_map_site",
        "description": "Discover all URLs on a website.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "url": {
                    "type": "string",
                    "description": "Starting URL to map",
                },
                "search": {
                    "type": "string",
                    "description": "Optional search term to filter URLs",
                },
                "limit": {
                    "type": "integer",
                    "default": 100,
                    "description": "Maximum URLs to return",
                },
            },
            "required": ["url"],
        },
    },
    {
        "name": "browser_fill_form",
        "description": "Fill and optionally submit a form.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "url": {
                    "type": "string",
                    "description": "URL containing the form",
                },
                "fields": {
                    "type": "object",
                    "description": "Field name/selector to value mapping",
                },
                "formGoal": {
                    "type": "string",
                    "description": "Natural language description of form filling goal",
                },
                "submit": {
                    "type": "boolean",
                    "default": False,
                    "description": "Whether to submit the form after filling",
                },
            },
            "required": ["url"],
        },
    },
    {
        "name": "browser_batch_extract",
        "description": "Extract content from multiple URLs concurrently.",
        "inputSchema": {
            "type": "object",
            "properties": {
                "urls": {
                    "type": "array",
                    "items": {"type": "string"},
                    "description": "List of URLs to extract from",
                },
                "formats": {
                    "type": "array",
                    "items": {"type": "string"},
                    "default": ["markdown"],
                    "description": "Output formats",
                },
                "maxConcurrent": {
                    "type": "integer",
                    "default": 4,
                    "description": "Maximum concurrent extractions",
                },
            },
            "required": ["urls"],
        },
    },
]


async def execute_tool(name: str, arguments: dict[str, Any]) -> dict[str, Any]:
    """Execute an MCP tool by name."""
    from ..tools import extraction, forms, navigation, research, screenshot

    if name == "browser_extract":
        return await extraction.extract_page(
            arguments["url"],
            formats=arguments.get("formats", ["markdown"]),
            prompt=arguments.get("prompt"),
        )

    elif name == "browser_navigate":
        return await navigation.navigate(
            arguments["url"],
            wait_until=arguments.get("waitUntil", "load"),
        )

    elif name == "browser_screenshot":
        return await screenshot.capture_screenshot(
            url=arguments.get("url"),
            full_page=arguments.get("fullPage", False),
            selector=arguments.get("selector"),
        )

    elif name == "browser_interact":
        from ..backends.router import get_router
        from ..core.types import BrowserOperation

        router = get_router()

        async def _interact(backend):
            result = await backend.interact(
                action=arguments["action"],
                selector=arguments.get("selector"),
                value=arguments.get("value"),
            )
            return {
                "success": result.success,
                "action": result.action,
                "error": result.error,
            }

        return await router.execute_with_fallback(BrowserOperation.INTERACT, _interact)

    elif name == "browser_research":
        return await research.deep_research(
            arguments["topic"],
            max_sources=arguments.get("maxSources", 15),
            schema=arguments.get("schema"),
        )

    elif name == "browser_map_site":
        return await research.map_site(
            arguments["url"],
            search=arguments.get("search"),
            limit=arguments.get("limit", 100),
        )

    elif name == "browser_fill_form":
        result = await forms.fill_form(
            url=arguments.get("url"),
            fields=arguments.get("fields"),
            form_goal=arguments.get("formGoal"),
        )

        if arguments.get("submit") and result.get("success"):
            submit_result = await forms.submit_form()
            result["submit_result"] = submit_result

        return result

    elif name == "browser_batch_extract":
        return await extraction.batch_extract(
            arguments["urls"],
            formats=arguments.get("formats", ["markdown"]),
            max_concurrent=arguments.get("maxConcurrent", 4),
        )

    else:
        return {"error": f"Unknown tool: {name}"}
