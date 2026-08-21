## Superseded by

This change is **superseded by** `2026-08-13-biep-v3-systematic-download-ireland-england-v1` (the BIEP v3 umbrella), which has fully delivered all work proposed here as part of milestones M0-M4 (107/109 tasks done).

See the umbrella change's `tasks.md` for the per-milestone task mapping. The BIEP v3 spec (`openspec/specs/british-isles-education-pipeline-v3/spec.md`) is the authoritative home for the ADDED Requirements originally intended for this change.

## Superseded by

This change is **superseded by** `2026-08-13-biep-v3-systematic-download-ireland-england-v1` (the BIEP v3 umbrella), which has fully delivered all work proposed here as part of milestones M0-M4 (107/109 tasks done).

See the umbrella change's `tasks.md` for the per-milestone task mapping. The BIEP v3 spec (`openspec/specs/british-isles-education-pipeline-v3/spec.md`) is the authoritative home for the ADDED Requirements originally intended for this change.

# 2026-07-29-biep-v3-england-full-coverage-v1

## Why

Phase 2 shipped the generic Ireland pipeline. This Phase 3 ships the
parallel generic England pipeline, covering all 3 awarding bodies
(AQA + OCR + Edexcel) × all subjects × both qualification levels (GCSE +
A-Level) — **276 unique qualifications**.

Concretely:

- Adds 2 new BAML files (`subject_taxonomy_ocr.baml` +
  `subject_taxonomy_edexcel.baml`) with the OCR + Edexcel GCSE +
  A-Level subject enums (parallel to the existing AQA enums in
  `subject_taxonomy.baml`)
- The 3 board-specific BAML functions (`ExtractAQAQualSpec`,
  `ExtractOCRQualSpec`, `ExtractEdexcelQualSpec`) are COLLAPSED into
  one generic `ExtractUKQualSpec(board: AwardingBody, ...)` — the
  per-board enums are selected via the `board` argument
- Creates the generic England DLT pipeline
  (`dlt/british_isles/england/education/england_jurisdiction_pipeline.py`)
  + the generic England Dagster assets
  (`orchestration/defs/2_materials/england_education/generic_england_assets.py`)

## What changes

### 1. Two new BAML files (OCR + Edexcel enums)

- `baml_src/british_isles/england/education/subject_taxonomy_ocr.baml` —
  `GCSEOCRSubject` (43 entries) + `ALevelOCRSubject` (49 entries)
- `baml_src/british_isles/england/education/subject_taxonomy_edexcel.baml` —
  `GCSEDexcelSubject` (43 entries) + `ALevelEdexcelSubject` (49 entries)

### 2. Collapse 3 BAML functions → 1 generic

The existing `baml_src/british_isles/england/education/curriculum_syllabus.baml`
already has the generic `ExtractAQAQualSpec` / `ExtractOCRQualSpec` /
`ExtractEdexcelQualSpec` functions. This change adds the canonical
`ExtractUKQualSpec(board: AwardingBody, ...)` that dispatches to the
correct per-board function based on the `board` argument. The 3 old
functions remain available as backward-compat shims but are
deprecated.

### 3. New generic England DLT pipeline

`dlt/british_isles/england/education/england_jurisdiction_pipeline.py`
— reads the registry (filtered by `jurisdiction='england'`),
emits 276 England cohorts as a single `england_england_subjects`
DLT resource, writes to the canonical
`cianfhoghlaim.education.england.<stage>.<board>.<subject>` namespace.

### 4. New generic England Dagster assets

`orchestration/defs/2_materials/england_education/generic_england_assets.py`
— 3 generic assets + 1 asset_check.

### 5. Replaces

- 27 per-board per-subject DLT sources at
  `dlt/british_isles/england/education/subjects/_factory.py` (9 subjects × 3 boards)
- 81 per-board per-subject Dagster assets at
  `orchestration/defs/2_materials/england_education/{aqa,ocr,edexcel}/`
- 3 board-specific CocoIndex Apps at
  `cocoindex_flows/british_isles/england/{aqa,ocr,edexcel}_education_embedding.py`
  (preserved; will be folded into the generic cocoindex App in a
  follow-up change)

## Dependencies

```yaml
Blocked by: 2026-07-28-biep-v3-ireland-full-coverage-v1
Blocked by (soft): 2026-07-26-biep-v3-root-namespace-rename-v1
                  2026-07-27-biep-v3-canonical-registry-v1
Affected repos: cianfhoghlaim (single-repo change)
```

## Acceptance gates

- `openspec validate 2026-07-29-biep-v3-england-full-coverage-v1 --strict` passes
- `cd baml_src && uv run baml-cli generate` succeeds cleanly
- `python3 -c "from dlt.british_isles._cross.registry_loader import seed_registry; print(seed_registry())"`
  returns counts >= 276 for England
- The companion notebook Tab 2 (Nation comparison) shows
  `england >= 276`
- `dg list assets | grep england_` lists 4 assets (3 + 1 check)
- `dg list code-locations` shows 1 CocoIndex v1 app for England
  (the parameterised one from Phase 0, not 3 board-specific ones)
- `mise run lint:skills` still passes (53/53)
- Push target: `origin/main`

## Cross-references

- [`british-isles-education-pipeline`](../../specs/british-isles-education-pipeline/spec.md) —
  the BIEP v1/v2 LC spec; extended by Phase 2 (Ireland) + Phase 3 (England)
- `openspec/changes/2026-07-28-biep-v3-ireland-full-coverage-v1/` — Phase 2
- `openspec/changes/2026-07-30-biep-v3-sct-wls-ni-v1/` — Phase 4, the
  next consumer of the same generic pipeline pattern (SQA + WJEC + CCEA)
- `baml_src/british_isles/england/education/curriculum_syllabus.baml` —
  the canonical BAML function `ExtractUKQualSpec` lives here
- `dlt/british_isles/england/education/england_jurisdiction_pipeline.py` —
  the new generic pipeline
- `.agents/skills/dlt/SKILL.md` — the DLT conventions
- `.agents/skills/dagster/SKILL.md` — the 5-layer group_name convention