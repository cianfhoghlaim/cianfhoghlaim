"""cianfhoghlaim-marimo — CLI for the 11 marimo notebooks (Ireland curriculum + leabharlann).

Usage:
    uv run cianfhoghlaim-marimo --help
    uv run cianfhoghlaim-marimo edit curriculum_educator
    uv run cianfhoghlaim-marimo list
"""
from __future__ import annotations

import argparse
import sys


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="cianfhoghlaim-marimo",
        description=(
            "Marimo CLI. Manages the 11 marimo notebooks under cianfhoghlaim/notebooks/ for "
            "Ireland curriculum (5 educational stages), leabharlann full-stack demos, "
            "official-media dashboards, and per-subject Leaving Cert views."
        ),
    )
    sub = parser.add_subparsers(dest="cmd")

    p_edit = sub.add_parser("edit", help="Open a notebook in marimo edit mode")
    p_edit.add_argument("name", help="Notebook name (without .py extension)")

    p_run = sub.add_parser("run", help="Run a notebook as a marimo app")
    p_run.add_argument("name", help="Notebook name (without .py extension)")

    p_list = sub.add_parser("list", help="List all marimo notebooks")

    args = parser.parse_args(argv)

    if args.cmd == "edit":
        print(f"[cianfhoghlaim-marimo] edit {args.name}")
        print("(Stub: delegates to `marimo edit cianfhoghlaim/notebooks/<name>.py`)")
        return 0

    if args.cmd == "run":
        print(f"[cianfhoghlaim-marimo] run {args.name}")
        print("(Stub: delegates to `marimo run cianfhoghlaim/notebooks/<name>.py`)")
        return 0

    if args.cmd == "list":
        for nb in (
            "curriculum_educator",
            "official_media",
            "leabharlann_full_stack_demo",
            "leabharlann_email_full_stack_demo",
            "leabharlann_cognify",
            "celtic_language",
            "mythology_corpus",
            "geospatial_h3",
            "fibo_assets",
        ):
            print(nb)
        return 0

    parser.print_help()
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))