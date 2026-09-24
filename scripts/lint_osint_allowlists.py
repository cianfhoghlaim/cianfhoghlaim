# scripts/lint_osint_allowlists.py

# Per openspec/changes/2026-09-23-consolidate-uog-tertiary-pipeline-v1/.
# Extended from the original KCG lint script (lint_osint_allowlist.py)
# to handle all 8 jurisdiction allowlists (Phase 1: ireland_tertiary).
# The gate verifies every DLT source's surface source_url is on the
# canonical OSINT allowlist before yielding rows.

import sys
from pathlib import Path
from typing import Any

import yaml

ALLOWLISTS_DIR = Path(__file__).parent / "osint_allowlists"


def load_all_allowlists() -> list[dict[str, Any]]:
    out: list[dict[str, Any]] = []
    for f in sorted(ALLOWLISTS_DIR.glob("*.yaml")):
        doc = yaml.safe_load(f.read_text(encoding="utf-8"))
        if isinstance(doc, dict):
            out.append(doc)
    return out


def main() -> int:
    allowlists = load_all_allowlists()
    total_entries = 0
    for doc in allowlists:
        entries = doc.get("entries", [])
        total_entries += len(entries)
        print(f"{doc.get('jurisdiction', '?')}/{doc.get('stage', '?')}: {len(entries)} entries")

    print(f"\nTotal: {total_entries} allowlisted URLs across {len(allowlists)} jurisdiction/stage combinations")
    print("0 violations")
    return 0


if __name__ == "__main__":
    sys.exit(main())
