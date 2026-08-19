"""marimo_integration_runtime — the canonical runtime for wiring Marimo
notebooks to the cross-package integration surface.

Per the 2026-11-25-mega-3c-marimo-and-integration-v1 change (Phase 5).

The runtime module exposes the 3 canonical helpers that the
CopilotKit + BAML + BIEP v3 dashboards use to:

1. Register every canonical marimo notebook with the CopilotKit runtime
   via `register_marimo_notebooks()`.
2. Build the BIEP v3 dashboard for a given jurisdiction via the
   canonical `build_biep_v3_dashboard()` helper from the v2 collapse.
3. Build the BAML chat handler for a given stage (LC/JC/A-Level/GCSE).

All 3 helpers are no-ops when the optional dependencies (BAML, ADK,
marimo) are not installed. Internal imports use
`spec_from_file_location` to avoid triggering the broken
`notebooks/__init__.py` (which has a known issue with
`notebooks/nb_utils.py`).

Usage:

    # In the canonical CopilotKit runtime:
    from notebooks._shared.marimo_integration_runtime import (
        register_marimo_with_all_runtimes,
        make_biep_dashboard,
        make_baml_chat_for_stage,
    )

    tools = register_marimo_with_all_runtimes()
    tabs = make_biep_dashboard(jurisdiction="ireland_lc")
    chat = make_baml_chat_for_stage(stage="lc")
"""
from __future__ import annotations

import importlib.util
import logging
import sys
from pathlib import Path
from typing import Any

logger = logging.getLogger(__name__)


# Lazy imports — Marimo is optional at type-check time
try:
    import marimo as mo  # noqa: F401
    _HAS_MARIMO = True
except ImportError:
    _HAS_MARIMO = False
    mo = None  # type: ignore


REPO_ROOT = Path(__file__).resolve().parents[2]


def _load_module_via_spec(name: str, rel_path: str) -> Any | None:
    """Load a module via importlib.util.spec_from_file_location.

    This avoids triggering the broken `notebooks/__init__.py` import
    chain (which fails on `notebooks/nb_utils.py:from __future__`
    being on line 47 instead of line 1).
    """
    try:
        path = REPO_ROOT / rel_path
        if not path.exists():
            return None
        spec = importlib.util.spec_from_file_location(name, str(path))
        if spec is None or spec.loader is None:
            return None
        module = importlib.util.module_from_spec(spec)
        sys.modules[name] = module
        spec.loader.exec_module(module)
        return module
    except Exception as e:
        logger.debug("marimo_integration_runtime: failed to load %s: %s", name, e)
        return None


def register_marimo_with_all_runtimes(
    notebooks: list[str] | None = None,
) -> list[Any]:
    """Register the canonical marimo notebooks with all runtimes.

    Wraps `register_marimo_notebooks()` from `marimo_to_copilotkit`.

    Args:
        notebooks: Optional list of notebook paths. Defaults to the
            10 canonical BIEP v3 notebooks.

    Returns:
        A list of `FunctionTool` instances (or empty list if ADK is
        not installed).
    """
    m2c = _load_module_via_spec(
        "notebooks._shared.marimo_to_copilotkit",
        "notebooks/_shared/marimo_to_copilotkit.py",
    )
    if m2c is None:
        return []

    register_fn = getattr(m2c, "register_marimo_notebooks", None)
    if register_fn is None or not callable(register_fn):
        return []

    try:
        return register_fn(notebooks=notebooks)
    except Exception as e:
        logger.debug("marimo_integration_runtime: register_marimo_notebooks failed: %s", e)
        return []


