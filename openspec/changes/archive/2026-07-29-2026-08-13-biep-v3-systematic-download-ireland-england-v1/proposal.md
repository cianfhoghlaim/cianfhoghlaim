# BIEP v3 — Systematic Download & Iteration: Ireland + England

## Purpose

This change systematically downloads, extracts, embeds, logs, and validates
the British Isles education curricula for **Ireland (Leaving Cycle + Junior
Cycle, English + Gaeilge)** and **England (AQA + OCR + Edexcel × A-Level +
GCSE, English)** — landing every artifact into the local lakehouse (Garage
S3 + DuckLake + Lakekeeper Iceberg REST + Lance REST namespace) with
snake_case schemas, ibis-first logging, and 4-path OCR ensemble + RAGAS
voting.

The change executes one pipeline at a time, runs each pipeline through its
acceptance gates, iterates, and only then proceeds to the next. It is
structured so any milestone can pause/resume without stranding the others.

This change is the **canonical umbrella for new BIEP coverage work** and
**supersedes** `british-isles-education-pipeline` (v1) and
`british-isles-education-pipeline-v2` (v2) as the authoritative home for
the 6 ADDED Requirements introduced here.

## Scope

| Dimension | In scope |
|:--|:--|
| Jurisdictions | Ireland (LC + JC), England (AQA + OCR + Edexcel) |
| Languages (Ireland) | English (en), Gaeilge (ga) |
| Languages (England) | English (en) only |
| Stages | Leaving Cycle, Junior Cycle, A-Level, GCSE |
| Cohorts | 12 (LC) + 140 (JC) + 147 (England A-Level) + 129 (England GCSE) = **428 cohorts** |
| OCR ensemble | 4 paths (Docling→BAML, Docling→Unstract, qwen3-vl-8b, gemma-4-26B-A4B) + RAGAS voting |
| Storage | Local lakehouse (Garage S3 + DuckLake + Lakekeeper + Lance namespace) |
| Iteration | One milestone at a time; test, improve, archive, then next milestone |

Out of scope (deferred to a follow-up change):

- Scotland (SQA), Wales (WJEC), Northern Ireland (CCEA)
- Crown Dependencies (Jersey, Guernsey, Isle of Man)
- Scots Gaelic / Welsh language variants in the England pipeline
- Cloudflare R2 production deployment (this change is local-lakehouse only)

## Milestones

| ID | Title | Cohorts | Test gate |
|:--|:--|--:|:--|
| **M0** | Foundation unblock | 0 | `lakehouse_smoke_test`, `baml_codegen_gate`, `registry_seed_count >= 210`, `lance_namespace_ready` |
| **M1** | Ireland Leaving Cycle (EN+GA) | 12 | `ireland_lc_documents_ingested >= 12`, `ireland_lc_extractions_ragas >= 0.70`, `ireland_lc_lance_chunks >= 12_000` |
| **M2** | Ireland Junior Cycle (EN+GA) | 88 | `ireland_jc_documents_ingested >= 88`, `ireland_jc_extractions_ragas >= 0.65`, `ireland_jc_lance_chunks >= 88_000` |
| **M3** | England A-Level (AQA + OCR + Edexcel) | 147 | `england_a_level_documents_ingested >= 147`, `england_a_level_extractions_ragas >= 0.70`, `england_a_level_lance_chunks >= 147_000` |
| **M4** | England GCSE (AQA + OCR + Edexcel) | 129 | `england_gcse_documents_ingested >= 129`, `england_gcse_extractions_ragas >= 0.70`, `england_gcse_lance_chunks >= 129_000` |

**Cohort arithmetic:**

- Ireland LC: 6 subjects × 2 langs = 12 cohorts
- Ireland JC: 18 subjects × 2 langs (36 specs) + 16 short courses + 36 CBAs = 88 cohorts
- England A-Level: 49 subjects × 3 boards (AQA + OCR + Edexcel) = 147 cohorts
- England GCSE: 43 subjects × 3 boards = 129 cohorts
- **Total: 428 cohorts** across the 4 jurisdiction pipelines

Milestones are **strictly sequential**: M0 → M1 → M2 → M3 → M4. Each
milestone has an explicit "must archive before next" gate in the
`british-isles-education-pipeline-v3` spec.

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

## The 5 milestones in detail

### M0 — Foundation unblock

