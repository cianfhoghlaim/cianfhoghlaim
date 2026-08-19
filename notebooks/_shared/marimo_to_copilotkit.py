"""marimo_to_copilotkit — mounts every marimo notebook as a CopilotKit tool.

Per the 2026-08-18-mega-3-fast-follow-v1 change (FF.4) + the
2026-11-25-mega-3c-marimo-and-integration-v1 change (Phase 5).

The helper imports every marimo notebook's public functions and
exposes them as `FunctionTool` instances that the CopilotKit UI
can route to.

Usage:

    # In the canonical CopilotKit runtime:
    from notebooks._shared.marimo_to_copilotkit import register_marimo_notebooks
    tools = register_marimo_notebooks(
        notebooks=["notebooks/19_ireland_pipeline_dashboard.py", ...],
    )

Dedup wins: -300 LOC (the 4 hand-written fetch patterns in the
web/apps/cianfhoghlaim/components/).
"""
from __future__ import annotations

from typing import Any, Callable


# Lazy imports — Google ADK is optional at type-check time
try:
    from google.adk.tools import FunctionTool
    _HAS_ADK = True
except ImportError:
    _HAS_ADK = False
    FunctionTool = None  # type: ignore


# The 10 BIEP v3 canonical notebooks (per the marimo patterns tour)
CANONICAL_NOTEBOOKS: list[str] = [
    "notebooks/00_marimo_patterns_tour.py",
    "notebooks/01_overview_setup.py",
    "notebooks/19_ireland_pipeline_dashboard.py",
    "notebooks/19_junior_cycle_pipeline_dashboard.py",
    "notebooks/20_england_alevel_pipeline_dashboard.py",
    "notebooks/20_england_gcse_pipeline_dashboard.py",
    "notebooks/21_sct_wls_ni_pipeline_dashboard.py",
    "notebooks/22_crown_dependencies_dashboard.py",
    "notebooks/23_8_jurisdiction_overview.py",
    "notebooks/24_deployment_control_panel.py",
]


def discover_public_functions(notebook_path: str) -> list[str]:
    """Discover the public functions in a marimo notebook.

    Returns a list of function names (heuristic — uses Python AST
    parsing to find top-level functions that aren't prefixed with `_`).
    """
    import ast
    from pathlib import Path

    repo_root = Path(__file__).resolve().parents[2]
    full_path = repo_root / notebook_path
    if not full_path.exists():
        return []

    try:
        tree = ast.parse(full_path.read_text())
    except SyntaxError:
        return []

    public_functions = []
    for node in ast.walk(tree):
        if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)):
            if not node.name.startswith("_"):
                public_functions.append(node.name)
    return public_functions


def notebook_to_function_tool(
    notebook_path: str,
    func_name: str,
) -> "FunctionTool":
    """Wrap a single marimo notebook function as a Google ADK FunctionTool.

    The wrapper calls the notebook's function (via dynamic import +
    exec) and returns the result as a string.
    """
    if not _HAS_ADK:
        raise ImportError(
            "google-adk is required. Install with `uv add google-adk`."
        )

    def wrapper(*args, **kwargs):
        """The sync wrapper that calls the notebook function."""
        from pathlib import Path
        import sys
        import importlib.util

        repo_root = Path(__file__).resolve().parents[2]
        full_path = repo_root / notebook_path

        # Dynamic import via importlib.util
        spec = importlib.util.spec_from_file_location(
            notebook_path.replace("/", "_").replace(".py", ""),
            full_path,
        )
        if spec is None or spec.loader is None:
            return f"Error: could not load {notebook_path}"
        module = importlib.util.module_from_spec(spec)
        sys.modules[spec.name] = module
        try:
            spec.loader.exec_module(module)
        except Exception as e:
            return f"Error loading notebook: {e}"

        # Call the function
        fn = getattr(module, func_name, None)
        if fn is None:
            return f"Error: {func_name} not found in {notebook_path}"
        try:
            result = fn(*args, **kwargs)
            return str(result)
        except Exception as e:
            return f"Error: {e}"

    wrapper.__name__ = func_name
    wrapper.__doc__ = f"BAML/CopilotKit wrapper for `{func_name}` from `{notebook_path}`."
    return FunctionTool(func=wrapper)


def register_marimo_notebooks(
    notebooks: list[str] | None = None,
) -> list["FunctionTool"]:
    """Discover the canonical marimo notebooks + register each public
    function as a CopilotKit tool.

    Returns the list of `FunctionTool` instances.
    """
    notebooks = notebooks or CANONICAL_NOTEBOOKS
    tools: list[FunctionTool] = []
    for nb in notebooks:
        func_names = discover_public_functions(nb)
        for fn in func_names:
            try:
                tool = notebook_to_function_tool(nb, fn)
                tools.append(tool)
            except Exception:
                # Skip tools that fail to register
                pass
    return tools


__all__ = [
    "CANONICAL_NOTEBOOKS",
    "discover_public_functions",
    "notebook_to_function_tool",
    "register_marimo_notebooks",
]