# baml-reorganize-by-cluster — Tasks

## Phase 1 — Create the new directory structure (no file moves)

- [ ] 1.1 Create `baml/education/_shared/`
- [ ] 1.2 Create `baml/education/stages/`
- [ ] 1.3 Create `baml/education/pdfs/`
- [ ] 1.4 Create `baml/education/subjects/`
- [ ] 1.5 Create `baml/education/cross_nation/`
- [ ] 1.6 Create `baml/education/statistics/`
- [ ] 1.7 Create `baml/education/university/`
- [ ] 1.8 Create `baml/celtic/_shared/`
- [ ] 1.9 Create `baml/celtic/curriculum/`
- [ ] 1.10 Create `baml/celtic/_archive/`
- [ ] 1.11 Create `baml/processing/_shared/`
- [ ] 1.12 Validate: `ls -la baml/` shows the new sub-directories + the 2 client files at root + `cli.py` + `shared/`

## Phase 2 — Move the 8 qpack_*.baml files into `education/subjects/`

Pure `git mv` operations, no content changes.

- [ ] 2.1 `git mv baml/qpack_mathematics.baml baml/education/subjects/qpack_mathematics.baml`
- [ ] 2.2 `git mv baml/qpack_applied_mathematics.baml baml/education/subjects/qpack_applied_mathematics.baml`
- [ ] 2.3 `git mv baml/qpack_chemistry.baml baml/education/subjects/qpack_chemistry.baml`
- [ ] 2.4 `git mv baml/qpack_geography.baml baml/education/subjects/qpack_geography.baml`
- [ ] 2.5 `git mv baml/qpack_history.baml baml/education/subjects/qpack_history.baml`
- [ ] 2.6 `git mv baml/qpack_english.baml baml/education/subjects/qpack_english.baml`
- [ ] 2.7 `git mv baml/qpack_gaeilge.baml baml/education/subjects/qpack_gaeilge.baml`
- [ ] 2.8 `git mv baml/qpack_computer_science.baml baml/education/subjects/qpack_computer_science.baml`
- [ ] 2.9 Validate: `ls baml/qpack_*.baml` returns "No such file or directory"
- [ ] 2.10 Validate: `ls baml/education/subjects/` shows all 8 qpack files

## Phase 3 — Move the 3 leaving_cert_*_extraction.baml files into `education/pdfs/`

Pure `git mv` operations, no content changes.

- [ ] 3.1 `git mv baml/leaving_cert_syllabus_extraction.baml baml/education/pdfs/leaving_cert_syllabus.baml`
- [ ] 3.2 `git mv baml/leaving_cert_past_paper_extraction.baml baml/education/pdfs/leaving_cert_past_paper.baml`
- [ ] 3.3 `git mv baml/leaving_cert_marking_scheme_extraction.baml baml/education/pdfs/leaving_cert_marking_scheme.baml`
- [ ] 3.4 Validate: `ls baml/leaving_cert_*.baml` returns "No such file or directory"
- [ ] 3.5 Validate: `ls baml/education/pdfs/` shows all 3 files

## Phase 4 — Move the cross_nation / statistics / university BAML files

Pure `git mv` operations.

- [ ] 4.1 `git mv baml/isles_education.baml baml/education/cross_nation/isles_education.baml`
- [ ] 4.2 `git mv baml/multi_nation_curriculum.baml baml/education/cross_nation/multi_nation_curriculum.baml`
- [ ] 4.3 `git mv baml/education_statistics.baml baml/education/statistics/education_statistics.baml`
- [ ] 4.4 `git mv baml/university_extraction.baml baml/education/university/university_extraction.baml`
- [ ] 4.5 Validate: `ls baml/isles_education.baml baml/multi_nation_curriculum.baml baml/education_statistics.baml baml/university_extraction.baml` all return "No such file or directory"

## Phase 5 — Merge the 5 NCCA stage duplicates into `education/stages/`

### Phase 5a — `aistear.baml` (merge from 3 sources)

