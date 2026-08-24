#!/usr/bin/env python3
"""
Wave 0 module-path repair script.

For each `defs.yaml` file under `orchestration/defs/3_model_lifecycle/cocoindex_v1/`,
replace broken `module: cianfhoghlaim.cocoindex.<app>` paths with the correct
`module: cianfhoghlaim.cocoindex_flows.<actual_path>` paths.

The mapping table is captured in
`openspec/changes/2026-08-24-wave-0-cocoindex-module-path-repair-v1/specs/cocoindex-v1-module-path-migration/spec.md`
(Buckets A, B, C).

Usage:
    uv run python scripts/wave_0_module_path_repair.py [--dry-run]
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

# Project root
PROJECT_ROOT = Path("/Users/cianmacandeisigh/dev/cianfhoghlaim")
DEFS_ROOT = PROJECT_ROOT / "orchestration/defs/3_model_lifecycle/cocoindex_v1"

# Mapping table: legacy module path → new module path
# The legacy paths are stripped of the `cianfhoghlaim.cocoindex.` prefix
# in the table below for readability; the prefix is added at lookup time.
MODULE_PATH_MAP: dict[str, str] = {
    # ─── Bucket A — Per-nation European education embeddings (40 ISO-3 + parent + law + medicine) ───
    # All map to the factory pattern at cocoindex_flows/european_nations/_factory.py
    # OR to the legacy _cross/ directory for law/medicine which were not folded into the factory.
    "european_nations_alb_education_embedding": "cianfhoghlaim.cocoindex_flows.european_nations._factory",
    "european_nations_aut_education_embedding": "cianfhoghlaim.cocoindex_flows.european_nations._factory",
    "european_nations_bel_education_embedding": "cianfhoghlaim.cocoindex_flows.european_nations._factory",
    "european_nations_bgr_education_embedding": "cianfhoghlaim.cocoindex_flows.european_nations._factory",
    "european_nations_bih_education_embedding": "cianfhoghlaim.cocoindex_flows.european_nations._factory",
    "european_nations_che_education_embedding": "cianfhoghlaim.cocoindex_flows.european_nations._factory",
    "european_nations_cyp_education_embedding": "cianfhoghlaim.cocoindex_flows.european_nations._factory",
    "european_nations_cze_education_embedding": "cianfhoghlaim.cocoindex_flows.european_nations._factory",
    "european_nations_deu_education_embedding": "cianfhoghlaim.cocoindex_flows.european_nations._factory",
    "european_nations_dnk_education_embedding": "cianfhoghlaim.cocoindex_flows.european_nations._factory",
    "european_nations_esp_education_embedding": "cianfhoghlaim.cocoindex_flows.european_nations._factory",
    "european_nations_est_education_embedding": "cianfhoghlaim.cocoindex_flows.european_nations._factory",
    "european_nations_fin_education_embedding": "cianfhoghlaim.cocoindex_flows.european_nations._factory",
    "european_nations_fra_education_embedding": "cianfhoghlaim.cocoindex_flows.european_nations._factory",
    "european_nations_geo_education_embedding": "cianfhoghlaim.cocoindex_flows.european_nations._factory",
    "european_nations_grc_education_embedding": "cianfhoghlaim.cocoindex_flows.european_nations._factory",
    "european_nations_hrv_education_embedding": "cianfhoghlaim.cocoindex_flows.european_nations._factory",
    "european_nations_hun_education_embedding": "cianfhoghlaim.cocoindex_flows.european_nations._factory",
    "european_nations_isl_education_embedding": "cianfhoghlaim.cocoindex_flows.european_nations._factory",
    "european_nations_ita_education_embedding": "cianfhoghlaim.cocoindex_flows.european_nations._factory",
    "european_nations_lie_education_embedding": "cianfhoghlaim.cocoindex_flows.european_nations._factory",
    "european_nations_ltu_education_embedding": "cianfhoghlaim.cocoindex_flows.european_nations._factory",
    "european_nations_lux_education_embedding": "cianfhoghlaim.cocoindex_flows.european_nations._factory",
    "european_nations_lva_education_embedding": "cianfhoghlaim.cocoindex_flows.european_nations._factory",
    "european_nations_mda_education_embedding": "cianfhoghlaim.cocoindex_flows.european_nations._factory",
    "european_nations_mkd_education_embedding": "cianfhoghlaim.cocoindex_flows.european_nations._factory",
    "european_nations_mlt_education_embedding": "cianfhoghlaim.cocoindex_flows.european_nations._factory",
    "european_nations_mne_education_embedding": "cianfhoghlaim.cocoindex_flows.european_nations._factory",
    "european_nations_nld_education_embedding": "cianfhoghlaim.cocoindex_flows.european_nations._factory",
    "european_nations_nor_education_embedding": "cianfhoghlaim.cocoindex_flows.european_nations._factory",
    "european_nations_pol_education_embedding": "cianfhoghlaim.cocoindex_flows.european_nations._factory",
    "european_nations_prt_education_embedding": "cianfhoghlaim.cocoindex_flows.european_nations._factory",
    "european_nations_rou_education_embedding": "cianfhoghlaim.cocoindex_flows.european_nations._factory",
    "european_nations_srb_education_embedding": "cianfhoghlaim.cocoindex_flows.european_nations._factory",
    "european_nations_svk_education_embedding": "cianfhoghlaim.cocoindex_flows.european_nations._factory",
    "european_nations_svn_education_embedding": "cianfhoghlaim.cocoindex_flows.european_nations._factory",
    "european_nations_swe_education_embedding": "cianfhoghlaim.cocoindex_flows.european_nations._factory",
    "european_nations_tur_education_embedding": "cianfhoghlaim.cocoindex_flows.european_nations._factory",
    "european_nations_ukr_education_embedding": "cianfhoghlaim.cocoindex_flows.european_nations._factory",
    "european_nations_xkx_education_embedding": "cianfhoghlaim.cocoindex_flows.european_nations._factory",
    # The generic "european_nations_education_embedding" maps to the factory too
    "european_nations_education_embedding": "cianfhoghlaim.cocoindex_flows.european_nations._factory",
    # European law + medicine are in the cross directory (they cross multiple nations)
    "european_nations_law_embedding": "cianfhoghlaim.cocoindex_flows.european_nations_cross.law_embedding",
    "european_nations_medicine_embedding": "cianfhoghlaim.cocoindex_flows.european_nations_cross.medicine_embedding",

    # ─── Bucket B — LC subjects (6) ───
    "mathematics_embedding": "cianfhoghlaim.cocoindex_flows.subjects.lc_subject_embedding",
    "chemistry_embedding": "cianfhoghlaim.cocoindex_flows.subjects.lc_subject_embedding",
    "geography_embedding": "cianfhoghlaim.cocoindex_flows.subjects.lc_subject_embedding",
    "english_embedding": "cianfhoghlaim.cocoindex_flows.subjects.lc_subject_embedding",
    "computer_science_embedding": "cianfhoghlaim.cocoindex_flows.subjects.lc_subject_embedding",
    # Gaeilge is a special case — it has its own file (Irish-only, no English sibling)
    "gaeilge_embedding": "cianfhoghlaim.cocoindex_flows.celtic.gaeilge_embedding",

    # ─── Bucket C — Specialised Apps ───
    "americas_california_education_embedding": "cianfhoghlaim.cocoindex_flows.american_nations.united_states.california_education_embedding",
    "commonwealth_education_embedding": "cianfhoghlaim.cocoindex_flows.biep_parity.lc_subject_embedding",
    "nigeria_education_embedding": "cianfhoghlaim.cocoindex_flows.commonwealth.nigeria.education_embedding",
    "quebec_montreal_education_embedding": "cianfhoghlaim.cocoindex_flows.commonwealth.canada.provinces.quebec.montreal_education_embedding",
    "eu_multilingual_alignment_embedding": "cianfhoghlaim.cocoindex_flows.european_nations._factory",
    "european_union_official_embedding": "cianfhoghlaim.cocoindex_flows.european_union.official_embedding",
    "ie_law_court_rules": "cianfhoghlaim.cocoindex_flows.british_isles.ireland.ie_law_court_rules",
    "ie_law_courts": "cianfhoghlaim.cocoindex_flows.british_isles.ireland.ie_law_courts",
    "ie_law_judgements": "cianfhoghlaim.cocoindex_flows.british_isles.ireland.ie_law_judgements",
    "ie_law_legal_aid": "cianfhoghlaim.cocoindex_flows.british_isles.ireland.ie_law_legal_aid",
    "ie_law_piab": "cianfhoghlaim.cocoindex_flows.british_isles.ireland.ie_law_piab",

    # Infrastructure flows
    "academic_history_flow": "cianfhoghlaim.cocoindex_flows.infrastructure.academic_history_flow",
    "agent_registry": "cianfhoghlaim.cocoindex_flows.infrastructure.agent_registry",
    "api_indexing": "cianfhoghlaim.cocoindex_flows.infrastructure.api_indexing",
    "code_embedding": "cianfhoghlaim.cocoindex_flows.infrastructure.code_embedding",
    "codebase_graph": "cianfhoghlaim.cocoindex_flows.infrastructure.codebase_graph",
    "codebase_indexing": "cianfhoghlaim.cocoindex_flows.infrastructure.codebase_indexing",
    "cocoindex_v1_conformance": "cianfhoghlaim.cocoindex_flows.infrastructure.cocoindex_v1_conformance",
    "config_indexing": "cianfhoghlaim.cocoindex_flows.infrastructure.config_indexing",
    "docs_skills_consolidation": "cianfhoghlaim.cocoindex_flows.infrastructure.docs_skills_consolidation",
    "filesystem_indexing": "cianfhoghlaim.cocoindex_flows.infrastructure.filesystem_indexing",
    "ocr_aware_flow": "cianfhoghlaim.cocoindex_flows.infrastructure.ocr_aware_flow",
    "root_pdfs_embedding": "cianfhoghlaim.cocoindex_flows.infrastructure.root_pdfs_embedding",
    "storage_indexing": "cianfhoghlaim.cocoindex_flows.infrastructure.storage_indexing",
    "upstream_api_surface": "cianfhoghlaim.cocoindex_flows.infrastructure.upstream_api_surface",
    "upstream_blog_monitor": "cianfhoghlaim.cocoindex_flows.infrastructure.upstream_blog_monitor",

    # BIEP parity
    "cross_subject_competency_embedding": "cianfhoghlaim.cocoindex_flows.biep_parity.cross_subject_competency_embedding",

    # Media
    "apple_photos_chunks": "cianfhoghlaim.cocoindex_flows.media_personal.apple_photos_chunks",
    "apple_photos_geospatial": "cianfhoghlaim.cocoindex_flows.media_personal.apple_photos_geospatial",
    "apple_photos_metadata": "cianfhoghlaim.cocoindex_flows.media_personal.apple_photos_metadata",

    # Cultural heritage
    "culture_heritage_embedding": "cianfhoghlaim.cocoindex_flows.cultural_heritage.embedding",
    "mythology_embedding": "cianfhoghlaim.cocoindex_flows.cultural_heritage.celtic_mythology_embedding",
    "history_embedding": "cianfhoghlaim.cocoindex_flows.cultural_heritage.embedding",

    # CV / portfolio
    "cv_embedding": "cianfhoghlaim.cocoindex_flows.cv.embedding",

    # Corpus / library
    "government_circulars_embedding": "cianfhoghlaim.cocoindex_flows.corpus.government_circulars_embedding",
    "ireland_legal_embedding": "cianfhoghlaim.cocoindex_flows.british_isles.ireland.ireland_legal_embedding",
    "leabharlann_embedding": "cianfhoghlaim.cocoindex_flows.corpus.leabharlann_embedding",
    "leabharlann_flow": "cianfhoghlaim.cocoindex_flows.corpus.leabharlann_embedding",
    "unified_embedding": "cianfhoghlaim.cocoindex_flows.corpus.unified_embedding",

    # Tertiary (UoG — Wave 2 will move these into education/tertiary/uog/, but the module paths exist now)
    "university_courses": "cianfhoghlaim.cocoindex_flows.education.tertiary.uog.courses",
    "university_modules": "cianfhoghlaim.cocoindex_flows.education.tertiary.uog.modules",

    # Knowledge graph
    "youtube_kg_embedding": "cianfhoghlaim.cocoindex_flows.knowledge_graph.youtube_kg_embedding",
}

LEGACY_PREFIX = "cianfhoghlaim.cocoindex."


def repair_file(path: Path, dry_run: bool = False) -> tuple[bool, list[str]]:
    """Return (modified, replacements_made)."""
    text = path.read_text()
    replacements: list[str] = []
    new_lines: list[str] = []
    for line in text.splitlines(keepends=True):
        new_line = line
        if LEGACY_PREFIX in line and "module:" in line:
            # Extract the legacy module path
            stripped = line.strip()
            for legacy_suffix, new_path in MODULE_PATH_MAP.items():
                legacy_full = f"{LEGACY_PREFIX}{legacy_suffix}"
                if legacy_full in stripped:
                    new_line = line.replace(legacy_full, new_path)
                    replacements.append(f"  {legacy_full} → {new_path}")
                    break
        new_lines.append(new_line)
    new_text = "".join(new_lines)
    modified = new_text != text
    if modified and not dry_run:
        path.write_text(new_text)
    return modified, replacements


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    if not DEFS_ROOT.exists():
        print(f"ERROR: {DEFS_ROOT} does not exist", file=sys.stderr)
        return 1

    total_files = 0
    modified_files = 0
    total_replacements = 0
    unmatched: list[tuple[Path, str]] = []

    for defs_yaml in sorted(DEFS_ROOT.rglob("defs.yaml")):
        total_files += 1
        modified, replacements = repair_file(defs_yaml, dry_run=args.dry_run)
        if modified:
            modified_files += 1
            total_replacements += len(replacements)
            mode = "DRY-RUN" if args.dry_run else "MODIFIED"
            print(f"{mode}: {defs_yaml.relative_to(PROJECT_ROOT)} ({len(replacements)} replacements)")
            for r in replacements:
                print(f"    {r}")

    print()
    print(f"Total defs.yaml files scanned: {total_files}")
    print(f"Files modified:                {modified_files}")
    print(f"Total replacements:            {total_replacements}")

    return 0


if __name__ == "__main__":
    sys.exit(main())
