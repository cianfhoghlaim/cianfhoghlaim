# British Isles Education Pipeline v3 (BIEP v3) Capability

## Purpose

`british-isles-education-pipeline-v3` (BIEP v3) is the v3 umbrella
capability that systematically downloads, extracts, embeds, logs, and
analyses **8 British Isles jurisdictions** + **2 general-purpose scanner
domains** in the Cianfhoghlaim data platform.

The 8 jurisdictions:

- 🇮🇪 Ireland (Leaving Cycle + Junior Cycle, EN + GA)
- 🏴󠁧󠁢󠁥󠁮󠁧󠁿 England (A-Level + GCSE, EN; 3 boards × 2 levels)
- 🏴󠁧󠁢󠁳󠁣󠁴󠁿 Scotland (SQA, EN; 3 levels)
- 🏴󠁧󠁢󠁷󠁬󠁳󠁿 Wales (WJEC, Welsh-medium + EN; 2 levels)
- 🇬🇧 Northern Ireland (CCEA, EN; 2 levels; includes Gaeltacht overlay)
- 🇯🇪 Jersey (English GCSE + French Baccalauréat hybrid; 4 levels)
- 🇬🇬 Guernsey (English GCSE + A-Level + Local qualifications; 4 levels)
- 🇮🇲 Isle of Man (English GCSE + A-Level + Local qualifications; 4 levels; includes Manx Gaelic GCSE)

The 2 scanner domains:

- `filesystem` — 11 canonical DLT sources (leabharlann_books, gemini_deep_research, google_takeout, takeout_v1, email_inbox, leaving_cert_source, university_of_galway, zotero, gemini_corpus_source, pdf_download_source, previews)
- `language` — 19 canonical DLT sources (ainm, canuint, canuint_audio, canuint_dialect_summary, canuint_search, canuint_word_alignment, duchas, duchas_images, gaois, gaois_combined, heritage, hidden_heritages, local_documents_by_subject, local_education_documents, logainm, tearma, tearma_search, universal_dependencies)

**Total: 12 + 88 + 147 + 129 + 150 + 160 + 70 + 120 + 120 + 120 = 1,116 cohorts + 30 scanner sources = 1,146 active items.**

The 5-milestone plan (M0-M4) covers Ireland + England. The 6 deferred
jurisdictions (M5-M10) cover Scotland + Wales + Northern Ireland +
Jersey + Guernsey + Isle of Man. The 2 scanner domains run on a
monthly cadence (separate from the annual education content).

Per the `2026-08-13-biep-v3-systematic-download-ireland-england-v1` change,
the BIEP v3 umbrella is the canonical home for new BIEP work.

## Background

The platform has been ingesting education content from NCCA and SEC
since 2026-03 (the pre-v4 `cianfhoghlaim-pipeline`). BIEP v3 brings the
full 8-jurisdiction + 2 scanner rollout to a fully-runnable end-to-end
state with:
- 18 BAML functions (6 new + 8 existing + 3 board-specific + 1 generic)
- 380+ CocoIndex v1 Apps
- 200+ Dagster assets + 30+ asset checks
- 14 MotherDuck Dives
- 12 MotherDuck Flights
- 9 ChangeDetection.io monitors (3 existing + 6 needed)
- 4-cadence scheduling policy (yearly + monthly + weekly + nightly + event-driven)
- 5-phase pattern (Ingestion → Extraction → Embedding → ibis logging → Analytics)
## Requirements
### Requirement: BIEP v3 5-milestone sequential plan (M0-M4)

The system SHALL provide the canonical 5-milestone sequential plan
(M0 → M4) for Ireland + England, where each milestone has an explicit
acceptance gate:

- **M0** (Foundation): lakehouse + BAML + registry + namespace
- **M1** (Ireland LC): 12 cohorts (6 subjects × 2 langs)
- **M2** (Ireland JC): 88 cohorts (36 + 16 + 36)
- **M3** (England A-Level): 147 cohorts (49 × 3 boards)
- **M4** (England GCSE): 129 cohorts (43 × 3 boards)

Each milestone has a canonical `mise run biep:v3:m<N>` entrypoint that
runs the 5-phase pattern (Ingestion → Extraction → Embedding → ibis
logging → Analytics) and exits 0 iff all 3 asset checks pass.

#### Scenario: Ireland LC (M1) acceptance gate

