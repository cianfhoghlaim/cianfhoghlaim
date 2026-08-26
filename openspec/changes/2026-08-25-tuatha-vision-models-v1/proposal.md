# Change: tuatha-vision-models (v1)

## Why

The capture pipeline consumes 3 vision models (one per source). All
three should be registered in `MODEL_REGISTRY` so the
`mise run lint:registry` pre-commit hook can enforce the no-hardcode
invariant.

## What changes

- New entries in `meaisinfhoghlaim/models/model_registry.py:MODEL_REGISTRY`
  under the `ocr_vision` family:
  - `qwen3-vl-8b` (role: `tier2_medium`) — for Hades + Comic.
  - `qwen3-vl-4b` (role: `tier3_light`) — for GBA (small frames).
- New BAML client declarations in `baml_src/tuatha_media_intel.baml`:
  - `HadesBoonClient` / `ComicParticleClient` / `GbaMagicClient` /
    `AnamMapClient` (4 clients, no hardcoded model strings).

## Impact

- Affected spec: `openspec/specs/centralized-model-registry/spec.md`
  (§11 OCR/VLM Pipeline).

## Out of scope

- Adding new `text_llm` entries (the `minimax-m3` default is already
  present and is what `AnamMapClient` uses).
- Adding `image_gen` entries (the ANAM particle generation is
  downstream of this change; it ships with the 2D asset generator).

## Verification

1. `mise run models:list | grep tuatha` shows the 3 new entries.
2. `mise run lint:registry --strict` exits 0.
3. `baml-cli test baml_src/tuatha_media_intel.baml` passes.
