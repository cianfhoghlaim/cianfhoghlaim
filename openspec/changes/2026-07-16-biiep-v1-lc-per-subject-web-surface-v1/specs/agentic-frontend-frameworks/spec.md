# `agentic-frontend-frameworks` MODIFIED — Per-subject Convex + TanStack interactive web surface for the 6 BIEP v1 LC subjects

## ADDED Requirements

### Requirement: Per-subject Convex + TanStack interactive web surface for the 6 BIEP v1 LC subjects

The system SHALL ship a per-subject Convex + TanStack interactive web
surface for each of the 6 BIEP v1 LC subjects: Mathematics, Chemistry,
Geography, Gaeilge, English, Computer Science (per the user's locked
plan; Applied Maths + History are out of scope).

For each of the 6 subjects, the system SHALL ship:
- 5 per-subject TanStack Start route files at
  `apps/cianfhoghlaim-leaving-cert/apps/web/src/routes/en/subjects/<subject>/`
  named `index.tsx`, `syllabus.tsx`, `exam-papers.tsx`,
  `marking-schemes.tsx`, `study-plan.tsx` (30 files total).
- 6 per-subject Convex files at `convex/<subject>/` named
  `schema.ts`, `createSession.ts`, `getSession.ts`,
  `updateSession.ts`, `generateStudyPlan.ts`,
  `discussExamPaper.ts` (36 files total).
- 1 per-subject BAML backend file at
  `baml/education/web/<subject>_web.baml` exposing the functions
  `WebStudyPlan`, `WebExamPaperDiscussion`, and
  `WebMarkingSchemeExplanation` (6 files total).

Total: 30 + 36 + 6 = 72 per-subject source files.

The per-subject Convex `generateStudyPlan` action SHALL call into the
per-subject BAML `WebStudyPlan` function. The per-subject Convex
`discussExamPaper` action SHALL call into the per-subject BAML
`WebExamPaperDiscussion` function. The per-subject BAML backend files
SHALL delegate to the existing per-subject foundation at
`baml/education/subjects/qpack_<subject>.baml`.

Per-subject route trees are added alongside (not replacing) the
existing flat `apps/.../routes/en/subjects/<subject>.tsx` files so
existing book-marks resolve to the new per-subject directories.

#### Scenario: Mathematics per-subject study plan generation

- **GIVEN** the user is on `/en/subjects/mathematics/study-plan`
- **WHEN** they press "Start studying" with `weeksUntilExam=12`,
  `targetLevel="hl"`, `language="en"`
- **THEN** the `convex/mathematics/createSession.ts` mutation runs and
  returns a session id
- **AND** the `convex/mathematics/generateStudyPlan.ts` action runs
  and calls `b.WebStudyPlan(subject="mathematics", ...)`
- **AND** the `WebStudyPlan` function returns a
  `MathematicsWebStudyPlanResponse` (bilingual EN+GA) with at least 12
  weeks + 3-5 milestones
- **AND** the response is persisted to the `study_plans` table by the
  `insertStudyPlan` internal mutation
- **AND** the UI re-renders the per-subject plan in real time via the
  Convex subscription

#### Scenario: Chemistry per-subject exam paper discussion

- **GIVEN** the user is on `/en/subjects/chemistry/exam-papers`
- **WHEN** they click a past paper question for the 2024 LC Chemistry
  HL paper
- **THEN** the `convex/chemistry/discussExamPaper.ts` action runs and
  calls `b.WebExamPaperDiscussion(subject="chemistry", paper_year=2024,
  paper_level="LC_HL", paper_language="EN", question_text="...")`
- **AND** the `WebExamPaperDiscussion` function returns a
  `ChemistryWebExamPaperDiscussionResponse` with a PCLM marking-scheme
  explanation + a model answer outline + common student mistakes +
  follow-up questions
- **AND** the response is persisted to the
  `exam_paper_discussions` table

#### Scenario: Geography per-subject marking scheme explanation

- **GIVEN** the user is on `/en/subjects/geography/marking-schemes`
- **WHEN** they select the 2023 LC Geography OL paper
- **THEN** the per-subject BAML `WebMarkingSchemeExplanation` function
  (at `baml/education/web/geography_web.baml`) returns a
  `GeographyWebMarkingSchemeExplanationResponse` with sections +
  questions + PCLM patterns
- **AND** the response renders in the UI without writing to Convex
  (this function is read-only)

#### Scenario: Gaeilge per-subject bilingual handling

- **GIVEN** the user is on `/ga/subjects/gaeilge` (the Irish-language
  mirror of the Gaeilge BIEP page)
- **WHEN** they press "Start studying" with `language="ga"`
- **THEN** the per-subject Convex action accepts the Gaeilge language
  flag
- **AND** the per-subject BAML backend responds in Gaeilge
  (or bilingual EN+GA where Gaeilge is the primary)
- **AND** the `study_plans.plan_json` row is tagged `language="ga"`

#### Scenario: English per-subject session progress

- **GIVEN** the user has an active English study session
- **WHEN** they complete a syllabus topic on
  `/en/subjects/english/syllabus`
- **THEN** the `convex/english/updateSession.ts` mutation runs with
  `messageCountDelta=1`
- **AND** the session's `message_count` and `last_active_at` are
  patched in the `study_sessions` table

#### Scenario: Computer Science per-subject BAML delegation

- **GIVEN** the `baml/education/web/computer_science_web.baml` backend
- **WHEN** any of `WebStudyPlan`, `WebExamPaperDiscussion`, or
  `WebMarkingSchemeExplanation` is invoked
- **THEN** the function delegates to the foundation at
  `baml/education/subjects/qpack_computer_science.baml` for the
  per-subject syllabus + past-paper grounding
