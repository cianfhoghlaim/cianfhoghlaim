#!/usr/bin/env python3
"""Restore dlt_sources.common.http_client — was missed by restore_dlt_sources_common.py.

The `restore_dlt_sources_common.py` script only knew about hardcoded
local common modules. The `http_client` (and any other `dlt_sources/common/`
module referenced from elsewhere in dlt_sources) wasn't included.

This script does a broad pass: every `dlt.common.X` reference inside
dlt_sources/ where X is a local module name (matches a file in
dlt_sources/common/) gets restored to `dlt_sources.common.X`.

Usage:
    python3 scripts/restore_dlt_sources_common_broad.py --dry-run
    python3 scripts/restore_dlt_sources_common_broad.py
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Restore dlt_sources.common.X for all X that exist locally"
    )
    parser.add_argument("--dry-run", action="store_true", help="Preview only")
    args = parser.parse_args()

    # Discover all module names that exist in dlt_sources/common/
    common_dir = REPO_ROOT / "dlt_sources" / "common"
    if not common_dir.is_dir():
        print(f"ERROR: {common_dir} not found", file=sys.stderr)
        return 1

    local_modules = sorted(
        [p.stem for p in common_dir.glob("*.py") if p.stem != "__init__"]
    )
    print(f"Found {len(local_modules)} local common modules: {local_modules[:5]}...")
    print()

    # Build a pattern that matches `dlt.common.<local_module>` (not
    # followed by another `.` — to avoid matching e.g. `dlt.common.foo.bar`
    # which would be a real dlt submodule).
    module_pattern = "|".join(re.escape(m) for m in local_modules)
    PATTERN = re.compile(rf"\bdlt\.common\.({module_pattern})\b(?![\w.])")

    files_changed = 0
    total_replacements = 0
    for path in (REPO_ROOT / "dlt_sources").rglob("*.py"):
        try:
            src = path.read_text()
        except (UnicodeDecodeError, OSError):
            continue
        new, count = PATTERN.subn(rf"dlt_sources.common.\1", src)
        if count > 0:
            if not args.dry_run:
                path.write_text(new)
            print(f"  [{'DRY' if args.dry_run else 'ok'} ] {path.relative_to(REPO_ROOT)}: {count}")
            files_changed += 1
            total_replacements += count

    print()
    print(f"Summary: {files_changed} file(s) changed, {total_replacements} replacement(s)")
    if args.dry_run:
        print("(dry-run — no files were written)")
    return 0


if __name__ == "__main__":
    sys.exit(main())