The 26 BIEP-related openspec changes that are currently `0/N tasks complete`
have left the codebase in a stub state. M0 unblocks the foundation:

1. Archive `2026-08-01-biep-v3-dlt-jurisdiction-pipeline-bugfix-v1` (the A1
   blocker — gates every jurisdiction pipeline at module load).
2. Fix the broken `from ..storage.ducklake_client import DuckLakeClient`
   import at `orchestration/resources.py:300` (the `storage/` directory
   does not exist post-v7).
3. Add the missing `IcebergCatalogResource` (PyIceberg 0.11.1 wrapper),
   `LanceNamespaceResource` (Lance REST namespace wrapper), and fix the
   `LanceDBResource` embedder from `paraphrase-multilingual-MiniLM-L12-v2`
   (384-d) to `BAAI/bge-m3` (1024-d).
4. Add the canonical 3 BAML clients (`BIEPV3Extract`,
   `BIEPV3ExtractStrong`, `BIEPV3Vision`).
5. Add the missing `ExtractUKQualSpec`, `ExtractSyllabusDiagram`, and
   `ExtractCrossLinguisticConcept` BAML functions (currently only their
   classes exist; the functions are referenced but not declared).
6. Bring the lakehouse stack up (`docker compose -f
   bonneagar/stacks/lakehouse/compose.yaml up -d`) — 13 services.
7. Seed the British Isles Subject Registry to ≥210 rows for Ireland +
   England (currently returns only 4 rows).
8. Create the `cianhoghlaim` Lance namespace in the Lakekeeper catalog.
9. Standardise the snake_case file naming contract and the metadata sidecar
   schema.

**M0 acceptance gate:**

```bash
mise run lakehouse:up
bun run scripts/smoke_test_lakehouse.sh      # all 13 services 200 OK
mise run baml:generate                        # exit 0
mise run registry:seed                        # ≥210 rows
mise run dagster:oideachais -- --select lakehouse_smoke_test,baml_codegen_gate,registry_seed_count,lance_namespace_ready
# All 4 assets materialise within 30s; all 4 asset_checks pass
```

### M1 — Ireland Leaving Cycle (12 cohorts)

For each of the 6 LC subjects (Mathematics, Chemistry, Geography, Gaeilge,
English, Computer Science) in both EN and GA, the 5-phase pattern runs:

| Phase | Asset | Snake_case output |
|:--|:--|:--|
| A. Ingestion | `ireland_lc_<subject>_<level>_<lang>_documents_ingested` | `s3://garage/cianfhoghlaim/ireland/leaving_cycle/<subject>/<lang>/<year>/<file>.pdf` + sibling `.meta.json` |
| B. Extraction | `ireland_lc_<subject>_<level>_<lang>_extractions` (4 OCR paths + RAGAS voting) | `cianfhoghlaim.education.ireland.leaving_cycle.<subject>.{baml_canonical, unstract_json, qwen3_vl, gemma4, voted_canonical}` |
| C. Embedding | CocoIndex v1 App `ireland_lc_<subject>_<level>_<lang>_embedding` | `cianhoghlaim.lc.<subject>.<level>_<lang>_chunks` LanceDB table |
| D. ibis logging | `ireland_lc_audit` DuckLake table | 1 audit row per cohort |
| E. Analytics | `notebooks/19_ireland_pipeline_dashboard.py` | per-cohort matrix + RAGAS histogram |

**M1 acceptance gate:**

```bash
mise run dagster:oideachais -- --select ireland_lc_documents_ingested
# Asset check ireland_lc_documents_ingested_check must pass with cohort count >= 12
# Asset check ireland_lc_extractions_ragas_check must pass with score >= 0.70
# Asset check ireland_lc_lance_chunks_check must pass with chunk count >= 12_000

marimo run notebooks/19_ireland_pipeline_dashboard.py
# Notebook renders 12-row cohort matrix; no raw duckdb.connect() in source

grep -rE "duckdb\.connect\(" orchestration/defs/2_materials/ireland_education/ | wc -l
# Returns 0
```

### M2 — Ireland Junior Cycle (140 cohorts)

For each of the 18 JC subjects + 16 short courses + 36 CBAs in both EN and
GA, the 5-phase pattern runs. The BAML functions are `ExtractJCCurriculum`,
`ExtractJCSubjectSpec`, `ExtractCBADescriptor`, `ExtractJCShortCourse`,
`ExtractJCExamPaper`.

