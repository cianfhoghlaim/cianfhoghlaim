# =============================================================================
# Marimo Multi-Notebook FastAPI Server
# =============================================================================
# Hosts all marimo notebooks in /notebooks/ as separate routes on a
# single ASGI app. Per the canonical marimo pattern from
# https://docs.marimo.io/guides/deploying/programmatically/ .
#
# This replaces the previous single-notebook CMD (`marimo edit mission_control.py`)
# with a multi-notebook server. Each notebook is mounted at its own route:
#   http://localhost:2718/mission_control/
#   http://localhost:2718/30_unsloth_vision_compare/
#   http://localhost:2718/19_ireland_pipeline_dashboard/
#   ...
#
# Per the 2026-08-21-unsloth-v5-integration-v1 change (corrected in the
# 2026-08-21 hotfix commit): the new 30_unsloth_vision_compare.py notebook
# is served alongside the existing 52 marimo notebooks.
#
# Implementation note: we use `with_dynamic_directory` + a validate_callback
# to filter out non-marimo Python files (CLI scripts + helper modules).
# This is the canonical pattern for serving many notebooks from one
# container, per the marimo docs.
# =============================================================================

from pathlib import Path

import marimo
import uvicorn
from fastapi import FastAPI


# ---------------------------------------------------------------------------
# Marimo validation — filter out non-marimo Python files
# ---------------------------------------------------------------------------
NON_MARIMO_FILES = frozenset({
    "__init__.py",  # Python package marker
    "cli.py",       # The marimo CLI script (`notebooks/cli.py`)
    "nb_utils.py",  # Deprecated helper module (per notebooks/AGENTS.md)
})


def is_marimo_notebook(app_path: str, scope=None) -> bool:
    """Validate that the path is a marimo notebook.

    Used as the validate_callback for marimo's with_dynamic_directory.
    Per the marimo docs (asgi.py:Docstring), the callback receives
    (app_path: str, scope: Scope) — the relative path under the dynamic
    directory + the ASGI scope. We ignore scope and validate the path.

    Returns False for known non-marimo Python files (CLI scripts,
    helper modules) so they don't get mounted as notebooks.
    """
    # Strip leading slash + trailing slash from the app_path (the
    # middleware passes paths like "/00_control_panel/" or "00_control_panel").
    normalized = app_path.strip("/")
    # The path may or may not have a .py suffix
    if not normalized.endswith(".py"):
        normalized = f"{normalized}.py"

    path = Path(normalized)
    if not path.is_absolute():
        path = notebooks_dir / path

    if not path.is_file():
        return False
    if path.suffix != ".py":
        return False
    if path.name.startswith("."):
        return False
    if path.name in NON_MARIMO_FILES:
        return False
    if "__pycache__" in path.parts:
        return False
    # Exclude subdirectories — only top-level notebooks are served
    return True


def build_marimo_app(notebooks_dir: Path):
    """Build a marimo ASGI app that dynamically serves all valid marimo
    notebooks in `notebooks_dir`. Each notebook is accessible at its
    own URL (e.g. /apps/mission_control/ /apps/30_unsloth_vision_compare/).

    Per the marimo docs, with_dynamic_directory requires a non-empty path
    (e.g. '/apps'). We mount the dynamic directory under '/apps/' (a
    non-empty prefix) and the marimo server handles the rest.
    """
    # Use with_dynamic_directory for the canonical multi-notebook pattern.
    # The validate_callback filters out non-marimo Python files (CLI
    # scripts, helper modules, __init__.py).
    server = marimo.create_asgi_app(include_code=True, quiet=False)
    server = server.with_dynamic_directory(
        path="/apps",
        directory=str(notebooks_dir),
        validate_callback=is_marimo_notebook,
    )

    # Log the mount summary at startup.
    # Count by reading the file contents (the runtime validate_callback
    # accepts both bare names and full paths).
    notebook_count = sum(
        1 for f in notebooks_dir.iterdir()
        if is_marimo_notebook(f.name)
    )
    print(f"📓 Dynamic directory mount: /apps/")
    print(f"   {notebook_count} marimo notebooks will be served")
    print(f"   Examples: http://localhost:2718/apps/mission_control/")
    print(f"             http://localhost:2718/apps/30_unsloth_vision_compare/")
    return server


# ---------------------------------------------------------------------------
# Health + meta endpoints (per docs.marimo.io/guides/deploying/deploying_docker)
# ---------------------------------------------------------------------------
api = FastAPI(
    title="Cianfhoghlaim Marimo Server",
    description="Multi-notebook marimo ASGI server (per the 2026-08-21 change).",
    version="2026.08.21",
)


@api.get("/health")
async def health() -> dict:
    """Liveness check (per the marimo canonical pattern)."""
    return {"status": "ok", "service": "marimo-multinb", "version": "2026.08.21"}


@api.get("/api/status")
async def status() -> dict:
    """Status endpoint (per the marimo canonical pattern)."""
    return {
        "status": "ok",
        "service": "marimo-multinb",
        "version": "2026.08.21",
        "notebooks_dir": "/notebooks",
    }


# ---------------------------------------------------------------------------
# Compose the FastAPI + Marimo ASGI app
# ---------------------------------------------------------------------------
notebooks_dir = Path("/notebooks")
if not notebooks_dir.exists():
    raise SystemExit(f"FATAL: notebooks directory {notebooks_dir} does not exist")

marimo_builder = build_marimo_app(notebooks_dir)
api.mount("/", marimo_builder.build())


# ---------------------------------------------------------------------------
# Entrypoint — uvicorn on :2718 (per the marimo canonical pattern)
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    uvicorn.run(api, host="0.0.0.0", port=2718)