# Tasks — BIEP v1 Phases 6+7 Unblock

## 1. Pre-flight

- [x] Checkout `pick-4-biep-v1` branch
- [x] Confirm branch is in sync with `origin/pick-4-biep-v1`
- [x] Note existing untracked dirty state (parallel-agent OCR work + submodule
  modification) — does not block this change

## 2. Phase 6 — 6 per-subject marimo notebooks

### 2.1 Inspect existing patterns

- [x] Read existing stub notebooks at `cianfhoghlaim/notebooks/leaving_cert/`
- [x] Read canonical 07_subject_full_pipeline.py parameterised pattern
- [x] Read qpack_<subject>.baml files for BAML extractor functions
- [x] Read nb_utils.py for `connect_biep_lakehouse` helper
- [x] Read canonical BIEP spec at `openspec/specs/british-isles-education-pipeline/spec.md`

### 2.2 Enhance the 5 existing stubs

- [ ] Enhance `chemistry.py` — add altair charts, BAML extractor calls,
      bilingual EN/GA strings, ~300-400 LOC
- [ ] Enhance `computer_science.py` — same pattern
- [ ] Enhance `gaeilge.py` — same pattern + cross-linguistic mapping
- [ ] Enhance `geography.py` — same pattern + fieldwork requirements
- [ ] Enhance `mathematics.py` — same pattern
- [ ] Enhance `english.py` — same pattern (already at 155 LOC, add altair charts)

### 2.3 Create the 6th cross-subject notebook

- [ ] Create `06_en_vs_ga_comparison.py` — bilingual EN ↔ GA competency
      comparison across the 5 EN/GA subjects + bilingual coverage matrix

## 3. Phase 7 — MotherDuck lc_pdf_sync_flight

- [ ] Create `cianfhoghlaim/motherduck/flights/lc_pdf_sync_flight.py`
      (daily Python job: cocoindex update + dagster materialize + status row)
- [ ] Create `cianfhoghlaim/motherduck/flights/config.yaml`
      (cron `0 4 * * *`)

## 4. Spec deltas

- [ ] Add 2 ADDED Requirements to
      `openspec/changes/2026-07-13-biep-v1-phases-6-7-unblock-v1/specs/british-isles-education-pipeline/spec.md`:
      - Phase 6 — 6 per-subject marimo notebooks
      - Phase 7 — MotherDuck lc_pdf_sync_flight

## 5. Verification

- [ ] All 7 .py files (6 notebooks + 1 flight) AST-parse cleanly
- [ ] `openspec validate 2026-07-13-biep-v1-phases-6-7-unblock-v1 --strict` passes

## 6. Commit + push

- [ ] Commit with the conventional `feat(biep):` prefix
- [ ] Push to `origin/pick-4-biep-v1` (NOT `main`)