# Tasks — dagster-ground-up-rewrite-5-layer-component-architecture

## Phase 0 — Inventory + freeze (½ day)

- [ ] **0.1** Generate `dg list defs --json` snapshot → `openspec/changes/2026-06-30-dagster-ground-up-rewrite-5-layer-component-architecture/inventory/pre-rewrite.json`
- [ ] **0.2** Generate `dg list components --json` snapshot → `openspec/changes/2026-06-30-dagster-ground-up-rewrite-5-layer-component-architecture/inventory/pre-rewrite-components.json`
- [ ] **0.3** `ccc search "from cianfhoghlaim.dagster.assets"` → count legacy `@asset` callers (expected ~190)
- [ ] **0.4** Capture the 6 KCG defs sub-folder shapes → `openspec/changes/2026-06-30-dagster-ground-up-rewrite-5-layer-component-architecture/inventory/pre-rewrite-defs-tree.txt`
- [ ] **0.5** Tag this commit `pre-dagster-rewrite` for the rollback path

## Phase 1 — Components (rewrite the 5 KCG Components)

- [ ] **1.1** `cianfhoghlaim/dagster/components/layer1_ingestion.py` (rewrite of `celtic_dlt_source.py`)
  - Subclass `dg.Component`, `dg.Model`, `dg.StateBackedComponent`
  - Reads `source_id`, `domain`, `nation`, `automation`, `automation_cron`, `state_backed`, `state_refresh_interval` (default `"monthly"`)
  - Emits 1 `@asset(group_name=f"1_ingestion/{domain}/{nation}", automation_condition=...)`
  - When `state_backed=True`, uses `dg.StateBackedComponent` with `state_refresh_interval` defaulting to `"monthly"` per user direction
  - Validates the 5 high-churn sources (NCCA, SEC, CCEA, SQA, WJEC) at scaffold time
- [ ] **1.2** `cianfhoghlaim/dagster/components/layer2_materials.py` (NEW)
  - Subclass `dg.Component`, `dg.Model`
  - Reads `baml_function`, `source_asset`, `partition_strategy`, `asset_check_kind`
  - Emits 1 `@asset(group_name=f"2_materials/baml_extraction/{subject}")` + 1 `@asset_check(partitions_def=...)`
- [ ] **1.3** `cianfhoghlaim/dagster/components/layer3_model_lifecycle.py` (rewrite of `celtic_cocoindex_v1.py` + absorbs `celtic_lancedb_hnsw.py`)
  - Subclass `dg.Component`, `dg.Model`
  - Reads `app_name`, `module`, `is_virtual=True`, `conformance_required=True`, `embedding_model`, `hnsw_index`
  - Calls `cocoindex_v1_conformance.check_module(module)` before emitting
  - On pass: emits 1 `@asset(is_virtual=True, group_name="3_model_lifecycle/cocoindex_v1/{app_name}", automation_condition=eager().resolve_through_virtual())`
  - On fail: raises `ConformanceViolation(R1/R2/R3/R4)` with the exact rule that failed
- [ ] **1.4** `cianfhoghlaim/dagster/components/layer4_asset_generation.py` (NEW)
  - Subclass `dg.Component`, `dg.Model`
  - Reads `dashboard_kind`, `dashboard_path`, `upstream_assets`, `refresh_on`
  - Emits 1 `@asset(group_name="4_asset_generation/{kind}/{slug}")` that exec's the marimo/TanStack Start page
- [ ] **1.5** `cianfhoghlaim/dagster/components/layer5_agent_ops.py` (NEW)
  - Subclass `dg.Component`, `dg.Model`
  - Reads `agent_name`, `framework` (one of `custom|adk|agno`; `pipecat` is deferred to a follow-on change per user direction), `tools`, `memory_backend`, `event_stream`, `event_stream_endpoint` (default `"risingwave.cianfhoghlaim.ie:4566"` per user direction), `langfuse_trace_tag`, `langfuse_drop_smoke_spans` (default `True` per user direction), `routing_keywords`
  - Emits 5 `@asset`s per agent:
    - `agent_health_{name}` — ping the agent's HTTP endpoint, return `MaterializeResult(metadata={"latency_ms": ...})`
    - `agent_routing_{name}` — verify `routing_keywords` are registered in `root_agent.py:ROUTING_KEYWORDS`
    - `agent_memory_{name}` — read/write Letta memory check
    - `agent_event_{name}` — publish a `agent.{name}.ready` event to RisingWave at `event_stream_endpoint`
    - `agent_trace_{name}` — Langfuse @observe span; if `langfuse_drop_smoke_spans=True`, return `MaterializeResult(metadata={"langfuse_span_dropped": True, "trace_tag": ...})` without persisting the span
  - Appends `routing_keywords` to `meaisinfhoghlaim/agents/root_agent.py:ROUTING_KEYWORDS`
