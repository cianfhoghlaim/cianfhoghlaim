"""
Declarative tool registry for Códeolas MCP server.

All MCP tools are defined here with the @register_tool decorator.
Both stdio and HTTP servers reference TOOL_REGISTRY.

Based on ChunkHound pattern from bonneagar/examples/chunkhound.
"""

import inspect
import logging
import types
from collections.abc import Callable
from dataclasses import dataclass
from typing import Any, TypedDict, Union, get_args, get_origin

logger = logging.getLogger(__name__)


@dataclass
class Tool:
    """Tool definition with metadata and implementation."""
    name: str
    description: str
    parameters: dict[str, Any]
    implementation: Callable


# Tool registry - populated by @register_tool decorator
TOOL_REGISTRY: dict[str, Tool] = {}


def _python_type_to_json_schema_type(type_hint: Any) -> dict[str, Any]:
    """Convert Python type hint to JSON Schema type definition."""
    if type_hint is None or type_hint is type(None):
        return {"type": "null"}

    origin = get_origin(type_hint)
    args = get_args(type_hint)

    # Handle Union types (including Optional)
    if origin is Union or isinstance(type_hint, types.UnionType):
        non_none_types = [arg for arg in args if arg is not type(None)]
        if len(non_none_types) == 1:
            return _python_type_to_json_schema_type(non_none_types[0])
        else:
            return {"anyOf": [_python_type_to_json_schema_type(t) for t in non_none_types]}

    # Handle basic types
    if type_hint == str or type_hint is str:
        return {"type": "string"}
    elif type_hint == int or type_hint is int:
        return {"type": "integer"}
    elif type_hint == float or type_hint is float:
        return {"type": "number"}
    elif type_hint == bool or type_hint is bool:
        return {"type": "boolean"}
    elif origin is list:
        item_type = args[0] if args else Any
        return {"type": "array", "items": _python_type_to_json_schema_type(item_type)}
    elif origin is dict:
        return {"type": "object"}
    else:
        return {"type": "object"}


def _extract_param_descriptions(func: Callable) -> dict[str, str]:
    """Extract parameter descriptions from docstring."""
    if not func.__doc__:
        return {}

    descriptions: dict[str, str] = {}
    lines = func.__doc__.split('\n')
    in_args_section = False

    for line in lines:
        stripped = line.strip()

        if stripped == "Args:":
            in_args_section = True
            continue

        if in_args_section and (stripped.endswith(':') or (not stripped and descriptions)):
            in_args_section = False

        if in_args_section and ':' in stripped:
            parts = stripped.split(':', 1)
            if len(parts) == 2:
                param_name = parts[0].strip()
                description = parts[1].strip()
                descriptions[param_name] = description

    return descriptions


def _generate_json_schema(func: Callable) -> dict[str, Any]:
    """Generate JSON Schema from function signature."""
    sig = inspect.signature(func)
    properties: dict[str, Any] = {}
    required: list[str] = []

    param_descriptions = _extract_param_descriptions(func)

    for param_name, param in sig.parameters.items():
        # Skip infrastructure parameters
        if param_name in ('catalog', 'embedding_model'):
            continue

        type_hint = param.annotation if param.annotation != inspect.Parameter.empty else Any
        schema = _python_type_to_json_schema_type(type_hint)

        if param_name in param_descriptions:
            schema["description"] = param_descriptions[param_name]

        if param.default != inspect.Parameter.empty and param.default is not None:
            schema["default"] = param.default

        properties[param_name] = schema

        if param.default == inspect.Parameter.empty:
            required.append(param_name)

    return {
        "type": "object",
        "properties": properties,
        "required": required if required else [],
    }


def register_tool(
    description: str,
    name: str | None = None,
) -> Callable[[Callable], Callable]:
    """
    Decorator to register a function as an MCP tool.

    Args:
        description: Tool description for LLM users
        name: Optional tool name (defaults to function name)

    Returns:
        Decorator function
    """
    def decorator(func: Callable) -> Callable:
        tool_name = name or func.__name__
        parameters = _generate_json_schema(func)

        TOOL_REGISTRY[tool_name] = Tool(
            name=tool_name,
            description=description,
            parameters=parameters,
            implementation=func,
        )

        return func

    return decorator


# Response types
class SearchResult(TypedDict):
    """A code search result."""
    file_path: str
    language: str
    chunk_type: str
    name: str | None
    start_line: int
    end_line: int
    text: str
    score: float


class SearchResponse(TypedDict):
    """Response from search operations."""
    results: list[SearchResult]
    total: int


class StatsResponse(TypedDict):
    """Response from stats operation."""
    indexed_files: int
    indexed_chunks: int
    languages: dict[str, int]


# =========================================================================
# Tool Implementations
# =========================================================================

@register_tool(
    description="Search code semantically by meaning and concept. Use when searching for functionality by description (e.g., 'authentication logic', 'database connection') or when unsure of exact keywords.",
    name="search_code",
)
async def search_code_impl(
    query: str,
    language: str | None = None,
    chunk_type: str | None = None,
    limit: int = 10,
) -> SearchResponse:
    """
    Search code using semantic similarity.

    Args:
        query: Natural language search query
        language: Filter by programming language (python, typescript, etc.)
        chunk_type: Filter by chunk type (function, class, method, etc.)
        limit: Maximum results to return (1-100)

    Returns:
        Dict with 'results' and 'total' keys
    """
    from ..cocoindex_flows.repo_embedding import search_code

    limit = max(1, min(limit, 100))

    results = await search_code(
        query=query,
        language=language,
        chunk_type=chunk_type,
        limit=limit,
    )

    formatted_results = [
        {
            "file_path": r.get("file_path", ""),
            "language": r.get("language", ""),
            "chunk_type": r.get("chunk_type", ""),
            "name": r.get("name"),
            "start_line": r.get("start_line", 0),
            "end_line": r.get("end_line", 0),
            "text": r.get("text", ""),
            "score": r.get("_distance", 0.0),
        }
        for r in results
    ]

    return {"results": formatted_results, "total": len(formatted_results)}


