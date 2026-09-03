# Dagster Ground-Up Rewrite — 5-Layer Component Architecture

## Why

The Cianfhoghlaim Dagster layer has accumulated 3 years of organic growth across 4 quadrants, 5 prior openspec changes (`refactor-dlt-dagster-2026-stack-align`, `refactor-dlt-cocoindex-baml-dagster-with-pdf-pipeline`, `2026-06-29-bonneagar-v4-canonical-and-stack-migration`, `consolidate-cianfhoghlaim-pyproject-and-8-dirs`, `2026-06-30-agent-platform-cluster-hermes-cocoindex`) and now exhibits 5 interlocking problems that no incremental change can resolve.

**1. The asset graph has no architecture.** `cianfhoghlaim/dagster/definitions.py` is a 619-line monolith that does 16 hand-rolled try/except imports, 11 hand-written `@define_asset_job(...)` calls, 5 hand-written `dg.Definitions(...).merge(...)` calls, and a 200+ element `combined_assets` list. The 4-layer narrative (Ingestion → Materials → Model Lifecycle → Asset Generation) is documented in the `dagster` skill but **not modelled in code** — assets live in a flat `dagster/assets/*.py` namespace with 60+ files and no layer boundary.

**2. The KCG-specific Components exist but only ~5% of assets use them.** Three KCG Components (`CelticDltSourceComponent`, `CelticLancedbHnswComponent`, `CelticCocoindexV1Component`) exist since `refactor-dlt-dagster-2026-stack-align` and `dagster/defs/` has 6 sub-mounts (`oideachais_pipeline`, `celtic_asset_generation`, `cognify`, `croilar`, `meaisinfhoghlaim_platform`, `tuatha`). But **~190 of the ~200 assets are still hand-written `@asset` functions in `dagster/assets/*.py`** — the Components cover a thin slice of the graph.

**3. The CocoIndex v1 conformance contract is not enforced at the Dagster layer.** The 4-rule R1–R4 contract (`oideachais-cocoindex-v1` skill) is enforced by `cocoindex_v1_conformance.py` against the 17 v1 Apps, but the **Dagster asset that wraps each CocoIndex App** is hand-written per-App with ad-hoc `importlib.import_module(self.module)` + `getattr(app, "update", None)` reflection. There is no single Component that emits a conformant, typed asset per App.

**4. The agent fleet is invisible to Dagster.** The 12-agent fleet (`meaisinfhoghlaim/agents/`), the OpenClaw/OpenChamber/Hermes gateway triad, the Letta memory layer, the RisingWave event stream, and the Langfuse + MLflow observability stack are all **outside the asset graph**. There is no asset that materialises agent health, no asset that fires on agent completion, no asset_check that gates a curriculum re-ingest on the `curriculum_agent` being reachable, and no asset that anchors an agent's `SkillTreeBadge` issuance to a Dagster run_id.

**5. Dagster 1.13+ features are unused.** The platform pins Dagster ≥ 1.10 (per `pyproject.toml`) but uses **none** of the 1.13+ surface: no `AutomationCondition`, no partition-aware `@asset_check`, no `is_virtual=True` for DuckDB/LanceDB views, no state-backed Components, no hierarchical `group_name` (`group_name="1_ingestion/dlt/curriculum"`). The `dg list components`, `dg list defs`, `dg check yaml`, and `dg scaffold defs` workflow is documented but not adopted.

This change lands the **canonical 5-layer Component architecture** in one coordinated change. After this lands, the Dagster layer is recognisably idiomatic for Dagster 1.13+ + Components + Declarative Automation, and the 12-agent fleet is a first-class Dagster citizen (5th layer).

## What Changes

### The 5-layer architecture

```
Layer 0 (cross-cutting): Resources & Config
   ↓
Layer 1 (Ingestion)        : DLT sources → DuckLake raw tables
Layer 2 (Materials)        : BAML/Docling extraction → typed DuckLake + LanceDB
Layer 3 (Model Lifecycle)  : CocoIndex v1 Apps + Cognee + FalkorDB
Layer 4 (Asset Generation) : marimo dashboards + TanStack Start pages + oRPC routes
Layer 5 (Agent Operations) : 12-agent fleet + OpenClaw/OpenChamber/Hermes + Letta + RisingWave + Langfuse
```

