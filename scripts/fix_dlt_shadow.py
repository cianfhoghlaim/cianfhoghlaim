#!/usr/bin/env python3
"""Bulk-fix `from dlt.X` and `import dlt.X` references to use `dlt_sources.X`.

Per the 2026-08-13 BIEP v3 lakehouse full activation plan (Phase 1):

The local `dlt/` directory was renamed to `dlt_sources/` to fix the
Python package shadowing issue (the real `dlt` PyPI package was being
shadowed by the local `dlt/__init__.py`, which exposed only
`british_isles` + `common` instead of the real dlt 1.29.0 features
like `@dlt.source`, `@dlt.resource`, `pipeline()`).

After renaming the directory, every Python file that referenced the
old `dlt.X` import paths needs to be rewritten to `dlt_sources.X`.

This script walks all .py files under the repo and rewrites:
- `from dlt.X import Y`  →  `from dlt_sources.X import Y`
- `import dlt.X`         →  `import dlt_sources.X`
- `from dlt import X`     →  `from dlt_sources import X` (the package-level)
- `import dlt`           →  `import dlt_sources` (only when it's a local
   package reference; the `dlt` PyPI package is imported via
   `scripts/bootstrap_dlt.py` which now becomes unnecessary)

Usage:
    python3 scripts/fix_dlt_shadow.py --dry-run  # preview
    python3 scripts/fix_dlt_shadow.py            # apply
"""
from __future__ import annotations

import argparse
import os
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]

# Directories to scan. The `dlt_sources/` directory itself is scanned
# because it still contains references to itself (e.g., cross-references
# between `dlt_sources.british_isles._cross.registry_api` and
# `dlt_sources.british_isles._cross.registry_loader`).
TARGET_DIRS = [
    "dlt_sources", "orchestration", "baml_src", "motherduck",
    "cocoindex", "meaisinfhoghlaim", "agents", "notebooks",
    "scripts", "tests",
]

# Patterns to rewrite:
#   `from dlt.<X> import <Y>`    →  `from dlt_sources.<X> import <Y>`
#   `import dlt.<X>`              →  `import dlt_sources.<X>`
#   `from dlt import <Y>`         →  `from dlt_sources import <Y>` (the package)
#   `import dlt`                  →  `import dlt_sources` (only if not part of an absolute import already)

# Pattern 1: `from dlt.<X> import <Y>` where X is one or more dotted segments
PATTERN_FROM_DOTTED = re.compile(r"^(\s*)from dlt(\.[\w.]+)?(\s+import\s+.+)$", re.MULTILINE)
# Pattern 2: `import dlt.<X>` or `import dlt.<X> as Y`
PATTERN_IMPORT_DOTTED = re.compile(r"^(\s*)import dlt(\.[\w.]+)?(\s+as\s+\w+)?$", re.MULTILINE)
# Pattern 3: `from dlt import Y` (the package-level)
PATTERN_FROM_PKG = re.compile(r"^(\s*)from dlt(\s+import\s+.+)$", re.MULTILINE)
# Pattern 4: `import dlt` (the package-level)
PATTERN_IMPORT_PKG = re.compile(r"^(\s*)import dlt(\s+as\s+\w+)?$", re.MULTILINE)


def fix_one(path: Path, *, dry_run: bool) -> int:
    """Rewrite one file. Returns count of replacements."""
    try:
        src = path.read_text()
    except (UnicodeDecodeError, OSError) as e:
        print(f"  [SKIP] {path.relative_to(REPO_ROOT)}: {e}", file=sys.stderr)
        return 0

    new = src
    new, n1 = PATTERN_FROM_DOTTED.subn(r"\1from dlt_sources\2\3", new)
    new, n2 = PATTERN_IMPORT_DOTTED.subn(r"\1import dlt_sources\2\3", new)
    new, n3 = PATTERN_FROM_PKG.subn(r"\1from dlt_sources\2", new)
    new, n4 = PATTERN_IMPORT_PKG.subn(r"\1import dlt_sources\2", new)

    count = n1 + n2 + n3 + n4
    if count > 0 and not dry_run:
        path.write_text(new)

    if count > 0:
        print(f"  [{'DRY' if dry_run else 'ok'} ] {path.relative_to(REPO_ROOT)}: {count} replacement(s)")
    return count


def main() -> int:
    parser = argparse.ArgumentParser(description="Bulk-fix dlt → dlt_sources imports")
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