- [ ] 5a.1 Read `baml/aistear.baml` (208 LOC) fully
- [ ] 5a.2 Read `baml/oideachais_other/aistear.baml` (31 LOC) fully
- [ ] 5a.3 Read `baml/early_childhood.baml` (82 LOC) fully
- [ ] 5a.4 Write `baml/education/stages/aistear.baml` (the merged file) containing:
  - All 4 enums from `aistear.baml`: `AistearTheme`, `AistearAgeBand`, `AistearLanguageMedium`
  - New enum: `AistearDialect` (Munster / Connacht / Ulster / Standard — the same dialect enum used in `celtic_sources.baml` and `gaois/duchas.baml`)
  - All 4 classes from `aistear.baml` (the richest schema): `AistearPrinciple`, `AistearLearningGoal`, `GeoPoint`, `Naionra`, `AistearDocument`, `BridgeEdge`
  - 3 distinct functions, each renamed to disambiguate:
    - `ExtractAistearFrameworkFromText(text, language)` (from `aistear.baml` `ExtractAistearFramework`)
    - `ExtractAistearFrameworkFromUrl(source_url)` (from `oideachais_other/aistear.baml` `ExtractAistearFrameworkFromUrl`)
    - `ExtractAistearFrameworkFromPdf(pdf_text)` (from `early_childhood.baml` `ExtractAistearFramework`)
  - 2 preserved functions (no rename needed): `ExtractNaionraListing(page_markdown)`, `BridgeAistearToPrimary(aistear_doc, primary_doc)`
  - 2 backward-compat aliases:
    - `ExtractAistearFramework(text, language)` → calls `ExtractAistearFrameworkFromText` (for the `aistear.baml` callers)
    - `ExtractAistearFramework(pdf_text)` → calls `ExtractAistearFrameworkFromPdf` (for the `early_childhood.baml` callers)
- [ ] 5a.5 `git rm baml/aistear.baml baml/early_childhood.baml`
- [ ] 5a.6 Validate: `ls baml/aistear.baml baml/early_childhood.baml` returns "No such file or directory"
- [ ] 5a.7 Validate: `ls baml/education/stages/aistear.baml` exists

### Phase 5b — `primary.baml` (merge from 2 sources)

- [ ] 5b.1 Read `baml/primary.baml` (171 LOC) fully
- [ ] 5b.2 Read `baml/oideachais_other/primary.baml` (45 LOC) fully
- [ ] 5b.3 Write `baml/education/stages/primary.baml` containing:
  - All enums from `primary.baml`: `PrimaryStage`, `PrimaryAreaCode`
  - All 4 classes from `primary.baml`: `CompetencyLink`, `PrimaryLearningOutcome`, `PrimaryStrand`, `PrimaryCurriculumArea`
  - 3 functions:
    - `ExtractPrimaryFramework(text, stage, area)` (from `primary.baml`)
    - `ExtractPrimaryLearningOutcomes(text, stage, area)` (from `primary.baml`)
    - `ExtractPrimaryFrameworkFromUrl(source_url, stage, area)` (from `oideachais_other/primary.baml`)
- [ ] 5b.4 `git rm baml/primary.baml`
- [ ] 5b.5 Validate: `ls baml/primary.baml` returns "No such file or directory"

### Phase 5c — `junior_cycle.baml` (merge from 2 sources)

- [ ] 5c.1 Read `baml/junior_cycle.baml` (229 LOC) fully
- [ ] 5c.2 Read `baml/oideachais_other/junior_cycle.baml` (39 LOC) fully
- [ ] 5c.3 Write `baml/education/stages/junior_cycle.baml` containing:
  - All enums: `JuniorCycleSubject`, `JuniorCycleShortCourse`, `AchievementLevel`
  - All 5 classes: `RubricDescriptor`, `CBATask`, `JCWellbeingStatement`, `JCSubjectSpec`, `L2LPOutcome`
  - 4 functions:
    - `ExtractJCSpec(text, subject)` (from `junior_cycle.baml`)
    - `ExtractCBADescriptor(text, task_name)` (from `junior_cycle.baml`)
    - `ExtractShortCourse(text, course_name)` (from `junior_cycle.baml`)
    - `ExtractJCSpecFromUrl(source_url, subject)` (from `oideachais_other/junior_cycle.baml`)
- [ ] 5c.4 `git rm baml/junior_cycle.baml`
- [ ] 5c.5 Validate: `ls baml/junior_cycle.baml` returns "No such file or directory"

### Phase 5d — `senior_cycle.baml` (move from 1 source)

- [ ] 5d.1 Read `baml/oideachais_other/senior_cycle.baml` (76 LOC) fully
- [ ] 5d.2 `git mv baml/oideachais_other/senior_cycle.baml baml/education/stages/senior_cycle.baml`
- [ ] 5d.3 Validate: `ls baml/education/stages/senior_cycle.baml` exists

### Phase 5e — `tertiary.baml` (merge from 2 sources)