Each layer has exactly **one** Dagster Component, **one** `defs/<layer>/defs.yaml`, and **one** hierarchical group prefix (`group_name="<N>_<layer>/<domain>"`). `dg list defs` then renders the asset graph as 5 nested groups.

### The 5 Components (one per layer)

```python
# cianfhoghlaim/dagster/components/layer1_ingestion.py
class CelticIngestionComponent(dg.Component, dg.Model):
    """L1 Ingestion — wraps one @dlt.source as a Dagster asset.
    Uses state-backed component (refresh = monthly) for the 5+ Celtic-nation sources."""
    source_id: str                        # e.g. "ie.education.curriculum"
    domain: str                           # e.g. "curriculum" / "law" / "medicine"
    nation: str                           # e.g. "ie" / "en" / "sct"
    automation: Literal["eager", "on_cron", "on_dlt_freshness", "manual"] = "on_cron"
    automation_cron: str | None = "0 2 * * *"  # 02:00 UTC daily
    state_backed: bool = False            # opt-in for the 5 high-churn sources
    state_refresh_interval: Literal["daily", "weekly", "monthly"] = "monthly"  # per user direction

# cianfhoghlaim/dagster/components/layer2_materials.py
class CelticMaterialsComponent(dg.Component, dg.Model):
    """L2 Materials — wraps one BAML extraction function as a partitioned asset.
    Partitioned by (cycle, language, subject) where applicable."""
    baml_function: str                    # e.g. "b.ExtractLeavingCertSyllabus"
    source_asset: str                     # e.g. "1_ingestion/ie/education/curriculum"
    partition_strategy: Literal["by_cycle", "by_subject", "by_nation", "none"] = "by_cycle"
    partitions_def: str | None = None     # JSON-encoded MultiPartitionsDefinition
    asset_check_kind: Literal["row_count", "baml_fidelity", "irish_fada", "lang_detect"] = "row_count"

# cianfhoghlaim/dagster/components/layer3_model_lifecycle.py
class CelticModelLifecycleComponent(dg.Component, dg.Model):
    """L3 Model Lifecycle — wraps one CocoIndex v1 App as a virtual Dagster asset.
    Enforces the 4-rule R1–R4 conformance contract via cocoindex_v1_conformance."""
    app_name: str                         # e.g. "LeabharlannBooksEmbedding"
    module: str                           # e.g. "cianfhoghlaim.cocoindex.leabharlann_embedding"
    is_virtual: bool = True               # the LanceDB table mirrors upstream automatically
    conformance_required: bool = True      # R1–R4 enforced at scaffold time
    embedding_model: Literal["BAAI/bge-m3", "BAAI/bge-large-en-v1.5"] = "BAAI/bge-large-en-v1.5"
    hnsw_index: bool = True               # drop + recreate at HNSW-DROP-THRESHOLD=50

# cianfhoghlaim/dagster/components/layer4_asset_generation.py
class CelticAssetGenerationComponent(dg.Component, dg.Model):
    """L4 Asset Generation — wraps one marimo dashboard / TanStack Start page / oRPC route
    as a Dagster asset that triggers re-materialisation on upstream changes."""
    dashboard_kind: Literal["marimo", "tanstack_page", "orpc_route", "hono_route"] = "marimo"
    dashboard_path: str                   # e.g. "notebooks/dashboards/education/mathematics.py"
    upstream_assets: list[str]            # ["3_model_lifecycle/...", ...]
    refresh_on: list[str]                 # sensor paths or cron expressions

# cianfhoghlaim/dagster/components/layer5_agent_ops.py  ← NEW
class CelticAgentOpsComponent(dg.Component, dg.Model):
    """L5 Agent Operations — wraps one agent from the 12-agent fleet as a Dagster asset.
    Emits 5 assets per agent (health, routing, memory, event, trace).

    Voice agent (pipecat) is deferred to a follow-on change per user direction.
    """
    agent_name: str                       # e.g. "curriculum_agent"
    framework: Literal["custom", "adk", "agno"] = "adk"   # no pipecat for v1
    tools: list[str]                      # e.g. ["search_curriculum_tool", "translate_text_tool"]
    memory_backend: Literal["letta", "graphiti", "cognee", "lancedb"] = "letta"
    event_stream: Literal["risingwave", "kafka", "nats"] = "risingwave"
    event_stream_endpoint: str = "risingwave.cianfhoghlaim.ie:4566"   # per user direction
    langfuse_trace_tag: str               # e.g. "agent.curriculum"
    langfuse_drop_smoke_spans: bool = True  # per user direction (don't pollute trace history)
    routing_keywords: list[str]           # appended to root_agent.py ROUTING_KEYWORDS
```

