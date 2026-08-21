# 2026-08-15-centralized-model-schema-registry-and-deployment-control-panel-v1

## Why

The Cianfhoghlaim monorepo has **~70 distinct model names** referenced across
**5 model registries**, **8 BAML client files**, **~30 LiteLLM aliases**, **320
BAML schema files**, **96 hand-written Pydantic duplicates**, **472 CocoIndex
v1 Apps**, **920 DLT sources**, **71 capability specs**, and **88+ Docker
Compose stacks** — and there is **no single dashboard** where an operator
re-deploying the platform can see "what models are wired, what pipelines
are enabled, what schemas are active, what stacks are running". The sprawl
is documented as drift in 4 places already (`google-adk/SKILL.md:403`,
`agents/adk/config.py:18`, `litellm/config.yaml:436`, `baml_src/clients.baml:165-179`).

This change ships **one canonical model registry**, **one canonical schema
source** (BAML → Pydantic + Zod + DuckDB introspection), and **one
deployment control panel** (marimo notebook + web UI + CLI), then **actually
replaces** every drift site the audit identified (32 hardcoded
`gemini-2.0-flash` agent sites, the 96 Pydantic duplicates, the 40
European-nation CocoIndex files, the 6 Irish LC CocoIndex files, the 8 BI
parity CocoIndex files, the 619 empty `1_ingestion/` YAMLs, and the
5+ ghost-model references in `litellm/config.yaml`).

## What Changes

### A. One canonical model registry

- **NEW**: `meaisinfhoghlaim/models/registry.py` extended from 22 OCR/VLM
  entries to ~70 entries covering all 5 model families (OCR/Vision, Text
  LLM, Embedding, Reranking, Image-Gen, Voice/ASR/TTS, Translation).
  Old `VISION_MODELS` is now a subset of a new top-level `MODEL_REGISTRY`
  keyed by `(family, role)` rather than just `key`.
- **NEW**: `meaisinfhoghlaim/models/routing.py` `model_for(family, role,
  language)` API consumed by the 12-agent fleet, BAML clients, LiteLLM,
  and the 3 deployment-control-panel surfaces.
- **MODIFIED**: `bonneagar/stacks/litellm/config/config.yaml` regenerated
  by `scripts/generate_litellm_config.py` to consume `MODEL_REGISTRY` (no
  more hardcoded aliases; no more 5 ghost-model comments).
- **MODIFIED**: `baml_src/clients.baml` + `clients_llama_swap.baml` +
  `clients_ocr_ensemble.baml` rewritten to reference `MODEL_REGISTRY`
  entries rather than hardcoded model strings. The 8 commented-out
  historical clients are deleted.
- **MODIFIED**: `agents/adk/config.py` `AgentConfig` reads `model_name`
  from `MODEL_REGISTRY` (`family="text_llm", role="default"`). The 32
  hardcoded `gemini-2.0-flash` sites in `agents/adk/*` are replaced
  with `MODEL_REGISTRY.resolve("text_llm", role="default")`.
- **MODIFIED**: `agents/adk/tuatha_config.py` merged into `agents/adk/config.py`
  (single `AgentConfig` class, 5 model fields all resolved via
  `MODEL_REGISTRY`).
- **MODIFIED**: `agents/image_generation.py:IMAGE_MODELS` becomes a
  re-export of `MODEL_REGISTRY.filter(family="image_gen")`.
- **MODIFIED**: `agents/translation.py:primary_model` + `fallback_model`
  become re-exports of `MODEL_REGISTRY.filter(family="translation")`.
- **MODIFIED**: `agents/letta_client.py:139` `claude-sonnet-4-20250514`
  → `MODEL_REGISTRY.resolve("text_llm", role="long_context")`.
- **MODIFIED**: `agents/hitl_agent.py:107,449` `gpt-4o-mini`
  → `MODEL_REGISTRY.resolve("text_llm", role="fast")`.
- **MODIFIED**: `agents/agno/education_team.py:170-185` 3 model constants
  → 3 `MODEL_REGISTRY.resolve(...)` calls.
- **MODIFIED**: `agents/adk/voice_agent.py:25-29` voice model strings
  → `MODEL_REGISTRY.filter(family="voice")`.
- **MODIFIED**: `agents/adk/email_triage_agent.py:504` `gemini-2.5-pro`
  → `MODEL_REGISTRY.resolve("text_llm", role="strong")`.
- **MODIFIED**: `agents/api/_oideachais_api/services/chatterbox.py:35`
  `ResembleAI/chatterbox` → `MODEL_REGISTRY.resolve("voice", role="tts")`.
- **MODIFIED**: `agents/tuatha/tools/*` (8 sites) hardcoded
  `BAAI/bge-m3` → `MODEL_REGISTRY.resolve("embedder", role="default")`.
- **MODIFIED**: `notebooks/10_biep_pipeline_lakehouse_semantic_01_search.py`
  embedder dropdown → `MODEL_REGISTRY.filter(family="embedder")`.
- **MODIFIED**: `notebooks/16_speedrun_mmo_01_mission_control.py` embedder
  dropdown → same.
- **MODIFIED**: `spaces/_common/baml_client.py:69-71` hackathon HF
  Inference fallback chain → 3 `MODEL_REGISTRY.resolve(family="text_llm",
  role=...)` calls (or marked explicitly out-of-registry).
- **MODIFIED**: `spaces/oideachais-pdf-review/app.py:39-40` env-driven
  SUGGESTION_MODEL/EXPLANATION_MODEL → `MODEL_REGISTRY.resolve(...)`.