### M3 — England A-Level (147 cohorts)

For each of the 49 A-Level subjects × 3 boards (AQA + OCR + Edexcel), the
5-phase pattern runs. The BAML function is `ExtractUKQualSpec(board:
ExamBoard, ...)`. Per-board CocoIndex Apps:
`england_aqa_<subject>_a_level_embedding`,
`england_ocr_<subject>_a_level_embedding`,
`england_edexcel_<subject>_a_level_embedding`.

### M4 — England GCSE (129 cohorts)

For each of the 43 GCSE subjects × 3 boards, the 5-phase pattern runs.
Per-board CocoIndex Apps:
`england_aqa_<subject>_gcse_embedding`,
`england_ocr_<subject>_gcse_embedding`,
`england_edexcel_<subject>_gcse_embedding`.

## Cross-cutting contracts (apply to ALL milestones)

### Snake_case file naming

Every PDF and metadata sidecar lands at:

```text
s3://garage/cianfhoghlaim/<jurisdiction>/<stage>/<subject_slug>/<language>/<year_or_undated>/<jurisdiction>__<stage>__<subject_slug>__<board_or_na>__<qual_level_or_untiered>__<language>__<year_or_undated>__<sha256[0:8]>.pdf
```

with a sibling `<file>.meta.json` sidecar carrying the metadata fields
(source_id, jurisdiction, stage, subject_slug, board, qualification_level,
language, year, source_url, crawled_at, byte_size, page_count,
content_hash_sha256, publisher).

### DuckLake namespace

Every BIEP cohort writes to one DuckLake namespace:

```text
cianfhoghlaim.education.<jurisdiction>.<stage>.<subject_slug>[.<variant>]
```

Per-path OCR ensembles land in:

```text
cianfhoghlaim.education.<jurisdiction>.<stage>.<subject_slug>.<baml_canonical|unstract_json|qwen3_vl|gemma4|voted_canonical>
```

### LanceDB namespace

Every BIEP chunked cohort writes to one LanceDB table:

```text
cianhoghlaim.<jurisdiction>.<stage>.<subject_slug>.<level>_<lang>_chunks
```

### ibis-first logging

Every Dagster asset, every marimo notebook, every MotherDuck Dive uses
ibis exclusively. The raw `duckdb.connect()` call is **forbidden** in
BIEP v3 paths. The canonical entrypoint:

```python
import ibis
conn = ibis.duckdb.connect("md:cianfhoghlaim")
lance = ibis.lancedb.connect("rest://lakehouse-lance-namespace:8182")
```

### 4-path OCR ensemble + RAGAS voting

Every PDF is processed by all 4 paths:

1. Docling → BAML (via `BIEPV3Extract`)
2. Docling → Unstract
3. qwen3-vl-8b page-image VLM (via `BIEPV3ExtractStrong`)
4. gemma-4-26B-A4B page-image VLM (via `BIEPV3Vision`)

RAGAS `biiep_extraction_consensus` voting writes the consensus row to
`cianfhoghlaim.education.<jurisdiction>.<stage>.<subject>.voted_canonical`.
The asset check `ragas_score >= 0.70` MUST pass before the voted row is
committed.

### Daily automation

`AutomationCondition.cron("@daily")` on each partitioned ingestion root:

- `ireland_leaving_cycle_documents_ingested` — 02:00 UTC
- `ireland_junior_cycle_documents_ingested` — 02:30 UTC
- `england_a_level_documents_ingested` — 03:00 UTC
- `england_gcse_documents_ingested` — 03:30 UTC

### Per-subject backfill jobs

Per-subject backfill jobs (`ireland_lc_mathematics_backfill_job`,
`england_aqa_gcse_mathematics_backfill_job`, etc.) are defined for **on-demand
trigger only** (no weekly cron; the daily automation covers the steady
state, and on-demand backfill is for incomplete or failed cohorts).

## Runbook

The 5-phase pattern operates identically across all 4 jurisdiction
pipelines. The per-milestone runbook:

1. **Resolve the milestone's M0 dependencies first** (registry seed + lakehouse
   smoke test + BAML clients loaded).
