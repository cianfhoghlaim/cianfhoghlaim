"""DLT trigger agent — runs a DLT source as an ADK FunctionTool.

Per the openspec change
`2026-09-06-adk-gemini-deep-research-control-plane-v1`. Pairs with
:class:`pipeline_orchestrator` and the
:class:`dlt.pipeline-trigger-via-adk` capability.
"""

from __future__ import annotations

import importlib
from typing import Any

from google.adk.tools import FunctionTool

from ..litellm_agent import make_litellm_agent


def run_dlt_source(
    source_module_path: str,
    pipeline_name: str = "gemini_deep_research_pipeline",
    dataset_name: str = "oideachais_gemini_deep_research",
    **kwargs: Any,
) -> dict[str, Any]:
    """Run a DLT source and return the pipeline load info.

    Args:
        source_module_path: Dotted module path to a function decorated
            with ``@dlt.source`` (e.g.
            ``"dlt_sources._shared.gemini_deep_research"``).
        pipeline_name: Name for the DLT pipeline (used for state tracking).
        dataset_name: Destination dataset name (e.g.
            ``"oideachais_gemini_deep_research"``).
        **kwargs: Forwarded to the source function call.

    Returns:
        ``dict`` with keys ``pipeline_run_id``, ``load_info``,
        ``row_counts``, ``schema_version``.

    Raises:
        ValueError: If ``source_module_path`` does not resolve.
    """
    try:
        import dlt

        module = importlib.import_module(source_module_path)
    except ImportError as exc:
        raise ValueError(
            f"DLT source module '{source_module_path}' could not be imported: {exc}"
        ) from exc

    source_func = getattr(module, "gemini_deep_research_source", None)
    if source_func is None:
        raise ValueError(
            f"Module '{source_module_path}' has no @dlt.source-decorated "
            f"`gemini_deep_research_source` function. Add one or update the "
            f"dlt_trigger_agent to call a different entry point."
        )

    pipeline = dlt.pipeline(
        pipeline_name=pipeline_name,
        destination="duckdb",
        dataset_name=dataset_name,
    )

    source = source_func(**kwargs)
    load_info = pipeline.run(source)

    row_counts: dict[str, int] = {}
    if hasattr(load_info, "load_packages") and load_info.load_packages:
        try:
            first_pkg = load_info.load_packages[0]
            if first_pkg.jobs:
                first_job = first_pkg.jobs[0]
                file_path = getattr(first_job, "file_path", "")
                table_name = file_path.split("/")[-1] if file_path else "unknown"
                row_counts[table_name] = len(getattr(load_info, "loads_ids", []) or [])
        except (IndexError, AttributeError):
            pass

    return {
        "pipeline_run_id": load_info.pipeline.pipeline_name,
        "load_info": str(load_info),
        "row_counts": row_counts,
        "schema_version": getattr(load_info, "schema_version", None),
        "first_run": load_info.first_run,
    }


dlt_trigger_agent = make_litellm_agent(
    name="dlt_trigger_agent",
    description=(
        "Runs a DLT pipeline against a named source module and emits "
        "STATE_DELTA AG-UI events. Per the 2026-09-06-adk-gemini-deep-research-control-plane-v1 "
        "change."
    ),
    model_alias="minimax",
    temperature=0.2,
    max_output_tokens=4096,
    instruction=(
        "You are the DLT trigger agent. Given a `source_module_path`, "
        "run the named DLT source via `pipeline.run(source())`. "
        "Use the default destination (`duckdb`) + `dataset_name` "
        "(`oideachais_<domain>`) unless the caller overrides. "
        "Emit a `STATE_DELTA` AG-UI event with the resulting "
        "`pipeline_run_id` and `load_info` so the orchestrator can chain "
        "the next stage. Every invocation MUST be wrapped in a Langfuse "
        "`@observe` decorator so the trace links to the parent run."
    ),
    tools=[FunctionTool(run_dlt_source)],
    output_key="dlt_run_result",
)


__all__ = ["dlt_trigger_agent", "run_dlt_source"]
