# Spec Delta — Subjects Manifest (5 stages × multilingual metadata)

## ADDED Requirements

### Requirement: Subjects Manifest
The system SHALL provide a JSON manifest of all subjects, stages, and HEIs, used by the BAML context files, the DLT source router, and the SPA's route metadata.

#### Scenario: Stages Manifest
- **GIVEN** `sruth/oideachais/data_platform/subjects/stages.json`
- **WHEN** the file is loaded
- **THEN** it contains 5 stages: `aistear`, `primary`, `junior_cycle`, `senior_cycle`, `tertiary`
- **AND** each stage has bilingual `name_en` and `name_ga` fields, an Irish-language URL slug, an icon, and a list of available BAML context files

#### Scenario: Senior Cycle Subjects Manifest
- **GIVEN** `sruth/oideachais/data_platform/subjects/lc_subjects.json`
- **WHEN** the file is loaded
- **THEN** it contains 50+ Leaving Cert subjects with: `{slug, name_en, name_ga, awarding_body, levels, marking_style, has_aural, has_coursework, specialism, nfq_level}`

#### Scenario: Junior Cycle Subjects Manifest
- **GIVEN** `sruth/oideachais/data_platform/subjects/jc_subjects.json`
- **WHEN** the file is loaded
- **THEN** it contains 18 core JC subjects + 16 short courses with: `{slug, name_en, name_ga, level_1lp, level_2lp, cbas: [{cba_1_name, cba_2_name}]}`

#### Scenario: HEI Manifest
- **GIVEN** `sruth/oideachais/data_platform/subjects/hei.json`
- **WHEN** the file is loaded
- **THEN** it contains 8+ HEIs (NUI: UCD, UCG, UCC, UL, Maynooth; Trinity; ATU; TUS; SETU; MTU; RCSI; MIC) with: `{code, name_en, name_ga, hei_type, nfq_max, matriculation_url, has_qqi_ladder, has_apprenticeship}`

#### Scenario: Manifest Lookup
- **GIVEN** a stage slug (e.g., `tertiary`) and a subject slug (e.g., `medicine`)
- **WHEN** `oideachais.data_platform.subjects.manifest.lookup(stage, subject)` is called
- **THEN** the function returns the manifest entry for that subject in that stage
- **AND** raises `KeyError` if the subject doesn't exist in that stage

### Requirement: BAML Context Files per Stage
The system SHALL provide 5 per-stage BAML context files in `sruth/oideachais/data_platform/subjects/baml_context/` that pre-load the BAML `client` with stage-specific system prompts.

#### Scenario: Aistear Context
- **GIVEN** `sruth/oideachais/data_platform/subjects/baml_context/aistear.baml`
- **WHEN** the file is loaded
- **THEN** the system prompt references NCCA Aistear framework, the 4 themes, the 4 age bands, and the principles of holistic child development
- **AND** the BAML client default is `litellm/gemini-2.0-flash`

#### Scenario: Primary Context
- **GIVEN** `sruth/oideachais/data_platform/subjects/baml_context/primary.baml`
- **WHEN** the file is loaded
- **THEN** the system prompt references the NCCA Primary Curriculum Framework, the 12 curriculum areas, the 4 stages
- **AND** the BAML client default is `litellm/gemini-2.0-flash`

#### Scenario: Junior Cycle Context
- **GIVEN** `sruth/oideachais/data_platform/subjects/baml_context/junior_cycle.baml`
- **WHEN** the file is loaded
- **THEN** the system prompt references the 18 JC subjects + 16 short courses, the CBA structure, the Level 1 / Level 2 Learning Programmes
- **AND** the BAML client default is `litellm/gemini-2.0-flash`

#### Scenario: Senior Cycle Context
- **GIVEN** `sruth/oideachais/data_platform/subjects/baml_context/senior_cycle.baml`
- **WHEN** the file is loaded
- **THEN** the system prompt references the SEC, Chief Examiner reports, the 50+ LC subjects, and the 10 `RubricStyle` values
- **AND** the BAML client default is `litellm/gemini-2.0-flash`
- **AND** `ScoreEssayAgainstRubric` overrides to `litellm/anthropic/claude-sonnet-4-20250514`

#### Scenario: Tertiary Context
- **GIVEN** `sruth/oideachais/data_platform/subjects/baml_context/tertiary.baml`
- **WHEN** the file is loaded
- **THEN** the system prompt references CAO, NUI/HEI matriculation, QQI FET awards, Apprenticeship pathways, and the DARE/HEAR/mature-student routes
- **AND** the BAML client default is `litellm/gemini-2.0-flash`
