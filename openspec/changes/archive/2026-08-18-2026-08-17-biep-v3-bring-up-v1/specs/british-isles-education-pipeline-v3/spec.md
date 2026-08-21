# british-isles-education-pipeline-v3

## ADDED Requirements

### Requirement: 6 LC subjects × real BAML extraction prompts

The system SHALL replace the stub `"Auto-generated extraction prompt."`
strings with real subject-specific extraction prompts for all 6 LC
subjects × 4 extraction kinds (chemistry, mathematics, geography,
gaeilge, english, computer_science × curriculum_syllabus,
exam_paper_layout, marking_scheme_guideline, syllabus_diagram) =
24 real prompts (per the `2026-08-10-baml-extraction-completion-v1`
change proposal).

Each prompt SHALL follow the canonical `{{ _.role("user") }}` +
`{{ ctx.output_format }}` marker pattern and SHALL pass the
`mise run lint:baml-stub-prompts` lint gate.

#### Scenario: Chemistry syllabus extraction

- **GIVEN** `baml_src/british_isles/ireland/education/lc_extraction/curriculum_syllabus.baml`
  declares `@function ExtractChemSyllabus(text, source_pdf) -> ChemSyllabus`
- **WHEN** the function is invoked against an Ireland LC Chemistry
  syllabus PDF (e.g. `LC022ACS000EV.pdf` or equivalent)
- **THEN** the prompt MUST request chemistry-specific extraction
  (learning outcomes, syllabus topics, experiment descriptions,
  atomic symbols, equation references) — not a generic stub
- **AND** the parsed `ChemSyllabus` Pydantic model MUST have
  non-empty `topics` and `learning_outcomes` arrays

#### Scenario: All 24 prompts are real (no stubs)

- **WHEN** `mise run lint:baml-stub-prompts` runs
- **THEN** all 24 LC subject × extraction kind prompts pass the lint
- **AND** `baml-cli generate --from baml_src` regenerates the 14
  BAML client files successfully

### Requirement: BAML ClientRegistry for OCR ensemble

The OCR ensemble Path 1 (BAML) SHALL use the BAML `ClientRegistry`
pattern (declared in `baml_src/clients.baml`) for primary + fallback
chains per the `baml-schemas` spec added by Mega-6.

#### Scenario: Path 1 primary client fails

- **GIVEN** the OCR ensemble runs Path 1 against an Ireland LC PDF
- **WHEN** the primary client `ExtractorPrimary` (minimax-m3) returns
  a 429 rate-limit error
- **THEN** the BAML runtime MUST automatically retry with
  `ExtractorFallback` (qwen3.7-plus via DashScope token plan)
- **AND** the BAML Collector MUST record both attempts in
  `collector.last.calls` (2 entries)
- **AND** the MLflow experiment `biiep_v3` MUST record both runs
  with token usage metrics

### Requirement: Irish-language BAML client path

The system SHALL use the `gaeilge_lc_client` (routed through
`uccix-mistral-24b` per the `centralized-model-registry` spec) for
the 2 Gaeilge-specific BAML functions:
`ExtractBilingualLearningOutcome` and `ExtractCrossLinguisticGA`.

Per the `meaisinfhoghlaim-ocr-htr` spec, this client is the canonical
Irish-language path; the platform has only `uccix-mistral-24b` as a
dedicated Irish-language model.

#### Scenario: ExtractBilingualLearningOutcome invoked

- **GIVEN** the function is called with an Irish-English bilingual
  curriculum extract
- **WHEN** the function executes
- **THEN** the `gaeilge_lc_client` MUST route to
  `model_for("text_llm", "irish", language="ga")` which resolves to
  `uccix-mistral-24b` per the `meaisinfhoghlaim/models/routing.py`
  IRISH_TEXT_MODEL constant (added by Mega-6 P3.1)
- **AND** the parsed Pydantic model MUST have populated `gaeilge` and
  `english` parallel columns

### Requirement: 7 v1 CocoIndex flows + England priority

The BIEP v3 lakehouse SHALL host 7 v1 CocoIndex flows (6 LC subjects +
`government_circulars`) per the `british-isles-education-pipeline-v3`
spec, plus the England priority factory (added by the
`2026-08-10-england-biiep-pipeline-v1` change).

The England priority factory covers 3 GCSE boards (AQA / OCR / Edexcel)
× ~43 subjects + 3 A-Level boards × ~49 subjects = 276 unwired
CocoIndex Apps, wired via 6 DLT sources + 6 Dagster asset groups.

#### Scenario: 7 v1 CocoIndex flows emit to MotherDuck

- **WHEN** `dagster asset materialize --select ireland_lc_factory --select england_priority_factory` runs
- **THEN** the 6 Ireland LC flows emit rows to
  `md:cianfhoghlaim.education.british_isles.ireland.lc.{subject}.{lang}`
- **AND** the England priority flow emits rows to
  `md:cianfhoghlaim.education.british_isles.england.{stage}.{board}.{subject}`
- **AND** the `government_circulars` flow emits rows to
  `md:cianfhoghlaim.education.ie.gov_circulars_archive`

### Requirement: 4 MotherDuck Dives + daily Flight

The BIEP v3 lakehouse SHALL host the 4 canonical MotherDuck Dives
(`lc_syllabus_topics`, `lc_exam_difficulty`, `lc_marking_complexity`,
`gov_circulars_archive`) + the daily `lc_pdf_sync_flight` per the
`british-isles-education-pipeline-v3` spec.

#### Scenario: 4 Dives are live

- **WHEN** MotherDuck `md:cianfhoghlaim` is opened in the BIEP portal
- **THEN** the 4 Dives return live query results (not stale cache)
- **AND** the daily `lc_pdf_sync_flight` ran within the last 24 hours