- **WHEN** the operator runs `mise run biep:v3:m1`
- **THEN** the 12 Ireland LC cohorts are materialised
- **AND** `ireland_lc_documents_ingested_check` passes (cohort count >= 12)
- **AND** `ireland_lc_extractions_ragas_check` passes (score >= 0.70)
- **AND** `ireland_lc_lance_chunks_check` passes (chunk count >= 12_000)

### Requirement: BIEP v3 6-deferred-jurisdiction plan (M5-M10)

The system SHALL provide the canonical 6-deferred-jurisdiction plan
(M5 → M10) for Scotland + Wales + Northern Ireland + Jersey + Guernsey
+ Isle of Man, where each milestone has an explicit acceptance gate:

- **M5** (Scotland): 150 cohorts (50 SCQF subjects × 3 levels)
- **M6** (Wales): 160 cohorts (80 WJEC subjects × 2 levels)
- **M7** (Northern Ireland): 70 cohorts (35 CCEA subjects × 2 levels)
- **M8** (Jersey): 120 cohorts (30 subjects × 4 levels)
- **M9** (Guernsey): 120 cohorts (30 subjects × 4 levels)
- **M10** (Isle of Man): 120 cohorts (30 subjects × 4 levels)

Each milestone has a canonical `mise run biep:v3:m<N>` entrypoint.

#### Scenario: Scotland (M5) acceptance gate

- **WHEN** the operator runs `mise run biep:v3:m5`
- **THEN** the 150 Scotland cohorts are materialised
- **AND** `scotland_documents_ingested_check` passes (cohort count >= 150)
- **AND** `scotland_extractions_ragas_check` passes (score >= 0.70)
- **AND** `scotland_lance_chunks_check` passes (chunk count >= 150_000)

### Requirement: BIEP v3 2-scanner-domain plan (filesystem + language)

The system SHALL provide the canonical 2-scanner-domain plan for the
filesystem (11 DLT sources) + language (19 DLT sources) scanner
domains, where each domain has a canonical monthly MotherDuck Flight
+ 3 generic Dagster assets + 3 asset checks.

#### Scenario: Filesystem monthly sync (Phase D)

- **WHEN** the operator runs `mise run biep:v3:filesystem:monthly:sync`
- **THEN** the 11 filesystem DLT sources are re-ingested
- **AND** the 3 filesystem asset checks pass
- **AND** the `filesystem_monthly_sync_flight` MotherDuck Flight runs
- **AND** the status row is written to
  `md:cianfhoghlaim.education.filesystem._audit.daily_sync_status`

### Requirement: BIEP v3 4-cadence scheduling policy

The system SHALL implement the canonical 4-cadence scheduling policy:

- **Yearly** (cron `0 0 1 9 *`) for NCCA + SEC + AQA + OCR + Edexcel + SQA + WJEC + CCEA + IoM + Jersey + Guernsey education content
- **Monthly** (cron `0 0 1 * *`) for gov.ie education circulars + the 2 scanner domains (filesystem + language)
- **Weekly** (cron `0 6 * * 1`) for the M0 foundation assets
- **Nightly** (cron `0 0 * * *`) for the BIEP v3 RAGAS + audit + asset checks
- **Event-driven** (eager) for the ChangeDetection.io sensors

#### Scenario: 4-cadence policy implemented

- **WHEN** the operator runs `mise run biep:v3:cron-schedule` (a fictional command for documentation purposes)
- **THEN** the BIEP v3 system displays the 4-cadence policy in a human-readable table

### Requirement: BIEP v3 5-phase pattern (Ingestion → Extraction → Embedding → ibis logging → Analytics)

The system SHALL implement the canonical 5-phase pattern for every
BIEP v3 cohort:

1. **Phase A — Ingestion**: DLT sources land raw PDFs + scraped HTML into `s3://garage/cianfhoghlaim/<jurisdiction>/<stage>/<subject>/<language>/<year>/<file>.pdf` with snake_case metadata sidecar
2. **Phase B — Extraction**: `EnsembledExtractor.extract()` runs the 4-path OCR ensemble (BAML/Docling + Unstract + qwen3-vl-8b + gemma-4-26B-A4B) + RAGAS `biiep_extraction_consensus` vote
3. **Phase C — Embedding**: per-jurisdiction CocoIndex v1 Apps chunk + embed via `BAAI/bge-m3` 1024-d multilingual embedder + write to LanceDB
4. **Phase D — ibis logging**: 1 audit row per cohort in `cianfhoghlaim.education.<jurisdiction>._audit.daily_sync_status`
5. **Phase E — Analytics**: marimo notebook renders the per-jurisdiction cohort matrix + MotherDuck Dive

