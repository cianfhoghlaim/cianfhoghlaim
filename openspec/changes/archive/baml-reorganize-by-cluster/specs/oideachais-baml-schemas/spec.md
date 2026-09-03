## MODIFIED Requirements

### Requirement: BAML file organisation (3-cluster taxonomy)

The system SHALL organise all BAML files under `cianfhoghlaim/baml/` into 3
purpose-driven cluster sub-directories: `education/`, `celtic/`, `processing/`.
Each cluster SHALL have its own `_shared/` sub-directory for cross-cluster
types. The `celtic/` cluster SHALL have an `_archive/` sub-directory for
BAML files explicitly archived per `openspec/changes/archive-celtic-baml-orphans/`.
Only 2 BAML files SHALL remain at the `baml/` root: `clients.baml` (canonical
LLM clients: `LitellmClient`, `DeepSeekClient`, `MiniMaxClient`,
`LitellmLongContext`, `Extractor`, vision clients, 2 fallback chains) and
`clients_llama_swap.baml` (specialty VL clients: `LlamaSwapClient`,
`LlamaSwapOCRClient`, `LlamaSwapExtractionClient`,
`LlamaSwapReasoningClient`).

The following BAML files are explicitly forbidden at the `baml/` root or
in any legacy location and SHALL be deleted:

- `baml/educational_clients.baml` (zero callers; clients moved to `clients.baml`)
- `baml/curriculum_extraction_0.baml` (BAML 0.x syntax superseded)
- `baml/oideachas.baml` (typo; zero callers)
- `baml/oideachais_other/` directory and all 5 files inside (all duplicates
  of top-level files)

#### Scenario: Aistear BAML lives in `education/stages/`

- **GIVEN** the 5 NCCA education stages (Aistear, Primary, Junior Cycle,
  Senior Cycle, Tertiary)
- **WHEN** a developer searches for the Aistear extraction BAML
- **THEN** `ccc search "ExtractAistearFramework"` returns exactly 1 hit at
  `baml/education/stages/aistear.baml` (plus its 2 backward-compat aliases
  in the same file)
- **AND** `baml/aistear.baml`, `baml/oideachais_other/aistear.baml`, and
  `baml/early_childhood.baml` do not exist

#### Scenario: Celtic BAML lives in `celtic/`

- **GIVEN** the Celtic / Irish language BAML files (the 4 `gaois/` API
  extraction layer files + `celtic_sources.baml` + `celtic_curriculum.baml`
  + `morphology.baml` + `grammar_patterns.baml` + `mythology_extraction.baml`)
- **WHEN** a developer searches for the Duchas Schools Collection BAML
- **THEN** `ccc search "ParseSchoolsVolume"` returns exactly 1 hit at
  `baml/celtic/gaois/duchas.baml`
- **AND** `baml/celtic_sources.baml` and `baml/celtic_curriculum.baml` do
  not exist (they are at `baml/celtic/sources.baml` and
  `baml/celtic/curriculum/celtic_curriculum.baml` respectively)

#### Scenario: Archived Celtic BAML is preserved at `_archive/`

- **GIVEN** the 2 BAML files explicitly archived on 2026-06-24 per
  `openspec/changes/archive-celtic-baml-orphans/`
  (`celtic_linguistics.baml` and `cognates.baml`)
- **WHEN** a developer needs to re-activate the `ExtractMorphology` or
  `IdentifyCognates` BAML functions
- **THEN** the files are at `baml/celtic/_archive/celtic_linguistics.baml`
  and `baml/celtic/_archive/cognates.baml`
- **AND** the re-activation procedure (git mv back to `baml_src/` + remove
  ARCHIVED header + wire the consumer) is documented in the
  `_archive/README.md`

#### Scenario: Generic file-processing BAML lives in `processing/`

- **GIVEN** the 23 generic file-processing BAML files (`email.baml`,
  `upstream_monitoring.baml`, `cv_extraction.baml`, etc.)
