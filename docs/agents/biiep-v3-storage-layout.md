# BIEP v3 — Storage Layout (the DuckLake + Lance + MotherDuck + BAML + Dagster canonical layout)

> Per the `2026-08-13-biep-v3-systematic-download-ireland-england-v1`
> openspec change. The canonical BIEP v3 storage layout for operators.

## Overview

The BIEP v3 systematic download plan stores data across 4 layers:

1. **Lakehouse Stack** (Bonneagar / Docker Compose) — Garage S3 + Lakekeeper Iceberg REST + Lance namespace + DuckLake Postgres
2. **DuckLake + DuckDB** — analytical OLAP queries (columnar Parquet on S3 + Postgres catalog)
3. **LanceDB** — vector embeddings (BAAI/bge-m3 1024-d, BGE-M3 multilingual)
4. **MotherDuck** — live dashboards + scheduled flights
5. **Dagster** — orchestration + assets + checks + sensors
6. **BAML** — type-safe LLM extraction (6 new Extract* functions)
7. **CocoIndex v1** — file → chunk → embed → LanceDB pipeline

## Layer 1: Lakehouse Stack (Bonneagar / Docker Compose)

The 13 lakehouse services run via `docker compose -f
bonneagar/stacks/lakehouse/compose.yaml up -d`:

| Service | Port | URL | Purpose |
|:--|--:|:--|:--|
| Garage S3 | 3900 | `http://localhost:3900` | S3-compatible object storage (Parquet + PDF cache) |
| Garage-admin | 3903 | `http://localhost:3903` | S3 admin UI |
| Lakekeeper Iceberg REST | 8181 | `http://localhost:8181` | Apache Iceberg REST catalog |
| Lakekeeper-metrics | 9100 | `http://localhost:9100` | Prometheus metrics |
| Lance namespace | 8182 | `http://localhost:8182` | LanceDB REST namespace (proxies Lakekeeper) |
| Postgres (Lakekeeper) | 5433 | `postgresql://lakekeeper:devpassword@localhost:5433/ducklake_cianfhoghlaim` | DuckLake metadata catalog |
| ClickHouse | 8123 | `http://localhost:8123/ping` | OLAP analytics |
| Redis | 6379 | `redis://localhost:6379` | Cache |
| Nimtable | 3018 | `http://localhost:3018` | Iceberg UI |
| Olake | admin | n/a | CDC engine |
| LanceDB Viewer | 8081 | `http://localhost:8081` | LanceDB schema viewer |
| Garage-init | n/a | one-shot | Create 7 S3 buckets (iceberg + lance + ducklake + langfuse-events + langfuse-media + langfuse-exports + mlflow-artifacts) |
| Lakekeeper-migrate | n/a | one-shot | Run Lakekeeper migrations |

## Layer 2: DuckLake + DuckDB (analytical OLAP)

The canonical DuckLake URI is `md:cianfhoghlaim` (MotherDuck + DuckLake).
The local fallback is `ducklake:postgres:dbname=ducklake_cianfhoghlaim
host=localhost port=5433 user=lakekeeper password=<env>`.

### DuckLake namespaces (per the BIEP v3 systematic download plan)

```text
md:cianfhoghlaim.education.<jurisdiction>.<stage>.<subject>.<level>_<lang>.baml_canonical
md:cianfhoghlaim.education.<jurisdiction>.<stage>.<subject>.<level>_<lang>.unstract_json
md:cianfhoghlaim.education.<jurisdiction>.<stage>.<subject>.<level>_<lang>.qwen3_vl
md:cianfhoghlaim.education.<jurisdiction>.<stage>.<subject>.<level>_<lang>.gemma4
md:cianfhoghlaim.education.<jurisdiction>.<stage>.<subject>.<level>_<lang>.voted_canonical
md:cianfhoghlaim.education.filesystem._audit.daily_sync_status
md:cianfhoghlaim.education.language._audit.daily_sync_status
md:cianfhoghlaim.education.ireland._audit.daily_sync_status
md:cianfhoghlaim.education.england._audit.daily_sync_status
md:cianfhoghlaim.education.scotland._audit.daily_sync_status
md:cianfhoghlaim.education.wales._audit.daily_sync_status
md:cianfhoghlaim.education.northern_ireland._audit.daily_sync_status
md:cianfhoghlaim.education.jersey._audit.daily_sync_status
md:cianfhoghlaim.education.guernsey._audit.daily_sync_status
md:cianfhoghlaim.education.isle_of_man._audit.daily_sync_status
```

