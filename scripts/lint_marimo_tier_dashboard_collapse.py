#!/usr/bin/env python3
"""Marimo tier-dashboard collapse lint.

Per the 2026-11-25-mega-3c-marimo-and-integration-v1 change
(TASK-M3C-2.2): every tier dashboard in `notebooks/*.py` MUST
use the canonical `build_biep_v3_dashboard` helper from
`notebooks/_shared/biiep_v3_dashboard_v2.py`.

Usage:
    mise run lint:marimo-tier-dashboard-collapse

Exit codes:
    0 = all tier dashboards use the canonical helper
    1 = one or more tier dashboards use hand-written operator consoles
"""
from __future__ import annotations

import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parents[1]
NOTEBOOKS_DIR = REPO_ROOT / "notebooks"

# Matches the canonical helper usage
CANONICAL_PATTERN = re.compile(
    r"build_biep_v3_dashboard",
    re.MULTILINE,
)

# The tier dashboards (per the BIEP v3 system)
TIER_DASHBOARDS: list[str] = [
    "19_ireland_pipeline_dashboard.py",
    "20_england_pipeline_dashboard.py",
    "21_sct_wls_ni_pipeline_dashboard.py",
    "22_crown_dependencies_dashboard.py",
    "23_8_jurisdiction_overview.py",
    "26_aistear_dashboard.py",
    "27_primary_dashboard.py",
]


def main() -> int:
    violations: list[Path] = []
    for name in TIER_DASHBOARDS:
        path = NOTEBOOKS_DIR / name
        if not path.exists():
            continue
        content = path.read_text()
        if not CANONICAL_PATTERN.search(content):
            violations.append(path)
    if violations:
        print(f"FAIL: {len(violations)} tier dashboards don't use the canonical helper:", file=sys.stderr)
        for path in violations:
            rel = path.relative_to(REPO_ROOT)
            print(f"  {rel}", file=sys.stderr)
        return 1
    print(f"OK: all tier dashboards use the canonical build_biep_v3_dashboard helper.")
    return 0


if __name__ == "__main__":
    sys.exit(main())