- [ ] 5e.1 Read `baml/tertiary.baml` (332 LOC) fully
- [ ] 5e.2 Read `baml/oideachais_other/tertiary.baml` (79 LOC) fully
- [ ] 5e.3 Write `baml/education/stages/tertiary.baml` containing:
  - All enums: `NFQLevel`, `EQFLevel`, `HEIType`, `EntryPathway`
  - All 10 classes: `MatriculationRequirement`, `CAOCourse`, `QqiFetAward`, `Apprenticeship`, `Programme`, `ApplicationTimeline`, `CAOGradeProfile`, `CoursePointsPrediction`, `MatriculationAudit`, `MatriculationAudit` (no dup)
  - 10 functions (merged from both sources):
    - `ExtractCAOCourseList(page_markdown, year)` (from `tertiary.baml`)
    - `ExtractMatriculationRules(page_markdown, institution)` (from `tertiary.baml`)
    - `ExtractQQIFetAwards(page_markdown)` (from `tertiary.baml`)
    - `ExtractApprenticeshipListings(page_markdown)` (from `tertiary.baml`)
    - `ExtractApplicationTimeline(page_markdown, year)` (from `tertiary.baml`)
    - `EstimateCoursePoints(course, historical_points, applicant_profile)` (from `tertiary.baml`)
    - `AuditMatriculation(institution, course_code, applicant_grades)` (from `tertiary.baml`)
    - `ExtractCAOCourseListFromUrl(page_url, year)` (from `oideachais_other/tertiary.baml`)
    - `ExtractMatriculationRulesFromUrl(page_url, institution)` (from `oideachais_other/tertiary.baml`)
    - `AuditMatriculationStdLib(institution, applicant_grades)` (from `oideachais_other/tertiary.baml`)
- [ ] 5e.4 `git rm baml/tertiary.baml`
- [ ] 5e.5 Validate: `ls baml/tertiary.baml` returns "No such file or directory"

## Phase 6 — Split the mega-file `curriculum_extraction.baml` (1114 LOC)

- [ ] 6.1 Read `baml/curriculum_extraction.baml` (1114 LOC) fully
- [ ] 6.2 Write `baml/education/_shared/education_level.baml` containing the 10 enums:
  - `RelationshipType` (PREREQUISITE_FOR, BUILDS_ON, ASSESSES, RELATED_TO, PART_OF, ENABLES, CONTRASTS_WITH)
  - `DifficultyLevel` (FOUNDATION, ORDINARY, HIGHER, EXTENSION)
  - `EducationLevel` (PRIMARY, JUNIOR_CYCLE, SENIOR_CYCLE, TRANSITION_YEAR)
  - `ExamLevel` (HIGHER, ORDINARY, FOUNDATION, COMMON)
  - `QuestionType` (MULTIPLE_CHOICE, SHORT_ANSWER, LONG_ANSWER, CALCULATION, ESSAY, PRACTICAL, COMPREHENSION, TRANSLATION, AURAL, ORAL)
  - `LeavingCertSubject` (50+ LC subject enum values)
  - `Specialism` (SCIENCES, LANGUAGES, BUSINESS, HUMANITIES, PRACTICAL, ARTS, APPLIED, INTERDISCIPLINARY)
  - `AssessmentComponentType` (WRITTEN, ORAL, AURAL, PRACTICAL, COURSEWORK, CBA, PROJECT, PORTFOLIO)
  - `RubricStyle` (PCLM, SRP, EQUATION_STEPS, KEYWORD_MATCH_DIAGRAM, COMPREHENSION_EXPRESSION, SECTION_B_KEYWORD, DIAGRAM_SKETCH_STEPS, BALANCED_EQUATION_STATE_SYMBOLS, DEFINITION_UNIT_FORMULA, RUBRIC_PCLM_IRISH, LINGUISTIC_PRINCIPLES)
  - `DocumentCategory` (SPECIFICATION, SYLLABUS, MEETING_MINUTES, ASSESSMENT_GUIDELINES, FRAMEWORK, CONSULTATION_DOCUMENT, EXAM_PAPER, MARKING_SCHEME, EXAMINER_REPORT, OTHER)
- [ ] 6.3 Write `baml/education/_shared/strand_outcome.baml` containing the 17 classes:
  - `LearningOutcome`, `Skill`, `SkillExtractionResult`, `RelationshipExtractionResult`, `ExtractedRelationship`
  - `CurriculumSection`, `ExtractedCurriculumDocument`
  - `EnhancedLearningOutcome`, `CurriculumStrand`, `AssessmentComponent`, `AssessmentInfo`, `CurriculumSpecification`
  - `ExamQuestion`, `OutcomeQuestionMapping`, `ExamSection`, `ExamPaper`
  - `MarkingScheme`, `MarkingSection`, `MarkingCriteria`, `MarkingPoint`
  - `ExaminerReport`, `QuestionAnalysis`, `ExamStatistics`
