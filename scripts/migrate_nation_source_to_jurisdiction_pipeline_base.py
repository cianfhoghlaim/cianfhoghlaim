"""Bulk-rewrite the 51 per-nation DLT source files to import
``JurisdictionPipelineBase`` from the canonical British-Isles location
instead of the legacy ``NationSource`` shim.

Per the 2026-08-24-dlt-sources-to-multi-repo-scaffold-v1 §11 change.

For each importer:
  1. Replace the import block
     ``from dlt_sources.european_nations._shared.nation_source import (NationSource, row_from_cache, use_local_scrapes)``
     with
     ``from dlt_sources.british_isles._cross.jurisdiction_pipeline_base import (JurisdictionPipelineBase, row_from_cache, use_local_scrapes)``
  2. Replace every ``(NationSource)`` base class with
     ``(JurisdictionPipelineBase)``.

The script is idempotent (re-runs are no-ops on already-rewritten
files because the legacy import path is not present any more).

Usage:
    python scripts/migrate_nation_source_to_jurisdiction_pipeline_base.py [--dry-run]
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

REPO_ROOT = Path("/Users/cianmacandeisigh/dev/cianfhoghlaim")

OLD_IMPORT_PATTERN = re.compile(
    r"from dlt_sources\.european_nations\._shared\.nation_source import \("
    r"\s*\n"
    r"\s*NationSource,\s*\n"
    r"\s*row_from_cache,\s*\n"
    r"\s*use_local_scrapes,\s*\n"
    r"\)",
)
NEW_IMPORT = (
    "from dlt_sources.british_isles._cross.jurisdiction_pipeline_base import (\n"
    "    JurisdictionPipelineBase,\n"
    "    row_from_cache,\n"
    "    use_local_scrapes,\n"
    ")"
)

# Match `class Foo(NationSource):` declarations (with any leading
# whitespace + no other inheritance content).
BASE_CLASS_PATTERN = re.compile(r"^(\s*)class\s+\w+\(NationSource\)(\s*:)", re.MULTILINE)


def rewrite_file(path: Path) -> tuple[bool, str]:
    """Return (changed, new_text) for one importer file."""
    original = path.read_text(encoding="utf-8")
    new = original

    new = OLD_IMPORT_PATTERN.sub(NEW_IMPORT, new)

    new = BASE_CLASS_PATTERN.sub(
        lambda m: f"{m.group(1)}class {m.group(0).split('class ', 1)[1].split('(', 1)[0]}(JurisdictionPipelineBase){m.group(2)}",
        new,
    )

    return (new != original, new)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true", help="show diffs but don't write")
    parser.add_argument("--files", nargs="*", help="restrict to these files (default: all 51 importers)")
    args = parser.parse_args()

    if args.files:
        files = []
        for p in args.files:
            pp = Path(p)
            if not pp.is_absolute():
                pp = REPO_ROOT / pp
            files.append(pp)
    else:
        # Discover via grep
        out = []
        from subprocess import check_output
        grep = check_output(
            [
                "git",
                "grep",
                "-lE",
                "from dlt_sources\\.european_nations\\._shared\\.nation_source",
                "--",
                "*.py",
            ],
            cwd=str(REPO_ROOT),
            text=True,
        )
        for line in grep.splitlines():
            out.append(REPO_ROOT / line)
        files = out

    if not files:
        print("No importer files found.")
        return 1

    changed_count = 0
    unchanged_count = 0
    for f in files:
        if not f.is_file():
            print(f"  SKIP (not a file): {f}")
            continue
        changed, new_text = rewrite_file(f)
        if changed:
            changed_count += 1
            if args.dry_run:
                print(f"  WOULD-CHANGE: {f.relative_to(REPO_ROOT)}")
            else:
                f.write_text(new_text, encoding="utf-8")
                print(f"  CHANGED: {f.relative_to(REPO_ROOT)}")
        else:
            unchanged_count += 1
            print(f"  unchanged: {f.relative_to(REPO_ROOT)}")

    print()
    print(f"Total files: {len(files)}")
    print(f"  changed:   {changed_count}")
    print(f"  unchanged: {unchanged_count}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
