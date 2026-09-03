# BIEP 8-Jurisdictions Capability (the canonical per-jurisdiction BIE contract)

## Purpose

`bie-8-jurisdictions` is the canonical per-jurisdiction British Isles
Education (BIE) capability that documents the per-jurisdiction BAML
Extract* function contract, the per-jurisdiction 2-axis partition, the
per-jurisdiction asset check, the per-jurisdiction MotherDuck Dive +
Flight, and the per-jurisdiction ChangeDetection.io monitor for all 8
British Isles jurisdictions.

This is the canonical home for the per-jurisdiction contracts that
underpin the BIEP v3 umbrella. It supersedes the per-jurisdiction
contracts that were previously scattered across the v1 + v2 specs.

The 8 jurisdictions:

- 🇮🇪 Ireland (Leaving Cycle + Junior Cycle, EN + GA)
- 🏴󠁧󠁢󠁥󠁮󠁧󠁿 England (A-Level + GCSE, EN; 3 boards × 2 levels)
- 🏴󠁧󠁢󠁳󠁣󠁴󠁿 Scotland (SQA, EN; 3 levels)
- 🏴󠁧󠁢󠁷󠁬󠁳󠁿 Wales (WJEC, Welsh-medium + EN; 2 levels)
- 🇬🇧 Northern Ireland (CCEA, EN; 2 levels; includes Gaeltacht overlay)
- 🇯🇪 Jersey (English GCSE + French Baccalauréat hybrid; 4 levels)
- 🇬🇬 Guernsey (English GCSE + A-Level + Local qualifications; 4 levels)
- 🇮🇲 Isle of Man (English GCSE + A-Level + Local qualifications; 4 levels; includes Manx Gaelic GCSE)
## Requirements
### Requirement: Per-jurisdiction BAML Extract* function contract

The system SHALL provide a per-jurisdiction BAML `Extract*` function
that extracts the structured syllabus / exam-paper data from a
per-jurisdiction PDF.

The 8 BAML functions are:

| Jurisdiction | BAML function | Return type | Per-jurisdiction flag |
|:--|:--|:--|:--|
| Ireland (LC) | `b.ExtractCurriculumSyllabus` | `SyllabusDocument` | n/a |
| Ireland (JC) | `b.ExtractJCCurriculum` | `JCCurriculumSpec` | n/a |
| England (AQA) | `b.ExtractAQAQualSpec` | `AQAQualSpec` | `board` enum |
| England (OCR) | `b.ExtractOCRQualSpec` | `OCRQualSpec` | `board` enum |
| England (Edexcel) | `b.ExtractEdexcelQualSpec` | `EdexcelQualSpec` | `board` enum |
| England (generic) | `b.ExtractUKQualSpec` | `UKQualificationSpec` | `board` enum |
| Scotland (SQA) | `b.ExtractScotlandSyllabus` | `ScotlandSyllabusSpec` | n/a |
| Wales (WJEC) | `b.ExtractWalesSyllabus` | `WalesSyllabusSpec` | `is_welsh_medium` |
| Northern Ireland (CCEA) | `b.ExtractNIExamPaper` | `NorthernIrelandExamPaper` | n/a |
| Jersey | `b.ExtractJerseySyllabus` | `JerseySyllabusSpec` | `is_french_bac` |
| Guernsey | `b.ExtractGuernseySyllabus` | `GuernseySyllabusSpec` | `is_local_qualification` |
| Isle of Man | `b.ExtractIsleOfManSyllabus` | `IsleOfManSyllabusSpec` | `has_manx_language` |

All 12 functions route via the canonical `BIEPV3Extract` BAML client
(post-v3 hardening per the 2026-08-07 change).

#### Scenario: Per-jurisdiction Extract* function availability

- **WHEN** the operator runs `cd baml_src && uv run baml-cli generate`
- **THEN** all 12 Extract* functions are compiled into the BAML client
- **AND** each function takes `(pdf_text, subject, level)` and returns the per-jurisdiction Spec type

