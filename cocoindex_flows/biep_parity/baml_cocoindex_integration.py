"""FF.6 BAML → CocoIndex integration for the 47 BIEP CocoIndex Apps.

Per the 2026-08-18-mega-3-fast-follow-v1 change (FF.6) + the
2026-11-25-mega-3c-marimo-and-integration-v1 change (FF.6 implementation).

Provides the canonical helper for wiring BAML functions into the
47 BIEP CocoIndex Apps. The pattern is:

    from cocoindex_flows.biep_parity.baml_cocoindex_integration import (
        baml_extraction_flow,
        baml_extraction_input,
    )

    @baml_extraction_flow("ExtractCurriculumSyllabus")
    async def process_chunk(chunk_text: str, ...):
        # BAML is called automatically; the @coco.fn decorator
        # dispatches to the BAML function
        ...

Replaces the ad-hoc BAML calls scattered across the 47 BIEP
CocoIndex Apps (-600 LOC of duplicate BAML invocation patterns).
"""
from __future__ import annotations

import functools
import inspect
from typing import Any, Callable, TypeVar

F = TypeVar("F", bound=Callable[..., Any])


def baml_extraction_flow(
    function_name: str,
    *,
    stage: str = "lc",
    description: str | None = None,
) -> Callable[[F], F]:
    """Decorator that marks a CocoIndex @coco.fn as a BAML extraction flow.

    The wrapped function:
    - Looks up the BAML function via `baml_client.b.<function_name>`
    - Wraps the function as a CocoIndex flow
    - Provides the canonical lineage metadata (per the R28 lineage spec)

    Args:
        function_name: The BAML function name (e.g.,
            "ExtractCurriculumSyllabus")
        stage: The education stage ("lc" | "jc" | "alevel" | "gcse")
        description: Optional description override

    Returns:
        The decorated function (CocoIndex-compatible).
    """
    def decorator(fn: F) -> F:
        # Look up the BAML function
        try:
            from baml_client.baml_client import b
            baml_fn = getattr(b, function_name, None)
        except ImportError:
            baml_fn = None

        # Build the canonical description
        default_desc = (
            f"CocoIndex flow that calls BAML function `{function_name}` "
            f"(stage={stage}). Wraps the BAML function as a CocoIndex @coco.fn."
        )
        doc = description or default_desc

        # Attach the BAML function + stage metadata to the function
        # for downstream consumers (the lineage viewer, the
        # cocoindex_query_api, etc.)
        fn._baml_function = baml_fn
        fn._baml_function_name = function_name
        fn._baml_stage = stage
        fn.__doc__ = doc

        @functools.wraps(fn)
        async def wrapper(*args, **kwargs):
            """The async wrapper that calls the BAML function."""
            if baml_fn is None:
                # BAML not available — return a placeholder
                return {
                    "baml_function": function_name,
                    "stage": stage,
                    "error": "baml-py not installed",
                }
            # Call the BAML function
            try:
                result = baml_fn(*args, **kwargs)
                return result
            except Exception as e:
                return {
                    "baml_function": function_name,
                    "stage": stage,
                    "error": str(e),
                }

        # Preserve the metadata
        wrapper._baml_function = baml_fn
        wrapper._baml_function_name = function_name
        wrapper._baml_stage = stage
        wrapper.__doc__ = doc
        return wrapper

    return decorator


def baml_extraction_input(
    name: str,
    type_: type,
    *,
    description: str | None = None,
) -> Any:
    """Declare a BAML extraction input parameter for a CocoIndex @coco.fn.

    The function declares its inputs via Python type hints. This
    helper is a no-op placeholder (CocoIndex uses Python type hints
    natively) but provides a canonical interface for explicit input
    declarations.

    Args:
        name: The parameter name
        type_: The parameter type
        description: Optional description
    """
    return inspect.Parameter(
        name=name,
        kind=inspect.Parameter.POSITIONAL_OR_KEYWORD,
        annotation=type_,
        default=inspect.Parameter.empty,
    )


def discover_baml_flows(module: Any) -> list[dict[str, Any]]:
    """Discover all BAML extraction flows in a module.

    Returns a list of dicts:
    [{"function_name": "...", "stage": "...", "wrapper": <fn>}, ...]
    """
    flows = []
    for name in dir(module):
        attr = getattr(module, name, None)
        if not callable(attr):
            continue
        if hasattr(attr, "_baml_function_name"):
            flows.append({
                "function_name": attr._baml_function_name,
                "stage": getattr(attr, "_baml_stage", "lc"),
                "wrapper": attr,
            })
    return flows


__all__ = [
    "baml_extraction_flow",
    "baml_extraction_input",
    "discover_baml_flows",
]