#### Scenario: 5-phase pattern applied to a Scotland cohort

- **WHEN** the operator runs `mise run biep:v3:m5`
- **THEN** the 5 phases run in order (Ingestion → Extraction → Embedding → ibis logging → Analytics)
- **AND** the 4-path OCR ensemble + RAGAS voting completes with `ragas_score >= 0.70`
- **AND** the LanceDB chunks land in the canonical table `cianhoghlaim.scotland.<level>.<subject>_chunks`
- **AND** the ibis audit row lands in `cianfhoghlaim.education.scotland._audit.daily_sync_status`
- **AND** the MotherDuck Dive `scotland_curriculum_topics` renders the 150-row cohort matrix

### Requirement: OCR completion webhook convention

The system MUST provide a single OCR_WEBHOOK_URL env convention that
the OCR router (at `bonneagar/stacks/ocr-router/`) MUST honour when
emitting OCR completion events. The webhook payload MUST be a JSON
envelope:

```json
{
  "document_id": "<uuid>",
  "capability": "<forms|layout|tables+latex|doctags|gaelic|english>",
  "backend_used": "<paddleocr|mlx-omni|olmocr|docling-serve|llama-swap|dots-ocr>",
  "model": "<model name>",
  "result_url": "<s3://lakehouse/ocr/...>",
  "duration_ms": <int>,
  "trace_id": "<opentelemetry trace id>",
  "completed_at": "<iso-8601 utc>"
}
```

The system MUST emit the webhook as a `POST` to `OCR_WEBHOOK_URL` with
HTTP Basic auth using the `OCR_WEBHOOK_TOKEN` env var. If
`OCR_WEBHOOK_URL` is empty, the router MUST skip the emission (graceful
degradation, matching the SaaS-only Logfire pattern).

The webhook MUST be idempotent: re-delivery of the same `document_id`
MUST be a no-op (the Dagster sensor filters by document_id + a
`created_at` window).

#### Scenario: Dagster sensor consumes the OCR completion event

```
# At OCR_WEBHOOK_URL=http://dagster-webhook:8080/webhooks/ocr_completion
$ curl -X POST http://dagster-webhook:8080/webhooks/ocr_completion \
    -H "Authorization: Basic $OCR_WEBHOOK_AUTH" \
    -d '{"document_id": "doc-abc", "capability": "tables+latex",
         "backend_used": "olmocr", "model": "olmocr-2-7b-1025",
         "result_url": "s3://lakehouse/ocr/abc.json",
         "duration_ms": 4128, "trace_id": "trace-def",
         "completed_at": "2026-07-31T12:34:56Z"}'
[webhook] 202 Accepted
[dagster-sensor] sensor_trigger(ocr_completion, document_id="doc-abc")
[asset]    ocr_extraction/lc_chem_2024_materialized (downstream triggers)
```

#### Scenario: re-delivery is a no-op

```
# Same document_id delivered twice within the 1-minute dedup window:
$ curl -X POST http://dagster-webhook:8080/webhooks/ocr_completion \
    -d '{"document_id": "doc-abc", ...}'
[webhook] 202 Accepted  (first delivery)
$ curl -X POST http://dagster-webhook:8080/webhooks/ocr_completion \
    -d '{"document_id": "doc-abc", ...}'
[webhook] 202 Accepted  (re-delivery — sensor filters out as duplicate)
```

### Requirement: Dagster ocr_completion_sensor

The system MUST provide a Dagster sensor
`orchestration/sensors/ocr_completion_sensor.py` that:

1. Polls the OCR_WEBHOOK_URL endpoint on a 30-second tick
2. Filters duplicates by `(document_id, completed_at)` tuple (in-memory
   dedup with a 1-minute rolling window)
3. Materialises a per-document `ocr_extraction/<document_id>` asset on
   receipt of a new event
4. Triggers the downstream `biiep_v3_<jurisdiction>_materialize` asset
   chain (per the existing BIEP v3 ingestion DAG)
5. Emits an OpenTelemetry span tagged with
   `dagster.sensor=ocr_completion, dagster.document_id=<doc-abc>` so
   the trace correlates to the OCR router's span (via shared trace_id)

The sensor MUST fail gracefully if `OCR_WEBHOOK_URL` is unset (returns
a SKIPPED state, not an ERROR).

#### Scenario: the sensor is healthy and emits a new run

