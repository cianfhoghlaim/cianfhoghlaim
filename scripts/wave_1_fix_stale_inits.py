#!/usr/bin/env python3
"""
Wave 1 stale __init__.py fixer.

After the migration, some `__init__.py` files in the new domain-first
locations still contain imports referencing the old jurisdiction-first
paths (e.g. `from dlt_sources.commonwealth.nga.law import nass` when the
actual location is now `dlt_sources.law.nigeria.commonwealth.nass`).

This script identifies and fixes these stale imports by:
1. Removing imports that reference the old jurisdiction-first paths
2. Adding a `from . import <local_module>` line for each .py sibling
3. Building `__all__` from the local .py file names

Usage:
    uv run python scripts/wave_1_fix_stale_inits.py [--dry-run]
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

PROJECT_ROOT = Path("/Users/cianmacandeisigh/dev/cianfhoghlaim")
DLT = PROJECT_ROOT / "dlt_sources"

# Pattern: `from dlt_sources.<old_path> import <something>`
# Matches ISO-3 short codes (2-4 letters like nga, fra, pol, aus) AND any
# dlt_sources.<x>.<y>.<z> chain that doesn't match the new domain-first layout.
STALE_IMPORT_RE = re.compile(
    r"^\s*from\s+dlt_sources\.[a-z_]+\.[a-z_]+(?:\.[a-z_]+)*\s+import\s+",
    re.MULTILINE,
)
# Also catch bare 2-3-letter package refs
STALE_IMPORT_RE_SHORT = re.compile(
    r"^\s*from\s+dlt_sources\.[a-z_]{2,4}\.[a-z_]+\s+import\s+",
    re.MULTILINE,
)


def is_migrated_init(init_path: Path) -> bool:
    """Check if an __init__.py is in a migrated location and has stale imports."""
    if not init_path.is_file():
        return False
    text = init_path.read_text()
    rel = init_path.relative_to(DLT)
    parts = rel.parts
    new_domains = {
        "law", "medicine", "education", "lexicographic", "cultural_heritage",
        "local_archive", "media_text", "media_comics", "media_games",
        "media_personal", "crypteolas_chain", "crypteolas_docs",
        "crypteolas_defi", "raw_files", "cv", "artwork", "labels",
        "api_documentation", "api_github", "api_local",
    }
    # In a new domain dir → candidate for stale imports
    if len(parts) >= 2 and parts[0] in new_domains:
        return True
    # In a legacy geographic dir (e.g. british_isles/england/law/__init__.py)
    # — only fix if there's a stale import
    legacy_geos = {"american_nations", "british_isles", "commonwealth",
                   "european_nations", "european_union", "celtic"}
    if len(parts) >= 2 and parts[0] in legacy_geos:
        return bool(STALE_IMPORT_RE.search(text) or STALE_IMPORT_RE_SHORT.search(text))
    # In a themed legacy dir (language/, media/, api_sources/, crypteolas/,
    # apple_photos/, filesystem/, portfolio/)
    themed_legacies = {"language", "media", "api_sources", "crypteolas",
                       "apple_photos", "filesystem", "portfolio"}
    if len(parts) >= 1 and parts[0] in themed_legacies:
        return bool(STALE_IMPORT_RE.search(text) or STALE_IMPORT_RE_SHORT.search(text))
    return False


def find_local_modules(init_path: Path) -> list[str]:
    """Find sibling .py files (excluding __init__.py)."""
    return sorted([
        f.stem for f in init_path.parent.glob("*.py")
        if f.stem != "__init__"
    ])


def fix_init(init_path: Path, dry_run: bool = False) -> bool:
    """Fix a stale __init__.py. Returns True if changed."""
    text = init_path.read_text()
    # Check for stale imports
    stale_matches = STALE_IMPORT_RE.findall(text)
    if not stale_matches:
        return False

    local_modules = find_local_modules(init_path)

    # Build the new __init__.py content
    if local_modules:
        imports = "\n".join(f"from . import {mod}  # noqa: F401" for mod in local_modules)
        new_content = f'''"""{init_path.parent.relative_to(PROJECT_ROOT)} — DLT sources.

Per the **2026-08-24-wave-1-dlt-sources-domain-restructure-v1** openspec
change, this package was migrated from its legacy jurisdiction-first
location. The `__init__.py` re-exports the local source modules.

Legacy import paths still work via re-export shims at the old locations.
"""
from __future__ import annotations

{imports}

__all__ = {local_modules!r}
'''
    else:
        # No local modules — just an empty package marker
        new_content = f'''"""{init_path.parent.relative_to(PROJECT_ROOT)} — DLT sources (empty).

Per the **2026-08-24-wave-1-dlt-sources-domain-restructure-v1** openspec
change, this package was migrated from its legacy jurisdiction-first
location.
"""
from __future__ import annotations

__all__ = []
'''

    if not dry_run:
        init_path.write_text(new_content)
    return True


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    fixed_count = 0
    scanned = 0
    for init_path in DLT.rglob("__init__.py"):
        scanned += 1
        text = init_path.read_text()
        # Always check for stale imports regardless of location
        if not (STALE_IMPORT_RE.search(text) or STALE_IMPORT_RE_SHORT.search(text)):
            continue
        # Make sure the file is in a candidate location
        if not is_migrated_init(init_path):
            continue
        if fix_init(init_path, dry_run=args.dry_run):
            fixed_count += 1
            mode = "DRY" if args.dry_run else "FIXED"
            print(f"  [{mode}] {init_path.relative_to(PROJECT_ROOT)}")
            local = find_local_modules(init_path)
            print(f"         local modules: {local}")

    print()
    print(f"Scanned: {scanned} __init__.py files")
    print(f"Fixed: {fixed_count} stale inits")
    return 0


if __name__ == "__main__":
    sys.exit(main())
