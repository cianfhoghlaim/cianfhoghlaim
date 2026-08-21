## ADDED Requirements

### Requirement: England (AQA + OCR + Edexcel) A-Level + GCSE

The system SHALL provide a full BIEP-grade England pipeline for the
3 main awarding bodies (AQA, OCR, Edexcel Pearson) × 9 priority subjects
(Mathematics, English Language, English Literature, Chemistry, Biology,
Physics, Computer Science, History, Geography) × 2 qualification levels
(GCSE, A-Level):

- **5 new BAML extraction functions** at `baml_src/british_isles/england/education/`:
  `ExtractAQAQualSpec`, `ExtractOCRQualSpec`, `ExtractEdexcelQualSpec`,
  `ExtractAQAExamPaper` (multi-board dispatch), `ExtractAQAMarkingScheme`
  (UMS / 9-1 grading) — plus `ExtractEnglandEnsembleConsensus` for Change 3's
  ensemble pipeline
- **27 per-subject DLT sources** at `dlt/british_isles/england/education/subjects/`
  (3 boards × 9 subjects), tagged with `country_code="england"`,
  `jurisdiction="england"`, `exam_board ∈ {aqa,ocr,edexcel}`,
  `qualification_level ∈ {gcse,a_level}`
- **3 CocoIndex v1 Apps** at `cocoindex_flows/british_isles/england/{aqa,ocr,edexcel}_education_embedding.py`,
  producing 27 LanceDB tables `cianfhoghlaim.england.<board>.<subject>.<level>`
- **81+ Dagster assets** at
  `orchestration/defs/2_materials/england_education/{aqa,ocr,edexcel}/`
  (27 × 3 layers: ingest → BAML extract → embed + 3 cross-board comparator assets)
- **3 MotherDuck Dives** (`eng_aqa_curriculum_dive`, `eng_gcse_difficulty_dive`,
  `eng_a_level_complexity_dive`) + **1 daily Flight** `eng_daily_sync_flight`

#### Scenario: mise run dagster:oideachais → materialize all 3 England boards

- **WHEN** a researcher clicks "Materialize all" in the Dagster UI for the England pipeline
- **THEN** the 81 England assets materialise within minutes
- **AND** the 27 LanceDB tables `cianfhoghlaim.england.<board>.<subject>.<level>` are populated
- **AND** the `eng_aqa_curriculum_dive` MotherDuck Dive shows topic coverage per AQA subject
- **AND** the daily `eng_daily_sync_flight` re-runs BAML extraction on any new PDFs
  landed in `s3://garage/cianfhoghlaim/england/<board>/<subject>/<level>/`

#### Scenario: AQA vs OCR vs Edexcel spec diff

- **WHEN** a researcher opens the `eng_aqa_vs_ocr_diff` Dagster asset
- **AND** selects subject="mathematics", qualification_level="gcse"
- **THEN** the diff asset returns the side-by-side topic + assessment objective comparison
- **AND** it surfaces any spec changes between the 3 awarding bodies since the last sync

#### Scenario: Gaeilge/specialised subjects are deferred

- **GIVEN** the Ireland-only BAML `ExtractGaeilgeCurriculum` exists in the BIEP v1 LC pipeline
- **WHEN** a developer queries the England pipeline for `subject="gaeilge"`
- **THEN** the system returns an empty result with the message
  "Gaeilge not offered by AQA / OCR / Edexcel — see Ireland pipeline"
