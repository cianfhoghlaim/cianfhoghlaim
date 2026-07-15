# 2026-07-21-biep-v2-england-aqa-ocr-baml-pipeline-v1

## Why

England is one of the 8 British Isles jurisdictions covered by the
`cross-region-pipeline` umbrella contract, but it has a thin scaffold today:

- `dlt/british_isles/england/education/national_curriculum.py` (38 lines)
- `dlt/british_isles/england/education/all_exam_boards.py` (56 lines)
- `dlt/british_isles/england/education/{aqa,ocr,edexcel}_qualifications.py` (53 lines each)
- `baml_src/british_isles/england/education.baml` (single `ExtractENEducationDocument` function)

That's it. There are no per-subject DLT sources for AQA/OCR/Edexcel, no per-board
BAML extraction functions, no CocoIndex v1 embedders, and no Dagster assets for
the England dimension. The earlier `2026-07-12-british-isles-parity-pipeline-v1`
proposed per-subject scaffolds but was deferred for the actual extraction
depth.

This change ships the **full BIEP-grade England pipeline** for all 3 main
awarding bodies (AQA, OCR, Edexcel Pearson) × 9 priority subjects (Mathematics,
English Language, English Literature, Chemistry, Biology, Physics, Computer
Science, History, Geography) × 2 qualification levels (GCSE, A-Level):

- **5 new BAML extraction functions** (`ExtractAQAQualSpec`, `ExtractOCRQualSpec`,
  `ExtractEdexcelQualSpec`, `ExtractAQAExamPaper` with multi-board dispatch,
  `ExtractAQAMarkingScheme` with UMS / 9-1 grading)
- **27 per-subject DLT sources** (9 subjects × 3 boards) following the
  `ncca_<subject>.py` pattern
- **3 CocoIndex v1 Apps** (one per awarding body) at
  `cocoindex/british_isles/england/{aqa,ocr,edexcel}_education_embedding.py`
- **81 Dagster L2 assets** at
  `orchestration/defs/2_materials/england_education/{aqa,ocr,edexcel}/`
  (27 × 3 layers: ingest → BAML extract → embed)
- **3 MotherDuck Dives** (`eng_aqa_curriculum_dive`, `eng_gcse_difficulty_dive`,
  `eng_a_level_complexity_dive`) + **1 daily Flight** `eng_daily_sync_flight`

The OCR/VLM convergence in the parallel Change 3 will reuse this pipeline to wire
in Docling-serve + Unstract + the 2-VLM ensemble (qwen3-vl-8b + gemma-4-26B-A4B)
+RAGAS voting. But this Change 2 stands alone — it ships a working BAML-only
extraction pipeline for England before the ensemble lands.

## What changes

### 1. New BAML extraction schemas

5 new BAML files at `baml_src/british_isles/england/education/`:

- `curriculum_syllabus.baml` — declares 3 board-specific functions:
  - `ExtractAQAQualSpec(text) -> AQAQualSpec { board, qualification_level,
    subject, specification_code, title, version, total_marks, assessment_objectives[] }`
  - `ExtractOCRQualSpec(text) -> OCRQualSpec` (same shape; separate class so
    future AQA-vs-OCR diffing is straightforward)
  - `ExtractEdexcelQualSpec(text) -> EdexcelQualSpec`
- `exam_paper_layout.baml` — `ExtractAQAExamPaper(text) -> AQAExamPaper
  { board, qualification_level, subject, paper_code, year, sections[],
  total_marks }` (multi-board: AQA primary, OCR + Edexcel aliases)
- `marking_scheme.baml` — `ExtractAQAMarkingScheme(text) -> AQAMarkingScheme
  { board, qualification_level, subject, grade_boundaries_9_to_1[],
  component_weights[] }` (UMS / 9-1 grading)
- `subject_taxonomy.baml` — declares 4 enums:
  `EXAM_BOARD ∈ {AQA, OCR, EDEXCEL, WJEC, CAIE}`,
  `QUALIFICATION_LEVEL ∈ {GCSE, A_LEVEL, AS_LEVEL, GCSE_SHORT, BTEC}`,
  `GCSE_AQA_SUBJECTS` (88+ entries — mathematics, english_language,
  english_literature, biology, chemistry, physics, computer_science,
  history, geography, religious_studies, etc.),
  `A_LEVEL_AQA_SUBJECTS` (45+ entries).
- `ensembled_extraction.baml` — `ExtractEnglandEnsembleConsensus(text, subject)
  -> EnsembleConsensus { baml_canonical, docling_text, unstract_json,
  qwen3_vl_response, gemma4_response, ragas_score, voted_output }` — this
  function is the **input contract** for Change 3's convergence change. It
  accepts the 4 path outputs (BAML, Docling, Unstract, 2 VLM) and returns
  the RAGAS-voted result.

Reuses the `clients.baml` `ExtractEnStrong` (Qwen3-VL 8B workhorse) for
extraction; the `ensembled_extraction` function uses the `Unstract` +
`Docling` clients that Change 3 introduces.

### 2. New per-subject DLT sources

27 per-subject DLT sources at
`dlt/british_isles/england/education/subjects/{aqa,ocr,edexcel}_{subject}.py`:
- 3 award bodies × 9 subjects = 27 sources
- Subjects: mathematics, english_language, english_literature, chemistry,
  biology, physics, computer_science, history, geography

Each source MUST:
- Use `from cianfhoghlaim.dlt.common.destinations_oideachais import with_namespace`
  and call `with_namespace("oideachais")` (per the v6 destination contract)
- Honour `USE_LOCAL_SCRAPES=true` (default) — the AQA/OCR/Edexcel PDFs are
  cached locally in `/stedding/ingest_queue/england/{aqa,ocr,edexcel}/<subject>/`
