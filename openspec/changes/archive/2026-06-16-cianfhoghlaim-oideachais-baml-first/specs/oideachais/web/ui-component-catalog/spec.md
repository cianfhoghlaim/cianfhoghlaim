# Spec Delta — UI Component Catalog (28 components, BAML-driven)

## ADDED Requirements

### Requirement: Per-Stage UI Components
The system SHALL provide 28 React components, one per `UIComponentKind` enum value, all bilingual (EN/GA aware), all backed by the BAML-extracted data.

#### Scenario: Aistear Components
- **GIVEN** the Aistear stage is loaded
- **WHEN** the user navigates to `/en/stages/aistear`
- **THEN** the page renders:
  - `<AistearThemesGrid themes={themes}>` — a 4-column grid (Well-being, Identity & Belonging, Communicating, Exploring & Thinking) with each theme's principles
  - `<NaionraMap points={naionra}>` — a choropleth of Ireland with naíonra markers; bilingual popovers
  - `<ParentTip tip_en={...} tip_ga={...}>` — a flip-card widget with daily parenting advice

#### Scenario: Primary Components
- **GIVEN** the Primary stage is loaded
- **WHEN** the user navigates to `/en/stages/primary`
- **THEN** the page renders:
  - `<PrimaryStrandTree strands={...}>` — a nested expandable tree (12 areas × 4 stages × ~6 strands × ~10 outcomes)
  - `<StageOutcomesMapper stage={...}>` — a chip grid showing which Stage 4 outcomes bridge to which Aistear learning goals

#### Scenario: Junior Cycle Components
- **GIVEN** the Junior Cycle stage is loaded
- **WHEN** the user navigates to `/en/stages/junior_cycle`
- **THEN** the page renders:
  - `<JCCBATimeline tasks={...}>` — a horizontal date strip of CBA-1 / CBA-2 timing per subject
  - `<JCShortCourseBadge course={...}>` — a chip with the 16 short courses
  - `<L2LPSpecialist>` — a Level 1/2 Learning Programme badge for SEN students

#### Scenario: Senior Cycle Components
- **GIVEN** the Senior Cycle stage is loaded
- **WHEN** the user navigates to `/en/stages/senior_cycle`
- **THEN** the page renders:
  - `<SCExamPaperCard paper={...} onExtract={...}>` — year/level/paper card with a "Extract" button (lazy BAML)
  - `<SCMarkingSchemePanel scheme={...}>` — per-question marks + rubric descriptors
  - `<SCRubricDescriptorList descriptors={...}>` — bullet list with weightings
  - `<SCPracticeEssayEditor rubric={...} onSubmit={...}>` — essay editor + score display
  - `<SCPointsCalculator>` — H1-H8, O1-O8, H6+25 bonus math
  - `<SCMatriculationAuditor>` — grade-vs-requirement table

#### Scenario: Tertiary Components
- **GIVEN** the Tertiary stage is loaded
- **WHEN** the user navigates to `/en/stages/tertiary`
- **THEN** the page renders:
  - `<TertiaryCAOCourseCard course={...}>` — institution, points, requirements
  - `<TertiaryQQILadder fet_award={...}>` — vertical ladder showing PLC → CAO routes
  - `<TertiaryApprenticeshipCard programme={...}>` — consortia + duration + NFQ level
  - `<TertiaryApplicationTimeline timeline={...}>` — horizontal date strip
  - `<TertiaryCAOPointsTrend course={...} profiles={...}>` — line chart of last 5 years

#### Scenario: Cross-Cutting Components
- **GIVEN** any page
- **WHEN** it renders
- **THEN** the page contains:
  - `<TranslationToggle locale="en|ga" />` in the header
  - `<BilingualBlock en={...} ga={...}>` for any human-readable concept (inline toggle)
  - `<CitationChip source="https://..." />` for every BAML-extracted fact
  - `<KeywordCloud keywords={...} source="baml_extraction" />` for the extracted concepts
  - `<LearningOutcomePill code={...} text={...} />` for compact outcome references

### Requirement: Component Catalog (Admin)
The system SHALL provide a `/en/admin/components` route (and `/ga/admin/components` mirror) that lists the `ui_component_suggestions` LanceDB table.

#### Scenario: Component Catalog Browse
- **GIVEN** a user with `admin` role visits `/en/admin/components`
- **WHEN** the page loads
- **THEN** the SPA queries the `ui_component_suggestions` LanceDB table
- **AND** displays a list of all `UIComponentSuggestion` records, grouped by `kind`
- **AND** each card shows: `title_en`, `title_ga`, `priority`, `route_slug`, `keywords[]`, `data_source`
- **AND** clicking a card opens a side panel with the BAML extraction provenance
