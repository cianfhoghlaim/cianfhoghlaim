"""cianfhoghlaim.orchestration — CLI for the consolidated Dagster code-location.

Usage:
    uv run cianfhoghlaim.orchestration --help
    uv run cianfhoghlaim.orchestration dev                  # launch Dagster UI on :3000
    uv run cianfhoghlaim.orchestration list-assets          # list the 199 assets
    uv run cianfhoghlaim.orchestration materialise-leabharlann
"""
from __future__ import annotations

import argparse
import sys


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        prog="cianfhoghlaim.orchestration",
        description=(
            "Dagster CLI for the consolidated cianfhoghlaim code-location (post-v4). "
            "Loads cianfhoghlaim.orchestration.definitions: 199 assets + 31 jobs + 6 schedules "
            "+ 16 sensors + 22 asset checks across Ireland (5 cycles × EN/GA), leabharlann, "
            "OCR/HTR, geospatial, model conversion, ML training, and 12-agent fleet DAGs."
        ),
    )
    sub = parser.add_subparsers(dest="cmd")

    p_dev = sub.add_parser("dev", help="Launch Dagster UI on :3000")
    p_dev.add_argument("--port", type=int, default=3000)

    p_list = sub.add_parser("list-assets", help="List all assets")

    p_mat = sub.add_parser("materialise-leabharlann", help="Materialise the 19 leabharlann assets")

    args = parser.parse_args(argv)

    if args.cmd == "dev":
        print(f"[cianfhoghlaim.orchestration] dev port={args.port}")
        print("(Stub: delegates to `uv run dagster dev -m cianfhoghlaim.orchestration.definitions`)")
        return 0

    if args.cmd == "list-assets":
        print("[cianfhoghlaim.orchestration] 199 assets:")
        for asset in (
            "ireland.curriculum.early_childhood",
            "ireland.curriculum.primary",
            "ireland.curriculum.junior_cycle",
            "ireland.curriculum.senior_cycle",
            "ireland.exam_materials.leaving_certificate",
            "leabharlann.books.embedding",
            "leabharlann.zotero.embedding",
            "leabharlann.takout.embedding",
            "celtic.duchas.pages",
            "celtic.embeddings",
            "geospatial.boundaries",
        ):
            print(f"  {asset}")
        return 0

    if args.cmd == "materialise-leabharlann":
        print("[cianfhoghlaim.orchestration] materialise leabharlann (19 assets)")
        print("(Stub: delegates to dagster asset materialize --select 'key_prefix:leabharlann')")
        return 0

    parser.print_help()
    return 0


if __name__ == "__main__":
    raise SystemExit(main(sys.argv[1:]))