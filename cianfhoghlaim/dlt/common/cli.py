"""cianfhoghlaim-dlt — CLI for the DLT ingestion sources + destination factory.

Usage:
    uv run cianfhoghlaim-dlt --help
    uv run cianfhoghlaim-dlt run-pipeline --target dev
    uv run cianfhoghlaim-dlt list-sources
"""
from __future__ import annotations

import argparse
import sys


# Canonical DLT sources exposed by `cianfhoghlaim.dlt`. See dlt/__init__.py.
DLT_SOURCES = (
    "logainm_placenames",
    "tearma_terminology",
    "ainm_biographies",
    "gaois_combined",
    "duchas_folklore",
    "duchas_images",
    "canuint_pronunciation",
    "canuint_audio_download",
    "universal_dependencies",
    "author_archive_uog",
    "author_archive_gemini",
    "author_archive_takout",
    "leabharlann_books",
    "leabharlann_zotero",
    "leabharlann_takeout",
    "leabharlann_email_inbox",
    "upstream_blog_post",
    "instagram_export",
    "linkedin_profiles",
    "github_repos",
    "spotify_api",
    "soundcloud_scraper",
)


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="cianfhoghlaim-dlt",
        description=(
            "DLT CLI. Manages the 30+ dlt sources (Ireland + UK + Celtic + leabharlann + "
            "official-media + croilar streams) and the 3-target destination factory "
            "(DEV = local DuckDB; STAGING = MotherDuck BYOB; PROD = Garage S3 + Lakekeeper)."
        ),
    )
    sub = parser.add_subparsers(dest="cmd")

    p_run = sub.add_parser("run-pipeline", help="Run a DLT pipeline against a target")
    p_run.add_argument("--target", choices=("dev", "staging", "prod"), default="dev")
    p_run.add_argument("--source", help="Source name to run (default: all)")

    p_list = sub.add_parser("list-sources", help="List all DLT sources")

    args = parser.parse_args(argv)

    if args.cmd == "run-pipeline":
        print(f"[cianfhoghlaim-dlt] run-pipeline target={args.target} source={args.source}")
        print(f"(Stub: delegates to mise run {'cic:dlt:dev-pipeline' if args.target == 'dev' else f'cic:dlt:{args.target}-pipeline'})")
        return 0

    if args.cmd == "list-sources":
        for src in DLT_SOURCES:
            print(src)
        return 0

    parser.print_help()
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))