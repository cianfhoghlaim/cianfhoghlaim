#!/usr/bin/env python3
"""Reverse-fix: restore dlt_sources.{dlt_1.x_submodule} back to dlt.{submodule}.

Per the 2026-08-13 BIEP v3 lakehouse full activation plan (Phase 1.5):

The `fix_dlt_shadow.py` script over-zealously rewrote `from dlt.X`
references to `from dlt_sources.X`, but some `X` values are real
dlt 1.x submodules (e.g., `dlt.sources.rest_api`,
`dlt.destinations.impl.ducklake.configuration`,
`dlt.pipeline.*`, `dlt.extract.*`, etc.). These references must be
RESTORED to `dlt.X` because `dlt_sources.X` doesn't exist for
those submodules.

Known dlt 1.x top-level submodules:
- dlt.sources
- dlt.destinations
- dlt.pipeline
- dlt.extract
- dlt.normalize
- dlt.load
- dlt.transformers
- dlt.common.* (note: this conflicts with our local dlt_sources.common!)

This script walks all .py files and reverts:
  `dlt_sources.<known_submodule>` → `dlt.<known_submodule>`

Usage:
    python3 scripts/revert_dlt_1x_submodule_imports.py --dry-run
    python3 scripts/revert_dlt_1x_submodule_imports.py
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]

# Submodules of `dlt` 1.x that should be reverted
DLT_1X_SUBMODULES = (
    "sources",
    "destinations",
    "pipeline",
    "extract",
    "normalize",
    "load",
    "transformers",
    "common",
)

# Build a regex that matches `dlt_sources.<known_submodule>` (with optional
# dotted suffixes) and replaces it with `dlt.<known_submodule>`.
_SUBMODULE_PATTERN = "|".join(re.escape(s) for s in DLT_1X_SUBMODULES)
PATTERN = re.compile(rf"dlt_sources\.({_SUBMODULE_PATTERN})(\b|\.)")


def fix_one(path: Path, *, dry_run: bool) -> int:
    """Rewrite one file. Returns count of replacements."""
    try:
        src = path.read_text()
    except (UnicodeDecodeError, OSError) as e:
        print(f"  [SKIP] {path.relative_to(REPO_ROOT)}: {e}", file=sys.stderr)
        return 0

    new = src
    new, count = PATTERN.subn(r"dlt.\1\2", new)

    if count > 0 and not dry_run:
        path.write_text(new)

    if count > 0:
        print(f"  [{'DRY' if dry_run else 'ok'} ] {path.relative_to(REPO_ROOT)}: {count} replacement(s)")
    return count


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Revert dlt_sources.{dlt_1.x_submodule} back to dlt.{submodule}"
    )
    parser.add_argument("--dry-run", action="store_true", help="Preview only")
    args = parser.parse_args()

    files_changed = 0
    total_replacements = 0
    for path in (REPO_ROOT / "dlt_sources").rglob("*.py"):
        n = fix_one(path, dry_run=args.dry_run)
        if n > 0:
            files_changed += 1
            total_replacements += n

    print()
    print(f"Summary: {files_changed} file(s) changed, {total_replacements} replacement(s)")
    if args.dry_run:
        print("(dry-run — no files were written)")
    return 0


if __name__ == "__main__":
    sys.exit(main())