# Cianfhoghlaim Dagster Layer — 5-Layer Component Architecture

The `orchestration/` module is the canonical Dagster layer for
the Cianfhoghlaim platform. As of the
**2026-06-30-dagster-ground-up-rewrite-5-layer-component-architecture**
change, the layer is organised into exactly **5 layers**, with
**one KCG-specific Dagster Component per layer** and a **YAML
`defs/` tree** that emits ~833 assets organised into 5 hierarchical
groups.

Post-v7 flattening: `orchestration/` is the canonical home (was
`cianfhoghlaim/dagster/` pre-v7). The pyproject.toml pins
`dagster>=1.13` so `dg.load_defs()` is the canonical load path.
The `[tool.dg]` section (also in pyproject.toml) declares
`registry_modules = ["orchestration.components"]` so `dg list components`
auto-discovers the 5 KCG Components.

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
`[tool.dg].registry_modules = ["orchestration.components"]`
entry in `pyproject.toml`.

Plus 5 derived Components (post-2026-08-03):

| Class | File | Purpose |
|:--|:--|:--|
| `BIEPSubjectComponent` | `components/biep_subject_component.py` | The base class — shared boilerplate for all BIEP jurisdiction components |
| `JuniorCycleSubjectComponent` | `components/junior_cycle_subject_component.py` | The 18 NCCA JC subjects (english + gaeilge + mathematics + ...) |
| `JuniorCycleShortCourseComponent` | `components/junior_cycle_subject_component.py` | The 16 JC short courses (coding + chinese + japanese + ...) |
| `JuniorCycleCBAComponent` | `components/junior_cycle_subject_component.py` | The 36 JC CBAs (18 subjects × 2 CBAs each) |
| `EnglandBoardSubjectComponent` | `components/england_board_subject_component.py` | The 49 England A-Level subjects (AQA + OCR + Edexcel per board) |
| `EnglandCrossBoardComparatorComponent` | `components/england_cross_board_comparator_component.py` | Cross-board per-subject comparator (AQA vs OCR vs Edexcel) |

## The 5-layer `defs/` tree

```
orchestration/defs/
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
`agents/routing_keywords.py` (post-v7 path; was
`meaisinfhoghlaim/agents/routing_keywords.py` pre-v7). The voice agent
(pipecat/voice_agent) is **deferred to a follow-on change** per user
direction.

Note: The `5_agent_ops/adk/` directory contains 15 sub-dirs (not 8).
The 15 = 8 ADK agents + 7 ADK agents wrapped by `BIEPSubjectComponent`
for the per-jurisdiction subjects (per the 2026-08-03 BIEP v3 fan-out).

## Developer workflow

The canonical 1.13+ workflow uses the `dg` CLI:

```bash
# List all 5 KCG Components
dg list components

# List all ~833 assets organised into 5 nested groups
# (95 hand-written @asset decorators + 783 YAML defs + 11 sensors)
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
  --app-name NewApp --module cocoindex.new_v1_app \
  --embedding-model BAAI/bge-m3

# Scaffold a new L5 agent asset
dg scaffold defs CelticAgentOpsComponent hybrid_agent \
  --agent-name hybrid_agent --framework agno --routing-keywords hybrid

# Local dev server (canonical Dagster port: 3000)
mise run dagster:dev  # http://localhost:3000
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

## `JurisdictionAssetsBase` (NEW 2026-08-15)

The canonical base class for the **10 per-jurisdiction Dagster asset wrappers**. Lives at `orchestration/defs/2_materials/_base/jurisdiction_assets_base.py` (263 LOC).

Each of the 10 jurisdictions (`ireland`, `england`, `scotland`, `wales`, `ni`, `sct_wls_ni`, `isle_of_man`, `jersey`, `guernsey`, `crown_dependencies`) has a ~378-LOC asset file at `orchestration/defs/2_materials/<jurisdiction>_education/generic_<jur>_assets.py`. After the rollout (issue #146), each becomes a ~30-LOC subclass:

```python
from orchestration.defs.2_materials._base.jurisdiction_assets_base import make_jurisdiction_assets

def pipeline_factory():
    from dlt_sources.british_isles.<jur>.education.<jur>_jurisdiction_pipeline import (
        <jur>_jurisdiction_pipeline,
    )
    return <jur>_jurisdiction_pipeline()

<jur>_assets = make_jurisdiction_assets(
    jurisdiction_name="<jur>",
    pipeline_factory=pipeline_factory,
).build_asset()
```

**Net reduction** when the 10 files are migrated: ~3,300 LOC.

The base class also exposes:
- `IrelandAssets` (the reference implementation; the only one with explicit subclass code today)
- `make_jurisdiction_assets(jurisdiction_name, pipeline_factory, ...)` — the dynamic factory for one-line rollouts
- `all_jurisdiction_assets()` — returns the list of all 10 Dagster `AssetsDefinition` objects (for the `Definitions` resolver)

**To add a new jurisdiction asset**:
1. Create the jurisdiction pipeline in `dlt_sources/british_isles/<jur>/education/<jur>_jurisdiction_pipeline.py` (subclass `JurisdictionPipelineBase`)
2. Subclass `JurisdictionAssetsBase` in the new jurisdiction asset file
3. The asset's group_name + partition_defs inherit from the base class

**To migrate an existing jurisdiction asset**:
1. Read `orchestration/defs/2_materials/_base/jurisdiction_assets_base.py` — the API is stable
2. Replace the per-jurisdiction ~378-LOC wrapper with the ~30-LOC subclass
3. Verify the asset key + partition definitions are unchanged

## Schema introspection

To introspect the 920 `@dlt.source` + ~4,900 `@dlt.resource` decorated functions from a Dagster asset (or any Python context), use:

```python
from notebooks._shared.schema import list_dlt_sources
sources = list_dlt_sources()  # returns 1963 dicts (sources + resources)
for s in sources:
    if s["dagster_asset"] is not None:
        print(s)
```

## `orchestration/defs/1_ingestion/` cleanup

The 619 empty placeholder YAMLs in `orchestration/defs/1_ingestion/{american_nations,commonwealth,european_nations,...}/` are **audited as dead** (per the 2026-08-15 audit). They reference nations/stages that have already been absorbed into the v3 generic pipeline pattern. They are NOT loaded by `mise run dagster:dev` and can be safely deleted in the cleanup follow-up (issue #146).

The 6 stale LC6 YAMLs at `orchestration/defs/1_ingestion/curriculum/lc6/{mathematics,chemistry,geography,gaeilge,english,computer_science}.yaml` were **updated 2026-08-15** to point at the live `ireland_jurisdiction_pipeline` runner (replacing pre-v7 `cianfhoghlaim.dlt.*` paths).

---

**Last updated**: 2026-08-15 (added the JurisdictionAssetsBase section + the schema introspection pointer + the 1_ingestion cleanup note).
**Owner**: Build agent.
