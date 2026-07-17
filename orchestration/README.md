# Cianfhoghlaim Dagster Layer — 5-Layer Component Architecture

The `cianfhoghlaim/dagster/` module is the canonical Dagster layer for
the Cianfhoghlaim platform. As of the
**2026-06-30-dagster-ground-up-rewrite-5-layer-component-architecture**
change, the layer is organised into exactly **5 layers**, with
**one KCG-specific Dagster Component per layer** and a **YAML
`defs/` tree** that emits 260+ assets organised into 5 hierarchical
groups.

## The 5 layers

```
┌────────────────────────────────────────────────────────┐
│  Layer 1 (Ingestion)        : DLT → DuckLake raw        │
│  Layer 2 (Materials)        : BAML/Docling → typed     │
│  Layer 3 (Model Lifecycle)  : CocoIndex v1 + Cognee    │
│  Layer 4 (Asset Generation) : marimo + TanStack + oRPC  │
│  Layer 5 (Agent Operations) : 12-agent fleet + Letta    │
└────────────────────────────────────────────────────────┘
```

## The 5 Components

| Layer | Component | File |
|:--|:--|:--|
| L1 | `CelticIngestionComponent` | `components/layer1_ingestion.py` |
| L2 | `CelticMaterialsComponent` | `components/layer2_materials.py` |
| L3 | `CelticModelLifecycleComponent` | `components/layer3_model_lifecycle.py` |
| L4 | `CelticAssetGenerationComponent` | `components/layer4_asset_generation.py` |
| L5 | `CelticAgentOpsComponent` | `components/layer5_agent_ops.py` |

Each Component is a subclass of `dagster.Component` and emits exactly
one or more `@asset` definitions via `build_defs()`. They are
auto-discovered by the `dg` CLI via the
`[tool.dg].registry_modules = ["cianfhoghlaim.dagster.components"]`
entry in `cianfhoghlaim/pyproject.toml`.

## The 5-layer `defs/` tree

```
cianfhoghlaim/dagster/defs/
├── 1_ingestion/                        # L1 CelticIngestionComponent
│   ├── curriculum/                     # MultiPartition by (cycle, language, subject)
│   ├── law/                           # 7 nation @dlt_assets consolidated
│   ├── medicine/                      # 9 nation @dlt_assets consolidated
│   ├── site_analysis/
│   └── filesystem/                    # leabharlann (books, zotero, takeout)
├── 2_materials/                        # L2 CelticMaterialsComponent
│   ├── baml_extraction/               # ExtractLeavingCertSyllabus × 33 subjects
│   ├── ocr_comparison/                # 24 OCR models × 6 backends
│   ├── pdf_processing/                # 133 leaving_cert PDFs
│   ├── embedding_pivot/               # BAAI/bge-large-en-v1.5 → LanceDB
│   └── dbt/                           # 3 dbt-duckdb models (DbtProjectComponent)
├── 3_model_lifecycle/                  # L3 CelticModelLifecycleComponent
│   ├── cocoindex_v1/                  # 19 v1 Apps (R1–R4 enforced at scaffold)
│   ├── cognify/                       # 5-stage cross-stage cognify
│   └── cross_archive/                 # 3 FalkorDB edge rules
├── 4_asset_generation/                 # L4 CelticAssetGenerationComponent
│   ├── marimo_dashboards/             # 11 marimo × 5 educational stages
│   ├── tanstack_pages/                # 5 TanStack Start routes
│   └── orpc_routes/                   # 6 oRPC routes
└── 5_agent_ops/                        # L5 CelticAgentOpsComponent
    ├── custom/                        # root_agent (1)
    ├── adk/                           # 8 ADK agents × 5 emitted assets each
    └── agno/                          # 3 Agno agents × 5 emitted assets each
                                       # (pipecat/voice_agent deferred to follow-on change)
```

## Dagster 1.13+ features in use

- **`AutomationCondition`** replaces all `@schedule` calls. Every
  asset has an `automation_condition=AutomationCondition.cron(...)`
  or `.eager() | .any_deps_updated()` composed expression.
- **`is_virtual=True`** on the 19 L3 CocoIndex v1 App assets (the
  LanceDB table mirrors its L1 upstream automatically).
- **`.resolve_through_virtual()`** on L3 + L5 automation conditions
  (so a virtual asset's automation chain looks through to its L1
  upstream).
- **Partition-aware `@asset_check`** on the L2 BAML extraction
  assets (e.g. `leaving_cert_math_baml_fidelity_check` evaluates
  the `(2026, en, mathematics)` partition in isolation).
- **`StateBackedComponent`** on the 5 L1 high-churn sources
  (NCCA, SEC, CCEA, SQA, WJEC) with `state_refresh_interval="monthly"`
  (per user direction). State is persisted via `DefsStateConfigArgs.local_filesystem()`.