- [ ] **1.6** `pyproject.toml` registers the 5 new components via `[tool.dg] registry_modules = ["cianfhoghlaim.dagster.components"]`
- [ ] **1.7** `dg list components` SHALL show `CelticIngestionComponent`, `CelticMaterialsComponent`, `CelticModelLifecycleComponent`, `CelticAssetGenerationComponent`, `CelticAgentOpsComponent`
- [ ] **1.8** `dg check yaml` SHALL pass on a sample scaffold (`dg scaffold defs CelticIngestionComponent test_ingest --source-id ie.education.curriculum`)

## Phase 2 — `defs/` tree (rewrite the 6 defs sub-folders as 5 layer-folders)

- [ ] **2.1** `defs/1_ingestion/defs.yaml` — root mount + 1 layer-folder per domain
- [ ] **2.2** `defs/1_ingestion/curriculum/` — 4 MultiPartition (cycle × language × subject) `DltLoadCollectionComponent` instances + 33 `@dlt.source` defs
- [ ] **2.3** `defs/1_ingestion/law/` — 7 nation `DltLoadCollectionComponent` instances (consolidated from `by_domain/law.py`)
- [ ] **2.4** `defs/1_ingestion/medicine/` — 9 nation `DltLoadCollectionComponent` instances (consolidated from `by_domain/medicine.py`)
- [ ] **2.5** `defs/1_ingestion/site_analysis/` — 6 nation `DltLoadCollectionComponent` instances
- [ ] **2.6** `defs/1_ingestion/filesystem/` — 5 leabharlann `DltLoadCollectionComponent` instances
- [ ] **2.7** `defs/2_materials/defs.yaml` + 5 sub-folders (`baml_extraction`, `ocr_comparison`, `pdf_processing`, `embedding_pivot`, `dbt`)
- [ ] **2.8** `defs/3_model_lifecycle/defs.yaml` + 3 sub-folders (`cocoindex_v1`, `cognify`, `cross_archive`)
  - 17 `CelticModelLifecycleComponent` instances (one per v1 App) — auto-discovered from `cianfhoghlaim/cocoindex/__init__.py`
- [ ] **2.9** `defs/4_asset_generation/defs.yaml` + 3 sub-folders (`marimo_dashboards`, `tanstack_pages`, `orpc_routes`)
- [ ] **2.10** `defs/5_agent_ops/defs.yaml` + 3 sub-folders (`custom`, `adk`, `agno`)
  - 12 `CelticAgentOpsComponent` instances (one per agent in the 12-agent fleet; `pipecat/voice_agent` is deferred to a follow-on change per user direction)
- [ ] **2.11** `dg list defs` SHALL render 5 nested groups with 260+ assets
- [ ] **2.12** `dg check yaml` SHALL pass on every `defs.yaml` in the tree

## Phase 3 — `definitions.py` shrink (delete ~590 lines of legacy bootstrap)

- [ ] **3.1** Rewrite `definitions.py` to ~30 lines:
  ```python
  from dagster_components import load_defs
  import cianfhoghlaim.dagster.defs as _defs_pkg
  defs = load_defs(defs_root=_defs_pkg)
  ```
- [ ] **3.2** Delete the 16 try/except import blocks (replaced by Components + YAML defs)
- [ ] **3.3** Delete the 11 hand-written `@define_asset_job(...)` calls (replaced by per-Component job)
- [ ] **3.4** Delete the 5 hand-written `dg.Definitions(...).merge(...)` chain (replaced by `load_defs`)
- [ ] **3.5** Delete `CONCURRENCY_LIMITS` dict (replaced by per-asset `op_tags={"dagster/concurrency_key": ...}` emitted by Components)
- [ ] **3.6** Delete `oideachais_dbt_assets` manual bootstrap (replaced by `DbtProjectComponent` in `defs/2_materials/dbt/`)