- **WHEN** a developer searches for the email-triage BAML
- **THEN** `ccc search "ClassifyEmail"` returns exactly 1 hit at
  `baml/processing/email.baml`
- **AND** `baml/email.baml` does not exist

### Requirement: Curriculum extraction mega-file split

The `curriculum_extraction.baml` mega-file (1114 LOC) SHALL be split into
5 files under `baml/education/_shared/`:

- `education_level.baml` — the 10 enums (`RelationshipType`,
  `DifficultyLevel`, `EducationLevel`, `ExamLevel`, `QuestionType`,
  `LeavingCertSubject`, `Specialism`, `AssessmentComponentType`,
  `RubricStyle`, `DocumentCategory`)
- `strand_outcome.baml` — the 17 classes (`LearningOutcome`, `Skill`,
  `CurriculumSpecification`, `ExamPaper`, `MarkingScheme`,
  `ExaminerReport`, etc.)
- `curriculum_relationships.baml` — the 4 relationship functions
  (`ExtractLearningOutcomeRelationships`, `ExtractSkillsFromOutcome`,
  `ExtractCurriculumFromDocument`, `IdentifyPrerequisiteChain`)
- `subject_rubric.baml` — the 4 rubric functions (`ExtractSubjectRubric`,
  `ScoreEssayAgainstRubric`, `CompareMarkingSchemes`,
  `LazyExtractExamPaper`) + 5 supporting classes
- `document_metadata.baml` — the 2 document metadata functions
  (`ExtractAllPdfMetadata`, `ExtractCurriculumSyllabus`)

#### Scenario: Aistear BAML and Curriculum extraction BAML coexist

- **GIVEN** the 5 NCCA stages (Aistear, Primary, JC, SC, Tertiary) plus the
  cross-stage curriculum extraction (relationships, rubrics, exam papers)
- **WHEN** a developer runs `baml-cli generate`
- **THEN** the generated Python client (`baml/shared/baml_client/`)
  exposes all functions from all 5 stage files PLUS all 5 `_shared/` files
- **AND** the total function count is >= 250 (the current count is 256)

### Requirement: ResearchGate extraction syntax fix

The `baml/processing/researchgate_extraction.baml` file SHALL use valid BAML
syntax (not TypeScript-style type unions). Specifically:
- `venue string | null` SHALL be written as `venue string?`
- `doi string | null` SHALL be written as `doi string?`
- `year int | null` SHALL be written as `year int?`
- `institution string | null` SHALL be written as `institution string?`
- `location string | null` SHALL be written as `location string?`
- `about string | null` SHALL be written as `about string?`
- `abstract string | null` SHALL be written as `abstract string?`

#### Scenario: ResearchGate BAML compiles cleanly

- **WHEN** `baml-cli generate` is run with the fixed
  `baml/processing/researchgate_extraction.baml`
- **THEN** the BAML compiler does NOT emit a syntax error
- **AND** the `ExtractResearchGateProfile` and `ExtractPublication`
  functions are regenerated with the correct optional-typed fields

### Requirement: Aistear extraction (cluster-renamed alias)

The system SHALL support 3 distinct Aistear extraction entry points via
the merged `baml/education/stages/aistear.baml` file:

- `ExtractAistearFrameworkFromText(text, language) -> AistearDocument`
  (canonical — from in-memory text)
- `ExtractAistearFrameworkFromUrl(source_url) -> AistearDocument`
  (from a URL — the oideachais_other variant)
- `ExtractAistearFrameworkFromPdf(pdf_text) -> AistearFramework`
  (from PDF text — the early_childhood variant)

PLUS 2 backward-compat aliases for the merged signatures:
- `ExtractAistearFramework(text, language)` → calls
  `ExtractAistearFrameworkFromText`
- `ExtractAistearFramework(pdf_text)` → calls `ExtractAistearFrameworkFromPdf`

