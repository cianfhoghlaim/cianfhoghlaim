#!/usr/bin/env python3
"""Add `import dlt` to files that use @dlt.* decorators but don't import dlt.

Per the 2026-08-13 BIEP v3 lakehouse full activation plan (Phase 1.5):

After renaming `dlt/` → `dlt_sources/`, the old re-export pattern
(the old `dlt/__init__.py` re-exported `dlt.source`, `dlt.resource`,
`dlt.pipeline`, etc.) no longer applies. Files that use the decorators
now need explicit `import dlt` to bring in the real dlt 1.x symbols.

This script:
1. Walks every .py file under dlt_sources/
2. For each file that uses `@dlt.<something>(` decorators but doesn't
   have `import dlt` (anywhere in the file), prepends `import dlt`
   to the imports block.

Usage:
    python3 scripts/add_dlt_imports.py --dry-run
    python3 scripts/add_dlt_imports.py
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]

# Match `@dlt.X(...)` decorator usages (X must start with a word char)
DLT_DECORATOR = re.compile(r"@dlt\.(\w+)\s*\(")
# Match an `import dlt` (line) statement
IMPORT_DLT_RE = re.compile(r"^\s*import dlt\s*$", re.MULTILINE)


def needs_dlt_import(src: str) -> bool:
    """True if the file uses @dlt.X decorators but lacks `import dlt`."""
    if not DLT_DECORATOR.search(src):
        return False
    if IMPORT_DLT_RE.search(src):
        return False
    return True


def add_import(src: str) -> str:
    """Prepend `import dlt` after the last `from __future__ import` line
    (or at the top if no future import)."""
    if not needs_dlt_import(src):
        return src
    # Find the `from __future__ import ...` line(s) block
    future_pattern = re.compile(
        r"((?:^from __future__ import [^\n]+\n)+)", re.MULTILINE
    )
    m = future_pattern.search(src)
    insertion = "import dlt\n\n"
    if m:
        return src[: m.end()] + insertion + src[m.end():]
    return insertion + src


def fix_one(path: Path, *, dry_run: bool) -> int:
    """Rewrite one file. Returns 1 if modified, 0 if not."""
    try:
        src = path.read_text()
    except (UnicodeDecodeError, OSError) as e:
        print(f"  [SKIP] {path.relative_to(REPO_ROOT)}: {e}", file=sys.stderr)
        return 0
    if not needs_dlt_import(src):
        return 0
    new = add_import(src)
    if new != src and not dry_run:
        path.write_text(new)
    print(f"  [{'DRY' if dry_run else 'ok'} ] {path.relative_to(REPO_ROOT)}")
    return 1


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Add `import dlt` to files using @dlt.* decorators"
    )
    parser.add_argument("--dry-run", action="store_true", help="Preview only")
    parser.add_argument(
        "--dirs", nargs="+", default=["dlt_sources"],
        help="Directories to scan (default: dlt_sources)",
    )
    args = parser.parse_args()

    files_changed = 0
    for target in args.dirs:
        target_dir = REPO_ROOT / target
        if not target_dir.is_dir():
            continue
        for path in target_dir.rglob("*.py"):
            files_changed += fix_one(path, dry_run=args.dry_run)

    print()
    print(f"Summary: {files_changed} file(s) changed")
    if args.dry_run:
        print("(dry-run — no files were written)")
    return 0


if __name__ == "__main__":
    sys.exit(main())