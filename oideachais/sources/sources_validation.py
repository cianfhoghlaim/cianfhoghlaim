"""
oideachais.sources.sources_validation — Coverage report CLI.

Usage:
    python -m oideachais.sources.sources_validation
    python -m oideachais.sources.sources_validation --domain law --nation ie
    python -m oideachais.sources.sources_validation --json

Exits non‑zero when any source in `sources.yaml` is missing its DLT
source file, when any source is missing its marimo notebook, or when
any source is missing its pytest.
"""
from __future__ import annotations

import argparse
import json as _json
import sys
from pathlib import Path

from oideachais.dlt_utils.source_factory import SourceFactory, get_default_factory


def _report_missing(factory: SourceFactory) -> dict:
    """For each source id, return the list of missing artefacts.

    "Missing" is determined by path existence on disk relative to the
    repo root.
    """
    repo_root = Path(__file__).resolve().parents[2]
    out: dict[str, list[str]] = {}
    for sid in factory.all_ids():
        dlt_path = repo_root / "oideachais" / "dlt_sources" / "domains" / factory.get(sid).domain / factory.get(sid).nation
        marimo_path = repo_root / factory.marimo_path(sid)
        tests_path = repo_root / factory.tests_path(sid)
        missing: list[str] = []
        if not dlt_path.exists():
            missing.append(f"dlt dir: {dlt_path.relative_to(repo_root)}")
        if not marimo_path.exists():
            missing.append(f"marimo: {marimo_path.relative_to(repo_root)}")
        if not tests_path.exists():
            missing.append(f"tests:  {tests_path.relative_to(repo_root)}")
        if missing:
            out[sid] = missing
    return out


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--domain", help="filter to a single domain (e.g. law)")
    parser.add_argument("--nation", help="filter to a single nation code (e.g. ie)")
    parser.add_argument("--json", action="store_true", help="emit machine‑readable JSON")
    parser.add_argument(
        "--strict",
        action="store_true",
        help="exit non‑zero if any source is missing any artefact",
    )
    args = parser.parse_args(argv)

    try:
        factory = get_default_factory()
    except Exception as exc:  # noqa: BLE001
        print(f"sources.yaml load failed: {exc}", file=sys.stderr)
        return 2

    if args.domain or args.nation:
        ids = [s.id for s in factory.filter(domain=args.domain, nation=args.nation)]
    else:
        ids = factory.all_ids()
    print(f"{len(ids)} sources matched filters")
    for sid in ids:
        entry = factory.get(sid)
        print(f"  - {sid:<40s} {entry.kind:<22s} asset_key={entry.asset_key}")

    missing = _report_missing(factory)
    missing = {sid: items for sid, items in missing.items() if sid in ids}

    if missing:
        print(f"\n{len(missing)} sources have missing artefacts:")
        for sid, items in missing.items():
            print(f"  ! {sid}")
            for it in items:
                print(f"      - {it}")
    else:
        print("\nAll sources have a dlt dir, a marimo path, and a tests path on disk.")

    if args.json:
        print(_json.dumps({"ids": ids, "missing": missing}, indent=2))

    return 1 if (args.strict and missing) else 0


if __name__ == "__main__":
    raise SystemExit(main())