```
$ dagster sensor list
ocr_completion_sensor    ACTIVE  last_tick=14s ago  last_run="2026-07-31T12:34:56Z"

# New event arrives:
[dagster-sensor] tick: 1 new event (document_id=doc-abc)
[dagster-sensor] → ocr_extraction/doc-abc  (asset materialised)
[dagster-sensor] → biiep_v3_ireland_lc5_materialize  (downstream triggered)
[langfuse] trace=trace-def → span "dagster.sensor=ocr_completion, document_id=doc-abc"
```

#### Scenario: OCR_WEBHOOK_URL unset → sensor SKIPPED

```
$ OCR_WEBHOOK_URL= dagster sensor list
ocr_completion_sensor    ACTIVE  last_tick=14s ago  state=SKIPPED  reason=OCR_WEBHOOK_URL unset
```

### Requirement: Foundation unblock (M0)

The system SHALL provide all 12 foundation prerequisites before any
jurisdiction pipeline can run:

1. The `LAKEHOUSE_DUCKDB = "md:cianfhoghlaim"` constant exported from
   `dlt_sources/common/destinations_cianfhoghlaim.py`.
2. A working `DuckLakeResource` whose `get_client()` returns a valid
   `DuckLakeClient` (no broken `..storage.ducklake_client` import).
3. An `IcebergCatalogResource` that wraps PyIceberg 0.11.1
   `load_catalog("kcg", type="rest", uri="http://lakehouse-lakekeeper:8181")`.
4. A `LanceNamespaceResource` that connects to
   `rest://lakehouse-lance-namespace:8182`.
5. A `LanceDBResource` with `embedding_model = "BAAI/bge-m3"` (1024-d).
6. The canonical 3 BAML clients (`BIEPV3Extract` /
   `BIEPV3ExtractStrong` / `BIEPV3Vision`) in
   `baml_src/clients_biep_v3.py`.
7. The generic `ExtractUKQualSpec(board: ExamBoard, ...)` BAML function in
   `baml_src/british_isles/england/education/curriculum_syllabus.baml`.
8. The `ExtractSyllabusDiagram(pdf_text) -> SyllabusDiagram` BAML function
   in `baml_src/british_isles/ireland/education/lc_extraction/syllabus_diagram.baml`.
9. The `ExtractCrossLinguisticConcept(pdf_text) -> CrossLinguisticConcept`
   BAML function in
   `baml_src/british_isles/ireland/education/lc_extraction/cross_linguistic.baml`.
10. The British Isles Subject Registry seeded to ≥210 rows for Ireland +
    England via `seed_registry()`.
11. The `cianhoghlaim` Lance namespace created in Lakekeeper.
12. The lakehouse stack (Garage + Lakekeeper + Lance-namespace + 10 other
    services) up and responding 200 OK on all 13 service health endpoints.

#### Scenario: All 4 M0 asset checks pass

- **WHEN** the operator runs
  `mise run biep:v3:m0`
- **THEN** all 4 assets (`lakehouse_smoke_test`, `baml_codegen_gate`,
  `registry_seed_count`, `lance_namespace_ready`) materialise within 30
  seconds
- **AND** all 4 asset checks pass
- **AND** the local lakehouse is ready to receive BIEP v3 cohort data

### Requirement: Snake_case file naming contract

The system SHALL land every PDF and metadata sidecar at the canonical
snake_case path:

```text
s3://garage/cianfhoghlaim/<jurisdiction>/<stage>/<subject_slug>/<language>/<year_or_undated>/<jurisdiction>__<stage>__<subject_slug>__<board_or_na>__<qual_level_or_untiered>__<language>__<year_or_undated>__<sha256[0:8]>.pdf
```

with a sibling `<file>.meta.json` sidecar carrying the metadata fields
(`source_id`, `jurisdiction`, `stage`, `subject_slug`, `board`,
`qualification_level`, `language`, `year`, `source_url`, `crawled_at`,
`byte_size`, `page_count`, `content_hash_sha256`, `publisher`).

#### Scenario: An LC Mathematics PDF lands at the canonical path

- **WHEN** the Ireland LC Mathematics Higher English 2024 syllabus PDF is
  ingested
- **THEN** it SHALL be written to
  `s3://garage/cianfhoghlaim/ireland/leaving_cycle/mathematics/en/2024/ireland__leaving_cycle__mathematics__na__higher__en__2024__<sha256[0:8]>.pdf`
- **AND** the sibling `.meta.json` SHALL carry
  `source_id="british_isles.ireland.education.ncca_lc_mathematics"`
- **AND** the asset check `ireland_lc_documents_ingested_check` SHALL pass
  for the 12-cohort count

