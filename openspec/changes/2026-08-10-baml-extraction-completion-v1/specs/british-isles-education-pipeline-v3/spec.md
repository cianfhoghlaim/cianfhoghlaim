# Spec Delta: british-isles-education-pipeline-v3

## ADDED Requirements

### Requirement: All 6 LC subjects SHALL have real BAML extraction prompts

`baml_src/british_isles/ireland/education/lc_extraction/{syllabus,exam_paper,marking_scheme,diagram,cross_linguistic}.baml` SHALL have real extraction prompts for all 6 priority subjects: mathematics, applied_mathematics, chemistry, geography, english, gaeilge, computer_science. Each prompt SHALL follow the `{{ _.role("user") }}` + `{{ ctx.output_format }}` marker pattern established in `aistear.baml`.

**WHEN** `b.ExtractCurriculumSyllabus(text=<pdf>, subject="chemistry")` is called
**THEN** the prompt SHALL extract: `{topics: [{code, title, learning_outcomes: [{code, text, blooms_level}]}], strands: [{name, topics}], assessment_objectives: [...], key_competencies: [...]}`

#### Scenario: Chemistry syllabus extraction returns structured topics + LOs

- **WHEN** `b.ExtractCurriculumSyllabus(text=<chemistry_specification_pdf>, subject="chemistry")` is called
- **THEN** the result has at least 5 topics with NCCA LO codes (e.g. `LC-CHEM-LO-001`)
- **AND** each topic has at least 3 learning_outcomes
- **AND** the JSON is serialisable via `.model_dump_json()`

### Requirement: LC subject pilot factory SHALL scale to all 6 subjects

The `lc_chemistry_pilot_assets.py` template SHALL be refactored into a factory `lc_subject_pilot_factory(subject)` that returns 3 assets + 3 checks per subject. Wire the factory in `orchestration/defs/2_materials/lc_extraction/lc_subjects.py`.

**WHEN** `dagster asset materialize --select lc_*_pilot_loaded` runs
**THEN** all 6 LC subjects SHALL materialize end-to-end (ingestion → BAML extraction → cross-check → MotherDuck load)

#### Scenario: All 6 LC subjects materialize end-to-end

- **WHEN** the operator runs `dagster asset materialize --select '*_pilot_loaded'`
- **THEN** 6 subjects × 3 assets = 18 assets complete
- **AND** each subject's `lc_<subject>_pilot_loaded` writes rows to `md:cianfhoghlaim.cianfhoghlaim.lc_<subject>_<level>_<language>`

### Requirement: Irish-language BAML path SHALL use `uccix-mistral-24b`

For the gaeilge LC subject pilot, the BAML client SHALL switch from `minimax-direct/MiniMax-M3` to `uccix-mistral-24b` (via LiteLLM `irish` alias).

**WHEN** `b.ExtractCurriculumSyllabus(text=<gaeilge_pdf>, subject="gaeilge")` is called
**THEN** the BAML client SHALL be `baml_src/clients.baml:gaeilge_lc_client` with `provider: litellm`, `model: uccix-mistral-24b`

#### Scenario: Gaeilge LC pilot uses Irish-language model

- **WHEN** the operator runs `dagster asset materialize --select lc_gaeilge_pilot_loaded`
- **THEN** the BAML calls route through `uccix-mistral-24b` via LiteLLM
- **AND** the extracted LOs have Irish-language text (not English)
