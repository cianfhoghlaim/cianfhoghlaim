---
name: dagster
description:
  Expert guidance for working with Dagster and the dg CLI. ALWAYS use before doing any task that requires
  knowledge specific to Dagster, or that references assets, materialization, components, data tools or data pipelines.
  Common tasks may include creating a new project, adding new definitions, understanding the current project structure, answering general questions about the codebase (finding asset, schedule, sensor, component or job definitions), debugging issues, or providing deep information about a specific Dagster concept.
  Drives the British-Isles Education pipeline (42 lc5/lc6 assets = 7 subjects × 6 BAML stages) via `orchestration/defs/2_materials/`.

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

## Core Dagster Concepts
# Oideachais Project Specific Rules
- **Environment**: Start local environment with `uv run dagster dev -m orchestration.definitions` inside the `cianfhoghlaim` directory.
- **Partitions**: `ireland/curriculum/` assets are MultiPartitioned by `language` and `subject` (e.g., `"en|mathematics"`). The lc5/lc6 BIEP assets are additionally partitioned by `level` (`higher` / `ordinary`) — 42 assets total = 7 subjects × 6 BAML stages.
- **Lakehouse**: MotherDuck/DuckLake is the sink. Ensure `USE_DUCKLAKE=true` if using MotherDuck, otherwise it uses a local DuckDB file.
- **Namespaces**: NEVER use absolute namespaces (e.g. `cianfhoghlaim.orchestration...`) from within the orchestration layer. Always use relative or local package imports.


Brief definitions only (see reference files for detailed examples):

- **Asset**: Persistent object (table, file, model) produced by your pipeline
- **Component**: Reusable building block that generates definitions (assets, schedules, sensors, jobs, etc.) relevant to a particular domain.

## Integration Workflow

When integrating with ANY external tool or service, read the [Integration libraries index](./references/integrations/INDEX.md). This contains information about which integration libraries exist, and references on how to create new custom integrations for tools that do not have a published library.

## dg CLI

The `dg` CLI is the recommended way to programmatically interact with Dagster (adding definitions, launching runs, exploring project structure, etc.). It is installed as part of the `dagster-dg-cli` package. If a relevant CLI command for a given task exists, always attempt to use it.

ONLY explore the existing project structure if it is strictly necessary to accomplish the user's goal. In many cases, existing CLI tools will have sufficient understanding of the project structure, meaning listing and reading existing files is wasteful and unnecessary.

Almost all `dg` commands that return information have a `--json` flag that can be used to get the information in a machine-readable format. This should be preferred over the default table output unless you are directly showing the information to the user.

## UV Compatibility

Projects typically use `uv` for dependency management, and it is recommended to use it for `dg` commands if possible:

```bash
uv run dg list defs
uv run dg launch --assets my_asset
```

## CRITICAL: Always Read Reference Files Before Answering

NEVER answer from memory or guess at CLI commands, APIs, or syntax. ALWAYS read the relevant reference file(s) from the Reference Index below before responding.

For every question, identify which reference file(s) are relevant using the index descriptions, read them, then answer based on what you read.

## Reference Index

<!-- BEGIN GENERATED INDEX -->

