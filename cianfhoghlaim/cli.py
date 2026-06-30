"""cianfhoghlaim — the consolidated Celtic education + multi-nation + multi-language data platform.

Single CLI entry-point for the consolidated package (post-v4 consolidation 2026-06-28,
post-Phase-1 manifest consolidation 2026-06-30).

Usage:
    uv run cianfhoghlaim --help
    uv run cianfhoghlaim --version
"""
from __future__ import annotations

import argparse
import sys


def main(argv: list[str] | None = None) -> int:
    """Entry-point for the `cianfhoghlaim` console script."""
    parser = argparse.ArgumentParser(
        prog="cianfhoghlaim",
        description=(
            "Cianfhoghlaim consolidated CLI. The actual work is delegated to sub-area CLIs: "
            "cianfhoghlaim-{ocr,baml,marimo,stack-doctor,dagster,dlt,cocoindex}. "
            "See `openspec/changes/2026-06-30-consolidate-cianfhoghlaim-pyproject-and-8-dirs/` "
            "for the consolidated manifest."
        ),
    )
    parser.add_argument(
        "--version",
        action="store_true",
        help="Print the consolidated package version and exit.",
    )
    parser.add_argument(
        "--list-subcommands",
        action="store_true",
        help="List the per-area sub-CLIs.",
    )
    args = parser.parse_args(argv)

    if args.version:
        # Defer to importlib.metadata to read the canonical version from pyproject.toml.
        try:
            from importlib.metadata import version

            print(f"cianfhoghlaim {version('cianfhoghlaim')}")
        except Exception:
            print("cianfhoghlaim 0.5.0 (importlib.metadata unavailable)")
        return 0

    if args.list_subcommands:
        for sub in (
            "cianfhoghlaim-ocr",
            "cianfhoghlaim-baml",
            "cianfhoghlaim-marimo",
            "cianfhoghlaim-stack-doctor",
            "cianfhoghlaim-dagster",
            "cianfhoghlaim-dlt",
            "cianfhoghlaim-cocoindex",
        ):
            print(sub)
        return 0

    parser.print_help()
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))