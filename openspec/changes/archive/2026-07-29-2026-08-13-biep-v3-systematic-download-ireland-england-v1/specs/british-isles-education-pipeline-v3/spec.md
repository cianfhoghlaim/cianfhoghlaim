# British-Isles Education Pipeline v3 Capability

## Purpose

`british-isles-education-pipeline-v3` (BIEP v3) is the umbrella capability
that systematically downloads, extracts, embeds, logs, and validates
British Isles education curricula for **Ireland (Leaving Cycle + Junior
Cycle, English + Gaeilge)** and **England (AQA + OCR + Edexcel × A-Level +
GCSE, English)** — landing every artifact into the local lakehouse (Garage
S3 + DuckLake + Lakekeeper Iceberg REST + Lance REST namespace) with
snake_case schemas, ibis-first logging, and 4-path OCR ensemble + RAGAS
voting.

This spec **supersedes** `british-isles-education-pipeline` (v1) and
`british-isles-education-pipeline-v2` (v2) as the canonical umbrella for
new BIEP coverage work. The v1 and v2 specs remain in place for historical
reference but new BIEP coverage MUST be authored against this v3 spec.

## Source code anchors

- `dlt_sources/british_isles/ireland/education/` — NCCA + SEC + gov.ie DLT sources
- `dlt_sources/british_isles/england/education/` — AQA + OCR + Edexcel DLT sources
- `baml_src/british_isles/ireland/education/` — BAML extraction schemas
- `baml_src/british_isles/england/education/` — BAML extraction schemas
- `orchestration/defs/2_materials/ireland_education/` — Ireland Dagster assets
- `orchestration/defs/2_materials/england_education/` — England Dagster assets
- `meaisinfhoghlaim/ocr/ensemble/` — 4-path OCR ensemble
- `cocoindex/biep_parity/` — CocoIndex v1 Apps
- `notebooks/{18-23}_*_pipeline_dashboard.py` — marimo dashboards
- `motherduck/dives/` — MotherDuck Dives
- `bonneagar/stacks/lakehouse/` — Garage + Lakekeeper + Lance-namespace stack
- `orchestration/automation/biiep_daily_automation.py` — daily automation

## ADDED Requirements

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

## Cross-references

- `british-isles-education-pipeline` (v1) — the legacy umbrella; this v3 spec
  supersedes it for new BIEP coverage work
- `british-isles-education-pipeline-v2` (v2) — the BIEP v2 umbrella; this v3
  spec supersedes it for the 4-path OCR ensemble + RAGAS voting contract
- `cross-region-pipeline` — the canonical snake_case file naming + source_id
  + DuckLake namespace contract (modified by this change to add the
  `dlt_sources/british_isles/` post-v7 path variant)
- `dagster-5-layer-component-architecture` — the 5-layer DAG component
  architecture (modified by this change to add the BIEP v3 2-axis
  `scope × year` partition)
- `meaisinfhoghlaim-ocr-htr` — the OCR backend registry (4-path ensemble
  uses the 6-backend registration)
- `motherduck-dive` — the MotherDuck Dive authoring contract
- `infrastructure-stacks` — the 88-stack IaC catalogue (the lakehouse stack
  is canonical)
- `agent-observability` — the MLflow + RAGAS + Langfuse observability
  contract (RAGAS voting writes to `biiep_v3` experiment)
