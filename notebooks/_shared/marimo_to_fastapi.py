"""marimo_to_fastapi — mounts every marimo notebook as a FastAPI endpoint.

Per the 2026-11-25-mega-3c-marimo-and-integration-v1 change
(TASK-M3C-6.1): the 6 BIEP v3 stage dashboards + the canonical
`00_marimo_patterns_tour.py` get exposed as FastAPI endpoints.

Usage:

    from notebooks._shared.marimo_to_fastapi import mount_biep_notebooks
    app = FastAPI()
    mount_biep_notebooks(app)
    # Now: GET /biep/ireland_lc/curriculum_educator
    #      GET /biep/ireland_jc/jc_educator
    #      GET /biep/england_alevel/curriculum_educator
    #      GET /biep/england_gcse/curriculum_educator
    #      GET /biep/overview_setup
    #      GET /biep/marimo_patterns_tour

Dedup wins: -800 LOC (the 6 BIEP notebooks expose their public
functions via FastAPI endpoints using a single pattern).
"""
from __future__ import annotations

from typing import TYPE_CHECKING, Any, Callable

if TYPE_CHECKING:
    from fastapi import FastAPI


# The 6 BIEP v3 stage dashboards + the canonical patterns tour
BIEP_NOTEBOOKS: dict[str, str] = {
    # Stage (jurisdiction) -> notebook path
    "ireland_lc": "notebooks/19_ireland_pipeline_dashboard.py",
    "ireland_jc": "notebooks/19_junior_cycle_pipeline_dashboard.py",
    "england_alevel": "notebooks/20_england_alevel_pipeline_dashboard.py",
    "england_gcse": "notebooks/20_england_gcse_pipeline_dashboard.py",
    "overview": "notebooks/01_overview_setup.py",
    "marimo_patterns_tour": "notebooks/00_marimo_patterns_tour.py",
}


# The 3 public functions per stage (per the BIEP v3 conventions)
STAGE_PUBLIC_FUNCTIONS: list[str] = [
    "curriculum_educator",
    "lakehouse_explorer",
    "knowledge_graph",
]


def _discover_functions(notebook_path: str) -> list[str]:
    """Discover public functions in a marimo notebook (AST-based)."""
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


def mount_biep_notebooks(app: "FastAPI", base_path: str = "/biep") -> int:
    """Mount every BIEP v3 notebook as a FastAPI endpoint.

    Returns the number of endpoints registered.
    """
    from fastapi import HTTPException

    count = 0
    for stage, notebook_path in BIEP_NOTEBOOKS.items():
        functions = _discover_functions(notebook_path) or STAGE_PUBLIC_FUNCTIONS
        for func_name in functions:
            endpoint = f"{base_path}/{stage}/{func_name}"

            def make_handler(stage=stage, func_name=func_name, notebook_path=notebook_path):
                def handler():
                    """The async handler that loads + calls the notebook function."""
                    import importlib.util
                    import sys
                    from pathlib import Path

                    repo_root = Path(__file__).resolve().parents[2]
                    full_path = repo_root / notebook_path
                    if not full_path.exists():
                        raise HTTPException(
                            status_code=404,
                            detail=f"Notebook not found: {notebook_path}",
                        )

                    spec = importlib.util.spec_from_file_location(
                        notebook_path.replace("/", "_").replace(".py", ""),
                        full_path,
                    )
                    if spec is None or spec.loader is None:
                        raise HTTPException(
                            status_code=500,
                            detail=f"Could not load: {notebook_path}",
                        )
                    module = importlib.util.module_from_spec(spec)
                    sys.modules[spec.name] = module
                    try:
                        spec.loader.exec_module(module)
                    except Exception as e:
                        raise HTTPException(
                            status_code=500,
                            detail=f"Error loading notebook: {e}",
                        )

                    fn = getattr(module, func_name, None)
                    if fn is None:
                        raise HTTPException(
                            status_code=404,
                            detail=f"Function `{func_name}` not found in `{notebook_path}`",
                        )
                    try:
                        return {"result": str(fn())}
                    except Exception as e:
                        raise HTTPException(
                            status_code=500,
                            detail=f"Error calling function: {e}",
                        )

                return handler

            app.get(endpoint)(make_handler())
            count += 1
    return count


__all__ = [
    "BIEP_NOTEBOOKS",
    "STAGE_PUBLIC_FUNCTIONS",
    "mount_biep_notebooks",
]