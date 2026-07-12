# BAML shared — per-quadrant BAML merger, Phase 2.1.

## What

The `cianfhoghlaim/core/baml/` tree currently has 4 per-quadrant
BAML sub-packages (`_oideachais_src/`, `_meaisinfhoghlaim_src/`,
`_tuatha_src/`, `_croilar_baml/`) plus 2 legacy sub-trees
(`docs/legacy/crypteolas/baml_src/` + `scéimre/`). Each quadrant
has its own `clients.baml` and `generators.baml` (where they
exist), leading to drift: 2 of the 4 quadrants use BAML 0.74.0,
the other 2 have no `generators.baml` at all.

Phase 2.1 creates the canonical `cianfhoghlaim/core/baml/shared/`
directory with 2 files:

1. `clients.baml` — the unified 7-client registry:
   - 1 default (`litellm` — the canonical LiteLLM gateway route)
   - 4 per-quadrant defaults (`oideachais_default`,
     `meaisinfhoghlaim_default`, `tuatha_default`,
     `croilar_default`)
   - 2 shared cross-quadrant clients (`vision_local` via
     llama-swap, `reasoning_strong` for hard extraction)
2. `generators.baml` — the unified Python + TypeScript codegen
   targets at BAML 0.76.2 (the current upstream version per
   the BAML skill).

This file does NOT yet replace the per-quadrant `clients.baml`
files (that's Phase 2.2). It just creates the canonical home
so the per-quadrant files can be migrated in Phase 2.2-2.5.

## Why

- The 4 per-quadrant `clients.baml` files have drifted:
  `_oideachais_src/clients.baml` uses the `litellm` provider;
  `_tuatha_src/tuatha_clients.baml` declares 5 standalone clients
  with hardcoded `openai` provider; `_croilar_baml/clients.baml`
  uses `local/vision/qwen3-vl` directly; `_meaisinfhoghlaim_src/`
  has no client file at all (falls through to inline `provider`).
- The 4 per-quadrant `generators.baml` files have similarly drifted:
  2 use 0.74.0, 2 are empty.
- A single `shared/` is required before the 4 quadrants can
  consolidate into the canonical 1-tree
  (`openspec/changes/2026-06-28-consolidate-sruth-into-cianfhoghlaim-v4`).

## Validation

- `baml-cli check` exits 0 against `shared/clients.baml` +
  `shared/generators.baml` standalone.
- All 7 named clients are discoverable by `baml-cli list clients`.
- The 2 generators produce identical outputs to the per-quadrant
  0.74.0 generators (modulo version bump to 0.76.2).
