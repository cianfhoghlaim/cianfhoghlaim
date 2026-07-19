"""cianfhoghlaim.cli — consolidated CLI entry-point (per `__main__.py:7`).

Canonical implementation. The historical `clio.py` file is kept as a
backward-compat re-export shim for one release cycle.

Per `openspec/changes/2026-07-14-fix-foundation-v7-flattening-and-baml-drift-v1`,
the rename from `clio.py` → `cli.py` is part of the v7 flattening
consolidation. Both filenames work for now; new code MUST use
`from cianfhoghlaim.cli import main`.
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
            "cianfhoghlaim.orchestration",
            "cianfhoghlaim-dlt",
            "cianfhoghlaim-cocoindex",
        ):
            print(sub)
        return 0

    parser.print_help()
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))


# Re-export from `clio.py` for backward compat. Kept at the bottom of the file
# to avoid double-defining `main` if a future cleanup just deletes `clio.py`.
try:
    from cianfhoghlaim import clio as _clio_shim  # noqa: F401
except ImportError:
    pass
