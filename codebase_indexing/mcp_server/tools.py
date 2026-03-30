"""
Declarative tool registry for Crypteolas MCP server.

Tools for protocol documentation search, analysis, and temporal queries.
"""

import inspect
import logging
import types
from collections.abc import Callable
from dataclasses import dataclass
from datetime import datetime
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
class ProtocolDocResult(TypedDict):
    """A protocol documentation search result."""
    id: str
    protocol: str
    title: str
    url: str
    text: str
    source_type: str
    score: float


class ProtocolEntityResult(TypedDict):
    """A protocol entity from the knowledge graph."""
    id: str
    entity_type: str
    name: str
    properties: dict[str, Any]
    valid_from: str | None
    valid_to: str | None


# =========================================================================
# Tool Implementations
# =========================================================================

@register_tool(
    description="Search protocol documentation semantically. Covers DeFi protocols like Uniswap, Aave, Compound, MakerDAO, Chainlink, and more.",
    name="search_protocol_docs",
)
async def search_protocol_docs_impl(
    query: str,
    protocol: str | None = None,
    source_type: str | None = None,
    limit: int = 10,
) -> dict[str, Any]:
    """
    Search protocol documentation using semantic similarity.

    Args:
        query: Natural language search query
        protocol: Filter by protocol name (uniswap, aave, compound, etc.)
        source_type: Filter by source type (docs, whitepaper, audit, github)
        limit: Maximum results to return (1-100)

    Returns:
        Dict with 'results' and 'total' keys
    """
    try:
        from ..cocoindex_flows.unified_embedding import unified_search
    except ImportError:
        return {"results": [], "total": 0, "error": "unified_embedding not available"}

    limit = max(1, min(limit, 100))

    try:
        results = await unified_search(
            query=query,
            protocol=protocol,
            source_type=source_type,
            limit=limit,
        )

        formatted = [
            {
                "id": r.get("id", ""),
                "protocol": r.get("protocol", ""),
                "title": r.get("title", ""),
                "url": r.get("url", ""),
                "text": r.get("text", "")[:500],
                "source_type": r.get("source_type", ""),
                "score": r.get("_distance", 0.0),
            }
            for r in results
        ]

        return {"results": formatted, "total": len(formatted)}
    except Exception as e:
        logger.error(f"Search failed: {e}")
        return {"results": [], "total": 0, "error": str(e)}


@register_tool(
    description="Search protocol code and smart contracts. Find implementations, functions, and contract patterns.",
    name="search_protocol_code",
)
async def search_protocol_code_impl(
    query: str,
    protocol: str | None = None,
    language: str | None = None,
    limit: int = 10,
) -> dict[str, Any]:
    """
    Search protocol code and smart contracts.

    Args:
        query: Search query for code functionality
        protocol: Filter by protocol name
        language: Filter by programming language (solidity, typescript, etc.)
        limit: Maximum results to return

    Returns:
        Dict with 'results' and 'total' keys
    """
    try:
        from ..cocoindex_flows.unified_embedding import code_search
    except ImportError:
        return {"results": [], "total": 0, "error": "unified_embedding not available"}

    limit = max(1, min(limit, 100))

    try:
        results = await code_search(
            query=query,
            protocol=protocol,
            language=language,
            limit=limit,
        )

        formatted = [
            {
                "id": r.get("id", ""),
                "protocol": r.get("protocol", ""),
                "file_path": r.get("file_path", ""),
                "language": r.get("language", ""),
                "text": r.get("text", "")[:500],
                "score": r.get("_distance", 0.0),
            }
            for r in results
        ]

        return {"results": formatted, "total": len(formatted)}
    except Exception as e:
        logger.error(f"Code search failed: {e}")
        return {"results": [], "total": 0, "error": str(e)}


@register_tool(
    description="Get protocol entity from knowledge graph with temporal awareness. Returns protocol state at a specific point in time.",
    name="get_protocol_entity",
)
async def get_protocol_entity_impl(
    protocol_name: str,
    entity_type: str | None = None,
    point_in_time: str | None = None,
) -> dict[str, Any]:
    """
    Get protocol entity with temporal awareness.

    Args:
        protocol_name: Name of the protocol
        entity_type: Type of entity (protocol, contract, token, oracle, governance)
        point_in_time: ISO datetime string for historical query (defaults to now)

    Returns:
        Dict with entity details and relationships
    """
    try:
        from ..cocoindex_flows.protocol_graph import get_protocol_graph
    except ImportError:
        return {"entity": None, "error": "protocol_graph not available"}

    try:
        graph = get_protocol_graph()

        pit = None
        if point_in_time:
            pit = datetime.fromisoformat(point_in_time)

        if pit:
            entity = graph.get_protocol_at_time(protocol_name, pit)
        else:
            entity = graph.get_entity_by_name(protocol_name, entity_type)

        return {"entity": entity}
    except Exception as e:
        logger.error(f"Failed to get entity: {e}")
        return {"entity": None, "error": str(e)}


@register_tool(
    description="Get relationships between protocols. Find integrations, dependencies, and oracle connections.",
    name="get_protocol_relationships",
)
async def get_protocol_relationships_impl(
    protocol_name: str,
    relationship_types: list[str] | None = None,
    direction: str = "both",
    limit: int = 20,
) -> dict[str, Any]:
    """
    Get protocol relationships from the knowledge graph.

    Args:
        protocol_name: Name of the protocol
        relationship_types: Filter by type (USES, DEPENDS_ON, INTEGRATES_WITH, PROVIDES_ORACLE, AUDITED_BY)
        direction: Relationship direction ('outgoing', 'incoming', 'both')
        limit: Maximum relationships to return

    Returns:
        Dict with 'relationships' grouped by type
    """
    try:
        from ..cocoindex_flows.protocol_graph import get_protocol_graph
    except ImportError:
        return {"relationships": {}, "error": "protocol_graph not available"}

    try:
        graph = get_protocol_graph()
        relationships = graph.get_entity_relationships(
            entity_id=protocol_name,
            relationship_types=relationship_types,
            direction=direction,
            limit=limit,
        )

        return {"relationships": relationships}
    except Exception as e:
        logger.error(f"Failed to get relationships: {e}")
        return {"relationships": {}, "error": str(e)}


