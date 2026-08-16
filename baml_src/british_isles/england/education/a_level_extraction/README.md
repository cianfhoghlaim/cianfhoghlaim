# `baml_src/british_isles/england/education/a_level_extraction/` — A-Level 15-priority-subject BAML

> **The canonical 15-subject A-Level BAML extraction surface for the 15
> priority subjects (mathematics, further_mathematics, english_literature,
> english_language, biology, chemistry, physics, psychology, history,
> geography, economics, business, history_of_art, politics, sociology) — all
> 3 boards (AQA / OCR / Edexcel).** Per the 2026-08-13-web-monorepo-consolidation-
> and-agent-integration-v1 change (Phase 4).

## The 15 priority subjects (A-Level level)

| Slug | Display name | AQA spec | OCR spec | Edexcel spec |
|:--|:--|:--|:--|:--|
| `MATHEMATICS` | Mathematics | 7357 | H240 | 9MA0 |
| `FURTHER_MATHEMATICS` | Further Mathematics | 7367 | H245 | 9FM0 |
| `ENGLISH_LITERATURE` | English Literature | 7717 | H472 | 9ET0 |
| `ENGLISH_LANGUAGE` | English Language | 7702 | H470 | 9EN0 |
| `BIOLOGY` | Biology | 7402 | H420 | 9BN0 |
| `CHEMISTRY` | Chemistry | 7405 | H433 | 9CH0 |
| `PHYSICS` | Physics | 7408 | H556 | 9PH0 |
| `PSYCHOLOGY` | Psychology | 7182 | H180 | 9PS0 |
| `HISTORY` | History | 7042 | H505 | 9HI0 |
| `GEOGRAPHY` | Geography | 7037 | H481 | 9GE0 |
| `ECONOMICS` | Economics | 7126 | H460 | 9EC0 |
| `BUSINESS` | Business | 7132 | H431 | 9BS0 |
| `HISTORY_OF_ART` | History of Art | 7203 | H401 | 9HA0 |
| `POLITICS` | Politics | 7152 | H485 | 9PL0 |
| `SOCIOLOGY` | Sociology | 7192 | H180 | 9SC0 |

## The 8 BAML functions (per subject × per board)

1. `ExtractALevelCurriculumSyllabus` → `ALevelSyllabusSpec`
2. `ExtractALevelExamPaperLayout` → `ALevelExamPaper`
3. `ExtractALevelMarkingSchemeGuideline` → `ALevelExamPaperMarkingScheme`
4. `ExtractALevelSyllabusDiagram` → `ALevelSyllabusDiagram[]`
5. `ExtractALevelCrossSubjectTopics` → `ALevelCrossSubjectTopicSet`

## The 3 boards (exam_board enum)

- `AQA` — Assessment and Qualifications Alliance
- `OCR` — Oxford Cambridge and RSA (Oxford, Cambridge, Pearson)
- `EDEXCEL` — Pearson Edexcel

## The 2 tiers (level enum)

- `AS_LEVEL` — Advanced Subsidiary (50% of A-Level)
- `A_LEVEL` — Advanced (full A-Level)

## Files

- `canonical_a_level_per_subject.baml` — the canonical 15-subject BAML surface (the codegen pipeline in Phase 5 consumes this)

## Related BAML (existing)

- `baml_src/british_isles/england/education/subject_taxonomy.baml` — the 49-subject A-Level enum (per the 2026-08-10-england-biiep-pipeline-v1 change)
- `baml_src/british_isles/england/education/curriculum_syllabus.baml` — the unified England syllabus extractor (covers both GCSE + A-Level)
- `baml_src/british_isles/england/education/england_aqa.baml` — the AQA-specific extraction

## DO NOT

- **Never** hand-write a Pydantic model that duplicates a BAML class — codegen it from `.baml`.
- **Never** edit `england/curriculum_syllabus.baml` directly — extend the canonical `england/a_level_extraction/canonical_a_level_per_subject.baml` instead.

## Skill pointers

- [`baml`](../../../../../.agents/skills/baml/SKILL.md) — BAML schema authoring
- [`schema-codegen`](../../../../../.agents/skills/schema-codegen/SKILL.md) — the codegen pipeline (Phase 5)
- [`centralized-registry`](../../../../../.agents/skills/centralized-registry/SKILL.md) — MODEL_REGISTRY

<!-- generated: 2026-08-13 (per the 2026-08-13-web-monorepo-consolidation-and-agent-integration-v1 change, Phase 4) -->
