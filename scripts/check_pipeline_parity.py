#!/usr/bin/env python3
"""scripts/check_pipeline_parity.py

Walk the four data-platform packages (baml_src/, dlt/,
orchestration/defs/1_ingestion/, cocoindex/) and emit a per-jurisdiction
matrix showing which layers contain each jurisdiction.

Exit non-zero when PIPELINE_PARITY_STRICT=1 and any layer is missing for
any jurisdiction that exists in at least one layer.
"""
from __future__ import annotations

import os
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
BAML_SRC = REPO_ROOT / "baml_src"
DLT = REPO_ROOT / "dlt"
ORCHESTRATION = REPO_ROOT / "orchestration" / "defs" / "1_ingestion"
COCOINDEX = REPO_ROOT / "cocoindex_flows"

REGIONS = ("european_nations", "commonwealth", "british_isles",
           "american_nations", "european_union")


def list_jurisdictions(base: Path, region: str) -> list[str]:
    """List jurisdiction directory names under {base}/{region}/."""
    region_dir = base / region
    if not region_dir.is_dir():
        return []
    return sorted(
        d.name for d in region_dir.iterdir()
        if d.is_dir() and not d.name.startswith("_") and not d.name.startswith(".")
    )


def layer_present(base: Path, region: str, jurisdiction: str) -> bool:
    """True if {base}/{region}/{jurisdiction}/ exists AND is non-empty."""
    p = base / region / jurisdiction
    return p.is_dir() and any(p.iterdir())


def cocoindex_layer_present(region: str, jurisdiction: str) -> bool:
    """CocoIndex per-jurisdiction is a FILE at the standard name."""
    p = COCOINDEX / region / jurisdiction / "education_embedding.py"
    return p.is_file()


def cocoindex_cross_present(region: str) -> bool:
    """Cross-jurisdiction CocoIndex app at {cocoindex}/{region}_cross/."""
    p = COCOINDEX / f"{region}_cross"
    return p.is_dir() and any(p.iterdir())


def main() -> int:
    # Build the union of jurisdictions across all 4 layers
    all_jurisdictions: set[tuple[str, str]] = set()
    layer_data: dict[tuple[str, str], dict[str, bool]] = {}

    for region in REGIONS:
        # baml_src: jurisdiction dirs under baml_src/{region}/
        for j in list_jurisdictions(BAML_SRC, region):
            all_jurisdictions.add((region, j))
            layer_data.setdefault((region, j), {})["baml_src"] = (
                BAML_SRC / region / j
            ).is_dir() and any((BAML_SRC / region / j).iterdir())

        # dlt: jurisdiction dirs under dlt/{region}/
        for j in list_jurisdictions(DLT, region):
            all_jurisdictions.add((region, j))
            layer_data.setdefault((region, j), {})["dlt"] = (
                DLT / region / j
            ).is_dir() and any((DLT / region / j).iterdir())

        # orchestration: jurisdiction dirs under orchestration/defs/1_ingestion/{region}/
        for j in list_jurisdictions(ORCHESTRATION, region):
            all_jurisdictions.add((region, j))
            layer_data.setdefault((region, j), {})["orchestration"] = (
                ORCHESTRATION / region / j
            ).is_dir() and any((ORCHESTRATION / region / j).iterdir())

        # cocoindex: per-jurisdiction FILE at cocoindex/{region}/{jurisdiction}/education_embedding.py
        for j in list_jurisdictions(COCOINDEX, region):
            all_jurisdictions.add((region, j))
            layer_data.setdefault((region, j), {})["cocoindex"] = (
                COCOINDEX / region / j / "education_embedding.py"
            ).is_file()

    # Header
    print(f"{'region':<20} {'jurisdiction':<30} {'baml_src':<12} {'dlt':<12} {'orchestration':<16} {'cocoindex':<12}")
    print("-" * 102)

    missing_any = False
    for region, j in sorted(all_jurisdictions):
        row = layer_data[(region, j)]
        cells = []
        for layer in ("baml_src", "dlt", "orchestration", "cocoindex_flows"):
            present = row.get(layer, False)
            cells.append("OK" if present else "MISSING")
            if not present:
                missing_any = True
        print(f"{region:<20} {j:<30} {cells[0]:<12} {cells[1]:<12} {cells[2]:<16} {cells[3]:<12}")

    # Cross-jurisdiction
    print()
    print(f"{'region':<20} {'_cross app':<30} {'cocoindex':<12}")
    print("-" * 62)
    cross_missing = False
    for region in REGIONS:
        present = cocoindex_cross_present(region)
        if not present:
            cross_missing = True
        print(f"{region:<20} {'(cross)':<30} {'OK' if present else 'MISSING':<12}")

    # Subjects
    print()
    print(f"{'cocoindex subdir':<30} {'status':<12}")
    print("-" * 42)
    required_subdirs = ("_shared", "subjects", "media", "portfolio",
                        "knowledge_graph", "infrastructure", "corpus",
                        "biep_parity")
    subdir_missing = False
    for sub in required_subdirs:
        present = (COCOINDEX / sub).is_dir()
        if not present:
            subdir_missing = False
        print(f"{sub:<30} {'OK' if present else 'MISSING':<12}")

    # Region-level cocoindex dirs
    required_coco_regions = ("european_nations", "commonwealth",
                             "british_isles", "american_nations",
                             "european_nations_cross", "commonwealth_cross",
                             "celtic", "european_union")
    for sub in required_coco_regions:
        present = (COCOINDEX / sub).is_dir()
        if not present:
            subdir_missing = False
        print(f"{sub:<30} {'OK' if present else 'MISSING':<12}")

    print()
    print(f"Total jurisdictions: {len(all_jurisdictions)}")

    strict = os.environ.get("PIPELINE_PARITY_STRICT", "0") == "1"
    if strict and (missing_any or cross_missing):
        print(f"\nSTRICT mode: missing layers detected. Exit non-zero.")
        return 1
    if strict and subdir_missing:
        print(f"\nSTRICT mode: missing cocoindex subdirs. Exit non-zero.")
        return 1
    print("\nADVISORY mode: no exit on missing layers.")
    return 0


if __name__ == "__main__":
    sys.exit(main())