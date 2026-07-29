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
