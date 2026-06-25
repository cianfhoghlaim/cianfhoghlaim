---
name: dlt
description: Master routing skill for data load tool (dlt). Use this to understand dlt rules, decide which sub-skill to invoke, and apply the Cianfhoghlaim dlt conventions (DuckLake/DuckDB destination, USE_LOCAL_SCRAPES offline fallback, relative imports only, type-safe BAML-driven pipelines, multi-destination fan-out to LanceDB / Memgraph / Graphiti, and Dagster dlt_assets wrapping).
---

# DLT Master Router & Rules (Cianfhoghlaim)

You are operating within the `cianfhoghlaim` stack which uses `dlt`
(data load tool) for extracting and loading data. This skill is the
**router + decision tree + project rules** for all dlt operations.

## 1. Project rules (PRESERVED from the original skill, with one fix)

When assuming the `data-engineer` persona, use these rules:

- **Destinations**: `dlt.pipeline(..., destination="ducklake")` for
  production (MotherDuck / DuckLake) or `destination="duckdb"` for
  local dev. Set `USE_DUCKLAKE=true` to switch to MotherDuck.
- **Tests**: disable plugins during testing by setting
  `DLT_DISABLE_PLUGINS=true`.
- **Source location**: `dlt_sources` lives at `sruth/oideachais/dlt_sources/`
  (NOT `sruth/oideachais/data_platform/dlt_sources/`, which is a deprecated
  path mentioned in the old skill).
- **Imports**: All `oideachais.data_platform...` absolute imports have
  been removed; use relative or local `dlt_sources` imports
  (e.g. `from dlt_sources.ireland...`).
- **Offline fallback**: `USE_LOCAL_SCRAPES=true` routes extraction
  to `stedding/ingest_queue/` (the curated local cache) instead of
  live web scraping (avoids API rate limits and credit drain).
- **Absolute namespaces** (per project AGENTS.md): NEVER import
  `oideachais.data_platform...` from within the data platform — use
  relative imports.
- **Ingestion cache** (per project AGENTS.md): Test with
  `USE_LOCAL_SCRAPES=true` before live web scraping to avoid API
  rate limits.

## 2. Decision tree → sub-skill or reference

When tasked with dlt operations or data exploration, use this
guide to invoke the most appropriate resource:

### Data exploration & notebooks (sruth/oideachais/notebooks)

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
from baml_client import b
from baml_client.types import PrimaryLearningOutcome  # auto-generated
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
    dataset_name="oideachais.education.ie",
)
load_info = pipeline.run(primary_outcomes("ncca_primary.pdf"))
print(load_info)
```

The BAML class is the **single source of truth** — both the
Pydantic `BaseModel` and the dlt `primary_key` derive from it.

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
        dataset_name="oideachais.education.ie",
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
- Import `oideachais.data_platform.dlt_sources` from within
  `sruth/oideachais/` (use relative imports)
- Hand-write DDL for the destination (let dlt infer the schema from
  the resource yield)
- Run live web scraping without `USE_LOCAL_SCRAPES=true` first
  (drains API credits and risks rate limits)
- Add a BAML client inline in a function (use a named client in
  `baml_src/clients.baml`)

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
notebooks:

- `data_engineering_dlt_small-data-sf-2025_elvis.ipynb` — Dremio
  "small data" workshop (SF 2025): dlt pipelines for small
  files, REST API ingestion patterns, and DuckDB destination
  examples.