- [Asset Selection Syntax](./references/asset-selection.md) — filtering assets by tag, group, kind, upstream, or downstream; AssetSelection in Python, UI search bar, or CLI
- [Environment Variables](./references/env-vars.md) — configuring environment variables across different environments
- [Asset Patterns](./references/assets/INDEX.md) — defining assets, dependencies, metadata, partitions, or multi-asset definitions
- [Choosing an Automation Approach](./references/automation/choosing-automation.md) — deciding between schedules, sensors, and declarative automation
- [Schedules](./references/automation/schedules.md) — time-based automation with cron expressions
- [Declarative Automation](./references/automation/declarative-automation/INDEX.md) — asset-centric condition-based automation using AutomationCondition
- [Asset Sensors](./references/automation/sensors/asset-sensors.md) — triggering on asset materialization events
- [Basic Sensors](./references/automation/sensors/basic-sensors.md) — event-driven automation with file watching or custom polling
- [Run Status Sensors](./references/automation/sensors/run-status-sensors.md) — reacting to run success, failure, or other status changes
- [dg check](./references/cli/check.md) — validating project configuration or definitions
- [create-dagster](./references/cli/create-dagster.md) — creating a new Dagster project from scratch
- [dg dev](./references/cli/dev.md) — starting a local Dagster development instance
- [dg launch](./references/cli/launch.md) — materializing assets or executing jobs locally
- [dg list components](./references/cli/list-components.md) — seeing available component types for scaffolding
- [dg list defs](./references/cli/list-defs.md) — listing or filtering registered definitions
- [Dagster Plus API](./references/cli/api/INDEX.md) — dg api, programmatically querying or managing Dagster Plus resources (assets, runs, deployments, code locations, schedules, sensors, secrets, issues, etc.)
- [dg list](./references/cli/list/INDEX.md) — exploring project structure (component tree, environment variables, workspace projects)
- [Dagster Plus CLI](./references/cli/plus/INDEX.md) — dg plus, Dagster Plus authentication, configuration, and deployment; logging in, setting config, creating API tokens, deploying code, pulling env vars, managing dbt manifests
- [dg scaffold component](./references/cli/scaffold/component.md) — creating a custom reusable component type
- [dg scaffold defs](./references/cli/scaffold/defs.md) — adding new definitions (assets, schedules, sensors, components) to a project
- [dg utilities](./references/cli/utils/INDEX.md) — dg utils, inspecting component types, viewing integrations, refreshing state-backed component cache
- [Creating Components](./references/components/creating-components.md) — building a new custom component from scratch
- [Designing Component Integrations](./references/components/designing-component-integrations.md) — designing a component that wraps an external service or tool; custom integrations
- [Resolved Framework](./references/components/resolved-framework.md) — defining custom YAML schema types using Resolver, Model, or Resolvable
- [Subclassing Components](./references/components/subclassing-components.md) — extending an existing component via subclassing; customize dagster integration component
- [Template Variables](./references/components/template-variables.md) — using Jinja2 template variables in component YAML (env, dg, context, or custom scopes)
- [Creating State-Backed Components](./references/components/state-backed/creating.md) — building a component that fetches and caches external state
- [Using State-Backed Components](./references/components/state-backed/using.md) — managing state-backed components in production, CI/CD, or refreshing state
- [Deployment Configuration Files](./references/deployment/config-files.md) — build.yaml, container_context.yaml, dagster_cloud.yaml; Dagster Plus deployment configuration; configuring Docker registry, container context, agent queue; Hybrid deployment files
- [Integration libraries index for 40+ tools and technologies (dbt, Fivetran, Snowflake, AWS, etc.).](./references/integrations/INDEX.md) — integration, external tool, dagster-\*; dbt, fivetran, airbyte, snowflake, bigquery, sling, aws, gcp
- [Migration Guides](./references/migration/INDEX.md) — sensor migration to declarative automation, sensor migration to automation condition
<!-- END GENERATED INDEX -->

## KCG-relevant references (added by `sync-skills-from-docs`)

These are project-specific reference files that extend the core
Dagster skill with KCG production patterns:

### Integrations

- [DuckLake integration (canonical KCG lakehouse sink)](./references/integrations/dagster-ducklake/INDEX.md) —
  `DuckLakeResource` config (Postgres catalog + S3 + `dg.EnvVar` secrets)
- [SQLMesh integration](./references/integrations/dagster-sqlmesh/INDEX.md) —
  `@sqlmesh_assets` + `SQLMeshResource` + central `SQLMeshDagsterTranslator`
- [DLT parallel-asset factory (GitHub reference)](./references/integrations/dagster-dlt/parallel-github.md) —
  the closest analogue to KCG's `ireland/curriculum/` 33+ REST endpoints
- [Evidence.dev BI dashboards](./references/integrations/dagster-evidence/INDEX.md) —
  thin INDEX stub (KCG currently uses marimo; Evidence is a future option)
- [Modal GPU compute](./references/integrations/dagster-modal/INDEX.md) —
  thin INDEX stub (KCG uses Modal for HTR fine-tuning + OCR ensemble)
- [Iceberg table integration](./references/integrations/dagster-iceberg/INDEX.md) —
  thin INDEX stub (KCG uses DuckLake primarily; Iceberg via the
  Lance + Iceberg companion-table pattern)

### Deployment

- [Self-hosted Docker Dagster deploy](./references/deployment/docker-self-hosted.md) —
  the canonical 4-service topology (Postgres + gRPC user-code +
  webserver + daemon) for KCG production (not Dagster+ Hybrid)

### Orchestration

