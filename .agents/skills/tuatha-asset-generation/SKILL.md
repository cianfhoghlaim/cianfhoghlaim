---
name: tuatha-asset-generation
description: The asset-generation pipeline for the Cianfhoghlaim platform. Replaces the deprecated celtic-asset-generation skill. Covers the 5 image_gen MODEL_REGISTRY entries (flux2-dev + z-image-turbo + qwen-image + sdxl + fibo) + the BAML contracts (gameplay_descriptor + extract_design_pattern + extract_syllabus_diagram) + the FIBO 2D diagram generation + the CocoIndex image_generation flow + the ADK 2 Pillar 3 render_assets_node integration. Use when adding or modifying anything in the asset-generation chain — image models, BAML contracts, CocoIndex flows, marimo dashboards, FIBO diagrams, ADK Pillar 3 wiring, or Tuatha sprite banks.
---

# Tuatha Asset Generation

> **Replaces the deprecated `celtic-asset-generation` skill** (the latter is
> archived; this skill is the canonical reference for the converged asset-gen
> pipeline post-Plan 1 of the 2026-10 convergence saga).

## The 5 image_gen MODEL_REGISTRY entries

| Role | Key | Alias | Backend |
|:--|:--|:--|:--|
| `flux` | `local/image/flux2-dev` | `local/image/flux2-dev` | llama-swap (bunchloch) |
| `z_image` | `local/image/z-image-turbo` | `local/image/z-image-turbo` | llama-swap |
| `qwen` | `local/image/qwen-image` | `local/image/qwen-image` | llama-swap |
| `sdxl` | `local/image/sdxl` | `local/image/sdxl` | llama-swap |
| `fibo` | `local/image/fibo` | `local/image/fibo` | FIBO (via invokeai when deployed) |
| `unsloth_diffusion` | `local/image/diffusiongemma-26b-a4b` | `local/unsloth/diffusiongemma-26b-a4b` | unsloth-serve |
| `unsloth_qwen_image` | `local/image/qwen-image-2512` | `local/unsloth/qwen-image-2512` | unsloth-serve |

**NEVER hardcode a model string** — always go through
`MODEL_REGISTRY.filter(family='image_gen')` + `model_for('image_gen', role)`.

## The asset-generation chain (Pillar 3 + image-gen)

```
Pillar 3 deep-research pipeline
        │
        ├── decompose_agent    (QuestionDecomposer)
        ├── research_topic[]    (parallel_worker, N per pipeline)
        ├── synthesize_agent    (DeepResearchBriefing)
        └── render_assets_node  (NEW — Plan 1 of the 2026-10 saga)
                │
                ├── derive_asset_prompts(briefing)
                ├── generate_2d_asset(prompt, role)  ← per role
                ├── generate_texture(prompt, role)  ← Babylon.js PBR
                ├── style_match(reference, target)  ← style transfer
                └── cocoindex_register(asset)        ← LanceDB upsert
```

The `render_assets_node` is the shared Pillar-4 node added to all 5
Pillar 3 pipelines (aistear + primary + JC + SC + tertiary). Lives at
`agents/workflows/_render_assets_node.py` + wired via the
`edges=[(START, decompose, research_topic, synthesize, render_assets)]`
declaration in each pipeline.

## The tools (canonical module: `agents/adk/tools/image_generation.py`)

| Tool | Purpose | Backed by |
|:--|:--|:--|
| `list_image_models()` | List the 5 image_gen entries + availability | MODEL_REGISTRY |
| `generate_2d_asset(prompt, role, style?, width?, height?)` | 2D subject illustration / sprite | LiteLLM + image_gen model |
| `generate_texture(prompt, pattern, name, role?)` | Babylon.js PBR material | LiteLLM + image_gen model |
| `style_match(reference_prompt, target_prompt, count?, role?)` | N variants in style of reference | LiteLLM + image_gen model |
| `cocoindex_register(asset_url, asset_kind, metadata?)` | Register in CocoIndex media flow | LanceDB |

