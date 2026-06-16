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

## Cross-references

- [`baml_src/`](../../baml_src/) (the 8 BAML files)
- [`baml_client/`](../../baml_client/) (the auto-generated client)
- [`.agents/skills/baml/SKILL.md`](../../.agents/skills/baml/SKILL.md)
- [`baml_src/README.md`](../../baml_src/README.md) (the BAML file map)
