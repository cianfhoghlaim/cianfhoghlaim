## ADDED Requirements

### Requirement: 8 NCCA Junior Cycle subjects at full scope

The system SHALL provide full BAML + CocoIndex + Marimo + ADK coverage
for the 8 NCCA Junior Cycle subjects (ages 12-15): Mathematics,
English, Gaeilge, Science, Geography, History, CSPE (Civic, Social,
Political Education), SPHE (Social, Personal, Health Education).

The reason: per the user's choice on open question Q4, the 8 NCCA
Junior Cycle subjects are in scope for Mega-3. Each subject gets:
- 1 BAML function in the `junior_cycle_template.baml` (with `{% if subject == "x" %}` conditional)
- 1 CocoIndex App (lands in Mega-3b)
- 1 ADK agent (`jc_subject_agent`)
- 1 A2UI surface (lands in Mega-3b)

#### Scenario: Each JC subject has full coverage across all 4 packages

- **GIVEN** the 8 NCCA Junior Cycle subjects
- **WHEN** the operator inspects the 4-stage plane dashboard
- **THEN** each subject appears in:
 - `junior_cycle_template.baml` as a `{% if subject == "JC-<SUBJECT>" %}` block
 - `cocoindex/biep_parity/ireland_jc_factory.py` (per Mega-3b)
 - `notebooks/19_junior_cycle_pipeline_dashboard.py` (per Mega-3c)
 - `agents/adk/jc_subject_agent.py` (per this change)
- **AND** each subject has a unique NCCA LO code prefix
  (e.g., `JC-MATH-LO-NNN` for JC Mathematics)

#### Scenario: Junior Cycle template covers 18 subjects

- **GIVEN** the 18 NCCA Junior Cycle subjects in the existing
  `JuniorCycleSubjectSlug` enum (English, Gaeilge, Mathematics,
  Irish_History, Geography, Science, Business_Studies, French,
  German, Spanish, Italian, Home_Economics, Music, Art, Technology,
  Engineering, Graphics, Wood_Technology)
- **WHEN** `mise run baml:generate` runs
- **THEN** the `junior_cycle_template.baml` covers the 8 priority
  subjects (Mathematics, English, Gaeilge, Science, Geography,
  History, CSPE, SPHE) via `{% if %}` conditionals
- **AND** the remaining 10 subjects are deferred to a follow-up
  change

### Requirement: BIEP v3 lineage viewer SSE streaming

The system SHALL expose a Server-Sent Events (SSE) streaming endpoint
at `/api/lineage/stream` that streams BAML `@@stream.done` outputs
from the 5 lc6 extraction functions to the BIEP v3 lineage viewer
in real-time.

The reason: per the 2026-04-07 SSE Streaming demo, SSE streaming
gives the lineage viewer real-time updates as BAML extraction
progresses through the 5 lc6 stages (curriculum, exam layout,
marking scheme, cross-linguistic, syllabus diagram).

#### Scenario: SSE endpoint streams BAML extraction progress

- **GIVEN** the operator starts a BAML extraction pipeline for an
  NCCA PDF
- **WHEN** the lineage viewer opens
  `/api/lineage/stream?source_pdf=<path>`
- **THEN** the endpoint streams `data: { stage: "extract_curriculum",
  status: "in_progress", progress: 0.25 }` events as the extraction
  progresses
- **AND** the final event has
  `status: "done", result: <CurriculumSyllabus>, lineage: <LineageTrace>`

### Requirement: BIEP v3 BAML extraction → Dagster asset chain

The system SHALL wire the 5 lc6 BAML functions
(`ExtractCurriculumSyllabus`, `ExtractExamPaperLayout`,
`ExtractMarkingScheme`, `ExtractCrossLinguistic`,
`ExtractSyllabusDiagram`) into the 42 Dagster assets at
`orchestration/defs/2_materials/england_education/` so each asset
materialization triggers the corresponding BAML extraction.

#### Scenario: Every Dagster asset calls BAML

- **WHEN** the operator runs `mise run dagster:asset-materialize --select "*england_education"`
- **THEN** each of the 42 England education Dagster assets
  materialises by calling at least 1 BAML function via
  `BAMLFunctionTool`
- **AND** the per-asset lineage metadata includes the BAML function
  name + the extraction confidence

### Requirement: BIEP v3 BAML Collector integration

The system SHALL wire the BAML `Collector` (per the
`meaisinfhoghlaim-ocr-htr` spec) into the 7 BIEP CocoIndex v1 flows
so every BAML extraction emits a Langfuse trace + a BAML `Collector`
record.

#### Scenario: Every BAML extraction emits a Collector record

- **WHEN** the operator runs the BIEP v3 extraction pipeline
- **THEN** every BAML function call emits:
 - 1 Langfuse trace (via the `LitellmClient`)
 - 1 BAML `Collector` record (via the `baml_client.collector.Collector` API)
- **AND** the `stedding/sync-reports/baml-{date}.md` report shows the
  Collector count matches the BAML function call count