### Requirement: Per-cohort 5-phase pattern (Ingestion → Extraction → Embedding → ibis logging → Analytics)

The system SHALL, for each of the 428 BIEP v3 cohorts, run the canonical
5-phase pattern:

| Phase | Asset | Output |
|:--|:--|:--|
| A. Ingestion | `<jurisdiction>_<stage>_<subject>_<lang>_documents_ingested` | raw PDF + meta sidecar at canonical snake_case path |
| B. Extraction | `<jurisdiction>_<stage>_<subject>_<lang>_extractions` (4 OCR paths + RAGAS voting) | 5 per-path DuckLake tables + 1 voted_canonical; RAGAS score ≥ 0.70 |
| C. Embedding | `<jurisdiction>_<stage>_<subject>_<lang>_chunks` CocoIndex v1 App | LanceDB table populated; ≥ 1000 chunks per cohort; vector index built |
| D. ibis logging | `<jurisdiction>_<stage>_audit` DuckLake table | 1 audit row per cohort (start_at / end_at / rows_landed / ragas_score) |
| E. Analytics | marimo notebook `<N>_<jurisdiction>_<stage>_dashboard.py` | notebook renders the per-cohort matrix in < 30s; no raw `duckdb.connect()` |

#### Scenario: Ireland LC Mathematics Higher English 2024 runs all 5 phases

- **WHEN** the M1 milestone pipeline is materialised
- **THEN** `ireland_lc_mathematics_higher_en_documents_ingested` materialises
  the PDF at the canonical snake_case path
- **AND** `ireland_lc_mathematics_higher_en_extractions` populates 5 per-path
  DuckLake tables + 1 voted_canonical row with RAGAS score ≥ 0.70
- **AND** `ireland_lc_mathematics_higher_en_chunks` LanceDB table has ≥ 1000
  chunks
- **AND** `ireland_lc_audit` DuckLake table has 1 audit row
- **AND** `notebooks/19_ireland_pipeline_dashboard.py` shows the Mathematics
  row with RAGAS score ≥ 0.70

### Requirement: 4-path OCR ensemble + RAGAS voting

The system SHALL run all 4 OCR/VLM paths on every BIEP v3 PDF:

1. Docling → BAML (via `BIEPV3Extract`)
2. Docling → Unstract
3. qwen3-vl-8b page-image VLM (via `BIEPV3ExtractStrong`)
4. gemma-4-26B-A4B page-image VLM (via `BIEPV3Vision`)

and SHALL run RAGAS `biiep_extraction_consensus` voting over the 4 outputs.

#### Scenario: AQA GCSE Mathematics spec change re-runs the ensemble

- **WHEN** the `england_aqa_gcse_monitor` ChangeDetection.io sensor fires
- **THEN** the Dagster asset `england_gcse_documents_ingested` re-ingests
- **AND** the 4-path ensemble runs against the new PDF
- **AND** the asset check `england_gcse_extractions_ragas_check` MUST pass
  with `ragas_score >= 0.70`
- **AND** the voted_canonical row is committed to
  `cianfhoghlaim.education.england.gcse.mathematics.voted_canonical`

### Requirement: ibis-first logging contract

The system SHALL reject any raw `duckdb.connect()` call in BIEP v3 paths
(`orchestration/defs/2_materials/{ireland,england}_education/`,
`notebooks/{18-23}_*_pipeline_dashboard.py`,
`motherduck/dives/*_topics.sql`). The canonical entrypoint is:

```python
import ibis
conn = ibis.duckdb.connect("md:cianfhoghlaim")
lance = ibis.lancedb.connect("rest://lakehouse-lance-namespace:8182")
```

#### Scenario: ibis-first contract enforced

- **WHEN** a developer opens a PR that adds `duckdb.connect(...)` to any
  BIEP v3 path
- **THEN** the `dg check yaml` lint SHALL reject the PR
- **AND** the CI gate `mise run biep:v3:lint` SHALL exit non-zero

### Requirement: Per-milestone iteration gates

The system SHALL enforce that M1 (Ireland LC) MUST archive before M2
(Ireland JC) may begin; M2 MUST archive before M3 (England A-Level); M3
MUST archive before M4 (England GCSE).

#### Scenario: M1 must archive before M2 begins

- **WHEN** the operator attempts to start M2 work
- **THEN** the pre-flight check `mise run biep:v3:gate --milestone=m2`
  SHALL fail with the message "M1 has not archived yet"
