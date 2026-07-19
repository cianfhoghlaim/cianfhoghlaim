#!/usr/bin/env python3
"""Restore dlt_sources.common (local) — was over-reverted by the previous script.

The `revert_dlt_1x_submodule_imports.py` script was overly aggressive
and reverted `dlt_sources.common.*` back to `dlt.common.*` — but
`dlt_sources.common.*` are OUR local modules (not real dlt 1.x).

This script re-restores:
  `dlt.common.{local_module}`  →  `dlt_sources.common.{local_module}`

For these specific local modules:
- endpoint_recovery
- content_deduplication
- (and any other local common/ module)

Usage:
    python3 scripts/restore_dlt_sources_common.py --dry-run
    python3 scripts/restore_dlt_sources_common.py
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]

# Local modules in dlt_sources/common/ that should be restored
LOCAL_COMMON_MODULES = (
    "endpoint_recovery",
    "content_deduplication",
    "destinations_cianfhoghlaim",
    "destinations_tuatha",
    "destinations_croilar",
    "motherduck_options",
    "motherduck_snapshots",
    "ducklake_options",
    "ducklake_pool",
    "iceberg_options",
    "named_destinations",
    "batching",
    "endpoint_recovery",
    "cocoindex_v1_migrate",
    "content_deduplication",
    "crawl_utils",
    "curriculum_registry",
    "_shared_utils_stub",
    "_http_factories",
    "cli",
)


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Restore dlt_sources.common imports"
    )
    parser.add_argument("--dry-run", action="store_true", help="Preview only")
    args = parser.parse_args()

    # Build pattern: `dlt.common.<known_local_module>`
    module_pattern = "|".join(re.escape(m) for m in LOCAL_COMMON_MODULES)
    PATTERN = re.compile(rf"\bdlt\.common\.({module_pattern})\b")

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