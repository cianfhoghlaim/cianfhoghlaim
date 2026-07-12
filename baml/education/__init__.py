"""cianfhoghlaim.baml.education — Pick-4 BAML extraction registry.

The BAML education cluster (post-v4 consolidation):

  - ``_shared/``        — 8 cross-stage shared BAML files (curriculum_relationships,
                          content_types, diagram_renderer, document_metadata,
                          eiraic_treasures, education_level, strand_outcome,
                          subject_rubric) + the runtime TypeBuilder helper
                          ``strand_type_builder.py`` for the NCCA catalog
                          (per ``openspec/changes/2026-07-12-baml-type-builder-ncca-v1``)
  - ``stages/``         — 5 NCCA stage files (primary, junior_cycle,
                          senior_cycle, tertiary, plus aistear) — covered by the
                          ``oideachais-pipeline`` spec
  - ``pdfs/``           — 3 Leaving-Cert PDF extraction files (exam_papers,
                          marking_schemes, examiner_reports)
  - ``subjects/``       — 8 ``qpack_<subject>.baml`` per-subject NCCA extraction
                          files (mathematics, chemistry, geography, gaeilge,
                          english, applied_mathematics, computer_science, history)
  - ``cross_nation/``   — 2 cross-British-Isles files (isles_education,
                          multi_nation_curriculum)
  - ``statistics/``     — 1 ``education_statistics.baml``
  - ``university/``     — 1 ``university_extraction.baml``
  - ``law/``            — 5+1 Ireland/law files (covered by the
                          Pick-8 Ireland/law spec)
  - ``lc_extraction/``  — 7 BIEP files (the 6 LC subjects + the shared
                          extraction library)

Generation: ``cd cianfhoghlaim && uv run baml-cli generate``
Validation: ``cd cianfhoghlaim && mise run baml:generate`` (alias)
"""
from __future__ import annotations
