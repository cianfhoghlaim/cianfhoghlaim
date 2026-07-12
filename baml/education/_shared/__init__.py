"""cianfhoghlaim.baml.education._shared — Cross-stage shared BAML + Python helpers.

The 8 cross-stage shared BAML files:

  - ``content_types.baml``          — Core content-type enums (ContentType, etc.)
  - ``curriculum_relationships.baml`` — 4 cross-stage relationship extraction
                                        functions (ExtractLearningOutcomeRelationships,
                                        ExtractSkillsFromOutcome,
                                        ExtractCurriculumFromDocument,
                                        IdentifyPrerequisiteChain)
  - ``diagram_renderer.baml``       — Diagram-rendering extraction classes
  - ``document_metadata.baml``      — Document-level metadata extraction
  - ``education_level.baml``        — EducationLevel + related enums
  - ``eiraic_treasures.baml``       — Eiraic treasures extraction (14 classes)
  - ``strand_outcome.baml``         — Strand / Outcome / Spec / Assessment classes
  - ``subject_rubric.baml``         — Subject-rubric extraction classes

Runtime Python helpers:

  - ``strand_type_builder.py``      — TypeBuilder for the NCCA catalog
                                        (per ``openspec/changes/
                                        2026-07-12-baml-type-builder-ncca-v1``)
                                        — reads ``strand_catalog.yaml`` and
                                        injects the per-strand / per-outcome
                                        properties into the 4 ``@@dynamic``
                                        BAML classes in ``strand_outcome.baml``.

Catalog data:

  - ``strand_catalog.yaml``         — Representative subset of the NCCA
                                        strand / outcome / spec / assessment
                                        tree (the 6 LC priority subjects).

Generation: ``cd cianfhoghlaim && uv run baml-cli generate``
"""
from __future__ import annotations
