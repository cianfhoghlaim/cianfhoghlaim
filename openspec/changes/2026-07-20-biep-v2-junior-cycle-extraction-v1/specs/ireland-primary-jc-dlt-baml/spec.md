## ADDED Requirements

### Requirement: Junior Cycle BAML extraction (per-subject)

The system SHALL provide 4 BAML extraction functions at
`baml_src/british_isles/ireland/education/junior_cycle/`:

- `ExtractJCCurriculum(subject, language, year, text) -> JCCurriculumSpec`
- `ExtractCBADescriptor(text) -> CBATask`
- `ExtractJCShortCourse(text) -> JCShortCourse`
- `ExtractJCExamPaper(text) -> JCExamPaper`

The 18 NCCA Junior Cycle subjects (`english`, `gaeilge`, `mathematics`,
`irish_history`, `geography`, `science`, `business_studies`, `french`,
`german`, `spanish`, `italian`, `home_economics`, `music`, `art`,
`technology`, `engineering`, `graphics`, `wood_technology`) SHALL each have
an EN source and a GA source at
`dlt/british_isles/ireland/education/junior_cycle_subjects/`
(36 sources total), and the 16 short courses SHALL each have a single source
(English-only is canonical, but the source SHALL emit rows tagged with
`language="en"` and optionally `language="ga"` if a GA spec exists).

#### Scenario: JC English GA extraction

- **WHEN** the developer runs `dagster asset materialize jc_english_ga_extracted`
- **THEN** the BAML function `b.ExtractJCCurriculum(subject="english", language="ga", year=1, text=...)` is invoked
- **AND** the resulting `JCCurriculumSpec` carries `language="ga"`, `subject="english"`, `year=YEAR_1`
- **AND** the row lands in `oideachais.education.british_isles.ireland.junior_cycle.english.ga`
- **AND** the corresponding LanceDB table `oideachais.jc.english.year_1_ga` is populated by the CocoIndex App

#### Scenario: JC Coding short-course

- **WHEN** the developer runs `dagster asset materialize jc_short_course_coding_extracted`
- **THEN** the BAML function `b.ExtractJCShortCourse(text=...)` is invoked
- **AND** the resulting `JCShortCourse` carries `course_slug="coding"`, `language="en"`, `hours > 0`, `learning_outcomes[]` non-empty

#### Scenario: CBA descriptor extraction

- **WHEN** the developer runs `dagster asset materialize jc_cba_english_1_extracted`
- **THEN** the BAML function `b.ExtractCBADescriptor(text=...)` is invoked
- **AND** the resulting `CBATask` carries `subject="english"`, `cba_id="english_cba_1"`, `weighting > 0`
- **AND** the row lands in `oideachais.education.british_isles.ireland.junior_cycle.cbas.english.1`