### Per-jurisdiction stage

| Jurisdiction | Stage (canonical) |
|:--|:--|
| Ireland | `leaving_cycle` (LC) + `junior_cycle` (JC) + `junior_cycle.short_courses` + `junior_cycle.cbas` |
| England | `a_level` + `gcse` |
| Scotland | `national_5` + `higher` + `advanced_higher` |
| Wales | `gcse` + `a_level` |
| Northern Ireland | `gcse` + `a_level` |
| Jersey | `gcse` + `a_level` + `ib` + `french_bac` |
| Guernsey | `gcse` + `a_level` + `ib` + `local` |
| Isle of Man | `gcse` + `a_level` + `ib` + `local` |

## Layer 3: LanceDB (vector embeddings)

The canonical LanceDB namespace is `cianhoghlaim` (created at Lakekeeper
catalog creation). The local fallback is `rest://lakehouse-lance-namespace:8182`.

### LanceDB namespaces

```text
cianhoghlaim.ireland.leaving_cycle.<subject>.<level>_<lang>_chunks
cianhoghlaim.ireland.junior_cycle.<subject>.<year>_<lang>_chunks
cianhoghlaim.england.a_level.<board>.<subject>_a_level_chunks
cianhoghlaim.england.gcse.<board>.<subject>_gcse_chunks
cianhoghlaim.scotland.<level>.<subject>_chunks
cianhoghlaim.wales.<level>.<subject>_chunks
cianhoghlaim.northern_ireland.<level>.<subject>_chunks
cianhoghlaim.jersey.<level>.<subject>_chunks
cianhoghlaim.guernsey.<level>.<subject>_chunks
cianhoghlaim.isle_of_man.<level>.<subject>_chunks
cianhoghlaim.biep.ga.education_chunks
cianhoghlaim.biep.ireland.education_chunks
```

The embedder is `BAAI/bge-m3` (1024-d, multilingual) per the
`orchestration/automation/biiep_scheduling.py` + the
`baml_src/british_isles/_client.biep_clients` setup.

## Layer 4: MotherDuck (live dashboards + scheduled flights)