### B. One canonical schema source (BAML → Pydantic + Zod + DuckDB)

- **NEW**: `baml_client_ts/` directory populated by
  `mise run baml:generate` (BAML 0.223.0 TypeScript codegen — declared in
  `baml_src/baml.toml:45-48` since v0.223.0 but **never executed**).
- **MODIFIED**: `web/apps/cianfhoghlaim-leaving-cert/apps/web/src/lib/bi-ep.gen.ts`
  regenerated from BAML TypeScript codegen (replaces the DuckDB-introspection
  approach). 671 LOC becomes a ~10-line re-export of the generated module.
- **NEW**: `baml_client/zod_exports.ts` mirror file that web apps can
  `import { z } from "@baml/..."` from directly (TanStack AI + oRPC
  consumers).
- **MODIFIED**: `dlt_sources/british_isles/ireland/education/subjects/{mathematics,chemistry,computer_science,gaeilge,english,geography,history,applied_mathematics}/schema.py`
  (8 files × ~165 LOC each = **~1320 LOC of duplicate Pydantic**) replaced
  with `from cianfhoghlaim.baml_client.types import MathBilingualText, MathFormativeItem, ...`
  (the generated Pydantic from BAML). The 8 `schema.py` files become thin
  re-export shims or are deleted outright.
- **NEW**: `notebooks/_shared/schema.py` `schema_introspect(conn)` helper
  that introspects every BIEP DuckDB table + every LanceDB table + every
  BAML class and returns a unified `(table_name, column_name, type, source)`
  list consumable by the control-panel notebook.
- **NEW**: `notebooks/_shared/schema_introspect_table(table_name)` helper
  that returns the canonical column metadata for any BIEP table — used by
  the central schema view.
- **MODIFIED**: `scripts/schema-generate.ts` rewritten to consume BAML
  TypeScript codegen rather than DuckDB introspection.

### C. One deployment control panel (notebook + web UI + CLI)

- **NEW**: `notebooks/00_control_panel.py` — marimo control-panel
  notebook with 5 tabs (Models, Pipelines, Datasets, Stacks, Registry).
  Each tab reads from the canonical registry via the `_shared/db.py` +
  `_shared/schema.py` helpers and lets the operator toggle items on/off
  via `mo.ui.checkbox` / `mo.ui.multiselect`. Writes the choice to
  `deployment-choice.yaml` (committed).
- **NEW**: `web/apps/cianfhoghlaim-web/control-panel/` — TanStack Start
  + Convex + oRPC control panel. 5 routes: `/models`, `/pipelines`,
  `/datasets`, `/stacks`, `/registry`. Reads from `deployment-choice.yaml`
  via Hono API; writes through oRPC mutation. Single-source for the
  web-admin surface.
- **NEW**: `scripts/cianfhoghlaim-cli.ts` extended with
  `models list/enable/disable`, `pipelines list/enable/disable`,
  `registry audit`, `schema introspect <table>` subcommands. The CLI is
  the **source of truth** that the notebook + web UI consume.
- **NEW**: `deployment-choice.yaml` (committed, ~100 LOC) — the canonical
  record of which models/pipelines/datasets/stacks are currently enabled
  in this deployment. Consumed by `mise run cic:*` and the LLM-routing
  layer at startup.
- **NEW**: 4 mise tasks: `models:list`, `models:enable`, `pipelines:list`,
  `pipelines:enable`. All proxy to the CLI.
- **MODIFIED**: `opencode.json` `provider` block: the `minimax` provider
  is configured to consult `deployment-choice.yaml` for the current
  "default" model rather than hardcoded `MiniMax-M3`.

### D. Replace the actual duplication

- **MODIFIED**: 40 European-nation CocoIndex files
  (`cocoindex_flows/european_nations/{albania,austria,…,ukraine}/education_embedding.py`)
  collapsed into one factory-driven `cocoindex_flows/european_nations/_factory.py`
  + a 40-row config table (mirrors `oideachais-cocoindex-v1-migration`'s
  factory pattern). Each nation becomes a row in a `NATION_CONFIG` dict;
  the factory iterates and instantiates a parameterized App. Net code
  reduction: ~3,200 LOC across 40 files → ~600 LOC in 1 factory.
- **MODIFIED**: 6 Irish LC subject CocoIndex files
  (`cocoindex_flows/biep_parity/ireland_lc_{mathematics,chemistry,geography,english,gaeilge,computer_science}_embedding.py`)
  collapsed into one factory-driven
  `cocoindex_flows/biep_parity/ireland_lc_factory.py` (mirrors
  `ireland_jc_apps.py`'s factory pattern). Net code reduction: ~600 LOC
  across 6 files → ~150 LOC in 1 factory.
- **MODIFIED**: 8 British Isles parity CocoIndex files
  (`cocoindex_flows/biep_parity/{ga,en,ni,sct,wls,isle_of_man,jersey,guernsey}_education_embedding.py`)
  collapsed into one factory-driven
  `cocoindex_flows/biep_parity/bi_factory.py`. Net code reduction: ~960 LOC
  across 8 files → ~200 LOC in 1 factory.
- **MODIFIED**: 10 per-jurisdiction Dagster asset wrappers
  (`orchestration/defs/2_materials/{ireland,england,scotland,wales,ni,sct_wls_ni,isle_of_man,jersey,guernsey,crown_dependencies}_education/generic_*_assets.py`)
  share a new `JurisdictionAssetsBase` (mirrors `JurisdictionPipelineBase`
  in `dlt_sources/british_isles/_cross/`). Net code reduction: ~3,800
  LOC across 10 files → ~800 LOC in 1 base + thin per-jurisdiction
  subclasses.
- **MODIFIED**: `orchestration/defs/1_ingestion/curriculum/lc6/{mathematics,chemistry,geography,gaeilge,english,computer_science}.yaml`
  (6 stale YAMLs pointing at `cianfhoghlaim.dlt.*` import paths) updated
  to point at the live `ireland_jurisdiction_pipeline` registry runner.
- **MODIFIED**: 619 empty placeholder YAMLs across
  `orchestration/defs/1_ingestion/european_nations/`,
  `orchestration/defs/1_ingestion/commonwealth/{canada,nigeria,australia}/`,
  `orchestration/defs/1_ingestion/american_nations/` deleted (the per-
  nation DLT sources exist; the 1_ingestion/ wrappers are not actively
  executed).
- **MODIFIED**: `agents/agent_registry.py:39-184` extended to consume
  `MODEL_REGISTRY` for each agent's `litellm_routing_key` (was already
  centralized as a key, now the key resolves through the registry).