def make_biep_dashboard(
    jurisdiction: str = "ireland_lc",
    milestone: str = "M1",
) -> Any:
    """Build the BIEP v3 dashboard for the given jurisdiction + milestone.

    Wraps `build_biep_v3_dashboard()` from
    `notebooks/_shared/biiep_v3_dashboard_v2` (per the
    2026-11-25 TASK-M3C-2.1 collapse).

    Args:
        jurisdiction: One of the 11 canonical jurisdictions
            (ireland_lc, ireland_jc, england_alevel, england_gcse,
            ireland, england, sct_wls_ni, crown, 8_jurisdiction,
            aistear, primary).
        milestone: One of M1-M5.

    Returns:
        A `mo.ui.tabs` widget (or a string fallback when marimo is
        not installed). Note: the v2 helper uses
        `_cell_function.bind(...)` which only works inside a marimo
        app context — outside of marimo, this returns a string error.
    """
    try:
        # Patch mo.cell before importing (the v2 helper uses @mo.cell
        # which doesn't exist in newer marimo versions — it's a runtime
        # decorator on the app, not the module).
        if _HAS_MARIMO and not hasattr(mo, "cell"):
            mo.cell = lambda *args, **kwargs: (lambda fn: fn)
    except Exception:
        pass

    bvd = _load_module_via_spec(
        "notebooks._shared.biiep_v3_dashboard_v2",
        "notebooks/_shared/biiep_v3_dashboard_v2.py",
    )
    if bvd is None:
        return f"Error: biiep_v3_dashboard_v2 not importable"

    build_fn = getattr(bvd, "build_biep_v3_dashboard", None)
    if build_fn is None or not callable(build_fn):
        return f"Error: build_biep_v3_dashboard not available"

    try:
        return build_fn(jurisdiction=jurisdiction, milestone=milestone)
    except Exception as e:
        # The v2 helper uses .bind() which only works inside a marimo
        # app context — gracefully fall back to returning a partial-
        # invocation helper that the caller can invoke inside a marimo
        # cell.
        logger.debug(
            "marimo_integration_runtime: build_biep_v3_dashboard returned "
            "outside marimo runtime (expected): %s",
            e,
        )

        def deferred_dashboard():
            """Deferred dashboard builder for use inside a marimo cell."""
            return build_fn(jurisdiction=jurisdiction, milestone=milestone)

        deferred_dashboard.__name__ = f"make_biep_dashboard_{jurisdiction}_{milestone}"
        deferred_dashboard.__doc__ = (
            f"Deferred BIEP v3 dashboard builder for "
            f"jurisdiction={jurisdiction}, milestone={milestone}. "
            f"Invoke inside a marimo cell to get the `mo.ui.tabs` widget."
        )
        return deferred_dashboard


def make_baml_chat_for_stage(
    stage: str = "lc",
    subject: str | None = None,
) -> Any:
    """Build the BAML chat handler for a given stage.

    Args:
        stage: One of "lc", "jc", "alevel", "gcse".
        subject: Optional subject slug (chemistry, mathematics, etc.).

    Returns:
        A `mo.ui.chat` widget (or a stub fallback when BAML or
        marimo is not installed).

    The stage determines which canonical function list is used:
    - "lc" → LC6_FUNCTIONS (5 functions)
    - "jc" → JC_FUNCTIONS (4 functions)
    - "alevel" / "gcse" → QPACK_FUNCTIONS (3 functions, cross-stage)
    """
    mb = _load_module_via_spec(
        "notebooks._shared.marimo_baml",
        "notebooks/_shared/marimo_baml.py",
    )
    if mb is None:
        return None

    # Stage → function list mapping
    stage_functions_map = {
        "lc": getattr(mb, "LC6_FUNCTIONS", []),
        "jc": getattr(mb, "JC_FUNCTIONS", []),
        "alevel": getattr(mb, "QPACK_FUNCTIONS", []),
        "gcse": getattr(mb, "QPACK_FUNCTIONS", []),
    }
    functions = stage_functions_map.get(stage.lower(), stage_functions_map["lc"])

    make_chat_fn = getattr(mb, "make_baml_chat", None)
    if make_chat_fn is None or not callable(make_chat_fn):
        return None

    try:
        return make_chat_fn(
            functions=functions,
            subject=subject,
            default_message=f"Ask me about the {stage.upper()} curriculum",
        )
    except Exception as e:
        logger.debug("marimo_integration_runtime: make_baml_chat failed: %s", e)
        return None


__all__ = [
    "register_marimo_with_all_runtimes",
    "make_biep_dashboard",
    "make_baml_chat_for_stage",
]
