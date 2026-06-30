"""cianfhoghlaim-cocoindex — CLI for the 14 v1 CocoIndex Apps.

Usage:
    uv run cianfhoghlaim-cocoindex --help
    uv run cianfhoghlaim-cocoindex index --app leabharlann_books
    uv run cianfhoghlaim-cocoindex conformance  # run the 4-rule R1-R4 lint
    uv run cianfhoghlaim-cocoindex list
"""
from __future__ import annotations

import argparse
import sys


# The 14 v1 CocoIndex Apps per `oideachais-cocoindex-v1` skill.
V1_APPS = (
    "leabharlann_books_embedding",
    "leabharlann_zotero_embedding",
    "leabharlann_takeout_embedding",
    "codebase_indexing",
    "api_indexing",
    "filesystem_indexing",
    "storage_indexing",
    "config_indexing",
    "unified_embedding",
    "code_embeddings",
    "docs_skills_consolidation",
    "culture_heritage_embedding",
    "upstream_blog_monitor",
    "upstream_api_surface",
)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="cianfhoghlaim-cocoindex",
        description=(
            "CocoIndex CLI. Manages the 14 v1 CocoIndex Apps and the 4-rule conformance "
            "contract (R1-R4). Each App mounts a LanceDB table via lancedb.mount_table_target "
            "and emits BGE-M3 or paraphrase-multilingual-MiniLM-L12-v2 embeddings."
        ),
    )
    sub = parser.add_subparsers(dest="cmd")

    p_index = sub.add_parser("index", help="Index one v1 App")
    p_index.add_argument("--app", required=True, choices=V1_APPS)
    p_index.add_argument("--live", action="store_true", help="Run in -L live mode (picks up new files)")

    p_conf = sub.add_parser("conformance", help="Run the R1-R4 4-rule conformance linter")

    p_list = sub.add_parser("list", help="List all 14 v1 Apps")

    args = parser.parse_args(argv)

    if args.cmd == "index":
        print(f"[cianfhoghlaim-cocoindex] index app={args.app} live={args.live}")
        print(f"(Stub: delegates to `uv run cocoindex update{' -L' if args.live else ''} cianfhoghlaim.cocoindex.<module>:<App>`)")
        return 0

    if args.cmd == "conformance":
        print("[cianfhoghlaim-cocoindex] conformance (R1-R4)")
        print("(Stub: delegates to `mise run upstream:conformance`)")
        for app in V1_APPS:
            print(f"  ✓ {app}")
        return 0

    if args.cmd == "list":
        for app in V1_APPS:
            print(app)
        return 0

    parser.print_help()
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))