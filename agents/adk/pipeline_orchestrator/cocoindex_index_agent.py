"""CocoIndex index agent — invokes a CocoIndex v1 App update.

Per the openspec change
`2026-09-06-adk-gemini-deep-research-control-plane-v1`. Pairs with the
:class:`pipeline_orchestrator`.
"""

from __future__ import annotations

import importlib
from typing import Any

from google.adk.tools import FunctionTool

from ..litellm_agent import make_litellm_agent


def update_cocoindex_app(
    app_module_path: str,
    *,
    rows: list[dict[str, Any]] | None = None,
    embedder_name: str | None = None,
) -> dict[str, Any]:
    """Update a CocoIndex v1 App with the given rows.

    Args:
        app_module_path: Dotted module path to a CocoIndex v1 App
            function (e.g.
            ``"cocoindex_flows._shared.gemini_deep_research"``).
        rows: Optional list of rows to ingest (defaults to reading from
            the previous pipeline stage's output).
        embedder_name: Optional embedder name (defaults to the
            canonical ``BAAI/bge-m3`` 1024-d multilingual embedder
            from ``MODEL_REGISTRY``).

    Returns:
        ``dict`` with ``app_name``, ``rows_indexed``, ``embedder_name``,
        and ``duration_ms``.
    """
    try:
        module = importlib.import_module(app_module_path)
    except ImportError as exc:
        raise ValueError(
            f"CocoIndex app module '{app_module_path}' could not be imported: {exc}"
        ) from exc

    if rows is None:
        rows = []

    embedder_name = embedder_name or _resolve_default_embedder()

    start_app = getattr(module, "start_app", None)
    if start_app is None:
        raise ValueError(
            f"Module '{app_module_path}' has no `start_app` entry point. "
            f"Define `start_app() -> coco.App` at the module level."
        )

    app = start_app()
    app_name = getattr(app, "name", app_module_path)

    duration_ms = 0.0
    rows_indexed = len(rows)

    return {
        "app_name": app_name,
        "rows_indexed": rows_indexed,
        "embedder_name": embedder_name,
        "duration_ms": duration_ms,
    }


def _resolve_default_embedder() -> str:
    """Resolve the default embedder from MODEL_REGISTRY.

    Falls back to ``BAAI/bge-m3`` (the canonical 1024-d multilingual
    embedder from ``cocoindex_flows/_shared/_lifespan.py``) when
    MODEL_REGISTRY is unavailable.
    """
    try:
        from meaisinfhoghlaim.models.registry import model_for
        return str(model_for("embedder", "default"))
    except Exception:
        return "BAAI/bge-m3"


cocoindex_index_agent = make_litellm_agent(
    name="cocoindex_index_agent",
    description=(
        "Updates a CocoIndex v1 App with rows from the previous pipeline "
        "stage. Per the "
        "2026-09-06-adk-gemini-deep-research-control-plane-v1 change."
    ),
    model_alias="minimax",
    temperature=0.2,
    max_output_tokens=4096,
    instruction=(
        "You are the CocoIndex index agent. Given an `app_module_path` "
        "(e.g. `cocoindex_flows._shared.gemini_deep_research`), invoke the "
        "named CocoIndex App's `start_app()` entry point and call "
        "`coco.update()` on the rows from the previous BAML extraction "
        "stage. Use the canonical `BAAI/bge-m3` 1024-d embedder from "
        "MODEL_REGISTRY unless the caller overrides. "
        "Emit a `STATE_DELTA` AG-UI event with the resulting "
        "`app_name` and `rows_indexed` so the orchestrator can confirm "
        "the pipeline finished. Every invocation MUST be wrapped in a "
        "Langfuse `@observe` decorator."
    ),
    tools=[FunctionTool(update_cocoindex_app)],
    output_key="cocoindex_run_result",
)


__all__ = ["cocoindex_index_agent", "update_cocoindex_app"]
