# Tasks: BAML Extraction Completion + LC Pilot Scale

## Phase 0 — Foundation work shipped (5 tasks done before this change)

Per the `2026-08-08-lakehouse-extensive-hydration-v1` change (already
archived as `2026-08-12-2026-08-08-lakehouse-extensive-hydration-v1`):

- [x] **T0.1** `lc5_chemistry_diagrams_extracted` is un-stubbed at
  `orchestration/defs/2_materials/lc_extraction/lc5_assets.py:218-313`
  — the one real implementation of the LC5 factory pattern.
- [x] **T0.2** `ExtractSyllabusDiagram` gained the `image: image[]?`
  parameter (backwards-compatible) at
  `baml_src/british_isles/ireland/education/lc_extraction/syllabus_diagram.baml:93`.
- [x] **T0.3** `pdf_to_image_bridge.py` created at
  `meaisinfhoghlaim/document_factory/pdf_to_image_bridge.py:155` —
  pymupdf-based page render → `baml_py.Image`.
- [x] **T0.4** `BAML_AVAILABLE` import fallback fixed in `lc5_assets.py`
  (now falls back to `baml_client.baml_client.sync_client`).
- [x] **T0.5** 139 real corpus rows + 11 real syllabus cross-check
  rows committed to live DuckLake (independently re-verified in a
  fresh connection/session).

## Phase 1 — Kickstart (2 tasks, ~2 hours; in progress as of 2026-08-13)

- [x] **T1.1** Un-stub `lc5_computer_science_papers_extracted` (the
  simplest non-chemistry LC5 asset — text-only BAML call against
  `ExtractExamPaperLayout`, no images required). Mirrors the
  `lc5_chemistry_diagrams_extracted` pattern minus the image bridge.
  Implemented at `orchestration/defs/2_materials/lc_extraction/lc5_assets.py:315`.
- [ ] **T1.2** Add the corresponding BAML function-side prompt to
  `baml_src/british_isles/ireland/education/lc_extraction/exam_paper_layout.baml`
  for computer_science (real prompt, not the
  `"Auto-generated extraction prompt."` placeholder).

## Phase 2 — Refactor chemistry pilot into factory (3 tasks, ~1 hour)

- [ ] **T2.1** Read `orchestration/defs/2_materials/lc_extraction/lc_chemistry_pilot_assets.py` to understand the pattern
- [ ] **T2.2** Create `orchestration/defs/2_materials/lc_extraction/lc_subjects.py` with `lc_subject_pilot_factory(subject)` returning 3 assets + 3 checks
- [ ] **T2.3** Refactor `lc_chemistry_pilot_assets.py` to delegate to the factory

## Phase 3 — Real prompts for 6 LC subjects (5 tasks, ~4 hours)

- [ ] **T3.1** Read existing `baml_src/british_isles/ireland/education/lc_extraction/curriculum_syllabus.baml` + identify stub vs real
- [ ] **T3.2** Add real prompts for chemistry + mathematics + geography + english + computer_science + applied_mathematics in `curriculum_syllabus.baml`
- [ ] **T3.3** Add real prompts for 6 LC subjects in `exam_paper_layout.baml` (ExtractExamPaperLayout)
- [ ] **T3.4** Add real prompts for 6 LC subjects in `marking_scheme.baml` (ExtractMarkingSchemeGuideline)
- [ ] **T3.5** Add real prompts for 6 LC subjects in `syllabus_diagram.baml` (ExtractSyllabusDiagram)

## Phase 4 — Irish-language BAML client (2 tasks, ~30 minutes)

- [ ] **T4.1** Read `baml_src/clients.baml` to find the canonical client block
- [ ] **T4.2** Add `gaeilge_lc_client` block with `provider: litellm`, `model: uccix-mistral-24b`

## Phase 5 — Dagster registration (2 tasks, ~30 minutes)

- [ ] **T5.1** Create `orchestration/defs/2_materials/lc_extraction/lc_subjects/defs.yaml` with 6 subjects × 3 assets = 18 assets
- [ ] **T5.2** Run `.venv/bin/baml-cli generate --from baml_src` to regenerate 14 BAML client files

## Phase 6 — Validate (3 tasks, ~15 minutes)

- [ ] **T6.1** `openspec validate 2026-08-10-baml-extraction-completion-v1 --strict`
- [ ] **T6.2** `mise run lint:registry && mise run lint:skills`
- [ ] **T6.3** Smoke test: `dagster asset materialize --select lc_<subject>_pilot_loaded` for 1 subject

## Total (remaining work after Phase 1 kickstart)

- **13 tasks** across **5 phases** (Phases 2-6)
- **~6 hours of focused work**
- **~30+ new BAML prompts** (real prompts replacing stubs)
- **18 new Dagster assets** (6 subjects × 3 assets)

