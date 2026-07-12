"""cianfhoghlaim-baml — CLI for the BAML extraction schema source + client regeneration.

Usage:
    uv run cianfhoghlaim-baml --help
    uv run cianfhoghlaim-baml generate       # regenerate baml_client/ Python module
    uv run cianfhoghlaim-baml test --filter curriculum
"""
from __future__ import annotations

import argparse
import sys


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="cianfhoghlaim-baml",
        description=(
            "BAML CLI. Manages 56+ .baml source files under cianfhoghlaim/baml/ (curriculum "
            "extraction, leaving-cert marking schemes, email triage, OCR validation, "
            "author-archive, mythology, etc.) and regenerates the baml_client/ Python module."
        ),
    )
    sub = parser.add_subparsers(dest="cmd")

    p_gen = sub.add_parser("generate", help="Regenerate baml_client/ Python module")
    p_test = sub.add_parser("test", help="Run baml-cli test")
    p_test.add_argument("--filter", help="Filter test cases by name substring")

    args = parser.parse_args(argv)

    if args.cmd == "generate":
        print("[cianfhoghlaim-baml] generate")
        print("(Stub: delegates to mise run baml:generate)")
        return 0

    if args.cmd == "test":
        print(f"[cianfhoghlaim-baml] test filter={args.filter}")
        print("(Stub: delegates to mise run cic:baml:test)")
        return 0

    parser.print_help()
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))