## Capabilities

### New Capabilities

- **`centralized-model-registry`**: the single canonical model registry
  that subsumes all 5 model families (OCR/Vision, Text LLM, Embedding,
  Reranking, Image-Gen, Voice/ASR/TTS, Translation). Drives LiteLLM,
  BAML clients, agent routing, and the deployment control panel.

- **`centralized-schema-registry`**: BAML is the single source of truth
  for all structured data shapes. Pydantic + Zod are codegen. DuckDB
  tables are introspected from BAML. The 96 hand-written Pydantic
  duplicates are removed.

- **`deployment-control-panel`**: the marimo notebook + web UI + CLI
  for picking models/pipelines/datasets/stacks. Single source for
  "what's enabled in this deployment".

### Modified Capabilities

- **`meaisin-24-ocr-models`**: the 22 OCR/VLM registry becomes a subset
  of the new `MODEL_REGISTRY`; the per-model 2-axis partition is
  preserved.
- **`meaisinfhoghlaim-ocr-htr`**: registered to consume
  `MODEL_REGISTRY.filter(family="ocr_vision")` rather than
  `VISION_MODELS`.
- **`meaisinfhoghlaim-platform`**: the canonical model-registry home
  is registered at `meaisinfhoghlaim/models/registry.py` (not the
  legacy `meaisinfhoghlaim/ocr/models/registry.py` shim).
- **`agent-registry`**: the 12-agent fleet consumes `MODEL_REGISTRY`
  via `model_for(family, role, language)`; the legacy `agents/adk/config.py`
  hardcoded `gemini-2.0-flash` default is replaced.
- **`agent-platform-cluster`**: the 8-stack cluster (including
  LiteLLM) regenerates its config from `MODEL_REGISTRY`.
- **`british-isles-education-pipeline`**: the 24 BIEP tables are
  exposed via `notebooks/_shared/schema.py:schema_introspect()` as
  the canonical schema view.
- **`cianfhoghlaim-baml-schemas`**: BAML TypeScript codegen is
  activated (`baml_client_ts/`); the 96 Pydantic duplicates are
  removed.
- **`cianfhoghlaim-pipeline`**: the DLT sources registry is exposed
  via `notebooks/_shared/db.py:list_dlt_sources()`.
- **`dagster-5-layer-component-architecture`**: the 5 KCG Components
  (Ingestion / Materials / Model Lifecycle / Asset Generation /
  Agent Operations) consume `MODEL_REGISTRY` for the Model Lifecycle
  layer.
- **`indexing-and-cognition`**: the `OPENCODE_REGISTRY` catalog
  consumed by the central registry dashboard.
- **`agentic-frontend-frameworks`**: the new
  `web/apps/cianfhoghlaim-web/control-panel/` is registered as the
  5th canonical surface (after `cianfhoghlaim-web`, `croilar-web`,
  `croilar-portal`, `tuatha-ui`).
- **`infrastructure-stacks`**: `deployment-choice.yaml` is registered
  as the canonical enablement file for the 88+ Docker Compose stacks.
- **`data-engineering-pipeline-documentation`**: `STATUS.md` and
  `REFACTORING.md` get entries for the 3 mega-change artifacts.

## Impact

