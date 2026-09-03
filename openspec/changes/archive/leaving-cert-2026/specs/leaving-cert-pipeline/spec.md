# Spec Deltas: leaving-cert-pipeline

## ADDED Requirements

### Requirement: Per-Subject Asset Graph

The system MUST produce, for each Leaving Certificate subject, a partitioned
Dagster asset graph that ingests SEC exam papers, NCCA syllabus PDFs, and
marking schemes, then extracts structured data via BAML and generates
analysis via MiniMax M3.

#### Scenario: Operator runs the per-subject pipeline for Mathematics

- **GIVEN** the `leaving_cert_mathematics` job is defined in `definitions.py`
- **WHEN** the operator triggers the job via Dagster
- **THEN** the job MUST materialise these assets in dependency order: `mathematics_syllabus_pdf` → `mathematics_syllabus_extracted` → `mathematics_past_papers` → `mathematics_past_papers_extracted` → `mathematics_marking_schemes` → `mathematics_marking_schemes_extracted` → `mathematics_topic_frequency` → `mathematics_study_prioritisation` → `mathematics_exam_layout_tips` → `mathematics_portal_page_payload`
- **AND** each asset MUST be partitioned on `subject × paper × year × language`
- **AND** the BAML extraction MUST use validated schemas in `baml_src/`

#### Scenario: The 7 subjects are ingested in order of exam date

- **GIVEN** the 7 priority subjects (Mathematics, Irish, Biology, French, History, Business, Construction Studies) have their exams between Fri 5 Jun and Thu 11 Jun 2026
- **WHEN** the build sequence executes
- **THEN** Mathematics SHALL be built first (D-3: Fri 5 Jun)
- **AND** Irish SHALL be built second (D-0: Mon 8 Jun)
- **AND** the remaining 5 subjects SHALL follow in order: Biology, French+History, Business+Construction

### Requirement: Per-Year Snapshot + Rolling Aggregator

The system MUST preserve per-year snapshots of each subject's analysis so that
a 2026 student sees 2026 analysis and a 2025 student sees 2025 analysis, while
also maintaining a cross-year rolling aggregator for long-run trend queries.

#### Scenario: 2026 student views Mathematics analysis

- **GIVEN** the 2026 Mathematics analysis has been materialised
- **WHEN** the 2026 public page loads
- **THEN** the page MUST show the 2026 per-year snapshot
- **AND** a "see last year's analysis" link MUST navigate to the 2025 snapshot

#### Scenario: Cross-year trend query is executed

- **GIVEN** the rolling aggregator table `topic_frequency_2017_2025` exists
- **WHEN** a query asks "which topics are asked most frequently across years"
- **THEN** the result MUST aggregate over all available years (2017-2025)
- **AND** the result MUST be weighted by mark allocation per year

### Requirement: SEC Examination PDF Scraping

The system MUST ingest SEC examination PDFs using the existing Playwright-native
`?fp=` URL scraper, with Stagehand as the LLM fallback when Playwright returns
no real materials.

#### Scenario: New exam paper PDFs are published on examinations.ie

- **GIVEN** SEC publishes new Leaving Cert exam papers for a subject
- **WHEN** the `leaving_cert_annual` sensor detects the new publication
- **THEN** the `?fp=` URL scraper MUST extract the obfuscated PDF URLs
- **AND** the PDFs MUST be downloaded and stored in `cianfhoghlaim-leaving-cert` R2 bucket
- **AND** the BAML extraction MUST produce structured question-topic-mark data

### Requirement: MiniMax M3 Analysis Layer

The system MUST use MiniMax M3 via the LiteLLM gateway for the analysis layer
(syllabus summary, study prioritisation, exam layout tips, and the CopilotKit
chat agent). DeepSeek V4 Pro MUST be used for the bulk BAML extraction.

#### Scenario: MiniMax M3 generates study prioritisation for Biology

- **GIVEN** the BAML-extracted past exam data is available for Biology
- **WHEN** the study prioritisation asset runs
- **THEN** MiniMax M3 MUST generate a ranked list of topics by `expected_marks ÷ hours_of_study`
- **AND** the output MUST be stored as a JSON payload in DuckLake/MotherDuck
- **AND** Langfuse MUST trace the M3 call for cost tracking

### Requirement: Annual Refresh Sensor

The system MUST provide a `leaving_cert_annual` Dagster sensor that detects new
syllabus PDFs in R2 and new exam papers on examinations.ie, then triggers the
extraction + analysis pipeline for changed subjects only.

#### Scenario: NCCA publishes a new syllabus post-June 2026

- **GIVEN** a new syllabus PDF is uploaded to `r2://cianfhoghlaim-leaving-cert/syllabus/{subject}/2027.pdf`
- **WHEN** the annual sensor detects the new file
- **THEN** the extraction pipeline MUST run for that subject only
- **AND** the 2027 per-year snapshot MUST be created without disturbing the 2026 snapshot
- **AND** the rolling aggregator MUST be extended to include 2027

### Requirement: Irish-Language Content Review

The system MUST flag MiniMax M3-generated Irish-language content for human
review before publishing.

#### Scenario: MiniMax M3 generates Irish exam layout tips

- **GIVEN** the M3 model generates tips in Irish
- **WHEN** the output is written
- **THEN** the content MUST be tagged with `ai-generated` and `language: ga`
- **AND** the content MUST not be visible on the public page until a human
  reviewer marks it as `reviewed: true`
