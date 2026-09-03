#!/usr/bin/env python3
"""Bulk-fix stale pre-v7 imports to v7-flattened paths.

Per the 2026-08-13 Phase A plan: get Dagster defs/assets materialised
on Dagster 1.10.9. The v7 flattening removed the cianfhoghlaim Python
package. The orchestration/defs/ + orchestration/components/ trees still
reference these stale paths.

Usage:
    python3 scripts/fix_v7_orchestration_imports.py --dry-run
    python3 scripts/fix_v7_orchestration_imports.py
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
TARGET_DIRS = ["orchestration"]

# (broken_prefix, target_prefix)
REWRITES = [
    ("cianfhoghlaim.orchestration.", "orchestration."),
    ("cianfhoghlaim.core.dlt._cianfhoghlaim_dlt_utils.", "dlt_sources.common."),
    ("cianfhoghlaim.core.dlt.", "dlt_sources.common."),
    ("cianfhoghlaim.meaisinfhoghlaim.", "meaisinfhoghlaim."),
    ("cianfhoghlaim.cocoindex.", "cocoindex."),
    ("cianfhoghlaim.baml_client", "baml_client"),
    ("cianfhoghlaim.tuatha.", "tuatha."),
    ("cianfhoghlaim.croilar.", "croilar."),
    ("cianfhoghlaim.agents.", "agents."),
    ("cianfhoghlaim.ocr.", "ocr."),
    ("cianfhoghlaim.dlt.", "dlt."),
]

SUBMODULES = tuple(s for s, _ in REWRITES)
SUBMODULE_PATTERN = "|".join(re.escape(s) for s in SUBMODULES)
PATTERN_FROM = re.compile(
    r"^(\s*)from (" + SUBMODULE_PATTERN + r")([\w.]*)?(\s+import\s+.+)$",
    re.MULTILINE,
)
PATTERN_IMPORT = re.compile(
    r"^(\s*)import (" + SUBMODULE_PATTERN + r")([\w.]*)?(\s+as\s+\w+)?$",
    re.MULTILINE,
)
REWRITE_MAP = dict(REWRITES)


def _repl_from(m):
    prefix, sub, rest, tail = m.groups()
    return f"{prefix}from {REWRITE_MAP[sub]}{rest or ""}{tail}"


def _repl_import(m):
    prefix, sub, rest, alias = m.groups()
    return f"{prefix}import {REWRITE_MAP[sub]}{rest or ""}{alias or ""}"


def fix_one(path, *, dry_run):
    try:
        src = path.read_text()
    except (UnicodeDecodeError, OSError) as e:
        print(f"  [SKIP] {path.relative_to(REPO_ROOT)}: {e}", file=sys.stderr)
        return 0
    new = src
    new, n1 = PATTERN_FROM.subn(_repl_from, new)
    new, n2 = PATTERN_IMPORT.subn(_repl_import, new)
    count = n1 + n2
    if count > 0 and not dry_run:
        path.write_text(new)
    if count > 0:
        print(f"  [{"DRY" if dry_run else "ok"}] {path.relative_to(REPO_ROOT)}: {count} replacement(s)")
    return count


def main():
    p = argparse.ArgumentParser()
    p.add_argument("--dry-run", action="store_true")
    p.add_argument("--dirs", nargs="+", default=TARGET_DIRS)
    args = p.parse_args()
    fc = tr = 0
    for t in args.dirs:
        d = REPO_ROOT / t
        if not d.is_dir():
            continue
        for f in d.rglob("*.py"):
            n = fix_one(f, dry_run=args.dry_run)
            if n > 0:
                fc += 1
                tr += n
    print(f"\nSummary: {fc} file(s) changed, {tr} replacement(s)")
    if args.dry_run:
        print("(dry-run - no files were written)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
