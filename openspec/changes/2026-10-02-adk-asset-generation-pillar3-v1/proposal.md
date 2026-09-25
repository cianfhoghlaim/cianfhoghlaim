# Change: 2026-10-02-adk-asset-generation-pillar3-v1

## Why

The ADK 2 Pillar 3 deep-research pipelines (aistear + primary + JC + SC + tertiary) currently produce a written briefing but no visual assets. The `image_generation_agent` exists but with `GENERATE_2D_ASSET_TOOL = None` (stub). The 6 `_stub_generate_image` calls return `{"stub": True}` dicts. The 5 `image_gen` MODEL_REGISTRY entries (flux2-dev + z-image-turbo + qwen-image + sdxl + fibo) are wired through litellm but never called.

This blocks the entire asset-generation chain — no real diagrams, no real subject illustrations, no real bilingual EN/GA artwork. The Tuatha British Isles MMO can't be built because its sprite banks depend on the image-gen pipeline. The educational agents can't show assets when answering questions.

This is Plan 1 of the convergence saga (`openspec/plans/2026-10-01-convergence-saga-v1.md`).

## What Changes

### Code — replaces stubs with real implementations
- `agents/adk/tools/image_generation.py` — replace `_stub_generate_image` with real LiteLLM-routed calls (line 547, 553, 565)
- `agents/adk/image_generation_agent.py` — replace the 5 `*_TOOL = None` placeholders with real `FunctionTool` wraps
- `agents/workflows/aistear_deep_research.py` — add `render_assets_node` (Pillar 4 stage)
- `agents/workflows/primary_deep_research.py` — same
- `agents/workflows/jc_deep_research.py` — same
- `agents/workflows/sc_deep_research.py` — same
- `agents/workflows/tertiary_deep_research.py` — same

### New files
- `scripts/asset_bench.py` — the visible demo CLI
- `notebooks/dashboards/asset_gen_demo.py` — the marimo dashboard
- `.agents/skills/tuatha-asset-generation/SKILL.md` — replaces deprecated `celtic-asset-generation`

### Specs — new
- `openspec/specs/adk-asset-gen-pillar3/spec.md` — 4 Requirements

### Reference surfaces
- `meaisinfhoghlaim/models/model_registry.py` — the 5 `image_gen` entries (lines 142-186)
- `baml_src/clients_image_gen.baml` — the 6 image-gen BAML clients
- `agents/workflows/sc_deep_research.py` — the existing Pillar 3 pattern to extend
- `openspec/plans/2026-10-01-convergence-saga-v1.md` — Plan 1 of the saga

## What this does NOT ship
- Tuatha closed-loop demo (Plan 7)
- CocoIndex retro gameplay flow (Plan 2)
- FIBO diagram generation (Plan 3)
- Lakehouse bridge for assets (Plan 4)
- Cognee entity-asset graph (Plan 5)
- Celtic bilingual asset generation (Plan 6)
- Fresh-slate spec refactor (Plan 8)

Licence: BUSL-1.1 Cianfhoghlaim edition (per LICENSE.md).
