# Tasks: BAML Extraction Completion + LC Pilot Scale

## Phase 1 — Refactor chemistry pilot into factory (3 tasks, ~1 hour)

- [ ] **T1.1** Read `orchestration/defs/2_materials/lc_extraction/lc_chemistry_pilot_assets.py` to understand the pattern
- [ ] **T1.2** Create `orchestration/defs/2_materials/lc_extraction/lc_subjects.py` with `lc_subject_pilot_factory(subject)` returning 3 assets + 3 checks
- [ ] **T1.3** Refactor `lc_chemistry_pilot_assets.py` to delegate to the factory

## Phase 2 — Real prompts for 6 LC subjects (5 tasks, ~4 hours)

- [ ] **T2.1** Read existing `baml_src/british_isles/ireland/education/lc_extraction/curriculum_syllabus.baml` + identify stub vs real
- [ ] **T2.2** Add real prompts for chemistry + mathematics + geography + english + computer_science + applied_mathematics in `curriculum_syllabus.baml`
- [ ] **T2.3** Add real prompts for 6 LC subjects in `exam_paper_layout.baml` (ExtractExamPaperLayout)
- [ ] **T2.4** Add real prompts for 6 LC subjects in `marking_scheme.baml` (ExtractMarkingSchemeGuideline)
- [ ] **T2.5** Add real prompts for 6 LC subjects in `syllabus_diagram.baml` (ExtractSyllabusDiagram)

## Phase 3 — Irish-language BAML client (2 tasks, ~30 minutes)

- [ ] **T3.1** Read `baml_src/clients.baml` to find the canonical client block
- [ ] **T3.2** Add `gaeilge_lc_client` block with `provider: litellm`, `model: uccix-mistral-24b`

## Phase 4 — Dagster registration (2 tasks, ~30 minutes)

- [ ] **T4.1** Create `orchestration/defs/2_materials/lc_extraction/lc_subjects/defs.yaml` with 6 subjects × 3 assets = 18 assets
- [ ] **T4.2** Run `.venv/bin/baml-cli generate --from baml_src` to regenerate 14 BAML client files

## Phase 5 — Validate (3 tasks, ~15 minutes)

- [ ] **T5.1** `openspec validate 2026-08-10-baml-extraction-completion-v1 --strict`
- [ ] **T5.2** `mise run lint:registry && mise run lint:skills`
- [ ] **T5.3** Smoke test: `dagster asset materialize --select lc_<subject>_pilot_loaded` for 1 subject

## Total

- **15 tasks** across **5 phases**
- **~6 hours of focused work**
- **~30+ new BAML prompts** (real prompts replacing stubs)
- **18 new Dagster assets** (6 subjects × 3 assets)
