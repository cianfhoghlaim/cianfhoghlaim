# Oideachais BAML Schemas Capability

## Purpose

`oideachais-baml-schemas` is a capability of the Cianfhoghlaim platform.
The corresponding source code lives at `baml_src/` (8 BAML files) and
`baml_client/` (the auto-generated Python client). See `docs/00_index.md`
for the quadrant map and `docs/00-core/CLAUDE.md` for the project
identity.

This spec was consolidated from the 3 separate `assessment-extraction`,
`bilingual-content`, and `author-archive-baml-extraction` specs. Each
former spec is now a section (Requirement) of this one spec.

## Background

BAML (Basically a Made-up Language) is the schema-validation LLM
extraction framework used across the oideachais lakehouse. The 8 BAML
files declare the typed extraction functions:

- `aistear.baml` — Aistear (early childhood) framework + themes
- `primary.baml` — Primary stage learning outcomes
- `junior_cycle.baml` — Junior Cycle subject spec + CBA tasks
- `senior_cycle.baml` — Senior Cycle subjects (covered by `oideachais-pipeline` spec)
- `tertiary.baml` — CAO / QQI-FET / Apprenticeship programmes
- `curriculum_extraction.baml` — Cross-stage curriculum area / learning outcome / cross-curricular theme
- `author_archive.baml` — UoG artefact / Gemini report / Zotero paper / handwritten equation
- `ui_components.baml` — UI component extraction
- `image_generation.baml` — Image generation prompts

The BAML client `ExtractEn` (English-only, BAAI/bge-large-en-v1.5
backbone) is the production extraction client; `ExtractEnStrong` is the
higher-accuracy variant.
## Requirements
### Requirement: Aistear (early childhood) extraction

The system SHALL extract Aistear themes and learning experiences from
NCCA Aistear documents.

#### Scenario: Aistear theme extracted

- **GIVEN** an NCCA Aistear PDF at `stedding/ingest_queue/aistear/`
- **WHEN** the `ExtractAistearFramework` BAML function is called
- **THEN** the function returns a `PrimaryCurriculumArea[]` with the
  4 Aistear themes (Well-being, Identity & Belonging, Communicating,
  Exploring & Thinking)

### Requirement: Primary + Junior Cycle extraction

The system SHALL extract Primary learning outcomes and Junior Cycle
subject specs from NCCA + SEC PDFs.

#### Scenario: Primary learning outcome extracted

- **GIVEN** an NCCA Primary curriculum spec PDF
- **WHEN** the `ExtractPrimaryLearningOutcomes` BAML function is called
- **THEN** the function returns a `PrimaryLearningOutcome[]` with the
  stage + curriculum area + learning outcome text

#### Scenario: Junior Cycle subject spec extracted

- **GIVEN** an NCCA Junior Cycle subject spec PDF
- **WHEN** the `ExtractJCSpec` BAML function is called
- **THEN** the function returns a `JCSubjectSpec` with the subject code
  + short course + assessment components

### Requirement: Senior Cycle + Tertiary extraction

The system SHALL extract Senior Cycle subjects and Tertiary programmes
(CAO, QQI-FET, Apprenticeship) from PDFs.

#### Scenario: Senior Cycle subject extracted

- **GIVEN** a Leaving Cert subject spec PDF
- **WHEN** the `ExtractSeniorCycleSubject` BAML function is called
- **THEN** the function returns a `SeniorCycleSubject` with the subject
  code + syllabus + assessment structure

#### Scenario: Tertiary programme extracted

- **GIVEN** a CAO / QQI-FET / Apprenticeship PDF
- **WHEN** the `ExtractTertiaryProgramme` BAML function is called
- **THEN** the function returns a `Programme` with the institution,
  award, and entry requirements

### Requirement: Assessment extraction

The system SHALL extract exam papers, marking schemes, and subject
rubrics from SEC examination PDFs.

#### Scenario: Exam paper structure extracted

- **GIVEN** an SEC exam paper PDF
- **WHEN** the `ExtractExamPaperStructure` BAML function is called
- **THEN** the function returns an `ExamPaper` with the question count,
  structure, and time allocation

#### Scenario: Marking scheme extracted

- **GIVEN** an SEC marking scheme PDF
- **WHEN** the `ExtractMarkingScheme` BAML function is called
- **THEN** the function returns a `MarkingScheme` with the marks per
  question and the expected answer template

### Requirement: Bilingual (English + Irish) content

The system SHALL support bilingual content extraction and parallel
corpus generation.

#### Scenario: English-Irish parallel corpus

