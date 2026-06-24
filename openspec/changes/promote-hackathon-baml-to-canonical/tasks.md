# Tasks: promote-hackathon-baml-to-canonical

## 1. Add 4 canonical BAML functions

- [x] Create `oideachais/baml_src/circular_extraction.baml` (the
      CircularReference + TopicDistribution + MarkingSchemeSummary
      + CircularExtraction + ExtractCircularMeta)
- [x] Append `CompareCelticNations` (+ CurriculumMapping +
      CrossNationComparison) to `tuatha/baml_src/celtic_curriculum.baml`
- [x] Append `GenerateExitCardQuestions` (+ ExitCardQuestion +
      ExitCardSet) to `tuatha/baml_src/player_assessment.baml`
- [x] Append `GenerateNpcDialogue` (+ NpcDialogue +
      NpcDialogueExchange) to `tuatha/baml_src/mythology_extraction.baml`

## 2. Replace BAML_HACKATHON_CHAINED with LitellmClient

- [x] In all 4 new function bodies, replace
      `client BAML_HACKATHON_CHAINED` with `client LitellmClient`
      (the canonical client from oideachais/baml_src/clients.baml)

## 3. Delete the hackathon BAML

- [x] `git rm -r spaces/_common/baml/` (deletes
      hackathon_schemas.baml + the empty directory)

## 4. Spec deltas

- [x] `openspec/changes/promote-hackathon-baml-to-canonical/specs/oideachais-baml-schemas/spec.md`
      - 1 ADDED Requirement: Circular extraction BAML
- [x] `openspec/changes/promote-hackathon-baml-to-canonical/specs/tuatha-platform/spec.md`
      - 3 ADDED Requirements: Cross-nation curriculum comparison +
        Formative exit cards + NPC dialogue generation

## 5. Validate

- [x] `openspec validate promote-hackathon-baml-to-canonical --strict`

## 6. Commit + push + archive

- [x] Commit with message
      `promote-hackathon-baml-to-canonical: 4 BAML functions to canonical locations`
- [x] Archive the openspec change
- [x] `git push`
