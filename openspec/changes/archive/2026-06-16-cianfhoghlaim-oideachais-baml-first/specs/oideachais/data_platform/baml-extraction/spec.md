# Spec Delta — BAML Extraction (5 stages)

## MODIFIED Requirements

### Requirement: BAML Schema Coverage

The system SHALL provide BAML schemas for **all 5 stages of Irish education** (Aistear, Primary, Junior Cycle, Senior Cycle, Tertiary), not just Senior Cycle.

#### Scenario: Aistear Schema
- **GIVEN** an Aistear framework PDF from `ncca.ie/en/early-childhood/` or `curriculumonline.ie`
- **WHEN** `baml.ExtractAistearFramework(text, language)` is invoked
- **THEN** the system returns an `AistearDocument` with `themes: AistearTheme[]`, `principles: AistearPrinciple[]`, `learning_goals: AistearLearningGoal[]` for each of the 4 themes (Well-being, Identity & Belonging, Communicating, Exploring & Thinking) × 4 age bands (Infants, Toddlers, Pre-school, Early-Primary Bridge)
- **AND** every field has both `*_en` and `*_ga` variants (bilingual)

#### Scenario: Primary Schema
- **GIVEN** a Primary Curriculum Framework PDF
- **WHEN** `baml.ExtractPrimaryFramework(text, stage, area)` is invoked
- **THEN** the system returns a `PrimaryCurriculumArea` with `strands: PrimaryStrand[]` × `outcomes: PrimaryLearningOutcome[]` for one of the 12 curriculum areas (English, Irish, Mathematics, SESE-Science, SESE-History, SESE-Geography, Visual Arts, Music, Drama, PE, SPHE, Religion) × 4 stages (Junior/Senior Infants, 1st/2nd, 3rd/4th, 5th/6th Class)
- **AND** outcomes link to Aistear via `BridgeAistearToPrimary` edges

#### Scenario: Junior Cycle Schema
- **GIVEN** a Junior Cycle specification PDF
- **WHEN** `baml.ExtractJCSpec(text, subject)` is invoked
- **THEN** the system returns a `JCSubjectSpec` with `strands: CurriculumStrand[]`, `cba_tasks: CBATask[]` (2 CBAs per subject), `learning_outcomes: LearningOutcome[]` for one of 18 core subjects or 16 short courses
- **AND** `RubricDescriptor` arrays are populated for each CBA with the 4 `AchievementLevel` levels (Exceptional, AboveExpectations, InLineWithExpectations, YetToMeetExpectations)

#### Scenario: Senior Cycle Schema (Extended)
- **GIVEN** a Leaving Certificate exam paper or marking scheme
- **WHEN** `baml.ExtractExamPaperStructure` / `baml.ExtractMarkingScheme` / `baml.ExtractSubjectRubric` is invoked
- **THEN** the system returns an `ExamPaper` / `MarkingScheme` / `SubjectRubric` with full question-marks-rubric-detail structure for one of 50+ Leaving Cert subjects
- **AND** the new `RubricStyle` enum discriminates the per-subject rubric style (PCLM, SRP, EQUATION_STEPS, KEYWORD_MATCH_DIAGRAM, COMPREHENSION_EXPRESSION, SECTION_B_KEYWORD, DIAGRAM_SKETCH_STEPS, BALANCED_EQUATION_STATE_SYMBOLS, DEFINITION_UNIT_FORMULA, RUBRIC_PCLM_IRISH)
- **AND** `LazyExtractExamPaper` is the on-demand variant that respects `ExtractionBudget` per session

#### Scenario: Tertiary Schema
- **GIVEN** a CAO course listing page, an NUI/HEI matriculation statement, a QQI FET award list, or an Apprenticeship listing
- **WHEN** `baml.ExtractCAOCourseList(page_markdown, year)` or `baml.ExtractMatriculationRules(page_markdown, institution)` is invoked
- **THEN** the system returns `CAOCourse[]` / `MatriculationRequirement[]` for one of 8+ HEI types (University, IoT, College of Education, Private College, RCSI, MIC) × 10 NFQ levels
- **AND** `EstimateCoursePoints(course, applicant_grades, historical)` predicts the cutoff points for a given LC grade profile
- **AND** `AuditMatriculation(institution, applicant_grades, rules)` returns a pass/fail per rule