@register_tool(
    description="Search code using regex patterns. Use when searching for exact syntax, function names, imports, or specific text patterns.",
    name="search_regex",
)
async def search_regex_impl(
    pattern: str,
    language: str | None = None,
    limit: int = 10,
) -> SearchResponse:
    """
    Search code using regex pattern matching.

    Args:
        pattern: Regex pattern to search for
        language: Filter by programming language
        limit: Maximum results to return (1-100)

    Returns:
        Dict with 'results' and 'total' keys
    """
    import re

    try:
        import lancedb
    except ImportError:
        return {"results": [], "total": 0}

    from ..cocoindex_flows.repo_embedding import DEFAULT_LANCEDB_URI

    limit = max(1, min(limit, 100))

    # Connect and search
    db = lancedb.connect(DEFAULT_LANCEDB_URI)
    try:
        table = db.open_table("codeolas_code_chunks")
    except Exception:
        return {"results": [], "total": 0}

    # Get all chunks and filter by regex
    # Note: For production, use FTS or proper regex indexing
    all_chunks = table.to_pandas()

    if language:
        all_chunks = all_chunks[all_chunks["language"] == language]

    regex = re.compile(pattern, re.IGNORECASE)
    matches = all_chunks[all_chunks["text"].apply(lambda x: bool(regex.search(str(x))))]

    results = matches.head(limit).to_dict("records")

    formatted_results = [
        {
            "file_path": r.get("file_path", ""),
            "language": r.get("language", ""),
            "chunk_type": r.get("chunk_type", ""),
            "name": r.get("name"),
            "start_line": r.get("start_line", 0),
            "end_line": r.get("end_line", 0),
            "text": r.get("text", ""),
            "score": 1.0,  # Regex matches don't have scores
        }
        for r in results
    ]

    return {"results": formatted_results, "total": len(formatted_results)}


@register_tool(
    description="Get statistics about the indexed codebase.",
    name="get_stats",
)
async def get_stats_impl() -> StatsResponse:
    """
    Get indexing statistics.

    Returns:
        Dict with indexed_files, indexed_chunks, and languages breakdown
    """
    try:
        import lancedb
    except ImportError:
        return {"indexed_files": 0, "indexed_chunks": 0, "languages": {}}

    from ..cocoindex_flows.repo_embedding import DEFAULT_LANCEDB_URI

    db = lancedb.connect(DEFAULT_LANCEDB_URI)
    try:
        table = db.open_table("codeolas_code_chunks")
    except Exception:
        return {"indexed_files": 0, "indexed_chunks": 0, "languages": {}}

    df = table.to_pandas()

    return {
        "indexed_files": df["file_path"].nunique(),
        "indexed_chunks": len(df),
        "languages": df["language"].value_counts().to_dict(),
    }


@register_tool(
    description="Get file content and its chunks.",
    name="get_file",
)
async def get_file_impl(
    file_path: str,
) -> dict[str, Any]:
    """
    Get all chunks for a specific file.

    Args:
        file_path: Path to the file (relative or absolute)

    Returns:
        Dict with file info and chunks
    """
    try:
        import lancedb
    except ImportError:
        return {"file_path": file_path, "chunks": [], "error": "lancedb not installed"}

    from ..cocoindex_flows.repo_embedding import DEFAULT_LANCEDB_URI

    db = lancedb.connect(DEFAULT_LANCEDB_URI)
    try:
        table = db.open_table("codeolas_code_chunks")
    except Exception:
        return {"file_path": file_path, "chunks": [], "error": "table not found"}

    # Search for file
    results = table.search().where(f"file_path LIKE '%{file_path}%'").to_pandas()

    chunks = results.to_dict("records")

    return {
        "file_path": file_path,
        "chunk_count": len(chunks),
        "languages": results["language"].unique().tolist() if len(results) > 0 else [],
        "chunks": [
            {
                "chunk_type": c.get("chunk_type"),
                "name": c.get("name"),
                "start_line": c.get("start_line"),
                "end_line": c.get("end_line"),
                "text": c.get("text", "")[:500],  # Truncate for response size
            }
            for c in chunks
        ],
    }


# =========================================================================
# Tool Execution
# =========================================================================

async def execute_tool(
    tool_name: str,
    arguments: dict[str, Any],
) -> dict[str, Any]:
    """
    Execute a tool from the registry.

    Args:
        tool_name: Name of the tool to execute
        arguments: Tool arguments

    Returns:
        Tool execution result

    Raises:
        ValueError: If tool not found
    """
    if tool_name not in TOOL_REGISTRY:
        raise ValueError(f"Unknown tool: {tool_name}")

    tool = TOOL_REGISTRY[tool_name]
    result = await tool.implementation(**arguments)

    if hasattr(result, "__dict__"):
        return dict(result)
    elif isinstance(result, dict):
        return result
    else:
        return {"result": result}