2. **Run the milestone's 5 phases in order**:
   - Phase A (Ingestion): `mise run dagster:oideachais -- --select
     <milestone>_documents_ingested_<subject>_<lang>`
   - Phase B (Extraction): `mise run dagster:oideachais -- --select
     <milestone>_extractions_<subject>_<lang>`
   - Phase C (Embedding): `mise run dagster:oideachais -- --select
     <milestone>_embeddings_<subject>_<lang>`
   - Phase D (ibis audit): automatic via asset dependency on AssetCheck
   - Phase E (Analytics): `marimo run notebooks/<N>_<milestone>_dashboard.py`
3. **Verify the 3 milestone-level asset checks**:
   - `<milestone>_documents_ingested_check` (cohort count >= N)
   - `<milestone>_extractions_ragas_check` (score >= 0.70)
   - `<milestone>_lance_chunks_check` (chunk count >= N * 1000)
4. **Verify the ibis-first contract**: `grep -rE "duckdb\.connect\("
   orchestration/defs/2_materials/<milestone>/ | wc -l` returns 0.
5. **If any gate fails, iterate**: read the Dagster run log, fix the
   specific code path, re-run the failing phase, re-verify the gate.
6. **Repeat for each cohort** until the full milestone's cohort count is
   reached.
7. **Once all gates pass and the milestone dashboard renders the full
   cohort matrix, archive the milestone** by checking all the tasks.md
   boxes for that milestone and running `openspec archive <change-id> --yes`
   (note: the parent change archives only after M4 completes; per-milestone
   archive is a separate mise `biep:v3:<milestone>:archive` task).
8. **Move to the next milestone** only after the prior one archives.

## Mise task aliases (new)

The change adds the following `mise run` aliases (to be added to
`mise.toml` under a new `[tasks.biep.v3]` section as part of task M0.12):

```toml
[tasks.biep]
[tasks.biep.v3]
[tasks.biep.v3.m0]
run = "bun run scripts/m0_foundation_unblock.ts"
description = "Foundation unblock (lakehouse + BAML + registry + namespace)"
[tasks.biep.v3.m1]
run = "bun run scripts/m1_ireland_lc.ts"
description = "Ireland LC pipeline (12 cohorts, EN+GA)"
[tasks.biep.v3.m2]
run = "bun run scripts/m2_ireland_jc.ts"
description = "Ireland JC pipeline (140 cohorts, EN+GA)"
[tasks.biep.v3.m3]
run = "bun run scripts/m3_england_a_level.ts"
description = "England A-Level pipeline (147 cohorts)"
[tasks.biep.v3.m4]
run = "bun run scripts/m4_england_gcse.ts"
description = "England GCSE pipeline (129 cohorts)"
[tasks.biep.v3.gate]
run = "bun run scripts/milestone_gate.ts"
description = "Verify the active milestone's 3 asset checks pass"
[tasks.biep.v3.lint]
run = "grep -rE 'duckdb\\.connect\\(' orchestration/defs/2_materials/{ireland,england}_education/ | wc -l"
description = "ibis-first contract lint (0 = pass)"
```

## Backfill cadence

Per-subject backfill jobs are **on-demand only** (no automatic cron) — the
operator triggers `mise run dagster:oideachais -- --select
<job_name>` when a cohort is incomplete or a BAML schema change requires
re-extraction. The daily automation cron handles the steady state.

## Dependencies

`Blocked by: 2026-08-01-biep-v3-dlt-jurisdiction-pipeline-bugfix-v1` (A1 — must archive before M0 begins)

`Blocked by (soft):`

- `2026-07-26-biep-v3-root-namespace-rename-v1` (Phase 0 — namespace canonical)
- `2026-07-27-biep-v3-canonical-registry-v1` (Phase 1 — registry seed ≥210 rows)
- `2026-07-28-biep-v3-ireland-full-coverage-v1` (Phase 2 — Ireland registry)
- `2026-07-29-biep-v3-england-full-coverage-v1` (Phase 3 — England registry)
- `2026-08-04-lakehouse-storage-cleanup-v1` (lakehouse stack smoke-tested)
- `2026-08-06-biep-v3-critical-path-fixes-v1` (10 silent failures)
- `2026-08-07-biep-v3-hardening-v1` (canonical BAML clients)

`Affected repos: cianfhoghlaim` (single-repo post-v7)

This change CANNOT archive until M4 (the last milestone) archives. Per-milestone
archives are tracked via the `mise run biep:v3:m<N>:archive` task and
maintained as separate openspec changes (or sub-archives of this umbrella
change).

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