#### Scenario: UI Component Suggestion Schema
- **GIVEN** a populated Cognee index summary and a list of extracted subjects
- **WHEN** `baml.SuggestUIComponents(extracted_subjects, cognee_index_summary, stage)` is invoked nightly
- **THEN** the system returns `UIComponentSuggestion[]` with 28 possible `UIComponentKind` values (STAGE_OVERVIEW, SUBJECT_GRID, AISTEAR_THEMES_GRID, PRIMARY_STRAND_TREE, JC_CBA_TIMELINE, SC_EXAM_PAPER_CARD, TERTIARY_CAO_COURSE_CARD, etc.) — each with a route slug, bilingual title, and priority 1-5

#### Scenario: BAML Tests Pass
- **GIVEN** the 5 new BAML files
- **WHEN** `baml-cli test` is run
- **THEN** all existing tests pass (the 3 from `baml_src/curriculum_extraction.baml`)
- **AND** at least one new test exists per new BAML file: `test ExtractAistearFrameworkTest`, `test ExtractPrimaryFrameworkTest`, `test ExtractJCSpecTest`, `test ExtractCAOCourseListTest`, `test SuggestUIComponentsTest`

## ADDED Requirements

### Requirement: Bilingual BAML Fields
The system SHALL require that every BAML class that represents a human-readable concept has both `*_en` and `*_ga` fields.

#### Scenario: Aistear Learning Goal Bilingual
- **GIVEN** an `AistearLearningGoal`
- **WHEN** the field set is inspected
- **THEN** `text_en: string` and `text_ga: string?` are both present
- **AND** `sample_practice_en: string?` and `sample_practice_ga: string?` are both present
- **AND** `parent_tip_en: string?` and `parent_tip_ga: string?` are both present

#### Scenario: Tertiary Course Bilingual
- **GIVEN** a `CAOCourse`
- **WHEN** the field set is inspected
- **THEN** `title_en: string` and `title_ga: string?` are both present
- **AND** `Programme.description_en: string` and `Programme.description_ga: string?` are both present

#### Scenario: Component Suggestion Bilingual
- **GIVEN** a `UIComponentSuggestion`
- **WHEN** the field set is inspected
- **THEN** `title_en: string` and `title_ga: string?` are both present
- **AND** the `route_slug` is language-neutral (e.g., `mathematics`, not `mathematics-ga`)

### Requirement: BAML Context Files per Stage
The system SHALL provide 5 per-stage BAML context files that pre-load the BAML `client` with stage-specific system prompts and exam-board conventions.

#### Scenario: Senior Cycle Context
- **GIVEN** `sruth/oideachais/data_platform/subjects/baml_context/senior_cycle.baml`
- **WHEN** the file is loaded
- **THEN** the system prompt references the SEC (State Examinations Commission), Chief Examiner reports, and the 50+ LC subjects
- **AND** the BAML client default is `litellm/gemini-2.0-flash`

#### Scenario: Tertiary Context
- **GIVEN** `sruth/oideachais/data_platform/subjects/baml_context/tertiary.baml`
- **WHEN** the file is loaded
- **THEN** the system prompt references CAO points, NUI matriculation, QQI FET awards, and Apprenticeship pathways
- **AND** the BAML client default for `ScoreEssayAgainstRubric` is `litellm/anthropic/claude-sonnet-4-20250514`

## REMOVED Requirements

### Requirement: Single-Stage Senior-Cycle-Only BAML

**Reason**: The BAML coverage is being extended to all 5 stages of Irish education, not just Senior Cycle. The single-stage restriction is replaced by the per-stage schemas above.

**Migration**: All existing BAML classes for Senior Cycle (`ExamPaper`, `MarkingScheme`, `ExaminerReport`, `CurriculumSpecification`, `LearningOutcome`) remain unchanged. The new schemas are additive — they add new types and functions, not modify existing ones.