- **Hierarchical `group_name`** of the form
  `"<N>_<layer>/<domain>/<slug>"` (e.g.
  `1_ingestion/curriculum/ie`, `5_agent_ops/adk/curriculum_agent`).
  Wildcards work in the UI search bar (`group:"3_model_lifecycle/*"`).
- **Dagster Components (`dg.Component`)** for all 5 KCG-specific
  factories, registered in `pyproject.toml:[tool.dg].registry_modules`.

## The R1–R4 CocoIndex v1 conformance contract (L3)

`CelticModelLifecycleComponent` enforces the 4-rule R1–R4 contract
(`cianfhoghlaim-cocoindex-v1` skill) at scaffold time by static
source-text inspection of the v1 App module, BEFORE emitting the
asset:

- **R1** — Module imports `from ._lifespan import shared_lifespan`
- **R2** — Module imports the canonical ContextKeys (`LANCE_DB`,
  `EMBEDDER`, `RESOLVED_FILE_REGISTRY`) OR declares an additional
  one with `# R2-exempt: <reason>`
- **R3** — `coco.App(...)` is at module scope (NOT inside a function
  body)
- **R4** — At least one `@coco.fn(` decorator is present

On R1–R4 fail, `ConformanceViolation` is raised with the exact
rule + fix instructions.

## The 12-agent fleet (L5)

`CelticAgentOpsComponent` wraps one agent from the 12-agent fleet as
5 Dagster assets:

1. `agent_health_<name>` — pings the agent's HTTP endpoint
2. `agent_routing_<name>` — verifies `routing_keywords` are registered
   in `meaisinfhoghlaim/agents/routing_keywords.py:ROUTING_KEYWORDS`
3. `agent_memory_<name>` — read/write sentinel in the agent's Letta
   memory namespace
4. `agent_event_<name>` — publishes `agent.<name>.ready` to RisingWave
   at `risingwave.cianfhoghlaim.ie:4566` (per user direction)
5. `agent_trace_<name>` — emits a Langfuse @observe span; the
   synthetic smoke-test span is **dropped** (per user direction) to
   avoid polluting the trace history

The 12 agents (1 custom + 8 ADK + 3 Agno) are listed in
`meaisinfhoghlaim/agents/routing_keywords.py`. The voice agent
(pipecat/voice_agent) is **deferred to a follow-on change** per user
direction.

## Developer workflow

The canonical 1.13+ workflow uses the `dg` CLI:

```bash
# List all 5 KCG Components
dg list components

# List all 260+ assets organised into 5 nested groups
dg list defs

# Validate all defs.yaml files
dg check yaml

# Scaffold a new L1 ingestion asset
dg scaffold defs CelticIngestionComponent ie_education_geography \
  --source-id ie.education.geography --domain curriculum --nation ie \
  --automation on_cron --automation_cron "0 4 * * *"

# Scaffold a new L2 BAML extraction asset
dg scaffold defs CelticMaterialsComponent leaving_cert_english \
  --baml_function b.ExtractLeavingCertSyllabus \
  --source_asset 1_ingestion/curriculum/ie/education \
  --subject english --language en --partition_strategy by_cycle \
  --asset_check_kind baml_fidelity

# Scaffold a new L3 v1 App asset
dg scaffold defs CelticModelLifecycleComponent new_v1_app \
  --app-name NewApp --module cianfhoghlaim.cocoindex.new_v1_app \
  --embedding-model BAAI/bge-large-en-v1.5

# Scaffold a new L5 agent asset
dg scaffold defs CelticAgentOpsComponent hybrid_agent \
  --agent-name hybrid_agent --framework agno --routing-keywords hybrid

# Local dev server
dg dev  # http://localhost:3335
```

## Code-location registration

The cianfhoghlaim code-location is registered in `dg.toml` (the
Dagster workspace config). Multiple code-locations can be
registered alongside the engineering code-location
(`oideachais`).

## Cross-references

- `openspec/changes/2026-06-30-dagster-ground-up-rewrite-5-layer-component-architecture/`
- `openspec/specs/dagster-5-layer-component-architecture/spec.md`
- `openspec/specs/cianfhoghlaim-pipeline/spec.md` (modified)
- `openspec/specs/meaisinfhoghlaim-platform/spec.md` (modified)
- `.agents/skills/dagster/SKILL.md` (Dagster 1.13+ patterns)
- `.agents/skills/cianfhoghlaim-cocoindex-v1/SKILL.md` (R1–R4 contract)
- `.agents/skills/dlt/SKILL.md` (DLT integration)
- `.agents/skills/agent-fleet-orchestration/SKILL.md` (12-agent fleet)
