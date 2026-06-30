#!/usr/bin/env python3
"""Update legacy dagster/assets/{law,medicine}/{nation}/__init__.py to re-export from by_domain/."""
from __future__ import annotations
from pathlib import Path

# Mapping: (legacy_path, asset_name_in_by_domain)
LAW_FILES = {
    "england": "law_england_legislation",
    "scotland": "law_scotland_legislation",
    "wales": "law_wales_legislation",
    "northern_ireland": "law_northern_ireland_legislation",
    "isle_of_man": "law_isle_of_man_legislation",
    "jersey": "law_jersey_legislation",
    "guernsey": "law_guernsey_legislation",
}

MEDICINE_FILES = {
    "england": [
        "medicine_england_nhs_england",
        "medicine_england_gmc",
        "medicine_england_nice",
    ],
    "scotland": ["medicine_scotland_nhs_scotland"],
    "wales": ["medicine_wales_nhs_wales"],
    "northern_ireland": ["medicine_northern_ireland_nidirect"],
    "isle_of_man": ["medicine_isle_of_man_health_social_care"],
    "jersey": ["medicine_jersey_health_community_services"],
    "guernsey": ["medicine_guernsey_health_social_care"],
}


def write_law_init(nation: str, asset_name: str) -> str:
    return f'''"""
Backward-compat shim — the legacy {nation} law @asset has moved to
dagster.assets.by_domain.law.{asset_name} (per the v3 consolidation
plan, consolidate-cianfhoghlaim-subdirs Phase B.6).

This file is preserved for one release as a re-export shim. Update
your imports to use the canonical by_domain/ path.
"""
from cianfhoghlaim.dagster.assets.by_domain import {asset_name}

__all__ = ["{asset_name}"]
'''


def write_medicine_init(nation: str, asset_names: list[str]) -> str:
    return f'''"""
Backward-compat shim — the legacy {nation} medicine @assets have moved to
dagster.assets.by_domain.medicine (per the v3 consolidation plan,
consolidate-cianfhoghlaim-subdirs Phase B.6).

This file is preserved for one release as a re-export shim. Update
your imports to use the canonical by_domain/ path.
"""
from cianfhoghlaim.dagster.assets.by_domain import (
{chr(10).join(f"    {name}," for name in asset_names)}
)

__all__ = {asset_names!r}
'''


def main() -> None:
    root = Path("/Users/cianmacandeisigh/dev/kings_college_galway/cianfhoghlaim/dagster/assets")

    # Write law re-exports
    for nation, asset_name in LAW_FILES.items():
        path = root / "law" / nation / "__init__.py"
        path.write_text(write_law_init(nation, asset_name))
        print(f"[OK] {path.relative_to(root.parent)}")

    # Write medicine re-exports
    for nation, asset_names in MEDICINE_FILES.items():
        path = root / "medicine" / nation / "__init__.py"
        path.write_text(write_medicine_init(nation, asset_names))
        print(f"[OK] {path.relative_to(root.parent)}")


if __name__ == "__main__":
    main()