#### Scenario: Aistear extraction from in-memory text

- **GIVEN** an NCCA Aistear PDF at `stedding/ingest_queue/aistear/`
- **WHEN** the `ExtractAistearFrameworkFromText(text, language)` BAML
  function is called with the extracted text + the language code
- **THEN** the function returns an `AistearDocument` with the
  4 Aistear themes (Well-being, Identity & Belonging, Communicating,
  Exploring & Thinking), the `document_id`, the 4 age bands, and the
  12 principles

#### Scenario: Aistear extraction from URL (backward-compat alias)

- **WHEN** the original `oideachais_other/aistear.baml`
  `ExtractAistearFrameworkFromUrl(source_url)` is called
- **THEN** the new merged `baml/education/stages/aistear.baml`
  `ExtractAistearFrameworkFromUrl(source_url)` returns the same shape
- **AND** the existing caller code in
  `baml/oideachais_other/aistear.baml` callers continues to work (the
  new function is at the new path with the same signature)

### Requirement: Primary + Junior Cycle + Tertiary extraction (cluster-renamed aliases)

The system SHALL support 3 Primary extraction entry points and 4 Junior
Cycle extraction entry points and 10 Tertiary extraction entry points via
the merged `baml/education/stages/{primary,junior_cycle,tertiary}.baml` files.
Each merged file SHALL expose ALL functions from both the original
`baml/*.baml` and `baml/oideachais_other/*.baml` files, preserving the
distinct signatures (text vs URL).

#### Scenario: Primary extraction from URL

- **GIVEN** a Primary curriculum area page at
  `https://curriculumonline.ie/primary/.../english/`
- **WHEN** the `ExtractPrimaryFrameworkFromUrl(source_url, stage, area)`
  BAML function is called
- **THEN** the function returns a `PrimaryCurriculumArea` with the
  rationale + strands + integration links

#### Scenario: Junior Cycle extraction (merged)

- **GIVEN** an NCCA Junior Cycle subject spec PDF
- **WHEN** either `ExtractJCSpec(text, subject)` (from in-memory text) or
  `ExtractJCSpecFromUrl(source_url, subject)` (from URL) is called
- **THEN** both functions return a `JCSubjectSpec` with the same shape
  (subject code + short course + assessment components + 2 CBAs)

#### Scenario: Tertiary extraction (merged)

- **GIVEN** a CAO / QQI-FET / Apprenticeship PDF
- **WHEN** either `ExtractCAOCourseList(page_markdown, year)` (from text)
  or `ExtractCAOCourseListFromUrl(page_url, year)` (from URL) is called
- **THEN** both functions return a `CAOCourse[]` with the same shape
  (course code, title, institution, HEI type, NFQ level, points)

### Requirement: NCCA education stages cluster

The `baml/education/stages/` cluster SHALL contain exactly 5 BAML files,
one per NCCA education stage:

