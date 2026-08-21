"""
MCP tools for códeolas.

Provides tool definitions for Claude Code integration.
"""

import functools
import inspect
import logging
from typing import Any, Callable, TypedDict

logger = logging.getLogger(__name__)

# Tool registry
_tools: dict[str, dict[str, Any]] = {}


class SearchResult(TypedDict):
    """Search result type."""

    file_path: str
    start_line: int
    end_line: int
    name: str | None
    chunk_type: str
    text: str
    score: float


class SearchResponse(TypedDict):
    """Search response type."""

    results: list[SearchResult]
    total: int


class StatsResponse(TypedDict):
    """Stats response type."""

    indexed: bool
    code_chunks: dict[str, Any]
    files: dict[str, Any]


def register_tool(
    name: str | None = None,
    description: str | None = None,
):
    """
    Decorator to register a function as an MCP tool.

    Args:
        name: Tool name (defaults to function name)
        description: Tool description (defaults to docstring)
    """

    def decorator(func: Callable) -> Callable:
        tool_name = name or func.__name__
        tool_desc = description or func.__doc__ or ""

        # Generate JSON schema from function signature
        sig = inspect.signature(func)
        properties = {}
        required = []

        for param_name, param in sig.parameters.items():
            if param_name in ("self", "cls"):
                continue

            # Determine type
            param_type = "string"
            if param.annotation != inspect.Parameter.empty:
                if param.annotation == int:
                    param_type = "integer"
                elif param.annotation == float:
                    param_type = "number"
                elif param.annotation == bool:
                    param_type = "boolean"
                elif param.annotation == list:
                    param_type = "array"

            properties[param_name] = {
                "type": param_type,
                "description": f"Parameter: {param_name}",
            }

            if param.default == inspect.Parameter.empty:
                required.append(param_name)

        _tools[tool_name] = {
            "name": tool_name,
            "description": tool_desc.strip(),
            "inputSchema": {
                "type": "object",
                "properties": properties,
                "required": required,
            },
            "function": func,
        }

        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            return func(*args, **kwargs)

        return wrapper

    return decorator


def list_tools() -> list[dict[str, Any]]:
    """List all registered tools."""
    return [
        {
            "name": tool["name"],
            "description": tool["description"],
            "inputSchema": tool["inputSchema"],
        }
        for tool in _tools.values()
    ]


async def execute_tool(name: str, arguments: dict[str, Any]) -> Any:
    """Execute a tool by name."""
    if name not in _tools:
        raise ValueError(f"Unknown tool: {name}")

    tool = _tools[name]
    func = tool["function"]

    # Check if async
    if inspect.iscoroutinefunction(func):
        return await func(**arguments)
    else:
        return func(**arguments)


# Register default tools
@register_tool(
    name="search_code",
    description="Semantic search for code by natural language query",
)
async def search_code_tool(
    query: str,
    limit: int = 10,
    language: str = None,
) -> SearchResponse:
    """Search for code semantically."""
    from ..flows import search_code

    results = await search_code(query, limit=limit, language=language)

    return {
        "results": [
            {
                "file_path": r.get("file_path", ""),
                "start_line": r.get("start_line", 0),
                "end_line": r.get("end_line", 0),
                "name": r.get("name"),
                "chunk_type": r.get("chunk_type", ""),
                "text": r.get("text", "")[:500],
                "score": r.get("_distance", 0.0),
            }
            for r in results
        ],
        "total": len(results),
    }


@register_tool(
    name="search_regex",
    description="Search code with regex pattern",
)
async def search_regex_tool(
    pattern: str,
    limit: int = 10,
    language: str = None,
) -> dict[str, Any]:
    """Search for code by regex pattern."""
    # Regex search not yet implemented in flows
    # Return empty for now
    return {
        "results": [],
        "total": 0,
        "note": "Regex search not yet implemented",
    }


@register_tool(
    name="get_stats",
    description="Get indexing statistics",
)
def get_stats_tool() -> StatsResponse:
    """Get indexing stats."""
    from ..storage import get_lance_catalog

    catalog = get_lance_catalog()
    stats = catalog.get_stats()

    return {
        "indexed": stats.get("code_chunks", {}).get("exists", False),
        "code_chunks": stats.get("code_chunks", {}),
        "files": stats.get("files", {}),
    }


@register_tool(
    name="get_file_chunks",
    description="Get all code chunks for a specific file",
)
def get_file_chunks_tool(file_path: str) -> dict[str, Any]:
    """Get all chunks for a file."""
    from ..storage import get_lance_catalog

    catalog = get_lance_catalog()
    chunks = catalog.get_file_chunks(file_path)

    return {
        "file_path": file_path,
        "chunks": chunks,
        "total": len(chunks),
    }
