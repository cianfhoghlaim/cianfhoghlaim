# `baml_src/british_isles/england/education/gcse_extraction/` — GCSE 9-priority-subject BAML

> **The canonical 9-subject GCSE BAML extraction surface for the 9 priority
> subjects (mathematics, english_language, english_literature, biology,
> chemistry, physics, computer_science, history, geography) — all 3 boards
> (AQA / OCR / Edexcel).** Per the 2026-08-13-web-monorepo-consolidation-and-
> agent-integration-v1 change (Phase 4).

## The 9 priority subjects (GCSE level)

| Slug | Display name | AQA spec | OCR spec | Edexcel spec |
|:--|:--|:--|:--|:--|
| `MATHEMATICS` | Mathematics | 8462 | J560 | 1MA1 |
| `ENGLISH_LANGUAGE` | English Language | 8700 | J351 | 1EN0 |
| `ENGLISH_LITERATURE` | English Literature | 8702 | J352 | 1ET0 |
| `BIOLOGY` | Biology | 8461 | J247 | 1BI0 |
| `CHEMISTRY` | Chemistry | 8462 | J248 | 1CH0 |
| `PHYSICS` | Physics | 8463 | J249 | 1PH0 |
| `COMPUTER_SCIENCE` | Computer Science | 8525 | J277 | 1CP2 |
| `HISTORY` | History | 8145 | J410 | 1HI0 |
| `GEOGRAPHY` | Geography | 8035 | J383 | 1GA0 |

## The 8 BAML functions (per subject × per board)

1. `ExtractGCSECurriculumSyllabus` → `GCSESyllabusSpec`
2. `ExtractGCSEExamPaperLayout` → `GCSEExamPaper`
3. `ExtractGCSEMarkingSchemeGuideline` → `GCSEExamPaperMarkingScheme`
4. `ExtractGCSESyllabusDiagram` → `GCSESyllabusDiagram[]`
5. `ExtractGCSECrossSubjectTopics` → `GCSECrossSubjectTopicSet`

## The 3 boards (exam_board enum)

- `AQA` — Assessment and Qualifications Alliance
- `OCR` — Oxford Cambridge and RSA (Oxford, Cambridge, Pearson)
- `EDEXCEL` — Pearson Edexcel

## The 2 tiers (tier enum)

- `FOUNDATION` — grades 1-5 (5-1 to 5-3)
- `HIGHER` — grades 4-9 (4-1 to 9-9)

## Files

- `canonical_gcse_per_subject.baml` — the canonical 9-subject BAML surface (the codegen pipeline in Phase 5 consumes this)

## Related BAML (existing)

- `baml_src/british_isles/england/education/subject_taxonomy.baml` — the 43-subject GCSE enum (the Edexcel/Ocr/AQA canonical taxonomy)
- `baml_src/british_isles/england/education/subject_taxonomy_edexcel.baml` — the Edexcel-specific taxonomy
- `baml_src/british_isles/england/education/subject_taxonomy_ocr.baml` — the OCR-specific taxonomy
- `baml_src/british_isles/england/education/england_aqa.baml` — the AQA-specific extraction
- `baml_src/british_isles/england/education/curriculum_syllabus.baml` — the unified England syllabus extractor (covers both GCSE + A-Level)

## DO NOT

- **Never** hand-write a Pydantic model that duplicates a BAML class — codegen it from `.baml`.
- **Never** edit `england/curriculum_syllabus.baml` directly — extend the canonical `england/gcse_extraction/canonical_gcse_per_subject.baml` instead.

## Skill pointers

- [`baml`](../../../../../.agents/skills/baml/SKILL.md) — BAML schema authoring
- [`schema-codegen`](../../../../../.agents/skills/schema-codegen/SKILL.md) — the codegen pipeline (Phase 5)
- [`centralized-registry`](../../../../../.agents/skills/centralized-registry/SKILL.md) — MODEL_REGISTRY

<!-- generated: 2026-08-13 (per the 2026-08-13-web-monorepo-consolidation-and-agent-integration-v1 change, Phase 4) -->
