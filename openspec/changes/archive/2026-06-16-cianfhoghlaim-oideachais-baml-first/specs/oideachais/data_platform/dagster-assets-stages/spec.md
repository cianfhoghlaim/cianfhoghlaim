# Spec Delta — Multi-Stage Dagster KG Assets (6 assets + cross-stage cognify)

## MODIFIED Requirements

### Requirement: Knowledge Graph (multi-stage)

The system SHALL provide a Dagster asset for each of the 5 stages of Irish education, plus 1 cross-stage cognify asset and 1 nightly UI suggestion asset.

#### Scenario: Aistear KG Asset
- **GIVEN** `oideachais/data_platform/dagster_defs/assets/aistear_kg.py`
- **WHEN** the `aistear_knowledge_graph` asset materialises
- **THEN** it reads from the Aistear DLT source
- **AND** runs `baml.ExtractAistearFramework` and `baml.ExtractNaionraListing` on the raw text
- **AND** writes `AistearDocument`, `AistearPrinciple`, `AistearLearningGoal`, `Naionra` rows to LanceDB `aistear_knowledge_graph` table
- **AND** triggers Cognee `oideachais.aistear` dataset cognify

#### Scenario: Primary KG Asset
- **GIVEN** `oideachais/data_platform/dagster_defs/assets/primary_kg.py`
- **WHEN** the `primary_knowledge_graph` asset materialises
- **THEN** it writes `PrimaryCurriculumArea`, `PrimaryStrand`, `PrimaryLearningOutcome` to LanceDB `primary_knowledge_graph`
- **AND** triggers Cognee `oideachais.primary` dataset cognify

#### Scenario: Junior Cycle KG Asset
- **GIVEN** `oideachais/data_platform/dagster_defs/assets/junior_cycle_kg.py`
- **WHEN** the `junior_cycle_knowledge_graph` asset materialises
- **THEN** it writes `JCSubjectSpec`, `CBATask`, `RubricDescriptor` to LanceDB `junior_cycle_knowledge_graph`
- **AND** triggers Cognee `oideachais.junior_cycle` dataset cognify

#### Scenario: Senior Cycle KG Asset
- **GIVEN** `oideachais/data_platform/dagster_defs/assets/senior_cycle_kg.py`
- **WHEN** the `senior_cycle_knowledge_graph` asset materialises
- **THEN** it joins the existing `pdf_extracted_text` asset (from `pdf_assets.py`) with the `exam_materials_assets` partitions
- **AND** fires `baml.ExtractExamPaperStructure`, `baml.ExtractMarkingScheme`, `baml.ExtractSubjectRubric` per `(subject, year, level, paper)`
- **AND** writes `ExamPaper`, `MarkingScheme`, `ExaminerReport`, `SubjectRubric` to LanceDB `senior_cycle_knowledge_graph`
- **AND** triggers Cognee `oideachais.senior_cycle` dataset cognify

#### Scenario: Tertiary KG Asset
- **GIVEN** `oideachais/data_platform/dagster_defs/assets/tertiary_kg.py`
- **WHEN** the `tertiary_knowledge_graph` asset materialises
- **THEN** it writes `CAOCourse`, `MatriculationRequirement`, `QqiFetAward`, `Apprenticeship`, `ApplicationTimeline` to LanceDB `tertiary_knowledge_graph`
- **AND** triggers Cognee `oideachais.tertiary` dataset cognify

#### Scenario: Cross-Stage Cognify
- **GIVEN** `oideachais/data_platform/cognee_integration/cross_stage_cognify.py`
- **WHEN** the `cross_stage_cognify` asset materialises after all 5 stage KGs
- **THEN** it creates the 8 cross-stage edges in Cognee:
  - `(:AistearPrinciple) -[:BRIDGES_TO]-> (:PrimaryLearningOutcome)`
  - `(:PrimaryLearningOutcome) -[:PREPARES_FOR]-> (:JCLearningOutcome)`
  - `(:JCLearningOutcome) -[:PROGRESSES_TO]-> (:SCLearningOutcome)`
  - `(:SCLearningOutcome) -[:ASSESSED_BY]-> (:ExamQuestion)`
  - `(:LCSubject) -[:REQUIRED_FOR]-> (:CAOCourse)`
  - `(:CAOCourse) -[:DELIVERS]-> (:Programme)`
  - `(:QQIFetAward) -[:LADDERS_INTO]-> (:CAOCourse)`
  - `(:Apprenticeship) -[:ALTERNATIVE_TO]-> (:CAOCourse)`

## ADDED Requirements

### Requirement: Nightly UI Suggestion Asset
The system SHALL provide a nightly `ui_suggestion_asset` that calls `baml.SuggestUIComponents` against the populated Cognee index and writes to LanceDB `ui_component_suggestions`.

#### Scenario: UI Suggestion Generation
- **GIVEN** all 5 stage KGs have materialised
- **WHEN** the `ui_suggestion_asset` runs (cron: `0 3 * * *`)
- **THEN** it calls `b.SuggestUIComponents(extracted_subjects, cognee_index_summary, stage)` for each of the 5 stages
- **AND** writes the resulting `UIComponentSuggestion[]` to LanceDB `ui_component_suggestions` table
- **AND** the SPA's `<ComponentCatalog>` admin route reads from this table
