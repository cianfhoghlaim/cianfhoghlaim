# Spec Delta: bie-8-jurisdictions

## ADDED Requirements

### Requirement: England BIEP SHALL have DLT sources for 3 boards × 2 qualification types

Six DLT source files SHALL exist at `dlt_sources/british_isles/england/education/{gcse,a_level}/{aqa,ocr,edexcel}_*.py` consuming PDFs from `stedding/site_scrape_samples/england/{gcse,a_level}/<board>/`.

**WHEN** `dlt pipeline run england_aqa_gcse` executes
**THEN** the source SHALL return rows for all 43 GCSE subjects for AQA board with `{pdf_path, subject, board, qualification, level, language}`

#### Scenario: AQA GCSE pipeline ingests 43 subjects

- **WHEN** the operator runs `USE_LOCAL_SCRAPES=true .venv/bin/dagster asset materialize --select england_aqa_gcse_loaded`
- **THEN** the source scans `stedding/site_scrape_samples/england/gcse/aqa/`
- **AND** yields 43 rows, one per GCSE subject (Mathematics, English Language, English Literature, Biology, Chemistry, Physics, etc.)
- **AND** each row has `pdf_path, subject, board="aqa", qualification="gcse", level="gcse", language="en"`

### Requirement: England BIEP SHALL have Dagster asset groups for all 6 board × qualification combinations

Six asset groups SHALL exist at `orchestration/defs/2_materials/england_education/{gcse,a_level}_assets.py` each wrapping the DLT source + BAML extraction + CocoIndex embedding + MotherDuck load.

**WHEN** `dagster asset materialize --select england_*_loaded` runs
**THEN** all 6 asset groups SHALL materialize (AQA GCSE + OCR GCSE + Edexcel GCSE + AQA A-Level + OCR A-Level + Edexcel A-Level)
**AND** 3 × 43 + 3 × 49 = 276 CocoIndex Apps SHALL be activated

#### Scenario: All 6 England asset groups materialize

- **WHEN** the operator runs `dagster asset materialize --select '*_gcse_loaded,aqa_a_level_loaded,ocr_a_level_loaded,edexcel_a_level_loaded'`
- **THEN** 6 asset groups complete
- **AND** 276 CocoIndex Apps write to `cianfhoghlaim.england.{gcse,a_level}.<board>.<subject>` tables in MotherDuck

### Requirement: England BIEP SHALL have BAML extraction for all 4 existing functions

`baml_src/british_isles/england/education/curriculum_syllabus.baml` SHALL add a real prompt for `ExtractAQAQualSpec` (the remaining stub — 3 of 4 already have real prompts: ExtractOCRQualSpec, ExtractEdexcelQualSpec, ExtractUKQualSpec).

**WHEN** `b.ExtractAQAQualSpec(text=<aqa_spec_pdf>)` is called
**THEN** the prompt extracts: `{spec_id, qualification_level, subject, units: [{code, title, learning_objectives}], assessment_objectives: [...]}`

#### Scenario: AQA qualification spec extraction

- **WHEN** the operator runs `b.ExtractAQAQualSpec(text=<aqa_a_level_chemistry_spec_pdf>)`
- **THEN** the result has at least 3 units with AQA UMS codes
- **AND** each unit has at least 5 learning_objectives
