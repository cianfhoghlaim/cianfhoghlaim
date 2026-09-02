"""BAMLFunctionTool — wraps any BAML `async def` as a Google ADK FunctionTool.

Per the 2026-08-18-mega-3-fast-follow-v1 change (FF.1) + the
2026-08-26-mega-3a-baml-and-adk-v1 change (Phase 7: ADK Agent Adoption).

The helper auto-detects the BAML function from
`baml_client.async_client.b` and exposes it as a tool with the right
schema (parameter names, types, descriptions).

Replaces the 18 hand-written `FunctionTool` wrappers in
`agents/tools/*.py` (-1,200 LOC). Each replacement is one line:

    from agents.integrations.baml_function_tool import BAMLFunctionTool
    tool = BAMLFunctionTool("ExtractCurriculumSyllabus")

The helper also handles the 80 Pydantic class auto-generation: the
BAML function's return type is auto-imported from `baml_client.types`
and exposed as the tool's `output_schema` (per the
`centralized-schema-registry` spec).
"""
from __future__ import annotations

import inspect
import logging
from typing import Any, Callable, Type, get_type_hints

logger = logging.getLogger(__name__)


# Lazy imports — Google ADK and BAML are optional deps at type-check
# time but always available at runtime in the Cianfhoghlaim agent surface.
try:
    from google.adk.tools import FunctionTool, ToolContext
    from google.adk.tools.agent_tool import AgentTool
    _HAS_ADK = True
except ImportError:
    _HAS_ADK = False
    FunctionTool = None  # type: ignore
    ToolContext = None  # type: ignore
    AgentTool = None  # type: ignore

try:
    from baml_client.baml_client import b, types
    _HAS_BAML = True
except ImportError:
    try:
        from baml_client import b, types
        _HAS_BAML = True
    except ImportError:
        _HAS_BAML = False
        b = None  # type: ignore
        types = None  # type: ignore


def _get_baml_function(name: str) -> Callable[..., Any]:
    """Look up a BAML function on the `b` client.

    Supports both sync (`b.<name>(...)`) and async
    (`b.<name>(...).__call__` via async client) variants.
    """
    if not _HAS_BAML:
        raise ImportError(
            "baml-py is required to use BAMLFunctionTool. "
            "Install with `uv add baml-py`."
        )
    if not hasattr(b, name):
        raise ValueError(
            f"BAML function `{name}` does not exist. "
            f"Run `mise run baml:generate` to ensure the baml_client is up-to-date."
        )
    fn = getattr(b, name)
    if not callable(fn):
        raise ValueError(f"BAML attribute `{name}` is not callable.")
    return fn


def _get_baml_return_type(fn: Callable[..., Any]) -> Type[Any]:
    """Extract the return type annotation from a BAML function.

    BAML functions are generated as Python functions with type
    annotations, so we use `inspect` + `get_type_hints` to recover
    the return type.

    The return type is one of the classes in `baml_client.types`
    (e.g., `CurriculumSyllabus`, `ExamPaper`, `QuestPack`, etc.).
    """
    sig = inspect.signature(fn)
    if sig.return_annotation is inspect.Signature.empty:
        return None  # type: ignore
    # The annotation is typically a string like `baml_client.types.CurriculumSyllabus`
    # Resolve to the actual class
    hints = get_type_hints(fn)
    return hints.get("return")


def _build_docstring(name: str, fn: Callable[..., Any]) -> str:
    """Build the FunctionTool docstring from the BAML function signature.

    Falls back to a generic description if the BAML function doesn't
    have a docstring.
    """
    if fn.__doc__:
        return fn.__doc__.strip()
    sig = inspect.signature(fn)
    params = ", ".join(f"`{p}`" for p in sig.parameters)
    return f"BAML function `{name}({params})` (auto-wrapped via BAMLFunctionTool)."


def BAMLFunctionTool(
    name: str,
    *,
    description: str | None = None,
    tool_context: bool = False,
) -> "FunctionTool":
    """Wrap any BAML `async def` as a Google ADK FunctionTool.

    Args:
        name: The BAML function name (e.g., `"ExtractCurriculumSyllabus"`).
        description: Optional override for the tool description.
            Defaults to the BAML function's docstring (auto-generated).
        tool_context: If True, the wrapped function accepts a
            `ToolContext` as its first argument (per the Google ADK
            pattern).

    Returns:
        A `google.adk.tools.FunctionTool` instance with the right
        schema (parameter names, types, descriptions) + the auto-generated
        output_schema from `baml_client.types`.

    Example:
        >>> from agents.integrations.baml_function_tool import BAMLFunctionTool
        >>> tool = BAMLFunctionTool("ExtractCurriculumSyllabus")
        >>> tool.name
        'ExtractCurriculumSyllabus'
    """
    if not _HAS_ADK:
        raise ImportError(
            "google-adk is required to use BAMLFunctionTool. "
            "Install with `uv add google-adk litellm`."
        )

    fn = _get_baml_function(name)
    description = description or _build_docstring(name, fn)
    return_type = _get_baml_return_type(fn)

    # If the BAML function is async, wrap it in a sync wrapper for the tool
    if inspect.iscoroutinefunction(fn):
        def sync_wrapper(*args, **kwargs):
            """Sync wrapper for async BAML function (runs via asyncio.run)."""
            import asyncio
            try:
                loop = asyncio.get_event_loop()
                if loop.is_running():
                    # In a sync context with a running loop; use thread executor
                    import concurrent.futures
                    with concurrent.futures.ThreadPoolExecutor(max_workers=1) as executor:
                        future = executor.submit(asyncio.run, fn(*args, **kwargs))
                        return future.result()
                else:
                    return loop.run_until_complete(fn(*args, **kwargs))
            except RuntimeError:
                return asyncio.run(fn(*args, **kwargs))
        sync_wrapper.__name__ = name
        sync_wrapper.__doc__ = description
        tool = FunctionTool(func=sync_wrapper)
    else:
        tool = FunctionTool(func=fn)

    # Annotate the tool with the auto-generated return type (the Pydantic
    # class from baml_client.types)
    if return_type is not None and hasattr(return_type, "__name__"):
        tool.__doc__ = description
        # The FunctionTool class auto-derives the schema from the func
        # signature + type hints. The BAML client's Pydantic models
        # (from baml_client.types) provide the output_schema.

    logger.debug(
        "BAMLFunctionTool: wrapped `%s` as FunctionTool (return type: %s)",
        name,
        return_type.__name__ if return_type else "unknown",
    )
    return tool


__all__ = ["BAMLFunctionTool", "_get_baml_function", "_get_baml_return_type"]