## Phase 4 — Delete legacy assets + factories (the big deletion)

- [ ] **4.1** `rm cianfhoghlaim/dagster/assets/*.py` (60+ files, ~6,000 LOC; replaced by `defs/<layer>/<domain>/`)
- [ ] **4.2** `rm cianfhoghlaim/dagster/assets/by_domain/` (consolidated into `defs/<layer>/`)
- [ ] **4.3** `rm cianfhoghlaim/dagster/assets/by_domain/pdf_processing/` (consolidated into `defs/2_materials/pdf_processing/`)
- [ ] **4.4** `rm cianfhoghlaim/dagster/factories.py` (replaced by 5 Components)
- [ ] **4.5** `rm cianfhoghlaim/dagster/tenant_resources.py` + `tenants.py` (replaced by `defs/1_ingestion/tenants/` YAML)
- [ ] **4.6** `rm cianfhoghlaim/dagster/schedules.py` (replaced by `AutomationCondition.cron(...)`)
- [ ] **4.7** `rm cianfhoghlaim/dagster/sensors/{author_archive_sensors.py, ccc_freshness_sensor.py, cognee_cron_sensor.py, curriculum_freshness.py, domain_sensors.py, leabharlann_sensors.py}` (replaced by 1 sensor per layer in `sensors/layer{N}.py`)
- [ ] **4.8** `rm cianfhoghlaim/dagster/asset_checks.py` (replaced by partition-aware `@asset_check` emitted per-Component)
- [ ] **4.9** `rm cianfhoghlaim/dagster/components/celtic_dlt_source.py` (rewritten as `layer1_ingestion.py`)
- [ ] **4.10** `rm cianfhoghlaim/dagster/components/celtic_cocoindex_v1.py` (rewritten as `layer3_model_lifecycle.py`)
- [ ] **4.11** `rm cianfhoghlaim/dagster/components/celtic_lancedb_hnsw.py` (absorbed into `layer3_model_lifecycle.py`)
- [ ] **4.12** `ccc search "from cianfhoghlaim.dagster.assets"` SHALL return 0 hits (all callers migrated to `defs/<layer>/<domain>/assets.py`)
- [ ] **4.13** `ccc search "from cianfhoghlaim.dagster.factories"` SHALL return 0 hits
- [ ] **4.14** `ccc search "@schedule("` SHALL return 0 hits inside `dagster/` (all migrated to `AutomationCondition.cron(...)`)
- [ ] **4.15** Verify `dg list defs --json | jq '.[] | .group_name' | cut -d/ -f1 | sort -u` shows ONLY the 5 hierarchical group prefixes

## Phase 5 — CocoIndex v1 conformance enforcement (R1–R4 at scaffold time)

- [ ] **5.1** Add `cocoindex_v1_conformance.check_module(module)` call inside `layer3_model_lifecycle.py:build_defs()` BEFORE emitting the asset
- [ ] **5.2** On R1–R4 fail, raise `dg.Failure` with the exact rule that failed + a `dg.MetadataValue.md(...)` with the fix instructions
- [ ] **5.3** Run `dg check yaml` on all 17 v1 App YAML defs — all SHALL pass
- [ ] **5.4** Update `oideachais-cocoindex-v1/SKILL.md` to add the new "enforcement at the Dagster layer" section
- [ ] **5.5** Add a Dagster `asset_check` `3_model_lifecycle/cocoindex_v1/cocoindex_v1_conformance_drift` that re-runs the lint weekly (scheduled via `AutomationCondition.cron("0 6 * * 1")`)

## Phase 6 — Agent Operations (L5 — the new layer)