- Yield `dlt.resource` records keyed by `source_id` of the form
  `british_isles.england.education.{aqa,ocr,edexcel}_<subject>` (per
  `cross-region-pipeline/spec.md` Requirement "Canonical source_id shape")
- Tag every row with `country_code="england"`, `jurisdiction="england"`,
  `exam_board ∈ {aqa,ocr,edexcel}`, `qualification_level ∈ {gcse,a_level}`
- Write to `ducklake_oideachais.education.british_isles.england.<board>.<subject>.<qualification_level>`

### 3. New CocoIndex v1 Apps

3 CocoIndex v1 Apps at
`cocoindex/british_isles/england/{aqa,ocr,edexcel}_education_embedding.py`,
each conforming to R1–R4:

- **R1** — `from cocoindex._shared._lifespan import shared_lifespan`
- **R2** — Imports `LANCE_DB` + `EMBEDDER` from `_lifespan`
- **R3** — `app = coco.App(coco.AppConfig(name=...))` at module scope
- **R4** — `@coco.fn` decorator + `lancedb.mount_table_target(LANCE_DB, ...)`

LanceDB table names: `oideachais.england.<board>.<subject>.<level>` (27 tables per board — but a subject×level×board PK triple gives the same 27 unique tables).

### 4. New Dagster L2 assets

81 assets at `orchestration/defs/2_materials/england_education/{aqa,ocr,edexcel}/`:

- 27 × `eng_<board>_<subject>_ingested` (Layer 1)
- 27 × `eng_<board>_<subject>_qual_extracted` (Layer 2 — BAML `Extract<Board>QualSpec`)
- 27 × `eng_<board>_<subject>_embedding_flow` (Layer 3 — CocoIndex)

+ 1 cross-board `eng_aqa_vs_ocr_diff` asset (the comparator asset that
joins AQA + OCR + Edexcel for the same subject and surfaces spec differences
— invaluable for curriculum researchers comparing the 3 awarding bodies)

All asset `group_name`s MUST follow the 5-layer convention `<N>_<layer>/<domain>/<slug>`.

### 5. New MotherDuck Dives + daily Flight

- **3 MotherDuck Dives**:
  - `eng_aqa_curriculum_dive` — topic coverage per AQA subject × level
  - `eng_gcse_difficulty_dive` — Bloom's taxonomy distribution per GCSE subject × year
  - `eng_a_level_complexity_dive` — mark-allocation patterns per A-Level question
- **1 daily MotherDuck Flight** `eng_daily_sync_flight` — re-runs BAML extraction on
  any new PDFs landed in
  `s3://garage/oideachais/england/<board>/<subject>/<level>/<year>/<file>.pdf`

### 6. Spec deltas

1 spec delta:

- `openspec/specs/british-isles-education-pipeline/spec.md` — add 1 new sibling
  requirement: "Requirement: England (AQA + OCR + Edexcel) A-Level + GCSE"
  mirroring the existing "Requirement: 6 Irish LC subjects end-to-end" +
  "Requirement: Junior Cycle end-to-end" but for England.

## Dependencies

```yaml
Blocked by: 2026-07-20-biep-v2-junior-cycle-extraction-v1
            (junior cycle goes first because it's Ireland-only and
             zero cross-jurisdiction risk)
Blocked by (soft): 2026-07-22-biep-v2-ocr-vlm-pipeline-convergence-v1
                   (Change 3 wires Docling/Unstract/VLM ensemble in;
                    this Change 2 ships BAML-only first and Change 3
                    adds the ensemble layer on top)
Affected repos: cianfhoghlaim (single-repo change)
```

## Acceptance gates

- `openspec validate 2026-07-21-biep-v2-england-aqa-ocr-baml-pipeline-v1 --strict` passes
- `dg check yaml` passes on all new defs
- `baml-cli generate` succeeds on the 5 new BAML files
- 5 new BAML files exist + AST-parse
- 27 new DLT sources exist + AST-parse
- 3 CocoIndex v1 Apps exist + conform to R1–R4 (verified by `mise run cocoindex:v1-conformance`)
- 81+ new Dagster L2 defs.yaml files YAML-parse
- 3 new MotherDuck Dive YAMLs + 1 Flight YAML exist
- The 6-subject BIEP v1 test + the JC pipeline (from Change 1) both still pass
- `mise run lint:skills` still passes (53/53)
- Push target: `origin/main`

## Cross-references

- [`british-isles-education-pipeline`](../../specs/british-isles-education-pipeline/spec.md) —
  the BIEP v1 flagship that this change extends with England parity
- [`british-isles-parity-pipeline`](../../specs/british-isles-parity-pipeline/spec.md) —
  the earlier parity-v1 scaffold this change completes
- [`cross-region-pipeline`](../../specs/cross-region-pipeline/spec.md) —
  the umbrella contract (DuckLake namespace, DLT path contract, partition contract)
- [`oideachais-baml-schemas`](../../specs/oideachais-baml-schemas/spec.md) —
  the BAML extraction library this change writes 5 new files into
- [`oideachais-cocoindex-v1-migration`](../../specs/oideachais-cocoindex-v1-migration/spec.md) —
  the R1–R4 v1 conformance contract the 3 new CocoIndex Apps must obey
- `docs/research/aqa_ocr_edexcel_endpoints.md` *(authoritative endpoint inventory)*
- `.agents/skills/dlt/SKILL.md` — DLT conventions
- `.agents/skills/baml/SKILL.md` — BAML schema patterns
- `.agents/skills/cocoindex/SKILL.md` — the R1–R4 conformance contract
- `.agents/skills/dagster/SKILL.md` — the 5-layer component architecture
- `.agents/skills/change-detection/SKILL.md` — ChangeDetection.io patterns (for the sibling sensor change)
