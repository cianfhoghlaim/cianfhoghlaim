# Spec Delta — british-isles-education-pipeline

This delta adds two new requirements to the existing `british-isles-education-pipeline`
capability. Existing requirements are preserved unchanged. The two requirements
correspond to Phase 6 (per-subject marimo notebooks) and Phase 7 (MotherDuck
Flight) of the BIEP v1 delivery — both have been delivered in
`openspec/changes/2026-07-13-biep-v1-phases-6-7-unblock-v1/`.

## ADDED Requirements

### Requirement: BIEP v1 Phase 6 — 6 per-subject marimo notebooks

The British-Isles Education Pipeline SHALL provide 6 per-subject marimo
notebooks at `cianfhoghlaim/notebooks/leaving_cert/`:

1. `chemistry.py` — 5 visualisations of `oideachais.leaving_cert.chemistry_*`
2. `computer_science.py` — 5 visualisations of `oideachais.leaving_cert.computer_science_*`
3. `gaeilge.py` — 5 visualisations of `oideachais.leaving_cert.gaeilge_*`
   (Irish-only; includes the `irish_fada` asset_check badge)
4. `geography.py` — 5 visualisations of `oideachais.leaving_cert.geography_*`
5. `mathematics.py` — 5 visualisations of `oideachais.leaving_cert.mathematics_*`
6. `06_en_vs_ga_comparison.py` — cross-subject EN ↔ GA competency
   comparison + bilingual coverage matrix (the 7th BIEP subject
   notebook per the spec's "BIEP Subject Notebooks" requirement)

Each notebook SHALL:

- Be a runnable PEP 723 marimo file (`__generated_with = "0.13.0"`)
- Connect to the `md:oideachais` lakehouse via
  `cianfhoghlaim.notebooks.nb_utils.connect_biep_lakehouse()`
- Render 5 visualisations per notebook: topic frequency per year
  (line chart), exam paper difficulty trend (bar chart), marking
  scheme complexity (heatmap), cross-linguistic mapping (for
  `gaeilge` and `06_en_vs_ga_comparison`), and an asset generator
  via the per-subject `qpack_<subject>.baml` function
- Invoke the canonical BAML extractors
  `ExtractCurriculumSyllabus` + `ExtractExamPaperLayout` +
  `ExtractMarkingSchemeGuideline` + `ExtractSyllabusDiagram`
- Be ~300–400 LOC each (the already-existing thin stubs at
  `notebooks/leaving_cert/` are enhanced up to that size)
- Preserve bilingual EN + GA UI strings (via the i18n helper at
  `cianfhoghlaim/web/packages/i18n/src/` or inline `mo.md(...)`
  strings in both English and Irish)

#### Scenario: Teacher opens the chemistry BIEP notebook

- **GIVEN** the `md:oideachais` MotherDuck lakehouse is up and the
  chemistry BAML extraction has produced rows in
  `oideachais.leaving_cert.chemistry_topics`
- **WHEN** a teacher runs
  `marimo edit cianfhoghlaim/notebooks/leaving_cert/chemistry.py`
- **THEN** the notebook renders 5 altair visualisations (topic
  frequency line chart, exam paper difficulty bar chart, marking
  scheme complexity heatmap, experiment ↔ learning outcome
  coverage, and the chemistry qpack asset generator) against
  live lakehouse data
- **AND** the BAML extractor cells show typed Pydantic records
  (not raw exceptions) for at least the chemistry syllabus PDF

#### Scenario: Gaeilge notebook preserves Irish fada

- **GIVEN** the gaeilge notebook renders
- **WHEN** the `irish_fada` asset_check fires on the loaded topic strings
- **THEN** every Irish-language string in `oideachais.leaving_cert.gaeilge_topics.topic_label_ga`
  preserves the fada diacritic (e.g. `Máirt`, `Gaeilge`, `scríbhneoir`,
  `Cian`, `Áireamhán`)
- **AND** the `gaeilge` notebook's "Cross-linguistic mapping" viz
  shows the EN ↔ GA topic pair side-by-side

#### Scenario: 06_en_vs_ga_comparison renders the bilingual coverage matrix

- **GIVEN** the bilingual EN + GA subject assets are loaded
- **WHEN** a teacher opens
  `cianfhoghlaim/notebooks/leaving_cert/06_en_vs_ga_comparison.py`
- **THEN** the notebook shows the EN ↔ GA topic coverage matrix
  for the 5 EN/GA subjects (Chemistry, Computer Science, Geography,
  Mathematics, English)
- **AND** the bilingual coverage heatmap shows the per-topic
  EN/GA gap (topics where the GA label is missing or stale)

### Requirement: BIEP v1 Phase 7 — Daily MotherDuck lc_pdf_sync_flight

The British-Isles Education Pipeline SHALL schedule a daily MotherDuck
Flight `lc_pdf_sync_flight` at
`cianfhoghlaim/motherduck/flights/lc_pdf_sync_flight.py`
that:

1. Runs `uv run cocoindex update lc_subjects` to re-ingest the
   6 LC subjects' PDF corpus (any new PDFs landed in
   `s3://garage/oideachais/leaving_cert/<subject>/<lang>/<year>/<file>.pdf`
   in the last 24h)
2. Runs `uv run dagster asset materialize --select '*lc*'` to
   re-materialise the 6×6+2 = 38 LC assets (6 subjects × 6 stages +
   gov.ie circulars)
3. Writes a status row to
   `md:oideachais.lc_ops.daily_sync_status(flight_name,
   started_at, completed_at, status, log)` capturing the
   subprocess exit codes + the full log

The Flight SHALL be registered in
`cianfhoghlaim/motherduck/flights/config.yaml` with
`schedule: "0 4 * * *"` (daily at 04:00 UTC). The IaC orchestration
(Docker Compose stack + cron binding) lives in the separate
`bonneagar` repo at `bonneagar/stacks/motherduck/`.

#### Scenario: New PDF lands in Garage S3

- **GIVEN** a teacher (or upstream agent) has uploaded a new
  mathematics syllabus PDF to
  `s3://garage/oideachais/leaving_cert/mathematics/en/2026/Q1.pdf`
- **WHEN** 24 hours elapse and the daily `lc_pdf_sync_flight`
  fires at 04:00 UTC
- **THEN** the Flight's `cocoindex update lc_subjects` step
  detects the new PDF and re-ingests it
- **AND** the `dagster asset materialize --select '*lc*'`
  step materialises the corresponding `lc5_mathematics_extract`
  asset
- **AND** the resulting typed rows appear in
  `md:oideachais.leaving_cert.mathematics` within minutes
- **AND** a status row with `status='ok'` lands in
  `md:oideachais.lc_ops.daily_sync_status`

#### Scenario: Daily flight failure is recorded

- **GIVEN** the `lc_pdf_sync_flight` runs at 04:00 UTC
- **WHEN** either the `cocoindex update` step OR the
  `dagster asset materialize` step exits non-zero
- **THEN** the Flight's status row in
  `md:oideachais.lc_ops.daily_sync_status` has `status='failed'`
- **AND** the `log` column contains the captured stderr from
  the failed subprocess
- **AND** the daily BIEP dive
  (`lc_syllabus_topics`) is not marked stale until the next
  successful run