### The `defs/` tree (new shape)

```
cianfhoghlaim/dagster/
├── components/                             # 5 KCG-specific Components (5 → 5; rewrite celtic_* → layer{1..5}_*)
│   ├── layer1_ingestion.py                 # was: celtic_dlt_source.py
│   ├── layer2_materials.py                 # NEW (BAML-driven materials Component)
│   ├── layer3_model_lifecycle.py           # was: celtic_cocoindex_v1.py + celtic_lancedb_hnsw.py
│   ├── layer4_asset_generation.py          # NEW (marimo + TanStack Start + oRPC Component)
│   └── layer5_agent_ops.py                 # NEW (12-agent fleet Component; no pipecat/voice_agent for v1)
├── defs/                                   # 5 layer-defs folders (was 6; consolidate cognify into L2/L3)
│   ├── 1_ingestion/
│   │   ├── defs.yaml
│   │   ├── curriculum/                     # MultiPartitions by (cycle, language, subject)
│   │   ├── law/
│   │   ├── medicine/
│   │   ├── site_analysis/
│   │   └── filesystem/                     # leabharlann (books, zotero, takeout)
│   ├── 2_materials/
│   │   ├── defs.yaml
│   │   ├── baml_extraction/                # ExtractLeavingCertSyllabus × 33 subjects
│   │   ├── ocr_comparison/                 # 24 OCR models × 6 backends (was: ocr_comparison_assets)
│   │   ├── pdf_processing/                 # 133 leaving_cert PDFs
│   │   ├── embedding_pivot/                # BAAI/bge-large-en-v1.5 → LanceDB
│   │   └── dbt/                            # 3 dbt-duckdb models (weekly_downloads, language_distribution, ocr_confidence_by_model)
│   ├── 3_model_lifecycle/
│   │   ├── defs.yaml
│   │   ├── cocoindex_v1/                   # 17 v1 Apps via layer3_component + R1–R4 lint
│   │   ├── cognify/                        # 5-stage cross-stage cognify + 3 leabharlann cognify
│   │   └── cross_archive/                  # 3 FalkorDB edge rules (celtic-tutor → mythology etc.)
│   ├── 4_asset_generation/
│   │   ├── defs.yaml
│   │   ├── marimo_dashboards/              # 11 marimo × 5 educational stages
│   │   ├── tanstack_pages/                 # the 5 sruth/oideachais/web routes
│   │   └── orpc_routes/                    # the 6 sruth/oideachais/api routes
│   └── 5_agent_ops/
│       ├── defs.yaml
│       ├── custom/                         # root_agent
│       ├── adk/                            # 8 ADK agents (curriculum, translation, corpus, research, geospatial, statistics, curriculum_comparison, mcp_curriculum)
│       └── agno/                           # 3 Agno agents (education_research, bunchloch_research, agui_curriculum)
├── definitions.py                          # SHRUNK to ~30 lines: load_defs() + DefsFolderComponent merge
├── assets/                                 # DELETED (200+ legacy @asset functions move to defs/<layer>/<domain>/assets.py)
├── sensors/                                # SHRUNK to 1 sensor per layer (was 6 hand-rolled sensors)
├── schedules/                              # DELETED (replaced by AutomationCondition.cron(...))
├── factories.py                            # DELETED (replaced by 5 Components)
├── tenants.py, tenant_resources.py         # DELETED (replaced by 1_ingestion/tenants/ YAML defs)
├── partitionals.py, partitions_v2.py       # KEPT (partition definitions are shared utility)
├── resources.py                            # KEPT + EXTENDED with CelticAgentOpsResource + CelticLettaResource + CelticRisingWaveResource
└── dbt_translator.py                       # KEPT (dbt-duckdb bridge)
```

