#!/usr/bin/env python3
"""Sweep consumer files: replace stale baml_src/X.baml refs with new cluster paths.

Usage: python scripts/sweep_baml_refs.py
"""
from __future__ import annotations
import re
from pathlib import Path

# Mapping table (old → new) — see proposal.md
MAPPING: dict[str, str] = {
    "baml_src/curriculum_extraction.baml": "baml/education/_shared/curriculum_relationships.baml",
    "baml_src/early_childhood.baml": "baml/education/stages/aistear.baml",
    "baml_src/aistear.baml": "baml/education/stages/aistear.baml",
    "baml_src/primary.baml": "baml/education/stages/primary.baml",
    "baml_src/junior_cycle.baml": "baml/education/stages/junior_cycle.baml",
    "baml_src/tertiary.baml": "baml/education/stages/tertiary.baml",
    "baml_src/senior_cycle.baml": "baml/education/stages/senior_cycle.baml",
    "baml_src/email.baml": "baml/processing/email.baml",
    "baml_src/official_media.baml": "baml/processing/official_media.baml",
    "baml_src/upstream_monitoring.baml": "baml/processing/upstream_monitoring.baml",
    "baml_src/circular_extraction.baml": "baml/processing/circular_extraction.baml",
    "baml_src/identity_verification.baml": "baml/processing/identity_verification.baml",
    "baml_src/author_archive.baml": "baml/processing/author_archive.baml",
    "baml_src/cv_extraction.baml": "baml/processing/cv_extraction.baml",
    "baml_src/portfolio_extraction.baml": "baml/processing/portfolio_extraction.baml",
    "baml_src/researchgate_extraction.baml": "baml/processing/researchgate_extraction.baml",
    "baml_src/linkedin_profile_extraction.baml": "baml/processing/linkedin_profile_extraction.baml",
    "baml_src/audio_extraction.baml": "baml/processing/audio_extraction.baml",
    "baml_src/ocr_extraction.baml": "baml/processing/ocr_extraction.baml",
    "baml_src/ocr_validation.baml": "baml/processing/ocr_validation.baml",
    "baml_src/image_generation.baml": "baml/processing/image_generation.baml",
    "baml_src/style_transfer.baml": "baml/processing/style_transfer.baml",
    "baml_src/game_content.baml": "baml/processing/game_content.baml",
    "baml_src/player_assessment.baml": "baml/processing/player_assessment.baml",
    "baml_src/generators.baml": "baml/processing/generators.baml",
    "baml_src/culture_extraction.baml": "baml/processing/culture_extraction.baml",
    "baml_src/named_entities.baml": "baml/processing/named_entities.baml",
    "baml_src/site_analysis.baml": "baml/processing/site_analysis.baml",
    "baml_src/ui_components.baml": "baml/processing/ui_components.baml",
    "baml_src/teaching_extraction.baml": "baml/processing/teaching_extraction.baml",
    "baml_src/celtic_sources.baml": "baml/celtic/sources.baml",
    "baml_src/celtic_curriculum.baml": "baml/celtic/curriculum/celtic_curriculum.baml",
    "baml_src/celtic_linguistics.baml": "baml/celtic/_archive/celtic_linguistics.baml",
    "baml_src/cognates.baml": "baml/celtic/_archive/cognates.baml",
    "baml_src/mythology_extraction.baml": "baml/celtic/curriculum/mythology_extraction.baml",
    "baml_src/morphology.baml": "baml/celtic/morphology.baml",
    "baml_src/grammar_patterns.baml": "baml/celtic/grammar_patterns.baml",
    "baml_src/isles_education.baml": "baml/education/cross_nation/isles_education.baml",
    "baml_src/multi_nation_curriculum.baml": "baml/education/cross_nation/multi_nation_curriculum.baml",
    "baml_src/education_statistics.baml": "baml/education/statistics/education_statistics.baml",
    "baml_src/university_extraction.baml": "baml/education/university/university_extraction.baml",
    "baml_src/leaving_cert_syllabus_extraction.baml": "baml/education/pdfs/leaving_cert_syllabus.baml",
    "baml_src/leaving_cert_past_paper_extraction.baml": "baml/education/pdfs/leaving_cert_past_paper.baml",
    "baml_src/leaving_cert_marking_scheme_extraction.baml": "baml/education/pdfs/leaving_cert_marking_scheme.baml",
    "baml_src/educational_clients.baml": "baml/clients.baml",
    # Also handle the oideachais/ prefix variant
    "oideachais/baml_src/upstream_monitoring.baml": "baml/processing/upstream_monitoring.baml",
    "oideachais/baml_src/culture_extraction.baml": "baml/processing/culture_extraction.baml",
    "oideachais/baml_src/site_analysis.baml": "baml/processing/site_analysis.baml",
    "oideachais/baml_src/senior_cycle.baml": "baml/education/stages/senior_cycle.baml",
    "oideachais/baml_src/": "baml/",
    # Handle the subjects/baml_context/ variant
    "baml_src/subjects/baml_context/senior_cycle.baml": "baml/education/stages/senior_cycle.baml",
}

