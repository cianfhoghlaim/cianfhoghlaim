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
corpora (UoG artefacts, Gemini deep research reports, Zotero papers)
PLUS the new `university_extraction.baml` file (5 classes + 4
functions for course / module / programme / reading-list descriptors)
on the *website* side (per the `oideachais-university-deep-extraction`
spec).

#### Scenario: Module descriptor extracted from UoG module page

- **GIVEN** a module page markdown blob (e.g. `https://www.universityofgalway.ie/.../ct516-deep-learning/`)
- **WHEN** the `ExtractModuleDescriptor` BAML function is called
- **THEN** the function returns a `ModuleDescriptor` with the module code, title, ECTS, semester, programme codes, learning outcomes, assessment breakdown, prerequisite modules, lecturers, and recommended reading
- **AND** the function routes through the canonical `ExtractEn` LiteLLM client (no direct Firecrawl call)

#### Scenario: Reading list extracted with ISBN-13 validation

- **GIVEN** a module page markdown blob with a "Recommended reading" section
- **WHEN** the `ExtractReadingList` BAML function is called
- **THEN** the function returns a `ReadingListItem[]` with format (`ISBN_13 | DOI | URL`), title, authors, year
- **AND** the deterministic eval `reading_list_isbn13_format` rejects any record where `format = "ISBN_13"` and the `isbn_13` field doesn't match `^\d{13}$`

#### Scenario: BAML client is missing

- **GIVEN** the BAML client is not yet generated (the `baml_client/` directory is empty)
- **WHEN** the `uog_extract_modules` Dagster asset runs
- **THEN** the asset SHALL log a warning and return 0 rows (graceful degradation, per the `university_of_galway_source` pattern in `leabharlann/`)
- **AND** the asset run SHALL NOT fail

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
- **AND** the in-repo reference is `cianfhoghlaim/baml_src/ocr_extraction.baml`
  (9,368 bytes) for the OCR multimodal pattern

### Requirement: Runtime deterministic evals

The system SHALL provide 6 deterministic Python evals (the existing set)
PLUS 3 new evals for the university extraction path:

7. **`course_code_format_regex_match`** — every `CourseDescriptor.course_code` SHALL match `^[A-Z]{2,4}\d{3,4}$` (e.g. `MA335`, `CT511`, `HDSD`)
8. **`programme_ects_sum`** — `sum(ProgrammeDescriptor.modules[*].ects)` SHALL equal `ProgrammeDescriptor.total_ects` within ±1
9. **`module_count_within_programme`** — `ProgrammeDescriptor.modules` SHALL contain 6-20 modules for a full undergraduate or master's programme (a 1-module or 100-module programme is flagged as suspect)

#### Scenario: Course code format validation

- **GIVEN** a `CourseDescriptor` with `course_code = "MA335"`
- **WHEN** the `course_code_format_regex_match` eval runs
- **THEN** the eval returns `passed = true`

#### Scenario: Course code format rejection

- **GIVEN** a `CourseDescriptor` with `course_code = "math-335"` (lowercase + dash)
- **WHEN** the `course_code_format_regex_match` eval runs
- **THEN** the eval returns `passed = false`
- **AND** the eval's `message` field SHALL be `"course_code 'math-335' does not match ^[A-Z]{2,4}\\d{3,4}$"`
- **AND** the auto-retry loop SHALL re-invoke `ExtractCourseDescriptor` with a stronger prompt

#### Scenario: Programme ECTS sum fails — auto-retry triggers

- **GIVEN** a `ProgrammeDescriptor` with `total_ects = 90` but 8 modules whose `ects` sum to `120`
- **WHEN** the `programme_ects_sum` eval runs
- **THEN** the eval returns `passed = false`
- **AND** the asset_check fires
- **AND** the auto-retry loop re-invokes `ExtractProgrammeDescriptor` with a stronger prompt that emphasises the ECTS sum

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

### Requirement: Circular extraction BAML

The oideachais quadrant MUST provide an `ExtractCircularMeta` BAML function at `cianfhoghlaim/baml_src/circular_extraction.baml`. The function MUST extract a `CircularExtraction` (composed of `CircularReference`, `MarkingSchemeSummary`, and `TopicDistribution` classes) from a Department of Education circular PDF. The function MUST use the canonical `LitellmClient` (routes through the LiteLLM gateway).

#### Scenario: Agent extracts circular metadata

- **WHEN** an agent has a DoE circular PDF and calls `ExtractCircularMeta(pdf_text=..., filename=...)`
- **THEN** the function returns a `CircularExtraction` with `circular` (CircularReference), `scheme` (MarkingSchemeSummary with topics), `raw_text_excerpt`, and `extraction_confidence`
- **AND** the call goes through the canonical `LitellmClient` (LiteLLM gateway), not the hand-rolled HF Inference wrapper

### Requirement: BAML class / function / enum duplicate names

