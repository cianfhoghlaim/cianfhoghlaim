# Spec Delta — Multi-Stage Cognee (6 datasets + cross-stage cognify)

## MODIFIED Requirements

### Requirement: Multi-Dataset Knowledge Graph

The system SHALL provide **6 Cognee datasets**, one per educational stage, plus a cross-stage cognify pass.

#### Scenario: Aistear Dataset
- **GIVEN** the `oideachais.aistear` Cognee dataset
- **WHEN** the `aistear_knowledge_graph` Dagster asset triggers cognify
- **THEN** the dataset contains `AistearDocument`, `AistearPrinciple`, `AistearLearningGoal`, `Naionra` nodes
- **AND** the dataset is queryable via `cognee.search("circular motion naíonra Well-being theme")` returning semantically-ranked results

#### Scenario: Senior Cycle Dataset
- **GIVEN** the `oideachais.senior_cycle` Cognee dataset
- **WHEN** the `senior_cycle_knowledge_graph` Dagster asset triggers cognify
- **THEN** the dataset contains `ExamPaper`, `MarkingScheme`, `ExaminerReport`, `SubjectRubric`, `LearningOutcome`, `CurriculumSpecification` nodes
- **AND** queries for "rubric descriptors for PCLM" return `RubricDescriptor` nodes with weightings

#### Scenario: Tertiary Dataset
- **GIVEN** the `oideachais.tertiary` Cognee dataset
- **WHEN** the `tertiary_knowledge_graph` Dagster asset triggers cognify
- **THEN** the dataset contains `CAOCourse`, `MatriculationRequirement`, `QqiFetAward`, `Apprenticeship`, `Programme`, `ApplicationTimeline` nodes
- **AND** queries for "matriculation requirements for medicine at UCD" return `MatriculationRequirement[]` for `LC_BIOLOGY`, `LC_CHEMISTRY`, `LC_PHYSICS`, `LC_MATHS` with grades `H4` etc.

#### Scenario: Cross-Stage Cognify Edges
- **GIVEN** all 5 stage datasets have cognified
- **WHEN** the `cross_stage_cognify` Dagster asset materialises
- **THEN** Cognee creates 8 edge types: `BRIDGES_TO`, `PREPARES_FOR`, `PROGRESSES_TO`, `ASSESSED_BY`, `REQUIRED_FOR`, `DELIVERS`, `LADDERS_INTO`, `ALTERNATIVE_TO`
- **AND** a query like "what prepares for LC Physics?" walks `(:JCLearningOutcome) -[:PROGRESSES_TO]-> (:SCLearningOutcome)` and returns the relevant LC topics

## ADDED Requirements

### Requirement: Per-Dataset Convex Mirror
The system SHALL mirror each Cognee dataset to a per-stage LanceDB table for low-latency retrieval from the SPA.

#### Scenario: Cross-Dataset Search from SPA
- **GIVEN** a user query from the Awen chat (e.g., "compare PCLM with Geography SRP")
- **WHEN** the `OideachasChat` component opens
- **THEN** the chat server fetches relevant nodes from BOTH `celtic_curriculum_embeddings` (existing) AND the 5 new stage LanceDB tables
- **AND** the Agno team routes the query to the right stage-specific sub-agent