- **cianfhoghlaim/**: ~50 new files + ~80 modified files
  - 3 new specs (this proposal)
  - 1 new `MODEL_REGISTRY` extended Python module
  - 1 new `notebooks/00_control_panel.py` marimo notebook (~600 LOC)
  - 1 new `web/apps/cianfhoghlaim-web/control-panel/` TanStack Start app (~12 files)
  - 1 new `deployment-choice.yaml`
  - 1 new `notebooks/_shared/schema.py` introspect helper
  - 3 new factory CocoIndex modules
  - 1 new Dagster `JurisdictionAssetsBase`
  - 8 deleted `dlt_sources/.../subjects/<subject>/schema.py` files (Pydantic dupes)
  - 40 collapsed European-nation CocoIndex files → 1 factory
  - 6 collapsed Irish LC CocoIndex files → 1 factory
  - 8 collapsed BI parity CocoIndex files → 1 factory
  - 619 deleted empty `1_ingestion/` YAMLs
  - 6 updated stale `1_ingestion/curriculum/lc6/*.yaml` YAMLs
  - 32 agent sites updated to consume `MODEL_REGISTRY`
  - 1 web app rewrite (`bi-ep.gen.ts` from BAML TS codegen)
  - CLI extensions in `scripts/cianfhoghlaim-cli.ts`
- **bonneagar/**: 0 changes (the LiteLLM config is regenerated from the
  registry at runtime; no IaC changes)
- **leabharlann/**: 0 changes (separate repo)
- **opencode.json**: 1 provider reconfigured to read `deployment-choice.yaml`
- **agent time**: 8 phases, ~80-100 hours total

## Motivation

The full audit results (saved as research artifacts):

- `openspec/research/2026-08-15-model-sprawl-audit.md` — 70 distinct
  model names + 5 model registries + duplication map
- `openspec/research/2026-08-15-pipeline-dedup-audit.md` — 40 + 6 + 8
  CocoIndex files + 619 empty YAMLs + 10 per-jurisdiction Dagster wrappers
- `openspec/research/2026-08-15-schema-duplication-audit.md` — 96
  Pydantic dupes + bi-ep.gen.ts drift + TS codegen dormant
- `openspec/research/2026-08-15-registry-landscape-audit.md` — 24
  distinct registries + 8 drift counts + 5 missing registries

The existing drift signals already documented (per the audit):

1. `agents/adk/config.py:18` hardcoded `gemini-2.0-flash` — flagged by
   `google-adk/SKILL.md:403-419` as "P0-#1 drift" — 32 sites bypass the
   registry
2. `agents/adk/tuatha_config.py` separate from `agents/adk/config.py` —
   two AgentConfig classes
3. `uccix-llama2-13b` in `tuatha_config.py:25` but registry marks
   `available=False`
4. `litellm/config.yaml:436` ghost `qwen3.6-35b-a3b-mtp` model
5. `baml_src/clients.baml:15-82` 8 commented-out historical clients
6. `baml_src/processing/ocr_validation.baml:334,345` model strings in
   dataclass fields (not routed)
7. `baml_src/british_isles/_cross/multi_nation_curriculum.baml:355-372`
   3 Anthropic clients with no credentials in `.infisical.env`
8. `baml.toml:45-48` TS codegen declared but `baml_client_ts/` doesn't exist
9. `bi-ep.gen.ts` 671 LOC DuckDB-introspection-derived Zod (drifts from
   BAML)
10. `dlt_sources/.../subjects/<subject>/schema.py` 96 hand-written
    Pydantic classes explicitly documented as BAML duplicates
11. `agents/agent_registry.py` 12-agent fleet uses `litellm_routing_key`
    but 32 sites in `agents/adk/*` hardcode the model

The user's request, paraphrased:

> "All throughout the repository we have different choices made for our
> sources and our destinations and in particular for this priority I
> noticed that we have a bit of sprawl with our choice for Agentic or AI
> models different models for different purposes these should be identified
> throughout the project find ways that we can have a centralised duck DB
> database to use within the context of our notebooks and in our using the
> notebook to interact with to set up and to understand the project but I
> want a centralised schema in line with what would be expected with our
> lake house and our data engineering pipelines anyway with the types of
> auto generated schemas that the data load tool to generates and also the
> BAML data schema that auto generates based on analysis and that can
> create ZOD type script scheme as those types of things that consolidation
> of types in our project that should be best that should be centralised
> in a way to the way we have been using IBIS and our duck DB so that there
> can be a centralised area of the project for someone who wants to
> re-deploy to choose what models they want what aspect of the software
> stack they want which pipelines they want to enable things like that and
> there is a lot of redundancy in the in similarities between the
> different pipelines and Coco index and DLT and all aspects of our data
> engineering and our infrastructure and key aspects of the project
> identify ways to do what i said"

Maps to 4 sub-goals:

1. **Centralized model registry** → §A above
2. **Centralized DuckDB schema for notebooks** → §B above
3. **Centralized area to re-deploy** → §C above (the marimo + web UI + CLI)
4. **Eliminate redundancy between CocoIndex / DLT / etc.** → §D above

## What changes

### Phase 0 — Foundation (model + schema registry skeletons) (~6 h)

- Create `meaisinfhoghlaim/models/registry.py:MODEL_REGISTRY` extending
  the existing `VISION_MODELS` / `CLASSICAL_OCR` / `TEXT_MODELS` with
  4 new families: `IMAGE_GEN_MODELS` (5 entries), `VOICE_MODELS`
  (5 entries), `TRANSLATION_MODELS` (3 entries), `EMBEDDING_MODELS`
  (3 entries), `RERANK_MODELS` (3 entries).
- Refactor `VISION_MODELS` to be a subset view:
  `MODEL_REGISTRY.filter(family="ocr_vision")` returns the same dict.
- Add `model_for(family: str, role: str, language: str | None = None) -> str`
  API + `MODEL_REGISTRY_MAPPING` dataclass with `key`, `unsloth_id`,
  `upstream_id`, `backend`, `role`, `available`, `notes`.
- Add `scripts/registry_audit.py` to lint that no Python file in
  `agents/`, `baml_src/`, `notebooks/`, `web/`, `orchestration/` contains
  a hardcoded model string (matches the registry pattern).
- Create `notebooks/_shared/schema.py:schema_introspect(conn)` that
  returns `list[dict]` of every BIEP table column metadata.
- Wire `baml_client_ts/` TypeScript codegen: verify `baml-cli generate`
  populates the directory on `mise run baml:generate`.
- Quality gate: `mise run lint:registry` exits 0 (no hardcoded model
  strings in the audited files).

### Phase 1 — Migrate all hardcoded model sites to `MODEL_REGISTRY` (~12 h)

- Update the 32 `LlmAgent(model=config.model_name)` sites in
  `agents/adk/*` to consume `MODEL_REGISTRY.resolve("text_llm", "default")`.
- Update `agents/adk/config.py:18` + `tuatha_config.py` so both
  AgentConfig classes consult the registry.
- Update `agents/image_generation.py:IMAGE_MODELS` to re-export
  `MODEL_REGISTRY.filter(family="image_gen")`.
- Update `agents/translation.py:primary_model/fallback_model` to
  re-export `MODEL_REGISTRY.filter(family="translation")`.
- Update `agents/letta_client.py:139`, `agents/hitl_agent.py:107,449`,
  `agents/agno/education_team.py:170-185`, `agents/adk/voice_agent.py:25-29`,
  `agents/adk/email_triage_agent.py:504` to consume `MODEL_REGISTRY`.
- Update `agents/api/_oideachais_api/services/chatterbox.py:35` to
  resolve `MODEL_REGISTRY.resolve("voice", role="tts")`.
- Update `agents/tuatha/tools/*` (8 sites) hardcoded `BAAI/bge-m3` →
  `MODEL_REGISTRY.resolve("embedder", role="default")`.
- Update `notebooks/10_biep_pipeline_lakehouse_semantic_01_search.py`
  + `notebooks/16_speedrun_mmo_01_mission_control.py` embedder
  dropdowns to `MODEL_REGISTRY.filter(family="embedder")`.
- Update `spaces/_common/baml_client.py:69-71` hackathon fallback
  chain to `MODEL_REGISTRY.resolve(...)`.
- Update `spaces/oideachais-pdf-review/app.py:39-40` env-driven
  `SUGGESTION_MODEL`/`EXPLANATION_MODEL` to `MODEL_REGISTRY.resolve(...)`.
- Update `baml_src/clients.baml` + `clients_llama_swap.baml` +
  `clients_ocr_ensemble.baml` to reference `MODEL_REGISTRY` entries
  rather than hardcoded model strings.
- Delete the 8 commented-out historical clients in `clients.baml:15-82`.
- Update `bonneagar/stacks/litellm/config/config.yaml` to be
  regenerated by `scripts/generate_litellm_config.py` from
  `MODEL_REGISTRY` (no more hardcoded aliases).
- Delete the 5 ghost-model references in `config.yaml` comments.
- Quality gate: `mise run lint:registry` exits 0.

### Phase 2 — BAML TypeScript codegen activation + Pydantic dedup (~10 h)

- Run `mise run baml:generate` to populate `baml_client_ts/`.
- Add `baml_client/zod_exports.ts` mirror file for web app imports.
- Rewrite `web/apps/cianfhoghlaim-leaving-cert/apps/web/src/lib/bi-ep.gen.ts`
  (671 LOC) to a 10-line re-export of `@baml/...` (or path-relative).
- Update `scripts/schema-generate.ts` to consume BAML TS codegen
  rather than DuckDB introspection.
- Replace the 8 `dlt_sources/.../subjects/<subject>/schema.py` files
  with `from cianfhoghlaim.baml_client.types import ...` imports.
- Delete the duplicate Pydantic classes (8 files × 12 classes = 96
  classes, ~1320 LOC).
- Quality gate: `mise run baml:generate` produces both `baml_client/`
  and `baml_client_ts/`; `mise run lint:registry` exits 0; web app
  builds green.

### Phase 3 — Centralized schema introspection (~6 h)

- Implement `notebooks/_shared/schema.py:schema_introspect(conn)`
  returning `list[dict]` of every BIEP table column metadata.
- Implement `notebooks/_shared/schema.py:schema_introspect_table(
  conn, table_name)` returning the canonical column metadata for any
  BIEP table.
- Add `notebooks/_shared/schema.py:list_dlt_sources()` returning all
  920 `@dlt.source` decorated functions + their primary keys + their
  destinations.
- Add `notebooks/_shared/schema.py:list_cocoindex_apps()` returning
  all 472 CocoIndex Apps + their LanceDB mount targets + their
  embedders.
- Add `notebooks/_shared/schema.py:list_baml_classes()` returning all
  838 BAML classes + their parent BAML files + their clients.
- Quality gate: `mise run py:typecheck` exits 0; the notebook
  `notebooks/00_control_panel.py` (Phase 4) can consume all 5
  introspection helpers.

### Phase 4 — Marimo control panel notebook (~10 h)

- Create `notebooks/00_control_panel.py` with 5 tabs:
  - **Tab 1: Models** — `mo.ui.multiselect` listing every
    `MODEL_REGISTRY` entry by family. Toggle on/off. Writes the
    choice to `deployment-choice.yaml`.
  - **Tab 2: Pipelines** — `mo.ui.multiselect` listing every DLT
    source (from `list_dlt_sources()`) + every CocoIndex App (from
    `list_cocoindex_apps()`). Toggle on/off.
  - **Tab 3: Datasets** — `mo.ui.table` showing every BIEP DuckDB
    table + column count + LanceDB table mount + row count. Read-only.
  - **Tab 4: Stacks** — `mo.ui.multiselect` listing every Docker
    Compose stack in `bonneagar/stacks/`. Toggle on/off (writes to
    `deployment-choice.yaml`).
  - **Tab 5: Registry** — `mo.ui.table` showing the full
    `MODEL_REGISTRY` view + drift warnings (e.g. "32 sites
    bypassing the registry").
- Wire the notebook to read/write `deployment-choice.yaml` via
  `_shared/deployment_choice.py:read_choice()` / `write_choice()`.
- Quality gate: notebook runs end-to-end with `marimo edit
  notebooks/00_control_panel.py`; all 5 tabs load.

### Phase 5 — Web UI control panel (~14 h)

- Create `web/apps/cianfhoghlaim-web/control-panel/` with:
  - TanStack Start route `/control-panel/models` reading
    `MODEL_REGISTRY` via Hono API (`/api/models`).
  - TanStack Start route `/control-panel/pipelines` reading
    `list_dlt_sources()` + `list_cocoindex_apps()` via Hono.
  - TanStack Start route `/control-panel/datasets` reading
    `schema_introspect()` via Hono.
  - TanStack Start route `/control-panel/stacks` reading the stack
    list via Hono.
  - TanStack Start route `/control-panel/registry` showing
    `MODEL_REGISTRY` + drift warnings.
  - oRPC mutation `/api/deployment-choice` that writes
    `deployment-choice.yaml` after a toggle.
- Wire Hono endpoints to the new
  `notebooks/_shared/registry.py` introspection helpers (no Python
  rewriting; the web UI calls Hono which calls Python via subprocess
  or via a thin Python wrapper at `web/hono-api/registry/`).
- Quality gate: `bun run dev` in `web/apps/cianfhoghlaim-web/` boots
  the control panel at `http://localhost:3000/control-panel` with all
  5 routes functional.

### Phase 6 — CLI + deployment-choice.yaml (~6 h)

- Extend `scripts/cianfhoghlaim-cli.ts` with:
  - `models list` — prints `MODEL_REGISTRY` entries (human + JSON).
  - `models enable <key>` / `models disable <key>` — writes
    `deployment-choice.yaml`.
  - `pipelines list` — prints every DLT source + CocoIndex App.
  - `pipelines enable <id>` / `pipelines disable <id>` — writes
    `deployment-choice.yaml`.
  - `stacks list` — prints every Docker Compose stack.
  - `stacks enable <name>` / `stacks disable <name>` — writes
    `deployment-choice.yaml`.
  - `registry audit` — runs `scripts/registry_audit.py` and prints
    drift count.
  - `schema introspect <table>` — runs
    `notebooks/_shared/schema.py:schema_introspect_table`.
- Create `deployment-choice.yaml` (committed, ~100 LOC) with sections:
  `enabled_models`, `enabled_pipelines`, `enabled_stacks`, with sane
  defaults (everything enabled except deprecated entries).
- Add 4 mise tasks: `models:list`, `models:enable <key>`, `pipelines:list`,
  `pipelines:enable <id>` (each proxies to the CLI).
- Update `opencode.json` `provider.minimax` block to read
  `deployment-choice.yaml` for the current "default" model.
- Quality gate: `bun run cianfhoghlaim models list` exits 0; the
  YAML validates against the JSON schema.

### Phase 7 — CocoIndex factory dedup (~10 h)

- Create `cocoindex_flows/european_nations/_factory.py` with
  `NATION_CONFIG` (40 rows) + `build_nation_app(nation) -> coco.App`
  function. Each nation becomes a row; the factory iterates and
  instantiates a parameterized App.
- Delete the 40 `cocoindex_flows/european_nations/<nation>/education_embedding.py`
  files (or make them 1-line shims that re-export the factory).
- Create `cocoindex_flows/biep_parity/ireland_lc_factory.py` with
  `LC_SUBJECT_CONFIG` (6 rows × 2 langs) + `build_lc_app(subject,
  language) -> coco.App`.
- Delete the 6 `cocoindex_flows/biep_parity/ireland_lc_<subject>_embedding.py`
  files.
- Create `cocoindex_flows/biep_parity/bi_factory.py` with
  `JURISDICTION_CONFIG` (8 rows) + `build_bi_app(jurisdiction) -> coco.App`.
- Delete the 8 `cocoindex_flows/biep_parity/{ga,en,ni,sct,wls,isle_of_man,jersey,guernsey}_education_embedding.py` files.
- Quality gate: `mise run cocoindex:conformance` exits 0 (all factory
  Apps satisfy R1+R2+R3+R4); L3 Component `defs.yaml` files updated to
  point at the new factory modules.

### Phase 8 — Dagster `JurisdictionAssetsBase` + 1_ingestion cleanup (~10 h)

- Create `orchestration/defs/2_materials/_base/jurisdiction_assets_base.py`
  with the shared `ireland_documents_ingested` / `england_documents_ingested`
  / etc. logic, parameterized on the jurisdiction pipeline.
- Refactor the 10 per-jurisdiction `generic_<jur>_assets.py` files
  to subclass `JurisdictionAssetsBase`. Each file becomes ~50 LOC.
- Update the 6 stale `orchestration/defs/1_ingestion/curriculum/lc6/*.yaml`
  files to point at the live `ireland_jurisdiction_pipeline` registry
  runner.
- Delete the 619 empty placeholder YAMLs across
  `orchestration/defs/1_ingestion/european_nations/`,
  `orchestration/defs/1_ingestion/commonwealth/{canada,nigeria,australia}/`,
  `orchestration/defs/1_ingestion/american_nations/`.
- Quality gate: `mise run dagster:dev` loads all 10 jurisdictions
  without errors; the 619 empty YAMLs are gone.

### Phase 9 — Cross-cutting integration + drift reconciliation (~6 h)

- Update `openspec/specs/indexing-and-cognition/spec.md` to reference
  the new `OPENCODE_REGISTRY` consumed by the central registry
  dashboard.
- Update `openspec/AGENTS.md` priority-specs table to add the 3
  new specs (brings to 71+3 = 74 specs).
- Update `INDEXING_AND_COGNITION.md` §8 to point at the new
  `deployment-control-panel` spec for the "how to redeploy" guidance.
- Update `agents/agent_registry.py:39-184` to consume
  `MODEL_REGISTRY.resolve(...)` for each agent's `litellm_routing_key`.
- Update `data-engineering-pipeline-documentation/STATUS.md` +
  `REFACTORING.md` to add entries for the 3 mega-change artifacts.

## Files changed (summary)

- **~50 new files + ~80 modified files** (across 8 phases)
- **0 modified existing source files in `bonneagar/`** (LiteLLM config
  is regenerated from the registry at runtime)
- **0 modified existing source files in `leabharlann/`** (separate repo)

## Spec deltas

### ADDED Requirements (3 new specs)

#### `openspec/specs/centralized-model-registry/spec.md` (canonical)

4 new Requirements (R1 + R2 + R3 + R4) covering:

- R1: Single canonical model registry covering all 5 model families
- R2: All LiteLLM + BAML + agent + embedder + image-gen + voice +
  translation sites consume the registry (zero hardcoded model strings)
- R3: Registry provides `model_for(family, role, language)` API +
  CLI + marimo tab
- R4: Registry is audited on every commit (`mise run lint:registry`)

#### `openspec/specs/centralized-schema-registry/spec.md` (canonical)

4 new Requirements (R1 + R2 + R3 + R4):

- R1: BAML is the single source of truth for all structured data shapes
- R2: BAML TypeScript codegen activated; `baml_client_ts/` is
  generated on every `mise run baml:generate`
- R3: The 96 hand-written Pydantic duplicates in
  `dlt_sources/.../subjects/<subject>/schema.py` are removed
- R4: A central DuckDB schema introspection view
  (`notebooks/_shared/schema.py`) exposes every BIEP table +
  LanceDB table + BAML class

#### `openspec/specs/deployment-control-panel/spec.md` (canonical)

5 new Requirements (R1-R5):

- R1: One marimo control-panel notebook at
  `notebooks/00_control_panel.py` with 5 tabs
- R2: One web UI control panel at
  `web/apps/cianfhoghlaim-web/control-panel/` with 5 routes
- R3: One CLI extending `scripts/cianfhoghlaim-cli.ts` with
  `models list/enable/disable`, `pipelines list/enable/disable`,
  `stacks list/enable/disable`, `registry audit`,
  `schema introspect <table>` subcommands
- R4: A `deployment-choice.yaml` (committed) is the canonical
  enablement file
- R5: All three surfaces show the same data

### MODIFIED Requirements (10 cross-referenced specs)

- `openspec/specs/meaisin-24-ocr-models/spec.md` — extend the
  registry to cover image-gen/voice/translation/embedding/rerank;
  register the new consumption rule
- `openspec/specs/meaisinfhoghlaim-ocr-htr/spec.md` — register
  the `MODEL_REGISTRY.filter(family="ocr_vision")` consumption
- `openspec/specs/meaisinfhoghlaim-platform/spec.md` — register
  the canonical model-registry home at
  `meaisinfhoghlaim/models/registry.py`
- `openspec/specs/agent-registry/spec.md` — register the
  centralized `AgentConfig` + the 12-agent fleet's consumption of
  `MODEL_REGISTRY.resolve(...)`
- `openspec/specs/agent-platform-cluster/spec.md` — register the
  new model-registry-as-LiteLLM-source + the 5 M3 routing keywords
- `openspec/specs/british-isles-education-pipeline/spec.md` —
  register the 24 BIEP tables as a centralized schema view
- `openspec/specs/cianfhoghlaim-baml-schemas/spec.md` — register
  the BAML TS codegen activation + the 96 Pydantic duplicate
  consolidation
- `openspec/specs/cianfhoghlaim-pipeline/spec.md` — register the
  DLT sources registry exposure via `notebooks/_shared/db.py`
- `openspec/specs/dagster-5-layer-component-architecture/spec.md` —
  register the 5 KCG Components' consumption of `MODEL_REGISTRY`
- `openspec/specs/indexing-and-cognition/spec.md` — register the
  central registry catalog
- `openspec/specs/agentic-frontend-frameworks/spec.md` — register
  the new web UI control panel as the 5th canonical surface
- `openspec/specs/infrastructure-stacks/spec.md` — register
  `deployment-choice.yaml` as the canonical enablement file for
  the 88+ stacks
- `openspec/specs/data-engineering-pipeline-documentation/spec.md`
  — STATUS.md + REFACTORING.md get entries for the 3 mega-change
  artifacts

## Dependencies

`Blocked by: none` — all required primitives exist (the
`meaisinfhoghlaim/models/registry.py:VISION_MODELS` 22-entry registry,
the `notebooks/_shared/db.py:connect_md()` helper, the BAML Python
client at `baml_client/`, the `dlt_sources/common/destinations_cianfhoghlaim.py:get_dlt_destination()`
factory, the `dlt_sources/british_isles/_cross/jurisdiction_pipeline_base.py`
base class, the `agents/agent_registry.py:AGENT_REGISTRY` 12-entry
registry, the 6 LC subjects + 40 European nations + 8 BI jurisdictions
+ 8 qpack subject BAML files, the `oideachais-cocoindex-v1-migration`
factory pattern, and `scripts/cianfhoghlaim-cli.ts`).

`Blocked by (soft): 2026-07-31-agentic-mesh-and-ocr-pipeline-coherence-v1`
(the LiteLLM config regeneration pattern is referenced; we extend it
to also regenerate from `MODEL_REGISTRY`).

`Affected repos: cianfhoghlaim only`. No `bonneagar/` (IaC) or
`leabharlann/` (corpus) work required.

## Risks

- **Token cost**: enabling TS codegen runs `baml-cli generate` for
  TypeScript on every `mise run baml:generate`. Adds ~30 s to the
  build (per `baml_client_ts/` size = ~3 MB of Zod-derived TS).
  Mitigated by running it conditionally on BAML changes only.
- **`bi-ep.gen.ts` rewrite**: the 671-LOC DuckDB-introspection-derived
  Zod becomes a thin re-export. Any drift between DuckDB columns and
  BAML classes will surface as type errors at the web app build. The
  drift audit confirms there are ~12 columns where DuckDB has `z.unknown()`
  because the BAML class has nested types — these need to be addressed
  by either flattening the BAML class or accepting `z.unknown()`.
- **`MODEL_REGISTRY.resolve(...)` runtime cost**: each call is a dict
  lookup (~µs); the 32 ADK agent sites resolve once at agent
  construction time (not per-call). No perf regression.
- **`deployment-choice.yaml` write race**: if 2 surfaces (notebook + web
  UI + CLI) write concurrently, the YAML could be clobbered. Mitigated
  by file-locking (`fcntl.flock` on read + write).
- **CocoIndex factory dedup**: replacing 54 CocoIndex files with 3
  factory files could break the L3 Component `defs.yaml` modules that
  import the old `cocoindex.<old_module>` paths. Mitigated by keeping
  1-line shim files that re-export the factory output for 1 release
  cycle.

## Quality gates

- `openspec validate 2026-08-15-centralized-model-schema-registry-and-deployment-control-panel-v1 --strict` MUST pass before commit
- `mise run lint:registry` MUST exit 0 (no hardcoded model strings in
  the audited files)
- `mise run cocoindex:conformance` MUST exit 0 (R1+R2+R3+R4 conformant
  for the 3 new factory Apps)
- `mise run dagster:dev` MUST load all 10 jurisdictions + the new
  control-panel notebook
- `mise run baml:generate` MUST populate both `baml_client/` and
  `baml_client_ts/`
- `bun run dev` in `web/apps/cianfhoghlaim-web/` MUST boot the control
  panel with all 5 routes functional

## Cross-references

- `openspec/specs/meaisin-24-ocr-models/spec.md` (existing OCR/VLM
  registry contract)
- `openspec/specs/agent-registry/spec.md` (existing 12-agent fleet
  wiring)
- `openspec/specs/agent-platform-cluster/spec.md` (existing 8-stack
  cluster + LiteLLM)
- `openspec/specs/cianfhoghlaim-baml-schemas/spec.md` (existing BAML
  registration spec)
- `openspec/specs/cianfhoghlaim-pipeline/spec.md` (existing DLT
  orchestration spec)
- `openspec/specs/british-isles-education-pipeline/spec.md` (the
  24 BIEP tables + BIEP v3 registry)
- `openspec/specs/cianfhoghlaim-cocoindex-v1-migration/spec.md`
  (R1+R2+R3+R4 conformance + factory pattern)
- `openspec/specs/dagster-5-layer-component-architecture/spec.md`
  (the 5 KCG Components)
- `openspec/specs/indexing-and-cognition/spec.md` (the OpenCode
  agent + skill + MCP registry)
- `openspec/specs/agentic-frontend-frameworks/spec.md` (the 4
  canonical web surfaces)
- `openspec/specs/infrastructure-stacks/spec.md` (the 88+ Docker
  Compose stacks)
- `openspec/specs/data-engineering-pipeline-documentation/spec.md`
  (STATUS.md + REFACTORING.md)
- `openspec/changes/2026-07-31-agentic-mesh-and-ocr-pipeline-coherence-v1`
  (the LiteLLM config regeneration pattern)
- `.agents/skills/ccc/SKILL.md` (semantic code search)
- `.agents/skills/baml/SKILL.md` (BAML 0.223.0 conventions)
- `.agents/skills/dlt/SKILL.md` (DLT conventions)
- `.agents/skills/cocoindex/SKILL.md` (CocoIndex v1 conformance +
  `_lifespan.py` shared home)
- `.agents/skills/dagster/SKILL.md` (Dagster asset + component
  authoring)
- `.agents/skills/motherduck/SKILL.md` (MotherDuck + DuckLake)
- `.agents/skills/marimo/SKILL.md` (marimo reactive notebook pattern)
- `.agents/skills/agentic-frontend-frameworks/SKILL.md` (TanStack
  Start + CopilotKit + AG-UI)
- `notebooks/_shared/db.py` (existing ibis-first connection helpers)
- `meaisinfhoghlaim/models/registry.py` (existing 22-entry
  `VISION_MODELS` registry)
- `agents/agent_registry.py` (existing 12-agent fleet)
- `baml_src/clients.baml` (existing 21 BAML clients)
- `dlt_sources/common/destinations_cianfhoghlaim.py` (existing
  DLT destination factory)
- `dlt_sources/british_isles/_cross/jurisdiction_pipeline_base.py`
  (existing jurisdiction pipeline base class)
- `scripts/cianfhoghlaim-cli.ts` (existing CLI)

## Research artifacts

- `openspec/research/2026-08-15-model-sprawl-audit.md` — 70 distinct
  model names + 5 model registries + duplication map
- `openspec/research/2026-08-15-pipeline-dedup-audit.md` — 40 + 6 +
  8 CocoIndex files + 619 empty YAMLs + 10 per-jurisdiction Dagster
  wrappers
- `openspec/research/2026-08-15-schema-duplication-audit.md` — 96
  Pydantic dupes + bi-ep.gen.ts drift + TS codegen dormant
- `openspec/research/2026-08-15-registry-landscape-audit.md` — 24
  distinct registries + 8 drift counts + 5 missing registries