- `aistear.baml` (merged from 3 sources — see "Aistear extraction
  (cluster-renamed alias)")
- `primary.baml` (merged from 2 sources — see "Primary + Junior Cycle +
  Tertiary extraction (cluster-renamed aliases)")
- `junior_cycle.baml` (merged from 2 sources)
- `senior_cycle.baml` (moved from `baml/oideachais_other/senior_cycle.baml`)
- `tertiary.baml` (merged from 2 sources)

PLUS 1 BAML file in `baml/education/pdfs/` for the leaving-cert PDF
extraction pipeline:
- `leaving_cert_syllabus.baml`
- `leaving_cert_past_paper.baml`
- `leaving_cert_marking_scheme.baml`

PLUS 8 BAML files in `baml/education/subjects/` for the per-NCCA-subject
quest pack generators:
- `qpack_mathematics.baml`, `qpack_applied_mathematics.baml`,
  `qpack_chemistry.baml`, `qpack_geography.baml`, `qpack_history.baml`,
  `qpack_english.baml`, `qpack_gaeilge.baml`, `qpack_computer_science.baml`

#### Scenario: 8 NCCA subject quest pack generators

- **GIVEN** the 8 NCCA LC subjects (Mathematics, Applied Mathematics,
  Chemistry, Geography, History, English, Gaeilge, Computer Science)
- **WHEN** the MMO agent for a specific subject (e.g.
  `agents/tuatha/subject_agents/math_agent.py`) imports the corresponding
  qpack BAML function
- **THEN** the import resolves to
  `baml.education.subjects.qpack_<subject>.Generate<Subject>QuestPack`
  (after the follow-on `wire-baml-to-consolidated-pipelines` change
  updates the consumer import paths)

### Requirement: Celtic / Irish language cluster

The `baml/celtic/` cluster SHALL contain:

- `gaois/duchas.baml`, `gaois/logainm.baml`, `gaois/tearma.baml`,
  `gaois/folklore_extraction.baml` (the 4 gaois.ie API extraction files)
- `sources.baml` (the source-agnostic unified record — renamed from
  `baml/celtic_sources.baml`)
- `curriculum/celtic_curriculum.baml` (Celtic-nation curriculum
  comparison — renamed from `baml/celtic_curriculum.baml`)
- `curriculum/mythology_extraction.baml` (moved from
  `baml/mythology_extraction.baml`)
- `morphology.baml`, `grammar_patterns.baml` (Irish grammar)
- `_archive/celtic_linguistics.baml`, `_archive/cognates.baml` (the 2
  archived 2026-06-24 files, preserved for re-activation)

#### Scenario: Duchas Schools Collection extraction

- **GIVEN** a Schools Collection volume JSON response from
  `docs.gaois.ie/en/data/duchas/v0.6/api`
- **WHEN** the `ParseSchoolsVolume(json_response)` BAML function is called
- **THEN** the function returns a `DuchasSchoolsVolume` with the volume ID
  + school information + parts + items + topics + collector + informant
  + transcription (preserves Irish text with fadas per the
  `ParseSchoolsVolume` prompt)

### Requirement: Generic file-processing cluster

The `baml/processing/` cluster SHALL contain exactly 23 BAML files covering
the 7 categories of generic file processing:

- **Email triage**: `email.baml` (the leabharlann inbox pipeline)
- **Upstream monitoring**: `upstream_monitoring.baml` (the 4 upstream
  packages — motherduck / dlthub / lancedb / cocoindex)
- **People / CV**: `cv_extraction.baml`, `portfolio_extraction.baml`,
  `linkedin_profile_extraction.baml`, `researchgate_extraction.baml`
- **Content / docs**: `author_archive.baml` (Gemini Deep Research PDFs),
  `circular_extraction.baml` (DoE circulars), `identity_verification.baml`
- **Media**: `audio_extraction.baml` (Canúint audio recordings),
  `artwork_analysis.baml`, `image_generation.baml` (FIBO),
  `style_transfer.baml` (FIBO)
- **MMO game content**: `game_content.baml`, `player_assessment.baml`,
  `generators.baml`
- **Generic**: `ocr_extraction.baml`, `ocr_validation.baml`,
  `culture_extraction.baml`, `named_entities.baml`, `site_analysis.baml`,
  `official_media.baml`, `ui_components.baml`, `teaching_extraction.baml`

#### Scenario: ResearchGate extraction (syntax-fixed)

- **GIVEN** a ResearchGate profile HTML page (e.g. for the
  `cianfhoghlaim` slug)
- **WHEN** `ExtractResearchGateProfile(text)` is called from
  `baml/processing/researchgate_extraction.baml`
- **THEN** the function returns a `ResearchGateProfile` with the name,
  headline, institution, fields of study, skills, publications
  (with `venue: string?`, `doi: string?`, `year: int?` — the
  syntax-fixed optional fields), followers, following, h-index, total
  reads, total citations, profile URL, streamId, and owner slug