- **AND** the operator SHALL be required to complete M1's 5-phase pattern
  for all 12 Ireland LC cohorts before M2 begins

### Requirement: BIEP v3 MUST expose its 24 tables via schema_introspect

The system SHALL update `openspec/specs/british-isles-education-pipeline-v3/spec.md`
to reference `notebooks/_shared/schema.py:schema_introspect_full(conn)`
as the canonical way to enumerate the 24 BIEP tables (6 subjects ×
4 tables: `_topics` / `_syllabus` / `_papers` / `_marking`).

#### Scenario: schema_introspect surfaces the 24 BIEP tables

- **GIVEN** the BIEP MotherDuck + DuckLake lakehouse at `md:cianfhoghlaim`
- **WHEN** the operator runs
  `notebooks._shared.schema.schema_introspect_full(connect_md())`
- **THEN** the 24 BIEP tables are surfaced with column metadata
- **AND** the BIEP dashboards (`19_*.py` through `23_*.py`) consume this API

#### Scenario: BIEP v3 connects to the deployment control panel

- **GIVEN** the 5-tab marimo control panel at `notebooks/00_control_panel.py`
- **WHEN** the BIEP v3 operator opens Tab 2 "Pipelines"
- **THEN** the 10 jurisdiction pipelines (`ireland_jurisdiction_pipeline` etc.) appear
- **AND** the operator can toggle each one on/off via `deployment-choice.yaml:enabled_pipelines`

### Requirement: M1-M4 milestones do not trigger deferred L3 assets

The `mise run biep:v3:m0..m4` milestone entrypoints SHALL NOT trigger
any L3 asset that has `automation_condition: Manual()` (the cognify +
federated_ocr subset). This is the canonical BIEP v3 "happy path"
contract — the lakehouse + BIEP layers L1-L2 + L4-L5 are sufficient
for the 12 Ireland LC cohorts + 88 Ireland JC cohorts + 147 England
A-Level + 129 England GCSE assets.

The L3 cognify + federated_ocr assets are reserved for the deferred
deliverables (per the open openspec change
`bring-cognify-stack-to-lakehouse-cluster`).

#### Scenario: M1 (Ireland LC) does not trigger L3 cognify assets

- **WHEN** `mise run biep:v3:m1` runs
- **THEN** the materialisation set contains 12 Ireland LC cohort assets
- **AND** zero `3_model_lifecycle/cognify/*` assets
- **AND** zero `3_model_lifecycle/federated_ocr/*` assets
- **AND** the 3 asset checks (`ireland_lc_documents_ingested_check`, `ireland_lc_extractions_ragas_check`, `ireland_lc_lance_chunks_check`) pass

#### Scenario: M2 (Ireland JC) does not trigger L3 cognify assets

- **WHEN** `mise run biep:v3:m2` runs
- **THEN** the materialisation set contains the 140 Ireland JC cohort assets
- **AND** zero `3_model_lifecycle/cognify/*` assets
- **AND** the milestone exits 0

### Requirement: The 3 L3 cognify assets + 1 L3 federated_ocr asset are documented as deferred

The system MUST document the 3 L3 components (`KCGCognifyComponent`,
`CognifyIngestSensorsComponent`, `CelticFederatedOcrComponent`) in their
respective Component docstrings as "deferred to the cognify stack
bringup openspec change". Operators discover their deferred status via
the new `scripts/dagster_load_smoke.py` companion (which prints the
manual-only badges).

#### Scenario: The L3 cognify assets are tagged manual-only in Dagster

- **WHEN** `dg list defs --json | jq '.[] | select(.key | startswith("3_model_lifecycle/cognify")) | .automation_condition' | sort -u` runs
- **THEN** the output is `["manual"]` (the only automation condition across the cognify assets)

#### Scenario: The L3 federated_ocr asset is tagged manual-only in Dagster

- **WHEN** `dg list defs --json | jq '.[] | select(.key | startswith("3_model_lifecycle/federated_ocr")) | .automation_condition' | sort -u` runs
- **THEN** the output is `["manual"]` (the only automation condition across the federated_ocr assets)

### Requirement: 6 LC subjects × real BAML extraction prompts

The system SHALL replace the stub `"Auto-generated extraction prompt."`
strings with real subject-specific extraction prompts for all 6 LC
subjects × 4 extraction kinds (chemistry, mathematics, geography,
gaeilge, english, computer_science × curriculum_syllabus,
exam_paper_layout, marking_scheme_guideline, syllabus_diagram) =
24 real prompts (per the `2026-08-10-baml-extraction-completion-v1`
change proposal).