- **GIVEN** a bilingual English-Irish document (e.g. NCCA primary spec)
- **WHEN** the parallel corpus extraction is run
- **THEN** the system produces an English-Irish parallel corpus for
  downstream Celtic-language model training

### Requirement: Author-archive extraction (UoG + Gemini + Zotero)

The system SHALL extract structured records from the 3 author-archive
corpora: UoG artefacts, Gemini deep research reports, and Zotero papers.

#### Scenario: UoG artefact extracted

- **GIVEN** a UoG PDF in `leabharlann/ollscoil_na_gaillimhe/`
- **WHEN** the `ExtractUoGArtifact` BAML function is called
- **THEN** the function returns a `UniversityOfGalwayArtifact` with
  the artifact kind, course code, module title, stage, and key topics

#### Scenario: Gemini deep research report extracted

- **GIVEN** a Gemini deep research PDF in `leabharlann/gemini_deep_research/`
- **WHEN** the `ExtractGeminiReport` BAML function is called
- **THEN** the function returns a `GeminiDeepResearchReport` with the
  topic, domain, summary, key findings, and cited URLs

#### Scenario: Zotero paper extracted

- **GIVEN** a Zotero PDF in `leabharlann/zotero/` with an arxiv_id
- **WHEN** the `ExtractZoteroMetadata` BAML function is called
- **THEN** the function returns a `ZoteroPaper` with the paper kind,
  arxiv_id, DOI, title, authors, year, abstract, venue, and the
  `irish_relevant` / `htr_relevant` flags

### Requirement: UI component + image generation

The system SHALL support UI component extraction and image generation
prompts (for the oideachais web app and the croilar public site).

#### Scenario: UI component extracted

- **GIVEN** a UI mockup screenshot
- **WHEN** the `ExtractUIComponent` BAML function is called
- **THEN** the function returns a `UIComponent` with the component
  kind, props, and layout

#### Scenario: Image generated

- **GIVEN** an image prompt
- **WHEN** the `GenerateImage` BAML function is called
- **THEN** the function returns a `GeneratedImage` with the prompt,
  model, and the image URL (stored in Cloudflare R2)

### Requirement: Dynamic schema extraction via TypeBuilder

The system SHALL support runtime-generated BAML extraction classes via
`@@dynamic` and `baml_client.type_builder.TypeBuilder.add_baml(...)`,
enabling extraction of records whose schema is not known at `.baml`
authoring time.

#### Scenario: Two-step dynamic schema

- **GIVEN** a `GenerateBAML(content) -> Schema` function (step 1) that
  asks an LLM to describe the schema in BAML source, plus an
  `ExecuteBAML(content, { tb: TypeBuilder }) -> Response` function
  (step 2) with a `@@dynamic` class
- **WHEN** the user calls `b.ExecuteBAML(content, { "tb": tb })` where
  `tb` was populated by step 1
- **THEN** the function returns a `Response` with the runtime-injected
  fields populated from the LLM extraction
- **AND** the schema is captured for downstream DuckLake mapping

#### Scenario: Multimodal content input

- **GIVEN** a `GenerateBAML(content: string | image | audio | image[]) -> Schema`
  function with a union-typed parameter
- **WHEN** the user passes a `baml_py.Pdf.from_base64(pdf_bytes)` to step 2
- **THEN** the dynamic extraction completes against the multimodal content
- **AND** the in-repo reference is `oideachais/baml_src/ocr_extraction.baml`
  (9,368 bytes) for the OCR multimodal pattern

### Requirement: Runtime deterministic evals

The system SHALL provide 6 deterministic Python evals that validate
extraction outputs using pure math/logic, NOT an LLM-as-judge:

1. **Sum validation** — `sum(transactions) + charges + tax + rounding - |discount| ≈ grand_total`
2. **Positive values** — monetary fields ≥ 0 (except `rounding`/`discount`)
3. **Subtotal consistency** — when `subtotal` present, `sum(transaction totals) ≈ subtotal`
4. **Unit price accuracy** — `(unit_price - |unit_discount|) × quantity ≈ total_price`
5. **Grand total calculation** — `subtotal + service + tax + rounding - |discount| ≈ grand_total`
6. **Data completeness** — `transactions` non-empty, `grand_total` present,
   every transaction has `item_name`/`quantity`/`unit_price`/`total_price`

#### Scenario: Receipt extraction passes all 6 evals

- **GIVEN** a BAML extraction of a CORD-v2 receipt into a `ReceiptData`
  object with `transactions: Transaction[]` + `subtotal` + `tax` + `grand_total`
- **WHEN** the 6 evals are run sequentially
- **THEN** each eval returns an `EvaluationResult { passed, message, expected_value, actual_value }`
- **AND** the overall pass rate is computed as
  `passed_count / 6`