@register_tool(
    description="Get protocol timeline showing historical changes. Track version updates, governance changes, and audit history.",
    name="get_protocol_timeline",
)
async def get_protocol_timeline_impl(
    protocol_name: str,
    start_date: str | None = None,
    end_date: str | None = None,
    event_types: list[str] | None = None,
) -> dict[str, Any]:
    """
    Get protocol timeline with historical events.

    Args:
        protocol_name: Name of the protocol
        start_date: Start of time range (ISO datetime)
        end_date: End of time range (ISO datetime)
        event_types: Filter by event type (version_update, governance_change, audit, integration)

    Returns:
        Dict with 'timeline' of events ordered by date
    """
    try:
        from ..cocoindex_flows.protocol_graph import get_protocol_graph
    except ImportError:
        return {"timeline": [], "error": "protocol_graph not available"}

    try:
        graph = get_protocol_graph()

        start = datetime.fromisoformat(start_date) if start_date else None
        end = datetime.fromisoformat(end_date) if end_date else None

        timeline = graph.get_entity_timeline(
            entity_id=protocol_name,
            start_date=start,
            end_date=end,
        )

        return {"timeline": timeline}
    except Exception as e:
        logger.error(f"Failed to get timeline: {e}")
        return {"timeline": [], "error": str(e)}


@register_tool(
    description="Sync latest documentation for a protocol. Fetches and indexes fresh content from official sources.",
    name="sync_protocol_docs",
)
async def sync_protocol_docs_impl(
    protocol_name: str,
    force_refresh: bool = False,
) -> dict[str, Any]:
    """
    Sync documentation for a protocol.

    Args:
        protocol_name: Name of the protocol to sync
        force_refresh: Force refresh even if recently synced

    Returns:
        Dict with sync status and statistics
    """
    try:
        from ..cocoindex_flows.live_docs import sync_protocol_docs
    except ImportError:
        return {"status": "error", "error": "live_docs not available"}

    try:
        result = await sync_protocol_docs(
            protocol_name=protocol_name,
            force_refresh=force_refresh,
        )

        return {
            "status": "success",
            "protocol": protocol_name,
            "pages_synced": result.get("pages_synced", 0),
            "last_sync": result.get("last_sync", ""),
        }
    except Exception as e:
        logger.error(f"Sync failed: {e}")
        return {"status": "error", "error": str(e)}


@register_tool(
    description="Get statistics about indexed protocol documentation.",
    name="get_protocol_stats",
)
async def get_protocol_stats_impl() -> dict[str, Any]:
    """
    Get protocol indexing statistics.

    Returns:
        Dict with protocol counts, document counts, and freshness info
    """
    try:
        import lancedb
    except ImportError:
        return {"error": "lancedb not installed"}

    try:
        db = lancedb.connect("./storage/data/lancedb")
        table = db.open_table("unified_embeddings")
        df = table.to_pandas()

        return {
            "total_documents": len(df),
            "protocols": df["protocol"].value_counts().to_dict() if "protocol" in df.columns else {},
            "source_types": df["source_type"].value_counts().to_dict() if "source_type" in df.columns else {},
        }
    except Exception as e:
        logger.error(f"Failed to get stats: {e}")
        return {"error": str(e)}


@register_tool(
    description="Compare two protocols across documentation, integrations, and features.",
    name="compare_protocols",
)
async def compare_protocols_impl(
    protocol_a: str,
    protocol_b: str,
    aspects: list[str] | None = None,
) -> dict[str, Any]:
    """
    Compare two protocols.

    Args:
        protocol_a: First protocol name
        protocol_b: Second protocol name
        aspects: Aspects to compare (features, integrations, audits, governance)

    Returns:
        Dict with comparison across specified aspects
    """
    try:
        from ..cocoindex_flows.protocol_graph import get_protocol_graph
    except ImportError:
        return {"comparison": {}, "error": "protocol_graph not available"}

    aspects = aspects or ["features", "integrations", "audits"]

    try:
        graph = get_protocol_graph()

        comparison = {}

        # Get basic info for both
        entity_a = graph.get_entity_by_name(protocol_a, "protocol")
        entity_b = graph.get_entity_by_name(protocol_b, "protocol")

        comparison["basic_info"] = {
            protocol_a: entity_a,
            protocol_b: entity_b,
        }

        # Get relationships for comparison aspects
        if "integrations" in aspects:
            rels_a = graph.get_entity_relationships(protocol_a, ["INTEGRATES_WITH"])
            rels_b = graph.get_entity_relationships(protocol_b, ["INTEGRATES_WITH"])
            comparison["integrations"] = {
                protocol_a: rels_a,
                protocol_b: rels_b,
            }

        if "audits" in aspects:
            rels_a = graph.get_entity_relationships(protocol_a, ["AUDITED_BY"])
            rels_b = graph.get_entity_relationships(protocol_b, ["AUDITED_BY"])
            comparison["audits"] = {
                protocol_a: rels_a,
                protocol_b: rels_b,
            }

        return {"comparison": comparison}
    except Exception as e:
        logger.error(f"Comparison failed: {e}")
        return {"comparison": {}, "error": str(e)}


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
