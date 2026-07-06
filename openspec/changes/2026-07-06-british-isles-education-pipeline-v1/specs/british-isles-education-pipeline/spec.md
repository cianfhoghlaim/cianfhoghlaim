## ADDED Requirements

### Requirement: NCCA syllabus corpus for 6 LC subjects

The system SHALL crawl `ncca.ie` for the 6 LC subjects (Mathematics,
Chemistry, Geography, Gaeilge, English, Computer Science) in both English
and Gaeilge via `cianfhoghlaim/dlt/british_isles/ireland/education/ncca.py`.

The system SHALL partition the crawl by `(cycle="senior_cycle", subject, language)`.

The system SHALL honour `USE_LOCAL_SCRAPES=true` to fall back to
`stedding/ingest_queue/ncca.ie/` when the network is unavailable.

#### Scenario: NCCA crawl succeeds for mathematics EN
- **WHEN** the NCCA DLT source is materialized with
  `subject="mathematics", language="en"`
- **THEN** at least 1 syllabus row exists in
  `md:oideachais.leaving_cert.mathematics_syllabus` within 5 minutes

#### Scenario: NCCA crawl fails on gaeilge + falls back to local cache
- **WHEN** the network is unavailable AND `USE_LOCAL_SCRAPES=true`
- **THEN** the source reads from `stedding/ingest_queue/ncca.ie/gaeilge/`
  and produces the same rows

### Requirement: SEC examination papers + marking schemes for 6 LC subjects

The system SHALL crawl `examinations.ie` for the 6 LC subjects' exam
papers + marking schemes (1990-2026) via
`cianfhoghlaim/dlt/british_isles/ireland/education/examinations.py`.

The system SHALL partition the crawl by `(subject, year, language, paper_kind)`
where `paper_kind ∈ {syllabus, paper, marking}`.

The system SHALL honour `USE_LOCAL_SCRAPES=true` to fall back to
`stedding/ingest_queue/examinations.ie/`.

#### Scenario: SEC crawl produces exam papers for chemistry
- **WHEN** the SEC source is materialized with
  `subject="chemistry", year=2024, language="en", paper_kind="paper"`
- **THEN** at least 1 paper row exists in
  `md:oideachais.leaving_cert.chemistry_papers` for that partition

#### Scenario: SEC coverage check passes
- **WHEN** the `sec_paper_year_coverage` asset_check runs
- **THEN** it asserts >=1 paper per subject per year for the last 5 years

### Requirement: gov.ie education circulars

The system SHALL crawl `gov.ie/en/circulars` and `gov.ie/ga/ciorcláin`
for DES / NCCA / SEC / DoE circulars via
`cianfhoghlaim/dlt/british_isles/ireland/education/gov_ie_circulars.py`.

The system SHALL extract structured data via `b.ExtractCircular` from
`baml/processing/circular_extraction.baml`.

The system SHALL link each circular to the relevant NCCA syllabus(es)
via `b.LinkCircularToSyllabus`.

The system SHALL partition the crawl by `(dept, year, language)`.

#### Scenario: gov.ie DES circular extracted
- **WHEN** the gov.ie source is materialized with `dept="DES", year=2024, language="en"`
- **THEN** at least 1 circular row exists in
  `md:oideachais.government.circulars` within 5 minutes

#### Scenario: Circular linked to syllabus
- **WHEN** a circular references an NCCA syllabus in its body
- **THEN** `b.LinkCircularToSyllabus` produces a row in
  `md:oideachais.government.circular_to_syllabus`

### Requirement: PDF download to Garage S3

The system SHALL download the crawled NCCA + SEC + gov.ie PDFs to
`s3://garage/oideachais/leaving_cert/<subject>/<lang>/<year>/<filename>.pdf`
via `cianfhoghlaim/dlt/filesystem/pdf_download_source.py`.

The system SHALL honour `USE_LOCAL_SCRAPES=true` for cached downloads
(reads from `cianfhoghlaim/leaving_certificate/<subject>/` and uploads
to Garage S3 if missing).

#### Scenario: PDF download succeeds
- **WHEN** a new NCCA syllabus PDF is detected in the lakehouse
- **THEN** within 24 hours the PDF exists at
  `s3://garage/oideachais/leaving_cert/<subject>/<lang>/<year>/<file>.pdf`

#### Scenario: Local PDF upload
- **WHEN** a PDF exists in `cianfhoghlaim/leaving_certificate/<subject>/`
  AND does not exist in Garage S3
- **THEN** the daily `daily_lc_pdf_download` asset uploads it

### Requirement: BAML extraction to DuckLake