- [ ] 6.4 Write `baml/education/_shared/curriculum_relationships.baml` containing the 4 relationship functions:
  - `ExtractLearningOutcomeRelationships(source_outcome, target_outcomes, subject_context)` (uses `anthropic/claude-sonnet-4-20250514`)
  - `ExtractSkillsFromOutcome(outcome, curriculum_context)` (uses `anthropic/claude-sonnet-4-20250514`)
  - `ExtractCurriculumFromDocument(document_text, subject, level)` (uses `anthropic/claude-sonnet-4-20250514`)
  - `IdentifyPrerequisiteChain(target_outcome, available_outcomes, max_depth)` (uses `anthropic/claude-sonnet-4-20250514`)
- [ ] 6.5 Write `baml/education/_shared/subject_rubric.baml` containing the 4 rubric functions:
  - `ExtractSubjectRubric(text, subject, level, exam_years)`
  - `ScoreEssayAgainstRubric(essay, subject, level, rubric_text)`
  - `CompareMarkingSchemes(year_a, year_b, scheme_a, scheme_b, subject)`
  - `LazyExtractExamPaper(text, subject, year, level)`
  - Plus 5 supporting classes: `SpecialismRubric`, `SubjectRubric`, `RubricScore`, `MarkingSchemeDiff`, `ExtractionBudget`
- [ ] 6.6 Write `baml/education/_shared/document_metadata.baml` containing the 2 document metadata functions:
  - `ExtractAllPdfMetadata(page_markdown, pdf_urls)`
  - `ExtractCurriculumSyllabus(pdf_text)` (uses `LitellmClient`)
- [ ] 6.7 `git rm baml/curriculum_extraction.baml`
- [ ] 6.8 Validate: `ls baml/curriculum_extraction.baml` returns "No such file or directory"
- [ ] 6.9 Validate: `ls baml/education/_shared/` shows 5 files

## Phase 7 — Move the Celtic / Irish language BAML files into `celtic/`

Pure `git mv` operations.

- [ ] 7.1 `git mv baml/gaois/duchas.baml baml/celtic/gaois/duchas.baml`
- [ ] 7.2 `git mv baml/gaois/logainm.baml baml/celtic/gaois/logainm.baml`
- [ ] 7.3 `git mv baml/gaois/tearma.baml baml/celtic/gaois/tearma.baml`
- [ ] 7.4 `git mv baml/gaois/folklore_extraction.baml baml/celtic/gaois/folklore_extraction.baml`
- [ ] 7.5 `rmdir baml/gaois/`
- [ ] 7.6 `git mv baml/celtic_sources.baml baml/celtic/sources.baml`
- [ ] 7.7 `git mv baml/celtic_curriculum.baml baml/celtic/curriculum/celtic_curriculum.baml`
- [ ] 7.8 `git mv baml/morphology.baml baml/celtic/morphology.baml`
- [ ] 7.9 `git mv baml/grammar_patterns.baml baml/celtic/grammar_patterns.baml`
- [ ] 7.10 `git mv baml/mythology_extraction.baml baml/celtic/curriculum/mythology_extraction.baml`
- [ ] 7.11 Validate: `ls baml/celtic_sources.baml baml/celtic_curriculum.baml baml/morphology.baml baml/grammar_patterns.baml baml/mythology_extraction.baml` all return "No such file or directory"
- [ ] 7.12 Validate: `ls baml/gaois/` returns "No such file or directory"

## Phase 8 — Move the generic file-processing BAML files into `processing/`

Pure `git mv` operations.

