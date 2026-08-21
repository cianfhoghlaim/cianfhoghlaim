"""
Declarative tool registry for Oideachas MCP server.

Tools for curriculum search, learning outcomes, and learning paths.
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


TOOL_REGISTRY: dict[str, Tool] = {}


def _python_type_to_json_schema_type(type_hint: Any) -> dict[str, Any]:
    """Convert Python type hint to JSON Schema type definition."""
    if type_hint is None or type_hint is type(None):
        return {"type": "null"}

    origin = get_origin(type_hint)
    args = get_args(type_hint)

    if origin is Union or isinstance(type_hint, types.UnionType):
        non_none_types = [arg for arg in args if arg is not type(None)]
        if len(non_none_types) == 1:
            return _python_type_to_json_schema_type(non_none_types[0])
        else:
            return {"anyOf": [_python_type_to_json_schema_type(t) for t in non_none_types]}

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
    lines = func.__doc__.split("\n")
    in_args_section = False

    for line in lines:
        stripped = line.strip()

        if stripped == "Args:":
            in_args_section = True
            continue

        if in_args_section and (stripped.endswith(":") or (not stripped and descriptions)):
            in_args_section = False

        if in_args_section and ":" in stripped:
            parts = stripped.split(":", 1)
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
class CurriculumResult(TypedDict):
    """A curriculum search result."""

    id: str
    title: str
    subject: str
    level: str
    language: str
    text: str
    score: float


class LearningOutcomeResult(TypedDict):
    """A learning outcome search result."""

    code: str
    description_en: str
    description_ga: str | None
    subject: str
    level: str
    strand: str | None
    score: float


class LearningPathResult(TypedDict):
    """A learning path result."""

    outcomes: list[LearningOutcomeResult]
    relationships: list[dict[str, Any]]


# =========================================================================
# Tool Implementations
# =========================================================================


@register_tool(
    description="Search Irish curriculum content semantically. Supports English and Irish queries for NCCA curriculum, SEC exam content, and learning outcomes.",
    name="search_curriculum",
)
async def search_curriculum_impl(
    query: str,
    subject: str | None = None,
    level: str | None = None,
    language: str | None = None,
    limit: int = 10,
) -> dict[str, Any]:
    """
    Search curriculum content using semantic similarity.

    Args:
        query: Natural language search query (English or Irish)
        subject: Filter by subject (e.g., 'mathematics', 'irish', 'geography')
        level: Filter by education level (primary, junior_cycle, senior_cycle)
        language: Filter by content language ('en' or 'ga')
        limit: Maximum results to return (1-100)

    Returns:
        Dict with 'results' and 'total' keys
    """
    try:
        from ..cocoindex_flows.curriculum_embedding import search_curriculum
    except ImportError:
        return {"results": [], "total": 0, "error": "curriculum_embedding not available"}

    limit = max(1, min(limit, 100))

    try:
        results = await search_curriculum(
            query=query,
            subject=subject,
            level=level,
            language=language,
            limit=limit,
        )

        formatted = [
            {
                "id": r.get("id", ""),
                "title": r.get("title", ""),
                "subject": r.get("subject", ""),
                "level": r.get("level", ""),
                "language": r.get("language", ""),
                "text": r.get("text", "")[:500],
                "score": r.get("_distance", 0.0),
            }
            for r in results
        ]

        return {"results": formatted, "total": len(formatted)}
    except Exception as e:
        logger.error(f"Search failed: {e}")
        return {"results": [], "total": 0, "error": str(e)}


@register_tool(
    description="Search for specific learning outcomes by code or description. Use for finding curriculum standards and objectives.",
    name="search_learning_outcomes",
)
async def search_learning_outcomes_impl(
    query: str,
    subject: str | None = None,
    level: str | None = None,
    strand: str | None = None,
    limit: int = 10,
) -> dict[str, Any]:
    """
    Search learning outcomes.

    Args:
        query: Search query for outcome description or code
        subject: Filter by subject
        level: Filter by education level
        strand: Filter by curriculum strand
        limit: Maximum results to return

    Returns:
        Dict with 'results' and 'total' keys
    """
    try:
        from ..cocoindex_flows.learning_outcome_graph import LearningOutcomeGraphBuilder
    except ImportError:
        return {"results": [], "total": 0, "error": "learning_outcome_graph not available"}

    limit = max(1, min(limit, 100))

    try:
        builder = LearningOutcomeGraphBuilder()
        results = await builder.search_outcomes(
            query=query,
            subject=subject,
            level=level,
            limit=limit,
        )

        return {"results": results, "total": len(results)}
    except Exception as e:
        logger.error(f"Search failed: {e}")
        return {"results": [], "total": 0, "error": str(e)}


@register_tool(
    description="Find the prerequisite learning path for a target outcome. Returns ordered sequence of outcomes that should be mastered first.",
    name="get_learning_path",
)
async def get_learning_path_impl(
    target_outcome_code: str,
    max_depth: int = 5,
) -> dict[str, Any]:
    """
    Get prerequisite learning path to a target outcome.

    Args:
        target_outcome_code: Code of the target learning outcome (e.g., 'LO-MATH-JC-2.3')
        max_depth: Maximum depth of prerequisite chain to explore

    Returns:
        Dict with 'path' (ordered outcomes) and 'relationships'
    """
    try:
        from ..cocoindex_flows.learning_outcome_graph import LearningPathFinder
    except ImportError:
        return {"path": [], "relationships": [], "error": "learning_outcome_graph not available"}

    max_depth = max(1, min(max_depth, 10))

    try:
        finder = LearningPathFinder()
        path = await finder.find_prerequisite_path(
            target_code=target_outcome_code,
            max_depth=max_depth,
        )

        return path
    except Exception as e:
        logger.error(f"Path finding failed: {e}")
        return {"path": [], "relationships": [], "error": str(e)}


@register_tool(
    description="Get all learning outcomes related to a specific outcome, including prerequisites, extensions, and related skills.",
    name="get_related_outcomes",
)
async def get_related_outcomes_impl(
    outcome_code: str,
    relationship_types: list[str] | None = None,
    limit: int = 20,
) -> dict[str, Any]:
    """
    Get outcomes related to a specific outcome.

    Args:
        outcome_code: Code of the learning outcome
        relationship_types: Filter by relationship type (PREREQUISITE_FOR, BUILDS_ON, ASSESSES, RELATED_TO)
        limit: Maximum results to return

    Returns:
        Dict with 'related_outcomes' grouped by relationship type
    """
    try:
        from ..cocoindex_flows.learning_outcome_graph import LearningOutcomeGraphBuilder
    except ImportError:
        return {"related_outcomes": {}, "error": "learning_outcome_graph not available"}

    try:
        builder = LearningOutcomeGraphBuilder()
        related = await builder.get_related_outcomes(
            outcome_code=outcome_code,
            relationship_types=relationship_types,
            limit=limit,
        )

        return {"related_outcomes": related}
    except Exception as e:
        logger.error(f"Failed to get related outcomes: {e}")
        return {"related_outcomes": {}, "error": str(e)}


@register_tool(
    description="Get statistics about the curriculum index including subjects, levels, and outcome counts.",
    name="get_curriculum_stats",
)
async def get_curriculum_stats_impl() -> dict[str, Any]:
    """
    Get curriculum indexing statistics.

    Returns:
        Dict with subject counts, level counts, and totals
    """
    try:
        import lancedb
    except ImportError:
        return {"error": "lancedb not installed"}

    try:
        db = lancedb.connect("./storage/data/lancedb")
        table = db.open_table("celtic_curriculum_embeddings")
        df = table.to_pandas()

        return {
            "total_documents": len(df),
            "subjects": df["subject"].value_counts().to_dict() if "subject" in df.columns else {},
            "levels": df["level"].value_counts().to_dict() if "level" in df.columns else {},
            "languages": df["language"].value_counts().to_dict()
            if "language" in df.columns
            else {},
        }
    except Exception as e:
        logger.error(f"Failed to get stats: {e}")
        return {"error": str(e)}


@register_tool(
    description="Translate curriculum content between English and Irish.",
    name="translate_curriculum",
)
async def translate_curriculum_impl(
    text: str,
    target_language: str = "ga",
) -> dict[str, Any]:
    """
    Translate curriculum text between English and Irish.

    Args:
        text: Text to translate
        target_language: Target language code ('en' or 'ga')

    Returns:
        Dict with 'translation' and 'source_language'
    """
    try:
        from ..cocoindex_flows.curriculum_translation import translate_text
    except ImportError:
        return {"error": "curriculum_translation not available"}

    try:
        result = await translate_text(
            text=text,
            target_language=target_language,
        )

        return {
            "translation": result.get("translation", ""),
            "source_language": result.get("source_language", ""),
        }
    except Exception as e:
        logger.error(f"Translation failed: {e}")
        return {"error": str(e)}


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
