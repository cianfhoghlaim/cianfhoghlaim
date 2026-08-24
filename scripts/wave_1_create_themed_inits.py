#!/usr/bin/env python3
"""
Wave 1 themed-package __init__.py creator.

Creates `__init__.py` files for all the new themed sub-packages that
were created during the migration. These packages are:

- lexicographic/, cultural_heritage/, local_archive/
- media_text/, media_comics/, media_games/, media_personal/
- crypteolas_chain/, crypteolas_docs/, crypteolas_defi/
- raw_files/, cv/, artwork/, labels/

Each `__init__.py` re-exports the local source modules.
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

PROJECT_ROOT = Path("/Users/cianmacandeisigh/dev/cianfhoghlaim")
DLT = PROJECT_ROOT / "dlt_sources"

NEW_PACKAGES = [
    "lexicographic", "cultural_heritage", "local_archive",
    "media_text", "media_comics", "media_games", "media_personal",
    "crypteolas_chain", "crypteolas_docs", "crypteolas_defi",
    "raw_files", "cv", "artwork", "labels",
    "law", "medicine", "education",  # domain-first (have nested dirs)
]


def find_local_modules(pkg_dir: Path) -> list[str]:
    """Find sibling .py files (excluding __init__.py)."""
    return sorted([
        f.stem for f in pkg_dir.glob("*.py")
        if f.stem != "__init__" and not f.stem.startswith(".")
    ])


def create_init(pkg_dir: Path, dry_run: bool = False) -> bool:
    """Create __init__.py for a new themed package."""
    init_path = pkg_dir / "__init__.py"
    if init_path.exists():
        return False
    local_modules = find_local_modules(pkg_dir)
    pkg_name = pkg_dir.name
    if local_modules:
        imports = "\n".join(f"from . import {mod}  # noqa: F401" for mod in local_modules)
        content = f'''"""{pkg_name} — DLT sources (Wave 1 restructure).

Per the **2026-08-24-wave-1-dlt-sources-domain-restructure-v1** openspec
change. The legacy `dlt_sources.language/`, `dlt_sources.media/`,
`dlt_sources.api_sources/`, `dlt_sources.crypteolas/`,
`dlt_sources.apple_photos/`, `dlt_sources.filesystem/`, and
`dlt_sources.portfolio/` packages have been split into these themed
sub-packages.

Legacy import paths still work via re-export shims at the old locations.
"""
from __future__ import annotations

{imports}

__all__ = {local_modules!r}
'''
    else:
        content = f'''"""{pkg_name} — DLT sources (Wave 1 restructure).

Per the **2026-08-24-wave-1-dlt-sources-domain-restructure-v1** openspec
change. The legacy packages have been split into themed sub-packages.
"""
from __future__ import annotations

__all__ = []
'''
    if not dry_run:
        init_path.write_text(content)
    return True


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    created = 0
    for pkg in NEW_PACKAGES:
        pkg_dir = DLT / pkg
        if not pkg_dir.exists():
            print(f"  MISSING: {pkg}")
            continue
        if create_init(pkg_dir, dry_run=args.dry_run):
            created += 1
            mode = "DRY" if args.dry_run else "CREATED"
            print(f"  [{mode}]: {pkg}/__init__.py")

    print(f"\n=== Created {created} __init__.py files ===")
    return 0


if __name__ == "__main__":
    sys.exit(main())