Each prompt SHALL follow the canonical `{{ _.role("user") }}` +
`{{ ctx.output_format }}` marker pattern and SHALL pass the
`mise run lint:baml-stub-prompts` lint gate.

#### Scenario: Chemistry syllabus extraction

- **GIVEN** `baml_src/british_isles/ireland/education/lc_extraction/curriculum_syllabus.baml`
  declares `@function ExtractChemSyllabus(text, source_pdf) -> ChemSyllabus`
- **WHEN** the function is invoked against an Ireland LC Chemistry
  syllabus PDF (e.g. `LC022ACS000EV.pdf` or equivalent)
- **THEN** the prompt MUST request chemistry-specific extraction
  (learning outcomes, syllabus topics, experiment descriptions,
  atomic symbols, equation references) — not a generic stub
- **AND** the parsed `ChemSyllabus` Pydantic model MUST have
  non-empty `topics` and `learning_outcomes` arrays

#### Scenario: All 24 prompts are real (no stubs)

- **WHEN** `mise run lint:baml-stub-prompts` runs
- **THEN** all 24 LC subject × extraction kind prompts pass the lint
- **AND** `baml-cli generate --from baml_src` regenerates the 14
  BAML client files successfully

### Requirement: BAML ClientRegistry for OCR ensemble

The OCR ensemble Path 1 (BAML) SHALL use the BAML `ClientRegistry`
pattern (declared in `baml_src/clients.baml`) for primary + fallback
chains per the `baml-schemas` spec added by Mega-6.

#### Scenario: Path 1 primary client fails

- **GIVEN** the OCR ensemble runs Path 1 against an Ireland LC PDF
- **WHEN** the primary client `ExtractorPrimary` (minimax-m3) returns
  a 429 rate-limit error
- **THEN** the BAML runtime MUST automatically retry with
  `ExtractorFallback` (qwen3.7-plus via DashScope token plan)
- **AND** the BAML Collector MUST record both attempts in
  `collector.last.calls` (2 entries)
- **AND** the MLflow experiment `biiep_v3` MUST record both runs
  with token usage metrics

### Requirement: Irish-language BAML client path

The system SHALL use the `gaeilge_lc_client` (routed through
`uccix-mistral-24b` per the `centralized-model-registry` spec) for
the 2 Gaeilge-specific BAML functions:
`ExtractBilingualLearningOutcome` and `ExtractCrossLinguisticGA`.

Per the `meaisinfhoghlaim-ocr-htr` spec, this client is the canonical
Irish-language path; the platform has only `uccix-mistral-24b` as a
dedicated Irish-language model.

#### Scenario: ExtractBilingualLearningOutcome invoked

- **GIVEN** the function is called with an Irish-English bilingual
  curriculum extract
- **WHEN** the function executes
- **THEN** the `gaeilge_lc_client` MUST route to
  `model_for("text_llm", "irish", language="ga")` which resolves to
  `uccix-mistral-24b` per the `meaisinfhoghlaim/models/routing.py`
  IRISH_TEXT_MODEL constant (added by Mega-6 P3.1)
- **AND** the parsed Pydantic model MUST have populated `gaeilge` and
  `english` parallel columns

### Requirement: 7 v1 CocoIndex flows + England priority

The BIEP v3 lakehouse SHALL host 7 v1 CocoIndex flows (6 LC subjects +
`government_circulars`) per the `british-isles-education-pipeline-v3`
spec, plus the England priority factory (added by the
`2026-08-10-england-biiep-pipeline-v1` change).

The England priority factory covers 3 GCSE boards (AQA / OCR / Edexcel)
× ~43 subjects + 3 A-Level boards × ~49 subjects = 276 unwired
CocoIndex Apps, wired via 6 DLT sources + 6 Dagster asset groups.

#### Scenario: 7 v1 CocoIndex flows emit to MotherDuck

- **WHEN** `dagster asset materialize --select ireland_lc_factory --select england_priority_factory` runs
- **THEN** the 6 Ireland LC flows emit rows to
  `md:cianfhoghlaim.education.british_isles.ireland.lc.{subject}.{lang}`
- **AND** the England priority flow emits rows to
  `md:cianfhoghlaim.education.british_isles.england.{stage}.{board}.{subject}`
- **AND** the `government_circulars` flow emits rows to
  `md:cianfhoghlaim.education.ie.gov_circulars_archive`

### Requirement: 4 MotherDuck Dives + daily Flight

