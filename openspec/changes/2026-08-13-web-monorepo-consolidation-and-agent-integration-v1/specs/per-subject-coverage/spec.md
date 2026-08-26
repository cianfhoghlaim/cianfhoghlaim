# per-subject-coverage Specification

## Purpose

Formalize the per-subject coverage matrix for the 60 subjects
across the 4 stages (LC + JC + GCSE + A-Level). Each subject
MUST have a complete end-to-end pipeline from BAML extraction
to TanStack Start routes.

The system is added by the
2026-08-13-web-monorepo-consolidation-and-agent-integration-v1
openspec change (Phase P).

## ADDED Requirements

### Requirement: Every subject SHALL have 8 BAML extraction functions

The 60 subjects × 8 BAML functions MUST exist at
`baml_src/<area>/<stage>/<subject>/<function>.baml`:

1. `ExtractCurriculumSyllabus`
2. `ExtractExamPaperLayout`
3. `ExtractMarkingScheme`
4. `ExtractCrossLinguistic`
5. `ExtractSyllabusDiagram`
6. `ExtractLearningOutcome`
7. `ExtractKeyTerm`
8. `ExtractTopicGraph`

The 60 subjects are:

- 14 LC (Maths, Applied Maths, Chemistry, Physics, Biology,
  English, Gaeilge, French, History, Geography, Business,
  Accounting, Art, Music, Computer Science)
- 8 JC (Maths, English, Gaeilge, Science, History, Geography,
  French, Business)
- 9 GCSE (Maths, English Lit, English Lang, Biology, Chemistry,
  Physics, History, Geography, MFL)
- 15+ A-Level (Maths, Further Maths, Chemistry, Biology, Physics,
  English Lit, English Lang, History, Geography, Psychology,
  Economics, Business, Politics, Sociology, MFL)

#### Scenario: A new subject is added to BIEP

- **WHEN** a developer adds a new subject (e.g. LC Music OL)
- **THEN** all 8 BAML functions MUST be added at
  `baml_src/british_isles/ireland/education/lc_extraction/music.baml`
- **AND** the DLT source MUST be added at
  `dlt_sources/british_isles/ireland/education/lc_music.py`
- **AND** the CocoIndex flow MUST be added at
  `cocoindex_flows/biep_parity/ireland_lc_music_embedding.py`
- **AND** the Convex schema MUST be added at
  `web/apps/oideachais-dashboard/convex/lc/music.ts`
- **AND** the CopilotKit actions MUST be added at
  `web/hono-api/src/routes/copilotkit/lc/music.ts`
- **AND** the routes MUST be added at
  `web/apps/oideachais/routes/lc/music/`

### Requirement: Subject coverage matrix SHALL be tracked

The system MUST track the per-subject coverage matrix at
`openspec/specs/per-subject-coverage/subjects.md`. Each row
records which of the 6 components (BAML / DLT / CocoIndex /
Convex / CopilotKit / Routes) is present.

#### Scenario: CI gate for subject coverage

- **WHEN** the operator runs `mise run lint:subject-coverage`
- **THEN** the script MUST verify all 60 subjects have all
  6 components
- **AND** MUST exit 1 if any component is missing for any subject