### Hierarchical asset group naming (Dagster 1.13.9+)

```python
@dg.asset(group_name="1_ingestion/curriculum/ie",  compute_kind="dlt", ...)
@dg.asset(group_name="2_materials/baml_extraction/leaving_cert_math", compute_kind="baml", ...)
@dg.asset(group_name="3_model_lifecycle/cocoindex_v1/leabharlann_books", compute_kind="cocoindex", ...)
@dg.asset(group_name="4_asset_generation/marimo_dashboards/primary_curriculum", compute_kind="marimo", ...)
@dg.asset(group_name="5_agent_ops/adk/curriculum_agent", compute_kind="adk", ...)
```

This renders as 5 nested groups in the Dagster UI (wildcards work: `group:"1_*"` or `group:"3_model_lifecycle/*"`).

### Declarative Automation (replaces all `@schedule`)

```python
# Old (deleted):
@schedule(cron_schedule="0 2 * * *", job=ireland_curriculum_assets_job)
def ireland_curriculum_schedule(): ...

# New (per Layer 1 Component):
@dg.asset(
    group_name="1_ingestion/curriculum/ie",
    automation_condition=dg.AutomationCondition.eager().resolve_through_virtual(),
)
def ireland_curriculum_ie(context, ducklake): ...

# New (per Layer 3 Component, with virtual-asset awareness):
@dg.asset(
    group_name="3_model_lifecycle/cocoindex_v1/leabharlann_books",
    automation_condition=(
        dg.AutomationCondition.eager()
        | dg.AutomationCondition.cron("0 */6 * * *")
    ).resolve_through_virtual(),
)
def leabharlann_books_app_update(...): ...
```

### Partition-aware `@asset_check`

```python
@dg.asset_check(
    asset=ireland_curriculum_ie,
    description="baml fidelity check on the 8 primary subjects",
    partitions_def=ireland_curriculum_partitions,   # partition-aware (Dagster 1.13+)
)
def ireland_curriculum_baml_fidelity_check(context, ducklake) -> dg.AssetCheckResult:
    ...
```

### Virtual assets for LanceDB + DuckDB views (1.13+ preview)

```python
@dg.asset(
    group_name="3_model_lifecycle/cocoindex_v1/leabharlann_zotero",
    is_virtual=True,                    # the LanceDB table mirrors upstream automatically
    deps=[dg.AssetDep("1_ingestion/filesystem/zotero", metadata=TableMetadataSet(...))],
)
def leabharlann_zotero_app(context, lancedb): ...
```

### State-backed Components (1.13+ default)

The 5 Celtic-nation ingestion sources with the highest external metadata churn (NCCA, SEC, CCEA, SQA, WJEC) use state-backed components. Per user direction, the default `state_refresh_interval` is **monthly** (not daily) to minimise unnecessary refreshes of cached external metadata.

```python
class CelticIngestionComponent(dg.Component, dg.Model, dg.StateBackedComponent):
    source_id: str
    state_refresh_interval: Literal["daily", "weekly", "monthly"] = "monthly"

    @property
    def state(self) -> CelticIngestionState:
        return CelticIngestionState.from_yaml("sources.yaml")  # cached
```

### R1–R4 conformance enforced at scaffold time

The `layer3_model_lifecycle.py` Component calls `cocoindex_v1_conformance.check_module(module)` before emitting the asset. If R1–R4 fail, `dg scaffold defs` and `dg check yaml` both error out. The 17 existing v1 Apps all pass (verified per the `oideachais-cocoindex-v1` skill).

### L5 Agent Operations — the 12 agents × 5 emitted assets

The 12-agent fleet maps to L5 as follows (per the `agent-fleet-orchestration` skill):

| Framework | Agents | L5 sub-folder | Notes |
|:--|:--|:--|:--|
| Custom | `root_agent` (1) | `5_agent_ops/custom/` | The query router + LiteLLM |
| ADK | 8 agents (curriculum, translation, corpus, research, geospatial, statistics, curriculum_comparison, mcp_curriculum) | `5_agent_ops/adk/` | |
| Agno | 3 agents (education_research, bunchloch_research, agui_curriculum) | `5_agent_ops/agno/` | |
| Pipecat | voice_agent | **DEFERRED** to follow-on change | Per user direction |