The system SHALL have at most 1 occurrence per name across the BAML `class`,
`function`, and `enum` declarations in `cianfhoghlaim/baml/**` (the 28 BAML
files + 3 new hoisted canonicals under `processing/_shared/`), per the
audit at the `2026-07-11-baml-cocoindex-modernization-v1` mega-change
(`tasks.md` Step 4).

The audit identified 22 class duplicates + 9 function duplicates + 11 enum
duplicates (42 total collisions, plus 7 `qpack_mathematics.baml` bare-name
classes that lack the `Math*` prefix used by the 7 sibling qpack files).
This change resolves all 42 + the 7 qpack renames.

#### Scenario: Class duplicates reduced to canonical-only

- **GIVEN** the 22 class duplicates per the audit (e.g. `MarkingScheme` ×5,
  `LearningOutcome` ×5, `ExamPaper` ×3, `BilingualText` ×3)
- **WHEN** the rename script is applied
- **THEN** the post-rename `grep -rE "^class (MarkingScheme|LearningOutcome|...)\b" cianfhoghlaim/baml/ --include='*.baml' --exclude-dir='_archive' | wc -l` SHALL return ≤ 22
- **AND** the 3 hoisted canonicals (`BilingualText`,
  `MusicGenre`, `LanguageCode`, `DocumentType`) SHALL live under
  `_shared/<type>.baml`

#### Scenario: Function duplicates reduced to canonical-only

- **GIVEN** the 9 function duplicates per the audit
- **WHEN** the rename script is applied
- **THEN** the post-rename `grep -rE "^function (ExtractCurriculumSyllabus|...)\b" cianfhoghlaim/baml/ --include='*.baml' --exclude-dir='_archive' | wc -l` SHALL return ≤ 9
- **AND** the 2 active renames (`ExtractCurriculumSyllabus` →
  `ExtractCurriculumExtraction` in `_shared/document_metadata.baml`,
  `ExtractPublication` → `ExtractResearchGatePublication` in
  `processing/researchgate_extraction.baml`, `CompareCurricula` →
  `CompareCelticCurricula` in `celtic/curriculum/celtic_curriculum.baml`)
  SHALL be applied
- **AND** the 6 legal-extraction dups (`ExtractCourtRule`, `ExtractCourtForm`,
  `ExtractCourtFee`, `ExtractJudgement`, `ExtractPIABPage`,
  `ExtractMarkingScheme`) SHALL already be single-occurrence because the
  parent change's `A2` step deleted `processing/ireland_legal_extraction.baml`

#### Scenario: Enum duplicates reduced to canonical-only

- **GIVEN** the 11 enum duplicates per the audit
- **WHEN** the rename script is applied
- **THEN** the post-rename `grep -rE "^enum (IrishDialect|CelticLanguage|...)\b" cianfhoghlaim/baml/ --include='*.baml' --exclude-dir='_archive' | wc -l` SHALL return ≤ 11
- **AND** the 3 hoisted canonical enums SHALL live under
  `processing/_shared/{music_genre,language_codes,document_type}.baml`

#### Scenario: qpack_mathematics Math* prefix

- **GIVEN** the 7 qpack_mathematics.baml bare-name classes (BilingualText,
  EvidenceLink, FormativeItem, FormativeItemAttempt, ScoreBreakdown,
  QuestPack, QuestPackValidation)
- **WHEN** the rename script is applied
- **THEN** each class SHALL be renamed to its `Math*` prefix form (e.g.
  `BilingualText` → `MathBilingualText`, `QuestPackValidation` →
  `MathQuestPackValidation`)
- **AND** all function signatures that reference these types SHALL be
  updated (`item: FormativeItem` → `item: MathFormativeItem`,
  `-> FormativeItem` → `-> MathFormativeItem`, etc.)
- **AND** the post-rename `qpack_mathematics.baml` SHALL be consistent
  with the 7 sibling qpack files (each uses 8 per-subject prefixed classes)

#### Scenario: Audit notes — canonical home corrections

- **GIVEN** 3 audit inconsistencies (the audit listed canonical homes
  that don't define the type)
- **WHEN** the rename script is applied
- **THEN** for `ExamSection` / `ExamQuestion`, the canonical SHALL stay
  in `_shared/strand_outcome.baml` (not `lc_extraction/exam_paper_layout.baml`
  as the audit listed; that file has `Question` + `QuestionSection` instead)
- **AND** for `CurriculumSpecification`, the canonical SHALL stay in
  `_shared/strand_outcome.baml` (not `cross_nation/multi_nation_curriculum.baml`
  as the audit listed; that file doesn't define it)
- **AND** `MarkingSchemeLc` SHALL be intentionally kept un-renamed
  (the audit called this out — 17 call-sites in `lc_extraction/` depend on it)

## Cross-references

- [`baml_src/`](../../baml_src/) (the 8 BAML files)
- [`baml_client/`](../../baml_client/) (the auto-generated client)
- [`.agents/skills/baml/SKILL.md`](../../.agents/skills/baml/SKILL.md)
- [`baml_src/README.md`](../../baml_src/README.md) (the BAML file map)
