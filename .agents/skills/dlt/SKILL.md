---
name: dlt
description: Master routing skill for data load tool (dlt 1.28.1, June 2026). Use this to understand dlt rules, decide which sub-skill to invoke, and apply the Cianfhoghlaim dlt conventions (DuckLake/DuckDB destination, USE_LOCAL_SCRAPES offline fallback, relative imports only, type-safe BAML-driven pipelines, multi-destination fan-out to LanceDB / Memgraph / Graphiti, and Dagster dlt_assets wrapping). Powers the British-Isles Education pipeline (6 LC subjects + gov.ie circulars). Notes the 1.27 `dlt[hub]` plugin split and the 1.28 `refresh` > `replace` deprecation.

## What's new in 2026-08/09

This skill was refreshed as part of the 2026-08-23 omnibus skill refresh
(per the  change). Key
updates:

- **2026-08 tooling**: aligned with the latest versions of upstream
  libraries (per the dev-tooling version-pinning change)
- **2026-08 patterns**: documented new features surfaced via the
  Phase 3 (surfaces round) refactor
- **Cross-references**: linked to adjacent skills (per the AGENTS.md
  dispatch matrix)

See the linked spec changes for full details.

---

# DLT Master Router & Rules (Cianfhoghlaim)

You are operating within the `cianfhoghlaim` stack which uses `dlt`
(data load tool) for extracting and loading data. This skill is the
**router + decision tree + project rules** for all dlt operations.

## 1.1 Live version (verified 2026-06-29)

- **Latest**: `dlt 1.28.1` (released **Jun 19, 2026**) on PyPI.
- **Python**: `requires-python = ">=3.10, <3.15"` — Python 3.9 dropped in
  1.28.1; Python 3.14 supported (experimental).
