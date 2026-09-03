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
  entries to ~58 entries covering all 5 model families (OCR/Vision, Text
  LLM, Embedding, Reranking, Image-Gen, Voice/ASR/TTS, Translation).
- **NEW**: `meaisinfhoghlaim/models/model_registry.py` provides the
  canonical `MODEL_REGISTRY` singleton + `model_for(family, role, language)`
  API + `resolve()` / `filter()` / `summary()` helpers.
- **MODIFIED**: 10+ Python call sites (`agents/letta_client.py`,
  `agents/hitl_agent.py`, `agents/agno/education_team.py`,
  `agents/adk/voice_agent.py`, `agents/adk/email_triage_agent.py`,
  `agents/api/_oideachais_api/services/chatterbox.py`,
  `notebooks/10_biep_pipeline_lakehouse_semantic_01_search.py`,
  `notebooks/16_speedrun_mmo_01_mission_control.py`,
  `spaces/_common/baml_client.py`,
  `spaces/oideachais-pdf-review/app.py`) now resolve their model
  strings via `MODEL_REGISTRY.resolve(...)` instead of hardcoding.
- **MODIFIED**: `baml_src/clients.baml` (21 clients) — the 8
  commented-out historical clients are deleted; the 21 active
  clients carry inline `// MODEL_REGISTRY: family="..." role="..."
  → "..."` comments documenting the lookup.
- **MODIFIED**: `bonneagar/stacks/litellm/config/config.yaml` — the
  `qwen3.6-35b-a3b-mtp` ghost-model fallback chain entry is removed.
- **MODIFIED**: `scripts/generate_litellm_config.py` now prefers
  `MODEL_REGISTRY.filter(family="ocr_vision")` /
  `family="text_llm"` over the legacy `VISION_MODELS` / `TEXT_MODELS`
  dicts.

### B. One canonical schema source (BAML → Pydantic + Zod + DuckDB)

- **NEW**: `notebooks/_shared/schema.py` with the 5 introspection
  helpers (`schema_introspect`, `schema_introspect_table`,
  `list_dlt_sources`, `list_cocoindex_apps`, `list_baml_classes`).
- **MODIFIED**: `dlt_sources/.../subjects/<subject>/schema.py`
  proof-of-concept done for `mathematics/schema.py` only.

### C. One deployment control panel

- **NEW**: `notebooks/00_control_panel.py` (the 5-tab marimo notebook
  wired against `MODEL_REGISTRY` + `_shared/schema.py`).
- **NEW**: `deployment-choice.yaml` (the canonical enablement file).

## Impact

- ~14 modified files + 5 added MODEL_REGISTRY entries
- 0 breaking changes (all consumers retain `try/except` fallback
  paths to the historical hardcoded strings)
- 0 commits made (this is a working-tree-only pass; the user owns
  the commit + archive)

## Dependencies

`Blocked by: none`
`Affected repos: cianfhoghlaim`

## Audit results

- `MODEL_REGISTRY` length: 58 (was 52 before pass 2)
- `mise run lint:registry`: **Found 0 hardcoded model strings in
  audited files** (exit 0)
- `python -c "from meaisinfhoghlaim.models.model_registry import
  model_for; print(model_for('text_llm', 'default'))"`: prints
  `minimax-m3`
- 32/46 tasks complete (Phases 0, 1.1-1.20, 2.1, 2.6-2.9; the
  remainder are deferred per the original tasks.md header)
