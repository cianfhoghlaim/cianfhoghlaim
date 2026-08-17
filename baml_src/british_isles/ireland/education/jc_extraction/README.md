# `baml_src/british_isles/ireland/education/jc_extraction/` — Junior Cycle 8-priority-subject BAML

> **The canonical 8-subject Junior Cycle BAML extraction surface for the
> 8 priority JC subjects (mathematics, english, gaeilge, science, history,
> geography, french, business).** Per the 2026-08-13-web-monorepo-consolidation-
> and-agent-integration-v1 change (Phase 4).

## The 8 priority subjects (JC_COMMON level)

| Slug | Display name | NCCA LO prefix |
|:--|:--|:--|
| `MATHEMATICS` | Mathematics | `JC-MATH-LO` |
| `ENGLISH` | English | `JC-ENGL-LO` |
| `GAEILGE` | Gaeilge | `JC-GAEL-LO` |
| `SCIENCE` | Science | `JC-SCI-LO` |
| `HISTORY` | History | `JC-HIST-LO` |
| `GEOGRAPHY` | Geography | `JC-GEOG-LO` |
| `FRENCH` | French | `JC-FREN-LO` |
| `BUSINESS` | Business | `JC-BUS-LO` |

## The 8 BAML functions (per subject)

1. `ExtractJCCurriculumSyllabus` → `JuniorCycleCurriculumSpec`
2. `ExtractJCExamPaperLayout` → `JuniorCycleExamPaper`
3. `ExtractJCMarkingSchemeGuideline` → `JuniorCycleMarkingScheme`
4. `ExtractJCSyllabusDiagram` → `JuniorCycleSyllabusDiagram[]`
5. `ExtractJCCrossLinguisticConcept` → `JuniorCycleCrossLinguistic[]`
6. `ExtractCrossSubjectTopics` → `JuniorCycleCrossSubjectTopicSet`

## Files

- `canonical_jc_per_subject.baml` — the canonical 8-subject BAML surface (the codegen pipeline in Phase 5 consumes this)

## Related BAML (existing)

- `baml_src/british_isles/ireland/education/junior_cycle/` — the 18-subject BAML files (8 priority + 10 short courses + electives) per the 2026-07-20-biep-v2-junior-cycle-extraction-v1 change

## DO NOT

- **Never** hand-write a Pydantic model that duplicates a BAML class — codegen it from `.baml`.
- **Never** edit `junior_cycle/jc_curriculum_syllabus.baml` directly — extend the canonical `canonical_jc_per_subject.baml` instead.

## Skill pointers

- [`baml`](../../../../.agents/skills/baml/SKILL.md) — BAML schema authoring
- [`schema-codegen`](../../../../.agents/skills/schema-codegen/SKILL.md) — the codegen pipeline (Phase 5)
- [`centralized-registry`](../../../../.agents/skills/centralized-registry/SKILL.md) — MODEL_REGISTRY

<!-- generated: 2026-08-13 (per the 2026-08-13-web-monorepo-consolidation-and-agent-integration-v1 change, Phase 4) -->