- **Source count**: **8,000+ sources** (was 5,000+ in Wave 1).
- **Yanked**: 1.27.0 and 1.27.1 — data-loss bug ("incremental merge
  truncates destination table"). Pin `dlt>=1.27.2,<1.28` if you must, or
  upgrade to 1.28.1.
- **CLI split (1.27.0)**: `pip install dlt[hub]` is now required for
  `dlt dashboard`, `dlt pipeline ... show`, `dlt pipeline ... mcp`. `dlt ai`
  is now `dlthub ai`.
- **`refresh` > `replace` (1.28.0)**: the `replace` write-disposition
  switch is deprecated; use the `refresh` parameter instead.
- **Lance destination (1.25.0)** + **Lance REST Namespace (1.27.0)**: a
  `lance` destination now exists alongside `lancedb` — use the former
  for local/S3/Az/GCS Lance files, the latter for LanceDB Cloud.
- **Native Polars (1.27.0)**: `@dlt.resource` can yield Polars DataFrame
  or LazyFrame directly (auto-routed through Arrow).
- **Databricks Zerobus (1.27.0)**: `databricks_adapter(...,
  insert_api="zerobus")`.
- **`dlt.Relation.join(...)` (1.26.0)** and **`dlt.current.interval()`
  (1.26.0)** for relational composition and time-windowed incrementals.

## 1. Project rules (PRESERVED from the original skill, with one fix)

When assuming the `data-engineer` persona, use these rules:

- **Destinations**: `dlt.pipeline(..., destination="ducklake")` for
  production (MotherDuck / DuckLake) or `destination="duckdb"` for
  local dev. Set `USE_DUCKLAKE=true` to switch to MotherDuck.
- **Tests**: disable plugins during testing by setting
  `DLT_DISABLE_PLUGINS=true`.
- **Canonical env vars** (per the 2026-08-01-lakehouse-and-reproducible-deploy-v1
  openspec change — now exported by all 5 data-plane stacks
  `secrets.env`):
  - `USE_DUCKLAKE` (default `true`) — switch to MotherDuck
  - `USE_LOCAL_SCRAPES` (default `true`) — offline fallback
  - `MOTHERDUCK_TOKEN` (resolved from `infisical://dev-baile/motherduck/token`)
  - `MOTHERDUCK_MODE` (default `byob`)
  - `MOTHERDUCK_DATABASE` (default `cianfhoghlaim`)
  - `MOTHERDUCK_S3_BUCKET` (default `ducklake-cianfhoghlaim`)
  - `MOTHERDUCK_S3_ENDPOINT` (default `http://lakehouse-garage:3900`)
  - `DUCKLAKE_BUCKET` (default `ducklake-cianfhoghlaim`)
  - `CIANFHOGHLAIM_EMBED_MODEL` (default `BAAI/bge-m3`)
  - `CIANFHOGHLAIM_EMBED_DIM` (default `1024`)
- **Source location**: `dlt_sources` lives at `dlt_sources/`
  (NOT `data_platform/dlt_sources/`, which is a deprecated
  path mentioned in the old skill; NOT `dlt/`,
  which was the pre-v4 path).
- **Imports**: All `cianfhoghlaim.data_platform...` absolute imports have
  been removed; use relative or local `dlt_sources` imports
  (e.g. `from cianfhoghlaim.dlt.british_isles.ireland.education.ncca...`).
- **Offline fallback**: `USE_LOCAL_SCRAPES=true` routes extraction
  to `stedding/ingest_queue/` (the curated local cache) instead of
  live web scraping (avoids API rate limits and credit drain).
- **Absolute namespaces** (per project AGENTS.md): NEVER import
  `cianfhoghlaim.data_platform...` from within the data platform — use
  relative imports.
- **Ingestion cache** (per project AGENTS.md): Test with
  `USE_LOCAL_SCRAPES=true` before live web scraping to avoid API
  rate limits.

## 2. Decision tree → sub-skill or reference

When tasked with dlt operations or data exploration, use this
guide to invoke the most appropriate resource:

### Data exploration & notebooks (notebooks/)

- **`explore-data`**: Use to analyze datasets and create an
  `analysis_plan.md` artifact
- **`build-notebook`**: Use to assemble or regenerate a marimo
  notebook from an `analysis_plan.md`

### Pipeline creation & maintenance

- **`create-filesystem-pipeline`**: Use to build pipelines that read
  from local files. Highly relevant for the `USE_LOCAL_SCRAPES`
  offline fallback pattern
- **`add-incremental-loading`**: Use to add state and incremental
  extraction to a filesystem pipeline
- **`create-rest-api-pipeline`**: Use for generic REST / HTTP API
  sources
- **`dlt-init-openapi`** (3rd-party): Use to auto-generate a verified
  dlt source from any OpenAPI spec
- **`dlt init <verified-source>`** (1.28+ recommended): For any of the
  28 verified sources listed at
  `https://dlthub.com/docs/dlt-ecosystem/verified-sources` (Airtable,
  GitHub, Stripe, Notion, Postgres replication, MongoDB, Salesforce,
  HubSpot, Kafka, Slack, etc.). Verified sources are downloaded into
  the working directory.

### Type-safe pipelines (BAML → dlt)

- **`baml-dlt-integration`** — see `references/type-safe-pipeline.md`
  for the canonical BAML → Pydantic → `columns=...` pattern

### Destinations

- **LanceDB** — see `references/destinations-lancedb.md` (the
  `lancedb_adapter(source, embed=[...])` pattern)
- **Cognee + Memgraph** — see
  `references/destinations-cognee-memgraph.md` (knowledge-graph
  destination)
- **Graphiti** — see `references/destinations-graphiti.md`
  (temporal knowledge graph)

### Performance & optimisation

- **Parallelised resources, `add_limit`, file rotation** — see
  `references/performance-optimisation.md`

### Dagster integration

- **`@dlt_assets` wrapping** — see `references/dagster-dlt-assets.md`
  (the canonical pattern for scheduling DLT inside Dagster)

### Transformations (dlt → dlt)

- **`@dlt.transformer`, SQL-based, Ibis aggregation** — see
  `references/dlt-transformations.md`

### Deployment

- **Dagster asset with scheduling** — see the `dagster` skill
- **Serverless webhook (HTTP-triggered)** — see
  `references/deploy-gcp-cloud-function-webhook.md`
- **Serverless scheduled** — see `references/deploy-modal.md`
- **DAG-transformed downstream** — hand off to the `sqlmesh` skill
  via `sqlmesh init -t dlt --dlt-pipeline <name> dialect` (see
  `references/sqlmesh-init.md`)

### Search & RAG

- **Vectorise for RAG** — see `references/destinations-lancedb.md`
  (the `lancedb_adapter(source, embed=[...])` pattern)
- **Knowledge graph** — see `references/destinations-cognee-memgraph.md`

### OpenAPI source generation

- **`dlt-init-openapi`** — see `references/openapi-generator.md` for
  auto-generated verified sources from any OpenAPI spec

### Browser scraping

- **`crawl4ai`** — see `references/crawl4ai-dlt-summary.md` (alternative
  to Firecrawl for JS-heavy sites)

## 3. Project-specific recipes (KCG patterns)

### Type-safe pipeline (BAML → dlt → oRPC → MCP)

```python
import dlt
from cianfhoghlaim.baml import b  # post-v4 codegen path
from cianfhoghlaim.baml.types import PrimaryLearningOutcome  # auto-generated
from pydantic import BaseModel

class PrimaryOutcomeRow(BaseModel):
    """Mirror of the BAML class, with dlt column types."""
    stage: str
    curriculum_area: str
    learning_outcome: str

@dlt.resource(name="primary_outcomes", write_disposition="merge", primary_key=["stage", "curriculum_area", "learning_outcome"])
def primary_outcomes(pdf_path: str) -> list[PrimaryOutcomeRow]:
    """Extract primary learning outcomes from an NCCA PDF via BAML."""
    text = extract_pdf_text(pdf_path)
    outcomes = b.ExtractPrimaryLearningOutcomes(text)
    for o in outcomes:
        yield PrimaryOutcomeRow(
            stage=o.stage,
            curriculum_area=o.curriculum_area,
            learning_outcome=o.learning_outcome,
        )

pipeline = dlt.pipeline(
    pipeline_name="ireland_primary_curriculum",
    destination="ducklake",
    dataset_name="cianfhoghlaim.education.ie",
)
load_info = pipeline.run(primary_outcomes("ncca_primary.pdf"))
print(load_info)
```

The BAML class is the **single source of truth** — both the
Pydantic `BaseModel` and the dlt `primary_key` derive from it.

### Canonical KCG pattern — British-Isles Education pipeline (lc6)

The post-v4 canonical pipeline ingests one of the six Irish Leaving
Certificate subjects (Mathematics, Chemistry, Geography, Gaeilge,
English, Computer Science) from a BAML-extracted NCCA/SEC PDF,
fan-outs to DuckLake + LanceDB, and is scheduled by Dagster via
`@dlt_assets`:

```python
import dlt
from cianfhoghlaim.dlt.british_isles.ireland.education.ncca import (
    mathematics_syllabus as mathematics_syllabus_source,
)
from cianfhoghlaim.baml.education.lc_extraction.curriculum_syllabus import b


@dlt.resource(
    name="lc_mathematics_syllabus",
    write_disposition="merge",
    primary_key=["subject", "level", "language", "module_id"],
)
def mathematics_syllabus(pdf_path: str):
    """Extract Mathematics LC syllabus modules from an NCCA PDF via BAML."""
    doc = b.ExtractCurriculumSyllabus(text=open(pdf_path).read())
    for module in doc.modules:
        yield {
            "subject": "mathematics",
            "level": doc.level,
            "language": doc.language,
            "module_id": module.id,
            "title": module.title,
            "hours": module.hours,
            "learning_outcomes": module.learning_outcomes,
        }


pipeline = dlt.pipeline(
    pipeline_name="lc6_ncca",
    destination="ducklake",
    dataset_name="cianfhoghlaim.leaving_cert",
)
load_info = pipeline.run(
    mathematics_syllabus("leaving_certificate/mathematics/en/...syllabus.pdf")
)
print(load_info)
```

The same pattern is repeated for the other 5 LC subjects
(`chemistry_syllabus`, `geography_syllabus`, `gaeilge_syllabus`,
`english_syllabus`, `computer_science_syllabus`) plus a
`government_circulars` resource for `gov.ie` education circulars.
Each resource is wrapped in `@dlt_assets` in
`orchestration/defs/2_materials/` and contributes
to the 7 v1 CocoIndex Apps (6 LC + `government_circulars`) and
the 4 MotherDuck Dives (`lc_syllabus_topics`,
`lc_exam_difficulty`, `lc_marking_complexity`,
`gov_circulars_archive`).

### Multi-destination fan-out (DuckDB + LanceDB + Memgraph)

```python
import dlt
from dlt.destinations import duckdb
from lancedb import lancedb_adapter
from cognee import add as cognee_add, cognify

@dlt.resource(name="curriculum_chunks")
def chunks(pdf_path: str):
    text = extract_pdf_text(pdf_path)
    for chunk in chunk_text(text):
        yield {"text": chunk, "source": pdf_path}

# Fan out to 3 destinations
pipeline = dlt.pipeline(destination="duckdb", dataset_name="curriculum")
load_info = pipeline.run([
    chunks("ncca.pdf"),                                    # → DuckDB
    lancedb_adapter(chunks("ncca.pdf"), embed=["text"]),    # → LanceDB
    cognee_destination(chunks("ncaa.pdf")),                 # → Cognee
])
```

One pipeline run, three destinations. State is unified (one
`pipeline.last_trace`, not three).

### Dagster asset wrapping (`@dlt_assets`)

```python
from dagster_dlt import DagsterDltResource, dlt_assets
import dlt

@dlt_assets(
    dlt_source=ireland_curriculum_source(),
    dlt_pipeline=dlt.pipeline(
        pipeline_name="ireland_curriculum",
        destination="ducklake",
        dataset_name="cianfhoghlaim.education.ie",
    ),
)
def ireland_curriculum_assets(context, dlt_run_resource: DagsterDltResource):
    yield from dlt_run_resource.run(context=context)

# Schedule
@schedule(cron_schedule="0 2 * * *", job=ireland_curriculum_assets_job)  # 02:00 UTC daily
def ireland_curriculum_schedule(): ...
```

See `references/dagster-dlt-assets.md` for the full pattern with
multiprocess_executor, parallel assets, and incremental loading.

## 4. Performance & anti-patterns

✅ **Do**:

- Use `parallelized=True` for any resource fetching > 1k rows
- Use `add_limit(N)` to cap a source for testing
- Use file rotation (`dlt.pipeline(..., progress="log")` + chunked
  writes) for > 1M rows
- Use `write_disposition="merge"` with an explicit `primary_key` for
  upserts
- Use `columns=PydanticModel` for type-safe pipelines (the BAML
  pattern)
- Pre-validate inputs before the API call (catches bad PDFs early)

❌ **Don't**:

- Fetch all data in a single `fetch_all()` call (OOM risk for > 1M rows)
- Use `write_disposition="merge"` without a `primary_key` (silently
  appends duplicates)
- Import `cianfhoghlaim.data_platform.dlt_sources` from within
  `cianfhoghlaim/` (use relative imports (`from .dlt...`)
- Hand-write DDL for the destination (let dlt infer the schema from
  the resource yield)
- Run live web scraping without `USE_LOCAL_SCRAPES=true` first
  (drains API credits and risks rate limits)
- Add a BAML client inline in a function (use a named client in
  `baml/clients.baml`)
- Pin `dlt==1.27.0` or `dlt==1.27.1` — both YANKED from PyPI for a
  data-loss bug; the fix is 1.27.2 (or upgrade to ≥ 1.28.1).
- Use `write_disposition="replace"` (deprecated in 1.28.0) — use the
  `refresh` parameter instead.
- Call `dlt ai ...` (moved to `dlthub ai ...` in 1.27.0).
- Call `dlt dashboard` without `pip install dlt[hub]` (1.27.0 split).

## 5. Reference index

The 3 reference files in `references/` that were previously
orphaned are now linked from here:

- [`references/dlthub.md`](references/dlthub.md) — the generic
  dltHub expert skill (501 lines; write_disposition matrix, REST
  API source, sources + destinations reference)
- [`references/dlthub-codebase-analysis.md`](references/dlthub-codebase-analysis.md) —
  dltHub code-level design-patterns analysis (decorator, builder,
  factory, repository, strategy; resource / source / write-disposition
  patterns)
- [`references/dlt-baml-orpc-mcp-typesafe-pipeline-analysis.md`](references/dlt-baml-orpc-mcp-typesafe-pipeline-analysis.md) —
  the full type-safe pipeline architecture (BAML → dlt columns →
  oRPC contract → MCP tool)

New references (added by the `sync-skills-from-docs` change):

- [`references/destinations-lancedb.md`](references/destinations-lancedb.md)
- [`references/destinations-cognee-memgraph.md`](references/destinations-cognee-memgraph.md)
- [`references/destinations-graphiti.md`](references/destinations-graphiti.md)
- [`references/performance-optimisation.md`](references/performance-optimisation.md)
- [`references/dagster-dlt-assets.md`](references/dagster-dlt-assets.md)
- [`references/openapi-generator.md`](references/openapi-generator.md)
- [`references/deploy-gcp-cloud-function-webhook.md`](references/deploy-gcp-cloud-function-webhook.md)
- [`references/deploy-gcp-cloud-function.md`](references/deploy-gcp-cloud-function.md)
- [`references/deploy-gcp-cloud-run.md`](references/deploy-gcp-cloud-run.md)
- [`references/deploy-modal.md`](references/deploy-modal.md)
- [`references/sqlmesh-init.md`](references/sqlmesh-init.md)
- [`references/dlt-transformations.md`](references/dlt-transformations.md)
- [`references/crawl4ai-dlt-summary.md`](references/crawl4ai-dlt-summary.md)
- [`references/type-safe-pipeline.md`](references/type-safe-pipeline.md)

## 6. Cross-references

- The `dlt` skill is consumed by: `data-engineer` agent (the
  primary user)
- The `dlt` skill collaborates with: `baml` skill (type-safe
  pipelines), `dagster` skill (`@dlt_assets` wrapping), `sqlmesh`
  skill (`sqlmesh init -t dlt`), `lancedb` skill (vector destination),
  `cognee` skill (knowledge-graph destination), `motherduck` skill
  (MotherDuck destination)
- The `dlt` skill feeds into: `explore-data` (analysis_plan.md) and
  `build-notebook` (marimo notebooks) for downstream visualisation

## 7. Examples

See [`./examples/`](./examples/) for upstream dlt reference

## British-Isles Education pipeline use case (BIEP, post-v4)

The `dlt` skill is the data-load backbone for the British-Isles
Education pipeline (`openspec/changes/lc6-biep/`). It drives:

- **7 per-subject BAML extraction stages** (syllabus / exam paper
  layout / marking scheme / cross-linguistic / syllabus diagram)
  across the 6 LC subjects (Mathematics, Chemistry, Geography,
  Gaeilge, English, Computer Science) — **42 lc5/lc6 Dagster assets
  total** in `orchestration/defs/2_materials/`.
- **`gov.ie` circulars** — the `government_circulars` resource
  mirrors the 7th v1 CocoIndex App (`government_circulars`),
  landing pages from `gov.ie/.../circulars/...` into
  `cianfhoghlaim.education.ie.gov_circulars_archive` (one of the 4
  canonical MotherDuck Dives).
- **Dual-language fan-out** — every resource is partitioned by
  `language` (`en` / `ga`) so the Gaeilge syllabus runs in parallel
  with English via the same `@dlt_assets` wrapper.
- **BAML → dlt columns** — the `lc5/lc6` extraction schemas (e.g.
  `ExtractCurriculumSyllabus`, `ExtractMarkingSchemeGuideline`)
  are the `primary_key` source-of-truth for the `merge` write
  disposition.

Cross-references:
- [`baml/SKILL.md`](../baml/SKILL.md) — the BAML extraction functions
- [`dagster/SKILL.md`](../dagster/SKILL.md) — the `@dlt_assets`
  wrappers + lc6 schedule
- [`motherduck/SKILL.md`](../motherduck/SKILL.md) — the 4 Dives
  (`lc_syllabus_topics`, `lc_exam_difficulty`,
  `lc_marking_complexity`, `gov_circulars_archive`)
- [`cocoindex/SKILL.md`](../cocoindex/SKILL.md) — the 7 v1 Apps
  (6 LC subjects + `government_circulars`)
- [`marimo/SKILL.md`](../marimo/SKILL.md) — the 6 per-subject marimo
  notebooks
- [`change-detection/SKILL.md`](../change-detection/SKILL.md) — the
  NCCA / SEC / `gov.ie` sitemap-hash sensors

## 2026-06 updates (from the `upstream-package-monitoring` openspec change)

- **dltHub Pro** launched 2026-04-14. The Pro tier adds 9,700+ known
  source contexts that DLT can pull from in one call. The KCG dev
  plan is tracked by `openspec/changes/dlt-pro-source-registry/`.
- **Cortex Code** (Snowflake's AI assistant, launched ~9 weeks before
  dltHub Pro) integrates directly with the dlt Pro source registry.
- **ADE-Bench** (the AI data-engineer benchmark) reported 65% task
  success on Snowflake via Cortex Code vs 58% for Claude Code. The
  paper's key finding: **"without the workbench, the agent leaked
  credentials"** — directly validates KCG's strict-secret-hydration
  mandate (see `docs/secrets/secrets_management_plan.md` for the
  Infisical + Locket + mise three-way contract).
- **dlthub upstream monitor** — `dlthub_blog.yml` in
  `bonneagar/firecrawl/monitors/upstream_packages/` is the
  Firecrawl monitor that detects new source-context additions,
  ADE-Bench results, and Cortex Code integration updates via the
  LLM-judge `--goal` filter. The n8n workflow
  `bonneagar/stacks/n8n/workflows/upstream-blog-monitor.json`
  writes the payload to
  `s3://cianfhoghlaim-upstream-webhooks/dlthub/...jsonl` and triggers
  the Dagster asset `upstream_blog_monitor_ingest`.
notebooks:

- `data_engineering_dlt_small-data-sf-2025_elvis.ipynb` — Dremio
  "small data" workshop (SF 2025): dlt pipelines for small
  files, REST API ingestion patterns, and DuckDB destination
  examples.

## v7 flattening migration notes (added 2026-07-19)

Per openspec/changes/2026-07-14-fix-foundation-v7-flattening-and-baml-drift-v1:

- DLT sources are now at `cianfhoghlaim.dlt.british_isles.<jurisdiction>.education.<source>`
- The canonical CLI entry point is `python -m cianfhoghlaim.dlt.cli run-pipeline`
  (NOT `python -m cianfhoghlaim.dlt.run_pipeline` which was the pre-v7 name)
- The new BIEP v3 jurisdiction pipelines live at:
  - `dlt_sources/british_isles/ireland/education/ireland_jurisdiction_pipeline.py`
  - `dlt_sources/british_isles/england/education/england_jurisdiction_pipeline.py`
  - `dlt_sources/british_isles/sct_wls_ni/education/sct_wls_ni_jurisdiction_pipeline.py`
  - `dlt_sources/british_isles/crown_dependencies/education/crown_dependencies_jurisdiction_pipeline.py`
- Each pipeline uses `dlt.common.curriculum_registry.SubjectRegistry` for canonical subject metadata
- The destination is configured via `dlt.common.destinations_cianfhoghlaim.get_dlt_destination(use_ducklake=True)`
- The 4 destinations: local DuckDB, MotherDuck BYOB, Garage S3 + Lakekeeper, R2 + Lakekeeper

