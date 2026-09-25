# adk-asset-gen-pillar3 Specification

## Purpose
`adk-asset-gen-pillar3` is the contract that the ADK 2 Pillar 3
deep-research pipelines always end with a `render_assets_node` that
produces typed visual assets via the 5 `image_gen` MODEL_REGISTRY
entries. This replaces the 6 `_stub_generate_image` calls + the 5
`*_TOOL = None` placeholders in `agents/adk/tools/image_generation.py` +
`agents/adk/image_generation_agent.py` with real LiteLLM-routed image-gen
calls. Part of the convergence saga
(`openspec/plans/2026-10-01-convergence-saga-v1.md`).

## ADDED Requirements

### Requirement: Real image-gen calls (no stubs)

The `agents/adk/tools/image_generation.py` module SHALL replace the 3
`_stub_generate_image` async functions (at lines 547, 553, 565) with real
LiteLLM-routed calls that:

1. Resolve the model via `MODEL_REGISTRY.filter(family='image_gen')` + `model_for('image_gen', role)` (NEVER hardcode a model string)
2. Call `litellm.completion(model=resolved, messages=[{"role":"user","content":prompt}], api_base=...)` with the appropriate provider routing
3. Return a typed dict: `{"asset_id": str, "url": str, "prompt": str, "model": str, "role": str, "sha256": str, "latency_ms": int, "metadata": dict}`
4. Surface a clear error message on failure (no silent `{"stub": True}` returns)

#### Scenario: Real asset generated via qwen-image
- **GIVEN** an operator runs `python scripts/asset_bench.py "An Irish round tower at sunset"`
- **AND** `local/image/qwen-image` is available (per MODEL_REGISTRY)
- **WHEN** the bench script calls `generate_2d_asset(prompt="An Irish round tower at sunset", role="bilingual")`
- **THEN** the tool calls LiteLLM with the qwen-image model
- **AND** the response contains a real `url` + `asset_id` + `sha256` (NOT `"stub": True`)
- **AND** the asset is upserted to `lance://media.image_gen_chunks`

#### Scenario: Stale stub fallback removed
- **WHEN** a caller asks for an asset via the legacy `GENERATE_2D_ASSET_TOOL` import path
- **THEN** the tool raises `ImportError` (the stub was removed)
- **AND** the error message redirects to the new `generate_2d_asset` import path

### Requirement: Pillar 3 → image-gen wiring (per pipeline)

The system MUST wire each of the 5 Pillar 3 deep-research pipelines
(`aistear_deep_research` + `primary_deep_research` +
`jc_deep_research` + `sc_deep_research` + `tertiary_deep_research`)
to add a `render_assets_node` after the existing `synthesize` node
that:

1. Takes the briefing as input
2. Generates N visual assets (subject illustrations + diagrams) via the 5 image-gen models
3. Uses a shared `agents/workflows/_render_assets_node.py` helper (to avoid duplication)
4. Returns the asset URLs + LanceDB record IDs as the final pipeline output
5. Edges the new node into the existing Workflow with `(START, decompose, research_topic, synthesize, render_assets)`

#### Scenario: Aistear Pillar 3 produces 12 assets
- **WHEN** an operator runs `python scripts/asset_bench.py` with the Aistear pipeline
- **THEN** the briefing produces 4 subject illustrations (one per Aistear theme: well-being + identity + communicating + exploring-thinking) + 4 theme diagrams
- **AND** all 8 assets are in `lance://media.image_gen_chunks`
- **AND** the marimo notebook at `notebooks/dashboards/asset_gen_demo.py` shows them

#### Scenario: SC Pillar 3 produces 50+ assets
- **WHEN** the SC pipeline runs end-to-end (decompose → research → synthesise → render)
- **THEN** the asset count ≥ 50 (1 per SC subject + 1 per past paper + 1 per marking scheme)
- **AND** the 50+ LanceDB records are queryable via `SELECT * FROM media.image_gen_chunks WHERE pipeline = 'sc_deep_research'`

### Requirement: 24 agents wired through image-gen tools

The system MUST wire the 24-agent fleet (10 K-12 + 14 tertiary per
`openspec/specs/agent-registry/spec.md`) to be able to call the
5 image-gen tools (`list_image_models` + `generate_2d_asset` +
`generate_texture` + `style_match` + `cocoindex_register`) via the
shared `agents/adk/tools/image_generation.py` module. Per
`agents/agent_registry.py:AGENT_REGISTRY`, each agent's
`LlmAgent.tools=[...]` list MUST include the 5 image-gen tools
when the agent's role involves visual asset generation (the
`image_generation_agent` role).

#### Scenario: image_generation_agent exposes the 5 tools
- **GIVEN** the `image_generation_agent` is registered in AGENT_REGISTRY
- **WHEN** the agent is loaded via `LlmAgent(tools=[...])`
- **THEN** all 5 image-gen tools are present (NOT `None`)
- **AND** calling any tool returns a real LiteLLM-routed response

#### Scenario: Non-asset agents do not expose the 5 tools
- **GIVEN** the `corpus_agent` is registered in AGENT_REGISTRY
- **WHEN** the agent is loaded
- **THEN** the image-gen tools are NOT in its `tools=[...]` list
- **AND** calling an image-gen tool from this agent raises `AttributeError`

### Requirement: Per-language asset generation (6 Celtic)

The system MUST ship `baml_src/british_isles/_cross/asset_generation.baml` (new file)
that defines 6 asset-generation BAML functions (one per Celtic language):
`GenerateIrishAsset`, `GenerateWelshAsset`, `GenerateScottishGaelicAsset`,
`GenerateManxAsset`, `GenerateCornishAsset`, `GenerateBretonAsset`.
Each function MUST:

1. Take a `prompt` (EN) + an `asset_role` (one of the 5 image_gen roles)
2. Route through `model_for('image_gen', role='bilingual')` (currently `local/image/qwen-image`)
3. Return a typed `GeneratedAsset` record with `url` + `language` + `prompt_translated` (the EN→Celtic translation)
4. Land in the per-language LanceDB table (`media.image_gen_chunks_<lang>`)

#### Scenario: Irish asset generation

#### Scenario: Irish asset generation
- **WHEN** the operator runs `python scripts/celtic_assets.py "An Irish round tower"` with `lang=gaeilge`
- **THEN** `GenerateIrishAsset` is called via BAML
- **AND** the asset lands in `lance://media.image_gen_chunks_gaeilge`
- **AND** the marimo notebook at `notebooks/dashboards/asset_gen_gaeilge.py` shows it

#### Scenario: 6-language parallel generation
- **WHEN** the operator runs `python scripts/celtic_assets.py "round tower"` with no lang
- **THEN** the 6 BAML functions fire in parallel
- **AND** all 6 assets land in their respective LanceDB tables
- **AND** the runtime is < 30s (parallelised)