#### Scenario: Single failing eval triggers re-extraction

- **GIVEN** a first-pass extraction where eval #5 (grand total) fails
- **WHEN** the auto-retry loop runs
- **THEN** the BAML function is re-called with the same input
- **AND** the retry attempt is recorded alongside the first attempt for
  downstream comparison
- **AND** `max_retries` (default 1) caps the loop to prevent runaway cost

### Requirement: Multimodal (vision) extraction

The system SHALL support BAML function parameters of type
`image` | `pdf` | `audio`, with the `baml_py` runtime helpers
`Image.from_base64("image/png", base64)` and `Pdf.from_base64(pdf_bytes)`.

#### Scenario: Vision extraction of a receipt

- **GIVEN** a receipt image at `image/png` base64
- **WHEN** `b.ExtractReceiptTransactions(receipt_image)` is called
  with the `image` parameter
- **THEN** the function returns a typed `ReceiptData` object
- **AND** the BAML client is `provider google-ai` with the `Gemini25Flash`
  or `Gemini3Pro` model

### Requirement: Streaming extraction

The system SHALL support `b.stream.<Function>(...)` for partial
streaming + `stream.get_final_response()` for the typed final result.

#### Scenario: Streamed function call

- **GIVEN** a BAML function with `@stream.not_null` (or `@stream.done`
  / `@stream.with_state`)
- **WHEN** the user iterates over the `BamlStream` returned by
  `b.stream.<Function>(...)`
- **THEN** partial chunks are yielded in real time
- **AND** `stream.get_final_response()` returns the typed final object
  once the LLM finishes

### Requirement: `@@dynamic` classes and enums

The system SHALL support the `@@dynamic` attribute on BAML classes
and enums, allowing runtime field injection via `TypeBuilder`.

#### Scenario: Dynamic class accepts runtime fields

- **GIVEN** `class Response { @@dynamic }` in `execute_baml.baml`
- **WHEN** the `TypeBuilder` adds fields via
  `tb.add_baml('class Response { data { name string age int } }')`
- **THEN** the `b.ExecuteBAML(content, { tb: tb })` call returns
  a `Response` with the `data.name` and `data.age` fields populated

### Requirement: `template_string` reusable prompt blocks

The system SHALL support `template_string` blocks for reusable
Jinja-prompt fragments that teach the LLM a DSL in-prompt (e.g.
BAML syntax for the dynamic-schema generator).

#### Scenario: template_string teaching BAML syntax

- **GIVEN** `template_string BAMLBackground() { ... }` defines a
  BAML-syntax primer
- **WHEN** the `GenerateBAML` function inlines it via
  `{{ BAMLBackground() }}`
- **THEN** the LLM sees the BAML syntax primer + the content to
  summarise in a single prompt
- **AND** the emitted `Schema` has the correct `interface_code`,
  `return_type`, and `other_code` fields

### Requirement: Multi-generator setup

The system SHALL support multiple BAML `generator` blocks in
`generators.baml` with separate `output_dir` per language target
(e.g. `output_type "python/pydantic"` → `output_dir "../backend"`,
`output_type "typescript/react"` → `output_dir "../frontend"`).

#### Scenario: Two-language code generation

- **GIVEN** `generators.baml` declares 2 generators: `python` →
  `output_dir "../backend"` and `typescript` → `output_dir "../frontend"`
- **WHEN** `baml generate` is run
- **THEN** the Python client is regenerated at
  `backend/baml_client/` AND the TypeScript client is regenerated
  at `frontend/baml_client/`

### Requirement: Named clients + retry policies

The system SHALL support named BAML clients (e.g. `ExtractEn`,
`ExtractEnStrong`, `LocalVision`) with `fallback` / `round-robin`
strategies and `Constant` / `Exponential` retry policies
(`max_retries`, `strategy { type constant_delay, delay_ms }` /
`exponential_backoff`).

#### Scenario: Fallback client chain

- **GIVEN** client `ExtractPrimary` with
  `fallback [openai/gpt-4o, anthropic/claude-sonnet-4, google-ai/gemini-2.5-flash]`
- **WHEN** the primary client fails
- **THEN** BAML falls through to the next client in order
- **AND** the retry policy is applied per client before falling through

## Cross-references

- [`baml_src/`](../../baml_src/) (the 8 BAML files)
- [`baml_client/`](../../baml_client/) (the auto-generated client)
- [`.agents/skills/baml/SKILL.md`](../../.agents/skills/baml/SKILL.md)
- [`baml_src/README.md`](../../baml_src/README.md) (the BAML file map)
