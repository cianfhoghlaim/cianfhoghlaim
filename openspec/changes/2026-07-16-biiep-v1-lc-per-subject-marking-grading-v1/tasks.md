# Tasks — 2026-07-16-biiep-v1-lc-per-subject-marking-grading-v1

## 1. Audit (DONE)

- [x] 1.1 Audit existing per-subject BAML infrastructure (`qpack_<subject>.baml` × 6)
- [x] 1.2 Audit canonical `marking_scheme.baml` + `exam_paper_layout.baml`
- [x] 1.3 Audit `CelticIngestionComponent` + `CelticMaterialsComponent`
- [x] 1.4 Audit existing per-subject defs YAMLs (leaving_cert_mathematics pattern)

## 2. Per-subject marking scheme BAML files (DONE)

- [x] 2.1 `baml/education/marking/mathematics_marking.baml` (+ MathMarkingBand, MathQuestionType, MathCommonMistake)
- [x] 2.2 `baml/education/marking/chemistry_marking.baml` (+ ChemQuestionType, ChemExperimentType, ChemCommonMistake)
- [x] 2.3 `baml/education/marking/geography_marking.baml` (+ GeoSkillType, GeoRegionalFocus, GeoCommonMistake)
- [x] 2.4 `baml/education/marking/gaeilge_marking.baml` (+ GaelSkillType, GaelRegister, GaelCommonMistake — GA primary)
- [x] 2.5 `baml/education/marking/english_marking.baml` (+ EngGenreType, EngSkillType, EngCommonMistake)
- [x] 2.6 `baml/education/marking/computer_science_marking.baml` (+ CsQuestionType, CsNotationType, CsCommonMistake)

## 3. Per-subject grading BAML files (DONE)

- [x] 3.1 `baml/education/grading/mathematics_grading.baml` (GradeMathematicsResponse + ExplainMathematicsMarkingScheme)
- [x] 3.2 `baml/education/grading/chemistry_grading.baml`
- [x] 3.3 `baml/education/grading/geography_grading.baml`
- [x] 3.4 `baml/education/grading/gaeilge_grading.baml` (Irish-medium feedback)
- [x] 3.5 `baml/education/grading/english_grading.baml`
- [x] 3.6 `baml/education/grading/computer_science_grading.baml`

## 4. Per-subject defs YAMLs (DONE)

- [x] 4.1 6 L1 ingestion defs at `orchestration/defs/1_ingestion/marking/<subject>.yaml`
- [x] 4.2 6 L2 materials defs at `orchestration/defs/2_materials/grading/<subject>.yaml`

## 5. Verify (DONE)

- [x] 5.1 All 12 BAML files exist
- [x] 5.2 All 12 defs YAMLs exist
- [x] 5.3 Per-subject discriminators are non-overlapping

## 6. OpenSpec change (DONE)

- [x] 6.1 Write `proposal.md` (with Dependencies section)
- [x] 6.2 Write `tasks.md`
- [x] 6.3 Write `specs/british-isles-education-pipeline/spec.md` (1 ADDED requirement)

## 7. Commit + push (DONE)

- [x] 7.1 git add + commit with the required commit message
- [x] 7.2 git push --set-upstream origin pick-4-biep-v1
- [x] 7.3 Confirm branch is up to date with `origin/pick-4-biep-v1`