Each agent emits 5 Dagster assets:

1. `agent_health_{name}` — pings the agent's HTTP endpoint
2. `agent_routing_{name}` — verifies `routing_keywords` registered in `root_agent.py:ROUTING_KEYWORDS`
3. `agent_memory_{name}` — read+write sentinel record in the agent's Letta memory namespace
4. `agent_event_{name}` — publish `agent.{name}.ready` event to RisingWave at `risingwave.cianfhoghlaim.ie:4566`
5. `agent_trace_{name}` — Langfuse @observe span; synthetic smoke-test spans are **dropped** (per user direction, do not pollute the trace history)

Total: 12 agents × 5 assets = **60 new L5 assets**.

### Affected files (the deletion list)

**Deleted (replaced by Components + YAML defs):**

- `cianfhoghlaim/dagster/assets/*.py` (60+ files, ~6,000 LOC)
- `cianfhoghlaim/dagster/assets/by_domain/` (consolidated into `defs/<layer>/`)
- `cianfhoghlaim/dagster/assets/by_domain/pdf_processing/`
- `cianfhoghlaim/dagster/factories.py`
- `cianfhoghlaim/dagster/tenant_resources.py` + `tenants.py`
- `cianfhoghlaim/dagster/schedules.py` (replaced by `AutomationCondition.cron(...)`)
- `cianfhoghlaim/dagster/sensors/{author_archive_sensors.py, ccc_freshness_sensor.py, cognee_cron_sensor.py, curriculum_freshness.py, domain_sensors.py, leabharlann_sensors.py}`
- `cianfhoghlaim/dagster/asset_checks.py` (replaced by per-Component partition-aware checks)
- `cianfhoghlaim/dagster/components/celtic_dlt_source.py` → `layer1_ingestion.py`
- `cianfhoghlaim/dagster/components/celtic_cocoindex_v1.py` → `layer3_model_lifecycle.py`
- `cianfhoghlaim/dagster/components/celtic_lancedb_hnsw.py` (absorbed into `layer3_model_lifecycle.py`)

**Created (new Components + YAML defs tree):**

- `cianfhoghlaim/dagster/components/layer1_ingestion.py`
- `cianfhoghlaim/dagster/components/layer2_materials.py`
- `cianfhoghlaim/dagster/components/layer3_model_lifecycle.py`
- `cianfhoghlaim/dagster/components/layer4_asset_generation.py`
- `cianfhoghlaim/dagster/components/layer5_agent_ops.py`
- `cianfhoghlaim/dagster/defs/1_ingestion/{curriculum,law,medicine,site_analysis,filesystem}/defs.yaml`
- `cianfhoghlaim/dagster/defs/2_materials/{baml_extraction,ocr_comparison,pdf_processing,embedding_pivot,dbt}/defs.yaml`
- `cianfhoghlaim/dagster/defs/3_model_lifecycle/{cocoindex_v1,cognify,cross_archive}/defs.yaml`
- `cianfhoghlaim/dagster/defs/4_asset_generation/{marimo_dashboards,tanstack_pages,orpc_routes}/defs.yaml`
- `cianfhoghlaim/dagster/defs/5_agent_ops/{custom,adk,agno}/defs.yaml`

**Modified (extended resources + new 5th-layer resources):**

- `cianfhoghlaim/dagster/definitions.py` (shrunk to ~30 lines)
- `cianfhoghlaim/dagster/resources.py` (+ `CelticAgentOpsResource`, `CelticLettaResource`, `CelticRisingWaveResource`, `CelticLangfuseResource`, `CelticMlflowResource`)
- `cianfhoghlaim/dagster/sensors/` (1 sensor per layer; was 6 hand-rolled)
- `pyproject.toml` (`[tool.dg] registry_modules = ["cianfhoghlaim.dagster.components"]`)
- `meaisinfhoghlaim/agents/root_agent.py:ROUTING_KEYWORDS` (extended per scaffold)
- `.agents/skills/dagster/SKILL.md` (mark 1.13+ features as KCG-canonical)
- `.agents/skills/oideachais-cocoindex-v1/SKILL.md` (add "enforcement at the Dagster layer" section)

