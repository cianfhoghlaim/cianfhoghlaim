# British-Isles Education Pipeline Capability

## Purpose

`british-isles-education-pipeline` (BIEP) is the flagship
ingestion+extraction+embedding+orchestration+analytics capability of the
Cianfhoghlaim platform. v1 covers the 6 priority Irish Leaving
Certificate subjects (Mathematics, Chemistry, Geography, Gaeilge,
English, Computer Science) plus the cross-cutting `gov.ie` education
circulars stream.

The corresponding source code lives at:

- `cianfhoghlaim/dlt/british_isles/` (NCCA + SEC + gov.ie DLT sources)
- `cianfhoghlaim/baml/education/lc_extraction/*.baml` (the BAML extraction schemas)
- `cianfhoghlaim/cocoindex/chemistry_embedding.py` + 5 sibling per-subject CocoIndex flows
- `cianfhoghlaim/orchestration/defs/2_materials/lc_extraction/` (Dagster lc5/lc6 assets)
- `cianfhoghlaim/notebooks/leaving_cert/` (per-subject marimo notebooks)
- `motherduck:` (`md:oideachais`) as the analytics surface (4 Dives + 1 daily Flight)

## Background

The platform has been ingesting education content from NCCA and SEC
since 2026-03 (the pre-v4 `oideachais-pipeline`). v1 brings the
6 priority subjects to fully-runnable end-to-end pipelines and adds
`gov.ie` education circulars as the cross-cutting ingestion stream.
Cross-nation extension (Scotland / Wales / England / NI / Isle of Man
/ Crown Dependencies) is deferred to v2 and explicitly out of scope for
this spec.

## Requirements

### Requirement: 6 Irish LC subjects end-to-end

The system SHALL provide NCCA + SEC + gov.ie DLT sources, BAML
extraction (lc5 + lc6), 6 v1 CocoIndex flows (one per subject), 42+
Dagster assets (`lc5_<subject>_documents` + `lc5_<subject>_extract` +
`lc6_<subject>_marking_schemes` + ... + the 2 gov.ie circular assets),
6 per-subject marimo notebooks + 1 cross-subject competency notebook,
for the 6 priority subjects: Mathematics, Chemistry, Geography,
Gaeilge, English, Computer Science.

#### Scenario: mise run dagster:oideachais → materialize all

- **WHEN** a teacher clicks "Materialize all" in the Dagster UI for the 6-subject pipeline
- **THEN** the 42+ lc5/lc6 assets materialise within minutes
- **AND** the 6 marimo notebooks show real data via `mo.sql(engine=md:oideachais)`
- **AND** the per-subject LanceDB `oideachais.lc.<subject>.<level>_<lang>` tables are populated

#### Scenario: gaeilge-only syllabuses (no English sibling)

- **GIVEN** Gaeilge is taught through Irish only (no `en/`-sibling per syllabus)
- **WHEN** the BAML extraction runs
- **THEN** the system SHALL extract Ga-classified records only
- **AND** not raise a missing-English error

### Requirement: gov.ie education circulars ingestion

The system SHALL ingest `gov.ie` education circulars via a DLT source at
`cianfhoghlaim/dlt/british_isles/ie/gov_ie_circulars.py`, extract via
BAML `circular_extraction.baml`, embed via the 7th v1 CocoIndex App
`government_circulars`, and surface via a dedicated MotherDuck Dive.

#### Scenario: New circular arrives

- **WHEN** the gov.ie RSS monitor detects a new circular
- **THEN** the BAML `ClassifyCircular` function is invoked
- **AND** the extracted record lands in `md:oideachais.education.ie.circulars`
- **AND** the `governance_circulars` CocoIndex App fires within the 60-second live-update window

### Requirement: Daily MotherDuck Flight for BAML backfill

The system SHALL schedule a daily MotherDuck Flight `lc_pdf_sync_flight`
that re-runs BAML extraction on any new PDFs landed in
`s3://garage/oideachais/leaving_cert/<subject>/<lang>/<year>/<file>.pdf`.

#### Scenario: PDF lands in Garage S3

- **WHEN** a new PDF is written to `s3://garage/oideachais/leaving_cert/mathematics/en/2026/Q1.pdf`
- **THEN** the daily Flight picks it up within 24h
- **AND** the corresponding lc5/lc6 rows appear in `md:oideachais.leaving_cert.mathematics`

### Requirement: Cross-nation extension deferred to v2

The system SHALL NOT (in v1) ingest Scotland (SQA), Wales (WJEC),
England (AQA/OCR/Edexcel), Northern Ireland (CCEA), Isle of Man,
Jersey, or Guernsey curricula. These are scoped for the separate v2
change and are explicitly out of scope for this spec.

#### Scenario: v2 boundary

- **WHEN** a developer queries the v1 BIEP for Scottish curriculum data
- **THEN** the system returns an empty result with the message
  "deferred to v2; cross-nation extension is the next phase"

### Requirement: 4 MotherDuck Dives (analytics layer)

The system SHALL provide 4 live MotherDuck Dives:

1. `lc_syllabus_topics` — topic coverage per subject
2. `lc_exam_paper_difficulty` — Bloom's taxonomy distribution per year
3. `lc_marking_complexity` — mark-allocation patterns per question
4. `gov_circulars_archive` — chronological archive with topic classification

#### Scenario: BIEP Dive analytics

- **WHEN** a teacher opens the `lc_syllabus_topics` Dive
- **THEN** the chart shows topic counts grouped by subject
- **AND** the data updates within 24h of new BAML extractions

## Cross-references

- [`oideachais-pipeline`](../oideachais-pipeline/spec.md) — the parent capability (5 education stages + leabharlann corpus)
- [`agent-platform-cluster`](../agent-platform-cluster/spec.md) — the 8-stack substrate (MotherDuck + Dagster + LiteLLM + Langfuse)
- [`ncca-leaving-cert-root-pdfs`](../ncca-leaving-cert-root-pdfs/spec.md) *(merged into oideachais-pipeline)* — the 5 NCCA root-level programme PDFs
- [`apple-photos-ingestion`](../apple-photos-ingestion/spec.md) — the 5th leabharlann corpus, sharing the same CocoIndex v1 pattern
- [`motherduck-dives`](../../.agents/skills/motherduck-create-dive/SKILL.md) — the 4 Dive authoring model

## Migrated from: *(none)*
