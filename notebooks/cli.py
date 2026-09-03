"""cianfhoghlaim-marimo — CLI for the BIEP Marimo notebooks.

Auto-discovers the 52 active marimo notebooks under
``notebooks/*.py`` via glob (the post-v7 flat layout — the
2026-07-17-pipeline-directory-consolidation-v1 change flattened the
previous numbered subdirs).

Supports four subcommands:

- ``edit <name>``       — open the notebook in ``marimo edit``
- ``run <name> ...``    — invoke the notebook as a standalone CLI script
                          (uses the notebook's PEP 723 inline deps via uv)
- ``dashboard <name>``  — run as a marimo app (production deployment)
- ``list [PATTERN]``    — list all notebooks (or matching PATTERN)

Usage:
    uv run cianfhoghlaim-marimo --help
    uv run cianfhoghlaim-marimo list                                  # all 52 active notebooks
    uv run cianfhoghlaim-marimo list 19_ireland                       # filter by prefix
    uv run cianfhoghlaim-marimo edit 19_ireland_pipeline_dashboard    # opens marimo edit
    uv run cianfhoghlaim-marimo run 19_ireland_pipeline_dashboard -- --milestone m1 --asset-check documents_ingested

Reference: openspec/changes/2026-08-10-marimo-v14-cascading-effects-verification-v1/
(post-v7 flat layout — the 2026-07-17 flattening removed the numbered subdirs;
notebooks are now directly under ``notebooks/``).
"""
from __future__ import annotations

import argparse
import fnmatch
import shutil
import subprocess
import sys
from pathlib import Path


NB_ROOT = Path(__file__).resolve().parent
REPO_ROOT = NB_ROOT.parents[1]
"""The repo root (post-v7 flattening — notebooks/ is directly under the repo root)."""


def find_notebook(name: str) -> Path | None:
    """Resolve ``name`` to a notebook path under ``NB_ROOT``.

    Accepts:
      - Bare basename: ``19_ireland_pipeline_dashboard``
      - With .py suffix: ``19_ireland_pipeline_dashboard.py`` (stripped first)
      - Partial basename: ``19_ireland`` → matches ``19_ireland_pipeline_dashboard.py``

    Returns None if not found.
    """
    # Strip .py suffix if present
    if name.endswith(".py"):
        name = name[:-3]

    # Try exact match first
    candidate = NB_ROOT / f"{name}.py"
    if candidate.exists():
        return candidate

    # Fall back to glob for partial matches (post-v7 flat layout)
    candidates = []
    for p in NB_ROOT.glob(f"{name}*.py"):
        if p.name.startswith("_"):
            continue
        if "__pycache__" in str(p):
            continue
        if "legacy" in str(p):
            continue
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
    return candidates[0]


def list_notebooks(pattern: str | None = None) -> list[str]:
    """List all active (non-legacy) notebook paths under NB_ROOT.

    If ``pattern`` is given, restrict to notebooks whose name starts with it.
    Returns paths relative to NB_ROOT.
    """
    paths = []
    for p in sorted(NB_ROOT.glob("*.py")):
        if p.name.startswith("_"):
            continue
        if "__pycache__" in str(p):
            continue
        if "legacy" in str(p):
            continue
        if pattern and not p.stem.startswith(pattern):
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


def cmd_list(pattern: str | None = None) -> int:
    """List notebooks (optionally filtered by pattern prefix)."""
    nbs = list_notebooks(pattern)
    if not nbs:
        if pattern:
            print(f"[cianfhoghlaim-marimo] no notebooks match pattern {pattern!r}", file=sys.stderr)
        return 0
    for nb in nbs:
        print(nb)
    total_str = f" matching {pattern!r}" if pattern else ""
    print(f"\n{len(nbs)} notebooks{total_str}")
    return 0


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="cianfhoghlaim-marimo",
        description=(
            "CI marimo notebook CLI. Auto-discovers the 52 active marimo "
            "notebooks under notebooks/*.py (the post-v7 flat layout — "
            "see openspec/changes/2026-07-17-v7-flatten-cianfhoghlaim-merge-bonneagar-rewrite-readme-license-v1/)."
        ),
    )
    sub = parser.add_subparsers(dest="cmd")

    p_edit = sub.add_parser("edit", help="Open a notebook in marimo edit mode")
    p_edit.add_argument("name", help="Notebook name (basename, with or without .py)")

    p_run = sub.add_parser("run", help="Run a notebook as a CLI script (uses PEP 723 inline deps)")
    p_run.add_argument("name", help="Notebook name")
    p_run.add_argument("args", nargs=argparse.REMAINDER, help="Args forwarded to the notebook CLI")

    p_dash = sub.add_parser("dashboard", help="Run a notebook as a marimo dashboard")
    p_dash.add_argument("name", help="Notebook name")
    p_dash.add_argument("args", nargs=argparse.REMAINDER)

    p_list = sub.add_parser("list", help="List all active notebooks (or filter by prefix)")
    p_list.add_argument("pattern", nargs="?", help="Filter by prefix (e.g. 19_ireland)")

    args = parser.parse_args(argv)

    if args.cmd == "edit":
        return cmd_edit(args.name)
    if args.cmd == "run":
        return cmd_run(args.name, *(args.args or []))
    if args.cmd == "dashboard":
        return cmd_dashboard(args.name, *(args.args or []))
    if args.cmd == "list":
        return cmd_list(args.pattern)
    parser.print_help()
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))