### Affected specs

- **MODIFIED `oideachais-pipeline`** — adds 5 Requirements: 5-Layer Component Architecture (L1 Ingestion), Partition-Aware Asset Checks (L2 Materials), Virtual CocoIndex v1 Assets (L3 Model Lifecycle), Hierarchical Asset Groups (1.13+), Declarative Automation Replaces @schedule, DBT Bridge via Upstream DbtProjectComponent
- **MODIFIED `meaisinfhoghlaim-platform`** — adds 1 Requirement: 12 Agents × 5 Dagster Assets per Agent (L5 Agent Operations)
- **ADDED `dagster-5-layer-component-architecture`** — new capability spec: 5-Layer Hierarchy, 5 KCG Components, Declarative Automation + Virtual Assets, CocoIndex v1 R1–R4 Conformance Enforced at Scaffold Time

## Impact

| Metric | Before | After |
|--|--|--|
| Lines in `dagster/definitions.py` | 619 | ~30 |
| Hand-written `@asset` functions in `dagster/assets/` | ~190 | 0 |
| Hand-written `@schedule` functions in `dagster/schedules.py` | 5+ | 0 |
| KCG-specific Components | 3 (`celtic_*`) | 5 (`layer{1..5}_*`) |
| `defs/<domain>/` sub-folders | 6 | 5 (the 5 layers; 4 layer sub-folders each) |
| Dagster assets in the asset graph | ~200 | ~260 (L5 adds 60 new) |
| Hierarchical asset groups | 0 | 5 |
| `AutomationCondition`-backed assets | 0 | ~260 |
| Partition-aware `@asset_check`s | 0 | ~50 (one per L2 BAML extraction asset) |
| Virtual assets (`is_virtual=True`) | 0 | 17 (one per CocoIndex v1 App) |
| State-backed Components | 0 | 5 (NCCA/SEC/CCEA/SQA/WJEC) |
| Dagster assets wrapping the 12-agent fleet | 0 | 60 |
| Files in `dagster/assets/` | 60+ | 0 |
| Files in `dagster/components/` | 3 | 5 (+ 2 from rewrite = 5 total) |

## Non-Goals

- The voice agent (Pipecat) is **deferred to a follow-on change** per user direction (the 13th `pipecat/` stack lands separately).
- No change to the underlying DLT sources in `cianfhoghlaim/dlt/` (only the Dagster wiring changes).
- No change to the BAML schemas in `cianfhoghlaim/baml_src/` (only the BAML-driven assets in `defs/2_materials/baml_extraction/` are reorganised).
- No change to the CocoIndex v1 Apps themselves (the R1–R4 contract is unchanged; only the Dagster wiring is canonicalised).
- No change to the FastAPI/Hono routes in `cianfhoghlaim/api/` (only their Dagster wrappers in `defs/4_asset_generation/orpc_routes/` are added).
- No change to the marimo dashboards themselves (only the `4_asset_generation/marimo_dashboards/` YAML defs are added).
- No change to the 12-agent fleet modules (only the `5_agent_ops/{custom,adk,agno}/` YAML defs are added; `root_agent.py:ROUTING_KEYWORDS` is appended-to, not rewritten).
- The `routing_keywords` extension happens at scaffold time, not runtime, so it is a static append (no runtime cost).

## Backward compatibility

- All consumer imports of the legacy `dagster/assets/*.py` modules continue to work via the `defs/<layer>/<domain>/assets.py` paths after the rewrite (the public Python symbols are preserved at the new paths).
- The `definitions.py` still constructs a single `dg.Definitions` object, so `dagster dev -m cianfhoghlaim.dagster.definitions` still works.
- The `dg list defs` output is richer (260+ assets vs 200+) but every existing asset key is still registered.
- The `dg list components` output is extended (5 vs 3) but the 3 existing Component paths still work (rewritten in-place, not deleted-then-added).
- The CocoIndex v1 R1–R4 contract is unchanged; only the enforcement point moves from `cocoindex_v1_conformance.py` (a static linter) to `layer3_model_lifecycle.py` (the scaffold-time check).

## Risk Assessment