- [ ] **6.1** `defs/5_agent_ops/custom/defs.yaml` — `root_agent` Component
- [ ] **6.2** `defs/5_agent_ops/adk/defs.yaml` — 8 ADK agents × 5 emitted assets each = 40 new assets
- [ ] **6.3** `defs/5_agent_ops/agno/defs.yaml` — 3 Agno agents × 5 = 15 new assets
- [ ] **6.4** *(deferred)* `defs/5_agent_ops/pipecat/defs.yaml` — voice_agent × 5 = 5 new assets. **Deferred to a follow-on change per user direction.**
- [ ] **6.5** `resources.py` — add `CelticLettaResource` (letta.cianfhoghlaim.ie:8283), `CelticRisingWaveResource` (risingwave.cianfhoghlaim.ie:4566), `CelticLangfuseResource` (langfuse.cianfhoghlaim.ie:3000), `CelticMlflowResource` (mlflow.cianfhoghlaim.ie:5000)
- [ ] **6.6** Wire `celtic_agent_ops.py` Component to call `LettaClient.get_memory()`, `RisingWavePublisher.publish()`, `langfuse_trace(...)`, `mlflow_log(...)`
- [ ] **6.7** Append `routing_keywords` to `meaisinfhoghlaim/agents/root_agent.py:ROUTING_KEYWORDS` at scaffold time
- [ ] **6.8** `dg launch --assets "5_agent_ops/*"` SHALL materialise all 60 new L5 assets (12 agents × 5; pipecat/voice_agent excluded per user direction)

## Phase 7 — Dagster 1.13+ feature rollout

- [ ] **7.1** All `@asset`s emitted by Components use `automation_condition=AutomationCondition.eager() | AutomationCondition.cron(...)` (NO `@schedule`)
- [ ] **7.2** All L3 CocoIndex App assets use `is_virtual=True` + `AutomationCondition.eager().resolve_through_virtual()`
- [ ] **7.3** All L2 BAML extraction assets have a partition-aware `@asset_check(partitions_def=...)`
- [ ] **7.4** The 5 L1 high-churn sources (NCCA/SEC/CCEA/SQA/WJEC) use state-backed Components with `state_refresh_interval="monthly"` (per user direction)
- [ ] **7.5** Update `.agents/skills/dagster/SKILL.md` to mark 1.13+ features as KCG-canonical

## Phase 8 — Cross-cutting docs + validation

- [ ] **8.1** Update `cianfhoghlaim/dagster/README.md` with the 5-layer Component architecture diagram + the `dg` CLI workflow
- [ ] **8.2** Update `openspec/specs/dagster-5-layer-component-architecture/spec.md` (mirror of the change's spec delta)
- [ ] **8.3** Update `openspec/specs/oideachais-pipeline/spec.md` (MODIFIED) — the layer-membership rule + the Component-must-not-be-hand-written rule
- [ ] **8.4** Update `openspec/specs/meaisinfhoghlaim-platform/spec.md` (MODIFIED) — the 12-agent × 5-emitted-asset rule
- [ ] **8.5** Update `openspec/AGENTS.md` — add `dagster-5-layer-component-architecture` to the 35-spec catalogue + quadrant map
- [ ] **8.6** Update `openspec/project.md` — add the new capability to the project conventions
- [ ] **8.7** `openspec validate 2026-06-30-dagster-ground-up-rewrite-5-layer-component-architecture --strict` SHALL pass
- [ ] **8.8** `mise run lint:skills` SHALL still pass 123/123
- [ ] **8.9** `mise run turbo typecheck` SHALL pass
- [ ] **8.10** `dg dev` SHALL start with no errors + 5 nested groups + 260+ assets visible
- [ ] **8.11** `dg launch --select "3_model_lifecycle/cocoindex_v1/leabharlann_books"` SHALL materialise successfully (smoke test for L3)
- [ ] **8.12** `dg launch --select "5_agent_ops/adk/curriculum_agent"` SHALL materialise successfully (smoke test for L5)
- [ ] **8.13** `dg list defs --json | jq '. | length'` SHALL return ≥ 260
- [ ] **8.14** `dg list defs --json | jq '.[] | select(.is_virtual == true) | .key' | wc -l` SHALL return ≥ 17
- [ ] **8.15** `dg list asset-checks --json | jq '.[] | select(.partitions_def != null) | .asset_key' | wc -l` SHALL return ≥ 50

## Phase 9 — Rollback

- [ ] **9.1** If Phase 8 fails: `git revert` to the `pre-dagster-rewrite` tag from Phase 0.5
- [ ] **9.2** Verify `dg list defs` returns the legacy 200+ assets (rollback sanity check)

## Phase 10 — Follow-on change (out of scope here, but tracked)

- [ ] **10.1** *Future:* `2026-07-add-pipecat-voice-agent-to-l5` — add the 13th L5 sub-folder `5_agent_ops/pipecat/` + 5 emitted assets for the voice agent (per user direction: deferred from this change).
