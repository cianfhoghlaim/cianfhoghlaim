#!/usr/bin/env python3
"""Bulk-fix stale `from cianfhoghlaim.dlt.X` imports to `from dlt.X`.

Per the v7 flattened layout, the `cianchoghlaim/dlt/` sub-directory was
removed and the dlt sub-package now lives at the repo root (so
`cianchoghlaim.dlt.X` → `dlt.X`).

This script:
1. Walks all .py files under dlt/, orchestration/, baml_src/, motherduck/, cocoindex/, meaisinfhoghlaim/, agents/
2. For each match of `from cianfhoghlaim.dlt.<X> import <Y>`, rewrites to `from dlt.<X> import <Y>`
3. For each match of `import cianfhoghlaim.dlt.<X>`, rewrites to `import dlt.<X>`
4. For each match of `import cianfhoghlaim` (without `.dlt`), leaves it alone (those imports are valid post-v7)

Usage:
    python3 scripts/fix_v7_imports.py --dry-run  # preview
    python3 scripts/fix_v7_imports.py            # apply
"""
from __future__ import annotations

import argparse
import os
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]

# Directories to scan
TARGET_DIRS = [
    "dlt", "orchestration", "baml_src", "motherduck", "cocoindex",
    "meaisinfhoghlaim", "agents", "notebooks", "scripts",
]

# Patterns to rewrite:
#   from cianfhoghlaim.dlt.<X> import <Y>  →  from dlt.<X> import <Y>
#   import cianfhoghlaim.dlt.<X>           →  import dlt.<X>
PATTERN_FROM = re.compile(r"^(\s*)from cianfhoghlaim\.dlt(\.[\w.]+)?(\s+import\s+.+)$", re.MULTILINE)
PATTERN_IMPORT = re.compile(r"^(\s*)import cianfhoghlaim\.dlt(\.[\w.]+)?(\s+as\s+\w+)?$", re.MULTILINE)


def fix_one(path: Path, *, dry_run: bool) -> int:
    """Rewrite one file. Returns count of replacements."""
    try:
        src = path.read_text()
    except (UnicodeDecodeError, OSError) as e:
        print(f"  [SKIP] {path.relative_to(REPO_ROOT)}: {e}", file=sys.stderr)
        return 0

    new = src
    new, n1 = PATTERN_FROM.subn(r"\1from dlt\2\3", new)
    new, n2 = PATTERN_IMPORT.subn(r"\1import dlt\2\3", new)

    count = n1 + n2
    if count > 0 and not dry_run:
        path.write_text(new)

    if count > 0:
        print(f"  [{'DRY' if dry_run else 'ok'} ] {path.relative_to(REPO_ROOT)}: {count} replacement(s)")
    return count


def main() -> int:
    parser = argparse.ArgumentParser(description="Bulk-fix stale v7 flattened imports")
    parser.add_argument("--dry-run", action="store_true", help="Preview only")
    parser.add_argument("--dirs", nargs="+", default=TARGET_DIRS,
                        help=f"Directories to scan (default: {TARGET_DIRS})")
    args = parser.parse_args()

    files_changed = 0
    total_replacements = 0
    for target in args.dirs:
        target_dir = REPO_ROOT / target
        if not target_dir.is_dir():
            continue
        for path in target_dir.rglob("*.py"):
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