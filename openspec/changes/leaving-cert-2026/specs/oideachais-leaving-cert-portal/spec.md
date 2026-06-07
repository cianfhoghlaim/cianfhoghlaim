# Spec Deltas: oideachais-leaving-cert-portal

## ADDED Requirements

### Requirement: Per-Subject Public Page

The system SHALL expose a public page at `oideachais.cianfhoghlaim.ie/leaving-cert/{subject}/`
for each of the 7 priority Leaving Certificate subjects, with the analysis
rendered via MotherDuck/DuckDB queries and original PDFs served from Cloudflare R2.

#### Scenario: Student navigates to the Mathematics page

- **GIVEN** the Mathematics pipeline has been run and the portal page payload exists
- **WHEN** a student navigates to `oideachais.cianfhoghlaim.ie/leaving-cert/mathematics`
- **THEN** the page SHALL render these sections in order: Hero (subject + exam countdown), Syllabus analysis, Past exam analysis (year-by-year table), Marking scheme patterns, Topic prioritisation (sorted by marks-per-study-hour), Exam layout tips, CopilotKit chat panel, Original PDFs tab
- **AND** the page SHALL use the `@croilar/ui` component library (Card, Tabs, Table, Accordion, Badge, Progress, Separator, Skeleton)
- **AND** the page SHALL load from MotherDuck for public reads and from R2 signed URLs for the PDF viewer

#### Scenario: Student views the Irish page

- **GIVEN** the Irish page is bilingual (en/ga)
- **WHEN** a student navigates to `oideachais.cianfhoghlaim.ie/leaving-cert/irish`
- **THEN** the page SHALL render Irish-language content tagged as `language: ga`
- **AND** Cluastuiscint audio links SHALL be listed as a separate section
- **AND** M3-generated Irish content SHALL NOT be visible until reviewed

### Requirement: CopilotKit AG-UI Chat Panel

The system SHALL provide a CopilotKit chat panel on every subject page, scoped
to that subject's extracted corpus, with tools that link to specific R2 PDFs.

#### Scenario: Student asks about a Mathematics topic

- **GIVEN** the student is viewing the Mathematics page
- **WHEN** the student types "how do I solve integration by substitution" in the chat
- **THEN** MiniMax M3 SHALL respond with a topic-specific answer drawn from the extracted syllabus + past papers
- **AND** the chat panel SHALL expose a `open_pdf` tool that returns a signed R2 URL to the relevant PDF

### Requirement: Per-Year Snapshot Navigation

The system SHALL support per-year snapshot navigation: the current year's
analysis is the default, with a link to the previous year's analysis.

#### Scenario: 2026 Mathematics page loads

- **GIVEN** a 2025 Mathematics snapshot exists
- **WHEN** the 2026 page loads
- **THEN** the page SHALL show the 2026 analysis as the default
- **AND** a link "See last year's analysis" SHALL navigate to the 2025 snapshot

### Requirement: Original PDFs Hosted in R2

The system SHALL host original exam papers, marking schemes, and syllabus PDFs
in the Cloudflare R2 bucket `cianfhoghlaim-leaving-cert` with signed URLs for
the per-subject page's PDF viewer.

#### Scenario: Student opens an exam paper PDF

- **GIVEN** the student clicks "View Paper 1 (2025)" on the Mathematics page
- **WHEN** the TanStack route resolves the PDF viewer
- **THEN** the page SHALL generate a signed R2 URL to `r2://cianfhoghlaim-leaving-cert/exam-papers/mathematics/2025-paper-1.pdf`
- **AND** the PDF SHALL render in an embedded viewer (react-pdf or pdf.js)
- **AND** the signed URL SHALL expire after 1 hour

### Requirement: Hybrid Access Policy

The system SHALL serve analysis publicly (anonymous read) and defer the
interactive personal study plan to a future change.

#### Scenario: Anonymous student views the public page

- **GIVEN** the student is not signed in
- **WHEN** they navigate to any `/leaving-cert/{subject}/` page
- **THEN** they SHALL see all 7 sections (Hero through original PDFs)
- **AND** they SHALL be able to interact with the CopilotKit chat without signing in
- **AND** there SHALL be no personal study plan section (deferred to a future change)

### Requirement: Build Order by Exam Date

The system SHALL build subjects in the order of their exam dates, with the
earliest-exam subject (Mathematics, Fri 5 Jun) built first.

#### Scenario: Build sequence begins

- **GIVEN** the 7 subjects have exam dates spanning Fri 5 Jun to Thu 11 Jun
- **WHEN** the build begins
- **THEN** Mathematics SHALL be the first subject built (D-3)
- **AND** Irish SHALL be the second (D-0)
- **AND** Biology SHALL be the third (D+1)
- **AND** French and History SHALL be the fourth set (D+2)
- **AND** Business and Construction Studies SHALL be the fifth set (D+3)