- [ ] 8.1 `git mv baml/email.baml baml/processing/email.baml`
- [ ] 8.2 `git mv baml/upstream_monitoring.baml baml/processing/upstream_monitoring.baml`
- [ ] 8.3 `git mv baml/cv_extraction.baml baml/processing/cv_extraction.baml`
- [ ] 8.4 `git mv baml/portfolio_extraction.baml baml/processing/portfolio_extraction.baml`
- [ ] 8.5 `git mv baml/linkedin_profile_extraction.baml baml/processing/linkedin_profile_extraction.baml`
- [ ] 8.6 `git mv baml/researchgate_extraction.baml baml/processing/researchgate_extraction.baml` (then fix the `string | null` syntax bug to `string?` — see Phase 8b)
- [ ] 8.7 `git mv baml/artwork_analysis.baml baml/processing/artwork_analysis.baml`
- [ ] 8.8 `git mv baml/author_archive.baml baml/processing/author_archive.baml`
- [ ] 8.9 `git mv baml/circular_extraction.baml baml/processing/circular_extraction.baml`
- [ ] 8.10 `git mv baml/identity_verification.baml baml/processing/identity_verification.baml`
- [ ] 8.11 `git mv baml/audio_extraction.baml baml/processing/audio_extraction.baml`
- [ ] 8.12 `git mv baml/ocr_extraction.baml baml/processing/ocr_extraction.baml`
- [ ] 8.13 `git mv baml/ocr_validation.baml baml/processing/ocr_validation.baml`
- [ ] 8.14 `git mv baml/image_generation.baml baml/processing/image_generation.baml`
- [ ] 8.15 `git mv baml/style_transfer.baml baml/processing/style_transfer.baml`
- [ ] 8.16 `git mv baml/game_content.baml baml/processing/game_content.baml`
- [ ] 8.17 `git mv baml/player_assessment.baml baml/processing/player_assessment.baml`
- [ ] 8.18 `git mv baml/generators.baml baml/processing/generators.baml`
- [ ] 8.19 `git mv baml/culture_extraction.baml baml/processing/culture_extraction.baml`
- [ ] 8.20 `git mv baml/named_entities.baml baml/processing/named_entities.baml`
- [ ] 8.21 `git mv baml/site_analysis.baml baml/processing/site_analysis.baml`
- [ ] 8.22 `git mv baml/official_media.baml baml/processing/official_media.baml`
- [ ] 8.23 `git mv baml/ui_components.baml baml/processing/ui_components.baml`
- [ ] 8.24 `git mv baml/teaching_extraction.baml baml/processing/teaching_extraction.baml`

### Phase 8b — Fix the `researchgate_extraction.baml` syntax bug

- [ ] 8b.1 In `baml/processing/researchgate_extraction.baml`, fix the TypeScript-style `string | null` syntax to valid BAML `string?` (in 2 places: `venue string | null` and `doi string | null`)

## Phase 9 — Delete dead files and directories

- [ ] 9.1 `git rm baml/educational_clients.baml` (0 callers per `ccc search`)
- [ ] 9.2 `git rm baml/curriculum_extraction_0.baml` (BAML 0.x syntax superseded)
- [ ] 9.3 `git rm -r baml/oideachais_other/` (all 5 files were duplicates)
- [ ] 9.4 If `baml/_croilar_src/` still exists: `git rm -r baml/_croilar_src/`
- [ ] 9.5 Validate: `ls baml/educational_clients.baml baml/curriculum_extraction_0.baml baml/oideachas.baml` all return "No such file or directory"
- [ ] 9.6 Validate: `ls -d baml/oideachais_other` returns "No such file or directory"
- [ ] 9.7 Validate: `ls -d baml/_croilar_src` returns "No such file or directory"

## Phase 10 — Move ARCHIVED Celtic BAML files to `_archive/`

Per `openspec/changes/archive-celtic-baml-orphans/` (the 2026-06-24 archived
headers in the files themselves).

- [ ] 10.1 `git mv baml/celtic_linguistics.baml baml/celtic/_archive/celtic_linguistics.baml`
- [ ] 10.2 `git mv baml/cognates.baml baml/celtic/_archive/cognates.baml`
- [ ] 10.3 Validate: `ls baml/celtic_linguistics.baml baml/cognates.baml` both return "No such file or directory"
- [ ] 10.4 Validate: `ls baml/celtic/_archive/` shows 2 files

## Phase 11 — Delete `baml/oideachas.baml`

- [ ] 11.1 Run `ccc search "oideachas\.baml"` — if 0 callers, `git rm baml/oideachas.baml`
- [ ] 11.2 Validate: `ls baml/oideachas.baml` returns "No such file or directory"

## Phase 12 — Validate the complete change

- [ ] 12.1 `ls baml/` shows exactly: 2 client files at root + `cli.py` + `shared/` + 3 cluster sub-directories (`education/`, `celtic/`, `processing/`)
- [ ] 12.2 `baml-cli generate` succeeds (or at minimum `baml-cli check` succeeds)
- [ ] 12.3 `ccc search "oideachais_other"` returns 0 hits in `baml/`
- [ ] 12.4 `ccc search "ExtractAistearFrameworkFromUrl"` returns 1 hit in `education/stages/aistear.baml`
- [ ] 12.5 `ccc search "GenerateMathQuestPack"` returns 1 hit in `education/subjects/qpack_mathematics.baml`
- [ ] 12.6 `ccc search "celtic_linguistics.baml"` returns 1 hit in `celtic/_archive/celtic_linguistics.baml`
- [ ] 12.7 `python -c "from cianfhoghlaim.baml_client import b; print(len([f for f in dir(b) if not f.startswith('_')]))"` prints >= 250
- [ ] 12.8 `openspec validate baml-reorganize-by-cluster --strict` passes