The system SHALL extract the 5 document kinds (curriculum syllabus, exam
paper, marking scheme, cross-linguistic concept, syllabus diagram) via the
5 functions in `baml/education/lc_extraction/*.baml`.

The system SHALL extract circular data via `b.ExtractCircular` and
`b.LinkCircularToSyllabus` from `baml/processing/circular_extraction.baml`.

The system SHALL write the extracted rows to DuckLake tables:
- `md:oideachais.leaving_cert.<subject>_syllabus`
- `md:oideachais.leaving_cert.<subject>_papers`
- `md:oideachais.leaving_cert.<subject>_marking`
- `md:oideachais.leaving_cert.<subject>_topics`
- `md:oideachais.leaving_cert.<subject>_cross_ling`
- `md:oideachais.leaving_cert.<subject>_diagrams`
- `md:oideachais.government.circulars`
- `md:oideachais.government.circular_to_syllabus`

#### Scenario: Chemistry syllabus extracted via BAML
- **WHEN** a chemistry syllabus PDF is in `lc6_chemistry_ingested`
- **THEN** `lc6_chemistry_syllabus_extracted` produces >=1 row in
  `md:oideachais.leaving_cert.chemistry_syllabus` within 10 minutes

#### Scenario: Irish fada asset_check passes
- **WHEN** gaeilge content is extracted by `lc6_gaeilge_*_extracted`
- **THEN** the `irish_fada` asset_check asserts all extracted Irish-language
  strings have correct fada diacritics (e.g. `Máirt`, `Gaeilge`, `scríbhneoir`)

### Requirement: CocoIndex v1 embeddings (BGE-M3) into LanceDB

The system SHALL embed the extracted content into LanceDB via 7 (6 LC
subjects + government circulars) v1-conformant CocoIndex Apps in
`cianfhoghlaim/cocoindex/<subject>_embedding.py` +
`cianfhoghlaim/cocoindex/government_circulars_embedding.py`.

Each App SHALL conform to the R1-R4 v1 conformance contract:
- R1: `from ._lifespan import shared_lifespan`
- R2: Imports the canonical ContextKeys from `._lifespan`
- R3: `coco.App(...)` is at module scope
- R4: At least one `@coco.fn(` decorator AND uses
  `lancedb.mount_table_target(LANCE_DB, ...)`

The system SHALL use `BAAI/bge-m3` (multilingual, 1024-dim) as the
canonical embedder.

The system SHALL write to LanceDB table
`oideachais.lc.<subject>.<level>_<language>` (per subject) and
`oideachais.government.circulars.<dept>_<year>_<language>` (per circular).

#### Scenario: Mathematics embedding yields LanceDB rows
- **WHEN** `cocoindex update mathematics_embedding` runs
- **THEN** rows appear in `oideachais.lc.mathematics.<level>_<language>`
  with valid BGE-M3 vectors (1024-dim)

#### Scenario: v1 conformance check passes
- **WHEN** `mise run upstream:conformance` runs
- **THEN** all 7 CocoIndex Apps pass the R1-R4 conformance contract

### Requirement: Dagster orchestration (5-layer architecture)

The system SHALL orchestrate the pipeline via the 5-layer architecture:
- L1 ingestion: `orchestration/defs/1_ingestion/curriculum/lc6_ncca/`
  + `.../lc6_examinations/` + `.../government/circulars/`
- L2 materials: `orchestration/defs/2_materials/lc_extraction/lc5_assets.py`
  (42 lc5/lc6 assets: 7 subjects × 6 BAML stages) +
  `.../circulars/government_circular_assets.py` (2 assets)
- L3 model-lifecycle: `orchestration/defs/3_model_lifecycle/cocoindex_v1/lc_subjects/`
  + `.../government_circulars/`
- L4 asset generation: `orchestration/defs/4_asset_generation/education_asset_assets.py`
  (daily 2D / 3D asset generation for all 6 LC subjects)
- L5 agent ops: deferred to v2

#### Scenario: Full 42-asset materialization succeeds
- **WHEN** `dagster asset materialize --select '*lc6*'` runs
- **THEN** all 42 lc5/lc6 assets materialize without error

### Requirement: Asset checks

The system SHALL enforce the following asset checks:
- `ncca_partition_count_min` (each of 6 subjects × 2 languages has >=1 row)
- `sec_paper_year_coverage` (>=1 paper per subject per year for the last 5 years)
- `circular_year_min` (circulars span >=5 years)
- `irish_fada` (gaeilge extraction output has correct fada on all extracted
  Irish-language strings)
- `topic_overlap_min` (cross-subject topics have >=10% overlap with at
  least one related subject)
