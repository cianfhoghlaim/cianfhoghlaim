"""cianfhoghlaim-marimo — CLI for the BIEP Marimo notebooks.

Auto-discovers notebooks under ``cianfhoghlaim/notebooks/{01..11}_*/*.py``
via glob. Supports three subcommands:

- ``edit <name>``  — open the notebook in ``marimo edit``
- ``run <name>``   — invoke the notebook as a standalone CLI script
                     (uses the notebook's PEP 723 inline deps via uv)
- ``dashboard <name>`` — run as a marimo app (production deployment)
- ``list [GROUP]`` — list all notebooks (or just one group's)

Usage:
    uv run cianfhoghlaim-marimo --help
    uv run cianfhoghlaim-marimo list                  # all 67 active notebooks
    uv run cianfhoghlaim-marimo list 01_dev_env       # 6 dev_env notebooks
    uv run cianfhoghlaim-marimo edit 01_ccc_search    # opens marimo edit
    uv run cianfhoghlaim-marimo run 01_ccc_search -- --query "X"   # CLI mode

Reference: openspec/changes/2026-07-06-notebooks-flatten-refactor-and-wire-bi-ep/
"""
from __future__ import annotations

import argparse
import fnmatch
import shutil
import subprocess
import sys
from pathlib import Path


NB_ROOT = Path(__file__).resolve().parent
REPO_ROOT = NB_ROOT.parents[2]
"""The repo root (set in __init__.py as REPO_ROOT)."""

# The 12 functional groups (+ legacy/) — what `list [GROUP]` accepts
# (13_baml_cocoindex_tutorial added 2026-07-12 per openspec change
# `2026-07-12-baml-cocoindex-tutorials-v1` — see
# openspec/specs/end-to-end-llm-zoomcamp-style-tutorial/spec.md)
GROUPS = (
    "01_dev_env",
    "02_vision_models",
    "03_leaving_cert",
    "04_biep_motherduck",
    "05_lakehouse_inspect",
    "06_observability",
    "07_educational_stages",
    "08_sources",
    "09_official_media",
    "10_cognify",  # added 2026-07-14 per openspec change
                   # `2026-07-14-oideachais-cognify-knowledge-graph-v1`
                   # — the 9-requirement cognify KG visualizer
                   # (5-stage cross-stage + 3 leabharlann + 3 FalkorDB
                   # cross-archive + 1 notebook at 10_cognify/01_knowledge_graph.py).
    "10_marimo_dashboards",  # added 2026-07-14 per openspec change
                            # `2026-07-14-oideachais-marimo-dashboards-v1`
                            # — the 10 follow-up dashboards for the
                            # oideachais-marimo-dashboards capability spec.
    "11_marimo_dashboards_v2",  # added 2026-07-15 per openspec change
                                # `2026-07-15-oideachais-marimo-dashboards-extension-v1`
                                # — the 10-dashboard Phase-2 extension
                                # (leabharlann corpus + university extraction
                                # + cross-archive edges + K-12 → university
                                # pipeline coverage).
    "12_subject_study_tools",   # added 2026-07-16 per openspec change
                                # `2026-07-16-biiep-v1-lc-per-subject-marimo-study-tools-v1`
                                # — the 6 per-subject interactive study tools
                                # (Math, Chem, Geog, Gaeilge, Eng, CS) shipping
                                # flashcards + practice questions + mock exams
                                # + study plans over the per-subject qpack BAML
                                # functions and the BIEP v1 lakehouse tables.
    "10_mmo",
    "11_speedrun",
    "12_semantic_search",  # added 2026-07-14 per openspec change
                          # `2026-07-14-oideachais-semantic-search-v1`
                          # — the 13-requirement semantic search notebook
                          # (cross-corpus LanceDB HNSW + BGE-M3 +
                          # BGE-large-en-v1.5; bilingual EN+GA).
    "13_baml_cocoindex_tutorial",
)


def find_notebook(name: str) -> Path | None:
    """Resolve ``name`` (e.g. ``01_ccc_search`` or ``01_dev_env/01_ccc_search``)
    to a notebook path under ``NB_ROOT``.

    Accepts:
      - Bare basename: ``01_ccc_search`` → searches all 11 groups
      - Partial basename: ``ccc_search`` → matches ``01_ccc_search.py`` etc.
      - Group-qualified: ``01_dev_env/01_ccc_search`` → exact match
      - With .py suffix: ``01_ccc_search.py`` (stripped first)

    Returns None if not found.
    """
    # Strip .py suffix if present
    if name.endswith(".py"):
        name = name[:-3]

    candidates: list[Path] = []

    if "/" in name:
        # Group-qualified: split and look for exact match
        candidates.append(NB_ROOT / f"{name}.py")
    else:
        # Try exact match in each group first
        for group in GROUPS:
            candidate = NB_ROOT / group / f"{name}.py"
            if candidate.exists():
                return candidate
        # Fall back to glob for partial matches
        for p in NB_ROOT.glob(f"*/*{name}*.py"):
            if "legacy" not in str(p) and "__pycache__" not in str(p) and p.name.startswith(("0", "1")):
                candidates.append(p)

    if not candidates:
        return None
    if len(candidates) == 1:
        return candidates[0]
    # Multiple matches: print and return first
    print(f"[cianfhoghlaim-marimo] {len(candidates)} matches for {name!r}:")
    for m in candidates:
        rel = m.relative_to(NB_ROOT)
        print(f"  {rel}")
    return candidates[0]  # type: ignore[return-value] 


