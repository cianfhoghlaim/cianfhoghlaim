"""Inspect the cached Firecrawl scrape samples for Plan 10 data fill.

This is a SAFE pre-step that lists what education scrape data is
already cached locally, so the data fill can process it without
requiring live Firecrawl API calls.
"""
from __future__ import annotations

import json
from pathlib import Path
from collections import Counter

REPO_ROOT = Path(__file__).resolve().parents[2]
SAMPLES_DIR = REPO_ROOT / "stedding" / "site_scrape_samples"

# Map of source -> jurisdiction
JURISDICTION_MAP: dict[str, str] = {
    "ncca.ie": "Ireland (NCCA)",
    "curriculumonline.ie": "Ireland (curriculumonline.ie)",
    "examinations.ie": "Ireland (examinations.ie)",
    "oide.ie": "Ireland (OIDE)",
    "aistear": "Ireland (Aistear)",
    "junior_cycle": "Ireland (JC)",
    "senior_cycle": "Ireland (LC)",
    "primary": "Ireland (Primary)",
    "sqa": "Scotland (SQA)",
    "wjec": "Wales (WJEC)",
    "ccea": "Northern Ireland (CCEA)",
    "aqa": "England (AQA)",
    "pearson": "England (Pearson)",
}


def inspect_cached_scrapes() -> dict:
    """Return inventory of cached education scrapes by jurisdiction."""
    inventory: dict[str, int] = {}
    if not SAMPLES_DIR.exists():
        return inventory
    for source_dir in SAMPLES_DIR.iterdir():
        if not source_dir.is_dir():
            continue
        name = source_dir.name
        jurisdiction = JURISDICTION_MAP.get(name, f"Unknown ({name})")
        # Count meaningful content (not admin pages)
        meaningful = 0
        for f in source_dir.rglob("*.json"):
            try:
                data = json.loads(f.read_text(errors="ignore"))
                md = data.get("markdown", "")
                if len(md) > 500:  # Skip trivial pages
                    url = data.get("metadata", {}).get("url", "").lower()
                    # Filter admin/cookie pages
                    admin_patterns = [
                        "/contact", "/cookie", "/privacy", "/about/",
                        "/login", "/signup", "/search", "/contact-us",
                    ]
                    if not any(p in url for p in admin_patterns):
                        meaningful += 1
            except Exception:
                pass
        if meaningful > 0:
            inventory[jurisdiction] = meaningful
    return inventory


if __name__ == "__main__":
    print("Cached education scrape inventory:")
    print(f"(Source: {SAMPLES_DIR})")
    print()
    inventory = inspect_cached_scrapes()
    total = sum(inventory.values())
    for jurisdiction, count in sorted(inventory.items(), key=lambda x: -x[1]):
        print(f"  {jurisdiction}: {count}")
    print(f"\n  TOTAL meaningful pages: {total}")
    print()
    print("Next step: process these through the BAML extraction functions")
    print("  (e.g. ExtractNCCACurriculumSpec, ExtractIrelandLCSubject)")
    print("  via scripts/education_data_fill/process_cached_scrapes.py")