- `ocr_confidence_min` (OCR confidence >=0.85 per document)
- `baml_extraction_latency_p95` (95th-percentile BAML extraction latency
  <=30s per document)

#### Scenario: irish_fada check fails on "Gaeilge" without fada
- **WHEN** gaeilge extraction produces the string "Gaeilge" (missing fada on `ae`)
- **THEN** the `irish_fada` asset_check fails

### Requirement: 4 MotherDuck Dives

The system SHALL provide 4 MotherDuck Dives for the British-Isles Education
analytics layer:

1. **Syllabus Topics Dive** (`lc_syllabus_topics`) — topic frequency per
   subject per year, filterable by level and language
2. **Exam Paper Difficulty Dive** (`lc_exam_difficulty`) — per-subject per-year
   per-paper difficulty score
3. **Marking Scheme Complexity Dive** (`lc_marking_complexity`) — per-subject
   per-topic average descriptor count
4. **Education Circulars Dive** (`gov_circulars_archive`) — `gov.ie` circulars
   by dept + year + subject area

#### Scenario: Syllabus Topics Dive shows live data
- **WHEN** the user opens `lc_syllabus_topics` in MotherDuck
- **THEN** the chart shows topic frequency per subject per year from
  `md:oideachais.leaving_cert.<subject>_topics`

### Requirement: MotherDuck Flight for daily sync

The system SHALL provide a `lc_pdf_sync_flight` MotherDuck Flight that runs
daily at 04:00 UTC, executes `cocoindex update lc_subjects` + the 42 lc5/lc6
Dagster assets + the 2 gov.ie circular assets, and writes a status row to
`md:oideachais.lc_ops.daily_sync_status`.

#### Scenario: Daily flight writes status row
- **WHEN** the `lc_pdf_sync_flight` runs at 04:00 UTC
- **THEN** within 30 minutes a status row exists in
  `md:oideachais.lc_ops.daily_sync_status` with `status="ok"`

### Requirement: 6 per-subject marimo notebooks

The system SHALL provide 6 per-subject marimo notebooks at
`cianfhoghlaim/notebooks/dashboards/leaving_cert/0X_<subject>_analysis.py`,
each rendering 5 visualisations:

1. Topic frequency per year (line chart)
2. Cross-subject competency mapping (or `irish_fada` badge for gaeilge)
3. Exam paper difficulty trend (bar chart) OR cross-linguistic mapping
4. Marking scheme complexity (heatmap)
5. Quiz generator: 10 quiz items per topic via
   `b.Generate<Subject>QuestPack`

Each notebook SHALL:
- Have PEP 723 inline deps at the top
- Read from `md:oideachais.leaving_cert.<subject>_*` via `mo.sql(engine=md:oideachais)`
- Use DuckDB + Ibis (no pandas-only analytics)
- Read PDF paths from `os.environ["CIANFHOGHLAIM_LEAVING_CERT_ROOT"]`
- Never hardcode secrets

#### Scenario: Mathematics notebook renders live data
- **WHEN** `marimo run cianfhoghlaim/notebooks/dashboards/leaving_cert/05_mathematics_analysis.py`
  runs against a populated lakehouse
- **THEN** the 5 cells render charts with real data from
  `md:oideachais.leaving_cert.mathematics_*`

### Requirement: Cross-subject competency mapping

The system SHALL provide a cross-subject competency Notebook + LanceDB table
at `oideachais.lc.cross_subject.competencies.<level>_<lang>` (240 vectors =
6 subjects × 5 key competencies × 4 levels × 2 languages) via
`cianfhoghlaim/cocoindex/cross_subject_competency_embedding.py`.

The system SHALL provide a `cross_subject_competency.py` marimo notebook
at `cianfhoghlaim/notebooks/dashboards/education/cross_subject_competency.py`.

#### Scenario: Cross-subject competency heatmap renders
- **WHEN** `marimo run cianfhoghlaim/notebooks/dashboards/education/cross_subject_competency.py`
  runs
- **THEN** a heatmap shows the 6 subjects × 5 key competencies

### Requirement: gov.ie circulars cross-archive

The system SHALL provide a `government_circulars_archive.py` marimo notebook
at `cianfhoghlaim/notebooks/dashboards/circulars/` that:
- Lists all gov.ie circulars by dept + year + subject area
- Shows the NCCA syllabuses that each circular references
- Allows drill-down to the full circular text

The system SHALL provide a `syllabus_to_circular_link.py` marimo notebook
that shows the reverse mapping.

#### Scenario: Circular-to-syllabus drill-down
- **WHEN** the user clicks a circular in `government_circulars_archive.py`
- **THEN** the linked NCCA syllabuses are displayed with their full text