The MotherDuck service runs at `md:cianfhoghlaim` (same as DuckLake but
read via MotherDuck's query engine). The canonical MotherDuck Dives
are at `motherduck/dives/`. The 14 BIEP v3 Dives are:

1. `ireland_lc_syllabus_topics`
2. `ireland_jc_curriculum_topics`
3. `england_a_level_topics`
4. `england_a_level_complexity`
5. `england_gcse_topics`
6. `england_gcse_complexity`
7. `scotland_curriculum_topics`
8. `wales_curriculum_topics`
9. `northern_ireland_exam_paper_dive`
10. `jersey_curriculum_topics_v2`
11. `guernsey_curriculum_topics_v2`
12. `isle_of_man_curriculum_topics_v2`
13. `filesystem_sources_overview`
14. `language_sources_overview`

The canonical MotherDuck Flights are at `motherduck/flights/`. The 8
BIEP v3 Flights are:

1. `ireland_lc_daily_sync_flight`
2. `ireland_jc_daily_sync_flight`
3. `england_a_level_daily_sync_flight`
4. `england_gcse_daily_sync_flight`
5. `sct_wls_ni_flight` (now calls m5 + m6 + m7)
6. `crown_dependencies_flight` (now calls m8 + m9 + m10)
7. `filesystem_monthly_sync_flight`
8. `language_monthly_sync_flight`

## Layer 5: Dagster (orchestration + assets + checks + sensors)

The canonical Dagster entry point is `orchestration.definitions`
(post-v7 flattened layout, not `orchestration.defs`). The 5 layers
follow the canonical pattern:

- **Layer 1 (Ingestion)**: 200+ DLT sources
- **Layer 2 (Materials)**: 200+ BAML extractions
- **Layer 3 (Model Lifecycle)**: 372+ CocoIndex v1 Apps
- **Layer 4 (Asset Generation)**: 9 marimo dashboards
- **Layer 5 (Agent Ops)**: M0 foundation + 4 M0 assets + 4 M0 checks

The canonical Dagster groups per the BIEP v3 systematic download plan:

- `1_ingestion_education_<jurisdiction>_documents`
- `2_materials_education_<jurisdiction>_extractions`
- `3_model_lifecycle_education_<jurisdiction>_embeddings`
- `1_ingestion_filesystem_documents`
- `2_materials_filesystem_extractions`
- `3_model_lifecycle_filesystem_embeddings`
- `1_ingestion_language_documents`
- `2_materials_language_extractions`
- `3_model_lifecycle_language_embeddings`
- `5_agent_ops_biiep_v3_m0_foundation`

## Layer 6: BAML (type-safe LLM extraction)

The canonical BAML files are at `baml_src/british_isles/<jurisdiction>/education/`.
The 6 new Extract* functions (Phase C) + 8 existing functions
(ExtractCurriculumSyllabus + ExtractJCCurriculum + ExtractJCSubjectSpec
+ ExtractCBADescriptor + ExtractJCShortCourse + ExtractExamPaperLayout
+ ExtractMarkingSchemeGuideline + ExtractPrimaryLearningOutcomes)
+ 3 board-specific functions (ExtractAQAQualSpec + ExtractOCRQualSpec
+ ExtractEdexcelQualSpec) + 1 generic function (ExtractUKQualSpec)
= 18 total functions.

The 3 BIEP v3 canonical BAML clients are:

- `BIEPV3Extract` — the canonical light-weight client (Gemma 3 4B / minimax-m3)
- `BIEPV3ExtractStrong` — the canonical detail-rich text client (Gemma 3 27B)
- `BIEPV3Vision` — the canonical vision client (qwen3-vl-8b via llama-swap)

## Layer 7: CocoIndex v1 (file → chunk → embed → LanceDB)

The canonical CocoIndex v1 Apps are at `cocoindex_flows/biep_parity/`. The 372+
Apps are:

- 8 BIEP v3 Ireland apps (6 LC × 2 langs + 1 Gaeilge + 1 parity)
- 88 Ireland JC apps (18 subjects × 2 langs + 16 short + 36 CBA)
- 2 BIEP v3 parity apps (`ga_education_embedding` + `ireland_education_embedding`)
- 147 England A-Level apps (49 × 3 boards)
- 129 England GCSE apps (43 × 3 boards)
- 6 BIEP v1 parity apps (en + ni + sct + wls + guernsey + jersey + isle_of_man)

## See also

- `docs/agents/biiep-v3-systematic-download.md` — the canonical newcomer guide
- `docs/agents/biiep-v3-quickstart.md` — the "first 30 minutes" guide
- `docs/agents/biiep-v3-faq.md` — the canonical FAQ
- `docs/agents/biiep-v3-baml-client.md` — how to invoke the 6 new Extract* functions from Python
- `docs/agents/biiep-v3-cron-schedule.md` — the 4-cadence scheduling policy in detail
- `docs/agents/biiep-v3-bie-8-jurisdictions.md` — the 8-jurisdiction rollout + the 2 scanner domains
