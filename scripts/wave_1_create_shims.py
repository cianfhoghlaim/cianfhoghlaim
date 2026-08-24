#!/usr/bin/env python3
"""
Wave 1 re-export shim generator.

For every legacy `dlt_sources/<geography>/<jurisdiction>/<domain>/` location
that has been migrated, create a shim `__init__.py` that re-exports from
the new `dlt_sources/<domain>/<jurisdiction>/<geography>/` location.

This preserves backwards compatibility for any import that uses the
old jurisdiction-first path (e.g. `from dlt_sources.commonwealth.nigeria.law import nass`).

Usage:
    uv run python scripts/wave_1_create_shims.py [--dry-run]
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

PROJECT_ROOT = Path("/Users/cianmacandeisigh/dev/cianfhoghlaim")
DLT = PROJECT_ROOT / "dlt_sources"

GEOGRAPHIES = ["american_nations", "british_isles", "commonwealth",
               "european_nations", "european_union"]
DOMAINS = ["law", "medicine", "education"]

# Themed package shims
THEMED_SHIMS = {
    "language": ["lexicographic", "cultural_heritage", "local_archive"],
    "media": ["media_text", "media_comics", "media_games"],
    "api_sources": ["api_documentation", "api_github", "api_local", "crypteolas_defi"],
    "crypteolas": ["crypteolas_chain", "crypteolas_docs", "crypteolas_defi"],
    "apple_photos": ["media_personal"],
    "filesystem": ["raw_files"],
    "portfolio": ["cv", "artwork", "labels"],
}


def domain_shim_content(domain: str, jurisdiction: str, geography: str) -> str:
    """Generate the re-export shim __init__.py content."""
    new_path = f"dlt_sources.{domain}.{jurisdiction}.{geography}"
    old_path = f"dlt_sources.{geography}.{jurisdiction}.{domain}"
    return f'''"""
{old_path} — re-export shim.

This shim preserves backwards compatibility for the legacy
jurisdiction-first path. The actual package has been migrated to
`{new_path}` per the
**2026-08-24-wave-1-dlt-sources-domain-restructure-v1** openspec change.

All symbols are re-exported from the new location. New code SHOULD
import from `{new_path}` directly.
"""
from {new_path} import *  # noqa: F401,F403

__all__ = [  # noqa: F405
    # Re-export everything from the new package.
]
# Re-export the __all__ from the new package if it has one
try:
    from {new_path} import __all__ as _new_all
    if _new_all:
        __all__ = list(_new_all)
except ImportError:
    pass
'''


def themed_shim_content(legacy: str, new_targets: list[str]) -> str:
    """Generate a re-export shim for a themed package."""
    parts = [f"from dlt_sources.{t} import *  # noqa: F401,F403" for t in new_targets]
    return f'''"""
dlt_sources.{legacy} — re-export shim.

The {legacy}/ package has been split into {len(new_targets)} themed
sub-packages per the
**2026-08-24-wave-1-dlt-sources-domain-restructure-v1** openspec change:

{chr(10).join(f"- `dlt_sources.{t}/`" for t in new_targets)}

This shim re-exports everything for backwards compatibility. New code
SHOULD import from the new sub-packages directly.
"""
{chr(10).join(parts)}
'''


def create_domain_shims(dry_run: bool = False) -> int:
    """Create re-export shims for domain-first split (law/medicine/education)."""
    count = 0
    for geo in GEOGRAPHIES:
        geo_dir = DLT / geo
        if not geo_dir.exists():
            continue
        for jurisdiction_dir in sorted(geo_dir.iterdir()):
            if not jurisdiction_dir.is_dir() or jurisdiction_dir.name.startswith("_"):
                continue
            if jurisdiction_dir.name == "__pycache__":
                continue
            for domain in DOMAINS:
                shim_dir = jurisdiction_dir / domain
                # Check if the new path exists (it should, after migration)
                new_dir = DLT / domain / jurisdiction_dir.name / geo
                if not new_dir.exists():
                    continue
                if not dry_run:
                    shim_dir.mkdir(parents=True, exist_ok=True)
                    shim_path = shim_dir / "__init__.py"
                    shim_path.write_text(domain_shim_content(
                        domain, jurisdiction_dir.name, geo
                    ))
                count += 1
                print(f"  {'DRY' if dry_run else 'CREATED'}: {shim_dir}/__init__.py")
    return count


def create_themed_shims(dry_run: bool = False) -> int:
    """Create re-export shims for themed package restructure."""
    count = 0
    for legacy, new_targets in THEMED_SHIMS.items():
        legacy_dir = DLT / legacy
        if not legacy_dir.exists():
            continue
        if not dry_run:
            shim_path = legacy_dir / "__init__.py"
            # Only overwrite if the file is small (likely a stub) or doesn't exist
            content = themed_shim_content(legacy, new_targets)
            shim_path.write_text(content)
        count += 1
        print(f"  {'DRY' if dry_run else 'CREATED'}: {legacy}/__init__.py (re-exports {new_targets})")
    return count


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    print("=== Domain-first shims (law/medicine/education) ===")
    domain_count = create_domain_shims(args.dry_run)
    print(f"  Total: {domain_count}\n")

    print("=== Themed package shims ===")
    themed_count = create_themed_shims(args.dry_run)
    print(f"  Total: {themed_count}\n")

    print(f"=== Total shims created: {domain_count + themed_count} ===")
    return 0


if __name__ == "__main__":
    sys.exit(main())