# Consumer files to sweep
CONSUMER_FILES = [
    "cianfhoghlaim/dlt/official_media/classifier.py",
    "cianfhoghlaim/dlt/cross/upstream/blog_post.py",
    "cianfhoghlaim/dlt/british_isles/ie/education/junior_cycle.py",
    "cianfhoghlaim/dlt/british_isles/ie/education/primary.py",
    "cianfhoghlaim/dlt/british_isles/ie/culture/heritage.py",
    "cianfhoghlaim/dlt/site_analysis/__init__.py",
    "cianfhoghlaim/dlt/leabharlann/gemini_deep_research.py",
    "cianfhoghlaim/dagster/definitions.py",
    "cianfhoghlaim/dagster/assets/senior_cycle_kg.py",
    "cianfhoghlaim/dagster/assets/asset_generation.py",
    "cianfhoghlaim/agents/baml_integration.py",
    "cianfhoghlaim/cocoindex/_v0_archive/learning_outcome_graph.py",
    "cianfhoghlaim/cocoindex/culture_heritage_embedding.py",
    "cianfhoghlaim/cocoindex/docs_skills_consolidation.py",
    "cianfhoghlaim/notebooks/meaisinfhoghlaim/01_leabharlann_descriptive.py",
    "cianfhoghlaim/notebooks/sources_load.py",
    "cianfhoghlaim/notebooks/dashboards/leabharlann_full_stack_demo.py",
    "cianfhoghlaim/notebooks/dashboards/aistear.py",
    "cianfhoghlaim/notebooks/dashboards/senior_cycle.py",
    "cianfhoghlaim/notebooks/dashboards/tertiary.py",
]


def sweep_file(path: Path) -> tuple[int, list[str]]:
    """Replace baml_src/ refs in a single file. Returns (replacements_made, unmatched_refs)."""
    text = path.read_text()
    original = text
    unmatched: list[str] = []
    replacements = 0

    # Sort mapping by length DESC so longer paths are replaced first
    for old, new in sorted(MAPPING.items(), key=lambda x: -len(x[0])):
        if old in text:
            count = text.count(old)
            text = text.replace(old, new)
            replacements += count

    # Find any remaining baml_src/ refs
    remaining = re.findall(r"baml_src/[^\s`'\")\]}]+", text)
    unmatched.extend(remaining)

    if text != original:
        path.write_text(text)
    return replacements, unmatched


def main() -> None:
    total_replacements = 0
    total_unmatched: list[str] = []
    files_changed = 0

    for relpath in CONSUMER_FILES:
        path = Path("/Users/cianmacandeisigh/dev/kings_college_galway") / relpath
        if not path.exists():
            print(f"[SKIP] {relpath} (does not exist)")
            continue
        replacements, unmatched = sweep_file(path)
        if replacements > 0:
            files_changed += 1
            total_replacements += replacements
            print(f"[OK] {relpath}: {replacements} replacements")
        if unmatched:
            print(f"[WARN] {relpath}: unmatched refs: {unmatched}")
            total_unmatched.extend(unmatched)

    print(f"\nTotal: {total_replacements} replacements in {files_changed} files")
    if total_unmatched:
        print(f"Unmatched refs (need manual handling):")
        for u in total_unmatched:
            print(f"  - {u}")


if __name__ == "__main__":
    main()