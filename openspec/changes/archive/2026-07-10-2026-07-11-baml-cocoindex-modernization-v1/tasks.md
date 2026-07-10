# BAML + CocoIndex modernization v1 — Tasks

Numbered mirror of the 3 in-scope phases (Phase A5 / B4 / B5 /
B6 / C / zoomcamp-spec are deferred to follow-ups per
[`proposal.md`](./proposal.md)).

## Phase A — Duplicate + collision removal (scoped)

- [ ] **1.** Preflight: capture the audit baseline.
  Run `grep -rE "^class (MarkingScheme|LearningOutcome|ExamPaper|
  BilingualText|EvidenceLink|CurriculumStrand|ExamSection|
  ExamQuestion|CourtForm|CourtFee|CourtRule|Judgement|PIABPage|
  PastPaper|DuchasPersonName|Subject|Skill|RubricDescriptor|
  VocabularyNote|CurriculumSpecification|AssessmentComponent|
  CrossNationComparison)\b" cianfhoghlaim/baml/ --include='*.baml'
  | wc -l` and record the number in the final report.
  Capture similarly for the 9 function dups + 11 enum dups.

- [ ] **2.** Delete the 4 legacy files at
  `cianfhoghlaim/baml/shared/baml_src/`:
  - [ ] 2.1 `clients.baml` (96 LOC, replaced by
    canonical `baml/clients.baml`)
  - [ ] 2.2 `clients_llama_swap.baml` (~40 LOC,
    replaced by canonical `baml/clients_llama_swap.baml`)
  - [ ] 2.3 `generators.baml` (28 LOC, replaced by
    `baml/baml.toml` generator blocks)
  - [ ] 2.4 `leaving_cert_marking_scheme_extraction.baml`
    (79 LOC, byte-identical to `education/pdfs/leaving_cert_marking_scheme.baml`)

- [ ] **3.** Delete `cianfhoghlaim/baml/processing/ireland_legal_extraction.baml`
  (621 LOC). All 5 classes (`CourtForm`, `CourtFee`, `CourtRule`,
  `Judgement`, `PIABPage`) + `CourtLevel` enum already live under
  `cianfhoghlaim/baml/education/law/`.

- [ ] **4.** Re-run the post-delete baseline `grep` from step 1.
  Record the new counts. The deletes in 2.4 + 3 alone should reduce
  the dup count by ~8 across all three categories (MarkingScheme
  ×3 → 2, MarkingType ×2 → 1, CourtRule/Form/Fee/Judgement/PIABPage
  /CourtLevel each ×2 → 1).

- [ ] **5.** Create `cianfhoghlaim/baml/processing/docs_skills_extraction.baml`
  with:
  - [ ] 5.1 `class DocSkillTag` (canonical `field Type @description("...")`
    syntax, BAML 0.223.0 conformant)
  - [ ] 5.2 `class Triple` (3 string fields: subject, predicate, object)
  - [ ] 5.3 `function ExtractDocSkillTag(content: string, path: string) -> DocSkillTag`
    (referenced from `cocoindex/docs_skills_consolidation.py:247,273`)
  - [ ] 5.4 `function ExtractTriples(content: string, path: string) -> Triple[]`
    (referenced from `cocoindex/docs_skills_consolidation.py:293`)
  - [ ] 5.5 1 `test` block (to confirm `baml-cli test` would
    pick it up once the CI gate is wired — Phase B6 follow-up)

- [ ] **6.** Verify post-Phase-A:
  - [ ] 6.1 `ls cianfhoghlaim/baml/shared/baml_src/*.baml | wc -l` = 0
  - [ ] 6.2 `ls cianfhoghlaim/baml/processing/ireland_legal_extraction.baml` returns "No such file"
  - [ ] 6.3 `grep -E "ExtractDocSkillTag|ExtractTriples|class DocSkillTag|class Triple" cianfhoghlaim/baml/processing/docs_skills_extraction.baml` returns 4 matches (the 2 functions + 2 classes).

## Phase B — BAML v0.223 feature adoption (scoped)

- [ ] **7.** Bump generator version `0.222.0` → `0.223.0` at:
  - [ ] 7.1 `cianfhoghlaim/baml/baml.toml` (`[project]` block)
  - [ ] 7.2 `cianfhoghlaim/baml/baml.toml` (`[generators.lang_py]` block)
  - [ ] 7.3 `cianfhoghlaim/baml/baml.toml` (`[generators.lang_ts]` block)
  Note: the `baml/shared/baml_src/generators.baml` deletes in step 2.3
  absorb the 4th version field, so no separate bump needed there.