The BIEP v3 lakehouse SHALL host the 4 canonical MotherDuck Dives
(`lc_syllabus_topics`, `lc_exam_difficulty`, `lc_marking_complexity`,
`gov_circulars_archive`) + the daily `lc_pdf_sync_flight` per the
`british-isles-education-pipeline-v3` spec.

#### Scenario: 4 Dives are live

- **WHEN** MotherDuck `md:cianfhoghlaim` is opened in the BIEP portal
- **THEN** the 4 Dives return live query results (not stale cache)
- **AND** the daily `lc_pdf_sync_flight` ran within the last 24 hours

### Requirement: BIEP v3 lineage viewer SSE streaming

The system SHALL expose a Server-Sent Events (SSE) streaming endpoint
at `/api/lineage/stream` that streams BAML `@@stream.done` outputs
from the 5 lc6 extraction functions to the BIEP v3 lineage viewer
in real-time (per the 2026-08-26-mega-3a-baml-and-adk-v1 change
D.7).

#### Scenario: SSE endpoint streams BAML extraction progress

- **GIVEN** the operator starts a BAML extraction pipeline for an NCCA PDF
- **WHEN** the lineage viewer opens `/api/lineage/stream?source_pdf=<path>`
- **THEN** the endpoint streams `data: { stage: "extract_curriculum",
  status: "in_progress", progress: 0.25 }` events as the extraction progresses

### Requirement: Marimo `mo.ui.code_editor` for the BAML prompt editor

The system SHALL use `mo.ui.code_editor(...)` to allow the operator
to edit the BAML extraction prompt at runtime.

#### Scenario: The operator edits the prompt

- **GIVEN** a BIEP v3 dashboard
- **WHEN** the operator clicks the "Edit Prompt" button
- **THEN** the dashboard renders a `mo.ui.code_editor` with the
  current BAML prompt + a "Save" button

### Requirement: Marimo `mo.ui.table` for the lineage view

The system SHALL use `mo.ui.table(...)` to display the lineage
metadata in a tabular form (per the lineage viewer requirement).

#### Scenario: The lineage table renders

- **GIVEN** a BAML extraction has produced 100 lineage rows
- **WHEN** the lineage viewer opens
- **THEN** the dashboard renders a `mo.ui.table` with the 100 rows

### Requirement: Marimo `mo.ui.slider` for the RAGAS threshold tuner

The system SHALL use `mo.ui.slider(...)` to allow the operator to
tune the RAGAS threshold (per the 4 stage dashboard adoption).

#### Scenario: The operator tunes the threshold

- **GIVEN** a BIEP v3 dashboard
- **WHEN** the operator clicks the "Tune Threshold" button
- **THEN** the dashboard renders a `mo.ui.slider` with the current
  threshold + a "Save" button

## Cross-references

- `british-isles-education-pipeline` (v1) — the legacy 6-subject Ireland LC spec
- `british-isles-education-pipeline-v2` (v2) — the 4-jurisdiction umbrella (LC + JC + A-Level + GCSE)
- `cross-region-pipeline` — the canonical snake_case + source_id + DuckLake namespace contract
- `dagster-5-layer-component-architecture` — the canonical 5-layer Dagster pattern
- `openbis-8-jurisdictions` — the BIEP v3 8-jurisdiction spec (proposed in Phase 7)
- `openspec/changes/2026-08-13-biep-v3-systematic-download-ireland-england-v1/` — the umbrella change
- `openspec/changes/2026-07-30-biep-v3-sct-wls-ni-v1/` — Scotland + Wales + NI
- `openspec/changes/2026-07-31-biep-v3-crown-dependencies-v1/` — Jersey + Guernsey + IoM
- `openspec/changes/2026-08-13-biep-v3-filesystem-and-language-pipelines-v1/` — filesystem + language
- `docs/agents/biiep-v3-systematic-download.md` — the canonical newcomer guide
- `docs/agents/biiep-v3-quickstart.md` — the "first 30 minutes" guide
- `docs/agents/biiep-v3-faq.md` — the canonical FAQ
- `docs/agents/biiep-v3-baml-client.md` — how to invoke the 6 new Extract* functions from Python
- `docs/agents/biiep-v3-storage-layout.md` — the DuckLake + Lance + MotherDuck layout
- `docs/agents/biiep-v3-cron-schedule.md` — the 4-cadence scheduling policy in detail
- `docs/agents/biiep-v3-bie-8-jurisdictions.md` — the 8-jurisdiction rollout + the 2 scanner domains
