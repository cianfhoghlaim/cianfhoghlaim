# 2026-07-29-biep-v3-england-full-coverage-v1 — Tasks

## Pre-implementation

- [ ] Verify openspec CLI ≥1.4: `openspec --version` → 1.4.1
- [ ] Verify Phases 0 + 1 + 2 merged
- [ ] Verify the ccc code index is fresh: `bun run ccc:index`

## Stage 1 — OCR + Edexcel BAML enums

- [ ] Create `baml_src/british_isles/england/education/subject_taxonomy_ocr.baml`
  with `GCSEOCRSubject` (43) + `ALevelOCRSubject` (49) enums
- [ ] Create `baml_src/british_isles/england/education/subject_taxonomy_edexcel.baml`
  with `GCSEDexcelSubject` (43) + `ALevelEdexcelSubject` (49) enums
- [ ] Run `cd baml_src && uv run baml-cli generate`

## Stage 2 — Generic ExtractUKQualSpec

- [ ] Add `ExtractUKQualSpec(board: AwardingBody, pdf_text: string, subject: string, qualification_level: string)` to
  `baml_src/british_isles/england/education/curriculum_syllabus.baml`
- [ ] Mark `ExtractAQAQualSpec` / `ExtractOCRQualSpec` / `ExtractEdexcelQualSpec`
  as `@deprecated` (the registry's `baml_function` field now points at the
  generic form)

## Stage 3 — Generic England DLT pipeline

- [ ] Create `dlt/british_isles/england/education/england_jurisdiction_pipeline.py`
  with `england_jurisdiction_pipeline()` factory

## Stage 4 — Generic England Dagster assets

- [ ] Create `orchestration/defs/2_materials/england_education/__init__.py`
- [ ] Create `orchestration/defs/2_materials/england_education/generic_england_assets.py`
  with 3 generic assets + 1 asset_check

## Stage 5 — Registry loader extension

- [ ] Extend `dlt/british_isles/_cross/registry_loader.py:load_england_subjects()`
  to return the FULL 276-row seed (43 GCSE + 49 A-Level × 3 boards)
- [ ] Test: `python3 -c "from dlt.british_isles._cross.registry_loader import seed_registry; print(seed_registry())"`
  returns `{'england': 276}`

## Stage 6 — Companion notebook verification

- [ ] Tab 2 (Nation comparison) shows `england >= 276`

## Stage 7 — Spec delta + validation

- [ ] Write the spec delta to
  `openspec/changes/2026-07-29-biep-v3-england-full-coverage-v1/specs/british-isles-education-pipeline/spec.md`
- [ ] Run `openspec validate 2026-07-29-biep-v3-england-full-coverage-v1 --strict`
- [ ] Commit + push the change
- [ ] Run `mise run lint:skills` — must remain 53/53
- [ ] After the PR merges and the change is deployed, run
  `openspec archive 2026-07-29-biep-v3-england-full-coverage-v1 --yes`

## Post-implementation hand-off

- [ ] File any remaining bugs as GitHub issues
- [ ] Update `docs/cianfhoghlaim-england-pipeline.md`
- [ ] Run `./scripts/sync_agent_docs.sh`