### Requirement: Per-jurisdiction 2-axis scope × year partition

The system SHALL partition every per-jurisdiction Dagster asset on
the canonical 2-axis partition:

- **Scope axis**: `<jurisdiction>__<stage>__<subject_slug>__<board>__<level>__<lang>`
- **Year axis**: integer year (2017-2027) or `undated`

The canonical partition implementation is at
`orchestration/partitions_v2.py::biep_v3_scope_year_partition`.

#### Scenario: Scotland partition

- **WHEN** the `scotland_documents_ingested` asset materialises
- **THEN** the partition key is `(scope="scotland__higher__mathematics__na__higher__en", year="2024")`
- **AND** the asset_check asserts that every emitted row's `jurisdiction` is "scotland"

### Requirement: Per-jurisdiction 3 asset checks (cohort count + RAGAS + LanceDB chunks)

The system SHALL provide 3 asset checks per jurisdiction:

- `<jurisdiction>_<stage>_documents_ingested_check`: cohort count >= expected
- `<jurisdiction>_<stage>_extractions_ragas_check`: RAGAS score >= 0.70
- `<jurisdiction>_<stage>_lance_chunks_check`: chunk count >= expected

The threshold is per-jurisdiction:
- Ireland LC: >= 12 / >= 0.70 / >= 12_000
- Ireland JC: >= 88 / >= 0.65 / >= 88_000
- England A-Level: >= 147 / >= 0.70 / >= 147_000
- England GCSE: >= 129 / >= 0.70 / >= 129_000
- Scotland: >= 150 / >= 0.70 / >= 150_000
- Wales: >= 160 / >= 0.70 / >= 160_000
- Northern Ireland: >= 70 / >= 0.70 / >= 70_000
- Jersey: >= 120 / >= 0.70 / >= 120_000
- Guernsey: >= 120 / >= 0.70 / >= 120_000
- Isle of Man: >= 120 / >= 0.70 / >= 120_000

#### Scenario: Per-jurisdiction asset check gating

- **WHEN** the per-jurisdiction extraction asset materialises
- **THEN** the RAGAS asset check asserts that the RAGAS-voted_canonical row has `ragas_score >= 0.70`
- **AND** if the check fails, the extraction asset is marked as failed
- **AND** the per-jurisdiction mise task (m1-m10) exits with non-zero status

### Requirement: Per-jurisdiction MotherDuck Dive + Flight

The system SHALL provide 1 MotherDuck Dive + 1 MotherDuck Flight per
jurisdiction:

- 8 Dives: `ireland_lc_syllabus_topics`, `ireland_jc_curriculum_topics`, `england_a_level_topics`, `england_a_level_complexity`, `england_gcse_topics`, `england_gcse_complexity`, `scotland_curriculum_topics`, `wales_curriculum_topics`, `northern_ireland_exam_paper_dive`, `jersey_curriculum_topics_v2`, `guernsey_curriculum_topics_v2`, `isle_of_man_curriculum_topics_v2`
- 8 Flights: `ireland_lc_daily_sync_flight`, `ireland_jc_daily_sync_flight`, `england_a_level_daily_sync_flight`, `england_gcse_daily_sync_flight`, `sct_wls_ni_flight`, `crown_dependencies_flight`, `filesystem_monthly_sync_flight`, `language_monthly_sync_flight`

#### Scenario: Per-jurisdiction MotherDuck Dive reads

- **WHEN** the operator opens the MotherDuck Dive `scotland_curriculum_topics`
- **THEN** the Dive reads from `md:cianfhoghlaim.education.scotland.<level>.<subject>.voted_canonical`
- **AND** the Dive shows 150 rows (50 subjects × 3 levels)

### Requirement: Per-jurisdiction ChangeDetection.io monitor

The system SHALL provide 1 ChangeDetection.io monitor per jurisdiction:

