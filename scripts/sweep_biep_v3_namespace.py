#!/usr/bin/env python3
"""BIEP v3 namespace sweep — replaces `md:oideachais` with `md:cianfhoghlaim`
across all notebooks under notebooks/.

Per the 2026-08-11-biep-v3-lakehouse-population-v1 openspec change.

This script:
1. Walks every `*.py` file under notebooks/ (recursively).
2. For each file, replaces the literal string `md:oideachais` with
   `md:cianfhoghlaim`.
3. Writes the file back iff a change was made.
4. Reports the count of files changed + the count of replacements.

The canonical target namespace is `md:cianfhoghlaim` per
`notebooks/_shared/db.py:26: LAKEHOUSE_URI_DEFAULT = "md:cianfhoghlaim"`.

Usage:
    python scripts/sweep_biep_v3_namespace.py
    python scripts/sweep_biep_v3_namespace.py --dry-run
"""
from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path

# The repo-root notebooks directory
REPO_ROOT = Path(__file__).resolve().parents[1]
NOTEBOOKS_DIR = REPO_ROOT / "notebooks"

# The canonical BIEP v3 namespace sweep: oideachais → cianfhoghlaim
OLD_NS = "md:oideachais"
NEW_NS = "md:cianfhoghlaim"


def sweep_one(path: Path, *, dry_run: bool) -> tuple[int, int]:
    """Sweep one file. Returns (files_with_changes, total_replacements)."""
    try:
        src = path.read_text()
    except (UnicodeDecodeError, OSError) as e:
        print(f"  [SKIP] {path.relative_to(REPO_ROOT)}: {e}", file=sys.stderr)
        return 0, 0

    count = src.count(OLD_NS)
    if count == 0:
        return 0, 0

    new = src.replace(OLD_NS, NEW_NS)
    if not dry_run:
        path.write_text(new)
    print(f"  [ok]   {path.relative_to(REPO_ROOT)}: {count} replacement(s)")
    return 1, count


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Sweep md:oideachais → md:cianfhoghlaim across notebooks/",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Don't write changes; just report what would change.",
    )
    parser.add_argument(
        "--dir",
        default=str(NOTEBOOKS_DIR),
        help=f"Notebooks directory (default: {NOTEBOOKS_DIR})",
    )
    args = parser.parse_args()

    notebooks_dir = Path(args.dir).resolve()
    if not notebooks_dir.is_dir():
        print(f"ERROR: {notebooks_dir} is not a directory", file=sys.stderr)
        return 1

    files_changed = 0
    total_replacements = 0
    for path in sorted(notebooks_dir.rglob("*.py")):
        fc, tr = sweep_one(path, dry_run=args.dry_run)
        files_changed += fc
        total_replacements += tr

    print()
    print(f"Summary: {files_changed} file(s) changed, {total_replacements} replacement(s)")
    if args.dry_run:
        print("(dry-run — no files were written)")
    return 0


if __name__ == "__main__":
    sys.exit(main())