- [ ] **8.** Modify `cianfhoghlaim/baml/clients.baml`:
  - [ ] 8.1 Add `timeout { total_ms 60000 }` to `generator default`
  - [ ] 8.2 Add `timeout { total_ms 60000 }` to `generator local_vision_qwen`
  - [ ] 8.3 Add `timeout { total_ms 60000 }` to `generator local_vision_glm`
  - [ ] 8.4 Add `timeout { total_ms 60000 }` to `generator local_vision_moondream`
  - [ ] 8.5 Add `timeout { total_ms 60000 }` to `generator gemini_2_flash`
  - [ ] 8.6 Add `timeout { total_ms 60000 }` to `generator gemini_1_5_pro`
  - [ ] 8.7 Add `timeout { total_ms 60000 }` to `generator gemini_pro`
  - [ ] 8.8 Add `timeout { total_ms 60000 }` to `generator gemini_2_5_flash`
  - [ ] 8.9 Add NEW `generator local_vision_gemma4` (per the
    Phase C tutorial 3 side-by-side plan)
  - [ ] 8.10 Add NEW `generator local_vision_qwen3vl` (per the
    Phase C tutorial 3 side-by-side plan)
  Note: the `retry_policy Exponential` block is already in all 8
  generators per T4 of the agent-fleet + observability change
  (`openspec/changes/2026-07-10-fix-baml-codegen-v4-syntax-v1`),
  confirmed by `grep "retry_policy" clients.baml`.

- [ ] **9.** Verify post-Phase-B:
  - [ ] 9.1 `grep "version" cianfhoghlaim/baml/baml.toml` returns 3
    matches with `"0.223.0"` (or `0.223.0` without quotes)
  - [ ] 9.2 `grep -c "timeout { total_ms 60000 }" cianfhoghlaim/baml/clients.baml` returns ≥8
  - [ ] 9.3 `grep -E "generator local_vision_gemma4|generator local_vision_qwen3vl" cianfhoghlaim/baml/clients.baml` returns 2 matches

## Phase C — 5 tutorials (DEFERRED to follow-up)

- [ ] **10.** **DEFERRED** — the 5 tutorial notebooks at
  `cianfhoghlaim/notebooks/13_baml_cocoindex_tutorial/` are
  tracked under `2026-07-12-baml-cocoindex-tutorials-v1`
  (a separate openspec change). See proposal.md "Out of scope".

## OpenSpec deltas (scoped)

- [ ] **11.** Write `specs/oideachais-baml-schemas/spec.md`
  MODIFIED delta (+4 reqs).

- [ ] **12.** Write `specs/meaisinfhoghlaim-agent-frameworks/spec.md`
  MODIFIED delta (+2 reqs).

- [ ] **13.** Write `specs/british-isles-education-pipeline/spec.md`
  MODIFIED delta (+2 reqs).

- [ ] **14.** Write `specs/oideachais-marimo-dashboards/spec.md`
  MODIFIED delta (+2 reqs).

  Note: `end-to-end-llm-zoomcamp-style-tutorial` spec delta is
  dropped from this change — that capability spec doesn't exist
  yet; it's part of the tutorials follow-up.

## Validation

- [ ] **15.** `openspec validate 2026-07-11-baml-cocoindex-modernization-v1
  --strict` passes.

- [ ] **16.** `grep -E "^class (MarkingScheme|LearningOutcome|ExamPaper|
  BilingualText|EvidenceLink|CurriculumStrand|ExamSection|
  ExamQuestion|CourtForm|CourtFee|CourtRule|Judgement|PIABPage|
  PastPaper|DuchasPersonName|Subject|Skill|RubricDescriptor|
  VocabularyNote|CurriculumSpecification|AssessmentComponent|
  CrossNationComparison)\b" cianfhoghlaim/baml/ --include='*.baml'
  | wc -l` returns the post-delete count (≤ audit baseline minus
  the 8 deletes that go away).

- [ ] **17.** `grep -rE "^function (ExtractCurriculumSyllabus|
  ExtractMarkingScheme|ExtractCourtRule|ExtractCourtForm|
  ExtractCourtFee|ExtractJudgement|ExtractPIABPage|
  ExtractPublication|CompareCurricula)\b" cianfhoghlaim/baml/
  --include='*.baml' | wc -l` returns the post-delete count.

- [ ] **18.** `grep -rE "^enum (IrishDialect|CelticLanguage|
  EducationLevel|CourtLevel|PartOfSpeech|SkillCategory|
  QuestionType|MusicGenre|MarkingType|LanguageCode|
  DocumentType)\b" cianfhoghlaim/baml/ --include='*.baml' | wc -l`
  returns the post-delete count.

## Commit + push

- [ ] **19.** Single commit on `pick-4-biep-v1` (NOT main).

- [ ] **20.** `git push --set-upstream origin pick-4-biep-v1`.

## Acceptance gates summary

| Gate | Expected |
|:--|:--|
| `openspec validate --strict` | passes |
| 4 spec deltas added | yes (baml-schemas, agent-frameworks, education-pipeline, marimo-dashboards) |
| `ls baml/shared/baml_src/*.baml \| wc -l` | 0 |
| `ls baml/processing/ireland_legal_extraction.baml` | "No such file" |
| `baml/processing/docs_skills_extraction.baml` | exists with the 2 functions + 2 classes + 1 test block |
| `baml.toml` | `0.223.0` (3 places) |
| `clients.baml` | 8 `timeout { total_ms 60000 }` blocks + 2 new local-vision generators |
| `grep "^class ...$" --include='*.baml'` | ≤ audit baseline minus 8 deletes |