- 8 monitors: `aqa_monitor.yaml`, `ocr_monitor.yaml`, `edexcel_monitor.yaml` (England), `ncca_monitor.yaml` (Ireland), `sqa_monitor.yaml` (Scotland), `wjec_monitor.yaml` (Wales), `ccea_monitor.yaml` (Northern Ireland), `iom_monitor.yaml` (Isle of Man), `jersey_monitor.yaml`, `guernsey_monitor.yaml`

The monitors are at `bonneagar/stacks/changedetection/monitors/`.

#### Scenario: Per-jurisdiction ChangeDetection webhook

- **WHEN** the AQA monitor detects a content change
- **THEN** it POSTs to the Dagster webhook `http://dagster-webhook:8080/webhooks/england_change_detection`
- **AND** the Dagster sensor `jcq_registry_sensor` picks up the change
- **AND** the 4-path OCR ensemble re-runs against the new PDF
- **AND** the RAGAS-voted_canonical row is committed to the new DuckLake table

### Requirement: Per-jurisdiction snake_case file naming

The system SHALL enforce the canonical per-jurisdiction snake_case
file naming convention:

```text
s3://garage/cianfhoghlaim/<jurisdiction>/<stage>/<subject_slug>/<language>/<year>/<jurisdiction>__<stage>__<subject_slug>__<board>__<qual_level>__<language>__<year>__<sha256_8>.pdf
```

The validation script is at `scripts/validate_snake_case_filenames.py` and
the canonical contract is at `dlt_sources/common/snake_case_contract.py`.

#### Scenario: Per-jurisdiction filename validation

- **WHEN** the operator runs `mise run biep:v3:filename-validate`
- **THEN** every file in `s3://garage/cianfhoghlaim/<jurisdiction>/...` matches the canonical snake_case pattern

### Requirement: England DLT sources for 3 GCSE + 3 A-Level boards

The system SHALL host 6 DLT sources for the England BIEP v3 pipeline:

1. `dlt_sources/british_isles/england/education/gcse/aqa_source.py`
2. `dlt_sources/british_isles/england/education/gcse/ocr_source.py`
3. `dlt_sources/british_isles/england/education/gcse/edexcel_source.py`
4. `dlt_sources/british_isles/england/education/a_level/aqa_source.py`
5. `dlt_sources/british_isles/england/education/a_level/ocr_source.py`
6. `dlt_sources/british_isles/england/education/a_level/edexcel_source.py`

Each source SHALL be exported from
`dlt_sources/british_isles/england/education/__init__.py` and SHALL
emit to the canonical BIEP DuckLake namespace
`cianfhoghlaim.education.british_isles.england.{stage}.{board}.{subject}`.

Per the `2026-08-10-england-biiep-pipeline-v1` change proposal.

#### Scenario: AQA GCSE source emits to DuckLake

- **GIVEN** the AQA GCSE source is registered via `@dlt.source(name="england_gcse_aqa")`
- **WHEN** `dagster asset materialize --select england_gcse_aqa_assets` runs
- **THEN** the source reads `stedding/site_scrape_samples/england/gcse/{subject}/`
- **AND** writes to `md:cianfhoghlaim.education.british_isles.england.gcse.aqa.{subject}`
- **AND** the asset check `row_count` passes with `row_count > 0`

#### Scenario: 6 sources are wired into Dagster

- **WHEN** `dagster job list | grep england` runs
- **THEN** the 6 jobs (one per board × stage) appear in the list
- **AND** `dagster asset materialize --select england_*` materializes all 6

### Requirement: England Dagster asset groups (6)

The system SHALL host 6 Dagster asset groups wrapping the 6 England
DLT sources + BAML extraction + CocoIndex embedding + MotherDuck load:

1. `orchestration/defs/2_materials/england_education/gcse/aqa_assets.py`
2. `orchestration/defs/2_materials/england_education/gcse/ocr_assets.py`
3. `orchestration/defs/2_materials/england_education/gcse/edexcel_assets.py`
4. `orchestration/defs/2_materials/england_education/a_level/aqa_assets.py`
5. `orchestration/defs/2_materials/england_education/a_level/ocr_assets.py`
6. `orchestration/defs/2_materials/england_education/a_level/edexcel_assets.py`