| Risk | Mitigation |
|:--|:--|
| The 200+ legacy asset keys must be preserved (not silently dropped) | Phase 0.1 captures `dg list defs --json` snapshot; Phase 8.11 diffs before/after; missing keys are a hard-fail |
| The 5 KCG Components must each handle a real source / baml function / app / dashboard / agent | Phase 1 scaffolds one sample per Component; Phase 2 wires all 260+ assets; Phase 8.9/8.10 smoke-test the 2 most critical |
| CocoIndex v1 R1–R4 enforcement could break a previously-OK App if the lint has a bug | The 17 existing v1 Apps are pre-validated per the `oideachais-cocoindex-v1` skill; the new Component just wraps the existing linter |
| L5 Agent Operations adds 60 new assets; some may be flaky in dev (the agent endpoints may not be reachable) | The `agent_health_*` asset is the smoke test; if it fails, the downstream assets are BLOCKED via `AutomationCondition.all_deps_blocked()` |
| The voice agent is deferred, so the 13th L5 sub-folder (`pipecat/`) is intentionally absent | The spec says "12 agents × 5 assets = 60" — the math is explicit; the voice agent lands in a follow-on change |
| `state_refresh_interval=monthly` (per user direction) is longer than the 5 sources' upstream change cadence | The 5 sources (NCCA/SEC/CCEA/SQA/WJEC) publish changes weekly at most; monthly refresh is a conservative baseline; per-source override is allowed via the Component YAML |
| Langfuse smoke-test spans are dropped (per user direction), so the `agent_trace_*` assets have no visible side effect | The asset materialisation still succeeds (we return `MaterializeResult(metadata={"langfuse_span_dropped": True, "trace_tag": ...})`); observability is preserved via the `langfuse_drop_smoke_spans=True` flag in the Component YAML |
| dbt-duckdb models move to `defs/2_materials/dbt/` (not a separate analytics layer) | The 3 models are pure transformation logic, not "asset generation" in the L4 sense (they feed L4 dashboards, not the other way around); L2 is the correct home per the 4-layer narrative |

## Validation

1. `openspec validate 2026-06-30-dagster-ground-up-rewrite-5-layer-component-architecture --strict` passes
2. `dg list defs --json | jq '.[].group_name' | cut -d/ -f1 | sort -u` returns exactly 5 layer prefixes: `1_ingestion`, `2_materials`, `3_model_lifecycle`, `4_asset_generation`, `5_agent_ops`
3. `dg list defs --json | jq '. | length'` returns ≥ 260
4. `dg list components` returns the 5 KCG Components + any upstream `dagster_dlt` / `dagster_dbt` Components
5. `dg check yaml` passes on every `defs.yaml` in the tree
6. `ccc search "@schedule\(" cianfhoghlaim/dagster/` returns 0 hits
7. `ccc search "from cianfhoghlaim.dagster.assets" cianfhoghlaim/` returns 0 hits
8. `ccc search "from cianfhoghlaim.dagster.factories" cianfhoghlaim/` returns 0 hits
9. `ccc search "from cianfhoghlaim.dagster.tenant_resources" cianfhoghlaim/` returns 0 hits
10. `mise run lint:skills` still passes 123/123
11. `mise run turbo typecheck` passes
12. `dg launch --select "3_model_lifecycle/cocoindex_v1/leabharlann_books"` materialises successfully (smoke test for the L3 Component)
13. `dg launch --select "5_agent_ops/adk/curriculum_agent"` materialises successfully (smoke test for the L5 Component)
14. `dg api asset list --limit 1000 | jq '.[] | .automation_condition'` confirms every asset has an `AutomationCondition` (not null)
15. `dg list asset-checks --limit 1000 | jq '.[] | .partitions_def'` confirms the L2 BAML extraction checks have non-null `partitions_def`
16. `dg list asset-checks --limit 1000 | jq '.[] | select(.asset_key | startswith("3_model_lifecycle")) | .is_virtual'` confirms the 17 L3 CocoIndex v1 assets have `is_virtual=true`
17. The Dagster UI at `http://localhost:3335` renders 5 nested groups (no flat group_name strings)
18. `git diff --stat` shows the deletion list above is fully applied