- [KCG CocoIndex + Graphiti asset graph](./references/orchestration/kcg-cocoindex-graphiti.md) —
  the canonical
  `raw_pdf → extracted_markdown → semantic_chunks → vector_embeddings → knowledge_graph_episodes`
  asset graph with `DynamicPartitionsDefinition` per file and
  sensor-driven `add_dynamic_partitions(...)`

## KCG 4-layer asset graph (canonical)

The Cianfhoghlaim platform organises its Dagster assets in
4 layers. Each layer is a separate asset group with its own
schedule and ownership.

```
┌────────────────────────────────────────────────────────┐
│  Layer 1: Ingestion (DLT sources)                       │
│  → fetch from NCCA / SEC / DES / UoG / leabharlann      │
│  → 4-quadrant MultiPartitions by language + subject    │
│  → writes to DuckLake (raw tables)                      │
└────────────────────────────────────────────────────────┘
                          ↓
┌────────────────────────────────────────────────────────┐
│  Layer 2: Materials (Docling, OCR, BAML extraction)     │
│  → PDF → markdown → chunks → typed BAML class           │
│  → runtime evals + auto-retry on extraction             │
│  → writes to DuckLake (typed tables) + LanceDB          │
└────────────────────────────────────────────────────────┘
                          ↓
┌────────────────────────────────────────────────────────┐
│  Layer 3: Model Lifecycle (CocoIndex v1 Apps)           │
│  → embed + index + graph-build                          │
│  → live mode (`cocoindex update -L`)                    │
│  → writes to LanceDB + FalkorDB + Cognee                │
└────────────────────────────────────────────────────────┘
                          ↓
┌────────────────────────────────────────────────────────┐
│  Layer 4: Asset Generation (Dagster re-materialization) │
│  → marimo dashboards (5 educational stages)             │
│  → FastAPI routes (`/dashboards/*`, `/api/*`)          │
│  → TanStack Start front-end (`web/apps/cianfhoghlaim-web/`)         │
└────────────────────────────────────────────────────────┘
```

**Asset groups:**

- `cianfhoghlaim-pipeline` — Layer 1 (DLT ingestion, 33+ sources
  for Ireland, UK, Celtic, geospatial)
- `cianfhoghlaim-cognify-knowledge-graph` — Layer 2 + 3
  (cognify, 3 leabharlann cognify, 3 cross-archive edges)
- `cianfhoghlaim-leabharlann` — Layer 2 (3 v1 CocoIndex Apps
  for the leabharlann corpus)
- `cianfhoghlaim-semantic-search` — Layer 3 (cross-corpus
  LanceDB HNSW search)
- `cianfhoghlaim-marimo-dashboards` — Layer 4 (11 marimo
  notebooks for the 5 educational stages)
- `cianfhoghlaim-baml-schemas` — Layer 2 (BAML extraction

  schemas, 23+ files)
- `docs-skills-consolidation` — Layer 4 (the
  `docs_skills_consolidation` v1 App that indexes all
  docs/ + .agents/skills/)

### Hierarchical asset groups (1.13.9+)

Asset group names may now contain `/` separators (e.g. `celtic/duchas`,
`celtic/gaeilge`, `celtic/bearla`). Wildcards work (`group:"celtic/*"`)
and the asset graph renders them as nested groups. Combined with the
new `is:` filter (`is:external`, `is:materializable`) for asset selection.

```python
@dg.asset(group_name="celtic/duchas", owners=["team:corpdev"])
def duchas_grammar_table() -> None: ...
```

## Dagster ports (KCG-specific)

| Service | Port | Notes |
|:--|:--|:--|
| `engineering-dagster-webserver` | 3335 | Main engineering Dagster (the canonical one) |
| `croilar-dagster-webserver` | 3000 | Croilar (the persona-specific Dagster) |
| `dagster-user-code` (gRPC) | 4000 | Internal — between webserver and the user-code container |
| `dagster-postgres` | 5432 | Internal — `PostgresRunStorage` etc. |

When developing locally, use port 3335 for the main Dagster UI.
Use port 3000 only for croilar-specific work.

## KCG port list summary

- Dagster: 3335 (engineering) / 3000 (croilar) / 4000 (gRPC)
- Lakekeeper Iceberg: 8181
- Lance Namespace sidecar: 9000
- MotherDuck (managed)
- Cognee: 8000 (Cognee web UI)
- FalkorDB: 6379
- LanceDB Cloud: db://<db-name>

## KCG install + integration (canonical)

```bash
# KCG engineering Dagster stack (the canonical one)
cd oideachais
uv add dagster dagster-duckdb "dagster-dlt>=0.29.11"
uv run dagster dev -m orchestration.definitions
# UI at http://localhost:3335
```

The KCG Dagster integration lives at:

- `orchestration/defs/` — the Dagster
  definitions module (assets, jobs, schedules, sensors, resources)
- `orchestration/definitions.py` —
  the entry point
- `dg.toml` — the Dagster workspace config (registers
  oideachais, tuatha, meaisínfhoghlaim, croilar as code-locations)

### KCG asset groups (4-layer narrative)

The Cianfhoghlaim asset graph is organised in 4 narrative
layers. Each layer has its own asset group, schedule, and
ownership:

1. **Ingestion** — DLT sources (33+ for Ireland, UK, Celtic,
   geospatial). Writes to DuckLake raw tables. Scheduled
   hourly.
2. **Materials** — Docling OCR + BAML extraction + runtime
   evals. Writes to DuckLake typed tables + LanceDB. Scheduled
   daily.
3. **Model Lifecycle** — CocoIndex v1 Apps (embeddings,
   knowledge graphs, FTS indexes). Live mode (`cocoindex update
   -L`). Writes to LanceDB + FalkorDB + Cognee.
4. **Asset Generation** — marimo dashboards, FastAPI routes,
   TanStack Start pages. Triggered by changes in the upstream
   layers.

### DLT + Firecrawl integration patterns

The KCG DLT sources use the `firecrawl-mcp` + Cianfhoghlaim browser
+ `Firecrawl API` fallback ladder (see
`.agents/skills/dlt/SKILL.md` for the full pattern):

```python
# dlt REST API source with Firecrawl fallback
@dlt.source
def firecrawl_source():
    config = {
        "client": {"base_url": os.environ["FIRECRAWL_BASE_URL"]},
        "resources": [{
            "name": "scraped_pages",
            "endpoint": {
                "path": "scrape",
                "params": {
                    "url": {"type": "resolve", "resource": "urls"},
                },
            },
        }],
    }
    return rest_api_source(config)
```

When a Dagster asset is materialised:

1. The DLT source fires
2. The dlt pipeline runs (writes to DuckLake)
3. `dlt_run_resource.run(context=context)` is called
4. The asset is marked materialised
5. Downstream assets (e.g. CocoIndex v1 Apps) are auto-triggered

### DLT via the upstream `DltLoadCollectionComponent` (1.13.9+)

The YAML-based Component natively supports `partitions_def` and
`backfill_policy` — something our bespoke `celtic_dlt_source.py`
wrapper does not. Migrate `celtic_dlt_source.py` to a thin
subclass that adds `partitions_def=MultiPartitionsDefinition(...)`
via `backfill_policy=BackfillPolicy.multi_run()` (1.13.9 release notes).

```bash
dg scaffold defs dagster_dlt.DltLoadCollectionComponent github_snowflake_ingest \
  --source github --destination snowflake
uv add dagster-dlt  # ensure >=0.29.11
```

```yaml
# defs/github_snowflake_ingest/defs.yaml
type: dagster_dlt.DltLoadCollectionComponent
attributes:
  loads:
    - source: .loads.my_source
      pipeline: .loads.my_pipeline
      translation:
        group_name: github_data
```

### Multi-tenant DLT asset factory (legacy `@dlt_assets`)

The KCG `orchestration/defs/1_ingestion/curriculum_dlt_assets.py`
defines a factory pattern for the 33+ Ireland curriculum
assets, each with the canonical
`MultiPartitionsDefinition(language, subject)` partition:

```python
@dlt_assets(
    dlt_source=ireland_curriculum_source(),
    dlt_pipeline=dlt.pipeline(
        pipeline_name="ireland_curriculum",
        destination="ducklake",
        dataset_name="cianfhoghlaim.education.ie",
    ),
    partitions_def=MultiPartitionsDefinition({
        "language": StaticPartitionsDefinition(["en", "ga"]),
        "subject": StaticPartitionsDefinition([
            "mathematics", "irish", "english", "history", ...
        ]),
    }),
)
def ireland_curriculum_assets(context, dlt_run_resource):
    yield from dlt_run_resource.run(context=context)

## KCG: 21-asset-module / 7-group inventory (canonical)

Per `orchestration/definitions.py` and the
leabharlann stack overview, the KCG Dagster workspace has
**21 asset modules** across **7 groups**:

| Group | Asset modules | Notes |
|:--|:--|:--|
| `multi_nation_curriculum` | 8 | NCCA, SEC, DES, CCEA, SQA, WJEC, IoM, Jersey, Guernsey |
| `uk_education` | 3 | DfE, Ofqual, UK Statistics |
| `leabharlann_books` | 3 | books / zotero / takeout |
| `author_archive_uog` | 4 | UoG / Gemini / Takeout / BAML |
| `ireland_primary_jc` | 1 | Primary + Junior Cycle factory (33+ asset instances) |
| `crown_dependencies` | 2 | Isle of Man + Channel Islands |
| `leabharlann` | 0 (orchestrator) | The cross-stage orchestrator |

**Total**: 56+ asset instances, all sharing the
`cianfhoghlaim.{domain}.{nation}.{entity}` asset-key contract
(see `.agents/skills/agent-memory-systems/SKILL.md`).

### The 5-stage leabharlann asset materialisation order

The leabharlann pipeline (`.agents/skills/leabharlann-pipeline/SKILL.md`)
is wired as 7 specific Dagster assets that fire in order:

1. `leabharlann_books_raw` (Stage 2: DLT filesystem scan)
2. `leabharlann_zotero_raw` (Stage 2)
3. `leabharlann_takeout_v1_raw` (Stage 2)
4. `leabharlann_paper_metadata` (Stage 3: BAML extraction)
5. `leabharlann_cocoindex_zotero_update` (Stage 4:
   CocoIndex v1)
6. `cognee_cognify_zotero` (Stage 5: Cognee, **queued**)
7. `cognee_cross_archive_edges` (Stage 5: edges, **queued**)

The **first 5 are wired**; the last 2 are queued in
`REFACTORING.md` Feature 2.

```

## 2026-06 update: dg CLI + Components

Dagster's `dg` CLI is now the recommended way to scaffold and manage Dagster projects. It supersedes the older `dagster project scaffold` pattern.

### The 5 high-value dg commands

```bash
# 1. Initialise a new Dagster project
dg init my-project
cd my-project

# 2. Scaffold a new asset
dg scaffold asset my_pipeline/my_asset

# 3. Scaffold a Component (YAML-defined integration)
dg scaffold component dagster.MyComponentType

# 4. Local build (validate types + dependencies)
dg build

# 5. Local dev (run the webserver + daemon)
dg dev
```

### The Components API

Components are YAML-defined integration points that let you wire Dagster assets, jobs, resources, and schedules declaratively without writing Python:

```yaml
# my_project/components/curriculum_assets.yaml
type: dagster.asset

params:
  group_name: ie_curriculum
  key_prefix: ie_education
  automation_condition: "{{ automation_condition.eager() }}"
  spec: |
    from dagster import AssetSpec
    return AssetSpec(
        key=["ie_education", "primary_curriculum"],
        description="Primary curriculum data from NCCA",
    )
```

Then in `definitions.py`:

```python
import dagster as dg
from my_project.components import CurriculumComponent

defs = dg.Definitions(
    assets=[CurriculumComponent()],
)
```

### The KCG code-location pattern

REFRESHED 2026-08-01 (lakehouse-and-reproducible-deploy-v1):
The Cianfhoghlaim platform runs **1 consolidated code-location**
from a single Dagster UI (post-v7). The historical 5-code-location
list was collapsed in the 2026-06-28 consolidation.

```toml
# /Users/cianmacandeisigh/dev/kings_college_galway/dg.toml
directory_type = "workspace"
[workspace]
[[workspace.locations]]
path = "."
code_location_name = "cianfhoghlaim"
module_name = "orchestration.definitions"
```

The single `orchestration.definitions` module aggregates 752
sub-components via `dg.load_defs_via_walker(...)` (or the
Dagster 1.13+ `dg.load_defs()` API path; see
`orchestration/definitions.py:71-86`).

## British-Isles Education pipeline — Canonical KCG pattern (post-v4)

The post-v4 lc6 pipeline (`openspec/changes/lc6-biep/`) wraps
the 6 LC subjects (Mathematics, Chemistry, Geography, Gaeilge,
English, Computer Science) + `gov.ie` circulars as `@dlt_assets`
in the 5-layer architecture (`1_ingestion/` →
`2_materials/` → `3_model_lifecycle/` →
`4_asset_generation/` → `5_agent_ops/`):

```python
from dagster_dlt import dlt_assets, DagsterDltResource
import dlt
from cianfhoghlaim.dlt.british_isles.ireland.education.subjects.mathematics import (
    mathematics_syllabus_source,
)


@dlt_assets(
    dlt_source=mathematics_syllabus_source(),
    dlt_pipeline=dlt.pipeline(
        pipeline_name="lc6_mathematics",
        destination="ducklake",
        dataset_name="cianfhoghlaim.leaving_cert",
    ),
)
def lc6_mathematics_assets(context, dlt_run_resource: DagsterDltResource):
    yield from dlt_run_resource.run(context=context)
```

The same wrapper pattern is repeated for the other 5 LC subjects
(`lc6_chemistry_assets`, `lc6_geography_assets`,
`lc6_gaeilge_assets`, `lc6_english_assets`,
`lc6_computer_science_assets`) plus `lc6_government_circulars_assets`
— each in `orchestration/defs/2_materials/` with
`MultiPartitionsDefinition(language=StaticPartitionsDefinition(["en", "ga"]),
subject=StaticPartitionsDefinition(["mathematics", "chemistry", ...]))`.

**British-Isles Education pipeline use case:**

- **42 lc5/lc6 Dagster assets** — 7 subjects (6 LC subjects +
  `government_circulars`) × 6 BAML stages (curriculum syllabus /
  exam paper layout / marking scheme / cross-linguistic /
  syllabus diagram / question corpus) in
  `orchestration/defs/2_materials/`.
- **`MultiPartitionsDefinition`** — `language` (`en` / `ga`) ×
  `subject` (6 LC subjects) × `level` (`higher` / `ordinary`) so
  the Gaeilge Higher Mathematics syllabus runs in parallel with
  English Ordinary Mathematics.
- **Lakehouse sink** — every `@dlt_assets` writes to
  `ducklake` (MotherDuck-managed) under
  `cianfhoghlaim.leaving_cert.<subject>.<level>_<lang>`.
- **Downstream surface** — the 7 v1 CocoIndex Apps consume the
  DuckLake tables; the 4 MotherDuck Dives + 6 per-subject marimo
  notebooks consume the CocoIndex output.
- **`gov.ie` circulars** — the `lc6_government_circulars_assets`
  wraps the `government_circulars` DLT source + ingests the
  `gov.ie/.../circulars/...` PDFs.

Cross-references:
- [`.agents/skills/dlt/SKILL.md`](../dlt/SKILL.md) — the canonical
  `@dlt.resource` template
- [`.agents/skills/baml/SKILL.md`](../baml/SKILL.md) — the
  5 lc6 BAML functions
- [`.agents/skills/cocoindex/SKILL.md`](../cocoindex/SKILL.md) —
  the 7 v1 Apps that consume the materialised DuckLake tables
- [`.agents/skills/motherduck/SKILL.md`](../motherduck/SKILL.md) —
  the 4 Dives
- [`.agents/skills/marimo/SKILL.md`](../marimo/SKILL.md) — the 6
  per-subject notebooks

## v7 flattening migration notes (added 2026-07-19)

Per openspec/changes/2026-07-14-fix-foundation-v7-flattening-and-baml-drift-v1:

- The canonical Dagster code-location entry point is:
  `uv run dagster dev -m orchestration.definitions`
  (NOT `uv run dagster dev -m cianfhoghlaim.dagster.definitions` which was the
  pre-v7 path that no longer exists)
- The 5 KCG Components map to the 5-layer DAG:
  - L1 Ingestion (CelticIngestionComponent) — NCCA / SEC / gov.ie DLT sources
  - L2 Materials (CelticMaterialsComponent) — BAML extraction with R1-R4 conformance
  - L3 Model Lifecycle (CelticModelLifecycleComponent) — 17 v1 CocoIndex Apps
  - L4 Asset Generation (CelticAssetGenerationComponent) — marimo notebooks, web routes
  - L5 Agent Ops (CelticAgentOpsComponent) — 12 agents × 5 assets = 60 assets
- Component definition files are at `orchestration/components/layer{1..5}_*.py`
- Defs tree is at `orchestration/defs/{1_ingestion,2_materials,3_model_lifecycle,4_asset_generation,5_agent_ops}/`