Each asset group SHALL wire:
- The DLT source (per Requirement 1 above)
- The BAML extraction function (`Extract<Board>QualSpec`)
- The CocoIndex v1 App (`england_<board>_<stage>_embedding`)
- The MotherDuck landing (per Requirement 1 above namespace)

#### Scenario: All 6 asset groups register with Dagster

- **WHEN** `dg list defs --location england_education` runs
- **THEN** all 6 asset groups are registered
- **AND** each group has 4 assets (source + BAML + CocoIndex + MotherDuck load)

### Requirement: England cross-board coverage check

The system SHALL host
`orchestration/defs/2_materials/england_education/misconfig_check.py`
that verifies the 3 boards (AQA / OCR / Edexcel) cover the same
~92 subjects (43 GCSE + 49 A-Level) — no board is missing any
subject.

#### Scenario: AQA is missing 2 subjects

- **GIVEN** the AQA GCSE source has 41 of the 43 expected subjects
  (missing `computer-science-aqa` and `drama-aqa`)
- **WHEN** `dagster asset check --select england_misconfig_check` runs
- **THEN** the check fails with `AQA GCSE missing 2 subjects: computer-science-aqa, drama-aqa`
- **AND** the check identifies which subjects are missing from which board

#### Scenario: All 3 boards cover all 92 subjects

- **WHEN** all 6 sources have the full subject coverage
- **THEN** the misconfig check exits 0
- **AND** `dagster asset check --select england_misconfig_check` returns passed

## Cross-references

- `british-isles-education-pipeline-v3` — the BIEP v3 umbrella spec
- `cross-region-pipeline` — the canonical snake_case + source_id + DuckLake namespace contract
- `dagster-5-layer-component-architecture` — the canonical 5-layer Dagster pattern
- `openspec/changes/2026-08-13-biep-v3-systematic-download-ireland-england-v1/` — the umbrella change
- `openspec/changes/2026-07-30-biep-v3-sct-wls-ni-v1/` — Scotland + Wales + NI
- `openspec/changes/2026-07-31-biep-v3-crown-dependencies-v1/` — Jersey + Guernsey + IoM
- `openspec/changes/2026-08-13-biep-v3-filesystem-and-language-pipelines-v1/` — filesystem + language
- `baml_src/british_isles/<jurisdiction>/education/subject_taxonomy.baml` — the per-jurisdiction BAML files
- `dlt_sources/british_isles/<jurisdiction>/education/<jurisdiction>_jurisdiction_pipeline.py` — the per-jurisdiction DLT pipelines
- `orchestration/defs/2_materials/<jurisdiction>_education/<jurisdiction>_assets.py` — the per-jurisdiction Dagster assets
- `motherduck/dives/<jurisdiction>_curriculum_dive.py` — the per-jurisdiction MotherDuck Dives
- `motherduck/flights/<jurisdiction>_daily_sync_flight.py` — the per-jurisdiction MotherDuck Flights
- `scripts/m{5,6,7,8,9,10}_*.py` — the per-jurisdiction entrypoint scripts
- `orchestration/automation/biiep_scheduling.py` — the canonical 4-cadence scheduling policy
- `docs/agents/biiep-v3-systematic-download.md` — the canonical newcomer guide
- `docs/agents/biiep-v3-quickstart.md` — the "first 30 minutes" guide
- `docs/agents/biiep-v3-faq.md` — the canonical FAQ
- `docs/agents/biiep-v3-baml-client.md` — how to invoke the 6 new Extract* functions from Python
- `docs/agents/biiep-v3-storage-layout.md` — the DuckLake + Lance + MotherDuck layout
- `docs/agents/biiep-v3-cron-schedule.md` — the 4-cadence scheduling policy in detail
- `docs/agents/biiep-v3-bie-8-jurisdictions.md` — the 8-jurisdiction rollout + the 2 scanner domains