All tools route via LiteLLM with the resolved model's `litellm_alias`.
On failure, they fall back to a placeholder PNG (the `_stub_generate_image`
legacy path — kept as a safety net for offline dev mode).

## The CocoIndex flows

- `cocoindex_flows/media/image_generation_flow.py` — registers image-gen
  assets in `lance://media.image_gen_chunks`
- `cocoindex_flows/media/ocr_aware_flow.py` — the BAML+VLM extraction for
  diagrams detected in source PDFs
- `cocoindex_flows/media/artwork_embedding.py` — the per-asset
  `bge-m3` embedding
- (Future) `cocoindex_flows/media/retro_design_embedding.py` — Plan 2
  of the 2026-10 saga

## The BAML contracts

- `baml_src/clients_image_gen.baml` — the 6 image-gen BAML clients
  (`InvokeAILocalImageGen` + `ImageGenDefault` + `ImageGenFast` +
  `ImageGenBilingual` + `ImageGenLegacy` + `ImageGenDiagrams`)
- `baml_src/media/gameplay_descriptor.baml` — the Hades/WoW/Golden Sun/
  Pokémon gameplay descriptors
- (Future) `baml_src/media/extract_design_pattern.baml` — Plan 2
- (Future) `baml_src/media/extract_syllabus_diagram.baml` — Plan 3
- (Future) `baml_src/british_isles/_cross/asset_generation.baml` — Plan 6

## The FIBO 2D diagram generation (Plan 3 of the saga)

- `tuatha/asset_generation/fibo/{__init__,assets,education_fibo,resources,schemas}.py`
  (the 5 source files; currently only the .pyc files exist in `__pycache__/`)
- The 3-stage pipeline: `fibo_json_configs` → `fibo_configs_from_syllabus_diagrams`
  → `generated_images` (with `FiboResource` render + `ValidationResource` score
  + refinement iteration up to `max_refinement_iterations`)
- Traceability: every diagram has a `diagram_id` + `source_pdf` + `page_number`
  (no fabricated concepts from sample/placeholder fallbacks)

## The visible demo (C6 quality-of-life)

```bash
# List the 5 available image_gen models
uv run python scripts/asset_bench.py --list-models

# Generate a single asset across all 5 roles
uv run python python scripts/asset_bench.py "An Irish round tower at sunset"

# Generate a single asset with a specific role
uv run python scripts/asset_bench.py "An Irish round tower at sunset" --role qwen

# Run a full Pillar 3 pipeline (decompose → research → synthesise → render)
uv run python scripts/asset_bench.py --pipeline aistear_deep_research --query "How do the 4 themes support wellbeing?"
```

## Reference

- Plan 1 of the convergence saga: `openspec/plans/2026-10-01-convergence-saga-v1.md`
- The change: `openspec/changes/2026-10-02-adk-asset-generation-pillar3-v1/`
- The spec: `openspec/specs/adk-asset-gen-pillar3/spec.md`
- The shared node: `agents/workflows/_render_assets_node.py`
- The tool module: `agents/adk/tools/image_generation.py`
- The agent: `agents/adk/image_generation_agent.py`
- The CLI demo: `scripts/asset_bench.py`

## When to use this skill

Activate when the user asks about:

- "Generate an image" / "make a sprite" / "render a diagram"
- "Add a new image-gen model" / "swap the FIBO model" / "use Flux instead"
- "Wire the Pillar 3 pipelines to asset-gen"
- "Add the 6 Celtic language asset generation"
- "Tuatha sprite bank" / "MMO asset generation"
- "Babylon.js texture" / "FIBO 2D diagram"
- "Why is the image-gen returning a stub?" — answer: the litellm provider
  mapping is missing for `local/image/qwen-image`; needs to be added to
  `bonneagar/stacks/litellm/config/config.yaml` as
  `model: openai/qwen-image` (the Qwen-Image-Edit-2511 litellm alias is
  already wired; see Plan 4 / Lakehouse wiring for the bridge)