def list_notebooks(group: str | None = None) -> list[str]:
    """List all active (non-legacy) notebook paths under NB_ROOT.

    If ``group`` is given, restrict to that group. Returns paths
    relative to NB_ROOT.
    """
    if group:
        if group not in GROUPS:
            print(f"[cianfhoghlaim-marimo] unknown group {group!r}; choices: {GROUPS}", file=sys.stderr)
            return []
        glob_pattern = f"{group}/*.py"
    else:
        glob_pattern = "[01][0-9]_*/[!__]*.py"
    paths = []
    for p in sorted(NB_ROOT.glob(glob_pattern)):
        if "__pycache__" in str(p):
            continue
        if p.name.startswith("__"):
            continue
        paths.append(str(p.relative_to(NB_ROOT)))
    return paths


def cmd_edit(name: str, *extra: str) -> int:
    """Open ``name`` in ``marimo edit``."""
    nb = find_notebook(name)
    if nb is None:
        print(f"[cianfhoghlaim-marimo] notebook not found: {name!r}", file=sys.stderr)
        return 2
    marimo = shutil.which("marimo")
    if not marimo:
        print("[cianfhoghlaim-marimo] marimo CLI not found on PATH; install with `uv tool install marimo`", file=sys.stderr)
        return 1
    return subprocess.call([marimo, "edit", str(nb), *extra])


def cmd_run(name: str, *args: str) -> int:
    """Run ``name`` as a CLI script via `uv run <nb> ...`.

    Uses the PEP 723 inline dependency block — uv resolves the deps
    into an isolated cache and executes the CLI in one shot.
    """
    nb = find_notebook(name)
    if nb is None:
        print(f"[cianfhoghlaim-marimo] notebook not found: {name!r}", file=sys.stderr)
        return 2
    uv = shutil.which("uv")
    if not uv:
        print("[cianfhoghlaim-marimo] uv not found on PATH", file=sys.stderr)
        return 1
    # Use the project venv by setting PYTHONPATH / cwd to the repo root
    # (so `from cianfhoghlaim...` imports work).
    return subprocess.call([uv, "run", "--no-sync", "python", str(nb), *args], cwd=str(REPO_ROOT))


def cmd_dashboard(name: str, *args: str) -> int:
    """Run ``name`` as a ``marimo run`` production dashboard."""
    nb = find_notebook(name)
    if nb is None:
        print(f"[cianfhoghlaim-marimo] notebook not found: {name!r}", file=sys.stderr)
        return 2
    marimo = shutil.which("marimo")
    if not marimo:
        print("[cianfhoghlaim-marimo] marimo CLI not found on PATH", file=sys.stderr)
        return 1
    return subprocess.call([marimo, "run", str(nb), *args])


def cmd_list(group: str | None = None) -> int:
    """List notebooks (optionally scoped to one group)."""
    nbs = list_notebooks(group)
    if not nbs:
        return 0
    for nb in nbs:
        print(nb)
    # Footer summary
    total_str = f" ({len(nbs)} notebooks)" if not group else f" in {group}/"
    print(f"\n{len(nbs)} notebooks{total_str}")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="cianfhoghlaim-marimo",
        description=(
            "CI marimo notebook CLI. Auto-discovers the 67+ active "
            "notebooks under cianfhoghlaim/notebooks/{01..11}_*/ "
            "(see openspec/changes/2026-07-06-notebooks-flatten-refactor-and-wire-bi-ep/)."
        ),
    )
    sub = parser.add_subparsers(dest="cmd")

    p_edit = sub.add_parser("edit", help="Open a notebook in marimo edit mode")
    p_edit.add_argument("name", help="Notebook name (basename or group/name)")

    p_run = sub.add_parser("run", help="Run a notebook as a CLI script (uses PEP 723 inline deps)")
    p_run.add_argument("name", help="Notebook name")
    p_run.add_argument("args", nargs=argparse.REMAINDER, help="Args forwarded to the notebook CLI")

    p_dash = sub.add_parser("dashboard", help="Run a notebook as a marimo dashboard")
    p_dash.add_argument("name", help="Notebook name")
    p_dash.add_argument("args", nargs=argparse.REMAINDER)

    p_list = sub.add_parser("list", help="List all active notebooks (or one group)")
    p_list.add_argument("group", nargs="?", help="Restrict to a single group (e.g. 01_dev_env)")

    args = parser.parse_args(argv)

    if args.cmd == "edit":
        return cmd_edit(args.name)
    if args.cmd == "run":
        return cmd_run(args.name, *(args.args or []))
    if args.cmd == "dashboard":
        return cmd_dashboard(args.name, *(args.args or []))
    if args.cmd == "list":
        return cmd_list(args.group)
    parser.print_help()
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))
